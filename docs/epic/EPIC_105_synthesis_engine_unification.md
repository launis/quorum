# EPIC 105: Synthesis Engine Unification

## 1. Goal Description
Following the extraction of the `TDAEngine` (Epic 104), the system now possesses a decoupled `ExecutionEngine` interface plugged into the `LLMNodeStrategy` (which acts as the SSOT Lifecycle Manager). However, `PreHydratedSynthesisStrategy` currently bypasses this entirely, operating as a parallel, standalone `NodeStrategy`.

**Objective**: Unify the architecture by converting the Synthesis execution logic into a `SynthesisEngine` (implementing the `ExecutionEngine` Protocol). This allows us to route Synthesis steps through `LLMNodeStrategy`, granting Synthesis tasks immediate access to advanced lifecycle features (Alias Engine hydration, standard telemetry, anomaly retry loops, and robust error handling) while completely deleting the duplicated `PreHydratedSynthesisStrategy` file.

> **CRITICAL DEPENDENCY**: This Epic MUST NOT be started until Epic 104 has fully merged the `ExecutionEngine` Protocol, `EngineExecutionRequest`, and `EngineExecutionResult` DTOs. This Epic explicitly owns the addition of `expected_sdui_type` to `StepRule` (previously deferred by Epic 104 Phase 0.5).

## 2. Architectural Impact & Safeguards
- **DRY Compliance (SSOT)**: We eliminate ~150 lines of duplicated code. `LLMNodeStrategy` becomes the absolute Single Source of Truth (SSOT) for ALL AI step lifecycles, guaranteeing that any future telemetry or retry enhancements automatically apply to both Reasoning and Synthesis.
- **Strict Separation of Concerns**: By implementing the Synthesis logic as an `ExecutionEngine`, it remains completely isolated from the `TDAEngine`. The DAG will execute them as separate nodes; they just share the same lifecycle manager.
- **Fail-Fast Safety & Dumb Engine Enforcement**: The extraction must ensure that the `GlobalAtomBlackboard` validation (Epic 101 Rule 1) is preserved inside the `SynthesisEngine.execute()` method. However, the engine MUST remain cognitively "dumb" regarding schemas. It MUST NOT perform any dynamic schema mapping itself; instead, it must strictly pass the pre-compiled `request.compiled_schema` down to the `LLMTaskExecutor`.
- **Schema Pre-Compilation Responsibility Chain (CRITICAL)**: Currently, `PreHydratedSynthesisStrategy` directly calls `self.compiler.build_dynamic_schema()` and `self.compiler.compile_static_instructions()` (lines 87-98 of `pre_hydrated_synthesis.py`). Since the `SynthesisEngine` MUST NOT use a `compiler` injection, ALL three compilation responsibilities MUST be lifted into `LLMNodeStrategy` via a new synthesis-specific pre-compilation branch. Specifically:
  1. `LLMNodeStrategy.execute()` detects `step.engine_override == "SYNTHESIS"` or `context.model_strategy == "synthesis"` and enters the synthesis compilation path.
  2. Loads criteria blocks from the database (mirroring lines 67-79 of `pre_hydrated_synthesis.py`).
  3. Calls `self.compiler.build_dynamic_schema()` using `StepRule.expected_sdui_type` to determine the target Pydantic schema.
  4. Calls `self.compiler.compile_static_instructions()` to produce static system messages.
  5. Constructs a `CompiledPrompt` with `static_messages` and an empty `dynamic_messages` (the engine will append the blackboard as its only dynamic message).
  6. Packages the compiled schema, hydrated messages list, bound LLM client, and concurrency tokens into the `EngineExecutionRequest` DTO.
  This ensures absolute separation: `LLMNodeStrategy` = compilation + lifecycle, `SynthesisEngine` = execution only.
- **Absolute Engine Statelessness**: Just like `TDAEngine`, the `SynthesisEngine` MUST be strictly stateless. It must NOT store any runtime variables, extraction results, or context in `self`. All data must flow immutably through the `execute()` signature to prevent race conditions during highly concurrent DAG invocations.
- **Strict DTO Location & Circular Import Prevention**: The engine must return the exact same `EngineExecutionResult` DTO defined in Epic 104. This DTO must be centrally located (e.g., `backend_v2/models/dtos/engine.py`) to prevent `synthesis_engine.py` from creating circular dependencies with `llm.py` or other heavy ML modules.
- **Anti-Corruption Layer (Epic 104 Compliance)**: The new engine MUST wrap all execution failures (e.g., Pydantic parsing errors, LLM crashes) inside an `EngineExecutionException`. This guarantees that `LLMNodeStrategy`'s Dead Letter Queue (DLQ) routing can deterministically catch and process them.
- **Append-Only Law & Seed Data Validation**: Executions (results) MUST NOT and do not need to be migrated during refactoring. **Historical execution data has zero structural value and is considered entirely disposable during migrations.** Historical payload data is append-only and mutation is strictly prohibited. ONLY `seed_data.json` is updated for configuration changes. Any modifications to `seed_data.json` MUST strictly follow the *Vault Mutation Protocol* (e.g., re-seeding via `run_seed.py`).

