# PostgreSQL persistence profile

The AI Yako Django server uses PostgreSQL via Django ORM and the host DATABASES setting. No SQLite or local database. Device-side cryptographic keys are not database records and must not be transmitted to PostgreSQL.

All persisted application metadata is scoped by the independent QVACIdentity and QVACDevice models. Server-side repository examples live in `server/persistence/repositories/postgres.py`. Business operations must not import the host's tenant/account/billing models.

The runtime has no DB imports and remains a pure orchestration component. If a future native client needs offline persistence, design it separately rather than silently reintroducing SQLite. Server-backed features require connectivity; do not market them as fully offline.
