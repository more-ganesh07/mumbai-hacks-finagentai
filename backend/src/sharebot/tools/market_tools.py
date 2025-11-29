"""
Market Tools for ShareBot
Two main tools:
1. Real-time stock and exchange data using yfinance
2. Financial queries using deep agent with Tavily search
"""

import os
import yfinance as yf
from typing import Dict, Any, Literal
from tavily import TavilyClient
from groq import Groq
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv(override=True)

# Initialize clients
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# -------------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------------

def _log_tool(name: str, arg: str = ""):
    """Log tool usage for debugging"""
    print(f"🔧 Tool → {name}('{arg}')")


@lru_cache(maxsize=128)
def _normalize_symbol(symbol: str) -> str:
    """
    Normalize stock symbols to yfinance format.
    Handles common Indian stock aliases and adds .NS suffix for NSE stocks.
    """
    aliases = {
        "SENSEX": "^BSESN",
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "BANK NIFTY": "^NSEBANK",
        "NIFTY 50": "^NSEI",
        "INDUS BANK": "INDUSINDBK.NS",
        "INDUSIND BANK": "INDUSINDBK.NS",
        "HDFC BANK": "HDFCBANK.NS",
        "HDFCBANK": "HDFCBANK.NS",
        "SBI": "SBIN.NS",
        "SBIN": "SBIN.NS",
        "STATE BANK": "SBIN.NS",
        "RELIANCE": "RELIANCE.NS",
        "TATA MOTORS": "TATAMOTORS.NS",
        "TCS": "TCS.NS",
        "INFOSYS": "INFY.NS",
        "INFY": "INFY.NS",
        "WIPRO": "WIPRO.NS",
        "HCL": "HCLTECH.NS",
        "HCL TECH": "HCLTECH.NS",
        "BHARTI AIRTEL": "BHARTIARTL.NS",
        "AIRTEL": "BHARTIARTL.NS",
        "ADANI ENTERPRISES": "ADANIENT.NS",
        "ADANI PORTS": "ADANIPORTS.NS",
        "ITC": "ITC.NS",
        "BAJAJ FINANCE": "BAJFINANCE.NS",
        "LIC": "LICI.NS",
        "TITAN": "TITAN.NS",
        "MARUTI": "MARUTI.NS",
    }
    
    # Normalize input
    alias = symbol.strip().upper()
    
    # Check if it's a known alias
    if alias in aliases:
        return aliases[alias]
    
    # Remove spaces and add .NS suffix if needed
    sym = alias.replace(" ", "")
    if not sym.endswith(".NS") and not sym.endswith(".BO") and not sym.startswith("^"):
        sym += ".NS"
    
    return sym


def _format_currency(value: float, decimals: int = 2) -> str:
    """Format value as Indian currency"""
    if value is None:
        return "N/A"
    return f"₹{value:,.{decimals}f}"


def _format_percentage(value: float) -> str:
    """Format value as percentage"""
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"


def _get_trend_indicator(change: float) -> str:
    """Get trend indicator emoji based on change"""
    if change > 0:
        return "🔺"
    elif change < 0:
        return "🔻"
    return "➖"


# -------------------------------------------------------------------------
# TOOL 1: Real-time Stock and Exchange Data (yfinance)
# -------------------------------------------------------------------------

