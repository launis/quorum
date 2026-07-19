# EPIC 105: Synthesis Engine Unification

## 1. Goal Description
Following the extraction of the `TDAEngine` (Epic 104), the system now possesses a decoupled `ExecutionEngine` interface plugged into the `LLMNodeStrategy` (which acts as the SSOT Lifecycle Manager). However, `PreHydratedSynthesisStrategy` currently bypasses this entirely, operating as a parallel, standalone `NodeStrategy`.

**Objective**: Unify the architecture by converting the Synthesis execution logic into a `SynthesisEngine` (implementing the `ExecutionEngine` Protocol). This allows us to route Synthesis steps through `LLMNodeStrategy`, granting Synthesis tasks immediate access to advanced lifecycle features (Alias Engine hydration, standard telemetry, anomaly retry loops, and robust error handling) while completely deleting the duplicated `PreHydratedSynthesisStrategy` file.

## 2. Architectural Impact & Safeguards
- **DRY Compliance (SSOT)**: We eliminate ~150 lines of duplicated code. `LLMNodeStrategy` becomes the absolute Single Source of Truth (SSOT) for ALL AI step lifecycles, guaranteeing that any future telemetry or retry enhancements automatically apply to both Reasoning and Synthesis.
- **Strict Separation of Concerns**: By implementing the Synthesis logic as an `ExecutionEngine`, it remains completely isolated from the `TDAEngine`. The DAG will execute them as separate nodes; they just share the same lifecycle manager.
- **Fail-Fast Safety & Dumb Engine Enforcement**: The extraction must ensure that the `GlobalAtomBlackboard` validation (Epic 101 Rule 1) is preserved inside the `SynthesisEngine.execute()` method. However, the engine MUST remain cognitively "dumb" regarding schemas. It MUST NOT perform any dynamic schema mapping itself; instead, it must strictly pass the pre-compiled `request.compiled_schema` down to the `LLMTaskExecutor`.
- **Schema Pre-Compilation Responsibility Chain (CRITICAL)**: Currently, `PreHydratedSynthesisStrategy` directly calls `self.compiler.build_dynamic_schema()` and `self.compiler.compile_static_instructions()` (lines 87-98 of `pre_hydrated_synthesis.py`). Since the `SynthesisEngine` MUST NOT use a `compiler` injection, this compilation responsibility MUST be lifted into `LLMNodeStrategy`'s existing pre-compilation pipeline. Specifically, `LLMNodeStrategy.execute()` must detect the engine type (or use the step's `model_strategy`) and invoke the appropriate schema compilation BEFORE constructing the `EngineExecutionRequest` DTO. The compiled schema, static instructions, and prompt context are then passed into the request DTO. This ensures absolute separation: `LLMNodeStrategy` = compilation + lifecycle, `SynthesisEngine` = execution only.
- **Absolute Engine Statelessness**: Just like `TDAEngine`, the `SynthesisEngine` MUST be strictly stateless. It must NOT store any runtime variables, extraction results, or context in `self`. All data must flow immutably through the `execute()` signature to prevent race conditions during highly concurrent DAG invocations.
- **Strict DTO Location & Circular Import Prevention**: The engine must return the exact same `EngineExecutionResult` DTO defined in Epic 104. This DTO must be centrally located (e.g., `backend_v2/models/dtos/engine.py`) to prevent `synthesis_engine.py` from creating circular dependencies with `llm.py` or other heavy ML modules.
- **Anti-Corruption Layer (Epic 104 Compliance)**: The new engine MUST wrap all execution failures (e.g., Pydantic parsing errors, LLM crashes) inside an `EngineExecutionException`. This guarantees that `LLMNodeStrategy`'s Dead Letter Queue (DLQ) routing can deterministically catch and process them.
- **Append-Only Law & Seed Data Validation**: Executions (results) MUST NOT and do not need to be migrated during refactoring. **Historical execution data has zero structural value and is considered entirely disposable during migrations.** Historical payload data is append-only and mutation is strictly prohibited. ONLY `seed_data.json` is updated for configuration changes. Any modifications to `seed_data.json` MUST strictly follow the *Vault Mutation Protocol* (e.g., re-seeding via `run_seed.py`).

## 3. Implementation Phases

