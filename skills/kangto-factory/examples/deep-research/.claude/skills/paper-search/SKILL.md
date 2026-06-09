---
name: paper-search
description: "Find peer-reviewed papers/studies and assess their strength. Use when gathering academic/empirical sources for a research question, or when asked whether a claim is supported by research. 학술/논문 근거 수집·평가 시 사용."
---

# paper-search — academic gathering with strength assessment

How `academic-scout` finds authoritative backing and judges it.

## Procedure
1. Identify which claims need empirical backing (not every claim does).
2. For each, find papers/studies; record: `claim | citation | year | venue | strength | finding`.
3. Assess strength: sample size, methodology, replication, peer-reviewed vs preprint.
4. Save to `_workspace/02_academic-scout_sources.md`.

## Principles
- A preprint or opinion piece is not a peer-reviewed finding — label the distinction.
- A single study is "suggestive", not "established"; reserve "established" for replicated/meta-analytic support.
- Conflicting studies are recorded with both strengths, not averaged away.

## Output shape
A markdown table with the columns above, plus a one-line strength note per row.
