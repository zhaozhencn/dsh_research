"""Validate supplementary article evidence and assets; this is not semantic review."""
from pathlib import Path
from urllib.parse import unquote
import hashlib
import json
import re
import subprocess
import textwrap
import xml.etree.ElementTree as ET

from PIL import Image

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
SOURCE = ROOT / '.sources/deepseek-harness'
MANIFEST = BASE / 'validation/supplementary-articles-manifest.json'
RESULT = BASE / 'validation/supplementary-articles-check.json'


def digest(value):
    return hashlib.sha256(value).hexdigest()


def main():
    manifest = json.loads(MANIFEST.read_text())
    sha = manifest['source_sha']
    failures = []
    rows = []
    cache = {}
    link_count = 0
    outline_text = (BASE / 'appendices/supplementary-article-outlines.md').read_text()
    outline_chunks = re.split(r'^### (\d+)\. .*$', outline_text, flags=re.M)
    outline_headings = {
        int(outline_chunks[i]): re.findall(r'^\d+\. \*\*(.*?)。\*\*', outline_chunks[i + 1], re.M)
        for i in range(1, len(outline_chunks), 2)
    }

    def require(condition, message):
        if not condition:
            failures.append(message)

    require(len(manifest['articles']) == 12, 'Expected twelve supplementary articles')
    require([a['number'] for a in manifest['articles']] == list(range(17, 29)), 'Article order')
    head = subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip()
    clean = not subprocess.check_output(['git', '-C', str(SOURCE), 'status', '--short'], text=True).strip()
    require(head == sha and clean, 'Pinned source checkout must be clean')
    protected = json.loads((BASE / manifest['protected_baseline']).read_text())
    for relative, expected in protected.items():
        path = ROOT / relative
        require(path.exists() and digest(path.read_bytes()) == expected, 'Protected file changed: ' + relative)

    for article in manifest['articles']:
        number = article['number']
        path = BASE / article['article']
        body = path.read_text()
        require(digest(path.read_bytes()) == article['sha256'], f'Article hash {number}')
        require(body.startswith(f'# {number:02d}｜{article["title"]}\n'), f'Title {number}')
        require(sha in body, f'Source baseline {number}')
        headings = re.findall(r'^## (.+)$', body, re.M)
        require(headings == article['headings'] and len(headings) == 8, f'Outline sections {number}')
        require([re.sub(r'^\d+\. ', '', h) for h in headings] == outline_headings.get(number),
                f'Original writing outline {number}')
        require(body.count('```') % 2 == 0, f'Unclosed code fence {number}')
        prose = re.sub(r'```[\s\S]*?```', '', body)
        require(not any(t in prose for t in ['代理', '回合']), f'Agent/Turn terminology {number}')
        found = re.findall(r'<!-- source:(S\d+) -->\n源码 [^\n]+\n\n```[^\n]*\n([\s\S]*?)\n```', body)
        require([s[0] for s in found] == [s['id'] for s in article['sources']], f'Excerpt identity/order {number}')
        require(len(found) >= 10, f'Source depth floor {number}')
        for record, (identity, code) in zip(article['sources'], found):
            key = record['path']
            if key not in cache:
                if key.startswith('local:'):
                    cache[key] = (ROOT / key[len('local:'):]).read_text().splitlines()
                else:
                    cache[key] = subprocess.check_output(['git', '-C', str(SOURCE), 'show', f'{sha}:{key}'], text=True).splitlines()
            lines = cache[key]
            require(1 <= record['start'] <= record['end'] <= len(lines), f'Source range {number}/{identity}')
            raw = '\n'.join(lines[record['start'] - 1:record['end']])
            require(digest(raw.encode()) == record['raw_sha256'], f'Original source hash {number}/{identity}')
            require(textwrap.dedent(raw) == code == record['code'], f'Original excerpt {number}/{identity}')
            require(digest(code.encode()) == record['code_sha256'], f'Excerpt hash {number}/{identity}')
            require(record['url'] in body, f'Excerpt attribution {number}/{identity}')
            if key.startswith('local:'):
                require(record.get('evidence_kind') == 'repository-enterprise-example', f'Local evidence classification {number}/{identity}')
            else:
                require(f'/blob/{sha}/' in record['url'], f'Pinned link {number}/{identity}')

        images = list(re.finditer(r'!\[[^\n]*\]\(assets/([^)]*)\.png\)', body))
        require(len(images) == len(article['figures']) == 4, f'Figure count {number}')
        positions = [len(re.findall(r'^## ', body[:m.start()], re.M)) for m in images]
        planned_positions = [f['position'] for f in article['figures']]
        require(positions == planned_positions, f'Planned illustration positions {number}')
        require(len(set(positions)) == 4 and positions == sorted(positions)
                and all(1 <= position <= 8 for position in positions), f'Distributed illustrations {number}')
        require([m[1] for m in images] == [f['stem'] for f in article['figures']], f'Figure order {number}')
        source_ids = {s['id'] for s in article['sources']}
        for figure in article['figures']:
            require(set(figure['source_ids']).issubset(source_ids), f'Figure evidence {figure["stem"]}')
            png = BASE / figure['png']
            svg = BASE / figure['svg']
            with Image.open(png) as im:
                require(im.format == 'PNG' and im.size == (1200, 1400), f'PNG format/dimensions {png.name}')
                im.verify()
            xml = ET.parse(svg).getroot()
            require(xml.tag.endswith('svg'), f'SVG root {svg.name}')
            require((int(xml.attrib['width']), int(xml.attrib['height'])) == (1200, 1400), f'SVG dimensions {svg.name}')
            texts = [n.text or '' for n in xml.iter() if n.tag.endswith('text')]
            # Wrapped titles may be represented by multiple text elements.
            require(figure['title'] in ''.join(texts), f'SVG title {svg.name}')
            require(figure['note'] in ''.join(texts), f'SVG caption {svg.name}')
            require(not any(t in ' '.join(texts) for t in ['代理', '回合']), f'SVG terminology {svg.name}')
            for element in xml.iter():
                if element.tag.endswith('text'):
                    require(0 <= float(element.attrib['x']) <= 1200 and 0 <= float(element.attrib['y']) <= 1400, f'SVG text origin {svg.name}')
            for kind, asset in [('png', png), ('svg', svg)]:
                require(digest(asset.read_bytes()) == figure[kind + '_sha256'], f'Asset hash {asset.name}')

        for match in re.finditer(r'!?\[[^\]\n]*\]\(([^)]+)\)', body):
            href = match[1]
            link_count += 1
            if not re.match(r'https?://|mailto:|#', href):
                require((path.parent / unquote(href.split('#')[0])).resolve().exists(), f'Missing local link {number}: {href}')
        no_links = re.sub(r'!?\[[^\]]*\]\([^)]*\)', '', prose)
        rows.append({'number': number, 'article': article['article'], 'source_excerpts': len(found),
                     'figures': len(images), 'sections': len(headings),
                     'cjk_characters_excluding_code_links': len(re.findall(r'[\u4e00-\u9fff]', no_links))})

    result = {'source_sha': sha, 'ok': not failures, 'article_count': len(rows), 'articles': rows,
              'source_excerpt_count': sum(r['source_excerpts'] for r in rows), 'png_count': 48, 'svg_count': 48,
              'checked_article_links': link_count, 'protected_file_count': len(protected),
              'source_checkout_clean': clean, 'failures': failures,
              'limits': ['Checks validate provenance, file structure and assets; they do not certify interpretation or business correctness.',
                         'Diagrams were visually reviewed separately. Source snippets are partial excerpts, not standalone programs.',
                         'Runtime evidence and its scope are recorded in supplementary-articles-validation.md.']}
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['articles', 'limits']}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
