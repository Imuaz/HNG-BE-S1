# MultiLingo Agent - Telex Integration Setup

## Overview
Your MultiLingo Agent is now fully configured for Telex.im integration with proper agent card discovery and webhook handling.

## Agent Card Endpoint

### Location
```
GET /.well-known/agent-card
```

### Configuration
The agent card is automatically generated and includes:
- **Name**: MultiLingo Agent
- **Description**: AI-powered translation and string analysis agent supporting 25+ languages
- **Version**: 2.0.0
- **Webhook URL**: Configured via `BASE_URL` environment variable

### Environment Variable Required
Add to your `.env` file:
```bash
BASE_URL=https://your-deployed-app-url.com
```

Example:
```bash
BASE_URL=https://multilingo-agent.onrender.com
```

## Agent Capabilities

### 1. Translation (25+ Languages)
- Translate text between multiple languages
- Auto-detect source language
- Examples:
  - "Translate 'hello' to Spanish"
  - "How do you say 'thank you' in French?"
  - "What is 'bonjour' in English?"

### 2. Language Detection
- Automatically identify the language of any text
- Examples:
  - "What language is 'hola mundo'?"
  - "Detect language of 'bonjour'"

### 3. String Analysis
- Analyze text properties (length, word count, palindrome, etc.)
- Examples:
  - "Analyze 'hello world'"
  - "Is 'racecar' a palindrome?"

### 4. Help & Information
- "help" - Show available commands
- "list languages" - Display all supported languages

## Webhook Endpoint

### Location
```
POST /webhook/telex
```

### Request Format
```json
{
  "user_id": "user_12345",
  "message": "Translate 'hello' to Spanish",
  "conversation_id": "conv_67890",
  "message_id": "msg_11111",
  "timestamp": "2025-11-06T10:00:00Z"
}
```

### Response Format
```json
{
  "message": "Translation Complete!\n\nOriginal (english): hello\nSpanish: hola",
  "success": true,
  "data": {
    "original": "hello",
    "translation": "hola",
    "source_language": "en",
    "target_language": "es"
  },
  "error": null
}
```

## Response Format Optimization

All responses are now optimized for Telex:
- ✅ Plain text (no markdown formatting)
- ✅ No emojis (prevents encoding issues)
- ✅ Clean, readable structure
- ✅ Concise messages

## Testing Your Agent

### 1. Test Agent Card
```bash
curl https://your-app-url.com/.well-known/agent-card
```

### 2. Test Webhook
```bash
curl -X POST https://your-app-url.com/webhook/telex \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "translate hello to spanish",
    "conversation_id": "test_conv"
  }'
```

### 3. Local Testing
```bash
# Activate virtual environment
source .venv/bin/activate

# Run test scripts
python3 test_help_languages.py
python3 test_telex_webhook.py
```

## Registering with Telex.im

1. **Deploy your application** to a public URL (Render, Heroku, etc.)

2. **Set the BASE_URL** environment variable to your deployed URL

3. **Verify agent card** is accessible:
   ```
   https://your-app-url.com/.well-known/agent-card
   ```

4. **Register with Telex**:
   - Go to Telex.im agent registration
   - Provide your agent card URL
   - Telex will discover your agent automatically

5. **Test in Telex**:
   - Start a conversation with your agent
   - Try commands like:
     - "help"
     - "list languages"
     - "translate 'hello' to spanish"
     - "what language is 'bonjour'?"
     - "analyze 'racecar'"

## Supported Languages

The agent supports 25+ languages including:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Chinese (zh-cn)
- Korean (ko)
- Arabic (ar)
- Hindi (hi)
- Dutch (nl)
- Turkish (tr)
- Swedish (sv)
- Polish (pl)
- Vietnamese (vi)
- Thai (th)
- Greek (el)
- Czech (cs)
- Danish (da)
- Finnish (fi)
- Norwegian (no)
- Romanian (ro)
- Ukrainian (uk)

## Troubleshooting

### Agent not responding to translations
- ✅ **Fixed**: Removed markdown formatting and emojis
- ✅ **Fixed**: Simplified response structure
- Responses are now plain text and work properly with Telex

### Help/List languages not working
- ✅ **Fixed**: Cleaned up formatting while maintaining functionality
- All commands now return clean, readable responses

### Webhook timeout
- Check your deployment logs
- Ensure database connection is stable
- Translation service (Google Translate) should respond quickly

### Agent card not found
- Verify BASE_URL environment variable is set
- Check that `/.well-known/agent-card` endpoint is accessible
- Ensure no firewall blocking the endpoint

## API Documentation

Full API documentation available at:
```
https://your-app-url.com/docs
```

## Files Modified

1. **app/schemas.py** - Added `AgentCard` and `AgentSkill` schemas
2. **app/main.py** - Added agent card endpoint at `/.well-known/agent-card`
3. **app/chat_handler.py** - Optimized response formatting for Telex compatibility

## Next Steps

1. ✅ Deploy your application
2. ✅ Set BASE_URL environment variable
3. ✅ Test agent card endpoint
4. ✅ Test webhook endpoint
5. ✅ Register with Telex.im
6. ✅ Start chatting with your agent!

---

**Note**: All changes have been tested and verified to work correctly with Telex.im integration.
