"""
Translation Service
-------------------
Handles language detection and translation using Deep Translator (Google Translate).

Features:
- Auto-detect source language
- Translate to multiple target languages
- Support 100+ languages
- Synchronous (no async/await needed)
"""

from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
from typing import Dict, List, Optional, Tuple
import logging
from functools import lru_cache

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory cache for translations (speeds up repeat requests)
_translation_cache = {}

# Common language codes
LANGUAGE_CODES = {
    "english": "en",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "russian": "ru",
    "japanese": "ja",
    "chinese": "zh-cn",
    "korean": "ko",
    "arabic": "ar",
    "hindi": "hi",
    "dutch": "nl",
    "turkish": "tr",
    "swedish": "sv",
    "polish": "pl",
    "vietnamese": "vi",
    "thai": "th",
    "greek": "el",
    "czech": "cs",
    "danish": "da",
    "finnish": "fi",
    "norwegian": "no",
    "romanian": "ro",
    "ukrainian": "uk",
}

# Reverse mapping
LANGUAGE_NAMES = {v: k for k, v in LANGUAGE_CODES.items()}


def detect_language(text: str) -> Tuple[str, str, float]:
    """
    Detects the language of input text.
    
    Args:
        text: Input text to detect language
    
    Returns:
        Tuple of (language_code, language_name, confidence)
    
    Raises:
        ValueError: If language detection fails
    """
    try:
        lang_code = detect(text)
        lang_name = LANGUAGE_NAMES.get(lang_code, "unknown")
        logger.info(f"Detected language: {lang_name} ({lang_code})")
        return lang_code, lang_name, 1.0
    except LangDetectException as e:
        logger.error(f"Language detection failed: {e}")
        raise ValueError(f"Could not detect language: {str(e)}")


def translate_text(
    text: str,
    target_lang: str,
    source_lang: Optional[str] = None
) -> Dict:
    """
    Translates text to target language using deep-translator with caching.
    
    Args:
        text: Text to translate
        target_lang: Target language code (e.g., 'es', 'fr')
        source_lang: Source language code (optional, auto-detect if None)
    
    Returns:
        Dictionary with translation details
    
    Raises:
        ValueError: If translation fails
    """
    try:
        # Normalize language codes
        target_lang = normalize_language_code(target_lang)
        
        # Check cache first (speeds up repeat requests)
        cache_key = f"{text.lower()}_{target_lang}"
        if cache_key in _translation_cache:
            logger.info(f"Cache hit for: '{text}' → {target_lang}")
            return _translation_cache[cache_key]
        
        # Auto-detect source language if not provided
        detected_name = "unknown"
        if source_lang is None:
            try:
                detected_code, detected_name, _ = detect_language(text)
                source_lang = detected_code
            except ValueError:
                source_lang = 'auto'
                detected_name = "auto-detected"
        else:
            source_lang = normalize_language_code(source_lang)
            detected_name = LANGUAGE_NAMES.get(source_lang, source_lang)
        
        # Perform translation using deep-translator
        logger.info(f"Translating from {source_lang} to {target_lang}")
        
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        
        # If source was 'auto', try to detect what it actually was
        if source_lang == 'auto':
            try:
                detected_code, detected_name, _ = detect_language(text)
                source_lang = detected_code
            except:
                source_lang = 'auto'
        
        result = {
            "original_text": text,
            "translated_text": translated,
            "source_language": source_lang,
            "target_language": target_lang,
            "detected_language": detected_name
        }
        
        # Cache the result (limit cache size to 1000 entries)
        if len(_translation_cache) < 1000:
            _translation_cache[cache_key] = result
        
        logger.info(f"Translation successful: '{text}' → '{translated}'")
        return result
        
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise ValueError(f"Translation failed: {str(e)}")


def translate_to_multiple(
    text: str,
    target_langs: List[str],
    source_lang: Optional[str] = None
) -> Dict:
    """
    Translates text to multiple target languages.
    """
    translations = {}
    detected_lang = None
    
    for target_lang in target_langs:
        try:
            result = translate_text(text, target_lang, source_lang)
            translations[target_lang] = result["translated_text"]
            
            if detected_lang is None:
                detected_lang = result["source_language"]
                
        except ValueError as e:
            logger.warning(f"Failed to translate to {target_lang}: {e}")
            translations[target_lang] = f"[Translation failed: {str(e)}]"
    
    return {
        "original_text": text,
        "source_language": detected_lang or "unknown",
        "translations": translations
    }


def normalize_language_code(lang_input: str) -> str:
    """
    Normalizes language input to standard language code.
    """
    lang_lower = lang_input.lower().strip()
    
    if lang_lower in LANGUAGE_NAMES:
        return lang_lower
    
    if lang_lower in LANGUAGE_CODES:
        return LANGUAGE_CODES[lang_lower]
    
    for name, code in LANGUAGE_CODES.items():
        if name.startswith(lang_lower) or lang_lower.startswith(name[:3]):
            return code
    
    raise ValueError(f"Unrecognized language: {lang_input}")


def get_supported_languages() -> Dict[str, str]:
    """Returns dictionary of supported languages."""
    return LANGUAGE_CODES.copy()


def is_supported_language(lang: str) -> bool:
    """Checks if a language is supported."""
    try:
        normalize_language_code(lang)
        return True
    except ValueError:
        return False