
import os
import time
import logging
from typing import List, Dict, Optional, Tuple
from groq import Groq
from dotenv import load_dotenv
from src.sharebot.agent.share_agent import Agent

load_dotenv(override=True)

# -------------------------------------------------------
# Logging Setup
# -------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("StockChatbot")

# -------------------------------------------------------
# Configuration Constants
# -------------------------------------------------------
DEFAULT_MAX_MEMORY = 10
DEFAULT_MAX_TOKENS = 1000
DEFAULT_TEMPERATURE = 0.3
LLM_TIMEOUT = 30  # seconds
MAX_RETRIES = 2
MAX_QUERY_LENGTH = 2000  # characters

class StockChatbot:
    """
    Advanced Stock Chatbot with enhanced features:
    - Retry logic for LLM calls
    - Smart memory management
    - Better error handling
    - Performance tracking
    """
    
    def __init__(self, enable_cache: bool = True, cache_ttl: int = 60):
        # Validate API key
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Configuration
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.temperature = float(os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE)))
        self.max_tokens = int(os.getenv("MAX_TOKENS", str(DEFAULT_MAX_TOKENS)))
        self.max_memory = int(os.getenv("MAX_MEMORY", str(DEFAULT_MAX_MEMORY)))
        
        # Initialize clients
        try:
            self.client = Groq(api_key=self.api_key)
            logger.info(f"Initialized Groq client with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise
        
        # Initialize agent with caching
        self.agent = Agent(enable_cache=enable_cache, cache_ttl=cache_ttl)
        
        # Memory management
        self.memory: List[Dict[str, str]] = []
        
        # Performance metrics
        self.metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "llm_calls": 0,
            "llm_errors": 0,
            "avg_response_time": 0.0,
            "total_response_time": 0.0,
        }
    
    # -------------------- Enhanced Memory Management --------------------
    def add_to_memory(self, role: str, content: str):
        """
        Add to memory with validation and automatic compression
        """
        if not content or not isinstance(content, str):
            logger.warning(f"Invalid content for memory: {type(content)}")
            return
        
        content = content.strip()
        if not content:
            return
        
        # Truncate very long messages to prevent memory bloat
        if len(content) > 2000:
            content = content[:1997] + "..."
            logger.debug("Truncated long message for memory")
        
        self.memory.append({"role": role, "content": content})
        
        # Auto-compress if memory gets too large
        if len(self.memory) > self.max_memory * 2:
            self._compress_memory()
    
    def _compress_memory(self):
        """
        Compress old memory by summarizing early messages
        """
        if len(self.memory) <= self.max_memory * 2:
            return
        
        # Keep recent messages, summarize older ones
        keep_count = self.max_memory
        to_compress = self.memory[:-keep_count]
        recent = self.memory[-keep_count:]
        
        if len(to_compress) > 0:
            # Create summary of compressed messages
            summary = self._summarize_memory(to_compress)
            self.memory = [{"role": "assistant", "content": f"[Previous conversation summary]: {summary}"}] + recent
            logger.debug(f"Compressed {len(to_compress)} messages into summary")
    
    def _summarize_memory(self, messages: List[Dict[str, str]]) -> str:
        """
        Create a brief summary of conversation history
        """
        if not messages:
            return ""
        
        # Simple summarization: extract key topics
        topics = []
        for msg in messages:
            content = msg.get("content", "")
            if len(content) > 50:
                # Extract first 50 chars as topic hint
                topics.append(content[:50] + "...")
        
        return " | ".join(topics[:3])  # Keep top 3 topics
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory = []
        logger.info("Memory cleared")
    
    def get_memory_summary(self) -> Dict:
        """Get memory statistics"""
        return {
            "total_messages": len(self.memory),
            "user_messages": sum(1 for m in self.memory if m.get("role") == "user"),
            "assistant_messages": sum(1 for m in self.memory if m.get("role") == "assistant"),
            "memory_limit": self.max_memory * 2,
        }
    
    # -------------------- Enhanced LLM Call with Retry & Timeout --------------------
    def llm_call(
        self, 
        prompt: str, 
        temperature: float = None, 
        max_tokens: int = None, 
        stream: bool = False,
        retry_count: int = 0
    ) -> str:
        """
        Enhanced LLM call with retry logic, timeout, and better error handling
        """
        if not prompt or not prompt.strip():
            logger.warning("Empty prompt provided to LLM")
            return "❌ Empty prompt provided."
        
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        # Validate token limits
        if tokens > 4000:
            logger.warning(f"Token limit too high ({tokens}), capping at 4000")
            tokens = 4000
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            self.metrics["llm_calls"] += 1
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                stream=stream,
                timeout=LLM_TIMEOUT,  # Add timeout
            )
            
            elapsed = time.time() - start_time
            logger.debug(f"LLM call completed in {elapsed:.2f}s")
            
            if stream:
                return response
            else:
                result = response.choices[0].message.content.strip()
                if not result:
                    logger.warning("Empty response from LLM")
                    return "❌ Received empty response from LLM."
                return result
                
        except Exception as e:
            self.metrics["llm_errors"] += 1
            error_msg = str(e)
            logger.error(f"LLM call error (attempt {retry_count + 1}): {error_msg}")
            
            # Retry logic
            if retry_count < MAX_RETRIES and "rate limit" not in error_msg.lower():
                logger.info(f"Retrying LLM call ({retry_count + 1}/{MAX_RETRIES})")
                time.sleep(1 * (retry_count + 1))  # Exponential backoff
                return self.llm_call(prompt, temperature, max_tokens, stream, retry_count + 1)
            
            # Return user-friendly error message
            if "rate limit" in error_msg.lower():
                return "❌ Rate limit exceeded. Please try again in a moment."
            elif "timeout" in error_msg.lower():
                return "❌ Request timed out. Please try again."
            else:
                return f"❌ LLM Error: {error_msg}"
    
    # -------------------- Enhanced Streaming Response --------------------
    def stream_response(self, user_query: str, system_prompt: str) -> str:
        """
        Generate streaming response with memory context and error handling
        """
        # Build messages with memory
        messages = self.memory.copy()
        messages.insert(0, {"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_query})
        
        # Check total message length (rough token estimate: 1 token ≈ 4 chars)
        total_chars = sum(len(m.get("content", "")) for m in messages)
        if total_chars > 12000:  # ~3000 tokens
            logger.warning("Message context too long, trimming memory")
            # Keep system prompt and user query, trim memory
            messages = [messages[0]] + self.memory[-5:] + [messages[-1]]
        
        try:
            start_time = time.time()
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
                timeout=LLM_TIMEOUT,
            )
            
            full_response = ""
            chunk_count = 0
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    chunk_count += 1
                    # Only print in CLI mode (not in API mode)
                    # In API mode, this will be False, so no printing
                    if getattr(self, '_cli_mode', False):
                        print(content, end="", flush=True)
                        time.sleep(0.05)  # Smooth streaming
            
            elapsed = time.time() - start_time
            logger.debug(f"Streamed {chunk_count} chunks in {elapsed:.2f}s")
            
            result = full_response.strip()
            if not result:
                logger.warning("Empty streaming response")
                return "❌ Received empty response."
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Streaming error: {error_msg}")
            
            if "rate limit" in error_msg.lower():
                return "❌ Rate limit exceeded. Please try again in a moment."
            elif "timeout" in error_msg.lower():
                return "❌ Request timed out. Please try again."
            else:
                return f"❌ Streaming error: {error_msg}"
    
    # -------------------- Input Validation --------------------
    def _validate_query(self, user_query: str) -> Tuple[bool, str]:
        """
        Validate user query before processing
        """
        if not user_query or not isinstance(user_query, str):
            return False, "Query must be a non-empty string"
        
        user_query = user_query.strip()
        
        if not user_query:
            return False, "Query cannot be empty"
        
        if len(user_query) > MAX_QUERY_LENGTH:
            return False, f"Query too long (max {MAX_QUERY_LENGTH} characters)"
        
        # Basic sanitization (remove potential injection attempts)
        if any(char in user_query for char in ['\x00', '\r']):
            user_query = user_query.replace('\x00', '').replace('\r', '')
        
        return True, user_query
    
    # -------------------- Enhanced Main Chat Flow --------------------
    def chat(self, user_query: str) -> str:
        """
        Enhanced chat flow with validation, error handling, and metrics
        """
        start_time = time.time()
        self.metrics["total_queries"] += 1
        
        # Validate input
        is_valid, validated_query = self._validate_query(user_query)
        if not is_valid:
            logger.warning(f"Invalid query: {validated_query}")
            return f"❌ {validated_query}"
        
        user_query = validated_query
        
        logger.info(f"Processing query: {user_query[:50]}...")
        
        try:
            # Step 1: Tool planning
            logger.debug("Planning tools...")
            tools = self.agent.plan_tools(user_query, self.llm_call)
            
            # Step 2: Execute tools
            tool_results = ""
            if tools:
                logger.info(f"Executing {len(tools)} tools: {[t.get('name') for t in tools]}")
                tool_results = self.agent.execute_tools(tools, parallel=True)
            else:
                logger.debug("No tools selected, using LLM fallback")
            
            # Step 3: Generate system prompt (pass user_query for intent detection)
            system_prompt = self.agent.get_system_prompt(tool_results, user_query)
            
            # Step 4: Generate response
            if not tools:
                # Fallback: use LLM with memory context
                fallback_prompt = f"""You are a helpful financial assistant. Answer the user's question based on your knowledge and the conversation context.

Previous conversation:
{self._format_memory_for_prompt()}

User Query: {user_query}

Provide a clear, concise answer. If you don't know something, say so."""
                
                response = self.llm_call(
                    fallback_prompt,
                    temperature=0.4,
                    max_tokens=400,
                    stream=False,
                )
            else:
                # Use streaming response with tool results
                response = self.stream_response(user_query, system_prompt)
            
            # Step 5: Update memory
            self.add_to_memory("user", user_query)
            self.add_to_memory("assistant", response)
            
            # Update metrics
            elapsed = time.time() - start_time
            self.metrics["successful_queries"] += 1
            self.metrics["total_response_time"] += elapsed
            self.metrics["avg_response_time"] = (
                self.metrics["total_response_time"] / self.metrics["successful_queries"]
            )
            
            logger.info(f"Query completed in {elapsed:.2f}s")
            
            return response or "No response generated."
            
        except Exception as e:
            self.metrics["failed_queries"] += 1
            error_msg = f"Error processing query: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"❌ {error_msg}"
    
    def _format_memory_for_prompt(self) -> str:
        """Format memory for prompt context"""
        if not self.memory:
            return "No previous conversation."
        
        # Get last few exchanges
        recent = self.memory[-6:] if len(self.memory) > 6 else self.memory
        formatted = []
        for msg in recent:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:200]  # Truncate long messages
            formatted.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(formatted)
    
    # -------------------- Metrics & Utilities --------------------
    def get_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        agent_metrics = self.agent.get_metrics()
        return {
            **self.metrics,
            **agent_metrics,
            "memory": self.get_memory_summary(),
            "success_rate": (
                self.metrics["successful_queries"] / max(1, self.metrics["total_queries"])
            ),
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "llm_calls": 0,
            "llm_errors": 0,
            "avg_response_time": 0.0,
            "total_response_time": 0.0,
        }
        self.agent.reset_metrics()
        logger.info("Metrics reset")

