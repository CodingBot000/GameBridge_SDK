#!/usr/bin/env python3
"""Require stable, unique Unity metadata for SDK package assets."""
import argparse
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parent.parent

def check(root):
    errors=[];guids={}
    if not root.is_dir(): return ['package directory missing']
    for asset in root.rglob('*'):
        if asset.name.endswith('.meta') or asset==root/'Samples~': continue
        meta=asset.with_name(asset.name+'.meta')
        if not meta.is_file(): errors.append('missing metadata: '+asset.relative_to(root).as_posix());continue
        try: text=meta.read_text(encoding='utf-8')
        except (OSError,UnicodeError): errors.append('unreadable metadata');continue
        found=re.findall(r'^guid: ([0-9a-f]{32})$',text,re.M)
        if len(found)!=1: errors.append('invalid GUID: '+meta.relative_to(root).as_posix());continue
        if asset.is_dir() and not re.search(r'^folderAsset: yes$',text,re.M): errors.append('folder metadata mismatch: '+meta.relative_to(root).as_posix())
        if found[0] in guids: errors.append('duplicate GUID: '+meta.relative_to(root).as_posix())
        guids[found[0]]=meta
    for meta in root.rglob('*.meta'):
        if not meta.with_name(meta.name[:-5]).exists(): errors.append('orphan metadata: '+meta.relative_to(root).as_posix())
    return errors

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT/'unity/Packages/com.gamebridge.sdk');args=parser.parse_args()
    errors=check(args.root)
    if errors:
        for error in errors: print(error,file=sys.stderr)
        return 1
    print('Unity package metadata PASS: complete and unique GUIDs; import validation is separate.')
    return 0
if __name__=='__main__':raise SystemExit(main())