def get_stock_data(input_str: str) -> str:
    """
    Fetch real-time stock and exchange data using yfinance.
    
    Args:
        input_str: Stock symbol or comma-separated parameters
                  Format: "symbol" or "symbol,period,interval"
                  Examples: 
                    - "RELIANCE"
                    - "TCS,1mo,1d"
                    - "NIFTY"
    
    Returns:
        Formatted string with stock data including:
        - Current price and change
        - Day high/low
        - 52-week high/low
        - Volume
        - Historical data summary if period specified
    """
    _log_tool("get_stock_data", input_str)
    
    try:
        # Parse input
        parts = [p.strip() for p in input_str.split(",")]
        symbol = _normalize_symbol(parts[0])
        period = parts[1] if len(parts) > 1 else None
        interval = parts[2] if len(parts) > 2 else "1d"
        
        # Fetch ticker data
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get current price with multiple fallbacks
        price = (info.get("currentPrice") or 
                info.get("regularMarketPrice") or 
                info.get("previousClose"))
        
        # If still no price, try historical data
        if not price:
            hist = ticker.history(period="5d", interval="1d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
        
        if not price:
            return f"❌ Could not fetch price data for {symbol}. The symbol might be incorrect or delisted.\n\nFinal Answer."
        
        # Get company/index name
        company_name = info.get("longName") or info.get("shortName") or symbol
        
        # Calculate change
        prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
        change = 0
        change_pct = 0
        if prev_close and price:
            change = price - prev_close
            change_pct = (change / prev_close) * 100
        
        # Build response
        response_lines = []
        response_lines.append(f"📊 **{company_name}** ({symbol})")
        response_lines.append("")
        
        # Current price
        indicator = _get_trend_indicator(change)
        response_lines.append(f"**Current Price**: {_format_currency(price)} {indicator} {_format_percentage(change_pct)}")
        
        # Price change context
        if abs(change_pct) > 2:
            if change_pct > 0:
                response_lines.append(f"_Strong upward movement today! (+{_format_currency(abs(change))})_")
            else:
                response_lines.append(f"_Significant decline today. ({_format_currency(change)})_")
        response_lines.append("")
        
        # Day range
        day_high = info.get("dayHigh") or info.get("regularMarketDayHigh")
        day_low = info.get("dayLow") or info.get("regularMarketDayLow")
        if day_high and day_low:
            response_lines.append(f"**Day Range**: {_format_currency(day_low)} - {_format_currency(day_high)}")
        
        # 52-week range
        year_high = info.get("fiftyTwoWeekHigh")
        year_low = info.get("fiftyTwoWeekLow")
        if year_high and year_low:
            response_lines.append(f"**52-Week Range**: {_format_currency(year_low)} - {_format_currency(year_high)}")
        
        # Volume
        volume = info.get("volume") or info.get("regularMarketVolume")
        if volume:
            volume_str = f"{volume:,}" if volume < 1_000_000 else f"{volume/1_000_000:.2f}M"
            response_lines.append(f"**Volume**: {volume_str}")
        
        # Market cap (if available)
        market_cap = info.get("marketCap")
        if market_cap:
            if market_cap >= 1_000_000_000_000:  # Trillion
                cap_str = f"₹{market_cap/1_000_000_000_000:.2f}T"
            elif market_cap >= 10_000_000_000:  # Billion
                cap_str = f"₹{market_cap/10_000_000_000:.2f}K Cr"
            else:
                cap_str = f"₹{market_cap/10_000_000:.2f} Cr"
            response_lines.append(f"**Market Cap**: {cap_str}")
        
        # Historical data if period specified
        if period:
            response_lines.append("")
            response_lines.append(f"**Historical Data ({period})**:")
            hist = ticker.history(period=period, interval=interval)
            
            if not hist.empty:
                start_date = hist.index[0].strftime("%Y-%m-%d")
                end_date = hist.index[-1].strftime("%Y-%m-%d")
                avg_close = hist["Close"].mean()
                high = hist["High"].max()
                low = hist["Low"].min()
                total_days = len(hist)
                
                response_lines.append(f"- Period: {start_date} to {end_date} ({total_days} trading days)")
                response_lines.append(f"- Average Close: {_format_currency(avg_close)}")
                response_lines.append(f"- Highest: {_format_currency(high)}")
                response_lines.append(f"- Lowest: {_format_currency(low)}")
            else:
                response_lines.append("_No historical data available for the specified period._")
        
        return "\n".join(response_lines) + "\n\nFinal Answer."
        
    except Exception as e:
        return f"❌ Error fetching stock data: {str(e)}\n\nFinal Answer."


# -------------------------------------------------------------------------
# TOOL 2: Financial Queries using Deep Agent (Tavily + Groq)
# -------------------------------------------------------------------------

def _internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "finance",
    include_raw_content: bool = False,
) -> Dict[str, Any]:
    """
    Run a web search using Tavily API.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        topic: Search topic (general, news, finance)
        include_raw_content: Whether to include raw HTML content
    
    Returns:
        Dictionary with search results
    """
    if not tavily_client:
        raise ValueError("Tavily API key not configured")
    
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
        include_domains=["economictimes.com", "moneycontrol.com", "livemint.com", 
                        "business-standard.com", "financialexpress.com", "investing.com"]
    )


