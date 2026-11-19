"""Pure E1/E2 fail-closed contracts. Synthetic fixtures never provision resources."""
import ast
import re

def required_lanes(source):
    tree=ast.parse(source);assignments={}
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            if node.targets[0].id in ('self_names','required_names'):assignments[node.targets[0].id]=node.value
    assert set(assignments)=={'self_names','required_names'}, 'required inventory unavailable'
    self_names=ast.literal_eval(assignments['self_names'])
    expression=assignments['required_names']
    assert not any(isinstance(n,(ast.Call,ast.Attribute,ast.Subscript)) for n in ast.walk(expression))
    names=eval(compile(ast.Expression(expression),'<required-lanes>','eval'),{'__builtins__':{}},{'self_names':self_names})
    return sorted(names|{'recorded-unresolved-failures'})

REQUIREMENTS=('sourceClean','stagingIntegrity','stagingSourceMatch','nativeSourceAttestation','unityExecutable','unityLicense','unityAndroidModule','unityIosModule','adbEndpointsSeparate','adbPortsAvailable','adbExecutable','distinctAvdPlan','simulatorRuntime','storekitRuntime','postgresAvailable','testcontainersAvailable','backendPortsAvailable','secretScopePlan','requiredArtifacts','ownedResourcePlan')
def assess_e1(report,expected_lanes):
    missing=[]
    if not re.fullmatch('[0-9a-f]{40}',report.get('sourceHead','')):missing.append('sourceHead')
    if set(report.get('requiredLanes',[]))!=set(expected_lanes) or len(report.get('requiredLanes',[]))!=len(expected_lanes):missing.append('requiredLanes')
    checks=report.get('checks',{})
    for name in REQUIREMENTS:
        if checks.get(name) is not True:missing.append(name)
    return {'status':'DEFERRED_ENV' if missing else 'PASS','exitCode':2 if missing else 0,'missing':missing}

def assess_e2(facts,expected):
    """Compares freshly observed identities to the run's intended ownership record."""
    errors=[]
    for name in ('sourceHead','adbExecutable','adbPid','adbRuntimePort','adbBuildPort','piiSerial','pushSerial','piiAvd','pushAvd','piiPid','pushPid','simulatorUuid','simulatorRuntime','storekitUuid','storekitRuntime','backendPid','backendPort','dbRole','dbName','packageChecksum'):
        if name not in facts or name not in expected or facts[name]!=expected[name]:errors.append(name)
    for name in ('adbPid','piiPid','pushPid','backendPid'):
        if type(facts.get(name)) is not int or facts[name]<=0:errors.append(name+'Type')
    for name in ('adbRuntimePort','adbBuildPort','backendPort'):
        if type(facts.get(name)) is not int or not 1024<=facts[name]<=65535:errors.append(name+'Type')
    if facts.get('piiSerial')==facts.get('pushSerial') or facts.get('piiPid')==facts.get('pushPid') or facts.get('piiAvd')==facts.get('pushAvd'):errors.append('distinctDevices')
    if facts.get('adbRuntimePort')==facts.get('adbBuildPort'):errors.append('separateAdbEndpoints')
    if facts.get('simulatorUuid')==facts.get('storekitUuid'):errors.append('distinctSimulators')
    return {'status':'FAIL' if errors else 'PASS','exitCode':1 if errors else 0,'errors':errors}
