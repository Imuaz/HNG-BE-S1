"""
Chat Handler & Intent Detection
--------------------------------
Handles natural language chat interactions with the MultiLingo Agent.

Features:
- Intent detection (translate, detect language, help, etc.)
- Natural language parsing
- Context-aware responses
- Multi-turn conversations
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


# ============================================================================
# INTENT DETECTION
# ============================================================================

def detect_intent(message: str) -> Tuple[str, Dict]:
    """
    Detects user intent from natural language message.
    
    Intents:
    - 'translate': User wants to translate text
    - 'detect_language': User wants to know what language something is
    - 'analyze': User wants string analysis
    - 'help': User needs help/instructions
    - 'list_languages': User wants to see supported languages
    - 'unknown': Cannot determine intent
    
    Args:
        message: User's message in natural language
    
    Returns:
        Tuple of (intent, extracted_data)
        
    Example:
        detect_intent("Translate 'hello' to Spanish")
        -> ("translate", {"text": "hello", "target_language": "spanish"})
    """
    message_lower = message.lower().strip()
    
    # Intent 1: Translation request
    translation_patterns = [
        # "translate X to Y"
        r'translate\s+["\']?(.+?)["\']?\s+to\s+(\w+)',
        # "translate X into Y"
        r'translate\s+["\']?(.+?)["\']?\s+into\s+(\w+)',
        # "how do you say X in Y"
        r'how\s+(?:do\s+)?(?:you\s+)?say\s+["\']?(.+?)["\']?\s+in\s+(\w+)',
        # "what is X in Y"
        r'what\s+(?:is|\'s)\s+["\']?(.+?)["\']?\s+in\s+(\w+)',
        # "X in Y" (simple form)
        r'^["\']?(.+?)["\']?\s+in\s+(\w+)$',
    ]
    
    for pattern in translation_patterns:
        match = re.search(pattern, message_lower, re.IGNORECASE)
        if match:
            text = match.group(1).strip('"\'')
            target_lang = match.group(2).strip()
            return "translate", {
                "text": text,
                "target_language": target_lang
            }
    
    # Check for "translate to Y" without explicit text
    translate_to_pattern = r'translate\s+(?:this\s+)?(?:to|into)\s+(\w+)'
    match = re.search(translate_to_pattern, message_lower)
    if match:
        target_lang = match.group(1)
        return "translate_context", {
            "target_language": target_lang,
            "needs_context": True
        }
    
    # Intent 2: Language detection
    detect_patterns = [
        r'what\s+language\s+is\s+["\']?(.+?)["\']?',
        r'detect\s+language\s+(?:of\s+)?["\']?(.+?)["\']?',
        r'identify\s+["\']?(.+?)["\']?',
        r'what\s+is\s+this\s+language[:\s]+["\']?(.+?)["\']?',
    ]
    
    for pattern in detect_patterns:
        match = re.search(pattern, message_lower, re.IGNORECASE)
        if match:
            text = match.group(1).strip('"\'')
            return "detect_language", {"text": text}
    
    # Intent 3: String analysis
    analyze_patterns = [
        r'analyze\s+["\']?(.+?)["\']?',
        r'check\s+["\']?(.+?)["\']?',
        r'is\s+["\']?(.+?)["\']?\s+a\s+palindrome',
    ]
    
    for pattern in analyze_patterns:
        match = re.search(pattern, message_lower, re.IGNORECASE)
        if match:
            text = match.group(1).strip('"\'')
            return "analyze", {"text": text}
    
    # Intent 4: Help request
    help_keywords = ['help', 'how', 'what can', 'commands', 'usage', 'guide']
    if any(keyword in message_lower for keyword in help_keywords):
        return "help", {}
    
    # Intent 5: List languages
    if any(phrase in message_lower for phrase in ['list languages', 'show languages', 'supported languages', 'available languages']):
        return "list_languages", {}
    
    # Intent 6: Greeting
    greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon']
    if any(message_lower.startswith(greet) for greet in greetings):
        return "greeting", {}
    
    # Default: Unknown intent
    return "unknown", {}


# ============================================================================
# RESPONSE GENERATION
# ============================================================================

def handle_translation(text: str, target_language: str, analyze: bool = True) -> Dict:
    """
    Handles translation request and generates response.
    
    Args:
        text: Text to translate
        target_language: Target language code or name
        analyze: Whether to include string analysis
    
    Returns:
        Dictionary with response message and data
    """
    try:
        # Normalize language code
        target_lang_code = normalize_language_code(target_language)
        
        # Perform translation
        result = translate_text(text, target_lang_code)
        
        # Build simple, clean response message (no markdown, minimal formatting)
        response_parts = [
            f"Translation Complete!",
            f"",
            f"Original ({result['detected_language']}): {result['original_text']}",
            f"{target_language.title()}: {result['translated_text']}"
        ]
        
        # Add analysis if requested (simplified)
        if analyze:
            analysis = analyze_string(text)
            response_parts.append(f"")
            response_parts.append(f"Analysis:")
            response_parts.append(f"Length: {analysis['length']} characters")
            response_parts.append(f"Words: {analysis['word_count']}")
            if analysis['is_palindrome']:
                response_parts.append(f"Palindrome: Yes")
        
        return {
            "success": True,
            "message": "\n".join(response_parts),
            "data": {
                "original": result['original_text'],
                "translation": result['translated_text'],
                "source_language": result['source_language'],
                "target_language": target_lang_code,
                "analysis": analyze_string(text) if analyze else None
            }
        }
        
    except ValueError as e:
        return {
            "success": False,
            "message": f"❌ Translation failed: {str(e)}",
            "data": None
        }


def handle_language_detection(text: str) -> Dict:
    """
    Handles language detection request.
    
    Args:
        text: Text to detect language
    
    Returns:
        Dictionary with response message and data
    """
    try:
        lang_code, lang_name, confidence = detect_language(text)
        
        message = f"Language Detected!\n\n"
        message += f"Text: {text}\n"
        message += f"Language: {lang_name.title()} ({lang_code})\n"
        message += f"Confidence: {confidence:.0%}"
        
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
            "message": f"❌ Could not detect language: {str(e)}",
            "data": None
        }


def handle_analysis(text: str) -> Dict:
    """
    Handles string analysis request.
    
    Args:
        text: Text to analyze
    
    Returns:
        Dictionary with response message and data
    """
    try:
        analysis = analyze_string(text)
        
        message = f"String Analysis\n\n"
        message += f"Text: {text}\n\n"
        message += f"Properties:\n"
        message += f"Length: {analysis['length']} characters\n"
        message += f"Words: {analysis['word_count']}\n"
        message += f"Unique characters: {analysis['unique_characters']}\n"
        message += f"Palindrome: {'Yes' if analysis['is_palindrome'] else 'No'}\n"
        if analysis['character_frequency_map']:
            most_common = max(analysis['character_frequency_map'].items(), key=lambda x: x[1])[0]
            message += f"Most common character: {most_common}"
        
        return {
            "success": True,
            "message": message,
            "data": analysis
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Analysis failed: {str(e)}",
            "data": None
        }


def handle_help() -> Dict:
    """
    Generates help message with available commands.
    
    Returns:
        Dictionary with help message
    """
    message = """MultiLingo Agent - Help Guide

