"""
Adapter: yargi-mcp to raw_capture.v1.json

Converts Emsal (UYAP) API output to Filex raw_capture.v1.json format.
CRITICAL: Validator expects SINGLE OBJECT per file, not arrays.

Pipeline:
  yargi-mcp API (search_emsal_detailed_decisions)
    |
  [This adapter - fetches metadata + full text]
    |
  raw_capture.v1.json files (one file = one decision object)
    |
  validate_raw_capture.ts (tsx runner - per file)
    |
  PASS/HOLD/REJECT results
"""

import json
import uuid
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import sys
import re

# Add parent tests dir to path for common utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "tests"))
from common import log, parse_sse_or_json, initialize_session, call_tool

# Filex validator paths (use Windows path on Windows, Bash path in subprocess)
VALIDATOR_PATH_BASH = Path("/c/FilexAI/filex-decision-intelligence/pipeline/intake/validate_raw_capture.ts")
VALIDATOR_DIR = Path("/c/FilexAI/filex-decision-intelligence")

RESULTS_DIR = Path(__file__).parent.parent / "results"
VALIDATED_DIR = RESULTS_DIR / "validated"
REJECTED_DIR = RESULTS_DIR / "rejected"


class EmsalToRawCaptureAdapter:
    """Converts Emsal decision metadata to raw_capture format."""

    SCHEMA_VERSION = "0.1.0"
    CAPTURE_METHOD = "manual_extension_assisted_capture"
    SOURCE_DOMAIN = "emsal.uyap.gov.tr"
    PROVENANCE_GRADE = "B"  # Portal-only (requires UYAP login, no stable URL)
    CANDIDATE_STATUS = "HOLD_PENDING_REVIEW"  # Always hold for review

    def __init__(self, captured_by: str = "yargi_mcp_bot"):
        self.captured_by = captured_by
        self.decision_counter = 0

    def adapt_emsal_metadata(
        self,
        decision: Dict[str, Any],
        full_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert single Emsal decision to raw_capture format.
        Returns SINGLE OBJECT (not array).

        Args:
            decision: From search_emsal_detailed_decisions API
            full_text: From get_emsal_document_markdown

        Returns:
            raw_capture.v1.json compatible dict (single object)
        """
        self.decision_counter += 1
        capture_id = f"yargi_mcp_emsal_{datetime.now().strftime('%Y%m%d')}_{self.decision_counter:03d}"

        # Parse metadata
        daire = decision.get("daire", "").strip()
        esas_no = decision.get("esasNo", "").strip()
        karar_no = decision.get("kararNo", "").strip()
        karar_tarihi = decision.get("kararTarihi", "").strip()  # DD.MM.YYYY

        # Convert date from DD.MM.YYYY to YYYY-MM-DD
        decision_date = self._parse_date(karar_tarihi)

        # Extract court info
        chamber = self._extract_chamber(daire)
        court = self._extract_court_name(daire)

        # Build excerpt (use full text if available, else construct from metadata)
        selected_text_excerpt = full_text if full_text else self._build_excerpt(decision)

        # PII check
        pii_check = self._check_pii(selected_text_excerpt)

        # Get current time in ISO format with timezone
        now_utc = datetime.now(timezone.utc)
        captured_at = now_utc.isoformat()

        # Build raw_capture document (SINGLE OBJECT, not array)
        raw_capture = {
            "capture_id": capture_id,
            "schema_version": self.SCHEMA_VERSION,
            "source_domain": self.SOURCE_DOMAIN,
            "source_name": "Emsal (UYAP)",
            "capture_method": self.CAPTURE_METHOD,
            "captured_at": captured_at,
            "captured_by": self.captured_by,
            "court": court,
            "esas_no": esas_no,
            "karar_no": karar_no,
            "decision_date": decision_date,
            "provenance_grade": self.PROVENANCE_GRADE,
            "provenance_status": "confirmed_no_stable_url",
            "source_url_note": f"Portal-only (UYAP login required). Document ID: {decision.get('id')}",
            "candidate_status": self.CANDIDATE_STATUS,
            "pii_initial_check": pii_check,
            "selected_text_excerpt": selected_text_excerpt[:5000]  # Truncate to safety limit
        }

        # Add optional fields
        if chamber:
            raw_capture["chamber"] = chamber

        if decision.get("document_url"):
            raw_capture["source_url"] = decision["document_url"]

        # Official locator for Emsal
        raw_capture["official_locator"] = {
            "source": "emsal_uyap",
            "document_id": decision.get("id"),
            "url_template": "https://emsal.uyap.gov.tr/getDokuman?id={id}"
        }

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
        m = re.search(r'(\d+\.(?:\s+)?(?:Hukuk|Ceza|Idari|Is)\s+Dairesi)', daire, re.I)
        if m:
            return m.group(1).strip()
        if "Daire" in daire:
            parts = daire.split()
            for i in range(len(parts) - 1, -1, -1):
                if "Daire" in parts[i]:
                    return " ".join(parts[max(0, i-1):i+1])
        return None

    def _extract_court_name(self, daire: str) -> str:
        """Extract court name from daire"""
        m = re.search(r'^([^D]*(?:Mahkemesi|Kurulu))', daire)
        if m:
            return m.group(1).strip()
        return daire.split("Dairesi")[0].strip() if "Dairesi" in daire else daire

    def _build_excerpt(self, decision: Dict[str, Any]) -> str:
        """Build text excerpt from metadata when full text unavailable"""
        parts = [
            f"Mahkeme: {decision.get('daire', '')}",
            f"Esas No: {decision.get('esasNo', 'N/A')}",
            f"Karar No: {decision.get('kararNo', 'N/A')}",
            f"Tarih: {decision.get('kararTarihi', 'N/A')}",
            "",
            "[Tam metin yargi-mcp tarafindan alinmistir. Cuneyt Bey incelemesi bekleniyor.]"
        ]
        return "\n".join(parts)

    def _check_pii(self, text: str) -> Dict[str, Any]:
        """
        Basic PII check on text.
        Conservative: flag everything for manual review.
        """
        signals = []
        pii_seen = False

        # Phone number pattern (Turkish)
        if re.search(r'\+90\d{10}|\b0\d{3}\s?\d{3}\s?\d{2}\s?\d{2}\b', text):
            signals.append("phone_number")
            pii_seen = True

        # Email pattern
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            signals.append("email_address")
            pii_seen = True

        # Turkish ID number (11 digits)
        if re.search(r'\b[0-9]{11}\b', text):
            signals.append("id_number_hint")
            pii_seen = True

        # Address patterns
        if re.search(r'(Sokak|Caddesi|Mah\.?|Mahallesi|No\.?)\s+[0-9]+', text, re.I):
            signals.append("address_hint")
            pii_seen = True

        # Conservative: always require manual review for API data
        return {
            "pii_seen": pii_seen,
            "signals": signals,
            "manual_review_required": True,  # ALWAYS true for API data
            "full_text_storage_policy": "do_not_store_until_cleaned"  # Conservative storage policy
        }


def fetch_emsal_and_validate(keyword: str, limit: int = 1, session_id: Optional[str] = None) -> dict:
    """
    1. Search Emsal
    2. Fetch full text for each result
    3. Adapt to raw_capture format
    4. Validate with tsx validator
    5. Sort into validated/ or rejected/

    Args:
        keyword: Search term
        limit: Number of decisions to fetch (default 1 for testing)
        session_id: MCP session ID

    Returns:
        Summary dict with pass/fail counts
    """
    log(f"Emsal arama: '{keyword}' (max {limit})", "INFO")

    # Step 1: Search metadata
    response = call_tool(
        "search_emsal_detailed_decisions",
        {"keyword": keyword},
        session_id, 1
    )

    try:
        content = response.get("result", {}).get("content", [])
        if not content:
            log("No content in response", "WARN")
            return {"pass": 0, "hold": 0, "reject": 0}

        response_text = content[0].get("text", "")
        is_error = response.get("result", {}).get("isError", False)

        if is_error:
            log(f"API error: {response_text[:100]}", "FAIL")
            return {"pass": 0, "hold": 0, "reject": 0}

        search_data = json.loads(response_text)
        if isinstance(search_data, dict) and "decisions" in search_data:
            decisions = search_data["decisions"]
        else:
            decisions = search_data if isinstance(search_data, list) else []
    except Exception as e:
        log(f"Parse error: {str(e)}", "FAIL")
        return {"pass": 0, "hold": 0, "reject": 0}

    if not decisions:
        log("Sonuc yok", "WARN")
        return {"pass": 0, "hold": 0, "reject": 0}

    log(f"Bulundu: {len(decisions)} karar, processing first {limit}", "OK")

    # Step 2: Fetch full text and validate each
    adapter = EmsalToRawCaptureAdapter()
    results = {"pass": 0, "hold": 0, "reject": 0}

    RESULTS_DIR.mkdir(exist_ok=True)
    VALIDATED_DIR.mkdir(exist_ok=True)
    REJECTED_DIR.mkdir(exist_ok=True)

    for i, decision in enumerate(decisions[:limit]):
        doc_id = decision.get("id")
        log(f"  [{i+1}] Karar {doc_id} isle aliniyor...", "INFO")

        try:
            # Fetch full text
            response = call_tool(
                "get_emsal_document_markdown",
                {"id": doc_id},
                session_id, i + 10
            )

            content = response.get("result", {}).get("content", [])
            full_text = content[0].get("text", "") if content else None

            # Adapt to raw_capture format (SINGLE OBJECT)
            raw_capture = adapter.adapt_emsal_metadata(decision, full_text)
            char_count = len(full_text) if full_text else len(raw_capture.get("selected_text_excerpt", ""))
            log(f"       Adapted: {char_count} chars", "OK")

            # Save to single JSON file (NOT array, NOT wrapper object)
            capture_id = raw_capture["capture_id"]
            capture_file = RESULTS_DIR / f"{capture_id}.json"

            capture_file.write_text(
                json.dumps(raw_capture, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            log(f"       Saved: {capture_file.name}", "OK")

            # Validate with tsx
            log(f"       Validating...", "INFO")
            # Convert Windows path to Bash path for subprocess
            bash_capture_path = f"/c/yargi-mcp-filex-test/results/{capture_file.name}"
            result = subprocess.run(
                ["npx", "tsx", "/c/FilexAI/filex-decision-intelligence/pipeline/intake/validate_raw_capture.ts", "--input", bash_capture_path],
                cwd="/c/FilexAI/filex-decision-intelligence",
                capture_output=True,
                text=True,
                shell=False
            )

            print("\n" + "=" * 80)
            print(f"VALIDATOR: {capture_file.name}")
            print(f"Exit code: {result.returncode}")
            if result.stdout:
                print("STDOUT:", result.stdout[:500])
            if result.stderr:
                print("STDERR:", result.stderr[:500])
            print("=" * 80 + "\n")

            # Classify result
            try:
                validator_output = json.loads(result.stdout) if result.stdout else {}
                routing = validator_output.get("routing", "")
                if routing == "PASS":
                    status = "PASS"
                    results["pass"] += 1
                    (VALIDATED_DIR / f"PASS_{capture_file.name}").write_text(capture_file.read_text())
                elif routing == "HOLD":
                    status = "HOLD"
                    results["hold"] += 1
                    (VALIDATED_DIR / f"HOLD_{capture_file.name}").write_text(capture_file.read_text())
                else:
                    status = "REJECT"
                    results["reject"] += 1
                    (REJECTED_DIR / capture_file.name).write_text(capture_file.read_text())
            except json.JSONDecodeError:
                status = "ERROR"
                results["reject"] += 1

            log(f"       Validator: {status}", "OK" if status in ["PASS", "HOLD"] else "FAIL")

        except Exception as e:
            log(f"       Error: {str(e)[:60]}", "FAIL")

    return results


if __name__ == "__main__":
    print("=" * 80)
    print("  yargi-mcp > raw_capture.v1.json Adapter + Validator")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Initialize session
    session_id = initialize_session()

    # Fetch and validate (START WITH 1 DECISION FOR TESTING)
    results = fetch_emsal_and_validate(
        keyword="menfi tespit borc",
        limit=1,  # SINGLE DECISION - test the pipeline
        session_id=session_id
    )

    print("\n" + "=" * 80)
    print("SUMMARY")
    print(f"  PASS:   {results['pass']}")
    print(f"  HOLD:   {results['hold']}")
    print(f"  REJECT: {results['reject']}")
    print("=" * 80)
