def compatible(value):
    if isinstance(value,list):return [compatible(x) for x in value]
    if not isinstance(value,dict):return value
    result={k:compatible(v) for k,v in value.items() if k!='nullable'}
    if value.get('nullable'):
        return {'anyOf':[result,{'type':'null'}]}
    return result

