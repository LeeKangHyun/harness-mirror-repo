# kangto-factory — 강토의 공장 (Harness Forge)

A custom **harness factory** for Claude Code: say *"build a harness for this project"* / *"하네스 만들어줘"* and it forges an **agent team + the skills they use**, recorded in a machine-readable `harness.json` manifest.

This is a personal variant of [`revfactory/harness`](https://github.com/revfactory/harness), rebuilt with three deliberate differences.

## How it differs from the original harness

| | Original `harness` | `kangto-factory` |
|-|--------------------|------------------|
| **Skill language** | Korean body (~458 lines) | **English** body (~173 lines, smaller per trigger) |
| **Generated record** | prose changelog in CLAUDE.md only | **`.claude/harness.json` manifest** — machine-readable + drift-checkable via `check_harness.py` |
| **Triggers** | Korean-leaning | **EN + KO bilingual** triggers throughout |
| **Model policy** | always `opus` | `opus` default + explicit opus/sonnet/haiku mapping (recorded per agent) |

The core design — 7-phase workflow, agent↔skill separation, 6 architecture patterns, 3 execution modes, progressive disclosure, pushy descriptions, evolution loop — is inherited from the original.

**Honest caveats.** (1) The factory triggers rarely, so its smaller body saves little on its own — the real token win is right-sizing the *generated* harness (SKILL.md Phase 2-4), not this skill. (2) "Token savings" is estimated, not tokenizer-measured: a char-based estimate puts the body at ~31% of the original's per-trigger tokens, driven mostly by the Korean→English token-density gap rather than line count (see the comparison report below). (3) The manifest is drift-*checkable* (the script verifies it matches disk), but not auto-*regenerable* — rebuilding from it is still a manual/LLM step. (4) Like the original, this is prompt-ware: its effect depends on the runtime model following the instructions, and is not independently benchmarked here.

**Deeper comparison.** A measured, file-by-file comparison against the original — token estimates, what moved vs what was genuinely lost, a same-brief behavioral test of both skills, and the resulting fix log — lives in [docs/kangto-factory-vs-harness.md](../../docs/kangto-factory-vs-harness.md).

## Structure
```
kangto-factory/
├── SKILL.md                          # 7-phase workflow (English, lean)
├── references/
│   ├── agent-design-patterns.md      # patterns, execution modes, agent template
│   ├── orchestrator-template.md      # team / sub-agent / hybrid templates
│   ├── skill-authoring.md            # skill writing + quick testing
│   ├── skill-testing-guide.md        # measured eval: assertions, eval agents, workspace
│   ├── qa-agent-guide.md             # integration coherence, checklist, real bug cases
│   └── manifest-guide.md             # harness.json lifecycle & rationale
├── scripts/
│   └── check_harness.py              # drift checker: manifest <-> disk (stdlib only)
├── assets/
│   ├── harness.schema.json           # JSON Schema for the manifest
│   └── harness.example.json          # synced copy of the canonical example (examples/deep-research)
├── examples/
│   └── deep-research/                # a real generated harness (passes the drift checker)
└── README.md
```

## When NOT to use it

A harness is a meta-layer — it generates config you could write by hand, and that has a cost (extra files, a manifest to sync, process overhead). For a **one-off task or 1–2 agents**, hand-writing a couple of `.claude/agents/*.md` files is faster. A harness earns its cost only when the work **recurs**, **3+ specialists genuinely collaborate**, or you're producing **many harnesses** you want auditable. For simple work, a single agent / a plain skill / a short CLAUDE.md note is the better fit.

## Install (as a global skill)
```shell
cp -r skills/kangto-factory ~/.claude/skills/kangto-factory
```
Then trigger with: `build a harness for ...`, `하네스 만들어줘`, `강토 공장`, or maintenance phrases like `audit the harness` / `하네스 점검`.

## What it produces
```
your-project/
├── .claude/
│   ├── agents/            # one .md per agent
│   ├── skills/            # skills + an orchestrator skill
│   └── harness.json       # the manifest (source of truth)
└── CLAUDE.md              # minimal pointer: trigger rule + manifest pointer (changelog lives in harness.json)
```

License: Apache 2.0 (same as the original harness).
