<!--
<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
</required_context_rules>
-->

# EPIC 155: Engine Concurrency Decoupling & Pure Compute Architecture (with F-03 Protocol Inheritance)

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Executive Summary & Problem Statement
Currently, Quorum's execution engines (`PromptEngine`, `SynthesisEngine`, `TDAEngine`) and node execution strategies violate the Single Responsibility Principle (SRP), the Pure Compute Model, and Protocol Symmetry. In-memory Python runtime concurrency primitives (`asyncio.Semaphore`, `asyncio.Event`) are threaded through four distinct architectural layers:
1. `DAGExecutor.run_step_wrapper` instantiates a macro-level `asyncio.Semaphore(max_concurrent_llm_steps)` and an `asyncio.Event` (`running_event`), launching a background watcher task (`watch_running`) to observe when the step transitions from `QUEUED` to `RUNNING`.
2. `NodeExecutor.execute` forwards these primitives to `NodeStrategy` implementations (`LLMNodeStrategy`, `LogicNodeStrategy`).
3. `LLMNodeStrategy` packs both `semaphore` and `running_event` into the `EngineExecutionRequest` DTO, while also prematurely signaling `running_event.set()` at method entry (violating the `atomic_telemetry_signaling_mandate`).
4. Individual execution engines interpret these fields with conflicting semantics:
   - `PromptEngine` and `SynthesisEngine` acquire `async with request.semaphore_cm:` at the top level and signal `running_event.set()` inside the lock.
   - `TDAEngine` signals `running_event.set()` at entry and forwards `request.semaphore` downwards into `TwoPassAtomizer.execute_phase_0` and `EnrichedDagExecutor.execute_graph`.
   - `LogicNodeStrategy` takes `semaphore` as a dead parameter solely to satisfy the `NodeStrategy` abstract base method signature.

Furthermore, execution engines suffered from structural protocol divergence and technical debt (Finding F-03 & Engine Parity):
- `TDAEngine(ExecutionEngine)` and `PromptEngine(ExecutionEngine)` lacked the PEP 698 `@override` decorator on `execute()`.
- `SynthesisEngine` was defined as a bare class (`class SynthesisEngine:`) without formal `ExecutionEngine(Protocol)` inheritance, without `@override`, and contained legacy `ValueError` duct-tape at L159 and L209 instead of structured `AppException(ErrorCodes.VALIDATION_FAILED)`.
- Test suites (`test_synthesis_engine.py`, `test_tda_engine.py`) relied on naked dictionaries (`dict[str, Any]` in `make_atom`) and defensive `.get()` dictionary lookups in assertions, while omitting formal ISTQB protocol subclass and instance assertions.

### 1.2 Core Architectural Antipatterns
- **Leaky Abstraction & Protocol Divergence:** `ExecutionEngine` implementations do not exhibit behavioral parity. `SynthesisEngine` lacked protocol inheritance entirely. `TDAEngine` requires an architectural exception because acquiring a top-level macro-semaphore across a multi-minute DAG evaluation would cause resource starvation or re-entrancy deadlocks when child nodes attempt to acquire the same semaphore.
- **Non-Serializable DTOs:** `EngineExecutionRequest` carries `asyncio.Semaphore` and `asyncio.Event`, forcing `ConfigDict(arbitrary_types_allowed=True)`. This couples the request payload to a single in-memory Python process and blocks clean serialization across distributed Arq worker boundaries or RPC boundaries.
- **Redundant Concurrency Layers:** `LiteLLMProvider` (`backend_v2/llm/provider.py`) already maintains its own authoritative dynamic semaphore registry (`_semaphores`) to throttle HTTP-level requests based on provider RPM/TPM thresholds. The macro-semaphore in `DAGExecutor` is an imprecise surrogate that throttles workflow step entry rather than physical token and request rate limits.
- **Fragile Telemetry Coupling:** `DAGExecutor` relies on an asynchronous background task (`watcher_task = asyncio.create_task(watch_running())`) to observe `running_event.wait()`. If a step crashes before signaling, or if an engine signals prematurely, step status reporting becomes desynchronized.

### 1.3 Strategic Scope & Objective
EPIC 155 completely eradicates `semaphore` and `running_event` from `EngineExecutionRequest`, `ExecutionEngine`, all concrete engines, and all node strategies while simultaneously achieving 100% Protocol Inheritance and Type Parity across `SynthesisEngine`, `PromptEngine`, and `TDAEngine`. Concurrency limiting is consolidated exclusively at the physical I/O boundary (`LLMClient` / `LiteLLMProvider`), while step status transitions (`QUEUED` $\rightarrow$ `RUNNING`) are owned directly and deterministically by `DAGExecutor` upon step dispatch. Execution engines become 100% pure computational pipelines: *Inputs In $\rightarrow$ Projected Results Out*.

### 1.4 Quantitative Scope & Blast Radius Validation

