#!/usr/bin/env python3
"""Validate exact Unity sample reimport GUID stability markers."""
from pathlib import Path
import sys
REQUIRED=('GB_SAMPLE_REIMPORT Editor Offline Demo ROOT=STABLE INTERNAL=STABLE',
          'GB_SAMPLE_REIMPORT Native Mock and Sandbox Demo ROOT=STABLE INTERNAL=STABLE',
          'GB_SAMPLE_REIMPORT_COMPLETE')
def passed(path,code):
    if code!=0:return False
    try: lines=Path(path).read_text(encoding='utf-8').splitlines()
    except (OSError,UnicodeError):return False
    return all(lines.count(marker)==1 for marker in REQUIRED) and not any('ROOT=CHANGED' in line or 'INTERNAL=CHANGED' in line for line in lines)
if __name__=='__main__':
    if len(sys.argv)!=3 or not sys.argv[2].isdigit() or not passed(sys.argv[1],int(sys.argv[2])):
        print('FAIL: sample reimport GUID evidence missing or changed',file=sys.stderr);raise SystemExit(1)
    print('Unity sample reimport GUID stability PASS: same project only')
