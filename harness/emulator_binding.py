"""Read-only process/port attestation for an explicitly owned local emulator."""
import re
import shlex
import subprocess

class BindingError(ValueError):pass


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
