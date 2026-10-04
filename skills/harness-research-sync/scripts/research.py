#!/usr/bin/env python3
"""Pin and compare Harness research inputs. Git objects only; no technical conclusions."""
import argparse
import collections
import datetime as dt
import fnmatch
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote, urlparse

DEFAULT_REMOTE = 'https://github.com/deepseek-ai/deepseek-harness'
DEPENDENCY_KINDS = ('dependencies', 'peerDependencies', 'devDependencies', 'optionalDependencies')
CATEGORIES = {'源码事实', '官方说明', '运行验证', '分析推断', '改造建议'}
REQUIRED = ('README.md', '01-architecture.md', '02-runtime-source.md', '03-extension-practices.md',
            'appendices/baseline.md', 'appendices/coverage.md', 'appendices/evidence-index.md',
            'appendices/validation.md', 'appendices/open-questions.md')


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def run(argv, cwd=None, check=True):
    p = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode:
        raise ValueError('%s failed (%s): %s' % (argv[0], p.returncode, p.stderr.decode('utf-8', 'replace').strip()))
    return p


def git(repo, *args, check=True):
    return run(['git', '-C', str(repo), *args], check=check)


def resolve_commit(repo, ref):
    return git(repo, 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}').stdout.decode().strip()


def json_read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def tree(repo, sha):
    result = {}
    for record in git(repo, 'ls-tree', '-r', '-z', sha).stdout.split(b'\0'):
        if not record:
            continue
        meta, path = record.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        result[path.decode('utf-8')] = {'mode': mode, 'kind': kind, 'object_id': oid}
    return result


