# Phase 2: Producer Refactoring & Type Strictness

**Overview:** Update the producers to use the new enums and types, while preserving the presentation flow layer.
**Target Files:**
- `@[c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py]`
- `@[c:\src\quorum\backend_v2\services\matrix_domain_parser.py]`
- `@[c:\src\quorum\backend_v2\services\orchestrator\matrix_reducer.py]`
- `@[c:\src\quorum\backend_v2\tests\integration\test_lazy_llm_simulation.py]`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    - [ ] `anchor_validation_service.py` method `process_atom_evaluation` has `Any` type hints removed and correctly uses `AtomResultDTO`.
    - [ ] `matrix_domain_parser.py` uses `ExecutionStatus` instead of `AtomEvaluationStatus`.
    - [ ] `matrix_reducer.py` uses `ExecutionStatus.PASSED`.
    - [ ] Test `test_lazy_llm_simulation.py` constructs `AtomResultDTO`.
  </dod_checklist>

  <required_context_rules>
    - `@[c:\src\quorum\.agents\rules\00-antigravity-core.md]`
    - `@[c:\src\quorum\.agents\rules\01-python-backend.md]`
    - `@[c:\src\quorum\.agents\rules\04_directory_reference.md]`
    - `@[c:\src\quorum\docs\epic\EPIC_135_Schema_Convergence_Architecture.md]`
  </required_context_rules>

  <anti_targets>
    - DO NOT replace `ScorecardAtomDTO` with `AtomResultDTO` in `matrix_domain_parser.py`.
    - DO NOT modify `backend_v2/hooks/scoring.py` yet.
  </anti_targets>

  <step id="1" name="UPDATE ANCHOR VALIDATION SERVICE">
    <action>In `@[c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py]`, update `process_atom_evaluation` to accept `atom: AtomResultDTO`, type `source_documents`, and return `AtomResultDTO`.</action>
    <demolish>REMOVE: `atom: Any` and `-> Any` type hints. REPLACE WITH: `atom: AtomResultDTO` and `-> AtomResultDTO`.</demolish>
  </step>

  <step id="2" name="UPDATE MATRIX PRODUCERS">
    <action>In `@[c:\src\quorum\backend_v2\services\matrix_domain_parser.py]`, replace `AtomEvaluationStatus.FAIL` usages with `ExecutionStatus.FAILED`.</action>
    <action>In `@[c:\src\quorum\backend_v2\services\orchestrator\matrix_reducer.py]`, replace `AtomEvaluationStatus.PASS` with `ExecutionStatus.PASSED`.</action>
  </step>

  <step id="3" name="UPDATE LAZY LLM TEST">
    <action>In `@[c:\src\quorum\backend_v2\tests\integration\test_lazy_llm_simulation.py]`, modify the construction of dummy/fixture results to use `AtomResultDTO` instead of `AtomEvaluationItemDTO`.</action>
  </step>

  <test_contracts>
    <test name="test_anchor_validation_process_atom_result" category="positive">
      <input>AtomResultDTO with quotes</input>
      <expected>returns validated AtomResultDTO (typing matches)</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loops: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test`</action>
    <action>Run backend audit loops: `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test`</action>
    <action>Run backend audit loops: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/matrix_reducer.py --test`</action>
    <action>Run pytest: `uv run pytest backend_v2/tests/integration/test_lazy_llm_simulation.py`</action>
  </validation_gate>
</execution_protocol>
```
