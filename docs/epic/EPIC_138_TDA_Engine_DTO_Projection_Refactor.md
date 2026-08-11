# EPIC 138: TDA Engine DTO Projection Refactor (ResultProjector Eradication)

## 1. Goal and Rationale
The primary goal of this Epic is to enforce the architectural invariants defined in `ki_dag_engine_dto_projection_rules.md` and `ki_tripartite_pipeline_architecture.md`.

Currently, `TDAEngine` utilizes an intermediate proxy layer (`ResultProjector`) to translate raw execution states (`LinkedAtomGraph` and `AtomExecutionState`) into Presentation-ready DTOs (`AtomResultDTO`, `HydratedAtomDTO`) before returning them to the orchestrator.

This violates strict CQRS phase isolation because:
1. It leaks Server-Driven UI (SDUI) concepts (e.g., `SDUIComponentType.ERROR_CARD`) deep into the Execution Phase.
2. It tightly couples the heavy mathematical extraction engine to the volatile presentation layer.
3. It forces the `ExecutionEngine` protocol to return "lossy" flattened DTOs instead of raw forensic execution graphs.

By removing `ResultProjector` and pushing the projection logic to the Synthesis/SDUI boundary (Universal Transformer Hub / `blueprint.py`), we achieve a pure, decoupled execution engine and a resilient Dumb Painter frontend.

---

## 2. Execution Phases

### Phase 1: Execution Engine Protocol & DTO Refactor
**Objective:** Decouple `EngineExecutionResult` from presentation DTOs.
- **Action 1:** Modify `backend_v2/models/dtos/engine.py` -> `EngineExecutionResult`. 
  - Remove `results: list[AtomResultDTO]` and `hydrated_references: dict[str, HydratedAtomDTO]`.
  - Add `nodes: list[LinkedAtomGraph] = Field(default_factory=list)` and `states: dict[str, AtomExecutionState] = Field(default_factory=dict)` to carry the pure execution graph.
  - **Safety:** Make these fields optional with `default_factory` so `SynthesisEngine` (which only returns `synthesis_output`) does not break.
- **Action 2:** Modify `backend_v2/services/orchestrator/engines/tda_engine.py`.
  - Remove the call to `ResultProjector.project(...)`.
  - Return the raw `nodes` (from `linker` or `request.shuffled_atoms`) and `states` (from `dag_executor`) directly inside the `EngineExecutionResult`.
- **Action 3:** Modify `backend_v2/services/orchestrator/strategies/llm.py`.
  - Update how `LLMNodeStrategy` packs the `final_dict` for the `TraceEvent` payload. Instead of dumping `results` and `hydrated_references`, dump the pure execution graph alongside the `matrix_id`:
    ```python
    final_dict = {
        "nodes": [n.model_dump(mode="json") for n in engine_result.nodes],
        "states": {k: v.model_dump(mode="json") for k, v in engine_result.states.items()},
        "matrix_id": matrix_block_id,
    }
    ```

### Phase 2: Universal Transformer Hub Projection
**Objective:** Shift the topological sorting and DTO mapping to the SDUI orchestrator.
- **Action 1:** Create a private static method `_project_engine_results` directly inside `backend_v2/services/blueprint.py` that handles the Kahn's algorithm topological sorting (migrated from `result_projector.py`). NOTE: SDUI Presentation Adapters in `backend_v2/services/sdui/adapters/` must NOT be used for this logic, as they are restricted to outputting `AnySduiBlock`.
- **Action 2:** Enforce the **Zero-Fallback Mandate** within `_project_engine_results`: If an `AtomExecutionState` is `PASSED` or `FAILED` but lacks `evaluation_reasoning`, explicitly raise `AppException` (Fail-Fast).
- **Action 3:** Update `backend_v2/services/blueprint.py` (`build_report_dto`) to completely REMOVE the legacy parsing of `"results"` and `"hydrated_references"`. Replace it with strictly checking for `"nodes"`, `"states"`, and `"matrix_id"`. Deserialize them into `LinkedAtomGraph` and `AtomExecutionState`, execute `_project_engine_results(nodes, states, matrix_id)`, and append the mapped output to `v2_results` and `v2_hydrated_refs`.
- **Action 4:** Safely delete `backend_v2/services/orchestrator/result_projector.py` AND its corresponding test file `backend_v2/tests/unit/services/orchestrator/test_result_projector.py`.

### Phase 3: Test Suite Alignment
**Objective:** Fix upstream mocks and tests that expect `ResultProjector` formatting.
- **Action 1:** Update `backend_v2/tests/unit/models/dtos/test_engine.py` (strictness and immutability tests) to supply `nodes` and `states` instead of `results` and `hydrated_references`.
- **Action 2:** Update `backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py` to assert that `TDAEngine.execute()` returns pure `nodes` and `states`.
- **Action 3:** Update `backend_v2/tests/unit/services/test_blueprint.py` to supply raw `nodes`/`states`/`matrix_id` in trace payloads and assert that the blueprint correctly performs the topological sort and SDUI projection.
- **Action 4:** Add explicit negative tests to `backend_v2/tests/unit/services/test_blueprint.py`:
  - **Negative Test 1:** Supply an `AtomExecutionState` marked `PASSED` with an empty `evaluation_reasoning` and assert that `AppException` is raised (Zero-Fallback Rule).
  - **Negative Test 2:** Supply cyclic dependencies in `nodes` and verify Kahn's algorithm safely processes remaining nodes without infinite loop lockups.

---

## 3. Constraints & Guardrails

- **Zero-Fallback Mandate:** If an `AtomExecutionState` is marked as PASSED or FAILED but lacks `evaluation_reasoning`, the projection layer MUST raise an explicit `AppException` (Fail-Fast). No silent substitution with empty strings.
- **Strict Pydantic V2:** The raw `LinkedAtomGraph` and `AtomExecutionState` must maintain `ConfigDict(strict=True, frozen=True, extra="forbid")`.
- **No Naked Dicts:** All data transiting between the background worker (TDAEngine) and the API router (Blueprint) must be encapsulated in strictly typed DTOs. Raw JSON manipulation is banned.

---

## 4. Required Context Before Execution
The execution agent MUST read:
1. `.agents/rules/00-antigravity-core.md`
2. `.agents/rules/01-python-backend.md`
3. `C:\Users\risto\.gemini\antigravity-ide\knowledge\dag_engine_dto_projection_rules\artifacts\ki_dag_engine_dto_projection_rules.md`
4. `C:\Users\risto\.gemini\antigravity-ide\knowledge\tripartite_pipeline_architecture\artifacts\ki_tripartite_pipeline_architecture.md`
