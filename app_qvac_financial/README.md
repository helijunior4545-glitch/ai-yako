# AI Yako — Financial Intelligence Network (V4)

Portable Django application hosted temporarily by the existing LojasNova project. The HOST owns its settings.py, root urls.py, PostgreSQL connection, ASGI and deployment; AI Yako owns its app code, models, views, templates, static files, services, and migrations. No imports from LojasNova commercial modules.

## Host integration
Read `docs/HOST_INTEGRATION.md`. Do not copy settings.py or root urls.py into this app. In the LojasNova host, add the app to INSTALLED_APPS and include its URLs. PostgreSQL is the only server database supported by this deployment profile. Host router must route AI Yako models consistently. No SQLite database or local database is used.

## Extraction to independent host
Read `docs/PORTABILITY.md`. Mount this same app in a clean Django project with PostgreSQL and the same URL namespace. Avoid references to host users, tenant models, billing, settings modules, or business middleware.

## Financial security
QVAC and WDK SDK integrations are not yet implemented. Financial actions stay disabled. Testnet only during integration. PostgreSQL does not hold wallet signing keys. No false inference or fake wallet transactions.
