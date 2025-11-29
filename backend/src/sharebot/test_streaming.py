"""
Test script for ShareBot streaming functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sharebot.main_sharebot import ShareBot

def test_streaming():
    """Test streaming response"""
    print("=" * 70)
    print("TESTING SHAREBOT STREAMING")
    print("=" * 70)
    
    # Create ShareBot instance
    bot = ShareBot()
    
    # Test query
    query = "Explain in detail the performance of TCS stock"
    
    print(f"\nQuery: {query}")
    print("-" * 70)
    print("\nStreaming Response:\n")
    
    # Stream response
    for chunk in bot.chat_stream(query):
        print(chunk, end="", flush=True)
    
    print("\n\n" + "=" * 70)
    print("STREAMING TEST COMPLETE")
    print("=" * 70)


def test_regular_vs_streaming():
    """Compare regular and streaming responses"""
    print("\n\n" + "=" * 70)
    print("COMPARING REGULAR VS STREAMING")
    print("=" * 70)
    
    bot = ShareBot()
    query = "What is the current price of Reliance?"
    
    # Regular response
    print(f"\n1. REGULAR RESPONSE for: {query}")
    print("-" * 70)
    response = bot.chat(query)
    print(response)
    
    # Clear memory for fair comparison
    bot.clear_memory()
    
    # Streaming response
    print(f"\n\n2. STREAMING RESPONSE for: {query}")
    print("-" * 70)
    for chunk in bot.chat_stream(query):
        print(chunk, end="", flush=True)
    
    print("\n\n" + "=" * 70)


if __name__ == "__main__":
    # Test 1: Basic streaming
    test_streaming()
    
    # Test 2: Compare regular vs streaming
    test_regular_vs_streaming()
