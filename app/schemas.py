from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional
from datetime import datetime

"""
Pydantic Schemas
----------------
These classes define the structure of data for our API.

Think of them as "contracts":
- Request schemas: What data must clients send to us
- Response schemas: What data we'll send back to clients

Pydantic automatically:
1. Validates data types
2. Converts types when possible
3. Returns clear error messages
4. Generates API documentation
"""


# ============================================================================
# REQUEST SCHEMAS (Data coming INTO our API)
# ============================================================================

class StringCreate(BaseModel):
    """
    Schema for creating a new string.
    
    Used by: POST /strings
    
    Example request body:
    {
        "value": "hello world"
    }
    """
    value: str = Field(
        ...,  # ... means "required field"
        min_length=0,  # Allow empty strings
        description="The string to analyze",
        examples=["hello world", "racecar", "A man a plan a canal Panama"]
    )
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v):
        """
        Custom validation for the value field.
        
        This runs AFTER type checking but BEFORE the data is used.
        
        Args:
            v: The value to validate
        
        Returns:
            The validated value (can be modified)
        
        Raises:
            ValueError: If validation fails
        """
        # We could add custom rules here, for example:
        # - Reject strings with special characters
        # - Limit maximum length
        # - Check for profanity
        
        # For now, we accept any string
        return v
    
    class Config:
        """
        Pydantic configuration.
        
        json_schema_extra provides examples for API documentation.
        These appear in the auto-generated Swagger UI docs.
        """
        json_schema_extra = {
            "examples": [
                {
                    "value": "hello world"
                },
                {
                    "value": "racecar"
                },
                {
                    "value": "The quick brown fox jumps over the lazy dog"
                }
            ]
        }


class StringFilterParams(BaseModel):
    """
    Schema for filtering strings.
    
    Used by: GET /strings (query parameters)
    
    Example: GET /strings?is_palindrome=true&min_length=5&word_count=1
    
    All fields are optional - if not provided, that filter isn't applied.
    """
    is_palindrome: Optional[bool] = Field(
        None,
        description="Filter by palindrome status"
    )
    min_length: Optional[int] = Field(
        None,
        ge=0,  # ge = "greater than or equal to"
        description="Minimum string length (inclusive)"
    )
    max_length: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum string length (inclusive)"
    )
    word_count: Optional[int] = Field(
        None,
        ge=0,
        description="Exact word count"
    )
    contains_character: Optional[str] = Field(
        None,
        min_length=1,
        max_length=1,
        description="Single character that must be present in the string"
    )
    
    @field_validator('max_length')
    @classmethod
    def validate_max_length(cls, v, info):
        """
        Ensures max_length is greater than min_length if both are provided.
        
        Args:
            v: The max_length value
            info: ValidationInfo object containing other field values
        """
        if v is not None and info.data.get('min_length') is not None:
            if v < info.data['min_length']:
                raise ValueError('max_length must be greater than or equal to min_length')
        return v


class NaturalLanguageQuery(BaseModel):
    """
    Schema for natural language filtering.
    
    Used by: GET /strings/filter-by-natural-language
    
    Example: ?query=all%20single%20word%20palindromic%20strings
    (URL encoded: "all single word palindromic strings")
    """
    query: str = Field(
        ...,
        min_length=1,
        description="Natural language query describing the strings to find",
        examples=[
            "all single word palindromic strings",
            "strings longer than 10 characters",
            "strings containing the letter z"
        ]
    )


# ============================================================================
# RESPONSE SCHEMAS (Data going OUT from our API)
# ============================================================================

