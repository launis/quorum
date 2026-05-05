# Epic 45: Smart LLM Error Logging & Finish Reason Tracking

## Context & Motivation
During Phase 9 hardening, an architectural "blind spot" was discovered when testing large data payloads. When constants like `MATRIX_SAMPLING_LIMIT` are increased (e.g., from 3 to 30), the massive prompt payload fundamentally shifts the LLM's cognitive routing. Instead of generating standard text, the LLM may:
1. **Trigger MCP Tool Calls:** Assuming the payload is too large for manual processing, the LLM hallucinates or triggers a tool call, resulting in an empty `content` field.
2. **Trigger Safety/Recitation Filters:** Large, repetitive blocks of text trigger provider-side safety or recitation filters (e.g., `finish_reason="SAFETY"` or `finish_reason="RECITATION"`), causing the provider to abruptly abort generation and return an empty `content` string.

Previously, `LLMResponse.content` had a strict `min_length=1` Pydantic constraint. This caused the orchestrator to crash completely (Fatal Crash) because the empty string triggered a Pydantic `ValidationError` deep inside the infrastructure layer, masking the actual root cause (Tool Calls / Filters).

## Current State
The `min_length=1` constraint has been removed from `LLMResponse.content`, allowing the system to safely receive empty LLM responses. The empty string is now correctly caught by the `LLMTaskExecutor`'s Self-Healing loop as an `LLMSchemaValidationError` (JSON parsing failure).

## Proposed Implementation (Pending)
To make the orchestrator fully transparent and "self-aware", we need to implement smart Python-level validation in `backend_v2/llm/client.py` *before* the JSON parsing attempts to read the empty string. 

Instead of a generic JSON parsing error, the system should inspect the raw LiteLLM response metadata (`finish_reason` and `tool_calls`) and log specific English error messages into the orchestrator stream.

### English Error Templates for Implementation
When `response.content` is empty, check the following conditions and inject the corresponding error message into the `LLMSchemaValidationError`:

1. **Safety/Content Filter Triggered:**
   ```python
   # Condition: response.finish_reason in ["SAFETY", "RECITATION", "content_filter"]
   error_msg = "Empty LLM payload received. Generation was aborted by the provider's Safety/Content filter."
   ```

2. **Tool Call Invoked:**
   ```python
   # Condition: len(response.tool_calls) > 0
   error_msg = f"Empty LLM payload received. The model attempted to invoke {len(response.tool_calls)} MCP tool(s) instead of generating text."
   ```

3. **Max Tokens Reached:**
   ```python
   # Condition: response.finish_reason == "length"
   error_msg = "LLM payload generation was aborted. The model hit the max_tokens limit before finishing."
   ```

## Architectural Rule
Do **not** remove `min_length=1` constraints from the inner Domain Models (e.g., `step_4_reasoning`, `title`). Those constraints are critical for the Fail-Fast Self-Healing loop. Only the outermost DTO (`LLMResponse`) is permitted to accept empty content strings to accommodate API-level anomalies.
