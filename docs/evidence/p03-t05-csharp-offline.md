# P03-T05 C# Offline 기반 검증

- 시각: 2026-11-10 Asia/Seoul. Unity 6000.5.8f1에 포함된 .NET SDK 8.0.318과 Unity managed reference, Unity 공식 Newtonsoft 3.2.2 DLL을 사용했다.
- `scripts/check-csharp-compile.sh`: Android, iOS, Editor, 미지원 플랫폼 분기 네 개 독립 컴파일 종료 0, 경고·오류 0. Unity Editor import, IL2CPP 또는 플랫폼 링크가 아니다.
- `scripts/smoke-csharp-registry.sh`: 종료 0. 요청/세션 상관관계, timeout·취소·중복 callback, 대기열 상한, 종료, Editor-only Fake 로그인·보류·취소·중복 지급 방지, facade 상태·동시 초기화·호출자별 취소 및 새 session ID 확인. 독립 .NET 프로세스의 메모리 Fake로 실행했다.
- 한계: Unity Editor Play Mode·씬 전환·domain reload·native bridge 왕복은 라이선스 대기로 미실행. 공용 facade의 capabilities·push·sync·이벤트 등과 Native operation 연결도 미완료다.
