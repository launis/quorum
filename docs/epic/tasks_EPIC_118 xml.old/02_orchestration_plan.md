# Phase 2 & 4: Orchestration, Registry & Prompt Compiler Updates

## Overview
Implement the Context-Enriched Decompose-Verify Pipeline in TDAEngine and enforce fail-fast hydration in llm.py strategy.

## Target Files
- `@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]`
- `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]`

```xml
<execution_protocol level="2_execute">
  <context_rules>
    <constraint invariant="python_314_root_model_ban">Always wrap standard types dynamically using the TypeAdapter pattern instead of RootModel.</constraint>
    <constraint invariant="fail_fast_hydration_mandate">All uncertain data flowing as dictionaries MUST be hydrated via .model_validate() IMMEDIATELY before processing. Use unconditional direct key access `state_data["shuffled_atoms"]` when `is_matrix_step` is True to raise KeyError on failure.</constraint>
    <constraint invariant="zero_db_hardcoding_mandate">Use module-level constant _MATRIX_SOURCE_SENTINEL.</constraint>
    <constraint invariant="xml_structural_sovereignty_mandate">Wrap dynamic contexts in rigid XML tags.</constraint>
    <constraint invariant="atom_aliasing_hydration_mandate">Intentionally exclude a.tda_id from string to prevent exposing raw UUIDs to the LLM.</constraint>
    <constraint invariant="high_fidelity_prompting_and_caching">Place massive full_context at absolute top of the prompt in <context> for O(1) Cache Survival.</constraint>
  </context_rules>

  <step id="phase_2.1" scope="MODIFY">
    <action>Pass the `shuffled_atoms` from `state_data` when the step is a matrix step. To enforce the **Fail-Fast Hydration Mandate** and **Zero-Duct-Tape Ban**, we MUST use **unconditional direct key access** `state_data["shuffled_atoms"]` when `is_matrix_step` is True. This means replacing the existing `if is_matrix_step and "shuffled_atoms" in state_data:` checks with unconditional access. If the `atom_flattening_hook` failed to inject the atoms, the native `KeyError` immediately crashes into a 500 error instead of silently passing `None` downstream.</action>
    <target>@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]</target>
    <invariants>
      <must>Unconditional state_data["shuffled_atoms"] key access when is_matrix_step is True (Fail-Fast KeyError → 500)</must>
      <must>TypeAdapter(list[FlattenedAtom]).validate_python(raw_atoms, strict=False) for hydration per python_314_root_model_ban</must>
      <must>Pass shuffled_atoms=hydrated_shuffled_atoms into BOTH EngineExecutionRequest constructor calls in llm.py (synthesis and regular paths)</must>
      <forbidden>dict.get() defensive access during schema compilation, modifying the chunking logic later in the file (around line 469) - it MUST remain unchanged, asyncio.gather, isinstance() duck-typing checks for atom validation</forbidden>
    </invariants>
    <tests min_negative="2">
      <positive>Verify llm.py compiles and integrates correctly</positive>
      <negative>Verify missing shuffled_atoms when is_matrix_step raises KeyError (test_llm_strategy_missing_atoms_crash)</negative>
      <negative>Verify invalid shuffled_atoms type triggers Pydantic ValidationError (test_tda_engine_invalid_shuffled_atoms_type)</negative>
    </tests>
    <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py --test</audit_command>
  </step>

  <step id="phase_2.2" scope="MODIFY">
    <action>Implement the **Context-Enriched Decompose-Verify Pipeline** in `TDAEngine.execute()`. If `request.shuffled_atoms` is present (Matrix path): execute Phase 0+1 to generate enriched context, construct `evaluation_context` with `<context>` XML wrapper, map predefined matrix atoms into `LinkedAtomGraph` nodes preserving `tda_id`, skip `SlidingWindowLinker`, and pass `evaluation_context` to `EnrichedDagExecutor.execute_graph()`. If `request.shuffled_atoms` is None (Regular path): preserve existing behavior with `SlidingWindowLinker` and `global_source_text`. Adjust progress callback ranges for Matrix path (skip linker allocation).</action>
    <target>@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]</target>
    <invariants>
      <must>Preserve AliasEngine block tags ([B0], [B1]) in hydrated_text within evaluation_context</must>
      <must>Static-First Caching: full_context at prompt top in XML context tags per context_enrichment_cache_survival KI</must>
      <must>_MATRIX_SOURCE_SENTINEL module-level constant per zero_db_hardcoding_mandate</must>
      <must>ExtractedAtom nodes use is_logical_deduction=True to allow null source_quote for matrix assertions</must>
      <forbidden>Raw dict state passing, asyncio.gather, exposing raw tda_id UUIDs to the LLM prompt</forbidden>
    </invariants>
    <tests min_negative="2">
      <positive>test_tda_engine_matrix_path: Verify EnrichedDagExecutor is called with original matrix atoms and enriched full_context</positive>
      <positive>test_tda_engine_no_shuffled_atoms_unchanged: Verify Regular TDA path uses SlidingWindowLinker unchanged</positive>
      <negative>Verify invalid shuffled_atoms structure triggers Pydantic ValidationError</negative>
      <negative>Verify missing tda_id triggers ExtractedAtom validation crash</negative>
    </tests>
    <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/services/orchestrator/engines/tda_engine.py --test</audit_command>
  </step>

  <step id="phase_4.1" scope="VERIFY">
    <action>Run the full backend audit loop for all modified files to verify compilation and >90% test coverage.</action>
    <invariants>
      <must>All 4 TDD test cases pass (2 success paths, 2 failure paths)</must>
      <must>Backend audit loop passes at >90% coverage</must>
    </invariants>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines backend_v2/services/orchestrator/strategies --test</audit_command>
  </step>
</execution_protocol>
```
