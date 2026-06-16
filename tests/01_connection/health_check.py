import httpx
import json
import time
from datetime import datetime
from pathlib import Path

BASE_URL = "https://yargimcp.surucu.dev"
RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

def log(msg, status="INFO"):
    icons = {"OK": "[OK]", "FAIL": "[FAIL]", "INFO": "[INFO]", "WARN": "[WARN]"}
    print(f"{icons.get(status, '.')} {msg}")

def test_health():
    log("Health endpoint kontrol ediliyor...", "INFO")
    try:
        r = httpx.get(f"{BASE_URL}/health", timeout=10)
        if r.status_code == 200:
            log(f"Health OK - {r.status_code} | {r.text[:100]}", "OK")
            return True
        else:
            log(f"Health FAIL - HTTP {r.status_code}", "FAIL")
            return False
    except Exception as e:
        log(f"Baglanti hatasi: {e}", "FAIL")
        return False

def parse_sse_or_json(r):
    text = r.text.strip()
    if text.startswith("{"):
        return r.json()
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except:
                pass
    return {}

def mcp_request(payload: dict, session_id: str = None):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    if session_id:
        headers["mcp-session-id"] = session_id
    r = httpx.post(f"{BASE_URL}/mcp", json=payload, headers=headers, timeout=30)
    return r

def initialize_session():
    log("MCP session baslatiliyor (initialize)...", "INFO")
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
    log(f"Initialize HTTP {r.status_code}", "OK" if r.status_code == 200 else "WARN")

    session_id = r.headers.get("mcp-session-id")
    log(f"Session ID: {session_id}", "INFO" if session_id else "WARN")

    try:
        data = r.json()
        log(f"Server info: {json.dumps(data.get('result',{}).get('serverInfo',{}))}", "INFO")
    except:
        pass

    return session_id

def test_tool_list(session_id=None):
    log("Tool listesi aliniyor...", "INFO")
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    r = mcp_request(payload, session_id)
    log(f"HTTP {r.status_code}", "OK" if r.status_code == 200 else "WARN")

    try:
        data = parse_sse_or_json(r)
        tools = data.get("result", {}).get("tools", [])

        log(f"Toplam {len(tools)} tool", "OK" if tools else "WARN")
        for t in tools[:10]:
            name = t.get('name','?')
            print(f"   . {name}")
            # Bedesten tool detaylarını ekrana yazdir
            if "bedesten" in name.lower():
                schema = t.get('inputSchema', {})
                if 'properties' in schema and 'court_types' in schema['properties']:
                    enum_vals = schema['properties']['court_types'].get('items', {}).get('enum', [])
                    print(f"      court_types enum: {enum_vals}")
        return tools
    except Exception as e:
        log(f"Parse hatasi: {e}", "FAIL")
        log(f"Ham yanit: {r.text[:300]}", "INFO")
        return []

def test_search(session_id=None):
    log("Yargitay arama testi...", "INFO")
    payload = {
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {
            "name": "search_yargitay_decisions",
            "arguments": {"keyword": "itirazin iptali", "page_size": 3}
        }
    }
    r = mcp_request(payload, session_id)
    log(f"HTTP {r.status_code}", "OK" if r.status_code == 200 else "WARN")

    data = parse_sse_or_json(r)
    content = data.get("result", {}).get("content", [])
    if content:
        result_text = content[0].get("text", "")
        is_error = data.get("result", {}).get("isError", False)
        log(f"Icerik: {len(result_text)} karakter, error={is_error}", "OK" if not is_error else "WARN")
        print(result_text[:500])
        return {"status": r.status_code, "char_count": len(result_text), "is_error": is_error, "preview": result_text[:500]}
    log("Bos yanit", "WARN")
    return {"status": r.status_code}

if __name__ == "__main__":
    print("=" * 60)
    print("  yargi-mcp FAZ 1 v2 - Protokol Testi")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    report = {"timestamp": datetime.now().isoformat(), "tests": {}}

    report["tests"]["health"] = test_health()
    session_id = initialize_session()
    report["tests"]["session_id"] = session_id
    tools = test_tool_list(session_id)
    report["tests"]["tool_count"] = len(tools)
    report["tests"]["tools"] = [t.get("name") for t in tools]
    report["tests"]["search"] = test_search(session_id)

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"faz1_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print("\n" + "=" * 60)
    log(f"Kaydedildi: {out}", "OK")
    print("=" * 60)
