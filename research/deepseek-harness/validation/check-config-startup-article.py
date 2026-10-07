"""Check fixed-commit excerpts, topic links, diagram placement and PNG/SVG assets.

Run from any directory with Python and Pillow installed. No runtime tests run here.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
from urllib.parse import unquote
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
REPORT = ROOT / 'validation/config-startup-check.json'


def digest(value):
    return hashlib.sha256(value.encode('utf-8') if isinstance(value,str) else value).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=PROJECT/'.sources/deepseek-harness')
    parser.add_argument('--protected-snapshot', type=Path)
    args = parser.parse_args()
    plan = json.loads((ROOT/'validation/config-startup-plan.json').read_text())
    figures = json.loads((ROOT/'articles/assets/config-startup-diagrams.json').read_text())
    sha = plan['source_baseline']['full_sha']
    article = PROJECT / plan['scope']['article']
    body = article.read_text()
    failures, checked_sources, checked_images = [], [], []

    def require(condition,message):
        if not condition:
            failures.append(message)

    source_cache = {}
    def source(path):
        if path not in source_cache:
            source_cache[path] = subprocess.check_output(['git','show',f'{sha}:{path}'],cwd=args.repo).decode('utf-8').splitlines()
        return source_cache[path]

    spec = importlib.util.spec_from_file_location('article_evidence',PROJECT/'skills/source-code-article-refiner/scripts/evidence_tools.py')
    evidence = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evidence)
    inventory = evidence.markdown_inventory(body)
    records = {row['id']:row for row in plan['source_excerpts']}
    blocks = re.findall(r'<!-- source:(S\d+) -->\s*```typescript\n([\s\S]*?)\n```',body)
    require(Counter(row[0] for row in blocks)==Counter(records.keys()),'source block ids')
    for eid,code in blocks:
        row = records[eid]
        excerpt = evidence.extract(args.repo,sha,row['path'],row['start'],row['end'])
        require(code==excerpt['code'],f'non-original excerpt {eid}')
        require(row['sha']==sha and row['raw_sha256']==excerpt['raw_sha256']
                and row['code_sha256']==digest(code),f'provenance {eid}')
        require(row['url'] in body,f'missing source caption {eid}')
        checked_sources.append({'id':eid,'path':row['path'],'start':row['start'],'end':row['end'],'code_sha256':digest(code)})
    require(len(inventory['steps'])==len(plan['steps'])==15,'step count')
    require(sha in body and len(sha)==40 and figures['sha']==sha,'source baseline')
    require('{{' not in body and '@@' not in body,'unresolved authoring markers')
    require(len(figures['figures'])==4,'diagram definition count')
    expected_images = ['assets/'+fig['stem']+'.png' for fig in figures['figures']]
    require(inventory['images']==expected_images,'embedded image order')
    names = ['第一步','第五步','第六步','第九步','第十步','第十二步','第十三步']
    position = {name:body.index('### '+name) for name in names}
    for fig in figures['figures']:
        require(set(fig['evidence']).issubset(records),f'diagram evidence {fig["id"]}')
        png, svg = ROOT/fig['png'], ROOT/fig['svg']
        with Image.open(png) as image:
            require(image.format=='PNG' and image.size==(fig['width'],fig['height']),f'PNG size {fig["id"]}')
            image.verify()
        node = ET.parse(svg).getroot()
        require(node.tag.endswith('svg') and int(node.attrib['width'])==fig['width']
                and int(node.attrib['height'])==fig['height'],f'SVG dimensions {fig["id"]}')
        texts = ' '.join(n.text or '' for n in node.iter() if n.tag.endswith('text'))
        require(fig['title'] in texts and fig['note'] in texts,f'SVG captions {fig["id"]}')
        require(not any(term in texts for term in ['回合','代理']),f'diagram terminology {fig["id"]}')
        image_position = body.index(expected_images[fig['id']-1])
        bounds = {1:(0,position['第一步']),2:(position['第五步'],position['第六步']),
                  3:(position['第九步'],position['第十步']),4:(position['第十二步'],position['第十三步'])}
        lo,hi = bounds[fig['id']]
        require(lo<image_position<hi,f'diagram placement {fig["id"]}')
        checked_images.append({'png':fig['png'],'svg':fig['svg'],'width':fig['width'],
                               'height':fig['height'],'png_sha256':digest(png.read_bytes()),'svg_sha256':digest(svg.read_bytes())})
    checked_links, source_links = 0, 0
    for href in re.findall(r'!?\[[^\]\n]*\]\(([^)\s]+)\)',body):
        checked_links += 1
        if href.startswith('https://github.com/deepseek-ai/deepseek-harness/blob/'):
            source_links += 1
            m = re.search(r'/blob/([^/]+)/(.*?)#L(\d+)-L(\d+)$',href)
            require(m is not None and m[1]==sha,f'source URL {href}')
            if m:
                require(1<=int(m[3])<=int(m[4])<=len(source(unquote(m[2]))),f'source range {href}')
        elif not href.startswith(('http:','https:','mailto:','#')):
            target = (article.parent/unquote(href.split('#')[0])).resolve()
            require(target.exists() or target==REPORT,f'missing local link {href}')
    protected_count = None
    if args.protected_snapshot:
        before = json.loads(args.protected_snapshot.read_text())
        protected_count = len(before)
        for path,checksum in before.items():
            file = PROJECT/path
            require(file.is_file() and digest(file.read_bytes())==checksum,f'protected file changed: {path}')
    require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=args.repo,text=True).strip()==sha,'source checkout SHA')
    require(not subprocess.check_output(['git','status','--short'],cwd=args.repo,text=True).strip(),'source checkout dirty')
    result = {'sha':sha,'article':str(article.relative_to(PROJECT)),'article_sha256':digest(body),
              'steps':len(inventory['steps']),'source_excerpt_count':len(blocks),'total_code_blocks':len(inventory['code_sha256']),
              'source_excerpts':checked_sources,'images':checked_images,'checked_links':checked_links,'source_links':source_links,
              'protected_files_checked':protected_count,'runtime_evidence':'See config-startup-runtime-tests.json; this checker does not execute runtime tests.',
              'limits':['Structure and provenance do not certify semantic quality or diagram readability.',
                        'Teaching configurations and plugin code are examples, separate from original excerpts.',
                        'No installed application, real-model, cross-platform or publishing verification.'],
              'failures':failures,'ok':not failures}
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['steps','source_excerpt_count','total_code_blocks','checked_links','protected_files_checked','failures','ok']},ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
