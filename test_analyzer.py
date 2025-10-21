"""
Test String Analyzer Functions
-------------------------------
Tests all string analysis functions to ensure they compute properties correctly.

Run: python test_analyzer.py
"""

from app.analyzer import (
    compute_length,
    is_palindrome,
    count_unique_characters,
    count_words,
    compute_sha256_hash,
    compute_character_frequency,
    analyze_string
)

def test_compute_length():
    """Test length computation"""
    print("\n" + "="*60)
    print("Testing: compute_length()")
    print("="*60)
    
    tests = [
        ("hello", 5),
        ("hello world", 11),
        ("", 0),
        ("a", 1),
        ("   ", 3),  # Spaces count as characters
    ]
    
    for string, expected in tests:
        result = compute_length(string)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{string}' -> {result} (expected: {expected})")

def test_is_palindrome():
    """Test palindrome detection"""
    print("\n" + "="*60)
    print("Testing: is_palindrome()")
    print("="*60)
    
    tests = [
        ("racecar", True),
        ("Racecar", True),  # Case-insensitive
        ("hello", False),
        ("A", True),  # Single character is palindrome
        ("aa", True),
        ("ab", False),
        ("", True),  # Empty string is palindrome
        ("A man a plan a canal Panama", False),  # Spaces matter
    ]
    
    for string, expected in tests:
        result = is_palindrome(string)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{string}' -> {result} (expected: {expected})")

def test_count_unique_characters():
    """Test unique character counting"""
    print("\n" + "="*60)
    print("Testing: count_unique_characters()")
    print("="*60)
    
    tests = [
        ("hello", 4),  # h, e, l, o (l appears twice but counted once)
        ("aaa", 1),  # Only 'a'
        ("Hello World", 10),  # Case-sensitive, space counts
        ("", 0),
        ("abc", 3),
    ]
    
    for string, expected in tests:
        result = count_unique_characters(string)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{string}' -> {result} (expected: {expected})")

def test_count_words():
    """Test word counting"""
    print("\n" + "="*60)
    print("Testing: count_words()")
    print("="*60)
    
    tests = [
        ("hello world", 2),
        ("one two three", 3),
        ("one   two    three", 3),  # Multiple spaces handled
        ("   spaced   ", 1),  # Leading/trailing spaces ignored
        ("", 0),  # Empty string
        ("single", 1),
    ]
    
    for string, expected in tests:
        result = count_words(string)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{string}' -> {result} (expected: {expected})")

def test_compute_sha256_hash():
    """Test SHA-256 hash computation"""
    print("\n" + "="*60)
    print("Testing: compute_sha256_hash()")
    print("="*60)
    
    # Test that same input gives same hash
    hash1 = compute_sha256_hash("hello")
    hash2 = compute_sha256_hash("hello")
    
    print(f"✅ Same input produces same hash: {hash1 == hash2}")
    print(f"   Hash: {hash1}")
    
    # Test that different inputs give different hashes
    hash3 = compute_sha256_hash("world")
    print(f"✅ Different input produces different hash: {hash1 != hash3}")
    print(f"   Hash: {hash3}")
    
    # Test hash length (SHA-256 always produces 64 character hex string)
    print(f"✅ Hash length is 64 characters: {len(hash1) == 64}")

def test_compute_character_frequency():
    """Test character frequency map"""
    print("\n" + "="*60)
    print("Testing: compute_character_frequency()")
    print("="*60)
    
    tests = [
        ("hello", {"h": 1, "e": 1, "l": 2, "o": 1}),
        ("aaa", {"a": 3}),
        ("", {}),  # Empty string
    ]
    
    for string, expected in tests:
        result = compute_character_frequency(string)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{string}'")
        print(f"   Result: {result}")
        if result != expected:
            print(f"   Expected: {expected}")

def test_analyze_string():
    """Test complete string analysis"""
    print("\n" + "="*60)
    print("Testing: analyze_string() - Complete Analysis")
    print("="*60)
    
    test_string = "hello world"
    result = analyze_string(test_string)
    
    print(f"\nAnalyzing: '{test_string}'")
    print(f"Results:")
    print(f"  - length: {result['length']}")
    print(f"  - is_palindrome: {result['is_palindrome']}")
    print(f"  - unique_characters: {result['unique_characters']}")
    print(f"  - word_count: {result['word_count']}")
    print(f"  - sha256_hash: {result['sha256_hash'][:32]}...")
    print(f"  - character_frequency_map: {result['character_frequency_map']}")
    
    # Verify all keys are present
    expected_keys = [
        "length", "is_palindrome", "unique_characters",
        "word_count", "sha256_hash", "character_frequency_map"
    ]
    
    all_present = all(key in result for key in expected_keys)
    print(f"\n✅ All properties present: {all_present}")
    
    # Test palindrome
    print(f"\nTesting palindrome: 'racecar'")
    palindrome_result = analyze_string("racecar")
    print(f"  is_palindrome: {palindrome_result['is_palindrome']} (expected: True)")

def main():
    """Run all tests"""
    print("="*60)
    print("STRING ANALYZER TEST SUITE")
    print("="*60)
    
    try:
        test_compute_length()
        test_is_palindrome()
        test_count_unique_characters()
        test_count_words()
        test_compute_sha256_hash()
        test_compute_character_frequency()
        test_analyze_string()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()