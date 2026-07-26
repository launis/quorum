# EPIC 118 - Phase 2: Orchestration, Registry & Prompt Compiler Updates

## Overview
This plan implements Phase 2 of EPIC 118. It involves updating the LLM Strategy to pass `shuffled_atoms` conditionally and implementing the Context-Enriched Decompose-Verify Pipeline in the TDA Engine.

## Target Files
- `@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]`
- `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]`

## Execution Protocol

```xml
<execution_protocol>
    <step id="phase_2.1" name="Pass shuffled_atoms conditionally">
        <action>Pass the `shuffled_atoms` from `state_data` when the step is a matrix step. To enforce the **Fail-Fast Hydration Mandate** and **Zero-Duct-Tape Ban**, we MUST use **unconditional direct key access** `state_data["shuffled_atoms"]` when `is_matrix_step` is True. This means replacing the existing `if is_matrix_step and "shuffled_atoms" in state_data:` checks with unconditional access. If the `atom_flattening_hook` failed to inject the atoms, the native `KeyError` immediately crashes into a 500 error instead of silently passing `None` downstream.</action>
        <target>@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]</target>
        <constraint>Unconditional state_data["shuffled_atoms"] key access when is_matrix_step is True (Fail-Fast KeyError → 500).</constraint>
        <constraint invariant="python_314_root_model_ban">TypeAdapter(list[FlattenedAtom]).validate_python(raw_atoms, strict=False) for hydration per python_314_root_model_ban.</constraint>
        <constraint>Pass shuffled_atoms=hydrated_shuffled_atoms into BOTH EngineExecutionRequest constructor calls in llm.py (synthesis and regular paths).</constraint>
        <tests>Verify missing shuffled_atoms when is_matrix_step raises KeyError. Verify invalid type triggers Pydantic ValidationError.</tests>
        <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py --test</audit_command>
    </step>

    <step id="phase_2.2" name="Context-Enriched Decompose-Verify Pipeline">
        <action>Implement the **Context-Enriched Decompose-Verify Pipeline** in `TDAEngine.execute()`. If `request.shuffled_atoms` is present (Matrix path): execute Phase 0+1 to generate enriched context, construct `evaluation_context` with `<context>` XML wrapper, map predefined matrix atoms into `LinkedAtomGraph` nodes preserving `tda_id`, skip `SlidingWindowLinker`, and pass `evaluation_context` to `EnrichedDagExecutor.execute_graph()`. If `request.shuffled_atoms` is None (Regular path): preserve existing behavior with `SlidingWindowLinker` and `global_source_text`. Adjust progress callback ranges for Matrix path (skip linker allocation).</action>
        <target>@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]</target>
        <constraint>Preserve AliasEngine block tags ([B0], [B1]) in hydrated_text within evaluation_context.</constraint>
        <constraint>Static-First Caching: full_context at prompt top in XML context tags.</constraint>
        <constraint invariant="zero_db_hardcoding_mandate">_MATRIX_SOURCE_SENTINEL module-level constant per zero_db_hardcoding_mandate.</constraint>
        <constraint>ExtractedAtom nodes use is_logical_deduction=True to allow null source_quote for matrix assertions.</constraint>
        <tests>test_tda_engine_matrix_path: Verify EnrichedDagExecutor is called with original matrix atoms and enriched full_context. test_tda_engine_no_shuffled_atoms_unchanged: Verify Regular TDA path uses SlidingWindowLinker unchanged.</tests>
        <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/services/orchestrator/engines/tda_engine.py --test</audit_command>
    </step>

    <step id="phase_2_checkpoint" name="Integration Checkpoint">
        <action>Run the full backend audit loop for all modified files to verify compilation and >90% test coverage. E2E verification is handled by tests.</action>
        <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test</audit_command>
    </step>
</execution_protocol>
```
