# Phase 5: DTO Purification & Macro Orchestrator Simplification

**Overview:** Purify `EngineExecutionRequest` DTO by completely deleting `semaphore`, `running_event`, and `@property semaphore_cm`, purify `NodeExecutor.execute` signature, simplify `DAGExecutor` by removing macro-semaphore initialization and unmanaged background watcher tasks (`watch_running`), replace the two-commit `QUEUED` transition with an atomic synchronous transition to `ExecutionStatus.RUNNING` upon step dispatch with exactly one persistence commit, refactor orchestrator unit tests, and modernize AST concurrency guardrails to verify zero semaphore and event leakage across all 11 decoupled modules plus `dag_executor.py`.

**Source:** @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md#L153-L189] Phase 5: DTO Purification & Macro Orchestrator Simplification

**Target Files:**
- `[MODIFY]` @[backend_v2/models/dtos/engine.py#L61-L132]
- `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_engine.py#L101-L148]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L189-L372]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L375-L1351]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L752-L1069]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L192-L259]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L346-L426]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L429-L465]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L468-L505]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L508-L586]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L589-L667]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L747-L864]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1187-L1266]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1724-L1797]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1870-L1940]
- `[MODIFY]` @[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L70-L81]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/dtos/engine.py#L61-L132]` (`EngineExecutionRequest`) | Concurrency primitives (`asyncio.Semaphore`, `asyncio.Event`) and nullcontext wrapper property (`@property def semaphore_cm`) residing inside a domain DTO. | Pure execution DTO configured with `ConfigDict(strict=True, extra="forbid", frozen=True, arbitrary_types_allowed=True)`. In-memory runtime handles safely encapsulated without serialization impedance. | Pruned 3 dead/concurrency fields (`semaphore`, `running_event`, `semaphore_cm`). Eradicated multi-hop plumbing across 6 layers. | `uv run pytest backend_v2/tests/unit/models/dtos/test_engine.py -v`. Direct attribute access asserts absence of `semaphore` and `semaphore_cm`. |
| `@[backend_v2/services/orchestrator/dag_executor.py#L189-L372]`, `@[backend_v2/services/orchestrator/dag_executor.py#L752-L1069]` (`NodeExecutor`, `DAGExecutor`) | Macro-semaphore `asyncio.Semaphore(max_concurrent_llm_steps)`, `running_event = asyncio.Event()`, `watch_running()` background task, and `watcher_task.cancel()`. | The existing `QUEUED` transition block (L819-L828) is REPLACED in place by a single `ExecutionStatus.RUNNING` transition: state mutation inside `_update_lock`, exactly one `_safe_commit()` awaited AFTER lock release (`async_io_lock_isolation_mandate`), immediately prior to dispatching `NodeExecutor.execute`. | Pruned 22 lines of complex background event watching; eliminated unmanaged background tasks evading `TaskGroup`. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py -v`. Atomic transition to `RUNNING` verified upon dispatch. |
| `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L70-L81]` | Obsolete AST assertion requiring `asyncio.Semaphore` in `dag_executor.py` (L81). | Modernized AST guardrail asserting `res["semaphore"] is False` and `res["event"] is False` in the 11 decoupled modules, `res["semaphore"] is False` in `dag_executor.py`, while retaining `res["semaphore"] is True` in `provider.py`. | Pruned obsolete AST concurrency assertion, vacuous missing-file passes, and unguarded `asyncio.Event` regressions. | `uv run pytest backend_v2/tests/unit/test_ast_concurrency_guardrails.py -v`; asserts `res["semaphore"] is False` and `res["event"] is False` for the 11 modules, with `assert filepath.exists()` in `scan_file_for_concurrency` (L63-L67). |

## Pre-Implementation Cleanups

1. `[CLEANUP]` Ensure Phase 4 strategy layer harmonization is committed and passing.
2. `[CLEANUP]` Delete `watcher_task` and `running_event` references from `dag_executor.py` (L830-L852, L931).
3. `[CLEANUP]` Delete `if "running_event" in kwargs` from `fake_node_execute` in `test_dag_executor.py#L849-L850`.
4. `[CLEANUP]` Refactor `test_dag_executor_hoists_and_passes_semaphore` into `test_dag_executor_pure_dispatch_without_semaphore`.

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 4. Verify `NodeStrategy` and its implementations execute without concurrency plumbing.</action>
    <action>Look forward: Verify that purifying `EngineExecutionRequest` and simplifying `DAGExecutor` completely decouples the macro orchestrator and domain DTOs from in-memory concurrency primitives.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md]) and the Tracker document (@[docs/epic/EPIC_155_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_155/05_phase5_plan.md] @[docs/epic/EPIC_155_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>EngineExecutionRequest DTO contains zero semaphore, running_event, or semaphore_cm attributes, and unused import asyncio is deleted.</item>
    <item>NodeExecutor.execute signature in dag_executor.py has zero semaphore or running_event parameters.</item>
    <item>DAGExecutor top-level semaphore, running_event, watch_running task, and watcher_task.cancel() are completely eradicated.</item>
    <item>Step dispatch performs atomic transition to ExecutionStatus.RUNNING inside _update_lock with exactly one status commit, and ExecutionStatus.QUEUED is never emitted by DAGExecutor.</item>
    <item>test_engine.py verifies EngineExecutionRequest rejects semaphore and running_event arguments.</item>
    <item>test_dag_executor.py watcher test is refactored to verify synchronous RUNNING transition on dispatch.</item>
    <item>test_ast_concurrency_guardrails.py asserts res["semaphore"] is False for dag_executor.py and the 11 decoupled modules, res["event"] is False for the 11 decoupled modules, and res["semaphore"] is True for provider.py.</item>
    <item>test_concurrency_fuzzer.py Stage B proves exact peak equality: assert peak_concurrent == min(expected_limit, 10).</item>
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
    <anti_target>Do NOT delete ExecutionStatus.QUEUED enum member from models/enums.py (persisted database records and Flutter client reference it).</anti_target>
    <anti_target>Do NOT modify LiteLLMProvider provider.py dynamic semaphore pool (sole authoritative micro-concurrency SSOT).</anti_target>
    <anti_target>Do NOT modify synthesis_worker.py concurrency boundary (out of scope for EPIC 155).</anti_target>
    <anti_target>Do NOT modify ExtractiveSensorService evaluate_atom_boolean_batch internal semaphore (out of scope for EPIC 155).</anti_target>
    <anti_target>Do NOT modify Tavily search client rate limiter (out of scope for EPIC 155).</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/models/dtos/engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
  </touched_artifacts>

  <contract_freeze>
    <interface name="EngineExecutionRequest">
      <signature>class EngineExecutionRequest(V2CoreBase):</signature>
      <constraint>EngineExecutionRequest enforces ConfigDict(arbitrary_types_allowed=True, strict=True, extra="forbid", frozen=True) without concurrency or event fields.</constraint>
    </interface>
    <interface name="NodeExecutor.execute">
      <signature>async def execute(self, step: StepRule, projector: StateProjector, context: StrategyContext, frozen_ctx: FrozenContext | None = None, trace: list[TraceEvent] | None = None, progress_callback: Callable[[int, int], Awaitable[None]] | None = None) -> list[TraceEvent]:</signature>
      <constraint>NodeExecutor.execute signature is frozen without semaphore or running_event parameters.</constraint>
    </interface>
  </contract_freeze>

  <test_contracts>
    <test name="test_engine_execution_request_pure_fields" category="positive">
      <input>valid EngineExecutionRequest instantiation</input>
      <expected>instantiates successfully without semaphore or running_event attributes</expected>
    </test>
    <test name="test_engine_execution_request_rejects_semaphore_kwarg" category="error_path">
      <input>EngineExecutionRequest(..., semaphore=asyncio.Semaphore(1))</input>
      <expected>raises pydantic.ValidationError (extra='forbid')</expected>
    </test>
    <test name="test_engine_execution_request_rejects_running_event_kwarg" category="error_path">
      <input>EngineExecutionRequest(..., running_event=asyncio.Event())</input>
      <expected>raises pydantic.ValidationError (extra='forbid')</expected>
    </test>
    <test name="test_dag_executor_synchronous_running_dispatch_transitions_step" category="positive">
      <input>DAG step dispatch</input>
      <expected>step transitions to ExecutionStatus.RUNNING inside _update_lock with exactly one status commit, and QUEUED is never emitted</expected>
    </test>
    <test name="test_dag_executor_pure_dispatch_without_semaphore" category="positive">
      <input>DAG executor dispatch</input>
      <expected>NodeExecutor.execute call_kwargs contains neither 'semaphore' nor 'running_event'</expected>
    </test>
    <test name="test_concurrency_fuzzer_peak_limit_stage_b" category="boundary">
      <input>DAG executor without macro-semaphore gating</input>
      <expected>assert peak_concurrent == min(expected_limit, 10) proving both bound enforcement and throughput increase</expected>
    </test>
  </test_contracts>

  <step id="5.1" name="PURIFY_ENGINE_EXECUTION_REQUEST_DTO">
    <action>In `@[backend_v2/models/dtos/engine.py#L61-L132]`, remove `semaphore: Annotated[asyncio.Semaphore | None, ...]` and `running_event: Annotated[asyncio.Event | None, ...]` fields (L100-L101), update the class docstring at L64 to drop "telemetry hooks", delete attribute docstring entries at L75-L76, and remove `import asyncio` at L8 (the inline `import contextlib` at L130 is deleted with the property).</action>
    <action>In `@[backend_v2/models/dtos/engine.py#L61-L132]`, remove `@property def semaphore_cm(self) -> Any:` context manager property.</action>
    <action>In `@[backend_v2/models/dtos/engine.py#L61-L132]`, retain `model_config = ConfigDict(arbitrary_types_allowed=True, strict=True, extra="forbid", frozen=True)` to safely permit in-memory execution handles (`bound_client: LLMClient`, `compiled_schema: type[BaseModel]`, and callback Callables) without triggering `PydanticSchemaGenerationError` at import time.</action>
  </step>

  <step id="5.2" name="UPDATE_ENGINE_DTO_TESTS">
    <action>In `@[backend_v2/tests/unit/models/dtos/test_engine.py#L101-L148]`, refactor `test_engine_execution_request_semaphore_cm_and_fields` to `test_engine_execution_request_pure_fields`, eliminating assertions on `req.semaphore_cm` and `req_sem.semaphore_cm` while verifying that `EngineExecutionRequest` enforces strict immutable fields and rejects `semaphore` or `running_event` arguments.</action>
  </step>

  <step id="5.3" name="PURIFY_NODE_EXECUTOR_AND_SIMPLIFY_DAG_EXECUTOR">
    <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L189-L372]`, remove `semaphore: asyncio.Semaphore` and `running_event: asyncio.Event | None = None` from `NodeExecutor.execute` signature.</action>
    <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L375-L1351]`, remove top-level `semaphore = asyncio.Semaphore(get_settings().max_concurrent_llm_steps)` initialization at L733.</action>
    <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L375-L1351]`, eradicate `running_event = asyncio.Event()`, `watch_running()` function, and `watcher_task = asyncio.create_task(watch_running())` at L830-L852.</action>
    <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L375-L1351]`, REPLACE the `ExecutionStatus.QUEUED` assignment block at L819-L828 with a direct `ExecutionStatus.RUNNING` assignment inside `_update_lock` immediately prior to dispatching `node_executor.execute`, followed by exactly ONE `_safe_commit()` call executed AFTER the lock is released. No second status commit is permitted. The `ExecutionStatus.QUEUED` enum member is RETAINED (persisted records and the Flutter client reference it) but is no longer emitted by `DAGExecutor`.</action>
    <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L375-L1351]`, remove `semaphore=semaphore` and `running_event=running_event` from `node_executor.execute` call at L923-L924.</action>
    <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L375-L1351]`, remove `watcher_task.cancel()` in the `finally:` block at L931.</action>
  </step>

  <step id="5.4" name="UPDATE_DAG_EXECUTOR_WATCHER_TEST">
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L747-L864]`, delete the `if "running_event" in kwargs and kwargs["running_event"]: kwargs["running_event"].set()` block at L849-L850 from `fake_node_execute`.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1724-L1797]`, refactor `test_dag_executor_watch_running_event_transitions_queued_step` into `test_dag_executor_synchronous_running_dispatch_transitions_step`, asserting that the step transitions to `ExecutionStatus.RUNNING` inside `_update_lock` on dispatch, that `ExecutionStatus.QUEUED` is never committed for the step, and that exactly one status commit occurs per dispatch.</action>
  </step>

  <step id="5.5" name="UPDATE_DAG_EXECUTOR_SEMAPHORE_TESTS">
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L346-L426]`, remove `semaphore=semaphore` from `executor.execute()` in `test_node_executor_injects_synthesis_engine`.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L429-L465]`, remove `semaphore=semaphore` from `executor.execute()` in `test_node_executor_blueprint_missing_error`.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L468-L505]`, remove `semaphore=semaphore` from `executor.execute()` in `test_node_executor_step_def_not_found_error`.</action>
    <action>VERIFICATION-ONLY (RETRACTED ACTION): `test_node_executor_injects_tda_and_prompt_engines` in `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L508-L586]` contains zero `semaphore` tokens; this is a NO-OP and MUST NOT be edited.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L589-L667]`, remove `semaphore=semaphore` from `executor.execute()` in `test_node_executor_normalizes_input_mappings_and_handles_exception`.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1187-L1266]`, remove `semaphore=asyncio.Semaphore(1)` from `node_executor.execute()` call.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1870-L1940]`, remove `semaphore=asyncio.Semaphore(1)` from `node_executor.execute()` call.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L192-L259]`, refactor `test_dag_executor_hoists_and_passes_semaphore` into `test_dag_executor_pure_dispatch_without_semaphore`, asserting that `call_kwargs` passed to `NodeExecutor.execute` contains neither `semaphore` nor `running_event`.</action>
  </step>

  <step id="5.6" name="UPDATE_AST_CONCURRENCY_GUARDRAILS">
    <action>In `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L70-L81]`, update `test_ast_semaphore_guardrail` to assert `res["semaphore"] is False` for `dag_executor.py` (`assert res["semaphore"] is False, f"Leaky asyncio.Semaphore found in {dag_executor_path}"`), proving pure compute decoupling while retaining `res["semaphore"] is True` for `provider.py`.</action>
    <action>In `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L70-L81]`, extend the `res["semaphore"] is False` assertion to the closed set of 11 modules (specifically and exhaustively: `backend_v2/models/dtos/engine.py`, `backend_v2/services/orchestrator/engines/base.py`, `backend_v2/services/orchestrator/engines/prompt_engine.py`, `backend_v2/services/orchestrator/engines/synthesis_engine.py`, `backend_v2/services/orchestrator/engines/tda_engine.py`, `backend_v2/services/orchestrator/two_pass_atomizer.py`, `backend_v2/services/orchestrator/enriched_dag_executor.py`, `backend_v2/services/orchestrator/sliding_window_linker.py`, `backend_v2/services/orchestrator/strategies/base.py`, `backend_v2/services/orchestrator/strategies/logic.py`, `backend_v2/services/orchestrator/strategies/llm.py`), each guarded by `assert path.exists()` per Step 1.5 so that a moved file fails loudly instead of passing vacuously.</action>
    <action>In `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py]`, add `found_event` detection to `ConcurrencyVisitor` (detecting `asyncio.Event` attribute and `from asyncio import Event` alias, mirroring L21-L33), and assert `res["event"] is False` for the closed set of 11 decoupled modules (specifically excluding `dag_executor.py`, which legitimately retains `asyncio.Event` for internal DAG step coordination at L722). Add negative unit tests mirroring L108-L129 proving `asyncio.Event` is detected and blocked.</action>
  </step>

  <validation_gate>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/engine.py backend_v2/services/orchestrator/dag_executor.py --test --ast-strict`</action>
    <action>Run `uv run pytest backend_v2/tests/unit/models/dtos/test_engine.py backend_v2/tests/unit/services/orchestrator/test_dag_executor.py backend_v2/tests/unit/test_ast_concurrency_guardrails.py -v`</action>
    <action>Run `uv run pytest backend_v2/tests/unit/test_concurrency_fuzzer.py -v`</action>
    <action>Assert zero occurrences of "asyncio.Semaphore" in dag_executor.py and models/dtos/engine.py</action>
    <action>Assert zero occurrences of "running_event" across backend_v2/models/dtos/engine.py and backend_v2/services/orchestrator/dag_executor.py</action>
  </validation_gate>
</execution_protocol>
```
