# JSON-RPC 2.0 Format Update

## ✅ Updated Response Format

Your MultiLingo Agent now uses the **JSON-RPC 2.0 protocol** matching the chess agent format that works with Telex!

---

## Response Structure

### Example Response:
```json
{
  "jsonrpc": "2.0",
  "id": "test-001",
  "result": {
    "id": "task-uuid",
    "contextId": "context-uuid",
    "status": {
      "state": "input-required",
      "timestamp": "2025-11-07T19:08:33.889738Z",
      "message": {
        "messageId": "msg-uuid",
        "role": "agent",
        "parts": [
          {
            "kind": "text",
            "text": "hello → Hola"
          }
        ],
        "kind": "message",
        "taskId": "task-uuid"
      }
    },
    "artifacts": [
      {
        "artifactId": "artifact-uuid",
        "name": "translate",
        "parts": [
          {
            "kind": "text",
            "text": "hello → Hola"
          }
        ]
      }
    ],
    "history": [
      {
        "role": "user",
        "content": "translate 'hello' to spanish"
      }
    ],
    "kind": "task"
  }
}
```

---

## Key Features

### 1. JSON-RPC 2.0 Compliance
- ✅ `jsonrpc`: "2.0"
- ✅ `id`: Request ID (echoed back)
- ✅ `result`: Task result object

### 2. Task-Based Structure
- ✅ `id`: Unique task ID
- ✅ `contextId`: Conversation context
- ✅ `status`: Current task status
- ✅ `artifacts`: Response artifacts
- ✅ `history`: Message history
- ✅ `kind`: "task"

### 3. Message Parts
- ✅ `kind`: "text"
- ✅ `text`: Actual response content
- ✅ `role`: "agent"

---

## Endpoints

### A2A Protocol Endpoint
```
POST /a2a/agent/multilingoAgent
```

### Request Format:
```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "messages": [
    {
      "role": "user",
      "content": "translate 'hello' to spanish"
    }
  ],
  "contextId": "optional-context-id"
}
```

### Response Examples:

#### Translation:
```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {
    "status": {
      "message": {
        "parts": [
          {
            "kind": "text",
            "text": "hello → hola"
          }
        ]
      }
    }
  }
}
```

#### Language Detection:
```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {
    "status": {
      "message": {
        "parts": [
          {
            "kind": "text",
            "text": "'bonjour' is French (fr)"
          }
        ]
      }
    }
  }
}
```

#### String Analysis:
```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {
    "status": {
      "message": {
        "parts": [
          {
            "kind": "text",
            "text": "'racecar' - 7 chars, 1 words, palindrome"
          }
        ]
      }
    }
  }
}
```

---

## Error Handling

### Error Response Format:
```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": "Error details here"
  }
}
```

---

## Testing

### Test Command:
```bash
python3 test_jsonrpc_format.py
```

### Expected Output:
```
✅ Verification:
  - Has 'jsonrpc': True
  - Has 'id': True
  - Has 'result': True
  - Has 'status': True
  - Has 'artifacts': True
  - Has 'kind': True
  - Message has 'parts': True
  - Message text: hello → Hola...
```

---

## Deployment

### 1. Deploy Changes
```bash
git add .
git commit -m "Update to JSON-RPC 2.0 format for Telex compatibility"
git push origin main
```

### 2. Test Endpoint
```bash
curl -X POST https://your-app-url.com/a2a/agent/multilingoAgent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-001",
    "messages": [
      {
        "role": "user",
        "content": "translate hello to spanish"
      }
    ]
  }'
```

### 3. Register with Telex
Use the A2A endpoint:
```
https://your-app-url.com/a2a/agent/multilingoAgent
```

---

## Compatibility

✅ **Matches chess agent format**  
✅ **JSON-RPC 2.0 compliant**  
✅ **Task-based structure**  
✅ **Message parts format**  
✅ **Artifact support**  
✅ **History tracking**  

---

## What Changed

### Before (Simple Format):
```json
{
  "role": "assistant",
  "content": "hello → hola",
  "metadata": {...}
}
```

### After (JSON-RPC 2.0):
```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {
    "status": {
      "message": {
        "parts": [{"kind": "text", "text": "hello → hola"}]
      }
    },
    "artifacts": [...],
    "kind": "task"
  }
}
```

---

## Benefits

1. **Telex Compatibility** - Matches working chess agent format
2. **Standard Protocol** - JSON-RPC 2.0 is industry standard
3. **Rich Structure** - Supports artifacts, history, metadata
4. **Error Handling** - Proper error response format
5. **Extensible** - Easy to add new features

---

## Status

✅ **JSON-RPC 2.0 format implemented**  
✅ **Tested and verified**  
✅ **Ready for Telex integration**  

Deploy and test with Telex!

---

*Last Updated: 2025-11-07*  
*Format: JSON-RPC 2.0*  
*Status: Production Ready*
