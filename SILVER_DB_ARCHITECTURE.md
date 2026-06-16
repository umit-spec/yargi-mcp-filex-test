# Silver DB Architecture v1.0

## Purpose

Silver DB adalah **validated but unapproved** decision candidate repository.

**Critical:** Silver DB is NOT a data warehouse.  
**Silver DB is an expert-review staging area.**

- ✅ Validator kapısından geçen kararlar
- ⏳ Cüneyt Bey review bekleyen kararlar  
- ❌ Gold DB'ye ASLA otomatik yazım
- 🔄 Chrome Extension + yargi-mcp + future sources → unified intake
- 🎯 **Purpose: Scale Cüneyt Bey's expert judgment across volumes of candidate data**

---

## Principles

### Principle 1: Schema Immutability
- Validator (validate_raw_capture.ts) hiçbir zaman değiştirilmez
- Validator ürettiği context_packet sabit kalır
- Tüm kaynaklar aynı Validator'dan geçer

### Principle 2: Human Gate
- No automatic Gold promotion
- Cüneyt Bey review_status = APPROVED → Gold DB entry
- Silver DB only = draft state

### Principle 3: Atomicity
- 1 decision = 1 capture file = 1 Silver DB row
- No bulk operations without explicit review
- Full audit trail per decision

### Principle 4: Gold Integrity
- Silver > Gold flow one-way only
- Gold > Silver is impossible
- Cüneyt Bey can reject, never auto-import

---

## Silver DB Schema (SQLite)

```sql
CREATE TABLE silver_decisions (
  -- Primary Keys
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  capture_id TEXT UNIQUE NOT NULL,
  
  -- Source & Provenance
  source_domain TEXT NOT NULL,  -- "emsal.uyap.gov.tr", "karararama.yargitay.gov.tr", etc
  source_url TEXT,
  captured_at DATETIME NOT NULL,
  captured_by TEXT NOT NULL,  -- "chrome_extension", "yargi_mcp_bot", etc
  
  -- Decision Metadata
  court TEXT NOT NULL,
  chamber TEXT,
  esas_no TEXT NOT NULL,
  karar_no TEXT NOT NULL,
  decision_date DATE NOT NULL,
  
  -- Content
  selected_text_excerpt TEXT NOT NULL,
  full_text_hash TEXT,  -- SHA256 of full text (not stored in DB)
  
  -- Classification
  topic TEXT,  -- "usulsuz_tebligat", "meskeniyet", "ihaleinin_feshi", etc
  subtopic TEXT,  -- Detailed subcategory
  legal_area TEXT,  -- "Icra ve Iflas Hukuku", etc
  
  -- Validator Status
  validator_routing TEXT NOT NULL,  -- "PASS", "HOLD", "REJECT"
  validator_timestamp DATETIME,
  validator_errors TEXT,  -- JSON array of errors (if REJECT)
  context_packet_id TEXT,  -- Links to context_packet.json
  
  -- Cüneyt Review Status
  review_status TEXT DEFAULT 'PENDING',  -- PENDING, APPROVED, REJECTED, NEEDS_METADATA_FIX, KEEP_IN_SILVER
  review_notes TEXT,
  reviewer_id TEXT,  -- "cuneyt", etc
  review_date DATETIME,
  
  -- Quality Assessment
  argument_category TEXT,  -- "tahkim", "hakimsiz karar", etc
  confidence_score REAL,  -- 0.0-1.0, AI-estimated relevance
  metadata_completeness REAL,  -- 0.0-1.0, field fill rate
  pii_status TEXT,  -- "cleared", "flagged", "manual_review_required"
  
  -- Tier 3: Strategic Role (THE MOAT)
  -- How does a lawyer use this decision in case strategy?
  strategic_role TEXT,  -- "ana_daynak|destekleyici|karsi_goruset_curut|ispat_yuku|usul|esas"
  strategic_confidence REAL,  -- 0.0-1.0, Cüneyt's certainty about strategic role
  
  -- Audit
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  gold_promoted_at DATETIME,  -- When (if) moved to Gold DB
  gold_promoted_by TEXT,
  
  -- Flags
  is_duplicate BOOLEAN DEFAULT 0,
  duplicate_of TEXT,  -- capture_id of original if duplicate
  requires_curation BOOLEAN DEFAULT 0,
  curation_notes TEXT
);

-- Indexes
CREATE INDEX idx_source_domain ON silver_decisions(source_domain);
CREATE INDEX idx_review_status ON silver_decisions(review_status);
CREATE INDEX idx_decision_date ON silver_decisions(decision_date DESC);
CREATE INDEX idx_topic ON silver_decisions(topic);
CREATE INDEX idx_capture_id ON silver_decisions(capture_id);
```