| Target Layer / Archetype | Affected Files (Relative Path) | Direct Violations & Deprecations | Target Modernization Pattern |
| :--- | :--- | :--- | :--- |
| **Domain DTOs** | `@[backend_v2/models/dtos/engine.py#L61-L132]` | `semaphore`, `running_event`, `@property semaphore_cm` | Pure compute `EngineExecutionRequest` with in-memory execution handles (`strict=True, extra="forbid", frozen=True, arbitrary_types_allowed=True`). |
| **Engine Protocols** | `@[backend_v2/services/orchestrator/engines/base.py#L11-L31]` | Legacy concurrency docstring references | Zero-semaphore, stateless `ExecutionEngine(Protocol)` definition. |
| **Concrete Engines** | `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L74]`<br>`@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`<br>`@[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]` | Macro `async with request.semaphore_cm:`, `running_event.set()`, missing `@override`, bare class in `SynthesisEngine`, `ValueError` duct-tape (L159, L209), dead `AliasEngine` import (L29) | `ExecutionEngine` protocol inheritance, PEP 698 `@override`, pure compute dispatch, structured `AppException(ErrorCodes.VALIDATION_FAILED)`, dead import pruning. |
| **Sub-Executors** | `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L39-L586]`<br>`@[backend_v2/services/orchestrator/enriched_dag_executor.py#L32-L218]` | `semaphore: asyncio.Semaphore \| None` parameters, local `async with sem:` chunk locks | Removal of redundant semaphore parameters; delegation of concurrency throttling to `LiteLLMProvider`. |
| **Node Strategies** | `@[backend_v2/services/orchestrator/strategies/base.py#L181-L208]`<br>`@[backend_v2/services/orchestrator/strategies/logic.py#L42-L224]`<br>`@[backend_v2/services/orchestrator/strategies/llm.py#L224-L1010]` | `semaphore` and `running_event` in `NodeStrategy.execute`, premature `running_event.set()` | Pure data strategy signatures without concurrency or event plumbing. |
| **Macro Orchestrator** | `@[backend_v2/services/orchestrator/dag_executor.py#L189-L372]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L749-L1065]` | `NodeExecutor.execute(semaphore, running_event)`, `asyncio.Semaphore(max_concurrent_llm_steps)`, `watch_running()` background task, `watcher_task.cancel()` | Synchronous state transition to `ExecutionStatus.RUNNING` inside `_update_lock` on dispatch; elimination of unmanaged background watcher tasks. |
| **Engine & DTO Unit Tests** | `@[backend_v2/tests/unit/models/dtos/test_engine.py#L101-L148]`<br>`@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]`<br>`@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`<br>`@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]`<br>`@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py]` | Tests verifying `semaphore_cm`, `semaphore`, and `running_event.is_set()`; naked `dict[str, Any]` in `make_atom`; defensive `.get()` lookups; missing protocol inheritance assertions | Protocol subclass/isinstance assertions, pure DTO fixtures, typed `DraftExtractedAtom`, direct dictionary subscripts (`exc_info.value.details["error_code"]`). |
| **Strategy & Orchestrator Tests** | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]`<br>`@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`<br>`@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`<br>`@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L174-L243]`<br>`@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L707-L820]`<br>`@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1131-L1212]`<br>`@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1666-L1737]`<br>`@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1808-L1882]` | Invocations passing `semaphore` and `running_event`; `node_executor.execute(semaphore=...)` calls in tests; `test_dag_executor_hoists_and_passes_semaphore`; `test_dag_executor_watch_running_event_transitions_queued_step`; `hasattr` reflection in `test_logic.py` (L57, L281) | Clean signature testing without concurrency fixtures; refactoring watcher and semaphore tests to assert atomic status transition and pure dispatch without concurrency plumbing; direct attribute access. |
| **AST Concurrency Guardrails** | `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L70-L81]` | Obsolete AST assertion requiring `asyncio.Semaphore` in `dag_executor.py` (L81) | Modernized AST guardrail asserting `res["semaphore"] is False` in `dag_executor.py` while retaining `res["semaphore"] is True` in `provider.py`. |

---

## 2. Architectural Impact & Compliance Matrix

### 2.1 Deprecations & Sunset List (`What We Will REMOVE`)

| Target Component | Deprecated Symbol / Logic | Reason for Removal | Migration Destination |
| :--- | :--- | :--- | :--- |
| `@[backend_v2/models/dtos/engine.py#L61-L132]` | `semaphore: asyncio.Semaphore \| None` field | In-memory concurrency primitive polluting domain DTO; prevents clean JSON serialization. | Consolidated into `LLMClient` / `LiteLLMProvider` dynamic semaphore pool. |
| `@[backend_v2/models/dtos/engine.py#L61-L132]` | `running_event: asyncio.Event \| None` field | Leaky telemetry callback; couples engine execution to orchestrator state machine. | Handled directly by `DAGExecutor` upon step dispatch. |
| `@[backend_v2/models/dtos/engine.py#L61-L132]` | `@property def semaphore_cm(self) -> Any:` | Nullcontext wrapper for nullable semaphore. | INTENTIONALLY DROPPED. Engines no longer manage semaphore context managers. |
| `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L74]` | `async with request.semaphore_cm:` block & `request.running_event.set()` | Macro-level locking inside leaf engine. | INTENTIONALLY DROPPED. Direct invocation of `self.task_executor.execute_structured_task`. |
| `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]` | `async with request.semaphore_cm:` block & any `running_event` signaling | Macro-level locking inside synthesis engine. | INTENTIONALLY DROPPED. Direct invocation of `self._executor.execute_structured_task`. |
| `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L29]` | `from backend_v2.utils.alias_engine import AliasEngine` | Dead, unused import polluting module namespace. | INTENTIONALLY DROPPED. |
| `@[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]` | `if request.running_event: request.running_event.set()` at L68-L69 | Premature telemetry trigger outside domain logic. | INTENTIONALLY DROPPED. Orchestrator marks step RUNNING upon dispatch. |
| `@[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]` | Passing `semaphore=request.semaphore` at L194 & L229 | Multi-hop parameter chaining to child executors. | INTENTIONALLY DROPPED. Child executors rely on `LLMClient` concurrency boundaries. |
| `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L73-L142]` | `semaphore: asyncio.Semaphore \| None = None` parameter in `execute_phase_0` | Redundant internal semaphore instantiation in `TaskGroup`. | Consolidated to `LLMClient` provider-level rate-limiting. |
| `@[backend_v2/services/orchestrator/enriched_dag_executor.py#L50-L218]` | `semaphore: asyncio.Semaphore \| None = None` parameter & `async with sem:` | Redundant chunk-level semaphore lock around `ExtractiveSensorService`. | Consolidated to `LLMClient` provider-level rate-limiting. |
| `@[backend_v2/services/orchestrator/strategies/base.py#L181-L208]` | `semaphore: asyncio.Semaphore` & `running_event: asyncio.Event \| None` in `NodeStrategy.execute` | Interface pollution forcing dead arguments on non-LLM strategies. | INTENTIONALLY DROPPED from `NodeStrategy` protocol. |
| `@[backend_v2/services/orchestrator/strategies/logic.py#L42-L224]` | `semaphore` parameter & `if running_event is not None: running_event.set()` | Dead parameter and manual event trigger in native logic step. | INTENTIONALLY DROPPED. |
| `@[backend_v2/services/orchestrator/strategies/llm.py#L224-L1010]` | `if running_event: running_event.set()` at L256 & DTO packing at L802, L846, L865 | Premature signaling and parameter bundling. | INTENTIONALLY DROPPED. |
| `@[backend_v2/services/orchestrator/dag_executor.py#L189-L372]` | `semaphore` & `running_event` in `NodeExecutor.execute` | Plumbing arguments across orchestrator boundaries. | INTENTIONALLY DROPPED. |
| `@[backend_v2/services/orchestrator/dag_executor.py#L749-L1065]` | `asyncio.Semaphore(max_concurrent_llm_steps)`, `running_event`, and `watch_running()` task | Asynchronous event waiting loop causing race conditions and telemetry lag. | Direct synchronous state update `status = ExecutionStatus.RUNNING` before `NodeExecutor.execute`. |
| `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]` | Bare `class SynthesisEngine:` without protocol inheritance | Duck-typing divergence from `ExecutionEngine(Protocol)`. | `class SynthesisEngine(ExecutionEngine):` with `@override`. |
| `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]` | `raise ValueError(...)` at L159 and L209 | Generic Python exception bypassing RFC 7807 structured error reporting. | Direct `AppException(ErrorCodes.VALIDATION_FAILED)`. |
| `@[backend_v2/tests/unit/models/dtos/test_engine.py#L101-L148]` | `test_engine_execution_request_semaphore_cm_and_fields` testing `semaphore_cm` & `semaphore` | Assertion of deprecated concurrency fields on domain DTO. | Refactored into `test_engine_execution_request_pure_fields`. |
| `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]` | `make_atom` returning `dict[str, Any]` & `.get("error_code")` lookups | Permissive typing and defensive dictionary access in test assertions. | Typed `DraftExtractedAtom` and direct subscript `details["error_code"]`. |
| `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]` | Defensive `.get()` dictionary lookups in mock assertions | Defensive dictionary reflection masking contract drift. | Direct subscript assertions (`eg_kwargs["execution_id"]`, `matrix_context`). |
| `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L174-L243]` | `test_dag_executor_hoists_and_passes_semaphore` | Obsolete test asserting that `NodeExecutor.execute` receives `semaphore`. | Refactored to `test_dag_executor_pure_dispatch_without_semaphore` asserting absence of concurrency plumbing in `call_kwargs`. |
| `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L707-L820]` | `if "running_event" in kwargs: kwargs["running_event"].set()` in `fake_node_execute` (L805-L806) | Unnecessary simulation of deprecated watcher event in test fake. | Clean `fake_node_execute` without `running_event` checks. |
| `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1131-L1212]` | `semaphore=asyncio.Semaphore(1)` in `node_executor.execute()` call at L1200 | Dead concurrency argument passed to `NodeExecutor`. | Direct `node_executor.execute()` call without `semaphore`. |
| `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1808-L1882]` | `semaphore=asyncio.Semaphore(1)` in `node_executor.execute()` call at L1873 | Dead concurrency argument passed to `NodeExecutor`. | Direct `node_executor.execute()` call without `semaphore`. |
| `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]` | `semaphore=asyncio.Semaphore(1)` in test strategy calls (L41, L61, L103, L152, L195, L230, L270, L346) & `test_execute_sets_running_event_and_merges_state_delta` | Concurrency plumbing passed to logic strategy unit tests. | Clean `execute()` test invocations without `semaphore` or `running_event`. |
| `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]` | `hasattr(mock_repo, "get_step_by_id")` and `assert hasattr(logic, "__all__")` | Dynamic reflection in test assertions violating QGR001. | Direct typed attribute access `mock_repo.get_step_by_id.return_value = None` and `assert "__all__" in dir(logic)`. |
| `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]` | `semaphore=asyncio.Semaphore(2)` in 27 test strategy calls & `test_execute_sets_running_event_and_handles_string_inputs` | Concurrency plumbing passed to LLM strategy unit tests. | Clean `execute()` test invocations without `semaphore` or `running_event`. |
| `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]` | `semaphore=asyncio.Semaphore(...)` & `running_event=asyncio.Event()` at L123-L124, L251 | Concurrency plumbing in cost tracking tests. | Clean test invocations without concurrency fixtures. |
| `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L70-L81]` | `assert res["semaphore"] is True, f"Missing asyncio.Semaphore in {dag_executor_path}"` | Obsolete AST guardrail requiring leaky concurrency primitive in orchestrator. | Refactored to `assert res["semaphore"] is False, f"Leaky asyncio.Semaphore found in {dag_executor_path}"`. |

### 2.2 Retained SSOT Invariants (`What We Will RETAIN`)
- **`ExecutionEngine` Structural Protocol (`@[backend_v2/services/orchestrator/engines/base.py#L11-L31]`):** Retained as the sole authoritative interface for execution engines, maintaining `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:`.
- **PEP 698 `@override` Parity:** All concrete implementations (`PromptEngine`, `SynthesisEngine`, `TDAEngine`) retain explicit `@override` decorators verified by MyPy strict mode.
- **Stateless Engine Immutability (`stateless_engine_immutability_mandate`):** Engines maintain zero cross-request instance state.
- **Tripartite Pipeline Consolidation & Unified Executive Summary (`tripartite_pipeline_architecture`):** `SynthesisEngine` is the authoritative, sovereign Phase 2 consolidator across the entire system. Phase 1 compute engines (`TDAEngine`, `CausalDiscoveryEngine`) produce raw evaluated atoms, DAG dependency topologies, and topological blame attributions (`blame_parent_ids`). `SynthesisEngine` consumes this Phase 1 causal state directly from the step states/context: in `synthesis_tasks.py` (`create_executive_summary_task`), causal diagnosis (`causal_result: CausalRootCauseDiagnosisDTO | CausalGraphPayloadDTO`) is injected into the LLM synthesis context inside `<causal_diagnosis>` at the dynamic payload tail. In Phase 3, this is projected into `TargetBlockType.EXECUTIVE_SUMMARY_BLOCK` as an integrated horizon combining the holistic strategic narrative with the empirical Unified Causal Action Card (`SduiCausalGraphBlock`). In Quorum Studio and OutputProfile, there remains strictly `TargetBlockType.EXECUTIVE_SUMMARY_BLOCK` (zero separate causal layout block types in `target_block_order`). The executive summary does not collapse into a pure diagnostic card: the holistic strategic narrative, observations, and recommendations remain fully preserved, while the empirical causal card provides root-cause anchoring. Bifurcated output pipelines, parallel output channels, and disjoint secondary reports are strictly prohibited.
- **Two-Tier Semaphore Architecture (`system_concurrency_ssot`):** Macro-level workflow concurrency remains in Arq (`settings.max_concurrent_workflows`), while micro-level LLM call concurrency remains in `LiteLLMProvider` (`settings.max_concurrent_llm_steps`).
- **RFC 7807 Dual-Reporting & Fail-Fast ACL:** Engines catch internal exceptions and re-raise structured `AppException` instances logged via `logger.error` before exiting.

### 2.3 Five-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/dtos/engine.py#L61-L132]` (`EngineExecutionRequest`) | Concurrency primitives (`asyncio.Semaphore`, `asyncio.Event`) and nullcontext wrapper property (`@property def semaphore_cm`) residing inside a domain DTO. | Pure execution DTO configured with `ConfigDict(strict=True, extra="forbid", frozen=True, arbitrary_types_allowed=True)`. In-memory runtime handles (`bound_client: LLMClient`, `Callable` callbacks) safely encapsulated without serialization impedance. | Pruned 3 dead/concurrency fields (`semaphore`, `running_event`, `semaphore_cm`). Eradicated multi-hop plumbing across 6 layers. | `uv run pytest backend_v2/tests/unit/models/dtos/test_engine.py -v`. Direct attribute access asserts absence of `semaphore` and `semaphore_cm`. |
| `@[backend_v2/services/orchestrator/engines/base.py#L11-L31]` (`ExecutionEngine`) | Concurrency and event references in Protocol docstrings. | Pure stateless `typing.Protocol` with signature `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:`. | Zero top-level concurrency management inside engine interfaces. | MyPy strict mode verification; runtime `@runtime_checkable` validation across all 3 concrete engines. |
| `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L74]` (`PromptEngine`) | `async with request.semaphore_cm:`, `request.running_event.set()`, and missing PEP 698 `@override`. | Direct invocation of `self.task_executor.execute_structured_task` at root function scope; explicit `@override` decorator. | Pruned redundant semaphore wrapping and telemetry event mutation inside leaf engine. | `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py -v`. Protocol subclass/isinstance assertions pass 100%. |
| `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]` (`SynthesisEngine`) | Duck-typing bare class (`class SynthesisEngine:`), missing `@override`, `async with request.semaphore_cm:`, generic `raise ValueError(...)` at L159 and L209, and dead `AliasEngine` import (L29). | Formal protocol inheritance `class SynthesisEngine(ExecutionEngine):`, PEP 698 `@override`, direct execution without semaphore locks, structured `AppException(ErrorCodes.VALIDATION_FAILED)` with RFC 7807 logging, dead import pruning. | Pruned redundant top-level semaphore acquisition; eradicated generic Python exceptions and dead imports. | `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py -v`. Assertions verify `AppException` with `ErrorCodes.VALIDATION_FAILED.value`. |
| `@[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]` (`TDAEngine`) | Missing `@override`, `request.running_event.set()`, and passing `semaphore=request.semaphore` to sub-executors (`TwoPassAtomizer`, `EnrichedDagExecutor`). | PEP 698 `@override` on `execute()`, direct compute pipeline delegating concurrency to `LiteLLMProvider`. | Eradicated multi-hop semaphore parameter drilling into child executors. | `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py -v`. Protocol inheritance and clean execution assertions pass. |
| `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L39-L586]` (`TwoPassAtomizer`) | `semaphore: asyncio.Semaphore \| None` parameter and local `async with sem:` block around `_extract_ontology_from_chunk`. | Autonomous `TaskGroup` chunk scheduling relying on `LiteLLMProvider` dynamic semaphore pool for rate-limiting. | Pruned redundant internal semaphore instantiation and parameter passing across chunks. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py -v`. |
| `@[backend_v2/services/orchestrator/enriched_dag_executor.py#L32-L218]` (`EnrichedDagExecutor`) | `semaphore: asyncio.Semaphore \| None` parameter and local `async with sem:` lock around `ExtractiveSensorService.evaluate_atom_boolean_batch`. | Direct batch evaluation relying on `LiteLLMProvider` for micro-concurrency throttling. | Pruned chunk-level semaphore lock and plumbing parameter. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py -v`. |
| `@[backend_v2/services/orchestrator/strategies/base.py#L181-L208]` (`NodeStrategy`) | `semaphore: asyncio.Semaphore` and `running_event: asyncio.Event \| None` in `NodeStrategy.execute` signature. | Pure domain signature `async def execute(self, step: StepRule, projector: StateProjector, context: StrategyContext, frozen_ctx: FrozenContext \| None, trace: list[TraceEvent] \| None, progress_callback: ...) -> list[TraceEvent]:`. | Eradicated interface pollution forcing dead arguments on non-LLM node strategies. | MyPy strict mode verification across all strategy implementations. |
| `@[backend_v2/services/orchestrator/strategies/logic.py#L42-L224]` (`LogicNodeStrategy`) | Dead `semaphore` parameter and manual `if running_event is not None: running_event.set()` trigger. | Clean `execute()` implementation with pure hook execution and state delta merging. | Pruned dead concurrency parameter and telemetry event mutation in native logic step. | `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py -v`. |
| `@[backend_v2/services/orchestrator/strategies/llm.py#L224-L1010]` (`LLMNodeStrategy`) | Premature `if running_event: running_event.set()` at L256 and packing `semaphore`/`running_event` into `EngineExecutionRequest` across 3 branches. | Pure execution strategy delegating to resolved `ExecutionEngine` without concurrency or event arguments. | Pruned premature telemetry signaling and parameter bundling. | `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py -v`. |
| `@[backend_v2/services/orchestrator/dag_executor.py#L189-L372]` (`NodeExecutor`, `DAGExecutor`) | Macro-semaphore `asyncio.Semaphore(max_concurrent_llm_steps)`, `running_event = asyncio.Event()`, `watch_running()` background task, and `watcher_task.cancel()`. | Deterministic synchronous step transition to `ExecutionStatus.RUNNING` inside `_update_lock` immediately prior to dispatching `NodeExecutor.execute`, committed via `_safe_commit()`. | Pruned 22 lines of complex background event watching; eliminated unmanaged background tasks evading `TaskGroup`. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py -v`. Atomic transition to `RUNNING` verified upon dispatch. |
| `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]` | `make_atom` returning naked `dict[str, Any]` and defensive `.get("error_code")` dictionary lookups. | Typed `make_atom` returning `DraftExtractedAtom` and direct subscript assertions `assert exc_info.value.details["error_code"] == ...`. | Pruned permissive typing and defensive dictionary reflection in unit tests. | `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py -v`. |
| `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]` | Defensive `.get()` dictionary lookups in mock assertions (`execution_id`, `step_id`, `matrix_context`, `progress_callback`). | Direct subscript assertions (`assert eg_kwargs["execution_id"] == ...`). | Pruned defensive dictionary reflection masking interface drift. | `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py -v`. |
| `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L174-L243]` | Obsolete test `test_dag_executor_hoists_and_passes_semaphore` asserting `semaphore` passed to `NodeExecutor`. | Refactored `test_dag_executor_pure_dispatch_without_semaphore` verifying absence of concurrency plumbing in `call_kwargs`. | Pruned legacy semaphore assertion from orchestrator unit test suite. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py -k test_dag_executor_pure_dispatch_without_semaphore -v`. |
| `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L70-L81]` | Obsolete AST assertion requiring `asyncio.Semaphore` in `dag_executor.py` (L81). | Modernized AST guardrail asserting `res["semaphore"] is False` in `dag_executor.py` while retaining `res["semaphore"] is True` in `provider.py`. | Pruned obsolete AST concurrency assertion enforcing leaky orchestrator plumbing. | `uv run pytest backend_v2/tests/unit/test_ast_concurrency_guardrails.py -v`. |

