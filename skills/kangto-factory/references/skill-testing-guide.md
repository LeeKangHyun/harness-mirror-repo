# Skill Testing & Iteration Guide

Methodology for verifying and iteratively improving a generated skill. Supplements Phase 6. Load when you want rigorous, measured skill evaluation (beyond the quick checks in `skill-authoring.md`).

## Contents
1. Framework
2. Writing test prompts
3. With-skill vs baseline
4. Assertion-based grading
5. Specialist eval agents
6. Iteration loop
7. Trigger validation
8. Workspace layout

---

## 1. Framework
Skill quality = qualitative + quantitative.

| Type | Method | Fits |
|------|--------|------|
| Qualitative | user reviews the output | tone, design, creative work |
| Quantitative | assertion-based auto-grading | file creation, extraction, code gen |

Core loop: **write → run → evaluate → improve → re-run.**

---

## 2. Writing test prompts
Prompts must read like something a **real user would type** — concrete and natural. Abstract prompts have little test value.

- Bad: `"process the PDF"`, `"extract the data"`.
- Good: `"In 'Q4_revenue_final_v2.xlsx' in Downloads, add a margin(%) column from column C (revenue) and D (cost), then sort descending by margin."`

Mix tones (formal/casual), intent (explicit format vs inferred from context), and complexity. Include some abbreviations/typos. Start with 2–3 prompts covering: 1 core case + 1 edge case + (optional) 1 composite.

---

## 3. With-skill vs baseline
For each prompt, spawn two sub-agents **simultaneously** on the same input:
- **With-skill** → reads the skill → `_workspace/iteration-N/eval-{id}/with_skill/outputs/`
- **Baseline** → no skill → `.../without_skill/outputs/`

Baseline choice: new skill → run with no skill; improving a skill → the pre-edit version (keep a snapshot).

**Capture timing immediately.** `total_tokens` and `duration_ms` are available only in the completion notification and cannot be recovered later — save them at once.
```json
{ "total_tokens": 84852, "duration_ms": 23332 }
```

---

## 4. Assertion-based grading
When output is objectively checkable, define assertions for auto-grading.

- **Good assertion:** objectively true/false; descriptively named; verifies the skill's core value.
- **Bad assertion:** always passes regardless of the skill ("output exists"); or needs subjective judgment ("well written").
- **Prefer scripts:** if an assertion is code-checkable, script it — faster, more reliable, reusable across iterations.
- **Watch non-discriminating assertions:** anything passing in BOTH configs measures nothing — remove or replace with a harder one.

Grading result schema:
```json
{
  "expectations": [
    { "text": "margin column added", "passed": true, "evidence": "col E 'profit_margin_pct'" },
    { "text": "sorted desc by margin", "passed": false, "evidence": "original order kept" }
  ],
  "summary": { "passed": 1, "failed": 1, "total": 2, "pass_rate": 0.5 }
}
```

---

## 5. Specialist eval agents
Optional roles that raise evaluation quality:
- **Grader** — judges each assertion pass/fail with evidence; extracts factual claims from the output and cross-checks; flags weak/ambiguous assertions.
- **Comparator** — blind A/B: anonymize the two outputs and judge quality without knowing which used the skill. Use when you need a rigorous "is the new version really better?"; skip for routine iteration.
- **Analyzer** — finds statistical patterns across the benchmark: non-discriminating assertions, high-variance evals (unstable run-to-run), time/token trade-offs (skill raises quality but also cost).

---

## 6. Iteration loop
1. **Collect feedback** — show output to the user; empty feedback = "fine."
2. **Improve by principle:**
   - **Generalize** the fix — a patch that only fits the test example is overfitting.
   - **Cut dead weight** — read the transcript; if the skill makes the agent do unproductive work, delete that part.
   - **Explain why** — even from terse feedback, understand why it matters and encode that.
   - **Bundle** repeated helper code into `scripts/`.
3. **Re-run** all cases into a fresh `iteration-N+1/`, present vs the prior iteration, collect feedback, repeat.

Stop when: the user is satisfied, all feedback is empty, or gains have plateaued.

**Draft → re-read pattern:** don't try to write the skill perfectly in one pass — draft, then re-read with fresh eyes and refine.

---

## 7. Trigger validation
Write 20 eval queries: 10 should-trigger + 10 should-NOT-trigger (EN + KO for a bilingual skill).

Query quality: concrete and natural (file paths, column names, company names); varied length/tone; focus on **edge cases**, not obvious ones.
- **Should-trigger:** same intent in varied phrasing (formal/casual); cases that clearly need the skill without naming it; niche uses; cases that compete with another skill but this one should win.
- **Should-NOT-trigger:** **near-misses are the point** — similar keywords but a different tool fits. Obviously unrelated queries ("write a Fibonacci function") have no test value.

**Collision check:** confirm the new description doesn't wrongly trigger on existing skills' territory; if it does, sharpen the boundary conditions in the description.

**Auto-optimization (advanced, optional):** split 20 queries Train(60%)/Test(40%); measure trigger accuracy; analyze failures → revise description; select the best on the **Test** set (not Train — avoids overfitting); ≤5 rounds. Run via a `claude -p` script; token-costly, so do it only as a final step once the skill is stable.

---

## 8. Workspace layout
```
{skill-name}-workspace/
├── iteration-1/
│   ├── eval-{descriptive-name}/
│   │   ├── eval_metadata.json
│   │   ├── with_skill/    { outputs/, timing.json, grading.json }
│   │   └── without_skill/ { outputs/, timing.json, grading.json }
│   └── benchmark.json
├── iteration-2/ ...
└── evals/evals.json
```
Rules: name eval dirs descriptively (`eval-multi-page-table-extraction`), not by number; keep each iteration in its own dir (never overwrite); never delete `_workspace/` — it's the audit trail.
