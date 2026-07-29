# Phase 7: Verification & E2E Integration Gate Plan

**Objective:** Verify schema integrity, ensure complete eradication of grouped_extensions, wipe local DB, and run E2E live tests.

Source: @[c:\src\quorum\docs\epic\EPIC_123_legacy_matrix_synthesis_and_pure_sdui_parity.md#L137-L146] Phase 7: Verification & E2E Integration Gate

## Target Files (Read-Only Context)
- @[c:\src\quorum\backend_v2\services\blueprint.py]
- @[c:\src\quorum\backend_v2\services\sdui_mapper_service.py]
- @[c:\src\quorum\backend_v2\templates\report_template.jinja2]
- @[c:\src\quorum\client_app_v2\lib] (Directory for grep)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="universal_fail_fast">Any remaining reference to grouped_extensions is a BLOCKING failure.</constraint>
  <step id="1" name="COMPLETE grouped_extensions Eradication Verification">
    <action>Use `grep_search` to verify that ZERO references to `grouped_extensions` or `groupedExtensions` remain in `@[c:\src\quorum\backend_v2\services\blueprint.py]`, `@[c:\src\quorum\backend_v2\services\sdui_mapper_service.py]`, `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`, and the entire `@[c:\src\quorum\client_app_v2\lib]` directory.</action>
  </step>
  <step id="2" name="Database Wipe &amp; Seed">
    <action>Since the removal of `grouped_extensions` is a breaking schema change, wipe the local database and re-seed by executing the command: `uv run python backend_v2/seed/run_seed.py local`</action>
  </step>
  <step id="3" name="Verification Gates">
    <action>Execute `uv run python scripts/backend_audit_loop.py` to ensure schema integrity.</action>
    <action>Execute `uv run python scripts/flutter_audit_loop.py --build` to synchronize Freezed DTOs and verify widget compilation.</action>
  </step>
  <step id="4" name="Testing &amp; Quality Gate Plan">
    <action>Execute E2E Live REST API verification gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`</action>
    <action>Verify SDUI Semantic Parity (Epic 123 Core Mandate) by running the E2E Golden Fixture pipeline as per KI guidelines (generating random Polyfactory fixtures and passing to Flutter via `--dart-define=GOLDEN_PATH=...`).</action>
  </step>
</execution_protocol>
```
