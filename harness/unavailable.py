#!/usr/bin/env python3
"""A missing required check is a non-success, never a placeholder pass."""
import sys
print('NOT_IMPLEMENTED: ' + (' '.join(sys.argv[1:]) or 'required check'), file=sys.stderr)
sys.exit(2)
