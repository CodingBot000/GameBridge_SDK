#!/usr/bin/env python3
"""Exercise local mock token registration; test rows remain in the dedicated DB."""
import json
import os
import sys
import urllib.error
import urllib.request
import uuid

BASE = 'http://127.0.0.1:18080'
KEY = os.environ.get('GAMEBRIDGE_DEV_AUTH_KEY', '')
if len(KEY) < 32:
    print('CONFIG_REQUIRED: GAMEBRIDGE_DEV_AUTH_KEY', file=sys.stderr); sys.exit(2)

def call(method, path, body=None, headers=None):
    data = None if body is None else json.dumps(body).encode()
    values = {'Content-Type': 'application/json'}; values.update(headers or {})
    request = urllib.request.Request(BASE + path, data=data, headers=values, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response: return response.status, json.load(response)
    except urllib.error.HTTPError as error: return error.code, json.load(error)

def main():
    count = 0
    def check(condition, label):
        nonlocal count
        count += 1
        if not condition: raise AssertionError(label)
    status, config = call('GET', '/v1/config'); check(status == 200 and config['source'] == 'DEFAULT', 'public default config')
    status, a = call('POST', '/v1/dev/auth', {'subject': 'A'}, {'X-Development-Key': KEY}); check(status == 200, 'login A')
    status, b = call('POST', '/v1/dev/auth', {'subject': 'B'}, {'X-Development-Key': KEY}); check(status == 200, 'login B')
    path = '/v1/devices/' + str(uuid.uuid4()) + '/push-token'
    payload = {'provider': 'MOCK', 'platform': 'MOCK', 'appId': 'gamebridge-sample', 'token': 'mock:' + str(uuid.uuid4())}
    auth_a = {'Authorization': 'Bearer ' + a['accessToken']}; auth_b = {'Authorization': 'Bearer ' + b['accessToken']}
    status, _ = call('PUT', path, payload); check(status == 401, 'anonymous rejected')
    status, registered = call('PUT', path, payload, auth_a); check(status == 200 and registered['registered'] and payload['token'] not in json.dumps(registered), 'register without token exposure')
    rotated = {**payload, 'token': 'mock:' + str(uuid.uuid4())}
    status, changed = call('PUT', path, rotated, auth_a); check(status == 200 and changed['tokenFingerprint'] != registered['tokenFingerprint'], 'rotate token')
    status, _ = call('PUT', path, rotated, auth_b); check(status == 403, 'ownership conflict')
    print(f'LOCAL_MOCK device checks passed: {count}; no remote push tested')

if __name__ == '__main__':
    try: main()
    except (AssertionError, OSError, ValueError, KeyError) as error:
        print(f'Local device check failed: {type(error).__name__}: {error}', file=sys.stderr); sys.exit(1)
