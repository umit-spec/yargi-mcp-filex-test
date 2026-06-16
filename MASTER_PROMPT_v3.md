# MASTER PROMPT v3 — FAZ 4 (Filex Integration Testing)

## PROJECT CONTEXT

**Name:** yargi-mcp × Filex Integration Test  
**Repo:** C:\yargi-mcp-filex-test  
**Python:** 3.14 | **Dependencies:** httpx, rich, python-dotenv  
**Status:** 3 phases complete, Faz 4 investigation needed

**Server:** https://yargimcp.surucu.dev (v0.2.0)  
**Target:** Evaluate Emsal (UYAP) and Yargıtay (Bedesten) source quality for Filex gold.db seeding

---

## COMPLETED PHASES SUMMARY

### FAZ 1 ✅ — Connection & Health Check
- Server health: **OK** (200, v0.2.0)
- Protocol: **Streamable HTTP MCP** (SSE format: `event: message\ndata: {...}`)
- Session: `initialize` handshake required → `Mcp-Session-Id` header
- Tools available: **26 total**
  - Key tools: `search_emsal_detailed_decisions`, `search_bedesten_unified`
  - ❌ `search_yargitay_decisions` does NOT exist
- Response time: ~300-400ms

**Files:**
- `tests/01_connection/health_check.py` — Logs health, tool list, SSE parsing
- `results/faz1_v2_*.json` — Tool list (26 items), session ID

### FAZ 2 🟨 — Decision Quality (Partial)

#### Emsal (UYAP) — ✅ WORKING
**Tool:** `search_emsal_detailed_decisions`

**Input:**
```json
{
  "keyword": "menfi tespit borc",
  "page_size": 10  (optional)
}
```

**Output:** JSON metadata list (NOT markdown)
```json
{
  "decisions": [
    {
      "id": "1211620800",
      "daire": "Diyarbakır Bölge Adliye Mahkemesi 4. Hukuk Dairesi",
      "esasNo": "2026/2283",
      "kararNo": "2026/1274",
      "kararTarihi": "04.06.2026",
      "arananKelime": "menfi tespit borc",
      "durum": "KESİNLEŞTİ",
      "document_url": "https://emsal.uyap.gov.tr/getDokuman?id=1211620800"
    }
    // ... 9 more
  ]
}
```

**Full Text Retrieval:** 2-step pipeline
1. Search → metadata list (10 results)
2. `get_emsal_document_markdown({"id": "1211620800"})` → full markdown

**Metadata Coverage:** ✓ 4/4 fields
- mahkeme ✓ (from `daire`)
- esasNo ✓
- kararNo ✓
- kararTarihi ✓

**Files:**
- `tests/02_quality/emsal_test.py` — Search + metadata parse
- `results/faz2_emsal_*.json` — Test results (3 searches, 10 results each)

#### Yargıtay (Bedesten) — ⚠️ BLOCKED
**Tool:** `search_bedesten_unified` (presumed)

**Problem:**
- Tool exists in list but `inputSchema` returns **empty**
- Parameters undefined: `phrase` vs `keyword`, `court_types` enum values unknown
- Test failed: validation error on `court_types`

**Investigation needed:** GitHub README, docs, or reverse-engineer from UI

**Files:**
- `tests/02_quality/yargitay_test.py` — Framework ready, params TBD
- `results/faz2_yargitay_*.json` — Failed (param validation error)

### FAZ 3 ✅ — Validator Compatibility
**Tool:** `tests/03_validator/format_check.py` — Regex parsing + schema mapping

**Mock Results:**
- Emsal: 7/8 fields (missing: chamber)
- Yargıtay: 5/8 fields (missing: case_number, decision_number, decision_date)

**Filex gold.db Schema:**
```python
{
  "court_name": str,
  "chamber": str | None,
  "case_number": str,          # REQUIRED
  "decision_number": str,       # REQUIRED
  "decision_date": str (DD.MM.YYYY),
  "full_text": str,
  "authority_rank": int,        # ybk>yhgk>yargitay_daire>bam_daire>ilk_derece>diger
  "capture_method": str,        # "yargi_mcp"
  "validation_status": str      # "pending" (awaits Cüneyt approval)
}
```

**Regex Patterns (Tested):**
- Esas No: `\d{4}/\d+` ✓
- Karar No: `\d{4}/\d+` ✓
- Date: `\d{1,2}[./]\d{1,2}[./]\d{4}` ✓

**Files:**
- `tests/03_validator/format_check.py` — Mock parsing
- `results/faz3_*.json` — Coverage metrics

---

## WORKING HELPER FUNCTIONS (common.py)

