# Integration Checkpoint: Full-Stack Validation

Source: @[c:\src\quorum\docs\epic\EPIC_122_legacy_parity_output_profile.md#L245-L246]

## Objective
Before proceeding to the Post-Implementation Gates, a full end-to-end (E2E) validation is required to verify pixel-perfect parity between the generated PDF (via Jinja) and the Flutter SDUI rendering for the modified OutputProfile.

## Target Files
- CONTEXT (Read-Only): `@[c:\src\quorum\backend_v2\tests\integration\test_integration_real_llm.py]`

## Execution Protocol

```xml
<execution_protocol level="2_execute">
  <step id="5_1" name="Mocked SDUI Semantic Parity Verification (KI Mandate)">
    <action>Run the E2E SDUI Semantic Parity script to dynamically verify that the Flutter rendering perfectly matches the Jinja PDF generation using Polyfactory mock data.</action>
    <action>Execute: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`</action>
    <action>Assert that the Flutter tester acts as an E2E compilation firewall, verifying that all schema changes in the backend align with the frontend Dart Freezed classes.</action>
  </step>
  
  <step id="5_2" name="Live E2E Verification (Final Epic Verification Gate)">
    <action>Use the `RUN_LIVE_E2E="true"` test flag to perform a full live API verification against real endpoints, guaranteeing the OutputProfile modifications are robust against real backend data hydration.</action>
    <action>Execute: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`</action>
    <action>Record the output logs and verify the end-to-end trace completes successfully without SDUI layout hydration errors.</action>
  </step>
  
  <step id="5_3" name="Context Handover">
    <action>Since this execution completes the phase, explicitly instruct the user to run `/tier5-session-handover` to preserve architectural context for the next iteration.</action>
  </step>
</execution_protocol>
```
