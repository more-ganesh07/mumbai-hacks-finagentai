"""
ShareBot Agent - Market Data Agent with Intelligent Fallback

This agent uses two tools:
1. get_stock_data - Real-time stock data using yfinance
2. get_financial_insights - AI-powered financial research using Tavily + Groq

Fallback Strategy:
- First tries get_stock_data for stock-related queries
- If it fails or returns insufficient data, automatically falls back to get_financial_insights
- For general financial queries, directly uses get_financial_insights
"""

import os
import re
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import the market tools
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sharebot.tools.market_tools import get_stock_data, get_financial_insights

load_dotenv(override=True)

# -------------------------------------------------------
# Logging Setup
# -------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ShareAgent")


# -------------------------------------------------------
# Market Agent with Intelligent Fallback
# -------------------------------------------------------
class MarketAgent:
    """
    Intelligent market agent that uses real-time data with AI fallback.
    
    Strategy:
    1. Analyzes user query to determine intent
    2. For stock-specific queries: tries get_stock_data first
    3. If get_stock_data fails/insufficient: falls back to get_financial_insights
    4. For general financial queries: directly uses get_financial_insights
    """
    
    def __init__(self):
        self.tools = {
            "get_stock_data": get_stock_data,
            "get_financial_insights": get_financial_insights
        }
        self.metrics = {
            "stock_data_calls": 0,
            "financial_insights_calls": 0,
            "fallback_triggered": 0,
            "errors": 0
        }
    
    def _is_stock_query(self, query: str) -> tuple[bool, Optional[str]]:
        """
        Detect if query is asking for specific stock data.
        
        Returns:
            (is_stock_query, extracted_symbol)
        """
        query_lower = query.lower()
        
        # Keywords that indicate stock data request
        stock_keywords = [
            "price", "quote", "current", "trading at", "stock price",
            "share price", "market price", "today's price", "latest price",
            "high", "low", "volume", "market cap", "52 week"
        ]
        
        # Check if query contains stock-related keywords
        is_stock = any(keyword in query_lower for keyword in stock_keywords)
        
        # Try to extract stock symbol
        symbol = self._extract_symbol(query)
        
        return is_stock, symbol
    
    def _extract_symbol(self, query: str) -> Optional[str]:
        """
        Extract stock symbol from query.
        
        Examples:
            "price of TCS" -> "TCS"
            "Reliance stock" -> "Reliance"
            "INFY current price" -> "INFY"
        """
        # Common patterns
        patterns = [
            r'\b([A-Z]{2,10})\b',  # All caps words (likely symbols)
            r'(?:of|for)\s+([A-Za-z]+)',  # "price of TCS"
            r'([A-Za-z]+)\s+(?:stock|share|price)',  # "TCS stock"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                symbol = match.group(1)
                # Filter out common words
                if symbol.upper() not in ['PRICE', 'STOCK', 'SHARE', 'MARKET', 'TODAY', 'CURRENT', 'LATEST']:
                    return symbol
        
        return None
    
    def _is_error_response(self, response: str) -> bool:
        """
        Check if response indicates an error or failure.
        """
        error_indicators = [
            "❌",
            "Error",
            "Could not fetch",
            "No data",
            "Failed to",
            "not configured",
            "not available"
        ]
        
        return any(indicator in response for indicator in error_indicators)
    
    def _is_insufficient_response(self, response: str) -> bool:
        """
        Check if response is insufficient (too short, missing data, etc.)
        """
        # Remove "Final Answer." and whitespace
        clean_response = response.replace("Final Answer.", "").strip()
        
        # If response is very short, it's likely insufficient
        if len(clean_response) < 50:
            return True
        
        # Check for warning indicators
        warning_indicators = [
            "⚠️",
            "N/A",
            "not found",
            "unavailable"
        ]
        
        return any(indicator in response for indicator in warning_indicators)
    
    def process_query(self, user_query: str) -> str:
        """
        Process user query with intelligent tool selection and fallback.
        
        Args:
            user_query: User's financial query
        
        Returns:
            Response from the appropriate tool(s)
        """
        if not user_query or not user_query.strip():
            return "⚠️ Please provide a query.\n\nFinal Answer."
        
        logger.info(f"Processing query: {user_query}")
        
        # Analyze query
        is_stock, symbol = self._is_stock_query(user_query)
        
        # Strategy 1: Stock-specific query
        if is_stock and symbol:
            logger.info(f"Detected stock query for symbol: {symbol}")
            
            # Try get_stock_data first
            try:
                logger.info("Attempting get_stock_data...")
                self.metrics["stock_data_calls"] += 1
                
                # Prepare input for get_stock_data
                stock_input = symbol
                
                # Check if user wants historical data
                if any(word in user_query.lower() for word in ["history", "historical", "past", "trend", "month", "week"]):
                    # Extract period if mentioned
                    if "month" in user_query.lower():
                        stock_input = f"{symbol},1mo,1d"
                    elif "week" in user_query.lower():
                        stock_input = f"{symbol},1wk,1d"
                    else:
                        stock_input = f"{symbol},3mo,1d"
                
                response = get_stock_data(stock_input)
                
                # Check if response is valid and sufficient
                if not self._is_error_response(response) and not self._is_insufficient_response(response):
                    logger.info("get_stock_data succeeded")
                    return response
                
                # Response is insufficient, trigger fallback
                logger.warning("get_stock_data returned insufficient data, triggering fallback")
                self.metrics["fallback_triggered"] += 1
                
            except Exception as e:
                logger.error(f"get_stock_data failed: {e}")
                self.metrics["errors"] += 1
                self.metrics["fallback_triggered"] += 1
            
            # Fallback to get_financial_insights
            logger.info("Falling back to get_financial_insights...")
            try:
                self.metrics["financial_insights_calls"] += 1
                response = get_financial_insights(user_query)
                logger.info("Fallback to get_financial_insights succeeded")
                return response
            except Exception as e:
                logger.error(f"get_financial_insights also failed: {e}")
                self.metrics["errors"] += 1
                return f"❌ Unable to process query: {str(e)}\n\nFinal Answer."
        
        # Strategy 2: General financial query (IPO, news, analysis, etc.)
        else:
            logger.info("Detected general financial query")
            try:
                self.metrics["financial_insights_calls"] += 1
                response = get_financial_insights(user_query)
                logger.info("get_financial_insights succeeded")
                return response
            except Exception as e:
                logger.error(f"get_financial_insights failed: {e}")
                self.metrics["errors"] += 1
                return f"❌ Unable to process query: {str(e)}\n\nFinal Answer."
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            **self.metrics,
            "total_calls": self.metrics["stock_data_calls"] + self.metrics["financial_insights_calls"],
            "fallback_rate": (
                self.metrics["fallback_triggered"] / max(1, self.metrics["stock_data_calls"])
                if self.metrics["stock_data_calls"] > 0 else 0
            )
        }
    
    def reset_metrics(self):
        """Reset performance metrics"""
        self.metrics = {
            "stock_data_calls": 0,
            "financial_insights_calls": 0,
            "fallback_triggered": 0,
            "errors": 0
        }
        logger.info("Metrics reset")


