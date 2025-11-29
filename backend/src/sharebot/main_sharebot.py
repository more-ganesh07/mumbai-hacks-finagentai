"""
ShareBot - Main Entry Point for FastAPI Integration

Features:
- Integrates MarketAgent with Groq LLM
- Buffer memory for conversation context
- Adaptive response length based on user query
- Markdown formatted responses
- Ready for FastAPI integration
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from groq import Groq

# Import MarketAgent
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sharebot.agent.share_agent import MarketAgent

load_dotenv(override=True)

# -------------------------------------------------------
# Logging Setup
# -------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ShareBot")


# -------------------------------------------------------
# ShareBot Main Class
# -------------------------------------------------------
class ShareBot:
    """
    Main ShareBot class for FastAPI integration.
    
    Features:
    - Uses MarketAgent for intelligent tool selection with fallback
    - Groq LLM for natural language processing
    - Buffer memory for conversation context
    - Adaptive response length (short/normal/detailed)
    - Markdown formatted responses
    """
    
    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",
        max_memory: int = 10,
        temperature: float = 0.3
    ):
        """
        Initialize ShareBot.
        
        Args:
            model: Groq model to use
            max_memory: Maximum conversation turns to keep in memory
            temperature: LLM temperature (0.0-1.0)
        """
        # Validate API key
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Initialize Groq client
        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        
        # Initialize MarketAgent
        self.agent = MarketAgent()
        
        # Buffer memory (stores last N conversation turns)
        self.max_memory = max_memory
        self.memory: List[Dict[str, str]] = []
        
        logger.info(f"ShareBot initialized with model: {model}")
    
    # -------------------------------------------------------
    # Memory Management
    # -------------------------------------------------------
    
    def add_to_memory(self, role: str, content: str):
        """Add message to buffer memory with automatic trimming."""
        if not content or not content.strip():
            return
        
        self.memory.append({"role": role, "content": content.strip()})
        
        # Keep only last N messages (N*2 for user+assistant pairs)
        if len(self.memory) > self.max_memory * 2:
            self.memory = self.memory[-(self.max_memory * 2):]
            logger.debug(f"Trimmed memory to last {self.max_memory} turns")
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory = []
        logger.info("Memory cleared")
    
    def get_memory_context(self) -> str:
        """Format memory for LLM context."""
        if not self.memory:
            return "No previous conversation."
        
        formatted = []
        for msg in self.memory[-6:]:  # Last 3 turns
            role = msg.get("role", "").capitalize()
            content = msg.get("content", "")[:300]  # Truncate long messages
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)
    
    # -------------------------------------------------------
    # Response Length Detection
    # -------------------------------------------------------
    
    def _detect_response_length(self, query: str) -> str:
        """
        Detect desired response length from user query.
        
        Returns:
            "short", "normal", or "detailed"
        """
        query_lower = query.lower()
        
        # Short response indicators
        short_keywords = [
            "price", "what is", "current", "today", "now", "quick",
            "brief", "short", "just tell", "simply"
        ]
        
        # Detailed response indicators
        detailed_keywords = [
            "explain", "why", "how", "detailed", "analysis", "analyze",
            "comprehensive", "full", "complete", "breakdown", "deep dive",
            "in depth", "elaborate", "describe", "compare", "evaluate",
            "assess", "insight", "outlook", "forecast", "recommendation"
        ]
        
        # Check for detailed request
        if any(keyword in query_lower for keyword in detailed_keywords):
            return "detailed"
        
        # Check for short request
        if any(keyword in query_lower for keyword in short_keywords):
            # But not if it also asks for explanation
            if not any(keyword in query_lower for keyword in ["explain", "why", "how"]):
                return "short"
        
        # Default to normal
        return "normal"
    
    # -------------------------------------------------------
    # System Prompt Generation
    # -------------------------------------------------------
    
    def _get_system_prompt(self, tool_results: str, response_length: str) -> str:
        """
        Generate system prompt based on tool results and desired response length.
        
        Args:
            tool_results: Results from MarketAgent tools
            response_length: "short", "normal", or "detailed"
        
        Returns:
            System prompt for LLM
        """
        base_prompt = """You are ShareBot, an expert financial assistant specializing in Indian stock markets.

