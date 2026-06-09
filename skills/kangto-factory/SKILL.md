---
name: kangto-factory
description: "Forges a custom harness for any project or domain — defines specialist agents and generates the skills they use. A meta-skill: a factory that turns one domain sentence into an agent team + skill set, recorded in a machine-readable harness.json manifest. TRIGGER on English: 'build/forge a harness', 'create an agent team', 'set up/design a harness for this project', 'kangto factory'. TRIGGER on Korean: '하네스 만들어줘/구성해줘/구축해줘/설계해줘', '강토 공장', '에이전트 팀 만들어줘'. ALSO maintenance & follow-up: 'audit/inspect/sync the harness', 'extend/rebuild/update/rerun the harness', '하네스 점검/감사/동기화/확장/재구성/업데이트'. Use whenever the user wants to scaffold OR evolve a domain-specific agent team and its skills."
---

# kangto-factory — Harness Forge (Agent Team & Skill Architect)

A meta-skill that builds a **harness** for a project/domain: it defines specialist **agents** (who), generates the **skills** they use (how), wires an **orchestrator** (when/in what order), and records everything in a **harness.json** manifest so the result is auditable and regenerable.

**Core principles**
1. Generate agent definitions (`.claude/agents/`) and skills (`.claude/skills/`).
2. **Default to agent teams** for 2+ collaborating agents; fall back to sub-agents only when team communication is genuinely unnecessary.
3. **Record the harness in `.claude/harness.json`** — the single source of truth for audit, drift detection, and follow-up runs.
4. **Register a pointer in CLAUDE.md** so the orchestrator skill triggers in new sessions.
5. **A harness evolves.** After each run, collect feedback and update agents, skills, and the manifest.

---

## When NOT to forge a harness

A harness is a meta-layer that generates config the user could write by hand. It is not free — it adds files, a manifest to keep in sync, and process overhead. Be honest about ROI before building one:

- **One-off task, or 1–2 agents** → skip the factory. Writing a couple of `.claude/agents/*.md` files by hand (or just calling the `Agent` tool with a good prompt) is faster than running a 7-phase build and reviewing its output.
- **No reuse expected** → if this team will run once and never again, the manifest/orchestrator ceremony is pure overhead.
- **Simple, well-scoped work** → the value of a harness scales with task complexity; for simple work it mostly adds ceremony. Say so instead of building anyway.

A harness earns its cost when: the work recurs, 3+ specialists genuinely collaborate, or you are producing many harnesses and want them auditable/regenerable. If the request doesn't clear that bar, tell the user a lighter option (a single agent, a plain skill, or a short CLAUDE.md note) is the better fit — then stop.

## Workflow

### Phase 0 — Audit current state

When triggered, first read what already exists:
1. Read `.claude/harness.json` (if present), `.claude/agents/`, `.claude/skills/`, and the harness pointer in `CLAUDE.md`.
2. Branch by situation:
   - **New build** — no manifest / empty agent+skill dirs → run Phases 1–6.
   - **Extend** — manifest exists, user wants new agent/skill → run only the phases the change touches (see matrix).
   - **Maintain** — audit/fix/sync request → go to Phase 7-5.
3. **Drift check:** run `scripts/check_harness.py {project-root}` — it diffs `harness.json` against the files on disk and validates cross-references mechanically (exit 0 = clean, 1 = drift, 2 = no/invalid manifest). Report any mismatch it prints.
4. Summarize the audit to the user and confirm the plan before writing.

**Extend matrix** (which phases to run):

| Change | P1 | P2 | P3 | P4 | P5 | P6 |
|--------|----|----|----|----|----|----|
| Add agent | skip | placement only | required (incl. 3-0) | only if a dedicated skill is needed (incl. 4-0) | update orchestrator | required |
| Add/edit skill | skip | skip | skip | required (incl. 4-0) | only if wiring changes | required |
| Architecture change | skip | required | only affected agents (3-0) | only affected skills (4-0) | required | required |

### Phase 1 — Domain analysis
1. Identify the domain and the core task types (generate / verify / edit / analyze …).
2. Explore the codebase — tech stack, data models, key modules.
3. Cross-check against existing agents/skills (from Phase 0) for overlap.
4. **Gauge user expertise** from their wording and calibrate tone — don't drop terms like "assertion" or "JSON schema" unexplained on a non-coder.

### Phase 2 — Team architecture

**2-1. Execution mode.** Agent teams are the default for 2+ collaborators; teammates self-coordinate via `SendMessage` + shared task list (`TaskCreate`). Choose sub-agents only when agents never need to talk to each other (results-only hand-off). Use hybrid when phases differ (e.g. parallel gather as sub-agents → consensus merge as a team).

