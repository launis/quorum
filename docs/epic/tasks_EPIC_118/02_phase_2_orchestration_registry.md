# Phase 2: Orchestration, Registry & Prompt Compiler Updates

Overview: Pass the `shuffled_atoms` to engine request safely and implement Context-Enriched Decompose-Verify in `TDAEngine`.

```xml
<execution_protocol>
<execution_block phase="phase_2" consumer="tier2-execute">
  <summary><![CDATA[Orchestration, Registry & Prompt Compiler Updates]]></summary>
  <step id="phase_2.0" scope="MODIFY">
    <action>Add `shuffled_atoms: list[FlattenedAtom] | None = None` to the `EngineExecutionRequest` model to allow the orchestrator to pass the matrix assertions to the execution engine safely.</action>
    <target>@[c:\src\quorum\backend_v2\models\dtos\engine.py]</target>
    <invariants>
      <must>Preserve ConfigDict(strict=True, extra="forbid") on EngineExecutionRequest</must>
    </invariants>
    <tests min_negative="0">
      <positive>Verify dtos/engine.py compiles</positive>
    </tests>
    <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/models/dtos/engine.py --test</audit_command>
  </step>
  <step id="phase_2.1" scope="MODIFY">
    <action>Pass the `shuffled_atoms` from `state_data` when the step is a matrix step. To enforce the **Fail-Fast Hydration Mandate** and **Zero-Duct-Tape Ban**, use a `try...except KeyError` block around `state_data["shuffled_atoms"]` when `is_matrix_step` is True, and explicitly log and raise an `AppException(status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})` to prevent unhandled 500s. Pass this hydrated list to the `EngineExecutionRequest` instantiations.</action>
    <target>@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]</target>
    <invariants>
      <must>Raise structured AppException on KeyError for shuffled_atoms access when is_matrix_step is True</must>
      <must>TypeAdapter(list[FlattenedAtom]).validate_python(raw_atoms, strict=False) for hydration per python_314_root_model_ban</must>
      <must>Pass shuffled_atoms=hydrated_shuffled_atoms into BOTH EngineExecutionRequest constructor calls in llm.py (synthesis and regular paths)</must>
      <forbidden>dict.get() defensive access, modifying chunking logic later in the file, asyncio.gather, native KeyError crash without AppException</forbidden>
    </invariants>
    <tests min_negative="2">
      <positive>Verify llm.py compiles and integrates correctly</positive>
      <negative>Verify missing shuffled_atoms raises structured AppException (test_llm_strategy_missing_atoms_crash)</negative>
      <negative>Verify invalid shuffled_atoms type triggers Pydantic ValidationError (test_tda_engine_invalid_shuffled_atoms_type)</negative>
    </tests>
    <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py --test</audit_command>
    <demolish>REMOVE: the existing safe access `if is_matrix_step and "shuffled_atoms" in state_data: shuffled_atoms = state_data["shuffled_atoms"]` pattern. REPLACE WITH: `try...except KeyError → AppException` pattern per Fail-Fast Hydration Mandate.</demolish>
  </step>
  <step id="phase_2.2" scope="MODIFY">
    <action>Implement the **Context-Enriched Decompose-Verify Pipeline** in `TDAEngine.execute()`. Update `test_tda_engine.py` `engine_request` fixture to include `shuffled_atoms=None`. If `request.shuffled_atoms` is present (Matrix path): execute Phase 0+1 to generate enriched context (Ontology + Hydrated Text), construct `evaluation_context` (DO NOT wrap in `<context>` tags manually, as `EnrichedDagExecutor` already does this), map the `FlattenedAtom` objects in `request.shuffled_atoms` into `ExtractedAtom` models, encapsulate them into `LinkedAtomGraph` nodes with empty `depends_on`, skip `SlidingWindowLinker`, and pass `evaluation_context` as `source_text` to `EnrichedDagExecutor.execute_graph()`. If `request.shuffled_atoms` is None (Regular path): preserve existing behavior with `SlidingWindowLinker` and `global_source_text`. Adjust progress callback ranges for Matrix path (skip linker allocation).</action>
    <target>@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]</target>
    <target>@[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\engines\test_tda_engine.py]</target>
    <invariants>
      <must>Preserve AliasEngine block tags ([B0], [B1]) in hydrated_text within evaluation_context</must>
      <must>Static-First Caching: full_context at prompt top in XML context tags per context_enrichment_cache_survival KI</must>
      <must>_MATRIX_SOURCE_SENTINEL module-level constant per zero_db_hardcoding_mandate</must>
      <must>ExtractedAtom nodes use is_logical_deduction=True to allow null source_quote for matrix assertions</must>
      <forbidden>Raw dict state passing, asyncio.gather, exposing raw tda_id UUIDs to the LLM prompt</forbidden>
    </invariants>
    <tests min_negative="2">
      <positive>test_tda_engine_matrix_path: Verify EnrichedDagExecutor is called with mapped matrix atoms and enriched full_context</positive>
      <positive>test_tda_engine_no_shuffled_atoms_unchanged: Verify Regular TDA path uses SlidingWindowLinker unchanged</positive>
      <negative>Verify invalid shuffled_atoms structure triggers ExtractedAtom Pydantic ValidationError</negative>
      <negative>Verify missing tda_id triggers ExtractedAtom validation crash</negative>
    </tests>
    <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/services/orchestrator/engines/tda_engine.py --test</audit_command>
  </step>
</execution_block>
</execution_protocol>
```
