# StoreKit XCTest 상품 조회 — Apple Feedback 제출 초안

**제출하지 않은 로컬 초안.** 환경 식별자와 원본 로그는 제출 전 사용자가 검토해야 한다.

- 환경: Xcode 26.6 (17F113), XcodeGen 2.46.0, iPhone 16 arm64 Simulator. iOS 26.5 (23F77)에서 재현, iOS 18.6 (22G86)은 별도 독립 대조에서 정상.
- 최소 재현: 이 저장소의 `tests/StoreKitIsolation`과 `ios/StoreKit/GameBridge.storekit` 사본을 사용한다. GameBridge SDK·Backend·Unity·DB나 실제 결제 계정은 필요하지 않다. 세션은 XCTest 안에서 `SKTestSession(contentsOf:)`로 만들고, `Product.products(for:)`에 `coins_100`, `premium_unlock`을 전달한다.
- 명령: `python3 harness/run-storekit-scheme-ab.py --run-local`. 새 iOS 26.5 Simulator 두 대를 생성·보존하고 각 scheme에서 테스트 한 번씩 실행한 후 shutdown한다. 실패는 runner exit 1이다.
- 기대: local configuration에 존재하는 두 product ID가 반환된다.
- 관찰: session 생성은 성공하나 두 scheme에서 빈 배열이 반환됐다. RunAction의 StoreKit configuration 참조를 제외한 scheme은 동일하게 비교했다. 이 참조가 TestAction에 실제로 적용됐는지는 확인하지 못했다.
- 참고 증거: [독립 비교](p05-storekit-26-isolation.md), 로컬 `artifacts/storekit-scheme-ab-izz719r6/A.xcresult`와 `B.xcresult`. 이전 iOS 18.6 대조는 `artifacts/storekit-isolation-products-dwknj5y4/18-6-products.xcresult`다. 원본 xcresult·로그에는 환경 정보가 포함될 수 있어 공유 전 검토한다.

Apple 내부 결함이라는 결론이나 특정 지원 여부를 주장하지 않는다. 실제 활성 configuration 확인 방법과 해당 조합의 지원 여부를 문의하는 자료다.
