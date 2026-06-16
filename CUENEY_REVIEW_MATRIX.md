# Cüneyt Review Matrix — Filex Product Manifesto

## What Filex Is NOT

❌ A court decision search engine  
❌ A legal database aggregator  
❌ An automated legal research tool  
❌ A replacement for lawyer expertise  
❌ A bulk data collection project

---

## What Filex IS

✅ **A decision intelligence system that transforms expert legal reflection into a curated database.**

Filex's engine is not algorithmic. Filex's engine is **Cüneyt Bey's expert judgment**, scaled.

---

## The Core Value Proposition

```
Many Data
    ↓
Expert Filter
    ↓
Few But Powerful Gold Decisions
```

Filex's competitive advantage is **curation at scale**, not volume.

**Volume without curation is a garbage dump.**  
**Curation without scale is manual work.**  
**Curation at scale is a moat.**

---

## Cüneyt Matrix: The Filtering Mechanism

For each Silver candidate, Cüneyt Bey selects ONE of five actions:

### 1. GOLD_APPROVED
**Decision:** This decision is ready for Gold DB.  
**Action:** Insert into gold_decisions table.  
**Criteria:** Metadata complete, authority appropriate, precedent value clear, no PII issues.  
**Result:** Decision becomes permanent Filex asset (1 of ~1000).

### 2. KEEP_IN_SILVER
**Decision:** Not ready now, but may be valuable later.  
**Action:** Archive in Silver DB, revisit in 6 months.  
**Criteria:** Good metadata, legal substance, but needs more context or market timing.  
**Result:** Decision stays in Silver, searchable but not promoted.

### 3. NEEDS_METADATA_FIX
**Decision:** Decision has merit but metadata is incomplete/wrong.  
**Action:** Show metadata editor to submitter or Filex team.  
**Criteria:** Legal text is sound, but esas_no/karar_no/date/chamber unclear or incorrect.  
**Result:** Decision re-submitted with corrected metadata, returns to Cüneyt review.

### 4. REJECT
**Decision:** This decision does not meet Filex standards.  
**Action:** Move to archive (not public, but retained for audit).  
**Criteria:** Poor authority (summary judgment), conflicting precedent, PII issues unresolvable, irrelevant legal area.  
**Result:** Decision removed from active review, logged for pipeline improvement.

### 5. DUPLICATE
**Decision:** This decision is already in Silver/Gold under different capture_id.  
**Action:** Mark as duplicate, link to original, do not insert.  
**Criteria:** Same esas_no/karar_no + decision_date (within 1 day), or same full text hash.  
**Result:** Duplicate dedup prevents bloat; original kept, clone archived.

---

## Why Cüneyt Matrix Matters

### It Prevents Scaling Disasters

Without explicit filtering:
- Silver DB grows to 10,000 mediocre decisions
- Gold DB gets contaminated with low-authority kararlar
- Filex becomes "a pile of cases," not "the curated cases"
- Competitive advantage disappears

### It Preserves Filex's Moat

With Cüneyt Matrix:
- Every Gold decision passed Cüneyt's expert eye
- Decisions are not just numerous, they're **selected**
- Competitors can collect data; Filex curates it
- Gold DB quality compounds over time

### It Scales Cüneyt's Judgment

One person cannot manually review 1000 court decisions in reasonable time.

But Cüneyt CAN:
- Set decision criteria (rules of the matrix)
- Sample-review (20 of 100 decisions, catch systematic issues)
- Delegate metadata fixes to team
- Override automated classifications

This is **how expertise scales**.

---

## Cüneyt's Review Workflow

**Weekly (target: 20-30 decisions reviewed per week)**

1. Dashboard shows PENDING decisions (sorted by topic/confidence)
2. Cüneyt reads decision excerpt (selected_text_excerpt from Silver DB)
3. Clicks ONE of five buttons: [GOLD_APPROVED] [KEEP] [NEEDS_FIX] [REJECT] [DUPLICATE]
4. Adds optional review_notes (1-2 sentences)
5. Next decision appears
6. Metrics update in real-time

**Monthly (target: 80-120 decisions reviewed per month)**

1. Report: APPROVED count, REJECT patterns, KEEP rate
2. If reject rate > 20%, investigate root cause
3. If APPROVED rate < 5%, pipeline may be too selective
4. Adjust intake keywords/sources if needed
5. Plan Phase 2 expansion or hold MVP

---

## Quality Signals Cüneyt Uses

When reviewing a decision, Cüneyt implicitly evaluates:

| Signal | Green | Yellow | Red |
|--------|-------|--------|-----|
| **Authority** | Yargıtay > BAM > İlk Derece | Mixed authority | Beledi karar |
| **Precedent** | Establishes rule | Applies known rule | Routine case |
| **Metadata** | Complete, correct | 1-2 fields unclear | Multiple errors |
| **Legal Area** | Execution/Insolvency | Related area | Outside scope |
| **PII** | None detected | Addressees mentioned | Personal info visible |
| **Duplicates** | Unique | Similar (but new angle) | Already in Gold |

