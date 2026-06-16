"""
TEK-KARAR map: results/pro_raw/pro_test_233351200.json -> Silver intake formatı.

Kapsam: yalnızca 1 karar. Gold'a dokunmaz. Toplu/batch yok.
Çıktı: results/pro_single/ (sadece bu karar) -> app "Klasörden İçe Aktar" ile Silver'a.

Alanlar (talimat gereği):
  authorityLevel=HGK · provenanceGrade=A · source=yargi_mcp_pro
  sourceUrl=resmi adalet.gov.tr URL · decisionText=tam metin
"""
import json
import re
import sys
from pathlib import Path

SRC = Path(__file__).parent.parent / "results" / "pro_raw" / "pro_test_233351200.json"
OUT_DIR = Path(__file__).parent.parent / "results" / "pro_single"

# Bu karara ait sabit metadata (HGK · ihalenin feshi · E.2014/1077 K.2016/584 · 04.05.2016)
META = {
    "captureId": "yargi_pro_233351200",
    "topic": "İhalenin Feshi",
    "court": "Yargıtay",
    "chamber": "Hukuk Genel Kurulu",
    "esasNo": "2014/1077",
    "kararNo": "2016/584",
    "decisionDate": "2016-05-04",
    "authorityLevel": "HGK",
    "provenanceGrade": "A",
}

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def check_pii(text):
    sig = []
    if re.search(r'\+90\d{10}|\b0\d{3}\s?\d{3}\s?\d{2}\s?\d{2}\b', text):
        sig.append("phone_number")
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text):
        sig.append("email_address")
    if re.search(r'\b[0-9]{11}\b', text):
        sig.append("id_number_hint")
    return {"pii_seen": bool(sig), "pii_signals": ",".join(sig) or None, "review_required": True}


def main():
    raw = json.load(open(SRC, encoding="utf-8"))
    text = (raw.get("markdown_content") or raw.get("raw_text") or "").strip()
    source_url = raw.get("source_url")
    if len(text) < 80:
        print(f"HATA: tam metin yok/çok kısa ({len(text)}c)")
        sys.exit(1)

    pii = check_pii(text)
    record = {
        "captureId": META["captureId"],
        "source": "yargi_mcp_pro",
        "topic": META["topic"],
        "court": META["court"],
        "chamber": META["chamber"],
        "esasNo": META["esasNo"],
        "kararNo": META["kararNo"],
        "decisionDate": META["decisionDate"],
        "summary": text[:240].replace("\n", " ").strip(),
        "decisionText": text[:20000],
        "sourceUrl": source_url,
        "authorityLevel": META["authorityLevel"],
        "piiSeen": pii["pii_seen"],
        "piiSignals": pii["pii_signals"],
        "reviewRequired": pii["review_required"],
        "provenanceGrade": META["provenanceGrade"],
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{META['captureId']}.json"
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"yazıldı: {out}")
    print(f"  {record['authorityLevel']} · provenance {record['provenanceGrade']} · "
          f"{record['esasNo']}/{record['kararNo']} · {len(text)}c · pii={record['piiSeen']}")
    print(f"  sourceUrl: {record['sourceUrl']}")


if __name__ == "__main__":
    main()