# -------------------------------------------------------
# Convenience Functions
# -------------------------------------------------------

def create_agent() -> MarketAgent:
    """Create and return a new MarketAgent instance"""
    return MarketAgent()


def process_query(query: str) -> str:
    """
    Convenience function to process a query without managing agent instance.
    
    Args:
        query: User's financial query
    
    Returns:
        Response from the agent
    """
    agent = MarketAgent()
    return agent.process_query(query)


# -------------------------------------------------------
# Main (for testing)
# -------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("TESTING MARKET AGENT WITH FALLBACK")
    print("=" * 70)
    
    # Create agent
    agent = MarketAgent()
    
    # Test cases
    test_queries = [
        "What is the current price of TCS?",
        "Show me Reliance stock price",
        "INFY price today",
        "Latest IPO listings in India",
        "What are the top performing IT stocks?",
        "Tell me about INVALIDSTOCK123",  # Should trigger fallback
        "Market sentiment for banking sector",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'='*70}")
        print(f"TEST {i}: {query}")
        print('-'*70)
        
        response = agent.process_query(query)
        print(response)
        
        print(f"\n{'='*70}")
    
    # Print metrics
    print("\n\n" + "="*70)
    print("AGENT METRICS")
    print("="*70)
    metrics = agent.get_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)
