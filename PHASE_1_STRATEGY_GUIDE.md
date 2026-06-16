# Phase 1 Strategy Guide — Filex Architecture Locked

## The Insight (One Sentence)

**Filex's value is not court decisions (commodity), not curated decisions (rare), but decision-usage strategy in litigation (defensible moat).**

---

## The 4-Tier Model (How Value Flows)

```
LAYER 1: COURT DECISIONS (Commodity)
         "Here is a court decision"
         → Anyone can find this (Google, UYAP)
         → Not differentiated

LAYER 2: EXPERT EVALUATION (Rare)
         "Cüneyt Bey says this is a good decision"
         → Hard to scale
         → Better than layer 1, but still just data

LAYER 3: STRATEGIC ROLE ⭐ THE MOAT
         "This decision is used as [primary argument | counter-argument | burden shift | ...]"
         → Almost nobody captures this
         → Lawyers actually need this
         → Creates defensible competitive advantage

LAYER 4: TOPIC CONTEXT (Searchability)
         "This is about TK 21/2"
         → Enables layer 3 to be found
         → Supporting layer, not differentiator
```

---

## Why Layer 3 Is The Moat

### The Lawyer's Real Problem

NOT: "Find a court decision"  
(Google, UYAP, Emsal solve this)

YES: "How do I use this decision in my case?"  
(Almost nobody solves this)

### Strategic Roles (What We Capture)

- **Ana daynak** (primary argument): This decision is the core of my case
- **Destekleyici** (supporting): This confirms my position
- **Karşı görüşü çürütür** (counter-argument): This refutes opposing counsel
- **İspat yükü argümanı** (burden shift): This changes who must prove what
- **Usul argümanı** (procedural): This is a procedural basis
- **Esas argümanı** (substantive): This is a substantive basis

### Example (Why This Matters)

**Old approach (Layer 1-2):**
Search: "meskeniyet kararları"  
Result: 500 court decisions about meskeniyet  
Problem: Lawyer doesn't know which one to cite for which argument

**New approach (Layer 3):**
Lawyer states: "I need to argue that the property is inhabited"  
Result: These 12 decisions work as primary argument → Here's why  
Layer 3 learned: "These 12 decisions share X characteristics → use as ana daynak"

---

## The Five Strategic Documents (Locked for Phase 1)

### 1. CUENEY_REVIEW_MATRIX.md
**Purpose:** The product manifesto  
**Contains:** 5-status review decisions (GOLD_APPROVED | KEEP | NEEDS_FIX | REJECT | DUPLICATE)  
**Why it matters:** Defines what "good curation" means — not volume, not speed, but Layer 3 depth  
**Key insight:** Cüneyt is not a bottleneck; he is the gatekeeper. His review latency is a feature.

### 2. SILVER_DB_ARCHITECTURE.md
**Purpose:** The database schema and intake staging area  
**Contains:** SQLite schema for validated-but-unapproved decisions  
**Why it matters:** Ensures all sources (Chrome Extension, yargi-mcp, future) feed into one pipeline  
**Key field:** `strategic_role` — layer 3 captured in the database

### 3. EXPERT_SIGNAL_MODEL.md
**Purpose:** What we learn from expert judgment  
**Contains:** The data structure that captures Layer 3 (and Layers 1-2)  
**Why it matters:** Transforms decisions from "curated list" to "learning dataset"  
**Real value:** After 100 evaluations with Layer 3 filled in, the model learns decision strategy

### 4. EXPERT_CONSISTENCY_STUDY.md
**Purpose:** The validation protocol that proves Layer 3 is reproducible  
**Contains:** EER (Expert Explainability Rate) as primary KPI, plus consistency/metadata/authority tests  
**Why it matters:** Determines if Cüneyt's Layer 3 judgments are learnable or just intuitive  
**Success looks like:** EER ≥85% — experts can articulate WHY a decision plays a certain strategic role

### 5. MASTER_PROMPT_SILVER_DB_PHASE_1.md
**Purpose:** The implementation roadmap  
**Contains:** 3-phase intake (manual 10 → MVP 100 → cron) + task breakdown  
**Why it matters:** Prevents scaling disasters (the "early growth intoxication" risk)  
**Discipline enforced:** 10 perfect → 100 measured → 1000 controlled

---

## The Implementation Flow

