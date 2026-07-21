# Phase 2: Zero-Chunking Cache Pagination & Attention Steering

Source: Epic Phase 1, Step 4

## Proposed Changes

### Orchestration
#### [MODIFY] @[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]
- **Target Location**: `TDAEngine.execute()`
- Remove `text_chunks` splitting logic.
- Hydrate the `global_source_text` using `AliasEngine` (prefix="B") to create a single globally numbered block representation.
- Pass the globally hydrated `source_text` to `atomizer.execute_phase_0` and `execute_phase_1` (removing the chunk lists).
- After `execute_phase_1` completes, explicitly `.sort()` the returned atoms by their `source_sequence_index` to guarantee deterministic graph ingestion.

#### [MODIFY] @[c:\src\quorum\backend_v2\services\orchestrator\two_pass_atomizer.py]
- **Target Location**: `execute_phase_0`, `execute_phase_1`, and internal workers.
- Change arguments from `chunks: list[str]` to `hydrated_text: str`.
- **Cache Lifecycle (Red-Team Fix)**: Inside `execute_phase_0` and `execute_phase_1`, initialize a `CompiledPrompt` with the static system instruction and the full `hydrated_text` inside a `<source_data>` tag. Call `LLMCachingService.pre_cache_document()` before the `asyncio.TaskGroup`, and wrap the TaskGroup in a `try...finally` block that calls `LLMCachingService.teardown_workflow_caches()`.
- Deterministically calculate logical chunk boundaries (e.g., packets of 50 blocks) by iterating over the `hydrated_text` block keys.
- **Prefix Purity (Red-Team Fix)**: Update the worker messages payload to use the orchestrator's `CompiledPrompt`. Pass the specific packet boundary instruction (e.g., "Extract atoms ONLY from [B0] to [B50]") as a dynamic user message wrapped strictly inside `<execution_parameters>`. Do NOT strip `<source_data>`.
- Inject the `chunk_index` (which becomes `source_sequence_index`) into the `DraftExtractedAtom` and `ExtractedAtom` DTOs.
- Implement Post-Generation Boundary Validation in `_extract_drafts_from_chunk_with_retry`. Any atom referencing a block ID outside its assigned packet MUST raise `ValueError` to trigger Tenacity `@retry`.

## Verification Plan
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/`
- Verify context cache telemetry and boundary extraction.

## Session Handover
Run the Tier 2 execution command provided in the tracker.