---

## Cüneyt Matrix

For each Silver decision, Cüneyt Bey selects:

### Review Decision

| Status | Meaning | Action |
|--------|---------|--------|
| **GOLD_APPROVED** | Move to Gold DB | Insert into gold_decisions, set gold_promoted_at |
| **KEEP_IN_SILVER** | Keep for future | Auto-archive after 6 months, revisit later |
| **NEEDS_METADATA_FIX** | Fix required | Show metadata editor, request re-submission |
| **REJECT** | Not suitable | Mark is_duplicate=false, move to archive |
| **DUPLICATE** | Already in Silver | Mark is_duplicate=true, link to duplicate_of capture_id |

### Quality Assessment

```json
{
  "review_status": "APPROVED | KEEP_IN_SILVER | NEEDS_METADATA_FIX | REJECT",
  "review_notes": "string (max 500 chars)",
  "argument_category": "tahkim | hakimsiz_karar | ...",
  "confidence_score": 0.0-1.0,
  "requires_curation": true | false,
  "curation_notes": "string"
}
```

### Cüneyt Dashboard

Display per decision:

```
┌─ Silver DB Candidate ─────────────────────────────┐
│ Karar: Diyarbakır BAM 4. Hukuk (2026/2283)        │
│ Tarih: 04.06.2026                                 │
│ Kaynak: Emsal (yargi-mcp_bot)                     │
│ Topic: Usulsüz Tebligat (98% confidence)          │
│ Status: ✓ Validator PASS                          │
│                                                    │
│ [APPROVED]  [KEEP_IN_SILVER]  [NEEDS_FIX]  [REJECT] │
│ Notes: [          ]                                │
│ Category: [tahkim ▼]                              │
│ Confidence: [████░░░░░░] 0.65                      │
└────────────────────────────────────────────────────┘
```

---

## MVP Target: 100 Silver Decisions

### Distribution (Initial Phase)

| Topic | Target | Status |
|-------|--------|--------|
| Usulsüz Tebligat | 40 | ← Start here |
| Meskeniyet | 30 | ← Start here |
| İhalenin Feshi | 30 | ← Start here |
| **TOTAL MVP** | **100** | **Gate before expanding** |

### Validation Criteria (before 200+ decisions)

