# AI Yako V5.2 — Independent authentication + public jury preview

- Public: `/qvac-financial/`, `/qvac-financial/demo/` (static synthetic read-only preview).
- Private: `/qvac-financial/app/` guarded by independent web cookie and DB session.
- Sign in `/qvac-financial/auth/`; sign up `/qvac-financial/auth/signup/`; registration API requires `AI_YAKO_REGISTRATION_INVITE` >=32 chars.
- Jury demo does not authenticate or grant access to the private workspace. It performs no financial actions and no database queries.
- Cookie `qvac_web_session` uses Secure, HttpOnly, SameSite Strict, Path `/qvac-financial/`, 8h expiry.
- The host's global CSRF_FAILURE_VIEW may return a 302 to `/` for failed CSRF; requests remain rejected. This installer does not modify host settings or app_store. Consider a host-level API-specific 403 handler as a separate reviewed change.
- Host must provide HTTPS, Django CSRF middleware and properly scoped host. Test login, logout, revoked session, CSRF and invitation policy before production use.
- No database schema changes or migrations. Device enrollment and real wallet/transaction flows remain disabled.
- Jury preview is an interface-only demonstration, not a live integration.
