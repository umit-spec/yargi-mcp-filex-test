"""
Bedesten crawler → Silver DB içe-aktarım dosyaları.

yargi-mcp `search_bedesten_unified` (YARGITAYKARARI + ISTINAFHUKUK) ile konu başına
en-yeni-önce karar toplar, `get_bedesten_document_markdown` ile TAM METNİ çeker,
authority_level türetir, PII tarar ve her kararı CreateDecisionInput (camelCase)
şeklinde results/silver_intake/*.json olarak yazar. Tauri app "Klasörden İçe Aktar"
ile bu klasörü içeri alır.

DİRENÇ: rate-limit (429 retry_after) + backoff + her istek arası nazik gecikme +
checkpoint/resume (yarıda kesilirse kaldığı yerden). Civil (Hukuk) filtresi; Ceza atlanır.

Kullanım:
  python pipeline/bedesten_adapter.py --smoke      # her konudan ~2 (toplam ~20)
  python pipeline/bedesten_adapter.py --full       # tam dağılım (~1000)
  python pipeline/bedesten_adapter.py --topic "Menfi Tespit" --limit 5
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tests"))
from common import initialize_session, call_tool, log  # noqa: E402

# Windows konsolu cp1254; Türkçe/→ için stdout'u UTF-8'e çevir.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT_DIR = Path(__file__).parent.parent / "results" / "silver_intake"
CHECKPOINT = OUT_DIR / "_checkpoint.json"

COURT_TYPES = ["YARGITAYKARARI", "ISTINAFHUKUK"]

# Konu -> (arama ifadesi, hedef adet)  | Toplam ~1000
TOPICS = [
    ("Usulsüz Tebligat", "usulsüz tebligat", 200),
    ("İtirazın Kaldırılması", "itirazın kaldırılması", 120),
    ("İtirazın İptali", "itirazın iptali", 100),
    ("Menfi Tespit", "menfi tespit", 100),
    ("İstirdat", "istirdat", 60),
    ("Haciz", "haciz", 100),
    ("Maaş Haczi", "maaş haczi", 50),
    ("Meskeniyet", "meskeniyet", 80),
    ("İhalenin Feshi", "ihalenin feshi", 100),
    ("Yetki İtirazı", "yetki itirazı", 50),
    ("Takibin Taliki / İptali", "takibin taliki", 40),
]

BASE_DELAY = 1.5      # her MCP çağrısı arası nazik gecikme (sn)
MAX_RETRY = 5         # 429 / hata için maksimum deneme
MAX_PAGES = 400       # konu başına güvenlik tavanı (10 sonuç/sayfa)


# ── Rate-limit'e saygılı MCP çağrısı ──────────────────────────────────────────
def mcp(tool, args, sid, req_id=1):
    """call_tool + 429 retry_after + backoff. (parsed_payload, error_str) döndürür."""
    for attempt in range(MAX_RETRY):
        time.sleep(BASE_DELAY)
        r = call_tool(tool, args, sid, req_id)
        res = r.get("result", {})
        content = res.get("content", [])
        text = content[0].get("text", "") if content else ""
        # JSON payload mı?
        try:
            payload = json.loads(text)
        except Exception:
            payload = None
        # rate limit?
        if isinstance(payload, dict) and payload.get("error") == "rate_limit_exceeded":
            try:
                wait = int(float(payload.get("retry_after") or (5 * (attempt + 1))))
            except (TypeError, ValueError):
                wait = 5 * (attempt + 1)
            log(f"    429 — {wait}s bekleniyor (deneme {attempt+1}/{MAX_RETRY})", "WARN")
            time.sleep(min(wait, 45))
            continue
        if res.get("isError"):
            # geçici olabilir; kısa backoff
            time.sleep(2 * (attempt + 1))
            continue
        return payload, text
    return None, "max_retry"


# ── Yardımcılar ───────────────────────────────────────────────────────────────
def parse_date(karar_tarihi_str):
    """DD.MM.YYYY -> YYYY-MM-DD. Makul olmayan yıl (kaynak hatası) -> None."""
    try:
        d, m, y = karar_tarihi_str.split(".")
        yi = int(y)
        if yi < 1960 or yi > 2030:  # kaynak veri hatası (ör. 6006) sıralamayı bozmasın
            return None
        return f"{yi:04d}-{m.zfill(2)}-{d.zfill(2)}"
    except Exception:
        return None


def derive_authority(item_type, birim_adi):
    b = (birim_adi or "").lower()
    if "genel kurul" in b:
        return "HGK"
    if "içtihad" in b or "ictihad" in b or "birleştirme" in b:
        return "IBK"
    if item_type == "ISTINAFHUKUK" or "bölge adliye" in b or "bolge adliye" in b:
        return "BAM"
    if item_type == "YARGITAYKARARI":
        return "YARGITAY_DAIRE"
    return "YEREL"


def is_civil(birim_adi):
    b = (birim_adi or "").lower()
    if "ceza" in b:
        return False
    return "hukuk" in b or "genel kurul" in b or "birleştirme" in b


def check_pii(text):
    signals = []
    if re.search(r'\+90\d{10}|\b0\d{3}\s?\d{3}\s?\d{2}\s?\d{2}\b', text):
        signals.append("phone_number")
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text):
        signals.append("email_address")
    if re.search(r'\b[0-9]{11}\b', text):
        signals.append("id_number_hint")
    if re.search(r'(Sokak|Caddesi|Mah\.?|Mahallesi)\s+\S', text, re.I):
        signals.append("address_hint")
    return {
        "pii_seen": bool(signals),
        "pii_signals": ",".join(signals) if signals else None,
        "review_required": True,  # API verisi her zaman manuel inceleme ister
    }


def court_name(item_type, birim_adi):
    if item_type == "ISTINAFHUKUK":
        return (birim_adi or "Bölge Adliye Mahkemesi")
    if "genel kurul" in (birim_adi or "").lower():
        return "Yargıtay Hukuk Genel Kurulu"
    return "Yargıtay"


# ── Checkpoint ─────────────────────────────────────────────────────────────────
def load_checkpoint():
    if CHECKPOINT.exists():
        try:
            return json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"seen": [], "counts": {}}


def save_checkpoint(ck):
    CHECKPOINT.write_text(json.dumps(ck, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Konu crawl ─────────────────────────────────────────────────────────────────
def crawl_topic(topic, phrase, target, sid, ck, court_types):
    seen = set(ck["seen"])
    collected = ck["counts"].get(topic, 0)
    if collected >= target:
        log(f"[{topic}] zaten dolu ({collected}/{target}), atlanıyor", "OK")
        return
    log(f"[{topic}] hedef {target}, mevcut {collected} — '{phrase}' (courts={court_types})", "INFO")

    page = 1
    while collected < target and page <= MAX_PAGES:
        payload, _ = mcp(
            "search_bedesten_unified",
            {"court_types": court_types, "phrase": phrase, "pageNumber": page},
            sid, page,
        )
        if not payload:
            log(f"  sayfa {page}: yanıt yok, konu durduruluyor", "WARN")
            break
        decisions = payload.get("decisions", []) if isinstance(payload, dict) else []
        if not decisions:
            log(f"  sayfa {page}: sonuç bitti (total={payload.get('total_records')})", "INFO")
            break

        for dec in decisions:
            if collected >= target:
                break
            item_type = (dec.get("itemType") or {}).get("name", "")
            birim = dec.get("birimAdi", "")
            if not is_civil(birim):
                continue
            esas = dec.get("esasNo")
            karar = dec.get("kararNo")
            ddate = parse_date(dec.get("kararTarihiStr", ""))
            key = f"{esas}|{karar}|{ddate}"
            if key in seen:
                continue
            doc_id = dec.get("documentId")
            if not doc_id:
                continue

            # Tam metin
            doc_payload, doc_text = mcp(
                "get_bedesten_document_markdown", {"documentId": doc_id}, sid, 1
            )
            full_text = ""
            if isinstance(doc_payload, dict):
                full_text = doc_payload.get("markdown_content", "") or ""
            elif doc_text and "rate_limit" not in doc_text:
                full_text = doc_text
            if not full_text or len(full_text) < 80:
                log(f"    {doc_id}: tam metin alınamadı, atlanıyor", "WARN")
                continue

            pii = check_pii(full_text)
            record = {
                "captureId": f"yargi_mcp_bedesten_{doc_id}",
                "source": "yargi_mcp",
                "topic": topic,
                "court": court_name(item_type, birim),
                "chamber": birim,
                "esasNo": esas,
                "kararNo": karar,
                "decisionDate": ddate,
                "summary": full_text[:240].replace("\n", " ").strip(),
                "decisionText": full_text[:20000],
                "sourceUrl": None,
                "authorityLevel": derive_authority(item_type, birim),
                "piiSeen": pii["pii_seen"],
                "piiSignals": pii["pii_signals"],
                "reviewRequired": pii["review_required"],
            }
            (OUT_DIR / f"{record['captureId']}.json").write_text(
                json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            seen.add(key)
            collected += 1
            ck["seen"] = list(seen)
            ck["counts"][topic] = collected
            save_checkpoint(ck)
            log(f"    [{collected}/{target}] {record['authorityLevel']} {esas}/{karar} ({ddate}) {len(full_text)}c", "OK")

        page += 1

    log(f"[{topic}] tamamlandı: {collected}/{target}", "OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="her konudan ~2 (toplam ~20)")
    ap.add_argument("--full", action="store_true", help="tam dağılım (~1000)")
    ap.add_argument("--topic", help="tek konu adı")
    ap.add_argument("--limit", type=int, help="bu konu için hedef adet (override)")
    ap.add_argument("--include-bam", action="store_true",
                    help="BAM (İstinaf) da çek. Varsayılan: yalnızca Yargıtay (90/10 tercihi).")
    ap.add_argument("--bam", action="store_true",
                    help="Yalnızca BAM (İstinaf) çek. Yüksek-otorite PRO ile geldiği için hacim/BAM katmanı.")
    args = ap.parse_args()

    # Yüksek-otorite (İBK/HGK/Yargıtay) artık PRO ile küratörlü geliyor; ücretsiz
    # endpoint'i BAM/hacim için kullan. --bam = sadece İstinaf.
    if args.bam:
        court_types = ["ISTINAFHUKUK"]
    elif args.include_bam:
        court_types = COURT_TYPES
    else:
        court_types = ["YARGITAYKARARI"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ck = load_checkpoint()
    sid = initialize_session()

    print("=" * 72)
    print(f"  Bedesten → Silver intake  |  {datetime.now(timezone.utc).isoformat()}")
    print(f"  çıktı: {OUT_DIR}  |  courts={court_types}")
    print("=" * 72)

    if args.topic:
        match = next((t for t in TOPICS if t[0] == args.topic), None)
        if not match:
            log(f"Bilinmeyen konu: {args.topic}", "FAIL")
            return
        name, phrase, default_target = match
        target = args.limit or (2 if args.smoke else default_target)
        crawl_topic(name, phrase, target, sid, ck, court_types)
    else:
        for name, phrase, default_target in TOPICS:
            target = 2 if args.smoke else (default_target if args.full else 2)
            crawl_topic(name, phrase, target, sid, ck, court_types)

    total = sum(ck["counts"].values())
    print("\n" + "=" * 72)
    print("ÖZET (checkpoint):")
    for name, _, _ in TOPICS:
        print(f"  {name:32s} {ck['counts'].get(name, 0)}")
    print(f"  {'TOPLAM':32s} {total}")
    print("=" * 72)


if __name__ == "__main__":
    main()
