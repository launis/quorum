# Phase 8: Verification & E2E Integration Gate

**Overview:** Final verification phase. Run backend audit loop, frontend compilation, E2E parity check, and live integration tests. Visual comparison against `raportti 2.pdf`.
**Target Files:** @[c:\src\quorum\scripts\backend_audit_loop.py], @[c:\src\quorum\scripts\flutter_audit_loop.py], @[c:\src\quorum\scripts\run_e2e_variance_test.py], @[c:\src\quorum\backend_v2\tests\integration\test_integration_real_llm.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    <item>MyPy strict passes with zero new # type: ignore annotations.</item>
    <item>Zero bare `except Exception:` catch-alls in any adapter file.</item>
  </dod_checklist>

  <anti_targets>
    <target>Do not modify domain files in `backend_v2/services/` or `client_app_v2/lib/` during this phase unless a test failure specifically requires a bug fix.</target>
  </anti_targets>

  <step id="1" name="Execute Global Backend Audit">
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to ensure all tests pass and coverage is met.</action>
    <constraint invariant="fragmented_quality_gates_prevention">Ensure the full audit loop is executed to verify global integration state.</constraint>
  </step>

  <step id="2" name="Execute Global Frontend Audit">
    <action>Run `uv run python scripts/flutter_audit_loop.py client_app_v2 --build` to ensure the Flutter frontend compiles properly and Freezed generation passes.</action>
  </step>

  <step id="3" name="Execute E2E Parity Check">
    <action>Run `uv run python scripts/run_e2e_variance_test.py` to ensure the new SDUI outputs match the baseline expectations or have acceptable structural variances.</action>
  </step>

  <step id="4" name="Execute Live E2E Gate">
    <action>Run `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py` to prove the full pipeline works end-to-end with the actual LLM.</action>
  </step>

  <step id="5" name="Manual User Validation">
    <action>Instruct the user to manually generate the PDF and visually compare it to `raportti 2.pdf`.</action>
    <action>Instruct the user to verify the Flutter app renders the exact same structure dynamically.</action>
  </step>

  <validation_gate>
    <check>uv run python scripts/backend_audit_loop.py backend_v2 --test</check>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2 --build</check>
    <check>uv run python scripts/run_e2e_variance_test.py</check>
    <check>$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py</check>
  </validation_gate>
</execution_protocol>
```
