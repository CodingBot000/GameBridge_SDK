"""Read-only process/port attestation for an explicitly owned local emulator."""
import re
import os
import shlex
import subprocess
from pathlib import Path

class BindingError(ValueError):pass


def validate_adb_environment(environment=None):
    env=os.environ if environment is None else environment
    # Guarded commands use the attested local endpoint, never an ambient override.
    if env.get('ADB_SERVER_SOCKET') or env.get('ANDROID_ADB_SERVER_ADDRESS') or any(env.get(name) not in (None,'','5037') for name in ('ANDROID_ADB_SERVER_PORT','ADB_SERVER_PORT')):
        raise BindingError('ADB_SERVER_ENDPOINT_OVERRIDE_REFUSED')


class GuiAdbGuard:
    """Only the already-running matching SDK server and one owned emulator."""
    def __init__(self, adb, server_pid, serial, avd, emulator_pid):
        self.adb=Path(adb).resolve(); self.server_pid=int(server_pid)
        self.serial=serial; self.avd=avd; self.emulator_pid=int(emulator_pid)

    def attest(self, command):
        validate_adb_environment()
        inspect_binding(self.serial,self.avd,self.emulator_pid)
        if _port_owners(5037)!={self.server_pid}:
            raise BindingError('ADB_SERVER_PORT_OWNER_CHANGED')
        p=subprocess.run(['lsof','-p',str(self.server_pid),'-d','txt','-Fn'],capture_output=True,text=True,timeout=5)
        paths={Path(l[1:]).resolve() for l in p.stdout.splitlines() if l.startswith('n') and l.endswith('/adb')}
        if p.returncode or self.adb not in paths:
            raise BindingError('ADB_SERVER_EXECUTABLE_MISMATCH')
        args=[str(x) for x in command]
        if not args or Path(args[0]).resolve()!=self.adb:
            raise BindingError('ADB_CLIENT_EXECUTABLE_MISMATCH')
        if args[1:]==['devices']:return
        if len(args)<4 or args[1:3]!=['-s',self.serial] or args[3] not in ('emu','shell','install','logcat'):
            raise BindingError('UNSCOPED_ADB_COMMAND_REJECTED')


def _process_arguments(pid):
    command=subprocess.check_output(['ps','-p',str(pid),'-o','comm='],text=True,timeout=5).strip()
    if 'qemu-system' not in command:raise BindingError('EMULATOR_PID_NOT_QEMU')
    return shlex.split(subprocess.check_output(['ps','-p',str(pid),'-o','args='],text=True,timeout=5).strip())


def _port_owners(port):
    process=subprocess.run(['lsof','-nP','-t',f'-iTCP:{port}','-sTCP:LISTEN'],text=True,capture_output=True,timeout=5)
    if process.returncode not in (0,1):raise BindingError('PORT_OWNER_QUERY_UNAVAILABLE')
    return {int(x) for x in process.stdout.split() if x.isdecimal()}


def inspect_binding(serial, avd, expected_pid):
    try:
        if not isinstance(expected_pid,(str,int)) or isinstance(expected_pid,bool):raise ValueError()
        pid=int(expected_pid)
        match=re.fullmatch(r'emulator-(\d+)',serial or '')
        if pid<=0 or not match or not avd.startswith('GameBridge_V2_'):raise ValueError()
        port=int(match.group(1))
        if port<1024 or port>=65535 or port%2:raise ValueError()
        args=_process_arguments(pid)
        if args[args.index('-avd')+1]!=avd:raise BindingError('EMULATOR_PROCESS_AVD_MISMATCH')
        if args[args.index('-port')+1]!=str(port):raise BindingError('EMULATOR_CONSOLE_ARGUMENT_MISMATCH')
        if any(_port_owners(value)!={pid} for value in (port,port+1)):
            raise BindingError('EMULATOR_PORT_OWNER_MISMATCH')
        return {'pid':pid,'serial':serial,'avd':avd,'consolePort':port,'adbPort':port+1,'portsOwned':True}
    except BindingError:raise
    except (OSError,ValueError,IndexError,subprocess.SubprocessError):raise BindingError('EMULATOR_BINDING_UNAVAILABLE') from None
