"""
API Integration Tests
---------------------
Tests all API endpoints with real HTTP requests.

Prerequisites:
1. API must be running: uvicorn app.main:app --reload
2. Install requests: pip install requests

Run: python test_api.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_response(response):
    """Pretty print response details"""
    print(f"   Status: {response.status_code}")
    try:
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"   Response: {response.text}")

def test_create_string():
    """Test POST /strings"""
    print("="*60)
    print("TEST 1: Create String (POST /strings)")
    print("="*60)
    
    # Test 1.1: Create valid string
    print("\n✅ Creating 'hello world'")
    response = requests.post(
        f"{BASE_URL}/strings",
        json={"value": "hello world"}
    )
    print_response(response)
    assert response.status_code == 201, "Expected 201 Created"
    data = response.json()
    assert data["value"] == "hello world"
    assert data["properties"]["length"] == 11
    assert data["properties"]["word_count"] == 2
    print("✅ Test passed!")
    
    # Test 1.2: Try to create duplicate (should fail)
    print("\n❌ Trying to create duplicate 'hello world'")
    response = requests.post(
        f"{BASE_URL}/strings",
        json={"value": "hello world"}
    )
    print_response(response)
    assert response.status_code == 409, "Expected 409 Conflict"
    print("✅ Correctly rejected duplicate!")
    
    # Test 1.3: Create palindrome
    print("\n✅ Creating palindrome 'racecar'")
    response = requests.post(
        f"{BASE_URL}/strings",
        json={"value": "racecar"}
    )
    print_response(response)
    assert response.status_code in [201, 409], "Expected 201 or 409"
    if response.status_code == 201:
        data = response.json()
        assert data["properties"]["is_palindrome"] == True
        print("✅ Palindrome detected correctly!")
    
    # Test 1.4: Invalid request (missing value)
    print("\n❌ Trying to create without 'value' field")
    response = requests.post(
        f"{BASE_URL}/strings",
        json={}
    )
    print_response(response)
    assert response.status_code == 422, "Expected 422 Validation Error"
    print("✅ Correctly rejected invalid request!")

def test_get_string():
    """Test GET /strings/{string_value}"""
    print("\n" + "="*60)
    print("TEST 2: Get Specific String (GET /strings/{value})")
    print("="*60)
    
    # First, ensure string exists
    requests.post(f"{BASE_URL}/strings", json={"value": "test string"})
    
    # Test 2.1: Get existing string
    print("\n✅ Getting 'test string'")
    response = requests.get(f"{BASE_URL}/strings/test string")
    print_response(response)
    assert response.status_code == 200, "Expected 200 OK"
    data = response.json()
    assert data["value"] == "test string"
    print("✅ Test passed!")
    
    # Test 2.2: Get non-existent string
    print("\n❌ Getting non-existent string")
    response = requests.get(f"{BASE_URL}/strings/does not exist")
    print_response(response)
    assert response.status_code == 404, "Expected 404 Not Found"
    print("✅ Correctly returned 404!")

def test_list_strings():
    """Test GET /strings with filters"""
    print("\n" + "="*60)
    print("TEST 3: List Strings (GET /strings)")
    print("="*60)
    
    # Create test data
    print("\n📝 Creating test data...")
    test_strings = ["racecar", "level", "hello", "world", "python"]
    for s in test_strings:
        requests.post(f"{BASE_URL}/strings", json={"value": s})
    
    # Test 3.1: Get all strings
    print("\n✅ Getting all strings")
    response = requests.get(f"{BASE_URL}/strings")
    print_response(response)
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Found {data['count']} strings")
    
    # Test 3.2: Filter by palindrome
    print("\n✅ Filtering palindromes")
    response = requests.get(f"{BASE_URL}/strings?is_palindrome=true")
    print_response(response)
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Found {data['count']} palindromes")
    
    # Verify all are palindromes
    for item in data["data"]:
        assert item["properties"]["is_palindrome"] == True
    print("✅ All results are palindromes!")
    
    # Test 3.3: Filter by word count
    print("\n✅ Filtering single-word strings")
    response = requests.get(f"{BASE_URL}/strings?word_count=1")
    print_response(response)
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Found {data['count']} single-word strings")
    
    # Test 3.4: Filter by length
    print("\n✅ Filtering strings with 5-10 characters")
    response = requests.get(f"{BASE_URL}/strings?min_length=5&max_length=10")
    print_response(response)
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Found {data['count']} strings")
    
    # Test 3.5: Filter by character
    print("\n✅ Filtering strings containing 'e'")
    response = requests.get(f"{BASE_URL}/strings?contains_character=e")
    print_response(response)
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Found {data['count']} strings with 'e'")
    
    # Test 3.6: Invalid filter (max < min)
    print("\n❌ Trying invalid filter (max_length < min_length)")
    response = requests.get(f"{BASE_URL}/strings?min_length=10&max_length=5")
    print_response(response)
    assert response.status_code == 400, "Expected 400 Bad Request"
    print("✅ Correctly rejected invalid filter!")

def test_natural_language():
    """Test GET /strings/filter-by-natural-language"""
    print("\n" + "="*60)
    print("TEST 4: Natural Language Filtering")
    print("="*60)
    
    # Test 4.1: Simple query
    print("\n✅ Query: 'all single word palindromic strings'")
    response = requests.get(
        f"{BASE_URL}/strings/filter-by-natural-language",
        params={"query": "all single word palindromic strings"}
    )
    print_response(response)
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Found {data['count']} matches")
    print(f"   Interpreted as: {data['interpreted_query']['parsed_filters']}")
    
    # Test 4.2: Length query
    print("\n✅ Query: 'strings longer than 10 characters'")
    response = requests.get(
        f"{BASE_URL}/strings/filter-by-natural-language",
        params={"query": "strings longer than 10 characters"}
    )
    print_response(response)
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Found {data['count']} matches")
    
    # Test 4.3: Character query
    print("\n✅ Query: 'strings containing the letter z'")
    response = requests.get(
        f"{BASE_URL}/strings/filter-by-natural-language",
        params={"query": "strings containing the letter z"}
    )
    print_response(response)
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Found {data['count']} matches")
    
    # Test 4.4: Invalid query
    print("\n❌ Query: 'gibberish query that makes no sense'")
    response = requests.get(
        f"{BASE_URL}/strings/filter-by-natural-language",
        params={"query": "gibberish query that makes no sense"}
    )
    print_response(response)
    assert response.status_code == 400, "Expected 400 Bad Request"
    print("✅ Correctly rejected invalid query!")

def test_delete_string():
    """Test DELETE /strings/{string_value}"""
    print("\n" + "="*60)
    print("TEST 5: Delete String (DELETE /strings/{value})")
    print("="*60)
    
    # First, create a string to delete
    print("\n📝 Creating 'deleteme' string")
    requests.post(f"{BASE_URL}/strings", json={"value": "deleteme"})
    
    # Test 5.1: Delete existing string
    print("\n✅ Deleting 'deleteme'")
    response = requests.delete(f"{BASE_URL}/strings/deleteme")
    print(f"   Status: {response.status_code}")
    assert response.status_code == 204, "Expected 204 No Content"
    print("✅ Delete successful!")
    
    # Test 5.2: Verify deletion
    print("\n✅ Verifying deletion")
    response = requests.get(f"{BASE_URL}/strings/deleteme")
    assert response.status_code == 404, "String should not exist"
    print("✅ String was deleted!")
    
    # Test 5.3: Delete non-existent string
    print("\n❌ Trying to delete non-existent string")
    response = requests.delete(f"{BASE_URL}/strings/does not exist")
    print(f"   Status: {response.status_code}")
    assert response.status_code == 404, "Expected 404 Not Found"
    print("✅ Correctly returned 404!")

def test_health_and_root():
    """Test health check and root endpoints"""
    print("\n" + "="*60)
    print("TEST 6: Health Check & Root Endpoints")
    print("="*60)
    
    # Test 6.1: Root endpoint
    print("\n✅ Testing root endpoint (GET /)")
    response = requests.get(f"{BASE_URL}/")
    print_response(response)
    assert response.status_code == 200
    print("✅ Root endpoint works!")
    
    # Test 6.2: Health check
    print("\n✅ Testing health check (GET /health)")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health check passed!")

def main():
    """Run all API tests"""
    print("="*60)
    print("API INTEGRATION TEST SUITE")
    print("="*60)
    print("\n⚠️  Make sure the API is running:")
    print("   uvicorn app.main:app --reload")
    print("\n" + "="*60)
    
    try:
        # Verify API is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not responding correctly!")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API!")
        print("   Make sure the API is running: uvicorn app.main:app --reload")
        return
    
    try:
        test_health_and_root()
        test_create_string()
        test_get_string()
        test_list_strings()
        test_natural_language()
        test_delete_string()
        
        print("\n" + "="*60)
        print("✅ ALL API TESTS PASSED!")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("❌ 'requests' library not installed!")
        print("   Install it with: pip install requests")
        exit(1)
    
    main()