**2-2. Pattern.** Pick one (details in `references/agent-design-patterns.md`):
Pipeline · Fan-out/Fan-in · Expert Pool · Producer-Reviewer · Supervisor · Hierarchical Delegation.

**2-3. Agent split.** Decide split vs merge on four axes — specialty, parallelism, context load, reuse. (Table in `references/agent-design-patterns.md`.)

### Phase 3 — Agent definitions

**3-0. Reuse check.** Before creating an agent, compare against existing `.claude/agents/`. If an existing agent fully covers the new role, reuse it; if it partially covers and can generalize, extend it; otherwise create new. (Classification in `references/agent-design-patterns.md`.)

**Every agent gets a file** at `.claude/agents/{name}.md` — even built-in types (`general-purpose`, `Explore`, `Plan`), which still get a file holding role + principles + protocols (the `subagent_type` just points at the built-in). Files exist so the team is reusable next session and the collaboration protocol is explicit.

**Model:** default `opus` for reasoning-heavy roles; you may assign `sonnet`/`haiku` to lightweight gather/format roles to save tokens. Record the chosen model per agent in the manifest, and pass it explicitly on every Agent/TeamCreate call.

Required sections per agent file: core role, working principles, I/O protocol, error handling, collaboration. In team mode add a **Team Communication Protocol** section (who it messages, what tasks it claims). Template + full examples: `references/agent-design-patterns.md`.

