# Runtime persistence boundary

No local SQLite or other local database is used in the current AI Yako deployment. The runtime remains independent of Django and delegates server persistence to explicit application interfaces. PostgreSQL storage is implemented in the optional Django server layer. Never store wallet private keys or seed phrases in PostgreSQL.
