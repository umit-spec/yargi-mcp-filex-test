# Expert Signal Model — The Real Moat

## What Competitors Cannot Copy

**Competitors can copy:**
- Court decisions (free on government sites)
- Database schema (straightforward)
- Chrome extension (technically feasible)
- Validator logic (documented)
- UI/UX (observable)

**Competitors CANNOT copy:**
- Cüneyt Bey's legal expertise
- His decision-making criteria
- His pattern recognition heuristics
- His judgment about precedent value
- His authority-weighting logic

---

## The Real Asset

Filex's strategic moat is not **Gold DB** (decisions).

Filex's moat is **Cüneyt's decision traces** (why/how decisions are selected).

```
Gold DB (copyable)
    ↓
Expert decisions about Gold DB (not copyable)
    ↓
Filex's competitive advantage
```

After 6-12 months with this data:
- We understand **Cüneyt's heuristics**
- We can predict **his approval patterns**
- We can identify **gap decisions he'd approve**
- We can **train other experts** using his model
- We can **automate triage** (with guardrails)

---

## The Model: Expert Signals

Every time Cüneyt Bey reviews a decision, he generates signals:

### Decision: GOLD_APPROVED

**Captured data:**
```json
{
  "capture_id": "yargi_mcp_emsal_20260616_001",
  "review_result": "GOLD_APPROVED",
  
  // Why approved? (required)
  "expert_review_reason": "TK 21/2 maddesi usulsüz tebligat yorumunda öncü karar",
  
  // How expert reasons about it (required)
  "expert_signals": {
    "precedent_strength": "strong",      // weak/moderate/strong
    "authority_weight": 9,                // 1-10, rare > 8
    "topic_coverage": "gap-filling",      // routine/gap-filling/novel
    "legal_certainty": "established",     // emerging/established/disputed
    "decision_date_relevance": "current", // outdated/historical/current/recent
    "draft_utility": 9,                   // 1-10, practical use
    "teaching_value": 8,                  // 1-10, for new lawyers
    "appellate_risk": 2                   // 1-10, risk of reversal
  },
  
  // Confidence in decision (required)
  "expert_confidence": 0.95,  // 0.0-1.0
  
  // Notes for audit (optional)
  "signal_notes": "BAM karşıt içtihadı var, ama Yargıtay'ın son tutumu bu yönde"
}
```

### Decision: KEEP_IN_SILVER

```json
{
  "review_result": "KEEP_IN_SILVER",
  "expert_review_reason": "Haklı olabilir ama Yargıtay jurisprudence henüz netleşmemiş",
  "expert_signals": {
    "precedent_strength": "emerging",
    "legal_certainty": "disputed",
    "decision_date_relevance": "historical",
    "timing_sensitivity": "high"
  },
  "revisit_after_months": 12
}
```

### Decision: REJECT

```json
{
  "review_result": "REJECT",
  "expert_review_reason": "Yargıtay tutarlı içtihadına aykırı, çelişkili karar",
  "expert_signals": {
    "precedent_strength": "weak",
    "authority_weight": 3,
    "legal_certainty": "disputed",
    "contradicts_established": true
  },
  "reject_reason": "precedent_conflict"
}
```

### Decision: NEEDS_METADATA_FIX

```json
{
  "review_result": "NEEDS_METADATA_FIX",
  "expert_review_reason": "Karar metni iyi ama tarih ve esas numarası hatalı",
  "missing_fields": ["decision_date", "esas_no"],
  "expert_signals": {
    "content_quality": "high",
    "metadata_quality": "low"
  }
}
```

---

## Why This Data Is Strategic

### Short Term (3-6 months)
- Understand approval patterns
- Identify missing topics
- Improve intake keywords
- Train new reviewers using Cüneyt's logic

### Medium Term (6-12 months)
- Build **approval predictor** (which decisions would Cüneyt approve?)
- Triage incoming decisions (auto-flag high-signal candidates)
- Identify gaps (what topics need more coverage?)
- Improve Gold DB quality metrics

### Long Term (1-3 years)
- **Scale Cüneyt's judgment** (other experts using his model)
- Automate triage (with human override)
- Licensing opportunity (sell model to other platforms)
- Investment thesis (expertise-as-asset, not data-as-asset)

---

## The Database Fields (Phase 1)

**Add to silver_decisions table:**

