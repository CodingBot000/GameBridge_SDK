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
