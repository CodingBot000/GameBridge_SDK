# P09 잔여 검증·안정화 배치25

기준 f6915e35f28e06a0d88e053a66883505bc7bc881. local fix/unity-android-mock-e2e-evidence에서 작업하고 handoff/p09-resume-20261113으로 관련 커밋만 FF push한다. A~D 순차 진행, 실제 Provider·main·force·Release·P01/P02/P10 변경 없음.

## A — AVD 연결 조사/보호

읽기 전용 조사: 현재 실행 중인 비전용 emulator 한 개의 요청 console5560과 실제 listen5560/5561 owner PID89772가 일치했다. 해당 AVD는 변경하지 않았다. 최초 adb devices 조회는 daemon 부재로 CLI가 자동 시작을 출력했으며 server kill/restart/초기화는 수행하지 않는다.

배치24의 요청5570·자기 PID93858은 실제 console/ADB 소유 증거가 없었고 해당 serial 조회는 다른 AVD 이름을 반환했다. PID가 살아 있고 인자에 -port가 있다는 사실은 실제 socket 소유와 같지 않다. 당시 최초 bind/포트 경쟁 시점의 증거가 없으므로 OS 차원의 원인은 미확정이다. 실기기/타 AVD로 재현해 충돌시키지 않는다.

`emulator_binding.py`는 ps의 qemu/AVD/요청 port, lsof의 console·ADB 두 port owner를 함께 확인한다. Push runner/CI는 GAMEBRIDGE_PUSH_EMULATOR_PID를 요구하며 매 기기 명령 전 재검증한다. cleanup도 기존 실패를 숨기거나 타 기기에 전송하지 않는다. guard·binding·CI·증거 검사 단위 **16건 PASS/skip0/exit0**. 실제 Player는 아직 NOT_RUN. 원본 조사 자료는 ignored artifacts/batch25에만 보존한다.

다음은 free port와 새 전용 AVD를 준비한 뒤 실제 serial·이름·PID·두 port의 일치 여부를 확인한다. 확인 불가 시 DEFERRED_ENV로 기록하고 B로 이동한다.

## B — StoreKit/DB 계획 차이

NOT_RUN. 배치24 최초 실패와 단독 성공, 동일 코드 범위와 checkpoint/로그 한계를 비교한다. 26.5 재조사나 timeout 증가·성공까지 반복은 하지 않는다. Testcontainers 요구와 현재 별도 PostgreSQL 방식을 비교해 처리 방향을 확정한다.

## C — 하네스/CI 범위/조건부 Strict

NOT_RUN. 기존 미연결4파일6건을 조사하고 Hosted 적합 시 연결한다. 현재 하네스 단위와 새 격리 자체시험9 lane을 실행한다. A 실제 Android Push PASS와 새 전용 전체 환경이 모두 확인돼야 ci-unity-e2e.sh 전체 Strict를 최대1회 실행한다. mapping50은 실제 테스트 수에 합산하지 않는다.

## D — 감사/인계

NOT_RUN. 개별 P09 상태 변경은 실제 근거 및 원장 검사로 판단한다. P05-T03 FAIL/ENV-STOREKIT-26 OPEN/Provider13 WAITING_USER/self-hosted·Release 미검증을 유지한다. 로컬 검증 후 비밀정보·범위 검사, handoff FF push, 변경된 Hosted 테스트가 있고 Unity 변수 안전 확인 가능 시 false 입력 dispatch1회만 수행한다.
