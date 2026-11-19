"""Validate checked-in bridge fixtures against the actual Draft 2020-12 schema."""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / 'contracts/bridge.schema.json').read_text())
FIXTURES = ROOT / 'contracts/fixtures/bridge'


class BridgeSchemaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Draft202012Validator.check_schema(SCHEMA)
        cls.validator = Draft202012Validator(SCHEMA, format_checker=FormatChecker())

    def fixture(self, name):
        return json.loads((FIXTURES / (name + '.json')).read_text())

    def test_checked_in_fixtures(self):
        for name in ('request', 'pending', 'unsupported', 'success', 'failure', 'event'):
            with self.subTest(name=name):
                self.assertEqual([], list(self.validator.iter_errors(self.fixture(name))))
        for name in ('invalid-version', 'invalid-operation', 'invalid-failure'):
            with self.subTest(name=name):
                self.assertTrue(list(self.validator.iter_errors(self.fixture(name))))

    def test_event_and_response_mutations(self):
        request = self.fixture('request')
        event = {'protocolVersion': 1, 'sdkSessionId': request['sdkSessionId'],
                 'kind': 'event', 'eventId': request['requestId'], 'payload': {}}
        self.assertTrue(self.validator.is_valid(event))
        for key in ('eventId', 'payload'):
            bad = copy.deepcopy(event)
            del bad[key]
            with self.subTest(missing_event=key):
                self.assertFalse(self.validator.is_valid(bad))
        for key in ('requestId', 'result', 'error'):
            bad = self.fixture('pending')
            del bad[key]
            with self.subTest(missing_response=key):
                self.assertFalse(self.validator.is_valid(bad))
        bad = self.fixture('request')
        bad['requestId'] = 'not-a-uuid'
        self.assertFalse(self.validator.is_valid(bad))


if __name__ == '__main__':
    unittest.main()