✅ All 100 decisions passed Validator contract (zero schema errors)  
✅ Duplicate detection functional (measure %, don't require 0%)  
✅ PII screening passed (no sensitive data leaked to Silver)  
✅ Cüneyt Bey reviewed minimum 20 decisions (sample validation)  
✅ Review outcomes recorded (GOLD_APPROVED / KEEP / NEEDS_FIX / REJECT / DUPLICATE counts)  
✅ At least 5 decisions marked GOLD_APPROVED (or 0 if Cüneyt judges none ready — acceptable)  
✅ Pipeline ran 7 days unattended without manual intervention  
✅ No automatic writes to Gold DB  

**Success interpretation:**
- High REJECT rate? → Filter working (normal, healthy)
- Low APPROVED rate? → Cüneyt is selective (correct, desired)
- Duplicates found? → Dedup mechanism works (good)

**If all criteria met:** Release Phase 2 (200 more decisions)  
**If any fail:** Halt, review root cause, adjust pipeline  
**If Cüneyt rates APPROVE at 0%:** Still success (he's the expert — we trust his judgment)

---

## Risk Matrix

### Risk 1: Gold DB Contamination

**Risk:** Bad Silver decisions leak to Gold  
**Mitigation:** Cüneyt Bey explicit approval required  
**Monitor:** Daily: review_status = APPROVED count  
**Alert:** If APPROVED rate > 90% (suggests no real review)

### Risk 2: Duplicate Decisions

**Risk:** Same karar_no/esas_no appears twice  
**Mitigation:** SQLite UNIQUE constraint on (esas_no, karar_no, decision_date)  
**Monitor:** Daily: is_duplicate flag check  
**Alert:** If > 5% duplicates, halt source

### Risk 3: PII Leakage

**Risk:** Personal data stored in Silver  
**Mitigation:** pii_status field, manual_review_required flag  
**Monitor:** Weekly: SELECT * WHERE pii_status = 'flagged'  
**Alert:** If any flagged decisions in Silver, quarantine immediately

### Risk 4: Authority Level Mixing

**Risk:** Mixing Yargıtay + BAM + İlk Derece  
**Mitigation:** chamber field + authority_rank calculation  
**Monitor:** Query by source_domain + chamber  
**Alert:** If mixing without intention, halt intake

### Risk 5: Uncontrolled Growth

**Risk:** Silver DB grows to 10K+ with low review rate  
**Mitigation:** Phase gates (100 → 200 → 500 → 1000)  
**Monitor:** Weekly: COUNT(*) WHERE review_status = 'PENDING'  
**Alert:** If PENDING > 500, pause intake until Cüneyt catches up

---

## Data Flow

```
Source (Chrome Extension / yargi-mcp / future)
  ↓
Adapter (format → raw_capture.v1.json)
  ↓
Validator (validate_raw_capture.ts)
  ↓
PASS ─→ context_packet.json
  ↓
Silver DB (INSERT new row)
  ↓
Cüneyt Dashboard
  ↓
[APPROVED / KEEP_IN_SILVER / NEEDS_FIX / REJECT]
  ↓
IF APPROVED → Gold DB entry (manual_extension_assisted_capture source)
IF REJECT → Archive (moved to history)
IF KEEP_IN_SILVER → Stay in Silver (revisit later)
IF NEEDS_FIX → Show metadata editor
```

---

## Metrics (Weekly)

```
Silver DB Health Dashboard
┌────────────────────────────────────────┐
│ Total Silver Decisions:        105     │
│   PENDING:                     12      │
│   APPROVED (→ Gold):           72      │
│   KEEP_IN_SILVER:              15      │
│   NEEDS_METADATA_FIX:           4      │
│   REJECTED:                     2      │
│                                        │
│ Validator Metrics:                     │
│   PASS rate:                   100%    │
│   Avg processing time:         2.3s    │
│   PII flagged:                  1      │
│   Duplicates detected:          0      │
│                                        │
│ Cüneyt Review:                        │
│   Avg time to review:         6 days   │
│   Approval rate:              68.6%    │
│   Last review:         2026-06-16     │
│                                        │
│ Gold Promotion:                       │
│   This week:                   12     │
│   This month:                  45     │
└────────────────────────────────────────┘
```

---

## Next Actions

1. **Create SQLite schema** (silver_decisions.db)
2. **Build Cüneyt Dashboard** (simple web UI or CLI)
3. **Implement intake cron** (daily: adapter → validator → Silver DB)
4. **MVP Collection** (100 Usulsüz Tebligat + Meskeniyet + İhalenin Feshi)
5. **Cüneyt Review Sprint** (review all 100, classify)
6. **Gate Check** (100% reviewed, metrics pass → Phase 2)
7. **Gold Promotion Batch** (move approved decisions to Gold)

---

## Success Metric

**Silver DB is successful when:**

✅ Chrome Extension + yargi-mcp feed into same Silver DB  
✅ Cüneyt Bey review latency < 2 weeks per 100 decisions  
✅ APPROVED → Gold promotion is smooth and audited  
✅ Duplicate rate < 1%  
✅ Scaling to 1000 decisions doesn't break architecture  
✅ Gold DB remains pristine (0 bad decisions from Silver)

---

## This Is Not (Common Misconceptions)

❌ NOT an automatic Gold DB feeder  
❌ NOT a replacement for Cüneyt Bey review  
❌ NOT a bulk data import system  
❌ NOT a Chrome Extension alternative  
❌ NOT a quick way to 1000 decisions without review

## This IS

✅ Unified intake layer for all sources  
✅ Scaling Cüneyt Bey's expert judgment  
✅ Safe candidate holding area  
✅ Audit trail and traceability  
✅ Foundation for 5-10 year data growth  

---

*Architecture v1.0 | Ready for Principal Architect review | Cüneyt Matrix validated*
