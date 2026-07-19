# EPIC 105: Synthesis Engine Unification

## 1. Goal Description
Following the extraction of the `TDAEngine` (Epic 104), the system now possesses a decoupled `ExecutionEngine` interface plugged into the `LLMNodeStrategy` (which acts as the SSOT Lifecycle Manager). However, `PreHydratedSynthesisStrategy` currently bypasses this entirely, operating as a parallel, standalone `NodeStrategy`.

**Objective**: Unify the architecture by converting the Synthesis execution logic into a `SynthesisEngine` (implementing the `ExecutionEngine` Protocol). This allows us to route Synthesis steps through `LLMNodeStrategy`, granting Synthesis tasks immediate access to advanced lifecycle features (Alias Engine hydration, standard telemetry, anomaly retry loops, and robust error handling) while completely deleting the duplicated `PreHydratedSynthesisStrategy` file.

## 2. Architectural Impact & Safeguards
- **DRY Compliance (SSOT)**: We eliminate ~150 lines of duplicated code. `LLMNodeStrategy` becomes the absolute Single Source of Truth (SSOT) for ALL AI step lifecycles, guaranteeing that any future telemetry or retry enhancements automatically apply to both Reasoning and Synthesis.
- **Strict Separation of Concerns**: By implementing the Synthesis logic as an `ExecutionEngine`, it remains completely isolated from the `TDAEngine`. The DAG will execute them as separate nodes; they just share the same lifecycle manager.
- **Fail-Fast Safety**: The extraction must ensure that the `GlobalAtomBlackboard` validation (Epic 101 Rule 1) and dynamic schema mapping tailored for Synthesis are perfectly preserved inside the `SynthesisEngine.execute()` method.

## 3. Implementation Phases

### Phase 1: ExecutionEngine Protocol Expansion & Engine Extraction
- **Protocol Expansion (`engines/base.py`)**: The original `ExecutionEngine` protocol (Epic 104) is too narrow. You MUST expand its `execute()` signature to accept `step: StepRule` and `context: StrategyContext`. Without this, the `SynthesisEngine` cannot access the `__GLOBAL_ATOM_BLACKBOARD__`.
- **Target File**: `backend_v2/services/orchestrator/engines/synthesis_engine.py`
- Create `SynthesisEngine` implementing the updated `ExecutionEngine` Protocol.
- Move the core execution logic from `PreHydratedSynthesisStrategy` into `SynthesisEngine.execute()`. This includes:
  1. Validating the `__GLOBAL_ATOM_BLACKBOARD__` from `context.context_variables`.
  2. Compiling the system prompt and payload block using `self.compiler` (passed via constructor).
  3. Executing the task via `LLMTaskExecutor.execute_structured_task()`.
  4. Packaging the response into the standard `dict[str, Any]` format.

### Phase 2: DAG Executor Wiring
- **Target File**: `backend_v2/services/orchestrator/dag_executor.py`
- Modify the routing logic for `step_def.model_strategy == "synthesis"`.
- Instead of instantiating `PreHydratedSynthesisStrategy`, explicitly instantiate `LLMNodeStrategy` and inject the newly created `SynthesisEngine`:
  ```python
  from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
  strategy_impl = LLMNodeStrategy(
      ...,
      engine=SynthesisEngine(self.compiler)
  )
  ```

### Phase 3: Deletion of Legacy Strategy
- **Target File**: `backend_v2/services/orchestrator/strategies/pre_hydrated_synthesis.py`
- Completely delete this file, as its logic is now governed by `LLMNodeStrategy` + `SynthesisEngine`.
- Remove references from `backend_v2/services/orchestrator/strategies/__init__.py`.

### Phase 4: Automated Testing
- **New Tests**: Create `tests/unit/services/orchestrator/engines/test_synthesis_engine.py` to test the new engine in isolation (mocking `LLMTaskExecutor` and the blackboard).
- **Cleanup**: Delete `tests/unit/services/orchestrator/strategies/test_pre_hydrated_synthesis.py` (or port relevant tests to the new engine test file).

## 4. Required User Review
- **Engine Naming**: The proposed name is `SynthesisEngine`. We avoid the name `StandardExecutionEngine` because Synthesis currently requires the `GlobalAtomBlackboard`, making it slightly specialized compared to a purely "vanilla" direct LLM call. Does this naming convention align with the roadmap?
