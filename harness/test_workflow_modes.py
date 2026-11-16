"""Check workflow trigger policy alongside the executable release-gate tests."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class WorkflowModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        code = '''require "yaml"; require "json"; x=YAML.load_file(ARGV[0]); puts JSON.generate({"trigger"=>x.fetch(true).fetch("workflow_dispatch"),"jobs"=>x.fetch("jobs")})'''
        cls.workflow = json.loads(subprocess.check_output(['ruby','-e',code,str(ROOT/'.github/workflows/verify.yml')],text=True))

    def test_release_input_defaults_off(self):
        item=self.workflow['trigger']['inputs']['release_validation']
        self.assertEqual(item['type'],'boolean'); self.assertIs(item['default'],False)

    def test_only_explicit_release_can_schedule_unity_and_gate(self):
        jobs=self.workflow['jobs']
        self.assertEqual(jobs['unity-e2e']['if'], "${{ github.event_name == 'workflow_dispatch' && inputs.release_validation == true && vars.GAMEBRIDGE_UNITY_E2E_ENABLED == 'true' }}")
        self.assertEqual(jobs['release-readiness']['if'], "${{ always() && !cancelled() && github.event_name == 'workflow_dispatch' && inputs.release_validation == true }}")
        self.assertEqual(jobs['release-readiness']['needs'],['basic-ci','unity-e2e'])
        for event,request,enabled,expected in [('pull_request',False,True,(False,False)),('workflow_dispatch',False,True,(False,False)),('workflow_dispatch',True,False,(False,True)),('workflow_dispatch',True,True,(True,True))]:
            with self.subTest(event=event,request=request,enabled=enabled):
                self.assertEqual((event=='workflow_dispatch' and request and enabled,event=='workflow_dispatch' and request),expected)


if __name__ == '__main__': unittest.main()
