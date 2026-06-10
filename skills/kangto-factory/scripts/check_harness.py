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
    1  drift found (schema violations, missing files, orphan files,
       or broken cross-references)
    2  manifest missing or invalid JSON

Enums and required fields are read from the bundled assets/harness.schema.json
so the schema stays the single source of truth; the fallback constants below
exist only so a standalone copy of this script keeps working.
No third-party dependencies.
"""
import json
import os
import sys

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           os.pardir, "assets", "harness.schema.json")

# Used only when the bundled schema is missing/unreadable (standalone copy).
FALLBACK_RULES = {
    "required_top": ["name", "version", "domain", "executionMode", "pattern",
                     "orchestrator", "agents", "skills", "changelog"],
    "exec_modes": {"team", "subagent", "hybrid"},
    "patterns": {"pipeline", "fan-out-fan-in", "expert-pool",
                 "producer-reviewer", "supervisor", "hierarchical", "composite"},
    "agent_types": {"general-purpose", "Explore", "Plan", "custom"},
    "models": {"opus", "sonnet", "haiku"},
    "agent_required": ["name", "type", "model", "file", "role"],
    "skill_required": ["name", "file", "usedBy"],
    "changelog_required": ["date", "change", "target", "reason"],
}


def load_rules() -> dict:
    """Derive validation rules from harness.schema.json (single source of truth)."""
    try:
        with open(SCHEMA_PATH, encoding="utf-8") as fh:
            schema = json.load(fh)
        props = schema["properties"]
        agent_items = props["agents"]["items"]
        return {
            "required_top": list(schema["required"]),
            "exec_modes": set(props["executionMode"]["enum"]),
            "patterns": set(props["pattern"]["enum"]),
            "agent_types": set(agent_items["properties"]["type"]["enum"]),
            "models": set(agent_items["properties"]["model"]["enum"]),
            "agent_required": list(agent_items["required"]),
            "skill_required": list(props["skills"]["items"]["required"]),
            "changelog_required": list(props["changelog"]["items"]["required"]),
        }
    except (OSError, ValueError, KeyError, TypeError):
        return FALLBACK_RULES


def load_manifest(root: str) -> tuple:
    path = os.path.join(root, ".claude", "harness.json")
    if not os.path.isfile(path):
        print(f"FATAL: no manifest at {path}")
        sys.exit(2)
    try:
        with open(path, encoding="utf-8") as fh:
            manifest = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"FATAL: {path} is not valid JSON: {exc}")
        sys.exit(2)
    if not isinstance(manifest, dict):
        print(f"FATAL: {path} must contain a JSON object, got {type(manifest).__name__}")
        sys.exit(2)
    return manifest, path


def object_entries(manifest: dict, key: str, errors: list) -> list:
    """Return the dict entries of manifest[key]; report anything else instead of crashing."""
    value = manifest.get(key, [])
    if not isinstance(value, list):
        errors.append(f"schema: '{key}' must be an array")
        return []
    entries = []
    for i, item in enumerate(value):
        if isinstance(item, dict):
            entries.append(item)
        else:
            errors.append(f"schema: {key}[{i}] must be an object, got {type(item).__name__}")
    return entries


def schema_check(manifest: dict, agents: list, skills: list, changelog: list,
                 rules: dict, errors: list) -> None:
    for k in rules["required_top"]:
        if k not in manifest:
            errors.append(f"schema: missing required field '{k}'")
    if manifest.get("executionMode") not in rules["exec_modes"]:
        errors.append(f"schema: executionMode '{manifest.get('executionMode')}' "
                      f"not in {sorted(rules['exec_modes'])}")
    if manifest.get("pattern") not in rules["patterns"]:
        errors.append(f"schema: pattern '{manifest.get('pattern')}' "
                      f"not in {sorted(rules['patterns'])}")
    for a in agents:
        label = a.get("name", "<unnamed>")
        for k in rules["agent_required"]:
            if k not in a:
                errors.append(f"schema: agent '{label}' missing required field '{k}'")
        if a.get("type") not in rules["agent_types"]:
            errors.append(f"schema: agent '{label}' type '{a.get('type')}' invalid")
        if a.get("model") not in rules["models"]:
            errors.append(f"schema: agent '{label}' model '{a.get('model')}' invalid")
    for s in skills:
        label = s.get("name", "<unnamed>")
        for k in rules["skill_required"]:
            if k not in s:
                errors.append(f"schema: skill '{label}' missing required field '{k}'")
    for i, c in enumerate(changelog):
        for k in rules["changelog_required"]:
            if k not in c:
                errors.append(f"schema: changelog[{i}] missing required field '{k}'")


def disk_check(root: str, manifest: dict, agents: list, skills: list,
               errors: list) -> None:
    # Every manifest file must exist on disk.
    listed_agent_files, listed_skill_files = set(), set()
    for a in agents:
        f = a.get("file")
        if isinstance(f, str) and f:
            listed_agent_files.add(os.path.normpath(f))
            if not os.path.isfile(os.path.join(root, f)):
                errors.append(f"missing file: agent '{a.get('name')}' -> {f}")
        elif "file" in a:
            errors.append(f"schema: agent '{a.get('name')}' field 'file' must be a non-empty string")
    for s in skills:
        f = s.get("file")
        if isinstance(f, str) and f:
            listed_skill_files.add(os.path.normpath(f))
            if not os.path.isfile(os.path.join(root, f)):
                errors.append(f"missing file: skill '{s.get('name')}' -> {f}")
        elif "file" in s:
            errors.append(f"schema: skill '{s.get('name')}' field 'file' must be a non-empty string")
    orch = manifest.get("orchestrator")
    if isinstance(orch, str) and orch:
        orch_norm = os.path.normpath(orch)
        if not os.path.isfile(os.path.join(root, orch_norm)):
            errors.append(f"missing file: orchestrator -> {orch}")
    else:
        orch_norm = None
        if "orchestrator" in manifest:
            errors.append("schema: 'orchestrator' must be a non-empty string")

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
                if rel not in listed_skill_files and orch_norm != rel:
                    errors.append(f"orphan skill file (not in manifest): {rel}")


def crossref_check(agents: list, skills: list, errors: list) -> None:
    agent_names = {a.get("name") for a in agents}
    skill_names = {s.get("name") for s in skills}
    for a in agents:
        used = a.get("skills", [])
        if not isinstance(used, list):
            errors.append(f"schema: agent '{a.get('name')}' field 'skills' must be an array")
            continue
        for sk in used:
            if sk not in skill_names:
                errors.append(f"crossref: agent '{a.get('name')}' uses unknown skill '{sk}'")
    for s in skills:
        used_by = s.get("usedBy", [])
        if not isinstance(used_by, list):
            errors.append(f"schema: skill '{s.get('name')}' field 'usedBy' must be an array")
            continue
        for u in used_by:
            if u not in agent_names:
                errors.append(f"crossref: skill '{s.get('name')}' usedBy unknown agent '{u}'")


def main() -> None:
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    manifest, path = load_manifest(root)
    rules = load_rules()
    errors = []
    agents = object_entries(manifest, "agents", errors)
    skills = object_entries(manifest, "skills", errors)
    changelog = object_entries(manifest, "changelog", errors)
    schema_check(manifest, agents, skills, changelog, rules, errors)
    disk_check(root, manifest, agents, skills, errors)
    crossref_check(agents, skills, errors)

    if errors:
        print(f"DRIFT — {len(errors)} issue(s) in {path}:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(f"OK — manifest matches disk ({len(agents)} agents, {len(skills)} skills, "
          f"mode={manifest.get('executionMode')}).")
    sys.exit(0)


if __name__ == "__main__":
    main()
