# Phase 6: Verification & E2E Integration Gate

**Objective:** Execute the global backend and frontend audit loops, and run the mandatory Final E2E REST API Verification Gate.
**Source:** @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix.md#L121-L123]

**Target Files:**
- `@[c:\src\quorum\backend_v2\tests\integration\test_integration_real_llm.py]`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    - Python backend audit loop passes with zero errors.
    - Flutter audit loop passes with zero errors.
    - Final E2E REST API tests pass successfully.
  </dod_checklist>

  <required_context_rules>
    - @[c:\src\quorum\.agents\rules\00-antigravity-core.md]
    - @[c:\src\quorum\.agents\rules\01-python-backend.md]
    - @[c:\src\quorum\.agents\rules\04_directory_reference.md]
    - @[c:\src\quorum\.agents\rules\02_flutter_desktop.md]
    - @[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]
  </required_context_rules>

  <anti_targets>
    - Do NOT write new tests or feature code during this phase unless fixing a breaking audit error.
    - Do NOT deploy the application.
  </anti_targets>

  <step id="1" name="GLOBAL PYTHON AUDIT LOOP">
    <action>Run the global Python backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
    <constraint>All Pytest unit tests, MyPy typing checks, and Ruff formatting must pass perfectly. Fix any trailing errors.</constraint>
  </step>

  <step id="2" name="GLOBAL FLUTTER AUDIT LOOP">
    <action>Run the global Flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.</action>
    <constraint>Freezed models must build successfully and Dart analysis must pass without errors. Fix any SDUI drift issues.</constraint>
  </step>

  <step id="3" name="MANDATORY FINAL E2E REST API VERIFICATION GATE">
    <action>Run the E2E REST API Verification: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.</action>
    <constraint>If the tests fail, you MUST debug the integration layer. The Epic is not complete until full E2E viability is proven.</constraint>
  </step>

  <validation_gate>
    - Verify that all three shell commands returned an exit code of 0.
  </validation_gate>
</execution_protocol>
```
