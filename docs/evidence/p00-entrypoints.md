# P00-T04 문서 검사 및 명령 진입점 검증

- `make doctor`와 `make verify-progress`는 로컬에서 exit 0이었다. doctor는 명령·Docker·Android SDK 경로 가용성만 확인하며 라이선스·서명·기기 또는 실제 제공자 동작을 검증하지 않는다.
- `harness/check-progress-negative.py`는 원본 문서가 아닌 격리 사본에서 문서 누락, Task 행 누락, 증거 없는 PASS, 잘못된 상태, 없는/외부 evidence, 선언 집계 오류를 주입해 검사기가 nonzero로 거부함을 확인했다.
- `harness/test_entrypoint_exit_codes.py`는 도구 부재를 exit 2로, 격리된 build 명령의 인위적 실패를 exit 7로 구분하는 2건을 실행했다. 이는 합성 종료 코드 시험이다.
- Makefile은 Android mock·iOS simulator·Unity Editor build script로 라우팅한다. 실제 플랫폼 실행 결과는 [Android Maven](p08-android-maven-consumer.md), [iOS XCFramework](p08-ios-xcframework-consumer.md), [Unity 소비자](consumer-install.md) 증거에 별도로 기록한다.
- 문서 검사/doctor 통과는 제품 전체, 실제 스토어·인증·원격 push 또는 실기기 검증을 뜻하지 않는다.
