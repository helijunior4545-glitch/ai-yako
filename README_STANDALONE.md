# AI YAKO standalone Django host

This directory hosts the existing `app_qvac_financial` Django app without the LojasNova project.

## Prerequisites
Python 3.11+, PostgreSQL, pip and a PostgreSQL database/user created beforehand.

## Local run (from repo root)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Set environment variables; do not commit real secrets.
set -a; source .env.example; set +a  # EXAMPLE VALUES ONLY: replace secrets first
python manage.py check
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

App URL prefix: `/qvac-financial/`. The Django host does not automatically install or validate the Linux desktop client, QVAC model/SDK, or WDK integrations.

**Important:** This bootstrap supplies only standard Django/PostgreSQL dependencies. If `app_qvac_financial` imports third-party packages, add and pin their verified versions to `requirements.txt`. Run `python manage.py check`, `python manage.py migrate --plan` and actual smoke tests before claiming reproducible deployment. Do not use example credentials for production.
