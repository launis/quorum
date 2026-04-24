# Phase 0: Token Overflow Mitigation (ContextBuilder)

## 1. Description and Objective
**Prerequisite for Epic 34: Global Hooks Zero-Compromise Hardening.**
When mapping the global `$steps` variable, `ContextBuilder` currently drops unrecognized non-evaluation steps (like `Input Processing`) directly into the LLM context. This leads to `TokenLimitExceededError` due to raw history leaking through the else-branch. The objective is to introduce "Safe Fallback Pruning" to explicitly prune heavy raw data and atoms, while enforcing Fail-Fast token limits without arbitrary truncation.

## 2. File Scoping
- **TARGET (Modify):** 
  - `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`
- **CONTEXT (Read-Only):** 
  - `backend_v2/models/state.py`
  - `backend_v2/models/enums.py`

## 3. Implementation Steps
1. In `ContextBuilder.build` (or its helper that processes `$steps` mapping), intercept step values before appending them to the LLM context.
2. Implement **A. Atomization Steps:** If `"atoms" in s_val`, replace it with `{"status": "omitted_raw_atoms", "count": len(s_val["atoms"])}`.
3. Implement **B. Raw Data Steps:** If `"history_text" in s_val` or `"extracted_text" in s_val`, replace it with `{"status": "omitted_raw_input_data"}`.
4. Implement **C. Fail-Fast Enforcement (Zero-Compromise):** Do NOT implement arbitrary string length truncation (e.g., `[:2000]`). Any other unrecognized step data must pass through unmodified.
5. If an unknown step causes the context to exceed limits, the system MUST crash with a `TokenLimitExceededError`. This forces the Workflow Admin to fix the DAG mapping in the UI.

## 4. Verification & Quality Gate Plan
- **Unit Testing:** Write pure function unit tests to verify the pruning logic properly replaces `atoms`, `history_text`, and `extracted_text`. Ensure no arbitrary string truncation is performed.
- **Fail-Fast Safety Tests:** Ensure that large unrecognized step data correctly triggers an error instead of being silently truncated.
- **Audit Loop Execution:** `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py --test`
