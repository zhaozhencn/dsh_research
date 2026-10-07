"""Render the configuration/startup topic using the column's PNG/SVG visual rules.

Usage: python build-config-startup-assets.py
Requires Pillow; DSH_COLUMN_FONT selects a Chinese font on other platforms.
"""
from pathlib import Path
from html import escape
import json
import os
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'articles/assets'
SPEC = ASSETS / 'config-startup-diagrams.json'
FONT = Path(os.environ.get('DSH_COLUMN_FONT', '/System/Library/Fonts/STHeiti Medium.ttc'))


class Canvas:
    def __init__(self, height):
        self.width, self.height = 1200, height
        self.image = Image.new('RGB', (self.width, height), '#f5f8fc')
        self.draw = ImageDraw.Draw(self.image)
        self.fonts = {}
        self.xml = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}">',
                    '<rect width="100%" height="100%" fill="#f5f8fc"/>']

    def font(self, size):
        if size not in self.fonts:
            self.fonts[size] = ImageFont.truetype(str(FONT), size)
        return self.fonts[size]

    def text(self, x, y, value, size=32, width=1100, color='#16324e'):
        assert self.draw.textlength(value, font=self.font(size)) <= width, (value, size, width)
        assert 0 <= y and y + size + 8 <= self.height, (value, y, self.height)
        self.draw.text((x, y), value, font=self.font(size), fill=color, anchor='mt')
        self.xml.append(f'<text x="{x}" y="{y+size}" text-anchor="middle" font-family="Heiti SC, PingFang SC, Noto Sans CJK SC, sans-serif" font-size="{size}" fill="{color}">{escape(value)}</text>')

    def wrapped(self, x, y, value, width, size=30, color='#526b85'):
        tokens = re.findall(r'[A-Za-z0-9_./<>-]+|\s+|.', value)
        while size > 26 and any(self.draw.textlength(t, font=self.font(size)) > width for t in tokens):
            size -= 1
        lines, line = [], ''
        for token in tokens:
            if line and self.draw.textlength(line + token, font=self.font(size)) > width:
                lines.append(line.rstrip())
                line = ''
            line += token if line else token.lstrip()
        if line:
            lines.append(line)
        for i, value in enumerate(lines):
            self.text(x, y + i * (size + 12), value, size, width, color)
        return y + len(lines) * (size + 12)

    def box(self, x, y, width, height, fill='#ffffff'):
        assert x >= 0 and y >= 0 and x+width <= self.width and y+height <= self.height
        self.draw.rounded_rectangle((x,y,x+width,y+height),radius=18,fill=fill,outline='#cedcea',width=2)
        self.xml.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" fill="{fill}" stroke="#cedcea" stroke-width="2"/>')

    def line(self, x1, y1, x2, y2, arrow=False):
        self.draw.line((x1,y1,x2,y2),fill='#6f8aa5',width=4)
        self.xml.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="#6f8aa5" stroke-width="4"/>')
        if arrow:
            if x1 == x2:
                points = [(x2,y2),(x2-8,y2-14),(x2+8,y2-14)]
            else:
                points = [(x2,y2),(x2-14,y2-8),(x2-14,y2+8)]
            self.draw.polygon(points,fill='#6f8aa5')
            self.xml.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+'" fill="#6f8aa5"/>')

    def header(self, fig):
        self.xml.extend([f'<title>{escape(fig["title"])}</title>',f'<desc>{escape(fig["note"])}</desc>'])
        self.text(600,28,'00 / DSH 配置与启动',30,color='#61758a')
        self.text(600,88,fig['title'],42)

    def panel(self, x, y, width, height, title, detail, fill='#ffffff', title_size=34):
        self.box(x,y,width,height,fill)
        end = self.wrapped(x+width/2,y+18,title,width-40,title_size,'#16324e')
        end = self.wrapped(x+width/2,end+12,detail,width-48,30)
        assert end <= y+height-5, (title, detail, end, y+height)

    def save(self, fig, sha):
        self.text(600,self.height-117,fig['note'],28,color='#526b85')
        self.text(600,self.height-62,f'基线 {sha[:12]} · 源码机制示意，非全量调用图',26,color='#70859b')
        self.xml.append('</svg>')
        png = ASSETS / (fig['stem']+'.png')
        svg = ASSETS / (fig['stem']+'.svg')
        self.image.save(png,dpi=(160,160),optimize=True)
        svg.write_text('\n'.join(self.xml)+'\n',encoding='utf-8')
        fig.update({'width':self.width,'height':self.height,
                    'png':'articles/assets/'+png.name,'svg':'articles/assets/'+svg.name})


