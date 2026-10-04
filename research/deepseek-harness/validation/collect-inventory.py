#!/usr/bin/env python3
"""Regenerate baseline inventory from tracked files and pnpm-workspace.yaml globs (no checkout mutation)."""
from pathlib import Path
import json,subprocess,sys,fnmatch,collections
here=Path(__file__).resolve().parent
repo=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else here.parents[2]/'.sources/deepseek-harness'
out=here.parent/'appendices'
files=subprocess.check_output(['git','ls-files'],cwd=repo,text=True).splitlines()
patterns=['vendor/*','packages/*/*','native/system','native/system/packages/*','apps/*','benchmarks','website','python/sdk-runtime']
def ismember(d):
 return any(len(d.split('/'))==len(p.split('/')) and fnmatch.fnmatchcase(d,p) for p in patterns)
rows=[]
for file in files:
 if not file.endswith('/package.json') or not ismember(file[:-13]): continue
 d=file[:-13];m=json.loads((repo/file).read_text())
 rows.append(dict(path=d,name=m['name'],version=m.get('version'),description=m.get('description',''),private=m.get('private',False),dsh=m.get('dsh'),deps={k:m[k] for k in ['dependencies','peerDependencies','devDependencies','optionalDependencies'] if k in m},files=[f for f in files if f.startswith(d+'/')]))
rows.sort(key=lambda x:x['path'])
(out/'workspace-inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(out/'tracked-files.txt').write_text('\n'.join(files)+'\n')
names={x['name']:x['path'] for x in rows}
edges=[]
for row in rows:
 for mode,deps in row['deps'].items():
  for name,version in deps.items():
   if name in names:edges.append(dict(source=row['path'],target=names[name],kind=mode,range=version))
(out/'dependency-graph.json').write_text(json.dumps({'note':'Manifest dependencies, NOT event, service or runtime import graph','nodes':[{k:r[k] for k in ['path','name','version']} for r in rows],'edges':edges},ensure_ascii=False,indent=2)+'\n')
b=json.loads((out/'baseline.json').read_text());b.update(workspace_packages=len(rows),pnpm_projects_including_root=len(rows)+1);(out/'baseline.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'tracked_files':len(files),'workspace_members':len(rows),'manifest_edges':len(edges)}))
