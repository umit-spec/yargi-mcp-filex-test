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
    {"aciklama": "Hukuk - icra takibi", "phrase": "icra takibi"},
    {"aciklama": "Ceza - suç", "phrase": "suç ve ceza"},
]

def extract_yargitay_metadata(text):
    """Yargıtay kararından metadata extract et"""
    meta = {
        "esas_no": None,
        "karar_no": None,
        "tarih": None,
        "daire": None,
        "has_full_text": len(text) > 200,
        "truncated": len(text) >= 4900,
        "char_count": len(text),
    }

    # Esas No
    m = re.search(r'Esas\s+No[:\s]+(\d{4}/\d+)', text, re.I)
    if m:
        meta["esas_no"] = m.group(1)

    # Karar No
    m = re.search(r'Karar\s+No[:\s]+(\d{4}/\d+)', text, re.I)
    if m:
        meta["karar_no"] = m.group(1)

    # Tarih (DD.MM.YYYY)
    m = re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{4})', text)
    if m:
        meta["tarih"] = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"

    # Daire
    m = re.search(r'(\d+\.\s*(?:Hukuk|Ceza)\s+Dairesi|Genel Kurulu)', text, re.I)
    if m:
        meta["daire"] = m.group(1).strip()

    return meta

def test_yargitay_bedesten(case, session_id, req_id):
    """search_bedesten_unified ile Yargıtay kararı ara"""
    log(f"Test: {case['aciklama']}", "INFO")

    try:
        start = time.time()
        # Bedesten Yargıtay hukuk ve ceza daireleri
        data = call_tool(
            "search_bedesten_unified",
            {
                "phrase": case["phrase"],
                "court_types": ["YARGITAY_HUKUK", "YARGITAY_CEZA"]
            },
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

        meta = extract_yargitay_metadata(text)
        filled = sum(1 for k, v in meta.items() if v and k not in ["char_count", "truncated", "has_full_text"])

        log(f"Response: {len(text)} chars, {elapsed:.1f}s", "OK")
        log(f"  Metadata: {filled}/4 fields", "OK" if filled >= 3 else "WARN")
        log(f"  Daire: {meta['daire'] or 'N/A'}", "OK" if meta['daire'] else "WARN")
        log(f"  Truncated: {meta['truncated']}", "WARN" if meta['truncated'] else "OK")

        print(f"\n--- Preview (ilk 500 char) ---\n{text[:500]}\n---\n")

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
    print("  FAZ 2 - Yargıtay Karar Kalite Testi")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    session_id = initialize_session()
    report = {"timestamp": datetime.now().isoformat(), "session_id": session_id[:16] + "...", "results": []}

    for i, case in enumerate(TEST_CASES):
        result = test_yargitay_bedesten(case, session_id, req_id=i+1)
        report["results"].append(result)
        time.sleep(2)

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"faz2_yargitay_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print("\n" + "=" * 60)
    log(f"Saved: {out}", "OK")
    print("=" * 60)
