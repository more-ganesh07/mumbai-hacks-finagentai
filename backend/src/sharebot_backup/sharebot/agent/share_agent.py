
import os
import json
import time
import hashlib
import logging
from typing import List, Dict, Optional, Tuple
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from src.sharebot.tools.market_tools import (
    get_price, get_history, get_company_info, get_financials,
    get_stock_news, get_market_overview, get_stock_analysis,
    track_portfolio, get_ipo_calendar, get_dividends, get_splits,
    get_mutual_fund_info
)

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
# Tool Registry
# -------------------------------------------------------
TOOLS = {
    "get_price": get_price,
    "get_history": get_history,
    "get_company_info": get_company_info,
    "get_financials": get_financials,
    "get_stock_news": get_stock_news,
    "get_market_overview": get_market_overview,
    "get_stock_analysis": get_stock_analysis,
    "track_portfolio": track_portfolio,
    "get_ipo_calendar": get_ipo_calendar,
    "get_dividends": get_dividends,
    "get_splits": get_splits,
    "get_mutual_fund_info": get_mutual_fund_info,
}

# Tools that can be executed in parallel (no dependencies)
PARALLEL_SAFE_TOOLS = {
    "get_price", "get_company_info", "get_stock_news", 
    "get_market_overview", "get_dividends", "get_splits",
    "get_ipo_calendar", "get_mutual_fund_info"
}

# -------------------------------------------------------
# Enhanced Tool Descriptions
# -------------------------------------------------------
TOOL_DESCRIPTIONS = """
Available tools:
1. get_price(symbol) - Current stock price with high/low (e.g., "TCS", "INFY")
2. get_history(symbol, period, interval) - Historical data (e.g., "TCS, 1mo, 1d")
3. get_company_info(symbol) - Company details, sector, summary (e.g., "TCS")
4. get_financials(symbol) - Financial statements (e.g., "TCS")
5. get_stock_news(query, count) - Latest news (e.g., "TCS, 3")
6. get_market_overview() - NIFTY, SENSEX, BANK NIFTY (no input needed)
7. get_stock_analysis(symbol, period, interval) - Technical analysis (e.g., "TCS, 6mo, 1d")
8. track_portfolio(holdings) - Portfolio tracking (e.g., "TCS:5, Reliance:3")
9. get_ipo_calendar() - Upcoming IPOs (no input needed)
10. get_dividends(symbol) - Dividend history (e.g., "TCS")
11. get_splits(symbol) - Stock split history (e.g., "TCS")
12. get_mutual_fund_info(fund_code) - Mutual fund details (e.g., "119551")

Tool Selection Strategy:
- Price query → get_price
- Analysis → get_stock_analysis + get_price + get_stock_news
- Company research → get_company_info + get_price + get_stock_news
- Market status → get_market_overview
- Portfolio → track_portfolio
- Use MULTIPLE tools for comprehensive queries

Response Format: {"tools": [{"name": "tool_name", "input": "input_value"}]}
If no tools needed: {"tools": []}
"""

# -------------------------------------------------------
# Cache for Tool Results (TTL-based)
# -------------------------------------------------------
class ToolResultCache:
    """Simple TTL-based cache for tool results"""
    def __init__(self, ttl_seconds: int = 60):
        self.cache: Dict[str, Tuple[str, float]] = {}
        self.ttl = ttl_seconds
    
    def _make_key(self, tool_name: str, tool_input: str) -> str:
        """Create cache key"""
        key_str = f"{tool_name}:{tool_input}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, tool_name: str, tool_input: str) -> Optional[str]:
        """Get cached result if valid"""
        key = self._make_key(tool_name, tool_input)
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                logger.debug(f"Cache HIT: {tool_name}({tool_input})")
                return result
            else:
                del self.cache[key]
        logger.debug(f"Cache MISS: {tool_name}({tool_input})")
        return None
    
    def set(self, tool_name: str, tool_input: str, result: str):
        """Cache result"""
        key = self._make_key(tool_name, tool_input)
        self.cache[key] = (result, time.time())
        # Clean old entries if cache gets too large
        if len(self.cache) > 100:
            current_time = time.time()
            self.cache = {
                k: v for k, v in self.cache.items()
                if current_time - v[1] < self.ttl
            }
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()

