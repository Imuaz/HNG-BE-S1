import os
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
# Format: postgresql://user:password@host:port/database
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate DATABASE_URL and provide a safe fallback for local/dev
if not DATABASE_URL:
    # No DATABASE_URL provided — fallback to a local sqlite file for development.
    # This prevents import-time crashes when running in environments without a DB.
    print("Warning: DATABASE_URL not set; falling back to sqlite:///./dev.db (development only)")
    DATABASE_URL = "sqlite:///./dev.db"
else:
    # Quick sanity check — try parsing the URL so we can give a helpful error message
    try:
        make_url(DATABASE_URL)
    except Exception as e:
        print(f"Warning: DATABASE_URL appears invalid ({e}); falling back to sqlite:///./dev.db for development")
        DATABASE_URL = "sqlite:///./dev.db"

"""
What is create_engine?
-----------------------
Creates a connection "pool" to the database.
Think of it like a phone line to the database - you can make multiple calls (queries)
without reconnecting each time.

Parameters:
- DATABASE_URL: Where to find the database
- echo=True: Prints SQL queries to console (useful for learning/debugging)
"""
engine = create_engine(DATABASE_URL, echo=True)

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