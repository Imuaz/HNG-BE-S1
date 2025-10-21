"""
Test Natural Language Parser
-----------------------------
Tests the natural language query parsing functionality.

Run: python test_nlp_parser.py
"""

from app.nlp_parser import parse_natural_language_query, get_example_queries

def test_palindrome_queries():
    """Test palindrome detection"""
    print("="*60)
    print("Testing Palindrome Queries")
    print("="*60)
    
    tests = [
        ("all palindromes", {"is_palindrome": True}),
        ("palindromic strings", {"is_palindrome": True}),
        ("show me palindrome strings", {"is_palindrome": True}),
        ("not palindromic strings", {"is_palindrome": False}),
        ("non-palindrome strings", {"is_palindrome": False}),
    ]
    
    for query, expected in tests:
        try:
            result = parse_natural_language_query(query)
            status = "✅" if result.get("is_palindrome") == expected.get("is_palindrome") else "❌"
            print(f"{status} '{query}'")
            print(f"   Result: {result}")
        except ValueError as e:
            print(f"❌ '{query}' - Error: {e}")

def test_word_count_queries():
    """Test word count parsing"""
    print("\n" + "="*60)
    print("Testing Word Count Queries")
    print("="*60)
    
    tests = [
        ("single word strings", {"word_count": 1}),
        ("one word palindromes", {"word_count": 1}),
        ("two word strings", {"word_count": 2}),
        ("three word strings", {"word_count": 3}),
        ("5 word strings", {"word_count": 5}),
        ("strings with 10 words", {"word_count": 10}),
    ]
    
    for query, expected in tests:
        try:
            result = parse_natural_language_query(query)
            status = "✅" if result.get("word_count") == expected.get("word_count") else "❌"
            print(f"{status} '{query}'")
            print(f"   Result: {result}")
        except ValueError as e:
            print(f"❌ '{query}' - Error: {e}")

def test_length_queries():
    """Test length filter parsing"""
    print("\n" + "="*60)
    print("Testing Length Queries")
    print("="*60)
    
    tests = [
        ("strings longer than 10 characters", {"min_length": 11}),
        ("strings shorter than 5 characters", {"max_length": 4}),
        ("strings between 5 and 10 characters", {"min_length": 5, "max_length": 10}),
        ("strings at least 20 characters", {"min_length": 20}),
        ("strings at most 15 characters", {"max_length": 15}),
        ("exactly 7 characters", {"min_length": 7, "max_length": 7}),
    ]
    
    for query, expected in tests:
        try:
            result = parse_natural_language_query(query)
            match = all(result.get(k) == v for k, v in expected.items())
            status = "✅" if match else "❌"
            print(f"{status} '{query}'")
            print(f"   Result: {result}")
            if not match:
                print(f"   Expected: {expected}")
        except ValueError as e:
            print(f"❌ '{query}' - Error: {e}")

def test_character_queries():
    """Test character containment parsing"""
    print("\n" + "="*60)
    print("Testing Character Containment Queries")
    print("="*60)
    
    tests = [
        ("strings containing the letter z", {"contains_character": "z"}),
        ("strings with character a", {"contains_character": "a"}),
        ("strings containing letter e", {"contains_character": "e"}),
        ("palindromes containing the first vowel", {"is_palindrome": True, "contains_character": "a"}),
        ("strings with the second vowel", {"contains_character": "e"}),
    ]
    
    for query, expected in tests:
        try:
            result = parse_natural_language_query(query)
            match = all(result.get(k) == v for k, v in expected.items())
            status = "✅" if match else "❌"
            print(f"{status} '{query}'")
            print(f"   Result: {result}")
            if not match:
                print(f"   Expected: {expected}")
        except ValueError as e:
            print(f"❌ '{query}' - Error: {e}")

def test_complex_queries():
    """Test complex multi-filter queries"""
    print("\n" + "="*60)
    print("Testing Complex Queries")
    print("="*60)
    
    tests = [
        (
            "all single word palindromic strings",
            {"word_count": 1, "is_palindrome": True}
        ),
        (
            "palindromes longer than 10 characters with one word",
            {"is_palindrome": True, "min_length": 11, "word_count": 1}
        ),
        (
            "two word strings containing the letter a",
            {"word_count": 2, "contains_character": "a"}
        ),
    ]
    
    for query, expected in tests:
        try:
            result = parse_natural_language_query(query)
            match = all(result.get(k) == v for k, v in expected.items())
            status = "✅" if match else "❌"
            print(f"{status} '{query}'")
            print(f"   Result: {result}")
            if not match:
                print(f"   Expected: {expected}")
        except ValueError as e:
            print(f"❌ '{query}' - Error: {e}")

def test_invalid_queries():
    """Test queries that should fail"""
    print("\n" + "="*60)
    print("Testing Invalid Queries (Should Fail)")
    print("="*60)
    
    invalid_queries = [
        "show me something",
        "hello world",
        "random text with no meaning",
        "",
    ]
    
    for query in invalid_queries:
        try:
            result = parse_natural_language_query(query)
            print(f"❌ '{query}' - Should have failed but got: {result}")
        except ValueError:
            print(f"✅ '{query}' - Correctly rejected")

def test_all_examples():
    """Test all example queries"""
    print("\n" + "="*60)
    print("Testing All Example Queries")
    print("="*60)
    
    examples = get_example_queries()
    passed = 0
    failed = 0
    
    for query in examples:
        try:
            result = parse_natural_language_query(query)
            print(f"✅ '{query}'")
            print(f"   Filters: {result}")
            passed += 1
        except ValueError as e:
            print(f"❌ '{query}' - Error: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")

def main():
    """Run all tests"""
    print("="*60)
    print("NATURAL LANGUAGE PARSER TEST SUITE")
    print("="*60)
    
    try:
        test_palindrome_queries()
        test_word_count_queries()
        test_length_queries()
        test_character_queries()
        test_complex_queries()
        test_invalid_queries()
        test_all_examples()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()