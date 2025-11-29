# 🧪 Test Questions for Stock Chatbot

## 📊 Basic Price Queries

1. **Simple price check**
   - "What is the price of TCS?"
   - "TCS price"
   - "Show me INFY stock price"

2. **Multiple stocks**
   - "What are the prices of TCS and Reliance?"
   - "Price of HDFC Bank and ICICI Bank"

3. **Different formats**
   - "What's the current price of Infosys?"
   - "Give me Wipro stock quote"
   - "RELIANCE.NS price"

---

## 🏢 Company Information

4. **Basic company info**
   - "Tell me about TCS"
   - "What does Reliance do?"
   - "Company information for Infosys"

5. **Detailed company research**
   - "Explain TCS company in detail"
   - "Give me full analysis of Reliance Industries"
   - "Deep dive into HDFC Bank"

---

## 📈 Technical Analysis

6. **Stock analysis**
   - "Analyze TCS stock"
   - "Technical analysis of Reliance"
   - "Stock analysis for INFY, 6 months"

7. **Historical data**
   - "Show me TCS history for last 3 months"
   - "Historical data for Reliance, 1 year"
   - "TCS price history, 6mo, 1d"

---

## 📰 News & Updates

8. **Stock news**
   - "Latest news about TCS"
   - "Show me 5 news articles on Reliance"
   - "What's happening with Infosys?"

---

## 🌐 Market Overview

9. **Market indices**
   - "What's the market overview?"
   - "Show me NIFTY and SENSEX"
   - "Current market status"

---

## 💼 Portfolio Tracking

10. **Portfolio queries**
    - "Track my portfolio: TCS:5, Reliance:3, Infosys:4"
    - "Portfolio value: HDFC Bank:10, ICICI Bank:5"

---

## 📅 IPO & Events

11. **IPO calendar**
    - "Show me upcoming IPOs"
    - "What IPOs are coming?"
    - "IPO calendar"

12. **Dividends & splits**
    - "Dividend history of TCS"
    - "Stock splits for Reliance"
    - "Show me dividends for HDFC Bank"

---

## 🔍 Complex Queries

13. **Multi-tool queries**
    - "Analyze TCS - give me price, news, and analysis"
    - "Complete research on Reliance: price, company info, and news"
    - "Tell me everything about Infosys"

14. **Comparison queries**
    - "Compare TCS and Infosys"
    - "Which is better: HDFC Bank or ICICI Bank?"

15. **Trend queries**
    - "How has TCS performed in the last 6 months?"
    - "What's the trend for Reliance stock?"

---

## 💡 General Financial Questions

16. **Educational queries**
    - "What is a stock split?"
    - "Explain technical analysis"
    - "How do dividends work?"

17. **Market insights**
    - "What's happening in the Indian stock market?"
    - "Market trends today"
    - "Best performing stocks"

---

## 🧪 Edge Cases & Error Handling

18. **Invalid inputs**
    - "" (empty string)
    - "XYZ123" (non-existent stock)
    - "What is the price of" (incomplete query)

19. **Long queries**
    - "Tell me everything about TCS including price, company information, financials, news, analysis, dividends, splits, and compare it with Infosys"

20. **Special characters**
    - "TCS & Reliance price"
    - "What's TCS's price?"

---

## 🎯 Quick Test Suite (Top 10)

**Run these first to verify core functionality:**

1. ✅ "What is the price of TCS?"
2. ✅ "Tell me about Reliance"
3. ✅ "Analyze INFY stock"
4. ✅ "Latest news about TCS, 3"
5. ✅ "Market overview"
6. ✅ "Track portfolio: TCS:5, Reliance:3"
7. ✅ "Show me upcoming IPOs"
8. ✅ "TCS dividend history"
9. ✅ "Complete analysis of HDFC Bank"
10. ✅ "Compare TCS and Infosys"

---

## 📝 Testing Checklist

### ✅ Basic Functionality
- [ ] Price queries work
- [ ] Company info retrieved
- [ ] News fetched correctly
- [ ] Market overview shows indices

### ✅ Advanced Features
- [ ] Technical analysis works
- [ ] Portfolio tracking calculates correctly
- [ ] IPO calendar displays
- [ ] Multi-tool queries execute

### ✅ Error Handling
- [ ] Empty queries handled
- [ ] Invalid stocks show error
- [ ] Long queries processed
- [ ] Special characters handled

### ✅ Performance
- [ ] Response time < 5 seconds
- [ ] Caching works (second query faster)
- [ ] Memory maintained across queries
- [ ] No crashes on errors

---

## 🚀 How to Test

### Via API (FastAPI)
```bash
# Start server
python main.py

# Test query
curl -X POST http://localhost:8000/chatbot_query \
  -H "Content-Type: application/json" \
  -d '{"user_query": "What is the price of TCS?"}'
```

### Via CLI
```bash
python -m src.sharebot.main_sharebot
# Then type questions interactively
```

### Via Python Script
```python
from src.sharebot.main_sharebot import StockChatbot

chatbot = StockChatbot()
response = chatbot.chat("What is the price of TCS?")
print(response)
```

---

## 📊 Expected Results

### ✅ Good Responses Should:
- Be concise (80-120 words) unless detailed analysis requested
- Include ₹ symbol for prices
- Provide accurate stock data
- Use proper formatting
- Reference tool results naturally

### ❌ Bad Responses (Should Not):
- Show raw tool output
- Include "Final Answer." text
- Have repetitive headers
- Show error messages for valid queries
- Take > 10 seconds

---

## 🎯 Success Criteria

**MVP is working if:**
1. ✅ 90%+ queries return valid responses
2. ✅ Price queries work for major stocks (TCS, Reliance, INFY, etc.)
3. ✅ Multi-tool queries execute correctly
4. ✅ Error handling is graceful
5. ✅ Response time < 5 seconds average
6. ✅ Memory persists across queries
7. ✅ Caching improves performance

---

## 💡 Pro Tips

1. **Start simple**: Test basic price queries first
2. **Test incrementally**: Add complexity gradually
3. **Check logs**: Monitor for errors in logs
4. **Verify caching**: Second query should be faster
5. **Test edge cases**: Invalid inputs, empty queries
6. **Monitor metrics**: Check `chatbot.get_metrics()`

---

## 🔧 Debugging

If queries fail:
1. Check logs for errors
2. Verify API keys are set
3. Check network connectivity
4. Verify stock symbols are correct
5. Check tool execution in logs
6. Review metrics for patterns

---

**Happy Testing! 🚀**

