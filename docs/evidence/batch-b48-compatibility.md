# Batch B Unity 및 OS 연동 검증

Batch A의 `0.1.1-dev` staging을 재사용했다. SDK 기준 커밋은 `026716fdedfdf0ff59e2156d1bfa54a0309e5320`, staging manifest SHA-256은 `2248c8dc3de252417bfd5fa39bfb3912e1347c7d348c68512fa0bead5a6997ae`다. Batch B는 기존 검증 진입점에 설치 방식과 런타임 선택을 추가했다. 공개 API, C ABI, Bridge v1과 패키지 바이트는 Batch A에서 검증한 그대로다.

| 대표 조합 | 실행 결과 |
| --- | --- |
| Unity 6000.5.8f1 Editor | 새 소비자에서 UPM 샘플 Import 및 같은 프로젝트에서 재Import GUID 유지. Editor 오프라인 테스트 1개 통과 |
| Unity 6000.5.8f1 · Android API 34 | 이전 `0.1.0-dev` APK 설치, LOCAL_MOCK 로그인과 구매 응답 유실, 동일 패키지·서명 및 더 높은 versionCode의 `0.1.1-dev` APK로 `adb install -r`, 앱 재시작과 세션·미완료 구매 복구, 재동기화·로그아웃 성공. 장부 1건·100코인 |
| Unity 6000.5.8f1 · Android API 30 | 후보 APK로 LOCAL_MOCK 초기화·로그인·구매·재시작 복구·로그아웃 성공. 장부 1건·100코인 |
| Unity 6000.5.8f1 · Android API 36 | 첫 스트리밍 설치 실패. 비스트리밍 설치로 APK 반입을 확인했다. 그 사전 설치가 남은 기기는 기존 보호 검사에 따라 실행에서 제외했다. 새 전용 AVD에서 비스트리밍 설치부터 전체 LOCAL_MOCK 흐름까지 통과. 장부 1건·100코인 |
| Unity 6000.5.8f1 · iOS 26.5 | 새 Export, ad-hoc 서명·Meta 동적 프레임워크 4종 확인, LOCAL_MOCK 초기화·인증·구매·로그아웃 성공. Player marker 23개, 장부 1건·100코인 |
| Unity 6000.5.8f1 · iOS 18.6 | 동일 staging의 Batch A 덮어 설치·복원 증거를 재사용. [Batch A 기록](batch-a47-dev-compatibility.md) |
| Unity 6000.4.0f1 | DEFERRED_ENV. Android/iOS 모듈이 없고 설치된 Editor의 테스트 프레임워크 1.6.0, NUnit 2.0.5, UGUI 2.0.0은 기존 샘플 검증의 고정 버전 1.7.0, 2.1.0, 2.5.0과 다르다. UPM 최소 Unity 6000.5는 유지한다. |

Android Maven R8 및 기존 Host/PBX 충돌 음성 검사는 Batch A의 동일 패키지 증거를 썼다. iOS 26.5 성공 범위는 LOCAL_MOCK이다. 기존 StoreKit 26.5 실패, 전체 Strict 제한은 계속 적용된다.

## Android Google 실제 계정

Native `com.gamebridge.sample`, Unity `com.gamebridge.sdk.googleoauth.androidtest` APK를 각각 빌드·서명 검증하고 전용 API 34 AVD에 설치했다. 두 APK의 실제 SHA-1은 `48:14:A5:59:DE:D1:61:1F:5F:E5:47:09:36:86:E9:29:8D:9A:A6:36`이다. 별도 DB의 HTTPS Sandbox는 CA와 호스트 이름 검증을 통과했다. 시험용 APK만 localhost에 대해 테스트 CA를 신뢰하도록 구성했다.

Google Cloud의 패키지·서명별 Android OAuth 클라이언트 등록과 테스트 계정 인증은 WAITING_USER다. 실제 로그인·취소 후 재시도·세션 복원·로그아웃 및 실제 인증정보의 Unity 이벤트·로그 점검은 미실행이다. 사용자 설정은 [Android 설정 절차](../USER_SETUP.md)를 따른다.

후속 실제 계정 시험 결과는 [Android Google 검증](android-google-live-20261125.md)에 기록했다. 위 WAITING_USER는 Batch B 당시 상태다.
