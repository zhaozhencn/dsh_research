#!/usr/bin/env python3
"""Local Git fixtures test update/provenance safeguards, without fetching Harness."""
import contextlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location('research', Path(__file__).with_name('research.py'))
research = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research)


class ResearchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.repo = self.root / 'repo'; self.repo.mkdir()
        self.g('init', '-b', 'main'); self.g('config', 'user.name', 'Fixture'); self.g('config', 'user.email', 'fixture@example.invalid')
        self.put('package.json', json.dumps({'name': 'fixture', 'version': '1.0.0', 'packageManager': 'pnpm@10.0.0'}))
        self.put('pnpm-workspace.yaml', "packages:\n  - 'packages/**'\n  - '!packages/excluded'\n")
        for path, pkg in [('packages/a', {'name': '@fixture/a', 'version': '1.0.0'}),
                          ('packages/b', {'name': '@fixture/b', 'version': '1.0.0', 'dependencies': {'@fixture/a': 'workspace:*'}}),
                          ('packages/excluded', {'name': 'excluded', 'version': '1.0.0'})]:
            self.put(path + '/package.json', json.dumps(pkg))
        self.put('packages/a/source.ts', 'first\nunique evidence\nlast\n')
        self.old = self.commit('initial')
        self.previous = self.root / 'previous'
        research.write_json(self.previous / 'appendices/baseline.json', {'sha': self.old})
        research.write_json(self.previous / 'appendices/evidence.json', {
            'E1': {'path': 'packages/a/source.ts', 'start': 2, 'end': 2, 'symbol': 'unique', 'category': '源码事实'}})

    def g(self, *args):
        return research.git(self.repo, *args).stdout.decode().strip()

    def put(self, path, value):
        target = self.repo / path; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(value)

    def commit(self, message):
        self.g('add', '--all'); self.g('commit', '-m', message)
        return self.g('rev-parse', 'HEAD')

    def snapshot(self, **updates):
        values = dict(repo=str(self.repo), target='HEAD', out=str(self.root / 'output'), previous=str(self.previous),
                      resolution=None, workspace_list=None, repo_url=research.DEFAULT_REMOTE)
        values.update(updates)
        with contextlib.redirect_stdout(io.StringIO()):
            research.command_snapshot(SimpleNamespace(**values))
        return Path(values['out'])

    def resolve(self, ref=None):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            research.command_resolve(SimpleNamespace(remote=str(self.repo), ref=ref, out=None))
        return json.loads(output.getvalue())

    def status(self, target=None):
        return research.evidence_diff(self.repo, self.previous, self.old, target or self.g('rev-parse', 'HEAD'))['records']['E1']

    def test_workspace_inventory_excludes_non_members_and_root(self):
        rows, _, meta = research.enumerate_workspaces(self.repo, self.old, research.tree(self.repo, self.old))
        self.assertEqual([r['path'] for r in rows], ['packages/a', 'packages/b'])
        self.assertEqual(len(research.dependency_graph(rows)['edges']), 1)
        self.assertEqual(meta['method'], 'commit-workspace-globs')

    def test_unsupported_workspace_fails_explicitly(self):
        self.put('pnpm-workspace.yaml', 'packages: ["packages/*"]\n'); sha = self.commit('complex yaml')
        with self.assertRaisesRegex(ValueError, 'workspace-list'):
            research.enumerate_workspaces(self.repo, sha, research.tree(self.repo, sha))

    def test_provided_workspace_omission_rejected(self):
        listing = self.root / 'workspaces.json'
        research.write_json(listing, [{'name': '@fixture/a', 'version': '1.0.0', 'path': str(self.repo / 'packages/a')}])
        with self.assertRaisesRegex(ValueError, 'missing='):
            research.enumerate_workspaces(self.repo, self.old, research.tree(self.repo, self.old), listing)

    def test_snapshot_reads_commit_not_dirty_worktree(self):
        self.put('packages/a/source.ts', 'uncommitted content\n')
        self.put('package.json', '{bad uncommitted JSON')
        out = self.snapshot(); baseline = research.json_read(out / 'appendices/baseline.json')
        self.assertEqual(baseline['version'], '1.0.0'); self.assertFalse(baseline['tracked_worktree_clean'])
        self.assertEqual(research.json_read(out / 'research-state.json')['status'], 'prepared')

    def test_same_sha_is_not_invented_update(self):
        out = self.snapshot()
        self.assertEqual(research.json_read(out / 'research-state.json')['mode'], 'no-upstream-change')
        self.assertEqual(research.json_read(out / 'appendices/changes.json')['files'], [])
        self.assertEqual(self.status()['review_status'], 'pending')

    def test_output_overwrite_rejected_and_previous_unchanged(self):
        before = (self.previous / 'appendices/baseline.json').read_bytes(); out = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            self.snapshot()
        self.assertEqual((self.previous / 'appendices/baseline.json').read_bytes(), before)
        self.assertTrue(out.is_dir())

    def test_prepared_report_cannot_be_previous(self):
        research.write_json(self.previous / 'research-state.json', {'status': 'prepared'})
        with self.assertRaisesRegex(ValueError, 'not complete'):
            self.snapshot()

    def test_reanchored_evidence_is_pending(self):
        self.put('packages/a/source.ts', 'inserted\nfirst\nunique evidence\nlast\n'); self.commit('move line')
        item = self.status()
        self.assertEqual(item['status'], 'reanchored-identical-text'); self.assertEqual(item['candidate_start'], 3)
        self.assertEqual(item['review_status'], 'pending')

    def test_renamed_evidence_and_consumer_impact(self):
        self.g('mv', 'packages/a/source.ts', 'packages/a/renamed.ts'); self.commit('rename')
        self.assertEqual(self.status()['candidate_path'], 'packages/a/renamed.ts')
        out = self.snapshot()
        self.assertEqual(research.json_read(out / 'appendices/impact.json')['possible_consumers'], ['packages/b'])

    def test_ambiguous_changed_and_missing_evidence(self):
        self.put('packages/a/source.ts', 'unique evidence\nunique evidence\n'); self.commit('duplicate')
        self.assertEqual(self.status()['status'], 'ambiguous')
        self.put('packages/a/source.ts', 'replacement\n'); self.commit('change')
        self.assertEqual(self.status()['status'], 'changed')
        self.g('rm', 'packages/a/source.ts'); self.commit('remove')
        self.assertEqual(self.status()['status'], 'missing')

    def test_removed_package_keeps_old_consumers_in_impact(self):
        self.g('rm', '-r', 'packages/a'); self.put('global.config.json', '{}\n'); self.commit('remove provider')
        out = self.snapshot(); impact = research.json_read(out / 'appendices/impact.json')
        self.assertEqual(impact['removed_packages'], ['packages/a'])
        self.assertEqual(impact['possible_consumers'], ['packages/b'])
        self.assertIn('global.config.json', impact['files_outside_packages'])

    def test_remote_default_branch_and_annotated_tag_resolve_commit(self):
        self.g('tag', '-a', 'v1', '-m', 'annotated')
        self.assertEqual(self.resolve()['ref'], 'refs/heads/main')
        self.assertEqual(self.resolve('v1')['sha'], self.old)
        self.assertEqual(self.resolve('refs/tags/v1')['sha'], self.old)

    def test_ambiguous_ref_rejected(self):
        self.g('tag', 'main')
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            self.resolve('main')

    def test_resolution_mismatch_rejected(self):
        resolution = self.root / 'resolution.json'
        research.write_json(resolution, {'sha': self.old, 'repository': 'https://example.invalid/other'})
        with self.assertRaisesRegex(ValueError, 'repository'):
            self.snapshot(resolution=str(resolution))
        research.write_json(resolution, {'sha': '0' * 40, 'repository': research.DEFAULT_REMOTE})
        with self.assertRaisesRegex(ValueError, 'SHA'):
            self.snapshot(resolution=str(resolution))

    def completed_fixture(self):
        out = self.snapshot()
        for filename in research.REQUIRED:
            target = out / filename; target.parent.mkdir(parents=True, exist_ok=True); target.write_text('Fixture report\n')
        research.write_json(out / 'appendices/coverage.json', [{'path': 'packages/a'}, {'path': 'packages/b'}])
        research.write_json(out / 'appendices/evidence.json', {'E1': {
            'category': '源码事实', 'sha': self.old, 'path': 'packages/a/source.ts', 'start': 2, 'end': 2,
            'review_status': 'reviewed', 'snippet_hash': research.snippet_hash(['unique evidence'])}})
        (out / 'appendices/delta.md').write_text('No change\n')
        research.write_json(out / 'appendices/claims.json', [{'id': 'C1', 'status': 'retained', 'reviewed_at_sha': self.old, 'evidence_ids': ['E1']}])
        for name in ['a', 'b']:
            directory = out / 'examples' / name; directory.mkdir(parents=True); (directory / 'index.ts').write_text('// fixture\n')
        (out / 'validation').mkdir(); (out / 'validation/log.txt').write_text('fixture execution\n')
        research.write_json(out / 'validation/runs.json', [{'id': 'run1', 'sha': self.old, 'command': ['fixture'],
            'scope': 'fixture', 'log_path': 'validation/log.txt', 'outcome': 'passed', 'exit_code': 0,
            'purposes': ['normal-loop', 'abnormal-or-cancel']}])
        return out

    def test_final_requires_current_sha_runtime_ledger(self):
        out = self.completed_fixture(); self.assertTrue(research.check_report(self.repo, out, True)['ok'])
        runs = research.json_read(out / 'validation/runs.json'); runs[0]['sha'] = '0' * 40
        research.write_json(out / 'validation/runs.json', runs)
        self.assertIn('another SHA', ' '.join(research.check_report(self.repo, out, True)['errors']))

    def test_invalid_anchor_and_unreviewed_evidence_rejected(self):
        out = self.completed_fixture(); evidence = research.json_read(out / 'appendices/evidence.json')
        evidence['E1']['review_status'] = 'pending'; research.write_json(out / 'appendices/evidence.json', evidence)
        self.assertFalse(research.check_report(self.repo, out, True)['ok'])
        evidence['E1']['review_status'] = 'reviewed'; evidence['E1']['end'] = 100
        research.write_json(out / 'appendices/evidence.json', evidence)
        self.assertIn('Out of range', ' '.join(research.check_report(self.repo, out, True)['errors']))

    def test_broken_links_and_wrong_source_sha_rejected(self):
        out = self.completed_fixture()
        (out / 'README.md').write_text('[missing](missing.md)\n[source](%s/blob/%s/packages/a/source.ts#L1)\n' %
                                      (research.DEFAULT_REMOTE, '0' * 40))
        errors = ' '.join(research.check_report(self.repo, out, True)['errors'])
        self.assertIn('Missing local link', errors); self.assertIn('Non-current source link', errors)

    def test_typed_runtime_and_inference_require_real_provenance(self):
        out = self.completed_fixture(); evidence = research.json_read(out / 'appendices/evidence.json')
        evidence['R1'] = {'category': '运行验证', 'sha': self.old, 'review_status': 'reviewed', 'run_ids': ['run1']}
        evidence['A1'] = {'category': '分析推断', 'sha': self.old, 'review_status': 'reviewed',
                          'based_on': ['E1', 'R1'], 'premise': 'fixture scope only'}
        research.write_json(out / 'appendices/evidence.json', evidence)
        self.assertTrue(research.check_report(self.repo, out, True)['ok'])
        evidence['R1']['run_ids'] = ['missing']; evidence['A1']['based_on'] = ['A1']
        research.write_json(out / 'appendices/evidence.json', evidence)
        errors = ' '.join(research.check_report(self.repo, out, True)['errors'])
        self.assertIn('run IDs', errors); self.assertIn('premises', errors)

    def test_false_pass_exit_code_and_missing_log_rejected(self):
        out = self.completed_fixture(); runs = research.json_read(out / 'validation/runs.json')
        runs[0]['exit_code'] = 1; runs[0]['log_path'] = 'validation/absent.log'
        research.write_json(out / 'validation/runs.json', runs)
        errors = ' '.join(research.check_report(self.repo, out, True)['errors'])
        self.assertIn('Missing validation log', errors); self.assertIn('nonzero', errors)

    def test_negated_glob_and_brace_patterns(self):
        self.assertTrue(research.glob_match('packages/nested/a', 'packages/**'))
        self.assertFalse(research.glob_match('packages/nested/a', 'packages/*'))
        self.assertEqual(research.brace_expand('packages/{a,b}'), ['packages/a', 'packages/b'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
