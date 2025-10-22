import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file (if it exists)
# This is optional and mainly for local development
load_dotenv()

# Get database URL from environment variable
# Format: postgresql://user:password@host:port/database
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate that DATABASE_URL is set
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please set it to your PostgreSQL connection string. "
        "Example: postgresql://user:password@host:port/database"
    )

# Railway provides DATABASE_URL but we may need to handle different formats
if DATABASE_URL.startswith("postgres://"):
    # Railway sometimes uses 'postgres://' instead of 'postgresql://'
    # SQLAlchemy needs 'postgresql://'
    logger.info("Converting postgres:// to postgresql:// for SQLAlchemy compatibility")
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

logger.info(f"Database URL configured: {DATABASE_URL[:20]}...")  # Log first 20 chars for debugging

"""
What is create_engine?
-----------------------
Creates a connection "pool" to the database.
Think of it like a phone line to the database - you can make multiple calls (queries)
without reconnecting each time.

Parameters:
- DATABASE_URL: Where to find the database
- echo=False: Don't print SQL queries (set to True for debugging)
- pool_pre_ping=True: Test connections before using them (prevents stale connections)
"""
try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Changed to False for production
        pool_pre_ping=True  # Test connections before using
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    logger.error(f"Database URL format: {DATABASE_URL[:50]}...")
    raise

"""
What is SessionLocal?
---------------------
A "session" is like a conversation with the database:
1. You open a session (start conversation)
2. You perform operations (ask questions, make changes)
3. You close a session (end conversation)

sessionmaker creates a factory for making these sessions.

Parameters:
- autocommit=False: Changes aren't saved automatically (you control when)
- autoflush=False: Changes aren't sent to DB automatically (you control when)
- bind=engine: Which database to talk to
"""
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

"""
What is Base?
-------------
This is the parent class for all our database models.
Any class that inherits from Base becomes a database table.

Example:
class StringModel(Base):  # This becomes a table!
    __tablename__ = "strings"
    # ... columns here
"""
Base = declarative_base()


def get_db():
    """
    Dependency function that provides a database session.
    
    This is a generator function (notice the 'yield').
    It's used with FastAPI's dependency injection.
    
    How it works:
    1. Creates a new database session
    2. Yields it (gives it to the endpoint to use)
    3. After endpoint finishes, closes the session automatically
    
    Why this pattern?
    - Ensures database connections are always closed (no leaks!)
    - Each API request gets its own isolated session
    - Automatic cleanup even if errors occur
    
    Usage in FastAPI:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            # 'db' is automatically provided by FastAPI
            # You can use it to query the database
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()