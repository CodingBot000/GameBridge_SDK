#!/usr/bin/env python3
"""Exercise only the explicit local-mock A/B identities; never print credentials."""
import hashlib
import subprocess
import json
import os
import sys
import urllib.error
import urllib.request

BASE = 'http://127.0.0.1:18080'
KEY = os.environ.get('GAMEBRIDGE_DEV_AUTH_KEY', '')
if len(KEY) < 32:
    print('CONFIG_REQUIRED: GAMEBRIDGE_DEV_AUTH_KEY', file=sys.stderr)
    sys.exit(2)

def call(method, path, body=None, headers=None):
    data = None if body is None else json.dumps(body).encode()
    request_headers = {'Content-Type': 'application/json'}
    request_headers.update(headers or {})
    request = urllib.request.Request(BASE + path, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)

def main():
    count = 0
    def check(condition, label):
        nonlocal count
        count += 1
        if not condition:
            raise AssertionError(label)
    status, _ = call('GET', '/v1/me'); check(status == 401, 'anonymous access')
    status, _ = call('POST', '/v1/dev/auth', {'subject': 'A'}, {'X-Development-Key': 'invalid'}); check(status == 403, 'bad development key')
    status, a = call('POST', '/v1/dev/auth', {'subject': 'A'}, {'X-Development-Key': KEY}); check(status == 200, 'login A')
    status, b = call('POST', '/v1/dev/auth', {'subject': 'B'}, {'X-Development-Key': KEY}); check(status == 200 and a['userId'] != b['userId'], 'separate identities')
    status, me = call('GET', '/v1/me', headers={'Authorization': 'Bearer ' + a['accessToken']}); check(status == 200 and me['userId'] == a['userId'], 'profile A')
    status, rotated = call('POST', '/v1/auth/refresh', {'refreshToken': a['refreshToken']}); check(status == 200 and rotated['refreshToken'] != a['refreshToken'], 'rotation')
    status, _ = call('POST', '/v1/auth/refresh', {'refreshToken': a['refreshToken']}); check(status == 401, 'refresh replay')
    status, _ = call('GET', '/v1/me', headers={'Authorization': 'Bearer ' + rotated['accessToken']}); check(status == 401, 'family revoked')
    auth = {'Authorization': 'Bearer ' + b['accessToken']}
    status, _ = call('POST', '/v1/auth/logout', headers=auth); check(status == 200, 'logout')
    status, _ = call('POST', '/v1/auth/logout', headers=auth); check(status == 200, 'repeated logout')
    status, _ = call('GET', '/v1/me', headers=auth); check(status == 401, 'revoked access')
    status, fresh = call('POST', '/v1/dev/auth', {'subject': 'A'}, {'X-Development-Key': KEY}); check(status == 200, 'refresh logout login')
    digest = hashlib.sha256(fresh['refreshToken'].encode()).hexdigest()
    sql = "UPDATE sessions SET expires_at=now()-interval '1 second' WHERE refresh_hash=decode('" + digest + "','hex');"
    process = subprocess.run(['docker', 'exec', '-i', 'gamebridge-sdk-local-postgres-1', 'psql', '-U', 'gamebridge', '-d', 'gamebridge_local', '-v', 'ON_ERROR_STOP=1', '-tA'], input=sql, capture_output=True, text=True, check=True)
    check(process.stdout.strip() == 'UPDATE 1', 'expire owned test session')
    status, _ = call('POST', '/v1/auth/logout', {'refreshToken': fresh['refreshToken']}); check(status == 200, 'refresh logout')
    status, _ = call('POST', '/v1/auth/logout', {'refreshToken': fresh['refreshToken']}); check(status == 200, 'refresh logout idempotent')
    status, _ = call('POST', '/v1/auth/refresh', {'refreshToken': fresh['refreshToken']}); check(status == 401, 'refresh revoked')
    print(f'LOCAL_MOCK session checks passed: {count}; actual platform providers not tested')

if __name__ == '__main__':
    try:
        main()
    except (AssertionError, OSError, ValueError, KeyError) as exc:
        print(f'Local session check failed: {type(exc).__name__}', file=sys.stderr)
        sys.exit(1)