### Phase 1: Engine Extraction & Parameter Object Utilization
- **Protocol Invariance (`engines/base.py`)**: The `ExecutionEngine` protocol signature from Epic 104 MUST REMAIN STRICTLY UNCHANGED to guarantee the Open/Closed Principle (OCP). It already utilizes the Parameter Object pattern (`EngineExecutionRequest` DTO), which includes `step` and `context`. The `SynthesisEngine` will natively read what it needs from this DTO (e.g., `request.context.context_variables`) without altering the global engine interface. The return type MUST strictly remain the `EngineExecutionResult` DTO.
- **Target File**: `backend_v2/services/orchestrator/engines/synthesis_engine.py`
- Create `SynthesisEngine` implementing the strictly unmodified `ExecutionEngine` Protocol.
- Move the core execution logic from `PreHydratedSynthesisStrategy` into `SynthesisEngine.execute(request: EngineExecutionRequest)`. This includes:
  1. Validating the `__GLOBAL_ATOM_BLACKBOARD__` directly from `request.context.context_variables`.
  2. **Idempotency & Format Crash Protection**: Creating a local copy of the context via Pydantic's official `request.prompt_context.model_copy(deep=True)` before hydrating the blackboard data. Using standard Python `copy.deepcopy()` is STRICTLY FORBIDDEN due to performance overhead and internal state corruption risks in Pydantic V2. The engine MUST treat the incoming `request` DTO as strictly immutable to prevent state leakage during retry loops. Furthermore, to prevent "Format Crashes" caused by JSON examples containing `{ }` braces in prompts, standard Python `.format()` is STRICTLY FORBIDDEN. Hydration MUST use a custom safe parser (e.g., Regex-based curly-brace substitution) that correctly replaces `{variable}` syntax while safely ignoring unmatched JSON braces without raising `KeyError`. `string.Template` is also forbidden as it uses `$var` syntax and would silently fail to hydrate existing templates. The `SynthesisEngine` MUST NOT use a `compiler` injection, relying solely on the pre-compiled context.
  3. **Real-Time Observability (Epic 104 Compliance)**: Emitting a structured debug log containing the final, hydrated messages list BEFORE executing the LLM call. This prevents an "Observability Black Hole" by ensuring the exact prompt state is forensically auditable even if the LLM network request fatally crashes.
  4. Executing the task via `LLMTaskExecutor.execute_structured_task()`. The engine MUST strictly pass down `request.bound_client` (the LLM multiplexer), `request.compiled_schema` (for Pydantic validation), and the hydrated local copy of the messages. It must also pass down the `semaphore` and `running_event` to prevent Concurrency Leaks.
  5. Packaging the response strictly into the `EngineExecutionResult` DTO. This MUST explicitly include picking up the rich telemetry (API latencies, token counts) returned by `LLMTaskExecutor` and correctly mapping it into the `EngineExecutionResult.trace_events` list so the `LLMNodeStrategy` can serialize it to the global audit log.
  6. Acting as an **Anti-Corruption Layer** by catching all raw exceptions (e.g. schema parsing errors) and wrapping them in `EngineExecutionException` for deterministic DLQ routing.

### Phase 2: DAG Executor Wiring
- **Target File**: `backend_v2/services/orchestrator/dag_executor.py`
- Modify the routing logic for `step_def.model_strategy == "synthesis"`.
- Instead of instantiating `PreHydratedSynthesisStrategy`, explicitly instantiate `LLMNodeStrategy` and inject the newly created lightweight `SynthesisEngine`:
  ```python
  from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
  strategy_impl = LLMNodeStrategy(
      ...,
      engine=SynthesisEngine()
  )
  ```

### Phase 3: Deletion of Legacy Strategy
- **Target File**: `backend_v2/services/orchestrator/strategies/pre_hydrated_synthesis.py`
- Completely delete this file, as its logic is now governed by `LLMNodeStrategy` + `SynthesisEngine`.
- Remove references from `backend_v2/services/orchestrator/strategies/__init__.py`.

### Phase 4: Observability Logger Refactoring (AI Forensic Readiness)
- **Target File**: `backend_v2/utils/llm_debug_logger.py`
- Refactor the monolithic `write_debug_prompt_log` to support the "Dumb Engine" paradigm while avoiding both Observability Black Holes and Asynchronous Log Spaghetti.
- **Memory Buffering + Atomic Write**: Instead of writing to 50 separate files (which breaks the global AI audit rule), the logger must use an in-memory trace object to collect chronological events for a specific step.
  1. `strategy.pre_hook` logs selected blocks to the memory buffer.
  2. `engine` logs the exact hydrated payload to the memory buffer.
  3. `executor` logs the raw text response to the memory buffer.
- **Fail-Safe Flushing (`try...finally`)**: To ensure the memory buffer is not lost during a software crash (e.g., LLM network timeout or Pydantic parsing error), the `LLMNodeStrategy` MUST wrap the entire execution in a strict `try...finally` block. The `finally` block calls `write_atomic_step_log(buffer)`, guaranteeing that the full forensic story is atomically appended to `llm_debug_prompts.md` during the stack unwind, even if the node fatally crashes.

### Phase 5: Automated Testing
- **New Tests**: Create `tests/unit/services/orchestrator/engines/test_synthesis_engine.py` to test the new engine in isolation (mocking `LLMTaskExecutor` and the blackboard).
- **Cleanup**: Delete `tests/unit/services/orchestrator/strategies/test_pre_hydrated_synthesis.py` (or port relevant tests to the new engine test file).

## 4. Required User Review
- **Engine Naming**: The proposed name is `SynthesisEngine`. We avoid the name `StandardExecutionEngine` because Synthesis currently requires the `GlobalAtomBlackboard`, making it slightly specialized compared to a purely "vanilla" direct LLM call. Does this naming convention align with the roadmap?

## 5. Cross-Epic Synchronization (Epic 104 & 106)
- **Dependency on Epic 104**: This Epic MUST NOT be started until Epic 104 has fully merged the `ExecutionEngine` Protocol and `EngineExecutionRequest`/`Result` DTOs into the main branch.
- **Enabling Epic 106**: By deleting `PreHydratedSynthesisStrategy` and making the engine "dumb" (relying on `compiled_schema`), this Epic directly unlocks Epic 106's ability to safely delete the `synthesis` configuration object from `OutputProfile` and rely strictly on `StepRule.expected_sdui_type`.
- **Execution Order**: Epic 105 MUST be implemented **SECOND**.
