# Expert Consistency Study — The Moat Validation Protocol

## The Critical Question

**Important caveat:** In law, inconsistency is not failure. It's natural.

Example: Same expert's views change legitimately:
- 2022: HGK establishes position A
- 2024: İBK contradicts with position B
- 2026: New chamber approach emerges (position C)

**This is not noise. This is how law evolves.**

---

**Real hypothesis:** Cüneyt Bey's decisions are **explainable and structured**, even when they evolve.

**Null hypothesis:** His decisions are intuitive ("it felt right"), post-hoc rationalized, and irreproducible.

**Why this matters:**

If signals are **explainable** → We can learn heuristics (even evolving ones) → Moat is real  
If signals are **inarticulate** ("my gut says so") → We have noise → Moat is fiction

---

## The Risk

We could collect 1000 expert signals and discover they're:
- Context-dependent (metadata determines outcome)
- Authority-biased (HGK label drives decision)
- Time-variable (same karar, different decision after 3 months)
- Rationalizations (post-hoc explanations, not actual logic)

**This would make Expert Signals worthless.**

---

## The Three Validation Tests

### Test 1: Consistency Over Time

**Protocol:**
1. Cüneyt reviews decision D1 on Day 0
   - Result: GOLD_APPROVED
   - Reason: "Clear precedent on TK 21/2"

2. On Day 30, show **exact same decision** (same text, same metadata, hidden as "new")
   - Ask: Would you approve this?

3. Compare results: D0 vs D30

**Success criteria:**
- ≥90% same outcome (GOLD→GOLD, REJECT→REJECT, etc)
- ≥85% reason consistency (similar justification, different words OK)

**Failure mode:**
- <70% consistency = decisions are not reproducible
- Indicates: Mood, context, fatigue matters more than logic

**Sample size:** First 50 decisions (repeat all 50 at day 30)

---

### Test 2: Metadata Sensitivity

**Protocol:**
1. Cüneyt reviews decision D2:
   ```
   Mahkeme: Yargıtay 12. Hukuk Dairesi
   Esas: 2024/351
   Karar: 2024/999
   Karar Tarihi: 15.05.2024
   [Full decision text]
   ```
   - Result: GOLD_APPROVED

2. Week later, show **same decision but with metadata stripped:**
   ```
   Mahkeme: [REDACTED]
   Esas: [REDACTED]
   Karar: [REDACTED]
   Karar Tarihi: [REDACTED]
   [Same decision text]
   ```
   - Ask: Would you approve this?

3. Compare: Full metadata vs stripped metadata results

**Success criteria:**
- ≥85% same outcome
- Indicates: Decision is based on legal substance, not authority label

**Failure mode:**
- <70% consistency = authority/court name is the decision driver
- Indicates: Heuristic is "if Yargıtay, approve" not "if legal principle..."

**Implication:** If metadata-dependent, we can automate with simple rules (not ML)

**Sample size:** 20 decisions (strip metadata, compare)

---

### Test 3: Authority Bias

**Protocol:**
1. Cüneyt reviews decision D3:
   ```
   Yargıtay Hukuk Genel Kurulu
   [Decision text about TK article interpretation]
   ```
   - Result: GOLD_APPROVED
   - Reason: "HGK precedent on statutory interpretation"

2. Week later, show **same decision with authority label changed:**
   ```
   Istanbul 3. Asliye Hukuk Mahkemesi
   [Identical decision text]
   ```
   - Ask: Would you approve this?

3. Compare: HGK vs İlk Derece results

**Success criteria:**
- Authority affects decision, but not deterministically
- Example: HGK → GOLD (90%), İlk Derece → KEEP_IN_SILVER (70%)
- Indicates: Authority is *one factor*, not *the factor*

**Failure mode:**
- HGK → always GOLD
- İlk Derece → always REJECT
- Indicates: Simple authority filter, not expert judgment

**Implication:** If purely authority-driven, we don't need ML — a lookup table suffices

**Sample size:** 15 decisions (relabel authority, compare)

---

## The Real KPI (Revised)

**Not measured:**
- ❌ Number of Gold decisions
- ❌ Number of Silver decisions
- ❌ Speed of review

**Measured:**
- ✅ Expert Explainability Rate (EER) ← PRIMARY
- ✅ Expert Consistency Rate (ECR) ← SECONDARY
- ✅ Metadata Independence (MI)
- ✅ Authority Independence (AI)

### Expert Explainability Rate (EER)

