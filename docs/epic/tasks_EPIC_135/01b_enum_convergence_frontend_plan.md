# Phase 1B: Enum Convergence & Status Mapping (Frontend)

**Overview:** Establish the unified status vocabulary in the Flutter frontend, mirroring backend changes.
**Target Files:**
- `@[c:\src\quorum\client_app_v2\lib\core\models\enums.dart]`
- `@[c:\src\quorum\client_app_v2\lib\features\execution\models\matrix_scorecard_dto.dart]`
- `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\atom_matrix_table_widget.dart]`
- `@[c:\src\quorum\client_app_v2\test\features\execution\views\widgets\atom_matrix_table_widget_test.dart]`
- `@[c:\src\quorum\client_app_v2\test\features\execution\models\matrix_scorecard_dto_test.dart]`
- `@[c:\src\quorum\client_app_v2\test\features\execution\matrix_blocks_snapshot_test.dart]`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    - [ ] `AtomEvaluationStatus` to `ExecutionStatus` migration in Dart frontend.
    - [ ] Freezed model generation successfully executed.
    - [ ] Frontend tests pass with the new Enum.
  </dod_checklist>

  <required_context_rules>
    - `@[c:\src\quorum\.agents\rules\00-antigravity-core.md]`
    - `@[c:\src\quorum\.agents\rules\02_flutter_desktop.md]`
    - `@[c:\src\quorum\.agents\rules\04_directory_reference.md]`
    - `@[c:\src\quorum\docs\epic\EPIC_135_Schema_Convergence_Architecture.md]`
  </required_context_rules>

  <anti_targets>
    - DO NOT modify Python `.py` files.
    - DO NOT remove `visualIntent` logic from `matrix_scorecard_dto.dart`.
  </anti_targets>

  <step id="1" name="UPDATE DART ENUMS AND MODELS">
    <action>In `@[c:\src\quorum\client_app_v2\lib\core\models\enums.dart]`, ensure `ExecutionStatus` matches the Python equivalent, and remove `AtomEvaluationStatus` if it exists independently.</action>
    <action>In `@[c:\src\quorum\client_app_v2\lib\features\execution\models\matrix_scorecard_dto.dart]`, update `ScorecardAtomDto.status` from `AtomEvaluationStatus` to `ExecutionStatus`.</action>
    <action>In `@[c:\src\quorum\client_app_v2\lib\features\execution\models\matrix_scorecard_dto.dart]`, update `HumanOverrideDto.newStatus` from `String` to `ExecutionStatus`.</action>
    <action>Run the flutter build runner to regenerate `.freezed.dart` and `.g.dart` files.</action>
    <constraint invariant="cross_language_enum_parity">Frontend enums must strictly match backend Pydantic Literals.</constraint>
  </step>

  <step id="1.5" name="UPDATE UI WIDGET LOGIC">
    <action>In `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\atom_matrix_table_widget.dart]`, update the `isPass` boolean logic. Replace string comparisons (specifically 'PASS' and 'CONTESTED') and enum comparisons (`AtomEvaluationStatus.pass`/`contested`) with strict typed enum checks against `ExecutionStatus.passed`.</action>
    <demolish>REMOVE: `atom.humanOverride!.newStatus.toUpperCase() == 'PASS'` and `AtomEvaluationStatus.contested`. REPLACE WITH: `atom.humanOverride!.newStatus == ExecutionStatus.passed` and `atom.status == ExecutionStatus.passed`.</demolish>
  </step>

  <step id="2" name="UPDATE FRONTEND TESTS">
    <action>Update `@[c:\src\quorum\client_app_v2\test\features\execution\views\widgets\atom_matrix_table_widget_test.dart]`, `@[c:\src\quorum\client_app_v2\test\features\execution\models\matrix_scorecard_dto_test.dart]`, and `@[c:\src\quorum\client_app_v2\test\features\execution\matrix_blocks_snapshot_test.dart]` to use `ExecutionStatus` instead of `AtomEvaluationStatus`.</action>
    <demolish>REMOVE: AtomEvaluationStatus references. REPLACE WITH: ExecutionStatus.</demolish>
  </step>

  <test_contracts>
    <test name="test_matrix_scorecard_dto_deserialization" category="positive">
      <input>JSON payload with ExecutionStatus.PASSED and visualIntent warning</input>
      <expected>returns parsed ScorecardAtomDTO</expected>
    </test>
    <test name="test_matrix_scorecard_dto_invalid_enum_throws" category="negative">
      <input>JSON payload with invalid status "INVALID_STATUS"</input>
      <expected>throws FormatException / TypeError during fromJson</expected>
    </test>
    <test name="test_human_override_dto_invalid_enum_throws" category="negative">
      <input>JSON payload for HumanOverrideDto with invalid new_status "SUPER_PASS"</input>
      <expected>throws FormatException / TypeError during fromJson (testing strict enum parsing)</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart --build`</action>
    <action>Run flutter tests for the modified test files.</action>
  </validation_gate>
</execution_protocol>
```
