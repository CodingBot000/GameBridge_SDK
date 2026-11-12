#!/usr/bin/env python3
"""Opt-in Unity Android Player -> Kotlin -> local-mock Backend/DB acceptance test.

Requires a licensed Unity Editor with Android Build Support, a dedicated GameBridge
emulator, a staged UPM package, and the explicitly local Compose PostgreSQL.
Never installs onto a non-dedicated device, replaces an existing app, or deletes a DB.
The created DB, emulator installation and raw local artifacts are retained.
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
PACKAGE = "com.gamebridge.sdk.mockconsumer"
STEPS = ("initialize", "login", "products", "purchase", "wallet", "logout")
HTTP_OPS = ("mock-auth", "catalog", "entitlements", "verify", "logout")


class GateError(Exception):
    def __init__(self, code, category="FAIL"):
        super().__init__(code)
        self.category = category


def run(command, timeout=120, input_text=None, env=None):
    try:
        return subprocess.run(
            [str(part) for part in command], cwd=ROOT, env=env, input=input_text,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise GateError("COMMAND_UNAVAILABLE_OR_TIMEOUT") from error


def must(command, code, timeout=120, input_text=None, env=None, category="FAIL"):
    result = run(command, timeout=timeout, input_text=input_text, env=env)
    if result.returncode:
        raise GateError(code, category)
    return result.stdout


def locate_adb(configured):
    candidates = [configured, shutil.which("adb")]
    for variable in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        root = os.environ.get(variable)
        if root:
            candidates.append(str(Path(root) / "platform-tools" / "adb"))
    candidates.append(str(Path.home() / "Library/Android/sdk/platform-tools/adb"))
    return next((candidate for candidate in candidates if candidate and Path(candidate).is_file()), None)


def find_dedicated_device(adb, serial, expected_avd):
    lines = must([adb, "devices"], "ADB_UNAVAILABLE", category="DEFERRED_ENV").splitlines()
    online = [line.split()[0] for line in lines[1:] if len(line.split()) >= 2 and line.split()[1] == "device"]
    emulators = [entry for entry in online if entry.startswith("emulator-")]
    if not serial:
        if len(emulators) != 1:
            raise GateError("SPECIFY_DEDICATED_EMULATOR_SERIAL", "DEFERRED_ENV")
        serial = emulators[0]
    if serial not in emulators:
        raise GateError("TARGET_NOT_AN_ONLINE_EMULATOR", "DEFERRED_ENV")
    output = must([adb, "-s", serial, "emu", "avd", "name"], "EMULATOR_NAME_UNAVAILABLE", category="DEFERRED_ENV")
    avd = next((line.strip() for line in output.splitlines() if line.strip() not in ("OK", "")), "")
    if not avd.startswith("GameBridge_V2_") or (expected_avd and expected_avd != avd):
        raise GateError("NOT_THE_DEDICATED_GAMEBRIDGE_AVD", "DEFERRED_ENV")
    packages = must([adb, "-s", serial, "shell", "pm", "list", "packages", PACKAGE], "PACKAGE_QUERY_FAILED", category="DEFERRED_ENV")
    if "package:" + PACKAGE in packages.splitlines():
        raise GateError("TEST_APP_ALREADY_INSTALLED_PRESERVE_EXISTING", "DEFERRED_ENV")
    return serial, avd


def wait_for_dedicated_device(adb, serial, expected_avd, timeout=45):
    """Unity may restart ADB during a build; wait for the same AVD to reappear."""
    deadline = time.monotonic() + timeout
    while True:
        try:
            return find_dedicated_device(adb, serial, expected_avd)
        except GateError as error:
            if str(error) not in ("ADB_UNAVAILABLE", "TARGET_NOT_AN_ONLINE_EMULATOR"):
                raise
            if time.monotonic() >= deadline:
                raise GateError("DEDICATED_EMULATOR_REDISCOVERY_TIMEOUT", "DEFERRED_ENV") from error
            time.sleep(1)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_staged_source_matches_checkout(staging):
    """Reject a UPM staging folder containing an older Unity SDK source tree."""
    source = ROOT / "unity" / "Packages" / "com.gamebridge.sdk"
    packaged = staging / "com.gamebridge.sdk"
    if not source.is_dir() or not packaged.is_dir():
        raise GateError("UPM_SOURCE_MISSING")
    for item in source.rglob("*"):
        if item.is_file():
            copy = packaged / item.relative_to(source)
            if not copy.is_file() or sha256(item) != sha256(copy):
                raise GateError("UPM_STAGING_SOURCE_MISMATCH")


def create_isolated_database(container, admin, port):
    if not re.fullmatch(r"gamebridge-sdk-local-[A-Za-z0-9_.-]*postgres-[0-9]+", container):
        raise GateError("REFUSE_NON_LOCAL_POSTGRES_CONTAINER", "DEFERRED_ENV")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", admin):
        raise GateError("INVALID_POSTGRES_ADMIN", "DEFERRED_ENV")
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=3):
            pass
    except OSError as error:
        raise GateError("LOCAL_POSTGRES_PORT_UNAVAILABLE", "DEFERRED_ENV") from error
    database = "gamebridge_ci_" + secrets.token_hex(5)
    password = secrets.token_hex(24)
    sql = (
        "CREATE ROLE " + database + " LOGIN PASSWORD '" + password + "';\n"
        "CREATE DATABASE " + database + " OWNER " + database + ";\n"
    )
    must(["docker", "exec", "-i", container, "psql", "-X", "-U", admin,
          "-d", "postgres", "-v", "ON_ERROR_STOP=1"], "ISOLATED_DB_CREATION_FAILED",
         input_text=sql, category="DEFERRED_ENV")
    return database, password


def free_local_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def start_backend(jar, output, database, password, dbport):
    port = free_local_port()
    key = "unity-v2-" + secrets.token_hex(24)
    env = os.environ.copy()
    env.update({
        "SPRING_PROFILES_ACTIVE": "local-mock",
        "DATABASE_URL": f"jdbc:postgresql://127.0.0.1:{dbport}/{database}",
        "DATABASE_USERNAME": database,
        "DATABASE_PASSWORD": password,
        "GAMEBRIDGE_PORT": str(port),
        "GAMEBRIDGE_DEV_AUTH_KEY": key,
        "SERVER_TOKEN_ENCRYPTION_KEY": base64.b64encode(secrets.token_bytes(32)).decode(),
        "GAMEBRIDGE_MAINTENANCE_ENABLED": "false",
        "GAMEBRIDGE_LOCAL_TRACE_ENABLED": "true",
    })
    log = (output / "server.log").open("w", encoding="utf-8")
    try:
        server = subprocess.Popen(["java", "-jar", str(jar)], cwd=ROOT, env=env,
                                  stdout=log, stderr=subprocess.STDOUT)
    except OSError as error:
        log.close()
        raise GateError("BACKEND_JAVA_UNAVAILABLE", "DEFERRED_ENV") from error
    try:
        for _ in range(160):
            if server.poll() is not None:
                raise GateError("BACKEND_EXITED")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as reply:
                    if reply.status == 200:
                        return server, log, port, key
            except Exception:
                time.sleep(0.25)
        raise GateError("BACKEND_HEALTH_TIMEOUT")
    except Exception:
        server.terminate()
        try:
            server.wait(timeout=8)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
        log.close()
        raise


def server_trace_status(log, key, password):
    trace = Path(log).read_text(encoding="utf-8", errors="replace")
    if key in trace or password in trace:
        raise GateError("SYNTHETIC_SECRET_IN_SERVER_LOG")
    counts = {}
    for operation in HTTP_OPS:
        pattern = (r"LOCAL_MOCK_TRACE operation=" + re.escape(operation)
                   + r" method=(?:GET|POST) requestId=[0-9a-fA-F-]{36} status=200")
        counts[operation] = len(re.findall(pattern, trace))
        if counts[operation] < 1:
            raise GateError("BACKEND_TRACE_MISSING_" + operation.upper().replace("-", "_"))
    return counts


def scan_unity_log(adb, serial, key, password):
    result = must([adb, "-s", serial, "logcat", "-d", "-v", "brief", "-s", "Unity:I", "*:S"],
                  "UNITY_LOGCAT_UNAVAILABLE", timeout=20)
    if key in result or password in result:
        raise GateError("SYNTHETIC_SECRET_IN_PLAYER_LOG")
    return [line for line in result.splitlines()
            if re.search(r"\b(?:GB_MOCK_(?:STEP|RESULT|NATIVE|REDACTION)|GB_UTF8_JNI_ROUNDTRIP|GB_NATIVE_DEMO_FLOW)\b", line)]


def check_player_markers(lines):
    combined = "\n".join(lines)
    if "GB_MOCK_RESULT FAIL" in combined:
        raise GateError("UNITY_PLAYER_REPORTED_FAILURE")
    if "GB_MOCK_RESULT PASS LOCAL_MOCK" not in combined:
        return False
    if "GB_MOCK_REDACTION PASS" not in combined: raise GateError("UNITY_RESULT_REDACTION_MISSING")
    for stage in STEPS:
        if not re.search(r"GB_MOCK_STEP " + stage + r" PASS", combined):
            raise GateError("UNITY_STEP_MISSING_" + stage.upper())
    for kind in ("INITIALIZE", "AUTH", "PURCHASE"):
        if not re.search(r"GB_MOCK_NATIVE kind=" + kind
                         + r" outcome=SUCCEEDED requestId=[0-9a-fA-F-]{36}", combined):
            raise GateError("UNITY_NATIVE_DIAGNOSTIC_MISSING_" + kind)
    return True


def assert_wallet_ledger(container, admin, database):
    sql = "SELECT count(*), coalesce(sum(delta),0) FROM wallet_ledger;\n"
    output = must(["docker", "exec", "-i", container, "psql", "-X", "-U",
                   admin, "-d", database, "-t", "-A", "-v", "ON_ERROR_STOP=1"],
                  "DB_LEDGER_QUERY_FAILED", input_text=sql)
    if output.strip() != "1|100":
        raise GateError("DB_LEDGER_NOT_EXACTLY_ONE_100_COIN_GRANT")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-local", action="store_true", required=True,
                        help="Explicit permission to create and retain a dedicated local DB and install test APK")
    parser.add_argument("--staging", type=Path, default=os.environ.get("GAMEBRIDGE_UPM_STAGING"))
    parser.add_argument("--serial", default=os.environ.get("GAMEBRIDGE_ANDROID_SERIAL"))
    parser.add_argument("--expected-avd", default=os.environ.get("GAMEBRIDGE_TEST_AVD_NAME"))
    parser.add_argument("--adb", default=os.environ.get("GAMEBRIDGE_ADB"))
    parser.add_argument("--postgres-container", default=os.environ.get("GAMEBRIDGE_TEST_POSTGRES_CONTAINER",
                                                                       "gamebridge-sdk-local-postgres-1"))
    parser.add_argument("--postgres-admin", default=os.environ.get("GAMEBRIDGE_TEST_POSTGRES_ADMIN", "gamebridge"))
    parser.add_argument("--postgres-port", type=int, default=int(os.environ.get("GAMEBRIDGE_TEST_POSTGRES_PORT", "54329")))
    parser.add_argument("--package-cache", type=Path, help="Previously resolved exact-version Unity PackageCache for this isolated consumer")
    parser.add_argument("--utf8-probe", action="store_true", help="Use test-only JNI UTF-8 round-trip consumer")
    parser.add_argument("--native-demo-probe", action="store_true", help="Use test-only staged Native Demo consumer")
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()
    if args.utf8_probe and args.native_demo_probe: parser.error("choose one specialized probe")

    (ROOT / "artifacts").mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="unity-android-e2e-", dir=ROOT / "artifacts"))
    source = must(["git", "rev-parse", "HEAD"], "GIT_HEAD_UNAVAILABLE").strip()
    tracked_dirty = bool(must(["git", "status", "--porcelain", "--untracked-files=no"],
                              "GIT_STATUS_UNAVAILABLE").strip())
    summary = {
        "status": "NOT_RUN", "scope": "Unity Android Player -> Kotlin Bridge -> LOCAL_MOCK Backend/PostgreSQL",
        "sourceHead": source, "sourceTrackedDirty": tracked_dirty,
        "unityPlayer": "NOT_RUN", "realGoogleLogin": "NOT_RUN",
        "realStorePurchase": "NOT_RUN", "retainsTestDatabase": True,
    }
    backend_process = None
    backend_log = None
    try:
        if not args.staging or not args.staging.is_dir() or not (args.staging / "SHA256SUMS").is_file():
            raise GateError("UPM_STAGING_REQUIRED", "DEFERRED_ENV")
        staging = args.staging.resolve()
        must(["python3", "harness/check-staging.py", staging], "UPM_CHECKSUM_FAILED")
        verify_staged_source_matches_checkout(staging)
        summary["stagingManifestSha256"] = sha256(staging / "SHA256SUMS")
        adb = locate_adb(args.adb)
        if adb is None:
            raise GateError("ADB_MISSING", "DEFERRED_ENV")
        expected_avd = args.expected_avd
        marker = ROOT / "artifacts/v2-test-avd-name.txt"
        if not expected_avd and marker.is_file():
            expected_avd = marker.read_text(encoding="utf-8").strip()
        serial, avd = find_dedicated_device(adb, args.serial, expected_avd)
        summary["emulatorAvd"] = avd
        summary["emulatorSerial"] = serial

        # Fail on missing Unity license/modules before touching PostgreSQL.
        environment = os.environ.copy()
        environment["GAMEBRIDGE_UPM_STAGING"] = str(staging)
        prepared = must(["bash", "scripts/prepare-unity-android-mock.sh", "--prepare"],
                        "UNITY_CONSUMER_PREPARE_FAILED", env=environment)
        match = re.search(r"^Prepared consumer: (/.+)$", prepared, re.MULTILINE)
        if not match:
            raise GateError("UNITY_CONSUMER_PATH_MISSING")
        project = Path(match.group(1))
        if not project.is_dir() or not project.is_relative_to((ROOT / "artifacts").resolve()):
            raise GateError("UNEXPECTED_UNITY_CONSUMER_PATH")
        if args.package_cache:
            import importlib.util
            spec = importlib.util.spec_from_file_location("ios_push_cache", ROOT / "harness/run-unity-ios-mock-push-e2e.py")
            cache_module = importlib.util.module_from_spec(spec); spec.loader.exec_module(cache_module)
            try:
                summary["embeddedCachedPackages"] = cache_module.embed_cached_packages(args.package_cache.resolve(), project)
            except cache_module.common.GateError as error:
                raise GateError(str(error), error.category) from error
        if args.utf8_probe:
            shutil.copy2(ROOT / "tests/UnityAndroidUtf8Consumer/MockPlayerScenario.cs", project / "Assets/MockPlayerScenario.cs")
        if args.native_demo_probe:
            shutil.copy2(ROOT / "tests/UnityAndroidNativeDemo/MockPlayerScenario.cs", project / "Assets/MockPlayerScenario.cs")
            shutil.copytree(staging / "com.gamebridge.sdk/Samples~/Native Demo", project / "Assets/Native Demo")
            editor = Path("/Applications/Unity/Hub/Editor") / os.environ.get("UNITY_EDITOR_VERSION", "6000.5.8f1") / "Unity.app/Contents/Resources/PackageManager/BuiltInPackages/com.unity.ugui"
            try:
                if json.loads((editor / "package.json").read_text()).get("version") != "2.5.0": raise ValueError()
                shutil.copytree(editor, project / "Packages/com.unity.ugui", ignore=shutil.ignore_patterns("Tests", "Tests.meta"))
            except (OSError, ValueError): raise GateError("UNITY_UGUI_REQUIRED", "DEFERRED_ENV")
            (project / "Packages/manifest.json").write_text('{"dependencies":{"com.unity.ugui":"2.5.0"}}\n')
            summary["nativeDemoProbe"] = True
        apk = output / "gamebridge-mock-consumer.apk"
        built = run(["bash", "scripts/build-unity-android-mock.sh", project, apk],
                    timeout=1200, env=environment)
        (output / "unity-build.log").write_text(built.stdout, encoding="utf-8")
        if built.returncode:
            if built.returncode == 2 and "DEFERRED_ENV" in built.stdout:
                raise GateError("UNITY_LICENSE_OR_ANDROID_MODULE_REQUIRED", "DEFERRED_ENV")
            raise GateError("UNITY_IMPORT_OR_ANDROID_BUILD_FAILED")
        if not apk.is_file() or not apk.stat().st_size:
            raise GateError("UNITY_APK_MISSING")
        summary["unityApkSha256"] = sha256(apk)
        summary["unityPlayer"] = "BUILT_NOT_RUN"

        jar = ROOT / "backend/build/libs/gamebridge-backend.jar"
        must(["bash", "backend/gradlew", "-p", "backend", "bootJar"],
             "BACKEND_BOOTJAR_BUILD_FAILED", timeout=600)
        if not jar.is_file():
            raise GateError("BACKEND_JAR_MISSING")
        summary["backendJarSha256"] = sha256(jar)
        database, password = create_isolated_database(args.postgres_container,
                                                     args.postgres_admin, args.postgres_port)
        summary["database"] = database
        backend_process, backend_log, port, key = start_backend(
            jar, output, database, password, args.postgres_port)
        summary["backend"] = "LOCAL_MOCK_READY"

        # Unity may restart ADB, so revalidate device identity and app absence after building.
        wait_for_dedicated_device(adb, serial, avd)
        installation = run([adb, "-s", serial, "install", apk], timeout=120)
        # APK path and installer diagnostics contain no development key or token.
        (output / "adb-install.log").write_text(installation.stdout, encoding="utf-8")
        if installation.returncode or "Success" not in installation.stdout:
            raise GateError("UNITY_APK_INSTALL_FAILED")
        summary["unityPlayer"] = "INSTALLED_NOT_RUN"
        # Safe because this is exclusively a dedicated test AVD.
        must([adb, "-s", serial, "logcat", "-c"], "LOGCAT_CLEAR_FAILED", timeout=20)
        # The key is synthetic and passed only to this dedicated test app; never print the argv.
        launched = run([adb, "-s", serial, "shell", "am", "start", "-W", "-n",
                        PACKAGE + "/com.unity3d.player.UnityPlayerGameActivity",
                        "--es", "gamebridge_mock_url", f"http://10.0.2.2:{port}",
                        "--es", "gamebridge_mock_key", key], timeout=30)
        (output / "adb-launch.log").write_text(launched.stdout.replace(key, "[REDACTED]"), encoding="utf-8")
        if launched.returncode or not re.search(r"^Status:\s*ok\s*$", launched.stdout, re.MULTILINE):
            raise GateError("UNITY_LAUNCH_FAILED")
        summary["unityPlayer"] = "LAUNCHED_PENDING"
        deadline = time.monotonic() + args.timeout_seconds
        while time.monotonic() < deadline:
            lines = scan_unity_log(adb, serial, key, password)
            if check_player_markers(lines):
                if args.utf8_probe and not any("GB_UTF8_JNI_ROUNDTRIP PASS" in line for line in lines):
                    raise GateError("JNI_UTF8_MARKER_MISSING")
                if args.native_demo_probe and not any("GB_NATIVE_DEMO_FLOW PASS" in line for line in lines):
                    raise GateError("NATIVE_DEMO_MARKER_MISSING")
                (output / "unity-test-markers.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
                summary["unityPlayer"] = "PASS"
                summary["unityMarkerCount"] = len(lines)
                break
            time.sleep(2)
        else:
            raise GateError("UNITY_PLAYER_RESULT_TIMEOUT")

        backend_log.flush()
        summary["backendTraceCounts"] = server_trace_status(output / "server.log", key, password)
        assert_wallet_ledger(args.postgres_container, args.postgres_admin, database)
        summary["ledgerCount"] = 1
        summary["ledgerDelta"] = 100
        summary["status"] = "PASS"
    except GateError as error:
        summary["status"] = error.category
        summary["errorCode"] = str(error)
    except Exception as error:
        summary["status"] = "FAIL"
        summary["errorCode"] = type(error).__name__
    finally:
        if backend_process:
            backend_process.terminate()
            try:
                backend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                backend_process.kill()
                backend_process.wait()
        if backend_log:
            backend_log.close()
        (output / "result.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("RESULT", summary["status"], summary.get("errorCode", ""),
          "EVIDENCE", output.relative_to(ROOT))
    return 0 if summary["status"] == "PASS" else 2 if summary["status"] == "DEFERRED_ENV" else 1


if __name__ == "__main__":
    sys.exit(main())
