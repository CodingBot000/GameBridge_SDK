"""Owned-device startup observations; diagnostics never substitute for E2E verdicts."""
import json
import re
import time
import xml.etree.ElementTree as ET

POINTS = ('awake','start_enter','intent_read','intent_checked','sdk_create_enter','sdk_created',
          'initialize_call','initialize_returned','backend_auth_call','exception',
          'focus_gained','focus_lost','pause_enter','pause_exit')
BUSINESS = POINTS[:10]


class DiagnosticsUnavailable(ValueError):
    pass


def analyze(logcat, pid_text, activity, windows, exit_info, ui_xml, package):
    pids = [int(x) for x in pid_text.split()] if re.fullmatch(r'\s*\d+(?:\s+\d+)*\s*',pid_text) else []
    points = re.findall(r'\bGB_BOOT point=([a-z_]+)\b',logcat)
    points = [p for p in points if p in POINTS]
    distinct = list(dict.fromkeys(points))
    business = [p for p in points if p in BUSINESS]
    failure = re.findall(r'GB_MOCK_RESULT FAIL stage=([a-z-]+) code=([A-Z_]{1,64})',logcat)
    known_guide = 'UNMEASURED'
    if ui_xml is not None:
        try:
            nodes=list(ET.fromstring(ui_xml).iter('node'))
            texts={n.get('text','') for n in nodes if n.get('package')=='com.android.systemui'}
            known_guide='Viewing full screen' in texts and 'Got it' in texts
        except ET.ParseError: pass
    log_lines=logcat.splitlines()
    package_crash=any('FATAL EXCEPTION' in line and re.search(r'Process:\s*'+re.escape(package)+r'\s*,\s*PID:', '\n'.join(log_lines[i:i+7])) for i,line in enumerate(log_lines))
    native_crash=bool(re.search(r'>>>\s*'+re.escape(package)+r'\s*<<<',logcat) and re.search(r'Fatal signal|backtrace:',logcat))
    package_crash=package_crash or native_crash
    native_load = sorted(set(re.findall(r'\b(UnsatisfiedLinkError|dlopen failed|JNI DETECTED ERROR)\b',logcat)))
    # These categories may be system-wide; only package-specific crash/ANR are attributed.
    app_anr = bool(re.search(r'ANR in '+re.escape(package)+r'\b',logcat))
    activity_start = bool(re.search(r'(?:Start proc|am_proc_start)[^\n]*'+re.escape(package),logcat))
    activity_stop = bool(re.search(r'(?:Killing|am_proc_died|Force stopping)[^\n]*'+re.escape(package),logcat))
    resumed = bool(re.search(r'(?:mResumedActivity|topResumedActivity)[^\n]*'+re.escape(package),activity))
    focused = bool(re.search(r'mCurrentFocus[^\n]*'+re.escape(package),windows))
    return dict(appPids=pids, pidObservation='PRESENT' if pids else 'ABSENT', bootPoints=distinct,
        lastBusinessPoint=business[-1] if business else 'UNMEASURED',
        unityEngineInitializationObserved='Initialize engine version:' in logcat,
        activityResumedObserved=resumed, appWindowFocusObserved=focused,
        knownFullscreenGuideObserved=known_guide, appCrashObserved=package_crash,
        appAnrObserved=app_anr, activityManagerStartObserved=activity_start, activityManagerStopObserved=activity_stop, nativeLoadErrorCategories=native_load,
        nativeLoadAttribution='system log categories; not automatically attributed to this app',
        historicalExitInfoAvailable=bool(exit_info.strip()),
        failureMarker=[dict(stage=s,code=c) for s,c in failure[-1:]])


def last_confirmed(summary):
    points=summary.get('bootPoints',[])
    if summary.get('appCrashObserved'):return 'APP_CRASH_OBSERVED'
    if summary.get('appAnrObserved'):return 'APP_ANR_OBSERVED'
    if summary.get('knownFullscreenGuideObserved') is True:return 'KNOWN_FULLSCREEN_GUIDE_OBSERVED'
    if 'initialize_call' in points and 'initialize_returned' not in points:return 'INITIALIZE_CALLED_NO_RETURN_OBSERVED'
    if 'sdk_create_enter' in points and 'sdk_created' not in points:return 'SDK_CREATE_ENTERED_NO_RETURN_OBSERVED'
    if 'backend_auth_call' in points:return 'BACKEND_AUTH_API_CALLED'
    if 'awake' in points and 'start_enter' not in points:return 'AWAKE_WITHOUT_START_OBSERVED'
    if 'start_enter' in points:return 'START_ENTERED'
    return 'NO_MANAGED_ENTRY_OBSERVED'


