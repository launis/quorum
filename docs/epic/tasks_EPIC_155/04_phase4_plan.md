# Phase 4: Strategy Layer Harmonization

**Overview:** Harmonize `NodeStrategy` base protocol and its implementations (`LogicNodeStrategy`, `LLMNodeStrategy`) by removing dead `semaphore` and `running_event` parameters, deleting unused `import asyncio` statements across strategy modules, eradicating premature `running_event.set()` triggers and DTO parameter packing, updating `NodeExecutor.execute` dispatch, and refactoring strategy test suites to eliminate concurrency fixtures.

**Source:** @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md#L129-L151] Phase 4: Strategy Layer Harmonization

**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/base.py#L119-L322]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/base.py#L184-L211]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/logic.py#L32-L234]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/logic.py#L43-L234]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L82-L1012]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L223-L1012]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L189-L372]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_logic.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/services/orchestrator/strategies/base.py#L184-L211]` (`NodeStrategy`) | `semaphore: asyncio.Semaphore` and `running_event: asyncio.Event \| None` in `NodeStrategy.execute` signature. | Pure domain signature `async def execute(self, step: StepRule, projector: StateProjector, context: StrategyContext, frozen_ctx: FrozenContext \| None, trace: list[TraceEvent] \| None, progress_callback: ...) -> list[TraceEvent]:`. Unused `import asyncio` deleted. | Eradicated interface pollution forcing dead arguments on non-LLM node strategies. | MyPy strict mode verification across all strategy implementations. |
| `@[backend_v2/services/orchestrator/strategies/logic.py#L43-L234]` (`LogicNodeStrategy`) | Dead `semaphore` parameter and manual `if running_event is not None: running_event.set()` trigger. Unused `import asyncio`. | Clean `execute()` implementation with pure hook execution and state delta merging. | Pruned dead concurrency parameter and telemetry event mutation in native logic step. | `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py -v`. |
| `@[backend_v2/services/orchestrator/strategies/llm.py#L223-L1012]` (`LLMNodeStrategy`) | Premature `if running_event: running_event.set()` at L255-L256, and packing `semaphore`/`running_event` into `EngineExecutionRequest` across 3 branches. | Pure execution strategy delegating to resolved `ExecutionEngine` without concurrency or event arguments. Unused `import asyncio` deleted. | Pruned premature telemetry signaling and parameter bundling. | `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py -v`. |
| `@[backend_v2/services/orchestrator/dag_executor.py#L189-L372]` (`NodeExecutor`) | Passing dead `semaphore` and `running_event` arguments from `NodeExecutor.execute` to `strategy_impl.execute` at L355-L356. | Clean dispatch to `strategy_impl.execute` with pure domain arguments. | Pruned 2 forwarding arguments across orchestrator-strategy boundary. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py -v`. |

## Pre-Implementation Cleanups

1. `[CLEANUP]` Ensure Phase 3 sub-executor decoupling is committed and passing.
2. `[CLEANUP]` Delete unused `import asyncio` in `base.py` (L5), `logic.py` (L3), and `llm.py` (L9).
3. `[CLEANUP]` Eliminate premature `running_event.set()` from `logic.py` (L74-L75) and `llm.py` (L255-L256).

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 3. Verify `TwoPassAtomizer`, `EnrichedDagExecutor`, and `SlidingWindowLinker` execute without semaphore plumbing.</action>
    <action>Look forward: Verify that modernizing `NodeStrategy.execute` signatures eliminates dead parameters from `LogicNodeStrategy` and prepares `EngineExecutionRequest` for DTO purification.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md]) and the Tracker document (@[docs/epic/EPIC_155_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_155/04_phase4_plan.md] @[docs/epic/EPIC_155_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>NodeStrategy.execute signature in base.py has zero semaphore or running_event parameters and unused import asyncio is deleted.</item>
    <item>LogicNodeStrategy.execute signature in logic.py has zero semaphore or running_event parameters, unused import asyncio is deleted, and running_event.set() is removed.</item>
    <item>LLMNodeStrategy.execute signature in llm.py has zero semaphore or running_event parameters, unused import asyncio is deleted, running_event.set() is removed, and DTO construction omits concurrency arguments.</item>
    <item>NodeExecutor.execute in dag_executor.py dispatches to strategy_impl.execute without passing semaphore or running_event.</item>
    <item>test_logic.py, test_llm.py, and test_llm_cost_tracking.py pass 100% without concurrency fixtures.</item>
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
    <anti_target>Do NOT remove semaphore or running_event from NodeExecutor.execute signature during Phase 4 (quarantined strictly for Phase 5 to preserve run_step_wrapper compatibility).</anti_target>
    <anti_target>Do NOT remove semaphore or running_event from EngineExecutionRequest DTO during Phase 4 (quarantined strictly for Phase 5).</anti_target>
    <anti_target>Do NOT modify DAGExecutor.watch_running or macro semaphore during Phase 4 (quarantined strictly for Phase 5).</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/strategies/base.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/logic.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
  </touched_artifacts>

  <contract_freeze>
    <interface name="NodeStrategy.execute">
      <signature>async def execute(self, step: StepRule, projector: StateProjector, context: StrategyContext, frozen_ctx: FrozenContext | None = None, trace: list[TraceEvent] | None = None, progress_callback: Callable[[int, int], Awaitable[None]] | None = None) -> list[TraceEvent]:</signature>
      <constraint>Base strategy interface is frozen with zero concurrency or event parameters.</constraint>
    </interface>
  </contract_freeze>

  <test_contracts>
    <test name="test_logic_strategy_execute_without_concurrency" category="positive">
      <input>valid step, projector, context</input>
      <expected>executes native logic hook and merges state delta without dead semaphore parameter</expected>
    </test>
    <test name="test_llm_node_strategy_execute_without_concurrency" category="positive">
      <input>valid step, projector, context</input>
      <expected>dispatches to ExecutionEngine without premature running_event signaling</expected>
    </test>
    <test name="test_strategy_rejects_semaphore_argument" category="error_path">
      <input>strategy.execute(step, projector, context, semaphore=asyncio.Semaphore(1))</input>
      <expected>raises TypeError (unexpected keyword argument 'semaphore')</expected>
    </test>
    <test name="test_strategy_rejects_running_event_argument" category="error_path">
      <input>strategy.execute(step, projector, context, running_event=asyncio.Event())</input>
      <expected>raises TypeError (unexpected keyword argument 'running_event')</expected>
    </test>
  </test_contracts>

  <step id="4.1" name="HARMONIZE_NODE_STRATEGY_BASE_PROTOCOL">
    <action>In `@[backend_v2/services/orchestrator/strategies/base.py#L119-L322]`, remove `semaphore: asyncio.Semaphore` and `running_event: asyncio.Event | None = None` parameters from `NodeStrategy.execute` signature at L192-L193 and the corresponding docstring entries at L204-L205. Delete unused `import asyncio` at L5 (Ruff F401).</action>
  </step>

  <step id="4.2" name="HARMONIZE_LOGIC_NODE_STRATEGY">
    <action>In `@[backend_v2/services/orchestrator/strategies/logic.py#L32-L234]`, remove `semaphore: asyncio.Semaphore` and `running_event: asyncio.Event | None = None` from `LogicNodeStrategy.execute` signature at L50-L51 and the corresponding docstring entries at L62-L63. Delete unused `import asyncio` at L3 (Ruff F401).</action>
    <action>In `@[backend_v2/services/orchestrator/strategies/logic.py#L32-L234]`, remove `if running_event is not None: running_event.set()` at L74-L75.</action>
  </step>

  <step id="4.3" name="HARMONIZE_LLM_NODE_STRATEGY">
    <action>In `@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1012]`, remove `semaphore: asyncio.Semaphore` and `running_event: asyncio.Event | None = None` from `LLMNodeStrategy.execute` signature at L230-L231 and the corresponding docstring entries at L242-L243. Delete unused `import asyncio` at L9 (Ruff F401).</action>
    <action>In `@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1012]`, remove premature `if running_event: running_event.set()` at L255-L256.</action>
    <action>In `@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1012]`, eliminate `semaphore` and `running_event` arguments when constructing `EngineExecutionRequest` instances at L797-L798, L841-L842, and L860-L861.</action>
  </step>

  <step id="4.4" name="HARMONIZE_NODE_EXECUTOR_STRATEGY_DISPATCH">
    <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L189-L372]`, eliminate `semaphore` and `running_event` arguments passed from `NodeExecutor.execute` to `strategy_impl.execute` at L355-L356, maintaining intra-file caller signature compatibility with `run_step_wrapper` until Phase 5.</action>
  </step>

  <step id="4.5" name="UPDATE_STRATEGY_UNIT_TESTS">
    <action>In `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]`, refactor `test_execute_sets_running_event_and_merges_state_delta` into `test_execute_merges_state_delta`, removing `semaphore` and `running_event` parameters and assertions across all test cases (L41/L44, L55/L58, L76/L97, L117-L146, L161/L183, L198/L215, L234/L251, L308/L323).</action>
    <action>In `@[backend_v2/tests/unit/test_logic.py]`, update `test_logic_strategy_missing_blueprint`, `test_logic_strategy_raw_inputs_extraction_bug`, and `test_logic_strategy_signature_parity` to remove `semaphore=asyncio.Semaphore(2)` arguments from `strategy.execute()` calls.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`, refactor `test_execute_sets_running_event_and_handles_string_inputs` into `test_execute_handles_string_inputs`, removing `running_event` and `semaphore` fixtures across all 27 test executions.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`, remove `running_event` and `semaphore` fixtures at L127-L128 and L270.</action>
  </step>

  <validation_gate>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/ --test --ast-strict`</action>
    <action>Run `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py backend_v2/tests/unit/test_logic.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py -v`</action>
    <action>Assert zero occurrences of "running_event.set()" in strategies/logic.py and strategies/llm.py</action>
    <action>Assert zero unused import asyncio in strategies/base.py, strategies/logic.py, and strategies/llm.py</action>
  </validation_gate>
</execution_protocol>
```
