---
name: web-search
description: "Search the open web for current sources and capture them as structured findings. Use when gathering news/blog/official sources for a research question, or when asked to find/collect/look up web sources on a topic. 웹 자료 수집/검색 시 사용."
---

# web-search — structured open-web gathering

How `web-scout` turns a question into sources without losing provenance.

## Procedure
1. Decompose the question into 3–5 sub-claims; write one targeted query per sub-claim.
2. For each result worth keeping, record: `claim | source title | url | date | confidence(high/med/low)`.
3. Mark a sub-claim "single-source" if only one source supports it — single sourcing is a confidence signal, not a failure.
4. Save the table to `_workspace/02_web-scout_sources.md`.

## Principles
- Provenance over volume: ten well-attributed claims beat fifty bare links.
- Record conflicts; never silently drop a source that disagrees with a teammate.
- Paywalled/uncertain → keep the reference, mark the summary "unverified".

## Output shape
A markdown table with the columns above, one row per claim.
