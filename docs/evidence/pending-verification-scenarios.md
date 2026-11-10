# 결제 대기·검증 실패 로컬 회귀

`artifacts/play-pending-08y6r7o4`의 Play gateway fake 17건은 PENDING일 때 verifier에 접근하지 않고, 같은 거래의 PURCHASED 이후에만 지급 결과를 전달하며 중복 요청이 한 번의 synthetic 지급으로 귀결되는 것을 확인했다. 서버 검증 timeout은 `VERIFICATION_PENDING`과 미지급으로 남고 이후 검증 성공 시에만 구매 ID가 반환됐다. 전용 DB `gamebridge_ci_9870ea16ad`에서는 synthetic PENDING proof가 구매·finalization job을 만들지 않았다.

`artifacts/storekit-pending-1794339452.xcresult`에서는 iOS 18.6의 Xcode Ask to Buy가 pending으로 반환됐고 fake 지급 호출이 없었다. `artifacts/xcode-storekit-e2e-azc6m12g` 및 `artifacts/xcode-storekit-e2e-71smgiej`에서는 local DB 지급 commit 뒤 응답을 일부러 유실시키자 StoreKit 거래가 unfinished로 남았고 Keychain 인스턴스를 다시 연 뒤 동일 attempt로 복구·finish해 잔액 100이 유지됐다. 실제 프로세스 강제 종료, Unity player, Apple sandbox 및 Google Play 네트워크 호출은 포함하지 않는다.
