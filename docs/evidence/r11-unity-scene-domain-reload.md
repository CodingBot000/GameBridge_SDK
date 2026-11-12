# R11 Unity Editor scene·Domain Reload 검증

- Unity 6000.5.8f1의 격리 소비 프로젝트 EditMode test에서 reload enabled/disabled 각각 1건, 총 2건 PASS·skip 0. source `a0ba7a5`와 그 시점의 tracked-clean 상태. 결과 `artifacts/unity-consumer.EfzZEr/results.xml`; `scripts/build-unity.sh --editor-smoke` 종료 0.
- 두 설정 각각 실제 play mode에 진입하고 scene을 만들고 전환·unload했다. SDK 초기화 후 dispatcher 1개, shutdown/dispose 후 0개, 새 client 생성 후 1개 및 재dispose 후 0개를 확인했다.
- 이전 session 합성 이벤트는 새 client에 전달되지 않고 현재 session 이벤트는 한 번만 전달되며, dispose 후 이벤트는 구독자에 전달되지 않음을 확인했다. 두 test 각각 완료 marker를 XML에서 검사했다. 이는 Unity Editor에서 합성된 callback 경계이며 OS/원격 푸시 시험은 아니다.
- Registry 접근 불가로 기존 exact-version package cache를 격리 프로젝트에 embedded했으며, 설치된 Unity의 Test Framework 1.7.0/NUnit 2.1.0을 사용했다. 원본 package cache와 사용자 프로젝트는 변경하지 않았다.
