import sseclient
import requests

SSE_URL = "http://localhost:8090/sse"

print("⚡ Connecting to MCP SSE stream...")
response = requests.post(SSE_URL, json={"name": "get_profile", "arguments": {}}, stream=True)
client = sseclient.SSEClient(response)

for event in client.events():
    print(f"EVENT: {event.event}")
    print(f"DATA: {event.data}")
