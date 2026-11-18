import copy
from pathlib import Path
import unittest
from strict_environment_contract import REQUIREMENTS,assess_e1,assess_e2,required_lanes
class StrictEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.lanes=required_lanes((Path(__file__).with_name('verify-all.py')).read_text())
        self.report={'sourceHead':'a'*40,'requiredLanes':self.lanes,'checks':{k:True for k in REQUIREMENTS}}
        self.identity=dict(sourceHead='a'*40,adbExecutable='/owned/adb',adbPid=1,adbRuntimePort=5037,adbBuildPort=5038,piiSerial='emulator-5600',pushSerial='emulator-5602',piiAvd='owned-pii',pushAvd='owned-push',piiPid=2,pushPid=3,simulatorUuid='sim',simulatorRuntime='iOS18.6',storekitUuid='store',storekitRuntime='iOS18.6',backendPid=4,backendPort=18080,dbRole='owned-role',dbName='owned-db',packageChecksum='b'*64)
    def test_complete_fixture(self):
        self.assertEqual(assess_e1(self.report,self.lanes)['exitCode'],0)
        self.assertEqual(assess_e2(self.identity,self.identity)['exitCode'],0)
    def test_every_missing_prerequisite_defers(self):
        for name in REQUIREMENTS:
            r=copy.deepcopy(self.report);r['checks'][name]=False
            with self.subTest(name=name):self.assertEqual(assess_e1(r,self.lanes)['exitCode'],2)
    def test_missing_lane(self):
        self.report['requiredLanes']=self.lanes[:-1];self.assertEqual(assess_e1(self.report,self.lanes)['exitCode'],2)
    def test_identity_changes_fail(self):
        for name in self.identity:
            r=dict(self.identity);r[name]=9999 if type(r[name]) is int else 'other'
            with self.subTest(name=name):self.assertEqual(assess_e2(r,self.identity)['exitCode'],1)
    def test_same_device_fails_even_if_plan_wrong(self):
        r=dict(self.identity,piiSerial=self.identity['pushSerial'])
        self.assertEqual(assess_e2(r,r)['exitCode'],1)
    def test_same_endpoints_fail_even_if_plan_wrong(self):
        r=dict(self.identity,adbBuildPort=5037);self.assertEqual(assess_e2(r,r)['exitCode'],1)
