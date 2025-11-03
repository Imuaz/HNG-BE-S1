# Telex AI Work Colleague - Setup Guide (Mastra A2A Format)

## 📋 Overview

This guide helps you configure MultiLingo Agent as an AI Work Colleague on Telex.im using the Mastra A2A workflow format.

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Get Your Railway URL

Your API should be deployed at:

```
https://your-app-name.up.railway.app
```

Verify it's working:

```bash
curl https://your-app-name.up.railway.app/health
```

### Step 2: Verify Discovery (optional but recommended)

Your agent card is available at:

```
GET https://your-app-name.up.railway.app/.well-known/agent.json
```

Test:

```bash
curl -s https://your-app-name.up.railway.app/.well-known/agent.json | jq
```

### Step 3: Update the Workflow JSON

Open `telex-multilingo-workflow.json` and replace:

```json
"url": "https://your-railway-app.up.railway.app/a2a/agent/multilingoAgent"
```

With your actual Railway URL:

```json
"url": "https://string-analyzer-production-abc123.up.railway.app/a2a/agent/multilingoAgent"
```

### Step 4: Create AI Work Colleague on Telex

1. Go to **Telex.im dashboard**
2. Click **"Create AI Work Colleague"** or **"New Workflow"**
3. Enter basic details:
   - **Name:** `multilingo_agent`
   - **Category:** `productivity`
   - **Description:** "An AI translation agent that supports 25+ languages"
4. **Upload/paste the JSON workflow configuration**
5. Click **"Activate"** to enable the workflow

### Step 5: Test Your Agent

Send these test messages to your agent on Telex:

```
Test 1: "hello"
Expected: Greeting response

Test 2: "Translate 'hello world' to Spanish"
Expected: "Hola Mundo" translation with analysis

Test 3: "What language is 'bonjour'?"
Expected: "French" detection

Test 4: "Is 'racecar' a palindrome?"
Expected: "Yes" with string analysis

Test 5: "help"
Expected: Help menu with commands
```

---

## 📝 Workflow Configuration Explained

### JSON Structure

```json
{
  "active": true, // Enable the workflow
  "category": "productivity", // Workflow category
  "description": "Short description",
  "id": "multilingo_translation_agent", // Unique identifier
  "long_description": "Detailed system prompt for the agent",
  "name": "multilingo_agent", // Agent name (lowercase, no spaces)
  "nodes": [
    // A2A nodes configuration
    {
      "id": "multilingo_translation_agent",
      "name": "MultiLingo Translation Agent",
      "type": "a2a/mastra-a2a-node",
      "url": "https://your-app.up.railway.app/a2a/agent/multilingoAgent"
    }
  ]
}
```

### Key Fields

**`active`**: Set to `true` to enable the agent

**`category`**: Choose from:

- `productivity` (recommended for MultiLingo)
- `utilities`
- `entertainment`
- `education`

**`long_description`**: This is your **system prompt**. It tells the agent its role and capabilities. Our agent knows it should:

- Translate text between languages
- Detect languages automatically
- Analyze string properties
- Respond in a friendly manner

**`url`**: Your A2A endpoint. MUST be:

```
https://your-railway-app.up.railway.app/a2a/agent/multilingoAgent
```

---

## 🔧 A2A Endpoint Details

### Endpoint URLs

```
GET  https://your-app.up.railway.app/a2a/agent/multilingoAgent    # agent info
POST https://your-app.up.railway.app/a2a/agent/multilingoAgent    # chat/messages
```

### Request Format (from Telex)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Translate 'hello' to Spanish"
    }
  ],
  "userId": "user_12345",
  "context": {}
}
```

### Response Format (to Telex)

```json
{
  "role": "assistant",
  "content": "✅ **Translation Complete!**\n\n**Original:** hello\n**Spanish:** hola",
  "metadata": {
    "intent": "translate",
    "action": "translated_to_spanish",
    "success": true,
    "data": {
      "original": "hello",
      "translation": "hola"
    }
  }
}
```

---

## ✅ Testing Checklist

Before activating, verify:

### 1. Test A2A Endpoint Directly

```bash
curl -X POST "https://your-app.up.railway.app/a2a/agent/multilingoAgent" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "hello"}
    ],
    "userId": "test_user"
  }'
```

**Expected Response:**

```json
{
  "role": "assistant",
  "content": "👋 Hello! I'm MultiLingo Agent! ...",
  "metadata": {
    "intent": "greeting",
    "success": true
  }
}
```

### 2. Test Translation

```bash
curl -X POST "https://your-app.up.railway.app/a2a/agent/multilingoAgent" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Translate hello to Spanish"}
    ],
    "userId": "test_user"
  }'
