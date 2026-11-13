#!/usr/bin/env python3
"""Run local backend smoke on a new retained DB and loopback port, with synthetic keys."""
import base64
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTAINER = 'gamebridge-sdk-local-postgres-1'


def main():
    if sys.argv[1:] != ['--run-local']:
        print('Usage: python3 harness/run-backend-smoke-isolated.py --run-local (retains new DB and role)')
        return 2
    artifacts = ROOT / 'artifacts'; artifacts.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='backend-smoke-isolated-', dir=artifacts))
    role = 'gamebridge_ci_' + secrets.token_hex(5)
    password = secrets.token_hex(24)
    for sql in (f"CREATE ROLE {role} LOGIN PASSWORD '{password}'", f'CREATE DATABASE {role} OWNER {role}'):
        try:
            result = subprocess.run(['docker', 'exec', '-i', CONTAINER, 'psql', '-X', '-U', 'gamebridge', '-d', 'postgres', '-v', 'ON_ERROR_STOP=1'],
                                    input=sql + ';\n', text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20, check=False)
        except (OSError, subprocess.TimeoutExpired):
            print('DEFERRED_ENV: dedicated postgres unavailable; any created DB/role retained'); return 2
        if result.returncode:
            print('DEFERRED_ENV: unable to create isolated DB/role; any created DB/role retained'); return 2
    print('Retained isolated DB:', role, flush=True)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
    env = os.environ.copy()
    env.update(SPRING_PROFILES_ACTIVE='local-mock', DATABASE_URL=f'jdbc:postgresql://127.0.0.1:54329/{role}',
               DATABASE_USERNAME=role, DATABASE_PASSWORD=password, GAMEBRIDGE_PORT=str(port),
               GAMEBRIDGE_DEV_AUTH_KEY='isolated-test-' + secrets.token_hex(24),
               SERVER_TOKEN_ENCRYPTION_KEY=base64.b64encode(secrets.token_bytes(32)).decode(),
               SERVER_PURCHASE_ENCRYPTION_KEY=base64.b64encode(secrets.token_bytes(32)).decode(),
               GAMEBRIDGE_MAINTENANCE_ENABLED='false', GAMEBRIDGE_FINALIZATION_POLL_INTERVAL_MS='3600000',
               GAMEBRIDGE_SMOKE_BASE_URL=f'http://127.0.0.1:{port}', GAMEBRIDGE_SMOKE_DB_NAME=role,
               GAMEBRIDGE_LOCAL_SMOKE_OPT_IN='1')
    build = subprocess.run(['backend/gradlew', '-p', 'backend', 'bootJar'], cwd=ROOT, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    (output / 'build.log').write_text(build.stdout)
    if build.returncode: print('FAIL: backend build; evidence:', output.relative_to(ROOT)); return 1
    with (output / 'server.log').open('w') as log:
        server = subprocess.Popen(['java', '-jar', str(ROOT / 'backend/build/libs/gamebridge-backend.jar')], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                if server.poll() is not None: break
                try:
                    with urllib.request.urlopen(env['GAMEBRIDGE_SMOKE_BASE_URL'] + '/health', timeout=1) as response:
                        if response.status == 200: break
                except (OSError, urllib.error.URLError): time.sleep(.25)
            else:
                print('FAIL: backend health timed out; evidence:', output.relative_to(ROOT)); return 1
            if server.poll() is not None:
                print('FAIL: backend exited before health; evidence:', output.relative_to(ROOT)); return 1
            result = subprocess.run(['bash', 'scripts/smoke-local.sh'], cwd=ROOT, env=env, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180, check=False)
            (output / 'smoke.log').write_text(result.stdout)
            print(result.stdout, end='')
            if result.returncode:
                print('Evidence:', output.relative_to(ROOT)); return result.returncode
            source = (ROOT / 'scripts/smoke-purchase-local.py').read_text()
            target = "int(first['entitlements']['coinBalance']) == before + 100"
            if source.count(target) != 1:
                print('FAIL: negative purchase mutation target changed'); return 1
            mutated = output / 'negative-purchase.py'
            mutated.write_text(source.replace(target, "int(first['entitlements']['coinBalance']) == before + 101"))
            negative = subprocess.run([sys.executable, str(mutated)], cwd=ROOT, env=env, text=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180, check=False)
            (output / 'negative.log').write_text(negative.stdout)
            if negative.returncode != 1 or 'grant once and finalization pending' not in negative.stdout:
                print('FAIL: incorrect balance expectation was not rejected'); return 1
            print('Negative balance expectation rejected: PASS')
            print('Evidence:', output.relative_to(ROOT)); return 0
        except subprocess.TimeoutExpired:
            print('FAIL: smoke timed out; evidence:', output.relative_to(ROOT)); return 1
        finally:
            server.terminate()
            try: server.wait(timeout=10)
            except subprocess.TimeoutExpired: server.kill(); server.wait()


if __name__ == '__main__':
    raise SystemExit(main())