## 3. Implementation Phases

### Phase 0: `expected_sdui_type` Field Addition (Prerequisite)
- **Ownership Declaration**: This field was deferred by Epic 104 (Phase 0.5: "REMOVED. Deferred to Epic 105"). Epic 105 MUST add it here to resolve the dependency chain.
- **Target File**: `backend_v2/models/v2_core.py` (specifically `StepRule` class)
- **Action**: Add `expected_sdui_type: Literal["markdown", "grid", "hero"] = Field(...)` to `StepRule`. This field explicitly declares the expected SDUI output schema for each step, used by the `SchemaFactory` and `PromptCompiler` for deterministic Pydantic validation. **The `"unknown"` value is STRICTLY PROHIBITED** — it would violate the `zero_compromise_pledge` by silently accepting unconfigured steps instead of crashing Fail-Fast.
- **Enum Rename (Atomic)**: Rename `EngineOverrideStrategy.PRE_HYDRATED_SYNTHESIS` → `EngineOverrideStrategy.SYNTHESIS` to reflect the unified engine architecture. The old enum value becomes semantically misleading after the legacy strategy deletion. Update ALL references in `dag_executor.py`, `seed_data.json`, and test fixtures simultaneously.
- **Seed Data Update**: Update `backend_v2/seed/seed_data.json` to: (1) add `expected_sdui_type` to all `StepRule` definitions within the `workflows` array (synthesis steps MUST use `"markdown"`), (2) rename all `"engine_override": "PRE_HYDRATED_SYNTHESIS"` values to `"engine_override": "SYNTHESIS"`.
- **Database Wipe**: After modifying the seed data, developers MUST run `uv run python backend_v2/seed/run_seed.py local` to flush old data.

### Phase 1: Engine Extraction & Parameter Object Utilization
- **Protocol Invariance (`engines/base.py`)**: The `ExecutionEngine` protocol signature from Epic 104 MUST REMAIN STRICTLY UNCHANGED to guarantee the Open/Closed Principle (OCP). It already utilizes the Parameter Object pattern (`EngineExecutionRequest` DTO), which includes `step` and `context`. The `SynthesisEngine` will natively read what it needs from this DTO (e.g., `request.context.context_variables`) without altering the global engine interface. The return type MUST strictly remain the `EngineExecutionResult` DTO.
- **Target File**: `backend_v2/services/orchestrator/engines/synthesis_engine.py`
- Create `SynthesisEngine` implementing the strictly unmodified `ExecutionEngine` Protocol.
- Move the core execution logic from `PreHydratedSynthesisStrategy` into `SynthesisEngine.execute(request: EngineExecutionRequest)`. This includes:
  1. Validating the `__GLOBAL_ATOM_BLACKBOARD__` directly from `request.context.context_variables`. If missing, the engine MUST crash immediately with an `AppException` (Zero-Compromise Fail-Fast).
  2. **Idempotency & XML Structural Isolation (Anti-Format-Crash)**: Creating a local copy of the hydrated messages list via `list(request.hydrated_messages)` + individual `dict(msg)` copies before appending the blackboard data. The engine MUST treat the incoming `request` DTO as strictly immutable to prevent state leakage during retry loops. Furthermore, to eliminate "Format Crashes" entirely and comply with the **High-Fidelity Prompting & Caching Mandate**, ANY inline string substitution (like `.format()` or Regex-based custom parsers) is **STRICTLY PROHIBITED** as it constitutes a "Duct-Tape" hack. The `SynthesisEngine` MUST NOT attempt to replace `{variable}` syntax inline. The SynthesisEngine MUST NOT attempt to alter or concatenate existing message strings. Instead, highly dynamic data like the `GlobalAtomBlackboard` MUST be appended as an entirely new, separate message object (e.g., `{"role": "user", "content": "\n<global_atom_blackboard>\n[JSON_DATA]\n</global_atom_blackboard>\n"}`) at the very end of the copied messages list. This perfectly isolates the data structure using strict XML boundaries, forces the LLM's attention to the most recent input, and preserves Static-First Context Caching (KI: Provider-Agnostic Caching). The `SynthesisEngine` MUST NOT use a `compiler` injection, relying solely on the pre-compiled context passed via `request.hydrated_messages` and `request.compiled_schema`.
  3. **Real-Time Observability (Epic 104 Compliance)**: Emitting a structured debug log containing the final, hydrated messages list BEFORE executing the LLM call. This prevents an "Observability Black Hole" by ensuring the exact prompt state is forensically auditable even if the LLM network request fatally crashes.
  4. Executing the task via `LLMTaskExecutor.execute_structured_task()`. The engine MUST strictly pass down `request.bound_client` (the LLM multiplexer), `request.compiled_schema` (for Pydantic validation), and the hydrated local copy of the messages. It must also pass down the `semaphore` and `running_event` to prevent Concurrency Leaks.
  5. Packaging the response strictly into the `EngineExecutionResult` DTO. This MUST explicitly include picking up the rich telemetry (API latencies, token counts) returned by `LLMTaskExecutor` and correctly mapping it into the `EngineExecutionResult.trace_events` list so the `LLMNodeStrategy` can serialize it to the global audit log.
  6. Acting as an **Anti-Corruption Layer** by catching all raw exceptions (e.g. schema parsing errors) and wrapping them in `EngineExecutionException` for deterministic DLQ routing. This MUST implement the RFC 7807 Dual-Reporting pattern: every caught exception must be preceded by a structured `logger.error` containing context before being wrapped and raised.