```

### 3. Verify Database Storage

After testing, check your database:

```bash
# Connect to Neon and run:
SELECT * FROM telex_conversations ORDER BY created_at DESC LIMIT 5;
```

You should see your test conversations stored!

---

## 🐛 Troubleshooting

### Issue 1: Agent Not Responding

**Symptom:** No response when messaging agent on Telex

**Solutions:**

1. **Check Railway logs:**

   - Go to Railway dashboard
   - View deployment logs
   - Look for incoming POST requests to `/a2a/agent/multilingoAgent`

2. **Verify workflow is active:**

   - In Telex dashboard, check workflow status
   - Should show "Active" or enabled toggle

3. **Test endpoint manually:**
   ```bash
   curl -X POST "https://your-app.up.railway.app/a2a/agent/multilingoAgent" \
     -H "Content-Type: application/json" \
     -d '{"messages":[{"role":"user","content":"test"}]}'
   ```

### Issue 2: Translation Errors

**Symptom:** Agent responds but translations fail

**Solutions:**

1. **Test translator locally:**

   ```bash
   python test_translator.py
   ```

2. **Check deep-translator is installed:**

   ```bash
   pip list | grep deep-translator
   # Should show: deep-translator==1.11.4
   ```

3. **Verify internet access from Railway**
   (needed for translation API)

### Issue 3: Database Connection Errors

**Symptom:** Agent responds but doesn't remember conversations

**Solutions:**

1. **Verify DATABASE_URL in Railway:**

   - Go to Railway dashboard
   - Check environment variables
   - Should have `DATABASE_URL` set

2. **Test database connection:**

   ```bash
   python -c "from app.database import engine; print(engine.url)"
   ```

3. **Verify tables exist:**
   ```bash
   python create_tables.py
   ```

### Issue 4: "404 Not Found" on A2A Endpoint

**Symptom:** Telex can't reach your endpoint

**Solutions:**

1. **Verify endpoint exists:**
   Visit: `https://your-app.up.railway.app/docs`
   Look for: `POST /a2a/agent/multilingoAgent`

2. **Check Railway deployment status:**

   - Make sure deployment succeeded
   - Check for any build errors

3. **Verify URL in JSON is correct:**
   - Must include full path: `/a2a/agent/multilingoAgent`
   - Check for typos in domain name

---

## 📊 Monitoring Your Agent

### View Logs in Real-Time

**Railway Dashboard:**

```
Project → Deployments → Latest Deployment → View Logs
```

Look for:

- `POST /a2a/agent/multilingoAgent` - Incoming requests
- `INFO:app.translator:Translating from...` - Translation activity
- `INFO:app.translator:Translation successful` - Successful translations

### Check Database Activity

Connect to Neon and run:

```sql
-- Recent conversations
SELECT
    telex_user_id,
    user_message,
    detected_intent,
    success,
    created_at
FROM telex_conversations
ORDER BY created_at DESC
LIMIT 20;

-- Translation statistics
SELECT
    target_language,
    COUNT(*) as count
FROM translations
GROUP BY target_language
ORDER BY count DESC;

-- Success rate
SELECT
    success,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM telex_conversations
GROUP BY success;
```

### API Health Check

```bash
# Quick health check
curl https://your-app.up.railway.app/health

# Detailed API info
curl https://your-app.up.railway.app/
```

---

## 🎯 Advanced Configuration

### Custom System Prompt

Edit the `long_description` field to customize your agent's behavior:

```json
{
  "long_description": "You are MultiLingo, a translation expert. Your tone is professional and concise. Always provide translations with confidence scores. When detecting languages, explain why you're confident in your detection."
}
```

### Adding Context Awareness

The agent automatically tracks conversation history. To customize:

Edit `app/chat_handler.py`:

```python
def process_chat_message(message: str, context: Optional[Dict] = None):
    # Access previous messages
    if context and context.get("history"):
        previous_messages = context["history"]
        # Use context to provide better responses
```

### Rate Limiting

Add rate limiting to prevent abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/a2a/agent/multilingoAgent")
@limiter.limit("60/minute")
async def a2a_multilingo_agent(...):
    # Handler code
