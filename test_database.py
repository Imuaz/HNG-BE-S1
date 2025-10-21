"""
Test Database Connection
-------------------------
Tests database connectivity and session management.

Run: python test_database.py
"""

from app.database import engine, SessionLocal, get_db
from sqlalchemy import text

def test_connection():
    """Test basic database connection"""
    print("="*60)
    print("Testing Database Connection")
    print("="*60)
    
    try:
        connection = engine.connect()
        print("✅ Database connection successful!")
        
        # Get database info
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✅ PostgreSQL version: {version.split(',')[0]}")
        
        connection.close()
        print("✅ Connection closed successfully")
        
    except Exception as e:
        print("❌ Database connection failed!")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Is PostgreSQL/Neon accessible?")
        print("2. Is the DATABASE_URL correct in .env file?")
        print("3. Check your internet connection (for Neon)")
        return False
    
    return True

def test_session_creation():
    """Test session creation and closure"""
    print("\n" + "="*60)
    print("Testing Session Management")
    print("="*60)
    
    try:
        # Create session
        db = SessionLocal()
        print("✅ Session created successfully")
        
        # Test session with a simple query
        result = db.execute(text("SELECT 1 as test;"))
        value = result.fetchone()[0]
        print(f"✅ Session query works: SELECT 1 returned {value}")
        
        # Close session
        db.close()
        print("✅ Session closed successfully")
        
    except Exception as e:
        print(f"❌ Session test failed: {e}")
        return False
    
    return True

def test_get_db_generator():
    """Test the get_db() dependency injection generator"""
    print("\n" + "="*60)
    print("Testing get_db() Generator")
    print("="*60)
    
    try:
        # Get database session from generator
        db_generator = get_db()
        db = next(db_generator)
        print("✅ get_db() generator yielded session")
        
        # Test the session
        result = db.execute(text("SELECT 'Hello from get_db()' as message;"))
        message = result.fetchone()[0]
        print(f"✅ Session works: {message}")
        
        # Close generator (this calls the finally block)
        try:
            next(db_generator)
        except StopIteration:
            print("✅ Generator closed properly (StopIteration raised)")
        
    except Exception as e:
        print(f"❌ get_db() test failed: {e}")
        return False
    
    return True

def test_table_exists():
    """Check if our strings table exists"""
    print("\n" + "="*60)
    print("Testing Table Existence")
    print("="*60)
    
    try:
        db = SessionLocal()
        
        # Check if strings table exists
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'strings'
            );
        """))
        
        exists = result.fetchone()[0]
        
        if exists:
            print("✅ 'strings' table exists")
            
            # Get column info
            result = db.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'strings'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            print(f"✅ Table has {len(columns)} columns:")
            for col_name, col_type in columns:
                print(f"   - {col_name}: {col_type}")
        else:
            print("❌ 'strings' table does not exist")
            print("   Run: python create_tables.py")
        
        db.close()
        return exists
        
    except Exception as e:
        print(f"❌ Table check failed: {e}")
        return False

def main():
    """Run all database tests"""
    print("="*60)
    print("DATABASE CONNECTION TEST SUITE")
    print("="*60)
    
    all_passed = True
    
    # Test 1: Basic connection
    if not test_connection():
        all_passed = False
        print("\n⚠️  Cannot proceed without database connection")
        return
    
    # Test 2: Session management
    if not test_session_creation():
        all_passed = False
    
    # Test 3: get_db() generator
    if not test_get_db_generator():
        all_passed = False
    
    # Test 4: Table existence
    if not test_table_exists():
        all_passed = False
    
    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL DATABASE TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*60)

if __name__ == "__main__":
    main()