```python
import httpx, json
from pathlib import Path

BASE_URL = "https://yargimcp.surucu.dev"

def parse_sse_or_json(response):
    """Parse SSE format or plain JSON"""
    text = response.text.strip()
    if text.startswith("{"):
        try: return response.json()
        except: pass
    for line in text.split("\n"):
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except: pass
    return {}

def mcp_request(payload, session_id=None):
    """Send MCP protocol request"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    if session_id:
        headers["mcp-session-id"] = session_id
    return httpx.post(f"{BASE_URL}/mcp", json=payload, headers=headers, timeout=30)

def initialize_session():
    """Initialize MCP session, return session_id"""
    payload = {
        "jsonrpc": "2.0", "id": 0, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "filex-test", "version": "0.1.0"}
        }
    }
    r = mcp_request(payload)
    sid = r.headers.get("mcp-session-id") or r.headers.get("MCP-Session-ID")
    return sid

def call_tool(tool_name, arguments, session_id=None, req_id=1):
    """Call MCP tool and return parsed result"""
    payload = {
        "jsonrpc": "2.0", "id": req_id, "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments}
    }
    r = mcp_request(payload, session_id)
    data = parse_sse_or_json(r)
    content = data.get("result", {}).get("content", [])
    return content[0].get("text", "") if content else ""
```

---

## FAZ 4 GOALS & TASKS

### TASK 1 — Emsal Full-Text Pipeline
**Status:** 🟡 Ready to execute

**Steps:**
1. Read latest `results/faz2_emsal_*.json`
2. Extract first decision's `id` field
3. Call `call_tool("get_emsal_document_markdown", {"id": "..."}, session_id)`
4. Parse returned markdown:
   - Character count
   - Truncation check (5000 char limit)?
   - Chamber regex works on full text?
   - Field extraction success rate
5. Save results to `results/faz4_emsal_fulltext_*.json`

**Success Criteria:**
- Full text retrieved > 500 chars
- No truncation
- Regex parses case_number, decision_number, date
- chamber field found in text

### TASK 2 — Bedesten Parameter Discovery
**Status:** 🔴 Blocked (needs research)

**Sources to check:**
1. https://github.com/saidsurucu/yargi-mcp → README, docs/, examples/
2. API schema endpoint (if exists)
3. Tool description text parsing
4. Reverse-engineer from UI or OpenAPI spec

**Find:**
- Correct parameter names: `phrase` or `keyword`?
- `court_types` enum values: `YARGITAYKARAR`, `YARGITAY_HUKUK`, others?
- Date range parameters?
- Pagination?

**Once found:**
- Update `tests/02_quality/yargitay_test.py` with correct params
- Run test
- Document in findings.md

### TASK 3 — Real Data Validation (if Bedesten resolved)
**Status:** ⏳ Depends on Task 2

**Steps:**
1. Use corrected yargitay_test.py
2. Run with real Bedesten queries
3. Extract metadata from response
4. Compare against Filex schema
5. Update Faz 3 mock test with real coverage metrics

### TASK 4 — Final Decision & findings.md Update
**Status:** 🟡 Ready after Tasks 1-3

**Decision Options:**
1. **ENTEGRE ET:** Emsal pipeline production-ready
   - Add to Filex bulk seed phase
   - Schedule periodic Emsal crawl
   - Yargıtay added when Bedesten resolved
   
2. **REDDET:** Too unstable / too risky
   - Manual Filex input continues
   - Revisit in Q3
   
3. **BEKLE:** Partial integration
   - Emsal seeding only, hold Yargıtay

**Update findings.md:**
- Finalize decision with rationale
- Document Bedesten blocker (if unresolved)
- Next steps for Cüneyt Bey

---

## IMPORTANT CONTEXT: Filex Role

This test **does NOT replace** Filex's existing workflow:
- Chrome Extension + Manual UI entry → gold.db (continues)
- Cüneyt Bey review → validation_status="approved" (continues)

**yargi-mcp role:** Optional PRE-FETCH / BULK SEED layer
- Provide Emsal/Yargıtay metadata for faster gold.db growth
- Still requires Cüneyt validation before production use
- Data tagged with `capture_method: "yargi_mcp"`, `validation_status: "pending"`

---

## OUTPUT DELIVERABLES (by end of Faz 4)

```
results/
├── faz4_emsal_fulltext_20260616_*.json    ← Task 1 output
├── faz4_bedesten_discovery_*.json         ← Task 2 findings
└── faz4_summary.json                      ← Task 4 final decision

docs/
└── findings.md                            ← Updated with decision
```

**findings.md Final Section:** Clear ENTEGRE ET / REDDET / BEKLE decision with:
- Emsal readiness level
- Yargıtay blockers (if any)
- Timeline for next phase
- Filex integration steps (if approved)

---

## KEY CONTACTS & ESCALATION

- **Cüneyt Bey:** gold.db strategy, validation approval
- **saidsurucu/yargi-mcp:** GitHub issues for parameter docs

---

## NEXT CLAUDE (Faz 4)

Start here: `docs/findings.md` (current status) + `MASTER_PROMPT_v3.md` (this file)  
Working code: `tests/common.py` (helpers), `tests/0x_*/` (implementations)  
Test results: `results/` (JSON outputs)

Focus on:
1. Emsal full-text fetch (high confidence task)
2. Bedesten parameter research (medium risk)
3. Final decision + implementation plan

Good luck! 🚀

---

*Last updated: 16.06.2026*
