"""Limited Kotlin data-class shape checker. Rejects unsupported types explicitly."""
import re
from pathlib import Path

def dto_shapes(root):
    result={}
    for path in (root/'backend/src/main/kotlin').rglob('*.kt'):
        text=path.read_text()
        for match in re.finditer(r'\bdata class (\w+)\s*\(',text):
            depth=1;end=match.end()
            while depth and end<len(text):
                depth+=(text[end]=='(')-(text[end]==')');end+=1
            fields={}
            for field in re.finditer(r'\bval (\w+)\s*:\s*([\w?]+)(\s*=\s*[^,]+)?',text[match.end():end-1]):
                typ=field[2];nullable=typ.endswith('?');base=typ.rstrip('?')
                fields[field[1]]={'kotlinType':base,'type':{'String':'string','UUID':'string','Boolean':'boolean','Int':'integer','IdentityProvider':'string','AuthProofType':'string'}.get(base),'nullable':nullable,'required':not nullable and not field[3]}
            result[match[1]]=fields
    return result

def check_dtos(doc,root):
    shapes=dto_shapes(root);checked=[]
    for name,schema in doc['components']['schemas'].items():
        aliases={'ReadinessInput':['AppleReadinessInput','GoogleReadinessInput']}
        types=aliases.get(name,[name] if name in shapes else [])
        for typ in types:
            fields=shapes[typ];assert fields, 'empty DTO '+typ
            assert set(fields)==set(schema['properties']), 'DTO fields drift '+name
            for field,actual in fields.items():
                expected=schema['properties'][field]
                if actual['type'] is None:
                    assert expected.get('$ref')=='#/components/schemas/'+actual['kotlinType'], 'DTO nested type drift '+name
                else:assert expected.get('type')==actual['type'], 'DTO type drift '+name
                assert bool(expected.get('nullable'))==actual['nullable'], 'DTO nullable drift '+name
            assert set(schema.get('required',[]))=={k for k,v in fields.items() if v['required']}, 'DTO required drift '+name
            checked.append(typ)
    return checked

def check_request_bindings(doc,root):
    expected={}
    for file in (root/'backend/src/main/kotlin').rglob('*.kt'):
        text=file.read_text();matches=list(re.finditer(r'@(Get|Post|Put|Delete|Patch)Mapping\("([^"\n]+)"\)',text))
        for index,match in enumerate(matches):
            segment=text[match.end():matches[index+1].start() if index+1<len(matches) else len(text)]
            body=re.search(r'@RequestBody(?:\(([^)]*)\))?\s+\w+\s*:\s*(\w+)',segment)
            if not body:continue
            typ=body[2]
            if typ=='ByteArray':
                assert 'LogoutInput::class.java' in segment, 'unmapped raw HTTP body'
                typ='LogoutInput'
            if typ in ('AppleReadinessInput','GoogleReadinessInput'):typ='ReadinessInput'
            expected.setdefault((match[2],match[1].lower()),[]).append((typ,not bool(body[1] and 'required = false' in body[1])))
    for (path,method),models in expected.items():
        request=doc['paths'][path][method].get('requestBody');assert request, 'missing request body contract'
        schema=request['content']['application/json']['schema']
        refs={schema['$ref'].split('/')[-1]} if '$ref' in schema else {s['$ref'].split('/')[-1] for s in schema.get('anyOf',schema.get('oneOf',[]))}
        assert refs=={m[0] for m in models}, 'operation request DTO mismatch'
        assert request.get('required',False)==any(m[1] for m in models), 'operation body required mismatch'
    return len(expected)