```
PHASE 1A (Week 1): Proof of Concept
  └─ Run adapter on 10 decisions (manual)
  └─ Validator confirms 100% PASS
  └─ Insert into Silver DB
  └─ Gate: Schema works, zero PII leakage

PHASE 1B (Week 1-2): MVP Collection
  └─ Expand to 100 decisions (Usulsüz Tebligat + Meskeniyet + İhalenin Feshi)
  └─ Still manual (not automated)
  └─ Monitor: duplicate rate, quality
  └─ Gate: All 100 validated, Cüneyt ready to review

PHASE 1C (Week 2-3): Expert Evaluation
  └─ Cüneyt reviews 100 decisions via dashboard
  └─ Records 4-tier evaluation (Outcome | Quality Signals | Strategic Role | Topic)
  └─ Measures EER (explainability) on Layer 3
  └─ Gate: EER ≥85%, decisions are articulable

PHASE 1D (Week 3-4): Consistency Validation
  └─ Run Expert Consistency Study on subset (50 decisions, repeat at day 30)
  └─ Metadata sensitivity test (strip labels, retest)
  └─ Authority bias test (relabel authority, retest)
  └─ Results: ECR, MI, AI scores
  └─ Gate: Heuristics are reproducible (or redesign if not)

PHASE 1E (Week 4+): Daily Automation
  └─ Only after all gates pass
  └─ Schedule: daily cron, 23:00 UTC
  └─ Intake: search Emsal → fetch text → validate → Silver DB
  └─ Logging: Slack notifications, weekly dashboard
  └─ Gate: 7 days unattended, zero errors
```

---

## The 4-Tier UI (How Cüneyt Evaluates)

```
════════════════════════════════════════════════════════════════

KARAR REVIEW

════════════════════════════════════════════════════════════════

[Decision summary excerpt from Silver DB]

════════════════════════════════════════════════════════════════

SEVİYE 1: KARAR SONUCU (Decision Outcome)

( ) GOLD_APPROVED
( ) KEEP_IN_SILVER
( ) NEEDS_METADATA_FIX
( ) REJECT
( ) DUPLICATE

════════════════════════════════════════════════════════════════

SEVİYE 2: KALİTE SİNYALLERİ (Quality Signals)

☐ Güçlü içtihat (strong precedent)
☐ Yerleşik uygulama (established practice)
☐ Dilekçede kullanılabilir (usable in brief)
☐ Güncel yaklaşım (current approach)
☐ HGK desteği (HGK support)
☐ Çelişkili karar (conflicting)
☐ Tekil olay (unique case)

════════════════════════════════════════════════════════════════

SEVİYE 3: STRATEJİK ROL ⭐ CRITICAL (Strategic Role)

How would an avukat use this decision in case strategy?

☐ Ana daynak (primary argument)
☐ Destekleyici içtihat (supporting)
☐ Karşı görüşü çürütür (counter-argument)
☐ İspat yükü argümanı (burden shifting)
☐ Usul argümanı (procedural)
☐ Esas argümanı (substantive)

════════════════════════════════════════════════════════════════

SEVİYE 4: KONU ETİKETİ (Topic Tag)

Which legal area?

☐ TK 21/2 (Usulsüz Tebligat)
☐ TK 35 (Yetki)
☐ Meskeniyet
☐ Haciz
☐ İhalenin Feshi
☐ İtirazın İptali
☐ İspat Yükü
☐ Sabit Olmayan Borç

════════════════════════════════════════════════════════════════

OPSİYONEL NOT (Optional Notes)

[...................]

[KAYDET / SONRAKI]

════════════════════════════════════════════════════════════════
```

**Why 4 tiers:**
- Tier 1 = Traditional quality gate
- Tier 2 = Expert opinion on strengths
- **Tier 3 = THE MOAT** (decision purpose in litigation)
- Tier 4 = Discoverability

---

## Success Metrics (Not What You'd Expect)

### What We Measure ✅

**Expert Explainability Rate (EER)**
- Goal: ≥85% of decisions have articulate Layer 3 reasoning
- Why: If experts can explain WHY a decision has a strategic role, we can learn it
- Red flag: <70% (decisions are intuitive, not learnable)

**Expert Consistency Rate (ECR)**
- Goal: ≥85% consistency on repeat reviews
- Why: Shows heuristics are reproducible, not mood-dependent
- Red flag: <70% (judgment is not stable)

**Metadata Independence (MI)**
- Goal: ≥80% same decision-making when metadata stripped
- Why: Shows judgment is substance-based, not authority-label-driven
- Red flag: <60% (could use simple heuristics, not ML)

### What We Do NOT Measure ❌

**Approval rate** (target 70%)  
→ Wrong metric (good curation has 20-40% approval)

**Review speed** (target X decisions/hour)  
→ Wrong metric (depth over speed)

**Gold DB size** (target 100 decisions)  
→ Wrong metric (quality over quantity)

---

## The Risk We're Preventing

**"Early Growth Intoxication"**

The temptation at this stage: "We have 100 decisions, let's scale to 1000 now!"

The reality: Without validated Layer 3 (Strategic Role) signals and proven EER, scaling just gives us a bigger database, not a bigger moat.

**The discipline we enforce:**
1. 10 decisions: Proof Validator works
2. 100 decisions: Proof EER is ≥85%
3. 100+ validated signals: Proof model is trainable
4. Only then: Scale to 1000

**This is the moment Filex either becomes:**
- ✅ An expertise-as-asset company (Layer 3 captured, moat real)
- ❌ A nice legal database (Layer 1-2 only, commodity)

---

## Competitive Positioning

