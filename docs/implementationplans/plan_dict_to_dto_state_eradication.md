# Implementation Plan: Eradication of dict[str, Any] in Orchestrator State & Double-Serialization Elimination

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
</required_context_rules>

## Goal Description
Eradicate all lingering `dict[str, Any]` type annotations and loose mapping containers across orchestrator state transit (`HookDeltaDTO`, `HookState`, `state_reducer.py`, `context_router.py`), eliminate the double-serialization anti-pattern (`model_dump(mode="json")` -> dict -> `model_validate()`) across all 17 execution hooks, and enforce Python 3.14 concurrency and strictness invariants. Establish a sovereign, pure state reduction protocol in `state_reducer.py` (`reduce_hook_delta`), eliminate duck-typing `isinstance(delta, Mapping)` in `strategies/base.py`, delete the redundant `SnapshotState` model from `context_router.py`, and safeguard concurrency progress updates (`async with _update_lock:` shallow updates on `ExecutionRecord`) while requiring pure constructor instantiation for domain construction.

---

## User Review Required

> [!IMPORTANT]
> **End-to-End Type Safety Across 17 Execution Hooks:**  
> All 17 hooks in `backend_v2/hooks/` will be migrated from returning serialized JSON dictionaries (`.model_dump(mode="json")`) to returning strongly typed DTO instances directly. Downstream consumers in `context_builder.py` and `dag_executor.py` will consume these typed objects without intermediate dictionary parsing or secondary re-validation.

> [!WARNING]
> **Removal of `| dict[str, Any]` Escape Hatch in `HookDeltaDTO`:**  
> Any hook or test returning a raw dictionary inside `HookDeltaDTO.delta` or `metadata_updates` will immediately fail fast with a Pydantic `ValidationError`. Test mock fixtures across `backend_v2/tests/` must be migrated to typed DTO fixtures.

> [!NOTE]
> **Python 3.14 Concurrency & Strictness Walkthrough:**  
> This plan incorporates the updated Knowledge Item `ki_python_314_concurrency_strictness.md`. It validates deferred annotations (PEP 649 and PEP 749) for clean DTO unions, enforces `finally` control flow integrity (PEP 765), enables live asyncio CLI introspection readiness (`python -m asyncio ps` and `pstree`), and isolates shallow `model_copy` concurrency updates from deep domain construction.

---

## Touched Scope Technical Debt & Anti-Pattern Sweep

An exhaustive AST and structural scan of `backend_v2` identified the following technical debt items across the target boundary:

1. **`backend_v2/models/dtos/hook_delta.py`**:
   - Permissive escape hatch `| dict[str, Any]` inside `HookDeltaDTO.delta`.
   - Naked dictionary `metadata_updates: dict[str, Any] | None`. Allows unvalidated key injection into `ExecutionMetadata`.
   - Lacks concrete payload DTOs for scalar and boolean hook results (specifically: passivity detection, anomaly retry, input control ratio, and interaction analysis).
2. **`backend_v2/services/orchestrator/context_router.py`**:
   - `SnapshotState` contains 4 unused `Any` fields (`raw_inputs: dict[str, Any] | None`, `inputs: Any | None`, `metadata: Any | None`, `global_context_vars: Any | None`) and `steps: list[Any] | None`.
   - `normalize_and_validate_variable` accepts untyped `snapshot: Any`.
   - Catches broad exceptions `except (TypeError, ValueError, KeyError):` instead of specific Pydantic `ValidationError` or `AppException`.
3. **`backend_v2/services/orchestrator/strategies/base.py`**:
   - Duck-typing `if isinstance(delta, Mapping):` in `run_pre_hooks` and `run_post_hooks` silently drops typed Pydantic DTOs that do not implement `Mapping`.
   - Duplicate 40-line state-merging loops between pre-hooks and post-hooks.
   - Unvalidated `model_copy(update={...})` in hook execution pathways.
4. **`backend_v2/services/orchestrator/state_reducer.py`**:
   - Incomplete reducer scope: only handles `ExecutionInputsDTO`, while metadata, global context variables, and step deltas are merged haphazardly in `base.py`.
   - Uses `base.model_copy(update={...})` with dictionary unpacking instead of pure constructor instantiation.
5. **`backend_v2/services/orchestrator/dag_executor.py`**:
   - Wraps `projector.snapshot` into an ad-hoc dictionary `{"steps": projector.snapshot}` to satisfy `SnapshotState.model_validate`.
