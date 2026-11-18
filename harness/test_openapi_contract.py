"""Mutations must fail independently of OpenAPI syntax validity."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('openapi_guard',Path(__file__).with_name('check-openapi.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class OpenApiTests(unittest.TestCase):
    def setUp(self): self.doc=json.loads((module.ROOT/'contracts/openapi.yaml').read_text())
    def test_current_source(self): self.assertEqual(module.check(self.doc),24)
    def test_path_removed(self):
        del self.doc['paths']['/health']
        with self.assertRaises(AssertionError): module.check(self.doc)
    def test_method_changed(self):
        item=self.doc['paths']['/health'];item['post']=item.pop('get')
        with self.assertRaises(AssertionError): module.check(self.doc)
    def test_auth_removed(self):
        self.doc['paths']['/v1/me']['get']['security']=[]
        with self.assertRaises(AssertionError): module.check(self.doc)
    def test_header_optional(self):
        self.doc['paths']['/v1/purchases/verify']['post']['parameters'][0]['required']=False
        with self.assertRaises(AssertionError): module.check(self.doc)
    def test_error_schema_mutated(self):
        self.doc['components']['schemas']['ApiError']['properties']['retryable']['type']='string'
        with self.assertRaises(AssertionError): module.check(self.doc)
    def test_profile_mutated(self):
        self.doc['paths']['/v1/dev/auth']['post']['x-source-bindings'][0]['profiles']=['production']
        with self.assertRaises(AssertionError): module.check(self.doc)
if __name__=='__main__': unittest.main()
