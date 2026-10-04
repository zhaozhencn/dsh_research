"""Render source-backed sequence, ownership and branch diagrams from explicit JSON.
Run build-column-assets.py to rebuild the complete original + supplemental set.
Set DSH_COLUMN_FONT to a Chinese font when using another platform.
"""
from pathlib import Path
from html import escape
import hashlib
import json
import os
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'articles/assets'
FONT = Path(os.environ.get('DSH_COLUMN_FONT', '/System/Library/Fonts/STHeiti Medium.ttc'))
if not FONT.is_file():
    raise SystemExit('Set DSH_COLUMN_FONT to an available Chinese font.')
spec = json.loads((ASSETS / 'diagram-supplements.json').read_text())
manifest = json.loads((ROOT / 'validation/column-manifest.json').read_text())
assert spec['sha'] == manifest['sha']
assert len(spec['figures']) == 48

class Canvas:
    def __init__(self, height):
        self.width, self.height = 1200, height
        self.image = Image.new('RGB', (1200, height), '#f5f8fc')
        self.draw = ImageDraw.Draw(self.image)
        self.fonts = {}
        self.xml = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}">',
                    '<rect width="100%" height="100%" fill="#f5f8fc"/>']
    def font(self, size):
        if size not in self.fonts:
            self.fonts[size] = ImageFont.truetype(str(FONT), size)
        return self.fonts[size]
    def width_of(self, value, size):
        return self.draw.textlength(value, font=self.font(size))
    def text(self, x, y, value, size=32, color='#16324e', max_width=1100):
        assert self.width_of(value, size) <= max_width, (value, size, max_width)
        self.draw.text((x, y), value, font=self.font(size), fill=color, anchor='mt')
        self.xml.append(f'<text x="{x}" y="{y+size}" text-anchor="middle" font-family="Heiti SC, PingFang SC, Noto Sans CJK SC, sans-serif" font-size="{size}" fill="{color}">{escape(value)}</text>')
    def wrapped(self, x, y, value, width, size=32, color='#16324e'):
        tokens = re.findall(r'[A-Za-z0-9_./=+-]+|\s+|.', value)
        # Keep source identifiers intact; reduce only when a single token needs it.
        while size > 26 and any(self.width_of(token, size) > width for token in tokens):
            size -= 1
        lines, line = [], ''
        for token in tokens:
            if line and self.width_of(line + token, size) > width:
                lines.append(line.rstrip())
                line = ''
            line += token if line else token.lstrip()
        if line:
            lines.append(line)
        for i, line in enumerate(lines):
            self.text(x, y + i * (size + 12), line, size, color, width)
        return y + len(lines) * (size + 12)
    def box(self, x, y, width, height, fill='#ffffff', stroke='#cedcea'):
        self.draw.rounded_rectangle((x, y, x+width, y+height), radius=18, fill=fill, outline=stroke, width=2)
        self.xml.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    def line(self, x1, y1, x2, y2, arrow=False):
        self.draw.line((x1, y1, x2, y2), fill='#6f8aa5', width=4)
        self.xml.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="#6f8aa5" stroke-width="4"/>')
        if arrow:
            points = [(x2,y2), (x2-8,y2-14), (x2+8,y2-14)] if x1==x2 else [(x2,y2),(x2-14,y2-8),(x2-14,y2+8)]
            self.draw.polygon(points, fill='#6f8aa5')
            self.xml.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+'" fill="#6f8aa5"/>')
    def header(self, fig):
        self.xml += [f'<title>{escape(fig["title"])}</title>', f'<desc>{escape(fig["note"])}</desc>']
        self.text(600, 28, f'{fig["article"]:02} / 从源码理解 Agent Harness', 30, '#61758a')
        self.text(600, 87, fig['title'], 46)
    def footer(self, fig, y):
        self.text(600, y, fig['note'], 30, '#526b85')
        self.text(600, y+50, '基线 5badb15009ae · 源码机制示意，非全量调用图', 28, '#70859b')
    def save(self, fig):
        self.xml.append('</svg>')
        self.image.save(ASSETS / (fig['stem']+'.png'), dpi=(160,160), optimize=True)
        (ASSETS / (fig['stem']+'.svg')).write_text('\n'.join(self.xml)+'\n')
        return {**fig, 'width':self.width, 'height':self.height,
                'png':'articles/assets/'+fig['stem']+'.png', 'svg':'articles/assets/'+fig['stem']+'.svg'}

