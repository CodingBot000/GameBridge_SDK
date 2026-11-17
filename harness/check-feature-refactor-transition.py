#!/usr/bin/env python3
"""Keep the closed Core guard intact, then lock the exact reviewed Native transition."""
import hashlib,importlib.util,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
RECORD=ROOT/'contracts/baseline/p10-feature-batch32.json'
spec=importlib.util.spec_from_file_location('closed_core_surface',ROOT/'harness/check-core-refactor-surface.py');core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
ALLOWED={
 'android/sdk-android/src/main/kotlin/com/gamebridge/android/auth/GoogleAuthProvider.kt',
 'android/sdk-android/src/main/kotlin/com/gamebridge/android/auth/StoredGoogleSessionCodec.kt',
 'ios/Sources/GameBridgeApple/AppleHttpProofSink.swift',
 'ios/Sources/GameBridgeApple/AppleGrantDecoder.swift'}
ROOTS=['android/sdk-core/src/main','android/sdk-android/src/main','android/sdk-unity-bridge/src/main','ios/Sources','ios/UnityBridge','ios/Framework/include','unity/Packages/com.gamebridge.sdk/Runtime']
CONTRACTS=['contracts/'+x for x in ('bridge.schema.json','models.schema.json','error-codes.json','public-api.md')]

def snapshot_at(ref):
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',ref,'--',*ROOTS,*CONTRACTS],cwd=ROOT,text=True).splitlines();files={};exports=[]
    for name in names:
        path=Path(name)
        if path.suffix not in ('.kt','.swift','.h','.cs') and name not in CONTRACTS:continue
        data=subprocess.check_output(['git','show',ref+':'+name],cwd=ROOT);item={'sha256':hashlib.sha256(data).hexdigest()}
        if path.suffix=='.cs':item['declarations']=[re.sub(r'\s+',' ',line.strip()) for line in data.decode().splitlines() if re.match(r'^\s*(?:public|internal|protected)\s+',line)]
        files[name]=item
        if name.startswith('ios/UnityBridge/') and path.suffix=='.swift':exports+=re.findall(r'@_cdecl\("([^"]+)"\)',data.decode())
    return dict(files=files,swiftCExports=sorted(exports))

def check_transition(before,after,record):
    errors=[];changes=record.get('changes',[])
    if not isinstance(changes,list) or len(changes)!=4 or any(not isinstance(x,dict) for x in changes):return ['exact four reviewed Native changes required']
    indexed={x.get('path'):x for x in changes}
    if set(indexed)!=ALLOWED:return ['Native transition scope changed']
    expected=set(before['files'])|ALLOWED
    if set(after['files'])!=expected:errors.append('current shipping/wire file set changed')
    for name in expected:
        old=before['files'].get(name);new=after['files'].get(name)
        if name in ALLOWED:
            item=indexed[name]
            if item.get('beforeSha256')!=(old or {}).get('sha256'):errors.append('closed preimage mismatch: '+name)
            digest=item.get('afterSha256')
            if not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest) or (new or {}).get('sha256')!=digest:errors.append('reviewed Native postimage mismatch: '+name)
        elif old!=new:errors.append('unscoped source/wire/Core changed: '+name)
    if before['swiftCExports']!=after['swiftCExports']:errors.append('C ABI export names changed')
    return errors

def main():
    try:
        record=json.loads(RECORD.read_text());ref=record['coreCompletedSourceHead']
        if not re.fullmatch('[0-9a-f]{40}',ref):raise ValueError('invalid closed Core ref')
        subprocess.run(['git','merge-base','--is-ancestor',ref,'HEAD'],cwd=ROOT,check=True,capture_output=True)
        raw=core.BASE.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        if digest!=record['originalCoreBaselineSha256'] or hashlib.sha256(subprocess.check_output(['git','show',ref+':contracts/baseline/p10-core-batch26.json'],cwd=ROOT)).hexdigest()!=digest:raise ValueError('original Core baseline changed')
        closed=snapshot_at(ref);errors=core.check(json.loads(raw),closed)
        errors+=check_transition(closed,core.snapshot(),record)
        for name in ALLOWED:
            if (ROOT/name).is_symlink():errors.append('Native source symlink refused: '+name)
        if errors:
            for error in errors:print(error)
            return 1
        print('Closed Core original guard PASS; exact reviewed Native transition/current Core/wire/export guard PASS')
        return 0
    except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as error:
        print('Feature transition FAIL:',type(error).__name__);return 1
if __name__=='__main__':raise SystemExit(main())
