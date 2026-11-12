import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('permission_os',Path(__file__).parent/'run-unity-android-permission-os.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class PermissionOsTests(unittest.TestCase):
    def test_only_unique_explicit_deny_button_is_selected(self):
        node='<node resource-id="com.android.permissioncontroller:id/permission_deny_button" text="deny" bounds="[10,20][50,60]"/>'
        self.assertEqual(module.button_center('<?xml version="1.0"?><hierarchy>'+node+'</hierarchy>'),(30,40))
        alternate=node.replace('permission_deny_button','permission_deny_and_dont_ask_again_button')
        self.assertEqual(module.button_center('<?xml version="1.0"?><hierarchy>'+alternate+'</hierarchy>'),(30,40))
        self.assertIsNone(module.button_center('<?xml version="1.0"?><hierarchy>'+node+node+'</hierarchy>'))
        self.assertIsNone(module.button_center('<?xml version="1.0"?><hierarchy><node text="deny" bounds="[1,2][3,4]"/></hierarchy>'))
        self.assertIsNone(module.button_center('not xml'))
    def test_interaction_mode_never_claims_automation_without_a_tap(self):
        self.assertEqual(module.interaction_mode(0),'EXTERNAL_OR_PREEXISTING')
        self.assertEqual(module.interaction_mode(1),'AUTOMATED_RESOURCE_ID')
    def test_requires_every_os_marker(self):
        self.assertTrue(module.markers_pass('\n'.join(module.REQUIRED)))
        for marker in module.REQUIRED:self.assertFalse(module.markers_pass('\n'.join(x for x in module.REQUIRED if x!=marker)))
if __name__=='__main__':unittest.main()
