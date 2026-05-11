# Phase 5: Prompt Topology and Prefix Caching

## Context
**Epic:** `c:\src\quorum\docs\epic\epic48_atomization_refactor_plan 2.md`

## Architectural Invariants
- **Rule 1:** Prompt Generation immutability. Top of prompt must remain identical for Prefix Caching.
- **Rule 2:** Structured State Envelopes Mandate (`01-python-backend.md`).

## Targets (Modify)
- `c:\src\quorum\backend_v2\services\orchestrator\llm_task_executor.py`

## Context (Read-Only)
- `c:\src\quorum\docs\epic\epic48_atomization_refactor_plan 2.md`
- `c:\src\quorum\.agents\rules\00-antigravity-core.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## Milestones
### [x] 1. Cross-Chunk Caching
- File: `backend_v2/services/orchestrator/llm_task_executor.py`
- Enforce API-level role isolation: Static `[System Prompt]` and `[TDA Rules]` must be sent in `"role": "system"` block.
- Place variable `[<source_text>]` in a later `"role": "user"` block to preserve Prefix Tree cache across chunks.

### [x] 2. Quality-First Retries (Tail-End Injection)
- If Pydantic crashes, inject `<PREVIOUS_SCHEMA_ERROR>` at the absolute end of the User Prompt (before schema request).
- The top part of the prompt (System, TDA rules, `<source_text>`) must remain bit-for-bit identical to retain OpenAI/Anthropic Prefix Caching in retry loops.

## Testing & Quality Gate Plan
- [x] **Unit Tests:** `tests/unit/test_llm_task_executor.py` to assert prompt topology order (System then User) and retry injection position.
- [x] **Execution:** Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/llm_task_executor.py --test`

## Documentation Update
- [x] Note prefix caching structure in `c:\src\quorum\docs\architecture\04_hooks_and_llm.md`.

---
**Session Handover:**
To execute this plan, start a NEW chat session and run: `/tier2-hardening-backend @[c:\src\quorum\docs\epic\tasks_epic48\phase5_caching_topology.md]`
