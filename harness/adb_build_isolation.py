"""Owned temporary ADB endpoint for batch builders; never replace an existing server."""
from contextlib import contextmanager
import json,os,subprocess,time
from pathlib import Path
from emulator_binding import _port_owners,BindingError

@contextmanager
def isolated_build_endpoint(adb,port,output,environment):
    if type(port) is not int or not 1024<=port<=65535 or port==5037:raise BindingError('INVALID_BUILD_ADB_PORT')
    if _port_owners(port):raise BindingError('BUILD_ADB_PORT_ALREADY_OWNED')
    adb=Path(adb).resolve();process=None;log=(Path(output)/'build-adb-server.log').open('w')
    env=dict(environment)
    for key in ('ADB_SERVER_SOCKET','ANDROID_ADB_SERVER_ADDRESS','ANDROID_ADB_SERVER_PORT','ADB_SERVER_PORT'):env.pop(key,None)
    try:
        # Binding directly is atomic; a port race exits instead of killing another daemon.
        process=subprocess.Popen([str(adb),'-L','tcp:'+str(port),'server','nodaemon'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        deadline=time.monotonic()+10
        while process.poll() is None and time.monotonic()<deadline:
            if _port_owners(port)=={process.pid}:break
            time.sleep(.1)
        if process.poll() is not None or _port_owners(port)!={process.pid}:raise BindingError('BUILD_ADB_OWNERSHIP_UNAVAILABLE')
        exe=subprocess.run(['lsof','-p',str(process.pid),'-d','txt','-Fn'],capture_output=True,text=True,timeout=5)
        if exe.returncode or 'n'+str(adb) not in exe.stdout.splitlines():raise BindingError('BUILD_ADB_EXECUTABLE_MISMATCH')
        (Path(output)/'build-adb-binding.json').write_text(json.dumps(dict(pid=process.pid,port=port,adbExecutable=str(adb),scope='owned temporary build endpoint; runtime endpoint unchanged'),indent=2)+'\n')
        env.update(ADB_SERVER_SOCKET='tcp:'+str(port),ANDROID_ADB_SERVER_PORT=str(port))
        yield env
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:process.kill();process.wait()
        log.close()
