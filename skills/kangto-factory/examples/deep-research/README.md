# Example harness: deep-research

A real, end-to-end harness produced by `kangto-factory` — not pseudocode. It doubles as the worked example referenced by the factory.

- **Pattern:** fan-out/fan-in · **Mode:** agent team
- **Agents:** `web-scout` (sonnet), `academic-scout` (opus), `synthesizer` (opus, custom)
- **Skills:** web-search, paper-search, cross-validate, report-write + the `research-orchestrator`
- **Manifest:** `.claude/harness.json` is the single canonical record

This directory is laid out as a project root. Verify the harness is internally coherent (manifest ↔ disk, cross-references) with the bundled drift checker:

```shell
python3 ../../scripts/check_harness.py .
# OK — manifest matches disk (3 agents, 4 skills, mode=team).
```

It shows the model-selection mapping in practice: `sonnet` for structured web gathering, `opus` for academic strength-judgment and synthesis.
