# 문서37 소셜 인증 확장 인계

별도 feature/social-login-20261119 브랜치에서 A/B/C 구현·로컬 검증을 마쳤다. 기존 SDK64 Task/포트폴리오 종료/원본 실패는 유지하며 P00–P11을 자동 재개하지 않는다. 실제 계정 인증은 네 경로 모두 WAITING_USER다. 원격 push/PR/main/Release/실Provider 실행은 하지 않았다.

| 경로 | 구현·로컬 검증 | Native/패키지 | 실연동 |
| --- | --- | --- | --- |
| iOS Google | 공식9.2.0 custom nonce·Native session·C ABI, Swift/JWT/기존HTTP PASS | device/sim XCF·source(A)/최종binary 소비·UPM PASS | WAITING_USER |
| Android Facebook | Meta18.3.0 Classic·JNI·서버debug, Kotlin/Fake HTTP PASS | Maven·기본 및Meta포함R8 소비 PASS | WAITING_USER |
| iOS Facebook | Meta18.1.1 Limited/Classic 종류분리·서버JWKS, Swift/Fake HTTP PASS | 공식검증cache로 device/sim XCF·binary 소비 PASS | WAITING_USER |
| Android Apple | Custom Tabs·HTTPS App Link·서버 form_post/code 교환/ES256·일회용handle, HTTP6·Native URL/세션/라우팅 PASS | Kotlin/JNI·Maven/R8·UPM PASS | WAITING_USER |

Unity는 기존 `SignInAsync(AuthProvider)`를 사용한다. MOCK0/GOOGLE1/APPLE2를 유지하고 FACEBOOK3을 추가했다. Legacy ID_TOKEN 요청에서 proofType 생략/null 호환을 실제 HTTP로 확인했다. Facebook Access Token과 Limited JWT는 별도 필드·검증기로 처리하고 Limited→Classic downgrade를 거부한다. Classic은 새 challenge/Meta 재검증 하에 유효 bearer 재사용을 허용하며 nonce 결속이나 bearer 탈취 방어를 보장하지 않는다. iOS는 Limited 기본값을 권장 선택했다. 이메일 계정 병합·구매 이전은 없다. 기존 SessionService·계정 binding·원장을 재사용하고 V10/V11은 forward migration만 추가했다.

Apple callback은 세션을 발급하지 않고 검증된 identity+짧은 handle만 준비한다. Native의 시도별 verifier가 있어야 complete에서 기존 세션을 발급한다. 잘못된 state/code/Services ID/nonce/만료/handle, 중복·동시 요청을 거부한다. Native 보안 저장소는 provider/app/backend/settings에 결속되며 원본 제공자 proof는 저장하거나 Unity로 전달하지 않는다.

실행한 주요 명령과 결과 (모든 아래 성공 명령 exit0; 재실행 snapshot의 수를 중복 합산하지 않음):

| 명령/범위 | 실제 결과 | 로컬 로그 |
| --- | --- | --- |
| `backend/gradlew -p backend test --rerun-tasks --tests '*AppleWebAuthHttpTest' --tests '*FacebookAuthHttpTest' --tests '*AppleWebConfigurationTest' --tests '*IdentityVerifierTest' --tests '*AudiencePolicyTest' --tests '*AuthRateLimitTest' --tests '*SensitiveAuthTypesTest'` | 20 tests /0 failure/0 skip; 새전용 sandbox DB gamebridge_ci_22718d625e | artifacts/social-login/backend-final-auth.log |
| opt-in AuthHttpIntegrationTest→AuthFlowDatabaseTest | 기존Google/Apple HTTP2+challenge DB1 PASS; 새전용DB gamebridge_ci_ecb3f6b5d4 | regression-sandbox-0/1.log |
| opt-in MockXcodeHttpIntegrationTest→LedgerInvariantDatabaseTest | Mock지급/계정격리·동시성1+원장제약1 PASS; 새전용DB gamebridge_ci_253e0d01bd/별도schema 보존 | regression-mock-0/1.log |
| `ANDROID_HOME="$HOME/Library/Android/sdk" android/gradlew -p android :sdk-android:testDebugUnitTest :sdk-unity-bridge:testDebugUnitTest` | Native47 + Bridge9 /0 failure/0 skip | artifacts/social-login/android-unit-delivery2.log |
| `USE_LOCAL_FB_BINARIES=1 swift test --package-path ios --filter 'SocialAuthProviderTests\|AppleAuthProviderTests\|CBridgeTests'` | Social7+Apple20+CBridge4=31 PASS | artifacts/social-login/swift-final.log |
| Unity bundled dotnet `run --project tests/SocialAuthContract/SocialAuthContract.csproj` (GAMEBRIDGE_NEWTONSOFT_DLL=installedUnity Newtonsoft) | enum互換/provider routing/typed privacy/no fallback PASS | artifacts/social-login/csharp-final.log |
| `python3 harness/check-openapi.py`; `PYTHONPATH=harness python3 -m unittest harness.test_openapi_contract` | 27 operations/static DTO・form・redirect guard +18 mutation tests PASS | artifacts/social-login/openapi-c.log |
| `GAMEBRIDGE_MAVEN_REPO=<new-owned-output> bash scripts/build-android.sh --mock` | Maven AAR/JAR +sample +staged R8 consumer PASS | artifacts/social-login/android-build-delivery.log |
| same final Maven / separate consumer with Meta18.3.0 implementation | release R8 build PASS | artifacts/social-login/android-social-consumer-delivery.log |
| `USE_LOCAL_FB_BINARIES=1 xcodebuild archive ... -destination 'generic/platform=iOS'` / `iOS Simulator` | device arm64 +sim arm64/x86_64 archive PASS | native-b-local/delivery-device.log,delivery-simulator.log |
| `xcodebuild -create-xcframework ...` +isolated binary-only app build with pinned Google/Meta dependencies | final XCF +Simulator app link/resource/embed PASS | ios-delivery-final-create.log,binary-consumer-final/build-delivery.log |
| installed Unity PBX assembly `scripts/smoke-ios-hook.sh` | hook compile +existing PBX/plist idempotence PASS; new full Unity export not executed | artifacts/social-login/unity-hook-delivery.log |
| `scripts/package-sdk.sh <final-maven> <final-XCF> artifacts/social-login/upm-handoff` | final staging+147 checksum all match | artifacts/social-login/package-handoff.log |

