"""
String Analyzer API - Main Application
---------------------------------------
RESTful API for analyzing and storing strings with their computed properties.

Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.database import get_db
from app.schemas import (
    StringCreate,
    StringResponse,
    StringListResponse,
    NaturalLanguageResponse,
    ErrorResponse
)
from app.crud import (
    create_string,
    get_string_by_value,
    get_all_strings,
    delete_string,
    string_exists
)

# ============================================================================
# CREATE FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="String Analyzer API",
    description="Analyze strings and store their computed properties",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

"""
What is FastAPI instance?
- 'app' is the main application object
- All routes are attached to it with decorators (@app.get, @app.post, etc.)
- Handles HTTP requests and routes them to correct functions
"""


# ============================================================================
# ENDPOINT 1: CREATE/ANALYZE STRING
# ============================================================================

@app.post(
    "/strings",
    response_model=StringResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "String created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request body"},
        409: {"model": ErrorResponse, "description": "String already exists"},
        422: {"description": "Validation error"}
    }
)
def create_and_analyze_string(
    string_data: StringCreate,
    db: Session = Depends(get_db)
):
    """
    Create and analyze a new string.
    
    Process:
    1. Validate request body (FastAPI does this automatically)
    2. Check if string already exists
    3. Analyze string properties
    4. Store in database
    5. Return complete analysis
    
    Args:
        string_data: Request body containing the string value
        db: Database session (injected by FastAPI)
    
    Returns:
        StringResponse with all computed properties
    
    Raises:
        409 Conflict: If string already exists
    """
    # Check if string already exists
    if string_exists(db, string_data.value):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="String already exists in the system"
        )
    
    try:
        # Create and analyze string
        db_string = create_string(db, string_data.value)
        
        # Convert database model to response schema
        return StringResponse(
            id=db_string.id,
            value=db_string.value,
            properties={
                "length": db_string.length,
                "is_palindrome": db_string.is_palindrome,
                "unique_characters": db_string.unique_characters,
                "word_count": db_string.word_count,
                "sha256_hash": db_string.sha256_hash,
                "character_frequency_map": db_string.character_frequency_map
            },
            created_at=db_string.created_at
        )
        
    except IntegrityError:
        # This handles race conditions (two requests at exact same time)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="String already exists in the system"
        )


# ============================================================================
# ENDPOINT 2: GET SPECIFIC STRING
# ============================================================================

@app.get(
    "/strings/{string_value}",
    response_model=StringResponse,
    responses={
        200: {"description": "String found"},
        404: {"model": ErrorResponse, "description": "String not found"}
    }
)
def get_specific_string(
    string_value: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific string by its exact value.
    
    The string_value in the URL is matched exactly (case-sensitive).
    
    Args:
        string_value: The exact string to retrieve (from URL path)
        db: Database session (injected by FastAPI)
    
    Returns:
        StringResponse with all properties
    
    Raises:
        404 Not Found: If string doesn't exist
    
    Example:
        GET /strings/hello%20world
        (URL encoding: space becomes %20)
    """
    # Query database
    db_string = get_string_by_value(db, string_value)
    
    # If not found, return 404
    if db_string is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="String does not exist in the system"
        )
    
    # Convert to response schema
    return StringResponse(
        id=db_string.id,
        value=db_string.value,
        properties={
            "length": db_string.length,
            "is_palindrome": db_string.is_palindrome,
            "unique_characters": db_string.unique_characters,
            "word_count": db_string.word_count,
            "sha256_hash": db_string.sha256_hash,
            "character_frequency_map": db_string.character_frequency_map
        },
        created_at=db_string.created_at
    )


# ============================================================================
# ENDPOINT 3: GET ALL STRINGS WITH FILTERING
# ============================================================================

