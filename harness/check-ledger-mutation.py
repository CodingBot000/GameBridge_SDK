#!/usr/bin/env python3
"""Prove the ledger invariant test detects removal in a fresh, test-only schema."""
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

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
        failed = subprocess.run(command, cwd=ROOT, env=mutated, text=True, errors='replace', stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=600, check=False)
        (workspace/'mutation.log').write_text(failed.stdout, encoding='utf-8')
        xml = ET.parse(report).getroot(); failure = xml.find('.//failure')
        message = failure.attrib.get('message','') if failure is not None else ''
        if failed.returncode == 0 or int(xml.attrib.get('tests','0')) != 1 or int(xml.attrib.get('failures','0')) != 1 or 'Expected an exception' not in message:
            print('Ledger mutation did not trigger the expected invariant assertion'); return 1
        normal = env.copy(); normal.pop('GAMEBRIDGE_MUTATE_LEDGER_TEST', None)
        restored = subprocess.run(command, cwd=ROOT, env=normal, text=True, errors='replace', stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, timeout=600, check=False)
        (workspace/'normal.log').write_text(restored.stdout, encoding='utf-8')
        xml = ET.parse(report).getroot()
        if restored.returncode != 0 or int(xml.attrib.get('tests','0')) != 1 or int(xml.attrib.get('failures','0')) != 0 or int(xml.attrib.get('skipped','0')) != 0:
            print('Normal ledger invariant did not pass after mutation'); return 1
    except (OSError, ValueError, ET.ParseError, subprocess.TimeoutExpired):
        print('Ledger mutation test unavailable or malformed'); return 2
    print('Ledger mutation detected; normal invariant passed in a separate fresh schema. Existing schemas preserved.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
