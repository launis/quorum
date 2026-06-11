# Phase 6: Schema Contract & Final Cleanup
Source: Epic Phase 5: Schema Contract

## Objective
Finalize the Expand & Contract migration by physically removing the legacy `ai_rule_description` from the backend and frontend. This phase hardens the schemas, enforces strict required fields, and confirms that the system operates entirely on the new Bilingual Schema Architecture.

## Targets (Modify)
- `backend_v2/models/v2_core.py`
- `client_app_v2/lib/core/models/prompt_block.dart`
- `client_app_v2/lib/core/models/prompt_block.freezed.dart`
- `backend_v2/seed/seed_data.json`

## Context (Read-Only)
- All previously updated `phase4` backend files.

## Architectural Invariants
- **Rule 1 (Zero Compromise)**: No fallback properties or backwards compatibility hacks. The database MUST align with the strict schema.
- **Rule 2 (Strict Pydantic V2)**: Pydantic schemas must fail fast.
- **Rule 35 (SSOT Mandate)**: The `seed_data.json` must only contain valid fields.

## Implementation Steps
1. **Backend Cleanup**: In `v2_core.py`, delete the `ai_rule_description` field from `TDAAssertion`. Change `concept_description` and `acceptance_criteria` from `Optional` to required.
2. **Frontend Cleanup**: In `prompt_block.dart`, delete the `aiRuleDescription` field from `TDAAssertion`. Change `conceptDescription` and `acceptanceCriteria` from `Optional` to required. Re-run `dart run build_runner build -d`.
3. **Database Cleanup**: Edit `seed_data.json` and cleanly remove all remaining `ai_rule_description` key-value pairs using a small throwaway script or regex replace, since they are no longer read by the backend.
4. **Final Audits**: The entire God Commit must pass both backend and frontend quality gates with zero errors.

## Testing & Quality Gate Plan
- **Universal Quality Gate (Backend)**: `uv run python scripts/backend_audit_loop.py . --test`
- **Universal Quality Gate (Frontend)**: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier2-execute docs/epic/tasks_bilingual_schema_refactor/phase6_schema_contract.md`
