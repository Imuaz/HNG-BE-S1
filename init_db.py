"""
Database Initialization Script
-------------------------------
Creates all database tables on Railway deployment.

This will be run automatically during Railway build process.
"""

import sys
from app.database import engine, Base
from app.models import StringModel

def init_database():
    """
    Initialize database tables.
    Safe to run multiple times - only creates tables that don't exist.
    """
    try:
        print("🔧 Initializing database...")
        print(f"📍 Database URL: {engine.url}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        print("\nTables created:")
        print("  - strings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)