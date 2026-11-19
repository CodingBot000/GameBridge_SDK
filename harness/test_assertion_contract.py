"""Helper invocation evidence cannot be replaced by static/test counts."""
import json
import unittest
from assertion_contract import records,totals,stress_assertions
class AssertionContractTests(unittest.TestCase):
    def text(self,**changes):
        return 'GB_ASSERTIONS_JSON '+json.dumps({'platform':'fixture','test':'executed','normalAssertions':2,'expectedErrorChecks':1,'assertionsExecuted':3,'assertionOutcomes':'UNMEASURED',**changes})
    def test_normal_and_expected_checks_are_separate(self):
        self.assertEqual(totals(records(self.text(),'fixture',1)),{'normalAssertions':2,'expectedErrorChecks':1,'assertionsExecuted':3})
    def test_zero_helpers_are_not_zero_tests(self):
        self.assertEqual(records(self.text(normalAssertions=0,expectedErrorChecks=0,assertionsExecuted=0),'fixture',1)[0]['assertionsExecuted'],0)
    def test_missing_duplicate_and_malformed_counts_rejected(self):
        for text in ('',self.text()+'\n'+self.text(),self.text(assertionsExecuted=True),self.text(assertionsExecuted=4),self.text(expectedErrorChecks=-1),self.text(assertionsExecuted='3')):
            with self.assertRaises(ValueError):records(text,'fixture',1)
    def test_partial_and_site_total_mismatch(self):
        with self.assertRaises(ValueError):records(self.text(complete=False),'fixture',1)
        self.assertEqual(len(records(self.text(complete=False),'fixture',1,True)),1)
        with self.assertRaises(ValueError):records(self.text(sites=[{'count':2}]),'fixture',1)
    def test_stress_counts_are_dynamic_and_warmup_separate(self):
        good={'samples':100,'liveClients':0,'liveTransports':0,'assertionExecution':{'executed':316,'warmup':15,'samples':300,'finalChecks':1}}
        self.assertEqual(stress_assertions(good)['samples'],300)
        with self.assertRaises(ValueError):stress_assertions({**good,'assertionExecution':{}})
if __name__=='__main__':unittest.main()
