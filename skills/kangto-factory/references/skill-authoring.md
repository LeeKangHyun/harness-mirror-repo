# Skill Authoring & Testing

## Structure
```
skill-name/
├── SKILL.md          # required: YAML frontmatter (name, description) + Markdown body
├── scripts/          # optional: deterministic/repeated code (run without loading into context)
├── references/       # optional: docs loaded only when needed
└── assets/           # optional: templates, images, schemas used in output
```

## Description — the only trigger mechanism
The model triggers conservatively, so write the description **pushy**: state what the skill does **and** concrete trigger situations, and distinguish near-miss cases that should NOT trigger it. For a bilingual factory, include both English and Korean trigger phrases.

- Bad: `"A skill that processes PDFs"`
- Good: `"Read PDFs, extract text/tables, merge, split, rotate, watermark, encrypt, OCR — every PDF operation. Use whenever a .pdf file is mentioned or a PDF output is requested. PDF 작업(읽기/추출/병합/분할/OCR) 시 반드시 사용."`

Always include **follow-up keywords** (rerun / update / fix / 다시 실행 / 업데이트) so the skill keeps triggering after the first use.

## Body rules

| Rule | Why |
|------|-----|
| Explain **why** | Bare ALWAYS/NEVER doesn't generalize. Given the reason, the model decides correctly on edge cases. |
| Stay **lean** | The context window is a shared resource. Target <300 lines; move detail to `references/`. |
| **Generalize** | Teach the principle, not a rule that fits one example. No overfitting. |
| **Bundle** repeated code | If agents keep writing the same helper, pre-bundle it in `scripts/`. |
| Write **imperatively** | "Do X", "Write Y". |

## Progressive disclosure (3-tier loading)

| Tier | Loaded | Size target |
|------|--------|-------------|
| Metadata (name + description) | always in context | ~100 words |
| SKILL.md body | on trigger | small (<300 lines) |
| `references/` | only when needed | unbounded (scripts run without loading) |

When SKILL.md nears the limit, split detail into `references/` and leave a pointer ("read this file when …"). Add a table of contents to references over ~300 lines. Split per-domain references so only the relevant file loads (e.g. `references/aws.md`, `gcp.md`, `azure.md`).

## Skill ↔ agent wiring

| Method | How | When |
|--------|-----|------|
| Skill-tool call | agent prompt says "use the Skill tool to call /skill-name" | skill is a standalone, user-callable workflow |
| Inline in prompt | embed the skill content in the agent definition | skill is short (≤50 lines), used only by this agent |
| Reference load | agent `Read`s the skill's references on demand | skill is large, needed only conditionally |

One agent ↔ one or more skills; shared skills are fine. Skill = "how", agent = "who".

## Reuse design (Phase 4-0)
Before creating a skill, scan `.claude/skills/` for functional overlap. If an existing skill covers it, reuse; if it partially covers and can generalize, extend; otherwise create new. Prefer generalizing the principle over duplicating a near-identical skill under a new name.

---

## Testing

**1. Test prompts** — write 2–3 realistic prompts per skill (natural phrasing a real user would type).

**2. With-skill vs without-skill** — when possible, spawn two agents on the same prompt (one reads the skill, one doesn't) to confirm the skill's added value.

**3. Evaluate** — objective outputs (file created, data extracted) → define assertions; subjective outputs (tone, design) → user review.

**4. Iterate** — on a problem, **generalize** the fix (no narrow one-case patch), re-test, repeat until the user is satisfied or gains plateau.

**5. Bundle** — if every test run rewrites the same helper, pre-bundle it in `scripts/`.

## Trigger validation
- 8–10 **should-trigger** queries (formal/casual, explicit/implicit, EN + KO).
- 8–10 **should-NOT-trigger** near-miss queries — boundary-ambiguous, not obviously unrelated. A good near-miss: "extract this Excel chart as PNG" (xlsx skill vs image-conversion). A useless one: "write a Fibonacci function".
- Check collisions with existing skills.

## Dry run
Orchestrator phase order is logical; no dead links in the data flow; each agent's input matches a prior phase's output; per-error fallback paths are executable.