# -------------------------------------------------------
# CLI Functions
# -------------------------------------------------------
def print_banner():
    """Display welcome banner"""
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    print(f"\n🚀 Stock Chatbot - MVP Edition")
    print(f"📊 Model: {model}")
    print(f"💡 Ask detailed or brief stock queries!\n")

def main():
    """Main CLI loop"""
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Missing GROQ_API_KEY in environment.\n")
        return
    
    try:
        chatbot = StockChatbot()
        print_banner()
        
        print("=" * 60)
        print("🤖 Ready! Ask me anything about stocks.")
        print("Commands: 'clear' to clear memory, 'exit' to quit")
        print("=" * 60 + "\n")
        
        while True:
            try:
                user_input = input("💭 You: ").strip()
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("\n👋 Goodbye! Happy investing! 📈\n")
                    break
                
                if user_input.lower() == "clear":
                    chatbot.clear_memory()
                    continue
                
                if user_input.lower() == "metrics":
                    metrics = chatbot.get_metrics()
                    print("\n📊 Performance Metrics:")
                    print(f"  Total Queries: {metrics['total_queries']}")
                    print(f"  Success Rate: {metrics['success_rate']:.1%}")
                    print(f"  Avg Response Time: {metrics['avg_response_time']:.2f}s")
                    print(f"  Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.1%}")
                    print(f"  Memory: {metrics['memory']['total_messages']} messages\n")
                    continue
                
                print("\n" + "=" * 60)
                chatbot._cli_mode = True  # Enable CLI mode for streaming
                response = chatbot.chat(user_input)
                # Response is already printed if streamed, otherwise print it
                if not getattr(chatbot, '_cli_mode', False) or not response.startswith("🤖"):
                    print(f"\n🤖 Agent: {response}")
                print("=" * 60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye! 📈\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                logger.error(f"CLI error: {e}", exc_info=True)
    
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}\n")
        logger.error(f"Initialization error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
