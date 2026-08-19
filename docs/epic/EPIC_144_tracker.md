# EPIC 144: Output Profile Studio UI Modernization — Tracker

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Task Directory:** `@[docs\epic\tasks_EPIC_144]`

<required_context_rules>
  <rule>@[.agents\rules\00-antigravity-core.md]</rule>
  <rule>@[.agents\rules\01-python-backend.md]</rule>
  <rule>@[.agents\rules\02_flutter_desktop.md]</rule>
  <rule>@[.agents\rules\03_seed_vault.md]</rule>
  <rule>@[.agents\rules\04_directory_reference.md]</rule>
  <rule>@[.agents\rules\05_llm_architecture.md]</rule>
  <ki>@[ki_god_code_prevention.md]</ki>
  <ki>@[ki_sdui_adapter_pattern.md]</ki>
  <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
  <ki>@[ki_dual_axis_localization_architecture.md]</ki>
  <ki>@[ki_strict_sdui_serialization.md]</ki>
  <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
  <ki>@[ki_sdui_matrix_synthesis.md]</ki>
  <ki>@[ki_global_config_sovereignty.md]</ki>
  <ki>@[ki_ai_testing_standards.md]</ki>
  <ki>@[ki_ast_guardrail_testing.md]</ki>
  <ki>@[ki_python_314_concurrency_strictness.md]</ki>
  <ki>@[ki_synthesis_payload_compression.md]</ki>
  <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
  <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  <ki>@[ki_epic_lifecycle_workflow.md]</ki>
</required_context_rules>

---

## Phase Execution Status

### Phase 0: Atomic Data, Mock Fixture & Code Generation Gate (Pre-requisite)

