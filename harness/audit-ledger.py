#!/usr/bin/env python3
"""Inventory tracked source and ledger without upgrading untested work to complete."""
import collections
import json
import re
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main() -> int:
    progress = (ROOT/'docs/PROGRESS.md').read_text(encoding='utf-8')
    plan = (ROOT/'docs/DEVELOPMENT_PLAN.md').read_text(encoding='utf-8')
    ids = re.findall(r'^#### (P\d\d-T\d\d)\b',plan,re.M)
    rows = []
    for line in progress.splitlines():
        if re.match(r'^\| P\d\d-T\d\d \|',line):
            parts = [item.strip() for item in line.strip().strip('|').split('|')]
            if len(parts) != 7: raise SystemExit('Malformed task row')
            rows.append(parts)
    if len(ids) != len(rows) or set(ids) != {row[0] for row in rows}: raise SystemExit('Task inventory mismatch')
    manifest = json.loads((ROOT/'harness/regression-manifest.json').read_text(encoding='utf-8'))
    blockers = []
    for line in progress.splitlines():
        if re.match(r'^\| (?:BUG|ENV|DEP|USER)-',line):
            cells = [item.strip() for item in line.strip().strip('|').split('|')]
            if len(cells) == 7 and cells[-1] == 'OPEN': blockers.append({'id':cells[0], 'type':cells[1], 'tasks':cells[2], 'description':cells[3]})
    source_files = subprocess.run(['git','ls-files','-z','android','ios','unity','backend','scripts','harness'],cwd=ROOT,
                                  stdout=subprocess.PIPE,check=True).stdout.decode('utf-8').split('\0')
    markers = []
    for name in source_files:
        path = Path(name)
        if not name or name == 'harness/audit-ledger.py' or path.suffix not in {'.kt','.swift','.cs','.py','.sh'}: continue
        try: lines = (ROOT/path).read_text(encoding='utf-8').splitlines()
        except (OSError,UnicodeError): continue
        for number,line in enumerate(lines,1):
            if re.search(r'\b(?:TODO|FIXME)\b|NotImplementedException|fatalError\(',line):
                markers.append({'path':name,'line':number})
    verify = subprocess.run(['python3','scripts/verify-progress.py'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,check=False)
    if verify.returncode != 0: raise SystemExit('Progress ledger validation failed')
    implementations = collections.Counter(row[2] for row in rows); local = collections.Counter(row[3] for row in rows); external = collections.Counter(row[4] for row in rows)
    coverage = collections.Counter(entry['coverage'] for entry in manifest['scenarios'])
    status = 'BLOCKED_INTERNAL' if any(x['type']=='BUG' for x in blockers) or local.get('FAIL',0) or coverage.get('NOT_IMPLEMENTED',0) or coverage.get('PARTIAL',0) else 'IN_PROGRESS'
    result = {'timestampUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'sourceHead':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stdout=subprocess.PIPE,check=True).stdout.strip(),
              'workingTree':'HEAD plus uncommitted changes may be present','status':status,'taskCount':len(rows),
              'implementation':dict(implementations),'local':dict(local),'external':dict(external),'scenarioCoverage':dict(coverage),
              'openBlockers':blockers,'trackedSourceMarkers':markers,'notes':['Untracked user files and ignored artifacts were not scanned.','Text search cannot prove feature completeness.']}
    artifacts = ROOT/'artifacts'; artifacts.mkdir(exist_ok=True); output = Path(tempfile.mkdtemp(prefix='ledger-audit-',dir=artifacts))
    (output/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Audit complete: {len(rows)} tasks; status {status}; open blockers {len(blockers)}; tracked source markers {len(markers)}")
    print('Evidence directory:',output.relative_to(ROOT)); return 0

if __name__ == '__main__': raise SystemExit(main())
