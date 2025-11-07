# Testing the A2A Endpoint

## Quick Test Commands

### 1. Test Translation (Standard Format)
```bash
curl -X POST https://your-app-url.com/a2a/agent/multilingoAgent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-001",
    "messages": [
      {
        "role": "user",
        "content": "translate '\''good morning'\'' to spanish"
      }
    ]
  }'
```

Expected response:
```json
{
  "jsonrpc": "2.0",
  "id": "test-001",
  "result": {
    "status": {
      "message": {
        "parts": [
          {
            "kind": "text",
            "text": "good morning → buen día"
          }
        ]
      }
    }
  }
}
```

### 2. Test with Alternative Format (text field)
```bash
curl -X POST https://your-app-url.com/a2a/agent/multilingoAgent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-002",
    "messages": [
      {
        "role": "user",
        "text": "translate '\''hello'\'' to french"
      }
    ]
  }'
```

### 3. Test Language Detection
```bash
curl -X POST https://your-app-url.com/a2a/agent/multilingoAgent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-003",
    "messages": [
      {
        "role": "user",
        "content": "what language is '\''bonjour'\''?"
      }
    ]
  }'
```

### 4. Test String Analysis
```bash
curl -X POST https://your-app-url.com/a2a/agent/multilingoAgent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-004",
    "messages": [
      {
        "role": "user",
        "content": "analyze '\''racecar'\''"
      }
    ]
  }'
```

## Testing in Telex.im

Once deployed, test these commands in Telex:

1. **Translation**
   - "translate 'good morning' to spanish"
   - "translate 'hello world' to french"
   - "translate 'thank you' to german"

2. **Language Detection**
   - "what language is 'bonjour'?"
   - "detect language of 'hola mundo'"

3. **String Analysis**
   - "analyze 'racecar'"
   - "is 'level' a palindrome?"

4. **Help Commands**
   - "help"
   - "list languages"

## Expected Behavior

✅ **Before the fix**: Agent would respond with help text for all translation requests  
✅ **After the fix**: Agent correctly processes translation requests and returns actual translations

## Debugging

If issues persist, check the logs for:
```
INFO:app.main:A2A: Extracted user message: '...'
```

This will show what message was actually extracted from the request.

## Local Testing

Run the comprehensive test script:
```bash
python3 /tmp/test_a2a_fix.py
```

This will test all message formats and verify the endpoint is working correctly.

---

*Last Updated: November 7, 2025*
