# src/kite/portbot/tool/market_analysis.py
import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv(override=True)

from src.kite.portbot.base import Agent
from tavily import TavilyClient
from groq import AsyncGroq

class MarketAnalysisAgent(Agent):
    """
    Market analysis agent using Tavily for deep research.
    Provides stock analysis, news, market insights, and research.
    """
    name = "market_analysis"
    description = "Deep market research and stock analysis using Tavily"

    tools = [
        {
            "name": "analyze_stock",
            "description": "Deep analysis of a specific stock with news, fundamentals, and outlook",
            "parameters": {"symbol": "str", "context": "str (optional - user's position details)"}
        },
        {
            "name": "get_market_news",
            "description": "Get latest market news and updates for stocks or sectors",
            "parameters": {"query": "str"}
        },
        {
            "name": "research_topic",
            "description": "Deep research on any financial topic, market trend, or investment question",
            "parameters": {"query": "str"}
        },
    ]

    def __init__(self, kite_client=None, shared_state=None):
        super().__init__(shared_state)
        self.kite_client = kite_client
        
        # Initialize Tavily
        tavily_key = os.getenv("TAVILY_API_KEY")
        if not tavily_key:
            raise ValueError("TAVILY_API_KEY not found in environment")
        self.tavily_client = TavilyClient(api_key=tavily_key)
        
        # Initialize Groq for analysis
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        self.groq_client = AsyncGroq(api_key=groq_key)
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    async def run(self, tool_name: str, **kwargs):
        """Execute the specified tool"""
        if tool_name == "analyze_stock":
            return await self._analyze_stock(**kwargs)
        elif tool_name == "get_market_news":
            return await self._get_market_news(**kwargs)
        elif tool_name == "research_topic":
            return await self._research_topic(**kwargs)
        raise ValueError(f"Unknown tool: {tool_name}")

    def _internet_search(self, query: str, max_results: int = 5, topic: str = "finance") -> Dict[str, Any]:
        """Run Tavily search"""
        try:
            return self.tavily_client.search(
                query,
                max_results=max_results,
                include_raw_content=False,
                topic=topic,
            )
        except Exception as e:
            print(f"Tavily search error: {e}")
            return {"results": []}

    async def _analyze_stock(self, symbol: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Deep stock analysis with Tavily research.
        
        Returns:
            {
                "status": "success" | "error",
                "data": {
                    "symbol": str,
                    "analysis": str (markdown formatted),
                    "sources": [{"title": str, "url": str}]
                },
                "summary": {
                    "symbol": str,
                    "analysis": str,
                    "source_count": int
                }
            }
        """
        try:
            # Search for stock information
            query = f"{symbol} stock financial performance news outlook analysis"
            search_results = self._internet_search(query, max_results=5, topic="finance")
            
            if not search_results.get('results'):
                return {
                    "status": "error",
                    "message": f"No market data found for {symbol}",
                    "data": None,
                    "summary": None
                }
            
            # Build context from search results
            research_context = "\n\n".join([
                f"Title: {result['title']}\nURL: {result['url']}\nContent: {result['content']}"
                for result in search_results['results']
            ])
            
            # Generate analysis using Groq
            system_prompt = """You are a senior financial analyst. Provide professional stock analysis.

**Guidelines:**
- Tone: Professional, objective, data-driven
- Format: Clean Markdown with tables where appropriate
- NO emojis
- Structure:
  1. Investment Verdict (Buy/Hold/Sell with rationale)
  2. Financial Health (key metrics from context)
  3. Key Catalysts & Risks
  4. Outlook (12-month forecast)
"""
            
            user_prompt = f"""**Stock**: {symbol}
{"**User Position**: " + context if context else ""}

**Market Data & News**:
{research_context}

Provide concise professional analysis."""
            
            response = await self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            sources = [{"title": r["title"], "url": r["url"]} for r in search_results['results']]
            
            return {
                "status": "success",
                "data": {
                    "symbol": symbol,
                    "analysis": analysis,
                    "sources": sources
                },
                "summary": {
                    "symbol": symbol,
                    "analysis": analysis,
                    "source_count": len(sources)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to analyze {symbol}: {str(e)}",
                "data": None,
                "summary": None
            }

    async def _get_market_news(self, query: str) -> Dict[str, Any]:
        """
        Get latest market news.
        
        Returns:
            {
                "status": "success" | "error",
                "data": [{"title": str, "url": str, "content": str, "published_date": str}],
                "summary": {
                    "news_items": [...],
                    "total_count": int
                }
            }
        """
        try:
            search_results = self._internet_search(query, max_results=5, topic="news")
            
            if not search_results.get('results'):
                return {
                    "status": "error",
                    "message": f"No news found for: {query}",
                    "data": [],
                    "summary": None
                }
            
            news_items = [
                {
                    "title": r["title"],
                    "url": r["url"],
                    "content": r["content"],
                    "published_date": r.get("published_date", "")
                }
                for r in search_results['results']
            ]
            
            return {
                "status": "success",
                "data": news_items,
                "summary": {
                    "news_items": news_items,
                    "total_count": len(news_items)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to fetch news: {str(e)}",
                "data": [],
                "summary": None
            }

    async def _research_topic(self, query: str) -> Dict[str, Any]:
        """
        Deep research on any financial topic.
        
        Returns:
            {
                "status": "success" | "error",
                "data": {
                    "query": str,
                    "research": str (markdown formatted),
                    "sources": [...]
                },
                "summary": {
                    "query": str,
                    "research": str,
                    "source_count": int
                }
            }
        """
        try:
            search_results = self._internet_search(query, max_results=5, topic="finance")
            
            if not search_results.get('results'):
                return {
                    "status": "error",
                    "message": f"No information found for: {query}",
                    "data": None,
                    "summary": None
                }
            
            # Build research context
            research_context = "\n\n".join([
                f"Title: {result['title']}\nURL: {result['url']}\nContent: {result['content']}"
                for result in search_results['results']
            ])
            
            # Generate research summary
            system_prompt = """You are a financial research analyst. Provide comprehensive, professional analysis.

**Guidelines:**
- Professional, objective tone
- Clean Markdown format
- NO emojis
- Cite key findings
- Provide actionable insights
"""
            
            user_prompt = f"""**Research Query**: {query}

**Sources**:
{research_context}

Provide detailed professional research summary."""
            
            response = await self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            research = response.choices[0].message.content
            sources = [{"title": r["title"], "url": r["url"]} for r in search_results['results']]
            
            return {
                "status": "success",
                "data": {
                    "query": query,
                    "research": research,
                    "sources": sources
                },
                "summary": {
                    "query": query,
                    "research": research,
                    "source_count": len(sources)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to research topic: {str(e)}",
                "data": None,
                "summary": None
            }
