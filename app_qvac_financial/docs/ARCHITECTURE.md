# AI Yako architecture V4

Host adapters: existing LojasNova Django settings.py/root urls.py during development, independent Django settings.py/root urls.py after transfer. Both use PostgreSQL. Portable app owns its own URL patterns, models, templates, static files and domain services. No dependency on commercial LojasNova modules. Runtime is DB-free, server repository uses Django ORM. QVAC and WDK integration contracts are currently fail-closed. A PostgreSQL-backed web app cannot claim offline database operation; local QVAC inference remains a separate future capability.
