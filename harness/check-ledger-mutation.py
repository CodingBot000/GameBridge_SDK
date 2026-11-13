#!/usr/bin/env python3
"""Prove the ledger invariant test detects removal in a fresh, test-only schema."""
import os
import re
import shutil
import time
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEST_NAME = 'one ledger entry per purchase is enforced by database()'


def valid_report(path: Path, started: int, mutation: bool) -> bool:
    if path.stat().st_mtime_ns < started:
        return False
    xml = ET.parse(path).getroot()
    expected = {'tests': 1, 'failures': 1 if mutation else 0, 'errors': 0, 'skipped': 0}
    if any(int(xml.attrib.get(key, '-1')) != value for key, value in expected.items()):
        return False
    cases = xml.findall('testcase')
    if len(cases) != 1 or cases[0].get('name') != TEST_NAME:
        return False
    failure = cases[0].find('failure')
    if not mutation:
        return failure is None
    message = failure.get('message', '') if failure is not None else ''
    return ('Expected an exception' in message and
            'org.springframework.dao.DataIntegrityViolationException' in message and
            'completed successfully' in message)

def main() -> int:
    env = os.environ.copy()
    required = ('GAMEBRIDGE_TEST_DB_URL','GAMEBRIDGE_TEST_DB_USER','GAMEBRIDGE_TEST_DB_PASSWORD')
    url = env.get('GAMEBRIDGE_TEST_DB_URL', '')
    embedded_credentials = bool(re.search(r'(?i)([?&](?:user|password)=|://[^/]*@)', url))
    if env.get('GAMEBRIDGE_RUN_DB_TESTS') != 'true' or embedded_credentials or not all(env.get(name) for name in required):
        print('DEFERRED_ENV: explicitly configured local-mock test DB required'); return 2
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix='ledger-mutation-', dir=artifacts))
    command = ['backend/gradlew','-p','backend','test','--rerun-tasks','--tests','com.gamebridge.purchase.LedgerInvariantDatabaseTest']
    report = ROOT/'backend/build/test-results/test/TEST-com.gamebridge.purchase.LedgerInvariantDatabaseTest.xml'
    mutated = env.copy(); mutated['GAMEBRIDGE_MUTATE_LEDGER_TEST'] = 'true'
    try:
        mutation_started = time.time_ns()
        failed = subprocess.run(command, cwd=ROOT, env=mutated, text=True, errors='replace', stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=600, check=False)
        (workspace/'mutation.log').write_text(failed.stdout, encoding='utf-8')
        if not valid_report(report, mutation_started, mutation=True) or failed.returncode != 1:
            print('Ledger mutation did not trigger the expected fresh invariant assertion'); return 1
        shutil.copyfile(report, workspace/'mutation.junit.xml')
        normal = env.copy(); normal.pop('GAMEBRIDGE_MUTATE_LEDGER_TEST', None)
        normal_started = time.time_ns()
        restored = subprocess.run(command, cwd=ROOT, env=normal, text=True, errors='replace', stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, timeout=600, check=False)
        (workspace/'normal.log').write_text(restored.stdout, encoding='utf-8')
        if not valid_report(report, normal_started, mutation=False) or restored.returncode != 0:
            print('Normal ledger invariant did not pass in a fresh report'); return 1
        shutil.copyfile(report, workspace/'normal.junit.xml')
    except (OSError, ValueError, ET.ParseError, subprocess.TimeoutExpired):
        print('Ledger mutation test unavailable or malformed'); return 2
    print('Ledger mutation detected; normal invariant passed in a separate fresh schema. Existing schemas preserved.')
    print('Mutation Gradle exit 1: 1 test, 1 expected failure, 0 errors, 0 skipped; normal exit 0: 1 test, 0 failures, 0 errors, 0 skipped.')
    print('Evidence directory:', workspace.relative_to(ROOT))
    return 0

if __name__ == '__main__': raise SystemExit(main())