**If a QA agent is included:** use `general-purpose` (not read-only `Explore`, which can't run verification scripts); QA's value is **cross-boundary comparison** (read API response + frontend hook, compare shapes), run **incrementally** after each module, not once at the end. Full methodology — boundary-mismatch patterns, integration-coherence checks, checklist + agent template, real bug cases: `references/qa-agent-guide.md`.

### Phase 4 — Skill generation

**4-0. Reuse check.** Before creating a skill, scan `.claude/skills/` for functional overlap; generalize instead of duplicating. (Patterns in `references/skill-authoring.md`.)

**4-1. Structure:** `{skill}/SKILL.md` (required: YAML `name` + `description`, then body) plus optional `scripts/` (deterministic code), `references/` (conditionally loaded docs), `assets/` (templates/images).

**4-2. Pushy description.** The description is the only trigger mechanism — write it actively. State what the skill does **and** concrete trigger phrases, and distinguish near-miss cases that should NOT trigger it.

**4-3. Body rules:** explain **why** (not bare ALWAYS/NEVER — the model generalizes from reasons); keep it **lean** (target <300 lines, move detail to `references/`); generalize over the principle, don't overfit to one example; bundle repeated code into `scripts/`; write imperatively.

**4-4. Progressive disclosure:** metadata (name+description, always loaded) → SKILL.md body (on trigger, keep small) → `references/` (only when needed). Split per-domain references so only the relevant file loads.

**4-5. Wiring:** one agent ↔ one or more skills; shared skills are fine. Skill = "how", agent = "who". Full guide: `references/skill-authoring.md`.

### Phase 5 — Orchestration & manifest

Build **one orchestrator skill** that ties agents + skills into a workflow ("who collaborates, when, in what order"). Pick the matching template from `references/orchestrator-template.md` (team / sub-agent / hybrid). When extending, edit the existing orchestrator instead of creating a new one.

The orchestrator must specify: execution mode, team composition, a **Phase 0 context check** (initial vs follow-up vs partial rerun, keyed on `_workspace/` existence), a data-passing protocol, error handling, and a test scenario.

**Data passing:** message-based (`SendMessage`, real-time), task-based (`TaskCreate/Update`, dependencies), file-based (`_workspace/{phase}_{agent}_{artifact}.ext`, large/structured outputs), return-value (sub-agent results). Keep intermediate files in `_workspace/`; emit only final outputs to the user path.

**5-A. Write the manifest.** Generate `.claude/harness.json` per `assets/harness.schema.json` — list every agent (name, type, model, file, skills, role), every skill (name, file, usedBy), the pattern, execution mode, orchestrator, and a changelog. This is the differentiator: the harness becomes auditable and regenerable, instead of living only as prose.

**5-B. Register the CLAUDE.md pointer** — trigger rule + a pointer to the manifest, nothing else. `harness.json` is the **single canonical record** (inventory + changelog); the `.claude/agents/` and `.claude/skills/` files are its implementation; CLAUDE.md only needs to make the orchestrator trigger in a new session. Do **not** copy the agent/skill list or the changelog into CLAUDE.md — duplicating them just creates a third surface to drift.

````markdown
## Harness: {domain}
**Goal:** {one line}
**Trigger:** For {domain} work, use the `{orchestrator-skill}` skill. Simple questions can be answered directly.
**Manifest:** `.claude/harness.json`
````

**Follow-up support:** include rerun keywords in the orchestrator description ("rerun / update / fix / improve / 다시 실행 / 업데이트"); add the Phase 0 context check; tell each agent how to behave when prior outputs exist (read them, apply only the requested change).

### Phase 6 — Validation

- **Structure:** every agent file present and in place; each skill's `name`+`description` frontmatter valid; no `.claude/commands/` created; **run `scripts/check_harness.py {project-root}` and confirm it exits 0** (manifest ↔ disk agree).
- **By mode:** team → communication paths, task dependencies, team size; sub-agent → I/O wiring, `run_in_background`, return collection; hybrid → mode noted per phase, no dead link at phase boundaries.
- **Skill execution:** for each skill write 2–3 realistic test prompts; when possible run with-skill vs without-skill to confirm added value; evaluate with assertions (objective) or user review (subjective); iterate by **generalizing** the fix, not patching one case. For rigorous measured evaluation — assertion grading, grader/comparator/analyzer agents, iteration workspace: `references/skill-testing-guide.md`.
- **Triggers:** 8–10 should-trigger + 8–10 should-NOT-trigger near-miss queries (boundary-ambiguous ones, not obviously-unrelated). Check for collisions with existing skills.
- **Dry run:** orchestrator phase order is logical; no dead links in data flow; each agent's input matches a prior phase's output; fallback paths are executable.

### Phase 7 — Evolution

A harness is not static.

**7-1. Collect feedback** after each run ("anything to improve in the result or the team setup?"). Offer the chance; don't force it.

**7-2. Route feedback:**

| Feedback | Edit |
|----------|------|
| Output quality | that agent's skill |
| Agent role | agent `.md` (or add a new agent) |
| Workflow order | orchestrator skill |
| Team composition | orchestrator + agents |
| Missing trigger | skill description |

**7-3. Record every change** in the `harness.json` changelog (date, change, target, reason) — the one canonical place. Update the affected `agents`/`skills` entries in the same edit, then re-run `scripts/check_harness.py` to confirm the manifest still matches disk. Do not also log it in CLAUDE.md.

**7-4. Propose evolution** proactively when: the same feedback recurs 2+ times, an agent fails repeatedly, or the user keeps bypassing the orchestrator manually.

**7-5. Maintenance workflow** (entered from Phase 0 "maintain"):
1. **Audit** — diff `harness.json` ↔ actual `.claude/agents/` + `.claude/skills/`; report mismatches.
2. **Change incrementally** — one change at a time, then immediately step 3.
3. **Sync** — update `harness.json` (and CLAUDE.md changelog).
4. **Verify** — structure check (6); trigger check if triggers changed; full execution/dry-run for large changes; confirm manifest ↔ disk agree.

---

## Output checklist

- [ ] `.claude/agents/` — a definition file per agent (even built-in types)
- [ ] `.claude/skills/` — skill files (SKILL.md + optional references/)
- [ ] One orchestrator skill (data flow + error handling + test scenario + Phase 0 context check)
- [ ] **`.claude/harness.json`** written and matching disk (per `assets/harness.schema.json`)
- [ ] Execution mode stated (team / sub-agent / hybrid)
- [ ] Per-agent model recorded; passed explicitly on every call
- [ ] Reuse checks done before new agents (3-0) and new skills (4-0)
- [ ] No `.claude/commands/` created; no collision with existing agents/skills
- [ ] Skill descriptions are pushy and include follow-up keywords (EN + KO)
- [ ] Tested with 2–3 prompts; triggers validated (should + should-NOT)
- [ ] CLAUDE.md pointer registered (trigger rule + manifest pointer only); no agent/skill list or changelog duplicated

## References

- Patterns, execution modes, agent definition template: `references/agent-design-patterns.md`
- Orchestrator templates (team / sub-agent / hybrid): `references/orchestrator-template.md`
- Skill authoring (writing + quick testing): `references/skill-authoring.md`
- Skill testing & iteration (measured: assertions, eval agents, workspace): `references/skill-testing-guide.md`
- QA agent (integration coherence, checklist, real bug cases): `references/qa-agent-guide.md`
- Manifest schema (`harness.json`): `assets/harness.schema.json` + `references/manifest-guide.md`
