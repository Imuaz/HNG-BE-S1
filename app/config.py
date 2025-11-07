"""
Application Configuration
-------------------------
Global settings and configurations for the application.
"""

import os
from functools import lru_cache

# ============================================================================
# HTTP CLIENT CONFIGURATION
# ============================================================================

# Default timeout for external API calls (in seconds)
DEFAULT_REQUEST_TIMEOUT = 8  # 8 seconds for translation API
DEFAULT_CONNECTION_TIMEOUT = 5  # 5 seconds for connection

# Configure requests library globally
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def configure_http_client():
    """
    Configure HTTP client with timeouts and retries for better reliability.
    """
    # Create a session with retry strategy
    session = requests.Session()
    
    # Retry strategy: 2 retries with backoff
    retry_strategy = Retry(
        total=2,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# Global HTTP session with configured timeouts
http_session = configure_http_client()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))

# ============================================================================
# API CONFIGURATION
# ============================================================================

API_TIMEOUT = int(os.getenv("API_TIMEOUT", "25"))  # Max time for API endpoint
TRANSLATION_TIMEOUT = int(os.getenv("TRANSLATION_TIMEOUT", "8"))  # Translation API timeout
