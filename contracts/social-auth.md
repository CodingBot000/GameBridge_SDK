# Social authentication extension

Approved separately by user document37; original frozen0.1 portfolio evidence is historical. Existing GOOGLE/APPLE enum meanings remain; FACEBOOK is appended (C#3). No automatic account linking/email merge or purchase transfer.

| Proof | Native exchange field | Server validation |
| --- | --- | --- |
| Google/Apple ID token | legacy idToken; proofType defaults ID_TOKEN | signedJWT issuer/aud/expiry/nonce + one-use challenge |
| Facebook Classic | proofType FACEBOOK_ACCESS_TOKEN, accessToken | Meta debug valid/USER/app_id/user_id/scopes/expiry/data-access expiry; no JWT nonce assumption |
| Facebook Limited | proofType FACEBOOK_LIMITED_ID_TOKEN, idToken | official RS256 JWKS, exact issuer https://www.facebook.com, audience/expiry/nonce |
| Android Apple web | server callback code only; Native receives one-use verifier-bound completion | state/code exchange/token verification, no code/client-secret in Native or Unity |

Challenge proofType is stored and cannot be downgraded from Limited to Classic. Classic->Limited upgrade is accepted only with the same signed server nonce. Classic bearer credentials may be reused with a fresh challenge and fresh Meta validation, as required by OAuth; this is not cryptographic nonce binding or stolen-bearer prevention. Protect Native storage/TLS/logs; iOS Limited is recommended. There is no token blacklist that breaks legitimate re-login.

Provider identity is verified provider+issuer+subject+app scope, not displayName/email. Facebook subject is additionally namespaced by verified Meta App ID, identically for Classic/Limited, to prevent accidental merging on app-ID changes. New authentication uses the existing SessionService and purchase account binding/ledger. Server App Secret/Apple private key never enter client settings. Host callbacks stay Native; C# gets typed profile/result only.

Apple web start stores only state/nonce hashes + verifier S256 challenge, fixed app/service/callback/return and expiry. Callback claims stage atomically before external code exchange and uniquely records code hash. It validates exact Services ID JWT audience + issuer/signature/nonce/expiry, ignores untrusted first-consent user data, then stores verified identity and a60s one-use handle hash. No session exists until verifier-bound complete succeeds under row lock and invokes the existing SessionService. No token/code/client secret in the return URL. Complete replay409; invalid state/verifier/expiry401; canceled/failed complete returns no session. App restart loses verifier. New V11 is forward-only; no existing migration/data reset.

Legacy omission/null of proofType explicitly maps to ID_TOKEN at Controller boundaries, preserving Jackson HTTP compatibility as well as Kotlin callsites. Callback raw form body bypasses servlet form-to-parameter reconstruction but retains the existing bounded replay/body filter and a stricter64KiB form bound. Only this registered form route is mapped explicitly by the OpenAPI guard.
