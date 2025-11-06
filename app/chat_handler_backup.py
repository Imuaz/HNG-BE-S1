"""
Chat Handler & Intent Detection - FIXED VERSION
"""

import re
from typing import Dict, Tuple, Optional, List
from app.translator import (
    translate_text,
    translate_to_multiple,
    detect_language,
    normalize_language_code,
    get_supported_languages
)
from app.analyzer import analyze_string


def detect_intent(message: str) -> Tuple[str, Dict]:
    """Detects user intent from natural language message."""
    message_lower = message.lower().strip()
    
    # Intent 1: Translation - try quoted text first, then unquoted
    if 'translate' in message_lower:
        # With quotes: translate 'good afternoon' to spanish
        match = re.search(r"translate\s+['\"]([^'\"]+)['\"]\s+(?:to|into)\s+(\w+)", message_lower)
        if match:
            return "translate", {"text": match.group(1), "target_language": match.group(2)}
        
        # Without quotes: translate good afternoon to spanish
        match = re.search(r"translate\s+(.+?)\s+(?:to|into)\s+(\w+)", message_lower)
        if match:
            return "translate", {"text": match.group(1), "target_language": match.group(2)}
    
    # Intent 2: Language detection
    if 'language' in message_lower or 'detect' in message_lower:
        # what language is 'bonjour'?
        match = re.search(r"what\s+language\s+is\s+['\"]?([^'\"?]+)['\"]?", message_lower)
        if match:
            return "detect_language", {"text": match.group(1).strip()}
        
        # detect language of bonjour
        match = re.search(r"detect\s+language\s+(?:of\s+)?['\"]?([^'\"?]+)['\"]?", message_lower)
        if match:
            return "detect_language", {"text": match.group(1).strip()}
    
    # Intent 3: String analysis
    if 'analyze' in message_lower or 'palindrome' in message_lower:
        # analyze 'racecar'
        match = re.search(r"analyze\s+['\"]?([^'\"]+)['\"]?", message_lower)
        if match:
            return "analyze", {"text": match.group(1).strip()}
        
        # is 'racecar' a palindrome
        match = re.search(r"is\s+['\"]?([^'\"]+)['\"]?\s+a\s+palindrome", message_lower)
        if match:
            return "analyze", {"text": match.group(1).strip()}
    
    # Intent 4: List languages (handle typos)
    if 'list' in message_lower and ('lang' in message_lower or 'language' in message_lower):
        return "list_languages", {}
    
    if 'show' in message_lower and 'language' in message_lower:
        return "list_languages", {}
    
    # Intent 5: Help
    if 'help' in message_lower or 'what can' in message_lower or 'commands' in message_lower:
        return "help", {}
    
    # Intent 6: Greeting
    greetings = ['hi', 'hello', 'hey', 'greetings']
    if any(message_lower.startswith(greet) for greet in greetings):
        return "greeting", {}
    
    return "unknown", {}


def handle_translation(text: str, target_language: str, analyze: bool = False) -> Dict:
    """Handles translation request."""
    try:
        target_lang_code = normalize_language_code(target_language)
        result = translate_text(text, target_lang_code)
        message = f"{result['original_text']} → {result['translated_text']}"
        
        return {
            "success": True,
            "message": message,
            "data": {
                "original": result['original_text'],
                "translation": result['translated_text'],
                "source_language": result['source_language'],
                "target_language": target_lang_code
            }
        }
    except ValueError as e:
        return {
            "success": False,
            "message": f"Translation failed: {str(e)}",
            "data": None
        }


def handle_language_detection(text: str) -> Dict:
    """Handles language detection request."""
    try:
        lang_code, lang_name, confidence = detect_language(text)
        message = f"'{text}' is {lang_name.title()} ({lang_code})"
        
        return {
            "success": True,
            "message": message,
            "data": {
                "text": text,
                "language_code": lang_code,
                "language_name": lang_name,
                "confidence": confidence
            }
        }
    except ValueError as e:
        return {
            "success": False,
            "message": f"Could not detect language: {str(e)}",
            "data": None
        }


def handle_analysis(text: str) -> Dict:
    """Handles string analysis request."""
    try:
        analysis = analyze_string(text)
        palindrome = "palindrome" if analysis['is_palindrome'] else "not a palindrome"
        message = f"'{text}' - {analysis['length']} chars, {analysis['word_count']} words, {palindrome}"
        
        return {
            "success": True,
            "message": message,
            "data": analysis
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Analysis failed: {str(e)}",
            "data": None
        }


def handle_help() -> Dict:
    """Generates help message."""
    message = """I can help with:

1. Translation - "Translate 'hello' to Spanish"
2. Language Detection - "What language is 'bonjour'?"
3. String Analysis - "Analyze 'racecar'"
4. List Languages - "list languages"

Just ask naturally!"""
    
    return {
        "success": True,
        "message": message.strip(),
        "data": None
    }


def handle_list_languages() -> Dict:
    """Lists all supported languages."""
    languages = get_supported_languages()
    lang_list = [f"{name.title()} ({code})" for name, code in sorted(languages.items())]
    
    message = "Supported Languages:\n" + ", ".join(lang_list[:10])
    message += f"\n\n+ {len(lang_list) - 10} more languages"
    
    return {
        "success": True,
        "message": message,
        "data": {"languages": languages}
    }


def handle_greeting() -> Dict:
    """Handles greeting messages."""
    message = "Hello! I'm MultiLingo Agent. I can translate text, detect languages, and analyze strings. Type 'help' for commands!"
    
    return {
        "success": True,
        "message": message,
        "data": None
    }


def handle_unknown() -> Dict:
    """Handles unknown/unclear requests."""
    message = "I'm not sure what you want. Try: 'translate hello to spanish', 'what language is bonjour?', or 'help'"
    
    return {
        "success": True,
        "message": message,
        "data": None
    }


def process_chat_message(message: str, context: Optional[Dict] = None) -> Dict:
    """Main entry point for chat interactions."""
    intent, extracted_data = detect_intent(message)
    
    if intent == "translate":
        result = handle_translation(extracted_data["text"], extracted_data["target_language"])
        action = f"translated_to_{extracted_data['target_language']}"
        
    elif intent == "detect_language":
        result = handle_language_detection(extracted_data["text"])
        action = "detected_language"
        
    elif intent == "analyze":
        result = handle_analysis(extracted_data["text"])
        action = "analyzed_string"
        
    elif intent == "help":
        result = handle_help()
        action = "provided_help"
        
    elif intent == "list_languages":
        result = handle_list_languages()
        action = "listed_languages"
        
    elif intent == "greeting":
        result = handle_greeting()
        action = "greeted_user"
        
    else:
        result = handle_unknown()
        action = "unknown_intent"
    
    return {
        "message": result["message"],
        "intent": intent,
        "action_taken": action,
        "data": result.get("data"),
        "success": result["success"]
    }
