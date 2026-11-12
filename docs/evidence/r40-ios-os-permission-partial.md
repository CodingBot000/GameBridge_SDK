# R40 iOS OS 권한 거부 부분 검증

- 실행 소스: 로컬 HEAD `e0acbd6`과 이 문서와 함께 커밋된 test-only `tests/UnityIosPermissionConsumer/MockIosPlayerScenario.cs`. 검증 당시 해당 테스트 소스는 미커밋 상태였다.
- 환경: Unity 6000.5.8f1 Simulator export, Xcode Simulator arm64 ad-hoc 빌드, 새 iPhone 16 iOS 18.6 Simulator. 앱은 합성 sandbox 설정을 사용하며 외부 로그인과 실제 인증키를 사용하지 않았다.
- 실제 OS 알림 권한 팝업에서 **허용 안 함**을 선택한 뒤 Unity 공개 API를 통해 첫 요청 `DENIED`, 등록 `PERMISSION_DENIED`, 재요청 `DENIED`를 확인했다.
- 결과 marker: `GB_IOS_PERMISSION_FIRST_DENIED PASS`, `GB_IOS_PERMISSION_REGISTRATION_BLOCKED PASS`, `GB_IOS_PERMISSION_SECOND_DENIED PASS`, `GB_IOS_PERMISSION_RESULT PASS IOS_OS_DENIED`.
- 실행 산출물은 로컬 `artifacts/unity-ios-mock.PLDU8j/permission-markers.log`에 있다. 원본 전체 콘솔 로그는 커밋하지 않는다. 첫 설치의 잘못된 앱 경로 오류는 수정 후 재설치했다.
- 이는 Simulator의 실제 OS 권한·SDK host adapter 경계 시험이다. 이 시험은 Mock 거부 주입, 실제 iOS 기기 및 APNs 발송 시험이 아니다. 이후 독립 managed Mock 거부 주입은 PASS했으나 OS 시험의 무인 재현 및 전체 시나리오 집계가 남아 R40 전체는 PARTIAL이다.

이 문서의 PARTIAL 표기는 해당 시험 당시 상태다. 이후 Android OS·iOS OS·Mock을 구분해 재현한 현재 범위는 [R40 통합 증거](r40-os-and-mock.md)를 참조한다. 실제 provider/실기기는 여전히 미검증이다.