```
EER = (Articulate reasons / Total reviews) × 100

What counts as "articulate":
  ✅ "HGK desteği var, yerleşik uygulama, dilekçede kullanılabilir"
  ✅ "TK 21/2'nin son İBK değişikliği önemli"
  ❌ "Çok iyi karar"
  ❌ "İçime sindi"
  ❌ "Olması gereken"

Example:
- 50 decisions reviewed
- 48 had articulate, structured reasons
- 2 had vague reasons
- EER = 48/50 = 96%
```

**Target EER:** ≥90% (decisions are explainable)  
**Red flag EER:** <70% (decisions are intuitive, not learnable)

---

### Expert Consistency Rate (ECR)

```
ECR = (Agreements / Total Comparisons) × 100

Example:
- 50 decisions reviewed Day 0
- 50 same decisions shown Day 30
- 46 matched (same outcome + similar reason)
- ECR = 46/50 = 92%
```

**Target ECR:** ≥85% (indicates reproducible judgment)  
**Red flag ECR:** <70% (indicates unreliable heuristics)

### Metadata Independence (MI)

```
MI = (Metadata-stripped agreement rate) × 100

Example:
- 20 decisions reviewed with full metadata
- 20 same decisions shown stripped
- 17 had same outcome
- MI = 17/20 = 85%
```

**Target MI:** ≥80% (judgment is substance-based)  
**Red flag MI:** <60% (judgment is authority-based)

### Authority Independence (AI)

```
AI = (Authority-relabeled agreement rate) × 100

Example:
- HGK decisions: 100% approval rate with HGK label
- Same decisions: 70% approval with İlk Derece label
- Difference = 30% (shows authority matters, but not deterministically)
```

