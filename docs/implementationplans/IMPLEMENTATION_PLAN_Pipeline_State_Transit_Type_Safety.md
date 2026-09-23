<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
</required_context_rules>

# Implementation Plan: Pipeline State Transit Type Safety & Validation Hardening

## Problem Overview
In the internal DAG execution pipeline, state transit between `DAGExecutor`, `StateProjector`, `TraceEvent`, `ContextRouter`, and hooks still permits loose typing constructs and validation bypasses:
1. `TraceEvent.content` and `TraceEvent.metadata` in @[backend_v2/models/state.py#L157-L207] are annotated as naked dictionaries (`dict[str, Any]`), acting as the primary leak site where untyped dictionaries infiltrate the event sourcing read model.
2. `StateProjector._build_dto_list()` in @[backend_v2/models/state.py#L551-L589] catches `ValidationError` when instantiating `StepOutputDTO` and silently falls back to `StepOutputDTO.model_construct(...)`. This duct-tape fallback swallows corrupted state and passes invalid DTOs downstream.
3. `ContextRouter.route_and_prune` in @[backend_v2/services/orchestrator/context_router.py#L52-L127] accepts untyped `trace_event: Any` and executes duck-typing inspection via `isinstance(trace_event, Mapping)` rather than enforcing a strict typed DTO contract.
4. `DAGExecutor` in @[backend_v2/services/orchestrator/dag_executor.py#L185-L350] and @[backend_v2/services/orchestrator/dag_executor.py#L438-L1317] contains defensive fallback dict-unpacking branches (`isinstance(..., Mapping)`) and converts typed models to raw dictionaries via `.model_dump()` before creating trace events (specifically and exhaustively: `inputs_dict = exec_record.raw_inputs.model_dump(...)` and `content=lightweight_matrix.model_dump()`).
5. `synthesis_payload_compressor.py` in @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L181-L384] retains 3 naked `dict[str, Any]` annotations.

These permissive typing loopholes delay boundary failures: type mismatches and validation errors do not trigger at ingress or compilation time, but surface deep in downstream execution (specifically and exhaustively: `PromptCompiler` and `SynthesisWorker`), where they are routed to the Dead Letter Queue (DLQ) or crash active runs.

---

## Target Scope & Boundaries

### TARGET Files (To Modify)
- @[backend_v2/models/state.py#L157-L207] [MODIFY]: Bind `TraceEvent.content` to closed union `StepPayloadValue | DomainInputValue | BaseModel | None`, bind `TraceEvent.metadata` to typed metadata model, and type `StateProjector._snapshot` as `dict[str, dict[str, StepPayloadValue]]`.
- @[backend_v2/models/state.py#L551-L589] [MODIFY]: Eradicate `model_construct()` fallback in `StateProjector._build_dto_list()`; raise `AppException(ErrorCodes.VALIDATION_FAILED)` immediately upon validation failure.
- @[backend_v2/services/orchestrator/context_router.py#L52-L127] [MODIFY]: Restrict `ContextRouter.route_and_prune` signature strictly to `trace_event: LightweightMatrixOutput` and eradicate `isinstance(trace_event, Mapping)` branches.
- @[backend_v2/services/orchestrator/dag_executor.py#L185-L350] [MODIFY]: Eradicate `isinstance(..., Mapping)` fallback dict unpacking for `global_context_vars` and `context_variables`.
- @[backend_v2/services/orchestrator/dag_executor.py#L438-L1317] [MODIFY]: Pass typed `ExecutionInputsDTO` and `StepOutputContentDTO` directly into `TraceEvent` without intermediate `.model_dump()` dictionary conversions, and pass `content=lightweight_matrix` directly.
- @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L181-L384] [MODIFY]: Eradicate 3 naked `dict[str, Any]` annotations in favor of typed models or `dict[str, JsonValue]`.
- @[backend_v2/tests/unit/models/test_state.py] [MODIFY]: Expand unit tests with ISTQB negative partitions asserting Fail-Fast on invalid payloads and zero `model_construct()` bypasses.
- @[backend_v2/tests/unit/services/orchestrator/test_context_router.py] [MODIFY]: Align test fixtures to pass `LightweightMatrixOutput` directly and assert `ValidationError` on untyped inputs.
- @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py] [MODIFY]: Update DAG state transit test assertions for typed `TraceEvent` content.

### CONTEXT Files (Read-Only SSOT References)
- @[backend_v2/models/dtos/step_output.py#L55-L69]: SSOT for `StepOutputDTO` and `StepPayloadValue` closed union.
- @[backend_v2/models/domain/inputs.py#L175-L212]: SSOT for `DomainInputValue` closed union.
- @[backend_v2/models/dtos/hook_state.py#L36-L63]: SSOT for `ExecutionInputsDTO`.
- @[backend_v2/models/dtos/lightweight_matrix.py]: SSOT for `LightweightMatrixOutput`.

---

## Phase 1: Pre-Implementation Technical Debt Cleanups
Before introducing structural schema modifications, the following technical debt items must be eradicated:
1. **`StateProjector` Validation Bypass Elimination**:
   - Location: @[backend_v2/models/state.py#L551-L589].
   - Action: Eradicate `except ValidationError: output.append(StepOutputDTO.model_construct(...))`. Replace with RFC 7807 structured logging and raise `AppException(status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})`.
2. **`ContextRouter` Duck-Typing Purge**:
   - Location: @[backend_v2/services/orchestrator/context_router.py#L52-L127].
   - Action: Eradicate `elif isinstance(trace_event, Mapping):` and associated dictionary indexing (`trace_event["evaluated_atoms"]`). Enforce `trace_event: LightweightMatrixOutput` in the function signature.
3. **`synthesis_payload_compressor.py` Naked Dict Purge**:
   - Location: @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L181-L384].
   - Action: Replace naked `dict[str, Any]` with typed Pydantic DTOs or `dict[str, JsonValue]`.

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`TraceEvent`**<br>@[backend_v2/models/state.py#L157-L207] | Banned `content: dict[str, Any]` and `metadata: dict[str, Any]`. | Replace with closed union `StepPayloadValue \| DomainInputValue \| BaseModel \| None` and typed metadata model. | Pruned generic dynamic event factories. Direct typed union with Pydantic V2 native validation. | `uv run python scripts/audit_dict_eradication.py backend_v2/models/state.py` reports 0 violations. |
| **`StateProjector`**<br>@[backend_v2/models/state.py#L480-L612] | Banned `_snapshot: dict[str, Any]` and banned `.model_construct()` fallback on `ValidationError`. | `_snapshot: dict[str, dict[str, StepPayloadValue]]`. When validation fails, raise `AppException(ErrorCodes.VALIDATION_FAILED)` immediately. | Pruned fallback compaction layers. Pure O(1) in-memory fold using typed DTOs. | Negative unit test: `test_state_projector_invalid_payload_raises_app_exception` passes 100%. |
| **`ContextRouter`**<br>@[backend_v2/services/orchestrator/context_router.py#L52-L127] | Banned `trace_event: Any` and `isinstance(trace_event, Mapping)` duck-typing check. | Signature strictly enforces `trace_event: LightweightMatrixOutput`. Remove dict parsing and validation bypass branches. | Pruned dual-branch parsing code (40 lines of dictionary validation removed). | `test_context_router.py` unit suite passes with zero `Mapping` checks. |
| **`DAGExecutor` Node Execution**<br>@[backend_v2/services/orchestrator/dag_executor.py#L185-L350] | Banned `isinstance(global_context_vars, Mapping)` and `GlobalContextVarsDTO(**dict(...))` conversion. | Pass `GlobalContextVarsDTO` and `ContextVariablesDTO` strictly as typed DTO instances. Remove fallback dict unpackers. | Pruned defensive `isinstance` cascades across NodeExecutor. | `test_dag_executor.py` asserts strict DTO transit without dictionary wrapping. |
| **`DAGExecutor` Pre-Hydration & Reducer**<br>@[backend_v2/services/orchestrator/dag_executor.py#L438-L1317] | Banned `.model_dump()` dictionary conversions before appending to `execution_trace`. | Pass `exec_record.raw_inputs` and `lightweight_matrix` directly into `TraceEvent(content=...)` as typed models. | Pruned intermediate serialization and deserialization overhead. | `test_dag_executor.py` verifies zero double-serialization in trace events. |

---

```xml
<execution_protocol>
  <step id="1" name="PRE_IMPLEMENTATION_CLEANUPS">
    <action>In @[backend_v2/models/state.py#L551-L589], eradicate the `.model_construct()` fallback in `StateProjector._build_dto_list()`. When `StepOutputDTO(...)` raises `ValidationError`, log structured RFC 7807 error and re-raise `AppException` with `ErrorCodes.VALIDATION_FAILED` (HTTP 500).</action>
    <action>In @[backend_v2/services/orchestrator/context_router.py#L52-L127], refactor `ContextRouter.route_and_prune` signature from `trace_event: Any` to `trace_event: LightweightMatrixOutput`. Delete `isinstance(trace_event, Mapping)` branch and dictionary base-field validation checks.</action>
    <action>In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L181-L384], replace 3 naked `dict[str, Any]` annotations with `dict[str, JsonValue]` and typed models.</action>
    <constraint invariant="the_duct_tape_ban">Zero tolerance for fallback bypasses via model_construct or loose Mapping duck typing.</constraint>
    <constraint invariant="no_naked_dicts_in_state">Eradicate naked dict[str, Any] in state and compressor layers.</constraint>
  </step>

  <step id="2" name="TYPED_TRACE_EVENT_AND_METADATA_DTO">
    <action>In @[backend_v2/models/state.py#L157-L207], define TraceEventMetadataDTO(V2CoreBase) with ConfigDict(strict=True, extra="forbid", frozen=True) containing typed optional fields: mcp_audit_traces: list[MCPAuditTrace], estimated_token_count: int | None, generated_schema: dict[str, JsonValue] | None.</action>
    <action>In @[backend_v2/models/state.py#L157-L207], update `TraceEvent.content` to `Annotated[StepPayloadValue | DomainInputValue | BaseModel | None, Field(default=None, description="Typed event payload")] = None`.</action>
    <action>In @[backend_v2/models/state.py#L157-L207], update `TraceEvent.metadata` to `Annotated[TraceEventMetadataDTO, Field(default_factory=TraceEventMetadataDTO, description="Typed event metadata")]`.</action>
    <constraint invariant="strict_pydantic_v2_rust">Enforce strict Pydantic V2 validation on all TraceEvent payloads.</constraint>
    <constraint invariant="absolute_pydantic_strictness">Data must remain strongly typed DTO objects throughout the entire execution trace.</constraint>
  </step>

  <step id="3" name="STATE_PROJECTOR_TYPED_SNAPSHOT">
    <action>In @[backend_v2/models/state.py#L480-L612], update `StateProjector._snapshot` type annotation to `dict[str, dict[str, StepPayloadValue]]`.</action>
    <action>In @[backend_v2/models/state.py#L591-L612], handle typed payloads directly from `event.content`: if `content` is a `BaseModel` or `StepPayloadValue`, store it directly in `_snapshot[step_id][block_id]` without intermediate dictionary conversion.</action>
    <constraint invariant="pydantic_pure_hydration_boundary">Zero json.dumps or model_dump dictionary roundtrips in in-memory state projection.</constraint>
  </step>

  <step id="4" name="DAG_EXECUTOR_STATE_TRANSIT_CLEANUP">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L185-L350], eradicate `isinstance(..., Mapping)` and `GlobalContextVarsDTO(**dict(...))` conversions. Pass `global_context_vars: GlobalContextVarsDTO` and `context_variables: ContextVariablesDTO` directly to `StrategyContext`.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L438-L1317], eradicate `.model_dump(mode="json")` conversions on `exec_record.raw_inputs`. Pass `content=exec_record.raw_inputs` directly to `TraceEvent`.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L438-L1317], eradicate `content=lightweight_matrix.model_dump()`. Pass `content=lightweight_matrix` directly to `TraceEvent`.</action>
    <constraint invariant="single_pipeline_invariant_mandate">All steps flow through one sovereign, strictly typed execution path with zero legacy dictionary shims.</constraint>
    <constraint invariant="zero_backward_compatibility_planning_ban">Do not maintain backwards-compatibility branches for legacy dictionary traces.</constraint>
  </step>

  <step id="5" name="UNIT_TEST_MODERNIZATION_AND_ISTQB_EXPANSION">
    <action>In @[backend_v2/tests/unit/models/test_state.py], modernize test fixtures to pass typed DTO instances to `TraceEvent`.</action>
    <action>Add ISTQB negative boundary partition 1 in `test_state.py`: `test_state_projector_invalid_payload_raises_validation_failed` asserting that feeding malformed event data raises `AppException(ErrorCodes.VALIDATION_FAILED)` instead of silently constructing via `model_construct()`.</action>
    <action>Add ISTQB negative boundary partition 2 in `test_state.py`: `test_trace_event_untyped_arbitrary_object_raises_validation_error` asserting that passing unregistered objects to `TraceEvent.content` raises Pydantic `ValidationError`.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_context_router.py], align all test cases to pass `LightweightMatrixOutput` and add negative partition asserting `ValidationError` when non-`LightweightMatrixOutput` is provided.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py], update state transit tests to assert typed `TraceEvent` content.</action>
    <constraint invariant="anti_happy_path_mandate">Mandate >=2 negative failure partitions per feature module.</constraint>
  </step>

  <step id="6" name="DETERMINISTIC_AST_AUDIT_VERIFICATION">
    <action>Run deterministic AST scan on touched files: `uv run python scripts/audit_dict_eradication.py backend_v2/models/state.py --strict` to verify 0 naked dicts and 0 reflection calls.</action>
    <action>Run deterministic AST scan on compressor: `uv run python scripts/audit_dict_eradication.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --strict` to verify 0 violations.</action>
    <constraint invariant="zero_naked_dicts_and_permissive_typing">Enforce 100% mathematical zero violations across all 8 AST metrics.</constraint>
  </step>

  <step id="7" name="UNIVERSAL_QUALITY_GATE_COMPLETION">
    <action>Run localized audit loop on models: `uv run python scripts/backend_audit_loop.py backend_v2/models/state.py --test`.</action>
    <action>Run localized audit loop on context router: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/context_router.py --test`.</action>
    <action>Run localized audit loop on dag executor: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test`.</action>
    <action>Run isolated unit test suites: `uv run pytest backend_v2/tests/unit/models/test_state.py backend_v2/tests/unit/services/orchestrator/test_context_router.py backend_v2/tests/unit/services/orchestrator/test_dag_executor.py`.</action>
    <constraint invariant="zero_tolerance_audit_loop">Universal quality gate must pass 100% with clean Mypy, Ruff, and 90%+ test coverage.</constraint>
  </step>

  <step id="8" name="ATOMIC_CHECKPOINT_COMMITS">
    <action>Instruct atomic git commit for staged changes with Conventional Commits message: `refactor(orchestrator): enforce strict pydantic v2 type safety across pipeline state transit`.</action>
    <constraint invariant="atomic_checkpoint_mandate">Stage specifically and exhaustively touched files.</constraint>
  </step>
</execution_protocol>
```

---

## Architectural Safeguards & Verification Plan

### Automated Test Gates
1. **Localized Unit Tests**:
   ```powershell
   uv run pytest backend_v2/tests/unit/models/test_state.py backend_v2/tests/unit/services/orchestrator/test_context_router.py backend_v2/tests/unit/services/orchestrator/test_dag_executor.py -v
   ```
2. **Deterministic AST Dict Eradication Gate**:
   ```powershell
   uv run python scripts/audit_dict_eradication.py backend_v2/models/state.py --strict
   uv run python scripts/audit_dict_eradication.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --strict
   ```
3. **Backend Audit Loops**:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/models/state.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/context_router.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test
   ```
4. **Final Integration REST API Gate (Offline Mocked)**:
   ```powershell
   uv run pytest backend_v2/tests/integration/test_pipeline_state_transit.py -v
   ```
