# P02-T06 격리 Backend smoke

2026-11-13, 로컬 소스 HEAD `1051557`에 미커밋 smoke 격리 runner 및 loopback/DB 선택 변경을 적용한 상태에서 실행했다. `python3 harness/run-backend-smoke-isolated.py --run-local`은 새 무작위 DB/role, 임시 loopback port와 합성 키로 Backend를 기동하고 결과를 확인한 뒤 서버만 종료한다. 생성 DB와 role은 보존한다.

- 성공: 인증 16, 구매 13, 기기·설정 19 assertions. 동일 거래 중복 및 다른 사용자 충돌 검사 포함.
- 음성: 별도 복사본에서 구매 후 기대 잔액을 100에서 101로 바꾸자 해당 assertion에서 실패했다. 원본 테스트는 변경하지 않았다.
- 증거 위치: `artifacts/backend-smoke-isolated-he08vjff` (로컬 생성물, 원본 로그는 저장소에 포함하지 않음); 테스트 DB `gamebridge_ci_a6026477d3`.
- 범위: local-mock Backend HTTP/DB만 검증했다. Unity Player, 실제 인증·스토어, FCM/APNs 원격 전송은 이 시험에서 실행하지 않았다. 단일 smoke가 다른 Task의 완결성을 보장하지 않는다.
