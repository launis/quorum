# Phase 0: Seed Data & Database Prerequisite

> Source: @[c:\src\quorum\docs\epic\EPIC_111_sdui_legacy_eradication_and_ui_refactor.md#L48-L51] Phase 0

## Overview

Before any legacy field eradication begins, the local database must be cleanly re-seeded to ensure no stale execution data containing legacy fields causes spurious test failures during the refactoring process.

## Target Files

- **CONTEXT (Read-Only)**: @[c:\src\quorum\backend_v2\seed\seed_data.json]
- **CONTEXT (Read-Only)**: @[c:\src\quorum\backend_v2\seed\run_seed.py]

## Execution Steps

```xml
<execution_protocol level="2_tier2_execute">
  <step id="0.1" name="BASELINE TEST RECORDING">
    <action>Run the full backend audit loop to record the current passing test count and coverage as a [BASELINE] metric before ANY code changes.</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/ --test</command>
    <constraint invariant="fragmented_quality_gates_prevention">Record the exact passing test count and coverage percentage. This is the [BASELINE] against which all subsequent phases will be compared.</constraint>
  </step>

  <step id="0.2" name="DATABASE HARD RESET">
    <action>Re-seed the local database to ensure a clean state.</action>
    <command>uv run python backend_v2/seed/run_seed.py local</command>
    <constraint invariant="seeding_command_mandate">ALWAYS include the `local` environment argument.</constraint>
  </step>

  <step id="0.3" name="POST-SEED VERIFICATION">
    <action>Re-run the backend audit loop to confirm the seed did not break any existing tests.</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/ --test</command>
    <constraint>The test count MUST match or exceed the [BASELINE] from step 0.1.</constraint>
  </step>
</execution_protocol>
```

## Testing & Quality Gate Plan

- **Automated**: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
- **Manual**: Verify the backend server starts cleanly after re-seed.
