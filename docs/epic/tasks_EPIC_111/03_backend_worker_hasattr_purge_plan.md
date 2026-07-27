# Phase 1C: Worker hasattr() Purge & Jinja Template Migration [PLACEHOLDER]

> Source: @[c:\src\quorum\docs\epic\EPIC_111_sdui_legacy_eradication_and_ui_refactor.md#L22-L24] Phase 1

## Objective

Purge all `hasattr()` and naked dictionary checks from `worker.py` (L846-L874) and refactor slop penalty detection (L444-L458) to scan the `layouts` array. Migrate `report_template.jinja2` to iterate exclusively over `layouts`.

## Expected Target Files

1. @[c:\src\quorum\backend_v2\worker.py#L444-L458] — Slop penalty detection
2. @[c:\src\quorum\backend_v2\worker.py#L846-L874] — hasattr() / isinstance(x, dict) purge
3. @[c:\src\quorum\backend_v2\templates\report_template.jinja2] — Jinja PDF template migration

> [!NOTE]
> **PLACEHOLDER**: This plan requires detailed generation by re-invoking the Tier 1 Planner after Phase 1A and 1B are completed, based on the updated codebase state.
