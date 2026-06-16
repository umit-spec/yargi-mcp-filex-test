# FILEX SILVER DB PHASE 1 — MASTER PROMPT

You are assuming four roles simultaneously:
- **Principal Architect** (design decisions)
- **Legal Knowledge Engineer** (domain constraints)
- **Data Pipeline Engineer** (implementation roadmap)
- **Product Risk Reviewer** (Gold DB safety)

---

## Critical Success Understanding

**Today's Achievement (16.06.2026):**

The first data source outside Chrome Extension passed Filex Validator.

```
Emsal (yargi-mcp)
  → Adapter
  → raw_capture.v1.json
  → validate_raw_capture.ts
  → ROUTING: PASS
  → context_packet generated
```

**This is not about "collecting 1000 decisions."**

This is about proving Filex can accept multiple sources while keeping Gold DB pristine.

**You are now tasked with formalizing this as Filex's second intake channel.**

---

## Immutable Rules

### Rule 1: Gold DB Remains Untouched
- Zero automatic writes to Gold DB
- Cüneyt Bey approval = only gate to Gold
- No schedule or batch job can bypass this

### Rule 2: Validator Is Sacred
- `validate_raw_capture.ts` must never change
- All sources (Chrome Extension, yargi-mcp, future) pass through same Validator
- Validator output (context_packet) is the lingua franca

### Rule 3: Chrome Extension Pipeline Survives
- Manual intake via Chrome Extension continues unchanged
- yargi-mcp becomes parallel channel
- Both feed into same Silver DB
- No breaking changes to existing workflow

### Rule 4: Single Atomic Decisions
- 1 decision = 1 capture JSON file
- NO arrays, NO bulk wrappers, NO nested lists
- Validator expects single object

### Rule 5: Human Remains Gatekeeper
- Every Silver decision requires explicit Cüneyt Bey action
- No background approval or auto-promotion
- Cüneyt Matrix is the control interface

---

## What You're Building

**Silver DB** is the **validated-but-unapproved decision candidate repository.**

- ✅ Validator gate passed
- ✅ Metadata extracted
- ✅ PII flagged (if needed)
- ⏳ Awaiting Cüneyt Bey review/decision
- ❌ NOT in Gold DB yet
- ❌ NOT automatic promotion possible

---

## Architecture Brief

See `SILVER_DB_ARCHITECTURE.md` for full details. Quick overview:

**Schema:** SQLite with fields:
- capture_id, source_domain, court, esas_no, karar_no, decision_date
- topic, subtopic, legal_area
- validator_routing, context_packet_id
- review_status (PENDING | APPROVED | KEEP_IN_SILVER | NEEDS_METADATA_FIX | REJECT)
- audit fields (created_at, reviewed_by, gold_promoted_at)

**Cüneyt Matrix:** Per decision, Cüneyt Bey chooses:
1. APPROVED → move to Gold DB
2. KEEP_IN_SILVER → archive in 6 months
3. NEEDS_METADATA_FIX → show editor, re-review
4. REJECT → delete from Silver

**MVP:** 100 decisions (40 Usulsüz Tebligat + 30 Meskeniyet + 30 İhalenin Feshi)

**Gate:** Must review all 100, achieve ≥70% APPROVED rate, <10% REJECT before Phase 2

---

## Your Immediate Tasks

### Task 1: Finalize Silver DB Schema

**Current state:** Architecture document outlines schema  
**Your task:**
- [ ] SQLite DDL (with comments)
- [ ] Migration strategy (if updating existing DB)
- [ ] Indexing plan (query performance for weekly dashboard)
- [ ] Backup/archival plan
- [ ] Decision: Cloud SQLite (cloud.sqlite.org) or local .db file?

**Validation:** Can you insert context_packet as-is from Validator? Yes/No + why

### Task 2: Build Cüneyt Dashboard (MVP)

