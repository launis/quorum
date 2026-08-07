<system_prompt>
  <objective>Generate Implementation Plan for Phase 6: Verification & E2E Integration Gate</objective>
  <context>
    Epic: @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix.md]
  </context>
  
  <execution_protocol level="1_planner">
    <step id="6.0" name="STRATEGIC ALIGNMENT CHECK">
      <action>Verify all prior phases are complete.</action>
    </step>
    <step id="6.1" name="PYTHON BACKEND AUDIT">
      <action>Execute the Python backend audit loop globally: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
    </step>
    <step id="6.2" name="FLUTTER AUDIT">
      <action>Execute the Flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.</action>
    </step>
    <validation_gate>
      Run: Integration check
      Assert: Both frontend and backend compile and tests pass.
    </validation_gate>
  </execution_protocol>
</system_prompt>
