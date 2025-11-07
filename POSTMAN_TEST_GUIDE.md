# Testing MultiLingo Agent with Postman

## Endpoint
```
POST http://localhost:8000/a2a/agent/multilingoAgent
```

Or for deployed version:
```
POST https://your-deployed-url.com/a2a/agent/multilingoAgent
```

## Headers
```
Content-Type: application/json
```

## Request Body Format

### Translation Request
```json
{
  "jsonrpc": "2.0",
  "id": "test-123",
  "messages": [
    {
      "role": "user",
      "content": "translate hello to Spanish"
    }
  ]
}
```

### Multi-word Translation
```json
{
  "jsonrpc": "2.0",
  "id": "test-456",
  "messages": [
    {
      "role": "user",
      "content": "translate good afternoon to Spanish"
    }
  ]
}
```

### With Quotes
```json
{
  "jsonrpc": "2.0",
  "id": "test-789",
  "messages": [
    {
      "role": "user",
      "content": "translate 'Good morning' to French"
    }
  ]
}
```

### Language Detection
```json
{
  "jsonrpc": "2.0",
  "id": "test-101",
  "messages": [
    {
      "role": "user",
      "content": "what language is 'bonjour'?"
    }
  ]
}
```

### Help
```json
{
  "jsonrpc": "2.0",
  "id": "test-102",
  "messages": [
    {
      "role": "user",
      "content": "help"
    }
  ]
}
```

## Expected Response Format
```json
{
  "jsonrpc": "2.0",
  "id": "test-123",
  "result": {
    "id": "task-uuid",
    "contextId": "context-uuid",
    "status": {
      "state": "input-required",
      "timestamp": "2025-11-07T20:51:28.818766Z",
      "message": {
        "messageId": "message-uuid",
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
        "content": "translate hello to Spanish"
      }
    ],
    "kind": "task"
  }
}
```

## Common Issues

### No Response / Timeout
- **Cause**: Request timeout (was 5 seconds, now increased to 15 seconds)
- **Solution**: Server has been updated with longer timeout

### Getting Help Message Instead of Translation
- **Cause**: Regex pattern not matching multi-word phrases
- **Solution**: Fixed in latest version - now handles all formats

### Server Not Running
- **Check**: `ps aux | grep uvicorn`
- **Start**: `uvicorn app.main:app --reload`
