

# src/kite/portbot/tool/login.py

import webbrowser
from typing import Any, Dict, Optional

from src.kite.portbot.base import Agent
from src.kite.mcpclient.kite_mcp_client import KiteMCPClient


class LoginAgent(Agent):
    name = "login"
    description = "Handles Kite authentication via MCP login tool."

    tools = [
        {
            "name": "login",
            "description": "Login to Zerodha Kite (interactive browser login).",
            "parameters": {}
        }
    ]

    def __init__(self, kite_client: KiteMCPClient, shared_state: Optional[Dict[str, Any]] = None):
        super().__init__(shared_state)
        self.kite_client = kite_client

    async def run(self, tool_name: str = "login", **kwargs: Any) -> Dict[str, Any]:
        if tool_name != "login":
            raise ValueError(f"Unknown tool: {tool_name}")
        return await self._login()

    async def _login(self) -> Dict[str, Any]:
        print("🔐 Initiating Kite login flow…")

        login_res = await self.kite_client.call("login", {})
        login_url = self.kite_client.extract_login_url(login_res)

        if not login_url:
            return {
                "status": "error",
                "message": "Could not extract login URL from MCP login()"
            }

        print(f"\n🔗 Login URL:\n{login_url}\n")
        try:
            webbrowser.open(login_url)
            print("🌐 Login URL opened in browser.")
        except Exception:
            print("⚠️ Could not open browser automatically.")

        input("\n⏳ Complete login in browser → then press ENTER here… ")

        # identical to working version
        session_obj = getattr(self.kite_client._client, "session", {})

        self.shared_state["session"] = session_obj

        print("🔐 Login successful. MCP session stored.")

        return {
            "status": "success",
            "message": "Login completed successfully.",
            "login_url": login_url,
            "session": session_obj,
        }
