# Host integration — LojasNova infrastructure

AI Yako is a portable Django app. LojasNova's root settings.py and urls.py are used ONLY as host wiring during development/deployment. Do not import LojasNova apps or copy its configuration into AI Yako.

## In existing root settings.py

Add `app_qvac_financial.apps.AIYakoConfig` to INSTALLED_APPS. Keep the host's PostgreSQL DATABASES configuration; no SQLite. Ensure its database router maps app_label `app_qvac_financial` to the intended PostgreSQL alias for BOTH reads/writes and migrations. Check global middleware for forced Loja, billing or commercial redirects; exclude the `ai-yako/` namespace if necessary. The host remains responsible for ALLOWED_HOSTS, CSRF, static files, TLS and deployment.

## In existing root urls.py

    from django.urls import include, path
    urlpatterns += [path('ai-yako/', include('app_qvac_financial.urls'))]

No changes are made automatically by the blueprint. Django URL names are namespaced as `app_qvac_financial:landing`, `app_qvac_financial:workspace`, `app_qvac_financial:health`.

## PostgreSQL model migrations

Use the host's normal deployment pipeline. Review the intended database alias and router first. Create and apply migrations only on the correct PostgreSQL DB. Never silently migrate an unrelated tenant DB. Database role/schema separation is preferred.

## Verify in host

    python manage.py check
    python manage.py showmigrations app_qvac_financial
    python manage.py reverse ai-yako/  # optional URL check through Django shell instead

For HTTP smoke checks, request `/ai-yako/`, `/ai-yako/app/`, `/ai-yako/health/`, `/ai-yako/capabilities/`. UI routes do not require a wallet or a model and must not claim financial execution works.

## Security

Keep signing secrets exclusively in an appropriate trusted signing environment. Testnet only. Avoid exposing user-specific data on public preview routes. Configure independent device authentication before private APIs are enabled.