#### Phase 0-A: Backend Config, Enums & Settings
**Plan:** `@[docs\epic\tasks_EPIC_144\01_p0_backend_config_enums.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\01_p0_backend_config_enums.md] @[docs\epic\EPIC_144_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\01_p0_backend_config_enums.md] @[docs\epic\EPIC_144_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Add DisplayScale Enum to enums.py
  - [x] Step 2: Add Authenticity Thresholds to settings.py
  - [x] Step 3: Add Boundary Tests to test_settings.py
  - [x] Step 4: Create Cross-Language Enum Parity Test
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\01_p0_backend_config_enums.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-B: Master Seed Sanitization & Local Reseed
**Plan:** `@[docs\epic\tasks_EPIC_144\02_p0_seed_sanitization.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\02_p0_seed_sanitization.md] @[docs\epic\EPIC_144_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\02_p0_seed_sanitization.md] @[docs\epic\EPIC_144_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Create Timestamped Backup of Master Seed Data
  - [x] Step 2: Audit Current Seed Data State via Python
  - [x] Step 3: Surgically Inject Bilingual Metadata Keys into metric_mappings
  - [x] Step 4: JSON Integrity & Syntax Check
  - [x] Step 5: Implement Automated Seed Integrity Unit Tests
  - [x] Step 6: Execute Local Database Reseed
  - [x] Step 7: Run Quality Audit Gate
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\02_p0_seed_sanitization.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-C: Backend Models & DTO Strict Purge
**Plan:** `@[docs\epic\tasks_EPIC_144\03_p0_backend_models_dto_purge.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\03_p0_backend_models_dto_purge.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\03_p0_backend_models_dto_purge.md] @[docs\epic\EPIC_144_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Modify OutputProfile in v2_core.py
  - [ ] Step 2: Modify OutputProfileCreateDTO
  - [ ] Step 3: Modify OutputProfileUpdateDTO
  - [ ] Step 4: Modify OutputProfileResponseDTO
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\03_p0_backend_models_dto_purge.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-D: Backend Test Fixtures Alignment Batch 1
**Plan:** `@[docs\epic\tasks_EPIC_144\04_p0_backend_test_fixtures_batch1.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\04_p0_backend_test_fixtures_batch1.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\04_p0_backend_test_fixtures_batch1.md] @[docs\epic\EPIC_144_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Update test_v2_core_models.py Fixtures
  - [ ] Step 2: Update and Add Negative Tests to test_output_profile.py
  - [ ] Step 3: Update test_output_profile_regression.py
  - [ ] Step 4: Update test_synthesis_distiller_hook.py
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\04_p0_backend_test_fixtures_batch1.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-E: Backend Test Fixtures Alignment Batch 2
**Plan:** `@[docs\epic\tasks_EPIC_144\05_p0_backend_test_fixtures_batch2.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\05_p0_backend_test_fixtures_batch2.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\05_p0_backend_test_fixtures_batch2.md] @[docs\epic\EPIC_144_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Update test_blueprint.py Fixtures
  - [ ] Step 2: Update test_scoring.py Fixtures
  - [ ] Step 3: Update test_worker_synthesis.py Fixtures
  - [ ] Step 4: Update test_matrix_domain_parser.py Fixtures
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\05_p0_backend_test_fixtures_batch2.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-F: OpenAPI Synchronization Gate
**Plan:** `@[docs\epic\tasks_EPIC_144\06_p0_openapi_sync_gate.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\06_p0_openapi_sync_gate.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\06_p0_openapi_sync_gate.md] @[docs\epic\EPIC_144_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Generate OpenAPI Specification
  - [ ] Step 2: Verify OpenAPI Parity
  - [ ] Step 3: Full Backend Regression Gate
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\06_p0_openapi_sync_gate.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-G: Frontend Enum & Freezed Synchronization
**Plan:** `@[docs\epic\tasks_EPIC_144\07_p0_frontend_enums_freezed.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\07_p0_frontend_enums_freezed.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\07_p0_frontend_enums_freezed.md] @[docs\epic\EPIC_144_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Add DisplayScale Enum to enums.dart
  - [ ] Step 2: Add Missing TargetBlockType Members
  - [ ] Step 3: Add SystemUiConstraints Enum
  - [ ] Step 4: Modify output_profile.dart Freezed Model
  - [ ] Step 5: Modify blueprint_config.dart Freezed Model
  - [ ] Step 6: Run Freezed Code Generation
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\07_p0_frontend_enums_freezed.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-H: Frontend Test Fixtures & Negative Tests
**Plan:** `@[docs\epic\tasks_EPIC_144\08_p0_frontend_test_fixtures.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\08_p0_frontend_test_fixtures.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\08_p0_frontend_test_fixtures.md] @[docs\epic\EPIC_144_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Update output_profile_test.dart
  - [ ] Step 2: Create blueprint_config_test.dart
  - [ ] Step 3: Update output_profile_controller_test.dart
  - [ ] Step 4: Update layout_editor_card_test.dart
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\08_p0_frontend_test_fixtures.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-I: Integration Checkpoint
**Plan:** `@[docs\epic\tasks_EPIC_144\09_p0_integration_checkpoint.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\09_p0_integration_checkpoint.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\09_p0_integration_checkpoint.md] @[docs\epic\EPIC_144_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Full Backend Regression
  - [ ] Step 2: Full Frontend Studio Build and Test
  - [ ] Step 3: Cross-Stack Parity Assertions
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\09_p0_integration_checkpoint.md] @[docs\epic\EPIC_144_tracker.md]`

---

### Phase 1: Sub-Tab Information Architecture & Scaffold Decomposition

#### Phase 1-A: Golden Master Test Baseline
**Plan:** `@[docs\epic\tasks_EPIC_144\10_p1_golden_master_baseline.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\10_p1_golden_master_baseline.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\10_p1_golden_master_baseline.md] @[docs\epic\EPIC_144_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Analyze Current View Structure
  - [ ] Step 2: Create Golden Master Widget Tests
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\10_p1_golden_master_baseline.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 1-B: 3-Tab Scaffold Decomposition
**Plan:** `@[docs\epic\tasks_EPIC_144\11_p1_tab_scaffold_decomposition.md]`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\11_p1_tab_scaffold_decomposition.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\11_p1_tab_scaffold_decomposition.md] @[docs\epic\EPIC_144_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Analyze Monolithic View Structure
  - [ ] Step 2: Extract General Tab
  - [ ] Step 3: Extract Scoring Tab
  - [ ] Step 4: Extract Layouts Tab
  - [ ] Step 5: Refactor CRUD View to Tab Shell
  - [ ] Step 6: Verify Golden Master Parity
  - [ ] Step 7: Line Count Verification
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\11_p1_tab_scaffold_decomposition.md] @[docs\epic\EPIC_144_tracker.md]`

---

### Phase 2: Adaptive Visual Block Builder & UI Patterns

#### Phase 2: Visual Block Builder
**Plan:** `@[docs\epic\tasks_EPIC_144\12_placeholder_phase2_block_builder.md]`
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md] @[docs\epic\tasks_EPIC_144\12_placeholder_phase2_block_builder.md] @[docs\epic\EPIC_144_tracker.md] --phase=2`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\12_placeholder_phase2_block_builder.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\12_placeholder_phase2_block_builder.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\12_placeholder_phase2_block_builder.md] @[docs\epic\EPIC_144_tracker.md]`

---

### Phase 3: Backend Execution, Synthesis Alignment & Prompt DRY Simplification

#### Phase 3: Backend Execution Alignment
**Plan:** `@[docs\epic\tasks_EPIC_144\13_placeholder_phase3_backend_alignment.md]`
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md] @[docs\epic\tasks_EPIC_144\13_placeholder_phase3_backend_alignment.md] @[docs\epic\EPIC_144_tracker.md] --phase=3`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\13_placeholder_phase3_backend_alignment.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\13_placeholder_phase3_backend_alignment.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\13_placeholder_phase3_backend_alignment.md] @[docs\epic\EPIC_144_tracker.md]`

---

### Phase 4: Localization Synchronization & Freezed Validation

#### Phase 4: Localization & Accessibility
**Plan:** `@[docs\epic\tasks_EPIC_144\14_placeholder_phase4_localization.md]`
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md] @[docs\epic\tasks_EPIC_144\14_placeholder_phase4_localization.md] @[docs\epic\EPIC_144_tracker.md] --phase=4`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\14_placeholder_phase4_localization.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\14_placeholder_phase4_localization.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\14_placeholder_phase4_localization.md] @[docs\epic\EPIC_144_tracker.md]`

---

### Phase 5: Automated Verification & Quality Gates

#### Phase 5: Quality Gates & Anti-Happy-Path Falsification
**Plan:** `@[docs\epic\tasks_EPIC_144\15_placeholder_phase5_quality_gates.md]`
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md] @[docs\epic\tasks_EPIC_144\15_placeholder_phase5_quality_gates.md] @[docs\epic\EPIC_144_tracker.md] --phase=5`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\15_placeholder_phase5_quality_gates.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\15_placeholder_phase5_quality_gates.md] @[docs\epic\EPIC_144_tracker.md]`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\15_placeholder_phase5_quality_gates.md] @[docs\epic\EPIC_144_tracker.md]`

---

### Integration Checkpoint: Full-Stack Validation

- [ ] **[NOK]** Full backend test suite: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- [ ] **[NOK]** Full frontend Studio build: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`
- [ ] **[NOK]** Full frontend Studio tests: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio --test`
- [ ] **[NOK]** OpenAPI parity: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_generate_openapi.py --test`
- [ ] **[NOK]** Enum parity (all skips removed): `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test`