I can help you with:

Translation:
- "Translate 'hello' to Spanish"
- "How do you say 'thank you' in French?"
- "What is 'bonjour' in English?"

Language Detection:
- "What language is 'hola mundo'?"
- "Detect language of 'bonjour'"

String Analysis:
- "Analyze 'hello world'"
- "Is 'racecar' a palindrome?"

Other Commands:
- "List languages" - See all supported languages
- "Help" - Show this message

Examples:
- Translate "good morning" to German
- What language is "ciao"?
- Analyze "level"

Just ask naturally! I'll understand."""
    
    return {
        "success": True,
        "message": message.strip(),
        "data": None
    }


def handle_list_languages() -> Dict:
    """
    Lists all supported languages.
    
    Returns:
        Dictionary with language list
    """
    languages = get_supported_languages()
    
    # Group languages for better readability
    message = "🌍 **Supported Languages** (25+ languages)\n\n"
    
    lang_list = []
    for name, code in sorted(languages.items()):
        lang_list.append(f"• {name.title()} ({code})")
    
    # Split into columns
    mid = len(lang_list) // 2
    col1 = lang_list[:mid]
    col2 = lang_list[mid:]
    
    message += "\n".join(col1[:10])
    message += f"\n\n...and {len(lang_list) - 10} more!"
    message += "\n\nYou can use either the language name or code!"
    
    return {
        "success": True,
        "message": message,
        "data": {"languages": languages}
    }


def handle_greeting() -> Dict:
    """
    Handles greeting messages.
    
    Returns:
        Dictionary with greeting response
    """
    message = """Hello! I'm MultiLingo Agent!

I'm here to help you with:
- Translations (25+ languages)
- Language detection
- String analysis

Try asking me:
- "Translate 'hello' to Spanish"
- "What language is this?"
- "Analyze 'racecar'"

Type "help" to see all commands!"""
    
    return {
        "success": True,
        "message": message.strip(),
        "data": None
    }


def handle_unknown() -> Dict:
    """
    Handles unknown/unclear requests.
    
    Returns:
        Dictionary with clarification message
    """
    message = """I'm not sure what you want me to do.

Here are some things I can help with:

Translation:
"Translate 'hello' to Spanish"

Language Detection:
"What language is 'bonjour'?"

String Analysis:
"Analyze 'hello world'"

Type "help" for more examples!"""
    
    return {
        "success": True,
        "message": message.strip(),
        "data": None
    }


# ============================================================================
# MAIN CHAT PROCESSOR
# ============================================================================

