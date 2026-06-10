# Phase 1: God Object Refactor (Ennakko-Epic A)
Source: Epic Ennakko-Epic A: God Object -purku

## Objective
Split the massive `prompt_compiler.py` into smaller files based on the Single Responsibility Principle without altering the existing Pydantic models. `ai_rule_description` remains a string. This is an "easy" refactor that must leave the codebase 100% executable and functionally identical.

## Targets (Modify)
- `backend_v2/services/orchestrator/prompt_compiler.py`
- `backend_v2/services/orchestrator/schema_factory.py` [NEW]
- `backend_v2/services/orchestrator/localization_compiler.py` [NEW]
- `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`

## Context (Read-Only)
- `backend_v2/models/v2_core.py`
- `c:\src\quorum\scripts\hardening.xml`

## Architectural Invariants
- **Rule 88 (SRP God Method Mandate) & Rules 47, 75, 81**: Split the God object by moving existing logic as-is. DO NOT perform algorithmic "simplifications".
- **Rule 54-58 (PEP 257 Google Style)**: Add Google style docstrings to all new methods and classes.
- **Rule 18 (RFC 7807)**: Use `AppException` for any new error boundaries.

## Implementation Steps
1. Create `schema_factory.py` and extract dynamic Pydantic schema generation logic from `prompt_compiler.py`.
2. Create `localization_compiler.py` and extract translation resolution and string injection logic.
3. Refactor `prompt_compiler.py` to act purely as a high-level orchestrator. Note: `ai_rule_description` remains a flat string in this phase. The architectural XML splitting of languages (Zero-Bilingual Leak) MUST be deferred to Phase 4, as the data is not yet structured. Simply move the existing string processing logic.
4. Refactor `apply_spatial_slicing` in `context_builder.py` to be more flexible, moving logic cleanly.

## Testing & Quality Gate Plan
- **Unit Tests**: Add tests for `schema_factory.py` and `localization_compiler.py`.
- **Integration Tests**: Verify end-to-end prompt generation output parity.
- **Universal Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test`

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier2-execute docs/epic/tasks_bilingual_schema_refactor/phase1_god_object_refactor.md`