class StringProperties(BaseModel):
    """
    Schema for the 'properties' object in responses.
    
    Contains all computed properties of a string.
    """
    length: int = Field(
        ...,
        ge=0,
        description="Number of characters in the string"
    )
    is_palindrome: bool = Field(
        ...,
        description="Whether the string reads the same forwards and backwards"
    )
    unique_characters: int = Field(
        ...,
        ge=0,
        description="Count of distinct characters"
    )
    word_count: int = Field(
        ...,
        ge=0,
        description="Number of words separated by whitespace"
    )
    sha256_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="SHA-256 hash of the string"
    )
    character_frequency_map: Dict[str, int] = Field(
        ...,
        description="Mapping of each character to its occurrence count"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "length": 11,
                "is_palindrome": False,
                "unique_characters": 8,
                "word_count": 2,
                "sha256_hash": "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
                "character_frequency_map": {
                    "h": 1,
                    "e": 1,
                    "l": 3,
                    "o": 2,
                    " ": 1,
                    "w": 1,
                    "r": 1,
                    "d": 1
                }
            }
        }


class StringResponse(BaseModel):
    """
    Schema for a single string response.
    
    Used by:
    - POST /strings (201 Created)
    - GET /strings/{string_value} (200 OK)
    
    This is what clients receive when they create or retrieve a string.
    """
    id: str = Field(
        ...,
        description="SHA-256 hash used as unique identifier"
    )
    value: str = Field(
        ...,
        description="The original string"
    )
    properties: StringProperties = Field(
        ...,
        description="Computed properties of the string"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the string was first stored (ISO 8601 format)"
    )
    
    class Config:
        # Allow creation from ORM models (our database StringModel)
        from_attributes = True
        
        json_schema_extra = {
            "example": {
                "id": "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
                "value": "hello world",
                "properties": {
                    "length": 11,
                    "is_palindrome": False,
                    "unique_characters": 8,
                    "word_count": 2,
                    "sha256_hash": "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
                    "character_frequency_map": {"h": 1, "e": 1, "l": 3, "o": 2, " ": 1, "w": 1, "r": 1, "d": 1}
                },
                "created_at": "2025-08-27T10:00:00Z"
            }
        }


class StringListResponse(BaseModel):
    """
    Schema for listing multiple strings with filters.
    
    Used by:
    - GET /strings (200 OK)
    - GET /strings/filter-by-natural-language (200 OK)
    
    Returns array of strings plus metadata about the query.
    """
    data: List[StringResponse] = Field(
        ...,
        description="Array of matching strings"
    )
    count: int = Field(
        ...,
        ge=0,
        description="Total number of strings returned"
    )
    filters_applied: Optional[Dict] = Field(
        None,
        description="The filters that were applied to this query"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": "abc123...",
                        "value": "racecar",
                        "properties": {
                            "length": 7,
                            "is_palindrome": True,
                            "unique_characters": 4,
                            "word_count": 1,
                            "sha256_hash": "abc123...",
                            "character_frequency_map": {"r": 2, "a": 2, "c": 2, "e": 1}
                        },
                        "created_at": "2025-08-27T10:00:00Z"
                    }
                ],
                "count": 1,
                "filters_applied": {
                    "is_palindrome": True,
                    "word_count": 1
                }
            }
        }


class NaturalLanguageResponse(BaseModel):
    """
    Schema for natural language query responses.
    
    Used by: GET /strings/filter-by-natural-language (200 OK)
    
    Includes interpretation of the natural language query.
    """
    data: List[StringResponse] = Field(
        ...,
        description="Array of matching strings"
    )
    count: int = Field(
        ...,
        ge=0,
        description="Total number of strings returned"
    )
    interpreted_query: Dict = Field(
        ...,
        description="How the natural language query was parsed"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "count": 0,
                "interpreted_query": {
                    "original": "all single word palindromic strings",
                    "parsed_filters": {
                        "word_count": 1,
                        "is_palindrome": True
                    }
                }
            }
        }


# ============================================================================
# ERROR RESPONSE SCHEMAS
# ============================================================================

class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    
    Used for all error cases (400, 404, 409, 422)
    
    Provides consistent error format across all endpoints.
    """
    detail: str = Field(
        ...,
        description="Human-readable error message"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "String already exists in the system"
            }
        }


class ValidationErrorResponse(BaseModel):
    """
    Schema for validation errors (422 Unprocessable Entity).
    
    FastAPI automatically uses this format for Pydantic validation errors.
    """
    detail: List[Dict] = Field(
        ...,
        description="List of validation errors"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": [
                    {
                        "loc": ["body", "value"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            }
        }