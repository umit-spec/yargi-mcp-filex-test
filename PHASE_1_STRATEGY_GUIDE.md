# Phase 1 Strategy Guide — Testable Hypotheses (Not Locked)

**🔴 CRITICAL CAVEAT**

This document proposes Layer 3 (Strategic Role) as a **leading moat candidate**.

We have **zero empirical data** to confirm this.

Phase 1's job is to **test whether Layer 3 is actually valuable or just plausible**.

If Phase 1 data shows Strategic Role consistency is low (SRCR <60%), we pivot.

---

## The Hypothesis (Not Proven)

**Layer 3 (Strategic Role) may be the moat IF:**
1. Cüneyt can articulate it (EER ≥85%)
2. He's consistent about it (SRCR ≥80%)
3. Consistency holds across time/metadata/authority
4. Model can learn the patterns

**If any of these fail, Layer 3 collapses and we need different strategy.**

---

## The 4-Tier Model (Proposed)

```
LAYER 1: COURT DECISIONS (Commodity)
         "Here is a court decision"
         → Anyone can find this

LAYER 2: EXPERT EVALUATION (Rare)
         "Cüneyt Bey says this is good"
         → Better, but copyable

LAYER 3: STRATEGIC ROLE (?)
         "This decision is used as [primary arg | counter | burden shift | ...]"
         → Could be moat IF consistent + learnable
         → Currently unproven

LAYER 4: TOPIC CONTEXT (Support)
         "This is about TK 21/2"
         → Enables discovery
```

---

## Strategic Role (The Bet)

**Hypothesis:** Lawyers don't search "find decisions" — they search "how do I argue X?"

**If Layer 3 data shows:**
- High EER (85%+ articulate)
- High SRCR (80%+ consistent choice of role)
- Low authority-bias (decisions role-classified by substance, not label)

**Then:** Model learns decision-strategy, becomes moat

**If data shows:**
- Low EER (<60% vague explanations)
- Low SRCR (<60% same decision, different role each time)
- High authority-bias (role driven by "is it Yargıtay?")

**Then:** Layer 3 is not learnable, pivot to Layer 2

---

## Five Strategic Documents (Temporary)

These five are **working hypotheses**, not final architecture:

1. **CUENEY_REVIEW_MATRIX.md** — Product manifesto (assuming Layer 3 is valuable)
2. **SILVER_DB_ARCHITECTURE.md** — Schema (includes strategic_role field)
3. **EXPERT_SIGNAL_MODEL.md** — Learning model (assumes Layer 3 is learnable)
4. **EXPERT_CONSISTENCY_STUDY.md** — Validation (tests the hypothesis)
5. **MASTER_PROMPT_SILVER_DB_PHASE_1.md** — Implementation roadmap

**Status:** All draft until Phase 1 data validates Layer 3

---

## New KPI: SRCR (Strategic Role Classification Rate)

**What it measures:** Does Cüneyt choose the same strategic role for the same decision?

**Test protocol:**

1. Cüneyt reviews decision D on June 20 → marks "Ana daynak"
2. Same decision shown again on July 20 (without memory)
3. Does he choose "Ana daynak" again?

**Scoring:**
```
SRCR = (Consistent role assignments / Total repeat reviews) × 100

Example:
- 50 decisions, each reviewed twice (day 0 and day 30)
- 42 chose same strategic role both times
- 8 changed strategic role between reviews
- SRCR = 42/50 = 84%
```

**Success threshold:** SRCR ≥80%  
**Red flag:** SRCR <60% (Layer 3 not stable)

---

## Phase 1 Timeline (Hypothesis Testing)

### Week 1: Proof of Concept
- Create SQLite schema (with strategic_role field)
- Build minimal review UI (10 decisions)
- Cüneyt reviews 10 decisions via 4-tier form
- **Test goal:** Can UI capture all 4 tiers without friction?
- **Artifact:** 10 reviews with Layer 3 filled in
- **Gate:** UI is usable (yes/no)

### Week 2: MVP Collection + First Consistency Check
- Expand to 100 decisions (Usulsüz Tebligat + Meskeniyet + İhalenin Feshi)
- Cüneyt does first pass (records Layer 3 for all 100)
- Select 50 of those 100 for day-30 repeat review
- **Test goal:** Measure SRCR on strategic role choices
- **Artifact:** 100 initial reviews + 50 repeat reviews
- **Gate:** SRCR ≥60% (minimal consistency to continue)

### Week 3: Consistency Study Full Validation
- Show 50 decisions again (day 30, masked)
- Calculate SRCR (same role choices?)
- Run metadata-strip test (does removing mahkeme/esas/tarih change role choice?)
- Run authority-relabel test (does changing "Yargıtay" to "İlk Derece" change role?)
- **Test goal:** Is Layer 3 substance-based or label-based?
- **Artifact:** SRCR, MI (metadata independence for Layer 3), AI (authority independence)
- **Gate:** SRCR ≥80% (Layer 3 is stable enough to continue)

### Week 4+: Scaling (Only if Gates Pass)

If SRCR ≥80%:
- Daily cron intake
- Ongoing Layer 3 evaluation
- Monitor consistency over time
- Begin training decision-strategy model

If SRCR <60%:
- Halt intake
- Investigate: Why inconsistent?
- Options:
  - Cüneyt needs training on Layer 3 definitions
  - Layer 3 is inherently unstable (abandon as moat)
  - Need different categorization (pivot)

