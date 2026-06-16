# Implementation Plan: Epic 1 - Phase A (Linguistic Context & SchemaFactory)

**Source**: `epic_structured_prompting.md` (Phase A)
**Epic Phase**: Globaali Ohjelmallinen Kielikonteksti & SchemaFactory Optimointi

## 1. Goal
Implement the Universal Linguistic Context to prevent Semantic Loss and Semantic Bleed. Optimize `SchemaFactory` to dynamically drop the `contextual_override` field from the JSON Schema dictionary when `strictness >= 100`, avoiding Rust memory leaks.

## 2. Files
**TARGET (Modify):**
- `c:\src\quorum\backend_v2\api\chunk_worker.py`
- `c:\src\quorum\backend_v2\api\synthesis.py`
- `c:\src\quorum\backend_v2\core\schema_factory.py`

**CONTEXT (Read-Only):**
- `c:\src\quorum\.agents\rules\00-antigravity-core.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## 3. Implementation Steps

### 3.1. Universal Linguistic Context (chunk_worker.py & synthesis.py)
- Retrieve `source_language` and `user_language` from the database/session context.
- Inject the standard `<linguistic_context>` XML block programmatically at the start of the LLM prompt.
```xml
<linguistic_context>
  <source_data_language>{db.source_language}</source_data_language>
  <required_output_language>{db.user_language}</required_output_language>
  <required_reasoning_language>English</required_reasoning_language>
</linguistic_context>
```
- **Semantic Bleed Mandate:** Ensure the Pydantic prompt `Field` description for `exact_quote` explicitly includes: *"CRITICAL: The `exact_quote` MUST ALWAYS be extracted in the exact original language of the source text. NEVER translate the quote, even if your reasoning is in another language."*

### 3.2. SchemaFactory Dynamic Drop (schema_factory.py)
- **Constraint:** Do NOT use Pydantic's `create_model()` to prune fields.
- **Action:** In the method that generates the JSON schema for Vertex AI, evaluate if `strictness >= 100` or if the protocol forbids overrides.
- If true, mutate the generated JSON dictionary directly:
  `schema["properties"].pop("contextual_override", None)`
  `schema["properties"].pop("override_reason", None)`
- Remove them from the `required` list if present.

### 3.3. Schema Cache Optimization
- Change the cache key in `schema_factory.py` to use ID string concatenation instead of `json.dumps()` for performance.
- Remove redundant `global_schema` calls from `llm.py` and populate XAI storage directly from `ChunkWorker.process_chunk` return values.

## 4. Testing & Quality Gate Plan
- **Unit Tests:** `tests/unit/test_schema_factory.py`. Verify that the dynamic drop completely removes the keys from the JSON schema output when strictness=100.
- **Hardening:** Run the Universal Quality Gate on the modified files:
  `uv run python scripts/backend_audit_loop.py c:\src\quorum\backend_v2\api`
  `uv run python scripts/backend_audit_loop.py c:\src\quorum\backend_v2\core`

---
### Session Handover
To execute this phase iteratively, start a NEW chat session and run:
`/tier2-execute --target docs/epic/tasks_structured_prompting/phase_a_linguistic_and_schema_factory.md`