### 2.4 Compliance & Modernity Gates
1. **Zero Naked Dictionaries (`no_naked_dicts_in_state`):** Engine boundaries operate strictly via Pydantic V2 DTOs (`EngineExecutionRequest`, `EngineExecutionResult`).
2. **DTO In-Memory Handle Strictness:** `EngineExecutionRequest` enforces `ConfigDict(strict=True, extra="forbid", frozen=True, arbitrary_types_allowed=True)`. While concurrency primitives are purged, `arbitrary_types_allowed=True` is mathematically required to encapsulate in-memory client and callback handles (`bound_client: LLMClient`, `compiled_schema: type[BaseModel]`, and callback Callables) within the worker process without triggering `PydanticSchemaGenerationError`.
3. **Python 3.14 Concurrency Integrity:** Eliminates background task watchers (`watch_running`) that evade `TaskGroup` cancellation contexts, preventing orphaned asyncio tasks.

### 2.5 Producer-Consumer Integration Check
- **Producer (`DAGExecutor`):** Directly sets `ExecutionStatus.RUNNING` in `exec_record.step_states` and commits to persistence before invoking `node_executor.execute()`. No intermediate `Event` signaling is required.
- **Consumer (`ExecutionEngine`):** Receives pure data payloads (`bound_client`, `hydrated_messages`, `step`, `context`, `global_source_text`, `shuffled_atoms`). Has zero awareness of whether caller is local asyncio, an Arq worker, or a unit test fixture.

