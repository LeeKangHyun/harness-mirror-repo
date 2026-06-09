---
name: research-orchestrator
description: "Coordinates the deep-research agent team to investigate a question from web + academic angles, cross-validate, and produce a report. Use for research requests on any topic. Follow-up: rerun, update, dig deeper, add a source, improve the report — 리서치 다시 실행/업데이트/심화/보완 요청 시에도 반드시 사용."
---

# Research Orchestrator

Coordinates the deep-research team to produce a confidence-rated report. Fan-out/fan-in pattern; agent-team mode (scouts share findings live, which redirects each other's search).

## Execution mode: Agent Team

## Team composition
| Member | Type | Model | Skill | Output |
|--------|------|-------|-------|--------|
| web-scout | general-purpose | sonnet | web-search | `02_web-scout_sources.md` |
| academic-scout | general-purpose | opus | paper-search | `02_academic-scout_sources.md` |
| synthesizer | custom | opus | cross-validate, report-write | `03_report.md` → final |

## Workflow

### Phase 0 — Context check
Check `_workspace/`: absent → initial run (Phase 1); present + "dig deeper/refine" → partial rerun (re-call only the relevant scout, pass prior outputs); present + new question → fresh run (move `_workspace/` to `_workspace_{timestamp}/`).

### Phase 1 — Prep
Analyze the question and reader's expertise; create `_workspace/`; save question/scope to `_workspace/00_input/`.

### Phase 2 — Form team
`TeamCreate(team_name:"deep-research-team", members:[web-scout, academic-scout, synthesizer])` with model per the table. `TaskCreate`: web-gather, academic-gather (parallel), then cross-validate+report (depends_on both).

### Phase 3 — Gather (scouts self-coordinate)
Scouts claim gather tasks and run in parallel, each saving its source table. They `SendMessage` findings that affect the other's search (e.g. academic-scout flags a claim as debunked → web-scout drops it). Leader monitors via `TaskGet`.

### Phase 4 — Synthesize
`synthesizer` reads both tables, cross-validates, requests sources for thin claims via `SendMessage`, writes `03_report.md`, then the final report to the user path.

### Phase 5 — Cleanup
Stop members, `TeamDelete`, keep `_workspace/`, summarize to user. Offer feedback (Phase 7 of the factory).

## Data flow
scouts → `02_*_sources.md` → synthesizer (Read) → `03_report.md` → final report.

## Error handling
| Situation | Strategy |
|-----------|----------|
| one scout fails | retry once; else note the missing angle in the report |
| sources conflict | synthesizer keeps both with attribution |
| timeout | report from sources gathered so far, mark coverage gaps |

## Test scenario
- Normal: question → 2 scouts gather in parallel → synthesizer cross-validates → confidence-rated report produced.
- Error: academic-scout stalls → leader gets idle alert → retry → on failure, report proceeds web-only with an "academic coverage missing" note.