Owned DB test controllers live under artifacts/social-login and reuse harness DB creator; environment opt-ins/credentials are injected in memory and not logged. Above shortened archive/consumer commands refer to exact local project/paths in the associated logs. Sanitized durable evidence: [A](evidence/social-login/a-ios-google.json), [B](evidence/social-login/b-facebook.json), [C/final](evidence/social-login/c-android-apple.json). Full logs and generated binaries stay local. Old DEV_RC and CI648 do not validate this new source. Full Strict/new CI/new Unity Player/actual OAuth UI/instrumentation were NOT_RUN.

외부 설정은 [USER_SETUP](USER_SETUP.md)의 문서37 A/B/C 절과 [Host 통합](INTEGRATION.md)을 따른다. Google iOS/server client IDs·reversed URL scheme; Meta App ID/Client Token·Android package/signing key hash·iOS fb scheme·테스트계정/권한·Backend-only App Secret; Apple Services ID/Primary App ID·Team/Key ID·Backend-only p8·등록HTTPS callback·검증App Link/assetlinks가 필요하다. 실제값/비밀/제공자토큰은 Git이나 Unity 에셋에 넣지 않는다.

환경 제한: Meta SwiftPM remote binary download가 지연됐다. upstream v18.1.1 공식 ZIP6개 SHA256 일치 및 codesign strict 검증 뒤 SDK의 공식 USE_LOCAL_FB_BINARIES 기능으로 검증했다. 제품 manifest는 공식 remote exact version을 유지하며 SDK 소스/서명검사를 바꾸지 않았다. 기본원격 경로는 DEFERRED_ENV다. 실제 Google/Meta/Apple 로그인, App Link 승인·브라우저 취소/복귀 실기기 동작, 새UnityPlayer는 대기/미실행이다. Facebook Classic UI의 논리취소 뒤 물리SDK 결과가 도착하기 전에는 오래된 토큰을 새 시도로 수용하지 않도록 process-wide BUSY를 유지한다; 결과가 영구 미도착하면 앱 재시작이 필요할 수 있다. SDK logout은 브라우저 Apple SSO 쿠키를 지우지 않는다.

수정한 실패는 원본log/XML을 보존했다: missing test mapper compile1→ObjectMapper; form body 재구성400→bounded servlet stream; 테스트303 추적→redirect 비활성화; legacy proofType 생략400→explicit nullable default; xcodegen PATH66→보존된pinned generator; PBX smoke에 잘못된Native target 입력→실제Sample 생성. Meta ZIP Python 추출의symlink손실/codesign65→ditto 원형복원. 이 수정 후 선택 검증은 모두 통과했고 미해결 선택 빌드/테스트 실패는 없다. 운영/실기기 성공을 주장하지 않는다.

Git 로컬 배치: A9848e56, B121d2c6, C는 `[SOC-C]` 메시지로 조회한다. 최종 SHA는 `git log -3 --oneline`을 따른다. 기존미추적 harness/cache·scripts/cache·unity/Demo를 보존했고 새 테스트의 generated bin/obj만 gitignore에 추가했다. 문서·코드·테스트를 같은 C commit에 묶고 tracked-clean 여부를 확인한다. push는 하지 않는다.
