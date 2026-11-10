#!/usr/bin/env python3
"""Exercise local mock token registration; test rows remain in the dedicated DB."""
import concurrent.futures
import json
import subprocess
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
    installation = str(uuid.uuid4())
    path = '/v1/devices/' + installation + '/push-token'
    def row_count(identifier):
        canonical = str(uuid.UUID(identifier))
        sql = "SELECT count(*) FROM device_tokens WHERE installation_id='" + canonical + "'::uuid"
        result = subprocess.run(['docker', 'exec', 'gamebridge-sdk-local-postgres-1', 'psql', '-U', 'gamebridge', '-d', 'gamebridge_local', '-tAc', sql], capture_output=True, text=True, check=True)
        return int(result.stdout.strip())
    payload = {'provider': 'MOCK', 'platform': 'MOCK', 'appId': 'gamebridge-sample', 'token': 'mock:' + str(uuid.uuid4())}
    auth_a = {'Authorization': 'Bearer ' + a['accessToken']}; auth_b = {'Authorization': 'Bearer ' + b['accessToken']}
    status, _ = call('PUT', path, payload); check(status == 401, 'anonymous rejected')
    status, registered = call('PUT', path, payload, auth_a); check(status == 200 and registered['registered'] and payload['token'] not in json.dumps(registered), 'register without token exposure')
    rotated = {**payload, 'token': 'mock:' + str(uuid.uuid4())}
    status, changed = call('PUT', path, rotated, auth_a); check(status == 200 and changed['tokenFingerprint'] != registered['tokenFingerprint'], 'rotate token')
    status, _ = call('PUT', path, rotated, auth_b); check(status == 403, 'ownership conflict')
    status, _ = call('DELETE', path, headers=auth_b); check(status == 403 and row_count(installation) == 1, 'other user cannot delete')
    status, a2 = call('POST', '/v1/dev/auth', {'subject': 'A'}, {'X-Development-Key': KEY}); check(status == 200, 'second session')
    auth_a2 = {'Authorization': 'Bearer ' + a2['accessToken']}
    second = str(uuid.uuid4()); second_path = '/v1/devices/' + second + '/push-token'
    status, _ = call('PUT', second_path, payload, auth_a2); check(status == 200, 'second device registered')
    status, _ = call('POST', '/v1/auth/logout', headers=auth_a); check(status == 200, 'logout first session')
    check(row_count(installation) == 0 and row_count(second) == 1, 'only logged-out session token deleted')
    status, _ = call('DELETE', second_path, headers=auth_a2); check(status == 200 and row_count(second) == 0, 'unregister deletes token')
    status, a3 = call('POST', '/v1/dev/auth', {'subject': 'A'}, {'X-Development-Key': KEY}); check(status == 200, 'race session')
    auth_a3 = {'Authorization': 'Bearer ' + a3['accessToken']}
    raced = str(uuid.uuid4()); race_path = '/v1/devices/' + raced + '/push-token'
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        put = pool.submit(call, 'PUT', race_path, payload, auth_a3)
        logout = pool.submit(call, 'POST', '/v1/auth/logout', None, auth_a3)
        put_status, _ = put.result(); logout_status, _ = logout.result()
    check(put_status in (200, 401) and logout_status == 200 and row_count(raced) == 0, 'register/logout race leaves no token')
    print(f'LOCAL_MOCK device checks passed: {count}; no remote push tested')

if __name__ == '__main__':
    try: main()
    except (AssertionError, OSError, ValueError, KeyError) as error:
        print(f'Local device check failed: {type(error).__name__}: {error}', file=sys.stderr); sys.exit(1)
