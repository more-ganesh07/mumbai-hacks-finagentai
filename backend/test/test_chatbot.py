"""
Quick Test Script for Stock Chatbot
Run: python test_chatbot.py
"""
from src.sharebot.main_sharebot import StockChatbot
import time

# Test questions organized by category
TEST_QUESTIONS = {
    "Basic Price": [
        "What is the price of TCS?",
        "TCS price",
        "Show me INFY stock price",
    ],
    "Company Info": [
        "Tell me about TCS",
        "What does Reliance do?",
    ],
    "Analysis": [
        "Analyze TCS stock",
        "Technical analysis of Reliance",
    ],
    "News": [
        "Latest news about TCS",
        "Show me 3 news articles on Reliance",
    ],
    "Market": [
        "What's the market overview?",
        "Show me NIFTY and SENSEX",
    ],
    "Portfolio": [
        "Track my portfolio: TCS:5, Reliance:3, Infosys:4",
    ],
    "Complex": [
        "Complete analysis of TCS - price, news, and analysis",
        "Compare TCS and Infosys",
    ],
}

def test_chatbot():
    """Run test questions"""
    print("=" * 70)
    print("🧪 Stock Chatbot Test Suite")
    print("=" * 70)
    
    try:
        chatbot = StockChatbot()
        print("✅ Chatbot initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}\n")
        return
    
    total_questions = sum(len(questions) for questions in TEST_QUESTIONS.values())
    passed = 0
    failed = 0
    
    for category, questions in TEST_QUESTIONS.items():
        print(f"\n📂 Testing: {category}")
        print("-" * 70)
        
        for question in questions:
            try:
                print(f"\n❓ Q: {question}")
                start = time.time()
                response = chatbot.chat(question)
                elapsed = time.time() - start
                
                if response and not response.startswith("❌"):
                    print(f"✅ Response ({elapsed:.2f}s): {response[:100]}...")
                    passed += 1
                else:
                    print(f"❌ Error: {response}")
                    failed += 1
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print(f"Total Questions: {total_questions}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total_questions)*100:.1f}%")
    
    # Metrics
    metrics = chatbot.get_metrics()
    print(f"\n📈 Performance Metrics:")
    print(f"  Avg Response Time: {metrics.get('avg_response_time', 0):.2f}s")
    print(f"  Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.1%}")
    print(f"  Total LLM Calls: {metrics.get('llm_calls', 0)}")
    print("=" * 70)

if __name__ == "__main__":
    test_chatbot()

