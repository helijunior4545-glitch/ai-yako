# Controlled deployment gates

**Gate 0 — generator**: parse blueprint, compile generated Python, run unittest suite in isolated directory. Do not overwrite an existing app.
**Gate 1 — Django integration**: inspect host database routers, middleware, ASGI, URL dispatcher and commercial auth. Ensure AI Yako routes are independent. Run `manage.py check` and `makemigrations app_qvac_financial --dry-run --check` appropriately for host Django version.
**Gate 2 — database**: inspect `sqlmigrate`/`migrate --plan`, create backups, restrict PostgreSQL role and schema; only then apply migrations in staging.
**Gate 3 — read-only preview**: enable landing, workspace, capabilities and health on staging; verify CSP, HTTPS, headers, static files, CSRF rules and rate limits.
**Gate 4 — finance**: enable no financial operation until native SDKs, cryptographic approvals, key custody, testnet transactions, negative tests, and independent security review are complete.

Do not call a UI shell a functioning QVAC/WDK product. Validate official hackathon submission rules separately.
