# P10-T01 Core·Bridge 변경 전후 — 배치26

## 기준/선정

shipping 기준6d200b0, 계측cohort b6fd537. C전 baseline은79개shipping/wire file및Swift C-export이름을contracts/baseline/p10-core-batch26.json에기록했다. Kotlin/Swift shipping bytehash는엄격동일조건,C#은RequestRegistry의private body만변경허용하고public/internal/protected선언을동일비교한다. 다른managed파일/wire는byte동일. 기존P08API검사도병행한다. 미존재contracts/openapi.yaml은UNMEASURED/기존부재로명시하고만들어졌다고주장하지않는다. binary ABI/실제Unity는D의새빌드로분리검증한다.

Native coordinator 검토: Kotlin의Mutex·Deferred/CoroutineScope identity와Swift actor·generation/Task소유는플랫폼고유경계다. 형식통일의이득이작고초기화/취소의미를흔들위험이있어이번에는수정하지않는다. 선택은managed registry의반복event header검증과반복pending ownership removal이다.

## C1 event header 책임 집중

3개handler의session/event-ID/UTC timestamp/payload-object조건을private TryReadEventEnvelope로분리했다. purchase type검사위치와push routing/body별제약,disposed gate,callback전달은유지했다. repeated validation3곳→1곳이며class hierarchy/새공개추상화는없다.

변경전기존runtime에서3종event×7invalid header와정상각1 callback matrix를추가해실행했다. 전후동일managedcohort **418 helper=198normal+220expected error checks**,processexit0. mutation/실제Native/Player는D에서각실행source로확인한다.

API/source/wire검사PASS,공개/internal호출선언과Native C-export이름변경없음.새경계음성3건은public/internal선언·unscoped native/wire·C-export/file-set drift를거부한다.

## C2 completion ownership 제거 경계

Finish와RequestAsync finally의동일entry참조확인/removal을private RemoveOwned로모았다. dictionary lookup/remove와선택적ignored증가는기존gate안에서원자적으로유지하며TaskCompletionSource통지는기존대로lock밖이다. finally의이미완료된entry정리는ignored를올리지않는다. Dispose의gate clear·각abandon오류완료/linkedCancellation/deadline수명은변경하지않았다.

C1후/C2후동일cohort418=198normal+220expected/exit0. 100회cancel-vs-dispose 각exactly-once/timeout후응답/중복/pending0/초기화join·새session의미검사유지. duplicate-only정상0/변이nonzero의예상guard실패도감지했다. source/API/wire baselinePASS. 중앙화로반복조건이줄었으며helper와설명추가때문에전체LOC감소를주장하지않는다.

실제shipping수정은RequestRegistry.cs한파일의두private경계다. 나머지변경은계측·test-only진단·회귀/harness·evidence다. P10-T01전체범위완료판정은D의현소스산출물/실제플랫폼결과및남은범위를함께고려한다.

## D 새 소스 빌드/API·ABI 결과

source **dc45a2f1b97e035655b4b6b2a9d5381248b040dc**,tracked-clean. 현재NativeMaven/Android/R8 compile exit0,새XCFramework device/simulator archive exit0,새UPM147파일checksum통과. 현재package의privateC#source가checkout과일치하며oldstaging은거부된다.

현재Native3종class(SdkCoordinator,BridgeProtocol,BridgeFacade)의javap publicsurface가변경전과동일하다. 양slice nm의Cexports는GB_Dispatch/GB_ProtocolVersion/GB_SetCallback/GB_Shutdown4개로동일. snapshot79파일의Kotlin/Swiftshipping/wire는동일하며유일한private수정파일의public/internal선언도일치했다. 전체SDK의모든binary ABI를검사한것이아닌선정표면의실제새빌드검증이다. 원본 `artifacts/batch26/artifact-compatibility.json`.

현재post ledger `core-assertions-zn69jotl` PASS/exit0:Kotlin10/50,Swift12/122,managed418(198normal+220expected),정상복원418,분기control419,stress316,Unity2/32. baseline391에matrix27을더한동일418cohort를C1/C2전후유지했다. counts를맞추도록assertion을제거하거나Fake제품으로대체하지않았다. 실제Native/Player/Strict는후속source별로추가한다.


## 실제 플랫폼 회귀의 완료 범위와 잔여

새 package/source의 managed Editor2/32 및 전체418 smoke는 PASS이고, 동일 shipping code d86ccc2에서 freshDB self9 PASS와 신규18.6 Simulator C ABI1 PASS를 확인했다. 실제 Android Unity Player는 새 Editor LicensingClient IPC 연결 실패로 APK 생성 전 차단됐다. raw runner FAIL/exit1을 보존하며 실제 Player는 NOT_RUN/DEFERRED_ENV다. 전체 Strict 호출은0/DEFERRED_ENV이며 과거 batch25 Player·Strict를 이번 refactor 실행으로 대체하지 않는다. 관련 현재 iOS Unity Player도 이번 batch에서 실행하지 않았다.

공개/internal API·wire·선정 javap/nm 표면 변경 없음은 검증 범위의 사실이며, 모든 OS·binary ABI·실기기 동작 보증은 아니다. T01 첫 두 private 개선은 구현 및 관련 로컬 회귀 확인을 마쳤으나 현재 Unity 전체 Player 영향 검증을 남겨 Task 전체 IN_PROGRESS/PARTIAL을 유지한다. 이후 P10-T02~T04를 이번 배치 완료로 표시하지 않는다. Native coordinator 등 제외 영역은 위 선정 근거를 유지한다.


## 배치27 후속

[배치27](p10-batch27-integrated.md)에서공식direct/CLI각새project1회실제Editor smoke가210초/124및180초/6으로미도달했다. protocol거부/mutex실패/channel부재를관측했지만복구/전체원인은미확정이다. 추가수정0,B현재Player NOT_RUN/CStrict0/DEFERRED_ENV로P10-T01PARTIAL유지. 현재Core10/12·managed418·Native42/38·self9·Python149및보존artifact/current79source·API/선정ABI재대조는독립PASS이며과거Player·Strict를현재로재작성하지않는다. T02는선행차단으로제품변경없이[경계감사·후보2·회귀설계](p10-auth-purchase-push-batch27.md)만수행했다. 기존FAIL/외부대기유지.

배치27 최종 [Hosted run44057317769](https://github.com/CodingBot000/GameBridge_SDK/actions/runs/44057317769),source50cd34c는SUCCESS(Hosted4+basic SUCCESS,Unity/ReleaseSKIPPED),새진단6건포함Python43파일/149건확인. currentPlayer/Strict미실행및P10-T01PARTIAL은해소하지않는다. [최종인계](p10-batch27-integrated.md).


## 배치28 후속

사용자가정상실행확인을위임했고에이전트가새전용project를Hub에서열어6000.5.8f1 Scene/Hierarchy/Inspector정상UI를확인했다. 별도direct batch1회는210초timeout/receipt없음으로실패한상태를보존했다. B현재Player·Strict0/DEFERRED_ENV,T01PARTIAL로C1/C2제품진입은미실행이다. 독립Python149/Core10·12/managed418/Native42·38/self9 PASS와API/선정ABI재대조는[배치28 증거](p10-batch28-integrated.md)에source별기록했다. GUI시작의다른SDK ADBserver종료경고·대상영향미확정도분리했다. 코드변경0이라추가Hosted dispatch0/NOT_RUN,과거CI는비교기준만유지한다.