```

---

## 📚 Common Use Cases

### Use Case 1: Customer Support (Multilingual)

**Customer:** "¿Cómo puedo devolver mi producto?"

**Agent:**

1. Detects Spanish
2. Translates to English for support team
3. Translates response back to Spanish

### Use Case 2: Content Localization

**User:** "Translate this product description to French, German, and Spanish"

**Agent:**

1. Processes multi-language request
2. Returns all three translations
3. Stores for future reference

### Use Case 3: Language Learning

**Student:** "How do you say 'good morning' in 5 different languages?"

**Agent:**

1. Translates to 5 languages
2. Shows pronunciation guide
3. Provides cultural context

---

## 🔄 Updating Your Agent

To update the agent configuration:

1. **Edit your local JSON file**
2. **Test changes locally** first
3. **Go to Telex dashboard**
4. **Edit your workflow**
5. **Upload updated JSON**
6. **Save and test**

Changes take effect immediately!

---

## 📖 Additional Resources

- **Live API Docs:** https://your-app.up.railway.app/docs
- **GitHub Repository:** [Your Repo URL]
- **Blog Post:** [Your Blog URL]
- **Telex Documentation:** https://docs.telex.im
- **Mastra Documentation:** https://mastra.ai/docs
- **Railway Documentation:** https://docs.railway.app

---

## 🆘 Still Having Issues?

1. **Check Railway logs** - Most issues show up here
2. **Test endpoints directly** - Use `/docs` for interactive testing
3. **Verify database** - Check if data is being stored
4. **Review this guide** - Follow each step carefully
5. **Contact support** - Telex.im support or open GitHub issue

---

## ✨ Success Indicators

Your agent is working correctly when:

- ✅ Responds to messages on Telex within 1-2 seconds
- ✅ Translations are accurate
- ✅ Remembers conversation context
- ✅ Stores data in database
- ✅ Shows up in Railway logs
- ✅ Handles errors gracefully
- ✅ Provides formatted responses with emoji

---

**Your MultiLingo Agent is now ready to serve users on Telex.im! 🎉🌍**

Test it thoroughly, monitor the logs, and enjoy your AI translation colleague!

---

## 🚀 Quick Setup

### Step 1: Get Your Railway URL

Your API should be deployed at:

```
https://your-app-name.up.railway.app
```

Verify it's working:

```bash
curl https://your-app-name.up.railway.app/health
```

### Step 2: Choose the Right Configuration File

Depending on Telex's current implementation, use:

1. **`telex-multilingo-workflow.json`** - Full featured workflow
2. **`telex-workflow-simple.json`** - Minimal configuration
3. **`telex-a2a-protocol.json`** - A2A protocol standard
4. **`mastra-config.json`** - If using Mastra framework

### Step 3: Update the Configuration

Replace `https://your-railway-app.up.railway.app` with your actual Railway URL in the chosen JSON file.

**Example:**

```json
{
  "webhook": {
    "url": "https://string-analyzer-production-abc123.up.railway.app/webhook/telex"
  }
}
```

### Step 4: Create AI Work Colleague on Telex

1. Go to Telex.im dashboard
2. Click "Create AI Work Colleague" or "New Agent"
3. Enter agent details:
   - **Name:** MultiLingo Agent
   - **Description:** AI translation assistant (25+ languages)
   - **Icon:** 🌍 or 🤖
4. Upload/paste your JSON configuration
5. Save and activate

### Step 5: Test the Integration

Send test messages to your agent:

```
Test 1: "help"
Test 2: "Translate 'hello world' to Spanish"
Test 3: "What language is 'bonjour'?"
Test 4: "Is 'racecar' a palindrome?"
```

---

## 🔧 Configuration Details

### Webhook Endpoint

Your agent uses this endpoint to receive webhook messages (if you choose to wire Telex webhooks):

```
POST https://your-app.up.railway.app/webhook/telex
```

**Expected Request Format:**

```json
{
  "user_id": "user_12345",
  "message": "Translate 'hello' to Spanish",
  "conversation_id": "conv_67890",
  "message_id": "msg_11111",
  "timestamp": "2025-11-03T10:00:00Z"
}
```

**Response Format:**

```json
{
  "message": "✅ **Translation Complete!**\n\n**Original:** hello\n**Spanish:** hola",
  "success": true,
  "data": {
    "original": "hello",
    "translation": "hola",
    "source_language": "en",
    "target_language": "es"
  }
}
```

---

## 🔐 Authentication

Telex does not require an API key for A2A calls. Keep your endpoints public for Telex to reach them. If you want to protect webhooks, add a shared secret header (see example under Advanced Configuration).

---

## 📝 Supported Commands

Your agent understands these natural language patterns:

### Translation

```
"Translate 'text' to language"
"How do you say 'text' in language?"
"What is 'text' in language?"
"'text' in language"
```

### Language Detection

```
"What language is 'text'?"
"Detect language of 'text'"
"Identify 'text'"
```

### String Analysis

```
"Analyze 'text'"
"Is 'text' a palindrome?"
"Check 'text'"
```

### Help & Info

```
"help"
"what can you do?"
"list languages"
```

---

## 🌍 Supported Languages (25+)

