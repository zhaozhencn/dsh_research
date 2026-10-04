"""Check article mapping, original excerpts, local/source links and publication images."""
from pathlib import Path
from urllib.parse import unquote
import json, re, hashlib, subprocess, textwrap, xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]/'.sources/deepseek-harness'
SHA='5badb15009ae1756c3afe0ae0cef1faafc290ccc'
RESULT=ROOT/'validation/column-check.json'
manifest=json.loads((ROOT/'validation/column-manifest.json').read_text())
evidence=json.loads((ROOT/'appendices/evidence.json').read_text())
figures=json.loads((ROOT/'articles/assets/diagrams.json').read_text())
structure=json.loads((ROOT/'validation/column-structure-baseline.json').read_text())
revisions=json.loads((ROOT/'validation/column-editorial-revisions.json').read_text())
supplements=json.loads((ROOT/'articles/assets/diagram-supplements.json').read_text())
concerns=re.findall(r'^## \d+\. (.*)$',(ROOT/'02-runtime-source.md').read_text(),re.M)
failures=[];rows=[];links=0;source_links=0;snippets=0;checked_images=[]

def require(condition,message):
    if not condition:failures.append(message)

require(revisions['source_sha']==SHA,'editorial revision source SHA')
require(set(revisions['articles'])=={str(n) for n in range(1,17)},'editorial revision scope')
require(manifest['sha']==SHA,'manifest SHA')
require(len(manifest['articles'])==16 and len(concerns)==16,'article / concern count')
require([row['number'] for row in manifest['articles']]==list(range(1,17)),'article reading order')
require(sorted(row['concern_number'] for row in manifest['articles'])==list(range(1,17)),'source concern coverage')
require(len(figures['figures'])==64,'figure count')
require(len(supplements['figures'])==48 and supplements['sha']==SHA,'supplement count / SHA')
for spec in supplements['figures']:
    matches=[fig for fig in figures['figures'] if fig['stem']==spec['stem']]
    require(len(matches)==1,f'supplement manifest entry {spec["stem"]}')
    if matches:
        require(all(matches[0].get(key)==value for key,value in spec.items()),f'supplement manifest differs from specification {spec["stem"]}')
require(len({fig['stem'] for fig in figures['figures']})==64,'unique figure stems')
require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()==SHA,'checkout SHA')
require(not subprocess.check_output(['git','status','--short'],cwd=REPO,text=True).strip(),'source checkout dirty')
for row in manifest['articles']:
    path=ROOT/row['file'];body=path.read_text();n=row['number']
    concern_number=row['concern_number']
    require(row['concern']==concerns[concern_number-1],f'concern mapping {n}')
    require(path.name.startswith(f'{n:02}-'),f'article filename number {n}')
    require(f'· 第 {n:02} 篇 · {row["concern"]}' in body,f'article banner number {n}')
    require(body.startswith('# '+row['title']+'\n'),f'title {n}')
    require(SHA in body,f'baseline missing {n}')
    require(hashlib.sha256(body.encode()).hexdigest()==row['sha256'],f'changed manifest hash {n}')
    require('{{' not in body,f'unexpanded marker {n}')
    require('技术心得' in body and any(word in body for word in ['不足','代价','局限','边界','约束']),f'boundaries / insights structure missing {n}')
    require(body.count('```')%2==0,f'unclosed fence {n}')
    revision=revisions['articles'].get(str(n))
    if revision:
        require(revision['previous_headings']==structure['headings'][str(concern_number)],f'editorial revision preserves historical baseline {n}')
    expected_headings=revision['headings'] if revision else structure['headings'][str(concern_number)]
    require(re.findall(r'^## .*$',body,re.M)==expected_headings,f'current section titles {n}')
    article_figures=[fig for fig in figures['figures'] if fig['article']==n]
    require(len(article_figures)==4,f'four figures per article {n}')
    image_stems=re.findall(r'!\[[^\n]*\]\(assets/([^)]*)\.png\)',body)
    require(len(image_stems)==4 and set(image_stems)==set(row['figure_stems']),f'embedded figures {n}')
    if revision:
        require(image_stems==revision['figure_order'],f'figure reading order {n}')
        positions=[len(re.findall(r'^## ',body[:match.start()],re.M)) for match in re.finditer(r'!\[[^\n]*\]\(assets/([^)]*)\.png\)',body)]
        require(positions==revision['figure_sections'],f'figure section placement {n}')
        prose=re.sub(r'```[\s\S]*?```','',body)
        require(not any(term in prose for term in ['回合','代理']),f'English Agent / Turn terminology {n}')
        require(len(re.findall(r'^## ',body,re.M))==len(revision['previous_headings']),f'preserved principal section count {n}')
    for fig in article_figures:
        require(fig['stem'] in row['figure_stems'],f'figure mapping {n}')
        require(set(fig.get('source_excerpt_ids',[])).issubset(row['snippet_ids']),f'figure source references {fig["stem"]}')
    blocks=re.findall(r'```typescript\n([\s\S]*?)\n```',body)
    require(len(blocks)==len(row['snippet_ids']) and len(blocks)>=12,f'excerpt count {n}')
    for key,block in zip(row['snippet_ids'],blocks):
        snippets+=1;v=manifest['snippets'][key]
        if v.get('local'):source=(ROOT/v['path']).read_text()
        else:source=subprocess.check_output(['git','show',f"{SHA}:{v['path']}"],cwd=REPO,text=True)
        raw='\n'.join(source.splitlines()[v['start']-1:v['end']])
        require(raw==v['raw'],f'excerpt not original {key}')
        require(textwrap.dedent(raw).rstrip()==block,f'excerpt altered {key}')
        require(hashlib.sha256(raw.encode()).hexdigest()==v['sha256'],f'excerpt hash {key}')
    for eid in row['evidence_ids']:require(eid in evidence,f'unknown evidence {n}: {eid}')
    no_code=re.sub(r'```[\s\S]*?```','',body)
    no_links=re.sub(r'!?\[[^\]]*\]\([^)]*\)','',no_code)
    rows.append({'number':n,'concern_number':concern_number,'file':row['file'],'concern':row['concern'],'code_excerpts':len(blocks),'illustrations':len(article_figures),'evidence_refs':len(row['evidence_ids']),'cjk_characters_excluding_code_links':len(re.findall(r'[\u4e00-\u9fff]',no_links))})