class Collector:
    def __init__(self, run, adb, serial, package, output, secrets=()):
        self.run=run;self.adb=adb;self.serial=serial;self.package=package;self.output=output
        self.output.mkdir(parents=True,exist_ok=False);self.secrets=tuple(x for x in secrets if x)
        self.start=time.monotonic();self.snapshots=[];self.first_http=None

    def command(self, args, timeout=12):
        return self.run([self.adb,'-s',self.serial,*args],timeout=timeout)

    def save(self, name, text):
        for secret in self.secrets:text=text.replace(secret,'[REDACTED]')
        (self.output/name).write_text(text,encoding='utf-8')

    def capture(self, phase, ui=False, backend_log=None):
        index=len(self.snapshots);prefix=f'{index:02d}-{phase}'
        logs=self.command(['logcat','-d','-b','all','-v','epoch'])
        if logs.returncode or not logs.stdout.strip():
            self.save(prefix+'-logcat-error.log',logs.stdout)
            raise DiagnosticsUnavailable('mandatory all-buffer logcat unavailable')
        self.save(prefix+'-logcat.log',logs.stdout)
        pid=self.command(['shell','pidof',self.package]);pid_status=pid.returncode
        if pid_status not in (0,1) or (pid_status==0 and not re.fullmatch(r'\s*\d+(?:\s+\d+)*\s*',pid.stdout)):
            raise DiagnosticsUnavailable('package PID query unavailable or malformed')
        activity=self.command(['shell','dumpsys','activity','activities'])
        windows=self.command(['shell','dumpsys','window','windows'])
        exits=self.command(['shell','dumpsys','activity','exit-info',self.package])
        for label,result in [('pid',pid),('activity',activity),('window',windows),('exit-info',exits)]:
            self.save(prefix+'-'+label+'.log',result.stdout)
        xml=None;ui_code=None
        if ui:
            path='/sdcard/gamebridge-startup-diagnostics.xml'
            try:
                dumped=self.command(['shell','uiautomator','dump',path],timeout=12);ui_code=dumped.returncode
                self.save(prefix+'-ui-command.log',dumped.stdout)
            except Exception as error:
                # Optional UI idle probing may time out while Unity is starting.
                # Ownership changes and all other errors must still propagate.
                if str(error)!='COMMAND_UNAVAILABLE_OR_TIMEOUT':raise
                ui_code=124
                self.save(prefix+'-ui-command.log','UI hierarchy unavailable: command timeout\n')
            if ui_code==0:
                read=self.command(['shell','cat',path]);ui_code=read.returncode
                if ui_code==0:xml=read.stdout;self.save(prefix+'-ui.xml',xml)
        summary=analyze(logs.stdout,pid.stdout,activity.stdout if activity.returncode==0 else '',
            windows.stdout if windows.returncode==0 else '',exits.stdout if exits.returncode==0 else '',xml,self.package)
        summary.update(phase=phase,observedAfterSeconds=round(time.monotonic()-self.start,3),
            queryExitCodes=dict(logcat=logs.returncode,pid=pid_status,activity=activity.returncode,window=windows.returncode,exitInfo=exits.returncode,ui=ui_code))
        if activity.returncode:summary['activityResumedObserved']='UNMEASURED'
        if windows.returncode:summary['appWindowFocusObserved']='UNMEASURED'
        if exits.returncode:summary['historicalExitInfoAvailable']='UNMEASURED'
        summary['observationCategory']=last_confirmed(summary)
        if backend_log is not None and backend_log.exists():
            text=backend_log.read_text(errors='replace')
            seen=re.findall(r'LOCAL_MOCK_TRACE operation=([a-z-]+) method=(?:GET|POST) requestId=[0-9a-fA-F-]{36} status=(\d+)',text)
            summary['backendTraceOperationsObserved']=list(dict.fromkeys(op for op,_ in seen))
            if seen and self.first_http is None:self.first_http=summary['observedAfterSeconds']
        self.snapshots.append(summary)
        (self.output/'summary.json').write_text(json.dumps({'scope':'startup observations only; never E2E PASS',
            'snapshots':self.snapshots,'firstHttpTraceObservedAfterSeconds':self.first_http,
            'processExitObserved':any(x['appPids'] for x in self.snapshots[:-1]) and not summary['appPids']},indent=2)+'\n')
        return summary
