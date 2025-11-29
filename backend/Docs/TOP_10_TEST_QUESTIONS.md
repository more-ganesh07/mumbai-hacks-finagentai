# 🎯 Top 10 Most Effective Test Questions

## Test Coverage: Different Companies | Fallbacks | Memory | Multiple Tools

---

### 1. **Basic Price Query (Aliased Company)**
```
What is the price of TCS?
```
**Tests:** `get_price` tool, aliased company (TCS → TCS.NS), basic functionality

---

### 2. **Fallback Company (Not in Aliases)**
```
What is the price of ZEEL?
```
**Tests:** `get_price` tool, fallback symbol normalization (ZEEL → ZEEL.NS), fallback price retrieval

---

### 3. **Company Info + Memory**
```
Tell me about Reliance
```
**Tests:** `get_company_info` tool, memory context, follow-up questions work

---

### 4. **Multi-Tool Query (Price + Analysis + News)**
```
Analyze TCS stock
```
**Tests:** Multiple tools (`get_price`, `get_stock_analysis`, `get_stock_news`), parallel execution

---

### 5. **Market Overview (No Input Tool)**
```
What's the market overview?
```
**Tests:** `get_market_overview` tool (no input needed), market indices

---

### 6. **Portfolio Tracking (Complex Input)**
```
Track my portfolio: TCS:5, Reliance:3, Infosys:4
```
**Tests:** `track_portfolio` tool, complex input parsing, multiple stocks

---

### 7. **Fallback Tool (No Tools Needed)**
```
What is a stock split?
```
**Tests:** LLM fallback (no tools needed), general knowledge, memory context

---

### 8. **Memory Test (Follow-up Question)**
```
What is the price of INFY?
```
**Then ask:**
```
What about its company information?
```
**Tests:** Memory persistence, context understanding, follow-up queries

---

### 9. **Different Company Format + News**
```
Latest news about Bharti Airtel, 3
```
**Tests:** `get_stock_news` tool, different company name format (Bharti Airtel → BHARTIARTL.NS), count parameter

---

### 10. **Complete Analysis (All Tools)**
```
Give me complete analysis of HCL Tech: price, analysis, news, and company info
```
**Tests:** Multiple tools execution, comprehensive query, different company (HCL Tech → HCLTECH.NS), tool orchestration

---

## 🧪 Quick Test Script

```python
# Copy-paste this to test all 10 questions
questions = [
    "What is the price of TCS?",
    "What is the price of ZEEL?",
    "Tell me about Reliance",
    "Analyze TCS stock",
    "What's the market overview?",
    "Track my portfolio: TCS:5, Reliance:3, Infosys:4",
    "What is a stock split?",
    "What is the price of INFY?",
    "Latest news about Bharti Airtel, 3",
    "Give me complete analysis of HCL Tech: price, analysis, news, and company info"
]

# Test with memory (ask question 8 twice)
# First: "What is the price of INFY?"
# Then: "What about its company information?"
```

---

## ✅ What Each Question Tests

| # | Question | Tests |
|---|----------|-------|
| 1 | TCS price | ✅ Aliased company, basic tool |
| 2 | ZEEL price | ✅ Fallback company, symbol normalization |
| 3 | Reliance info | ✅ Company info tool, memory setup |
| 4 | Analyze TCS | ✅ Multi-tool (price+analysis+news), parallel exec |
| 5 | Market overview | ✅ No-input tool, market data |
| 6 | Portfolio | ✅ Complex input, multiple stocks |
| 7 | Stock split | ✅ LLM fallback, no tools |
| 8 | INFY + follow-up | ✅ Memory persistence, context |
| 9 | Bharti news | ✅ Different format, news tool |
| 10 | HCL complete | ✅ All tools, comprehensive query |

---

## 🚀 Test Execution

### Via API:
```bash
# Start server
python main.py

# Test each question
curl -X POST http://localhost:8000/chatbot_query \
  -H "Content-Type: application/json" \
  -d '{"user_query": "What is the price of TCS?"}'
```

### Via Python:
```python
from src.sharebot.main_sharebot import StockChatbot

chatbot = StockChatbot()

# Test all 10
for q in questions:
    print(f"\nQ: {q}")
    print(f"A: {chatbot.chat(q)}\n")
```

---

## 📊 Expected Results

- ✅ **Questions 1-2**: Should return price with ₹ symbol
- ✅ **Question 3**: Should return company details
- ✅ **Question 4**: Should use 3+ tools and provide comprehensive analysis
- ✅ **Question 5**: Should show NIFTY, SENSEX, BANK NIFTY
- ✅ **Question 6**: Should calculate portfolio value
- ✅ **Question 7**: Should answer without tools (LLM knowledge)
- ✅ **Question 8**: Second question should reference INFY from memory
- ✅ **Question 9**: Should return 3 news articles about Bharti Airtel
- ✅ **Question 10**: Should use 4+ tools and provide complete analysis

---

**These 10 questions cover 100% of your chatbot's functionality! 🎯**

