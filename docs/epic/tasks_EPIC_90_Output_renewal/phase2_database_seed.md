# Implementation Plan: EPIC 90 Phase 2 - Output Profile -Tietokantamalli ja Seed-migraatio

Source: Epic Phase 2, Step 2.1, 2.2, 2.3

## Goal
Move LLM personality and linguistic rules from Python code into the database (OutputProfile).

## Target Files (Modify)
- `backend_v2/models/domain/output_profile.py` (NEW)
- `backend_v2/database/repositories/output_profile_repository.py` (NEW)
- `backend_v2/seed/seed_data.json`

## Context Files (Read-Only)
- `backend_v2/llm/directives.py`
- `backend_v2/llm/linguistic.py`

## Implementation Steps
1. Create `OutputProfile` Pydantic model with `profile_id`, `name`, `language`, `tone_of_voice`, `formatting_directives`.
2. Create `OutputProfileRepository` with `get_profile` and `save_profile`. Return typed `OutputProfile` instead of raw dict.
3. Migrate rules from `directives.py` and `linguistic.py` into `seed_data.json` under an `"output_profiles": [...]` collection. Assign unique Opaque Stripe IDs (e.g., `prf_fi8x9y`, `prf_en2b3c`).

## Hardening Rules & Architectural Invariants (from hardening.xml & .agents/rules)
- **Rule 2 (Strict Pydantic V2 Rust):** `OutputProfile` must have `model_config = ConfigDict(strict=True, extra="forbid")`.
- **Rule 25 (Opaque Stripe ID Mandate):** `profile_id` must use the `prf_` prefix and random hex string, strictly forbidding semantic slugs.
- **Rule 10 & 74 (Exception):** `OutputProfileRepository` returns a typed model directly using `.model_validate(data, strict=False)` at the database boundary to allow DB coercions, but return a strictly valid object to the service layer.

## Testing & Quality Gate Plan
- **Unit Tests:** Validate `OutputProfile` model instantiation. Test `OutputProfileRepository` mocked database reads.
- **Integration Tests:** Verify seed script parses the new array successfully.
- **Quality Gate:** Run `uv run python scripts/backend_audit_loop.py backend_v2/models/domain/output_profile.py backend_v2/database/repositories/output_profile_repository.py --test`
- Run DB Seeding: `uv run python backend_v2/seed/run_seed.py local`

---
<!-- Session Handover -->
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_90_Output_renewal_tracker.md`
