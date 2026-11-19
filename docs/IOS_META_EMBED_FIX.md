# Unity iOS Meta Embed fix — document42

Base: 36ca83638125f5ccdf915a5b55dda71633a326b5. This fixes export packaging only. Android document41 PASS is retained; Android was not rerun.

## Confirmed cause and permanent correction

The old UnityFramework strongly required FBAEMKit, FBSDKCoreKit_Basics, FBSDKCoreKit and FBSDKLoginKit, but the app embedded none. Existing runpaths and ad-hoc signatures were valid. Its same-launch runtime log reported UnityFramework dlopen/FBAEMKit lookup failure.

FacebookLogin18.1.1 was assigned only to UnityFramework. The hook now retains that strong link and assigns the same pinned SPM product to the Host App; Xcode embeds/signs exactly the four transitive dynamic frameworks. GameBridgeNative stays static, GoogleSignIn9.2.0 remains connected, and no app is repaired by hand-copying libraries. ios/Package.swift/project.yml and Native/Android/Backend code are unchanged.

Owned package identity/version, target product ownership and strong links are checked before adding missing links. Repeat/reload does not duplicate references/products/phases. Conflicting Host package setup fails explicitly without deletion or takeover. The iOS runner now verifies actual app framework files and ad-hoc signatures before Backend/Player startup.

## Actual results

| Check | Result |
| --- | --- |
| Independent Hook checks /installed Unity API + Apple plutil | PASS /40 checks /exit0 |
| Old failed app /new embedding gate | Correctly rejected: META_FRAMEWORK_NOT_EMBEDDED_FBAEMKit |
| New UPM | PASS /147 files /manifest SHA256 997fd8dea785aafa859c7ddb319492a101583bc6b59978e799ff3c8952a8bf36 |
| New Unity project/import/export and Simulator app build | PASS |
| Actual app dynamic dependencies | Four present, strict signatures exit0, strong LC_LOAD_DYLIB retained |
| Meta release | SPM18.1.1/revision 80d0ee82f6370d1bace1431a80cb80575f98ee90 |
| New iOS18.6 Unity Player /LOCAL_MOCK | PASS /attempt1 /exit0 /23 markers |
| initialize/login/products/purchase/wallet/logout/redaction | All PASS |
| Backend trace | {"mock-auth": 1, "catalog": 1, "entitlements": 2, "verify": 1, "logout": 1} |
| Independent DB query | Ledger1/+100; sessions1/active0 after logout /exit0 |
| New Player runtime log |0 dyld failure matches |
| Actual OAuth /real Store /remote push | NOT_RUN |

Some vendor Info.plist bundle version labels are1.0; they are not SDK release numbers. The exact SPM pin establishes18.1.1. No vendor binary/version was modified. Unit development failures (test constant/entrypoint name collision; inline PBX BuildFile reader rejection) were corrected, with all original logs retained before the40 checks passed. No check was skipped or forced green.

## Exact commands and local evidence

- Hook: installed Unity bundled dotnet run --project tests/UnityIosHook/IosHook.csproj, UNITY_MANAGED/UNITY_XCODE_DLL pointing to6000.5.8f1 assemblies; exit0.
- Package: scripts/package-sdk.sh with retained document41 main36 Maven/XCFramework and new output /Users/switch/Development/App/GameSDK/GameBridge_SDK_Codex_Plan_v1/artifacts/ios-meta42-gwys9f5p/source/artifacts/meta-embed.wu_f4khd/upm; exit0. Native sources were unchanged; Android was not rebuilt.
- E2E: python3 harness/run-unity-ios-mock-e2e.py --run-local --staging /Users/switch/Development/App/GameSDK/GameBridge_SDK_Codex_Plan_v1/artifacts/ios-meta42-gwys9f5p/source/artifacts/meta-embed.wu_f4khd/upm --adhoc --package-cache <exact-version registry cache>; exit0. Public argument record: /Users/switch/Development/App/GameSDK/GameBridge_SDK_Codex_Plan_v1/artifacts/ios-meta42-gwys9f5p/source/artifacts/meta-embed.wu_f4khd/command.json.
- Runner result: /Users/switch/Development/App/GameSDK/GameBridge_SDK_Codex_Plan_v1/artifacts/ios-meta42-gwys9f5p/source/artifacts/unity-ios-e2e-rhtr8rw7/result.json
- Player markers: /Users/switch/Development/App/GameSDK/GameBridge_SDK_Codex_Plan_v1/artifacts/ios-meta42-gwys9f5p/source/artifacts/unity-ios-e2e-rhtr8rw7/unity-test-markers.log
- New app: /Users/switch/Development/App/GameSDK/GameBridge_SDK_Codex_Plan_v1/artifacts/ios-meta42-gwys9f5p/source/artifacts/unity-ios-e2e-rhtr8rw7/Derived/Build/Products/Debug-iphonesimulator/project.app
- Export project: /Users/switch/Development/App/GameSDK/GameBridge_SDK_Codex_Plan_v1/artifacts/ios-meta42-gwys9f5p/source/artifacts/unity-ios-e2e-rhtr8rw7/xcode/Unity-iPhone.xcodeproj/project.pbxproj
- Xcode log: /Users/switch/Development/App/GameSDK/GameBridge_SDK_Codex_Plan_v1/artifacts/ios-meta42-gwys9f5p/source/artifacts/unity-ios-e2e-rhtr8rw7/xcodebuild.log
- Signature/strong-load/pin/SQL inspection: /Users/switch/Development/App/GameSDK/GameBridge_SDK_Codex_Plan_v1/artifacts/ios-meta42-gwys9f5p/source/artifacts/meta-embed.wu_f4khd/app-and-db-inspection.json
- Scoped runtime log: /Users/switch/Development/App/GameSDK/GameBridge_SDK_Codex_Plan_v1/artifacts/ios-meta42-gwys9f5p/source/artifacts/meta-embed.wu_f4khd/new-player-runtime.log
- Cleanup: /Users/switch/Development/App/GameSDK/GameBridge_SDK_Codex_Plan_v1/artifacts/ios-meta42-gwys9f5p/source/artifacts/meta-embed.wu_f4khd/runtime-and-cleanup.json
- Durable sanitized evidence: [ios-meta-embed-fix.json](evidence/ios-meta-embed-fix.json).

Local staging/logs are not Git/Release assets. The tested Hook/runner hashes are recorded and compared with the final commit. Previous failed app/staging/DBs/Simulator and original checkout/untracked files remain intact. Only this run's owned Simulator was shut down; its data/new DB remain. This is LOCAL_MOCK integration proof, not real account/IAP/Push, full Strict or release readiness.
