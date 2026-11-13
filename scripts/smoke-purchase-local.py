#!/usr/bin/env python3
"""Local mock purchase checks; creates durable test purchases and prints no tokens/proofs."""
import concurrent.futures
import json
import os
import sys
import urllib.error
import urllib.request
import uuid

BASE = os.environ.get('GAMEBRIDGE_SMOKE_BASE_URL', 'http://127.0.0.1:18080')
if not BASE.startswith('http://127.0.0.1:') or not BASE[len('http://127.0.0.1:'):].isdigit():
    print('CONFIG_REQUIRED: loopback GAMEBRIDGE_SMOKE_BASE_URL', file=sys.stderr); sys.exit(2)
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
    def login(subject): return call('POST', '/v1/dev/auth', {'subject': subject}, {'X-Development-Key': KEY})
    status, a = login('A'); check(status == 200, 'login A')
    status, b = login('B'); check(status == 200, 'login B')
    auth_a = {'Authorization': 'Bearer ' + a['accessToken']}; auth_b = {'Authorization': 'Bearer ' + b['accessToken']}
    status, baseline = call('GET', '/v1/entitlements', headers=auth_a); check(status == 200, 'baseline')
    before = int(baseline['coinBalance']); tx = str(uuid.uuid4()); key = str(uuid.uuid4())
    payload = {'productId': 'coins_100', 'proof': f'mock:{a["userId"]}:coins_100:{tx}', 'quantity': 1}
    def buy(body, k, auth=auth_a): return call('POST', '/v1/purchases/verify', body, {**auth, 'Idempotency-Key': k})
    status, first = buy(payload, key); check(status == 200 and int(first['entitlements']['coinBalance']) == before + 100 and first['finalizationStatus'] == 'PENDING', 'grant once and finalization pending')
    status, repeat = buy(payload, key); check(status == 200 and repeat['serverPurchaseId'] == first['serverPurchaseId'] and int(repeat['entitlements']['coinBalance']) == before + 100, 'same key retry')
    changed = {**payload, 'proof': f'mock:{a["userId"]}:coins_100:{uuid.uuid4()}'}
    status, error = buy(changed, key); check(status == 409 and error['code'] == 'IDEMPOTENCY_CONFLICT', 'key conflict')
    status, error = buy(payload, str(uuid.uuid4()), auth_b); check(status == 409 and error['code'] == 'PURCHASE_ACCOUNT_MISMATCH', 'ownership')
    forged = {**payload, 'proof': f'mock:{b["userId"]}:coins_100:{tx}'}
    status, error = buy(forged, str(uuid.uuid4()), auth_b); check(status == 409 and error['code'] == 'PURCHASE_ACCOUNT_MISMATCH', 'transaction ownership')
    status, _ = buy({**changed, 'quantity': 2}, str(uuid.uuid4())); check(status == 400, 'quantity rejected')
    parallel_id = str(uuid.uuid4()); parallel = {**payload, 'proof': f'mock:{a["userId"]}:coins_100:{parallel_id}'}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: buy(parallel, str(uuid.uuid4())), range(2)))
    check(all(code == 200 for code, _ in results), 'concurrent retries')
    status, after = call('GET', '/v1/entitlements', headers=auth_a); check(status == 200 and int(after['coinBalance']) == before + 200, 'concurrent one grant')
    premium = {'productId': 'premium_unlock', 'proof': f'mock:{a["userId"]}:premium_unlock:{uuid.uuid4()}', 'quantity': 1}
    status, one = buy(premium, str(uuid.uuid4())); check(status == 200 and one['entitlements']['premiumEnabled'], 'premium')
    status, two = buy(premium, str(uuid.uuid4())); check(status == 200 and two['serverPurchaseId'] == one['serverPurchaseId'] and two['entitlements']['premiumEnabled'], 'premium retry')
    print(f'LOCAL_MOCK purchase checks passed: {count}; real store verification not tested')

if __name__ == '__main__':
    try: main()
    except (AssertionError, OSError, ValueError, KeyError) as error:
        print(f'Local purchase check failed: {type(error).__name__}: {error}', file=sys.stderr); sys.exit(1)
