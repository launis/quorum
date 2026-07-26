# Phase 2: Orchestration, Registry & Prompt Compiler Updates

**Goal**: Implement the Context-Enriched Decompose-Verify Pipeline in the TDA engine and LLM strategy.

**Target Files**:
- @[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py] (Modify)
- @[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py] (Modify)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="fail_fast_hydration_mandate">All uncertain data flowing as dictionaries MUST be hydrated via `.model_validate()` IMMEDIATELY before processing.</constraint>
  <constraint invariant="zero_db_hardcoding_mandate">Logic MUST always be based on the abstract attributes, schema types, or dynamically injected configuration values. Do not use magic strings like 'MATRIX'. Use a module-level constant like `_MATRIX_SOURCE_SENTINEL`.</constraint>
  <constraint invariant="universal_quality_gate">Run backend audit loop.</constraint>
  <constraint invariant="atomic_checkpoint_mandate">Atomic commits required.</constraint>
  <constraint invariant="python_314_root_model_ban">Always use TypeAdapter for array validation instead of RootModel.</constraint>
  <constraint invariant="orchestrator_god_object_fragility">Run FULL backend audit loop and evaluate entire topological flow.</constraint>

  <step id="1" name="LLM Strategy Hydration">
    <action>Pass the `shuffled_atoms` from `state_data` when the step is a matrix step.</action>
    <target>@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]</target>
    <instruction>
      - Replace `if is_matrix_step and "shuffled_atoms" in state_data:` with an unconditional direct key access `raw_atoms = state_data["shuffled_atoms"]` when `is_matrix_step` is True. This enforces Fail-Fast (KeyError to 500).
      - Hydrate raw array using `hydrated_shuffled_atoms = TypeAdapter(list[FlattenedAtom]).validate_python(raw_atoms, strict=False)`.
      - Pass `shuffled_atoms=hydrated_shuffled_atoms` into the `EngineExecutionRequest` constructor.
    </instruction>
  </step>
  
  <step id="2" name="Context-Enriched Decompose-Verify Pipeline">
    <action>Implement Matrix vs Regular path in TDAEngine.execute().</action>
    <target>@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]</target>
    <instruction>
      - If `request.shuffled_atoms` is present (Matrix path): execute Phase 0+1 to generate enriched context, construct `evaluation_context` with `&lt;context&gt;` XML wrapper, map predefined matrix atoms into `LinkedAtomGraph` nodes preserving `tda_id` (via `request.shuffled_atoms[i].atom_id`), skip `SlidingWindowLinker`, and pass `evaluation_context` to `EnrichedDagExecutor.execute_graph()`.
      - Use `_MATRIX_SOURCE_SENTINEL: Final[str] = "MATRIX"` module-level constant.
      - ExtractedAtom nodes use `is_logical_deduction=True` and `source_quote=None`.
      - If `request.shuffled_atoms` is None (Regular path): preserve existing behavior with `SlidingWindowLinker` and `global_source_text`.
      - Adjust progress callback ranges for Matrix path (skip linker allocation).
    </instruction>
  </step>

  <step id="3" name="Testing &amp; Quality Gate Plan">
    <action>Run the backend audit loop.</action>
    <instruction>
      - Run `uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py --test`
      - Run `uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/services/orchestrator/engines/tda_engine.py --test`
      - Add explicit negative test cases: `test_llm_strategy_missing_atoms_crash` (missing key) and `test_tda_engine_invalid_shuffled_atoms_type` (invalid types).
      - Add positive test cases for Matrix path and Regular path in TDA engine.
    </instruction>
  </step>
  
  <step id="4" name="Integration Checkpoint">
    <action>Integration Checkpoint Plan.</action>
    <instruction>
      - Run full end-to-end REST API verification gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
    </instruction>
  </step>
</execution_protocol>
```
