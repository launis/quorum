# Phase 1: Pre-Implementation Technical Debt Cleanups

**Overview:** Eradicate legacy duct-tape `ValueError` instances and dead imports in `SynthesisEngine`, eliminate dual-access context fallback chains reading `context_variables["__GLOBAL_ATOM_BLACKBOARD__"]` and `context_variables["__MATRIX_REDUCER_OUTPUT__"]` in favor of typed `ContextVariablesDTO` fields, verify zero residual reflection debt from EPIC 157, clean the `ExecutionEngine(Protocol)` base docstring, harden AST concurrency guardrail path resolution against vacuous passes, enforce `Field(ge=1)` lower bounds on all provider concurrency settings in `settings.py`, and eliminate twin blackboard fallback chains across `TDAEngine` and `LLMNodeStrategy`.

**Source:** @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md#L33-L74] Phase 1: Pre-Implementation Technical Debt Cleanups

**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L292]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L51-L292]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L363-L373]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L376-L386]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L434-L453]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L456-L489]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/base.py#L11-L31]
- `[MODIFY]` @[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L63-L67]
- `[MODIFY]` @[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L70-L81]
- `[MODIFY]` @[backend_v2/settings.py#L211]
- `[MODIFY]` @[backend_v2/tests/unit/models/test_system_concurrency_compliance.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/tda_engine.py#L37-L271]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L82-L1012]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py#L252-L278]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]
- `[MODIFY]` @[backend_v2/models/dtos/context_variables.py#L38-L203]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L292]`, `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L51-L292]` | Generic `raise ValueError(...)` at L159 and L215, dual-access context fallback chains (L71-L73, L88-L92, L98-L102), and unreachable ternary fallback (L246). | Structured `AppException(ErrorCodes.VALIDATION_FAILED)` preceded by `logger.error` (RFC 7807 dual-reporting), typed-field-only context access (`request.context.context_variables.global_atom_blackboard`, `request.context.context_variables.matrix_reducer_output`). `AliasEngine` import (L29) RETAINED: consumed at L235. | Pruned generic Python exceptions, fallback chains, and unreachable branches. | `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py -v`. Assertions verify `AppException` with `ErrorCodes.VALIDATION_FAILED.value`. |
| `@[backend_v2/services/orchestrator/engines/base.py#L11-L31]` (`ExecutionEngine`) | Concurrency and event references in Protocol docstrings. | Pure stateless `typing.Protocol` with signature `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:`. | Zero top-level concurrency management inside engine interfaces. | MyPy strict mode verification; docstring clean of concurrency references. |
| `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L63-L67]`, `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L70-L81]` | Vacuous `if not filepath.exists(): return ...` passes and cwd-relative `Path("backend_v2")` paths. | `assert filepath.exists()` anchored to `Path(__file__).resolve().parents[2]` ensuring missing guardrail targets fail loudly. | Pruned deceptive green test passes on non-existent targets. | `uv run pytest backend_v2/tests/unit/test_ast_concurrency_guardrails.py -v`. |
| `@[backend_v2/settings.py#L211]`, `@[backend_v2/tests/unit/models/test_system_concurrency_compliance.py]` | Unbounded integer settings permitting `asyncio.Semaphore(0)` deadlock and `ZeroDivisionError`, and obsolete L177 docstring. | `Field(ge=1)` on `semaphore_low_rpm_limit`, `semaphore_max_concurrency`, `semaphore_rpm_divisor`, `max_concurrent_workflows`, and `max_concurrent_llm_steps`; docstring corrected at L177; Fail-Fast `ValidationError` at settings load. | Zero new settings fields; zero shadow concurrency settings. | `uv run pytest backend_v2/tests/unit/models/test_system_concurrency_compliance.py -v` (min-1 and min partitions across all 5 settings). |
| `@[backend_v2/services/orchestrator/engines/tda_engine.py#L37-L271]` (L86-L119), `@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1012]` (L132-L148) | Dual-access and duck-typing fallback reading `ctx_vars["__GLOBAL_ATOM_BLACKBOARD__"]`, `raw_blackboard: Any`, `isinstance` branches, and `try/except`. | Direct typed attribute access `request.context.context_variables.global_atom_blackboard` and `context.context_variables.global_atom_blackboard`. | Eradicated duck-typing blackboard dictionary fallback and dead subscript branches. | `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py -v`. |

## Pre-Implementation Cleanups

1. `[CLEANUP]` Replace generic `ValueError` at L159 and L215 in `SynthesisEngine` with structured `AppException(ErrorCodes.VALIDATION_FAILED)` and structured RFC 7807 logging.
2. `[CLEANUP]` Retain `AliasEngine` import at L29 of `SynthesisEngine` (consumed at L235).
3. `[CLEANUP]` Replace dual-access lookups and ternaries on `__GLOBAL_ATOM_BLACKBOARD__` and `__MATRIX_REDUCER_OUTPUT__` in `SynthesisEngine` with direct typed dot-notation access.
4. `[CLEANUP]` Verify zero residual matches for `dict[str, Any]`, `from typing import Any`, `.get(`, and `hasattr` across engine and logic strategy test suites pre-satisfied by EPIC 157.
5. `[CLEANUP]` Clean docstrings in `backend_v2/services/orchestrator/engines/base.py` to remove legacy concurrency references.
6. `[CLEANUP]` Replace vacuous `if not filepath.exists():` guards in `backend_v2/tests/unit/test_ast_concurrency_guardrails.py` with `assert filepath.exists()`.
7. `[CLEANUP]` Enforce `Field(ge=1)` on all 5 concurrency settings in `backend_v2/settings.py` with min-1 and min ISTQB boundary tests in `test_system_concurrency_compliance.py`.
8. `[CLEANUP]` Eradicate duck-typing blackboard fallback chains in `TDAEngine` and `LLMNodeStrategy` in favor of direct typed `ContextVariablesDTO.global_atom_blackboard` access.

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state. Verify `synthesis_engine.py`, `tda_engine.py`, `strategies/llm.py`, `settings.py`, and `test_ast_concurrency_guardrails.py` are present.</action>
    <action>Look forward: Verify that resolving technical debt in `SynthesisEngine`, settings bounds, and blackboard access prepares a clean foundation for Phase 2 protocol harmonization.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md]) and the Tracker document (@[docs/epic/EPIC_155_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_155/01_phase1_plan.md] @[docs/epic/EPIC_155_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>SynthesisEngine ValueError instances at L159 and L215 replaced with AppException(ErrorCodes.VALIDATION_FAILED) and RFC 7807 logging.</item>
    <item>AliasEngine import at L29 of SynthesisEngine retained and verified consumed at L235.</item>
    <item>SynthesisEngine dual-access lookups on __GLOBAL_ATOM_BLACKBOARD__ and __MATRIX_REDUCER_OUTPUT__ eradicated in favor of typed fields.</item>
    <item>Unreachable ternary fallback at L246 of SynthesisEngine eliminated.</item>
    <item>Verification gate confirms zero matches for dict[str, Any], from typing import Any, and .get( in test_synthesis_engine.py, zero .get( in test_tda_engine.py, and zero hasattr in test_logic.py.</item>
    <item>ExecutionEngine protocol docstrings cleaned of concurrency and event references.</item>
    <item>AST concurrency guardrails enforce assert filepath.exists() anchored to project root, eliminating vacuous passes.</item>
    <item>Settings fields semaphore_low_rpm_limit, semaphore_max_concurrency, semaphore_rpm_divisor, max_concurrent_workflows, and max_concurrent_llm_steps enforce Field(ge=1).</item>
    <item>ISTQB boundary tests in test_system_concurrency_compliance.py verify value 0 raises ValidationError and value 1 is accepted across all 5 settings.</item>
    <item>Duck-typing blackboard fallback chains in TDAEngine and LLMNodeStrategy eradicated in favor of direct typed global_atom_blackboard access.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT remove semaphore or running_event from EngineExecutionRequest during Phase 1 (quarantined strictly for Phase 5).</anti_target>
    <anti_target>Do NOT modify LiteLLMProvider provider.py during Phase 1 (quarantined as read-only).</anti_target>
    <anti_target>Do NOT modify sub-executors TwoPassAtomizer, EnrichedDagExecutor, or SlidingWindowLinker during Phase 1 (quarantined strictly for Phase 3).</anti_target>
    <anti_target>Do NOT modify NodeStrategy.execute signatures during Phase 1 (quarantined strictly for Phase 4).</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/engines/synthesis_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/base.py]</backend>
    <backend>@[backend_v2/settings.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/tda_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm.py]</backend>
  </touched_artifacts>

  <contract_freeze>
    <interface name="ExecutionEngine.execute">
      <signature>async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:</signature>
      <constraint>Engine signature remains locked to typing.Protocol accepting single EngineExecutionRequest DTO and returning EngineExecutionResult DTO.</constraint>
    </interface>
  </contract_freeze>

  <test_contracts>
    <test name="test_synthesis_engine_missing_hydrated_messages_raises_app_exception" category="error_path">
      <input>EngineExecutionRequest with hydrated_messages=None</input>
      <expected>raises AppException with details["error_code"] == ErrorCodes.VALIDATION_FAILED.value</expected>
    </test>
    <test name="test_synthesis_engine_missing_compiled_schema_raises_app_exception" category="error_path">
      <input>EngineExecutionRequest with compiled_schema=None</input>
      <expected>raises AppException with details["error_code"] == ErrorCodes.VALIDATION_FAILED.value</expected>
    </test>
    <test name="test_synthesis_engine_ignores_untyped_blackboard_variable" category="negative">
      <input>ContextVariablesDTO(variables={"__GLOBAL_ATOM_BLACKBOARD__": "not_a_valid_dict"})</input>
      <expected>raises AppException with details["error_code"] == ErrorCodes.SYNTHESIS_ENGINE_ERROR.value</expected>
    </test>
    <test name="test_settings_concurrency_zero_limits_raise_validation_error" category="boundary">
      <input>Settings with semaphore_low_rpm_limit=0, semaphore_max_concurrency=0, semaphore_rpm_divisor=0, max_concurrent_workflows=0, or max_concurrent_llm_steps=0</input>
      <expected>raises pydantic.ValidationError (min-1 partition)</expected>
    </test>
    <test name="test_settings_concurrency_min_limits_accepted" category="boundary">
      <input>Settings with semaphore_low_rpm_limit=1, semaphore_max_concurrency=1, semaphore_rpm_divisor=1, max_concurrent_workflows=1, max_concurrent_llm_steps=1</input>
      <expected>model validates successfully with values == 1 (min partition)</expected>
    </test>
    <test name="test_context_variables_corrupted_blackboard_raises_validation_error_at_ingress" category="negative">
      <input>ContextVariablesDTO.model_validate({"__GLOBAL_ATOM_BLACKBOARD__": "not_a_valid_dict"})</input>
      <expected>raises pydantic.ValidationError at ingress boundary</expected>
    </test>
    <test name="test_tda_engine_typed_blackboard_success" category="positive">
      <input>EngineExecutionRequest with ContextVariablesDTO(global_atom_blackboard=GlobalAtomBlackboard(...))</input>
      <expected>executes successfully without duck-typing inspection</expected>
    </test>
  </test_contracts>

  <step id="1.1" name="FIX_SYNTHESIS_ENGINE_VALUEERROR_DUCT_TAPE_AND_DEAD_IMPORTS">
    <action>RETAIN `from backend_v2.utils.alias_engine import AliasEngine` at `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L29]`: the symbol is consumed at L235 (`alias_engine = AliasEngine()`). The pre-audit dead-import directive is RETRACTED (deleting it raises `NameError` and Ruff F821).</action>
    <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L292]`, replace `raise ValueError("hydrated_messages must be provided for SynthesisEngine")` at L159 with a structured `logger.error("synthesis_engine_missing_hydrated_messages", extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": request.step.id})` (RFC 7807 dual-reporting) followed by `AppException(message="hydrated_messages must be provided for SynthesisEngine", status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "step_id": request.step.id})`.</action>
    <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L292]`, replace `raise ValueError("compiled_schema must be provided for SynthesisEngine")` at L215 with a structured `logger.error("synthesis_engine_missing_compiled_schema", extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": request.step.id})` (RFC 7807 dual-reporting) followed by `AppException(message="compiled_schema must be provided for SynthesisEngine", status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "step_id": request.step.id})`.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L363-L373]`, update `test_synthesis_engine_missing_hydrated_messages` to assert `exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value`.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L376-L386]`, update `test_synthesis_engine_missing_compiled_schema` to assert `exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value`.</action>
  </step>

  <step id="1.2" name="ERADICATE_SYNTHESIS_ENGINE_CONTEXT_FALLBACK_CHAINS">
    <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L51-L292]` (L70-L92), replace the dual-access lookup at L71-L73 with `blackboard = request.context.context_variables.global_atom_blackboard`, retain the existing `None` Fail-Fast branch (L74-L86, `ErrorCodes.SYNTHESIS_ENGINE_ERROR`), and delete the `isinstance`/`GlobalAtomBlackboard.model_validate` ternary at L88-L92 (the typed field is already `GlobalAtomBlackboard | None`).</action>
    <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L51-L292]` (L98-L102), replace the subscript fallback with `matrix_reducer_output = request.context.context_variables.matrix_reducer_output`. Root cause: `ContextVariablesDTO` (`@[backend_v2/models/dtos/context_variables.py#L38-L203]` (`AliasChoices` at L43-L58)) already maps `__GLOBAL_ATOM_BLACKBOARD__` and `__MATRIX_REDUCER_OUTPUT__` onto typed fields via `AliasChoices`, and `with_update` (L87-L93) routes both keys to the typed fields; the consumer-side subscript fallback is a banned "if A is missing, try B" chain.</action>
    <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L51-L292]` (L244-L247), replace `request.compiled_schema.model_validate(output_dict) if request.compiled_schema else validated_model` with `request.compiled_schema.model_validate(output_dict)` (non-`None` is proven by the L214-L215 guard).</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L434-L453]`, rewrite `test_synthesis_engine_validation_error` into `test_synthesis_engine_ignores_untyped_blackboard_variable`: a `ContextVariablesDTO(variables={"__GLOBAL_ATOM_BLACKBOARD__": "not_a_valid_dict"})` context MUST raise `AppException` with `exc_info.value.details["error_code"] == ErrorCodes.SYNTHESIS_ENGINE_ERROR.value`, proving the fallback path no longer exists.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L456-L489]`, migrate `variables={"__MATRIX_REDUCER_OUTPUT__": matrix_output}` (L473) to the typed field `matrix_reducer_output=matrix_output`. All step 1.2 production and test edits MUST land in one atomic commit.</action>
    <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/synthesis_engine.py --test --ast-strict`; zero failures before step 1.3.</action>
  </step>

  <step id="1.3" name="VERIFY_EPIC_157_RESOLVED_TEST_REFLECTION_DEBT">
    <action>Verification-only (pre-satisfied by EPIC 157): `grep_search` for each of `dict[str, Any]`, `from typing import Any`, and `.get(` in `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]` MUST return zero matches; any match blocks Phase 2.</action>
    <action>Verification-only (pre-satisfied by EPIC 157): `grep_search` for `.get(` in `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]` MUST return zero matches.</action>
    <action>Verification-only (pre-satisfied by EPIC 157): `grep_search` for `hasattr` in `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]` MUST return zero matches. Root cause of this conversion: re-executing the pre-audit edits would target code that no longer exists.</action>
  </step>

  <step id="1.4" name="CLEAN_BASE_EXECUTION_ENGINE_PROTOCOL">
    <action>In `@[backend_v2/services/orchestrator/engines/base.py#L11-L31]`, audit docstrings and signature of `ExecutionEngine.execute` to ensure complete decoupling from concurrency limiters and telemetry events.</action>
  </step>

  <step id="1.5" name="HARDEN_AST_CONCURRENCY_GUARDRAIL_PATH_RESOLUTION">
    <action>In `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L63-L67]`, replace `if not filepath.exists(): return ...` in `scan_file_for_concurrency` with `assert filepath.exists(), f"Guardrail target missing: {filepath}"` so that non-existent files fail loudly instead of returning all-`False` vacuous passes.</action>
    <action>In `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L70-L81]`, replace the cwd-relative `base = Path("backend_v2")` with `Path(__file__).resolve().parents[2]` and replace every `if <path>.exists():` guard in the module with `assert <path>.exists()` so that a missing target fails loudly. The existing `res["semaphore"] is True` assertion for `dag_executor.py` is retained until Phase 5 step 5.6. (The `fake_node_execute` hook removal at `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L747-L864]` (L849-L850) is relocated to Phase 5 step 5.4 because it simulates behavior that remains live until step 5.3.)</action>
  </step>

  <step id="1.6" name="HARDEN_PROVIDER_CONCURRENCY_SETTINGS_BOUNDS">
    <action>In `@[backend_v2/settings.py#L211]` (fields L211-L214), add `ge=1` to the existing `Field(...)` declarations of `semaphore_low_rpm_limit`, `semaphore_max_concurrency`, and `semaphore_rpm_divisor` (zero new fields). Root cause: these settings become the sole micro-concurrency SSOT; `0` yields an `asyncio.Semaphore(0)` silent deadlock or a `ZeroDivisionError` at `@[backend_v2/llm/provider.py#L530-L658]` (L645-L651).</action>
    <action>In `@[backend_v2/settings.py#L176]` (fields L176-L177), add `ge=1` to `max_concurrent_workflows` and `max_concurrent_llm_steps`. Rewrite the description of `max_concurrent_llm_steps` at L177 to "Max parallel Phase 2 synthesis LLM tasks per synthesis job" (root cause: the old description "Max parallel LLM extractions within a TaskGroup" is obsolete).</action>
    <action>In `@[backend_v2/tests/unit/models/test_system_concurrency_compliance.py]`, add ISTQB boundary tests: value `0` raises `pydantic.ValidationError` (min-1 partition) and value `1` is accepted (min partition) across `semaphore_low_rpm_limit`, `semaphore_max_concurrency`, `semaphore_rpm_divisor`, `max_concurrent_workflows`, and `max_concurrent_llm_steps`. Correct the L9 comment so it states that `max_concurrent_llm_steps` governs Phase 2 synthesis fan-out only.</action>
  </step>

  <step id="1.7" name="ERADICATE_TWIN_BLACKBOARD_FALLBACK_CHAINS">
    <action>In `@[backend_v2/services/orchestrator/engines/tda_engine.py#L37-L271]` (L86-L119), replace the banned dict duck-typing fallback chain with direct typed access: `blackboard = request.context.context_variables.global_atom_blackboard`; `is_starved = blackboard is not None and (blackboard.is_data_starved or not blackboard.atoms_by_input)`. Delete `raw_blackboard: Any`, `isinstance(ctx_vars, ContextVariablesDTO)`, `isinstance(ctx_vars, (str, int, float, bool, list))`, `"__GLOBAL_ATOM_BLACKBOARD__" in ctx_vars`, `"is_data_starved" in raw_blackboard`, and the `try/except (TypeError, KeyError)` block.</action>
    <action>In `@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1012]` (L132-L148), replace the triple fallback chain with direct typed access: `blackboard = context.context_variables.global_atom_blackboard if context is not None else None`; `atoms_by_input = blackboard.atoms_by_input if blackboard is not None else {}`. Delete `raw_bb: Any`, dictionary subscript lookups, `gvars["__GLOBAL_ATOM_BLACKBOARD__"]`, and the dictionary branch at L146-L148.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]`, migrate raw dictionary blackboard fixtures (L219, L278) to `ContextVariablesDTO(global_atom_blackboard=GlobalAtomBlackboard(...))`. Delete the `CorruptedMapping` test (`test_tda_engine_blackboard_corrupted_mapping_logged_and_ignored`, L266-L278) and replace it with an ISTQB negative test asserting that `ContextVariablesDTO.model_validate({"__GLOBAL_ATOM_BLACKBOARD__": "not_a_valid_dict"})` raises `pydantic.ValidationError` at ingress.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py#L426]`, migrate raw dictionary blackboard fixture to `ContextVariablesDTO(global_atom_blackboard=GlobalAtomBlackboard(...))`.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py#L2779]`, migrate dictionary blackboard fixture to typed field `ContextVariablesDTO(global_atom_blackboard=GlobalAtomBlackboard(...))`.</action>
    <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/tda_engine.py backend_v2/services/orchestrator/strategies/llm.py --test --ast-strict` to ensure zero failures. All step 1.7 production and test changes MUST land in one atomic commit.</action>
  </step>

  <validation_gate>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/synthesis_engine.py backend_v2/services/orchestrator/engines/tda_engine.py backend_v2/services/orchestrator/strategies/llm.py backend_v2/settings.py backend_v2/services/orchestrator/engines/base.py --test --ast-strict`</action>
    <action>Run `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py backend_v2/tests/unit/models/test_system_concurrency_compliance.py backend_v2/tests/unit/test_ast_concurrency_guardrails.py -v`</action>
    <action>Assert zero occurrences of ValueError in synthesis_engine.py</action>
    <action>Assert zero occurrences of "__GLOBAL_ATOM_BLACKBOARD__" subscript lookups in synthesis_engine.py, tda_engine.py, and strategies/llm.py</action>
  </validation_gate>
</execution_protocol>
```
