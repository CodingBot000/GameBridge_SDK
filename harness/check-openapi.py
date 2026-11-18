#!/usr/bin/env python3
"""Static source correspondence guard; runtime HTTP tests remain separate."""
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def inventory(root=ROOT):
    result = {}
    for file in (root/'backend/src/main/kotlin').rglob('*.kt'):
        source = file.read_text()
        for match in re.finditer(r'@(Get|Post|Put|Delete|Patch)Mapping\("([^"\n]+)"\)', source):
            start = source.rfind('@RestController', 0, match.start())
            if start < 0:
                raise ValueError('mapping without controller')
            prefix = source[start:match.start()]
            profiles = re.search(r'@Profile\(([^)]+)\)', prefix)
            profiles = re.findall(r'"([^"]+)"', profiles[1]) if profiles else ['all']
            end = re.search(r'@(Get|Post|Put|Delete|Patch)Mapping', source[match.end():])
            body = source[match.end():match.end()+end.start()] if end else source[match.end():]
            headers = re.findall(r'@RequestHeader\("([^"]+)"', body)
            key = (match[2], match[1].lower())
            result.setdefault(key, []).append({'source': str(file.relative_to(root)), 'profiles': profiles, 'headers': headers})
    return result

def check(doc, root=ROOT):
    actual = inventory(root)
    defined = {(p,m) for p, ops in doc['paths'].items() for m in ops if m in ('get','post','put','delete','patch')}
    assert defined == set(actual), 'path/method drift'
    security = (root/'backend/src/main/kotlin/com/gamebridge/session/Sessions.kt').read_text()
    permitted = set(re.findall(r'"([^"]+)"', re.search(r'requestMatchers\((.*?)\)\.permitAll', security)[1]))
    for key, bindings in actual.items():
        op = doc['paths'][key[0]][key[1]]
        expected = [] if key[0] in permitted else [{'BearerSession': []}]
        assert op['security'] == expected, f'authentication drift: {key}'
        assert op['x-source-bindings'] == bindings, f'profile/header binding drift: {key}'
        headers = {p['name'] for p in op.get('parameters',[]) if p['in']=='header' and p.get('required')}
        assert headers == {h for b in bindings for h in b['headers']}, f'header drift: {key}'
        for status, response in op['responses'].items():
            if status != '200':
                assert response['content']['application/json']['schema'] == {'$ref':'#/components/schemas/ApiError'}, 'error response drift'
    error = doc['components']['schemas']['ApiError']
    assert error == {'type':'object','required':['code','message','requestId','retryable'],'properties':{k:{'type':t} for k,t in [('code','string'),('message','string'),('requestId','string'),('retryable','boolean')]}} , 'error schema drift'
    errors = (root/'backend/src/main/kotlin/com/gamebridge/config/HttpInfrastructure.kt').read_text()
    assert all('"'+field+'"' in errors for field in error['required']), 'error source drift'
    return len(actual)

if __name__ == '__main__':
    doc=json.loads((ROOT/'contracts/openapi.yaml').read_text())
    print(f'OpenAPI source guard PASS: {check(doc)} operations (static; runtime coverage separate)')
