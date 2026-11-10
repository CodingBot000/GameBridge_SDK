# R50 필수 suite·증거 누락 게이트

`python3 harness/run-r50.py`는 `harness/test_aggregation.py`의 필수 suite 누락·미실행·0건·실패·부분 결과 검증과 `harness/check-progress-negative.py`의 문서·증거 누락 및 외부 symlink 거부를 실행한다. 둘 중 하나라도 실패하거나 실행할 수 없으면 scenario가 PASS가 되지 않는다.

2026-11-11 로컬 실행에서 runner 종료 0 및 `R50 PASS`를 확인했다. 이는 하네스 자체의 부정 검증이며 Unity player나 실제 외부 서비스가 통과했다는 뜻은 아니다. 전체 집계는 별도 required lane과 미실행 상태를 유지한다.
