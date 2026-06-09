# QA Agent Guide

Reference for including a **QA agent** in a build harness. Based on real bug patterns found in production projects, it gives a verification methodology that catches the defects QA most often misses. Load when Phase 3 adds a QA agent.

## Contents
1. Defects QA misses
2. Integration Coherence Verification
3. QA agent design principles
4. Verification checklist template
5. QA agent definition template
6. Real bug cases

---

## 1. Defects QA misses

### 1-1. Boundary mismatch (most common)
Two components are each implemented "correctly," but their contract breaks at the seam.

| Boundary | Mismatch example | Why it's missed |
|----------|-----------------|-----------------|
| API response → frontend hook | API returns `{ projects: [...] }`, hook expects `Project[]` | each verified alone passes; no cross-check |
| API field name → type def | API returns `thumbnailUrl`, type says `thumbnail_url` | a generic cast hides it from the compiler |
| File path → link href | page lives at `/dashboard/create`, link points to `/create` | file tree and href never cross-compared |
| State transition map → actual updates | map defines `generating → approved`, code never performs it | only the map's existence is checked, not every update site |
| API endpoint → hook | endpoint exists but no hook calls it | endpoint list and hook list not mapped 1:1 |
| Immediate response → async result | API returns `{ status }` now, frontend reads `data.failedIndices` | sync/async response shapes not distinguished |

### 1-2. Why static review and `build` pass don't catch it
- **Generics lie:** `fetchJson<Project[]>()` compiles even if the runtime payload is `{ projects: [...] }`.
- **Build success ≠ correct runtime:** casts, `any`, and generics make the build green while runtime fails.
- **Existence ≠ connection:** "does the API exist?" and "does the API's response match what the caller expects?" are entirely different checks.

---

## 2. Integration Coherence Verification

The **cross-comparison** checks a QA agent must run. The unifying rule: **read both sides at once** (producer + consumer), never one alone.

### 2-1. API response ↔ hook type
Compare each API route's response object shape against the consuming hook's `fetchJson<T>` type.
1. Extract the shape passed to the response (`NextResponse.json(...)` / `res.json(...)` / etc.).
2. Read the consuming hook's expected type `T`.
3. Compare shape vs `T`; check wrapping (does `{ data: [...] }` get unwrapped to `.data`?).
- Watch: pagination (`{ items, total, page }` vs array), snake_case↔camelCase, 202-accepted vs final result shape.

### 2-2. File path ↔ link/router path
Extract URL paths from page files and diff against every `href`, `router.push()`, `redirect()`.
- Strip route groups `(group)` from the URL; treat `[param]` as a dynamic segment; mind path prefixes (e.g. everything under `dashboard/`).

### 2-3. State transition completeness
Extract every `status:` update and diff against the transition map.
1. List allowed transitions from the map. 2. Grep all `update({ status: "..." })`. 3. Confirm each is in the map (no unauthorized transition). 4. Find map transitions never executed in code (dead transitions). 5. Especially: intermediate → final transitions that are silently missing.

### 2-4. Endpoint ↔ hook 1:1 mapping
List all API routes and all hooks; flag endpoints no hook calls. Decide whether "unused" is intentional (admin API) or a missing call.

---

## 3. QA agent design principles

**3-1. Use `general-purpose`, not `Explore`.** Effective QA needs to Grep for patterns, run comparison scripts, and sometimes fix — `Explore` is read-only. Define a "verify → report → request fix" protocol in the agent.

**3-2. Cross-comparison over existence.**

| Weak check | Strong check |
|-----------|--------------|
| Does the endpoint exist? | Does its response shape match the hook's type? |
| Is the transition map defined? | Does every status update match a map transition? |
| Does the page file exist? | Does every link point to a real page? |
| Is strict mode on? | Is type safety bypassed by a generic cast? |

**3-3. "Read both sides."** State explicitly in the agent definition: read the API route **and** its hook together; the transition map **and** the update code together; the file tree **and** the link paths together.

**3-4. Run incrementally, not once at the end.** QA placed only after full build lets bugs accumulate and early mismatches propagate. Run cross-checks the moment each module (e.g. each API + its hook) is done.

---

## 4. Verification checklist template

Embed in the QA agent definition (web-app example; generalize per stack).

```markdown
### Integration coherence (web app)
#### API ↔ frontend
- [ ] Every API response shape matches the consuming hook's generic type
- [ ] Wrapped responses ({ items: [...] }) are unwrapped in the hook
- [ ] snake_case ↔ camelCase conversion is consistent
- [ ] Immediate (202) vs final result shapes are distinguished on the frontend
- [ ] Every endpoint has a hook that actually calls it
#### Routing
- [ ] Every href/router.push points to a real page file
- [ ] Route groups ((group)) removed from the URL are accounted for
- [ ] Dynamic segments ([id]) are filled with the right param
#### State machine
- [ ] Every defined transition is executed (no dead transitions)
- [ ] Every status update is a defined transition (no unauthorized ones)
- [ ] Intermediate → final transitions are not missing
- [ ] Frontend branches (if status === "X") have a reachable X
#### Data flow
- [ ] DB field names ↔ API response field names map consistently
- [ ] Frontend type defs match API response field names
- [ ] null/undefined handling for optional fields is consistent on both sides
```

---

## 5. QA agent definition template

```markdown
---
name: qa-inspector
description: "QA verification expert. Checks spec compliance, integration coherence, and design quality. Use after each module and before final delivery."
---

# QA Inspector

## Core role
Verify implementation quality against spec, prioritizing **cross-module integration coherence**.

## Priority
1. Integration coherence (highest) — boundary mismatch is the top cause of runtime errors
2. Functional spec compliance — API / state machine / data model
3. Design quality — color / type / responsive
4. Code quality — dead code, naming

## Method: read both sides

| Target | Producer (left) | Consumer (right) |
|--------|-----------------|------------------|
| Response shape | route response | hook fetchJson<T> |
| Routing | page file path | href, router.push |
| State | transition map | status update code |
| DB → API → UI | column name | API field → type def |

## Team communication protocol
- On a finding, send a concrete fix request to the owning agent (file:line + how to fix)
- Boundary issues: notify BOTH sides
- To leader: a report separating passed / failed / unverified
```

---

## 6. Real bug cases
Every rule above was extracted from these production bugs:

| Bug | Boundary | Cause |
|-----|----------|-------|
| `projects?.filter is not a function` | API→hook | API returned `{projects:[]}`, hook expected an array |
| all dashboard links 404 | path→href | missing `/dashboard/` prefix |
| theme image not showing | API→component | `thumbnailUrl` vs `thumbnail_url` |
| theme selection not saved | API→hook | select-theme API existed, no hook |
| create page waits forever | transition→code | `template_approved` transition missing in code |
| `data.failedIndices` crash | immediate→frontend | accessed a background result on the immediate response |
| view-slides 404 after done | path→href | `/projects/` vs `/dashboard/projects/` |
