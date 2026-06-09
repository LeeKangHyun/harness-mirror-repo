#!/usr/bin/env python3
"""check_harness.py — drift checker for a kangto-factory harness.

Compares .claude/harness.json against the agent/skill files actually on disk
and validates internal cross-references. This is what makes the manifest's
"auditable" claim real instead of aspirational: drift detection is mechanical,
not a human reading prose.

Usage:
    python3 check_harness.py [PROJECT_ROOT]   # defaults to current directory

Exit codes:
    0  manifest and disk agree
    1  drift found (missing files, orphan files, or broken cross-references)
    2  manifest missing or invalid JSON

No third-party dependencies.
"""
import json
import os
import sys

REQUIRED_TOP = ["name", "version", "domain", "executionMode", "pattern",
                "orchestrator", "agents", "skills", "changelog"]
EXEC_MODES = {"team", "subagent", "hybrid"}
PATTERNS = {"pipeline", "fan-out-fan-in", "expert-pool", "producer-reviewer",
            "supervisor", "hierarchical", "composite"}
AGENT_TYPES = {"general-purpose", "Explore", "Plan", "custom"}
MODELS = {"opus", "sonnet", "haiku"}


def load_manifest(root):
    path = os.path.join(root, ".claude", "harness.json")
    if not os.path.isfile(path):
        print(f"FATAL: no manifest at {path}")
        sys.exit(2)
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), path
    except json.JSONDecodeError as exc:
        print(f"FATAL: {path} is not valid JSON: {exc}")
        sys.exit(2)


def schema_check(m, errors):
    for k in REQUIRED_TOP:
        if k not in m:
            errors.append(f"schema: missing required field '{k}'")
    if m.get("executionMode") not in EXEC_MODES:
        errors.append(f"schema: executionMode '{m.get('executionMode')}' not in {sorted(EXEC_MODES)}")
    if m.get("pattern") not in PATTERNS:
        errors.append(f"schema: pattern '{m.get('pattern')}' not in {sorted(PATTERNS)}")
    for a in m.get("agents", []):
        if a.get("type") not in AGENT_TYPES:
            errors.append(f"schema: agent '{a.get('name')}' type '{a.get('type')}' invalid")
        if a.get("model") not in MODELS:
            errors.append(f"schema: agent '{a.get('name')}' model '{a.get('model')}' invalid")


def disk_check(root, m, errors):
    # Every manifest file must exist on disk.
    listed_agent_files, listed_skill_files = set(), set()
    for a in m.get("agents", []):
        f = a.get("file")
        if f:
            listed_agent_files.add(os.path.normpath(f))
            if not os.path.isfile(os.path.join(root, f)):
                errors.append(f"missing file: agent '{a.get('name')}' -> {f}")
    for s in m.get("skills", []):
        f = s.get("file")
        if f:
            listed_skill_files.add(os.path.normpath(f))
            if not os.path.isfile(os.path.join(root, f)):
                errors.append(f"missing file: skill '{s.get('name')}' -> {f}")
    orch = m.get("orchestrator")
    if orch and not os.path.isfile(os.path.join(root, orch)):
        errors.append(f"missing file: orchestrator -> {orch}")

    # Orphans: files on disk that the manifest does not list.
    agents_dir = os.path.join(root, ".claude", "agents")
    if os.path.isdir(agents_dir):
        for fn in os.listdir(agents_dir):
            if fn.endswith(".md"):
                rel = os.path.normpath(os.path.join(".claude", "agents", fn))
                if rel not in listed_agent_files:
                    errors.append(f"orphan agent file (not in manifest): {rel}")
    skills_dir = os.path.join(root, ".claude", "skills")
    if os.path.isdir(skills_dir):
        for name in os.listdir(skills_dir):
            sp = os.path.join(skills_dir, name, "SKILL.md")
            if os.path.isfile(sp):
                rel = os.path.normpath(os.path.join(".claude", "skills", name, "SKILL.md"))
                # the orchestrator is a skill too; allow it to be listed as orchestrator
                if rel not in listed_skill_files and (not orch or os.path.normpath(orch) != rel):
                    errors.append(f"orphan skill file (not in manifest): {rel}")


def crossref_check(m, errors):
    agent_names = {a.get("name") for a in m.get("agents", [])}
    skill_names = {s.get("name") for s in m.get("skills", [])}
    for a in m.get("agents", []):
        for sk in a.get("skills", []):
            if sk not in skill_names:
                errors.append(f"crossref: agent '{a.get('name')}' uses unknown skill '{sk}'")
    for s in m.get("skills", []):
        for u in s.get("usedBy", []):
            if u not in agent_names:
                errors.append(f"crossref: skill '{s.get('name')}' usedBy unknown agent '{u}'")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    m, path = load_manifest(root)
    errors = []
    schema_check(m, errors)
    disk_check(root, m, errors)
    crossref_check(m, errors)

    if errors:
        print(f"DRIFT — {len(errors)} issue(s) in {path}:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    n_a, n_s = len(m.get("agents", [])), len(m.get("skills", []))
    print(f"OK — manifest matches disk ({n_a} agents, {n_s} skills, mode={m.get('executionMode')}).")
    sys.exit(0)


if __name__ == "__main__":
    main()
