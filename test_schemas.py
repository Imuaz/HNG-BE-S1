"""
Test Pydantic Schemas
---------------------
Run this to see how Pydantic validates data.

Usage: python test_schemas.py
"""

from app.schemas import StringCreate, StringFilterParams
from pydantic import ValidationError

def test_string_create():
    """Test StringCreate schema validation"""
    print("=" * 60)
    print("Testing StringCreate Schema")
    print("=" * 60)
    
    # Test 1: Valid data
    print("\n✅ Test 1: Valid data")
    try:
        valid = StringCreate(value="hello world")
        print(f"Success! Created: {valid}")
        print(f"Value: {valid.value}")
    except ValidationError as e:
        print(f"Error: {e}")
    
    # Test 2: Missing required field
    print("\n❌ Test 2: Missing 'value' field")
    try:
        invalid = StringCreate()
        print(f"Success: {invalid}")
    except ValidationError as e:
        print(f"Validation Error (expected):")
        print(e)
    
    # Test 3: Wrong type
    print("\n❌ Test 3: Wrong type (integer instead of string)")
    try:
        invalid = StringCreate(value=123)
        print(f"Success: {invalid}")
    except ValidationError as e:
        print(f"Validation Error (expected):")
        print(e)
    
    # Test 4: Empty string (should be allowed)
    print("\n✅ Test 4: Empty string (allowed)")
    try:
        valid = StringCreate(value="")
        print(f"Success! Created: {valid}")
    except ValidationError as e:
        print(f"Error: {e}")


def test_filter_params():
    """Test StringFilterParams schema validation"""
    print("\n" + "=" * 60)
    print("Testing StringFilterParams Schema")
    print("=" * 60)
    
    # Test 1: Valid filters
    print("\n✅ Test 1: Valid filters")
    try:
        valid = StringFilterParams(
            is_palindrome=True,
            min_length=5,
            max_length=20,
            word_count=2
        )
        print(f"Success! Filters: {valid}")
    except ValidationError as e:
        print(f"Error: {e}")
    
    # Test 2: No filters (all optional)
    print("\n✅ Test 2: No filters (all optional)")
    try:
        valid = StringFilterParams()
        print(f"Success! No filters applied: {valid}")
    except ValidationError as e:
        print(f"Error: {e}")
    
    # Test 3: Invalid max_length < min_length
    print("\n❌ Test 3: max_length < min_length")
    try:
        invalid = StringFilterParams(
            min_length=20,
            max_length=5  # Less than min_length!
        )
        print(f"Success: {invalid}")
    except ValidationError as e:
        print(f"Validation Error (expected):")
        print(e)
    
    # Test 4: Invalid contains_character (too long)
    print("\n❌ Test 4: contains_character with multiple characters")
    try:
        invalid = StringFilterParams(
            contains_character="abc"  # Should be single character!
        )
        print(f"Success: {invalid}")
    except ValidationError as e:
        print(f"Validation Error (expected):")
        print(e)
    
    # Test 5: Negative values
    print("\n❌ Test 5: Negative min_length")
    try:
        invalid = StringFilterParams(min_length=-5)
        print(f"Success: {invalid}")
    except ValidationError as e:
        print(f"Validation Error (expected):")
        print(e)


def test_type_coercion():
    """Test how Pydantic converts types"""
    print("\n" + "=" * 60)
    print("Testing Type Coercion")
    print("=" * 60)
    
    # Test 1: String to boolean
    print("\n✅ Test 1: String 'true' → Boolean True")
    try:
        filters = StringFilterParams(is_palindrome="true")
        print(f"Success! is_palindrome type: {type(filters.is_palindrome)}")
        print(f"Value: {filters.is_palindrome}")
    except ValidationError as e:
        print(f"Error: {e}")
    
    # Test 2: String to integer
    print("\n✅ Test 2: String '10' → Integer 10")
    try:
        filters = StringFilterParams(min_length="10")
        print(f"Success! min_length type: {type(filters.min_length)}")
        print(f"Value: {filters.min_length}")
    except ValidationError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_string_create()
    test_filter_params()
    test_type_coercion()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)