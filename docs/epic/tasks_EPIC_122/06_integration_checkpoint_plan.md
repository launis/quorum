# Integration Checkpoint: Full-Stack Validation

Source: @[c:\src\quorum\docs\epic\EPIC_122_legacy_parity_output_profile.md#L245-L246]

## Objective
Before proceeding to the Post-Implementation Gates, a full end-to-end (E2E) validation is required to verify pixel-perfect parity between the generated PDF (via Jinja) and the Flutter SDUI rendering for the modified OutputProfile.

## Target Files
- CONTEXT (Read-Only): `@[c:\src\quorum\backend_v2\tests\integration\test_integration_real_llm.py]`

## Execution Protocol

```xml
<execution_protocol level="2_execute">
  <step id="5_1" name="Full-Stack Integration Verification">
    <action>Run the Backend and Frontend on a simulated `full_context` DAG payload to verify the pipeline.</action>
    <action>Assert that all 3 layout arrays (`summary`, `matrix`, `penalties_block`) are properly hydrated in the backend response.</action>
    <action>Use the `RUN_LIVE_E2E="true"` test flag for API validation against real endpoints to guarantee the OutputProfile modifications are robust against real data.</action>
    <action>Execute: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`</action>
    <action>Record the output logs and verify the end-to-end trace completes successfully without SDUI layout hydration errors.</action>
  </step>
</execution_protocol>
```
