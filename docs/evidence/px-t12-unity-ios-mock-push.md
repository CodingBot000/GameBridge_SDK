# PX-T12 Unity iOS Simulator LOCAL_MOCK Push 부분 검증

- 결과: **Mock 등록·수신·동일 ID 중복 억제·Unity 메인 스레드·background/foreground·테스트 연결 단절/복구·A→B 세션 전환·등록 해제/로그아웃 PASS**. 실제 APNs 및 Push/Lifecycle 전체 완료를 뜻하지 않는다.
- 소스 `5d3993423f1e56fdf3a2c28d75dc2e6f64142de2`, 실행 당시 tracked-clean. Unity 6000.5.8f1, Xcode 26.6, iOS 18.6 ARM64 Simulator, Unity IL2CPP 개발 빌드, 별도 local-mock PostgreSQL DB. Apple 계정·개인키 없는 Simulator 로컬 ad-hoc 서명.
- 실행: `python3 harness/run-unity-ios-mock-push-e2e.py --run-local --staging <검증된 staging> --package-cache <동일 버전 Unity cache>`, exit 0. Unity registry timeout 때문에 기존에 내려받은 notifications 2.5.0/Newtonsoft 3.2.2를 새 격리 프로젝트에 embedded 복사했고 패키지 자체 테스트만 제외했다. 원본 cache·전역 설정은 수정하지 않았다.
- Unity Player → Swift C ABI → local Backend에서 동일 메시지 중복은 한 번 전달됐다. 실제 Simulator background/foreground 전환 뒤 test-only loopback TCP 경로의 연결을 끊어 오프라인 메시지가 전달되지 않음을 확인했고, 재연결 뒤 새 메시지가 전달됐다. OS 전체 Wi-Fi 차단 시험은 아니다.
- A 로그아웃 및 B 전환 후 A의 발송은 403, B 이벤트는 한 번 전달됐다. 등록 해제/로그아웃 후 device_tokens row 0개. Swift Native event callback의 Unity 전달 및 API 완료는 main-thread assertion을 통과했다.
- UnityFramework binary SHA-256 `187cdfc7c052ae6124bb8c75879c01cab5eecbaae3114c5a5c2b61dc2aebfeb3`. 원본 로그·기기 식별자·합성 키·DB·빌드는 Git에 넣지 않는다.
- **초기 시험에서 NOT_RUN:** iOS 프로세스 강제 종료·재시작 및 pending, 임의 지연 Native callback 및 재연결 실패 명시적 주입, 실제 Apple 로그인·StoreKit·APNs, 실제 기기. 후속 시험 결과는 아래에 기록한다.


## 강제 종료 및 pending 복구 추가 시험

- 소스 `0b105c3dfbf2681e6c3225fe9a332b5b13d805f3`, 실행 당시 tracked-clean. `harness/run-unity-ios-mock-restart-e2e.py --run-local --staging <staging> --package-cache <동일 버전 cache>` 전용 iOS 18.6 ARM64 Simulator 실행 exit 0, `artifacts/unity-ios-restart-vidqoa21/result.json` PASS.
- test-only loopback proxy가 서버의 최초 구매 검증 200 commit 응답을 503으로 바꿨다. Unity 앱을 Simulator에서 terminate/relaunch하고 서로 다른 PID, 세션 복원, pending 1회 복구·재sync 0건, DB 원장 1건·100코인 및 Unity main-thread를 확인했다. 단순 background 전환과 다른 시험이다.
- UnityFramework binary SHA-256 `36e6da9a02d0c49ea7bd6baa0865ed0181f5235ca6388d2308d0ea8061a29225`. Simulator 로컬 ad-hoc 및 exact-version embedded package cache를 사용했다.
- 임의 지연 Native callback 및 재연결 실패 명시적 주입, 실제 Apple 로그인·StoreKit·APNs와 실기기는 여전히 NOT_RUN이다.

## 재연결 실패 주입 추가 시험

- 소스 `837c016458159e836253998c9f212a50a616fd53`, tracked-clean. 새 전용 iOS 18.6 Simulator에서 Push Runner exit 0 (`artifacts/unity-ios-push-gcmp59n7/result.json`).
- test-only loopback TCP proxy가 SDK 연결 재시도 6회를 거부한 뒤 연결을 복구했다. Unity Player가 복구 후 새 Mock 이벤트를 받고 기존 중복·background/foreground·A→B 전환·등록 해제 검사도 통과했다. 이는 OS 전체 Wi-Fi 차단이나 실제 APNs 시험이 아니다.
- UnityFramework SHA-256 `f515a7f71d858e815985d77c9e90fe12566159bdc8ba98ab6ca9f5cf242e486b`. Simulator local ad-hoc 및 exact-version embedded cache를 사용했다.

## 기존 인증·구매 회귀

소스 `90311242becb02c649eea29844237875d3a0b8cd`, tracked-clean에서 기존 Unity iOS LOCAL_MOCK 인증·구매 전체 Runner를 새 전용 iOS 18.6 Simulator·DB로 재실행해 exit 0, `artifacts/unity-ios-e2e-zizcrlvt/result.json` PASS. local ad-hoc Simulator signing 및 exact-version embedded Unity package cache를 사용했다. 실제 Apple 로그인·StoreKit 결제는 미실행이다.
