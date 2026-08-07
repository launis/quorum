<system_prompt>
  <objective>Generate Implementation Plan for Phase 2: DTO Extraction & Strangler Fig Proxy</objective>
  <context>
    Epic: @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix.md]
  </context>
  
  <execution_protocol level="1_planner">
    <step id="2.0" name="STRATEGIC ALIGNMENT CHECK">
      <action>Verify Phase 1 completed successfully and test coverage >80% with no skipped tests in `test_lightweight_matrix.py`.</action>
    </step>
    <step id="2.1" name="CREATE NEW ATOM EVALUATION DTO FILE">
      <action>Create a new file `@[c:\src\quorum\backend_v2\models\dtos\atom_evaluation.py]`.</action>
      <action>Extract the following classes from `@[c:\src\quorum\backend_v2\models\dtos\lightweight_matrix.py]` into the new file in exact dependency order: `ReasoningStepDTO` (L287), `LightweightExtractionAtom` (L160), `MatrixEvaluationItemDTO` (L300), `AtomEvaluationItemDTO` (L316), `ReducedAtomDTO` (L711), `LightweightMatrixDTO` (L721).</action>
      <action>Copy necessary imports (like `BaseModel`, `Field`, `ConfigDict`, `PrivateAttr`) to the new file.</action>
      <contract_freeze>
        DO NOT alter any type hints, `@model_validator` logic, or properties during this physical extraction. Maintain `ConfigDict(strict=True, extra='forbid')`.
      </contract_freeze>
    </step>
    <step id="2.2" name="IMPLEMENT STRANGLER FIG RE-EXPORTS">
      <action>In `@[c:\src\quorum\backend_v2\models\dtos\lightweight_matrix.py]`, add re-export imports for ALL 6 migrated classes to prevent breaking the 23+ consumers.</action>
      <action>Add: `from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO, LightweightExtractionAtom, MatrixEvaluationItemDTO, AtomEvaluationItemDTO, ReducedAtomDTO, LightweightMatrixDTO`.</action>
    </step>
    <validation_gate>
      Run: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
      Assert: All tests pass. Zero import errors globally.
    </validation_gate>
    <anti_targets>
      DO NOT remove duck-typing, logic, or aliases yet. Phase 2 is strictly a physical file move with re-exports.
    </anti_targets>
  </execution_protocol>
</system_prompt>