def process_chat_message(
    message: str,
    context: Optional[Dict] = None
) -> Dict:
    """
    Processes a chat message and generates appropriate response.
    
    This is the main entry point for chat interactions.
    
    Args:
        message: User's message
        context: Optional conversation context (previous messages, etc.)
    
    Returns:
        Dictionary with:
        {
            "message": "Agent's response",
            "intent": "detected_intent",
            "action_taken": "action_performed",
            "data": {...additional data...},
            "success": True/False
        }
    """
    # Detect intent
    intent, extracted_data = detect_intent(message)
    
    # Route to appropriate handler
    if intent == "translate":
        result = handle_translation(
            extracted_data["text"],
            extracted_data["target_language"],
            analyze=True
        )
        action = f"translated_to_{extracted_data['target_language']}"
        
    elif intent == "translate_context":
        # Need previous context
        if context and context.get("last_text"):
            result = handle_translation(
                context["last_text"],
                extracted_data["target_language"],
                analyze=True
            )
            action = f"translated_context_to_{extracted_data['target_language']}"
        else:
            result = {
                "success": False,
                "message": "I need some text to translate! Try: 'Translate [your text] to [language]'",
                "data": None
            }
            action = "missing_context"
            
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
        
    else:  # unknown
        result = handle_unknown()
        action = "unknown_intent"
    
    # Build complete response
    return {
        "message": result["message"],
        "intent": intent,
        "action_taken": action,
        "data": result.get("data"),
        "success": result["success"]
    }


# ============================================================================
# OPTIMIZED A2A PROCESSOR (Fast, no analysis, uses cache)
# ============================================================================

def process_chat_message_fast(
    message: str,
    context: Optional[Dict] = None
) -> Dict:
    """
    Optimized chat processor for A2A endpoints.
    
    Differences from process_chat_message:
    - Uses translation cache
    - Skips string analysis (faster)
    - Optimized for sub-2s response times
    
    Args:
        message: User's message
        context: Optional conversation context
    
    Returns:
        Dictionary with response data
    """
    from app.cache import get_cached_translation, set_cached_translation
    
    # Detect intent
    intent, extracted_data = detect_intent(message)
    
    # Route to appropriate handler
    if intent == "translate":
        text = extracted_data["text"]
        target_lang = extracted_data["target_language"]
        
        # Check cache first
        cached = get_cached_translation(text, target_lang)
        if cached:
            # Fast path: return cached result
            response_parts = [
                f"✅ **Translation Complete!**\n",
                f"**Original ({cached['detected_language']}):** {cached['original_text']}",
                f"**{target_lang.title()}:** {cached['translated_text']}"
            ]
            result = {
                "success": True,
                "message": "\n".join(response_parts),
                "data": {
                    "original": cached['original_text'],
                    "translation": cached['translated_text'],
                    "source_language": cached['source_language'],
                    "target_language": target_lang
                }
            }
        else:
            # Cache miss: translate (no analysis for speed)
            result = handle_translation(text, target_lang, analyze=False)
            # Cache the result
            if result["success"] and result.get("data"):
                set_cached_translation(
                    text,
                    target_lang,
                    {
                        "original_text": result["data"]["original"],
                        "translated_text": result["data"]["translation"],
                        "source_language": result["data"]["source_language"],
                        "target_language": result["data"]["target_language"],
                        "detected_language": result["data"].get("source_language", "unknown")
                    }
                )
        
        action = f"translated_to_{target_lang}"
        
    elif intent == "translate_context":
        if context and context.get("last_text"):
            text = context["last_text"]
            target_lang = extracted_data["target_language"]
            
            # Check cache
            cached = get_cached_translation(text, target_lang)
            if cached:
                response_parts = [
                    f"✅ **Translation Complete!**\n",
                    f"**Original ({cached['detected_language']}):** {cached['original_text']}",
                    f"**{target_lang.title()}:** {cached['translated_text']}"
                ]
                result = {
                    "success": True,
                    "message": "\n".join(response_parts),
                    "data": {
                        "original": cached['original_text'],
                        "translation": cached['translated_text'],
                        "source_language": cached['source_language'],
                        "target_language": target_lang
                    }
                }
            else:
                result = handle_translation(text, target_lang, analyze=False)
                if result["success"] and result.get("data"):
                    set_cached_translation(
                        text,
                        target_lang,
                        {
                            "original_text": result["data"]["original"],
                            "translated_text": result["data"]["translation"],
                            "source_language": result["data"]["source_language"],
                            "target_language": result["data"]["target_language"],
                            "detected_language": result["data"].get("source_language", "unknown")
                        }
                    )
            action = f"translated_context_to_{target_lang}"
        else:
            result = {
                "success": False,
                "message": "I need some text to translate! Try: 'Translate [your text] to [language]'",
                "data": None
            }
            action = "missing_context"
            
    elif intent == "detect_language":
        result = handle_language_detection(extracted_data["text"])
        action = "detected_language"
        
    elif intent == "analyze":
        # For A2A, keep analysis but make it faster
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
        
    else:  # unknown
        result = handle_unknown()
        action = "unknown_intent"
    
    # Build complete response
    return {
        "message": result["message"],
        "intent": intent,
        "action_taken": action,
        "data": result.get("data"),
        "success": result["success"]
    }