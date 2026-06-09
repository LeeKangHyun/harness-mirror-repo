# Harness Manifest Guide — `harness.json`

The manifest is kangto-factory's signature: a machine-readable record of the harness so it can be **audited, drift-checked, and regenerated** instead of living only as prose in CLAUDE.md.

## Location
`.claude/harness.json` at the project root. One manifest per project (a multi-domain project may keep an array of harnesses under `"harnesses"`, but prefer one per domain repo).

## Lifecycle
- **Phase 0 (audit):** read the manifest first, then diff it against the files on disk (`.claude/agents/`, `.claude/skills/`). Report drift — a file the manifest omits, or a manifest entry with no file.
- **Phase 5 (write):** after the orchestrator and all agents/skills exist, write the manifest listing everything.
- **Phase 7 (evolve):** on every change, append a `changelog` entry and update the affected `agents`/`skills` entries. Mirror the one-line changelog into the CLAUDE.md pointer.

## Why this beats prose-only
- **Drift detection is mechanical** — compare manifest ↔ disk, no human reading required.
- **Regeneration** — the manifest captures pattern + mode + wiring, so a later session can rebuild or extend deterministically.
- **CLAUDE.md stays minimal** — it holds only the trigger pointer + changelog; the full inventory lives here, avoiding duplication.

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
Validate the written manifest against the schema before finishing Phase 5/6. Every `file` path must exist on disk; every `skills`/`usedBy` cross-reference must resolve to a listed entry.
