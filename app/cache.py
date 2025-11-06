"""
Translation Cache
----------------
In-memory LRU cache for translations to improve A2A response times.
"""
from functools import lru_cache
from typing import Optional, Tuple
import hashlib
import time

# Simple TTL cache implementation
_cache = {}
_cache_ttl = 3600  # 1 hour TTL


def _make_cache_key(text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
    """Create a cache key from translation parameters."""
    key_str = f"{text}|{target_lang}|{source_lang or 'auto'}"
    return hashlib.md5(key_str.encode()).hexdigest()


def get_cached_translation(text: str, target_lang: str, source_lang: Optional[str] = None) -> Optional[dict]:
    """
    Get cached translation if available and not expired.
    
    Returns:
        Cached translation dict or None if not found/expired
    """
    cache_key = _make_cache_key(text, target_lang, source_lang)
    
    if cache_key in _cache:
        cached_data, timestamp = _cache[cache_key]
        if time.time() - timestamp < _cache_ttl:
            return cached_data
        else:
            # Expired, remove it
            del _cache[cache_key]
    
    return None


def set_cached_translation(text: str, target_lang: str, translation_result: dict, source_lang: Optional[str] = None):
    """
    Cache a translation result.
    
    Args:
        text: Original text
        target_lang: Target language
        translation_result: Translation result dict
        source_lang: Source language (optional)
    """
    cache_key = _make_cache_key(text, target_lang, source_lang)
    _cache[cache_key] = (translation_result, time.time())
    
    # Simple cleanup: if cache gets too large, remove oldest entries
    if len(_cache) > 1000:
        # Remove 20% of oldest entries
        sorted_items = sorted(_cache.items(), key=lambda x: x[1][1])
        for key, _ in sorted_items[:200]:
            del _cache[key]


def clear_cache():
    """Clear all cached translations."""
    _cache.clear()


def get_cache_stats() -> dict:
    """Get cache statistics."""
    now = time.time()
    valid_entries = sum(1 for _, (_, ts) in _cache.items() if now - ts < _cache_ttl)
    
    return {
        "total_entries": len(_cache),
        "valid_entries": valid_entries,
        "expired_entries": len(_cache) - valid_entries,
        "ttl_seconds": _cache_ttl
    }