# -------------------------------------------------------
# Core Agent Class (Enhanced)
# -------------------------------------------------------
class Agent:
    """Advanced agent with caching, retry, and parallel execution"""
    
    def __init__(self, enable_cache: bool = True, cache_ttl: int = 60, max_retries: int = 2):
        self.tools = TOOLS
        self.tool_descriptions = TOOL_DESCRIPTIONS
        self.cache = ToolResultCache(ttl_seconds=cache_ttl) if enable_cache else None
        self.max_retries = max_retries
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.metrics = {
            "tool_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "total_time": 0.0
        }
    
    # ---------------- Enhanced Tool Planning with Retry ---------------- 
    def plan_tools(self, user_query: str, llm_call_fn, retry_count: int = 0) -> List[Dict[str, str]]:
        """
        Plan which tools to use with retry logic and better JSON parsing
        """
        if not user_query or not user_query.strip():
            logger.warning("Empty user query provided")
            return []
        
        prompt = f"""You are a stock market assistant. Decide which tools to use.

{self.tool_descriptions}

User Query: {user_query}

IMPORTANT:
- For price queries, use get_price
- For analysis, combine multiple tools (get_price + get_stock_analysis + get_stock_news)
- For company info, use get_company_info + get_price
- Extract symbol names correctly (e.g., "TCS", "INFY", "Reliance")

Respond ONLY with valid JSON: {{"tools": [{{"name": "tool_name", "input": "input_value"}}]}}
If no tools needed: {{"tools": []}}
"""
        try:
            response = llm_call_fn(prompt, temperature=0.1, max_tokens=500, stream=False)
            
            # Enhanced JSON extraction
            response = self._extract_json(response)
            
            if not response:
                if retry_count < self.max_retries:
                    logger.warning(f"JSON extraction failed, retrying ({retry_count + 1}/{self.max_retries})")
                    return self.plan_tools(user_query, llm_call_fn, retry_count + 1)
                return []
            
            plan = json.loads(response)
            tools = plan.get("tools", [])
            
            # Validate tools
            validated_tools = self._validate_tools(tools)
            if validated_tools != tools and retry_count < self.max_retries:
                logger.warning(f"Tool validation failed, retrying ({retry_count + 1}/{self.max_retries})")
                return self.plan_tools(user_query, llm_call_fn, retry_count + 1)
            
            logger.info(f"Planned {len(validated_tools)} tools: {[t.get('name') for t in validated_tools]}")
            return validated_tools
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            if retry_count < self.max_retries:
                return self.plan_tools(user_query, llm_call_fn, retry_count + 1)
            return []
        except Exception as e:
            logger.error(f"Planning error: {e}", exc_info=True)
            return []
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response with multiple strategies"""
        if not text:
            return ""
        
        # Strategy 1: Look for ```json blocks
        if "```json" in text:
            parts = text.split("```json")
            if len(parts) > 1:
                json_part = parts[1].split("```")[0].strip()
                if json_part:
                    return json_part
        
        # Strategy 2: Look for ``` blocks
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("{") and "tools" in part:
                    return part
        
        # Strategy 3: Find JSON object directly
        start_idx = text.find("{")
        if start_idx != -1:
            brace_count = 0
            for i in range(start_idx, len(text)):
                if text[i] == "{":
                    brace_count += 1
                elif text[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        json_str = text[start_idx:i+1]
                        if "tools" in json_str:
                            return json_str
        
        # Strategy 4: Return as-is if it looks like JSON
        text = text.strip()
        if text.startswith("{") and text.endswith("}"):
            return text
        
        return ""
    
    def _validate_tools(self, tools: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Validate and filter tools"""
        validated = []
        for tool in tools:
            tool_name = tool.get("name", "").strip()
            tool_input = tool.get("input", "").strip()
            
            if not tool_name:
                logger.warning("Tool missing name, skipping")
                continue
            
            if tool_name not in self.tools:
                logger.warning(f"Unknown tool: {tool_name}, skipping")
                continue
            
            # Some tools don't need input
            if tool_name in ["get_market_overview", "get_ipo_calendar"]:
                tool_input = ""
            
            validated.append({"name": tool_name, "input": tool_input})
        
        return validated
    
    # ---------------- Enhanced Tool Execution with Caching & Parallel ---------------- 
    def execute_tools(self, tools: List[Dict[str, str]], parallel: bool = True) -> str:
        """
        Execute tools with caching and optional parallel execution
        """
        if not tools:
            return ""
        
        start_time = time.time()
        results = []
        
        # Separate tools into parallel-safe and sequential
        parallel_tools = []
        sequential_tools = []
        
        for tool in tools:
            tool_name = tool.get("name")
            if parallel and tool_name in PARALLEL_SAFE_TOOLS:
                parallel_tools.append(tool)
            else:
                sequential_tools.append(tool)
        
        # Execute parallel-safe tools concurrently
        if parallel_tools:
            logger.info(f"Executing {len(parallel_tools)} tools in parallel")
            parallel_results = self._execute_parallel(parallel_tools)
            results.extend(parallel_results)
        
        # Execute sequential tools one by one
        for tool in sequential_tools:
            result = self._execute_single_tool(tool)
            if result:
                results.append(result)
        
        execution_time = time.time() - start_time
        self.metrics["total_time"] += execution_time
        self.metrics["tool_calls"] += len(tools)
        
        logger.info(f"Executed {len(tools)} tools in {execution_time:.2f}s")
        return "\n".join(results)
    
    def _execute_parallel(self, tools: List[Dict[str, str]]) -> List[str]:
        """Execute tools in parallel"""
        results = []
        futures = {}
        
        for tool in tools:
            future = self.executor.submit(self._execute_single_tool, tool)
            futures[future] = tool
        
        for future in as_completed(futures):
            tool = futures[future]
            try:
                result = future.result(timeout=30)  # 30s timeout per tool
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Parallel execution error for {tool.get('name')}: {e}")
                results.append(f"[{tool.get('name')}]: ❌ Error: {e}\n")
        
        return results
    
    def _execute_single_tool(self, tool: Dict[str, str]) -> str:
        """Execute a single tool with caching"""
        tool_name = tool.get("name")
        tool_input = tool.get("input", "")
        
        if not tool_name or tool_name not in self.tools:
            return f"[{tool_name}]: ⚠️ Unknown tool\n"
        
        # Check cache
        if self.cache:
            cached_result = self.cache.get(tool_name, tool_input)
            if cached_result:
                self.metrics["cache_hits"] += 1
                return f"[{tool_name}]:\n{cached_result}\n"
            self.metrics["cache_misses"] += 1
        
        # Execute tool
        logger.info(f"Executing: {tool_name}({tool_input})")
        try:
            start = time.time()
            result = self.tools[tool_name](tool_input)
            exec_time = time.time() - start
            
            # Cache result
            if self.cache and result and not result.startswith("❌"):
                self.cache.set(tool_name, tool_input, result)
            
            logger.debug(f"{tool_name} completed in {exec_time:.2f}s")
            return f"[{tool_name}]:\n{result}\n"
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Tool execution error: {tool_name} - {e}", exc_info=True)
            return f"[{tool_name}]: ❌ Error: {str(e)}\n"
    
    # ---------------- Enhanced System Prompt Generation ---------------- 
    def get_system_prompt(self, tool_results: str = None, user_query: str = None) -> str:
        """
        Generate system prompt dynamically with context awareness
        """
        # Detect intent
        is_detailed = self._detect_detailed_intent(user_query)
        
        if tool_results:
            if is_detailed:
                return f"""You are an expert stock market analyst. Analyze the tool results comprehensively.

Tool Results:
{tool_results}

Instructions:
- Write a detailed, coherent analysis (300–500 words).
- Structure: Overview → Technical Analysis → News Context → Key Insights → Actionable Recommendations.
- Use professional markdown formatting.
- Format prices with ₹ for Indian market.
- Never repeat tool output verbatim - synthesize and analyze.
- Provide actionable insights based on data.
- Compare with market trends when relevant.
- Mention risk factors if applicable.
"""
            else:
                return f"""You are a concise, professional financial assistant.
Provide a brief, insightful summary (80–120 words) based on the tool results.

Tool Results:
{tool_results}

Guidelines:
- Keep response short and informative.
- Focus on key metrics and insights.
- Format prices with ₹.
- One cohesive paragraph preferred.
- Avoid repetitive headers or templates.
"""
        else:
            # No tool results - conversational fallback
            if is_detailed:
                return """You are a detailed financial assistant.
Provide an analytical response (≈300 words) explaining the user's question about stocks or markets.
Use professional tone and format prices with ₹.
"""
            else:
                return """You are a brief, helpful financial assistant.
Provide a concise, factual answer (≈80–120 words).
Format prices with ₹ for Indian market.
"""
    
    def _detect_detailed_intent(self, user_query: str) -> bool:
        """Detect if user wants detailed analysis"""
        if not user_query:
            return False
        
        detailed_keywords = [
            "explain", "why", "reason", "detailed", "full", "comprehensive",
            "deep", "in depth", "long", "report", "breakdown", "analysis",
            "analyze", "evaluate", "assess", "compare"
        ]
        
        brief_keywords = ["price", "quote", "today", "current", "value", "update", "what is"]
        
        q_lower = user_query.lower()
        
        # Check for explicit detailed requests
        if any(k in q_lower for k in detailed_keywords):
            return True
        
        # Check for brief requests
        if any(k in q_lower for k in brief_keywords) and "explain" not in q_lower:
            return False
        
        # Default to brief for simple queries
        return False
    
    # ---------------- Metrics & Utilities ---------------- 
    def get_metrics(self) -> Dict:
        """Get performance metrics"""
        return {
            **self.metrics,
            "cache_hit_rate": (
                self.metrics["cache_hits"] / max(1, self.metrics["cache_hits"] + self.metrics["cache_misses"])
            ) if self.cache else 0,
            "avg_tool_time": (
                self.metrics["total_time"] / max(1, self.metrics["tool_calls"])
            ),
        }
    
    def clear_cache(self):
        """Clear tool result cache"""
        if self.cache:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def reset_metrics(self):
        """Reset performance metrics"""
        self.metrics = {
            "tool_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "total_time": 0.0
        }
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
            