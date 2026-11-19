"""Owned lifecycle evidence is mandatory; no Docker/Gradle is invoked by these units."""
import importlib.util
import os
import subprocess
import sys
import unittest
import tempfile
from xml.sax.saxutils import quoteattr
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('tc_contract',Path(__file__).with_name('run-purchase-testcontainers.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class TestcontainersContractTests(unittest.TestCase):
    def setUp(self):
        self.proof={'sourceHead':'head','runId':'run','task':'tcPurchaseLocal','image':'postgres:17.6-alpine3.22','profile':'local-mock','containerStarted':True,'containerStopped':True,'loopbackOnly':True,'mappedPort':5555,'containerId':'a'*64}
    def test_owned_started_stopped_local_container(self):
        self.assertTrue(module.valid_container(self.proof,'head','run','tcPurchaseLocal'))
    def test_missing_foreign_stale_or_unmeasured_proof_is_not_pass(self):
        for key,value in [('sourceHead','old'),('runId','other'),('containerStarted',False),('containerStopped',False),('loopbackOnly',False),('mappedPort',True),('mappedPort',-1),('mappedPort',65536),('containerId','other'),('profile','sandbox')]:
            self.assertFalse(module.valid_container({**self.proof,key:value},'head','run','tcPurchaseLocal'),key)
        for key in self.proof:
            changed=self.proof.copy();changed.pop(key)
            self.assertFalse(module.valid_container(changed,'head','run','tcPurchaseLocal'),key)
    def test_not_found_is_case_insensitive_but_not_arbitrary_inspect_failure(self):
        for error in ('Error: No such object: abc','error: no such container: abc'):
            self.assertTrue(module.removed_container(subprocess.CompletedProcess([],1,stderr=error)))
        for error in ('permission denied','cannot connect to docker daemon','invalid endpoint',''):
            self.assertFalse(module.removed_container(subprocess.CompletedProcess([],1,stderr=error)))
        self.assertFalse(module.removed_container(subprocess.CompletedProcess([],0,stderr='')))
    def test_mutation_requires_the_named_invariant_assertion(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'junit.xml'
            name=module.ledger.TEST_NAME
            def write(message):
                path.write_text('<testsuite tests="1" failures="1" errors="0" skipped="0"><testcase name='+quoteattr(name)+'><failure message='+quoteattr(message)+'/></testcase></testsuite>')
            write('Expected an exception of org.springframework.dao.DataIntegrityViolationException, but completed successfully')
            self.assertTrue(module.named_ledger_evidence('tcLedgerMutation',[path],0))
            write('unrelated database connection failure')
            self.assertFalse(module.named_ledger_evidence('tcLedgerMutation',[path],0))
            self.assertFalse(module.named_ledger_evidence('tcLedgerMutation',[path],path.stat().st_mtime_ns+1))

    def test_remote_docker_and_missing_opt_in_never_start_containers(self):
        with patch.object(sys,'argv',['runner','--run-local']),patch.dict(os.environ,{'DOCKER_HOST':'tcp://remote.invalid:2376'},clear=True),patch.object(module.subprocess,'run') as run,patch.object(module.subprocess,'check_output') as context:
            self.assertEqual(module.main(),2);run.assert_not_called();context.assert_not_called()
        with patch.object(sys,'argv',['runner']),patch.object(module.subprocess,'run') as run:
            self.assertEqual(module.main(),2);run.assert_not_called()
if __name__=='__main__':unittest.main()
