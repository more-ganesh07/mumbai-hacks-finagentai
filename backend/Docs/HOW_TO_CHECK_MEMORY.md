# 🧠 How to Check Memory

## Methods to Check Memory

---

## 1. **Via API Endpoint** (Recommended)

### Get Memory Statistics & Content
```bash
# Get memory info
curl http://localhost:8000/memory
```

**Response:**
```json
{
  "summary": {
    "total_messages": 6,
    "user_messages": 3,
    "assistant_messages": 3,
    "memory_limit": 20
  },
  "messages": [
    {"role": "user", "content": "What is the price of TCS?"},
    {"role": "assistant", "content": "TCS current price is ₹..."},
    ...
  ],
  "total_exchanges": 3
}
```

### Clear Memory
```bash
curl -X POST http://localhost:8000/clear-memory
```

---

## 2. **Via Python Code**

### Check Memory Summary
```python
from src.sharebot.main_sharebot import StockChatbot

chatbot = StockChatbot()

# Get memory statistics
memory_summary = chatbot.get_memory_summary()
print(memory_summary)
# Output: {'total_messages': 6, 'user_messages': 3, ...}

# Get full memory content
print(chatbot.memory)
# Output: [{'role': 'user', 'content': '...'}, ...]
```

### View Full Memory
```python
# Pretty print memory
for i, msg in enumerate(chatbot.memory, 1):
    print(f"{i}. [{msg['role']}]: {msg['content'][:100]}...")
```

### Clear Memory
```python
chatbot.clear_memory()
print("Memory cleared!")
```

---

## 3. **Via Metrics** (Includes Memory Info)

```python
metrics = chatbot.get_metrics()
print(metrics['memory'])
# Output: {'total_messages': 6, 'user_messages': 3, ...}
```

---

## 4. **Test Memory Persistence**

### Step-by-Step Test:
```python
from src.sharebot.main_sharebot import StockChatbot

chatbot = StockChatbot()

# Query 1
chatbot.chat("What is the price of TCS?")
print(f"Memory after Q1: {len(chatbot.memory)} messages")

# Query 2 (should remember TCS)
chatbot.chat("What about its company information?")
print(f"Memory after Q2: {len(chatbot.memory)} messages")

# Check memory
print(chatbot.get_memory_summary())
```

---

## 5. **Quick Memory Check Script**

```python
"""
Quick memory checker
Run: python check_memory.py
"""
from src.sharebot.main_sharebot import StockChatbot

chatbot = StockChatbot()

# Check current memory
print("=" * 70)
print("📊 Memory Status")
print("=" * 70)

summary = chatbot.get_memory_summary()
print(f"Total Messages: {summary['total_messages']}")
print(f"User Messages: {summary['user_messages']}")
print(f"Assistant Messages: {summary['assistant_messages']}")
print(f"Memory Limit: {summary['memory_limit']}")

print("\n" + "=" * 70)
print("💬 Conversation History")
print("=" * 70)

if chatbot.memory:
    for i, msg in enumerate(chatbot.memory, 1):
        role = msg['role'].upper()
        content = msg['content'][:150] + "..." if len(msg['content']) > 150 else msg['content']
        print(f"\n{i}. [{role}]")
        print(f"   {content}")
else:
    print("No conversation history yet.")

print("\n" + "=" * 70)
```

---

## 📊 Memory Structure

Memory is stored as a list of message dictionaries:
```python
[
    {"role": "user", "content": "What is the price of TCS?"},
    {"role": "assistant", "content": "TCS current price is ₹3500..."},
    {"role": "user", "content": "What about Reliance?"},
    {"role": "assistant", "content": "Reliance current price is ₹2500..."},
    ...
]
```

---

## 🔍 Memory Features

### Auto-Compression
- Memory auto-compresses when it exceeds `max_memory * 2` (default: 20 messages)
- Old messages are summarized, recent ones kept

### Memory Limit
- Default: 10 exchanges (20 messages)
- Configurable via `MAX_MEMORY` env variable

### Memory Persistence
- Memory persists across queries in the same chatbot instance
- Cleared when chatbot instance is recreated or `clear_memory()` is called

---

## 🧪 Test Memory

```bash
# 1. Start server
python main.py

# 2. Make some queries
curl -X POST http://localhost:8000/chatbot_query \
  -H "Content-Type: application/json" \
  -d '{"user_query": "What is the price of TCS?"}'

curl -X POST http://localhost:8000/chatbot_query \
  -H "Content-Type: application/json" \
  -d '{"user_query": "What about its company info?"}'

# 3. Check memory
curl http://localhost:8000/memory
```

---

## 💡 Tips

1. **Memory persists** across queries in the same session
2. **Auto-compression** happens when memory gets too large
3. **Check regularly** to see if memory is working correctly
4. **Clear memory** if you want to start fresh
5. **Memory limit** prevents context overflow

---

**Now you can easily check and manage memory! 🧠**

