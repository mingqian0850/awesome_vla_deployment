#!/usr/bin/env python3
"""Build paired learner indexes, resource catalogs and troubleshooting pages.

Source: data/*.yaml and templates/README.{head,foot}[.en].md.
Editorial records are deliberately outside the publishing inputs.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
LANGS = ('zh', 'en')
LABELS = {
 'en': {'resources':'Resource catalog','trouble':'Troubleshooting','contents':'Contents',
        'source':'Additional sources','note':'Use conditions','cause':'Possible cause',
        'test':'Check','fix':'Action','home':'Home','entries':'resources',
        'production':'hardware use reported','research':'research','toy':'demo','abandoned':'archived reference'},
 'zh': {'resources':'资源目录','trouble':'排错手册','contents':'目录',
        'source':'补充来源','note':'使用条件','cause':'可能原因',
        'test':'检查','fix':'处理','home':'首页','entries':'条资源',
        'production':'有真机使用记录','research':'研究阶段','toy':'演示阶段','abandoned':'历史参考'},
}
TYPES = dict(repo='代码仓库',dataset='数据集',paper='论文',tool='工具',docs='文档',
             blog='技术文章',video='视频',discussion='讨论记录',standard='标准资料',
             list='资料索引',benchmark='测量或基准',gap='资料缺口')

def local(obj, key, lang):
    value = obj.get(key if lang == 'en' else key + '_zh')
    if not isinstance(value,str) or not value.strip():
        raise ValueError(f"Missing {lang} field {key}: {obj.get('id', obj.get('section', '?'))}")
    return ' '.join(value.split())

def load():
    docs=[];ids=set()
    for path in sorted((ROOT/'data').glob('*.yaml')):
        d=yaml.safe_load(path.read_text())
        if path.name=='link-exceptions.yaml':continue
        if not isinstance(d,dict) or 'section' not in d:raise ValueError(f'Invalid data file: {path}')
        d['_slug']=path.stem
        for lang in LANGS:
            local(d,'section',lang);local(d,'description',lang)
        for e in d.get('entries',[]):
            if e['id'] in ids:raise ValueError(f"Duplicate ID: {e['id']}")
            ids.add(e['id'])
            if 'why' in e:raise ValueError('Selection rationale belongs in editorial/')
            for lang in LANGS:
                local(e,'what',lang)
                if 'notes' in e or 'notes_zh' in e:local(e,'notes',lang)
        for s in d.get('symptoms',[]):
            for lang in LANGS:
                local(s,'symptom',lang)
                for c in s['causes']:
                    for key in ('cause','test','fix'):local(c,key,lang)
        docs.append(d)
    return sorted(docs,key=lambda d:d.get('order',999))

def nav(page,lang):
    if lang=='zh':return f'[首页](../../README.md) · [English](../{page}.md)'
    return f'[Home](../README.en.md) · [中文](zh/{page}.md)'

def build_catalog(docs,lang):
    L=LABELS[lang]
    out=[f"# {L['resources']}",'',nav('resources',lang),'']
    out += [('Descriptions refer to the linked sources and recorded versions. A research result is not an independently reproduced deployment.' if lang=='en' else '条目描述对应所链接来源及其记录版本。研究结果不等于已独立复现的部署方案。'),'']
    out += [f"## {L['contents']}",'']
    for d in docs:
        if d.get('entries'):out.append(f"- [{local(d,'section',lang)}](#{d['_slug']})")
    out.append('')
    for d in docs:
        if not d.get('entries'):continue
        out += [f'<a id="{d["_slug"]}"></a>',f"## {local(d,'section',lang)}",'',local(d,'description',lang),'']
        for e in d['entries']:
            title=e['name'];url=e.get('url');title=f'[{title}]({url})' if url else title
            meta=[TYPES.get(e['type'],e['type']) if lang=='zh' else e['type'],L.get(e['maturity'],e['maturity'])]
            if e.get('license'):meta.append(e['license'])
            out += [f'<a id="{e["id"]}"></a>',f'### {title}','', ' · '.join(meta),'',local(e,'what',lang),'']
            if e.get('notes'):out += [f"**{L['note']}：** {local(e,'notes',lang)}",'']
            if e.get('sources'):out += [f"{L['source']}: "+' · '.join(f'[↗ {i}]({u})' for i,u in enumerate(e['sources'],1)),'']
    return '\n'.join(out).rstrip()+'\n'

def build_troubleshooting(docs,lang):
    L=LABELS[lang];d=next(d for d in docs if d.get('symptoms'))
    out=[f"# {L['trouble']}",'',nav('troubleshooting',lang),'',local(d,'description',lang),'']
    for s in d['symptoms']:out.append(f"- [{local(s,'symptom',lang)}](#{s['id']})")
    out.append('')
    for s in d['symptoms']:
        out += [f'<a id="{s["id"]}"></a>',f"## {local(s,'symptom',lang)}",'']
        for i,c in enumerate(s['causes'],1):
            out += [f"### {i}. {local(c,'cause',lang)}",'',f"- **{L['test']}：** {local(c,'test',lang)}",f"- **{L['fix']}：** {local(c,'fix',lang)}"]
            if c.get('sources'):out.append(f"- **{L['source']}：** "+' · '.join(f'[↗ {j}]({u})' for j,u in enumerate(c['sources'],1)))
            out.append('')
        if s.get('sources'):out += [L['source']+': '+' · '.join(f'[↗ {j}]({u})' for j,u in enumerate(s['sources'],1)),'']
    return '\n'.join(out).rstrip()+'\n'

def outputs(docs):
    total=sum(len(d.get('entries',[])) for d in docs)
    result={}
    for lang in LANGS:
        suffix='' if lang=='zh' else '.en'
        head=(ROOT/'templates'/f'README.head{suffix}.md').read_text()
        foot=(ROOT/'templates'/f'README.foot{suffix}.md').read_text()
        result[f'README{suffix}.md']=(head.rstrip()+'\n\n'+foot.rstrip()+'\n').replace('{{TOTAL}}',str(total))
        folder='docs/zh' if lang=='zh' else 'docs'
        result[f'{folder}/resources.md']=build_catalog(docs,lang)
        result[f'{folder}/troubleshooting.md']=build_troubleshooting(docs,lang)
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    try: rendered=outputs(load())
    except (ValueError,KeyError) as e:print(str(e),file=sys.stderr);return 1
    stale=[]
    for name,text in rendered.items():
        p=ROOT/name
        if args.check:
            if not p.exists() or p.read_text()!=text:stale.append(name)
        else:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    if stale:print('Generated files out of date: '+', '.join(stale),file=sys.stderr);return 1
    print(f'{len(rendered)} bilingual generated pages '+('are up to date.' if args.check else 'written.'))
    return 0

if __name__=='__main__':sys.exit(main())
