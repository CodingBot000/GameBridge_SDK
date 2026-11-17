"""Exercise full GUI input validation with disposable byte fixtures, never real builds."""
import contextlib, copy, importlib.util, io, json, os, shutil, subprocess, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import gui_verification as gui
REAL_ROOT=Path(__file__).resolve().parent.parent


@contextlib.contextmanager
def fixture(variant):
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);project=root/'artifacts/owned/project';stage=root/'stage';project.mkdir(parents=True);stage.mkdir()
        sources={'Assets/Editor/GameBridgeGuiVerification.cs':'tests/UnityGuiVerification/GameBridgeGuiVerification.cs',
                 'Assets/Editor/GuiAndroidBuild.cs':'tests/UnityGuiVerification/GuiAndroidBuild.cs',
                 'Assets/Editor/BuildMockPlayer.cs':'tests/UnityAndroidMockConsumer/BuildMockPlayer.cs',
                 'Assets/MockPlayerScenario.cs':'tests/'+gui.ANDROID_SCENARIOS[variant]+'/MockPlayerScenario.cs'}
        sources.update({'Assets/'+target:source for target,source in gui.auxiliary_sources(variant)})
        for target,source in sources.items():
            for dest in (root/source,project/target):dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(REAL_ROOT/source,dest)
        lines=[]
        for i in range(147):
            relative=f'com.gamebridge.sdk/fixture-{i}.txt'
            for dest in (stage/relative,project/'Packages'/relative):dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(f'unit fixture {i}')
            lines.append(gui.file_hash(stage/relative)+'  '+relative)
        (stage/'SHA256SUMS').write_text('\n'.join(lines)+'\n');shutil.copyfile(stage/'SHA256SUMS',project/'GameBridgeStaging.SHA256SUMS')
        for name,version in [('com.unity.mobile.notifications','2.5.0'),('com.unity.nuget.newtonsoft-json','3.2.2')]:
            p=project/'Packages'/name;p.mkdir();(p/'package.json').write_text(json.dumps(dict(name=name,version=version)))
        apk=project.parent/'fixture.apk';apk.write_bytes(b'unit byte fixture, not an actual APK')
        c=dict(schemaVersion=1,runId='a'*32,sourceHead='b'*40,projectRoot=str(project),outputPath=str(apk),variant=variant,operation='android',expectedUnityVersion='6000.5.8f1')
        for key,target in [('scriptSha256','Assets/Editor/GameBridgeGuiVerification.cs'),('adapterSha256','Assets/Editor/GuiAndroidBuild.cs'),('buildScriptSha256','Assets/Editor/BuildMockPlayer.cs'),('scenarioSha256','Assets/MockPlayerScenario.cs')]:c[key]=gui.file_hash(project/target)
        c['stagingManifestSha256']=gui.file_hash(stage/'SHA256SUMS');config=project/'GameBridgeGuiRun.json';config.write_text(json.dumps(c))
        os.utime(config,ns=(1_000_000_000,1_000_000_000))
        log=project/'Logs/Editor.log';log.parent.mkdir();log.write_text('GB_GUI_ANDROID_STARTED '+c['runId']+'\nGB_MOCK_BUILD PASS\nGB_GUI_ANDROID_PASS '+c['runId']+'\n')
        value=dict(c,status='PASS',isBatchMode=False,unityVersion=c['expectedUnityVersion'],method='GuiAndroidBuild.Build',originalBuilderReturned=True,packageFilesVerified=147,artifactSize=apk.stat().st_size,artifactSha256=gui.file_hash(apk),editorLogPath=str(log),editorPid=42)
        receipt=project/'GameBridgeGuiResults'/(c['runId']+'.json');receipt.parent.mkdir();receipt.write_text(json.dumps(value))
        with patch.object(gui,'__file__',str(root/'harness/gui_verification.py')),patch.object(gui.subprocess,'run',return_value=subprocess.CompletedProcess([],0)):
            yield root,project,stage,receipt,apk