6. **`backend_v2/models/dtos/step_output.py`**:
   - `payload: Any` lacks closed union boundary, allowing untyped objects into trace events.
   - Missing `frozen=True` in `model_config = ConfigDict(strict=True, extra="forbid")`.
7. **`backend_v2/hooks/` (17 Active Hooks)**:
   - Hooks authoring `HookResult` call `.model_dump(mode="json")` to bypass `strategies/base.py`'s `isinstance(delta, Mapping)` check (specifically: `atom_flattening.py`, `synthesis_distiller.py`, `security.py`, `references.py`, `validation.py`, `passivity_hook.py`, `metrics.py`, `scoring.py`, `interaction_hook.py`, `linguistic_shield.py`, `translation_hook.py`, `contrastive_hook.py`, `tavily_search_hook.py`, `wikipedia_hook.py`, `document_preflight.py`, `rag_preflight.py`, `rag_enrichment_hook.py`).
8. **`scripts/audit_dict_eradication.py`**:
   - Requires verification of zero naked dicts and zero `model_dump` conversions across orchestrator and hook states.

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`hook_delta.py`** (`HookDeltaDTO`) | Banned `\| dict[str, Any]` in `delta` and `dict[str, Any]` in `metadata_updates`. | Exhaustive closed union `HookPayloadDTO` and typed `ExecutionMetadataDeltaDTO`. Enforce `frozen=True`. | Avoid generic multi-level wrapper classes; define flat payload DTOs for simple boolean and metric hooks. | `audit_dict_eradication.py` reports 0 naked dicts. Test asserting `HookDeltaDTO(delta={"raw": 1})` raises `ValidationError`. |
| **`context_router.py`** (`ContextRouter`) | Banned `list[Any]`, `dict[str, Any]`, and untyped `Any` snapshot parameters. | Change signature: `normalize_and_validate_variable(path: str, steps: Sequence[StepOutputDTO]) -> str`. | **DELETE `SnapshotState` completely**. Pass `projector.snapshot` directly without intermediate wrapper model. | `test_context_router.py` updated with typed `StepOutputDTO` fixtures; 100% passing tests. |
| **`state_reducer.py`** (`StateReducer`) | Banned `base.model_copy(update=...)` with dictionaries and fragmented state merging. | Implement `reduce_hook_delta(state: HookState, delta: HookDeltaDTO, step_id: str \| None) -> tuple[HookState, list[TraceEvent]]` as a pure function. | Eliminate intermediate dictionary copies; construct new immutable `HookState` directly via constructor. | Unit tests in `test_state_reducer.py` covering all hook payload types with positive and negative partitions. |
| **`strategies/base.py`** (`run_pre_hooks`, `run_post_hooks`) | Banned `isinstance(delta, Mapping)` duck-typing and duplicate state reduction logic. | Delegate state mutation 100% to `reduce_hook_delta`. Zero dictionary munging in node strategies. | Prune 60+ lines of redundant state-copying loops between pre-hooks and post-hooks. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/base.py --test`. |
| **`backend_v2/hooks/`** (17 Hook Modules) | Banned `.model_dump(mode="json")` and raw dictionary returns in `HookResult`. | Return typed DTOs directly in `HookDeltaDTO(delta=my_dto)`. | Remove manual serialization code and JSON encoding inside hooks. | Verification that all 17 hooks return valid typed DTOs without dictionary conversions. |
| **`step_output.py`** (`StepOutputDTO`) | Banned `payload: Any` and missing `frozen=True`. | Define `payload: StepPayloadValue` (closed union of valid step output models and `str`). Enforce `frozen=True`. | Reuse existing domain models (`LightweightMatrixOutput`, `AnalystOutput`) instead of redundant DTO clones. | Pydantic strict validation test ensuring invalid payload types are rejected at instantiation. |
| **`dag_executor.py`** (`DAGExecutor`) | Banned wrapping `projector.snapshot` in naked dictionary `{"steps": projector.snapshot}`. | Pass `projector.snapshot` directly into `ContextRouter.normalize_and_validate_variable`. | Eliminate ad-hoc dictionary construction at step validation call site. | `test_dag_executor.py` passing with zero naked dictionary warnings. |

---

## Python 3.14 Concurrency & Strictness Walkthrough

This plan aligns the target components with the updated Knowledge Item `ki_python_314_concurrency_strictness.md`:

1. **Deferred Evaluation of Annotations (PEP 649 & PEP 749):**
   - All newly introduced hook payload DTOs and unions in `hook_delta.py` leverage native unquoted type annotations evaluated lazily via `annotationlib`.
   - Circular dependencies between hook states and step outputs are resolved natively without string forward references.

2. **Absolute Double-Serialization Ban across Pipeline Boundaries:**
   - Intermediate state handoffs between hooks, strategies, and state reducers pass strongly typed Pydantic V2 DTOs directly.
   - Calling `.model_dump(mode="json")` to produce a dictionary only for the next function to `.model_validate()` is eliminated from all 17 hooks.

3. **Safe `model_copy` Concurrency Boundary:**
   - **Domain Construction:** `reduce_hook_delta` instantiates `HookState` via its pure constructor (`HookState(...)`), ensuring that all field validators execute. Passing unvalidated dictionaries into `model_copy(update=...)` is eradicated.
   - **Concurrency Progress Invariant:** Inside `DAGExecutor`'s concurrency lock (`async with _update_lock:`), shallow updates of `ExecutionRecord.step_states` (specifically: updating `status=ExecutionStatus.RUNNING` or progress values) continue to use `.model_copy(update={...})` with typed fields, avoiding full recursive re-validation of large object trees.

4. **Finally Control Flow Integrity (PEP 765):**
   - Resource cleanup, semaphore releases, and trace emission inside `strategies/base.py` and `dag_executor.py` maintain clean `try ... finally` blocks with zero `return`, `break`, or `continue` jumps.

5. **`asyncio.TaskGroup` Concurrency with Bracketless `except*` (PEP 758):**
   - Hook pipelines and sub-tasks executed in parallel run inside managed `asyncio.TaskGroup` contexts, trapping parallel exceptions via native `except*` syntax without tuple brackets.

6. **Non-Invasive Live Asyncio Introspection:**
   - Worker and DAG processes are structured so that live inspection via `python -m asyncio ps <PID>` and `python -m asyncio pstree <PID>` can diagnose awaiter chains without invasive profiling hooks.

7. **Two-Tier Semaphore Isolation:**
   - Macro worker limits (`settings.max_concurrent_workflows`) and micro extraction limits (`settings.max_concurrent_llm_steps`) remain strictly isolated, guarded via `nullcontext()` when semaphores are optional.

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="0" name="PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUPS &amp; AST BASELINE">
    <action>Execute baseline AST scan using `uv run python scripts/audit_dict_eradication.py backend_v2/models/dtos backend_v2/services/orchestrator --strict` to record existing violation counts.</action>
    <action>Review `ki_python_314_concurrency_strictness.md` to ensure full compliance with Python 3.14 concurrency, deferred annotations, and double-serialization bans.</action>
    <constraint invariant="zero_tolerance_audit_loop">No domain code modifications may begin until baseline scan results are established.</constraint>
  </step>

  <step id="1" name="DTO MODELS &amp; SEALED HOOK PAYLOAD UNIONS">
    <action>In `backend_v2/models/dtos/hook_delta.py`, define typed payload DTOs:
      - `PassivityDetectionResultDTO` [NEW]
      - `AnomalyDetectionResultDTO` [NEW]
      - `MetricCalculationResultDTO` [NEW]
      - `InputControlRatioResultDTO` [NEW]
      - `InteractionAnalysisResultDTO` [NEW]
      - `ExecutionMetadataDeltaDTO` [NEW]
      - `FlatteningHookOutputDTO` [NEW]
      - `HookPayloadDTO` [NEW]
    </action>
    <action>In `backend_v2/models/dtos/hook_delta.py`, assemble the exhaustive closed union `HookPayloadDTO` [NEW]:
      `type HookPayloadDTO = MatrixHookResultDTO | SynthesisDistillationDTO | StepOutputDTO | SanitizationResultDTO | BibliographyResultDTO | MetadataHookPayloadDTO | PassivityDetectionResultDTO | AnomalyDetectionResultDTO | MetricCalculationResultDTO | InputControlRatioResultDTO | InteractionAnalysisResultDTO | FlatteningHookOutputDTO`
    </action>
    <action>Update `HookDeltaDTO`:
      - Set `delta: Annotated[HookPayloadDTO | None, Field(default=None)]`.
      - Set `metadata_updates: Annotated[ExecutionMetadataDeltaDTO | None, Field(default=None)]`.
      - Remove `| dict[str, Any]` completely.
    </action>
    <action>In `backend_v2/models/dtos/step_output.py`, update `StepOutputDTO`:
      - Set `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)`.
      - Constrain `payload` to `StepPayloadValue` closed union.
    </action>
    <constraint invariant="the_zero_compromise_pledge">Strictly forbid `dict[str, Any]` in `HookDeltaDTO`. All payload fields must be typed Pydantic models.</constraint>
  </step>

  <step id="2" name="SOVEREIGN STATE REDUCER &amp; CONTEXT ROUTER DECOUPLING">
    <action>In `backend_v2/services/orchestrator/state_reducer.py`:
      - Modernize `merge_execution_inputs` to construct `ExecutionInputsDTO` via pure constructor instead of `base.model_copy(update={...})`.
      - Implement `reduce_hook_delta(current_state: HookState, delta_dto: HookDeltaDTO, step_id: str | None = None) -> tuple[HookState, list[TraceEvent]]`:
        * Merges `delta_dto.metadata_updates` into `ExecutionMetadata`.
        * Merges `global_context_vars` if present in delta.
        * Merges `dynamic_inputs` and `raw_inputs` into `ExecutionInputsDTO`.
        * Generates decision `TraceEvent` for context updates.
        * Returns newly constructed, immutable `HookState` and list of emitted `TraceEvent` instances.
    </action>
    <action>In `backend_v2/services/orchestrator/context_router.py`:
      - Delete `SnapshotState` class completely.
      - Refactor `normalize_and_validate_variable(path: str, steps: Sequence[StepOutputDTO]) -> str`:
        * Verify step presence directly against `steps` sequence: `found = any(dto.step_id == step_key for dto in steps)`.
        * Raise `AppException(ErrorCodes.RESOURCE_NOT_FOUND)` if step is missing.
        * Raise `AppException(ErrorCodes.VALIDATION_FAILED)` if legacy `.output` syntax is present.
      - Refactor `validate_routing_mode` to handle specific Pydantic `ValidationError`.
    </action>
    <action>In `backend_v2/services/orchestrator/dag_executor.py`:
      - Update call site at line 264 to pass `projector.snapshot` directly into `ContextRouter.normalize_and_validate_variable(path, projector.snapshot)`.
    </action>
    <constraint invariant="anti_god_file_dumping">State reduction must be isolated in `state_reducer.py`. ContextRouter must remain purely a router.</constraint>
  </step>

  <step id="3" name="EXECUTION STRATEGY DECOUPLING">
    <action>In `backend_v2/services/orchestrator/strategies/base.py`:
      - Refactor `run_pre_hooks` to delegate state merging to `state_reducer.reduce_hook_delta`.
      - Refactor `run_post_hooks` to delegate state merging to `state_reducer.reduce_hook_delta`.
      - Eliminate all `isinstance(delta, Mapping)` checks and manual dictionary-copying loops.
      - Remove unvalidated `model_copy(update={...})` calls.
    </action>
    <constraint invariant="single_pipeline_invariant_mandate">Both pre-hooks and post-hooks must flow through the identical sovereign state reduction pipeline.</constraint>
  </step>

  <step id="4" name="HOOK MODERNIZATION ACROSS 17 HOOK MODULES">
    <action>In each of the 17 hooks under `backend_v2/hooks/`, eliminate `.model_dump(mode="json")` and return typed DTOs directly:
      1. `atom_flattening.py`: Return `HookDeltaDTO(delta=output_payload)` where `output_payload` is `FlatteningHookOutputDTO`.
      2. `synthesis_distiller.py`: Return `HookDeltaDTO(delta=distillation_dto)`.
      3. `security.py`: Return `HookDeltaDTO(delta=SanitizationResultDTO(...))`.
      4. `references.py`: Return `HookDeltaDTO(delta=BibliographyResultDTO(...))`.
      5. `validation.py`: Return `HookDeltaDTO(delta=AnomalyDetectionResultDTO(...))`.
      6. `passivity_hook.py`: Return `HookDeltaDTO(delta=PassivityDetectionResultDTO(...))`.
      7. `metrics.py`: Return `HookDeltaDTO(delta=MetricCalculationResultDTO(...))`.
      8. `scoring.py`: Return `HookDeltaDTO(delta=scoring_dto)`.
      9. `interaction_hook.py`: Return `HookDeltaDTO(delta=InteractionAnalysisResultDTO(...))`.
      10. `linguistic_shield.py`: Return `HookDeltaDTO(delta=shield_dto)`.
      11. `translation_hook.py`: Return `HookDeltaDTO(delta=translation_dto)`.
      12. `contrastive_hook.py`: Return `HookDeltaDTO(delta=contrastive_dto)`.
      13. `tavily_search_hook.py`: Return `HookDeltaDTO(delta=search_result_dto)`.
      14. `wikipedia_hook.py`: Return `HookDeltaDTO(delta=wiki_result_dto)`.
      15. `document_preflight.py`: Return `HookDeltaDTO(delta=preflight_dto)`.
      16. `rag_preflight.py`: Return `HookDeltaDTO(delta=rag_dto)`.
      17. `rag_enrichment_hook.py`: Return `HookDeltaDTO(delta=enrichment_dto)`.
    </action>
    <constraint invariant="the_duct_tape_ban">Zero `.model_dump(mode="json")` calls inside hooks. DTOs must remain typed objects.</constraint>
  </step>

  <step id="5" name="TEST FIXTURE MODERNIZATION &amp; UNIT VERIFICATION">
    <action>Update unit test fixtures in:
      - `backend_v2/tests/unit/services/orchestrator/test_context_router.py`: Replace dict snapshots with typed `list[StepOutputDTO]`.
      - `backend_v2/tests/unit/services/orchestrator/test_state_reducer.py`: Add test cases for `reduce_hook_delta` with each payload type.
      - `backend_v2/tests/unit/services/orchestrator/strategies/test_base.py`: Verify hook execution with typed deltas.
      - `backend_v2/tests/unit/hooks/`: Update assertions to check DTO types instead of dictionary keys.
      - `backend_v2/tests/unit/test_dag_executor.py`: Verify direct snapshot passing.
    </action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_context_router.py backend_v2/tests/unit/services/orchestrator/test_state_reducer.py`.</action>
    <constraint invariant="anti_tdd_trap">Rewrite legacy test fixtures that expect dictionaries; never compromise domain typing for outdated tests.</constraint>
  </step>

  <step id="6" name="QUALITY GATES &amp; AST GUARDRAILS VERIFICATION">
    <action>Execute AST dict eradication audit: `uv run python scripts/audit_dict_eradication.py backend_v2/models/dtos backend_v2/services/orchestrator backend_v2/hooks --strict`.</action>
    <action>Execute global backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test`.</action>
    <action>Run Markdown boundaries audit: `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/plan_dict_to_dto_state_eradication.md`.</action>
    <constraint invariant="universal_quality_gate">All audit loops and quality gates must pass with zero warnings and zero failures.</constraint>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **Unit Test Suite for ContextRouter and StateReducer:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/orchestrator/test_context_router.py backend_v2/tests/unit/services/orchestrator/test_state_reducer.py -v
   ```
