# P02-T04 Mock 완료 처리 검증

- 시각: 2026-11-10 Asia/Seoul. 사용자 선택: 기본 동시 1개, 최초 5초 지수 백오프. 설정명은 USER_SETUP 및 DECISIONS 참조.
- 환경: 전용 local-mock PostgreSQL 17.6. 별도 시험 DB와 synthetic 거래만 사용; 테스트 데이터는 보존.
- opt-in Backend JUnit: 종료 0, 10건, 실패 0·skip 0. 5초 첫 재시도, 5/10/20초 계산, worker 객체 재생성, 원장 1회 유지 및 두 worker가 기본 한 slot을 초과하지 못함을 확인.
- 실제 프로세스 재시작: 첫 Mock 완료 처리 실패 후 DB `PENDING`, attempt 1을 확인하고 전용 서버 종료. 재시작 후 `FINALIZED`, attempt 2, 구매 `GRANTED/FINALIZED`, ledger 1건·합계 100 확인. 첫 수동 종료 시도가 늦어 재시작 증거가 되지 못한 실패와 후속 재시험은 WORK_LOG에 기록.
- 한계: 최초 실패 후의 재시작만 확인했으며 실행 도중 강제 종료, 다중 서버 설정 불일치, 실제 Google Play consume/ack·Apple 거래는 검증하지 않았다. Mock worker의 성공은 실제 스토어 완료 처리가 아니다.
