# Implementation Plan: EPIC 90 Phase 3 - Studio API & DB Haku

Source: Epic Phase 3, Step 3.1 & 3.2

## Goal
Enable dynamic fetching and CRUD management of `OutputProfile` for the Admin Studio and the LLM engine without local cache issues.

## Target Files (Modify)
- `backend_v2/api/routers/studio/output_profiles.py` (NEW)
- `backend_v2/services/orchestrator/strategies/llm_execution.py` (or where LLM initializes)

## Context Files (Read-Only)
- `backend_v2/models/domain/output_profile.py`

## Implementation Steps
1. Create CRUD endpoints for `OutputProfile` in a new studio router (`PUT /studio/profiles/{profile_id}`).
2. In LLM initialization hook, dynamically fetch `OutputProfile` from DB via `OutputProfileRepository` for every LLM task (no `lru_cache`).

## Hardening Rules & Architectural Invariants (from hardening.xml & .agents/rules)
- **Rule 32 & 78 (Anemic Routers / API vs Service Layer Separation):** Router must not contain business logic or create Opaque Stripe IDs. Delegate to `StudioService`.
- **Rule 33 (Data Leak Prevention Firewall):** Must force a strict `response_model` on endpoints.
- **Rule 3 & 23 (Fail-Fast Hydration / Zero Service Layer Fallbacks):** If a requested profile doesn't exist in DB, immediately raise `AppException`. No silent `.get()` fallbacks.

## Testing & Quality Gate Plan
- **Integration Tests:** Test the API router endpoints via `FastAPI TestClient`.
- **Quality Gate:** Run `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/studio/output_profiles.py --test --openapi`
- Update `docs/architecture/` reflecting dynamic profile routing.

---
<!-- Session Handover -->
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_90_Output_renewal_tracker.md`