**Current state:** Sketch in SILVER_DB_ARCHITECTURE.md  
**Your task:**
- [ ] CLI tool (faster) or Web UI (nicer)?
- [ ] Show PENDING decisions one-by-one
- [ ] Buttons: [APPROVED] [KEEP_IN_SILVER] [NEEDS_FIX] [REJECT]
- [ ] Text field for review_notes
- [ ] Dropdown for argument_category (tahkim, hakimsiz_karar, etc)
- [ ] Slider for confidence_score (AI suggestion, Cüneyt overrides)

**Validation:** Can Cüneyt review 10 decisions in <5 minutes? Yes/No + UX issues

### Task 3: Intake Pipeline (Cron Job)

**Current state:** Manual adapter runs in `pipeline/yargi_mcp_adapter.py`  
**Your task:**
- [ ] Schedule: daily 23:00 UTC (or other off-peak?)
- [ ] Intake logic:
  1. Search Emsal with topic keywords (usulsuz_tebligat, meskeniyet, ihaleinin_feshi)
  2. For each result: fetch full text
  3. Run adapter → raw_capture.v1.json
  4. Run validator → context_packet
  5. If PASS: INSERT into silver_decisions
  6. If HOLD/REJECT: log (don't insert)
- [ ] Logging: What goes to Slack? To file?
- [ ] Idempotency: prevent duplicates on re-run?

**Validation:** Can it run unattended for 7 days without human intervention? Yes/No + failure modes

### Task 4: Duplicate Detection

**Current state:** UNIQUE constraint on (esas_no, karar_no, decision_date)  
**Your task:**
- [ ] Is this constraint sufficient?
- [ ] What if Emsal returns same decision under different keyword search?
- [ ] Hash-based dedup? (full_text_hash)
- [ ] Manual review for edge cases?

**Validation:** How would you catch "same decision, entered twice with 1-day date diff"?

### Task 5: PII Screening

**Current state:** Adapter flags with pii_initial_check  
**Your task:**
- [ ] Current PII detection rules sufficient?
- [ ] Should Silver DB store full_text or only excerpt?
- [ ] What triggers manual_review_required → HOLD?
- [ ] Backup plan if PII detected: quarantine in Silver or reject?

**Validation:** Can you store 1000 full judicial texts (Turkish) without regulatory risk?

### Task 6: Topic Classification

**Current state:** Adapter doesn't classify (topic=NULL)  
**Your task:**
- [ ] Hardcode topic based on Emsal search keyword?
- [ ] Use AI/keyword matching (confidence_score)?
- [ ] Cüneyt Bey overrides in dashboard?
- [ ] What if decision spans multiple topics?

**Validation:** Is 80% classification accuracy acceptable for MVP?

---

## Risk Assessment Framework

For each design decision, evaluate:

| Risk | Mitigation | Monitor | Alert Threshold |
|------|------------|---------|-----------------|
| **Gold DB Contamination** | Cüneyt explicit approval | APPROVED count | If >90% auto |
| **Duplicates** | UNIQUE constraint + hash | Weekly check | If >5% |
| **PII Leakage** | pii_status flag, quarantine | Manual audit | Any flagged |
| **Authority Mixing** | chamber field, authority_rank | Query by source | Mixed without intent |
| **Uncontrolled Growth** | Phase gates (100→200→1K) | PENDING count | If >500 |
| **Validator Drift** | Never modify Validator | Run tests | Any changes |
| **Chrome Ext Breakage** | Separate intake path | E2E tests | Manual entry fails |

---

## Deliverables (This Phase)

### Code

- [ ] `schema/silver_decisions.sql` (DDL)
- [ ] `dashboard/cuneyt_matrix.py` (CLI or web UI)
- [ ] `pipeline/intake_scheduler.py` (cron entry point)
- [ ] `tests/silver_db_test.py` (schema + pipeline tests)

### Documentation

- [ ] `SILVER_DB_OPERATIONS.md` (how to run, troubleshoot)
- [ ] `CUENEY_REVIEW_GUIDE.md` (how to use dashboard)
- [ ] `INTAKE_METRICS.md` (weekly dashboard screenshot)

### Data

- [ ] `silver_decisions.db` (initialized, ready for MVP)
- [ ] 1-2 test inserts (verify schema works)

### Success Criteria

✅ Schema reviewed + approved  
✅ Dashboard usable by Cüneyt Bey  
✅ Intake cron runs without error for 7 days  
✅ 0 duplicates in first 50 decisions  
✅ 0 PII leakage  
✅ Validator integration seamless  
✅ Can scale to 100 MVP with no changes  

---

## This Week's Scope

**DO:**
- Finalize Silver DB schema
- Build MVP Cüneyt dashboard (CLI is fine)
- Set up intake cron job (daily 23:00)
- Collect first 10-20 decisions (sanity check)

**DON'T:**
- Collect 1000 decisions yet
- Assume 70% APPROVED rate (gate requires review)
- Modify Validator
- Write to Gold DB
- Break Chrome Extension workflow

---

## Success Metric

Silver DB Phase 1 succeeds when:

✅ 100 decisions collected (Usulsüz Tebligat + Meskeniyet + İhalenin Feshi)  
✅ 100% reviewed by Cüneyt Bey  
✅ ≥70% APPROVED rate → Gold DB  
✅ <10% REJECT rate  
✅ 0 duplicates  
✅ 0 Gold DB contamination  
✅ All metrics pass gate → Phase 2 approved

**Timeline:** 2-3 weeks (allow time for Cüneyt Bey's review schedule)

---

## Context & Prior Work

**What already works:**

1. **Validator proved:** Single Emsal decision passes validate_raw_capture.ts
2. **Adapter works:** Emsal → raw_capture.v1.json conversion confirmed
3. **Schema designed:** SILVER_DB_ARCHITECTURE.md (review + refine)
4. **Cüneyt Matrix sketched:** Review interface design (build it)

**What you're adding:**

1. Production Silver DB (SQLite, tested)
2. Daily intake automation
3. Cüneyt review dashboard
4. Risk monitoring
5. Phase gate logic

---

## Contact/Escalation

- **Architecture questions:** Can MVP be extended to 1000 decisions without breaking? → Architect
- **Legal/topic classification:** Is "Usulsüz Tebligat" broad enough for 40 decisions? → Legal
- **Cüneyt Bey workflow:** How many hours per week for 100 reviews? → Product

---

## Anti-Patterns (Do NOT Do)

❌ Insert Silver decisions directly into Gold DB  
❌ Create separate Validator for Silver (breaks architecture)  
❌ Bulk upload without Cüneyt review  
❌ Store full text in SQLite (use hash, external storage)  
❌ Skip PII detection  
❌ Assume 90%+ approval (red flag → halt intake)  
❌ Grow to 500+ decisions before MVP gate  
❌ Modify Chrome Extension pipeline  

---

## Timeline Proposal

| Week | What | Owner | Gate |
|------|------|-------|------|
| Week 1 (now) | Schema + Dashboard MVP | You | Schema reviewed |
| Week 1-2 | Intake cron job + testing | You | 0 errors in 50 runs |
| Week 2 | Collect first 100 MVP | Automation | Cüneyt ready to review |
| Week 2-3 | Cüneyt review all 100 | Cüneyt Bey | ≥70% APPROVED |
| Week 3 | Gold promotion batch | Automation | All metrics pass |
| Week 3+ | Phase 2 (expand topics) | You | Decision to proceed |

---

## You Are Ready When

You can answer these questions in <30 seconds each:

1. What happens if Emsal returns same decision twice in one week?
2. How does Cüneyt Bey reject a Silver decision?
3. Where does full text of 1000 decisions get stored?
4. How would you catch a bad decision that made it to Gold?
5. What prevents Silver intake from breaking Chrome Extension?
6. How do you know 100 decisions is enough for MVP?

---

**This is the moment Filex architecture scales beyond Chrome Extension.**

**Execute with the discipline that this is a gate-locked MVP, not a bulk data project.**

**Cüneyt Bey remains the expert authority.**

---

*Master Prompt v1.0 | Silver DB Phase 1 | Ready for Principal Architect*
