# Phase 1A: Enum Convergence & Status Mapping (Backend)

**Overview:** Establish the unified status vocabulary before touching any DTO models in the backend. Replaces AtomEvaluationStatus with ExecutionStatus.
**Target Files:**
- `@[c:\src\quorum\backend_v2\models\enums.py]`
- `@[c:\src\quorum\backend_v2\models\v2_core.py]`
- `@[c:\src\quorum\backend_v2\models\dtos\atom_evaluation.py]`
- `@[c:\src\quorum\backend_v2\services\matrix_domain_parser.py]`
- `@[c:\src\quorum\backend_v2\services\orchestrator\matrix_reducer.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\models\test_v2_core.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\services\test_execution.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\test_matrix_reducer.py]`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    - [x] `AtomEvaluationStatus` and `LaxAtomEvaluationStatus` usages are migrated to `ExecutionStatus` and `LaxExecutionStatus` in target files.
    - [x] `ScorecardAtomDTO.status` is updated.
    - [x] `ScorecardAtomDTO` correctly maps `contextual_override=True` to `visual_intent=VisualIntent.WARNING` for frontend parity.
    - [x] `HumanOverrideRequest` and `HumanOverrideDTO` `new_status` updated with proper Pydantic descriptions.
    - [x] `matrix_domain_parser.py` and `matrix_reducer.py` updated to use `ExecutionStatus` to preserve `ScorecardAtomDTO` build integrity.
    - [x] Test files `test_v2_core.py`, `test_execution.py`, and `test_matrix_reducer.py` updated atomically.
  </dod_checklist>

  <required_context_rules>
    - `@[c:\src\quorum\.agents\rules\00-antigravity-core.md]`
    - `@[c:\src\quorum\.agents\rules\01-python-backend.md]`
    - `@[c:\src\quorum\.agents\rules\04_directory_reference.md]`
    - `@[c:\src\quorum\docs\epic\EPIC_135_Schema_Convergence_Architecture.md]`
  </required_context_rules>

  <anti_targets>
    - DO NOT modify frontend `.dart` files in this step.
    - DO NOT modify `backend_v2/hooks/scoring.py` or `anchor_validation_service.py` yet.
    - DO NOT delete `AtomEvaluationStatus` from `enums.py` (it might still be imported by other files until phase 4).
  </anti_targets>

  <step id="1" name="MAP ENUMS AND SCORECARD ATOM">
    <action>In `@[c:\src\quorum\backend_v2\models\v2_core.py]`, update `ScorecardAtomDTO.status` from `LaxAtomEvaluationStatus | None` to `LaxExecutionStatus | None`.</action>
    <action>Update `ScorecardAtomDTO` to map `CONTESTED` state to `visual_intent=VisualIntent.WARNING` so the Flutter frontend does not lose visual distinction when parsing `PASSED` with override. Implement this via a Pydantic `@model_validator(mode="after")` that checks `if self.status == ExecutionStatus.PASSED and self.contextual_override:`.</action>
    <action>Update `HumanOverrideRequest.new_status` and `HumanOverrideDTO.new_status` to use `LaxExecutionStatus` and `ExecutionStatus` respectively, and update their `Field(description=...)` to specifically list PASSED, FAILED, SYSTEM_ERROR, omitting "e.g.".</action>
    <constraint invariant="schema_convergence_mandate">One Concept = One Schema.</constraint>
  </step>

  <step id="2" name="UPDATE REDUCED ATOM DTO">
    <action>In `@[c:\src\quorum\backend_v2\models\dtos\atom_evaluation.py]`, update `ReducedAtomDTO.status` from `LaxAtomEvaluationStatus` to `LaxExecutionStatus`.</action>
  </step>
  
  <step id="3" name="PRODUCER ATOMIC INTEGRITY (MOVED FROM PHASE 2)">
    <action>In `@[c:\src\quorum\backend_v2\services\matrix_domain_parser.py]`, replace hardcoded `AtomEvaluationStatus.FAIL` with `ExecutionStatus.FAILED` in the `ScorecardAtomDTO` constructor.</action>
    <action>In `@[c:\src\quorum\backend_v2\services\orchestrator\matrix_reducer.py]`, replace boolean check for `AtomEvaluationStatus.PASS` with `ExecutionStatus.PASSED`.</action>
    <directive>CRITICAL: These were moved from Phase 2 into Phase 1A because Pydantic `strict=True` validation on `ScorecardAtomDTO` will immediately crash if they are not updated atomically alongside Step 1.</directive>
  </step>

  <step id="4" name="UPDATE TESTS">
    <action>In `@[c:\src\quorum\backend_v2\tests\unit\models\test_v2_core.py]`, `@[c:\src\quorum\backend_v2\tests\unit\services\test_execution.py]`, and `@[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\test_matrix_reducer.py]`, replace all references to `AtomEvaluationStatus` with `ExecutionStatus` (PASS -> PASSED, FAIL -> FAILED).</action>
    <demolish>REMOVE: existing AtomEvaluationStatus enum usage at call sites in tests. REPLACE WITH: ExecutionStatus.</demolish>
  </step>

  <test_contracts>
    <test name="test_scorecard_atom_contested_warning_mapping" category="positive">
      <input>ScorecardAtomDTO created with parameters triggering the old CONTESTED state (PASSED + contextual_override)</input>
      <expected>returns visual_intent == VisualIntent.WARNING</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loops: `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py backend_v2/models/dtos/atom_evaluation.py backend_v2/services/matrix_domain_parser.py backend_v2/services/orchestrator/matrix_reducer.py --test`</action>
    <action>Run pytest: `uv run pytest backend_v2/tests/unit/models/test_v2_core.py backend_v2/tests/unit/services/test_execution.py backend_v2/tests/unit/services/orchestrator/test_matrix_reducer.py`</action>
  </validation_gate>
</execution_protocol>
```
