# EPIC 131: SDUI Layout Unification Tracker
@[c:\src\quorum\docs\epic\EPIC_131_sdui_layout_unification.md]
@[c:\src\quorum\docs\epic\tasks_EPIC_131\]

## Phase Execution Status

### Phase 1: New Pydantic SDUI Block Models (Backend Only)
- [OK] `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\01_phase1_backend_models.md]`
- [OK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\01_phase1_backend_models.md]`
  - [x] Step 1.1: Create SduiRadarChartBlock
  - [x] Step 1.2: Create SduiScatterPlotBlock
  - [x] Step 1.3: Create SduiMatrixTableBlock
  - [x] Step 1.4: Create SduiMetrics1DBlock
  - [x] Step 1.5: Update AnySduiBlock Discriminated Union
  - [x] Step 1.6: Satisfy Enum Parity Tests (Cross-Domain Atomicity)
  - [x] Step 1.7: Unit Tests for New Blocks

### Phase 3 Step 3.1: Frontend Models (Cross-Domain Dependency)
- [OK] `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\02_phase3_step1_frontend_models.md]`
- [OK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\02_phase3_step1_frontend_models.md]`
- [OK] `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\02_phase3_step1_frontend_models.md]`
  - [x] Step 3.1: Add 4 New Variants to SduiBlockDTO
  - [x] Step 3.2: Add Unit Tests for New Variants
  - [x] Step 3.8: Regenerate Freezed Files
  - [x] Hotfix: Correct @FreezedUnionValue string discriminators to exactly match backend payload (e.g. 3d_matrix)


### Phase 2: Blueprint Refactoring (Backend Orchestration)
- [OK] `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\03_phase2_blueprint_refactor.md]`
- [OK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\03_phase2_blueprint_refactor.md]`
- [OK] `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\03_phase2_blueprint_refactor.md]` (Audit gaps resolved)
- [OK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\03_phase2_blueprint_refactor.md]`
  - [x] Step 2.1: Refactor _build_layouts() -> _build_visualization_blocks()
  - [x] Step 2.2: Update build_report_dto()
  - [x] Step 2.3: Update ReportDataDTO - Remove layouts Field
  - [x] Step 2.4: Delete ReportLayoutDTO Class
  - [x] Step 2.6: Update Downstream Backend Consumers
  - [x] Step 2.7: Update Backend Tests & Fixtures
  - [x] Step 2.8: Cleanup Title Debt

### Phase 3: Frontend Flutter UI & Freezed DTO Synchronization (Completed)
- [OK] Execute `/tier1-planner` for remaining Phase 3-5 implementation plans once Phase 2 is complete.
- [OK] `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\04_phase3_frontend_ui_plan.md]`
- [OK] Architecture Hotfix: Restored Flat Pipeline (Completed in Phase 2 via blueprint.py inner_sdui_blocks routing).
- [OK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\04_phase3_frontend_ui_plan.md]`
- [OK] `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\04_phase3_frontend_ui_plan.md]`

### Phase 4: PDF Template & Jinja Synchronization
- [OK] `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\05_phase4_pdf_plan.md]`
- [OK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\05_phase4_pdf_plan.md]`
- [OK] `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\05_phase4_pdf_plan.md]`

### Phase 5: Verification & E2E Integration Gate
- [NOK] `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_131\06_phase5_verification_plan.md]`
- [NOK] `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_131\06_phase5_verification_plan.md]`

### Integration Checkpoint: Full-Stack Validation
- [NOK] Backend and Frontend full-stack integration test gates.
- [NOK] `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_131_sdui_layout_unification.md]`

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
- Completed Execution of Phase 1 (Backend Models). Implemented `SduiRadarChartBlock`, `SduiScatterPlotBlock`, `SduiMatrixTableBlock`, `SduiMetrics1DBlock`.
- Updated `AnySduiBlock` and successfully resolved complex Pydantic V2 circular import dependencies by utilizing delayed schema compilation and `model_rebuild()` combined with `TYPE_CHECKING` string references.
- [x] Resolve `AttributeError: 'NoneType' object has no attribute 'translations'` in `test_epic_chain_e2e.py` after the `ReportDataDTO` migration to `inner_sdui_blocks`.
- [x] Resolve `AttributeError: 'SduiMatrixTableBlock' object has no attribute 'preset_view'` in `test_sdui_semantic_parity.py`.
- [x] Ensure full semantic parity between `ReportDataDTO` and the `report_template.jinja2` rendering after transitioning to the flat `inner_sdui_blocks` architecture.
- Completed Execution of Phase 3 Step 3.1 (Frontend Models). Added `matrix3d`, `compare2d`, `metrics1d`, and `matrixSummary` union variants to `SduiBlockDTO`.
- Removed old `PresetView.complex3d` dependencies and upgraded them to `PresetView.matrix3d`.
- Implemented and passed positive/negative unit tests for the new Freezed variants.
- Successfully regenerated Flutter client models.
- Successfully completed System 2 Red-Team audit of Phase 3 Step 3.1 using `/tier8-audit-plan`.
- Executed Hotfix for Phase 3 Step 3.1: Corrected string discriminators in SduiBlockDTO to strictly map to backend payload (e.g., `3d_matrix` instead of `matrix3d`).
- Completed partial Execution of Phase 2 (Blueprint Refactoring).
  - Deleted `layouts` from `ReportDataDTO` and eliminated `ReportLayoutDTO`.
  - Refactored `blueprint.py` to instantiate explicit `SduiMetrics1DBlock`, `SduiMatrixTableBlock`, `SduiRadarChartBlock`, and `SduiScatterPlotBlock` instances and append them directly into `inner_sdui_blocks`.
  - Fixed Jinja PDF template (`report_template.jinja2`) to handle flat `inner_sdui_blocks` logic safely without assuming all blocks possess `axes`.
  - Fully resolved E2E Pydantic Validation & Jinja rendering crashes in `test_epic_chain_e2e.py` and `test_sdui_semantic_parity.py`. Test suite is 100% green.
  - [x] Step 2.8: Cleaned up title debt. Removed loose ParagraphBlock titles from `blueprint.py` and embedded them directly into the SDUI component constructors for true Dumb Painter parity.
