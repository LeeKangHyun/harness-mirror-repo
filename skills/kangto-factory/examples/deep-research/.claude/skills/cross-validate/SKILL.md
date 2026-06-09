---
name: cross-validate
description: "Cross-validate findings from multiple sources, assign confidence, and resolve conflicts by source strength. Use when merging research findings, deciding what is established vs uncertain, or reconciling conflicting sources. 교차검증/근거 통합 시 사용."
---

# cross-validate — turn raw findings into a confidence-rated claim set

How `synthesizer` decides what the research actually supports.

## Procedure
1. Merge all scout tables into one claim set, keyed by claim.
2. For each claim, count corroborating sources and note their strength.
3. Assign confidence:
   - **Established** — 2+ independent sources, at least one strong.
   - **Likely** — multiple weak, or one strong, no contradiction.
   - **Contested** — sources conflict → keep all sides with attribution.
   - **Single-source** — one source only → flag explicitly.
4. Produce a confidence-rated claim set for `report-write`.

## Principles
- Corroboration ≠ repetition: three outlets citing one study is still one source.
- A conflict is a finding. Present both sides with citations; never pick silently.
- Do not upgrade a single weak source to a confident claim.

## Output shape
`claim | confidence | supporting sources | conflicts (if any)`.
