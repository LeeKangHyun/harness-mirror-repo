# Agent Design Patterns

## Execution modes: Agent Teams vs Sub-agents

### Agent Teams (default)
A leader runs `TeamCreate` to spawn teammates as independent Claude Code instances. They talk directly via `SendMessage` and self-coordinate through a shared task list (`TaskCreate`/`TaskUpdate`).

```
[leader] ←→ [member A] ←→ [member B]
   ↕            ↕            ↕
   └──── shared task list ───┘
```

- **Tools:** `TeamCreate` (spawn), `SendMessage({to})` (direct) / `({to:"all"})` (broadcast, costly), `TaskCreate`/`TaskUpdate`.
- **Strengths:** members challenge and verify each other; findings shared in real time can redirect another member's work mid-flight.
- **Limits:** one active team per session (you may delete and recreate between phases); no nested teams; fixed leader; higher token cost.

### Sub-agents (lightweight)
The main agent spawns sub-agents with the `Agent` tool. They return results only to the main agent and never talk to each other.

```
[main] → [sub A] → result
      → [sub B] → result
```

- **Tool:** `Agent(prompt, subagent_type, run_in_background, model)`.
- **Strengths:** fast, token-efficient, results summarized back to main context.
- **Limits:** no inter-agent communication; main coordinates everything; no real-time challenge.

### Decision tree
```
2+ agents?
├── Yes → need inter-agent communication?
│         ├── Yes → Agent Team (default)
│         └── No  → Sub-agents are fine (results-only hand-off)
└── No (1) → Sub-agent
```
Default to teams; when choosing sub-agents, ask "is communication *really* unnecessary?"

### Team sizing

| Workload | Team size | Tasks per member |
|----------|-----------|------------------|
| Small (5–10 tasks) | 2–3 agents | 3–5 |
| Medium (10–20 tasks) | 3–5 agents | 4–6 |
| Large (20+ tasks) | 5–7 agents | 4–5 |

Coordination overhead grows with every member: 3 focused members beat 5 diffuse ones. Size from the task list, not by default.

---

## Architecture patterns

| # | Pattern | Shape | Best for | Team-mode fit |
|---|---------|-------|----------|---------------|
| 1 | **Pipeline** | A→B→C→D | each stage depends strongly on the prior output | limited (strong sequential dep); useful if a stage has a parallel sub-section |
| 2 | **Fan-out/Fan-in** | split → [A,B,C] → merge | same input, different angles | **best fit — use a team.** Members share/challenge findings live |
| 3 | **Expert Pool** | router → {A\|B\|C} | input type selects the handler | sub-agents fit better (call only the needed expert) |
| 4 | **Producer-Reviewer** | gen → review → (regen) | quality matters, objective check exists | team useful (live gen↔review feedback); cap retries at 2–3 |
| 5 | **Supervisor** | supervisor → workers (dynamic) | variable workload, runtime allocation | shared task list matches naturally; workers self-claim |
| 6 | **Hierarchical Delegation** | lead → sub-leads → workers | problem decomposes hierarchically | no nested teams — flatten, or level-1 team + level-2 sub-agents; keep depth ≤2 |

**Composite patterns** are common: Fan-out + Producer-Reviewer (parallel gen, each reviewed); Pipeline + Fan-out (parallelize one stage); Supervisor + Expert Pool (dynamic expert dispatch). Default composites to agent teams.

---

## Agent type selection

| Type | Tool access | Use for |
|------|------------|---------|
| `general-purpose` | full (incl. WebSearch/WebFetch) | web research, general work, **QA** (needs to run scripts) |
| `Explore` | read-only | codebase exploration/analysis |
| `Plan` | read-only | architecture/planning |
| custom (`.claude/agents/{name}.md`) | full | complex reusable roles with a defined persona |

**Every agent gets a `.claude/agents/{name}.md` file** — even built-in types. The file holds role/principles/protocol; `subagent_type` points at the built-in. Files make the team reusable next session and make the collaboration protocol explicit.

**Model selection.** Don't guess "light vs heavy" — apply this mapping, and **default to `opus` whenever a role is ambiguous** (a predictable default beats inconsistent ones). Record the chosen model per agent in `harness.json` and pass it explicitly on every call.

| Model | Assign when the role's core work is… | Examples |
|-------|--------------------------------------|----------|
| `opus` | reasoning, synthesis, integration, planning, conflict resolution, code generation, QA cross-comparison | synthesizer, architect, reviewer, qa-inspector, implementer |
| `sonnet` | structured gathering with light judgment, drafting, routine transforms, summarization | web-scout, drafter, summarizer, router |
| `haiku` | deterministic/mechanical work with clear rules — extraction, formatting, rule-based classification, renaming | formatter, extractor, tagger |

Rule of thumb: if a wrong output would require *reasoning* to catch, use `opus`. If correctness is *mechanically checkable*, a smaller model is fine. When unsure, use `opus`.

---

## Agent definition template

```markdown
---
name: agent-name
description: "1-2 sentence role. Trigger keywords."
---

# Agent Name — one-line role

You are a {role} expert in {domain}.

## Core role
1. ...
## Working principles
- ...
## I/O protocol
- Input:  {where/what it reads}
- Output: {where/what it writes}
- Format: {file format, structure}
## Team communication protocol   (team mode only)
- Receives: {from whom, what}
- Sends:    {to whom, what}
- Claims:   {which task types from the shared list}
## Error handling
- {on failure} / {on timeout}
## Collaboration
- relationship to other agents
```

---

## Agent split criteria

| Axis | Split | Merge |
|------|-------|-------|
| Specialty | different domains | overlapping domains |
| Parallelism | independently runnable | sequentially dependent |
| Context | heavy context load | light and fast |
| Reuse | used by other teams too | used only by this team |

## Agent reuse design (Phase 3-0)

| Situation | Action |
|-----------|--------|
| Existing agent fully covers the new role | reuse — don't create |
| Existing partially covers, can generalize | extend/generalize the existing one |
| Intended domain-specific partial overlap | create new, keep separate |
| Completely different scope | create new |

One agent, one focused role → higher reuse, less duplication. When generalizing an existing agent, check the orchestrators/teams that depend on it and dry-run to confirm prior behavior holds.

## Skill vs agent

| | Skill | Agent |
|-|-------|-------|
| Is | procedural knowledge + tool bundle | expert persona + behavior rules |
| Lives in | `.claude/skills/` | `.claude/agents/` |
| Triggered by | user keyword match | explicit `Agent` call |
| Answers | "how" | "who" |
