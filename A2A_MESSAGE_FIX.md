# A2A Message Extraction Fix

## Issue Description

The MultiLingo Agent was not responding correctly to translation requests from Telex.im. When users sent messages like "translate 'good morning' to spanish", the agent would respond with help text instead of performing the actual translation.

## Root Cause

The A2A endpoint (`/a2a/agent/multilingoAgent`) was only checking for the `content` field when extracting user messages from the request:

```python
# OLD CODE (only checked 'content')
for msg in reversed(messages):
    if msg.get("role") == "user":
        user_message = msg.get("content", "")
        break
```

However, Telex.im and other A2A clients may send messages in different formats:
1. Standard format: `{"role": "user", "content": "..."}`
2. Alternative format: `{"role": "user", "text": "..."}`
3. Parts format: `{"role": "user", "parts": [{"kind": "text", "text": "..."}]}`

When the message was sent with the `text` field or `parts` format, the extraction would fail, resulting in an empty `user_message`. The code would then default to "help", causing the agent to return help text instead of processing the actual request.

## Solution

Updated the message extraction logic to support all three message formats:

```python
# NEW CODE (supports multiple formats)
for msg in reversed(messages):
    if msg.get("role") == "user":
        # Try multiple message formats:
        # 1. Standard: {"role": "user", "content": "..."}
        # 2. Alternative: {"role": "user", "text": "..."}
        # 3. Parts format: {"role": "user", "parts": [{"kind": "text", "text": "..."}]}
        user_message = msg.get("content") or msg.get("text")
        
        # Check parts format if content/text not found
        if not user_message and "parts" in msg:
            parts = msg.get("parts", [])
            for part in parts:
                if part.get("kind") == "text" and part.get("text"):
                    user_message = part.get("text")
                    break
        
        if user_message:
            break
```

## Changes Made

### File: `app/main.py`

1. **Added logging import** (line 17):
   ```python
   import logging
   ```

2. **Created logger instance** (line 56):
   ```python
   logger = logging.getLogger(__name__)
   ```

3. **Updated message extraction** (lines 1134-1149):
   - Now checks `content`, `text`, and `parts` fields
   - Supports all common A2A message formats
   - Added logging for debugging

4. **Added debug logging** (line 1156):
   ```python
   logger.info(f"A2A: Extracted user message: '{user_message}'")
   ```

## Testing

All message formats have been tested and verified:

✅ **Standard format (content field)**
```json
{
  "messages": [{"role": "user", "content": "translate 'good morning' to spanish"}]
}
```
Result: `good morning → buen día`

✅ **Alternative format (text field)**
```json
{
  "messages": [{"role": "user", "text": "translate 'hello' to french"}]
}
```
Result: `hello → Bonjour`

✅ **Parts format (Mastra style)**
```json
{
  "messages": [{
    "role": "user",
    "parts": [{"kind": "text", "text": "what language is 'bonjour'?"}]
  }]
}
```
Result: `'bonjour' is French (fr)`

## Deployment

The fix is backward compatible and requires no configuration changes. Simply deploy the updated code:

```bash
git add app/main.py
git commit -m "Fix A2A message extraction to support multiple formats"
git push
```

## Impact

- ✅ Fixes translation requests from Telex.im
- ✅ Supports multiple A2A message formats
- ✅ Backward compatible with existing integrations
- ✅ Improved debugging with logging
- ✅ No breaking changes

## Related Files

- `app/main.py` - A2A endpoint implementation
- `app/chat_handler.py` - Message processing logic (unchanged)
- `JSONRPC_UPDATE.md` - A2A protocol documentation

## Status

✅ **Fixed and tested**  
✅ **Ready for deployment**  
✅ **All tests passing**

---

*Fixed: November 7, 2025*  
*Issue: A2A agent not responding to translation requests*  
*Solution: Support multiple message format standards*
