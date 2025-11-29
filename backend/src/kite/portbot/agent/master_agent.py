
# C:\Users\Ganesh.More\Desktop\GaneshMore\KiteInfi\src\kite\portbot\agent\master_agent.py
import os
import time
from typing import Any, Dict, List, Optional

from src.kite.mcpclient.kite_mcp_client import KiteMCPClient
from src.kite.portbot.tool.login import LoginAgent
from src.kite.portbot.tool import (
    AccountAgent,
    PortfolioAgent,
    OrdersAgent,
    MarketAnalysisAgent,
)
from src.kite.portbot.router import ToolRouter


def _fmt_kwargs(d: Dict[str, Any], max_len: int = 120) -> str:
    if not d:
        return ""
    s = ", ".join(f"{k}={repr(v)}" for k, v in d.items())
    return (s[: max_len - 3] + "..." if len(s) > max_len else s)


class MasterAgent:
    """
    Top-level orchestrator for all Kite sub-agents.

    NEW (2025 revision):
    --------------------
    ✔ Uses SSE-only KiteMCPClient (connection stable for hosted MCP)
    ✔ Explicit login step via LoginAgent (remove ensure_logged_in)
    ✔ All other agents receive the same client + shared state
    ✔ Router support unchanged
    """

    def __init__(self, user_id: str):
        self.user_id = user_id

        # MCP Client (SSE-only)
        self.kite_client: Optional[KiteMCPClient] = None

        # Will contain: session object, user-validated flags, etc.
        self.shared_state: Dict[str, Any] = {}

        # Agent registry (populated after login)
        self.agents: Dict[str, Any] = {}

        self._catalog: List[Dict[str, Any]] = []
        self._router: Optional[ToolRouter] = None

        self._initialized = False
        self._trace = os.getenv("AGENT_TRACE", "1").strip().lower() not in ("0", "false")

    # --------------------------------------------------------------------------
    # Async context lifecycle
    # --------------------------------------------------------------------------
    async def __aenter__(self):
        """
        Steps:
        1. Connect KiteMCPClient (SSE-based)
        2. Run LoginAgent (interactive) if needed
        3. Initialize all other agents
        4. Build router catalog
        """
        # 1) Connect SSE-only client (returns the KiteMCPClient instance)
        # Note: KiteMCPClient().__aenter__() returns the instance in this codebase
        self.kite_client = await KiteMCPClient().__aenter__()

        # 1.b) If the client exposes restore_session(), try it
        try:
            restore_ok = False
            if hasattr(self.kite_client, "restore_session"):
                # restore_session might be async or sync
                res = self.kite_client.restore_session()
                if hasattr(res, "__await__"):
                    restore_ok = await res
                else:
                    restore_ok = bool(res)

                if restore_ok:
                    # attempt to pick up restored session into shared_state
                    session_obj = getattr(self.kite_client, "session", None) or getattr(self.kite_client, "_client", None) and getattr(self.kite_client._client, "session", None)
                    if session_obj:
                        self.shared_state["session"] = session_obj
        except Exception:
            # best-effort restore; ignore failures and continue to validate/login
            pass

        # 2) Try existing session first via validate_session() if available
        is_valid = False
        try:
            validate = getattr(self.kite_client, "validate_session", None)
            if callable(validate):
                val = validate()
                if hasattr(val, "__await__"):
                    is_valid = await val
                else:
                    is_valid = bool(val)
        except Exception:
            is_valid = False

        if not is_valid:
            print("\n🔑 No active session. Attempting login via LoginAgent...")
            login_agent = LoginAgent(self.kite_client, self.shared_state)
            login_result = await login_agent.run(tool_name="login")

            # Normalize different return shapes and be tolerant
            if isinstance(login_result, tuple):
                # sometimes tools return (result, meta)
                login_result = login_result[0] if login_result else {}

            if not isinstance(login_result, dict):
                login_result = {"status": "error", "message": repr(login_result)}

            status = login_result.get("status") or (login_result.get("result") and "success")
            if status != "success":
                # Try to provide more debugging info if possible
                raise RuntimeError(f"Login failed: {login_result.get('message') or repr(login_result)}")

            print(f"Session: {self.shared_state.get('session')}")

            # ensure session is available in shared_state — login agent should store it,
            # but do a best-effort fetch from underlying client
            if "session" not in self.shared_state:
                session_obj = (
                    getattr(self.kite_client, "session", None)
                    or getattr(self.kite_client, "_client", None) and getattr(self.kite_client._client, "session", None)
                    or login_result.get("session")
                    or login_result.get("data", {}).get("session")
                )
                if session_obj:
                    self.shared_state["session"] = session_obj

            print("✅ Login completed. Session stored in shared_state.")
        else:
            print("🔐 Existing session validated.")
            login_agent = LoginAgent(self.kite_client, self.shared_state)  # keep it registered

        # 3) Create other agents
        self.agents = {
            "login":       login_agent,  # optional exposure
            "account":     AccountAgent(self.kite_client, self.shared_state),
            "portfolio":   PortfolioAgent(self.kite_client, self.shared_state),
            "orders":      OrdersAgent(self.kite_client, self.shared_state),
            "market_analysis": MarketAnalysisAgent(self.kite_client, self.shared_state),
        }

        # 4) Router
        self._catalog = self._build_catalog()
        enable_router = os.getenv("ROUTER_ENABLED", "1").strip().lower() not in ("0", "false")
        self._router = ToolRouter(self._catalog) if enable_router else None

        self._initialized = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.kite_client:
            # If client has a save_session hook, call it (best-effort)
            try:
                saver = getattr(self.kite_client, "save_session", None)
                if callable(saver):
                    res = saver()
                    if hasattr(res, "__await__"):
                        await res
            except Exception:
                pass

            await self.kite_client.__aexit__(exc_type, exc, tb)

    # --------------------------------------------------------------------------
    # Direct Execution
    # --------------------------------------------------------------------------
    async def execute(self, agent_name: str, tool_name: str, **kwargs: Any) -> Dict[str, Any]:
        if not self._initialized:
            return {
                "status": "error",
                "message": "MasterAgent not initialized. Use 'async with MasterAgent(...)'.",
            }

        agent = self.agents.get(agent_name)
        if not agent:
            return {"status": "error", "message": f"Agent '{agent_name}' not found"}

        if not self._has_tool(agent, tool_name):
            return {"status": "error", "message": f"Tool '{tool_name}' not found on '{agent_name}'"}

        if self._trace:
            print(f"🧭 [AGENT] {agent_name}.{tool_name}({_fmt_kwargs(kwargs)})")

        t0 = time.perf_counter()
        try:
            result = await agent.run(tool_name=tool_name, **kwargs)
            dt = (time.perf_counter() - t0) * 1000.0

            if self._trace:
                print(f"✅ [DONE] {agent_name}.{tool_name} — {result.get('status')} — {dt:.0f} ms")

            return result
        except Exception as e:
            dt = (time.perf_counter() - t0) * 1000.0
            if self._trace:
                print(f"❌ [FAIL] {agent_name}.{tool_name} — {e} — {dt:.0f} ms")
            return {"status": "error", "message": str(e)}

    # --------------------------------------------------------------------------
    # Query Routing
    # --------------------------------------------------------------------------
    async def route_query(self, user_query: str) -> Dict[str, Any]:
        print(f"Routing query: {user_query}")
        if not self._router:
            return {"status": "error", "message": "Router disabled"}

        selection = await self._router.route(user_query)

        # Single-step tool
        if selection and selection.get("agent") and selection.get("tool"):
            step = {
                "agent": selection["agent"],
                "tool": selection["tool"],
                "arguments": selection.get("arguments", {}) or {},
            }

            if self._is_valid_selection(step):
                res = await self.execute(step["agent"], step["tool"], **step["arguments"])
                return {
                    "status": res.get("status"),
                    "data": {
                        "steps": [step],
                        "results": [self._compact_result(res)],
                    },
                    "message": res.get("message"),
                }

        # Multi-step plan
        if selection and isinstance(selection.get("plan"), list):
            steps = []
            results = []

            for s in selection["plan"]:
                step = {
                    "agent": s["agent"],
                    "tool": s["tool"],
                    "arguments": s.get("arguments", {}) or {},
                }

                if not self._is_valid_selection(step):
                    return {"status": "error", "message": "Router produced invalid step."}

                steps.append(step)
                r = await self.execute(step["agent"], step["tool"], **step["arguments"])
                results.append(self._compact_result(r))

            return {
                "status": "success",
                "data": {"steps": steps, "results": results},
            }

        return {
            "status": "error",
            "message": (
                "I couldn't map that to a portfolio tool. Try: "
                "'show holdings', 'check margins', 'show orders', "
                "'account details', or 'show positions'."
            ),
        }

    # --------------------------------------------------------------------------
    # Helper utilities
    # --------------------------------------------------------------------------
    def list_agents(self) -> List[str]:
        return list(self.agents.keys())

    def get_tools_catalog(self) -> List[Dict[str, Any]]:
        return self._catalog.copy()

    def prefer_message(self, result: Dict[str, Any]) -> str:
        if not isinstance(result, dict):
            return str(result)
        return result.get("message") or (
            str(result.get("data")) if "data" in result else str(result)
        )

    def _build_catalog(self) -> List[Dict[str, Any]]:
        catalog = []
        for agent_name, agent in self.agents.items():
            for t in getattr(agent, "tools", []):
                catalog.append({
                    "agent": agent_name,
                    "tool": t.get("name"),
                    "description": t.get("description", ""),
                    "parameters": t.get("parameters", {}),
                })
        return sorted(catalog, key=lambda x: (x["agent"], x["tool"]))

    @staticmethod
    def _has_tool(agent_obj: Any, tool_name: str) -> bool:
        return any(t.get("name") == tool_name for t in getattr(agent_obj, "tools", []))

    def _is_valid_selection(self, sel: Dict[str, Any]) -> bool:
        """Validate agent + tool + arguments."""
        agent = sel.get("agent")
        tool = sel.get("tool")
        if not agent or not tool:
            return False

        for item in self._catalog:
            if item["agent"] == agent and item["tool"] == tool:
                params = item.get("parameters", {}) or {}
                args = sel.get("arguments", {}) or {}

                # Remove unknown arguments
                for k in list(args.keys()):
                    if k not in params:
                        args.pop(k, None)

                sel["arguments"] = args
                return True

        return False

    @staticmethod
    def _compact_result(res: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compact result for LLM consumption.
        Prefers 'summary' field (clean data without source) over 'data' field.
        """
        out = {"status": res.get("status")}
        
        if "message" in res:
            out["message"] = res["message"]
        
        # Prefer summary (excludes source field, includes totals)
        if "summary" in res:
            out["summary"] = res["summary"]
        elif "data" in res:
            # Fallback to data if summary not available
            out["data"] = res["data"]
        
        return out












