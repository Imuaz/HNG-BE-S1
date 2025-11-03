"""
String Analyzer API - Main Application
---------------------------------------
RESTful API for analyzing and storing strings with their computed properties.

Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import datetime
from typing import Any, Dict

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
    ChatResponse,
    AgentCard,
    AgentSkill
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
# AUTH HELPERS (Telex API Key)
# ============================================================================

def verify_telex_api_key(request: Request) -> None:
    """
    If TELEX_API_KEY is set in the environment, require matching X-API-Key header.
    """
    import os
    expected_key = os.getenv("TELEX_API_KEY")
    if not expected_key:
        return None
    provided_key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
    if provided_key != expected_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


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
# AGENT CARD ENDPOINT (Telex Agent Discovery)
# ============================================================================

@app.get(
    "/.well-known/agent-card",
    response_model=AgentCard,
    tags=["Agent Discovery"],
    responses={
        200: {"description": "Agent card retrieved successfully"}
    }
)
def get_agent_card():
    """
    Agent Card endpoint for Telex.im discovery.
    
    This endpoint provides metadata about the MultiLingo Agent,
    including its capabilities, supported languages, and webhook URL.
    
    Telex.im uses this to discover and register agents.
    
    Standard location: /.well-known/agent-card
    """
    import os
    from app.translator import get_supported_languages
    
    # Get base URL from environment or use default
    base_url = os.getenv("BASE_URL", "https://your-app-domain.com")
    webhook_url = f"{base_url}/webhook/telex"
    
    # Get supported languages
    supported_langs = get_supported_languages()
    lang_codes = list(supported_langs.values())[:10]  # Top 10 for brevity
    
    return AgentCard(
        name="MultiLingo Agent",
        description="AI-powered translation and string analysis agent supporting 25+ languages with natural language understanding",
        version="2.0.0",
        author="HNG Backend Team",
        homepage="https://github.com/yourusername/multilingo-agent",
        webhook_url=webhook_url,
        skills=[
            AgentSkill(
                name="Translation",
                description="Translate text between 25+ languages including Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Arabic, and more",
                examples=[
                    "Translate 'hello world' to Spanish",
                    "How do you say 'thank you' in French?",
                    "What is 'bonjour' in English?",
                    "Translate 'good morning' to German and Italian"
                ]
            ),
            AgentSkill(
                name="Language Detection",
                description="Automatically detect the language of any text with high accuracy",
                examples=[
                    "What language is 'hola mundo'?",
                    "Detect language of 'bonjour'",
                    "Identify this: 'ciao bella'"
                ]
            ),
            AgentSkill(
                name="String Analysis",
                description="Analyze text properties including length, word count, palindrome detection, character frequency, and more",
                examples=[
                    "Analyze 'hello world'",
                    "Is 'racecar' a palindrome?",
                    "Check the properties of 'level'"
                ]
            ),
            AgentSkill(
                name="Multi-Language Translation",
                description="Translate text to multiple languages simultaneously",
                examples=[
                    "Translate 'hello' to Spanish, French, and German",
                    "Say 'goodbye' in 5 different languages"
                ]
            )
        ],
        supported_languages=lang_codes,
        tags=[
            "translation",
            "language",
            "multilingual",
            "nlp",
            "analysis",
            "string-processing",
            "ai-agent",
            "language-detection"
        ],
        icon_url="https://api.dicebear.com/7.x/bottts/svg?seed=multilingo",
        metadata={
            "max_text_length": 5000,
            "response_time": "fast",
            "total_languages": len(supported_langs),
            "features": [
                "Natural language understanding",
                "Context-aware responses",
                "Multi-turn conversations",
                "Automatic language detection",
                "String property analysis",
                "Batch translations"
            ],
            "api_version": "v1",
            "last_updated": "2025-11-03"
        }
    )


# ============================================================================
# TELEX AGENT JSON (A2A Discovery per docs)
# ============================================================================

@app.get(
    "/.well-known/agent.json",
    tags=["Agent Discovery"],
    responses={
        200: {"description": "Telex Agent JSON retrieved successfully"}
    }
)
def get_telex_agent_json():
    """
    Telex-compliant Agent JSON served at /.well-known/agent.json
    including agent skills as described in the docs.
    """
    import os
    base_url = os.getenv("BASE_URL", "https://your-app-domain.com")
    provider_name = os.getenv("PROVIDER_NAME", "HNG Backend Team")
    provider_url = os.getenv("PROVIDER_URL", "https://github.com/yourusername/multilingo-agent")

    # Define skills in Telex format
    skills = [
        {
            "id": "translation",
            "name": "Translation",
            "description": "Translate text between many languages",
            "inputModes": ["text/plain", "application/json"],
            "outputModes": ["application/json", "text/plain"],
            "examples": [
                "Translate 'hello world' to Spanish",
                "How do you say 'thank you' in French?"
            ]
        },
        {
            "id": "language-detection",
            "name": "Language Detection",
            "description": "Automatically detect the language of input text",
            "inputModes": ["text/plain"],
            "outputModes": ["application/json", "text/plain"],
            "examples": [
                "What language is 'hola mundo'?",
                "Detect language of 'bonjour'"
            ]
        },
        {
            "id": "string-analysis",
            "name": "String Analysis",
            "description": "Analyze text properties like length, word count, palindrome detection",
            "inputModes": ["text/plain"],
            "outputModes": ["application/json"],
            "examples": [
                "Analyze 'racecar'",
                "Check properties of 'level'"
            ]
        },
        {
            "id": "multi-language-translation",
            "name": "Multi-Language Translation",
            "description": "Translate text to multiple languages simultaneously",
            "inputModes": ["application/json", "text/plain"],
            "outputModes": ["application/json"],
            "examples": [
                "Translate 'hello' to Spanish, French, and German"
            ]
        }
    ]

    agent_json = {
        "name": "MultiLingo Agent",
        "description": "AI-powered translation and string analysis agent with NLU",
        "url": base_url,
        "provider": {
            "name": provider_name,
            "url": provider_url
        },
        "version": "2.0.0",
        "documentationUrl": provider_url,
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "stateTransitionHistory": True
        },
        "defaultInputModes": ["text/plain", "application/json"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": skills,
        "supportsAuthenticatedExtendedCard": False
    }

    return agent_json


# ============================================================================
# JSON-RPC 2.0 ROOT ENDPOINT (Telex A2A Communication)
# ============================================================================

@app.post(
    "/",
    tags=["Telex Integration"],
    responses={
        200: {"description": "JSON-RPC processed"},
        400: {"description": "Invalid request"},
        401: {"description": "Unauthorized"}
    }
)
def jsonrpc_root(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    _: None = Depends(verify_telex_api_key)
):
    """
    Minimal JSON-RPC 2.0 endpoint expected by Telex for A2A.
    Supported methods:
      - translation.translate (params: {text, target_language, source_language?})
      - translation.multiple (params: {text, target_languages: []})
      - language.detect (params: {text})
      - string.analyze (params: {text})
    """
    try:
        jsonrpc = payload.get("jsonrpc")
        method = payload.get("method")
        params = payload.get("params") or {}
        req_id = payload.get("id")

        if jsonrpc != "2.0" or not method:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Invalid Request"}}

        # Import here to avoid circulars on startup
        from app.translator import translate_text, translate_to_multiple, detect_language
        from app.analyzer import analyze_string

        if method == "translation.translate":
            text = params.get("text")
            target_language = params.get("target_language")
            source_language = params.get("source_language")
            if not text or not target_language:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Missing text or target_language"}}
            result = translate_text(text, target_language, source_language)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}

        if method == "translation.multiple":
            text = params.get("text")
            target_languages = params.get("target_languages") or params.get("targets")
            if not text or not isinstance(target_languages, list) or not target_languages:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Missing text or target_languages"}}
            result = translate_to_multiple(text, target_languages, params.get("source_language"))
            return {"jsonrpc": "2.0", "id": req_id, "result": result}

        if method == "language.detect":
            text = params.get("text")
            if not text:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Missing text"}}
            code, name, confidence = detect_language(text)
            return {"jsonrpc": "2.0", "id": req_id, "result": {"language_code": code, "language_name": name, "confidence": confidence}}

        if method == "string.analyze":
            text = params.get("text")
            if not text:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Missing text"}}
            analysis = analyze_string(text)
            return {"jsonrpc": "2.0", "id": req_id, "result": analysis}

        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
    except HTTPException:
        raise
    except Exception as e:
        return {"jsonrpc": "2.0", "id": payload.get("id"), "error": {"code": -32603, "message": f"Internal error: {str(e)}"}}


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
    db: Session = Depends(get_db),
    _: None = Depends(verify_telex_api_key)
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