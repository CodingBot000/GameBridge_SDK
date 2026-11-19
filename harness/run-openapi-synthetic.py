#!/usr/bin/env python3
"""Run existing synthetic HTTP suites against separate fresh profile databases and validate sanitized shapes."""
import argparse,importlib.util,json,os,re,subprocess,tempfile,xml.etree.ElementTree as ET
from pathlib import Path
from jsonschema import Draft4Validator, RefResolver
from run_openapi_adapter import compatible
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('synthetic_backend',ROOT/'harness/run-unity-android-mock-e2e.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-local',required=True,action='store_true');parser.parse_args()
    out=Path(tempfile.mkdtemp(prefix='openapi-synthetic-',dir=ROOT/'artifacts'))
    doc=json.loads((ROOT/'contracts/openapi.yaml').read_text());converted=compatible(doc)
    result={'sourceHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'sourceState':'HEAD plus current test-only capture changes','status':'FAIL','groups':[],'operations':[],'rawResponseStrings':'NEVER_WRITTEN'}
    groups={'sandbox':['AuthHttpIntegrationTest','ApplePurchaseHttpIntegrationTest','GooglePurchaseHttpIntegrationTest','SandboxPushHttpIntegrationTest'],'local-mock':['MockXcodeHttpIntegrationTest','DevPushHttpIntegrationTest']}
    try:
        for profile,classes in groups.items():
            db,password=common.create_isolated_database('gamebridge-sdk-local-postgres-1','gamebridge',54329)
            env=dict(os.environ,GAMEBRIDGE_RUN_AUTH_DB_TESTS='true',GAMEBRIDGE_RUN_DB_TESTS='true',GAMEBRIDGE_TEST_DB_URL='jdbc:postgresql://127.0.0.1:54329/'+db,GAMEBRIDGE_TEST_DB_USER=db,GAMEBRIDGE_TEST_DB_PASSWORD=password,GAMEBRIDGE_OPENAPI_HTTP_EVIDENCE=str(out/(profile+'.jsonl')))
            command=['backend/gradlew','-p','backend','test','--rerun-tasks']
            for name in classes:command+=['--tests','*'+name]
            with (out/(profile+'.log')).open('w') as log:r=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
            counts={k:0 for k in ['tests','failures','errors','skipped']}
            for name in classes:
                paths=list((ROOT/'backend/build/test-results/test').glob('TEST-*.'+name+'.xml'));assert len(paths)==1
                suite=ET.parse(paths[0]).getroot()
                for key in counts:counts[key]+=int(suite.get(key,'0'))
                (out/(profile+'-'+name+'.xml')).write_bytes(paths[0].read_bytes())
            result['groups'].append({'profile':profile,'exitCode':r.returncode,'counts':counts,'database':db})
            assert r.returncode==0 and counts['tests']>0 and all(counts[k]==0 for k in ['failures','errors','skipped'])
            for line in (out/(profile+'.jsonl')).read_text().splitlines():
                row=json.loads(line);matches=[path for path,ops in doc['paths'].items() if row['method'] in ops and re.fullmatch(re.sub(r'\{[^}]+\}',r'[^/]+',path),row['path'])]
                if row['path'] in matches: matches=[row['path']] # Spring prefers literal mappings over path variables.
                result['lastResponse']={'path':row['path'],'method':row['method'],'status':row['status']}
                assert len(matches)==1
                path=matches[0];op=doc['paths'][path][row['method']];response=op['responses'].get(str(row['status']),op['responses'].get('default'))
                schema=response['content']['application/json']['schema']
                Draft4Validator(compatible(schema),resolver=RefResolver.from_schema(converted)).validate(row['bodyShape'])
                assert row['requestIdHeaderPresent'] and row['requestIdCorrelated']
                result['operations'].append({'path':path,'method':row['method'],'profile':profile,'status':row['status'],'serializedShape':'PASS','requestId':'PASS'})
        result['status']='PASS';return 0
    except Exception as error:
        result['failureType']=type(error).__name__;return 1
    finally:
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('Evidence directory:',out.relative_to(ROOT))
if __name__=='__main__':raise SystemExit(main())
