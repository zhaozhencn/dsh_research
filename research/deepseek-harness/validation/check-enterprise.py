#!/usr/bin/env python3
"""Verify enterprise reference provenance and artifacts, not production readiness."""
import hashlib
import json
import pathlib
import re
import subprocess

root = pathlib.Path(__file__).resolve().parents[1]
repo = root.parents[1] / '.sources/deepseek-harness'
sha = '5badb15009ae1756c3afe0ae0cef1faafc290ccc'
errors = []
manifest = json.loads((root / 'validation/enterprise-runs.json').read_text())
anchors = json.loads((root / 'validation/enterprise-source-anchors.json').read_text())
article = (root / '04-enterprise-harness-practices.md').read_text()
actual_urls = set(re.findall(r'https://github.com/deepseek-ai/deepseek-harness/blob/' + sha + r'/[^)\s]+', article))
if actual_urls != {entry['url'] for entry in anchors['anchors']}:
    errors.append('Source URLs differ from reviewed supplemental anchor manifest')
for entry in anchors['anchors']:
    source = subprocess.check_output(['git', 'show', sha + ':' + entry['path']], cwd=repo, text=True)
    excerpt = '\n'.join(source.splitlines()[entry['start'] - 1:entry['end']])
    if hashlib.sha256(excerpt.encode()).hexdigest() != entry['snippet_hash']:
        errors.append('Source excerpt hash: ' + entry['path'])
for relative, digest in manifest['example_sha256'].items():
    if hashlib.sha256((root / relative).read_bytes()).hexdigest() != digest:
        errors.append('Example artifact hash: ' + relative)
for run in manifest['runs']:
    if not (root / run['log_path']).is_file():
        errors.append('Missing run log: ' + run['id'])
    if run['sha'] != sha or (run['outcome'] == 'passed' and run['exit_code'] != 0):
        errors.append('Invalid run provenance: ' + run['id'])
result = json.loads((root / 'validation/enterprise-tests.json').read_text())
names = [case['fullName'] for file in result['testResults'] for case in file['assertionResults']]
if len(set(names)) != 16 or result['numPassedTests'] != 16 or result['numFailedTests']:
    errors.append('Expected 16 distinct passed test cases')
rows = re.findall(r'^\|(\d+)\. ', article, flags=re.M)
if rows != [str(number) for number in range(1, 17)]:
    errors.append('Enterprise concerns must cover the original 16 in order')
pkg = root / 'examples/enterprise-harness'
package = json.loads((pkg / 'package.json').read_text())
for relative in package['exports'].values():
    if not (pkg / relative).is_file():
        errors.append('Missing ESM export: ' + relative)
for file in (pkg / 'lib').glob('*.js'):
    code = file.read_text()
    if '.sources/deepseek-harness' in code:
        errors.append('Bundled checkout path: ' + file.name)
    for imported in re.findall(r"from ['\"]([^'\"]+)['\"]", code):
        if imported.startswith('.') and not (file.parent / imported).is_file():
            errors.append('Missing ESM relative import: ' + imported)
        if imported.startswith('@deepseek-ai/') and imported not in package['peerDependencies']:
            errors.append('Undeclared peer import: ' + imported)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
status = subprocess.check_output(['git', 'status', '--short'], cwd=repo, text=True).strip()
if head != sha or status:
    errors.append('Source checkout changed')
checked = dict(ok=not errors, sha=sha, concerns=16, distinct_tests=len(set(names)),
               supplemental_source_anchors=len(anchors['anchors']),
               example_files=len(manifest['example_sha256']), source_checkout_clean=not status,
               errors=errors, limits='Structural, provenance and ESM reference checks only; no new runtime execution or production certification.')
(root / 'validation/enterprise-check.json').write_text(json.dumps(checked, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(checked, ensure_ascii=False, indent=2))
raise SystemExit(0 if checked['ok'] else 1)