2. **Unit Test Suite for Execution Strategies:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/test_base.py -v
   ```
3. **Hook Modernization Verification:**
   ```powershell
   uv run pytest backend_v2/tests/unit/hooks/ -v
   ```
4. **AST Dict Eradication Audit:**
   ```powershell
   uv run python scripts/audit_dict_eradication.py backend_v2/models/dtos backend_v2/services/orchestrator backend_v2/hooks --strict
   ```
5. **Global Backend Audit Loop:**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test
   ```
6. **Markdown Boundaries Audit:**
   ```powershell
   uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/plan_dict_to_dto_state_eradication.md
   ```

### Anti-Happy-Path Test Scenarios (ISTQB Boundary Partitions)

1. **Negative Scenario 1: Raw Dictionary Passed to `HookDeltaDTO.delta`**
   - **Input:** `HookDeltaDTO(delta={"untyped": "payload"})`
   - **Expected Result:** Raises `pydantic.ValidationError` with `extra_forbidden` or `union_tag_invalid`. Zero naked dictionaries permitted in state deltas.

2. **Negative Scenario 2: Orphaned Step in `ContextRouter.normalize_and_validate_variable`**
   - **Input:** `path="$steps.step_nonexistent.data"`, `steps=[StepOutputDTO(step_id="step_1", ...)]`
   - **Expected Result:** Raises `AppException(ErrorCodes.RESOURCE_NOT_FOUND, status_code=500)` with message `"Fail-Fast: Required step 'step_nonexistent' not found in state (Orphaned Step)."`.

3. **Negative Scenario 3: Legacy V1 `.output` Notation in Variable Path**
   - **Input:** `path="$steps.step_1.output"`, `steps=[StepOutputDTO(step_id="step_1", ...)]`
   - **Expected Result:** Raises `AppException(ErrorCodes.VALIDATION_FAILED, status_code=400)` with message `"Fail-Fast: Legacy V1 '.output' variable format is strictly forbidden."`.

4. **Negative Scenario 4: Unvalidated Dictionary in `metadata_updates`**
   - **Input:** `HookDeltaDTO(metadata_updates={"arbitrary_key": 123})`
   - **Expected Result:** Raises `pydantic.ValidationError`. `metadata_updates` strictly requires `ExecutionMetadataDeltaDTO` with validated fields.
