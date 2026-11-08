<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
</required_context_rules>

# EPIC 163 - Phase 3: Immutable `ExecutionRecord` State Transitions & Zero Redundant Re-Validation (`QGR028`)

## 1. Executive Summary & Architectural Directives

This phase eliminates all 22 `QGR028` violations across the 10 files in `RESIDUAL_FUTURE_PHASE_QGR028_FILES` and deletes `RESIDUAL_FUTURE_PHASE_QGR028_FILES` from `@[scripts/_ast_guardrails.py]`.

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/domain/execution.py#L250-L521]`, `@[backend_v2/workers/execution_worker.py#_mark_execution_failed]`, `@[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]`, `@[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase]`, `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]` | Copying `dict(record.step_states)` or `dict(record.profile_syntheses)` into mutable local dictionaries for in-place mutation and calling `.model_validate()` on already-typed worker state objects (`QGR028`). | Define pure immutable transition helper methods on `ExecutionRecord` (`with_updated_step_state`, `with_updated_profile_synthesis`, `with_cleared_profile_syntheses`) encapsulating `model_copy(update=...)` transitions and invoke them across all workers. | Zero intermediate mutable dictionary clones in worker transition loops. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/execution.py backend_v2/workers/ --test --ast-strict` |
| `@[backend_v2/hooks/atom_flattening.py#atom_flattening_hook]`, `@[backend_v2/hooks/scoring/falsifier_hook.py#falsifier_adversarial_hook]`, `@[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook]`, `@[backend_v2/hooks/scoring/normalization_hook.py#score_normalization_hook]`, `@[backend_v2/services/execution/ingress_service.py#L377-L783]`, `@[backend_v2/services/orchestrator/strategies/logic.py#L38-L241]`, `@[backend_v2/services/orchestrator/synthesis_distiller.py#L173-L389]`, `@[scripts/_ast_guardrails.py]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` | Calling redundant `.model_validate()` on already-hydrated Pydantic V2 DTO instances across hooks, ingress, logic strategy, and synthesis distiller (`QGR028`). | Consume and pass typed Pydantic V2 DTO instances directly via dot notation (`the_duct_tape_ban` and `frozen_state_mutability`) and delete `RESIDUAL_FUTURE_PHASE_QGR028_FILES` from `@[scripts/_ast_guardrails.py]`. | Zero redundant re-hydration loops inside post-processing hooks or orchestrator services. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/hooks/ backend_v2/services/execution/ingress_service.py backend_v2/services/orchestrator/ scripts/_ast_guardrails.py --test --ast-strict` |

---

## 2. Execution Protocol

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that all 10 files in `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]` are targeted in this plan and that immutable `ExecutionRecord` transition methods preserve `ConfigDict(extra="forbid", strict=True, frozen=True)` semantics.</action>
  </step>

  <dod_checklist>
    <item>Immutable transition helpers (`with_updated_step_state`, `with_updated_profile_synthesis`, `with_cleared_profile_syntheses`) exist on `ExecutionRecord` in `@[backend_v2/models/domain/execution.py#L394-L411]`.</item>
    <item>All `dict(record.step_states)` and `dict(record.profile_syntheses)` copies and redundant `.model_validate()` calls across workers, hooks, and services are eliminated.</item>
    <item>`RESIDUAL_FUTURE_PHASE_QGR028_FILES` is deleted from `@[scripts/_ast_guardrails.py]`.</item>
  </dod_checklist>

  <anti_targets>
    <file>@[backend_v2/seed/seed_data.json]</file>
    <file>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]</file>
  </anti_targets>

  <touched_artifacts>
    <file>@[backend_v2/models/domain/execution.py#L250-L521]</file>
    <file>@[backend_v2/hooks/atom_flattening.py#atom_flattening_hook]</file>
    <file>@[backend_v2/hooks/scoring/falsifier_hook.py#falsifier_adversarial_hook]</file>
    <file>@[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook]</file>
    <file>@[backend_v2/hooks/scoring/normalization_hook.py#score_normalization_hook]</file>
    <file>@[backend_v2/services/execution/ingress_service.py#L377-L783]</file>
    <file>@[backend_v2/services/orchestrator/strategies/logic.py#L38-L241]</file>
    <file>@[backend_v2/services/orchestrator/synthesis_distiller.py#L173-L389]</file>
    <file>@[backend_v2/workers/execution_worker.py#_mark_execution_failed]</file>
    <file>@[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]</file>
    <file>@[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase]</file>
    <file>@[scripts/_ast_guardrails.py]</file>
    <file>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</file>
    <file>@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]</file>
    <file>@[backend_v2/tests/unit/workers/test_synthesis_worker.py]</file>
  </touched_artifacts>

  <step id="3.1" name="Immutable ExecutionRecord Transition Helpers &amp; Worker State Updates">
    <context>
      `@[backend_v2/workers/execution_worker.py#_mark_execution_failed]`, `@[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]`, and `@[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase]` unpack `record.step_states` and `record.profile_syntheses` into mutable dictionaries (`dict(record.step_states)`), triggering `QGR028`.
    </context>
    <demolish>
      Remove `dict(record.step_states)`, `dict(latest_record.step_states)`, `dict(record.profile_syntheses)`, `dict(latest_record.profile_syntheses)`, and redundant `.model_validate()` calls in `@[backend_v2/workers/execution_worker.py#_mark_execution_failed]`, `@[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]`, and `@[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase]`.
    </demolish>
    <action>
      1. `[MODIFY]` `@[backend_v2/models/domain/execution.py#L250-L521]`: Define pure immutable transition helper methods on `ExecutionRecord` (`with_updated_step_state`, `with_updated_profile_synthesis`, `with_cleared_profile_syntheses`) encapsulating `model_copy(update=...)` transitions.
      2. `[MODIFY]` `@[backend_v2/workers/execution_worker.py#_mark_execution_failed]`: Replace `dict(record.step_states)` mutation with `ExecutionRecord` immutable transition helper.
      3. `[MODIFY]` `@[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]`: Replace `dict(latest_record.profile_syntheses)` and `dict(latest_record.step_states)` copies with `ExecutionRecord` immutable transition helpers.
      4. `[MODIFY]` `@[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase]`: Replace all 5 `dict(record.step_states)` / `dict(record.profile_syntheses)` and redundant `.model_validate()` calls with `ExecutionRecord` immutable transition helpers.
      5. `[MODIFY]` `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]` and `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]`: Update unit tests to verify immutable `ExecutionRecord` transition helper behavior across positive, negative, and boundary cases.
    </action>
    <constraint>
      All transition helpers on `ExecutionRecord` must return `Self` (`from typing import Self`) and preserve complete immutability without mutating the source `ExecutionRecord` instance.
    </constraint>
    <test_contracts>
      <contract name="test_execution_record_with_updated_step_state_returns_new_frozen_instance" category="positive">
        <input>Valid `ExecutionRecord` instance and a new `StepExecutionState` entry for `stp_01965b88000070008000000000000001`.</input>
        <expected>Returns a new `ExecutionRecord` containing the updated step state while leaving the original `ExecutionRecord.step_states` unchanged.</expected>
      </contract>
      <contract name="test_execution_record_with_updated_profile_synthesis_preserves_existing_profiles" category="boundary">
        <input>`ExecutionRecord` with 1 existing `RenderedSynthesisCache` entry and a second profile synthesis update (`prf_01965b88000070008000000000000002`).</input>
        <expected>Returns a new `ExecutionRecord` containing both profile synthesis entries and updated `step_states` when passed.</expected>
      </contract>
      <contract name="test_execution_record_with_cleared_profile_syntheses_empties_cache" category="negative">
        <input>`ExecutionRecord` populated with stale `profile_syntheses` entries.</input>
        <expected>`with_cleared_profile_syntheses()` returns a new `ExecutionRecord` with `profile_syntheses == {}`.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/execution.py backend_v2/workers/ --test --ast-strict`
    </validation_gate>
  </step>

  <step id="3.2" name="Eradicate Redundant .model_validate() Calls in Hooks &amp; Services and Delete RESIDUAL_FUTURE_PHASE_QGR028_FILES">
    <context>
      7 hook and service files invoke `.model_validate()` on objects that are already validated Pydantic V2 DTO instances (`QGR028`).
    </context>
    <demolish>
      Delete all redundant `.model_validate()` calls on typed DTOs in `@[backend_v2/hooks/atom_flattening.py#atom_flattening_hook]`, `@[backend_v2/hooks/scoring/falsifier_hook.py#falsifier_adversarial_hook]`, `@[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook]`, `@[backend_v2/hooks/scoring/normalization_hook.py#score_normalization_hook]`, `@[backend_v2/services/execution/ingress_service.py#L377-L783]`, `@[backend_v2/services/orchestrator/strategies/logic.py#L38-L241]`, and `@[backend_v2/services/orchestrator/synthesis_distiller.py#L173-L389]`, and delete `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]`.
    </demolish>
    <action>
      1. `[MODIFY]` `@[backend_v2/hooks/atom_flattening.py#atom_flattening_hook]`: Replace redundant `.model_validate()` on typed DTOs with direct typed instance access.
      2. `[MODIFY]` `@[backend_v2/hooks/scoring/falsifier_hook.py#falsifier_adversarial_hook]`: Replace redundant `.model_validate()` with direct typed DTO access.
      3. `[MODIFY]` `@[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook]`: Replace both redundant `.model_validate()` calls with direct typed DTO access.
      4. `[MODIFY]` `@[backend_v2/hooks/scoring/normalization_hook.py#score_normalization_hook]`: Replace both redundant `.model_validate()` calls with direct typed DTO access.
      5. `[MODIFY]` `@[backend_v2/services/execution/ingress_service.py#L377-L783]`: Replace 4 redundant `.model_validate()` calls on typed ingress/context models with direct typed instances.
      6. `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/logic.py#L38-L241]`: Replace redundant `.model_validate()` call with direct typed DTO handling.
      7. `[MODIFY]` `@[backend_v2/services/orchestrator/synthesis_distiller.py#L173-L389]`: Replace both redundant `.model_validate()` calls with direct typed DTO access.
      8. `[MODIFY]` `@[scripts/_ast_guardrails.py]`: Delete `RESIDUAL_FUTURE_PHASE_QGR028_FILES`.
      9. `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`: Assert that `RESIDUAL_FUTURE_PHASE_QGR028_FILES` no longer exists in `@[scripts/_ast_guardrails.py]` and that `QGR028` enforces zero exemptions across the entire repository.
    </action>
    <constraint>
      Never introduce `isinstance(..., Mapping)` or duck-typing checks when removing `.model_validate()`; rely strictly on static Pydantic V2 type contracts.
    </constraint>
    <test_contracts>
      <contract name="test_qgr028_zero_residual_exemption_set" category="positive">
        <input>Inspect `@[scripts/_ast_guardrails.py]` and run `QGR028` across `backend_v2/`.</input>
        <expected>`hasattr(_ast_guardrails, "RESIDUAL_FUTURE_PHASE_QGR028_FILES")` is `False` and `QGR028` reports 0 violations.</expected>
      </contract>
      <contract name="test_qgr028_flags_dict_record_step_states_unpacking" category="negative">
        <input>Synthetic AST snippet containing `states = dict(record.step_states)` inside a worker module.</input>
        <expected>`QGR028` raises a fatal AST guardrail violation.</expected>
      </contract>
      <contract name="test_qgr028_flags_redundant_model_validate_on_typed_dto" category="boundary">
        <input>Synthetic AST snippet invoking `MyDTO.model_validate(already_typed_dto)` inside a service or hook module.</input>
        <expected>`QGR028` raises a fatal AST guardrail violation.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/hooks/ backend_v2/workers/ backend_v2/services/execution/ingress_service.py backend_v2/services/orchestrator/ scripts/_ast_guardrails.py --test --ast-strict`
    </validation_gate>
  </step>
</execution_protocol>
```
