#!/usr/bin/env python3
"""Detect missing docs, missing evidence and false counts in new disposable copies."""
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main() -> int:
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix='progress-negative-', dir=artifacts))
    def check(case, expected):
        result = subprocess.run(['python3',str(ROOT/'scripts/verify-progress.py'),'--root',str(case)],cwd=ROOT,
                                text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
        return result.returncode != 0 and expected in result.stdout
    missing = workspace/'missing-doc'; missing.mkdir()
    shutil.copytree(ROOT/'docs',missing/'docs',ignore=shutil.ignore_patterns('USER_SETUP.md'))
    if not check(missing,'document read failed'): print('Missing document was not detected'); return 1
    evidence = workspace/'missing-evidence'; evidence.mkdir(); shutil.copytree(ROOT/'docs',evidence/'docs')
    progress = evidence/'docs/PROGRESS.md'; text = progress.read_text(encoding='utf-8')
    old = 'docs/evidence/p04-t03-identity-verifier.md'
    if old not in text: print('Evidence mutation target missing'); return 1
    progress.write_text(text.replace(old,'docs/evidence/does-not-exist.md'),encoding='utf-8')
    if not check(evidence,'evidence file missing'): print('Missing evidence was not detected'); return 1
    counts = workspace/'wrong-count'; counts.mkdir(); shutil.copytree(ROOT/'docs',counts/'docs')
    progress = counts/'docs/PROGRESS.md'; text = progress.read_text(encoding='utf-8')
    changed, number = re.subn(r'(^- 구현: NOT_STARTED )\d+',r'\g<1>999',text,count=1,flags=re.M)
    if number != 1: print('Count mutation target missing'); return 1
    progress.write_text(changed,encoding='utf-8')
    if not check(counts,'declared counts differ'): print('False count was not detected'); return 1
    escaped = workspace/'escaped-evidence'; escaped.mkdir(); shutil.copytree(ROOT/'docs',escaped/'docs')
    progress = escaped/'docs/PROGRESS.md'; text = progress.read_text(encoding='utf-8')
    (escaped/'docs/evidence/escape.md').symlink_to('/etc/hosts')
    progress.write_text(text.replace(old,'docs/evidence/escape.md'),encoding='utf-8')
    if not check(escaped,'evidence file missing'): print('External evidence symlink was not detected'); return 1
    duplicate = workspace/'duplicate-count'; duplicate.mkdir(); shutil.copytree(ROOT/'docs',duplicate/'docs')
    progress = duplicate/'docs/PROGRESS.md'; text = progress.read_text(encoding='utf-8')
    changed, number = re.subn(r'(^- 구현: .+)$',r'\g<1> / NOT_STARTED 0',text,count=1,flags=re.M)
    if number != 1: print('Duplicate count mutation target missing'); return 1
    progress.write_text(changed,encoding='utf-8')
    if not check(duplicate,'declared counts differ'): print('Duplicate count was not detected'); return 1
    for name, mutation, expected in (
        ('missing-row', 'row', 'plan and ledger task IDs differ'),
        ('empty-pass', 'evidence', 'PASS requires evidence'),
        ('invalid-state', 'state', 'invalid status'),
    ):
        case=workspace/name;case.mkdir();shutil.copytree(ROOT/'docs',case/'docs')
        progress=case/'docs/PROGRESS.md';text=progress.read_text(encoding='utf-8')
        match=re.search(r'^\| P00-T01 \|[^\n]+$',text,re.M)
        if not match: print('Task mutation target missing');return 1
        if mutation=='row':changed=text[:match.start()]+text[match.end():]
        else:
            columns=match.group(0).strip('|').split('|')
            if len(columns)!=7: print('Task mutation shape invalid');return 1
            columns[5 if mutation=='evidence' else 3]=' - ' if mutation=='evidence' else ' INVALID_STATE '
            changed=text[:match.start()]+'|'+'|'.join(columns)+'|'+text[match.end():]
        progress.write_text(changed,encoding='utf-8')
        if not check(case,expected):print(name+' mutation was not detected');return 1
    print('Progress negatives PASS: missing document, evidence, task row, invalid status, external symlink and incorrect counts rejected; originals unchanged.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
