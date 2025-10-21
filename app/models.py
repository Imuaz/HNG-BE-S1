from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

"""
What is a Model?
----------------
A model is a Python class that represents a database table.
Each attribute becomes a column in the table.

Example visualization:

Python Class (Model):              Database Table:
--------------------              ----------------
class StringModel:                strings
  id                         →    | id (TEXT, PRIMARY KEY)
  value                      →    | value (TEXT, UNIQUE)
  length                     →    | length (INTEGER)
  ...                        →    | ...
"""


class StringModel(Base):
    """
    Represents a stored string and its analyzed properties.
    
    This class maps to a database table called 'strings'.
    Each instance of this class = one row in the table.
    """
    
    # Table name in the database
    __tablename__ = "strings"
    
    # PRIMARY KEY: Unique identifier for each row
    # We use the SHA-256 hash as the ID (guaranteed unique per string)
    id = Column(
        String,           # Data type: text
        primary_key=True, # This is the unique identifier
        index=True        # Create an index for faster lookups
    )
    """
    Why SHA-256 as primary key?
    - Same string always has same hash → natural duplicate detection
    - No need for auto-incrementing IDs
    - Hash is unique (collision probability is astronomically low)
    """
    
    # The original string value
    value = Column(
        String,
        unique=True,  # No two rows can have the same value
        nullable=False, # This field is required (cannot be NULL/empty)
        index=True    # Index for faster searches
    )
    """
    unique=True means if we try to insert "hello" twice, database will reject it.
    This helps us return 409 Conflict error as required.
    """
    
    # Analyzed properties - stored as separate columns for easy filtering
    
    length = Column(Integer, nullable=False)
    """
    Integer type: whole numbers only
    We'll use this for filtering: "strings longer than 10 characters"
    """
    
    is_palindrome = Column(Boolean, nullable=False)
    """
    Boolean type: True or False only
    Used for filtering: "show me all palindromes"
    """
    
    unique_characters = Column(Integer, nullable=False)
    """
    Count of distinct characters
    Could filter by: "strings with more than 5 unique characters"
    """
    
    word_count = Column(Integer, nullable=False)
    """
    Number of words in the string
    Filter by: "single word strings" (word_count=1)
    """
    
    sha256_hash = Column(String, nullable=False)
    """
    We store this even though it's the same as 'id' for clarity.
    It appears in the response JSON, so users see it explicitly.
    """
    
    character_frequency_map = Column(JSON, nullable=False)
    """
    JSON type: Stores complex data structures (dictionaries/objects)
    
    Example value: {"h": 1, "e": 1, "l": 2, "o": 1}
    
    PostgreSQL has special JSON support - we can even query inside it!
    (Though we won't need that for this project)
    """
    
    # Timestamp: when this string was added
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    """
    DateTime: Stores date and time
    server_default=func.now(): Database automatically sets this to current time
    timezone=True: Stores timezone info (important for global apps!)
    
    Example value: 2025-08-27T10:00:00Z
    The 'Z' means UTC (Coordinated Universal Time)
    """
    
    def __repr__(self):
        """
        String representation for debugging.
        When you print(string_model), you'll see this.
        
        Example output:
        <StringModel(value='hello world', length=11, is_palindrome=False)>
        """
        return (f"<StringModel(value='{self.value}', "
                f"length={self.length}, "
                f"is_palindrome={self.is_palindrome})>")
    
    def to_dict(self):
        """
        Converts the model instance to a dictionary.
        Useful for creating API responses.
        
        Returns:
            Dictionary matching our API response format
        """
        return {
            "id": self.id,
            "value": self.value,
            "properties": {
                "length": self.length,
                "is_palindrome": self.is_palindrome,
                "unique_characters": self.unique_characters,
                "word_count": self.word_count,
                "sha256_hash": self.sha256_hash,
                "character_frequency_map": self.character_frequency_map
            },
            "created_at": self.created_at.isoformat()  # Convert datetime to string
        }


"""
SQLAlchemy Column Types Quick Reference:
----------------------------------------
String       → Text data (VARCHAR in SQL)
Integer      → Whole numbers (-∞ to +∞)
Boolean      → True/False
DateTime     → Date and time
JSON         → Complex data structures
Float        → Decimal numbers
Text         → Unlimited text (for very long strings)

Column Options:
---------------
primary_key=True  → Unique identifier, automatically indexed
unique=True       → No duplicates allowed
nullable=False    → Field is required (cannot be NULL)
index=True        → Create index for faster searches
default=value     → Default value if not provided
server_default    → Database sets default (not Python)
"""