---

## The Real Test (UI > Docs)

**This week's docs are smart thinking.**

**Next week's UI is the reality check.**

When Cüneyt sits down and reviews 10 actual decisions:

- Does he naturally use Layer 3 categories?
- Or does he force-fit decisions into boxes?
- Does "Ana daynak" feel right, or does it feel arbitrary?
- Can he explain WHY a decision is "Ana daynak" vs "Destekleyici"?

**That UX reality will be worth more than all of tonight's strategy documents.**

---

## Possible Outcomes of Phase 1

### Outcome A (Best Case)
```
EER ≥85%: Experts articulate Layer 3 clearly
SRCR ≥80%: Same role for same decision (consistent)
MI ≥80%: Role choice based on substance, not label
AI: Authority matters but not deterministic

→ Layer 3 is learnable, moat is real
→ Proceed to Phase 2 with confidence
→ Investor pitch: "We learned decision strategy"
```

### Outcome B (Promising)
```
EER ≥85%: Clear articulation
SRCR 60-79%: Somewhat consistent
MI 60-75%: Somewhat substance-based

→ Layer 3 has promise but needs refinement
→ Redesign Layer 3 categories? More training?
→ Continue but with skepticism
```

### Outcome C (Concerning)
```
EER <70%: Vague explanations
SRCR <60%: Same decision, wildly different roles
MI <60%: Role driven by "is it Yargıtay?"

→ Layer 3 is not stable enough to learn
→ Halt Layer 3 as moat strategy
→ Pivot to Layer 2 (curation) or different approach
→ Possibly add more structured Layer 3 definitions
```

### Outcome D (Worst Case)
```
EER <50%: "İyi karar, kötü karar" only
SRCR <40%: No pattern
Cüneyt can't explain reasoning

→ Expert judgment is intuitive, not systematizable
→ Filex is a curated database (nice, but not moat)
→ Licensing/scaling becomes hard
→ Rethink entire strategy
```

---

## What Phase 1 Actually Proves

**NOT:** Layer 3 is the moat (too early)

**YES:** Whether Layer 3 can be systematically captured

If SRCR ≥80%: Yes, we can systematically capture it → potential moat

If SRCR <60%: No, it's unstable → need different approach

---

## The UI That Matters

**Don't build for 100 decisions yet.**

Build for **10 decisions with review history:**

```
┌─────────────────────────────────────────┐
│ Silver DB Review UI (MVP)                │
├─────────────────────────────────────────┤
│                                          │
│ [DECISION 1 of 10]                      │
│                                          │
│ Mahkeme: Ankara BAM, 4. Hukuk            │
│ Esas: 2024/512                          │
│ Tarih: 15.03.2024                       │
│ [Summary...]                            │
│                                          │
│ ───────────────────────────────────────│
│                                          │
│ TIER 1: OUTCOME                         │
│ ( ) GOLD_APPROVED                       │
│ ( ) KEEP_IN_SILVER                      │
│ ( ) REJECT                              │
│                                          │
│ TIER 2: QUALITY SIGNALS                 │
│ ☐ Güçlü içtihat                        │
│ ☐ Yerleşik uygulama                    │
│                                          │
│ TIER 3: STRATEGIC ROLE                  │
│ ☐ Ana daynak                            │
│ ☐ Destekleyici                          │
│ ☐ Karşı görüşü çürütür                │
│ ☐ İspat yükü                            │
│ ☐ Usul                                  │
│ ☐ Esas                                  │
│                                          │
│ TIER 4: TOPIC                           │
│ ☐ TK 21/2                               │
│ ☐ Meskeniyet                            │
│                                          │
│ ───────────────────────────────────────│
│                                          │
│ [SAVE] [NEXT] [HISTORY]                │
│                                          │
└─────────────────────────────────────────┘
```

With **[HISTORY]** button showing:
- When reviewed
- What was selected (all 4 tiers)
- What changed

This is the **real experiment**.

---

## What Gets Built This Week

**Stop writing docs. Start building UI.**

1. **SilverReviewPage** (React/Python CLI)
   - Display 1 decision
   - 4-tier checkbox form
   - Save button
   
2. **Database tables:**
   - review_result (outcome)
   - expert_signals (tier 2 + 3 + 4 as JSON)
   - strategic_role (explicit: ana_daynak | destekleyici | etc)
   - review_timestamp

3. **Review history view**
   - Show all reviews of same decision
   - Compare: what changed between reviews?

4. **Gold promotion button**
   - Move GOLD_APPROVED to Gold DB
   - Audit trail

**That's it. 4 things. Week 1 = done.**

---

## The Honest Assessment

**Strategic docs say:** Layer 3 is the moat!

**Reality check says:** We don't know yet. We're guessing.

**Phase 1 is the bet that our guess is right.**

**If Phase 1 data proves SRCR ≥80%, we win.**

**If SRCR <60%, we need a different bet.**

Either way, **Phase 1 gives us data instead of theories.**

---

## Next Conversation

When you reconvene:

❌ Don't update these docs more  
✅ Build SilverReviewPage  
✅ Run adapter on 10 decisions  
✅ Cüneyt reviews 10 via UI  
✅ Measure: Is UI usable? Does Layer 3 feel natural?

That feedback is worth 1000x the docs.

---

*Phase 1 Strategy Guide v1.1 (Revised)*

*This is a testable hypothesis, not a locked strategy.*

*Phase 1 exists to prove or disprove it.*
