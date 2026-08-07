<system_prompt>
  <objective>Generate Implementation Plan for Phase 5: Frontend Flutter UI Enum Synchronization</objective>
  <context>
    Epic: @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix.md]
  </context>
  
  <execution_protocol level="1_planner">
    <step id="5.0" name="STRATEGIC ALIGNMENT CHECK">
      <action>Verify Phase 4 is complete and backend is stable.</action>
    </step>
    <step id="5.1" name="FLUTTER AUDIT LOOP">
      <action>Run `uv run python scripts/flutter_audit_loop.py client_app_v2 --build` to ensure Enum parity. Update Dart enums in `@[c:\src\quorum\client_app_v2\lib\core\models\enums.dart]` if new enum states were introduced.</action>
    </step>
    <validation_gate>
      Run: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`
      Assert: Build succeeds with zero errors.
    </validation_gate>
  </execution_protocol>
</system_prompt>
