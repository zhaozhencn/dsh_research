"""Render the fixed-SHA supplementary article diagrams from their authored plans."""
from pathlib import Path
from html import escape
import importlib.util
import json
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('column_canvas',Path(__file__).with_name('build-config-startup-assets.py'))
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

def render(fig,sha,number):
    c=module.Canvas(1400)
    c.xml.extend([f'<title>{escape(fig["title"])}</title>',f'<desc>{escape(fig["note"])}</desc>'])
    c.text(600,28,f'{number:02d} / DSH 二次开发源码研究',30,color='#61758a')
    c.wrapped(600,92,fig['title'],1080,40,'#16324e')
    if fig['kind']=='sequence':
        for i,(title,detail) in enumerate(fig['nodes']):
            y=218+i*233
            c.panel(110,y,980,180,title,detail,title_size=36)
            c.text(65,y+55,str(i+1),32,width=55)
            if i<3: c.line(600,y+183,600,y+228,True)
    else:
        c.text(600,175,'对象与边界对照 · 以下节点不表示顺序执行',28,color='#70859b')
        for i,(title,detail) in enumerate(fig['nodes']):
            y=243+i*227
            c.panel(85,y,1030,184,title,detail,fill=['#e7eff9','#eef7f2','#eef4fc','#fff6ed'][i],title_size=36)
    c.save(fig,sha)

def main():
    diagrams=[]
    for path in sorted((ROOT/'validation/supplementary-article-plans').glob('*.json')):
        data=json.loads(path.read_text()); number=int(path.name[:2])
        for fig in data['figure_plan']:
            render(fig,data['source_baseline']['full_sha'],number); diagrams.append(fig)
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'articles/assets/supplementary-diagrams.json').write_text(json.dumps({'source_sha':data['source_baseline']['full_sha'],'figures':diagrams},ensure_ascii=False,indent=2)+'\n')
    print(f'{len(diagrams)} PNG/SVG pairs rendered')
if __name__=='__main__': main()
