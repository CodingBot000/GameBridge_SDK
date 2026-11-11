#!/usr/bin/env python3
"""Export safe Markdown evidence from clean-checkout LOCAL_MOCK PASS results.

Never copy raw logs, keys, device serials, DB credentials or local paths.
Reject partial, stale or dirty results; original artifacts remain local.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "docs" / "evidence"


def checked_result(path, kind, current_head):
    if not path.is_file() or path.name != "result.json" or not path.is_relative_to(ROOT / "artifacts"):
        raise ValueError("a local artifacts/*/result.json is required")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "PASS" or data.get("sourceTrackedDirty") is not False:
        raise ValueError("result must PASS on a tracked-clean checkout")
    if (not isinstance(data.get("sourceHead"), str)
            or not re.fullmatch(r"[0-9a-f]{40}", data["sourceHead"])
            or data["sourceHead"] != current_head):
        raise ValueError("source SHA is stale; rerun on current HEAD")
    if data.get("ledgerCount") != 1 or data.get("ledgerDelta") != 100:
        raise ValueError("wallet ledger proof missing")
    if kind == "unity":
        if data.get("unityPlayer") != "PASS" or not re.fullmatch(r"[0-9a-f]{64}", data.get("unityApkSha256", "")):
            raise ValueError("actual Unity Android Player PASS proof missing")
        trace = data.get("backendTraceCounts")
        if not isinstance(trace, dict) or any(
                not isinstance(trace.get(operation), int) or trace[operation] < 1
                for operation in ("mock-auth", "catalog", "entitlements", "verify", "logout")):
            raise ValueError("backend trace incomplete")
        required = ("unity-build.log", "unity-test-markers.log", "server.log")
    elif kind == "native":
        if data.get("unityPlayer") != "NOT_RUN" or data.get("tests") != 1 or data.get("skipped") != 0:
            raise ValueError("native-only proof missing or misclassified")
        operations = data.get("nativeOperations")
        if not isinstance(operations, list) or not set(
                ("sdk.initialize", "auth.signIn", "store.products", "store.purchase",
                 "store.entitlements", "auth.signOut")).issubset(operations):
            raise ValueError("native operations incomplete")
        required = ("instrumentation.log", "native-requests.log", "server.log")
    else:
        raise ValueError("unsupported kind")
    for filename in required:
        if not (path.parent / filename).is_file():
            raise ValueError("raw local evidence missing: " + filename)
    return data


def public_summary(data, kind, result_hash):
    unity = kind == "unity"
    tick = chr(96)
    title = "Unity Android Player" if unity else "Android Kotlin Bridge (Unity 제외)"
    lines = [
        "# GameBridge LOCAL_MOCK 검증 증거 — " + title,
        "",
        "**상태: 로컬 Mock PASS. Google 로그인·실제 스토어 결제 NOT_RUN.**",
        "",
        "| 검증 항목 | 결과 |",
        "|---|---|",
        "| 실행 경로 | " + ("Unity Player → " if unity else "Android instrumentation → ")
        + "Kotlin Bridge → LOCAL_MOCK Backend/PostgreSQL |",
        "| 소스 SHA | " + tick + data["sourceHead"] + tick + " |",
        "| 추적 파일 변경 | 없음 |",
        "| DB 지급 원장 | 1건, 100코인 |",
        "| Unity Android Player | " + ("PASS" if unity else "NOT_RUN") + " |",
        "| 실제 Provider·스토어 | NOT_RUN |",
        "| result.json SHA-256 | " + tick + result_hash + tick + " |",
    ]
    if unity:
        lines.extend([
            "| APK SHA-256 | " + tick + data["unityApkSha256"] + tick + " |",
            "| Unity 마커 수 | " + str(data.get("unityMarkerCount", 0)) + " |",
            "| Backend HTTP 200 trace | " + ", ".join(
                str(data["backendTraceCounts"][operation]) + " " + operation
                for operation in ("mock-auth", "catalog", "entitlements", "verify", "logout")) + " |",
        ])
    else:
        lines.append("| Android instrumentation | 1 PASS, 0 skip |")
    lines.extend([
        "",
        "Runner는 지정된 Unity/Native 결과, Backend trace, 로컬 DB 원장을 검사한 뒤 PASS를 기록한다.",
        "Native request ID와 Backend HTTP request ID는 별개이다.",
        "",
        "원본 로그·실기기 식별자·개발 키·로컬 DB·APK는 Git에 포함하지 않는다.",
        "이 요약은 Unity iOS 또는 실제 Google/Apple/FCM/APNs 연동 완료의 증거가 아니다.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("unity", "native"), required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, output = args.result.resolve(), args.output.resolve()
    if not output.is_relative_to(EVIDENCE.resolve()) or output.suffix != ".md" or output.exists():
        parser.error("output must be a new docs/evidence/*.md file")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    try:
        data = checked_result(source, args.kind, head)
        result_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        summary = public_summary(data, args.kind, result_hash)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print("EVIDENCE_REJECTED:", error, file=sys.stderr)
        return 1
    output.write_text(summary, encoding="utf-8")
    print("EXPORTED:", output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
