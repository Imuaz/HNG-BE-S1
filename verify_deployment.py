"""
Final verification before deployment
"""
import sys

print("=" * 70)
print("DEPLOYMENT VERIFICATION")
print("=" * 70)

# Test 1: Import main app
print("\n1. Testing app imports...")
try:
    from app.main import app
    print("   ✅ Main app imports successfully")
except Exception as e:
    print(f"   ❌ Failed to import app: {e}")
    sys.exit(1)

# Test 2: Import chat handler
print("\n2. Testing chat handler...")
try:
    from app.chat_handler import process_chat_message
    print("   ✅ Chat handler imports successfully")
except Exception as e:
    print(f"   ❌ Failed to import chat handler: {e}")
    sys.exit(1)

# Test 3: Test chat processing
print("\n3. Testing chat message processing...")
try:
    result = process_chat_message("help")
    if result['success']:
        print("   ✅ Chat processing works")
    else:
        print("   ❌ Chat processing failed")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error processing message: {e}")
    sys.exit(1)

# Test 4: Test translation
print("\n4. Testing translation...")
try:
    result = process_chat_message("translate hello to spanish")
    if result['success'] and result['intent'] == 'translate':
        print(f"   ✅ Translation works: {result['message']}")
    else:
        print("   ❌ Translation failed")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error in translation: {e}")
    sys.exit(1)

# Test 5: Test list languages
print("\n5. Testing list languages...")
try:
    result = process_chat_message("list languages")
    if result['success'] and result['intent'] == 'list_languages':
        print("   ✅ List languages works")
    else:
        print("   ❌ List languages failed")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error listing languages: {e}")
    sys.exit(1)

# Test 6: Check schemas
print("\n6. Testing schemas...")
try:
    from app.schemas import AgentCard, AgentSkill
    print("   ✅ Agent card schemas available")
except Exception as e:
    print(f"   ❌ Failed to import schemas: {e}")
    sys.exit(1)

# Test 7: Check all endpoints exist
print("\n7. Checking endpoints...")
try:
    routes = [route.path for route in app.routes]
    required_endpoints = [
        "/.well-known/agent-card",
        "/webhook/telex",
        "/translate",
        "/health"
    ]
    
    missing = []
    for endpoint in required_endpoints:
        if endpoint in routes:
            print(f"   ✅ {endpoint}")
        else:
            print(f"   ❌ {endpoint} - MISSING")
            missing.append(endpoint)
    
    if missing:
        print(f"\n   ❌ Missing endpoints: {missing}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error checking endpoints: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
print("=" * 70)
print("\nNext steps:")
print("1. Commit and push changes")
print("2. Deploy to production")
print("3. Set BASE_URL environment variable")
print("4. Register with Telex")
print("=" * 70)
