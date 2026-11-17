import contextlib,importlib.util,io,json,os,shutil,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import gui_verification as gui
from test_gui_android_variants import fixture as android_fixture,REAL_ROOT

@contextlib.contextmanager
def fixture():
    with android_fixture('push') as (root,p,stage,receipt,apk):
        c=json.loads((p/'GameBridgeGuiRun.json').read_text())
        for key,dest,source in [('adapterSha256','Assets/Editor/GuiIosExport.cs','tests/UnityGuiVerification/GuiIosExport.cs'),('buildScriptSha256','Assets/Editor/BuildMockIosPlayer.cs','tests/UnityIosMockConsumer/BuildMockIosPlayer.cs'),('scenarioSha256','Assets/MockIosPlayerScenario.cs','tests/UnityIosPushConsumer/MockIosPlayerScenario.cs')]:
            for target in (p/dest,root/source):target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(REAL_ROOT/source,target)
            c[key]=gui.file_hash(p/dest)
        out=p.parent/'xcode';pbx=out/'Unity-iPhone.xcodeproj/project.pbxproj';pbx.parent.mkdir(parents=True);pbx.write_text('unit fixture only');(out/'fixture.cpp').write_text('fixture')
        c.update(operation='ios',outputPath=str(out));config=p/'GameBridgeGuiRun.json';config.write_text(json.dumps(c));os.utime(config,ns=(1_000_000_000,1_000_000_000))
        log=p/'Logs/Editor.log';log.write_text('GB_GUI_IOS_STARTED '+c['runId']+'\nGB_IOS_MOCK_EXPORT PASS\nGB_GUI_IOS_PASS '+c['runId']+'\n');digest,count=gui.export_tree_hash(out)
        v=dict(c,status='PASS',isBatchMode=False,unityVersion=c['expectedUnityVersion'],method='GuiIosExport.Export',originalBuilderReturned=True,packageFilesVerified=147,artifactFileCount=count,artifactSha256=digest,pbxprojSha256=gui.file_hash(pbx),editorPid=42,editorLogPath=str(log));receipt.write_text(json.dumps(v))
        yield root,p,stage,receipt,out

def load():
    spec=importlib.util.spec_from_file_location('ios_gui_push',REAL_ROOT/'harness/run-unity-ios-mock-push-e2e.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class IosPushGuiTests(unittest.TestCase):
    def test_full_push_export_exact_sources_and_tree_accepted(self):
        with fixture() as (_,p,s,r,out):self.assertEqual(gui.load_ios_export(p,r,s,'b'*40,'push')['output'],out.resolve())

    def test_other_variant_missing_auxiliary_modified_source_tree_and_stale_receipt_rejected(self):
        for kind in ('variant','aux','source','tree','stale'):
            with self.subTest(kind=kind),fixture() as (_,p,s,r,out):
                variant='standard' if kind=='variant' else 'push'
                if kind=='aux':(p/'Assets/LateCallbackProbe.cs').unlink()
                if kind=='source':(p/'Assets/MockIosPlayerScenario.cs').write_text('mutated')
                if kind=='tree':(out/'fixture.cpp').write_text('mutated')
                if kind=='stale':os.utime(r,ns=(0,0))
                with self.assertRaises((ValueError,OSError)):gui.load_ios_export(p,r,s,'b'*40,variant)

    def test_invalid_export_stops_before_xcode_backend_simulator_and_batch(self):
        m=load()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'artifacts').mkdir();stage=root/'stage';stage.mkdir()
            def command(parts,*a,**kw):return 'b'*40 if parts[:3]==['git','rev-parse','HEAD'] else ''
            argv=['ios','--run-local','--staging',str(stage),'--gui-project',str(root/'project'),'--gui-export-receipt',str(root/'bad')]
            with patch.object(m,'ROOT',root),patch('sys.argv',argv),patch.object(m.common,'must',side_effect=command),patch.object(m.common,'run') as run,patch.object(m.common,'verify_staged_source_matches_checkout'),patch.object(m,'load_ios_export',side_effect=ValueError('modified')),patch.object(m.common,'start_backend') as backend,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(m.main(),1);run.assert_not_called();backend.assert_not_called()
            result=json.loads(next((root/'artifacts').glob('*/result.json')).read_text());self.assertEqual(result['errorCode'],'GUI_EXPORT_INPUT_INVALID')

    def test_owned_simulator_cleanup_case_insensitive_and_fail_closed(self):
        m=load();sim='AAAABBBB-0000-0000-0000-000000000001';name='GameBridge-Unity-iOS-Push-unit'
        for state,other_name in [('Shutdown',name),('Booted',name),('Shutdown','User Simulator')]:
            calls=[]
            def run(cmd,**kw):
                calls.append(cmd)
                if cmd[2]=='shutdown':return subprocess.CompletedProcess([],149)
                return subprocess.CompletedProcess([],0,stdout=json.dumps({'devices':{'runtime':[{'udid':sim.lower(),'name':other_name,'state':state}]}}))
            if state=='Shutdown' and other_name==name:self.assertEqual(m.shutdown_owned_simulator(run,sim,name),149)
            else:
                with self.assertRaises(ValueError):m.shutdown_owned_simulator(run,sim,name)
            self.assertEqual(calls[0],['xcrun','simctl','shutdown',sim]);self.assertFalse(any('delete' in x or 'erase' in x for x in calls))
        with self.assertRaises(ValueError):m.shutdown_owned_simulator(lambda *a,**kw:self.fail('must not execute'),'bad','User Simulator')

if __name__=='__main__':unittest.main()
