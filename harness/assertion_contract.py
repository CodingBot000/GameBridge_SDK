"""Executed helper invocations, never framework test counts or static declarations."""
import json
import re


def records(text, platform, expected_count=None, allow_partial=False):
    found=[];seen=set()
    for raw in re.findall(r'GB_ASSERTIONS_JSON (\{[^\n]+\})',text):
        item=json.loads(raw)
        if item.get('platform')!=platform:continue
        if not isinstance(item.get('test'),str) or not item['test'] or item['test'] in seen:raise ValueError('missing/duplicate measured test')
        keys=('normalAssertions','expectedErrorChecks','assertionsExecuted')
        if any(type(item.get(k)) is not int or item[k]<0 for k in keys):raise ValueError('invalid assertion count')
        if item['assertionsExecuted']!=item['normalAssertions']+item['expectedErrorChecks']:raise ValueError('count mismatch')
        if item.get('assertionOutcomes')!='UNMEASURED':raise ValueError('unsupported assertion outcome claim')
        if item.get('complete') is False and not allow_partial:raise ValueError('partial invocation')
        if 'sites' in item:
            if not isinstance(item['sites'],list) or any(type(x.get('count')) is not int or x['count']<=0 for x in item['sites']):raise ValueError('invalid site counts')
            if sum(x['count'] for x in item['sites'])!=item['assertionsExecuted']:raise ValueError('site total mismatch')
        seen.add(item['test']);found.append(item)
    if not found or expected_count is not None and len(found)!=expected_count:raise ValueError('missing assertion evidence')
    return found


def totals(items):
    return {key:sum(x[key] for x in items) for key in ('normalAssertions','expectedErrorChecks','assertionsExecuted')}


def stress_assertions(value):
    counts=value.get('assertionExecution',{})
    keys=('executed','warmup','samples','finalChecks')
    if any(type(counts.get(k)) is not int or counts[k]<0 for k in keys):raise ValueError('unmeasured stress assertions')
    if counts['executed']!=counts['warmup']+counts['samples']+counts['finalChecks']:raise ValueError('stress total mismatch')
    if value.get('samples')!=100 or value.get('liveClients')!=0 or value.get('liveTransports')!=0:raise ValueError('stress not complete')
    return counts
