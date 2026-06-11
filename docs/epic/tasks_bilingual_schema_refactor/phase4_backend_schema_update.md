# Phase 4: Backend Schema Update & Atomic Commit
Source: Epic Phase 1: Backend & Schema Architecture

## Objective
Replace the flat `ai_rule_description: str` with structured Pydantic fields in the Backend. This phase involves swapping the draft database into the live source and updating all test data, committing everything together to prevent crashes.

## Targets (Modify)
- `backend_v2/models/v2_core.py`
- `backend_v2/services/orchestrator/localization_compiler.py`
- `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`
- `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py`
- `backend_v2/hooks/atom_flattening.py`
- `backend_v2/hooks/scoring.py`
- `backend_v2/llm/mock_data.py`
- `backend_v2/tests/unit/hooks/test_scoring.py`
- `backend_v2/tests/unit/hooks/test_atom_flattening.py`
- All other 14 test files referencing `ai_rule_description` or `generate_atom_hash` as identified in the audit.
- `backend_v2/seed/seed_data.json` (Replace with the draft)

## Targets (Delete)
- `backend_v2/utils/hashing.py`
- `backend_v2/tests/unit/test_hashing.py`

## Context (Read-Only)
- `backend_v2/seed/seed_data_v2_draft.json`

## Architectural Invariants
- **Rule 1 & 22 (Zero Compromise & No Legacy)**: NO `.get("ai_rule_description")` fallbacks allowed. Strict failure is mandatory.
- **Rule 2 & 10 (Strict Pydantic V2)**: Use `ConfigDict(strict=True, extra="forbid")`.
- **Rule 84 (Schema Freeze Mandate)**: This Epic serves as explicit architectural permission to override Rule 84 and deeply alter the `TDAAssertion` schema.
- **Rule 25 (Opaque Stripe ID Mandate)**: Do NOT use hashes for IDs.
- **Rule 35 (SSOT Mandate)**: Purge V1 era `.get()` fallback hacks.
- **Rule 76 (Strict Attribute Integrity)**: Do not use `getattr` fallback mechanisms for structure integrity.
- **Rule 18 (AppException)**: Fix `details={"error_code": ...}` to `error_code=ErrorCodes.XYZ` across all modified files.
- **Rule 69 (PEP 736)**: New model instantiations should use kwargs shorthand.

## Implementation Steps
1. **Schema Update**: In `v2_core.py`, update `TDAAssertion`. Remove `ai_rule_description` and add `concept_description: I18nText`, `acceptance_criteria: I18nText`, `anti_patterns: I18nText`, `syntactic_anchors: dict[str, list[str]] | None`, and `enforce_pre_flight: bool = False`. Also, add `is_lightweight_protocol: bool = Field(default=False)` to `PromptBlock` to enable safe routing.
2. **Atom Schema Update**: In `backend_v2/models/dtos/lightweight_matrix.py`, add `confidence: float | None = Field(default=None, ge=0.0, le=1.0)` to `LightweightExtractionAtom`.
3. **Wire Up Dormant Routing**: In `execution_strategy.py`, wire up the dormant Best-of-Three logic (from Phase 2) so that it triggers dynamically if `block.is_lightweight_protocol` is True.
4. **Hook Parity**: In `atom_flattening.py`, replace `generate_atom_hash` with `tda.tda_id` and replace `ai_rule_description` usage with `tda.concept_description.resolve("en")`.
5. **Database Swap**: Physically replace `backend_v2/seed/seed_data.json` with the contents of `backend_v2/seed/seed_data_v2_draft.json`.
6. **Test Fixtures Fix**: Deeply update `mock_data.py` (around line 360) so it matches the full `I18nText` nested structure instead of flat strings, otherwise tests will crash. Fix `test_scoring.py` to use UUIDs instead of hashes. Remove `test_hashing.py`.
7. **RapidFuzz Tolerance & SSOT**: The `fuzz.partial_ratio` threshold is currently hardcoded to 95.0 in both `lightweight_matrix.py` and `integrity.py`. Create a global Enum (e.g., `QuorumLexicalConfig.FUZZ_THRESHOLD_BILINGUAL = 85.0`) in the backend settings or constants file. Replace the hardcoded `95` values in both `lightweight_matrix.py` and `integrity.py` with this new Enum variable. This guarantees Single Source of Truth and increases recall for Finnish morphology.

## Testing & Quality Gate Plan
- **Integration Tests**: Re-run the global test suite against the new seed data and mock data.
- **Universal Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/models backend_v2/hooks backend_v2/services --test`

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier2-execute docs/epic/tasks_bilingual_schema_refactor/phase4_backend_schema_update.md`
