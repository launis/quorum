# EPIC 138: TDA Engine DTO Projection Refactor (ResultProjector Eradication)

## 1. Goal and Rationale
The primary goal of this Epic is to enforce the architectural invariants defined in @[C:\Users\risto\.gemini\antigravity-ide\knowledge\dag_engine_dto_projection_rules\artifacts\ki_dag_engine_dto_projection_rules.md] and @[C:\Users\risto\.gemini\antigravity-ide\knowledge\tripartite_pipeline_architecture\artifacts\ki_tripartite_pipeline_architecture.md].

Currently, `TDAEngine` utilizes an intermediate proxy layer (`ResultProjector`) to translate raw execution states (`LinkedAtomGraph` and `AtomExecutionState`) into Presentation-ready DTOs (`AtomResultDTO`, `HydratedAtomDTO`) before returning them to the orchestrator.

This violates strict CQRS phase isolation because:
1. It leaks Server-Driven UI (SDUI) concepts (specifically: `SDUIComponentType.ERROR_CARD`) deep into the Execution Phase.
2. It tightly couples the heavy mathematical extraction engine to the volatile presentation layer.
3. It forces the `ExecutionEngine` protocol to return "lossy" flattened DTOs instead of raw forensic execution graphs.

By removing `ResultProjector` and pushing the projection logic to the Synthesis/SDUI boundary (Universal Transformer Hub / @[backend_v2/services/blueprint.py]), we achieve a pure, decoupled execution engine and a resilient Dumb Painter frontend.

---

## 2. Architectural Impact & Compliance Matrix

### 2.1 Deprecations & Sunset List
- **Eradicated Layer:** `ResultProjector` proxy layer is safely deleted to decouple the mathematical extraction engine from the presentation layer.
- **Deleted Files:** @[backend_v2/services/orchestrator/result_projector.py] and @[backend_v2/tests/unit/services/orchestrator/test_result_projector.py].

### 2.2 Retained SSOT Invariants
- **Zero-Fallback Mandate:** Procedural `if` checks in the service layer are banned. `AtomExecutionState` MUST raise a `ValidationError` immediately upon instantiation if it is marked as `PASSED` or `FAILED` but lacks an `evaluation_reasoning`. No silent substitution with empty strings is allowed.
- **Strict Pydantic V2:** The raw `LinkedAtomGraph` and `AtomExecutionState` must strictly maintain `ConfigDict(strict=True, frozen=True, extra="forbid")`.
- **No Naked Dicts:** All data transiting between the background worker (`TDAEngine`) and the API router (`Blueprint`) must be strictly typed DTOs.

### 2.3 Compliance Gates
- **CQRS Phase Isolation:** The execution graph must be kept pure and decoupled from the Server-Driven UI concepts.
- **Anti-God File Principle:** Complex graph logic MUST be strictly separated into a pure, decoupled helper module.

---

## 3. Execution Phases

### Task Breakdown & Context Quarantine Strategy
To prevent context amnesia and ensure architectural adherence, this Epic's execution is broken down into small, isolated phases. At the end of each phase, a session handover is mandated using the `/tier5-session-handover` command to flush the LLM context window. The next phase begins by resuming the session with `/tier5-resume`, providing a clean state focused entirely on the immediate target files.

<execution_block>
<step id="1" name="Phase 1: Execution Engine Protocol & DTO Refactor">
<action>
**Objective:** Decouple `EngineExecutionResult` from presentation DTOs.
- **Action 1:** Modify @[backend_v2/models/dtos/engine.py] -> `EngineExecutionResult`. 
  - Remove `results: list[AtomResultDTO]` and `hydrated_references: dict[str, HydratedAtomDTO]`.
  - Add `nodes: list[LinkedAtomGraph] = Field(default_factory=list)` and `states: dict[str, AtomExecutionState] = Field(default_factory=dict)` to carry the pure execution graph (importing them from `backend_v2.models.dtos.dag_models`).
  - **Safety:** Make these fields optional with `default_factory` so `SynthesisEngine` (which only returns `synthesis_output`) does not break.
</action>
<action>
- **Action 2:** Modify @[backend_v2/services/orchestrator/engines/tda_engine.py].
  - Remove the call to `ResultProjector.project(...)`.
  - Return the raw `nodes` (from `linker` or `request.shuffled_atoms`) and `states` (from `dag_executor`) directly inside the `EngineExecutionResult`.
</action>
<action>
- **Action 3:** Modify @[backend_v2/services/orchestrator/strategies/llm.py].
  - Update how `LLMNodeStrategy` packs the `final_dict` for the `TraceEvent` payload. Instead of dumping `results` and `hydrated_references`, dump the pure execution graph alongside the `matrix_id`:
    ```python
    final_dict = {
        "nodes": [n.model_dump(mode="json") for n in engine_result.nodes],
        "states": {k: v.model_dump(mode="json") for k, v in engine_result.states.items()},
        "matrix_id": matrix_block_id,
    }
    ```
</action>
<action>
- **Action 4:** Enforce the **Zero-Fallback Mandate** structurally. Add a Pydantic `@model_validator(mode='after')` to `AtomExecutionState` (in @[backend_v2/models/dtos/dag_models.py]) that raises a `ValueError` if the state is `PASSED` or `FAILED` but lacks an `evaluation_reasoning`. This ensures Fail-Fast behavior upon deserialization anywhere in the system.
</action>
<action>Execute `/tier5-session-handover` to flush context and start a new session.</action>
</step>

