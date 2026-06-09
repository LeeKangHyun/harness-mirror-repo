# kangto-factory — 강토의 공장 (Harness Forge)

A custom **harness factory** for Claude Code: say *"build a harness for this project"* / *"하네스 만들어줘"* and it forges an **agent team + the skills they use**, recorded in a machine-readable `harness.json` manifest.

This is a personal variant of [`revfactory/harness`](https://github.com/revfactory/harness), rebuilt with three deliberate differences.

## How it differs from the original harness

| | Original `harness` | `kangto-factory` |
|-|--------------------|------------------|
| **Skill language** | Korean body (~458 lines) | **English** body (leaner, lower token cost per trigger) |
| **Generated record** | prose changelog in CLAUDE.md only | **`.claude/harness.json` manifest** — machine-readable, drift-checkable, regenerable |
| **Triggers** | Korean-leaning | **EN + KO bilingual** triggers throughout |
| **Model policy** | always `opus` | `opus` default, `sonnet`/`haiku` allowed for light roles (recorded per agent) |

The core design — 7-phase workflow, agent↔skill separation, 6 architecture patterns, 3 execution modes, progressive disclosure, pushy descriptions, evolution loop — is inherited from the original.

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
│   └── harness.example.json          # worked example (deep-research)
└── README.md
```

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
└── CLAUDE.md              # minimal pointer: trigger rule + changelog
```

License: Apache 2.0 (same as the original harness).
