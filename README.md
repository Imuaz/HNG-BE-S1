# String Analyzer API

Lightweight FastAPI application that analyzes strings and stores their computed properties in a PostgreSQL database.

Quick start

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set `DATABASE_URL` in a `.env` file (example):

```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

3. Create tables (development only):

```bash
python create_tables.py
```

4. Run the API:

```bash
uvicorn app.main:app --reload
```

Applying the migration to remove the redundant `sha256_hash` column

```bash
python migrations/apply_migration.py migrations/0001_drop_sha256_hash.sql
```

Notes & recommendations

- For production use, enable Alembic for migrations instead of the ad-hoc SQL script in `migrations/`.
- Add CI (GitHub Actions) to run linting (ruff/flake8), formatting (black), and tests.
- Add automated tests that run against a test database (use Docker or a CI-provided DB).
- Prefer logging over `print()` inside library modules; keep `print()` in test scripts or example harnesses.
- Consider separating liveness and readiness endpoints (readiness should check DB connectivity).