---

## 3. Phased Execution Plan (Implementation Strategy)

```xml
<execution_protocol level="epic_155">
  <phase id="1" name="PRE_IMPLEMENTATION_TECHNICAL_DEBT_CLEANUPS">
    <step id="1.1" name="FIX_SYNTHESIS_ENGINE_VALUEERROR_DUCT_TAPE_AND_DEAD_IMPORTS">
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L29]`, remove unused import `from backend_v2.utils.alias_engine import AliasEngine` to clean module namespace.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`, replace `raise ValueError("hydrated_messages must be provided for SynthesisEngine")` at L159 with structured `AppException(message="hydrated_messages must be provided for SynthesisEngine", status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "step_id": request.step.id})`.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`, replace `raise ValueError("compiled_schema must be provided for SynthesisEngine")` at L209 with structured `AppException(message="compiled_schema must be provided for SynthesisEngine", status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "step_id": request.step.id})`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L363-L373]`, update `test_synthesis_engine_missing_hydrated_messages` to assert `exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L376-L386]`, update `test_synthesis_engine_missing_compiled_schema` to assert `exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value`.</action>
    </step>
    <step id="1.2" name="FIX_SYNTHESIS_TEST_ASSERTION_REFLECTION">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, remove `from typing import Any` and import `DraftExtractedAtom` from `backend_v2.models.domain.blackboard` to enforce zero permissive typing imports.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L29-L43]`, refactor `make_atom` test helper to return typed `DraftExtractedAtom` instead of naked `dict[str, Any]` to comply with `ki_zero_permissive_typing.md`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L108-L121]`, eliminate defensive dictionary lookup `.get("error_code")` and replace with direct typed dictionary access `assert exc_info.value.details["error_code"] == ErrorCodes.SYNTHESIS_ENGINE_ERROR.value` to comply with `ki_zero_permissive_typing.md`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L167-L180]`, eliminate defensive dictionary lookup `.get("error_code")` and replace with direct typed dictionary access `assert exc_info.value.details["error_code"] == ErrorCodes.SYNTHESIS_ENGINE_ERROR.value` to comply with `ki_zero_permissive_typing.md`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L183-L199]`, eliminate defensive dictionary lookup `.get("error_code")` and replace with direct typed dictionary access `assert exc_info.value.details["error_code"] == "CUSTOM_ERROR"` to comply with `ki_zero_permissive_typing.md`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L434-L453]`, add explicit `assert exc_info.value.details is not None` and `assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value` to enforce Fail-Fast schema assertions.</action>
    </step>
    <step id="1.3" name="FIX_TDA_ENGINE_TEST_ASSERTION_REFLECTION">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py#L76-L133]`, eliminate defensive `.get("progress_callback")` lookups in mock callbacks and replace with positive key membership guards.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py#L76-L133]`, eliminate defensive dictionary lookups `eg_kwargs.get("execution_id")` and `eg_kwargs.get("step_id")` and replace with direct subscript assertions `assert eg_kwargs["execution_id"] == engine_request.context.execution_id` and `assert eg_kwargs["step_id"] == engine_request.step.id`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py#L329-L371]`, eliminate defensive dictionary lookup `eg_kwargs.get("matrix_context")` and replace with direct subscript assertion `passed_matrix_context = eg_kwargs["matrix_context"]`.</action>
    </step>
    <step id="1.4" name="CLEAN_BASE_EXECUTION_ENGINE_PROTOCOL">
      <action>In `@[backend_v2/services/orchestrator/engines/base.py#L11-L31]`, audit docstrings and signature of `ExecutionEngine.execute` to ensure complete decoupling from concurrency limiters and telemetry events.</action>
    </step>
    <step id="1.5" name="CLEAN_DAG_EXECUTOR_TEST_RUNNING_EVENT_HOOK">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L707-L820]`, remove `if "running_event" in kwargs: kwargs["running_event"].set()` from `fake_node_execute` (L805-L806).</action>
    </step>
    <step id="1.6" name="FIX_LOGIC_STRATEGY_TEST_REFLECTION">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py#L47-L64]`, eliminate `hasattr(mock_repo, "get_step_by_id")` reflection at L57 and set `mock_repo.get_step_by_id.return_value = None` directly.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py#L278-L282]`, replace `assert hasattr(logic, "__all__")` at L281 with direct membership assertion `assert "__all__" in dir(logic)` to comply with `ki_zero_permissive_typing.md` (QGR001 anti-reflection mandate).</action>
    </step>
  </phase>

  <phase id="2" name="CONCRETE_ENGINE_PURITY_AND_PROTOCOL_HARMONIZATION">
    <step id="2.1" name="PURIFY_AND_HARMONIZE_PROMPT_ENGINE">
      <action>In `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L74]`, import `override` from `typing` and decorate `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:` with `@override`.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L74]`, remove `if request.running_event: request.running_event.set()`.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L74]`, remove `async with request.semaphore_cm:` block and invoke `self.task_executor.execute_structured_task` directly at root function indentation.</action>
    </step>
    <step id="2.2" name="PURIFY_AND_HARMONIZE_SYNTHESIS_ENGINE">
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`, import `override` from `typing` and import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base`.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`, update class definition to `class SynthesisEngine(ExecutionEngine):`.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`, decorate `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:` with `@override`.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`, remove `async with request.semaphore_cm:` block at L215 and invoke `self._executor.execute_structured_task` directly.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`, ensure zero `running_event` references exist.</action>
    </step>
    <step id="2.3" name="PURIFY_AND_HARMONIZE_TDA_ENGINE">
      <action>In `@[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]`, import `override` from `typing` and decorate `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:` with `@override`.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]`, remove `if request.running_event: request.running_event.set()` at L68-L69.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]`, remove `semaphore=request.semaphore` from `atomizer.execute_phase_0` call at L194.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]`, remove `semaphore=request.semaphore` from `dag_executor.execute_graph` call at L229.</action>
    </step>
    <step id="2.4" name="UPDATE_ORCHESTRATOR_ENGINE_UNIT_TESTS">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]`, remove all `semaphore` and `running_event` fixtures, mock injections, and assertions asserting `running_event.is_set()`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]`, import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base` and add `test_prompt_engine_implements_protocol()` asserting `issubclass(PromptEngine, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, remove all `semaphore` and `running_event` fixtures and tests verifying `null_concurrency_guards` or event signaling.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base` and add `test_synthesis_engine_implements_protocol()` asserting `issubclass(SynthesisEngine, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]`, remove `running_event` assertions and `semaphore` fixtures.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]`, import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base` and add `test_tda_engine_implements_protocol()` asserting `issubclass(TDAEngine, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py]`, remove `running_event` instantiation.</action>
    </step>
  </phase>

  <phase id="3" name="SUB_EXECUTOR_CONCURRENCY_DECOUPLING">
    <step id="3.1" name="DECOUPLE_TWO_PASS_ATOMIZER">
      <action>In `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L39-L586]`, remove `semaphore: asyncio.Semaphore | None = None` parameter from `execute_phase_0` signature at L78.</action>
      <action>In `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L39-L586]`, remove manual `sem = semaphore or asyncio.Semaphore(...)` initialization and remove `sem` argument from `_extract_ontology_from_chunk` helper.</action>
    </step>
    <step id="3.2" name="DECOUPLE_ENRICHED_DAG_EXECUTOR">
      <action>In `@[backend_v2/services/orchestrator/enriched_dag_executor.py#L32-L218]`, remove `semaphore: asyncio.Semaphore | None = None` parameter from `execute_graph` signature at L58.</action>
      <action>In `@[backend_v2/services/orchestrator/enriched_dag_executor.py#L32-L218]`, remove `sem = semaphore if semaphore is not None else ...` and remove `async with sem:` block around `ExtractiveSensorService.evaluate_atom_boolean_batch` at L115-L117.</action>
    </step>
  </phase>

  <phase id="4" name="STRATEGY_LAYER_HARMONIZATION">
    <step id="4.1" name="HARMONIZE_NODE_STRATEGY_BASE_PROTOCOL">
      <action>In `@[backend_v2/services/orchestrator/strategies/base.py#L116-L319]`, remove `semaphore: asyncio.Semaphore` and `running_event: asyncio.Event | None = None` parameters from `NodeStrategy.execute` signature at L189-L190.</action>
    </step>
    <step id="4.2" name="HARMONIZE_LOGIC_NODE_STRATEGY">
      <action>In `@[backend_v2/services/orchestrator/strategies/logic.py#L31-L224]`, remove `semaphore: asyncio.Semaphore` and `running_event: asyncio.Event | None = None` from `LogicNodeStrategy.execute` signature at L49-L50.</action>
      <action>In `@[backend_v2/services/orchestrator/strategies/logic.py#L31-L224]`, remove `if running_event is not None: running_event.set()` at L73-L74.</action>
    </step>
    <step id="4.3" name="HARMONIZE_LLM_NODE_STRATEGY">
      <action>In `@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1010]`, remove `semaphore: asyncio.Semaphore` and `running_event: asyncio.Event | None = None` from `LLMNodeStrategy.execute` signature at L231-L232.</action>
      <action>In `@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1010]`, remove premature `if running_event: running_event.set()` at L256-L257.</action>
      <action>In `@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1010]`, eliminate `semaphore` and `running_event` arguments when constructing `EngineExecutionRequest` instances across all execution branches.</action>
    </step>
    <step id="4.4" name="HARMONIZE_NODE_EXECUTOR_STRATEGY_DISPATCH">
      <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L189-L372]`, eliminate `semaphore` and `running_event` arguments passed from `NodeExecutor.execute` to `strategy_impl.execute` at L355-L356, maintaining intra-file caller signature compatibility with `run_step_wrapper` until Phase 5.</action>
    </step>
    <step id="4.5" name="UPDATE_STRATEGY_UNIT_TESTS">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]`, refactor `test_execute_sets_running_event_and_merges_state_delta` into `test_execute_merges_state_delta`, removing `semaphore` and `running_event` parameters and assertions across all test cases (L41, L61, L103, L152, L195, L230, L270, L346).</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`, refactor `test_execute_sets_running_event_and_handles_string_inputs` into `test_execute_handles_string_inputs`, removing `running_event` and `semaphore` fixtures across all 27 test executions.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`, remove `running_event` and `semaphore` fixtures at L123-L124 and L251.</action>
    </step>
  </phase>

  <phase id="5" name="DTO_PURIFICATION_AND_MACRO_ORCHESTRATOR_SIMPLIFICATION">
    <step id="5.1" name="PURIFY_ENGINE_EXECUTION_REQUEST_DTO">
      <action>In `@[backend_v2/models/dtos/engine.py#L61-L132]`, remove `semaphore: Annotated[asyncio.Semaphore | None, ...]` and `running_event: Annotated[asyncio.Event | None, ...]` fields.</action>
      <action>In `@[backend_v2/models/dtos/engine.py#L61-L132]`, remove `@property def semaphore_cm(self) -> Any:` context manager property.</action>
      <action>In `@[backend_v2/models/dtos/engine.py#L61-L132]`, retain `model_config = ConfigDict(arbitrary_types_allowed=True, strict=True, extra="forbid", frozen=True)` to safely permit in-memory execution handles (`bound_client: LLMClient`, `compiled_schema: type[BaseModel]`, and callback Callables) without triggering `PydanticSchemaGenerationError` at import time.</action>
    </step>
    <step id="5.2" name="UPDATE_ENGINE_DTO_TESTS">
      <action>In `@[backend_v2/tests/unit/models/dtos/test_engine.py#L101-L148]`, refactor `test_engine_execution_request_semaphore_cm_and_fields` to `test_engine_execution_request_pure_fields`, eliminating assertions on `req.semaphore_cm` and `req_sem.semaphore_cm` while verifying that `EngineExecutionRequest` enforces strict immutable fields and rejects `semaphore` or `running_event` arguments.</action>
    </step>
    <step id="5.3" name="PURIFY_NODE_EXECUTOR_AND_SIMPLIFY_DAG_EXECUTOR">
      <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L189-L372]`, remove `semaphore: asyncio.Semaphore` and `running_event: asyncio.Event | None = None` from `NodeExecutor.execute` signature.</action>
      <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]`, remove top-level `semaphore = asyncio.Semaphore(get_settings().max_concurrent_llm_steps)` initialization at L730.</action>
      <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]`, eradicate `running_event = asyncio.Event()`, `watch_running()` function, and `watcher_task = asyncio.create_task(watch_running())` at L827-L850.</action>
      <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]`, transition the step state directly to `ExecutionStatus.RUNNING` inside `_update_lock` immediately prior to dispatching `node_executor.execute`, committing status to persistence in a single atomic commit.</action>
      <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]`, remove `semaphore=semaphore` and `running_event=running_event` from `node_executor.execute` call at L920-L921.</action>
      <action>In `@[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]`, remove `watcher_task.cancel()` in the `finally:` block at L928.</action>
    </step>
    <step id="5.4" name="UPDATE_DAG_EXECUTOR_WATCHER_TEST">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1666-L1737]`, refactor `test_dag_executor_watch_running_event_transitions_queued_step` into `test_dag_executor_synchronous_running_dispatch_transitions_step`, asserting that the step transitions to `ExecutionStatus.RUNNING` inside `_update_lock` on dispatch.</action>
    </step>
    <step id="5.5" name="UPDATE_DAG_EXECUTOR_SEMAPHORE_TESTS">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1131-L1212]`, remove `semaphore=asyncio.Semaphore(1)` from `node_executor.execute()` call at L1200.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1808-L1882]`, remove `semaphore=asyncio.Semaphore(1)` from `node_executor.execute()` call at L1873.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L174-L243]`, refactor `test_dag_executor_hoists_and_passes_semaphore` into `test_dag_executor_pure_dispatch_without_semaphore`, asserting that `call_kwargs` passed to `NodeExecutor.execute` contains neither `semaphore` nor `running_event`.</action>
    </step>
    <step id="5.6" name="UPDATE_AST_CONCURRENCY_GUARDRAILS">
      <action>In `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L70-L81]`, update `test_ast_semaphore_guardrail` to assert `res["semaphore"] is False` for `dag_executor.py` (`assert res["semaphore"] is False, f"Leaky asyncio.Semaphore found in {dag_executor_path}"`), proving pure compute decoupling while retaining `res["semaphore"] is True` for `provider.py`.</action>
    </step>
  </phase>

  <phase id="6" name="COMPREHENSIVE_QUALITY_GATES_AND_REGRESSION_VERIFICATION">
    <step id="6.1" name="EXECUTE_GLOBAL_QUALITY_GATE">
      <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/engine.py backend_v2/services/orchestrator/engines/prompt_engine.py backend_v2/services/orchestrator/engines/synthesis_engine.py backend_v2/services/orchestrator/engines/tda_engine.py backend_v2/services/orchestrator/dag_executor.py --test` to verify Ruff formatting, strict MyPy typing, AST guardrails, and full Pytest suite passing.</action>
    </step>
    <step id="6.2" name="EXECUTE_MARKDOWN_BOUNDARIES_AUDIT">
      <action>Execute `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md` to ensure markdown reference integrity.</action>
    </step>
    <step id="6.3" name="EXECUTE_MANDATORY_LIVE_E2E_VERIFICATION">
      <action>Execute `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py` to confirm zero regressions in live end-to-end execution.</action>
    </step>
  </phase>

  <phase id="7" name="KNOWLEDGE_BASE_AND_ARCHITECTURE_SYNCHRONIZATION">
    <step id="7.1" name="UPDATE_KNOWLEDGE_ITEM_PROTOCOL">
      <action>In `@[ki_execution_engine_protocol.md]`, deprecate `atomic_telemetry_signaling_mandate` and `engine_concurrency_nullcontext_mandate`. Replace with the new Pure Compute Engine Law: execution engines are 100% computational pipelines with zero semaphore or event dependencies.</action>
    </step>
    <step id="7.2" name="SYNCHRONIZE_META_ARCHITECTURE_DOCUMENTATION">
      <action>Execute `/tier7-describe-architecture @[docs/architecture/03_cognitive_orchestration_engine.md]` to document the streamlined 2-tier concurrency architecture: macro job queue in Arq, micro request throttling in `LLMClient` / `LiteLLMProvider`, and pure stateless computation in `ExecutionEngine`.</action>
    </step>
  </phase>