def render(fig, sha):
    kind, nodes = fig['kind'], fig['nodes']
    c = Canvas({'sequence':1320,'layers':1320,'ownership':1320,'audit':1240}[kind])
    c.header(fig)
    if kind == 'sequence':
        for i,(title,detail) in enumerate(nodes):
            y = 181+i*163
            c.panel(165,y,960,135,title,detail,title_size=38)
            c.box(70,y+40,60,60,'#e4eef9')
            c.text(100,y+50,str(i+1),32,width=55)
            if i < len(nodes)-1:
                c.line(645,y+137,645,y+160,True)
    elif kind == 'layers':
        c.text(600,160,'以空 Entry 列表为根，按下列顺序执行 patch',30)
        for i,(title,detail) in enumerate(nodes):
            y = 218+i*136
            c.panel(140,y,995,124,title,detail,title_size=33)
            c.text(90,y+33,str(i+1),32,width=55)
            if i < len(nodes)-1:
                c.line(638,y+126,638,y+133,True)
        for i,(title,detail) in enumerate(fig['example']):
            y = 940+i*86
            c.box(70,y,1060,62,'#eef7f2' if i==2 else '#eef4fc')
            c.text(275,y+18,title,28,width=380)
            c.text(810,y+19,detail,26,width=590)
            if i < 2:
                c.line(600,y+64,600,y+82,True)
    elif kind == 'ownership':
        c.box(50,174,1100,328,'#e7eff9')
        c.text(600,191,nodes[0][0],38)
        c.text(600,245,nodes[0][1],30)
        c.panel(80,304,490,176,*nodes[1],title_size=34)
        c.panel(690,304,430,176,*nodes[2],title_size=34)
        c.line(575,370,687,370,True)
        c.text(631,319,'fiber',28,width=110)
        c.line(325,481,325,556,True)
        c.text(430,513,'subtree',30,width=185)
        c.box(50,562,1100,560,'#eef4fc')
        c.text(600,583,nodes[3][0],38)
        c.text(600,641,nodes[3][1],30)
        c.panel(80,714,490,176,*nodes[4],title_size=34)
        c.panel(690,714,430,176,*nodes[5],title_size=34)
        c.line(575,787,687,787,True)
        c.text(631,736,'fiber',28,width=110)
        c.panel(80,930,1040,150,*nodes[6],title_size=34)
    else:
        c.panel(70,181,1060,130,'inactiveEntries()','检查 Entry.disabled、fiber 是否存在与 Fiber.state',fill='#e7eff9',title_size=36)
        for i,(title,detail) in enumerate(nodes[:3]):
            c.panel(50+i*385,363,330,186,title,detail,fill=['#eef7f2','#eef7f2','#fff6ed'][i],title_size=35)
        c.line(985,552,985,595)
        c.line(600,595,985,595)
        c.line(600,595,600,625,True)
        c.panel(70,632,1060,134,'auditStartupEntries()',fig['decision'],title_size=35)
        for i,(title,detail) in enumerate(nodes[3:5]):
            c.panel(70+i*570,800,490,160,title,detail,fill='#fff6ed' if i==0 else '#eef7f2',title_size=32)
        c.line(315,767,315,797,True)
        c.line(885,767,885,797,True)
        c.text(368,769,'是',28,width=60)
        c.text(938,769,'否',28,width=60)
        c.panel(70,977,1060,122,*nodes[5],fill='#e7eff9',title_size=33)
    c.save(fig,sha)


def main():
    if not FONT.is_file():
        raise SystemExit('Set DSH_COLUMN_FONT to an available Chinese font.')
    spec = json.loads(SPEC.read_text(encoding='utf-8'))
    for fig in spec['figures']:
        render(fig,spec['sha'])
    SPEC.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'png':len(spec['figures']),'svg':len(spec['figures'])}))


if __name__ == '__main__':
    main()
