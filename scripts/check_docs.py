#!/usr/bin/env python3
"""Validate learner navigation, language pairs and editorial separation."""
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit
import yaml
from build_readme import ROOT, load


def anchors(text):
    result=set(re.findall(r'<a\s+id="([^"]+)"',text));counts={}
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$',text,re.M):
        heading=re.sub(r'\[([^]]+)\]\([^)]*\)',r'\1',heading).lower().replace(' ','-')
        slug=''.join(c for c in heading if c in '-_' or unicodedata.category(c)[0] in 'LN')
        n=counts.get(slug,0);counts[slug]=n+1
        result.add(slug+(f'-{n}' if n else ''))
    return result


def check():
    errors=[];docs=load()
    pages=[ROOT/'README.md',ROOT/'README.en.md']
    pairs=[]
    for folder in ('docs','checklists'):
        for en in sorted((ROOT/folder).glob('*.md')):
            zh=en.parent/'zh'/en.name;pairs.append((en,zh));pages += [en,zh]
            if not zh.exists():errors.append(f'Missing translation: {zh.relative_to(ROOT)}')
        expected={zh for _,zh in pairs if zh.parent==ROOT/folder/'zh'}
        for zh in (ROOT/folder/'zh').glob('*.md'):
            if zh not in expected:errors.append(f'Chinese page without English pair: {zh.relative_to(ROOT)}')
    for en,zh in pairs:
        if not zh.exists():continue
        e,z=en.read_text(),zh.read_text()
        for page,peer,text in ((en,zh,e),(zh,en,z)):
            links=re.findall(r'\]\(([^)]+)\)',text)
            if not any((page.parent/unquote(u.split('#')[0])).resolve()==peer.resolve() for u in links if not urlsplit(u).scheme):
                errors.append(f'Missing language switch: {page.relative_to(ROOT)}')
        if len(re.findall(r'^#{1,6} ',e,re.M))!=len(re.findall(r'^#{1,6} ',z,re.M)):
            errors.append(f'Heading-count mismatch: {en.name}')
        if len(re.findall(r'^- \[ \]',e,re.M))!=len(re.findall(r'^- \[ \]',z,re.M)):
            errors.append(f'Checklist-item mismatch: {en.name}')
    for page in pages:
        if not page.exists():continue
        text=page.read_text()
        if re.search(r'editorial/|Why it matters here|选材理由|archive-2026-10-12',text):
            errors.append(f'Editorial content leaked into {page.relative_to(ROOT)}')
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if urlsplit(target).scheme:continue
            path,_,fragment=unquote(target).partition('#')
            dest=(page.parent/path).resolve() if path else page
            if not dest.exists():errors.append(f'{page.relative_to(ROOT)}: missing {target}');continue
            if fragment and dest.suffix=='.md' and fragment not in anchors(dest.read_text()):
                errors.append(f'{page.relative_to(ROOT)}: missing anchor {target}')
    current={e['id'] for d in docs for e in d.get('entries',[])}
    old=set()
    for p in (ROOT/'editorial/archive-2026-10-12/data').glob('*.yaml'):
        d=yaml.safe_load(p.read_text())
        if isinstance(d,dict):old.update(e['id'] for e in d.get('entries',[]))
    record=yaml.safe_load((ROOT/'editorial/curation-record.yaml').read_text())
    archived=set(record['archived_entry_ids'])
    if current & archived:errors.append('A resource is both current and archived')
    if not old <= current | archived:errors.append('Original resource IDs were lost without an archive record')
    for lang,folder in [('en','docs'),('zh','docs/zh')]:
        text=(ROOT/folder/'resources.md').read_text()
        for id in current:
            if text.count(f'<a id="{id}"></a>')!=1:errors.append(f'{lang}: missing or duplicate resource {id}')
        text=(ROOT/folder/'troubleshooting.md').read_text()
        for d in docs:
            for s in d.get('symptoms',[]):
                if text.count(f'<a id="{s["id"]}"></a>')!=1:errors.append(f'{lang}: missing symptom {s["id"]}')
    return errors,len(pages),len(current),len(archived)


if __name__=='__main__':
    try:errors,n,current,archived=check()
    except (ValueError,KeyError) as e:print(e,file=sys.stderr);sys.exit(1)
    for e in errors:print(e,file=sys.stderr)
    if errors:sys.exit(1)
    print(f'{n} learner pages checked; {current} paired resources; {archived} editorial records preserved; links and language pairs valid.')