---

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains (specifically and exhaustively: `@[backend_v2/tests/unit/test_settings.py]`, `@[backend_v2/tests/unit/test_enum_parity.py]`, `@[backend_v2/tests/unit/test_v2_core_models.py]`, `@[backend_v2/tests/unit/models/dtos/test_output_profile.py]`, `@[backend_v2/tests/unit/models/test_output_profile_regression.py]`, `@[backend_v2/tests/unit/test_synthesis_distiller_hook.py]`, `@[backend_v2/tests/unit/services/test_blueprint.py]`, `@[backend_v2/tests/unit/hooks/test_scoring.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]`, `@[backend_v2/tests/unit/services/sdui/adapters/test_metadata_adapter.py]`, `@[backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py]`, `@[backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py]`, `@[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]`, `@[backend_v2/tests/unit/models/prompts/test_synthesis_directives.py]`, `@[client_app_v2/test/features/studio/models/output_profile_test.dart]`, `@[client_app_v2/test/features/studio/models/blueprint_config_test.dart]`, `@[client_app_v2/test/features/studio/controllers/output_profile_controller_test.dart]`, `@[client_app_v2/test/features/studio/views/widgets/profile/layout_editor_card_test.dart]`, `@[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart]`).
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths — verify zero references to `include_diagnostic_scorecard`, zero `unknownEnumValue` usage, zero `Literal["original", "custom", "normalized_100"]` string type definitions, zero raw `list[str]` `target_block_order` types.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: `/tier2-hardening-backend @[backend_v2/settings.py] @[backend_v2/models/enums.py] @[backend_v2/models/v2_core.py] @[backend_v2/models/dtos/output_profile.py] @[backend_v2/services/blueprint.py] @[backend_v2/services/matrix_domain_parser.py] @[backend_v2/services/sdui/adapters/authenticity_adapter.py] @[backend_v2/services/sdui/adapters/metadata_adapter.py] @[backend_v2/services/sdui/adapters/synthesis_text_adapter.py] @[backend_v2/services/sdui/adapters/executive_summary_adapter.py] @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py] @[backend_v2/services/sdui/adapters/printable_sources_adapter.py] @[backend_v2/models/prompts/synthesis_directives.py] @[backend_v2/models/prompts/__init__.py] @[backend_v2/worker.py] @[backend_v2/tests/unit/test_settings.py] @[backend_v2/tests/unit/test_enum_parity.py] @[backend_v2/tests/unit/test_v2_core_models.py] @[backend_v2/tests/unit/models/dtos/test_output_profile.py] @[backend_v2/tests/unit/models/test_output_profile_regression.py] @[backend_v2/tests/unit/test_synthesis_distiller_hook.py] @[backend_v2/tests/unit/services/test_blueprint.py] @[backend_v2/tests/unit/hooks/test_scoring.py] @[backend_v2/tests/unit/test_worker_synthesis.py] @[backend_v2/tests/unit/services/test_matrix_domain_parser.py] @[backend_v2/tests/unit/services/sdui/adapters/test_metadata_adapter.py] @[backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py] @[backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py] @[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py] @[backend_v2/tests/unit/models/prompts/test_synthesis_directives.py]`
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: `/tier2-hardening-frontend @[client_app_v2/lib/core/models/enums.dart] @[client_app_v2/lib/features/studio/models/output_profile.dart] @[client_app_v2/lib/features/studio/models/blueprint_config.dart] @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/base_block_card.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/synthesis_text_block_card.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart] @[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart] @[client_app_v2/test/features/studio/models/output_profile_test.dart] @[client_app_v2/test/features/studio/models/blueprint_config_test.dart] @[client_app_v2/test/features/studio/controllers/output_profile_controller_test.dart] @[client_app_v2/test/features/studio/views/widgets/profile/layout_editor_card_test.dart] @[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart]`
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain — zero imports of deleted `include_diagnostic_scorecard` field, zero references to removed `AUTHENTICITY_THRESHOLDS` dict in adapters, zero raw XML tags in cleansed PromptBlocks.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic across `@[backend_v2/services/blueprint.py]`, `@[backend_v2/services/sdui/adapters/]`, and `@[backend_v2/models/v2_core.py]`.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

