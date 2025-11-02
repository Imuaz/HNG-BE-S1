from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
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
    
    # sha256_hash column removed: use `id` (SHA-256) as primary key instead
    
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
                "sha256_hash": self.id,
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


#============================================================================
# TRANSLATION MODELS (New for MultiLingo Agent)
# ============================================================================

class TranslationModel(Base):
    """
    Represents a translation record.
    
    Stores translation requests and their results for history and analytics.
    """
    
    __tablename__ = "translations"
    
    id = Column(
        String,
        primary_key=True,
        index=True
    )
    """
    Primary key: combination of original_text_hash + target_language
    Example: "abc123_es" (SHA-256 hash of original + language code)
    """
    
    # Original text information
    original_text = Column(Text, nullable=False, index=True)
    """Full original text to be translated"""
    
    original_hash = Column(String, nullable=False, index=True)
    """SHA-256 hash of original text for quick lookups"""
    
    detected_language = Column(String, nullable=False)
    """Auto-detected source language code (e.g., 'en', 'es')"""
    
    detected_language_name = Column(String, nullable=False)
    """Human-readable detected language name (e.g., 'english', 'spanish')"""
    
    # Translation information
    target_language = Column(String, nullable=False, index=True)
    """Target language code for translation (e.g., 'es', 'fr')"""
    
    translated_text = Column(Text, nullable=False)
    """The translated result"""
    
    # Metadata
    translation_service = Column(String, default="googletrans")
    """Which service was used (googletrans, deepl, openai, etc.)"""
    
    request_source = Column(String, default="api")
    """Source of request: 'api', 'telex', 'webhook'"""
    
    user_id = Column(String, nullable=True, index=True)
    """User identifier from Telex or other sources (optional)"""
    
    # String analysis (from original String Analyzer)
    original_properties = Column(JSON, nullable=True)
    """
    Stores analysis of original text:
    {
        "length": 11,
        "word_count": 2,
        "is_palindrome": false,
        "unique_characters": 8
    }
    """
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    """When the translation was performed"""
    
    def __repr__(self):
        return (f"<TranslationModel(original='{self.original_text[:30]}...', "
                f"target={self.target_language}, "
                f"translated='{self.translated_text[:30]}...')>")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "original": {
                "text": self.original_text,
                "language": self.detected_language,
                "language_name": self.detected_language_name,
                "properties": self.original_properties
            },
            "translation": {
                "text": self.translated_text,
                "target_language": self.target_language
            },
            "metadata": {
                "service": self.translation_service,
                "source": self.request_source,
                "user_id": self.user_id
            },
            "created_at": self.created_at.isoformat()
        }


class TelexConversationModel(Base):
    """
    Stores Telex conversation history and context.
    
    Tracks user interactions for context-aware responses.
    """
    
    __tablename__ = "telex_conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    """Auto-incrementing ID"""
    
    # Telex identifiers
    telex_user_id = Column(String, nullable=False, index=True)
    """User ID from Telex platform"""
    
    telex_conversation_id = Column(String, nullable=True, index=True)
    """Conversation/thread ID from Telex"""
    
    telex_message_id = Column(String, nullable=True)
    """Specific message ID from Telex"""
    
    # Message content
    user_message = Column(Text, nullable=False)
    """What the user sent"""
    
    agent_response = Column(Text, nullable=False)
    """What our agent responded"""
    
    # Intent and action
    detected_intent = Column(String, nullable=True)
    """
    Detected user intent:
    - 'translate'
    - 'detect_language'
    - 'analyze_string'
    - 'help'
    - 'unknown'
    """
    
    action_taken = Column(String, nullable=True)
    """Action performed by agent (e.g., 'translated_to_spanish')"""
    
    # Context
    context_data = Column(JSON, nullable=True)
    """
    Stores conversation context:
    {
        "previous_language": "es",
        "translation_history": [...],
        "user_preferences": {...}
    }
    """
    
    # Status
    success = Column(Boolean, default=True)
    """Whether the interaction was successful"""
    
    error_message = Column(Text, nullable=True)
    """Error details if success=False"""
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    def __repr__(self):
        return (f"<TelexConversation(user_id={self.telex_user_id}, "
                f"intent={self.detected_intent}, "
                f"success={self.success})>")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "telex_user_id": self.telex_user_id,
            "conversation_id": self.telex_conversation_id,
            "user_message": self.user_message,
            "agent_response": self.agent_response,
            "intent": self.detected_intent,
            "action": self.action_taken,
            "success": self.success,
            "created_at": self.created_at.isoformat()
        }


class AgentAnalyticsModel(Base):
    """
    Tracks agent usage analytics and metrics.
    
    Useful for monitoring performance and usage patterns.
    """
    
    __tablename__ = "agent_analytics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Metrics
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    """Date of the metric"""
    
    total_requests = Column(Integer, default=0)
    """Total API requests received"""
    
    successful_translations = Column(Integer, default=0)
    """Number of successful translations"""
    
    failed_translations = Column(Integer, default=0)
    """Number of failed translations"""
    
    telex_interactions = Column(Integer, default=0)
    """Number of Telex chat interactions"""
    
    unique_users = Column(Integer, default=0)
    """Number of unique users (based on user_id)"""
    
    # Language statistics
    most_requested_languages = Column(JSON, nullable=True)
    """
    Top requested target languages:
    {"es": 150, "fr": 120, "de": 80}
    """
    
    most_detected_languages = Column(JSON, nullable=True)
    """
    Most common source languages detected:
    {"en": 200, "es": 100, "fr": 50}
    """
    
    # Performance
    average_response_time_ms = Column(Integer, default=0)
    """Average response time in milliseconds"""
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    def __repr__(self):
        return (f"<AgentAnalytics(date={self.date}, "
                f"requests={self.total_requests}, "
                f"success={self.successful_translations})>")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "total_requests": self.total_requests,
            "successful_translations": self.successful_translations,
            "failed_translations": self.failed_translations,
            "telex_interactions": self.telex_interactions,
            "unique_users": self.unique_users,
            "most_requested_languages": self.most_requested_languages,
            "most_detected_languages": self.most_detected_languages,
            "average_response_time_ms": self.average_response_time_ms
        }