English (en), Spanish (es), French (fr), German (de), Italian (it), Portuguese (pt), Russian (ru), Japanese (ja), Chinese (zh-cn), Korean (ko), Arabic (ar), Hindi (hi), Dutch (nl), Turkish (tr), Swedish (sv), Polish (pl), Vietnamese (vi), Thai (th), Greek (el), Czech (cs), Danish (da), Finnish (fi), Norwegian (no), Romanian (ro), Ukrainian (uk)

---

## 🐛 Troubleshooting

### Agent Not Responding

**Check 1: Verify webhook URL**

```bash
curl -X POST "https://your-app.up.railway.app/webhook/telex" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "hello",
    "conversation_id": "test_conv"
  }'
```

**Check 2: Review Railway logs**

- Go to Railway dashboard
- View deployment logs
- Look for incoming webhook requests

**Check 3: Test direct API**
Visit: `https://your-app.up.railway.app/docs`
Try the `/agents/multilingo/chat` endpoint

### Translation Fails

**Check 1: Test translator locally**

```bash
python test_translator.py
```

**Check 2: Verify dependencies**

```bash
pip list | grep -i translator
# Should show: deep-translator==1.11.4
```

### Database Connection Issues

**Check 1: Verify DATABASE_URL**

- Go to Railway dashboard
- Check environment variables
- Verify Neon database is active

**Check 2: Test connection**

```bash
python -c "from app.database import engine; print(engine.url)"
```

---

## 🔄 Updating the Configuration

If you need to update the workflow:

1. Edit your JSON file with new settings
2. Go to Telex dashboard
3. Find your AI Work Colleague
4. Click "Edit Configuration"
5. Upload/paste updated JSON
6. Save changes

Changes take effect immediately!

---

## 📊 Monitoring & Analytics

### Check Request Logs

**Railway Dashboard:**

- View real-time logs
- Monitor response times
- Track error rates

**API Endpoint:**

```bash
# Check health
curl https://your-app.up.railway.app/health

# View recent translations
curl https://your-app.up.railway.app/translations
```

### Database Analytics

Connect to your Neon database to query:

```sql
-- Total translations
SELECT COUNT(*) FROM translations;

-- Most popular language pairs
SELECT target_language, COUNT(*) as count
FROM translations
GROUP BY target_language
ORDER BY count DESC
LIMIT 10;

-- Recent conversations
SELECT * FROM telex_conversations
ORDER BY created_at DESC
LIMIT 20;
```

---

## 🚀 Advanced Configuration

### Adding Authentication

If you want to secure your webhook:

1. **Update Railway environment variables:**

```bash
WEBHOOK_SECRET=your-secret-key-here
```

2. **Update your endpoint to validate:**

```python
@app.post("/webhook/telex")
def telex_webhook(
    payload: TelexWebhookPayload,
    authorization: str = Header(None)
):
    if authorization != os.getenv("WEBHOOK_SECRET"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    # ... rest of handler
```

3. **Update JSON config:**

```json
{
  "webhook": {
    "url": "https://your-app.up.railway.app/webhook/telex",
    "headers": {
      "Authorization": "your-secret-key-here"
    }
  }
}
```

### Custom Response Formatting

Modify response formatting in `app/chat_handler.py`:

```python
# Add custom formatting
def format_response(text: str, use_emoji: bool = True) -> str:
    if use_emoji:
        text = text.replace("Translation", "🌍 Translation")
        text = text.replace("Language", "🔍 Language")
    return text
```

### Rate Limiting

Add rate limiting to prevent abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/webhook/telex")
@limiter.limit("60/minute")
def telex_webhook(...):
    # Handler code
```

---

## 📚 Additional Resources

- **API Documentation:** https://your-app.up.railway.app/docs
- **GitHub Repository:** [Your Repo URL]
- **Blog Post:** [Your Blog URL]
- **Telex Documentation:** https://docs.telex.im
- **Railway Documentation:** https://docs.railway.app

---

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs** - Railway dashboard shows all requests/errors
2. **Test endpoints directly** - Use `/docs` for interactive testing
3. **Review database** - Check if data is being stored correctly
4. **Contact support** - Telex.im support or open GitHub issue

---

## ✅ Verification Checklist

Before going live, verify:

- [ ] Railway deployment is active and healthy
- [ ] Database connection working (check `/health`)
- [ ] Webhook endpoint responds correctly
- [ ] JSON configuration uploaded to Telex
- [ ] Test messages work end-to-end
- [ ] Error handling works (try invalid requests)
- [ ] Logs are being captured
- [ ] Rate limiting is configured (if needed)
- [ ] Analytics are tracking correctly

---

**Your MultiLingo Agent should now be live and ready to help users on Telex.im! 🎉**

Need more help? Check the full documentation or reach out!
