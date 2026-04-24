# Phase 2: Chunk Worker (Map-Reduce Engine)

## Objective
Extract the asynchronous map-reduce chunk processing logic from the `process_chunk` inline function within `llm.py` into a dedicated `ChunkWorker` class. This isolates the physical LLM interaction, MCP tool loops, and caching logic into a highly testable component.

## Scope

### CONTEXT (Read-Only)
- `backend_v2/services/orchestrator/strategies/llm.py`
- `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`
- `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py`

### TARGET (Modify)
- `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py` [NEW]

## Implementation Steps

### 1. `ChunkWorker` Implementation
Create `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`.
- Migrate the `process_chunk(chunk: Any)` asynchronous local function from `LLMNodeStrategy`.
- Refactor it into an isolated class method (e.g., `async def execute_chunk(...)`).
- The method must take all required parameters: `chunk`, `criteria_blocks`, `user_payload`, `base_system_prompt`, `has_search`, `has_shuffled_atoms`, `atom_to_block_ids`, `effective_mcp_tools`, `bound_client`, `step_id`, `target_locale`, etc.
- Retain the exact same exception handling, `AppException` mapping, and JSON unpacking logic.
- Retain the MCP Audit Trace mapping and `litellm` tuple structure return format: `tuple[dict[str, Any], dict[str, Any], list[Any]]`.

### 2. Pydantic Architecture Enforcement
- Ensure that the imported types and schemas match strictly with the existing architecture.
- Do not introduce any new dictionaries for state transit without proper Pydantic schemas if applicable, although the previous logic used dictionaries for chunks. We must preserve the existing logic identically.

## Verification & Quality Gate Plan
- **Unit Tests:** Create `tests/backend_v2/services/orchestrator/strategies/test_chunk_worker.py` to ensure the isolated worker logic behaves correctly using mocked LLM responses.
- **Quality Gate:** `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/ --test`
