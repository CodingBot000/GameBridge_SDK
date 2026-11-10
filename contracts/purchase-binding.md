# 구매 account binding — 구현 중인 계약

서버는 인증된 사용자와 app ID의 조합에 대해 Apple `appAccountToken`용 무작위 UUID와 Google `obfuscatedAccountId`용 별도 무작위 UUID를 안정적으로 발급한다. 두 값은 email·사용자 이름·원본 계정 ID에서 파생하지 않으며, 각 스토어 값은 서로 다르다. 사용자·앱이 다르면 다른 값이어야 한다. `PurchaseBindings`는 DB unique 제약과 원자적 insert를 사용한다.

Native 구매 adapter는 서버가 인증된 세션에 대해 발급한 값을 사용하고, 검증 서버는 스토어에서 확인한 binding과 현재 사용자·최초 구매 소유자를 비교해야 한다. Unity 공개 UserProfile이나 로그에 원본 구매 증명·ID token·binding을 추가하지 않는다.

현재 binding DB 서비스와 Android/Swift Native 거래 상태기계의 독립 시험이 구현됐다. session에 app ID를 안전하게 연결하는 경로, Native binding 제공 API, 실제 스토어 adapter와 서버 검증은 미완료다. 기존 session의 app ID를 추측해 이관하지 않는다. 실제 스토어 거래 성공으로 간주하지 않는다.
