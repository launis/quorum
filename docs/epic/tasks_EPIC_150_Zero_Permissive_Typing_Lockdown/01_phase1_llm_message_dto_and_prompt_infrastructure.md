# Phase 1: LLM Message DTO & Prompt Infrastructure

> **STATUS: DEFERRED** — This is a placeholder. Run `/tier0-create-plan @[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md] @[docs/epic/EPIC_150_tracker.md]` to generate the full implementation plan for this phase.

## Scope Summary

Create `LLMMessageDTO` and refactor the entire LLM prompt compilation → adapter → provider pipeline to eliminate all `list[dict[str, Any]]` message lists and reflection on LiteLLM response objects.

## Target Files (~10 files)

- `@[backend_v2/models/llm.py]`
- `@[backend_v2/models/prompt.py]`
- `@[backend_v2/llm/provider.py]`
- `@[backend_v2/llm/adapters/base_adapter.py]`
- `@[backend_v2/llm/adapters/ai_studio_adapter.py]`
- `@[backend_v2/llm/adapters/vertex_adapter.py]`
- `@[backend_v2/llm/adapters/anthropic_adapter.py]`
- `@[backend_v2/llm/adapters/openai_adapter.py]`
- `@[backend_v2/llm/client.py]`
- `@[backend_v2/llm/ingress_pipeline.py]`
- `@[backend_v2/llm/mock.py]`
