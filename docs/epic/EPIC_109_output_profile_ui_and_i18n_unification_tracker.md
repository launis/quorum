# EPIC 109: Output Profile UI and i18n Unification Tracker

Original Epic: @[c:\src\quorum\docs\epic\EPIC_109_output_profile_ui_and_i18n_unification.md]
Task Directory: @[c:\src\quorum\docs\epic\tasks_EPIC_109\]

## Phase Execution Status

### Phase 0: Seed Data & Database Prerequisite / Migration
- [x] **[OK]** `/tier0-research-plan` @[c:\src\quorum\docs\epic\tasks_EPIC_109\00_phase0_seed_data_migration.md]
- [x] **[OK]** `/tier2-execute` @[c:\src\quorum\docs\epic\tasks_EPIC_109\00_phase0_seed_data_migration.md]

### Phase 1: Backend Domain Models & Service Engine Hardening
- [x] **[OK]** `/tier0-research-plan` @[c:\src\quorum\docs\epic\tasks_EPIC_109\01_phase1_backend_hardening.md]
- [x] **[OK]** `/tier2-execute` @[c:\src\quorum\docs\epic\tasks_EPIC_109\01_phase1_backend_hardening.md]

### Phase 2: Orchestration, Registry & Prompt Compiler Updates
- [x] **[OK]** `/tier0-research-plan` @[c:\src\quorum\docs\epic\tasks_EPIC_109\02_phase2_orchestration_registry.md]
- [x] **[OK]** `/tier2-execute` @[c:\src\quorum\docs\epic\tasks_EPIC_109\02_phase2_orchestration_registry.md]

### Integration Checkpoint: Full-Stack Validation
- [x] **[OK]** Invoke Tier 1 Planner again to generate detailed plans for Phase 3 (Frontend) based on the updated codebase state. (CRITICAL LIMIT requirement).

### Phase 3A: Top Navigation Refactor
- [ ] **[NOK]** `/tier0-research-plan` @[c:\src\quorum\docs\epic\tasks_EPIC_109\03_phase3A_top_nav.md]
- [ ] **[NOK]** `/tier2-execute` @[c:\src\quorum\docs\epic\tasks_EPIC_109\03_phase3A_top_nav.md]

### Phase 3B: Output Profile Sub-Tab Restructuring
- [ ] **[NOK]** `/tier0-research-plan` @[c:\src\quorum\docs\epic\tasks_EPIC_109\04_phase3B_output_profile_subtabs.md]
- [ ] **[NOK]** `/tier2-execute` @[c:\src\quorum\docs\epic\tasks_EPIC_109\04_phase3B_output_profile_subtabs.md]

### Integration Checkpoint: Phase 3 Planner Invocation
- [ ] **[NOK]** Invoke Tier 1 Planner again to generate detailed plans for Phase 3C and 3D based on the updated codebase state. (CRITICAL LIMIT requirement).

### Phase 3C: Section Template UI & i18n Widget Updates
- [ ] **[NOK]** `/tier0-research-plan` @[c:\src\quorum\docs\epic\tasks_EPIC_109\05_phase3C_ui_widgets.md]
- [ ] **[NOK]** `/tier2-execute` @[c:\src\quorum\docs\epic\tasks_EPIC_109\05_phase3C_ui_widgets.md]

### Phase 3D: Excel Action Button (VERIFY & ENHANCE)
- [ ] **[NOK]** `/tier0-research-plan` @[c:\src\quorum\docs\epic\tasks_EPIC_109\06_phase3D_excel_action.md]
- [ ] **[NOK]** `/tier2-execute` @[c:\src\quorum\docs\epic\tasks_EPIC_109\06_phase3D_excel_action.md]

### Post-Implementation Gates
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` on modified Python files.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` on modified Flutter files.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Update docs/architecture/ with newly created modules or protocols.
- [ ] **[NOK]** Update .agents/rules/04_directory_reference.md to include any new directories.
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in <appDataDir>/knowledge/.