```sql
-- Expert review signals
expert_review_reason TEXT NOT NULL,      -- Why approved/rejected/etc
expert_signals JSON,                      -- Structured signals (see below)
expert_confidence REAL DEFAULT 0.5,      -- 0.0-1.0 confidence
expert_notes TEXT,                        -- Audit notes

-- Metadata for future learning
review_duration_seconds INTEGER,          -- How long did review take?
review_flags TEXT,                        -- Any special flags?
requires_second_review BOOLEAN DEFAULT 0, -- Uncertain decisions
```

**expert_signals schema:**

```json
{
  "precedent_strength": "weak|moderate|strong",
  "authority_weight": 1-10,
  "topic_coverage": "routine|gap-filling|novel",
  "legal_certainty": "emerging|established|disputed",
  "decision_date_relevance": "outdated|historical|current|recent",
  "draft_utility": 1-10,
  "teaching_value": 1-10,
  "appellate_risk": 1-10,
  "contradicts_established": boolean,
  "timing_sensitive": boolean
}
```

---

## The Real Phase 2 Objective

**NOT:** "Collect 100 decisions"

**YES:** "Capture 100 expert review signals from Cüneyt Bey"

After 100 decisions with signals:
- We have a dataset of expert reasoning
- We can build predictive models
- We can measure consistency
- We can identify knowledge gaps
- We can tell investors: "We're learning expert judgment"

---

## Example: What We Learn From Signals

**After 50 reviews, we discover:**

| Topic | Avg Approval Rate | Avg Authority Weight | Avg Precedent Strength |
|-------|-------------------|----------------------|------------------------|
| Usulsüz Tebligat | 35% | 7.2 | strong |
| Meskeniyet | 25% | 5.8 | moderate |
| İhalenin Feshi | 60% | 8.1 | strong |
| Yetki İtirazı | 10% | 4.2 | weak |

**Insights:**
- İhalenin Feshi has high approval = we need more of this topic
- Yetki İtirazı has low approval = probably low utility for our market
- Authority weight varies = Cüneyt weighs different authorities differently

This is **expert knowledge being revealed**.

---

## For Investors

When investors ask: "What differentiates Filex?"

**Old answer:** "We have curated court decisions."  
→ Competitors can do the same.

**New answer:** "We have structured expert judgment about which decisions matter and why."  
→ This is much harder to replicate.

**With 1000+ expert signals:**
- We can **predict** which decisions experts care about
- We can **automate** parts of review (with human gate)
- We can **license** the model to other legal tech platforms
- We can **train** other experts using Cüneyt's heuristics

---

## The Broader Play

Expert Signal Model is not just about Gold DB curation.

It's about **building a decision-intelligence product** that:

1. **Captures** expert judgment (Cüneyt Matrix)
2. **Structures** it (Expert Signals)
3. **Learns** from it (ML on signals)
4. **Scales** it (other experts, automation)
5. **Monetizes** it (licensing, APIs, SaaS)

The decisions themselves? Commodity.  
The **judgment about decisions**? Differentiated.

---

## Implementation (Phase 1)

**Just add to the schema now:**
```sql
expert_review_reason TEXT NOT NULL,
expert_signals JSON,
expert_confidence REAL DEFAULT 0.5,
expert_notes TEXT
```

**Cüneyt Matrix UI includes fields:**
- [Text box] Review reason: ________________
- [Sliders] Authority (1-10), Precedent strength, Draft utility
- [Checkboxes] Contradicts established? Timing sensitive?
- [Text box] Additional notes

**No complex ML needed yet.**  
Just structured data capture.

After 100 reviews, we'll see patterns that no competitor has.

---

## Protection

This data is Filex's property.

- Every signal is Cüneyt Bey's proprietary judgment
- Not publicly visible
- Not shared with sources
- Backed up and encrypted
- Only shared with trusted team members

This is the crown jewel. Treat it as such.

---

## Timeline

| Phase | What | Why |
|-------|------|-----|
| Phase 1 | Add fields, collect signals | Build dataset |
| Phase 2 | Analyze patterns, train predictors | Understand heuristics |
| Phase 3 | Use signals for automation | Scale expertise |
| Year 2+ | Licensing, APIs, models | Monetize |

---

## The Insight

Most legal tech companies collect **data**.

Filex collects **expert behavior about data**.

This is the moat.

---

*Expert Signal Model v1.0 — Locked for Phase 1+  
This is the secret sauce. Guard it carefully.*