- [x] Fixed all downstream MyPy typing errors in `linguistics.py`, `execution.py`, and `worker.py` caused by the removal of `ReportDataDTO.layouts`.
- [x] Refactored `test_blueprint.py` and `test_linguistics.py` to assert against the flattened polymorphic `inner_sdui_blocks` structure. Removed legacy assertions targeting deleted `matrix_column_labels`.
- [x] Successfully ran `backend_audit_loop.py` verifying full codebase compliance, 80.95% coverage, and 1,190 passing unit tests. Phase 2 Execution is fully complete.
- [x] Resolved Phase 2 Audit finding: Added missing `test_blueprint_transformer_custom_scale_missing_bounds` negative test to verify `ConfigurationError` when custom scale lacks bounds.
- [x] Executed Phase 2 Audit Plan. Uncovered two minor gaps: `except Exception: pass` not removed in `blueprint.py:1412`, and missing negative test for unrecognized `text_delivery_mode`. Generated `plan_audit_report.md`.
- [x] Fixed Phase 2 audit gaps: Removed `except Exception: pass`, added `ConfigurationError` for unrecognized `text_delivery_mode`, and updated tests.
- [x] Successfully ran `backend_audit_loop.py` verifying full codebase compliance, 80.99% coverage, and 1,192 passing unit tests. Phase 2 is fully complete.
- [x] Executed `/tier0-research-epic` audit on Phase 3, 4, and 5 plans (`04_...`, `05_...`, `06_...`) to ensure alignment with `output_profile_layout_v2.md`.
- [x] Resolved `[NOK] Architecture Hotfix` tracker constraint. Verified Phase 2 already achieved flat pipeline architecture for `description` and `synthesis_blocks`.
- [x] Fixed Critical Architecture Bug in Phase 3 Frontend Plan: Updated `SduiMetrics1DBlock` rendering logic to correctly map to `MatrixRowItemWidget` instead of `SduiBlocksRenderer`. This prevents the numeric score and visual layout of 1D metrics from disappearing.
- [x] Fixed Critical Architecture Bug in Phase 4 PDF Plan: Updated Jinja 1D metrics rendering instructions to retain the visual score HTML layout before calling the `render_sdui_blocks` text macro.
- [x] Executed `/tier0-research-plan` on Phase 3 Frontend UI Plan (`04_phase3_frontend_ui_plan.md`).
- [x] Mutated Phase 3 Frontend UI plan to fix two critical regressions: Loss of chart titles (added `_buildChartWithTitle` helper) and Loss of Matrix Summary UI (added extraction step for `SduiMatrixTableWidget`).
- [x] Executed Phase 3 Frontend UI plan. Refactored `sdui_blocks_renderer` and `report_renderer_v2_widget`, created `sdui_matrix_table_widget`, dropped `report_layout_dto`, and updated flutter tests.
- [x] Executed `/tier0-research-plan` on Phase 4 PDF Plan (`05_phase4_pdf_plan.md`).
- [x] Mutated Phase 4 PDF plan to fix critical architectural bugs: Replaced hallucinated `visible_columns` with `matrix_visible_columns`, eradicated legacy 1D metrics atom parsing in favor of flat `inner_sdui_blocks` rendering, and strictly handled `ConfigurationError` native bubbling in the generator.
- [x] Executed Phase 4 PDF Plan. Refactored `report_template.jinja2` to use `render_sdui_blocks` as the Single Source of Truth for visualization generation, successfully stripping out legacy layout iteration.
- [x] Hardened `pdf_generator.py` with Python 3.10 `match block` pattern matching and explicit exception routing, preventing silent layout failures.
- [x] Added negative test assertions to `test_pdf_generator.py` for empty chart data and unknown block type handling.
- [x] Executed Phase 4 PDF Plan Audit. Detected a minor MyPy missing parameter initialization on `ParagraphBlock` inside the test script. Automatically surgically fixed.
- [x] All Phase 4 features natively pass Quorum Phase 9 Mathematical Verification (MyPy strict + Fail-Fast exception catching).

