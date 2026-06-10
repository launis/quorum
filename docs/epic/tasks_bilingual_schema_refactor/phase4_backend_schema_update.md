# Phase 4: Backend Schema Update & Atomic Commit
Source: Epic Phase 1: Backend & Schema Architecture

## Objective
Replace the flat `ai_rule_description: str` with structured Pydantic fields in the Backend. This phase involves swapping the draft database into the live source and updating all test data, committing everything together to prevent crashes.

## Targets (Modify)
- `backend_v2/models/v2_core.py`
- `backend_v2/models/dtos/lightweight_matrix.py`
- `backend_v2/hooks/atom_flattening.py`
- `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py`
- `backend_v2/seed/seed_data.json` (Replace with the draft)
- `backend_v2/llm/mock_data.py`

## Targets (Delete)
- `backend_v2/utils/hashing.py`
- `backend_v2/tests/unit/test_hashing.py`

## Context (Read-Only)
- `backend_v2/services/orchestrator/localization_compiler.py`
- `backend_v2/seed/seed_data_v2_draft.json`

## Architectural Invariants
- **Rule 1 & 22 (Zero Compromise & No Legacy)**: NO `.get("ai_rule_description")` fallbacks allowed. Strict failure is mandatory.
- **Rule 2 & 10 (Strict Pydantic V2)**: Use `ConfigDict(strict=True, extra="forbid")`.
- **Rule 84 (Schema Freeze Mandate)**: This Epic serves as explicit architectural permission to override Rule 84 and deeply alter the `TDAAssertion` schema.
- **Rule 25 (Opaque Stripe ID Mandate)**: Do NOT use hashes for IDs.
- **Rule 35 (SSOT Mandate)**: Purge V1 era `.get()` fallback hacks.
- **Rule 76 (Strict Attribute Integrity)**: Do not use `getattr` fallback mechanisms for structure integrity.

## Implementation Steps
1. **Schema Update**: In `v2_core.py`, update `TDAAssertion`. Remove `ai_rule_description` and add `concept_description: I18nText`, `acceptance_criteria: I18nText`, `anti_patterns: I18nText`, `contrastive_example: I18nText | None`, `syntactic_anchors: dict[str, list[str]] | None`, and `enforce_pre_flight: bool = False`. Also, add `is_lightweight_protocol: bool = Field(default=False)` to `PromptBlock` to enable safe routing.
2. **Wire Up Dormant Routing**: In `execution_strategy.py`, wire up the dormant Best-of-Three logic (from Phase 2) so that it triggers dynamically if `block.is_lightweight_protocol` is True.
3. **Hook Parity**: In `atom_flattening.py`, replace `generate_atom_hash` with `tda.tda_id` and replace `ai_rule_description` usage with `tda.concept_description.resolve("en")`.
4. **Database Swap**: Physically replace `backend_v2/seed/seed_data.json` with the contents of `backend_v2/seed/seed_data_v2_draft.json`.
5. **Test Fixtures Fix**: Deeply update `mock_data.py` (around line 360) so it matches the full `I18nText` nested structure instead of flat strings, otherwise tests will crash. Fix `test_scoring.py` to use UUIDs instead of hashes. Remove `test_hashing.py`.

## Testing & Quality Gate Plan
- **Integration Tests**: Re-run the global test suite against the new seed data and mock data.
- **Universal Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/models backend_v2/hooks backend_v2/services --test`

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier2-execute docs/epic/tasks_bilingual_schema_refactor/phase4_backend_schema_update.md`