def blobs(repo, oids):
    ids = sorted(set(oids))
    if not ids:
        return {}
    p = subprocess.run(['git', '-C', str(repo), 'cat-file', '--batch'],
                       input=('\n'.join(ids) + '\n').encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise ValueError(p.stderr.decode('utf-8', 'replace'))
    result, pos = {}, 0
    for oid in ids:
        end = p.stdout.index(b'\n', pos)
        header = p.stdout[pos:end].decode().split()
        if len(header) != 3 or header[1] != 'blob':
            raise ValueError('Expected a Git blob: ' + oid)
        size = int(header[2]); pos = end + 1
        result[oid] = p.stdout[pos:pos + size]; pos += size + 1
    return result


def source(repo, entries, path):
    entry = entries.get(path)
    if not entry or entry['kind'] != 'blob':
        raise ValueError('Missing source blob: ' + path)
    return blobs(repo, [entry['object_id']])[entry['object_id']].decode('utf-8')


def brace_expand(pattern):
    if '[' in pattern or ']' in pattern:
        raise ValueError('Workspace character classes require authoritative pnpm list')
    match = re.search(r'\{([^{}]+)\}', pattern)
    if match:
        items = match.group(1).split(',')
        if len(items) < 2:
            raise ValueError('Unsupported brace pattern: ' + pattern)
        return [p for item in items for p in brace_expand(pattern[:match.start()] + item + pattern[match.end():])]
    if '{' in pattern or '}' in pattern or re.search(r'[+@?!*]\(', pattern):
        raise ValueError('Unsupported workspace pattern: ' + pattern)
    return [pattern]


def glob_match(path, pattern):
    a = PurePosixPath(path).parts; b = PurePosixPath(pattern.removeprefix('./')).parts
    def match(i, j):
        if j == len(b):
            return i == len(a)
        if b[j] == '**':
            return match(i, j + 1) or (i < len(a) and match(i + 1, j))
        return i < len(a) and fnmatch.fnmatchcase(a[i], b[j]) and match(i + 1, j + 1)
    return match(0, 0)


def workspace_patterns(text):
    """Intentionally a strict scalar-list subset, not a general YAML parser."""
    lines = text.splitlines(); collecting = False; result = []
    for line in lines:
        if not collecting:
            if re.fullmatch(r'packages:\s*(?:#.*)?', line):
                collecting = True
            continue
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if not line.startswith((' ', '\t')) and not line.startswith('-'):
            break
        m = re.fullmatch(r'\s*-\s*(?:\'([^\']*)\'|"([^"\\]*)"|([^#\[\]{}\s][^#]*?))\s*(?:#.*)?', line)
        if not m:
            raise ValueError('Complex workspace YAML; use current pnpm list: ' + line.strip())
        value = next(x for x in m.groups() if x is not None).strip()
        if not value or any(x in value for x in ('\n', '\\', '://')):
            raise ValueError('Unsupported workspace value')
        result.append(value)
    if not collecting or not result:
        raise ValueError('No supported pnpm packages list')
    return result


def enumerate_workspaces(repo, sha, entries, workspace_list=None):
    manifest_paths = [p for p, e in entries.items() if PurePosixPath(p).name == 'package.json' and e['kind'] == 'blob']
    content = blobs(repo, [entries[p]['object_id'] for p in manifest_paths])
    manifests = {str(PurePosixPath(p).parent): json.loads(content[entries[p]['object_id']]) for p in manifest_paths}
    root_manifest = manifests.get('.', {})
    patterns = None; parse_error = None
    try:
        if 'pnpm-workspace.yaml' in entries:
            patterns = workspace_patterns(source(repo, entries, 'pnpm-workspace.yaml'))
        else:
            patterns = root_manifest.get('workspaces')
            if isinstance(patterns, dict):
                patterns = patterns.get('packages')
            if not isinstance(patterns, list) or not patterns:
                raise ValueError('No workspace declaration')
        positive = [p for v in patterns if not v.startswith('!') for p in brace_expand(v)]
        negative = [p for v in patterns if v.startswith('!') for p in brace_expand(v[1:])]
        expected = {p for p in manifests if p != '.' and any(glob_match(p, v) for v in positive)
                    and not any(glob_match(p, v) for v in negative)}
    except ValueError as error:
        parse_error = str(error); expected = None
    method = 'commit-workspace-globs'
    if workspace_list:
        if resolve_commit(repo, 'HEAD') != sha or git(repo, 'diff', '--quiet', 'HEAD', check=False).returncode:
            raise ValueError('pnpm list requires HEAD and tracked working files to match target')
        projects = json_read(workspace_list)
        if not isinstance(projects, list):
            raise ValueError('pnpm workspace list must be a JSON array')
        selected = set()
        for project in projects:
            try:
                path = Path(project['path']).resolve().relative_to(Path(repo).resolve()).as_posix()
            except (KeyError, ValueError):
                raise ValueError('pnpm project path outside checkout')
            if path == '.':
                continue
            manifest = manifests.get(path)
            if manifest is None or project.get('name') != manifest.get('name') or project.get('version') != manifest.get('version'):
                raise ValueError('pnpm entry does not match target manifest: ' + path)
            if path in selected:
                raise ValueError('Duplicate pnpm project: ' + path)
            selected.add(path)
        if expected is not None and selected != expected:
            raise ValueError('pnpm projects mismatch declaration; missing=%s extra=%s' % (sorted(expected - selected), sorted(selected - expected)))
        expected = selected; method = 'provided-pnpm-list'
    if expected is None:
        raise ValueError(parse_error + '; supply --workspace-list from the clean target checkout')
    rows = []
    for path in sorted(expected):
        m = manifests[path]
        rows.append({'path': path, 'name': m.get('name'), 'version': m.get('version'),
                     'description': m.get('description', ''), 'private': m.get('private', False),
                     'dsh': m.get('dsh'), 'deps': {k: m[k] for k in DEPENDENCY_KINDS if k in m},
                     'manifest_blob': entries[path + '/package.json']['object_id'],
                     'files': [p for p in entries if p.startswith(path + '/')]})
    return rows, root_manifest, {'method': method, 'patterns': patterns, 'parser_limitation': parse_error}


def load_previous(report):
    report = Path(report).resolve(); baseline = json_read(report / 'appendices/baseline.json')
    sha = baseline.get('sha') or baseline.get('commit_sha')
    if not isinstance(sha, str) or not re.fullmatch(r'[0-9a-f]{40,64}', sha):
        raise ValueError('Previous baseline requires a full commit SHA')
    state = report / 'research-state.json'
    status = json_read(state).get('status') if state.exists() else 'legacy-ungraded'
    if status != 'complete' and status != 'legacy-ungraded':
        raise ValueError('Previous report is not complete: ' + str(status))
    return report, sha, status


def changes(repo, old, new):
    parts = git(repo, 'diff', '--name-status', '-M', '-z', old, new, '--').stdout.split(b'\0')
    result = []; i = 0
    while i < len(parts) and parts[i]:
        status = parts[i].decode(); i += 1
        if status.startswith(('R', 'C')):
            before = parts[i].decode('utf-8'); after = parts[i + 1].decode('utf-8'); i += 2
        else:
            name = parts[i].decode('utf-8'); i += 1
            before = None if status == 'A' else name
            after = None if status == 'D' else name
        result.append({'status': status, 'old_path': before, 'new_path': after})
    return result


def snippet_hash(lines):
    return hashlib.sha256('\n'.join(lines).encode('utf-8')).hexdigest()


def evidence_diff(repo, report, old, new):
    evidence_file = Path(report) / 'appendices/evidence.json'
    records = json_read(evidence_file) if evidence_file.exists() else {}
    before_tree = tree(repo, old); after_tree = tree(repo, new)
    rename = {r['old_path']: r['new_path'] for r in changes(repo, old, new) if r['status'].startswith('R')}
    result = {}
    for key, record in records.items():
        path = record.get('path'); candidate = rename.get(path, path)
        item = {'previous_sha': old, 'target_sha': new, 'previous': record,
                'candidate_path': candidate, 'review_status': 'pending', 'status': 'invalid-previous'}
        result[key] = item
        try:
            lines = source(repo, before_tree, path).splitlines()
            a, b = record['start'], record['end']
            if not isinstance(a, int) or not isinstance(b, int) or not (0 < a <= b <= len(lines)):
                raise ValueError('Invalid old range')
            selected = lines[a - 1:b]; item['previous_snippet_hash'] = snippet_hash(selected)
        except (ValueError, KeyError, TypeError):
            continue
        if candidate not in after_tree:
            item['status'] = 'missing'; continue
        new_lines = source(repo, after_tree, candidate).splitlines()
        positions = [i for i in range(len(new_lines) - len(selected) + 1) if new_lines[i:i + len(selected)] == selected]
        if len(positions) == 1:
            start = positions[0] + 1
            item.update(status='identical-text' if path == candidate and start == a else 'reanchored-identical-text',
                        candidate_start=start, candidate_end=start + len(selected) - 1,
                        candidate_snippet_hash=snippet_hash(selected), candidate_blob=after_tree[candidate]['object_id'])
        elif len(positions) > 1:
            item.update(status='ambiguous', candidate_starts=[i + 1 for i in positions])
        else:
            item['status'] = 'changed'
    return {'old_sha': old, 'new_sha': new, 'note': 'Text matching only. All semantic conclusions require review; no old runtime results are carried forward.', 'records': result}


def dependency_graph(rows):
    names = {r['name']: r['path'] for r in rows if r['name']}
    edges = []
    for row in rows:
        for kind, deps in row['deps'].items():
            for name, version in deps.items():
                if name in names:
                    edges.append({'source': row['path'], 'target': names[name], 'kind': kind, 'range': version})
    return {'note': 'Manifest declarations only; not static imports, DI, events or runtime reachability.',
            'nodes': [{k: r[k] for k in ('path', 'name', 'version')} for r in rows], 'edges': edges}


def impact(rows, old_rows, diff):
    all_paths = sorted({r['path'] for r in rows + old_rows}, key=len, reverse=True)
    def owner(path):
        return next((p for p in all_paths if path and path.startswith(p + '/')), None)
    affected = set()
    for row in diff:
        affected.update(x for x in [owner(row['old_path']), owner(row['new_path'])] if x)
    graph = dependency_graph(rows); old_graph = dependency_graph(old_rows); consumers = set(affected)
    edges = graph['edges'] + old_graph['edges']
    while True:
        new = {e['source'] for e in edges if e['target'] in consumers} - consumers
        if not new:
            break
        consumers.update(new)
    old = {r['path']: r for r in old_rows}; current = {r['path']: r for r in rows}
    return {'direct_packages': sorted(affected), 'possible_consumers': sorted(consumers - affected),
            'added_packages': sorted(set(current) - set(old)), 'removed_packages': sorted(set(old) - set(current)),
            'files_outside_packages': sorted({p for r in diff for p in (r['old_path'], r['new_path']) if p and not owner(p)}),
            'manifest_changed': sorted(p for p in set(old) & set(current) if old[p].get('manifest_blob') != current[p].get('manifest_blob')),
            'note': 'Conservative old+new manifest graph includes test/peer edges and consumers of removed packages. Files outside packages may have global effects. Agent must inspect symbols, dynamic subscriptions, configuration and unchanged consumers.'}


def command_resolve(args):
    if args.remote.startswith('-'):
        raise ValueError('Remote must not be a Git option')
    base = ['git', 'ls-remote', '--symref', '--', args.remote]
    if args.ref:
        patterns = ([args.ref, args.ref + '^{}'] if args.ref.startswith('refs/tags/') else
                    [args.ref] if args.ref.startswith('refs/') else
                    ['refs/heads/' + args.ref, 'refs/tags/' + args.ref, 'refs/tags/' + args.ref + '^{}'])
        data = run(base + patterns).stdout.decode('utf-8')
        refs = {line.split('\t')[1]: line.split('\t')[0] for line in data.splitlines() if not line.startswith('ref:')}
        plain = [r for r in refs if not r.endswith('^{}')]
        if len(plain) != 1:
            raise ValueError('Requested ref is missing or ambiguous: ' + args.ref)
        branch = plain[0]; sha = refs.get(branch + '^{}', refs[branch])
    else:
        data = run(base + ['HEAD']).stdout.decode('utf-8')
        sha = branch = None
        for line in data.splitlines():
            value, name = line.split('\t')
            if value.startswith('ref:') and name == 'HEAD':
                branch = value[5:]
            elif name == 'HEAD':
                sha = value
        if not sha:
            raise ValueError('Remote HEAD unavailable')
    result = {'repository': args.remote, 'requested_ref': args.ref or 'default-branch-HEAD',
              'ref': branch, 'sha': sha, 'resolved_at': now(), 'method': 'git-ls-remote'}
    if args.out:
        if Path(args.out).exists():
            raise ValueError('Refusing to overwrite resolution output')
        write_json(args.out, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_snapshot(args):
    repo = Path(args.repo).resolve(); out = Path(args.out).resolve()
    if out.exists():
        raise ValueError('Refusing to overwrite existing report directory: ' + str(out))
    sha = resolve_commit(repo, args.target); entries = tree(repo, sha)
    rows, root_manifest, enumeration = enumerate_workspaces(repo, sha, entries, args.workspace_list)
    previous_report = old = previous_status = None
    if args.previous:
        previous_report, old, previous_status = load_previous(args.previous)
        if resolve_commit(repo, old) != old:
            raise ValueError('Previous commit unavailable in checkout')
    resolution = json_read(args.resolution) if args.resolution else None
    if resolution and resolution.get('sha') != sha:
        raise ValueError('Target does not match freshly resolved SHA')
    if resolution and resolution.get('repository', '').rstrip('/') != args.repo_url.rstrip('/'):
        raise ValueError('Resolution repository does not match --repo-url')
    commit = git(repo, 'show', '-s', '--format=%cI%n%s', sha).stdout.decode('utf-8').splitlines()
    head = resolve_commit(repo, 'HEAD')
    clean = git(repo, 'status', '--porcelain', '--untracked-files=no').stdout == b''
    def version(program):
        try:
            p = run([program, '--version'], check=False)
            return p.stdout.decode('utf-8').strip() if p.returncode == 0 else None
        except OSError:
            return None
    baseline = {'schema_version': 1, 'research_date': now(), 'repository': args.repo_url.rstrip('/'), 'sha': sha,
                'previous_sha': old, 'commit_date': commit[0], 'commit_subject': commit[1], 'checkout': str(repo),
                'checkout_head': head, 'tracked_worktree_clean': clean, 'checkout_matches_target': sha == head,
                'version': root_manifest.get('version'), 'packageManager': root_manifest.get('packageManager'),
                'engines': root_manifest.get('engines'), 'tracked_files': len(entries), 'workspace_packages': len(rows),
                'environment': {'platform': platform.platform(), 'python': platform.python_version(),
                                'git': version('git'), 'node': version('node'), 'corepack': version('corepack')},
                'workspace_enumeration': enumeration, 'latest_resolution': resolution}
    mode = 'no-upstream-change' if old == sha else 'incremental' if old else 'initial'
    state = {'schema_version': 1, 'status': 'prepared', 'mode': mode, 'sha': sha, 'previous_sha': old,
             'previous_report': str(previous_report) if previous_report else None,
             'previous_status': previous_status, 'prepared_at': now(),
             'note': 'Inventory and review candidates only. Reports, examples and current-SHA validation remain required.'}
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.harness-snapshot-', dir=out.parent))
    try:
        write_json(stage / 'research-state.json', state); write_json(stage / 'appendices/baseline.json', baseline)
        write_json(stage / 'appendices/workspace-inventory.json', rows)
        write_json(stage / 'appendices/dependency-graph.json', dependency_graph(rows))
        files = sorted(entries)
        write_json(stage / 'appendices/tracked-files.json', files)
        (stage / 'appendices/tracked-files.txt').write_text('\n'.join(files) + '\n', encoding='utf-8')
        write_json(stage / 'appendices/directory-inventory.json', dict(sorted(collections.Counter(p.split('/')[0] if '/' in p else '[root files]' for p in files).items())))
        if old:
            diff = changes(repo, old, sha); old_entries = tree(repo, old)
            old_rows, _, _ = enumerate_workspaces(repo, old, old_entries)
            ancestor = git(repo, 'merge-base', '--is-ancestor', old, sha, check=False).returncode == 0
            write_json(stage / 'appendices/changes.json', {'old_sha': old, 'new_sha': sha, 'old_is_ancestor': ancestor, 'files': diff})
            write_json(stage / 'appendices/impact.json', impact(rows, old_rows, diff))
            log = git(repo, 'log', '--format=%H%x09%cI%x09%s', old + '..' + sha).stdout.decode('utf-8')
            commits = [dict(zip(('sha', 'committed_at', 'subject'), line.split('\t', 2))) for line in log.splitlines()]
            write_json(stage / 'appendices/commits.json', {'range': old + '..' + sha, 'old_is_ancestor': ancestor, 'commits': commits})
            write_json(stage / 'appendices/evidence-status.json', evidence_diff(repo, previous_report, old, sha))
        if out.exists():
            raise ValueError('Output appeared while preparing snapshot')
        stage.rename(out)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True); raise
    print(json.dumps({'report': str(out), 'status': 'prepared', 'mode': mode, 'sha': sha,
                      'tracked_files': len(entries), 'workspace_packages': len(rows)}, ensure_ascii=False, indent=2))


def command_evidence_diff(args):
    report, old, _ = load_previous(args.previous); sha = resolve_commit(args.repo, args.target)
    if Path(args.out).exists():
        raise ValueError('Refusing to overwrite evidence review candidates')
    result = evidence_diff(args.repo, report, old, sha); write_json(args.out, result)
    print(json.dumps({'out': args.out, 'statuses': dict(collections.Counter(r['status'] for r in result['records'].values()))}, ensure_ascii=False, indent=2))


def check_report(repo, report, final=False):
    repo = Path(repo).resolve(); report = Path(report).resolve(); errors = []; notes = []
    baseline = json_read(report / 'appendices/baseline.json'); sha = baseline['sha']; entries = tree(repo, resolve_commit(repo, sha))
    previous_sha = baseline.get('previous_sha'); repo_url = baseline.get('repository', DEFAULT_REMOTE).rstrip('/')
    for name in REQUIRED:
        if not (report / name).is_file():
            errors.append('Missing artifact: ' + name)
    evidence = json_read(report / 'appendices/evidence.json')
    run_file = report / 'validation/runs.json'
    run_records = json_read(run_file) if run_file.is_file() else []
    runs_by_id = {r.get('id'): r for r in run_records}
    for key, e in evidence.items():
        try:
            if e.get('path'):
                lines = source(repo, entries, e['path']).splitlines(); a, b = e['start'], e['end']
                if not (isinstance(a, int) and isinstance(b, int) and 0 < a <= b <= len(lines)):
                    raise ValueError('Out of range')
                if e.get('snippet_hash') and e['snippet_hash'] != snippet_hash(lines[a - 1:b]):
                    raise ValueError('Snippet hash mismatch')
            elif e.get('category') in {'源码事实', '官方说明'}:
                raise ValueError('Source/document evidence requires a pinned source anchor')
            if final and e.get('category') == '运行验证':
                if not e.get('run_ids') or any(i not in runs_by_id for i in e['run_ids']):
                    raise ValueError('Runtime evidence requires current validation run IDs')
            if final and e.get('category') in {'分析推断', '改造建议'}:
                if not e.get('premise') or not e.get('based_on') or any(i not in evidence or i == key for i in e['based_on']):
                    raise ValueError('Inference/advice requires premises and other evidence IDs')
            if final and (e.get('sha') != sha or e.get('review_status') != 'reviewed'):
                raise ValueError('Evidence is not reviewed at current SHA')
            if final and e.get('category') not in CATEGORIES:
                raise ValueError('Unknown evidence category')
        except (ValueError, KeyError, TypeError) as exc:
            errors.append('Evidence %s: %s' % (key, exc))
    links = source_links = 0; markdown = sorted(report.rglob('*.md'))
    for file in markdown:
        rel = file.relative_to(report).as_posix(); text = file.read_text(encoding='utf-8')
        if '{{E' in text or re.search(r'^\s*\[TODO:[^\n]*\]\s*$', text, re.M):
            errors.append('Unfinished artifact: ' + rel)
        for href in re.findall(r'\[[^\]\n]+\]\((<[^>]+>|[^)\s]+)\)', text):
            href = href.strip('<>'); links += 1
            if href.startswith(repo_url + '/blob/'):
                source_links += 1
                path_and_sha = href[len(repo_url + '/blob/'):]; linked_sha, _, path_and_range = path_and_sha.partition('/')
                path, _, fragment = path_and_range.partition('#'); path = unquote(path)
                historical = rel == 'appendices/delta.md' and linked_sha == previous_sha
                if linked_sha != sha and not historical:
                    errors.append('Non-current source link in %s: %s' % (rel, linked_sha)); continue
                try:
                    linked_tree = tree(repo, linked_sha) if historical else entries
                    lines = source(repo, linked_tree, path).splitlines()
                    if fragment:
                        m = re.fullmatch(r'L(\d+)(?:-L(\d+))?', fragment)
                        if not m or not 0 < int(m[1]) <= int(m[2] or m[1]) <= len(lines):
                            raise ValueError('Invalid line range')
                except ValueError as exc:
                    errors.append('Source link in %s: %s' % (rel, exc))
            elif not urlparse(href).scheme and not href.startswith('#'):
                destination = (file.parent / unquote(href.split('#')[0])).resolve()
                if not destination.exists():
                    errors.append('Missing local link in %s: %s' % (rel, href))
    inventory = json_read(report / 'appendices/workspace-inventory.json')
    coverage_path = report / 'appendices/coverage.json'
    if coverage_path.exists():
        coverage = json_read(coverage_path)
        if {r['path'] for r in inventory} != {r['path'] for r in coverage} or len(coverage) != len(inventory):
            errors.append('Workspace coverage mismatch / duplicate rows')
    elif final:
        errors.append('Missing coverage.json')
    if baseline.get('workspace_packages') != len(inventory):
        errors.append('Baseline workspace count mismatch')
    if final:
        if not evidence:
            errors.append('Empty evidence ledger')
        state = json_read(report / 'research-state.json')
        if state.get('sha') != sha:
            errors.append('Research-state SHA mismatch')
        if state.get('previous_sha') != previous_sha:
            errors.append('Previous SHA mismatch')
        if previous_sha:
            for name in ('appendices/delta.md', 'appendices/claims.json'):
                if not (report / name).is_file():
                    errors.append('Missing sync artifact: ' + name)
        claims_path = report / 'appendices/claims.json'
        if claims_path.exists():
            for claim in json_read(claims_path):
                if claim.get('reviewed_at_sha') != sha or claim.get('status') not in {'new', 'modified', 'retained', 'removed', 'uncertain'}:
                    errors.append('Claim not classified at target: ' + str(claim.get('id')))
                if claim.get('status') != 'uncertain' and not claim.get('evidence_ids'):
                    errors.append('Claim lacks evidence IDs: ' + str(claim.get('id')))
                if any(k not in evidence for k in claim.get('evidence_ids', [])):
                    errors.append('Unknown claim evidence ID: ' + str(claim.get('id')))
        validation_file = report / 'validation/runs.json'
        if not validation_file.is_file():
            errors.append('Missing current-SHA validation ledger')
        else:
            records = json_read(validation_file)
            if not records:
                errors.append('Empty validation ledger')
            for r in records:
                if r.get('sha') != sha:
                    errors.append('Validation belongs to another SHA: ' + str(r.get('id')))
                if r.get('outcome') not in {'passed', 'failed', 'blocked', 'skipped'}:
                    errors.append('Missing validation outcome: ' + str(r.get('id')))
                if not r.get('command') or not r.get('scope') or not r.get('log_path'):
                    errors.append('Incomplete validation provenance: ' + str(r.get('id')))
                elif not (report / r['log_path']).is_file():
                    errors.append('Missing validation log: ' + r['log_path'])
                if r.get('outcome') == 'passed' and r.get('exit_code') != 0:
                    errors.append('Passed run has nonzero/missing exit code: ' + str(r.get('id')))
            purposes = {p for r in records if r.get('outcome') == 'passed' for p in r.get('purposes', [])}
            if not {'normal-loop', 'abnormal-or-cancel'} <= purposes:
                notes.append('Complete normal and abnormal/cancel runtime validation missing; explicitly mark delivery limited.')
        example_paths = sorted((report / 'examples').glob('*/index.*')) if (report / 'examples').is_dir() else []
        if len({p.parent for p in example_paths}) < 2:
            errors.append('Fewer than two standalone extension examples; document migrated replacements or limits before completion')
    if git(repo, 'status', '--porcelain', '--untracked-files=no').stdout or resolve_commit(repo, 'HEAD') != sha:
        notes.append('Working checkout differs from pinned commit; object citations checked, runtime provenance requires separate review.')
    notes.append('Checks are structural, not semantic. Only inline Markdown links are parsed; internal heading anchors and HTTP availability are not tested. Mermaid requires separate parser execution.')
    return {'ok': not errors, 'sha': sha, 'final_mode': final, 'evidence_records': len(evidence),
            'workspace_members': len(inventory), 'markdown_files': len(markdown), 'inline_links': links,
            'source_links': source_links, 'errors': errors, 'limits': notes}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('resolve'); p.add_argument('--remote', default=DEFAULT_REMOTE); p.add_argument('--ref'); p.add_argument('--out'); p.set_defaults(handler=command_resolve)
    p = sub.add_parser('snapshot'); p.add_argument('--repo', required=True); p.add_argument('--target', default='HEAD'); p.add_argument('--out', required=True)
    p.add_argument('--previous'); p.add_argument('--resolution'); p.add_argument('--workspace-list'); p.add_argument('--repo-url', default=DEFAULT_REMOTE); p.set_defaults(handler=command_snapshot)
    p = sub.add_parser('evidence-diff'); p.add_argument('--repo', required=True); p.add_argument('--previous', required=True); p.add_argument('--target', default='HEAD'); p.add_argument('--out', required=True); p.set_defaults(handler=command_evidence_diff)
    p = sub.add_parser('check'); p.add_argument('--repo', required=True); p.add_argument('--report', required=True); p.add_argument('--final', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'check':
            result = check_report(args.repo, args.report, args.final); print(json.dumps(result, ensure_ascii=False, indent=2)); return 0 if result['ok'] else 1
        args.handler(args); return 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        print('ERROR: ' + str(error), file=sys.stderr); return 2


if __name__ == '__main__':
    sys.exit(main())
