#!/usr/bin/env python3
"""Opt-in Kotlin Bridge -> local-mock Backend/DB test (NOT a Unity Player test).

Creates a dedicated random PostgreSQL database, requires an empty GameBridge_V2_
emulator, and retains both after testing. Never uninstalls an existing app.
Override tool paths/device with CLI flags or GAMEBRIDGE_* environment variables.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_OPS = ("sdk.initialize", "auth.signIn", "store.products",
                "store.purchase", "store.entitlements", "auth.signOut")
SERVER_OPS = ("mock-auth", "catalog", "entitlements", "verify", "logout")


def execute(command, *, input_text=None, timeout=120, env=None):
    return subprocess.run([str(value) for value in command], cwd=ROOT, input=input_text,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, timeout=timeout, env=env)


def require(command, message, **kwargs):
    response = execute(command, **kwargs)
    if response.returncode:
        raise RuntimeError(message)
    return response.stdout


def adb_path(configured):
    paths = [configured, shutil.which("adb")]
    for name in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        if os.environ.get(name):
            paths.append(str(Path(os.environ[name]) / "platform-tools" / "adb"))
    paths.append(str(Path.home() / "Library/Android/sdk/platform-tools/adb"))
    return next((path for path in paths if path and Path(path).is_file()), None)


def choose_emulator(adb, requested, expected):
    device_lines = require([adb, "devices"], "ADB_UNAVAILABLE").splitlines()[1:]
    devices = [line.split()[0] for line in device_lines
               if len(line.split()) > 1 and line.split()[1] == "device"
               and line.split()[0].startswith("emulator-")]
    if not requested and len(devices) != 1:
        raise RuntimeError("SPECIFY_DEDICATED_GAMEBRIDGE_EMULATOR")
    serial = requested or devices[0]
    if serial not in devices:
        raise RuntimeError("DEVICE_NOT_AN_ONLINE_EMULATOR")
    lines = require([adb, "-s", serial, "emu", "avd", "name"], "AVD_NAME_UNAVAILABLE").splitlines()
    name = next((line.strip() for line in lines if line.strip() and line.strip() != "OK"), "")
    if not name.startswith("GameBridge_V2_") or (expected and name != expected):
        raise RuntimeError("NOT_DEDICATED_GAMEBRIDGE_AVD")
    packages = require([adb, "-s", serial, "shell", "pm", "list", "packages", "com.gamebridge.sample"],
                       "PACKAGE_LOOKUP_FAILED").splitlines()
    if "package:com.gamebridge.sample" in packages:
        raise RuntimeError("EXISTING_APP_PRESERVED_USE_NEW_AVD")
    return serial, name


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-local", action="store_true", required=True)
    parser.add_argument("--adb", default=os.environ.get("GAMEBRIDGE_ADB"))
    parser.add_argument("--serial", default=os.environ.get("GAMEBRIDGE_ANDROID_SERIAL"))
    parser.add_argument("--expected-avd", default=os.environ.get("GAMEBRIDGE_TEST_AVD_NAME"))
    parser.add_argument("--postgres-container", default=os.environ.get("GAMEBRIDGE_TEST_POSTGRES_CONTAINER",
                                                                        "gamebridge-sdk-local-postgres-1"))
    parser.add_argument("--postgres-admin", default=os.environ.get("GAMEBRIDGE_TEST_POSTGRES_ADMIN", "gamebridge"))
    parser.add_argument("--postgres-port", type=int,
                        default=int(os.environ.get("GAMEBRIDGE_TEST_POSTGRES_PORT", "54329")))
    args = parser.parse_args()

    (ROOT / "artifacts").mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="android-mock-bridge-e2e-", dir=ROOT / "artifacts"))
    result = {
        "status": "NOT_RUN", "scope": "Android Kotlin Bridge -> isolated LOCAL_MOCK Backend/DB, not Unity",
        "sourceHead": require(["git", "rev-parse", "HEAD"], "GIT_SHA_UNAVAILABLE").strip(),
        "sourceTrackedDirty": bool(require(["git", "status", "--porcelain", "--untracked-files=no"],
                                           "GIT_STATUS_UNAVAILABLE").strip()),
        "unityPlayer": "NOT_RUN", "realGoogleLogin": "NOT_RUN", "realStorePurchase": "NOT_RUN",
        "retainsTestDatabase": True,
    }
    server = None
    logfile = None
    try:
        adb = adb_path(args.adb)
        if adb is None:
            raise RuntimeError("ADB_UNAVAILABLE")
        expected = args.expected_avd
        avd_marker = ROOT / "artifacts/v2-test-avd-name.txt"
        if not expected and avd_marker.is_file():
            expected = avd_marker.read_text(encoding="utf-8").strip()
        serial, avd = choose_emulator(adb, args.serial, expected)
        result["emulatorAvd"] = avd
        if not re.fullmatch(r"gamebridge-sdk-local-[A-Za-z0-9_.-]*postgres-[0-9]+", args.postgres_container):
            raise RuntimeError("REFUSE_NON_LOCAL_POSTGRES_CONTAINER")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", args.postgres_admin):
            raise RuntimeError("INVALID_POSTGRES_ADMIN")
        with socket.create_connection(("127.0.0.1", args.postgres_port), timeout=3):
            pass
        database = "gamebridge_ci_" + secrets.token_hex(5)
        password = secrets.token_hex(24)
        # Values are generated locally and cannot contain SQL delimiters.
        for statement in (f"CREATE ROLE {database} LOGIN PASSWORD '{password}';\n",
                          f"CREATE DATABASE {database} OWNER {database};\n"):
            require(["docker", "exec", "-i", args.postgres_container, "psql", "-X",
                     "-U", args.postgres_admin, "-d", "postgres", "-v", "ON_ERROR_STOP=1"],
                    "LOCAL_DB_CREATE_FAILED", input_text=statement)
        result["database"] = database
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        key = "local-v2-" + secrets.token_hex(24)
        backend_jar = ROOT / "backend/build/libs/gamebridge-backend.jar"
        if not backend_jar.is_file():
            raise RuntimeError("BACKEND_JAR_MISSING_BUILD_FIRST")
        result["backendJarSha256"] = sha256(backend_jar)
        env = os.environ.copy()
        env.update({
            "SPRING_PROFILES_ACTIVE": "local-mock",
            "DATABASE_URL": f"jdbc:postgresql://127.0.0.1:{args.postgres_port}/{database}",
            "DATABASE_USERNAME": database, "DATABASE_PASSWORD": password,
            "GAMEBRIDGE_PORT": str(port), "GAMEBRIDGE_DEV_AUTH_KEY": key,
            "SERVER_TOKEN_ENCRYPTION_KEY": base64.b64encode(secrets.token_bytes(32)).decode(),
            "GAMEBRIDGE_MAINTENANCE_ENABLED": "false",
            "GAMEBRIDGE_LOCAL_TRACE_ENABLED": "true",
        })
        logfile = (output / "server.log").open("w", encoding="utf-8")
        server = subprocess.Popen(["java", "-jar", str(backend_jar)], cwd=ROOT, env=env,
                                  stdout=logfile, stderr=subprocess.STDOUT)
        for _ in range(160):
            if server.poll() is not None:
                raise RuntimeError("BACKEND_TERMINATED_EARLY")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as response:
                    if response.status == 200:
                        break
            except Exception:
                time.sleep(.25)
        else:
            raise RuntimeError("BACKEND_HEALTH_TIMEOUT")
        for path in ("android/sample-app/build/outputs/apk/debug/sample-app-debug.apk",
                     "android/sample-app/build/outputs/apk/androidTest/debug/sample-app-debug-androidTest.apk"):
            require([adb, "-s", serial, "install", ROOT / path], "TEST_APK_INSTALL_FAILED", timeout=90)
        # Test key is synthetic and passed to an isolated dedicated AVD; never print argv.
        invocation = [adb, "-s", serial, "shell", "am", "instrument", "-w", "-e", "class",
                      "com.gamebridge.sample.LocalMockBridgeDeviceTest", "-e", "gamebridge_mock_url",
                      f"http://10.0.2.2:{port}", "-e", "gamebridge_mock_key", key,
                      "com.gamebridge.sample.test/androidx.test.runner.AndroidJUnitRunner"]
        test = execute(invocation, timeout=150)
        (output / "instrumentation.log").write_text(test.stdout.replace(key, "[REDACTED]"), encoding="utf-8")
        if test.returncode or not re.search(r"OK \(1 test\)", test.stdout) or "FAILURES!!!" in test.stdout:
            raise RuntimeError("ANDROID_INSTRUMENTATION_FAILED")
        device = require([adb, "-s", serial, "logcat", "-d", "-v", "brief",
                          "-s", "GB_NATIVE_E2E:I", "*:S"], "NATIVE_LOGCAT_FAILED", timeout=20)
        native = "\n".join(line for line in device.splitlines() if "GB_NATIVE_E2E" in line) + "\n"
        if key in native or password in native:
            raise RuntimeError("SECRET_LEAK_NATIVE_LOG")
        for operation in REQUIRED_OPS:
            if not re.search(r"operation=" + re.escape(operation)
                             + r" requestId=[0-9a-fA-F-]{36} status=PASS", native):
                raise RuntimeError("MISSING_NATIVE_REQUEST_" + operation)
        (output / "native-requests.log").write_text(native, encoding="utf-8")
        logfile.flush()
        server_trace = (output / "server.log").read_text(encoding="utf-8", errors="replace")
        if key in server_trace or password in server_trace:
            raise RuntimeError("SECRET_LEAK_SERVER_LOG")
        for operation in SERVER_OPS:
            if not re.search(r"LOCAL_MOCK_TRACE operation=" + operation
                             + r" method=(?:GET|POST) requestId=[0-9a-fA-F-]{36} status=200",
                             server_trace):
                raise RuntimeError("MISSING_BACKEND_TRACE_" + operation)
        sql = "SELECT count(*), coalesce(sum(delta),0) FROM wallet_ledger;\n"
        ledger = require(["docker", "exec", "-i", args.postgres_container, "psql", "-X",
                          "-U", args.postgres_admin, "-d", database, "-t", "-A", "-v", "ON_ERROR_STOP=1"],
                         "LEDGER_QUERY_FAILED", input_text=sql)
        if ledger.strip() != "1|100":
            raise RuntimeError("LEDGER_ASSERTION_FAILED")
        result.update(status="PASS", tests=1, skipped=0, ledgerCount=1, ledgerDelta=100,
                      nativeOperations=list(REQUIRED_OPS), backendOperations=list(SERVER_OPS))
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        result.update(status="FAIL", errorCode=str(error) if isinstance(error, RuntimeError)
                      else type(error).__name__)
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()
        if logfile is not None:
            logfile.close()
        (output / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                                            encoding="utf-8")
    print("RESULT", result["status"], result.get("errorCode", ""), "EVIDENCE", output.relative_to(ROOT))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
