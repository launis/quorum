# Phase 1: Context Builder & Prompt Factory

## Objective
Extract the data preparation and prompt compilation logic from `LLMNodeStrategy.execute()` into dedicated Single Responsibility classes: `ContextBuilder` and `PromptFactory`. This reduces the complexity of the God Method without changing any underlying logic.

## Scope

### CONTEXT (Read-Only)
- `backend_v2/services/orchestrator/strategies/llm.py`
- `backend_v2/services/orchestrator/prompt_compiler.py`
- `backend_v2/core/hook_registry.py`

### TARGET (Modify)
- `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py` [NEW]
- `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py` [NEW]
- `backend_v2/services/orchestrator/strategies/llm_execution/__init__.py` [NEW]

## Implementation Steps

### 1. `ContextBuilder` Implementation
Create `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`.
- Move the logic that extracts `input_mappings` and resolves dot notation.
- Migrate the `ContextRouter` integration (for pruning) and token limit validation (`litellm.token_counter`).
- The output should be a clean `llm_context_data` dictionary and a sanitized `input_mappings` dictionary.
- Enforce Fail-Fast principles (e.g. `TokenLimitExceededError` must be allowed to propagate).

### 2. `PromptFactory` Implementation
Create `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py`.
- Migrate the prompt compilation logic utilizing the existing `PromptCompiler`.
- Gather `static_instructions`, `dynamic_instructions`, `blind_instruction`, and `mcp_instruction`.
- Build the `xml_ctx` and combine them into a final `user_payload` (base system prompt).
- Provide a clear DTO or NamedTuple (e.g., `PromptPayload`) containing `base_system_prompt`, `user_payload`, and the `atom_to_block_ids` mapping used for dynamic chunk rubrics.

### 3. Initialize Package
Create `backend_v2/services/orchestrator/strategies/llm_execution/__init__.py`.
- Expose the newly created classes.

## Verification & Quality Gate Plan
- **Unit Tests:** Run existing tests for LLM strategies to ensure logic hasn't broken (since we are just scaffolding classes, we can run them after integration, or test these new classes directly). Create `tests/backend_v2/services/orchestrator/strategies/test_context_builder.py` and `test_prompt_factory.py`.
- **Quality Gate:** `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/ --test`
