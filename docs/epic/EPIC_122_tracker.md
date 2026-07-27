# EPIC 122: Legacy Parity Output Profile (Strict SDUI) - Tracker

**Epic Reference**: @[c:\src\quorum\docs\epic\EPIC_122_legacy_parity_output_profile.md]
**Task Directory**: @[c:\src\quorum\docs\epic\tasks_EPIC_122\]

## Phase Execution Status

### Phase 0: Backend Domain Model Refactoring
- [ ] **[NOK] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\00_phase0_backend_refactoring_plan.md]`
- [ ] **[NOK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_122\00_phase0_backend_refactoring_plan.md]`
  - [ ] `0_1`: Refactor SynthesisConfigDTO and OutputLayoutBlock
  - [ ] `0_2`: GlobalSynthesisDTO User Role Support
  - [ ] `0_3`: Update Blueprint Service
  - [ ] `0_4`: Update Jinja Template
  - [ ] `0_5`: Testing & Quality Gate Plan
- [ ] **[NOK] Audit**: `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\00_phase0_backend_refactoring_plan.md]`

### Phase 0: Frontend DTO Parity
- [ ] **[NOK] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\01_phase0_frontend_dto_parity_plan.md]`
- [ ] **[NOK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_122\01_phase0_frontend_dto_parity_plan.md]`
  - [ ] `1_1`: OutputLayoutBlock and ReportLayoutDto Parity
  - [ ] `1_2`: SynthesisConfigDto and ReportDataDto Cleanup
  - [ ] `1_3`: GlobalSynthesisDto and OutputProfile Updates
  - [ ] `1_4`: Testing & Quality Gate Plan
- [ ] **[NOK] Audit**: `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\01_phase0_frontend_dto_parity_plan.md]`

### Phase 1: OutputProfile Configuration in seed_data.json
- [ ] **[NOK] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\02_phase1_output_profile_seed_plan.md]`
- [ ] **[NOK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_122\02_phase1_output_profile_seed_plan.md]`
  - [ ] `2_1`: Update Target OutputProfile in Seed Data
  - [ ] `2_2`: Configure layouts Array
  - [ ] `2_3`: Testing & Quality Gate Plan
- [ ] **[NOK] Audit**: `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\02_phase1_output_profile_seed_plan.md]`

### Phase 2: Backend Context Mappers & Blueprint Hydration (Placeholder)
- [ ] **[NOK] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_122\03_phase2_backend_mappers_placeholder.md]`
- [ ] **[NOK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_122\03_phase2_backend_mappers_placeholder.md]`
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

| Req ID | Requirement Description | Plan Step ID |
|---|---|---|
| R1 | Remove `matrix_visible_columns` from `SynthesisConfigDTO` in backend | 0_1 |
| R2 | Add `matrix_visible_columns` to `OutputLayoutBlock` in backend | 0_1 |
| R3 | Add `matrix_visible_columns` to `ReportLayoutDTO` in backend | 0_1 |
| R4 | Remove `matrix_visible_columns` from `ReportDataDTO` in backend | 0_1 |
| R5 | Update `OutputProfile` backend DTO for layout block changes | 0_1 |
| R6 | Add `user_role` and `user_role_justification` to `GlobalSynthesisDTO` in backend | 0_2 |
| R7 | Add `user_role_label` to `OutputProfile` in backend | 0_2 |
| R8 | Extract `matrix_visible_columns` from `3d_matrix` block in `blueprint.py` | 0_3 |
| R9 | Directly access `lay.synthesis` in `blueprint.py` | 0_3 |
| R10 | Implement Fail-Fast for user role extraction in `blueprint.py` | 0_3 |
| R11 | Extract `matrix_visible_columns` from layout in `report_template.jinja2` | 0_4 |
| R12 | Remove hardcoded fallback columns from `report_template.jinja2` | 0_4 |
| R13 | Run backend audit loop for Phase 0 | 0_5 |
| R14 | Add `matrixVisibleColumns` to `OutputLayoutBlock` and `ReportLayoutDto` in frontend | 1_1 |
| R15 | Remove `matrixVisibleColumns` from `SynthesisConfigDTO` in frontend | 1_2 |
| R16 | Remove `matrixVisibleColumns` from `ReportDataDto` in frontend | 1_2 |
| R17 | Add `userRole` and `userRoleJustification` to `GlobalSynthesisDto` in frontend | 1_3 |
| R18 | Add `userRoleLabel` to `OutputProfile` in frontend | 1_3 |
| R19 | Run flutter build runner for Phase 0 | 1_4 |
| R20 | Add metadata to `visible_metadata` array in seed data `OutputProfile` | 2_1 |
| R21 | Set `custom_preface` with default and translations in seed data | 2_1 |
| R22 | Add `user_role_label` in seed data | 2_1 |
| R23 | Add extensions to `visible_block_extensions` in seed data | 2_1 |
| R24 | Configure `layouts` sequence in seed data (summary, chart, matrix) | 2_2 |
| R25 | Configure `3d_matrix` layout block in seed data with columns and labels | 2_2 |
| R26 | Add `1d_metrics` blocks (Global Score, Jargon Ratio) in seed data | 2_2 |
| R27 | Add `text_only` blocks (Penalties & Audit Trail, Sources) in seed data | 2_2 |
| R28 | Run seed dry-run command to validate JSON integrity | 2_3 |

# Session Handover Context
## Achieved
- Generated the EPIC 122 tracker document based on the implementation plans for Phase 0 and Phase 1.

## Learned
- **Baseline State Snapshot**:
  - The backend `SynthesisConfigDTO` and `ReportDataDTO` currently contain `matrix_visible_columns` which needs to be removed.
  - The frontend `SynthesisConfigDto` and `ReportDataDto` also contain `matrixVisibleColumns`.
  - `blueprint.py` has a fallback logic for `matrix_visible_columns` that needs replacement.
  - `report_template.jinja2` has a hardcoded fallback for `matrix_visible_columns` that needs to be removed.
  - The `OutputProfile` (specifically `holistic_audit`) in `seed_data.json` currently uses the old structure and lacks the required layout definitions and metadata extensions.

## Remaining
- Proceed to execution of Phase 0 Backend Refactoring.

## Resume Command
`/tier5-resume --workflow=/tier0-research-plan --target="@[c:\src\quorum\docs\epic\EPIC_122_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_122\00_phase0_backend_refactoring_plan.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md]"`