**Target AI:** 40-60% variance (authority matters but isn't deterministic)  
**Red flag AI:** 0% variance (pure authority filter) OR >80% variance (irrelevant)

---

## The Investment Thesis Shift

### Before Study (Hypothesis)

"We collect expert signals about court decisions."

**Investor problem:** So does everyone else.

### After Study (Proven)

"We've measured Cüneyt Bey's decision-making consistency at 92% over time, independent of metadata labeling."

**Investor reaction:** This is a reproducible heuristic. You can automate it. You can license it. You can train others.

---

## Timeline

### Phase 1a (Week 1-2): Baseline High-Quality Evals
- Collect 50 decisions
- Review via checkbox UI (not free text)
- Measure: EER (explainability), not just outcome
- **Gate:** EER ≥85%? (decisions are articulate)

### Phase 1b (Week 2-3): Consistency Test
- Show same 50 decisions at day 30
- Metadata visible, authority visible
- Compare outcomes: ECR = ?
- **Gate decision:** If ECR <70%, halt. Check if inconsistency is legitimate (law evolved) or expert was unclear.

### Phase 1c (Week 3-4): Metadata & Authority Tests
- 20 decisions: strip metadata, compare (MI = ?)
- 15 decisions: relabel authority, compare (AI = ?)
- **Decision:** Continue to 100 evals (if all tests pass) or redesign

### Phase 2: Expand to 100 High-Quality Evals
- Same three tests on new 50 decisions
- Validate EER holds at scale
- Gate: EER ≥85% on full 100

### Phase 3: Analysis & Modeling
- Cluster high-EER signals
- Identify decision patterns (checkboxes, not prose)
- Build decision tree / rule-based model
- Test model on holdout 20 decisions

---

## What Success Looks Like

**Test Results:**
```
Expert Consistency Rate:    92%  ✅
Metadata Independence:      84%  ✅
Authority Independence:     48%  ✅
(authority matters but not deterministic)
```

**Interpretation:**
- Cüneyt's judgment is **reproducible** (92% same result, same input)
- His judgment is **substance-based** (84% independent of metadata)
- His judgment is **nuanced** (authority matters, but context-dependent)

**Business impact:**
- We can build predictive models
- We can train new reviewers using his heuristics
- We can automate triage (high-confidence cases)
- We can license the model

---

## What Failure Looks Like

### Scenario A: Low ECR (<70%)

```
Expert Consistency Rate: 62%
```

**Meaning:** Same decision, same metadata, same day → different outcome ~40% of the time

**Implication:** Judgment is mood/context-dependent, not heuristic-based

**Action:** Halt expert signal collection. Redesign as "capture raw expert preference" (not learned model).

### Scenario B: Low MI (<60%)

```
Metadata Independence: 55%
```

**Meaning:** Removing mahkeme/esas/karar labels → decision changes ~45% of the time

**Implication:** Judgment is authority-label-driven, not substance-driven

**Action:** Don't build complex models. Use simple lookup table (if Yargıtay → higher approval rate).

### Scenario C: High AI Variance (>80%)

```
Authority Independence: 88%
(HGK decision → 100% approval; İlk Derece → 12% approval)
```

**Meaning:** Authority is nearly deterministic

**Implication:** We're capturing "authority rules," not "expert heuristics"

**Action:** This is fine for triage, but not for licensing/scaling expertise.

---

## The Moat Test

**If all three tests pass (ECR >85%, MI >75%, AI 30-70%):**

"Filex has scientifically validated that expert legal judgment is reproducible, learnable, and scalable."

This is a **defensible moat**.

**If any test fails:**

"Filex has expert signals about decisions, but they're not consistent enough to automate or license."

This is **just data**, not moat.

---

## For the Investor Pitch

**Version A (If tests pass):**

"We've measured expert legal judgment (92% consistency, 84% substance-based, 48% authority-weighted). This is the first time legal expertise has been quantified and validated as reproducible. We can now:
1. Automate triage (with human override)
2. Train new experts (using heuristic model)
3. License the model (to other platforms)
4. Build SaaS on top"

**Version B (If tests fail):**

"We have a comprehensive database of curated court decisions, selected by expert legal judgment."

(Version A is worth 10x more than Version B.)

---

## The Question We're Actually Testing

**Not:** "Do we have expert signals?"  
**Yes:** "Are expert signals learnable from expert behavior?"

This determines whether Filex is a **data company** or an **AI company**.

---

## The MVP Dashboard Design

**Critical insight:** Don't ask for free-text explanations.

**Why:** Long-form text degrades to:
- "güzel karar"
- "iyi karar"
- "kullanılır"

**Result:** Unusable data.

---

**Better approach:** Checkbox model + optional notes

```
════════════════════════════════════════════════════════════════

KARAR REVIEW

════════════════════════════════════════════════════════════════

[Decision summary excerpt]

════════════════════════════════════════════════════════════════

SONUÇ

( ) GOLD_APPROVED
( ) KEEP_IN_SILVER
( ) NEEDS_METADATA_FIX
( ) DUPLICATE
( ) REJECT

════════════════════════════════════════════════════════════════

NEDEN?

☐ Güçlü içtihat
☐ Yerleşik uygulama
☐ Dilekçede kullanılabilir
☐ Güncel yaklaşım
☐ HGK desteği
☐ Çelişkili karar
☐ Tekil olay

════════════════════════════════════════════════════════════════

ÖLÇÜLER

Authority Weight:      [██████░░░░] 7/10
Draft Utility:         [████████░░] 8/10
Precedent Strength:    [strong / moderate / weak]
Topic Coverage:        [gap-filling / routine / novel]

════════════════════════════════════════════════════════════════

OPSİYONEL NOT

[...................]

[KAYDET]

════════════════════════════════════════════════════════════════
```

**Benefits:**
- ✅ Structured data (each checkbox = one signal)
- ✅ Consistent capture (no vague prose)
- ✅ Quick (expert spends 2 min, not 10)
- ✅ Learnable (ML can train on checkbox patterns)
- ✅ Audit trail (exactly what expert selected)

---

## Implementation

Add to silver_decisions schema:

```sql
-- For consistency tests
consistency_test_id TEXT,  -- Links repeated decision reviews
consistency_test_days INT, -- Days between reviews
consistency_test_result BOOLEAN, -- Did outcome match?

-- For metadata sensitivity
metadata_visibility TEXT, -- "full" / "stripped"
metadata_sensitivity_test_id TEXT,

-- For authority sensitivity
authority_label TEXT, -- Original authority displayed
authority_sensitivity_test_id TEXT,

-- Results
consistency_score REAL, -- Per-decision consistency (0.0-1.0)
metadata_independence REAL, -- 0.0-1.0
authority_independence REAL -- 0.0-1.0
```

---

## The Real MVP Goal (Revised)

**NOT:** "Collect 100 decisions"  
**NOT:** "Collect 100 signals"  

**YES:** "Capture 100 high-quality, structured expert evaluations"

High-quality = Expert Explainability Rate ≥85%  
Structured = Checkbox model (not free text)  

After 100 such evaluations:
- You have learnable heuristics
- You can build predictive models
- You have licensable assets
- You have an AI company, not a data company

---

## The Bet

We are betting that Cüneyt Bey's expert judgment is:
1. **Explainable** (not just intuitive)
2. **Structured** (reproducible in format, even if opinion evolves)
3. **Learnable** from articulate signals

**If we win this bet: Filex is defensible, licensable, and valuable.**

**If we lose: Filex is a nice curated database, not a moat.**

---

*Expert Consistency Study v1.1 (Revised)  
The Moat Validation Protocol*

Primary gate: Measure EER (explainability) on first 50 decisions  
Secondary gate: Validate consistency (ECR) on repeat reviews  
This is the most important experiment Filex will run in Phase 1.*
