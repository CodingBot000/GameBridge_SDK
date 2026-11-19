"""Detection for test-only LOCAL_MOCK credential/proof shapes; not a general secret scanner."""
import re
_PATTERN = re.compile(r'(?<![A-Za-z0-9_])mock:[0-9a-fA-F-]{36}(?![A-Za-z0-9-])')
def contains_mock_credential(text):
    return _PATTERN.search(text) is not None
