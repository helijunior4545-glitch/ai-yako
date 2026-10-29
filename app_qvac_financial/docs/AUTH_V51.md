# AI Yako V5.1 authentication scope

- Jury landing `/ai-yako/` remains PUBLIC, as does health and capabilities.
- `/ai-yako/app/` is private and uses its own account/session, not LojasNova auth.
- Registration API is **disabled by default** until `AI_YAKO_REGISTRATION_INVITE` (at least 32 characters) is configured. No public registration UI. This is invitation-gated, not verified-email registration.
- Web login uses Django password hashers but NOT Django's AUTH_USER_MODEL or login sessions.
- CSRF is mandatory for browser mutations. Requires host CsrfViewMiddleware and HTTPS in production.
- Device challenge/verify supports registered, verified Ed25519 devices; **device enrollment/pairing remains disabled** until a fully authenticated ownership proof flow is implemented. Existing device rows must NOT be manually marked verified without proof of possession.
- Device session bearer tokens must never be stored in localStorage or logs. They are short lived; revocation is checked per request.
- Device `/auth/device/me/` is read-only. Synchronization, WDK, signing, WebSockets remain disabled.
- Authentication is NOT equivalent to financial approval. Human signing authorization remains unimplemented.
- Deployment gates: verify DB router, migration plan, HTTPS, CSRF, auth rate limits, reverse proxy trusted IP handling, audit events, session expiry and device enrollment before production activation.
- Registration invite is a temporary administrative bootstrap; replace with verified email invitation/passkeys before general public onboarding.
