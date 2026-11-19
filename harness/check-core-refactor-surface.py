#!/usr/bin/env python3
"""Source/API baseline for the explicitly scoped private managed refactor."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'contracts/baseline/p10-core-batch26.json'
TARGET='unity/Packages/com.gamebridge.sdk/Runtime/Core/RequestRegistry.cs'


def snapshot():
    files={}
    roots=[ROOT/'android/sdk-core/src/main',ROOT/'android/sdk-android/src/main',ROOT/'android/sdk-unity-bridge/src/main',ROOT/'ios/Sources',ROOT/'ios/UnityBridge',ROOT/'ios/Framework/include',ROOT/'unity/Packages/com.gamebridge.sdk/Runtime']
    for directory in roots:
        for p in sorted(directory.rglob('*')):
            if p.suffix not in ('.kt','.swift','.h','.cs'):continue
            data=p.read_bytes();item={'sha256':hashlib.sha256(data).hexdigest()}
            if p.suffix=='.cs':item['declarations']=[re.sub(r'\s+',' ',line.strip()) for line in data.decode().splitlines() if re.match(r'^\s*(?:public|internal|protected)\s+',line)]
            files[p.relative_to(ROOT).as_posix()]=item
    for name in ('bridge.schema.json','models.schema.json','error-codes.json','public-api.md'):
        p=ROOT/'contracts'/name;files[p.relative_to(ROOT).as_posix()]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    exports=[]
    for p in (ROOT/'ios/UnityBridge').rglob('*.swift'):exports+=re.findall(r'@_cdecl\("([^"]+)"\)',p.read_text())
    return {'files':files,'unavailable':['contracts/openapi.yaml (not present in existing repository)'],'swiftCExports':sorted(exports),'privateRefactorTarget':TARGET}


def check(before,after):
    errors=[]
    if set(before['files'])!=set(after['files']):errors.append('shipping file set changed')
    for name,item in before['files'].items():
        other=after['files'].get(name,{})
        if name==TARGET:
            if item.get('declarations')!=other.get('declarations'):errors.append('managed declaration changed: '+name)
        elif item!=other:errors.append('unscoped shipping source/wire changed: '+name)
    if before['swiftCExports']!=after['swiftCExports']:errors.append('Swift C export names changed')
    return errors


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');args=parser.parse_args()
    data=snapshot()
    if args.record:
        if BASE.exists():raise SystemExit('Existing refactor baseline preserved')
        data['sourceHead']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        BASE.write_text(json.dumps(data,indent=2)+'\n');print('Recorded Core API/source/wire baseline:',len(data['files']),'files');return 0
    errors=check(json.loads(BASE.read_text()),data)
    for error in errors:print(error)
    if not errors:print('Core refactor API/source/wire baseline PASS; binary ABI is separately verified')
    return 1 if errors else 0

if __name__=='__main__':raise SystemExit(main())
