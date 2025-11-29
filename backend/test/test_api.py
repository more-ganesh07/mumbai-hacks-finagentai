"""
API Test Script for Stock Chatbot
Run: python test_api.py
Make sure FastAPI server is running: python main.py
"""
import requests
import json
import time

API_URL = "http://localhost:8000/chatbot_query"
HEALTH_URL = "http://localhost:8000/health"

TEST_QUESTIONS = [
    "What is the price of TCS?",
    "Tell me about Reliance",
    "Analyze INFY stock",
    "Latest news about TCS, 3",
    "What's the market overview?",
    "Track portfolio: TCS:5, Reliance:3",
]

def test_api():
    """Test API endpoints"""
    print("=" * 70)
    print("🧪 Stock Chatbot API Test Suite")
    print("=" * 70)
    
    # Health check
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Make sure server is running: python main.py")
        return
    
    print("\n" + "=" * 70)
    print("📝 Testing Chatbot Queries")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        try:
            print(f"\n{i}. ❓ Q: {question}")
            start = time.time()
            
            response = requests.post(
                API_URL,
                json={"user_query": question},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "")
                if answer and not answer.startswith("❌"):
                    print(f"   ✅ Response ({elapsed:.2f}s): {answer[:150]}...")
                    passed += 1
                else:
                    print(f"   ❌ Error in response: {answer}")
                    failed += 1
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print(f"Total Questions: {len(TEST_QUESTIONS)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(TEST_QUESTIONS))*100:.1f}%")
    print("=" * 70)

if __name__ == "__main__":
    test_api()