def render(fig):
    kind, nodes = fig['kind'], fig['nodes']
    c = Canvas({'sequence':1240, 'call-tree':1240, 'layers':1060, 'branches':1140}[kind])
    c.header(fig)
    if kind == 'sequence':
        assert len(nodes) == 6
        for i, (owner, title, detail) in enumerate(nodes):
            y = 190+i*152
            c.box(350,y,770,128)
            c.text(735,y+17,title,40,max_width=710)
            bottom = c.wrapped(735,y+72,detail,700,30,'#526b85')
            assert bottom <= y+128, (fig['stem'], detail)
            c.wrapped(151,y+35,owner,210,32)
            c.box(272,y+34,56,56, '#e4eef9','#a9c2dd')
            c.text(300,y+43,str(i+1),32)
            c.line(328,y+62,350,y+62,True)
            if i < 5:
                c.line(300,y+90,300,y+186,True)
        c.footer(fig,1133)
    elif kind == 'call-tree':
        assert len(nodes) == 6
        c.box(100,185,1000,130,'#e7eff9')
        c.text(600,203,nodes[0][1],40,max_width=940)
        c.text(600,263,nodes[0][2],31,max_width=920)
        c.line(600,315,600,340)
        c.line(220,340,980,340)
        for i, (owner, title, detail) in enumerate(nodes[1:4]):
            x=55+i*380;center=x+165
            c.line(center,340,center,380,True)
            c.box(x,380,330,236)
            c.text(center,402,owner,30,max_width=290)
            c.wrapped(center,453,title,280,35)
            bottom=c.wrapped(center,541,detail,280,29,'#526b85')
            assert bottom-12 <= 616,(fig['stem'],detail)
            c.line(center,616,center,655)
        c.line(220,655,980,655)
        c.line(600,655,600,699,True)
        c.box(100,700,1000,135)
        c.text(600,718,nodes[4][1],40,max_width=940)
        c.text(600,777,nodes[4][2],31,max_width=920)
        # A proposal panel has no arrow: reservation is not an after-the-fact step.
        c.box(100,903,1000,145,'#fff6ed')
        c.text(600,918,'企业扩展建议：'+nodes[5][1],36,max_width=940)
        c.text(600,984,nodes[5][2],31,max_width=920)
        c.footer(fig,1133)
    elif kind == 'layers':
        assert len(nodes) == 4
        for i, (title, identity, boundary) in enumerate(nodes):
            y = 178+i*182
            c.box(80,y,1040,152)
            c.box(80,y,285,152,'#e7eff9','#cedcea')
            c.wrapped(222,y+40,title,245,38)
            c.text(740,y+22,identity,36,max_width=710)
            bottom=c.wrapped(740,y+82,boundary,690,31,'#526b85')
            assert bottom <= y+152,(fig['stem'], boundary)
            # Ownership layers intentionally have no arrows: no false causal chain.
        c.footer(fig,946)
    else:
        assert len(nodes) == 3
        c.box(130,175,940,110,'#e7eff9')
        c.text(600,205,'根据资格、已知事实与生命周期分别判断',36,max_width=900)
        c.line(600,285,600,312)
        c.line(220,312,980,312)
        for i, branch in enumerate(nodes):
            x=55+i*380;center=x+165
            c.line(center,312,center,352,True)
            c.box(x,352,330,630,['#eef7f2','#eef4fc','#fff6ed'][i])
            c.wrapped(center,378,branch[0],288,38)
            y=476
            for item in branch[1:]:
                bottom=c.wrapped(center,y,item,280,31)
                c.line(x+27,bottom+12,x+303,bottom+12)
                y=max(y+113,bottom+40)
            assert bottom+12 <= 982,(fig['stem'],bottom)
        c.footer(fig,1024)
    return c.save(fig)

rows=[]
for fig in spec['figures']:
    row=manifest['articles'][fig['article']-1]
    assert set(fig['source_excerpt_ids']).issubset(row['snippet_ids'])
    rows.append(render(fig))
existing=json.loads((ASSETS/'diagrams.json').read_text())
original=[fig for fig in existing['figures'] if fig['kind'] in ('flow','pairs')]
assert len(original)==16
existing['figures']=sorted(original+rows,key=lambda fig:(fig['article'],fig['stem']))
existing['supplement_renderer']='Pillow; shared SVG geometry; explicit source-linked JSON'
(ASSETS/'diagrams.json').write_text(json.dumps(existing,ensure_ascii=False,indent=2)+'\n')
# Separate sheets by mechanism allow comparison of all 16 topics at legible thumbnail size.
for kind in ('sequence','layers','branches'):
    sheet=Image.new('RGB',(2000,2800),'white')
    for i,row in enumerate(fig for fig in rows if fig['kind']==kind or (kind=='sequence' and fig['kind']=='call-tree')):
        with Image.open(ROOT/row['png']) as im:
            im.thumbnail((480,650))
            sheet.paste(im,(10+(i%4)*500,10+(i//4)*700))
    sheet.save(ROOT/'validation'/f'column-{kind}-contact-sheet.png',optimize=True)
print('Rendered 48 supplemental PNG/SVG pairs and 3 contact sheets; total 64 pairs.')
