"""
Database Table Creation Script
-------------------------------
This script creates all database tables defined in our models.

Run this once to set up your database:
    python create_tables.py
"""

from app.database import engine, Base
from app.database import engine, Base
from app.models import StringModel  # Import required to register model with Base.metadata

def create_tables():
    """
    Creates all tables defined in models.py
    
    How it works:
    1. Base.metadata contains info about all our models
    2. create_all() generates SQL CREATE TABLE statements
    3. Executes them against our database
    
    What happens:
    - If table doesn't exist: Creates it
    - If table exists: Does nothing (safe to run multiple times)
    
    Note: This doesn't handle migrations (changing existing tables).
    For production apps, use Alembic for migrations.
    """
    print("Creating database tables...")
    
    try:
        # This line does the magic!
        # It looks at all classes that inherit from Base (like StringModel)
        # and creates corresponding tables in the database
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tables created successfully!")
        print("\nCreated tables:")
        print("  - strings")
        print("\nColumns in 'strings' table:")
        print("  - id (TEXT, PRIMARY KEY)")
        print("  - value (TEXT, UNIQUE)")
        print("  - length (INTEGER)")
        print("  - is_palindrome (BOOLEAN)")
        print("  - unique_characters (INTEGER)")
        print("  - word_count (INTEGER)")
    # sha256_hash column removed; id stores the SHA-256 hash
        print("  - character_frequency_map (JSON)")
        print("  - created_at (TIMESTAMP)")
        
    except Exception as e:
        print("❌ Error creating tables!")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Is PostgreSQL running?")
        print("2. Can you connect to the database? (run: python app/database.py)")
        print("3. Do you have permission to create tables?")

if __name__ == "__main__":
    create_tables()