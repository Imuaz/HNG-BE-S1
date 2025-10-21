"""Simple migration runner for SQL files in migrations/.

Usage:
    python migrations/apply_migration.py 0001_drop_sha256_hash.sql

It uses DATABASE_URL from environment (same as app/database.py).
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not set in environment")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python apply_migration.py <migration_sql_file>")
    sys.exit(1)

migration_file = sys.argv[1]
if not os.path.exists(migration_file):
    print(f"Migration file not found: {migration_file}")
    sys.exit(1)

with open(migration_file, 'r') as f:
    sql = f.read()

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    print(f"Applying migration: {migration_file}")
    conn.execute(text(sql))
    conn.commit()
    print("Migration applied.")