@app.get(
    "/strings",
    response_model=StringListResponse,
    responses={
        200: {"description": "List of strings"},
        400: {"model": ErrorResponse, "description": "Invalid query parameters"}
    }
)
def list_strings(
    is_palindrome: Optional[bool] = Query(None, description="Filter by palindrome status"),
    min_length: Optional[int] = Query(None, ge=0, description="Minimum string length (inclusive)"),
    max_length: Optional[int] = Query(None, ge=0, description="Maximum string length (inclusive)"),
    word_count: Optional[int] = Query(None, ge=0, description="Exact word count"),
    contains_character: Optional[str] = Query(None, min_length=1, max_length=1, description="Single character to search for"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all strings with optional filtering.
    
    All query parameters are optional. If not provided, no filter is applied.
    Multiple filters are combined with AND logic.
    
    Args:
        is_palindrome: Filter by palindrome status (optional)
        min_length: Minimum string length (optional)
        max_length: Maximum string length (optional)
        word_count: Exact word count (optional)
        contains_character: Single character that must be present (optional)
        db: Database session (injected by FastAPI)
    
    Returns:
        StringListResponse with array of matching strings and metadata
    
    Examples:
        GET /strings
        GET /strings?is_palindrome=true
        GET /strings?min_length=5&max_length=20
        GET /strings?is_palindrome=true&word_count=1
    """
    # Validate max_length >= min_length
    if min_length is not None and max_length is not None:
        if max_length < min_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_length must be greater than or equal to min_length"
            )
    
    # Query database with filters
    db_strings = get_all_strings(
        db,
        is_palindrome=is_palindrome,
        min_length=min_length,
        max_length=max_length,
        word_count=word_count,
        contains_character=contains_character
    )
    
    # Convert database models to response schemas
    string_responses = []
    for db_string in db_strings:
        string_responses.append(
            StringResponse(
                id=db_string.id,
                value=db_string.value,
                properties={
                    "length": db_string.length,
                    "is_palindrome": db_string.is_palindrome,
                    "unique_characters": db_string.unique_characters,
                    "word_count": db_string.word_count,
                    "sha256_hash": db_string.sha256_hash,
                    "character_frequency_map": db_string.character_frequency_map
                },
                created_at=db_string.created_at
            )
        )
    
    # Build filters_applied dict (only include non-None values)
    filters_applied = {}
    if is_palindrome is not None:
        filters_applied["is_palindrome"] = is_palindrome
    if min_length is not None:
        filters_applied["min_length"] = min_length
    if max_length is not None:
        filters_applied["max_length"] = max_length
    if word_count is not None:
        filters_applied["word_count"] = word_count
    if contains_character is not None:
        filters_applied["contains_character"] = contains_character
    
    # Return list response
    return StringListResponse(
        data=string_responses,
        count=len(string_responses),
        filters_applied=filters_applied if filters_applied else None
    )


# ============================================================================
# ENDPOINT 4: NATURAL LANGUAGE FILTERING
# ============================================================================

@app.get(
    "/strings/filter-by-natural-language",
    response_model=NaturalLanguageResponse,
    responses={
        200: {"description": "Filtered results"},
        400: {"model": ErrorResponse, "description": "Unable to parse query"},
        422: {"model": ErrorResponse, "description": "Query parsed but resulted in conflicting filters"}
    }
)
def filter_by_natural_language(
    query: str = Query(..., description="Natural language query describing the strings to find"),
    db: Session = Depends(get_db)
):
    """
    Filter strings using natural language queries.
    
    Parses natural language and converts it to filters.
    
    Supported patterns:
    - "all single word palindromic strings" → word_count=1, is_palindrome=true
    - "strings longer than 10 characters" → min_length=11
    - "strings containing the letter z" → contains_character=z
    - "palindromic strings" → is_palindrome=true
    
    Args:
        query: Natural language query string
        db: Database session (injected by FastAPI)
    
    Returns:
        NaturalLanguageResponse with matching strings and interpretation
    
    Raises:
        400 Bad Request: If query cannot be parsed
        422 Unprocessable Entity: If query results in conflicting filters
    """
    # Import the parser (we'll create this next)
    from app.nlp_parser import parse_natural_language_query
    
    try:
        # Parse the natural language query into filters
        parsed_filters = parse_natural_language_query(query)
        
        # Check for conflicting filters
        if parsed_filters.get("min_length") and parsed_filters.get("max_length"):
            if parsed_filters["max_length"] < parsed_filters["min_length"]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Query parsed but resulted in conflicting filters (max_length < min_length)"
                )
        
        # Query database with parsed filters
        db_strings = get_all_strings(
            db,
            is_palindrome=parsed_filters.get("is_palindrome"),
            min_length=parsed_filters.get("min_length"),
            max_length=parsed_filters.get("max_length"),
            word_count=parsed_filters.get("word_count"),
            contains_character=parsed_filters.get("contains_character")
        )
        
        # Convert to response schemas
        string_responses = []
        for db_string in db_strings:
            string_responses.append(
                StringResponse(
                    id=db_string.id,
                    value=db_string.value,
                    properties={
                        "length": db_string.length,
                        "is_palindrome": db_string.is_palindrome,
                        "unique_characters": db_string.unique_characters,
                        "word_count": db_string.word_count,
                        "sha256_hash": db_string.sha256_hash,
                        "character_frequency_map": db_string.character_frequency_map
                    },
                    created_at=db_string.created_at
                )
            )
        
        # Return response with interpretation
        return NaturalLanguageResponse(
            data=string_responses,
            count=len(string_responses),
            interpreted_query={
                "original": query,
                "parsed_filters": parsed_filters
            }
        )
        
    except ValueError as e:
        # Parser couldn't understand the query
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to parse natural language query: {str(e)}"
        )


# ============================================================================
# ENDPOINT 5: DELETE STRING
# ============================================================================

@app.delete(
    "/strings/{string_value}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "String deleted successfully"},
        404: {"model": ErrorResponse, "description": "String not found"}
    }
)
def delete_specific_string(
    string_value: str,
    db: Session = Depends(get_db)
):
    """
    Delete a specific string by its exact value.
    
    Args:
        string_value: The exact string to delete (from URL path)
        db: Database session (injected by FastAPI)
    
    Returns:
        204 No Content (empty response body)
    
    Raises:
        404 Not Found: If string doesn't exist
    
    Example:
        DELETE /strings/hello%20world
    """
    # Attempt to delete
    success = delete_string(db, string_value)
    
    # If not found, return 404
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="String does not exist in the system"
        )
    
    # Return 204 No Content (no response body)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============================================================================
# ROOT ENDPOINT (Welcome Message)
# ============================================================================

@app.get("/", include_in_schema=False)
def root():
    """
    Welcome endpoint.
    
    Returns basic API information and links to documentation.
    """
    return {
        "message": "Welcome to String Analyzer API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "create_string": "POST /strings",
            "get_string": "GET /strings/{string_value}",
            "list_strings": "GET /strings",
            "natural_language_filter": "GET /strings/filter-by-natural-language",
            "delete_string": "DELETE /strings/{string_value}"
        }
    }


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health", include_in_schema=False)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Verifies API and database are operational.
    """
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }