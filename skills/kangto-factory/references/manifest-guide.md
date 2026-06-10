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
Read the canonical worked example: `examples/deep-research/.claude/harness.json` — a real generated harness that passes the drift checker (expected output in `examples/deep-research/README.md`). It is deliberately **not** copied inline here: a duplicated example JSON drifted from the real one once already, which is exactly the failure mode this manifest exists to prevent. One canonical copy, pointers everywhere else — the only exception is `assets/harness.example.json`, a convenience copy that must stay byte-identical to the canonical file (touch one, sync the other).

## Validation
Run `scripts/check_harness.py {project-root}` before finishing Phase 5/6 and confirm it exits 0. It enforces: required schema fields and enum values; every `file` (agents, skills, orchestrator) exists on disk; no orphan agent/skill files missing from the manifest; every `skills`/`usedBy` cross-reference resolves. This is the mechanical guarantee behind "auditable" — without running it, the claim is hollow.
