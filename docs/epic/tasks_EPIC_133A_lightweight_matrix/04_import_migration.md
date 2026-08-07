<system_prompt>
  <objective>Generate Implementation Plan for Phase 4: Import Migration (Batched Strangler Fig Sunset)</objective>
  <context>
    Epic: @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix.md]
  </context>
  
  <execution_protocol level="1_planner">
    <step id="4.0" name="STRATEGIC ALIGNMENT CHECK">
      <action>Verify Phase 3 completed successfully and backend tests pass.</action>
    </step>
    <step id="4.1" name="UPDATE IMPORT PATHS">
      <action>Update imports in all 23+ consumer files listed in the Epic in batches of maximum 5 files. Change `from backend_v2.models.dtos.lightweight_matrix import X` to `from backend_v2.models.dtos.atom_evaluation import X`.</action>
    </step>
    <step id="4.2" name="REMOVE STRANGLER FIG EXPORTS">
      <action>In `@[c:\src\quorum\backend_v2\models\dtos\lightweight_matrix.py]`, delete the re-exports for the 6 migrated classes.</action>
    </step>
    <step id="4.3" name="GLOBAL AUDIT">
      <action>Run the global audit loop one final time to confirm zero import errors.</action>
    </step>
    <validation_gate>
      Run: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
      Assert: Zero import errors across the entire backend.
    </validation_gate>
  </execution_protocol>
</system_prompt>
