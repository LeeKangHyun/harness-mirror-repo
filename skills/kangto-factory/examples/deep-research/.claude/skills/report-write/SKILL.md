---
name: report-write
description: "Write a research report from a confidence-rated claim set, surfacing uncertainty and attribution. Use when producing the final research deliverable, writing up findings, or summarizing validated research. 리서치 보고서 작성 시 사용."
---

# report-write — honest research report

How `synthesizer` writes up validated findings without overclaiming.

## Structure
1. **Question & scope** — what was asked, what was excluded.
2. **Key findings** — grouped by theme; each statement carries its confidence inline (established / likely / contested / single-source).
3. **Open questions / conflicts** — contested claims with both sides and sources.
4. **Sources** — full list, grouped web vs academic.

## Principles
- Confidence travels with the claim, not in a footnote the reader skips.
- Lead with what is established; do not bury a contested claim as if settled.
- Write for the reader's expertise level (calibrated by the orchestrator).

## Output
Final report at the user-specified path; draft at `_workspace/03_report.md`.
