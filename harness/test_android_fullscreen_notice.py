import unittest
from android_fullscreen_notice import known_guide_button


class FullscreenNoticeTests(unittest.TestCase):
    def xml(self,package='android'):
        return '<hierarchy><node package="'+package+'" text="Viewing full screen"/><node package="'+package+'" text="Got it" enabled="true" bounds="[100,200][300,260]"/></hierarchy>'

    def test_framework_and_systemui_known_notice(self):
        for p in ('android','com.android.systemui'):self.assertEqual(known_guide_button(self.xml(p)),(200,230))

    def test_other_app_and_permission_prompts_rejected(self):
        for xml in (self.xml('com.gamebridge.sdk.mockconsumer'),self.xml().replace('Viewing full screen','Allow notifications?')):
            with self.assertRaises(ValueError):known_guide_button(xml)

    def test_ambiguous_disabled_or_missing_button_rejected(self):
        for xml in (self.xml().replace('enabled="true"','enabled="false"'),self.xml().replace('</hierarchy>','<node package="android" text="Got it"/></hierarchy>'),self.xml().replace('Got it','Allow')):
            with self.assertRaises(ValueError):known_guide_button(xml)

    def test_bad_geometry_or_xml_rejected(self):
        for xml in (self.xml().replace('[100,200][300,260]','[300,200][100,260]'),'<broken'):
            with self.assertRaises(ValueError):known_guide_button(xml)
