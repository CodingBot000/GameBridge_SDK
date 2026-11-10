# 보안 및 신뢰 경계 — 개발 중

이 문서는 현재 구현과 미완료 항목을 함께 기록한다. 상용 서비스의 보안 심사 또는 스토어 승인 결과가 아니다.

## 실행 모드와 저장소

- `LOCAL_MOCK`은 별도 PostgreSQL과 명시적 개발키를 사용한다. 개발 인증·가짜 구매·Mock 푸시 route는 `local-mock`에서만 등록된다. Sandbox/production에서 실제 Provider 실패를 Fake 성공으로 대체하지 않는다.
- DB에 환경 표식을 두고 다른 profile에서 같은 DB를 사용하려 하면 migration 전에 거부한다. 기존 DB에 표식이 없는 경우 소유권을 임의로 추정하지 않는다.
- Native session은 Android Keystore 기반 암호화 저장소 또는 iOS Keychain의 device-only 항목에 저장한다. Unity `PlayerPrefs`에 token을 저장하지 않는다. Native session은 app ID·모드·Backend 주소에 결속되며, 다른 환경의 저장값은 전송하거나 임의 삭제하지 않는다.
- refresh 기본 만료는 최초 로그인부터 7일이며 회전 시 연장하지 않는다. refresh 전 저장소를 token 없는 `refresh_pending` 표식으로 원자 교체한다. 응답 유실·프로세스 종료 후 이전 refresh token을 재사용하지 않고 재인증한다. 저장소를 직접 구현하는 Host도 `save`를 원자적 전체 교체로 제공해야 한다.
- 로그아웃은 로컬 session을 먼저 삭제한다. 서버 revoke가 확인되지 않으면 `REVOCATION_UNCONFIRMED`를 표시한다. 현재 이 경고의 재시작 후 영속 표시와 자동 revoke 재시도는 미구현이다.
- 새 형식의 저장 session에만 provenance 검사가 적용된다. 이전 형식은 자동 이전·삭제하지 않으며 재인증이 필요하다.

## 인증과 구매

- 실제 인증 경로는 Google/Apple의 공개 JWKS, RS256 서명, issuer, app별 audience, 만료와 서버 challenge nonce hash를 확인한다. challenge 소비와 사용자 identity/session 생성은 DB transaction으로 묶는다. 실제 Provider 발급 token과 실기기 시험은 아직 사용자 설정 대기다.
- 인증 rate limit은 사용자가 선택한 단일 프로세스 IP별 rolling 1분 challenge 30회·교환 10회가 기본이다. 전달 proxy header는 신뢰하지 않고 다중 서버 전역 제한은 지원하지 않는다.
- 구매 원장·Google/Apple verifier 및 Google finalizer는 Mock·synthetic 데이터와 전용 DB 경계에서 검증했다. 실제 Google/Apple 거래·finalization은 실행하지 않았고 환불/취소 알림 운영은 범위 밖이다. Mock 지급을 실결제 성공으로 취급하지 않는다.
- 사용자가 선택한 푸시 정책은 등록 해제·로그아웃 시 해당 session 토큰 즉시 삭제다. local-mock 신규 등록과 삭제는 검증했다. FCM/APNs sender와 등록 경계는 구현됐지만 실제 원격 연결은 미검증이며 과거 session 미연결 시험 행은 자동 삭제하지 않았다.

## 현재 제한

- Mock 서버는 기본 loopback에만 노출한다. Android 및 iOS Debug 샘플의 HTTP 예외는 명시된 로컬 주소에만 적용되며, iOS Release에는 해당 예외가 없다. 실제 Provider에서는 TLS 검증을 무시하거나 오류를 Mock으로 전환하지 않는다.
- Google/Apple Provider는 Native 및 Unity bridge에 연결됐으나 Unity Editor/JNI/IL2CPP 및 실제 기기 보안 저장소 시험, 실제 스토어 인증·결제·푸시, 키 rotation·운영 보안 심사는 미완료다.
- 환불 자동화, Google RTDN 및 Apple Server Notifications 운영, 스토어 심사와 SLA는 이번 계획의 범위 밖이다.

## Xcode StoreKit 개발 경계

Xcode 로컬 StoreKit은 iOS 18 이상과 host 소모품 이력 opt-in을 요구한다. StoreKit이 검증한 Xcode 거래만 Native가 받아 고정 필드 후보 식별자를 생성하고, 같은 식별자 이력의 단일성을 확인한다. 개발 서버는 Apple JWS를 검증하지 않는 fake 지급이며 별도 Xcode 사용자·지갑과 개발 DB profile에 격리된다. 서버는 시도 UUID와 거래 키를 원자적으로 연결해 다른 시도의 충돌을 거부하고, Native Keychain은 finish 확인 후 시도 단서를 삭제한다. 전용 simulator/local DB 응답 유실과 저장소 인스턴스 재생성 시험은 통과했으나 실제 프로세스 종료·Unity player·Apple sandbox는 미검증이다.
