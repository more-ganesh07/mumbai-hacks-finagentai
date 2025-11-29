
import asyncio
import os
import json
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from groq import AsyncGroq

from src.kite.portbot.agent.master_agent import MasterAgent

load_dotenv(override=True)

def _truncate(s: str, n: int = 8000) -> str:
    return s if len(s) <= n else s[: n - 3] + "..."

class KiteChatbot:
    """
    Professional Portfolio Chatbot with financial advisor tone.
    """
    def __init__(self, user_id: Optional[str] = None):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY in environment")

        self.user_id = user_id or os.getenv("USER_ID", "demo-user")

        self.client = AsyncGroq(api_key=api_key)
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.temperature = float(os.getenv("TEMPERATURE", 0.3))
        self.max_tokens = int(os.getenv("MAX_TOKENS", 400))

        self.narrate = os.getenv("NARRATE_USING_LLM", "1").strip().lower() not in ("0", "false")
        self.memory: List[Dict[str, str]] = []
        self.master: Optional[MasterAgent] = None  

    async def __aenter__(self):
        self.master = await MasterAgent(user_id=self.user_id).__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.master:
            await self.master.__aexit__(exc_type, exc, tb)

    # ------------- LLM streaming -------------
    async def _stream_llm(self, messages: List[Dict[str, str]]) -> str:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )
        
        stream_delay = float(os.getenv("STREAM_DELAY_MS", "20")) / 1000.0
        
        full = ""
        async for chunk in stream:
            delta = getattr(chunk.choices[0], "delta", None)
            if delta and getattr(delta, "content", None):
                token = delta.content
                print(token, end="", flush=True)
                full += token
                
                if stream_delay > 0:
                    await asyncio.sleep(stream_delay)
        print()
        return full

    # ------------- Professional Financial Advisor Prompt -------------
    def _detect_response_length(self, user_input: str) -> str:
        """Detect desired response length from user query."""
        query_lower = user_input.lower()
        
        detailed_keywords = ['detail', 'detailed', 'analyze', 'analysis', 'deep', 'explain in detail', 'comprehensive', 'full analysis']
        if any(kw in query_lower for kw in detailed_keywords):
            return "detailed"
        
        normal_keywords = ['explain', 'why', 'how', 'what happened']
        if any(kw in query_lower for kw in normal_keywords):
            return "normal"
        
        return "short"

    def _build_narration_messages(self, user_input: str, routed_result: Dict[str, Any]) -> List[Dict[str, str]]:
        response_length = self._detect_response_length(user_input)
        
        length_guidance = {
            "short": "ULTRA BRIEF: 2-4 lines max. Just the essential answer. If user asked short question then given short answer if user asked long question then given long answer",
            "normal": "CONCISE: 6-8 lines. Answer the question naturally. No extra fluff.",
            "detailed": "COMPREHENSIVE: Full analysis with context. Still conversational, not robotic."
        }
        
        sys_prompt = (
            "You are analyzing the user's personal portfolio. Speak naturally, like a knowledgeable friend.\\n\\n"
            "If user asked short question then given short answer if user asked long question then given long answer.\\n\\n"
            "Make conversational chat sometime asked follow up question.\\n\\n"
            
            f"RESPONSE LENGTH: {length_guidance[response_length]}\\n\\n"
            
            "CRITICAL - BE NATURAL:\\n"
            "- NEVER say 'Based on the provided data' or 'According to the information'\\n"
            "- NEVER use sections like 'Key Insights:', 'Recommendations:', 'Action Items:', 'Next Steps:'\\n"
            "- Talk about 'your portfolio', 'your holdings', 'your orders' - it's THEIR data\\n"
            "- Be conversational and direct, like explaining to a friend\\n"
            "- Vary your language - don't repeat the same phrases\\n\\n"
            
            "RESPONSE STYLE:\\n"
            "- SHORT queries: Just answer. Table if needed + 1-2 lines. Done.\\n"
            "- NORMAL queries: Answer naturally. Maybe ask a follow-up question sometimes.\\n"
            "- DETAILED queries: Explain thoroughly but still conversationally.\\n"
            "- Use dynamic headings that fit the context (e.g., 'Your Recent Orders', 'Portfolio Performance')\\n"
            "- Sometimes end with a relevant question to keep conversation going\\n\\n"
            
            "SCOPE:\\n"
            "- Portfolio queries: Answer directly\\n"
            "- Market/stock research: 'For market analysis, check out the Market Chat in the sidebar.'\\n\\n"
            
            "FORMATTING:\\n"
            "- Use markdown tables for data\\n"
            "- Currency: ₹1,23,456 format\\n"
            "- P&L: Show sign (+₹500 or -₹200)\\n"
            "- Emojis: Only 📈📉⚠️💡 for trends, NO status emojis\\n"
            "- Bold totals\\n\\n"
                
            "AVOID:\\n"
            "- 'Based on the data provided...'\\n"
            "- 'Key Insights:'\\n"
            "- 'Actionable Recommendations:'\\n"
            "- 'Risk Assessment:'\\n"
            "- 'Next Steps:'\\n"
            "- Any robotic, formal language\\n\\n"
            
            "BE:\\n"
            "- Natural and conversational\\n"
            "- Direct and to the point\\n"
            "- Helpful without being preachy\\n"
            "- Dynamic - change your style based on the question\\n"
        )

        safe_payload = {}
        if "data" in routed_result:
            data = routed_result["data"]
            if isinstance(data, dict) and "results" in data:
                results = data["results"]
                if results and isinstance(results, list):
                    for result in results:
                        if "summary" in result:
                            safe_payload = result["summary"]
                            break
                        elif "data" in result:
                            safe_payload = result["data"]
                            break
            else:
                safe_payload = data
        
        portfolio_context = _truncate(json.dumps(safe_payload, indent=2, ensure_ascii=False), 7000)

        messages: List[Dict[str, str]] = [{"role": "system", "content": sys_prompt}]
        
        for m in self.memory[-8:]:
            messages.append(m)
        
        messages.append({"role": "user", "content": user_input})
        messages.append({
            "role": "assistant", 
            "content": f"I've retrieved your portfolio data:\\n```json\\n{portfolio_context}\\n```"
        })
        messages.append({
            "role": "user", 
            "content": "Based on this data, provide a professional analysis with clear formatting and actionable insights."
        })
        
        return messages

    def _remember(self, role: str, content: str):
        self.memory.append({"role": role, "content": content})
        self._maybe_compress_memory()

    def _maybe_compress_memory(self, max_turns: int = 24):
        """Enhanced memory compression with better context retention."""
        if len(self.memory) <= max_turns:
            return
        
        recent = self.memory[-12:]
        old = self.memory[:-12]
        
        summary_bits = []
        for m in old[-6:]:
            role = "User" if m["role"] == "user" else "Assistant"
            content = m["content"]
            if len(content) > 100:
                content = content[:97] + "..."
            summary_bits.append(f"{role}: {content}")
        
        if summary_bits:
            summary = "Previous conversation context:\\n" + "\\n".join(summary_bits)
            self.memory = [{"role": "system", "content": summary}] + recent
        else:
            self.memory = recent

    # ------------- Chat entry -------------
    async def chat(self, user_input: str) -> str:
        """
        Process user input and return response.
        
        Args:
            user_input: User's question or query
            
        Returns:
            str: The chatbot's response in markdown format
        """
        if not user_input.strip():
            return ""

        # 1) Route query to MasterAgent
        try:
            routed = await self.master.route_query(user_input)
        except Exception as e:
            error_msg = f"I encountered an issue processing your request: {str(e)}. Please try rephrasing your question or ask something else."
            print(f"⚠️ Routing error: {e}\\n")
            print(f"🤖 {error_msg}\\n")
            self._remember("user", user_input)
            self._remember("assistant", error_msg)
            return error_msg

        # 2) Handle errors with better user feedback
        if isinstance(routed, Dict) and routed.get("status") == "error":
            err_msg = routed.get("message") or "I couldn't process that request."
            if "not found" in err_msg.lower():
                err_msg = "I couldn't find the information you're looking for. Could you try rephrasing your question?"
            elif "failed" in err_msg.lower():
                err_msg = f"There was an issue: {err_msg}. Please try again or ask something else."
            
            print(f"⚠️ {err_msg}\\n")
            self._remember("user", user_input)
            self._remember("assistant", err_msg)
            return err_msg

        # 3) Successful execution → LLM narration
        if isinstance(routed, Dict) and routed.get("status") == "success":
            if self.narrate:
                messages = self._build_narration_messages(user_input, routed)
                print("🤖 ", end="", flush=True)
                answer = await self._stream_llm(messages)

                self._remember("user", user_input)
                self._remember("assistant", answer)

                try:
                    memo = json.dumps({"had_tools": True}, ensure_ascii=False)
                    self._remember("assistant", f"[memo]{memo}")
                except Exception:
                    pass

                return answer

            else:
                pretty = self.master.prefer_message(routed)
                print(f"\\n{pretty}\\n")
                self._remember("user", user_input)
                self._remember("assistant", pretty)
                return pretty

        # 4) Fallback conversational mode
        self._remember("user", user_input)
        system_msg = {
            "role": "system",
            "content": (
                "You are a professional financial advisor for Zerodha Kite trading platform.\\n\\n"
                "CURRENT SITUATION:\\n"
                "- Portfolio data is temporarily unavailable\\n"
                "- You can provide general investment guidance and answer questions\\n\\n"
                "GUIDELINES:\\n"
                "- Be helpful and professional\\n"
                "- Never ask for credentials (username, password, PIN, OTP, 2FA, API key)\\n"
                "- Don't fabricate specific portfolio data or account balances\\n"
                "- Provide general market insights and investment principles when appropriate\\n"
                "- Suggest checking back later for specific portfolio information\\n"
            ),
        }

        messages = [system_msg] + self.memory[-10:]
        print("🤖 ", end="", flush=True)
        answer = await self._stream_llm(messages)

        self._remember("assistant", answer)
        return answer

async def main():
    async with KiteChatbot() as bot:
        print("💬 Kite Portfolio Chatbot Ready! (type 'quit' to exit)\\n")
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("👋 Goodbye!")
                    break
                response = await bot.chat(user_input)
                print()
            except KeyboardInterrupt:
                print("\\n👋 Interrupted")
                break
            except Exception as e:
                print(f"❌ Error: {e}\\n")

if __name__ == "__main__":
    asyncio.run(main())