Your role is to provide accurate, data-driven financial insights in a professional yet accessible manner.

**Key Guidelines:**
- Always respond in **markdown format** with proper formatting
- Use headers (##, ###), **bold**, _italic_, bullet points, and tables where appropriate
- Format currency as ₹X,XXX.XX
- Never mention "tools" or "resources" - present information naturally
- Be factual and cite data from the tool results
- If you don't have information, acknowledge it clearly
"""
        
        if tool_results:
            # Tool results available
            if response_length == "short":
                return f"""{base_prompt}

**Tool Results:**
{tool_results}

**Response Instructions:**
- **Length**: SHORT (2-4 lines maximum)
- **Format**: Direct answer only, use bullet points
- **Content**: Just the key data requested, no analysis or recommendations
- **Tone**: Concise and efficient

Example:
"**TCS Current Price**: ₹3,245.50 🔺 +1.2%
- Day Range: ₹3,200 - ₹3,260
- Volume: 2.5M"
"""
            
            elif response_length == "detailed":
                return f"""{base_prompt}

**Tool Results:**
{tool_results}

**Response Instructions:**
- **Length**: DETAILED (200-400 words)
- **Structure**: 
  1. Summary (2-3 lines)
  2. Detailed Analysis with data points
  3. Key Insights
  4. Recommendations (if applicable)
- **Format**: Use markdown headers, tables, bullet points
- **Content**: Comprehensive analysis with context and implications
- **Tone**: Professional and analytical

Provide thorough analysis with supporting data and actionable insights.
"""
            
            else:  # normal
                return f"""{base_prompt}

**Tool Results:**
{tool_results}

**Response Instructions:**
- **Length**: NORMAL (50-100 words)
- **Structure**: Brief overview + key points
- **Format**: Use markdown with bullet points
- **Content**: Balanced information without excessive detail
- **Tone**: Professional and clear

Provide a concise yet informative response.
"""
        
        else:
            # No tool results (general conversation)
            return f"""{base_prompt}

**Response Instructions:**
- You are in general conversation mode
- Answer based on your financial knowledge
- Keep responses concise and helpful
- If user asks for specific stock data, guide them to provide a symbol
- Always respond in markdown format
"""
    
    # -------------------------------------------------------
    # Main Chat Function
    # -------------------------------------------------------
    
    def chat(self, user_query: str, session_id: Optional[str] = None) -> str:
        """
        Process user query and generate response.
        
        Args:
            user_query: User's question or request
            session_id: Optional session ID for memory management
        
        Returns:
            Markdown formatted response
        """
        if not user_query or not user_query.strip():
            return "⚠️ Please provide a query."
        
        user_query = user_query.strip()
        logger.info(f"Processing query: {user_query[:100]}...")
        
        try:
            # Step 1: Detect desired response length
            response_length = self._detect_response_length(user_query)
            logger.info(f"Response length: {response_length}")
            
            # Step 2: Use MarketAgent to get tool results
            tool_response = self.agent.process_query(user_query)
            
            # Check if tool response is an error or "Final Answer"
            # If it contains "Final Answer.", extract the content before it
            if "Final Answer." in tool_response:
                tool_results = tool_response.replace("Final Answer.", "").strip()
            else:
                tool_results = tool_response.strip()
            
            # Step 3: Generate system prompt
            system_prompt = self._get_system_prompt(tool_results, response_length)
            
            # Step 4: Build messages for LLM
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add memory context (last few exchanges)
            if self.memory:
                messages.extend(self.memory[-6:])  # Last 3 turns
            
            # Add current user query
            messages.append({"role": "user", "content": user_query})
            
            # Step 5: Call LLM
            logger.debug("Calling Groq LLM...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self._get_max_tokens(response_length),
            )
            
            assistant_response = response.choices[0].message.content.strip()
            
            # Step 6: Update memory
            self.add_to_memory("user", user_query)
            self.add_to_memory("assistant", assistant_response)
            
            logger.info("Query processed successfully")
            return assistant_response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return f"❌ **Error**: {str(e)}\n\nPlease try again or rephrase your query."
    
    def chat_stream(self, user_query: str, session_id: Optional[str] = None):
        """
        Process user query and generate streaming response.
        
        Args:
            user_query: User's question or request
            session_id: Optional session ID for memory management
        
        Yields:
            Chunks of markdown formatted response
        """
        if not user_query or not user_query.strip():
            yield "⚠️ Please provide a query."
            return
        
        user_query = user_query.strip()
        logger.info(f"Processing streaming query: {user_query[:100]}...")
        
        try:
            # Step 1: Detect desired response length
            response_length = self._detect_response_length(user_query)
            logger.info(f"Response length: {response_length}")
            
            # Step 2: Use MarketAgent to get tool results
            tool_response = self.agent.process_query(user_query)
            
            # Check if tool response is an error or "Final Answer"
            if "Final Answer." in tool_response:
                tool_results = tool_response.replace("Final Answer.", "").strip()
            else:
                tool_results = tool_response.strip()
            
            # Step 3: Generate system prompt
            system_prompt = self._get_system_prompt(tool_results, response_length)
            
            # Step 4: Build messages for LLM
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add memory context (last few exchanges)
            if self.memory:
                messages.extend(self.memory[-6:])  # Last 3 turns
            
            # Add current user query
            messages.append({"role": "user", "content": user_query})
            
            # Step 5: Call LLM with streaming
            logger.debug("Calling Groq LLM with streaming...")
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self._get_max_tokens(response_length),
                stream=True,
            )
            
            # Step 6: Stream response
            full_response = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            # Step 7: Update memory with full response
            self.add_to_memory("user", user_query)
            self.add_to_memory("assistant", full_response.strip())
            
            logger.info("Streaming query processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing streaming query: {e}", exc_info=True)
            yield f"\n\n❌ **Error**: {str(e)}\n\nPlease try again or rephrase your query."
    
    def _get_max_tokens(self, response_length: str) -> int:
        """Get max tokens based on response length."""
        token_limits = {
            "short": 200,
            "normal": 500,
            "detailed": 1500
        }
        return token_limits.get(response_length, 500)
    
    # -------------------------------------------------------
    # Utility Functions
    # -------------------------------------------------------
    
    def get_metrics(self) -> Dict:
        """Get performance metrics."""
        agent_metrics = self.agent.get_metrics()
        return {
            **agent_metrics,
            "memory_size": len(self.memory),
            "max_memory": self.max_memory,
        }
    
    def reset(self):
        """Reset memory and metrics."""
        self.clear_memory()
        self.agent.reset_metrics()
        logger.info("ShareBot reset")


# -------------------------------------------------------
# Convenience Functions for FastAPI
# -------------------------------------------------------

# Global instance (can be replaced with session-based instances)
_sharebot_instance: Optional[ShareBot] = None


def get_sharebot() -> ShareBot:
    """
    Get or create ShareBot instance.
    
    For FastAPI, you might want to use dependency injection instead.
    """
    global _sharebot_instance
    if _sharebot_instance is None:
        _sharebot_instance = ShareBot()
    return _sharebot_instance


def process_query(query: str, session_id: Optional[str] = None) -> str:
    """
    Convenience function to process a query.
    
    Args:
        query: User's question
        session_id: Optional session ID for memory management
    
    Returns:
        Markdown formatted response
    """
    bot = get_sharebot()
    return bot.chat(query, session_id)


# -------------------------------------------------------
# Main (for testing)
# -------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("SHAREBOT - TESTING")
    print("=" * 70)
    
    # Create ShareBot instance
    bot = ShareBot()
    
    # Test queries with different response lengths
    test_queries = [
        ("What is the price of TCS?", "short"),
        ("Tell me about Reliance stock performance", "normal"),
        ("Explain in detail the IT sector performance and provide comprehensive analysis", "detailed"),
        ("Latest IPO listings", "normal"),
    ]
    
    for i, (query, expected_length) in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {query}")
        print(f"Expected Length: {expected_length}")
        print('-'*70)
        
        response = bot.chat(query)
        print(response)
        
        print(f"\n{'='*70}")
    
    # Print metrics
    print("\n\n" + "="*70)
    print("METRICS")
    print("="*70)
    metrics = bot.get_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)
