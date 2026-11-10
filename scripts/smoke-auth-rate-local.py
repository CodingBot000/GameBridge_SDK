#!/usr/bin/env python3
"""Tests configured rolling limits against a freshly started loopback sandbox test server."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

base = os.environ.get('GAMEBRIDGE_TEST_BASE_URL', 'http://127.0.0.1:18082').rstrip('/')
parts = urllib.parse.urlsplit(base)
if parts.scheme != 'http' or parts.hostname not in ('127.0.0.1', 'localhost') or parts.username or parts.password or parts.path or parts.query or parts.fragment:
    print('Only an explicit loopback test server is permitted.', file=sys.stderr); sys.exit(2)
challenge_limit = int(os.environ.get('GAMEBRIDGE_AUTH_CHALLENGE_PER_MINUTE', '30'))
exchange_limit = int(os.environ.get('GAMEBRIDGE_AUTH_EXCHANGE_PER_MINUTE', '10'))
app = os.environ.get('GAMEBRIDGE_TEST_APP_ID', 'gamebridge-sample')

def post(path, body, extra=None):
    headers = {'Content-Type': 'application/json'}; headers.update(extra or {})
    request = urllib.request.Request(base + path, data=json.dumps(body).encode(), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=5) as response: return response.status, response.headers, json.load(response)
    except urllib.error.HTTPError as error: return error.code, error.headers, json.load(error)

def main():
    for _ in range(challenge_limit):
        status, _, body = post('/v1/auth/challenges', {'appId': app, 'provider': 'GOOGLE'})
        assert status == 200 and body.get('nonce') and body.get('challengeId'), 'challenge before limit'
    status, headers, body = post('/v1/auth/challenges', {'appId': app, 'provider': 'GOOGLE'}, {'X-Forwarded-For': '203.0.113.99'})
    assert status == 429 and body.get('code') == 'BUSY' and body.get('requestId') == headers.get('X-Request-Id'), 'challenge limit or forwarded header handling'
    invalid = {'challengeId': str(uuid.uuid4()), 'provider': 'GOOGLE', 'idToken': 'synthetic-invalid-token'}
    for _ in range(exchange_limit):
        status, headers, body = post('/v1/auth/exchange', invalid)
        assert status == 401 and body.get('code') == 'AUTH_FAILED' and 'synthetic-invalid-token' not in json.dumps(body), 'invalid exchange'
    status, headers, body = post('/v1/auth/exchange', invalid)
    assert status == 429 and body.get('code') == 'BUSY' and body.get('requestId') == headers.get('X-Request-Id'), 'exchange limit'
    print(f'Sandbox HTTP rate checks passed: {challenge_limit} challenge + {exchange_limit} invalid exchange allowed; over-limit rejected; no real identity tested')

if __name__ == '__main__':
    try: main()
    except (AssertionError, OSError, ValueError, KeyError) as error:
        print(f'Auth rate smoke failed: {type(error).__name__}: {error}', file=sys.stderr); sys.exit(1)
