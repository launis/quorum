# EPIC 131: SDUI Layout Unification Tracker
@[c:\src\quorum\docs\epic\EPIC_131_sdui_layout_unification.md]
@[c:\src\quorum\docs\epic\tasks_EPIC_131\]

## Phase Execution Status

### Phase 1: New Pydantic SDUI Block Models (Backend Only)
- [OK] `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\01_phase1_backend_models.md]`
- [NOK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\01_phase1_backend_models.md]`
  - [ ] Step 1.1: Create SduiRadarChartBlock
  - [ ] Step 1.2: Create SduiScatterPlotBlock
  - [ ] Step 1.3: Create SduiMatrixTableBlock
  - [ ] Step 1.4: Create SduiMetrics1DBlock
  - [ ] Step 1.5: Update AnySduiBlock Discriminated Union
  - [ ] Step 1.6: Satisfy Enum Parity Tests (Cross-Domain Atomicity)
  - [ ] Step 1.7: Unit Tests for New Blocks

### Phase 3 Step 3.1: Frontend Models (Cross-Domain Dependency)
- [NOK] `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\02_phase3_step1_frontend_models.md]`
- [NOK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\02_phase3_step1_frontend_models.md]`
  - [ ] Step 3.1: Add 4 New Variants to SduiBlockDTO
  - [ ] Step 3.8: Regenerate Freezed Files

### Phase 2: Blueprint Refactoring (Backend Orchestration)
- [NOK] `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\03_phase2_blueprint_refactor.md]`
- [NOK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\03_phase2_blueprint_refactor.md]`
  - [ ] Step 2.1: Refactor _build_layouts() -> _build_visualization_blocks()
  - [ ] Step 2.2: Update build_report_dto()
  - [ ] Step 2.3: Update ReportDataDTO - Remove layouts Field
  - [ ] Step 2.4: Delete ReportLayoutDTO Class
  - [ ] Step 2.6: Update Downstream Backend Consumers
  - [ ] Step 2.7: Update Backend Tests & Fixtures

### Phase 3: Frontend Flutter UI & Freezed DTO Synchronization (Remaining)
- [NOK] Execute `/tier1-planner` for remaining Phase 3-5 implementation plans once Phase 2 is complete.
- [NOK] `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\04_phase3_frontend_ui_placeholder.md]`
- [NOK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\04_phase3_frontend_ui_placeholder.md]`

### Phase 4: PDF Template & Jinja Synchronization
- [NOK] `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\05_phase4_pdf_placeholder.md]`
- [NOK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\05_phase4_pdf_placeholder.md]`

### Phase 5: Verification & E2E Integration Gate
- [NOK] `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\06_phase5_verification_placeholder.md]`
- [NOK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\06_phase5_verification_placeholder.md]`

### Integration Checkpoint: Full-Stack Validation
- [NOK] Backend and Frontend full-stack integration test gates.

### Post-Implementation Gates
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in <appDataDir>/knowledge/.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_131_sdui_layout_unification.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Requirements Traceability Matrix
| Req ID | Description | Target Component | Plan Step ID |
|---|---|---|---|
| R1 | Create SduiRadarChartBlock inheriting V2CoreBase | Backend Model | 1.1 |
| R2 | Create SduiScatterPlotBlock inheriting V2CoreBase | Backend Model | 1.2 |
| R3 | Create SduiMatrixTableBlock inheriting V2CoreBase | Backend Model | 1.3 |
| R4 | Create SduiMetrics1DBlock inheriting V2CoreBase | Backend Model | 1.4 |
| R5 | Add new blocks to AnySduiBlock Discriminator Union | Backend Model | 1.5 |
| R6 | Update Flutter SduiBlockType Enum for Parity | Frontend Model | 1.6 |
| R7 | Update Jinja render_sdui_blocks macro for Enum Parity | Backend Template | 1.6 |
| R8 | Unit Tests for New SDUI Blocks (Positive & Negative) | Backend Tests | 1.7 |
| R9 | Create SduiRadarChartBlock variant in SduiBlockDTO | Frontend Model | 3.1 |
| R10 | Create SduiScatterPlotBlock variant in SduiBlockDTO | Frontend Model | 3.1 |
| R11 | Create SduiMatrixTableBlock variant in SduiBlockDTO | Frontend Model | 3.1 |
| R12 | Create SduiMetrics1DBlock variant in SduiBlockDTO | Frontend Model | 3.1 |
| R13 | Regenerate Freezed and JsonSerializable files | Frontend Build | 3.8 |
| R14 | Refactor _build_layouts() to _build_visualization_blocks() | Backend Service | 2.1 |
| R15 | Update build_report_dto() to append to inner_sdui_blocks | Backend Service | 2.2 |
| R16 | Remove layouts field from Backend ReportDataDTO | Backend Model | 2.3 |
| R17 | Delete ReportLayoutDTO Class from Backend | Backend Model | 2.4 |
| R18 | Update Downstream Backend Consumers (Mapper, Flattener, etc.) | Backend Services | 2.6 |
| R19 | Update Backend Tests & Migrate Static JSON Fixtures | Backend Tests | 2.7 |

## Instructions for the Execution Agent
- Atomic commit mandates: You MUST perform atomic commits via `run_command` after each file or logical block modification passes its quality gate.
- Seeding environment: If required, use `uv run python backend_v2/seed/run_seed.py local`.
- All target paths MUST strictly use `@-reference` syntax.
- **CRITICAL INSTRUCTION**: You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session. Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the `/tier5-resume` command in your chat response so the user can easily copy-paste it to continue.
- **Mandatory Workflow Loop**: `/tier0-research-plan` (Phase N) -> `/tier2-execute` (Phase N) -> `/tier8-audit-plan` (Phase N) -> `/tier0-research-plan` (Phase N+1). Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`.

# Session Handover Context
## Achieved
- Formally generated the Tracker and Requirements Traceability Matrix for EPIC 131 using the strict /tier1-tracker-generator constraints.
- Broke down Phase 1, Phase 3.1 (Cross-Domain Dependency), and Phase 2 into micro-chunked executable plans tracked accurately in the matrix.
- Completed Tier 0 Research & Analysis on Phase 1 Backend Models. Identified and fixed structural issues in the plan (enforcing SduiBlockBase inheritance, resolving hidden scopes for layout fields, and fixing ambiguity in jinja2 instructions).

## Learned
- **Baseline State Snapshot**: The codebase currently uses `ReportLayoutDTO` containing a `preset_view` enum field to determine visualization rendering on the client side. This violates Dumb Painter SDUI constraints. The `layouts` field exists on both Python's `ReportDataDTO` and Flutter's `ReportDataDto`.
- **Dependency Nuance**: The Flutter UI parser (Freezed) strictly requires recognized block schemas (`disallowUnrecognizedKeys: true`). We must update the Dart parsing definitions (`SduiBlockDTO`) *before* or *atomically with* the backend starting to emit these new variants into the `inner_sdui_blocks` pipeline.
- **Model Inheritance**: The new SDUI blocks must inherit from `SduiBlockBase` (not `V2CoreBase`) to properly utilize the `AnySduiBlock` polymorphic discriminated union in Pydantic V2 and support OpenAPI configuration.

## Remaining
- Execute Phase 1 (Backend Models) using `/tier2-execute`.

## Resume Command
`/tier5-resume --workflow=/tier2-execute --target="@[c:\src\quorum\docs\epic\EPIC_131_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_131\01_phase1_backend_models.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md]"`