### Phase 2: DAG Executor Wiring & Strategy Registry
- **Target File**: `backend_v2/services/orchestrator/dag_executor.py`
- **Quorum 2026 Invariant Enforcement**: The existing `if/elif/else` routing chain for `strategy_impl` in `dag_executor.py` (lines 229-280) violates the Modernity Architect laws. You MUST completely delete the `if/else` chain and replace it with a **Factory-Based Strategy Registry** (lazy construction, eager key registration). The registry maps string keys (e.g., `"synthesis"`, `"logic"`, `"reasoning"`) to factory callables (lambdas or functions) that lazily construct the appropriate `NodeStrategy` with its dependencies. This avoids triggering cold-start imports at module load time while maintaining OCP compliance.
- **Registry Implementation**: Define a `dict[str, Callable[..., NodeStrategy]]` at the method scope of the routing function. Each factory callable encapsulates the lazy import and construction of its target strategy. Unrecognized strategy keys MUST trigger an immediate Fail-Fast `AppException` (no default fallback).
- Since `SynthesisEngine` is "dumb" and MUST NOT take `self.compiler`, it MUST accept an instantiated `LLMTaskExecutor` via its constructor. `dag_executor.py` already instantiates `llm_executor = LLMTaskExecutor(self.compiler)` in this scope.
- The `"synthesis"` factory MUST lazily import and instantiate `LLMNodeStrategy` with the newly created lightweight `SynthesisEngine(llm_executor)` injected as the engine. The `LLMClient.from_strategy()` resolution uses `context.model_strategy` (NOT a hardcoded `"reasoning"` string) to ensure the model is resolved dynamically from the step definition.

### Phase 3: Deletion of Legacy Strategy
- **Target File**: `backend_v2/services/orchestrator/strategies/pre_hydrated_synthesis.py`
- Completely delete this file, as its logic is now governed by `LLMNodeStrategy` + `SynthesisEngine`.
- Remove references from `backend_v2/services/orchestrator/strategies/__init__.py`.

### Phase 4: Observability Logger Refactoring (DEFERRED TO EPIC 107)
- **Status: DEFERRED**. The proposed "Memory Buffering + Atomic Write" refactoring of `llm_debug_logger.py` is a "Big Bang" architectural change that risks corrupting existing TDA forensic logs. It MUST NOT be performed during Epic 105.
- Epic 105 MUST rely on the existing logging mechanism. The `SynthesisEngine` should just pass necessary information to the existing logger or rely on `LLMNodeStrategy`'s existing telemetry. Atomic logging hardening is formally moved to Epic 107.

### Phase 5: Automated Testing
- **New Tests**: Create `tests/unit/services/orchestrator/engines/test_synthesis_engine.py` to test the new engine in isolation (mocking `LLMTaskExecutor` and the blackboard).
- **Cleanup**: Delete `tests/unit/services/orchestrator/strategies/test_pre_hydrated_synthesis.py` (or port relevant tests to the new engine test file).

## 4. Required User Review
- **Engine Naming**: The proposed name is `SynthesisEngine`. We avoid the name `StandardExecutionEngine` because Synthesis currently requires the `GlobalAtomBlackboard`, making it slightly specialized compared to a purely "vanilla" direct LLM call. Does this naming convention align with the roadmap?
- **`expected_sdui_type` Ownership**: This Epic adds `expected_sdui_type` to `StepRule`, resolving the deferral from Epic 104 Phase 0.5. This field is a prerequisite for both Epic 105 (schema compilation) and Epic 106 (OutputProfile simplification). Confirm this ownership is acceptable.

## 5. Cross-Epic Synchronization (Epic 104 & 106)
- **Dependency on Epic 104**: This Epic MUST NOT be started until Epic 104 has fully merged the `ExecutionEngine` Protocol and `EngineExecutionRequest`/`Result` DTOs into the main branch.
- **Enabling Epic 106**: By deleting `PreHydratedSynthesisStrategy` and making the engine "dumb" (relying on `compiled_schema`), this Epic directly unlocks Epic 106's ability to safely delete the `synthesis` configuration object from `OutputProfile` and rely strictly on `StepRule.expected_sdui_type`.
- **Development Phase Wipe**: Since we are in active development, there are no strict database migration orders. Epic 105 and 106 can be treated as a single "Big Bang" architectural update. Developers simply update `seed_data.json` and wipe the local MongoDB.
