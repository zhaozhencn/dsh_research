"""Verify protected historical files and report final artifacts without changing them."""
from pathlib import Path
import hashlib
import json
import sys

report = Path(__file__).resolve().parents[1]
root = report.parents[3]
before = json.loads((report / 'validation/protected-before.json').read_text())
allowed = {
    'research/deepseek-harness/articles/README.md',
    'research/deepseek-harness/examples/README.md',
    'research/deepseek-harness/validation/check-artifacts.mjs',
}
changed = [name for name, digest in before.items()
           if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest]
unexpected = sorted(set(changed) - allowed)
result = {'checked': len(before), 'changed': changed, 'allowed': sorted(allowed),
          'unexpected': unexpected, 'ok': not unexpected}
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(1 if unexpected else 0)
