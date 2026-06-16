import httpx
import json

BASE_URL = "https://yargimcp.surucu.dev"

def log(msg, status="INFO"):
    icons = {"OK": "[OK]", "FAIL": "[FAIL]", "INFO": "[INFO]", "WARN": "[WARN]"}
    print(f"{icons.get(status, '.')} {msg}")

def parse_sse_or_json(response):
    """Parse SSE format (event: message\ndata: {...}) atau plain JSON"""
    text = response.text.strip()
    if text.startswith("{"):
        try:
            return response.json()
        except:
            pass
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except:
                pass
    return {}

def mcp_request(payload, session_id=None):
    """MCP protokol isteği gönder"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    if session_id:
        headers["mcp-session-id"] = session_id
    return httpx.post(f"{BASE_URL}/mcp", json=payload, headers=headers, timeout=30)

def initialize_session():
    """MCP session başlat, session_id döndür"""
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "filex-test", "version": "0.1.0"}
        }
    }
    r = mcp_request(payload)
    session_id = r.headers.get("mcp-session-id") or r.headers.get("MCP-Session-ID")
    if session_id:
        log(f"Session: {session_id[:16]}...", "OK")
    else:
        log("No session ID in headers, using request-scoped", "WARN")
        session_id = None
    return session_id

def call_tool(tool_name, arguments, session_id=None, req_id=1):
    """Tool çağır ve sonuç döndür"""
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments}
    }
    r = mcp_request(payload, session_id)
    return parse_sse_or_json(r)