## Learned
- **Baseline State Snapshot**: The codebase currently uses `ReportLayoutDTO` containing a `preset_view` enum field to determine visualization rendering on the client side. This violates Dumb Painter SDUI constraints. The `layouts` field exists on both Python's `ReportDataDTO` and Flutter's `ReportDataDto`.
- **Dependency Nuance**: The Flutter UI parser (Freezed) strictly requires recognized block schemas (`disallowUnrecognizedKeys: true`). We must update the Dart parsing definitions (`SduiBlockDTO`) *before* or *atomically with* the backend starting to emit these new variants into the `inner_sdui_blocks` pipeline.
- **Model Inheritance**: The new SDUI blocks must inherit from `SduiBlockBase` (not `V2CoreBase`) to properly utilize the `AnySduiBlock` polymorphic discriminated union in Pydantic V2 and support OpenAPI configuration.
- **Pydantic Circular Imports**: Resolving string annotations for `AnySduiBlock` in circular dependency environments (between `sdui.py`, `v2_core.py`, and `state.py`) requires meticulous top-vs-bottom loading strategies. `test` modules that load isolated schemas can easily fail with `PydanticUserError` if they don't load the core re-builder module (`v2_core.py`) first.
- **Legacy Enum Cleanup**: The frontend contained obsolete hardcoded views mapping to `complex3d` within `report_renderer_v2_widget.dart` and studio editors. We cleanly excised it to favor `matrix3d` mapping, reinforcing Dumb Painter bounds.
- **String Discriminator Parity**: Freezed union string values MUST explicitly match the backend payload exactly, even if Dart variable naming conventions differ. A previous plan hallucinated Dart-compatible names into the string discriminators.
- **Audit Findings**: The universal quality gate is strict. Even if E2E integration tests aren't explicitly run by the agent yet, MyPy will hard-block compilation if cross-file references to deleted fields (like `layouts`) still exist in orphaned files not explicitly mentioned in the plan targets.
- **SDUI Rendering Trap**: Directly mapping a block containing `axes` (like `1d_metrics`) to `SduiBlocksRenderer(blocks: axis.innerSduiBlocks)` completely destroys the UI visualization layer (scores, progress bars) of that component. The frontend must map it to the wrapper widget (`MatrixRowItemWidget`) which internally renders the `innerSduiBlocks`.
- **Phase 3 Audit**: Successfully audited Phase 3 Frontend UI plan. All Freezed DTOs and Flutter view refactoring are perfectly in sync with the Phase 2 flat architecture.

## Remaining
- [x] Executed `/tier2-execute` on the new Architecture Hotfix Plan.
- [x] Verified Phase 2 audits passed via `backend_audit_loop.py` and `flutter_audit_loop.py`.
- [x] Executed `/tier5-resume --target="@[c:\src\quorum\docs\epic\tasks_EPIC_131\04_phase3_frontend_ui_plan.md]" --workflow=/tier0-research-plan`
- [x] Executed `/tier5-resume --target="@[c:\src\quorum\docs\epic\tasks_EPIC_131\04_phase3_frontend_ui_plan.md]" --workflow=/tier2-execute`
- [x] Executed `/tier5-resume --target="@[c:\src\quorum\docs\epic\tasks_EPIC_131\04_phase3_frontend_ui_plan.md]" --workflow=/tier8-audit-plan`
- [x] Executed `/tier5-resume --target="@[c:\src\quorum\docs\epic\tasks_EPIC_131\05_phase4_pdf_plan.md]" --workflow=/tier0-research-plan`
- [x] Executed `/tier5-resume --target="@[c:\src\quorum\docs\epic\tasks_EPIC_131\05_phase4_pdf_plan.md]" --workflow=/tier2-execute`
- [x] Executed `/tier5-resume --target="@[c:\src\quorum\docs\epic\tasks_EPIC_131\05_phase4_pdf_plan.md]" --workflow=/tier8-audit-plan`
- Execute `/tier5-resume --target="@[c:\src\quorum\docs\epic\tasks_EPIC_131\06_phase5_verification_plan.md]" --workflow=/tier0-research-plan`

## Resume Command
`/tier5-resume --target="@[c:\src\quorum\docs\epic\tasks_EPIC_131\06_phase5_verification_plan.md]" --workflow=/tier0-research-plan`