### What Competitors Can Do

- ✅ Collect court decisions (free data, trivial)
- ✅ Build a search engine (technical, not complex)
- ✅ Hire expert curator (hires Cüneyt-like person)
- ✅ Create curated database (slower than Filex, but doable)

### What Competitors Cannot Do (The Moat)

- ❌ Systematize decision-usage strategy (Layer 3)
- ❌ Capture expert judgment at scale (requires protocol + discipline)
- ❌ Build decision-strategy model (requires 100+ Layer 3 evaluations + ML)
- ❌ Train lawyers on "how to use decisions" (requires strategy framework)

### The Investor Pitch (Revised)

**Version A (Before Phase 1):**
"We curate high-quality court decisions"  
→ Worth: $X

**Version B (After Phase 1, EER validated):**
"We've systematized how expert lawyers choose and use decisions in litigation. Our model learns decision strategy, not just decision quality. Lawyers don't search for 'good cases' — they search for 'how do I argue this?' We answer that question."  
→ Worth: $10X

---

## Architecture Decision Log (Why These Choices)

### Decision: Why SQLite Silver DB (not dump to Gold)?

**Choice:** All intake goes to Silver DB first, Cüneyt reviews before promotion to Gold

**Alternatives:** Auto-promote validated decisions to Gold  
**Rejected because:**
- Gold DB integrity must be maintained
- Validator proves schema, not quality
- Cüneyt's Layer 3 evaluation is what creates value
- Without human gate, we're just a big database

**Cost:** Slower time-to-Gold (but worth it)

### Decision: Why 4-tier UI (not just approve/reject)?

**Choice:** Tier 1-4 structure forces capture of Layer 3

**Alternatives:** Simple APPROVED/REJECTED buttons  
**Rejected because:**
- Would lose Strategic Role data
- Would miss the moat
- Cüneyt's judgment would be lost, not learned

**Cost:** Slower review time (but higher value per review)

### Decision: Why EER > ECR (explainability > consistency)?

**Choice:** Can explain inconsistency = success. Can't explain consistency = failure.

**Why:**
- Law legitimately evolves (2022 HGK ≠ 2024 İBK)
- Inconsistency is OK if articulated ("The law changed, here's why")
- Consistency that's inarticulate is noise

**Cost:** Requires cultural shift (consistency ≠ always good)

---

## Implementation Checklist (Week by Week)

### Week 1: Foundation
- [ ] Create SQLite schema (silver_decisions.db)
- [ ] Build CLI dashboard for Cüneyt review
- [ ] Run adapter on 10 test decisions
- [ ] Validate schema, zero PII
- [ ] Gate: 10/10 PASS

### Week 1-2: MVP Collection
- [ ] Expand intake to 100 decisions
- [ ] Monitor duplicates, quality
- [ ] Prepare Cüneyt review export
- [ ] Gate: 100 decisions in Silver DB

### Week 2-3: Expert Evaluation
- [ ] Cüneyt reviews 100 via 4-tier dashboard
- [ ] Captures all 4 tiers (especially Tier 3)
- [ ] Records expert notes
- [ ] Measures EER on Tier 3
- [ ] Gate: EER ≥85%

### Week 3-4: Consistency Study
- [ ] Run repeat-review test (50 decisions, day 30)
- [ ] Run metadata-strip test (20 decisions)
- [ ] Run authority-relabel test (15 decisions)
- [ ] Calculate ECR, MI, AI scores
- [ ] Gate: All tests ≥70%

### Week 4+: Automation
- [ ] Daily cron job (only after all gates pass)
- [ ] Intake: search → validate → Silver DB
- [ ] Monitor: weekly dashboard
- [ ] Logging: Slack notifications
- [ ] Gate: 7 days unattended, zero errors

---

## The Bet We're Making

We are betting that:

1. **Cüneyt's Layer 3 judgments are explainable** (EER ≥85%)
2. **His judgments are reproducible** (ECR ≥85%)
3. **His judgments are substance-based** (MI ≥80%)
4. **His judgments can be learned by a model** (after 100+ Layer 3 signals)

**If we win:** Filex is defensible, scalable, licensable  
**If we lose:** Filex is a nice curated database (not a moat)

---

## The Moment of Truth

**Phase 1 is the validation phase.**

Not the collection phase. Not the scaling phase. The validation phase.

By end of Phase 1:
- We will know if Cüneyt's judgment is learnable
- We will have 100 structured Layer 3 evaluations
- We will have an artifact (the model, the signals) worth licensing

Or:

- We will know curation at scale requires humans (Cüneyt remains bottleneck)
- We will have a nice curated database (not a moat)
- We will pivot to different strategy

**Either way, Phase 1 answers the fundamental question: Is this expertise-as-asset or data-as-asset?**

---

**Phase 1 Strategy Guide v1.0 — Locked for execution**

The path: 10 perfect → 100 measured → 1000 controlled.

Execute with discipline. The moat is Layer 3. Layer 3 is the prize.
