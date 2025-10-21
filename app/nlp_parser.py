"""
Natural Language Query Parser
------------------------------
Converts natural language queries into filter parameters.

Examples:
- "all single word palindromic strings" → {word_count: 1, is_palindrome: True}
- "strings longer than 10 characters" → {min_length: 11}
- "strings containing the letter z" → {contains_character: "z"}
"""

import re
from typing import Dict, Optional


def parse_natural_language_query(query: str) -> Dict:
    """
    Parses a natural language query into filter parameters.
    
    Uses regex patterns to detect keywords and extract filter values.
    
    Args:
        query: Natural language string describing desired filters
    
    Returns:
        Dictionary of filter parameters
    
    Raises:
        ValueError: If query cannot be parsed
    
    Examples:
        >>> parse_natural_language_query("all single word palindromes")
        {'word_count': 1, 'is_palindrome': True}
        
        >>> parse_natural_language_query("strings longer than 10 characters")
        {'min_length': 11}
    """
    filters = {}
    query_lower = query.lower()
    
    # Pattern 1: Palindrome detection
    # Matches: "palindrome", "palindromic", "palindromes"
    if re.search(r'\bpalindrom(?:e|ic|es)\b', query_lower):
        filters["is_palindrome"] = True
    
    # Pattern 2: Word count
    # Matches: "single word", "one word", "2 words", "three words"
    word_count_patterns = [
        (r'\bsingle\s+word\b', 1),
        (r'\bone\s+word\b', 1),
        (r'\b(\d+)\s+words?\b', None),  # "2 words", "3 word"
        (r'\btwo\s+words?\b', 2),
        (r'\bthree\s+words?\b', 3),
        (r'\bfour\s+words?\b', 4),
        (r'\bfive\s+words?\b', 5),
    ]
    
    for pattern, count in word_count_patterns:
        match = re.search(pattern, query_lower)
        if match:
            if count is None:
                # Extract number from match (e.g., "5 words" → 5)
                filters["word_count"] = int(match.group(1))
            else:
                filters["word_count"] = count
            break
    
    # Pattern 3: Length filters
    # Matches: "longer than X", "shorter than X", "between X and Y characters"
    
    # Longer than X → min_length = X + 1
    longer_match = re.search(r'\blonger\s+than\s+(\d+)', query_lower)
    if longer_match:
        filters["min_length"] = int(longer_match.group(1)) + 1
    
    # Shorter than X → max_length = X - 1
    shorter_match = re.search(r'\bshorter\s+than\s+(\d+)', query_lower)
    if shorter_match:
        filters["max_length"] = int(shorter_match.group(1)) - 1
    
    # At least X characters → min_length = X
    at_least_match = re.search(r'\bat\s+least\s+(\d+)\s+characters?', query_lower)
    if at_least_match:
        filters["min_length"] = int(at_least_match.group(1))
    
    # At most X characters → max_length = X
    at_most_match = re.search(r'\bat\s+most\s+(\d+)\s+characters?', query_lower)
    if at_most_match:
        filters["max_length"] = int(at_most_match.group(1))
    
    # Between X and Y characters → min_length = X, max_length = Y
    between_match = re.search(r'\bbetween\s+(\d+)\s+and\s+(\d+)\s+characters?', query_lower)
    if between_match:
        filters["min_length"] = int(between_match.group(1))
        filters["max_length"] = int(between_match.group(2))
    
    # Exactly X characters → min_length = X, max_length = X
    exactly_match = re.search(r'\bexactly\s+(\d+)\s+characters?', query_lower)
    if exactly_match:
        length = int(exactly_match.group(1))
        filters["min_length"] = length
        filters["max_length"] = length
    
    # Pattern 4: Contains character
    # Matches: "containing the letter X", "with the character Y", "that contain Z"
    
    # "containing the letter X" or "contains letter X"
    letter_match = re.search(r'\bcontain(?:ing|s)?\s+(?:the\s+)?letter\s+([a-z])\b', query_lower)
    if letter_match:
        filters["contains_character"] = letter_match.group(1)
    
    # "containing the character X" or "with character X"
    char_match = re.search(r'\b(?:containing|with)\s+(?:the\s+)?characters?\s+([a-z])\b', query_lower)
    if char_match:
        filters["contains_character"] = char_match.group(1)
    
    # "strings with X" where X is a single letter
    with_match = re.search(r'\bstrings?\s+with\s+([a-z])\b', query_lower)
    if with_match:
        filters["contains_character"] = with_match.group(1)
    
    # Special case: "first vowel" or "second vowel", etc.
    vowel_match = re.search(r'\b(?:first|second|third|fourth|fifth)\s+vowel\b', query_lower)
    if vowel_match:
        vowels = ['a', 'e', 'i', 'o', 'u']
        vowel_order = {
            'first': 0,
            'second': 1,
            'third': 2,
            'fourth': 3,
            'fifth': 4
        }
        for word, index in vowel_order.items():
            if word in query_lower:
                filters["contains_character"] = vowels[index]
                break
    
    # Pattern 5: Empty/blank strings
    if re.search(r'\bempty\s+strings?\b', query_lower):
        filters["min_length"] = 0
        filters["max_length"] = 0
    
    # Pattern 6: Non-palindrome
    # Matches: "not palindrome", "non-palindromic"
    if re.search(r'\b(?:not|non)[-\s]palindrom(?:e|ic|es)\b', query_lower):
        filters["is_palindrome"] = False
    
    # If no filters were extracted, raise error
    if not filters:
        raise ValueError(
            "Could not parse query. Try queries like: "
            "'all single word palindromes', "
            "'strings longer than 10 characters', "
            "'strings containing the letter z'"
        )
    
    return filters


def get_example_queries() -> list:
    """
    Returns list of example natural language queries that can be parsed.
    
    Useful for API documentation and testing.
    """
    return [
        "all single word palindromic strings",
        "palindromes with one word",
        "strings longer than 10 characters",
        "strings shorter than 5 characters",
        "strings between 5 and 10 characters",
        "strings containing the letter z",
        "strings with the character a",
        "palindromic strings containing the first vowel",
        "two word strings",
        "strings with exactly 7 characters",
        "not palindromic strings",
        "strings at least 20 characters long",
        "empty strings",
    ]


# ============================================================================
# Examples and Testing
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Natural Language Query Parser - Examples")
    print("="*60)
    
    examples = get_example_queries()
    
    for query in examples:
        print(f"\nQuery: \"{query}\"")
        try:
            filters = parse_natural_language_query(query)
            print(f"Parsed filters: {filters}")
        except ValueError as e:
            print(f"❌ Error: {e}")
    
    # Test custom query
    print("\n" + "="*60)
    print("Test Your Own Query")
    print("="*60)
    
    custom_query = "all palindromes with 3 words containing the letter e"
    print(f"\nQuery: \"{custom_query}\"")
    try:
        filters = parse_natural_language_query(custom_query)
        print(f"Parsed filters: {filters}")
    except ValueError as e:
        print(f"❌ Error: {e}")