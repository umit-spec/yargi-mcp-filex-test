import re
import json
from datetime import datetime
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

MOCK_YARGITAY = """
## Yargitay 12. Hukuk Dairesi Karari
**Esas No:** 2023/1234
**Karar No:** 2023/5678
**Karar Tarihi:** 15.03.2023
**Daire:** 12. Hukuk Dairesi
Icra takibine itirazin iptali davasinda, borcunun itirazinin haksiz oldugu
anlasilmakla itirazin iptaline, yuzde 20 icra inkar tazminatina hukmedilmistir.
"""

MOCK_EMSAL = """
# Emsal Karar
Mahkeme: Istanbul 3. Asliye Hukuk Mahkemesi
Esas No: 2022/456
Karar No: 2022/789
Tarih: 20.06.2022
Menfi tespit davasinda, davacinin senede dayali borcunun bulunmadigi
ispat edildiginden davanin kabulune karar verilmistir.
"""

REQUIRED = ["court_name","chamber","case_number","decision_number",
            "decision_date","full_text","authority_rank","capture_method"]

def parse_yargitay(text):
    r = {"capture_method": "yargi_mcp", "source": "yargitay", "full_text": text.strip()}
    m = re.search(r'(\d+\.\s*(?:Hukuk|Ceza)\s+Dairesi|Hukuk Genel Kurulu|Ceza Genel Kurulu)', text, re.I)
    r["chamber"] = m.group(1).strip() if m else None
    m = re.search(r'Esas\s+No[:\s]+(\d{4}/\d+)', text, re.I)
    r["case_number"] = m.group(1) if m else None
    m = re.search(r'Karar\s+No[:\s]+(\d{4}/\d+)', text, re.I)
    r["decision_number"] = m.group(1) if m else None
    m = re.search(r'Karar\s+Tarihi[:\s]+(\d{1,2}[./]\d{1,2}[./]\d{4})', text, re.I)
    r["decision_date"] = m.group(1) if m else None
    r["court_name"] = f"Yargitay {r['chamber']}" if r["chamber"] else "Yargitay"
    ch = r.get("chamber","") or ""
    if "Ictihadı Birlestirme" in ch: r["authority_rank"] = "ybk"
    elif "Genel Kurul" in ch: r["authority_rank"] = "yhgk"
    else: r["authority_rank"] = "yargitay_daire"
    r["validation_status"] = "pending"
    return r

def parse_emsal(text):
    r = {"capture_method": "yargi_mcp", "source": "emsal_uyap", "full_text": text.strip()}
    m = re.search(r'Mahkeme[:\s]+(.+?)(?:\n|$)', text, re.I)
    r["court_name"] = m.group(1).strip() if m else None
    r["chamber"] = None
    m = re.search(r'Esas\s+No[:\s]+(\d{4}/\d+)', text, re.I)
    r["case_number"] = m.group(1) if m else None
    m = re.search(r'Karar\s+No[:\s]+(\d{4}/\d+)', text, re.I)
    r["decision_number"] = m.group(1) if m else None
    m = re.search(r'Tarih[:\s]+(\d{1,2}[./]\d{1,2}[./]\d{4})', text, re.I)
    r["decision_date"] = m.group(1) if m else None
    court = r.get("court_name","") or ""
    r["authority_rank"] = "bam_daire" if "Bolge Adliye" in court else "ilk_derece"
    r["validation_status"] = "pending"
    return r

def coverage(parsed, source):
    rep = {"source": source, "fields": {}}
    for f in REQUIRED:
        v = parsed.get(f)
        rep["fields"][f] = {"present": v is not None, "value": str(v)[:60] if v else None}
    filled = sum(1 for f in REQUIRED if parsed.get(f))
    rep["coverage"] = f"{filled}/{len(REQUIRED)}"
    rep["missing"] = [f for f in REQUIRED if not parsed.get(f)]
    return rep

if __name__ == "__main__":
    print("=" * 60)
    print("  FAZ 3 - Validator Uyumu & Alan Mapping")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    report = {"timestamp": datetime.now().isoformat()}

    print("\n[Yargitay Mock Parse]")
    cov_y = coverage(parse_yargitay(MOCK_YARGITAY), "yargitay")
    print(json.dumps(cov_y, ensure_ascii=False, indent=2))

    print("\n[Emsal Mock Parse]")
    cov_e = coverage(parse_emsal(MOCK_EMSAL), "emsal")
    print(json.dumps(cov_e, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print(f"Yargitay kapsam : {cov_y['coverage']} | Eksik: {cov_y['missing']}")
    print(f"Emsal kapsam    : {cov_e['coverage']} | Eksik: {cov_e['missing']}")
    print("=" * 60)

    report["yargitay"] = cov_y
    report["emsal"] = cov_e
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"faz3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"[OK] Kaydedildi: {out}")
