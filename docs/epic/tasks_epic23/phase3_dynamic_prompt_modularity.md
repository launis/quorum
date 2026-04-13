# TIER 2 EXECUTION PLAN: Phase 3 - PromptCompiler Dynamic Modularity

## Objective
Execute phase 3 of Epic 23. Update the `PromptCompiler` so that it seamlessly handles dynamic `ChunkResponseSchema` rendering for the Map-Reduce chunks. It must strictly utilize the `llm_structured_execution_mandate` to guarantee that the LLM is forced to output structured JSON mapping precisely to the chunk's Opaque IDs, preventing the LLM from merely rendering arbitrary Markdown text.

## Target & Context Files
- **TARGET (Modify):** `backend_v2/services/orchestrator/prompt_compiler.py` (Flagged as extremely secure architecture target, requires Surgical Precision Exception granted by Epic 23).
- **TARGET (Modify):** `backend_v2/models/dto.py` (Or relevant file holding evaluation output schemas) to ensure `ChunkResponseSchema` is solidly typed.
- **CONTEXT (Read-Only):** `.agents/rules/05_llm_architecture.md`, `backend_v2/services/orchestrator/chunking_service.py`

## Architectural Sequence
1. **Dependencies:** `PromptCompiler` logic adjustments.
2. **Pydantic Models:** Finalize `ChunkResponseSchema` and `ChunkRecordSchema`.
3. **Logic Update:** Refactor `PromptCompiler` to generate an isolated, chunk-specific directive using only the specific chunk's data, instead of injecting the entire evaluation tree.
4. **Validation Pipeline:** Ensure the final compiled output uses `<user_payload>` fencing to protect against injection as per Phase 9 LLM architecture rules.

## Strict Constraints
- **Prompt Compiler Immutability:** Epic 23 explicitly permits this change, but the core compilation logic for non-chunked tasks MUST NOT break.
- **Surgical Precision:** Do not add complex conditionals to the base prompt compiler. Abstract the chunk schema compilation cleanly so it acts as an O(1) pass-through.
- **Context Caching:** Maintain completely static `_SYSTEM_INSTRUCTION` strings; push all dynamic chunk definitions to the `user` message boundary.

## Verification & Quality Gate Plan
- Update `tests/backend_v2/services/orchestrator/test_prompt_compiler.py`.
- Ensure output schema generation still generates a valid Rust-executable `model_json_schema()`.
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py` to ensure zero typing regressions.
