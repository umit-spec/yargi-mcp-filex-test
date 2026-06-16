"""
Adapter: yargi-mcp → raw_capture.v1.json

Converts Emsal (UYAP) API output to Filex raw_capture.v1.json format.
Bridges the gap between yargi-mcp and validate_raw_capture.ts.

Pipeline:
  yargi-mcp (search_emsal_detailed_decisions)
    |
  [This adapter]
    |
  raw_capture.v1.json (Filex intake format)
    |
  validate_raw_capture.ts (schema lock)
    |
  PASS/HOLD/REJECT
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add parent tests dir to path for common utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "tests"))
from common import log, parse_sse_or_json, initialize_session, call_tool


class EmsalToRawCaptureAdapter:
    """Converts Emsal decision metadata → raw_capture.v1.json"""

    SCHEMA_VERSION = "0.1.0"
    CAPTURE_METHOD = "manual_extension_assisted_capture"
    SOURCE_DOMAIN = "emsal.uyap.gov.tr"
    PROVENANCE_GRADE = "B"  # Portal-only (requires UYAP login, no stable URL)
    CANDIDATE_STATUS = "HOLD_PENDING_REVIEW"  # Always hold for review by Cüneyt Bey

    def __init__(self, captured_by: str = "yargi_mcp_bot"):
        self.captured_by = captured_by

    def adapt_emsal_metadata(
        self,
        decision: Dict[str, Any],
        full_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert single Emsal decision to raw_capture format.

        Args:
            decision: From search_emsal_detailed_decisions API (metadata only)
            full_text: Optional full markdown text from get_emsal_document_markdown

        Returns:
            raw_capture.v1.json compatible dict
        """
        capture_id = f"emsal-{decision.get('id', 'unknown')}-{uuid.uuid4().hex[:8]}"

        # Parse metadata
        daire = decision.get("daire", "").strip()
        esas_no = decision.get("esasNo", "").strip()
        karar_no = decision.get("kararNo", "").strip()
        karar_tarihi = decision.get("kararTarihi", "").strip()  # DD.MM.YYYY
        document_url = decision.get("document_url", "")

        # Convert date from DD.MM.YYYY to YYYY-MM-DD
        decision_date = self._parse_date(karar_tarihi)

        # Extract chamber from daire (e.g., "4. Hukuk Dairesi" from full name)
        chamber = self._extract_chamber(daire)

        # Court name (use first part of daire as court)
        court = self._extract_court_name(daire)

        # Build excerpt (use full text if available, else construct from metadata)
        selected_text_excerpt = full_text if full_text else self._build_excerpt(decision)

        # Run PII check
        pii_check = self._check_pii(selected_text_excerpt)

        # Build raw_capture document
        raw_capture = {
            "capture_id": capture_id,
            "schema_version": self.SCHEMA_VERSION,
            "source_domain": self.SOURCE_DOMAIN,
            "source_name": "Emsal (UYAP)",
            "capture_method": self.CAPTURE_METHOD,
            "captured_at": datetime.utcnow().isoformat() + "Z",
            "captured_by": self.captured_by,
            "court": court,
            "chamber": chamber,
            "esas_no": esas_no,
            "karar_no": karar_no,
            "decision_date": decision_date,
            "provenance_grade": self.PROVENANCE_GRADE,
            "provenance_status": "confirmed_no_stable_url",
            "source_url_note": "Portal-only decision. Requires UYAP login. Document ID: " + decision.get("id", "unknown"),
            "candidate_status": self.CANDIDATE_STATUS,
            "pii_initial_check": pii_check,
            "selected_text_excerpt": selected_text_excerpt[:5000],  # Truncate to safety limit
            "official_locator": {
                "source": "emsal_uyap",
                "document_id": decision.get("id"),
                "url_template": "https://emsal.uyap.gov.tr/getDokuman?id={id}"
            }
        }

        # Add optional fields
        if document_url:
            raw_capture["source_url"] = document_url

        return raw_capture

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Convert DD.MM.YYYY to YYYY-MM-DD"""
        try:
            parts = date_str.split(".")
            if len(parts) == 3:
                day, month, year = parts
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
        return None

    def _extract_chamber(self, daire: str) -> Optional[str]:
        """Extract chamber from full daire name"""
        # e.g., "Diyarbakır Bölge Adliye Mahkemesi 4. Hukuk Dairesi" → "4. Hukuk Dairesi"
        import re
        m = re.search(r'(\d+\.(?:\s+)?(?:Hukuk|Ceza|İdari|Iş)\s+Dairesi)', daire, re.I)
        if m:
            return m.group(1).strip()
        # Fallback: use last part if it contains "Daire"
        if "Daire" in daire:
            parts = daire.split()
            for i in range(len(parts) - 1, -1, -1):
                if "Daire" in parts[i]:
                    return " ".join(parts[max(0, i-1):i+1])
        return None

    def _extract_court_name(self, daire: str) -> str:
        """Extract court name from daire"""
        # e.g., "Diyarbakır Bölge Adliye Mahkemesi" from full daire
        # Simple heuristic: take up to "Mahkemesi" or "Kurulu"
        import re
        m = re.search(r'^([^M]*(?:Mahkemesi|Kurulu))', daire)
        if m:
            return m.group(1).strip()
        # Fallback: use whole daire
        return daire.split("Dairesi")[0].strip() if "Dairesi" in daire else daire

    def _build_excerpt(self, decision: Dict[str, Any]) -> str:
        """Build text excerpt from metadata when full text unavailable"""
        parts = []

        # Header
        daire = decision.get("daire", "")
        parts.append(f"Mahkeme: {daire}")

        # Case info
        parts.append(f"Esas No: {decision.get('esasNo', 'N/A')}")
        parts.append(f"Karar No: {decision.get('kararNo', 'N/A')}")
        parts.append(f"Tarih: {decision.get('kararTarihi', 'N/A')}")

        # Status
        durum = decision.get("durum", "")
        if durum:
            parts.append(f"Durum: {durum}")

        # Note
        parts.append(f"\n[Tam metin şu araç ile alınmıştır: yargi-mcp. Cüneyt Bey incelemesi bekleniyor.]")

        return "\n".join(parts)

    def _check_pii(self, text: str) -> Dict[str, Any]:
        """
        Basic PII check on text.
        Rules: phone numbers, emails, personal addresses, ID numbers
        """
        import re

        signals = []
        pii_seen = False

        # Phone number pattern (Turkish: +90, 0xx, etc.)
        if re.search(r'\+90\d{10}|\b0\d{3}\s?\d{3}\s?\d{2}\s?\d{2}\b', text):
            signals.append("phone_number")
            pii_seen = True

        # Email pattern
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            signals.append("email_address")
            pii_seen = True

        # Turkish ID number pattern (11 digits)
        if re.search(r'\b[0-9]{11}\b', text):
            signals.append("id_number_hint")
            pii_seen = True

        # Personal address hints (Istanbul, İzmir, etc. with address markers)
        if re.search(r'(Sokak|Caddesi|Mah\.?|Mahallesi|No\.?)\s+[0-9]+', text, re.I):
            signals.append("address_hint")
            pii_seen = True

        return {
            "pii_seen": pii_seen,
            "signals": signals,
            "manual_review_required": pii_seen,
            "full_text_storage_policy": "do_not_store_until_cleaned" if pii_seen else "ok_excerpt_only"
        }


def fetch_emsal_and_adapt(keyword: str, session_id: Optional[str] = None) -> list:
    """
    1. Search Emsal with yargi-mcp
    2. Fetch each result's full text
    3. Adapt to raw_capture.v1.json format

    Returns list of raw_capture documents
    """
    log(f"Emsal arama: '{keyword}'", "INFO")

    # Step 1: Search metadata
    response = call_tool(
        "search_emsal_detailed_decisions",
        {"keyword": keyword},
        session_id, 1
    )

    try:
        # response is dict: {result: {content: [{type, text}]}, ...}
        content = response.get("result", {}).get("content", [])
        if not content:
            log("No content in response", "WARN")
            return []

        response_text = content[0].get("text", "")
        is_error = response.get("result", {}).get("isError", False)

        if is_error:
            log(f"API error: {response_text[:100]}", "FAIL")
            return []

        # Parse the JSON text
        search_data = json.loads(response_text)

        if isinstance(search_data, dict) and "decisions" in search_data:
            decisions = search_data["decisions"]
        else:
            decisions = search_data if isinstance(search_data, list) else []
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        log(f"Parse error: {str(e)}", "FAIL")
        return []

    if not decisions:
        log("Sonuç yok", "WARN")
        return []

    log(f"Bulundu: {len(decisions)} karar", "OK")

    # Step 2: Fetch full text for each decision
    adapter = EmsalToRawCaptureAdapter()
    raw_captures = []

    for i, decision in enumerate(decisions[:5]):  # Limit to first 5 for testing
        doc_id = decision.get("id")
        log(f"  [{i+1}] Karar {doc_id} tam metni alınıyor...", "INFO")

        try:
            response = call_tool(
                "get_emsal_document_markdown",
                {"id": doc_id},
                session_id, i + 10
            )

            # Extract text from response
            content = response.get("result", {}).get("content", [])
            full_text = ""
            if content:
                full_text = content[0].get("text", "")

            # Adapt to raw_capture format
            raw_capture = adapter.adapt_emsal_metadata(decision, full_text)
            raw_captures.append(raw_capture)
            log(f"       Adapted: {len(full_text)} chars", "OK")

        except Exception as e:
            log(f"       Fetch error: {str(e)[:60]}", "WARN")
            # Still add with metadata-only excerpt
            raw_capture = adapter.adapt_emsal_metadata(decision, None)
            raw_captures.append(raw_capture)

    return raw_captures


if __name__ == "__main__":
    print("=" * 60)
    print("  yargi-mcp > raw_capture.v1.json Adapter")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Initialize session
    session_id = initialize_session()

    # Fetch and adapt
    raw_captures = fetch_emsal_and_adapt(
        keyword="menfi tespit borc",
        session_id=session_id
    )

    print("\n" + "=" * 60)
    log(f"Üretilen raw_capture documents: {len(raw_captures)}", "OK")

    # Save to file
    output_dir = Path(__file__).parent.parent / "results"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"raw_capture_emsal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "source": "yargi_mcp_adapter",
        "adapted_count": len(raw_captures),
        "documents": raw_captures
    }

    output_file.write_text(json.dumps(output_data, ensure_ascii=False, indent=2))
    log(f"Kaydedildi: {output_file}", "OK")
    print("=" * 60)
