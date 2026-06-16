"""
PRO (yargi.betaspacestudio.com) küratörlü içtihatları Silver intake dosyasına çevirir.

Claude bu oturumda `ictihat_ara` + `ictihat_getir` ile yüksek-otorite (İBK/HGK/Yargıtay
dairesi) kararları seçer; tam metni ham bir .md dosyasına yazar; bu script metadatayla
birleştirip CreateDecisionInput (camelCase) JSON üretir. Böylece uzun metni elle
JSON-escape etme derdi olmaz.

Kullanım:
  python pipeline/pro_intake.py \
    --capture-id yargi_pro_169454700 --court "Yargıtay" --chamber "Hukuk Genel Kurulu" \
    --esas 2013/2211 --karar 2015/1300 --date 2015-04-29 --topic "İhalenin Feshi" \
    --authority HGK --source-url https://mevzuat.adalet.gov.tr/ictihat/169454700 \
    --text-file results/silver_intake/_pro_169454700.md
"""
import argparse
import json
import re
import sys
from pathlib import Path

OUT_DIR = Path(__file__).parent.parent / "results" / "silver_intake"

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
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture-id", required=True)
    ap.add_argument("--court", required=True)
    ap.add_argument("--chamber", required=True)
    ap.add_argument("--esas")
    ap.add_argument("--karar")
    ap.add_argument("--date", help="YYYY-MM-DD")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--authority", required=True,
                    choices=["IBK", "HGK", "HDK", "YARGITAY_DAIRE", "BAM", "YEREL"])
    ap.add_argument("--source-url")
    ap.add_argument("--text-file", required=True)
    args = ap.parse_args()

    text = Path(args.text_file).read_text(encoding="utf-8").strip()
    if len(text) < 80:
        print(f"UYARI: metin çok kısa ({len(text)}c) — atlanıyor: {args.capture_id}")
        return
    pii = check_pii(text)
    record = {
        "captureId": args.capture_id,
        "source": "yargi_mcp_pro",
        "topic": args.topic,
        "court": args.court,
        "chamber": args.chamber,
        "esasNo": args.esas,
        "kararNo": args.karar,
        "decisionDate": args.date,
        "summary": text[:240].replace("\n", " ").strip(),
        "decisionText": text[:20000],
        "sourceUrl": args.source_url,
        "authorityLevel": args.authority,
        "piiSeen": pii["pii_seen"],
        "piiSignals": pii["pii_signals"],
        "reviewRequired": pii["review_required"],
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{args.capture_id}.json"
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"yazıldı: {out.name}  ({args.authority} · {args.topic} · {len(text)}c · pii={pii['pii_seen']})")


if __name__ == "__main__":
    main()
