import importlib.util
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('external_config',Path(__file__).resolve().parents[1]/'scripts/verify-external-config.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class ConfigShapeTests(unittest.TestCase):
    def test_product_ids_must_be_list_of_nonblank_strings(self):
        for values,expected in [('coins_100',False),([1],False),([' '],False),(['coins_100'],True)]:
            with self.subTest(values=values), patch.dict(os.environ,{'CONFIG':json.dumps({'app':{'productIds':values}})}):
                self.assertEqual(module.valid_json('CONFIG',('productIds',)),expected)
    def test_scalar_must_be_string(self):
        with patch.dict(os.environ,{'CONFIG':json.dumps({'app':{'teamId':['wrong-type']}})}):
            self.assertFalse(module.valid_json('CONFIG',('teamId',)))
