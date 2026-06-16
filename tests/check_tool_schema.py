import httpx
import json
from pathlib import Path

BASE_URL = "https://yargimcp.surucu.dev"

def parse_sse_or_json(r):
    text = r.text.strip()
    if text.startswith("{"):
        return r.json()
    for line in text.split("\n"):
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except:
                pass
    return {}

# Initialize
init_payload = {
    "jsonrpc": "2.0", "id": 0, "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "schema-check", "version": "0.1"}
    }
}
r_init = httpx.post(f"{BASE_URL}/mcp", json=init_payload, timeout=30)
session_id = r_init.headers.get("mcp-session-id")
print(f"Session: {session_id}")

# Get tools
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}
if session_id:
    headers["mcp-session-id"] = session_id

list_payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
r_list = httpx.post(f"{BASE_URL}/mcp", json=list_payload, headers=headers, timeout=30)

data = parse_sse_or_json(r_list)
tools = data.get("result", {}).get("tools", [])

# Find Bedesten
for t in tools:
    if "bedesten" in t.get("name", "").lower():
        print(f"\nTool: {t['name']}")
        print(f"Desc: {t.get('description', '')[:100]}")
        schema = t.get("inputSchema", {})
        if "properties" in schema:
            for key, prop in schema["properties"].items():
                print(f"\n{key}:")
                if "enum" in prop:
                    print(f"  enum: {prop['enum']}")
                elif "items" in prop and "enum" in prop.get("items", {}):
                    print(f"  items.enum: {prop['items']['enum']}")
                else:
                    print(f"  {json.dumps(prop)[:150]}")

# Also check search_bedesten_unified specifically
print("\n\n=== search_bedesten_unified details ===")
for t in tools:
    if t.get("name") == "search_bedesten_unified":
        schema = t.get("inputSchema", {})
        print(json.dumps(schema, ensure_ascii=False, indent=2)[:2000])
