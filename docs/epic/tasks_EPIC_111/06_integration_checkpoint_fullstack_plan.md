# Phase INT-FULL: Full-Stack Integration Checkpoint [PLACEHOLDER]

> Source: @[c:\src\quorum\docs\epic\EPIC_111_sdui_legacy_eradication_and_ui_refactor.md#L80-L95] DoD

## Objective

Full-stack validation after both backend and frontend legacy field eradication is complete. This verifies the report renders flawlessly in both Flutter UI and Jinja PDF without any legacy top-level variables.

## Expected Verification Commands

- `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
- `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`
- Manual: Run a test execution and verify the report renders correctly.

> [!NOTE]
> **PLACEHOLDER**: This integration checkpoint requires detailed generation by re-invoking the Tier 1 Planner after all Phase 1 sub-plans are completed.
