# EPIC 122: Legacy Parity Output Profile (Strict SDUI) - Tracker

**Epic Reference**: @[c:\src\quorum\docs\epic\EPIC_122_legacy_parity_output_profile.md]
**Task Directory**: @[c:\src\quorum\docs\epic\tasks_EPIC_122\]

## Phase Execution Status

### Phase 0: Backend Domain Model Refactoring
- [x] **[OK] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\00_phase0_backend_refactoring_plan.md]`
- [x] **[OK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_122\00_phase0_backend_refactoring_plan.md]`
  - [x] `0_1`: Refactor SynthesisConfigDTO and OutputLayoutBlock
  - [x] `0_2`: GlobalSynthesisDTO User Role Support
  - [x] `0_3`: Update Blueprint Service
  - [x] `0_4`: Update Jinja Template
  - [x] `0_5`: Testing & Quality Gate Plan
- [x] **[OK] Audit**: `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\00_phase0_backend_refactoring_plan.md]` (Report: `@[c:\src\quorum\docs\epic\tasks_EPIC_122\00_phase0_backend_audit_report.md]`)

### Phase 0: Frontend DTO Parity
- [x] **[OK] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\01_phase0_frontend_dto_parity_plan.md]`
- [x] **[OK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_122\01_phase0_frontend_dto_parity_plan.md]`
  - [x] `1_1`: OutputLayoutBlock and ReportLayoutDto Parity
  - [x] `1_2`: SynthesisConfigDto and ReportDataDto Cleanup
  - [x] `1_3`: GlobalSynthesisDto and OutputProfile Updates
  - [x] `1_4`: Testing & Quality Gate Plan
- [x] **[OK] Audit**: `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\01_phase0_frontend_dto_parity_plan.md]` (Report: `@[c:\src\quorum\docs\epic\tasks_EPIC_122\01_phase0_frontend_audit_report.md]`)

### Phase 1: OutputProfile Configuration in seed_data.json
- [x] **[OK] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\02_phase1_output_profile_seed_plan.md]`
- [x] **[OK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_122\02_phase1_output_profile_seed_plan.md]`
  - [x] `2_1`: Update Target OutputProfile in Seed Data
  - [x] `2_2`: Configure layouts Array
  - [x] `2_3`: Testing & Quality Gate Plan
- [x] **[OK] Audit**: `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\02_phase1_output_profile_seed_plan.md]` (Report: `@[c:\src\quorum\docs\epic\tasks_EPIC_122\02_phase1_output_profile_seed_audit_report.md]`)

### Phase 2: Backend Context Mappers & Blueprint Hydration
- [x] **[OK] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\03_phase2_backend_mappers_placeholder.md]`
- [x] **[OK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_122\03_phase2_backend_mappers_placeholder.md]`
  - [x] Implement `TARGET_BLOCK_HYDRATORS` Strategy Pattern registry in `blueprint.py`.
  - [x] Extract `penalties_block` mapping logic from core loop into Hydrator component.
  - [x] Verify Pydantic V2 Strict parity for `ReportDataDTO` layouts array typing.
  - [x] Run `backend_audit_loop.py` on modified domain model layers.
- [ ] **[NOK] Audit**: `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\03_phase2_backend_mappers_placeholder.md]`

### Phase 3: Database Re-seeding & Verification (Placeholder)
- [ ] **[NOK] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\04_phase3_database_reseeding_placeholder.md]`
- [ ] **[NOK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_122\04_phase3_database_reseeding_placeholder.md]`
- [ ] **[NOK] Audit**: `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\04_phase3_database_reseeding_placeholder.md]`

### Phase 4: Flutter UI Implementation (View-Only Parity) (Placeholder)
- [ ] **[NOK] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\05_phase4_flutter_ui_placeholder.md]`
- [ ] **[NOK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_122\05_phase4_flutter_ui_placeholder.md]`
- [ ] **[NOK] Audit**: `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\05_phase4_flutter_ui_placeholder.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Full-Stack Validation Completed**

### Post-Implementation Gates
- [ ] **[NOK] Proxy Sunset & Consumer Migration**
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in `<appDataDir>/knowledge/`.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_122_legacy_parity_output_profile.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent

- You MUST perform atomic commits after every successfully verified step or phase.
- Use `uv run python backend_v2/seed/run_seed.py local` for database seeding tasks.
- Respect the `@-reference` syntax rule for all file references.
- You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session.
- Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the `/tier5-resume` command in your chat response so the user can easily copy-paste it to continue.
- The mandatory workflow loop is: `/tier0-research-plan` (Phase N) -> `/tier2-execute` (Phase N) -> `/tier8-audit-plan` (Phase N) -> `/tier0-research-plan` (Phase N+1).
- Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`.

## Requirements Traceability Matrix