class AndroidVariantTests(unittest.TestCase):
    def test_full_push_and_utf8_input_accept_exact_source_package_bytes(self):
        for variant in ('push','utf8'):
            with self.subTest(variant=variant),fixture(variant) as (_,p,s,r,a):self.assertEqual(gui.load_android_build(p,r,s,'b'*40,variant)['apk'],a)

    def test_wrong_variant_or_receipt_correlation_rejected(self):
        with fixture('push') as (_,p,s,r,a):
            with self.assertRaises(ValueError):gui.load_android_build(p,r,s,'b'*40,'utf8')
            v=json.loads(r.read_text());v['runId']='c'*32;r.write_text(json.dumps(v))
            with self.assertRaises(ValueError):gui.load_android_build(p,r,s,'b'*40,'push')

    def test_missing_or_mutated_push_auxiliary_rejected(self):
        for name in ('LateCallbackProbe.cs','link.xml'):
            for remove in (True,False):
                with self.subTest(name=name,remove=remove),fixture('push') as (_,p,s,r,a):
                    target=p/'Assets'/name
                    if remove:target.unlink()
                    else:target.write_text('mutated')
                    with self.assertRaises((OSError,ValueError)):gui.load_android_build(p,r,s,'b'*40,'push')

    def test_changed_scenario_apk_package_or_cache_rejected(self):
        for kind in ('scenario','apk','package','cache'):
            with self.subTest(kind=kind),fixture('utf8') as (_,p,s,r,a):
                target={'scenario':p/'Assets/MockPlayerScenario.cs','apk':a,'package':p/'Packages/com.gamebridge.sdk/fixture-1.txt','cache':p/'Packages/com.unity.mobile.notifications/package.json'}[kind]
                target.write_text('{"name":"other","version":"0"}' if kind=='cache' else 'mutated')
                with self.assertRaises((OSError,ValueError)):gui.load_android_build(p,r,s,'b'*40,'utf8')

    def test_old_receipt_apk_nonancestor_or_protected_diff_rejected(self):
        for kind in ('receipt','apk','ancestor','protected'):
            with self.subTest(kind=kind),fixture('push') as (_,p,s,r,a):
                if kind in ('receipt','apk'):os.utime(r if kind=='receipt' else a,ns=(0,0))
                result=[subprocess.CompletedProcess([],1)] if kind=='ancestor' else [subprocess.CompletedProcess([],0),subprocess.CompletedProcess([],1)]
                context=patch.object(gui.subprocess,'run',side_effect=result) if kind in ('ancestor','protected') else contextlib.nullcontext()
                with context,self.assertRaises(ValueError):gui.load_android_build(p,r,s,'b'*40,'push')

    def test_invalid_push_gui_input_stops_before_adb_backend_or_batch(self):
        spec=importlib.util.spec_from_file_location('push_gui_gate',REAL_ROOT/'harness/run-unity-android-mock-push-e2e.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'artifacts').mkdir();stage=root/'stage';stage.mkdir()
            def command(parts,*a,**kw):
                if parts[:3]==['git','rev-parse','HEAD']:return 'b'*40
                if parts[:2]==['git','status']:return ''
                if str(parts[0])=='bash':raise AssertionError('batch fallback')
                return 'fixture'
            argv=['push','--run-local','--staging',str(stage),'--serial','emulator-5596','--expected-avd','GameBridge_V2_unit','--expected-emulator-pid','42','--expected-adb-server-pid','43','--gui-project',str(root/'project'),'--gui-build-receipt',str(root/'bad.json')]
            with patch.object(m,'ROOT',root),patch('sys.argv',argv),patch.object(m.common,'must',side_effect=command),patch.object(m.common,'verify_staged_source_matches_checkout'),patch.object(m.common,'load_android_build',side_effect=ValueError('invalid')),patch.object(m.common,'locate_adb') as adb,patch.object(m.common,'start_backend') as backend,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(m.main(),1);adb.assert_not_called();backend.assert_not_called()
                result=json.loads(next((root/'artifacts').glob('*/result.json')).read_text());self.assertEqual(result['errorCode'],'GUI_BUILD_INPUT_INVALID')

if __name__=='__main__':unittest.main()
