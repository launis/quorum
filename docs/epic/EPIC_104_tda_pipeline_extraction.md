# EPIC 104: TDA Pipeline Extraction & Strategy Injection

## 1. Goal Description
The Quorum Phase 3 architecture orchestrates LLM executions through `LLMNodeStrategy` (in `llm.py`). Currently, `llm.py` acts as a monolithic "God Class" by serving as both the SSOT Lifecycle Manager (handling pre-hooks, schemas, post-hooks, telemetry, and anomaly retries) AND the execution engine. Specifically, lines 560-612 of `llm.py` contain a hardcoded, inline execution of the Topological Data Analysis (TDA) pipeline (`TwoPassAtomizer` → `SlidingWindowLinker` → `EnrichedDagExecutor` → `ResultProjector`).

**Objective**: Decouple the execution logic from the lifecycle management. Extract the inline TDA pipeline into a standalone, injectable `ExecutionEngine` following the Composition/Strategy Injection pattern. This resolves major Single Responsibility Principle (SRP) and Open-Closed Principle (OCP) violations, enabling the future integration of diverse execution paths (e.g., standard RAG, MCP tool loops, direct LLM generation) without modifying the core `LLMNodeStrategy`.

## 2. Architectural Impact & Safeguards
- **Structural Subtyping via Protocol**: We will introduce an `ExecutionEngine` Protocol instead of an ABC. This adheres to Quorum's lightweight duck-typing rules for strategy injection. The Protocol will enforce a single `execute()` method that returns a standard `dict[str, Any]` matching the expected `final_dict` structure.
- **Zero Cold Start Protection (Lazy Loading)**: The existing `llm.py` uses inline imports to avoid loading the heavy AI pipeline components globally. However, moving the pipeline to a dedicated `tda_engine.py` means the sub-services (which are standard Quorum modules) can be imported at the top-level of `tda_engine.py`. To protect the global execution pipeline from PyO3 initialization delays and cold start bloat (per the `inline_imports_ban` exception), the `TDAEngine` class itself will be **lazily imported** inside the `LLMNodeStrategy` constructor and the `dag_executor.py` wiring logic.
- **Backward Compatibility**: The new `engine` parameter in `LLMNodeStrategy` will default to `None`, dynamically instantiating the `TDAEngine` fallback. This ensures all existing unit tests and untocuhed workflow logic continue to function without immediately breaking backwards compatibility.

## 3. Implementation Phases

### Phase 1: ExecutionEngine Protocol & TDA Engine Extraction
- **Protocol Definition (`engines/base.py`)**: Define the `ExecutionEngine` Protocol with the `execute()` signature accepting `bound_client`, `global_source_text`, `target_locale`, and `progress_callback`.
- **TDA Engine Implementation (`engines/tda_engine.py`)**: Move the entire inline block from `llm.py` into this engine. 
- **Top-Level Standard Imports**: Import the 5 sub-services (`LLMTaskExecutor`, `TwoPassAtomizer`, `SlidingWindowLinker`, `EnrichedDagExecutor`, `ResultProjector`) globally at the top of `tda_engine.py`. These are standard modules (not native ML extensions), meaning they belong at the top level to adhere to Quorum's strict `inline_imports_ban`.

### Phase 2: LLMNodeStrategy Refactoring
- **Constructor Override (`strategies/llm.py`)**: Override `LLMNodeStrategy.__init__` to accept all `NodeStrategy` positional arguments plus an optional `engine: Any | None = None`. 
- **Lazy Instantiation**: If `engine` is `None`, perform a localized lazy import of `TDAEngine` and instantiate it. The `Any` type hint avoids a top-level import of the `ExecutionEngine` Protocol, preserving the lazy-load barrier.
- **Delegated Execution**: Replace the 50-line inline TDA pipeline with a single `await self._engine.execute(...)` delegation. `llm.py` strictly retains ownership of telemetry, schema compilation, and trace event generation.

### Phase 3: DAG Executor Wiring
- **Explicit DI Injection (`dag_executor.py`)**: Update the `NodeExecutor.execute()` step routing logic. When instantiating `LLMNodeStrategy` (e.g., in the `"reasoning"` branch and default `else` branch), explicitly inject the `TDAEngine(self.compiler)`.
- **Lazy DI Import**: Perform the `from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine` inline within the conditional branches, exactly matching the existing resilient pattern used for `PreHydratedSynthesisStrategy`.

### Phase 4: Automated Testing
- **Engine Unit Tests**: Create `test_tda_engine.py` to mock the 5 sub-services and verify proportional progress callback routing (0-15%, 15-35%, 35-60%, 60-100%).
- **Strategy Unit Tests**: Update `test_llm.py` to inject a mock `ExecutionEngine` and verify that `LLMNodeStrategy` delegates execution properly without invoking the actual TDA logic. Ensure the existing parameter-less fixture maintains backwards compatibility.

## 4. Required User Review
- **Future Non-TDA Engines**: Currently, all LLM steps use the TDA pipeline unconditionally. Should we proactively create a `StandardExecutionEngine` for direct synthesis steps that bypass atom extraction? 
  - *Recommendation*: **Defer**. The extraction of the pipeline itself establishes the correct architectural boundary. Additional engines should be added incrementally when feature-driven requirements dictate.
