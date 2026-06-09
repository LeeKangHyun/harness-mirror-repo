# Orchestrator Templates

The orchestrator is the top-level skill that coordinates the whole team. Three templates by execution mode.

---

## Template A — Agent Team (default)

```markdown
---
name: {domain}-orchestrator
description: "Coordinates the {domain} agent team. {initial trigger keywords}. Follow-up: rerun / update / fix / improve / partial rerun of {domain} — {도메인} 다시 실행/업데이트/수정/보완. Always use this skill for those."
---

# {Domain} Orchestrator
## Execution mode: Agent Team

## Team composition
| Member | Agent type | Role | Skill | Output |
|--------|-----------|------|-------|--------|
| {m1} | {custom/built-in} | ... | ... | ... |

## Workflow

### Phase 0 — Context check (follow-up support)
1. Check whether `_workspace/` exists.
2. Decide: none → initial run (→ Phase 1); exists + partial-edit request → partial rerun (re-call only the affected agent, overwrite only its output); exists + new input → fresh run (move `_workspace/` to `_workspace_{YYYYMMDD_HHMMSS}/`, then Phase 1).
3. On partial rerun, pass prior output paths into the agent prompt so it reads and improves on them.

### Phase 1 — Prep
1. Analyze input. 2. Create `_workspace/`. 3. Save input to `_workspace/00_input/`.

### Phase 2 — Form team
TeamCreate(team_name:"{domain}-team", members:[
  { name:"{m1}", agent_type:"{type}", model:"opus", prompt:"{role + instructions}" }, ... ])
TaskCreate(tasks:[ { title, description, assignee }, { title, depends_on:["..."] } ])  # ~5-6 tasks/member

### Phase 3 — Main work (members self-coordinate)
Members claim tasks from the shared list and run independently. Communication rules:
- {m1} sends {what} to {m2} via SendMessage; each saves output to `_workspace/{phase}_{member}_{artifact}.md` and notifies the leader.
Leader monitors via TaskGet, intervenes/reassigns when a member stalls.

### Phase 4 — Integrate
Wait for all tasks done (TaskGet) → Read each output → integrate/verify → write final to `{output-path}/{file}`.

### Phase 5 — Cleanup
SendMessage members to stop → TeamDelete → keep `_workspace/` (audit trail) → summarize to user.

## Error handling
| Situation | Strategy |
|-----------|----------|
| one member fails | leader detects → SendMessage status → restart or spawn replacement |
| majority fail | notify user, ask whether to continue |
| timeout | use partial results, stop unfinished members |
| data conflict between members | keep both, annotate source, never delete |

## Test scenario
- Normal: input → analysis → team of N + M tasks → self-coordinated work → integrate → `{output}` produced.
- Error: {m2} stops → leader gets idle alert → SendMessage/restart → reassign to {m1} → finish → report notes "{m2} area partially missing".
```

---

## Template B — Sub-agent

```markdown
---
name: {domain}-orchestrator
description: "Coordinates {domain} agents. {keywords} + follow-up keywords."
---
## Execution mode: Sub-agent

## Phase 0 — Context check  (same `_workspace/` branching as Template A)
## Phase 1 — Prep: analyze input; create `_workspace/`.
## Phase 2 — Parallel run: in ONE message, call N Agent tools with run_in_background:true, model set per agent; each writes `_workspace/{phase}_{agent}_{artifact}.md`.
## Phase 3 — Integrate: collect return values + Read file outputs → integrate → final output.
## Phase 4 — Cleanup: keep `_workspace/`; summarize.

## Error handling: one fail → 1 retry, then note missing & continue; majority fail → ask user; timeout → use partial.
```

---

## Template C — Hybrid

State `**Mode:** {team|sub}` at the top of each phase.

| Phase | Mode | Why |
|-------|------|-----|
| 2 (parallel gather) | sub-agent | independent gather, no comms needed |
| 3 (consensus merge) | agent team | discuss/resolve conflicts |
| 4 (independent verify) | sub-agent | one QA agent, objective check |

**Transition rules:** team→sub: `TeamDelete` before any `Agent` call. sub→team: pass sub outputs to members as Read paths. team→team: delete the old team before a new `TeamCreate` (one active team/session).

---

## Authoring rules
1. State the execution mode first (hybrid → per-phase table required).
2. Team mode: spell out TeamCreate/SendMessage/TaskCreate usage. Sub mode: spell out every Agent param (name, subagent_type, prompt, run_in_background, model).
3. Use explicit `_workspace/`-relative paths, never bare relative paths.
4. Declare phase dependencies; emphasize mode-switch points in hybrid.
5. Error handling must be realistic — don't assume everything succeeds.
6. Required test scenario: ≥1 normal + ≥1 error.

## Follow-up keywords (required in description)
Initial keywords alone leave the harness dead after the first run. Always include: rerun / re-run / update / fix / improve / "redo only the {part} of {domain}" / "based on previous result" + Korean equivalents (다시 실행 / 재실행 / 업데이트 / 수정 / 보완) + everyday domain requests.
