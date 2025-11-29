# ShareBot - Complete Usage Guide

## Overview

ShareBot is a production-ready financial chatbot for Indian stock markets with intelligent tool selection, LLM processing, conversation memory, and streaming responses.

## Features

✅ **Two Intelligent Tools:**
- `get_stock_data` - Real-time stock data via yfinance
- `get_financial_insights` - AI-powered research via Tavily + Groq

✅ **Smart Fallback Mechanism:**
- Tries real-time data first
- Automatically falls back to AI research if needed

✅ **Adaptive Response Length:**
- **Short** (2-4 lines) - for simple queries like "price of TCS"
- **Normal** (50-100 words) - for general queries
- **Detailed** (200-400 words) - for analysis requests

✅ **Conversation Memory:**
- Buffer memory keeps last 10 conversation turns
- Maintains context across queries

✅ **Streaming Support:**
- Real-time response streaming for better UX
- Both regular and streaming endpoints

✅ **Markdown Formatted:**
- Clean, readable responses with proper formatting

---

## Installation

```bash
pip install groq tavily-python yfinance fastapi uvicorn python-dotenv
```

## Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

## Usage

### 1. Basic Usage (Python)

```python
from sharebot.main_sharebot import ShareBot

# Create instance
bot = ShareBot()

# Regular response
response = bot.chat("What is the price of TCS?")
print(response)

# Streaming response
for chunk in bot.chat_stream("Explain TCS performance in detail"):
    print(chunk, end="", flush=True)

# Clear memory
bot.clear_memory()

# Get metrics
metrics = bot.get_metrics()
print(metrics)
```

### 2. FastAPI Integration

#### Start the Server

```bash
python src/sharebot/fastapi_example.py
```

Server runs on: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

#### API Endpoints

**1. Regular Chat (POST /chat)**

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current price of TCS?",
    "session_id": "user123"
  }'
```

Response:
```json
{
  "response": "**TCS Current Price**: ₹3,245.50 🔺 +1.2%\n- Day Range: ₹3,200 - ₹3,260\n- Volume: 2.5M",
  "session_id": "user123"
}
```

**2. Streaming Chat (POST /chat/stream)**

```bash
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain TCS performance in detail",
    "session_id": "user123"
  }'
```

Returns streaming response chunks in real-time.

**3. Clear Memory (POST /clear-memory)**

```bash
curl -X POST "http://localhost:8000/clear-memory"
```

**4. Get Metrics (GET /metrics)**

```bash
curl "http://localhost:8000/metrics"
```

---

## Response Length Examples

### Short Response
**Query:** "What is the price of TCS?"

**Response:**
```markdown
**TCS Current Price**: ₹3,245.50 🔺 +1.2%
- Day Range: ₹3,200 - ₹3,260
- Volume: 2.5M
```

### Normal Response
**Query:** "Tell me about Reliance stock"

**Response:**
```markdown
**Reliance Industries** is currently trading at ₹2,450.30, up 0.8% today.

**Key Highlights:**
- Strong performance in the energy sector
- Day Range: ₹2,430 - ₹2,465
- Market Cap: ₹16.5 Lakh Crore
- Volume: 5.2M shares

The stock is showing positive momentum with steady trading volume.
```

### Detailed Response
**Query:** "Explain in detail the IT sector performance"

**Response:**
```markdown
## IT Sector Performance Analysis

### Summary
The Indian IT sector has shown resilient performance in Q3 2024, with major players like TCS, Infosys, and Wipro reporting steady growth despite global economic headwinds.

### Detailed Analysis
**Key Metrics:**
- Sector average growth: +12.5% YoY
- TCS leads with ₹3,245.50 (+15.2%)
- Infosys at ₹1,450.20 (+10.8%)
- HCL Tech at ₹1,250.30 (+8.5%)

**Market Drivers:**
1. Strong demand from BFSI sector
2. Digital transformation projects
3. Cloud migration initiatives
4. AI/ML adoption

### Key Insights
- Deal pipeline remains robust
- Margin pressures from wage hikes
- Attrition rates stabilizing
- Strong order book visibility

### Recommendations
Investors with medium to long-term horizon may consider accumulating quality IT stocks on dips. Focus on companies with strong digital capabilities and diversified client base.
```

---

## Architecture

```
User Query
    ↓
ShareBot (main_sharebot.py)
    ↓
MarketAgent (share_agent.py)
    ↓
├─→ get_stock_data (yfinance) ──→ Success ──→ Return
│                                      ↓
│                                    Fail/Insufficient
│                                      ↓
└─→ get_financial_insights (Tavily + Groq) ──→ Return
    ↓
LLM Processing (Groq)
    ↓
Markdown Response (Regular or Streaming)
```

---

## File Structure

```
src/sharebot/
├── tools/
│   └── market_tools.py          # Two market tools
├── agent/
│   └── share_agent.py           # MarketAgent with fallback
├── main_sharebot.py             # Main ShareBot class
├── fastapi_example.py           # FastAPI integration
└── test_streaming.py            # Streaming test script
```

---

## Advanced Features

### Session-Based Memory (Future Enhancement)

```python
# You can extend ShareBot to support session-based memory
sessions = {}

def get_bot_for_session(session_id: str) -> ShareBot:
    if session_id not in sessions:
        sessions[session_id] = ShareBot()
    return sessions[session_id]

# Usage
bot = get_bot_for_session("user123")
response = bot.chat("What is TCS price?")
```

### Custom Configuration

```python
bot = ShareBot(
    model="llama-3.3-70b-versatile",  # Groq model
    max_memory=20,                     # Keep 20 turns
    temperature=0.5                    # Higher creativity
)
```

---

## Testing

### Run Tests

```bash
# Test basic functionality
python src/sharebot/main_sharebot.py

# Test streaming
python src/sharebot/test_streaming.py

# Test agent
python src/sharebot/agent/share_agent.py

# Test tools
python src/sharebot/tools/market_tools.py
```

---

## Performance Metrics

Get real-time metrics:

```python
metrics = bot.get_metrics()
print(metrics)
```

Output:
```python
{
    'stock_data_calls': 5,
    'financial_insights_calls': 3,
    'fallback_triggered': 1,
    'errors': 0,
    'total_calls': 8,
    'fallback_rate': 0.2,
    'memory_size': 6,
    'max_memory': 10
}
```

---

## Error Handling

ShareBot handles errors gracefully:

- **Invalid symbol**: Falls back to AI research
- **API errors**: Returns user-friendly error messages
- **Rate limits**: Automatic retry with exponential backoff
- **Empty responses**: Validates and handles appropriately

---

## Best Practices

1. **Use streaming for long responses** - Better UX for detailed analysis
2. **Clear memory periodically** - Prevents context bleeding
3. **Monitor metrics** - Track performance and fallback rates
4. **Set appropriate response length** - Use keywords to guide response size
5. **Handle sessions** - Implement session-based memory for multi-user scenarios

---

## Troubleshooting

### Issue: "GROQ_API_KEY not found"
**Solution:** Set the environment variable in `.env` file

### Issue: "Tavily API key not configured"
**Solution:** Add `TAVILY_API_KEY` to `.env` file

### Issue: Slow responses
**Solution:** 
- Use streaming for better perceived performance
- Check your internet connection
- Verify API rate limits

### Issue: Incorrect stock data
**Solution:**
- Verify symbol format (e.g., "TCS", "RELIANCE")
- Check if market is open
- Try alternative query phrasing

---

## License

This project is part of KiteInfi platform.

---

## Support

For issues or questions, refer to the main project documentation.
