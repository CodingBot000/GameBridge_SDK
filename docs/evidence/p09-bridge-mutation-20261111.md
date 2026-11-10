# P09 Bridge mutation 시험 — 2026-11-11

- 기준: `e0afb97` + 검사기 미커밋 변경. 새 `artifacts/bridge-mutation.*`의 registry 복제본에서 중복 응답 guard만 제거했다.
- `harness/check-bridge-mutation.py`: 손상된 복제본의 smoke가 해당 registry runtime 경로에서 실패함을 확인, 원본 파일 미변경.
- 정상 원본 재실행: C# 독립 smoke 1, Swift CBridge 3, Android core 2·bridge 6 결과 통과. Android 일부 build task는 up-to-date.
- Unity Editor scene/Domain Reload, IL2CPP, Android JNI 및 모든 R01~R12 시나리오의 완전 검증은 아니다.
