import json
import time
import re
from datetime import datetime
from pathlib import Path
from sys import path as syspath

syspath.insert(0, str(Path(__file__).parent.parent))
from common import log, parse_sse_or_json, initialize_session, call_tool

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

TEST_CASES = [
    {"aciklama": "Emsal - menfi tespit", "keyword": "menfi tespit borc"},
    {"aciklama": "Emsal - icra tazminati", "keyword": "icra inkar tazminati"},
    {"aciklama": "Emsal - kiralık tahliye", "keyword": "tahliye taahhutnamesi kira"},
]

def extract_emsal_metadata(text):
    """Emsal kararından Filex uyumlu metadata extract et"""
    meta = {
        "mahkeme": None,
        "esas_no": None,
        "karar_no": None,
        "tarih": None,
        "markdown_format": False,
        "has_full_text": len(text) > 200,
        "truncated": len(text) >= 4900,
        "char_count": len(text),
    }

    # Mahkeme Adı
    m = re.search(r'Mahkeme[:\s]+(.+?)(?:\n|$)', text, re.I)
    if m:
        meta["mahkeme"] = m.group(1).strip()

    # Esas No
    m = re.search(r'Esas\s+No[:\s]+(\d{4}/\d+)', text, re.I)
    if m:
        meta["esas_no"] = m.group(1)

    # Karar No
    m = re.search(r'Karar\s+No[:\s]+(\d{4}/\d+)', text, re.I)
    if m:
        meta["karar_no"] = m.group(1)

    # Tarih (DD.MM.YYYY veya DD/MM/YYYY)
    m = re.search(r'(?:Tarih|Date)[:\s]+(\d{1,2})[./](\d{1,2})[./](\d{4})', text, re.I)
    if m:
        meta["tarih"] = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"

    # Markdown format (# başlığı veya ** bold)
    meta["markdown_format"] = text.startswith("#") or "**" in text or "## " in text

    return meta

def test_emsal_detailed(case, session_id, req_id):
    """search_emsal_detailed_decisions ile emsal karası ara"""
    log(f"Test: {case['aciklama']}", "INFO")

    try:
        start = time.time()
        data = call_tool(
            "search_emsal_detailed_decisions",
            {"keyword": case["keyword"]},
            session_id, req_id
        )
        elapsed = time.time() - start

        content = data.get("result", {}).get("content", [])
        if not content:
            log("Sonuç yok", "WARN")
            return {"case": case["aciklama"], "status": "EMPTY"}

        text = content[0].get("text", "")
        is_error = data.get("result", {}).get("isError", False)

        if is_error:
            log(f"API error: {text[:100]}", "FAIL")
            return {"case": case["aciklama"], "status": "ERROR", "error": text}

        # Text is JSON list of decisions, not markdown
        log(f"Response: {len(text)} chars, {elapsed:.1f}s (JSON metadata list)", "OK")

        # Parse JSON to extract first decision
        try:
            decisions = json.loads(text)
            if isinstance(decisions, dict) and "decisions" in decisions:
                decisions = decisions["decisions"]

            if decisions and len(decisions) > 0:
                first = decisions[0]
                log(f"  Found {len(decisions)} decisions", "OK")
                log(f"  Esas: {first.get('esasNo')}, Karar: {first.get('kararNo')}", "OK")
                log(f"  Daire: {first.get('daire', 'N/A')[:50]}", "OK")

                # Check document URL
                doc_url = first.get("document_url")
                if doc_url:
                    log(f"  Document URL available for fetching", "OK")
                    meta = {
                        "mahkeme": first.get("daire"),
                        "esas_no": first.get("esasNo"),
                        "karar_no": first.get("kararNo"),
                        "tarih": first.get("kararTarihi"),
                        "metadata_available": True,
                        "full_text_available": False,  # Needs separate fetch
                        "decision_count": len(decisions)
                    }
                else:
                    meta = {"metadata_available": True, "full_text_available": False}

                return {
                    "case": case["aciklama"],
                    "status": "PARTIAL_OK",
                    "elapsed_s": round(elapsed, 2),
                    "meta": meta,
                    "note": "Metadata list returned. Use get_emsal_document_markdown for full text.",
                    "preview": text[:500]
                }
        except json.JSONDecodeError:
            pass

        meta = extract_emsal_metadata(text)
        return {
            "case": case["aciklama"],
            "status": "OK",
            "elapsed_s": round(elapsed, 2),
            "meta": meta,
            "preview": text[:500]
        }
    except Exception as e:
        log(f"Error: {e}", "FAIL")
        return {"case": case["aciklama"], "status": "ERROR", "error": str(e)}

if __name__ == "__main__":
    print("=" * 60)
    print("  FAZ 2 - Emsal (UYAP) Karar Kalite Testi")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    session_id = initialize_session()
    report = {"timestamp": datetime.now().isoformat(), "session_id": session_id[:16] + "...", "results": []}

    for i, case in enumerate(TEST_CASES):
        result = test_emsal_detailed(case, session_id, req_id=i+1)
        report["results"].append(result)
        time.sleep(2)

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"faz2_emsal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print("\n" + "=" * 60)
    log(f"Saved: {out}", "OK")
    print("=" * 60)