---

### Documentation & Knowledge Item Update

- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in `<appDataDir>/knowledge/` (specifically and exhaustively: `synthesis_directives.py` SSOT, `SystemUiConstraints` enum, `DisplayScale` cross-language enum parity, `TargetBlockType` strict dispatch pattern).
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

---

### Final Epic Audit

- [ ] **[NOK]** Epic Boundary Audit: Run `uv run python scripts/audit_markdown_boundaries.py --file @[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]` to verify all AST line boundaries in the Epic are still correct.
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

---

## Instructions for the Execution Agent

1. **Atomic Commit Mandate:** After each successfully passing audit loop (`backend_audit_loop.py` or `flutter_audit_loop.py`), perform an atomic `git commit` specifying ALL modified file paths before proceeding to the next plan or step.
2. **Seeding Environment:** When executing seed-related plans, run `uv run python backend_v2/seed/run_seed.py local` to refresh the local TinyDB database. Under `ConfigDict(strict=True, extra="forbid")`, stale keys in the local DB cause fatal `pydantic.ValidationError`.
3. **`@-reference` Syntax:** All file references in plans and this tracker use workspace-relative `@[path]` notation. The IDE resolves these automatically.
4. **You MUST update the Resume Command at the bottom of this tracker before handing over the session.** Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue.
5. **Mandatory Workflow Loop:** `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute -> /tier8-audit-plan`. You MUST ALWAYS pass BOTH the plan AND the tracker file in ALL commands.
6. **Post-Phase Completion Loop:** Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`.
7. **Note:** You do not need to specify `--rules` in the resume command; context rules are self-hydrating.

---

## Requirements Traceability Matrix

| # | Requirement | Source | Plan | Step(s) |
|:--|:-----------|:-------|:-----|:--------|
| R01 | Define `DisplayScale(StrEnum)` in `@[backend_v2/models/enums.py]` with ORIGINAL, CUSTOM, NORMALIZED_100 and `@property l10n_key` | Epic V6 (L59) | Plan 01 | Step 1 |
| R02 | Add `authenticity_threshold_high` (default=80.0, ge=0.0, le=100.0) to `@[backend_v2/settings.py]` | Epic V13 (L69) | Plan 01 | Step 2 |
| R03 | Add `authenticity_threshold_low` (default=50.0, ge=0.0, le=100.0) to `@[backend_v2/settings.py]` | Epic V13 (L69) | Plan 01 | Step 2 |
| R04 | `@model_validator(mode="after")` enforcing `high >= low` in Settings | Epic V13 (L69) | Plan 01 | Step 2 |
| R05 | Boundary tests for thresholds in `@[backend_v2/tests/unit/test_settings.py]` (-0.1, 100.1, inversion, env overrides) | Epic Phase 5 (L653) | Plan 01 | Step 3 |
| R06 | Cross-language enum parity test `@[backend_v2/tests/unit/test_enum_parity.py]` for all shared enums | Epic V6/V14 (L59-L70) | Plan 01 | Step 4 |
| R07 | Purge `include_diagnostic_scorecard` from `@[backend_v2/seed/seed_data.json]` | Epic V12 (L68) | Plan 02 | Step 2 |
| R08 | Complete `metric_mappings` with bilingual metadata keys (metadata_user, metadata_organization, metadata_scoring_engine, metadata_strictness) | Epic V7 (L60) | Plan 02 | Step 3 |
| R09 | Verify all `display_scale`, `preset_view`, `text_delivery_mode` values are valid enum strings in seed | Epic V6/V9 (L59, L65) | Plan 02 | Step 4 |
| R10 | Execute local database reseed: `uv run python backend_v2/seed/run_seed.py local` | Epic V12 (L68) | Plan 02 | Step 5 |
| R11 | Remove `include_diagnostic_scorecard` from `OutputProfile` in `@[backend_v2/models/v2_core.py]` | Epic V12 (L68) | Plan 03 | Step 1 |
| R12 | Migrate `display_scale` from `Literal[...]` to `DisplayScale` in `OutputProfile` | Epic V6 (L59) | Plan 03 | Step 1 |
| R13 | Migrate `target_block_order` from `list[str]` to `list[LaxTargetBlockType]` in `OutputProfile` | Epic V14 (L70) | Plan 03 | Step 1 |
| R14 | Remove `include_diagnostic_scorecard` from `OutputProfileCreateDTO` | Epic V12 (L68) | Plan 03 | Step 2 |
| R15 | Migrate `display_scale` to `DisplayScale` in `OutputProfileCreateDTO` | Epic V6 (L59) | Plan 03 | Step 2 |
| R16 | Migrate `target_block_order` to `list[TargetBlockType]` in `OutputProfileCreateDTO` | Epic V14 (L70) | Plan 03 | Step 2 |
| R17 | Non-nullable `max_extension_items: Annotated[int, Field(default=3, ge=1, le=100)]` on `OutputProfileCreateDTO` | Epic V10 (L66) | Plan 03 | Step 2 |
| R18 | Remove `include_diagnostic_scorecard` from `OutputProfileUpdateDTO` | Epic V12 (L68) | Plan 03 | Step 3 |
| R19 | `max_extension_items: Annotated[int | None, Field(default=None, ge=1, le=100)]` on `OutputProfileUpdateDTO` | Epic V10 (L66) | Plan 03 | Step 3 |
| R20 | Remove `include_diagnostic_scorecard` from `OutputProfileResponseDTO` | Epic V12 (L68) | Plan 03 | Step 4 |
| R21 | Non-nullable `max_extension_items` on `OutputProfileResponseDTO` | Epic V10 (L66) | Plan 03 | Step 4 |
| R22 | `ConfigDict(strict=True, extra="forbid")` enforced on OutputProfile, OutputLayoutBlock, SynthesisConfigDTO, all DTOs | Epic §2.2 (L41) | Plan 03 | Steps 1-4 |
| R23 | Update `test_v2_core_models.py` fixtures: DisplayScale enum, remove include_diagnostic_scorecard | Epic V9 (L65) | Plan 04 | Step 1 |
| R24 | Negative tests for `max_extension_items` bounds (0, -1, 101), invalid `display_scale`, legacy keys, nested extra keys | Epic Phase 5 (L654) | Plan 04 | Step 2 |
| R25 | Update `test_output_profile_regression.py` with TargetBlockType enum values | Epic V14 (L70) | Plan 04 | Step 3 |
| R26 | Update `test_synthesis_distiller_hook.py` fixtures | Epic V9 (L65) | Plan 04 | Step 4 |
| R27 | Update `test_blueprint.py` fixtures with DisplayScale, metric_mappings, target_block_order TargetBlockType | Epic V9 (L65) | Plan 05 | Step 1 |
| R28 | Update `test_scoring.py` fixtures | Epic V9 (L65) | Plan 05 | Step 2 |
| R29 | Update `test_worker_synthesis.py` fixtures | Epic V9 (L65) | Plan 05 | Step 3 |
| R30 | Add DisplayScale coverage tests (ORIGINAL, CUSTOM, NORMALIZED_100) to `test_matrix_domain_parser.py` | Epic V6 (L59) | Plan 05 | Step 4 |
| R31 | OpenAPI spec generation: `uv run python backend_v2/scripts/generate_openapi.py` | Epic V11 (L67) | Plan 06 | Step 1 |
| R32 | OpenAPI parity test passes green | Epic V11 (L67) | Plan 06 | Step 2 |
| R33 | Full backend regression gate passes | Epic §3.0 Step 3 (L248) | Plan 06 | Step 3 |
| R34 | `@JsonEnum() enum DisplayScale` in `@[client_app_v2/lib/core/models/enums.dart]` | Epic V6 (L59) | Plan 07 | Step 1 |
| R35 | Add 4 missing `TargetBlockType` enum members (matrixGraphsBlock, matrixSummaryTableBlock, varianceValidationBlock, authenticityEvaluationBlock) | Epic V14 (L70) | Plan 07 | Step 2 |
| R36 | `SystemUiConstraints` enum in `enums.dart` (sliderMin=1, sliderMax=20, absoluteMax=100, default=3) | Epic V10 (L66) | Plan 07 | Step 3 |
| R37 | Remove `includeDiagnosticScorecard` from `output_profile.dart` Freezed model | Epic V12 (L68) | Plan 07 | Step 4 |
| R38 | Type `displayScale` as `DisplayScale` in Dart Freezed | Epic V6 (L59) | Plan 07 | Step 4 |
| R39 | Type `targetBlockOrder` as `List<TargetBlockType>` in Dart Freezed | Epic V14 (L70) | Plan 07 | Step 4 |
| R40 | Non-nullable `@Default(3) int maxExtensionItems` in Dart Freezed | Epic V10 (L66) | Plan 07 | Step 4 |
| R41 | Eradicate ALL `unknownEnumValue` fallback parameters from `output_profile.dart` | Epic V1 (L54) | Plan 07 | Step 4 |
| R42 | Eradicate `unknownEnumValue: PresetView.metrics1d` from `blueprint_config.dart` | Epic V1 (L54) | Plan 07 | Step 5 |
| R43 | Freezed code generation passes cleanly | Epic V11 (L67) | Plan 07 | Step 6 |
| R44 | Frontend negative tests: unmapped PresetView, TextDeliveryMode, HistoricalContextMode, DisplayScale, TargetBlockType → `CheckedFromJsonException` | Epic Phase 5 (L665) | Plan 08 | Step 1 |
| R45 | Frontend negative tests: unrecognized JSON keys at root and nested levels → `CheckedFromJsonException` | Epic Phase 5 (L665) | Plan 08 | Steps 1-2 |
| R46 | [NEW] `blueprint_config_test.dart` asserting `CheckedFromJsonException` on unmapped preset_view | Epic Phase 5 (L665) | Plan 08 | Step 2 |
| R47 | Update `output_profile_controller_test.dart` fixtures | Epic V9 (L65) | Plan 08 | Step 3 |
| R48 | Update `layout_editor_card_test.dart` fixtures | Epic V9 (L65) | Plan 08 | Step 4 |
| R49 | Full backend regression: `uv run python scripts/backend_audit_loop.py backend_v2 --test` | Epic §3.0 (L262) | Plan 09 | Step 1 |
| R50 | Full frontend Studio build and test passes green | Epic §3.0 (L263) | Plan 09 | Step 2 |
| R51 | Cross-stack parity: zero `include_diagnostic_scorecard`, zero `unknownEnumValue`, all enum parity skips removed | Epic §3.0 (L262-263) | Plan 09 | Step 3 |
| R52 | Golden Master characterization test baseline for `output_profile_crud_view.dart` | Epic Phase 1 (L365-367) | Plan 10 | Step 2 |
| R53 | Decompose `output_profile_crud_view.dart` into ≤200-line TabBar/TabBarView shell | Epic Phase 1 (L369) | Plan 11 | Step 5 |
| R54 | [NEW] `profile_general_tab.dart` ≤200 lines | Epic Phase 1 (L370-374) | Plan 11 | Step 2 |
| R55 | [NEW] `profile_scoring_tab.dart` ≤200 lines | Epic Phase 1 (L375-378) | Plan 11 | Step 3 |
| R56 | [NEW] `profile_layouts_tab.dart` ≤200 lines | Epic Phase 1 (L379-381) | Plan 11 | Step 4 |
| R57 | Golden Master parity tests still pass after decomposition | Epic Phase 1 (L365-367) | Plan 11 | Step 6 |
| R58 | Visual Block Builder with Registry Map pattern `Map<TargetBlockType, Widget Function()>` | Epic Phase 2 (L397) | Plan 12 | DEFERRED |
| R59 | 9 dedicated block card widgets under `blocks/` directory | Epic Phase 2 (L384-395) | Plan 12 | DEFERRED |
| R60 | Matrix Graphs Collection Builder with inline accordion editing | Epic Phase 2 (L407-412) | Plan 12 | DEFERRED |
| R61 | Matrix Summary Table independent block card with FilterChip column toggles | Epic Phase 2 (L414-418) | Plan 12 | DEFERRED |
| R62 | XAI Extensions slider with clamping + companion TextFormField validation | Epic Phase 2 (L427-483) | Plan 12 | DEFERRED |
| R63 | Migrate `AUTHENTICITY_THRESHOLDS` from adapter to `get_settings()` dynamic resolution | Epic V13 (L69) | Plan 13 | DEFERRED |
| R64 | MetadataAdapter: eradicate V7 hardcoded Finnish strings, V7a getattr duck-typing, V7b title fallback, V7c isinstance guard | Epic V7/V7a/V7b/V7c (L60-63) | Plan 13 | DEFERRED |
| R65 | SynthesisTextAdapter: read both `content_blocks` and `section_syntheses` (V8 fix) | Epic V8 (L64) | Plan 13 | DEFERRED |
| R66 | [NEW] `synthesis_directives.py` SSOT with XML mandate constants | Epic V15 (L71) | Plan 13 | DEFERRED |
| R67 | Strip 6 dead-weight fields from `SynthesisConfigDTO` and seed_data.json layouts | Epic V15 (L71) | Plan 13 | DEFERRED |
| R68 | Cleanse graph synthesis PromptBlocks to Markdown headings (de_generator_mandate_no_xml) | Epic V15 (L71) | Plan 13 | DEFERRED |
| R69 | Worker.py inject `SYNTHESIS_GRAPH_DIRECTIVES_XML` into dynamic context | Epic V15 (L71) | Plan 13 | DEFERRED |
| R70 | Type `xai_highlights` from `list[Any]` to `list[XaiHighlightItem]` | Epic Phase 3 §7 (L549) | Plan 13 | DEFERRED |
| R71 | `matrix_domain_parser.py` compare native `DisplayScale` enum members | Epic V6 (L59) | Plan 13 | DEFERRED |
| R72 | `blueprint.py` `_target_block_hydrators` typed as `dict[TargetBlockType, Callable]` with strict KeyError handling | Epic V14 (L70) | Plan 13 | DEFERRED |
| R73 | Bilingual `.arb` keys for all 3 tab titles, 10 block card titles, preset labels, toggle labels | Epic Phase 4 (L622-627) | Plan 14 | DEFERRED |
| R74 | Backend Enum `@property l10n_key` mapping for PresetView, XaiExtensionType, DisplayScale, ScoringStrategy | Epic Phase 4 (L627) | Plan 14 | DEFERRED |
| R75 | `SynthesisConfigDTO` dead-weight field purge in Dart Freezed models | Epic V15 (L607) | Plan 14 | DEFERRED |
| R76 | Backend negative tests: blueprint.py unmapped TargetBlockType → AppException | Epic Phase 5 (L650) | Plan 15 | DEFERRED |
| R77 | Backend negative tests: MetadataAdapter missing metric_mappings keys → AppException | Epic Phase 5 (L651) | Plan 15 | DEFERRED |
| R78 | Backend negative tests: AuthenticityAdapter threshold boundary classifications (80.0, 79.99, 50.0, 49.99) | Epic Phase 5 (L652) | Plan 15 | DEFERRED |
| R79 | Frontend negative tests: SduiBlockDTO unknown block_type, missing fields, extra keys → exceptions | Epic Phase 5 (L666) | Plan 15 | DEFERRED |
| R80 | Widget tests: max_extension_items=50 slider clamping without assertion crash | Epic Phase 5 (L668) | Plan 15 | DEFERRED |
| R81 | Eradicate V2 (SizedBox.shrink to hide unavailable XAI extensions) | Epic V2 (L55) | Plan 11 | Steps 2-5 |
| R82 | Eradicate V3 (AsyncValue<List<dynamic>> → typed AsyncValue) | Epic V3 (L56) | Plan 11 | Steps 2-5 |
| R83 | Eradicate V4 (Hardcoded color `Color(0xFF2E7D32)`) | Epic V4 (L57) | Plan 11 | Steps 2-5 |
| R84 | Eradicate V5 (Hardcoded pixel values → AppSpacing design tokens) | Epic V5 (L58) | Plan 11 | Steps 2-5 |

---

# Session Handover Context

## Achieved
- **Tier 1 Epic Planning Completed:** 15 implementation plan files generated in `@[docs\epic\tasks_EPIC_144]`.
  - Plans 01-11 contain fully specified execution protocols, granular steps, test contracts, validation gates, anti-targets, and DoD checklists.
  - Plans 12-15 are defined as structured placeholders (DEFERRED) for Phases 2-5.
- **EPIC 144 Tracker Established:** Comprehensive tracker initialized with phase checkboxes, post-implementation gates, and a complete 84-item Requirements Traceability Matrix (`R01`–`R84`).
- **Neuro-Symbolic Plan Verification:** `audit_planner_output.py` executed successfully against `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]` with 100% boundary and target file fidelity.
- **Phase 0-A Red-Teaming & Falsification Passed (`[OK]`):**
  - Completed System 2 Red-Teaming on `@[docs\epic\tasks_EPIC_144\01_p0_backend_config_enums.md]`.
  - Added `LaxDisplayScale = Annotated[DisplayScale, Field(strict=False)]` alias to `@[backend_v2/models/enums.py]` for database hydration resilience per `annotated_hydration_mandate`.
  - Enforced PEP 673 `Self` return type on `@model_validator(mode="after")` in `@[backend_v2/settings.py]`.
  - Consolidated cross-language enum parity testing into `@[backend_v2/tests/unit/test_enum_parity.py]` (AST-based) and scheduled legacy `@[backend_v2/tests/architecture/test_enum_parity.py]` for clean demolition per `test_directory_isolation`.
- **Phase 0-A Implementation & Quality Gate Execution Completed (`[OK]`):**
  - Implemented `DisplayScale(StrEnum)` and `LaxDisplayScale` in `@[backend_v2/models/enums.py#L69-L80, L640]`.
  - Centralized `authenticity_threshold_high` (80.0) and `authenticity_threshold_low` (50.0) in `@[backend_v2/settings.py#L212-L230]` with `@model_validator(mode="after") validate_authenticity_thresholds(self) -> Self:`.
  - Implemented boundary, negative, and environment override tests in `@[backend_v2/tests/unit/test_settings.py#L32-L76]`.
  - Implemented cross-language enum parity verification in `@[backend_v2/tests/unit/test_enum_parity.py#L1-L176]` via AST and regex parsers, covering 7 shared enums immediately with skipped placeholders for `DisplayScale` and `TargetBlockType` awaiting Plan 07.
  - Demolished legacy `@[backend_v2/tests/architecture/test_enum_parity.py]`.
  - Passed Universal Quality Gate (`backend_audit_loop.py`) with 100% test pass rate and >95% TDD coverage across target files.
  - Committed atomically: `798b296c feat(config): implement DisplayScale enum, authenticity thresholds, and cross-language enum parity test`.
- **Phase 0-A Post-Implementation Audit Signed Off (`[OK]`):**
  - Executed `/tier8-audit-plan` against `@[docs\epic\tasks_EPIC_144\01_p0_backend_config_enums.md]`.
  - Verified 100% physical traceability for requirements R01–R06 and demolition D01.
  - Confirmed zero supply-chain violations (banned AI bloatware packages).
  - Executed global test suite (1444 tests passed, 0 failures).
  - Emitted formal artifact: `@[red_team_audit_01_p0_backend_config_enums.md]`.
  - Committed tracker sign-off: `5155ff2f docs(epic-144): sign off Phase 0-A audit in tracker`.
- **Phase 0-B Red-Teaming & Falsification Passed (`[OK]`):**
  - Completed System 2 Red-Teaming on `@[docs\epic\tasks_EPIC_144\02_p0_seed_sanitization.md]`.
  - Verified physical state of `@[backend_v2/seed/seed_data.json#L9185-L9925]` (`include_diagnostic_scorecard` already absent; 4 bilingual metadata keys missing from `metric_mappings`).
  - Enforced strict compliance with `@[.agents/rules/03_seed_vault.md]` (replaced CRLF-breaking `grep_search` with deterministic Python scripts; added mandatory timestamped backup in `backend_v2/seed/backups/`).
  - Added automated unit test requirement in `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]` covering positive & negative seed integrity assertions.
  - Mutated Plan 02 and re-verified 100% boundary fidelity with `audit_planner_output.py`.
- **Phase 0-B Implementation & Quality Gate Execution Completed (`[OK]`):**
  - Created timestamped backup `@[backend_v2/seed/backups/seed_data_backup_p0b.json]`.
  - Surgically injected 4 bilingual metadata label keys (`metadata_user`, `metadata_organization`, `metadata_scoring_engine`, `metadata_strictness`) into `metric_mappings` of profile `prf_5d6e7f8091a2b3c4` in `@[backend_v2/seed/seed_data.json#L9260-L9290]`.
  - Verified zero occurrences of `include_diagnostic_scorecard` across `seed_data.json`.
  - Implemented automated guardrail tests in `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py#L95-L215]` covering positive and negative assertions for legacy scorecard absence, complete bilingual metadata keys, and valid enum values.
  - Resolved dynamic `SEED_FILE` path relative to `Path(__file__).resolve().parents[2]` per `absolute_path_context_amnesia_ban`.
  - Executed local database reseed (`uv run python backend_v2/seed/run_seed.py local`) successfully with exit code 0.
  - Passed Universal Quality Gate (`backend_audit_loop.py`) with 100% test pass rate and 92% TDD coverage.
  - Committed atomically: `15607978 feat(seed): sanitize output profiles and inject bilingual metadata keys in metric_mappings`.
  - Updated tracker and task plan status: `021ea172 docs(epic-144): update Phase 0-B execution completion status and handover context`.

## Learned
- **Codebase Baseline & Violation Topology:** The codebase currently has a monolithic 856-line `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` with 15 identified architectural violations (V1–V15).
- **Fail-Fast Hydration Invariant:** The `OutputProfile` model currently contains legacy `include_diagnostic_scorecard: bool`, uses raw `Literal["original", "custom", "normalized_100"]` for `display_scale`, and `list[str]` for `target_block_order`. Flutter models utilize `unknownEnumValue` fallback annotations.
- **Atomic 6-Step Execution Protocol:** To prevent fatal `pydantic.ValidationError(extra_forbidden)` crashes under `ConfigDict(strict=True, extra="forbid")`, modifications MUST execute in strict order: Seed Sanitization & Local Reseed (02) → Models & DTO Purge (03) → OpenAPI Sync (06) → Frontend Enums & Freezed (07) → UI Decomposition (10-11) → Quality Gates.
- **Seed Vault Protocol Invariants:** When auditing or modifying `seed_data.json`, CRLF encoding causes `grep_search` to silently fail; deterministic Python scripts using `json.load` and bounded reads are mandatory. Pre-mutation backups in `backend_v2/seed/backups/` are strictly required before any JSON modifications.
- **Testing Architecture Consolidation:** Architectural tests in `tests/architecture/` must be transitioned to the standard test pyramid (`tests/unit/`) to maintain single test suite sovereignty without duplicate scanners.
- **Dynamic File Path SSOT in Tests:** In test fixtures accessing seed files, hardcoded Windows absolute paths (e.g., `c:\src\quorum\...`) must be replaced with `Path(__file__).resolve().parents[N]` to prevent cross-machine amnesia.
- **Settings Post-Init Credential Scanning:** Testing `Settings.model_post_init` credential checks requires mocking `Path.exists` because `Settings` automatically scans the filesystem root for `service-account.json`.
- **Enum Parity Testing Paradigm:** Python `ast.parse` and regex extraction over Dart `@JsonValue` provide deterministic verification without importing heavy cross-stack runtimes.

## Remaining
- **Phase 0-B (Plan 02):** Master Seed Sanitization & Local Reseed (`@[docs\epic\tasks_EPIC_144\02_p0_seed_sanitization.md]`) — Audit (`/tier8-audit-plan`).
- **Phase 0-C through Phase 0-I (Plans 03-09):** Model & DTO purge, test fixtures alignment batches 1 & 2, OpenAPI generation, frontend enum sync, frontend test fixtures, integration checkpoint.
- **Phase 1-A & Phase 1-B (Plans 10-11):** Golden Master baseline characterization and 3-tab scaffold decomposition (`output_profile_crud_view.dart` decomposed into ≤200-line shell + 3 tabs).
- **Phases 2-5 Detailed Planning (Plans 12-15):** Generate executable plans via `/tier0-create-plan` and execute Phases 2-5.
- **Post-Implementation Gates:** Golden Master restoration audit, Proxy sunset, Tier 2 Hardening Backend & Frontend, Pre-delete audit, Semantic coverage (>90%), and Live E2E verification (`test_integration_real_llm.py`).
- **Knowledge Item & Architecture Sync:** Create KIs for new SSOTs and execute `/tier7-describe-architecture` and `/tier8-audit-epic`.

## Resume Command
`/tier5-resume --target="@[docs\epic\tasks_EPIC_144\02_p0_seed_sanitization.md] @[docs\epic\EPIC_144_tracker.md]" --workflow=/tier8-audit-plan`