</execution_protocol>
```

---

## 4. Definition of Done (DoD) & Verification Plan

### 4.1 Definition of Done (DoD)
1. **100% Pure DTO Contracts:** `EngineExecutionRequest` contains zero references to `asyncio.Semaphore`, `asyncio.Event`, or `contextlib.nullcontext()`. `model_config` strictly enforces `strict=True, extra="forbid", frozen=True, arbitrary_types_allowed=True` to safely encapsulate in-memory client and callback handles.
2. **100% Protocol Inheritance & Parity:** `SynthesisEngine` explicitly inherits from `ExecutionEngine(Protocol)`. All concrete implementations (`PromptEngine`, `SynthesisEngine`, `TDAEngine`) implement PEP 698 `@override` on `execute()`, verified by MyPy strict mode and unit tests (`issubclass` and `isinstance` return `True`).
3. **Zero In-Memory Concurrency in Engines:** `PromptEngine`, `SynthesisEngine`, and `TDAEngine` execute without top-level semaphore wrapping and without mutating external `Event` objects.
4. **Structured RFC 7807 Error Handling:** `SynthesisEngine` replaces all `ValueError` duct-tape with structured `AppException(ErrorCodes.VALIDATION_FAILED)`.
5. **Zero Permissive Test Typing:** `test_synthesis_engine.py` eradicates `from typing import Any` and naked `dict[str, Any]` in favor of typed `DraftExtractedAtom`, and all engine test assertions use direct dictionary subscripts.
6. **Elimination of Orphaned Watchers:** `DAGExecutor` no longer spawns `watch_running()` tasks; step status transitions atomically to `ExecutionStatus.RUNNING` upon dispatch.
7. **Zero AST / Linter Violations:** Ruff, MyPy strict mode, and QGR AST guardrails pass 100% across all touched backend targets.
8. **No Regressions in Matrix Evaluation:** Full TDA graph execution (`EnrichedDagExecutor`) succeeds with unchanged assertion resolution and token usage aggregation.
9. **AST Concurrency Guardrail Modernization:** `test_ast_semaphore_guardrail` passes asserting `res["semaphore"] is True` in `provider.py` and `res["semaphore"] is False` in `dag_executor.py`.
10. **Zero Dynamic Reflection in Tests:** `test_logic.py` eradicates `hasattr` reflection in favor of direct attribute access.

### 4.2 Automated Unit & Integration Tests
- **Unit Test Command:**
  ```powershell
  uv run pytest backend_v2/tests/unit/services/orchestrator/engines/ -v
  uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/ -v
  uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py -v
  ```
- **Global Backend Audit Gate:**
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test
  ```

### 4.3 MANDATORY Final E2E REST API Verification Gate
```powershell
# Windows 11 PowerShell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 5. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document (lines 1..15) for the authoritative registry of active rules and Knowledge Items governing this Epic.
