"""
Test CRUD Operations
--------------------
This file tests all database CRUD operations.

Run from project root: python test_crud.py
"""

from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.crud import (
    create_string,
    get_string_by_value,
    get_all_strings,
    delete_string,
    string_exists
)

def main():
    print("=" * 60)
    print("Testing CRUD Operations")
    print("=" * 60)
    
    # Create a test session
    db = SessionLocal()
    
    try:
        # Test 1: Create a string
        print("\n✅ Test 1: Create a string")
        test_value = "hello world test"
        
        # First, delete it if it exists (cleanup from previous runs)
        delete_string(db, test_value)
        
        # Create new string
        new_string = create_string(db, test_value)
        print(f"Created: {new_string.value}")
        print(f"ID: {new_string.id[:16]}...")  # Show first 16 chars of hash
        print(f"Properties: length={new_string.length}, palindrome={new_string.is_palindrome}")
        print(f"Word count: {new_string.word_count}")
        print(f"Created at: {new_string.created_at}")
        
        # Test 2: Try to create duplicate (should fail)
        print("\n❌ Test 2: Try to create duplicate")
        try:
            duplicate = create_string(db, test_value)
            print("ERROR: Duplicate was allowed!")
        except IntegrityError:
            print("Success! Duplicate was rejected (expected)")
            db.rollback()  # Roll back the failed transaction
        
        # Test 3: Check if string exists
        print("\n✅ Test 3: Check if string exists")
        exists = string_exists(db, test_value)
        print(f"String exists: {exists}")
        
        # Test 4: Retrieve by value
        print("\n✅ Test 4: Retrieve by value")
        found = get_string_by_value(db, test_value)
        if found:
            print(f"Found: {found.value}")
            print(f"Length: {found.length}")
        else:
            print("Not found")
        
        # Test 5: Create more test strings
        print("\n✅ Test 5: Create test palindromes")
        test_strings = [
            "racecar",
            "level",
            "hello",
            "world"
        ]
        
        for s in test_strings:
            # Delete if exists
            delete_string(db, s)
            # Create
            try:
                created = create_string(db, s)
                print(f"  Created: '{s}' (palindrome: {created.is_palindrome})")
            except IntegrityError:
                db.rollback()
                print(f"  Skipped: '{s}' (already exists)")
        
        # Test 6: Get all strings
        print("\n✅ Test 6: Get all strings")
        all_strings = get_all_strings(db)
        print(f"Total strings in database: {len(all_strings)}")
        for s in all_strings[:3]:  # Show first 3
            print(f"  - {s.value} (length: {s.length})")
        
        # Test 7: Filter palindromes
        print("\n✅ Test 7: Filter palindromes")
        palindromes = get_all_strings(db, is_palindrome=True)
        print(f"Palindromes found: {len(palindromes)}")
        for p in palindromes:
            print(f"  - {p.value}")
        
        # Test 8: Filter by word count
        print("\n✅ Test 8: Filter by word count")
        single_words = get_all_strings(db, word_count=1)
        print(f"Single-word strings: {len(single_words)}")
        for s in single_words[:3]:
            print(f"  - {s.value}")
        
        # Test 9: Filter by length range
        print("\n✅ Test 9: Filter by length (5-10 characters)")
        filtered = get_all_strings(db, min_length=5, max_length=10)
        print(f"Strings with 5-10 characters: {len(filtered)}")
        for s in filtered[:3]:
            print(f"  - {s.value} (length: {s.length})")
        
        # Test 10: Filter by character
        print("\n✅ Test 10: Filter strings containing 'e'")
        with_e = get_all_strings(db, contains_character='e')
        print(f"Strings containing 'e': {len(with_e)}")
        for s in with_e[:3]:
            print(f"  - {s.value}")
        
        # Test 11: Complex filter (palindrome + single word)
        print("\n✅ Test 11: Complex filter (palindrome + single word)")
        complex_filter = get_all_strings(db, is_palindrome=True, word_count=1)
        print(f"Single-word palindromes: {len(complex_filter)}")
        for s in complex_filter:
            print(f"  - {s.value}")
        
        # Test 12: Delete string
        print("\n✅ Test 12: Delete test string")
        success = delete_string(db, test_value)
        if success:
            print(f"Deleted: '{test_value}'")
        else:
            print("Delete failed")
        
        # Verify deletion
        found = get_string_by_value(db, test_value)
        if found is None:
            print("Verified: String no longer exists")
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()
        print("\nDatabase session closed.")

if __name__ == "__main__":
    main()