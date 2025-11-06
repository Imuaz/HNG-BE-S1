"""
String Analyzer API - Main Application
---------------------------------------
RESTful API for analyzing and storing strings with their computed properties.

Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query, Request, BackgroundTasks
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Dict
from datetime import datetime
import asyncio

from app.database import get_db
from app.schemas import (
    StringCreate,
    StringResponse,
    StringListResponse,
    NaturalLanguageResponse,
    ErrorResponse,
    TranslationRequest,
    MultiTranslationRequest,
    TranslationResponse,
    MultiTranslationResponse,
    TelexWebhookPayload,
    TelexResponse,
    ChatRequest,
    ChatResponse
)
from app.crud import (
    create_string,
    get_string_by_value,
    get_all_strings,
    delete_string,
    string_exists,
    create_translation,
    get_translation,
    get_translation_by_id,
    get_all_translations,
    create_telex_conversation,
    get_telex_conversation_history
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

# ============================================================================
# CORS MIDDLEWARE (Allow cross-origin requests)
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
CORS (Cross-Origin Resource Sharing):
- Allows frontend apps from different domains to access your API
- In production, replace ["*"] with specific frontend URLs
- Example: allow_origins=["https://myapp.com", "https://www.myapp.com"]
"""

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
        "message": "Welcome to String Analyzer API with MultiLingo Agent",
        "version": "2.0.0",
        "documentation": "/docs",
        "features": {
            "string_analysis": "Analyze string properties (length, palindrome, etc.)",
            "translation": "AI-powered translation to 25+ languages",
            "telex_integration": "Chat with MultiLingo Agent on Telex.im"
        },
        "endpoints": {
            "string_analysis": {
                "create_string": "POST /strings",
                "get_string": "GET /strings/{string_value}",
                "list_strings": "GET /strings",
                "natural_language_filter": "GET /strings/filter-by-natural-language",
                "delete_string": "DELETE /strings/{string_value}"
            },
            "translation": {
                "translate": "POST /translate",
                "translate_multiple": "POST /translate/multiple",
                "get_translations": "GET /translations",
                "get_translation": "GET /translations/{translation_id}"
            },
            "agent": {
                "telex_webhook": "POST /webhook/telex",
                "chat": "POST /agents/multilingo/chat"
            }
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


# ============================================================================
# TRANSLATION ENDPOINTS (MultiLingo Agent)
# ============================================================================

@app.post(
    "/translate",
    response_model=TranslationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Translation"],
    responses={
        201: {"description": "Translation completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"description": "Validation error"}
    }
)
def translate_text_endpoint(
    request: TranslationRequest,
    db: Session = Depends(get_db)
):
    """
    Translate text to a target language.
    
    This endpoint:
    1. Detects source language (if not provided)
    2. Translates to target language
    3. Optionally analyzes string properties
    4. Stores translation in database
    5. Returns comprehensive response
    
    Example request:
        POST /translate
        {
            "text": "hello world",
            "target_language": "es",
            "analyze": true
        }
    """
    try:
        from app.translator import translate_text
        from app.analyzer import analyze_string
        
        # Check if we already have this translation cached
        existing = get_translation(db, request.text, request.target_language)
        if existing:
            return TranslationResponse(
                id=existing.id,
                original=existing.to_dict()["original"],
                translation=existing.to_dict()["translation"],
                metadata=existing.to_dict()["metadata"],
                created_at=existing.created_at
            )
        
        # Perform translation
        translation_result = translate_text(
            request.text,
            request.target_language,
            request.source_language
        )
        
        # Analyze original text if requested
        original_properties = None
        if request.analyze:
            original_properties = analyze_string(request.text)
        
        # Store in database
        db_translation = create_translation(
            db=db,
            original_text=request.text,
            translated_text=translation_result["translated_text"],
            source_language=translation_result["source_language"],
            target_language=translation_result["target_language"],
            detected_language_name=translation_result["detected_language"],
            original_properties=original_properties,
            request_source="api"
        )
        
        # Build response
        return TranslationResponse(
            id=db_translation.id,
            original={
                "text": db_translation.original_text,
                "language": db_translation.detected_language,
                "language_name": db_translation.detected_language_name,
                "properties": db_translation.original_properties
            },
            translation={
                "text": db_translation.translated_text,
                "target_language": db_translation.target_language
            },
            metadata={
                "service": db_translation.translation_service,
                "source": db_translation.request_source
            },
            created_at=db_translation.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


@app.post(
    "/translate/multiple",
    response_model=MultiTranslationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Translation"],
    responses={
        201: {"description": "Translations completed"},
        400: {"model": ErrorResponse, "description": "Invalid request"}
    }
)
def translate_multiple_languages(
    request: MultiTranslationRequest,
    db: Session = Depends(get_db)
):
    """
    Translate text to multiple target languages at once.
    
    Example request:
        POST /translate/multiple
        {
            "text": "hello",
            "target_languages": ["es", "fr", "de"],
            "analyze": true
        }
    """
    try:
        from app.translator import translate_to_multiple
        from app.analyzer import analyze_string
        
        # Perform translations
        translation_results = translate_to_multiple(
            request.text,
            request.target_languages,
            request.source_language
        )
        
        # Analyze original text if requested
        original_properties = None
        if request.analyze:
            original_properties = analyze_string(request.text)
        
        # Store each translation in database
        for lang, translated_text in translation_results["translations"].items():
            if not translated_text.startswith("[Translation failed"):
                try:
                    create_translation(
                        db=db,
                        original_text=request.text,
                        translated_text=translated_text,
                        source_language=translation_results["source_language"],
                        target_language=lang,
                        detected_language_name=translation_results.get("source_language", "unknown"),
                        original_properties=original_properties,
                        request_source="api"
                    )
                except:
                    pass  # Skip if already exists
        
        # Build response
        return MultiTranslationResponse(
            original={
                "text": request.text,
                "language": translation_results["source_language"],
                "properties": original_properties
            },
            translations=translation_results["translations"],
            metadata={
                "service": "deep-translator",
                "source": "api"
            },
            created_at=datetime.now()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get(
    "/translations",
    response_model=List[TranslationResponse],
    tags=["Translation"],
    responses={
        200: {"description": "Translation history retrieved"}
    }
)
def get_translations_history(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    source_language: Optional[str] = Query(None, description="Filter by source language"),
    target_language: Optional[str] = Query(None, description="Filter by target language"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Retrieve translation history with optional filtering.
    
    Example:
        GET /translations?target_language=es&limit=50
    """
    translations = get_all_translations(
        db=db,
        user_id=user_id,
        source_language=source_language,
        target_language=target_language,
        limit=limit
    )
    
    return [
        TranslationResponse(
            id=t.id,
            original=t.to_dict()["original"],
            translation=t.to_dict()["translation"],
            metadata=t.to_dict()["metadata"],
            created_at=t.created_at
        )
        for t in translations
    ]


@app.get(
    "/translations/{translation_id}",
    response_model=TranslationResponse,
    tags=["Translation"],
    responses={
        200: {"description": "Translation found"},
        404: {"model": ErrorResponse, "description": "Translation not found"}
    }
)
def get_translation_endpoint(
    translation_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific translation by ID.
    
    Example:
        GET /translations/abc123def456_es
    """
    translation = get_translation_by_id(db, translation_id)
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    return TranslationResponse(
        id=translation.id,
        original=translation.to_dict()["original"],
        translation=translation.to_dict()["translation"],
        metadata=translation.to_dict()["metadata"],
        created_at=translation.created_at
    )


# ============================================================================
# TELEX INTEGRATION & CHAT ENDPOINTS
# ============================================================================

@app.post(
    "/webhook/telex",
    response_model=TelexResponse,
    tags=["Telex Integration"],
    responses={
        200: {"description": "Message processed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid payload"}
    }
)
def telex_webhook(
    payload: TelexWebhookPayload,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for Telex.im integration.
    
    Telex sends user messages here, and we respond with agent's reply.
    
    This endpoint:
    1. Receives message from Telex user
    2. Detects intent and processes request
    3. Performs translation/analysis as needed
    4. Stores conversation in database
    5. Returns formatted response to Telex
    
    Example payload from Telex:
    {
        "user_id": "user_12345",
        "message": "Translate 'hello' to Spanish",
        "conversation_id": "conv_67890"
    }
    """
    try:
        from app.chat_handler import process_chat_message
        
        # Get conversation history for context
        history = get_telex_conversation_history(db, payload.user_id, limit=5)
        context = {
            "last_text": history[0].user_message if history else None
        }
        
        # Process the message
        chat_response = process_chat_message(payload.message, context)
        
        # Store conversation in database
        create_telex_conversation(
            db=db,
            telex_user_id=payload.user_id,
            telex_conversation_id=payload.conversation_id,
            telex_message_id=payload.message_id,
            user_message=payload.message,
            agent_response=chat_response["message"],
            detected_intent=chat_response["intent"],
            action_taken=chat_response["action_taken"],
            context_data=context,
            success=chat_response["success"]
        )
        
        # Return response to Telex
        return TelexResponse(
            message=chat_response["message"],
            success=chat_response["success"],
            data=chat_response.get("data"),
            error=None if chat_response["success"] else "Processing failed"
        )
        
    except Exception as e:
        # Log error and return friendly message
        error_message = "Sorry, I encountered an error processing your request. Please try again!"
        
        # Still store failed conversation
        try:
            create_telex_conversation(
                db=db,
                telex_user_id=payload.user_id,
                telex_conversation_id=payload.conversation_id,
                telex_message_id=payload.message_id,
                user_message=payload.message,
                agent_response=error_message,
                detected_intent="error",
                action_taken="error",
                success=False,
                error_message=str(e)
            )
        except:
            pass
        
        return TelexResponse(
            message=error_message,
            success=False,
            data=None,
            error=str(e)
        )


@app.post(
    "/agents/multilingo/chat",
    response_model=ChatResponse,
    tags=["MultiLingo Agent"],
    responses={
        200: {"description": "Chat processed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid message"}
    }
)
def multilingo_chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Direct chat interface with MultiLingo Agent.
    
    This endpoint allows you to chat with the agent directly via API
    (not through Telex). Useful for testing and custom integrations.
    
    Example request:
    {
        "message": "Translate 'hello world' to Spanish",
        "user_id": "user_123"
    }
    
    Example response:
    {
        "message": "Translation complete! ...",
        "intent": "translate",
        "action_taken": "translated_to_spanish",
        "data": {...},
        "success": true
    }
    """
    try:
        from app.chat_handler import process_chat_message
        
        # Get context if user_id provided
        context = request.context or {}
        if request.user_id:
            history = get_telex_conversation_history(db, request.user_id, limit=5)
            if history:
                context["last_text"] = history[0].user_message
        
        # Process message
        chat_response = process_chat_message(request.message, context)
        
        # Store if user_id provided
        if request.user_id:
            create_telex_conversation(
                db=db,
                telex_user_id=request.user_id,
                user_message=request.message,
                agent_response=chat_response["message"],
                detected_intent=chat_response["intent"],
                action_taken=chat_response["action_taken"],
                context_data=context,
                success=chat_response["success"]
            )
        
        return ChatResponse(
            message=chat_response["message"],
            intent=chat_response["intent"],
            action_taken=chat_response["action_taken"],
            data=chat_response.get("data"),
            success=chat_response["success"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )


# ============================================================================
# A2A PROTOCOL ENDPOINTS (Mastra Format for Telex)
# ============================================================================

@app.get(
    "/a2a/agent/multilingoAgent",
    tags=["A2A Protocol"],
    responses={
        200: {"description": "Agent information"}
    }
)
async def a2a_multilingo_agent_info():
    """
    A2A Protocol GET endpoint - Returns agent information.
    
    This is called by Telex/Mastra to get agent capabilities.
    """
    return {
        "name": "MultiLingo Translation Agent",
        "description": "AI-powered translation agent supporting 25+ languages with natural language understanding",
        "version": "1.0.0",
        "capabilities": [
            "translation",
            "language_detection",
            "text_analysis",
            "natural_language_understanding"
        ],
        "supported_languages": [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh-cn", "ko",
            "ar", "hi", "nl", "tr", "sv", "pl", "vi", "th", "el", "cs",
            "da", "fi", "no", "ro", "uk"
        ],
        "endpoints": {
            "chat": "/a2a/agent/multilingoAgent",
            "health": "/health",
            "docs": "/docs"
        },
        "status": "active",
        "response_format": "mastra-a2a",
        "system_prompt": "You are MultiLingo, an intelligent translation assistant that provides accurate translations in 25+ languages, detects languages automatically, and analyzes text properties. You understand natural language queries and respond in a friendly, helpful manner with formatted results."
    }


@app.post(
    "/a2a/agent/multilingoAgent",
    tags=["A2A Protocol"],
    responses={
        200: {"description": "A2A request processed successfully"}
    }
)
async def a2a_multilingo_agent_post(request: Request, background_tasks: BackgroundTasks):
    """
    A2A Protocol POST endpoint for Mastra integration with Telex.
    
    This endpoint follows the Mastra A2A protocol format.
    Telex will send requests here when users interact with the agent.
    
    Expected request format:
    {
        "messages": [
            {
                "role": "user",
                "content": "Translate 'hello' to Spanish"
            }
        ],
        "context": {...}
    }
    """
    try:
        from app.chat_handler import process_chat_message_fast
        from app.database import SessionLocal
        
        # Get request body
        try:
            body = await request.json()
        except:
            body = {}
        
        # Handle empty request
        if not body or not body.get("messages"):
            return {
                "role": "assistant",
                "content": "👋 Hello! I'm MultiLingo Agent!\n\nI can help you with:\n• Translations (25+ languages)\n• Language detection\n• String analysis\n\nTry: 'Translate hello to Spanish'",
                "metadata": {
                    "intent": "greeting",
                    "success": True
                }
            }
        
        # Extract message from A2A format
        messages = body.get("messages", [])
        user_message = ""
        user_id = body.get("userId") or body.get("user_id") or "telex_user"
        
        # Get the last user message
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        if not user_message:
            return {
                "role": "assistant",
                "content": "I didn't receive a message. Please try again!",
                "metadata": {
                    "success": False
                }
            }
        
        # Minimal context (no DB query for speed)
        context = {}
        
        # Process the message using optimized fast handler (with cache, no analysis)
        try:
            chat_response = await asyncio.wait_for(
                asyncio.to_thread(process_chat_message_fast, user_message, context),
                timeout=8  # Reduced timeout for faster failure
            )
        except asyncio.TimeoutError:
            return {
                "role": "assistant",
                "content": "Sorry, that took too long. Please try again! ⏳",
                "metadata": {
                    "intent": "timeout",
                    "success": False
                }
            }
        
        # Store conversation in background (don't wait for DB write)
        # This improves response time significantly - DB writes are slow
        def store_conversation_bg():
            try:
                db = SessionLocal()
                try:
                    create_telex_conversation(
                        db=db,
                        telex_user_id=user_id,
                        user_message=user_message,
                        agent_response=chat_response["message"],
                        detected_intent=chat_response["intent"],
                        action_taken=chat_response["action_taken"],
                        context_data=context,
                        success=chat_response["success"]
                    )
                    db.commit()
                except:
                    db.rollback()
                finally:
                    db.close()
            except:
                pass  # Fail silently - don't block response
        
        # Add background task (runs after response is sent)
        background_tasks.add_task(store_conversation_bg)
        
        # Return immediately (don't wait for DB)
        return {
            "role": "assistant",
            "content": chat_response["message"],
            "metadata": {
                "intent": chat_response["intent"],
                "action": chat_response["action_taken"],
                "success": chat_response["success"],
                "data": chat_response.get("data")
            }
        }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "role": "assistant",
            "content": "Sorry, I encountered an error processing your request. Please try again! 🔄",
            "metadata": {
                "error": str(e),
                "success": False
            }
        }