<step id="2" name="Phase 2: Universal Transformer Hub Projection">
<action>Execute `/tier5-resume` to restore context and begin Phase 2.</action>
<action>
**Objective:** Shift the topological sorting and DTO mapping to the SDUI orchestrator without creating God Files.
- **Action 1:** Create a pure, decoupled helper module `backend_v2/services/topological_sorter.py` containing a function `sort_nodes` that handles the Kahn's algorithm topological sorting (migrated from @[backend_v2/services/orchestrator/result_projector.py]). This strictly enforces the Anti-God File principle by keeping complex graph logic out of the @[backend_v2/services/blueprint.py] orchestrator.
</action>
<action>
- **Action 2:** Create a private static method `_project_engine_results` inside @[backend_v2/services/blueprint.py] that delegates the sorting to `backend_v2/services/topological_sorter.py` and maps the results. NOTE: SDUI Presentation Adapters in @[backend_v2/services/sdui/adapters/] must NOT be used for this logic, as they are restricted to outputting `AnySduiBlock`.
</action>
<action>
- **Action 3:** Update @[backend_v2/services/blueprint.py] (`build_report_dto`) to completely REMOVE the legacy parsing of `"results"` and `"hydrated_references"`. Replace it with strictly checking for `"nodes"`, `"states"`, and `"matrix_id"`. Deserialize them into `LinkedAtomGraph` and `AtomExecutionState`, execute `_project_engine_results(nodes, states, matrix_id)`, and append the mapped output to `v2_results` and `v2_hydrated_refs`.
</action>
<action>
- **Action 4:** Safely delete @[backend_v2/services/orchestrator/result_projector.py] AND its corresponding test file @[backend_v2/tests/unit/services/orchestrator/test_result_projector.py].
</action>
<action>Execute `/tier5-session-handover` to flush context and start a new session.</action>
</step>

<step id="3" name="Phase 3: Test Suite Alignment">
<action>Execute `/tier5-resume` to restore context and begin Phase 3.</action>
<action>
**Objective:** Fix upstream mocks and tests that expect `ResultProjector` formatting.
- **Action 1:** Update @[backend_v2/tests/unit/models/dtos/test_engine.py] (strictness and immutability tests) to supply `nodes` and `states` instead of `results` and `hydrated_references`.
</action>
<action>
- **Action 2:** Update @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py] to assert that `TDAEngine.execute()` returns pure `nodes` and `states`.
</action>
<action>
- **Action 3:** Update @[backend_v2/tests/unit/services/test_blueprint.py] to supply raw `nodes`/`states`/`matrix_id` in trace payloads and assert that the blueprint correctly performs the topological sort and SDUI projection.
</action>
<action>
- **Action 4:** Add explicit negative tests to @[backend_v2/tests/unit/models/dtos/test_dag_models.py]:
  - **Negative Test 1:** Attempt to instantiate an `AtomExecutionState` marked `PASSED` with an empty `evaluation_reasoning` and assert that a Pydantic `ValidationError` is raised (Zero-Fallback Rule).
</action>
<action>
- **Action 5:** Add explicit negative tests to `backend_v2/tests/unit/services/test_topological_sorter.py`:
  - **Negative Test 1:** Supply cyclic dependencies in `nodes` and verify Kahn's algorithm safely processes remaining nodes without infinite loop lockups.
</action>
</step>
</execution_block>

### Phase 1: Execution Engine Protocol & DTO Refactor
#### [MODIFY] @[backend_v2/models/dtos/engine.py]
#### [MODIFY] @[backend_v2/services/orchestrator/engines/tda_engine.py]
#### [MODIFY] @[backend_v2/services/orchestrator/strategies/llm.py]
#### [MODIFY] @[backend_v2/models/dtos/dag_models.py]

### Phase 2: Universal Transformer Hub Projection
#### [NEW] @[backend_v2/services/topological_sorter.py]
#### [MODIFY] @[backend_v2/services/blueprint.py]
#### [DELETE] @[backend_v2/services/orchestrator/result_projector.py]
#### [DELETE] @[backend_v2/tests/unit/services/orchestrator/test_result_projector.py]

### Phase 3: Test Suite Alignment
#### [MODIFY] @[backend_v2/tests/unit/models/dtos/test_engine.py]
#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]
#### [MODIFY] @[backend_v2/tests/unit/services/test_blueprint.py]
#### [MODIFY] @[backend_v2/tests/unit/models/dtos/test_dag_models.py]
#### [NEW] @[backend_v2/tests/unit/services/test_topological_sorter.py]

---

## 4. Constraints & Guardrails

- **Zero-Fallback Mandate:** If an `AtomExecutionState` is marked as PASSED or FAILED but lacks `evaluation_reasoning`, the Pydantic model MUST raise a `ValidationError` immediately upon instantiation (Fail-Fast). Procedural `if` checks in the service layer are banned. No silent substitution with empty strings.
- **Strict Pydantic V2:** The raw `LinkedAtomGraph` and `AtomExecutionState` must maintain `ConfigDict(strict=True, frozen=True, extra="forbid")`.
- **No Naked Dicts:** All data transiting between the background worker (TDAEngine) and the API router (Blueprint) must be encapsulated in strictly typed DTOs. Raw JSON manipulation is banned.

---

## 5. Required Knowledge Items (KI Registry)

<required_knowledge_items>
- @[.agents/rules/00-antigravity-core.md]
- @[.agents/rules/01-python-backend.md]
- @[C:\Users\risto\.gemini\antigravity-ide\knowledge\dag_engine_dto_projection_rules\artifacts\ki_dag_engine_dto_projection_rules.md]
- @[C:\Users\risto\.gemini\antigravity-ide\knowledge\tripartite_pipeline_architecture\artifacts\ki_tripartite_pipeline_architecture.md]
</required_knowledge_items>