**GOLD_APPROVED:** 5/5 green or 4/5 green + explanation  
**KEEP_IN_SILVER:** 3/5 green, substance is sound, context unclear  
**NEEDS_METADATA_FIX:** 4/5 green, but metadata breaks  
**REJECT:** ≤2/5 green, or critical PII issue  
**DUPLICATE:** Exact match to existing decision

---

## The Number Behind the Philosophy

**Target Gold DB size: ~1,000 decisions over 3 years**

Why 1,000?
- Enough to cover major execution/insolvency topics
- Small enough that Cüneyt can meaningfully review (3 per week = 3 years)
- Focused enough to maintain quality
- Large enough to provide precedent coverage

NOT 10,000. NOT 100,000.

**1,000 pristine decisions > 100,000 mediocre decisions.**

---

## Anti-Patterns (Do NOT Let This Happen)

❌ "Cüneyt reviewed 5%, so auto-approve the rest" (defeats purpose)  
❌ "70%+ approval rate = success" (means filter isn't filtering)  
❌ "Reject rate too high, loosen criteria" (correct response is investigate)  
❌ "10 decisions worked, scale to 1000 now" (how disasters happen)  
❌ "Silver DB has 5000 decisions pending" (halt, something is broken)  
❌ "Cüneyt Bey overwhelmed, skip review" (integrity compromised)  
❌ "This decision almost fits criteria" (close doesn't count in curation)

---

## Governance

### Who Can Change the Matrix?

| Action | Authority | Frequency |
|--------|-----------|-----------|
| Apply matrix (APPROVED/REJECT/etc) | Cüneyt Bey | Per decision |
| Refine criteria | Product team + Cüneyt | Quarterly review |
| Add new statuses | Engineering + legal | Never (locked 1.0) |
| Override to Gold | Cüneyt only | Explicit approval |
| Delete from Silver | Cüneyt only | With documented reason |

### Audit Trail

Every matrix decision is logged:
```json
{
  "capture_id": "yargi_mcp_emsal_20260616_001",
  "review_status": "GOLD_APPROVED",
  "reviewer": "cuneyt",
  "review_date": "2026-06-17T14:22:00Z",
  "review_notes": "Precedent on usulsuz tebligat, clean authority, no PII.",
  "confidence_score": 0.85
}
```

Filex's integrity is tied to this audit trail.

---

## Success Indicators

**Good Signs:**
- ✅ REJECT rate: 10-20% (filter is working)
- ✅ KEEP_IN_SILVER rate: 30-40% (future optionality)
- ✅ DUPLICATE rate: 5-15% (normal in legal data)
- ✅ Cüneyt completes 20+ reviews per week
- ✅ APPROVED rate: 20-40% (selective curation)
- ✅ Gold DB grows by 50-100 decisions per year

**Warning Signs:**
- ⚠️ APPROVED rate > 60% (not filtering enough)
- ⚠️ REJECT rate < 5% (intake too selective)
- ⚠️ Cüneyt reviews < 10 per week (bottleneck)
- ⚠️ Silver PENDING > 200 (backlog growing)
- ⚠️ Duplicate rate > 20% (intake quality issue)

**Red Flags:**
- 🔴 APPROVED rate > 80% (gate is broken)
- 🔴 Silver DB > 1000 decisions (uncontrolled growth)
- 🔴 No Cüneyt review for > 2 weeks (integrity gap)
- 🔴 PII incident (critical)
- 🔴 Bypass of matrix (discipline failure)

---

## The Tempo (Non-Negotiable)

```
Phase 1: 10 decisions
  └─ Manual run
  └─ Validator: 100% PASS
  └─ Gate: Schema validated ✓

Phase 2: 100 decisions (MVP)
  └─ Manual batch
  └─ Cüneyt reviews 20+
  └─ Gate: Metrics pass ✓

Phase 3: 1000 decisions
  └─ Daily cron (proven safe)
  └─ Ongoing Cüneyt review
  └─ Gate: Quality maintained ✓
```

**Do NOT skip steps.**  
**Do NOT accelerate timeline without data.**  
**Do NOT auto-promote Silver to Gold.**

---

## For Future Stakeholders

If you're reading this:

1. **Cüneyt is not a bottleneck. Cüneyt is the value.**  
   His review latency is not a problem to solve; it's a feature that prevents database pollution.

2. **More data is NOT better. Better data is better.**  
   Filex's competitive advantage is precision curation, not volume.

3. **The Matrix is not bureaucracy. The Matrix is integrity.**  
   Every APPROVED decision is a promise: "This decision passed expert review."

4. **Scale comes from Cüneyt's rules, not from Cüneyt's time.**  
   Once the matrix is proven (100 reviewed), we automate the intake. We never automate the judgment.

---

## Product Promise

**Every decision in Filex Gold DB has been:**

✅ Extracted from official source (court website or yargi-mcp)  
✅ Validated through Filex Validator (schema-locked)  
✅ Reviewed by Cüneyt Bey or his delegation  
✅ Classified through the Cüneyt Matrix  
✅ Either GOLD_APPROVED or subject to documented reason  

**No decision in Gold DB is there by accident.**  
**No decision was auto-promoted.**  
**No decision bypassed expert review.**

This is why Gold DB has value.

---

*Cüneyt Review Matrix v1.0 — Locked for Phase 1+  
This document is the product manifesto. Do not change without unanimous stakeholder approval.*