## Instructions for the Execution Agent
- Enforce atomic commits per-file/per-domain after any successful run of the universal quality gate.
- Seed database using: `uv run python backend_v2/seed/run_seed.py local`
- You MUST explicitly wrap all target file paths in `@-reference` syntax. If files are massive, use line bounds like `#Lnn-mm`.
- You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session.

## Requirements Traceability Matrix

| Epic Requirement | Implementation Phase | Status |
|------------------|----------------------|--------|
| Zero Legacy State Support Mandate (Re-seeding) | Phase 0 | Complete |
| Excel Export Fail-Fast Boundary (Zero Duct-Tape) | Phase 1 | Complete |
| RFC-7807 Dual-Reporting for execution errors | Phase 1 | Complete |
| Replace hardcoded Finnish column headers with ARB | Phase 1 | Complete |
| Cross-Domain DTO Parity (`is_synthesis_enabled`) | Phase 2 | Complete |
| 3-tab layout for Studio Workflow Top Navigation | Phase 3A | Pending |
| 3-tab layout for Output Profile Admin UI | Phase 3B | Pending |
| Bilingual support for section templates (`I18nTextField`) | Phase 3C | Pending |
| Strict SDUI Rendering Mandate for layout configuration | Phase 3C | Pending |

# Session Handover Context
## Achieved
- Initialized Tier 1 planning for EPIC 109.
- Generated detailed micro-chunked plans for backend phases (0, 1, 2) in `c:\src\quorum\docs\epic\tasks_EPIC_109\`.
- Encountered a Pydantic Validation Error during Phase 0 execution due to strict literals.
- Overrode the blocker per user instruction: Updated `backend_v2/models/v2_core.py` to allow `"xlsx"` in `allowed_exports`.
- Successfully executed Phase 0 data migration (seed data modifications to add `"xlsx"`).
- Re-seeded the local database seamlessly with `run_seed.py local`.
- Passed the `backend_audit_loop.py` quality gate for `v2_core.py` and `run_seed.py`.
- Hardened `get_execution_export_bytes` in `backend_v2/services/execution.py` to strictly Fail-Fast.
- Replaced hardcoded Finnish column headers in Excel export with Flutter ARB translation keys.
- Ensured `/api/v2/executions/{execution_id}/export` relies solely on execution metadata `target_locale`.
- Updated `backend_v2/tests/unit/services/test_execution.py` and passed universal quality gate.
- Executed `/tier0-research-plan` for Phase 2, eliminating duplicate schemas and dead code.
- Successfully executed `/tier2-execute` for Phase 2, adding `is_synthesis_enabled` to models and mapping it in `blueprint.py`.
- Passed the `backend_audit_loop.py` quality gate for `v2_core.py` and `blueprint.py`.
- Invoked Tier 1 Planner to generate detailed implementation plans for Phase 3A and 3B, treating them as the current batch to prevent LLM cognitive overload. Created placeholder plans for Phase 3C and 3D.
- Added a new integration checkpoint to invoke the planner for Phase 3C and 3D after Phase 3B is complete.

## Learned
- **Strict Seed Vault Exemption**: While `03_seed_vault.md` forbids mutating Pydantic schemas to fit data during seed operations, an explicit user override allowed us to update `Literal['pdf', 'docx', 'raw_json', 'xlsx']` simultaneously to prevent a Catch-22 with `run_seed.py` failing fast.
- **Single Responsibility Validation**: `output_profile.py` does not need explicit modification because its DTOs properly inherit `OutputLayoutBlock` from `v2_core.py`.
- **Dead Code Cleanup**: `_resolve_i18n_str` in `blueprint.py` was verified as entirely unreferenced dead code and safely deleted.
- **Cognitive Boundary Mandate**: Followed the limit of generating max 2 detailed Phase plans at a time (3A and 3B), leaving the rest as placeholders to preserve system context stability.

## Remaining
- Execute Phase 3A (Top Navigation Refactor) using `/tier2-execute`.

## Resume Command
`/tier5-resume --workflow=/tier2-execute --target="@[c:\src\quorum\docs\epic\EPIC_109_output_profile_ui_and_i18n_unification_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_109\03_phase3A_top_nav.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\02_flutter_desktop.md]"`