for path in sorted((ROOT/'articles').glob('*.md')):
    for m in re.finditer(r'!?\[[^\]\n]*\]\(([^)]+)\)',path.read_text()):
        href=m[1];links+=1
        if href.startswith('https://github.com/deepseek-ai/deepseek-harness/blob/'):
            source_links+=1
            match=re.search(r'/blob/([^/]+)/(.*?)(?:#L(\d+)(?:-L(\d+))?)?$',href)
            require(match is not None and match[1]==SHA,f'source URL: {href}')
            if match is not None:
                source=(REPO/match[2]).read_text();length=len(source.splitlines())
                if match[3]:require(0<int(match[3])<=int(match[4] or match[3])<=length,f'source range {href}')
        elif not re.match(r'https?://|mailto:|#',href):
            target=(path.parent/unquote(href.split('#')[0])).resolve()
            if target!=RESULT:require(target.exists(),f'missing link: {path.name} → {href}')

for fig in figures['figures']:
    png=ROOT/fig['png'];svg=ROOT/fig['svg']
    with Image.open(png) as im:
        require(im.size==(fig['width'],fig['height']),f'PNG dimensions {png.name}')
        require(im.format=='PNG',f'PNG format {png.name}')
        im.verify()
    node=ET.parse(svg).getroot()
    require(node.tag.endswith('svg'),f'SVG root {svg.name}')
    require(int(node.attrib['width'])==fig['width'] and int(node.attrib['height'])==fig['height'],f'SVG size {svg.name}')
    texts=[n.text or '' for n in node.iter() if n.tag.endswith('text')]
    require(fig['title'] in texts and fig['note'] in texts,f'SVG captions {svg.name}')
    require(not any(term in ' '.join(texts) for term in ['回合','代理']),f'English diagram terminology {svg.name}')
    checked_images.append({'png':fig['png'],'svg':fig['svg'],'width':fig['width'],'height':fig['height'],'ok':True})

result={'sha':SHA,'articles':rows,'article_count':len(rows),'source_excerpt_count':snippets,'checked_links':links,'checked_source_links':source_links,'figures':checked_images,'png_count':len(checked_images),'svg_count':len(checked_images),'source_checkout_clean':not subprocess.check_output(['git','status','--short'],cwd=REPO,text=True).strip(),'existing_runtime_tests':'Reused previously executed same-SHA evidence; no new behavior-test runs claimed.','checks':'16 concern mapping / explicit editorial section contract and preserved principal section count / figure order and placement for all 16 articles / English Agent and Turn terms in prose and diagrams / four embedded illustrations per article / supplemental source references / exact Git or local fixture excerpts / hashes / source SHA and ranges / local targets / fences / insights and boundaries / PNG decode / SVG XML and dimensions / checkout status','limits':['Structural checks and editorial keywords do not certify source semantics, tradeoff analysis or business correctness.','Code blocks are original partial excerpts, not standalone programs; no new typecheck claim.','Figures use standard drawing tools; no WeChat editor preview or remote publication.','Existing Mermaid parsing is checked separately by the report checker.'],'failures':failures,'ok':not failures}
RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'articles':len(rows),'excerpts':snippets,'png':len(checked_images),'svg':len(checked_images),'links':links,'ok':not failures,'failures':failures},ensure_ascii=False))
raise SystemExit(1 if failures else 0)
