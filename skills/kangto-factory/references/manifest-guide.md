# Harness Manifest Guide — `harness.json`

The manifest is kangto-factory's signature: a machine-readable record of the harness so it can be **audited, drift-checked, and regenerated** instead of living only as prose in CLAUDE.md.

## Location
`.claude/harness.json` at the project root. One manifest per project (a multi-domain project may keep an array of harnesses under `"harnesses"`, but prefer one per domain repo).

## Lifecycle
- **Phase 0 (audit):** read the manifest first, then run `scripts/check_harness.py {project-root}` to diff it against the files on disk (`.claude/agents/`, `.claude/skills/`) and validate cross-references. Report any drift it prints.
- **Phase 5 (write):** after the orchestrator and all agents/skills exist, write the manifest listing everything.
- **Phase 7 (evolve):** on every change, append a `changelog` entry and update the affected `agents`/`skills` entries, then re-run the drift checker. Do not also log the change in CLAUDE.md — the manifest is the one canonical record.

## Why this beats prose-only
- **Drift detection is mechanical** — compare manifest ↔ disk, no human reading required.
- **Regeneration** — the manifest captures pattern + mode + wiring, so a later session can rebuild or extend deterministically.
- **One canonical source** — the full inventory AND the changelog live only here. CLAUDE.md holds just the trigger pointer (so the orchestrator fires in a new session); the `.claude/` files are the implementation. No third surface to drift.

## Schema
The authoritative JSON Schema is `assets/harness.schema.json`. Minimum required fields: `name`, `version`, `domain`, `executionMode`, `pattern`, `orchestrator`, `agents`, `skills`, `changelog`.

## Example
```json
{
  "name": "deep-research",
  "version": "1.0.0",
  "domain": "Multi-source research with cross-validation",
  "createdAt": "2026-06-09",
  "executionMode": "team",
  "pattern": "fan-out-fan-in",
  "orchestrator": ".claude/skills/research-orchestrator/SKILL.md",
  "agents": [
    { "name": "web-scout", "type": "general-purpose", "model": "sonnet",
      "file": ".claude/agents/web-scout.md", "skills": ["web-search"], "role": "Gather web/news sources" },
    { "name": "academic-scout", "type": "general-purpose", "model": "opus",
      "file": ".claude/agents/academic-scout.md", "skills": ["paper-search"], "role": "Gather peer-reviewed sources" },
    { "name": "synthesizer", "type": "custom", "model": "opus",
      "file": ".claude/agents/synthesizer.md", "skills": ["cross-validate", "report-write"],
      "role": "Cross-validate findings and write the report" }
  ],
  "skills": [
    { "name": "web-search",     "file": ".claude/skills/web-search/SKILL.md",     "usedBy": ["web-scout"] },
    { "name": "paper-search",   "file": ".claude/skills/paper-search/SKILL.md",   "usedBy": ["academic-scout"] },
    { "name": "cross-validate", "file": ".claude/skills/cross-validate/SKILL.md", "usedBy": ["synthesizer"] },
    { "name": "report-write",   "file": ".claude/skills/report-write/SKILL.md",   "usedBy": ["synthesizer"] }
  ],
  "changelog": [
    { "date": "2026-06-09", "change": "initial build", "target": "all", "reason": "-" }
  ]
}
```

## Validation
Run `scripts/check_harness.py {project-root}` before finishing Phase 5/6 and confirm it exits 0. It enforces: required schema fields and enum values; every `file` (agents, skills, orchestrator) exists on disk; no orphan agent/skill files missing from the manifest; every `skills`/`usedBy` cross-reference resolves. This is the mechanical guarantee behind "auditable" — without running it, the claim is hollow.
