# Epic 91 Tracker: Quote Evidence Architecture & 2-Stage Opaque Schema

**Target Epic:** `docs/epic/EPIC_91_Quote_Evidence_Architecture.md`

## Instructions for the Execution Agent
- At the start of a session, check which tasks are `[NOK]`, `[/]`, or `[OK]`.
- Pick the first `[NOK]` task and read its implementation plan from `docs/epic/tasks_epic_91/[filename]`.
- Execute the plan step-by-step. Use strict quality gates (`backend_audit_loop.py` / `flutter_audit_loop.py`).
- Once finished and tested, mark it `[OK]`.
- **MANDATORY:** Before handing over the session, you MUST update the `/tier5-resume` command at the bottom of this file. The `--done` parameter MUST be a comprehensive, cumulative summary of ALL previously completed phases (e.g., if phases 1-3 are done, the summary must reflect what was accomplished in all of them).

## Phase Tracker

- [OK] `phase1_pydantic_llm.md` - Backend Pydantic-mallit & Domain Isolation
- [OK] `phase2_backend_alias_resolution.md` - Alias-resoluutio & 2-Stage Translation & Recalculate Extraction
- [OK] `phase3_backend_display_blueprint.md` - Display Blueprint & Immutability (O(1) Snapshot)
- [OK] `phase4_backend_human_override_api.md` - Human Override API & SSOT Mutaatio
- [OK] `phase5_frontend_flutter.md` - Flutter UI ja Dumb Frontend Renderöinti

---

# Session Handover
*Copy and paste the command below to resume execution in a fresh session.*

`/tier5-resume --target docs/epic/epic_91_tracker.md --done "Phases 1-5 completed successfully. Phase 1: Primitive string arrays migrated to QuoteEvidenceDTO. Phase 2: Implemented AliasRegistry and 2-Stage Translation for Opaque ID consistency, and decoupled hybrid math logic into recalculate() function. Phase 3: Implemented O(1) source_identity_manifest in execution.py, removed legacy regex parsing from blueprint.py BFF, and updated synthesis.py to parse QuoteEvidenceDTO. Phase 4: Added HumanOverrideRequest and HumanOverrideDTO, implemented override_atom in ExecutionService to persist overrides to ScorecardAtomDTO and recalculate execution via scoring hook, and exposed PATCH /api/v2/executions/{id}/atoms/{atom_id}/override endpoint. Phase 5: Refactored Flutter UI AtomMatrixTableWidget to remove legacy string split hacks, implemented Dual-Evidence pattern fading AI quotes, added HumanOverrideDialog connecting to the new PATCH endpoint, updated execution client, and added UI tests. All Flutter and Python tests pass. Epic 91 is complete."`
