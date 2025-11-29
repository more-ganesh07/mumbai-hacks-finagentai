import requests
import json

MCP_URL = "http://localhost:8090/mcp"

# JSON-RPC style payload as per Model Context Protocol spec
payload = {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "createSession",
    "params": {
        "provider": "kite",
        "user_id": "ganesh.local"
    }
}

print(f"🧩 Creating session at {MCP_URL} ...")
response = requests.post(MCP_URL, json=payload)

print("🔍 Status Code:", response.status_code)
if response.status_code == 200:
    try:
        data = response.json()
        print("✅ Server response:")
        print(json.dumps(data, indent=2))
    except Exception:
        print("⚠️ Response not JSON:", response.text)
else:
    print("❌ Error:", response.text)
