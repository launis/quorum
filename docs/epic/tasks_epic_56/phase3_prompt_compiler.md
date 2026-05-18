# Implementation Plan: Phase 3 - Prompt Compiler Topologies & Security (EPIC 56)

## 1. Goal
Refactor `prompt_compiler.py` to enforce strict Static-to-Dynamic prompt caching ordering, and implement the API 400 Bad Request prevention mechanism.

## 2. Architectural Rules & Invariants
- **Rule 1: High-Fidelity Prompting & 100% Caching Efficiency**: Dynamic vars go into `<execution_parameters>` at the end. System instructions are static.
- **Rule 2: Structured Execution Mandate**: Must use `LLMTaskExecutor.execute_structured_task()`.
- **Source**: Epic Phase 3, Phase 4 (Rule 2), Phase 5 (Test 1).

## 3. Implementation Steps

### Step 1: Refactor Prompt Ordering
**Target File**: `backend_v2/services/orchestrator/prompt_compiler.py`
- Ensure prompt ordering is strictly:
  1. **System Prompt & Few-Shot (Static Global)**
  2. **Document (Static per Document)**: Wrapped in `<source_data>`.
  3. **Execution Parameters & Attention Anchoring (Dynamic)**: Placed at the end of the User Message within `<execution_parameters>` and `<task>`.
- **CRITICAL**: Maintain the existing `<CRITICAL_LANGUAGE_MANDATE>` tag directly before execution begins to prevent "Lost in the Middle".

### Step 2: Prevent API 400 Bad Request on Max Length
**Target File**: `backend_v2/llm/client.py` (or wherever Pydantic schema is passed to OpenAI/Vertex)
- Set strict `max_tokens` or `max_completion_tokens` directly on the LLM API call (e.g., max 600 tokens) to prevent lazy dumping.
- Implement an adapter hook that strips `maxLength` constraints from the JSON schema dynamically before sending it to the LLM.
- **Why**: Native Structured Outputs API crashes with 400 Bad Request if `maxLength` is included. Pydantic still enforces `max_length=1500` locally.

### Step 3: TDD Tests
**Target File**: `tests/unit/llm/test_client_schema.py`
- **`test_native_schema_strips_unsupported_constraints`** (Unit):
  - Generate a JSON Schema from a Pydantic model containing `Field(max_length=1500)`.
  - Pass it through the schema-stripping adapter.
  - Assert that `"maxLength" not in schema`.

### Step 4: Documentation Update
**Target File**: `docs/architecture/llm/prompt_standards.md`
- Document the prompt sequence rules to preserve Prompt Caching and the schema stripping logic for Structured Outputs.

## 4. Scoping
**TARGET (Modify)**: `backend_v2/services/orchestrator/prompt_compiler.py`, `backend_v2/llm/client.py`, `tests/unit/llm/test_client_schema.py`
**CONTEXT (Read-Only)**: `backend_v2/models/v2_core.py`

## 5. Testing & Quality Gate Plan
- **UNIT TESTS**: Run `test_native_schema_strips_unsupported_constraints`.
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py --test`.

---
*Session Handover: To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/EPIC_56_vaihtoehtob_tracker.md`*
