#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$#" != 3 ]]; then
  echo 'Usage: package-sdk.sh ANDROID_MAVEN_REPO IOS_XCFRAMEWORK NEW_OUTPUT_DIR' >&2; exit 64
fi
maven="$1"; ios="$2"; output="$3"
for module in sdk-core sdk-android sdk-unity-bridge; do
  if [[ ! -f "$maven/com/gamebridge/$module/0.1.0-dev/$module-0.1.0-dev.pom" ]]; then
    echo "Missing $module Maven POM; run scripts/build-android.sh --mock first." >&2; exit 2
  fi
  ext=aar; [[ "$module" == sdk-core ]] && ext=jar
  if [[ ! -f "$maven/com/gamebridge/$module/0.1.0-dev/$module-0.1.0-dev.$ext" ]]; then
    echo "Missing $module binary; run scripts/build-android.sh --mock first." >&2; exit 2
  fi
done
if ! python3 - "$ios" <<'PYVERIFY'
import plistlib
from pathlib import Path
import sys
root = Path(sys.argv[1])
try:
    data = plistlib.loads((root / "Info.plist").read_bytes())
    found = set()
    for library in data["AvailableLibraries"]:
        if library.get("SupportedPlatform") != "ios":
            continue
        framework = root / library["LibraryIdentifier"] / library["LibraryPath"]
        if (framework / "GameBridgeNative").is_file():
            found.add(library.get("SupportedPlatformVariant", "device"))
    assert {"device", "simulator"} <= found
except (OSError, KeyError, ValueError, AssertionError, plistlib.InvalidFileException):
    sys.exit(1)
PYVERIFY
then echo 'Missing XCFramework device/simulator slices; run scripts/build-ios.sh --xcframework first.' >&2; exit 2; fi
if [[ -e "$output" ]]; then echo 'Output already exists; choose a new directory.' >&2; exit 2; fi
mkdir -p "$(dirname "$output")"
mkdir "$output"
cp -R "$root/unity/Packages/com.gamebridge.sdk" "$output/com.gamebridge.sdk"
mkdir -p "$output/com.gamebridge.sdk/Plugins/Android" "$output/com.gamebridge.sdk/Plugins/iOS"
cp -R "$maven" "$output/com.gamebridge.sdk/Plugins/Android/maven-repo"
cp -R "$ios" "$output/com.gamebridge.sdk/Plugins/iOS/GameBridgeNative.xcframework"
python3 - "$output" <<'PY'
import hashlib
from pathlib import Path
import sys
root = Path(sys.argv[1])
entries = []
for path in sorted(root.rglob('*')):
    if path.is_file():
        entries.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.relative_to(root).as_posix())
(root / 'SHA256SUMS').write_text('\n'.join(entries) + '\n')
PY
printf '%s\n' 'Staging created; Unity import and build hooks are not yet verified.'
