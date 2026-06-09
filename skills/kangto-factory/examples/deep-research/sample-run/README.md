# Sample run — measured evidence

This is a **real, executed run** of the deep-research harness (not pseudocode), kept as durable evidence. All four agents ran live with WebSearch/WebFetch on 2026-06-09.

**Question:** "Do humans really use only 10% of their brains? Is it true, and where did the myth originate?"

**Setup (with-skill vs baseline, per `references/skill-testing-guide.md`):**
- **With-skill harness** (sub-agent mode, since Agent Teams needs the experimental flag): `web-scout` + `academic-scout` ran in parallel reading their skills, then `synthesizer` read both tables + `cross-validate` + `report-write`.
- **Baseline:** one plain agent, same question, no skill.

## Files
| File | Producer |
|------|----------|
| `02_web-scout_sources.md` | web-scout (sonnet) — 13 claims, web sources |
| `02_academic-scout_sources.md` | academic-scout (opus) — 12 sources w/ strength notes |
| `03_report.md` | synthesizer (opus) — **with-skill** final report |
| `baseline_report.md` | plain agent — **baseline** report (no skill) |

## Measured outcome

| | With-skill harness | Baseline |
|--|--------------------|----------|
| Tokens | **67,778** (17.8k + 26.1k + 23.9k) | **27,158** |
| Agents | 3 | 1 |
| Result | epistemically tighter | richer & more readable |

**What the skill genuinely added** (absent in baseline): inline confidence labels per claim (Established/Likely/Single-source); the *corroboration ≠ repetition* catch (it noticed the 1936 Carnegie foreword and 1929 Almanac both trace to one Wikipedia citation and refused to upgrade them); an explicit conflict/under-determination section; source-strength caveats; and exclusion transparency (the Jaina-epistemology paper was reviewed and excluded).

**What the baseline did better:** it was richer and more readable, and surfaced insights the fan-out pipeline *lost* — notably glial cells (~90% of brain cells, a real frontier often confused with the myth) and a "why the myth persists" section with neuromyth-prevalence data.

## Honest verdict
The harness is **not theater** — the skills produced specific, real epistemic discipline a strong baseline did not. But it is **not free or strictly better** — it cost ~2.5× the tokens and the fan-out structure traded breadth for structure. Whether to use it is a **measured trade-off**, not a belief: worth it when calibration/auditability matters, overkill for a general write-up (exactly the "when NOT to forge a harness" guidance, now confirmed with data).
