# Phase 2: Evaluation Chunk Hardening (Anti-Sycophancy XAI Header)

## Goal
Inject a global "Anti-Sycophancy XAI Header" into the evaluation prompt compiler (`backend_v2/services/orchestrator/prompt_compiler.py`) to prevent the LLM from slipping into a polite "corporate consultant" mode.

## Target Files (Modify)
- `backend_v2/services/orchestrator/prompt_compiler.py`

## Context Files (Read-Only)
- `backend_v2/llm/schema_builder.py`

## Implementation Steps
1. **Acknowledge `prompt_compiler_immutability` Rule**: We are making an explicit, Epic-mandated change to `prompt_compiler.py` to inject the Anti-Sycophancy XAI Header.
2. **Locate Rubric Compilation**: In `backend_v2/services/orchestrator/prompt_compiler.py`, locate the `compile_xml_rubrics` method (or similar global prompt compiler point for matrices).
3. **Inject Anti-Sycophancy Mandate**: Add a new block `<ANTI_SYCOPHANCY_MANDATE>` to the XML blocks array before returning the prompt string.
4. **Define the Mandate Content (English translation from Epic)**:
   - "ANTI-SYCOPHANCY MANDATE: All extension fields MUST follow the same strict, coldly analytical tone as the main score. If the user's score is low, coaching and missing_context must NOT be encouraging. You must precisely point out the missing data, flawed metric, or shaky causal relationship. Speak like a strict professional auditor."
5. **Ensure Correct Placement**: Make sure this header is glued to every single matrix evaluation prompt so the LLM context is globally forced out of "Fluff-In, Fluff-Out" behavior.

## Verification & Quality Gate Plan
- **Linting & Formatting**: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py`
- **Unit Testing**: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py --test`