# System prompt for financial research agent
FINANCIAL_RESEARCH_PROMPT = """You are an expert financial analyst and researcher specializing in Indian stock markets.

Your job is to conduct thorough research using internet search results and provide comprehensive, accurate financial analysis.

## Guidelines:
- Provide factual, data-driven insights based on the search results
- Focus on Indian markets (NSE, BSE) unless specified otherwise
- Include relevant numbers, dates, and statistics
- Cite sources when making specific claims
- Be concise but comprehensive
- Use professional financial terminology
- If search results are insufficient, acknowledge limitations

## Response Format:
- Start with a brief summary
- Provide detailed analysis with supporting data
- Include relevant context and implications
- End with key takeaways or recommendations if applicable

You have access to recent internet search results about the query. Use them to provide an informed, expert response.
"""


def get_financial_insights(query: str) -> str:
    """
    Get comprehensive financial market insights using deep agent (Tavily search + Groq LLM).
    
    This tool performs intelligent web searches and uses an LLM to analyze and synthesize
    information to answer financial queries.
    
    Args:
        query: Financial query or question
               Examples:
                 - "What are the latest IPO listings?"
                 - "Analysis of IT sector performance this week"
                 - "News about Reliance Industries"
                 - "Market sentiment for banking stocks"
    
    Returns:
        Comprehensive analysis based on latest web search results
    """
    _log_tool("get_financial_insights", query)
    
    try:
        # Validate API keys
        if not tavily_client:
            return "❌ Tavily API key not configured. Please set TAVILY_API_KEY in environment.\n\nFinal Answer."
        
        if not groq_client:
            return "❌ Groq API key not configured. Please set GROQ_API_KEY in environment.\n\nFinal Answer."
        
        # Enhance query for better search results
        enhanced_query = f"{query} India stock market financial"
        
        # Get search results
        search_results = _internet_search(
            enhanced_query,
            max_results=5,
            topic="finance",
            include_raw_content=False
        )
        
        if not search_results.get("results"):
            return f"⚠️ No search results found for: {query}\n\nTry rephrasing your query or being more specific.\n\nFinal Answer."
        
        # Format search results as context
        context_parts = []
        for i, result in enumerate(search_results["results"], 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "No content available")
            
            context_parts.append(
                f"Source {i}:\n"
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Content: {content}\n"
            )
        
        context = "\n---\n".join(context_parts)
        
        # Call Groq LLM with search results
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": FINANCIAL_RESEARCH_PROMPT},
                {
                    "role": "user", 
                    "content": f"User Query: {query}\n\n"
                               f"Search Results:\n{context}\n\n"
                               f"Based on these search results, provide a comprehensive answer to the user's query."
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Extract and format response
        analysis = response.choices[0].message.content
        
        # Add sources footer
        sources = "\n\n**Sources:**\n"
        for i, result in enumerate(search_results["results"], 1):
            sources += f"{i}. [{result.get('title', 'Source')}]({result.get('url', '#')})\n"
        
        return f"{analysis}\n{sources}\nFinal Answer."
        
    except Exception as e:
        return f"❌ Error getting financial insights: {str(e)}\n\nFinal Answer."


# -------------------------------------------------------------------------
# Tool Registry (for easy integration with agents)
# -------------------------------------------------------------------------

MARKET_TOOLS = {
    "get_stock_data": {
        "function": get_stock_data,
        "description": "Get real-time stock and exchange data using yfinance. Supports Indian stocks (NSE/BSE) and indices.",
        "parameters": {
            "input_str": "Stock symbol or 'symbol,period,interval' (e.g., 'RELIANCE' or 'TCS,1mo,1d')"
        }
    },
    "get_financial_insights": {
        "function": get_financial_insights,
        "description": "Get comprehensive financial market insights using AI-powered research. Answers questions about IPOs, market trends, company news, sector analysis, etc.",
        "parameters": {
            "query": "Financial query or question (e.g., 'Latest IPO listings' or 'IT sector performance')"
        }
    }
}


# -------------------------------------------------------------------------
# Main (for testing)
# -------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("TESTING MARKET TOOLS")
    print("=" * 70)
    
    # Test 1: Stock data
    print("\n\n📊 TEST 1: Get Stock Data for Reliance")
    print("-" * 70)
    result1 = get_stock_data("RELIANCE")
    print(result1)
    
    # Test 2: Stock data with history
    print("\n\n📊 TEST 2: Get Stock Data with History for TCS")
    print("-" * 70)
    result2 = get_stock_data("TCS,1mo,1d")
    print(result2)
    
    # Test 3: Financial insights
    print("\n\n🔍 TEST 3: Get Financial Insights - Latest IPO Listings")
    print("-" * 70)
    result3 = get_financial_insights("Latest IPO listings in India this week")
    print(result3)
    
    print("\n" + "=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)
