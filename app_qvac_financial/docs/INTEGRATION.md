# Integration with an existing Django host

1. Keep AI Yako in `app_qvac_financial/` with its own app label and models.
2. Review host `DATABASE_ROUTERS`: the correct database alias must be used for every AI Yako model and migration. Do not assume `default` works.
3. Create least-privilege PostgreSQL credentials or isolate schema; ensure no cross-application grants.
4. Review global middleware: it must not force `Loja`, billing, theme or commercial authentication on AI Yako routes.
5. Add to `INSTALLED_APPS` and mount `urls.py` manually only after review. No financial endpoints enabled.
6. Generate Django migrations after inspecting the exact target database and migration plan; back up before applying.
7. Verify host ASGI routing; do not expose WebSocket consumers until independent device authentication works.
8. Run all offline tests without Django configured.
9. Never copy secret keys, wallet seed phrases or production tokens to the repository.
