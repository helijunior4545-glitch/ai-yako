# Real infrastructure validation
- Existing PostgreSQL may be used only after reviewing routers, database grants, migration dependencies, backups and restore drills.
- Prefer a restricted PostgreSQL role/schema even when sharing the server.
- No production migrations or destructive operations are performed by the blueprint.
- WDK tests use testnets and test assets, never real funds.
- Verify offline AI with network disabled and Django server unavailable.
- Record results, timestamps and evidence; never label stubs as working integrations.
