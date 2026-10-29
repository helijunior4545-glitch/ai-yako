# AI Yako V5.3 — capped public signup + one-click jury preview

Configuration: `AI_YAKO_MAX_USERS=20` (default 20). Set to another nonnegative integer to change the cap; 0 disables new registrations, not logins. Restart/redeploy after changing env vars.

Signup: `/qvac-financial/auth/signup/`. No invitation code, but password must meet existing 14-character and Django password validation requirements. Registration counts QVACWebCredential rows in the `default` PostgreSQL database, not LojasNova users. This includes disabled credentials. Existing users are not removed if the cap is lowered.

Concurrency: registration obtains a PostgreSQL transaction-scoped advisory lock before checking capacity and inserting identity and credential atomically. This prevents concurrent registrations from exceeding the cap across application workers using the same database. The application requires PostgreSQL for registration.

Rate limiting: existing QVACLoginThrottle table limits registration attempts by REMOTE_ADDR. A cap of 20 is NOT DDoS protection; use Cloudflare/WAF and edge rate limits.

Jurors: large button on Sign In opens `/qvac-financial/demo/`, a read-only synthetic preview without a login, session, financial operations, or access to real tenants. It is NOT a shared authenticated account. A real one-click authenticated juror account must be designed with explicit per-tenant authorization and read-only restrictions before enabling.

Isolation: this update does NOT prove tenant-level data isolation. Do not expose real customer financial data to the demo. No models or migrations are modified.

Validation: `python manage.py check`; `python manage.py makemigrations app_qvac_financial --dry-run`; test signup with two accounts, duplicate email, invalid password, limit=0, and limit reached; test CSRF and logout. Existing global CSRF failure handler may return HTTP 302; requires separate fix if so.