| Req ID | Requirement Description | Plan Step ID | Status |
|---|---|---|---|
| R1 | Remove `matrix_visible_columns` from `SynthesisConfigDTO` in backend | 0_1 | ✅ Done |
| R2 | Add `matrix_visible_columns` to `OutputLayoutBlock` in backend | 0_1 | ✅ Done |
| R3 | Add `matrix_visible_columns` to `ReportLayoutDTO` in backend | 0_1 | ✅ Done |
| R4 | Remove `matrix_visible_columns` from `ReportDataDTO` in backend | 0_1 | ✅ Done |
| R5 | Update `OutputProfile` backend DTO for layout block changes | 0_1 | ✅ Done |
| R6 | Add `user_role` and `user_role_justification` to `GlobalSynthesisDTO` in backend | 0_2 | ✅ Done |
| R7 | Add `user_role_label` to `OutputProfile` in backend | 0_2 | ✅ Done |
| R8 | Extract `matrix_visible_columns` from `3d_matrix` block in `blueprint.py` | 0_3 | ✅ Done |
| R9 | Directly access `lay.synthesis` in `blueprint.py` | 0_3 | ✅ Done |
| R10 | Implement Fail-Fast for user role extraction in `blueprint.py` | 0_3 | ✅ Done |
| R11 | Extract `matrix_visible_columns` from layout in `report_template.jinja2` | 0_4 | ✅ Done |
| R12 | Remove hardcoded fallback columns from `report_template.jinja2` | 0_4 | ✅ Done |
| R13 | Run backend audit loop for Phase 0 | 0_5 | ✅ Done |
| R14 | Add `matrixVisibleColumns` to `OutputLayoutBlock` and `ReportLayoutDto` in frontend | 1_1 | ✅ Done |
| R15 | Remove `matrixVisibleColumns` from `SynthesisConfigDTO` in frontend | 1_2 | ✅ Done |
| R16 | Remove `matrixVisibleColumns` from `ReportDataDto` in frontend | 1_2 | ✅ Done |
| R17 | Add `userRole` and `userRoleJustification` to `GlobalSynthesisDto` in frontend | 1_3 | ✅ Done |
| R18 | Add `userRoleLabel` to `OutputProfile` in frontend | 1_3 | ✅ Done |
| R19 | Run flutter build runner for Phase 0 | 1_4 | ✅ Done |
| R20 | Add metadata to `visible_metadata` array in seed data `OutputProfile` | 2_1 | ✅ Done |
| R21 | Set `custom_preface` with default and translations in seed data | 2_1 | ✅ Done |
| R22 | Add `user_role_label` in seed data | 2_1 | ✅ Done |
| R23 | Add extensions to `visible_block_extensions` in seed data | 2_1 | ✅ Done |
| R24 | Configure `layouts` sequence in seed data (summary, chart, matrix) | 2_2 | ✅ Done |
| R25 | Configure `3d_matrix` layout block in seed data with columns and labels | 2_2 | ✅ Done |
| R26 | Add `1d_metrics` blocks (Global Score, Jargon Ratio) in seed data | 2_2 | ✅ Done |
| R27 | Add `text_only` blocks (Penalties & Audit Trail, Sources) in seed data | 2_2 | ✅ Done |
| R28 | Run seed dry-run command to validate JSON integrity | 2_3 | ✅ Done |

# Session Handover Context
## Achieved
- Generated the EPIC 122 tracker document based on the implementation plans for Phase 0 and Phase 1.
- Executed Phase 0: Backend Domain Model Refactoring, moving `matrix_visible_columns` and adding `global_synthesis` Fail-Fast checks to `blueprint.py`.
- Passed the backend audit loop and unit tests for the modified domain models.
- Completed Tier 8 Audit for Phase 0 Backend execution and generated the audit report at `@[c:\src\quorum\docs\epic\tasks_EPIC_122\00_phase0_backend_audit_report.md]`.
- Implemented Phase 0 Frontend DTO Parity Step 1_1: OutputLayoutBlock and ReportLayoutDto Parity.
- Implemented Phase 0 Frontend DTO Parity Step 1_2: SynthesisConfigDto and ReportDataDto Cleanup.
- Implemented Phase 0 Frontend DTO Parity Step 1_3: GlobalSynthesisDto and OutputProfile Updates.
- Completed Tier 8 Audit for Phase 0 Frontend execution and generated the audit report at `@[c:\src\quorum\docs\epic\tasks_EPIC_122\01_phase0_frontend_audit_report.md]`.
- Executed Tier 0 (Red-Teaming) on Phase 1 Implementation Plan `@[c:\src\quorum\docs\epic\tasks_EPIC_122\02_phase1_output_profile_seed_plan.md]`.
- Executed Phase 1 to surgically mutate `seed_data.json` without breaking context window bounds.
- Completed Tier 8 Audit for Phase 1 and generated the audit report at `@[c:\src\quorum\docs\epic\tasks_EPIC_122\02_phase1_output_profile_seed_audit_report.md]`.
- Executed Phase 2: Backend Context Mappers & Blueprint Hydration.
- Implemented Strategy Pattern registry for SDUI layout hydration and strict type adherence via Pydantic model updates in `v2_core.py` and `blueprint.py`.
- Passed backend audit and achieved required unit test coverage.

## Learned
- **Baseline State Snapshot**:
  - The `OutputProfile` (specifically `holistic_audit` with id `prf_5d6e7f8091a2b3c4`) in `seed_data.json` currently uses the old structure and lacks the required layout definitions and metadata extensions.
- **Audit Findings**:
  - The original Phase 1 plan lacked safeguards against context window saturation when modifying the massive 10,000+ line `seed_data.json` file.
  - (RESOLVED): Mutated the Phase 1 implementation plan to enforce dynamic line-bounds extraction using a Python script in `scratch/` before invoking structural replacements. This guarantees `multi_replace_file_content` will not trigger `Context Amnesia`.
  - The JSON was safely updated, and `uv run python backend_v2/seed/run_seed.py local --dry-run` successfully verified the schema structure.
  - Phase 2 execution successfully implemented the `TARGET_BLOCK_HYDRATORS` to extract the `penalties_block` generation from the score mapping loop in `blueprint.py`, conforming to Open-Closed principles.

## Remaining
- Proceed to Tier 8 Plan Audit of Phase 2 to ensure no architectural deviations exist.
- Then, proceed to Phase 3: Database Re-seeding & Verification.

## Resume Command
`/tier5-resume --workflow=/tier8-audit-plan --target="@[c:\src\quorum\docs\epic\tasks_EPIC_122\03_phase2_backend_mappers_placeholder.md] @[c:\src\quorum\docs\epic\EPIC_122_tracker.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md]"`
