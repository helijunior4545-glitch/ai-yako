# Independent extraction contract

The portable unit is the complete `app_qvac_financial/` directory. It owns models, migrations, templates, static, URL namespace, application logic, and protocol contracts. It does NOT own root settings.py, root urls.py, DATABASES, deployment credentials, or the host project name.

To transfer: (1) create a clean Django host, (2) configure PostgreSQL and STATIC_ROOT, (3) install app dependencies, (4) add AIYakoConfig to INSTALLED_APPS, (5) mount `app_qvac_financial.urls`, (6) generate/apply migrations for that DB, (7) test HTTP and backend services, (8) integrate actual QVAC/WDK clients and their security controls.

Portability constraints: no `lojasnova`, `app_config`, `Loja`, billing, tenant DB alias, or AUTH_USER_MODEL dependency inside AI Yako. The Django host is a replaceable adapter, not an application dependency. A server-centric PostgreSQL product is not fully offline without a separately engineered offline client; QVAC on-device inference can still be independent of the DB choice.
