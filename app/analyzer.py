import hashlib
from typing import Dict


def compute_length(value: str) -> int:
    """
    Computes the length of the string.
    
    Example: "hello" -> 5
    
    Args:
        value: The input string
    
    Returns:
        Number of characters in the string
    """
    return len(value)


def is_palindrome(value: str) -> bool:
    """
    Checks if a string is a palindrome (reads same forwards and backwards).
    Case-insensitive comparison.
    
    Examples:
        "Racecar" -> True (case-insensitive)
        "hello" -> False
        "A man a plan a canal Panama" -> False (spaces matter)
        "aaa" -> True
    
    Args:
        value: The input string
    
    Returns:
        True if palindrome, False otherwise
    """
    # Convert to lowercase for case-insensitive comparison
    normalized = value.lower()
    
    # Compare string with its reverse
    # [::-1] is Python slice notation that reverses a string
    return normalized == normalized[::-1]


def count_unique_characters(value: str) -> int:
    """
    Counts the number of distinct characters in the string.
    
    Examples:
        "hello" -> 4 (h, e, l, o - 'l' appears twice but counted once)
        "aaa" -> 1 (only 'a')
        "Hello World" -> 10 (case-sensitive, space counts)
    
    Args:
        value: The input string
    
    Returns:
        Number of unique characters
    """
    # set() removes duplicates automatically
    # Example: set("hello") -> {'h', 'e', 'l', 'o'}
    return len(set(value))


def count_words(value: str) -> int:
    """
    Counts the number of words separated by whitespace.
    
    Examples:
        "hello world" -> 2
        "one   two    three" -> 3 (multiple spaces handled)
        "   spaced   " -> 1 (leading/trailing spaces ignored)
        "" -> 0 (empty string)
    
    Args:
        value: The input string
    
    Returns:
        Number of words
    """
    # split() without arguments splits by any whitespace and removes empty strings
    words = value.split()
    return len(words)


def compute_sha256_hash(value: str) -> str:
    """
    Computes the SHA-256 hash of the string.
    
    SHA-256 creates a unique "fingerprint" for the string:
    - Same input always produces same hash
    - Different inputs produce different hashes (collision-resistant)
    - One-way (can't reverse the hash to get original string)
    
    Example: "hello" -> "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    
    Args:
        value: The input string
    
    Returns:
        64-character hexadecimal hash string
    """
    # Encode string to bytes (SHA-256 works with bytes, not strings)
    encoded_value = value.encode('utf-8')
    
    # Create SHA-256 hash object
    hash_object = hashlib.sha256(encoded_value)
    
    # Get hexadecimal representation (readable format)
    return hash_object.hexdigest()


def compute_character_frequency(value: str) -> Dict[str, int]:
    """
    Creates a dictionary mapping each character to its occurrence count.
    
    Examples:
        "hello" -> {"h": 1, "e": 1, "l": 2, "o": 1}
        "aaa" -> {"a": 3}
        "Hi There" -> {"H": 1, "i": 1, " ": 1, "T": 1, "h": 1, "e": 2, "r": 1}
    
    Args:
        value: The input string
    
    Returns:
        Dictionary with characters as keys and counts as values
    """
    frequency_map = {}
    
    # Iterate through each character
    for char in value:
        # If character already in map, increment count
        if char in frequency_map:
            frequency_map[char] += 1
        # Otherwise, initialize count to 1
        else:
            frequency_map[char] = 1
    
    return frequency_map


def analyze_string(value: str) -> Dict:
    """
    Performs complete analysis on a string, computing all properties.
    
    This is the main function that combines all individual analyzers.
    
    Args:
        value: The string to analyze
    
    Returns:
        Dictionary containing all computed properties
    
    Example output:
        {
            "length": 11,
            "is_palindrome": False,
            "unique_characters": 8,
            "word_count": 2,
            "sha256_hash": "abc123...",
            "character_frequency_map": {"h": 1, "e": 1, ...}
        }
    """
    return {
        "length": compute_length(value),
        "is_palindrome": is_palindrome(value),
        "unique_characters": count_unique_characters(value),
        "word_count": count_words(value),
        "sha256_hash": compute_sha256_hash(value),
        "character_frequency_map": compute_character_frequency(value)
    }
