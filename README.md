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

## Deploying to Railway

Two simple options to deploy this app on Railway:

1. Deploy using the GitHub integration (automatic build)

   - Push this repo to GitHub and connect Railway to the repository.
   - Railway will detect the project. Make sure the `Start Command` (or Procfile) is:

     web: uvicorn app.main:app --host 0.0.0.0 --port $PORT

   - Add `DATABASE_URL` as a Railway Postgres plugin or environment variable in the Railway project settings.

2. Deploy using Docker on Railway

   - Railway supports Docker deployments. The included `Dockerfile` produces a slim image.
   - The `Procfile` and `Dockerfile` are present; Railway will respect either route.

After deployment, Railway provides a `PORT` env var; the app uses that to bind Uvicorn.

## Security & env

- Don't commit `.env` with secrets. Use Railway environment variables or the Postgres add-on.
- Use HTTPS endpoints and configure connection pooling for production databases.
