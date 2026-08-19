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
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\02_p0_seed_sanitization.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-C: Backend Models & DTO Strict Purge
**Plan:** `@[docs\epic\tasks_EPIC_144\03_p0_backend_models_dto_purge.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\03_p0_backend_models_dto_purge.md] @[docs\epic\EPIC_144_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\03_p0_backend_models_dto_purge.md] @[docs\epic\EPIC_144_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Modify OutputProfile in v2_core.py
  - [x] Step 2: Modify OutputProfileCreateDTO
  - [x] Step 3: Modify OutputProfileUpdateDTO
  - [x] Step 4: Modify OutputProfileResponseDTO
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\03_p0_backend_models_dto_purge.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-D: Backend Test Fixtures Alignment Batch 1
**Plan:** `@[docs\epic\tasks_EPIC_144\04_p0_backend_test_fixtures_batch1.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\04_p0_backend_test_fixtures_batch1.md] @[docs\epic\EPIC_144_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\04_p0_backend_test_fixtures_batch1.md] @[docs\epic\EPIC_144_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Update test_v2_core_models.py Fixtures
  - [x] Step 2: Update and Add Negative Tests to test_output_profile.py
  - [x] Step 3: Update test_output_profile_regression.py
  - [x] Step 4: Update test_synthesis_distiller_hook.py
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\04_p0_backend_test_fixtures_batch1.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-E: Backend Test Fixtures Alignment Batch 2
**Plan:** `@[docs\epic\tasks_EPIC_144\05_p0_backend_test_fixtures_batch2.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\05_p0_backend_test_fixtures_batch2.md] @[docs\epic\EPIC_144_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\05_p0_backend_test_fixtures_batch2.md] @[docs\epic\EPIC_144_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Update test_blueprint.py Fixtures
  - [x] Step 2: Update test_scoring.py Fixtures
  - [x] Step 3: Update test_worker_synthesis.py Fixtures
  - [x] Step 4: Update test_matrix_domain_parser.py Fixtures
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\05_p0_backend_test_fixtures_batch2.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-F: OpenAPI Synchronization Gate
**Plan:** `@[docs\epic\tasks_EPIC_144\06_p0_openapi_sync_gate.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\06_p0_openapi_sync_gate.md] @[docs\epic\EPIC_144_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\06_p0_openapi_sync_gate.md] @[docs\epic\EPIC_144_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Generate OpenAPI Specification
  - [x] Step 2: Verify OpenAPI Unit Test Parity
  - [x] Step 3: Verify Generated OpenAPI Schema Assertions
  - [x] Step 4: Full Backend Regression Gate
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\06_p0_openapi_sync_gate.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-G: Frontend Enum & Freezed Synchronization
**Plan:** `@[docs\epic\tasks_EPIC_144\07_p0_frontend_enums_freezed.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\07_p0_frontend_enums_freezed.md] @[docs\epic\EPIC_144_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\07_p0_frontend_enums_freezed.md] @[docs\epic\EPIC_144_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Add DisplayScale Enum to enums.dart
  - [x] Step 2: Add Missing TargetBlockType Members
  - [x] Step 3: Add SystemUiConstraints Enum
  - [x] Step 4: Modify output_profile.dart Freezed Model
  - [x] Step 5: Modify blueprint_config.dart Freezed Model
  - [x] Step 6: Run Freezed Code Generation
  - [x] Step 7: Unskip Python Cross-Language Enum Parity Tests
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\07_p0_frontend_enums_freezed.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-H: Frontend Test Fixtures & Negative Tests
**Plan:** `@[docs\epic\tasks_EPIC_144\08_p0_frontend_test_fixtures.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\08_p0_frontend_test_fixtures.md] @[docs\epic\EPIC_144_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\08_p0_frontend_test_fixtures.md] @[docs\epic\EPIC_144_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Update output_profile_test.dart
  - [x] Step 2: Create blueprint_config_test.dart
  - [x] Step 3: Update output_profile_controller_test.dart
  - [x] Step 4: Update layout_editor_card_test.dart
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\08_p0_frontend_test_fixtures.md] @[docs\epic\EPIC_144_tracker.md]`

---

#### Phase 0-I: Integration Checkpoint
**Plan:** `@[docs\epic\tasks_EPIC_144\09_p0_integration_checkpoint.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\09_p0_integration_checkpoint.md] @[docs\epic\EPIC_144_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\09_p0_integration_checkpoint.md] @[docs\epic\EPIC_144_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Full Backend Regression & Quality Gate Audit
  - [x] Step 2: Frontend Studio Model Build and Test
  - [x] Step 3: Cross-Stack Parity Assertions
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\09_p0_integration_checkpoint.md] @[docs\epic\EPIC_144_tracker.md]`

---

### Phase 1: Sub-Tab Information Architecture & Scaffold Decomposition

#### Phase 1-A: Golden Master Test Baseline
**Plan:** `@[docs\epic\tasks_EPIC_144\10_p1_golden_master_baseline.md]`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_144\10_p1_golden_master_baseline.md] @[docs\epic\EPIC_144_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_144\10_p1_golden_master_baseline.md] @[docs\epic\EPIC_144_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Analyze Current View Structure
  - [x] Step 2: Create Golden Master Widget Tests
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_144\10_p1_golden_master_baseline.md] @[docs\epic\EPIC_144_tracker.md]`

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

- [x] **[OK]** Full backend test suite: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- [x] **[OK]** Full frontend Studio build: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`
- [x] **[OK]** Full frontend Studio tests: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio --test`
- [x] **[OK]** OpenAPI parity: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_generate_openapi.py --test`
- [x] **[OK]** Enum parity (all skips removed): `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test`

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
  - Implemented automated guardrail tests in `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py#L95-L230]` covering positive and negative assertions for legacy scorecard absence, complete bilingual metadata keys, and valid enum values.
  - Resolved dynamic `SEED_FILE` path relative to `Path(__file__).resolve().parents[2]` per `absolute_path_context_amnesia_ban`.
  - Executed local database reseed (`uv run python backend_v2/seed/run_seed.py local`) successfully with exit code 0.
  - Passed Universal Quality Gate (`backend_audit_loop.py`) with 100% test pass rate and 92% TDD coverage.
  - Committed atomically: `15607978 feat(seed): sanitize output profiles and inject bilingual metadata keys in metric_mappings`.
- **Phase 0-B Post-Implementation Audit Signed Off (`[OK]`):**
  - Executed `/tier8-audit-plan` against `@[docs\epic\tasks_EPIC_144\02_p0_seed_sanitization.md]`.
  - Verified 100% physical traceability for requirements R07–R15 (seed backup, bilingual metadata keys injection, zero legacy fields, automated guardrail unit tests, local reseed).
  - Confirmed zero supply-chain violations (banned AI bloatware packages).
  - Executed global test suite (1447 passed, 29 skipped, 4 xpassed, 0 failures).
  - Emitted formal artifact: `@[red_team_audit_02_p0_seed_sanitization.md]`.
- **Phase 0-C Implementation & Quality Gate Execution Completed (`[OK]`):**
  - Completely purged legacy `include_diagnostic_scorecard` from `OutputProfile` in `@[backend_v2/models/v2_core.py#L1355]` and from `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO` in `@[backend_v2/models/dtos/output_profile.py]`, including cleaning all class docstrings.
  - Migrated `display_scale` from raw string literals (`Literal["original", "custom", "normalized_100"]`) to PEP 593 `Annotated[LaxDisplayScale, Field(default=DisplayScale.ORIGINAL, ...)] = DisplayScale.ORIGINAL` on `OutputProfile` (using `LaxDisplayScale` for database string coercion) and `Annotated[DisplayScale, ...]` across all DTOs (`DisplayScale | None` for update).
  - Migrated `target_block_order` to `Annotated[list[LaxTargetBlockType], Field(default_factory=lambda: [...])]` on `OutputProfile` and `Annotated[list[TargetBlockType], ...]` on `OutputProfileResponseDTO`, while preserving client flexibility with optional `Annotated[list[TargetBlockType] | None, ...] = None` on `CreateDTO` and `UpdateDTO`.
  - Enforced strict integer range bounds on `max_extension_items`: non-nullable `Annotated[int, Field(default=3, ge=1, le=100)] = 3` on `OutputProfile`, `CreateDTO`, and `ResponseDTO`, and `Annotated[int | None, Field(default=None, ge=1, le=100)] = None` on `UpdateDTO`.
  - Confirmed strict Pydantic V2 metadata enforcement (`model_config = ConfigDict(strict=True, extra="forbid")`) across `OutputProfile`, `OutputLayoutBlock`, `SynthesisConfigDTO`, and all output profile DTOs.
  - Executed database re-seeding (`uv run python backend_v2/seed/run_seed.py local`) successfully with clean TinyDB table recreation and zero validation errors.
  - Executed quality audit loops: Ruff linting & formatting 100% clean, MyPy strict typing 100% clean, and unit tests passing with 100% statement coverage on `backend_v2/models/dtos/output_profile.py`.
  - Verified zero occurrences of `include_diagnostic_scorecard` and raw `Literal["original"` in both `v2_core.py` and `output_profile.py`.

- **Phase 0-C Post-Implementation Audit Signed Off (`[OK]`):**
  - Executed `/tier8-audit-plan` against `@[docs\epic\tasks_EPIC_144\03_p0_backend_models_dto_purge.md]`.
  - Verified 100% physical traceability for requirements R11–R22.
  - Confirmed complete eradication of legacy `include_diagnostic_scorecard` and raw string `Literal["original", ...]` across target files.
  - Confirmed zero supply-chain violations (banned AI bloatware packages).
  - Executed target quality gates and full suite audit (1446 passed, 29 skipped, 4 xpassed).
  - Verified 100% planner fidelity via `audit_planner_output.py`.
  - Emitted formal artifact: `@[red_team_audit_03_p0_backend_models_dto_purge.md]`.
- **Phase 0-D Red-Teaming & Falsification Passed (`[OK]`):**
  - Completed System 2 Red-Teaming on `@[docs\epic\tasks_EPIC_144\04_p0_backend_test_fixtures_batch1.md]`.
  - Diagnosed baseline test failure in `@[backend_v2/tests/unit/models/test_output_profile_regression.py]` where `target_block_order` fixture passed raw string list `["metadata_block", ...]` causing `ValidationError` against strict `OutputProfileResponseDTO`.
  - Refined Step 3 to explicitly pass `[TargetBlockType.METADATA_BLOCK, TargetBlockType.SYNTHESIS_TEXT_BLOCK]` enum instances and assert against enum members.
  - Refined Step 2 test contracts in `@[backend_v2/tests/unit/models/dtos/test_output_profile.py]` with 9 deterministic boundary and negative assertions (`max_extension_items` 0, -1, 101, 1, 100; invalid `display_scale`; legacy `include_diagnostic_scorecard`; nested `synthesis.ghost_field`; invalid `target_block_order`).
  - Removed ambiguous file references, locking `@[backend_v2/tests/unit/models/dtos/test_output_profile.py]`.
  - Re-verified planner output fidelity via `audit_planner_output.py` with 100% compliance.
- **Phase 0-D Implementation & Quality Gate Execution Completed (`[OK]`):**
  - Updated `@[backend_v2/tests/unit/test_v2_core_models.py#L4-L70]` to import `DisplayScale` and use `DisplayScale.ORIGINAL` across test fixtures. Verified zero occurrences of `include_diagnostic_scorecard`.
  - Updated `@[backend_v2/tests/unit/models/dtos/test_output_profile.py#L1-L150]` with all 9 mandated negative & boundary test contracts for `OutputProfileCreateDTO` (0, -1, 101, 1, 100 on `max_extension_items`; invalid `display_scale`; legacy `include_diagnostic_scorecard` forbidden extra; nested `SynthesisConfigDTO` forbidden extra; invalid `target_block_order`), and updated `OutputProfileUpdateDTO`/`OutputProfileResponseDTO` strictness tests.
  - Updated `@[backend_v2/tests/unit/models/test_output_profile_regression.py#L1-L45]` to import `TargetBlockType` and pass `[TargetBlockType.METADATA_BLOCK, TargetBlockType.SYNTHESIS_TEXT_BLOCK]` in `target_block_order` fixture and assertions.
  - Updated `@[backend_v2/tests/unit/test_synthesis_distiller_hook.py#L1-L150]` to import `HookResult` at top level per `inline_imports_ban`, verified zero occurrences of `include_diagnostic_scorecard`, and added explicit `cast(Awaitable[HookResult], ...)` for full MyPy strict compliance.
  - Passed Universal Quality Gate (`backend_audit_loop.py`) with 100% test pass rate and 100% TDD coverage across all 4 target files.
  - Committed atomically: `fb5d93db test(output-profile): align backend test fixtures batch 1 with DisplayScale, TargetBlockType enums and update tracker handover`.

- **Phase 0-D Post-Implementation Audit Signed Off (`[OK]`):**
  - Executed `/tier8-audit-plan` against `@[docs\epic\tasks_EPIC_144\04_p0_backend_test_fixtures_batch1.md]`.
  - Verified 100% physical traceability for requirements R23–R26 across all 4 test files.
  - Confirmed complete eradication of legacy `include_diagnostic_scorecard` and raw literal strings.
  - Verified 9 ISTQB-aligned boundary and negative test cases for `OutputProfileCreateDTO` and `SynthesisConfigDTO`.
  - Confirmed zero supply-chain violations (banned AI bloatware packages).
  - Executed target quality gates (100% pass, 100% coverage) and full unit test suite (1456 passed, 29 skipped, 4 xpassed, 0 failures).
  - Emitted formal artifact: `@[red_team_audit_04_p0_backend_test_fixtures_batch1.md]`.

- **Phase 0-E Red-Teaming & Falsification Passed (`[OK]`):**
  - Completed System 2 Red-Teaming on `@[docs\epic\tasks_EPIC_144\05_p0_backend_test_fixtures_batch2.md]`.
  - Verified physical state of the 4 target test files (`@[backend_v2/tests/unit/services/test_blueprint.py]`, `@[backend_v2/tests/unit/hooks/test_scoring.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]`): zero occurrences of legacy `include_diagnostic_scorecard` found across all 4 files.
  - Refined Step 1 in Plan 05 to reference exact line ranges (L124–L2276) and mandate `TargetBlockType` enum instances at L2277 for `target_block_order`.
  - Refined Step 4 in Plan 05 to mandate ISTQB-aligned test additions in `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]` covering all 3 `DisplayScale` enum options (`DisplayScale.ORIGINAL`, `DisplayScale.NORMALIZED_100`, `DisplayScale.CUSTOM`) and a negative test for `DisplayScale.CUSTOM` with missing `scale_min`/`scale_max` triggering Fail-Fast `AppException(CONFIGURATION_ERROR)`.
- **Phase 0-E Implementation & Quality Gate Execution Completed (`[OK]`):**
  - Updated `@[backend_v2/tests/unit/services/test_blueprint.py]` to import `DisplayScale` and `TargetBlockType`, defined `_DEFAULT_TARGET_BLOCK_ORDER`, migrated all `OutputProfile` fixtures to use `DisplayScale.ORIGINAL`, `DisplayScale.CUSTOM`, `DisplayScale.NORMALIZED_100` and `TargetBlockType` enum members for `target_block_order`.
  - Verified `@[backend_v2/tests/unit/hooks/test_scoring.py]` and `@[backend_v2/tests/unit/test_worker_synthesis.py]` fixtures contain valid `DisplayScale` enum strings and zero references to legacy `include_diagnostic_scorecard`.
  - Updated `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]` with `DisplayScale` import and default parameter on `get_dummy_profile(display_scale=DisplayScale.ORIGINAL)`. Added 4 test contracts covering all 3 `DisplayScale` enum modes (`ORIGINAL`, `NORMALIZED_100`, `CUSTOM`) and negative Fail-Fast test on missing custom scale bounds (`CONFIGURATION_ERROR`).
  - Passed Universal Quality Gate (`backend_audit_loop.py`) across all 4 target files with 100% test pass rate and >95% statement coverage (100% on `test_matrix_domain_parser.py`).
  - Executed full backend unit test suite: 1460 passed, 29 skipped, 4 xpassed, 0 failures.
  - Committed atomically: `ecaca1cf test(output-profile): align backend test fixtures batch 2 with DisplayScale, TargetBlockType enums and update tracker`.

- **Phase 0-E Post-Implementation Audit Signed Off (`[OK]`):**
  - Executed `/tier8-audit-plan` against `@[docs\epic\tasks_EPIC_144\05_p0_backend_test_fixtures_batch2.md]`.
  - Verified 100% physical traceability for requirements R27–R30 and demolition D01.
  - Confirmed complete eradication of legacy `include_diagnostic_scorecard` across all 4 target test files.
  - Verified ISTQB-aligned unit tests covering all 3 `DisplayScale` modes (`ORIGINAL`, `NORMALIZED_100`, `CUSTOM`) and negative Fail-Fast test on missing custom scale bounds (`CONFIGURATION_ERROR`) in `test_matrix_domain_parser.py`.
  - Confirmed zero supply-chain violations (banned AI bloatware packages).
  - Executed target quality gates (>97% coverage on each target file) and full backend test suite (1460 passed, 29 skipped, 4 xpassed, 0 failures).
  - Emitted formal artifact: `@[red_team_audit_05_p0_backend_test_fixtures_batch2.md]`.

- **Phase 0-F Implementation & Quality Gate Execution Completed (`[OK]`):**
  - Executed `@[backend_v2/scripts/generate_openapi.py]` generating the static OpenAPI schema at `@[docs/swagger/openapi.json]`.
  - Executed OpenAPI unit tests (`test_generate_openapi.py`) passing 2/2 tests green and passing all 5 backend audit loop quality steps (ruff check, ruff format, mypy --strict, Jinja validation, Seed Data dry-run).
  - Verified all 5 deterministic OpenAPI schema assertions in `docs/swagger/openapi.json` with 100% compliance:
    1. `DisplayScale` enum in `components/schemas` with values `["original", "custom", "normalized_100"]`.
    2. `TargetBlockType` enum in `components/schemas` with 13 members (`global_score_block`, `penalties_block`, `audit_trail_block`, `jargon_ratio_block`, `printable_sources_block`, `grouped_extensions_block`, `executive_summary_block`, `metadata_block`, `synthesis_text_block`, `matrix_graphs_block`, `matrix_summary_table_block`, `variance_validation_block`, `authenticity_evaluation_block`).
    3. Complete eradication of `include_diagnostic_scorecard` from `OutputProfileCreateDTO` and `OutputProfileResponseDTO`.
    4. `OutputProfileCreateDTO.properties.max_extension_items` enforces `minimum: 1` and `maximum: 100`.
    5. `OutputProfileResponseDTO.properties.target_block_order.items` correctly references `#/components/schemas/TargetBlockType`.
  - Executed full backend regression test suite: 1460 passed, 29 skipped, 4 xpassed, 0 failures.
  - Committed atomically: `a1803fa5 feat(openapi): regenerate openapi spec reflecting DisplayScale and TargetBlockType enums and update tracker`.

- **Phase 0-F Post-Implementation Audit Signed Off (`[OK]`):**
  - Executed `/tier8-audit-plan` against `@[docs\epic\tasks_EPIC_144\06_p0_openapi_sync_gate.md]`.
  - Verified 100% physical traceability for requirements R31–R33.
  - Confirmed `generate_openapi.py` executed cleanly and regenerated `@[docs/swagger/openapi.json]`.
  - Verified 5 deterministic schema assertions via Python script:
    1. `DisplayScale` enum in `components/schemas` with values `["original", "custom", "normalized_100"]`.
    2. `TargetBlockType` enum in `components/schemas` with 13 members (`global_score_block`, `penalties_block`, `audit_trail_block`, `jargon_ratio_block`, `printable_sources_block`, `grouped_extensions_block`, `executive_summary_block`, `metadata_block`, `synthesis_text_block`, `matrix_graphs_block`, `matrix_summary_table_block`, `variance_validation_block`, `authenticity_evaluation_block`).
    3. Complete eradication of `include_diagnostic_scorecard` from `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO`.
    4. `OutputProfileCreateDTO.properties.max_extension_items` enforces `minimum: 1.0` and `maximum: 100.0`.
    5. `OutputProfileResponseDTO.properties.target_block_order.items` correctly references `#/components/schemas/TargetBlockType`.
  - Confirmed zero supply-chain violations (banned AI bloatware packages).
  - Executed OpenAPI unit tests (`test_generate_openapi.py` 2/2 passed) and full quality gate checks (ruff check, ruff format, mypy strict, Jinja validation, seed dry-run).
  - Emitted formal artifact: `@[red_team_audit_06_p0_openapi_sync_gate.md]`.
  - Committed tracker sign-off: `4b3add75 docs(epic-144): sign off Phase 0-F audit in tracker and advance resume command`.

- **Phase 0-G Implementation & Quality Gate Execution Completed (`[OK]`):**
  - Added `DisplayScale` enum to `@[client_app_v2/lib/core/models/enums.dart]` with `@JsonEnum()` and `@JsonValue` annotations matching Python `DisplayScale` SSOT character-for-character (`original`, `custom`, `normalized_100`).
  - Added 4 missing `TargetBlockType` enum members to `@[client_app_v2/lib/core/models/enums.dart]` (`matrix_graphs_block`, `matrix_summary_table_block`, `variance_validation_block`, `authenticity_evaluation_block`) bringing total member count to 13 matching Python SSOT.
  - Added `SystemUiConstraints` enum to `@[client_app_v2/lib/core/models/enums.dart]` centralizing systemic UI constraints (`maxExtensionItemsSliderMin(1)`, `maxExtensionItemsSliderMax(20)`, `maxExtensionItemsAbsoluteMax(100)`, `maxExtensionItemsDefault(3)`), eliminating magic numbers across widget trees.
  - Eradicated all `unknownEnumValue` fallback parameters from `@[client_app_v2/lib/features/studio/models/output_profile.dart]` (`OutputLayoutBlock.preset_view`, `OutputLayoutBlock.text_delivery_mode`, `SynthesisConfigDTO.historical_context_mode`) and `@[client_app_v2/lib/features/studio/models/blueprint_config.dart]` (`BlueprintConfig.preset_view`), restoring the Fail-Fast Client Firewall.
  - Purged legacy `includeDiagnosticScorecard` field and `@JsonKey(name: 'include_diagnostic_scorecard')` from `OutputProfile` Freezed model.
  - Strictly typed `displayScale` as `@Default(DisplayScale.original) @JsonKey(name: 'display_scale') DisplayScale displayScale`.
  - Strictly typed `targetBlockOrder` as `@JsonKey(name: 'target_block_order') @Default([...]) List<TargetBlockType> targetBlockOrder` with full 12-member Dart enum defaults.
  - Strictly typed `maxExtensionItems` as non-nullable `@Default(3) @JsonKey(name: 'max_extension_items') int maxExtensionItems`.
  - Executed Freezed code generator: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models --build` cleanly generated all `.freezed.dart` and `.g.dart` files (wrote 55 outputs, 0 analyzer issues).
  - Unskipped `test_display_scale_parity` and `test_target_block_type_parity` in `@[backend_v2/tests/unit/test_enum_parity.py]`.
  - Executed Universal Quality Gate on parity tests: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test` passing 13/13 tests green with 0 skipped and 98% coverage.
  - Executed Frontend Unit Test suite: `uv run python scripts/flutter_audit_loop.py client_app_v2/test --test` passing 95/95 tests green with 0 errors.
  - Verified all 8 Validation Gate assertions in Plan 07 with 100% compliance (zero `unknownEnumValue`, zero `includeDiagnosticScorecard`, 13 `TargetBlockType` members, clean builds).
- **Phase 0-H Implementation & Quality Gate Execution Completed (`[OK]`):**
  - Updated `@[client_app_v2/test/features/studio/models/output_profile_test.dart]` positive test fixtures with typed `DisplayScale` (`DisplayScale.original`, `DisplayScale.custom`) and `TargetBlockType` enums, with non-nullable `maxExtensionItems: 3`.
  - Implemented all 9 negative and positive test contracts in `output_profile_test.dart`:
    1. `test_output_layout_block_unknown_preset_view_throws`: unmapped `preset_view` string throws `CheckedFromJsonException`.
    2. `test_output_layout_block_unknown_text_delivery_mode_throws`: unmapped `text_delivery_mode` string throws `CheckedFromJsonException`.
    3. `test_synthesis_config_dto_unknown_historical_context_mode_throws`: unmapped `historical_context_mode` string throws `CheckedFromJsonException`.
    4. `test_output_profile_unknown_display_scale_throws`: unmapped `display_scale` string throws `CheckedFromJsonException`.
    5. `test_output_profile_unknown_target_block_type_throws`: unmapped `target_block_order` string throws `CheckedFromJsonException`.
    6. `test_output_profile_extra_root_key_throws`: unrecognized root key (`include_diagnostic_scorecard`) throws `CheckedFromJsonException` under `disallowUnrecognizedKeys: true`.
    7. `test_output_profile_extra_key_in_synthesis_config_throws`: extra key in nested `synthesis` object throws `CheckedFromJsonException`.
    8. `test_output_profile_extra_key_in_layout_throws`: extra key in nested `layouts[]` entry throws `CheckedFromJsonException`.
    9. `test_output_profile_valid_deserialization`: complete valid JSON with all required fields deserializes successfully into strongly typed Freezed models.
  - Created `@[client_app_v2/test/features/studio/models/blueprint_config_test.dart]` with all 3 specified test contracts:
    1. `test_blueprint_config_valid_preset_view`: valid preset view deserializes to `PresetView.metrics1d`.
    2. `test_blueprint_config_unknown_preset_view_throws`: unmapped `preset_view` string throws `CheckedFromJsonException`.
    3. `test_blueprint_config_extra_key_throws`: unrecognized key in `BlueprintConfig` throws `CheckedFromJsonException` under `disallowUnrecognizedKeys: true`.
  - Updated `@[client_app_v2/test/features/studio/controllers/output_profile_controller_test.dart]` mock fixtures with `DisplayScale.original`, `maxExtensionItems: 3`, and `HistoricalContextMode.disabled`, eliminating all legacy defaults.
  - Verified `@[client_app_v2/test/features/studio/views/widgets/profile/layout_editor_card_test.dart]` passes cleanly with typed `PresetView.matrixSummary` and `TextDeliveryMode.full`.
  - Executed Universal Quality Gate audits across all 4 target test suites via `flutter_audit_loop.py`:
    - `output_profile_test.dart`: format passed, analyze passed (0 issues), all tests passed.
    - `blueprint_config_test.dart`: format passed, analyze passed (0 issues), all tests passed.
    - `output_profile_controller_test.dart`: format passed, analyze passed (0 issues), all tests passed.
    - `layout_editor_card_test.dart`: format passed, analyze passed (0 issues), all tests passed.
  - Committed atomically: `d0944db3 test(studio): update frontend test fixtures and add negative deserialization tests and update tracker`.

- **Phase 0-H Post-Implementation Audit Signed Off (`[OK]`):**
  - Executed `/tier8-audit-plan` against `@[docs\epic\tasks_EPIC_144\08_p0_frontend_test_fixtures.md]`.
  - Verified 100% physical traceability for requirements R44–R48 across all 4 target test suites.
  - Confirmed all 9 negative and boundary test contracts in `@[client_app_v2/test/features/studio/models/output_profile_test.dart]` and 3 test contracts in `@[client_app_v2/test/features/studio/models/blueprint_config_test.dart]` throw `CheckedFromJsonException` on invalid enums and extra JSON keys.
  - Confirmed complete eradication of legacy `include_diagnostic_scorecard`, `includeDiagnosticScorecard`, and `unknownEnumValue` fallback assumptions across frontend test suites.
  - Confirmed zero supply-chain violations (banned AI bloatware packages in `pubspec.yaml`).
- **Phase 0-I Execution Completed (`[OK]`):**
  - **Full Backend Regression Audit:** Executed `uv run pytest backend_v2` with **1490 passed**, 30 skipped, 4 xpassed, **0 failures** across the entire backend suite.
  - **Integration Test Contract Alignment:** Resolved `TypeError` in `@[backend_v2/tests/integration/test_topological_evaluator.py]` by updating mock callback definitions to accept `(batch_nodes, current_states)` per the `TopologicalEvaluator.evaluate_graph` protocol contract.
  - **Universal Quality Gate Backend Audits:**
    - `@[backend_v2/tests/unit/test_enum_parity.py]`: 13/13 passed, 0 skipped, **98% statement coverage**, full compliance with AST and regex verification.
    - `@[backend_v2/scripts/generate_openapi.py]` / `@[backend_v2/tests/unit/scripts/test_generate_openapi.py]`: 4/4 passed, **97% statement coverage**, added comprehensive unit tests covering script success, file system error, `__main__` execution, and `__main__` exception handling.
    - Batch targets (`test_settings.py`, `test_v2_core_models.py`, `test_output_profile.py`, `test_output_profile_regression.py`, `test_synthesis_distiller_hook.py`, `test_blueprint.py`, `test_scoring.py`, `test_worker_synthesis.py`, `test_matrix_domain_parser.py`): 100% passed with strict >90% coverage on each target.
  - **Frontend Studio Model Code Generation & Analysis:** `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models --build` produced clean Freezed/Riverpod serialization code with **0 analyzer issues**.
  - **Frontend Unit Test Suite:** `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/models --test` passed **107/107 tests green**.
  - **Deterministic Cross-Stack Parity Verification:**
    1. Zero occurrences of `include_diagnostic_scorecard` or `includeDiagnosticScorecard` across `backend_v2/models/`, `backend_v2/services/`, `backend_v2/seed/`, and `client_app_v2/lib/`.
    2. Zero occurrences of `unknownEnumValue` across entire `client_app_v2/lib/`.
    3. Python cross-language enum parity tests in `test_enum_parity.py` pass 13/13 with 0 skips.
    4. Static OpenAPI schema in `docs/swagger/openapi.json` contains `DisplayScale` enum (3 members), `TargetBlockType` enum (13 members), and zero references to legacy `include_diagnostic_scorecard`.
  - **Atomic Commit:** `478679ff feat(epic-144): execute Phase 0-I integration checkpoint and verify cross-stack parity`.
- **Phase 0-I Post-Implementation Audit Signed Off (`[OK]`):**
  - Executed `/tier8-audit-plan` against `@[docs\epic\tasks_EPIC_144\09_p0_integration_checkpoint.md]`.
  - Verified 100% physical traceability for requirements R49–R51 across backend, frontend, and OpenAPI schemas.
  - Verified full backend regression test suite (`1492 passed`, 30 skipped, 4 xpassed, `0 failures`).
  - Confirmed Freezed model generation and static analysis produce `0 analyzer issues` via `flutter_audit_loop.py`.
  - Confirmed frontend unit test suite passes `107/107 tests green` via `flutter_audit_loop.py`.
  - Confirmed cross-language enum parity test passes `13/13 active tests with 0 skips` (98% coverage).
  - Confirmed zero occurrences of legacy `include_diagnostic_scorecard` across models, DTOs, seed data, and frontend `lib/`.
  - Confirmed zero occurrences of `unknownEnumValue` across frontend `lib/`.
  - Confirmed zero supply-chain violations (banned AI bloatware packages in `pyproject.toml` and `pubspec.yaml`).
  - Confirmed 100% Epic boundary fidelity via `audit_planner_output.py`.
  - Emitted formal artifact: `@[red_team_audit_09_p0_integration_checkpoint.md]`.

- **Phase 1-A Red-Teaming & Falsification Passed (`[OK]`):**
  - Completed System 2 Red-Teaming on `@[docs\epic\tasks_EPIC_144\10_p1_golden_master_baseline.md]`.
  - Audited monolithic `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` (897 lines) and verified all Riverpod providers and Hook states.
  - Enriched `<test_contracts>` with 10 explicit positive and negative test cases covering `AsyncLoading`, `AsyncError`, wide-screen 3-pane `Row` layout (1920x1080), narrow-screen `ListView` layout (800x600), identity and scoring fields, workflow selector and XAI extensions, empty workflow warning state, max extension items integer validation, and save failure exception handling.
  - Enforced full compliance with `anti_happy_path_mandate` and `remedial_refactoring_coverage` (`@[ki_god_code_prevention.md]`).
  - Mutated Plan 10 and re-verified 100% boundary fidelity via `audit_planner_output.py`.

- **Phase 1-A Execution Passed (`[OK]`):**
  - **Golden Master Characterization Suite Established:** Implemented `@[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart]` with 10 comprehensive widget test contracts locking down form state, error handling, layout responsiveness, and submission flows:
    1. `test_crud_view_renders_loading_state`: verified `AsyncLoading` displays `CircularProgressIndicator` inside AppBar body.
    2. `test_crud_view_renders_error_state`: verified `AsyncError` renders `ErrorView` with `AppException` diagnostics without UI crashes.
    3. `test_crud_view_renders_data_state_wide_screen`: verified wide-screen viewport (1920x1080) renders 3-pane `Row` layout (`buildIdentityPane`, `buildLayoutPane`, `buildTargetBlockOrderPane`) without overflow or rendering assertion errors.
    4. `test_crud_view_renders_data_state_narrow_screen`: verified compact viewport (800x600) renders single-column `ListView` layout without overflow.
    5. `test_crud_view_displays_identity_and_scoring_fields`: verified text fields for ID, slug, display name, strictness level dropdown (`StrictnessLevel.balanced.value` = 50), and scoring strategy dropdown (`ScoringStrategy.waterfall`).
    6. `test_crud_view_displays_workflow_selector_and_extensions`: verified workflow selector dropdown and XAI extension checkboxes (`Source Citation`, `Justification`).
    7. `test_crud_view_displays_workflow_warning_when_unselected`: verified unselected workflow (`workflowId: ''`) displays localized `workflowSelectWarning` in Layout pane.
    8. `test_crud_view_validates_max_extension_items`: verified invalid string/negative inputs (`-5`) fail form validation with localized `extensionItemsMustBeIntError` ("Given value must be an integer >= 1").
    9. `test_crud_view_triggers_save_action`: verified tapping `Save Changes` button invokes `outputProfileFormProvider` notifier `.submit()` with updated payload.
    10. `test_crud_view_handles_save_failure_gracefully`: verified `AppException.validation` error during submission triggers error `SnackBar` via `ScaffoldMessenger` without widget tree unmounting or unhandled exceptions.
  - **Type Synchronization in Legacy View:** Surgically adapted `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` to strongly typed `DisplayScale` enum in `DropdownButton<DisplayScale>` (L368–L403) and `TargetBlockType` enum in `ReorderableListView` (L776–L791) introduced in Phase 0-G.
  - **Quality Gate Audit Passed:** Executed `flutter_audit_loop.py` on the test suite: **All 117 tests passed green with 0 errors**.
  - **Committed Atomically:** `feat(studio): establish phase 1-a golden master characterization tests for output profile crud view`.

- **Phase 1-A Post-Implementation Audit Signed Off (`[OK]`):**
  - Executed `/tier8-audit-plan` against `@[docs\epic\tasks_EPIC_144\10_p1_golden_master_baseline.md]`.
  - Verified 100% physical traceability for requirement R52 and all 10 Golden Master characterization test contracts.
  - Confirmed `@[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart]` (578 lines) comprehensively tests loading (`CircularProgressIndicator`), error (`ErrorView`), wide-screen (3-pane Row layout at 1920x1080), narrow-screen (single-column ListView layout at 800x600), identity and scoring fields, workflow selector and XAI extensions, empty workflow warning state, max extension items integer validation, form submission, and submission failure `SnackBar` handling.
  - **E2E Static Analysis Remediation across Studio Views:** Resolved analyzer errors in `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart]` by strongly typing `DropdownButton<DisplayScale>` with `DisplayScale` enum members and binding `Slider` bounds to `SystemUiConstraints` enum (`maxExtensionItemsSliderMin`/`maxExtensionItemsSliderMax`), eliminating all magic numbers and invalid null-aware operators.
  - Confirmed zero supply-chain violations (banned AI bloatware packages in `pubspec.yaml`).
  - Executed global quality gates (`flutter_audit_loop.py`): build runner clean (55 outputs), **0 analyzer issues**, full frontend test suite passing **117/117 tests green**.
  - Emitted formal artifact: `@[red_team_audit_10_p1_golden_master_baseline.md]`.

## Learned
- **Codebase Baseline & Violation Topology:** The codebase currently has a monolithic 856-line `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` with 15 identified architectural violations (V1–V15).
- **Fail-Fast Hydration Invariant:** The `OutputProfile` model currently contains legacy `include_diagnostic_scorecard: bool`, uses raw `Literal["original", "custom", "normalized_100"]` for `display_scale`, and `list[str]` for `target_block_order`. Flutter models utilize `unknownEnumValue` fallback annotations.
- **Atomic 6-Step Execution Protocol:** To prevent fatal `pydantic.ValidationError(extra_forbidden)` crashes under `ConfigDict(strict=True, extra="forbid")`, modifications MUST execute in strict order: Seed Sanitization & Local Reseed (02) → Models & DTO Purge (03) → OpenAPI Sync (06) → Frontend Enums & Freezed (07) → UI Decomposition (10-11) → Quality Gates.
- **Seed Vault Protocol Invariants:** When auditing or modifying `seed_data.json`, CRLF encoding causes `grep_search` to silently fail; deterministic Python scripts using `json.load` and bounded reads are mandatory. Pre-mutation backups in `backend_v2/seed/backups/` are strictly required before any JSON modifications.
- **Testing Architecture Consolidation:** Architectural tests in `tests/architecture/` must be transitioned to the standard test pyramid (`tests/unit/`) to maintain single test suite sovereignty without duplicate scanners.
- **Dynamic File Path SSOT in Tests:** In test fixtures accessing seed files, hardcoded Windows absolute paths (e.g., `c:\src\quorum\...`) must be replaced with `Path(__file__).resolve().parents[N]` to prevent cross-machine amnesia.
- **Settings Post-Init Credential Scanning:** Testing `Settings.model_post_init` credential checks requires mocking `Path.exists` because `Settings` automatically scans the filesystem root for `service-account.json`.
- **Enum Parity Testing Paradigm:** Python `ast.parse` and regex extraction over Dart `@JsonValue` provide deterministic verification without importing heavy cross-stack runtimes.
- **DTO Optionality vs Domain Strictness:** When creating DTOs for REST APIs, fields that have sensible defaults in the domain model (e.g. `target_block_order`) should remain optional (`| None = None`) in `CreateDTO`/`UpdateDTO` to prevent forced over-specification by API clients, while remaining strictly typed non-nullable enums in `ResponseDTO` and the domain model.
- **Test Fixture Ripple Effects on Enum Migration:** Migrating `target_block_order` from `list[str]` to `list[TargetBlockType]` causes legacy test fixtures passing raw strings like `["metadata_block", ...]` to fail under strict Pydantic V2 validation; these fixtures are scheduled for comprehensive alignment in Phase 0-D (Plan 04).
- **Strict DTO Validation on Enum Collections:** In Pydantic V2 models configured with `strict=True` (e.g., `OutputProfileResponseDTO`), lists of StrEnums (`list[TargetBlockType]`) strictly reject raw string inputs (`str`) during `.model_validate(payload)`. Test fixtures for strict DTOs MUST construct payloads using native Enum instances (`TargetBlockType.METADATA_BLOCK`), whereas domain models utilizing lax aliases (`LaxTargetBlockType` with `Field(strict=False)`) permit string coercion during database hydration.
- **Pydantic V2 Instantiation vs Field Defaults in Mypy:** In strict Mypy environments, instantiating Pydantic DTOs via constructor kwargs (`OutputProfileUpdateDTO(slug="...")`) flags missing arguments if fields declare `Field(default=None)` without `= None` at the Python class attribute syntax level. Instantiating via `.model_validate({"slug": "..."})` guarantees full runtime validation and static type checking compatibility without mutating domain class definitions.
- **Async Hook Testing & Awaitable Typing:** In pytest-asyncio test suites, calling async hook functions returning `HookResult | Awaitable[HookResult]` requires wrapping calls in `cast(Awaitable[HookResult], ...)` when awaiting under MyPy `--strict` mode to prevent type union awaitability errors.
- **DisplayScale Enum Isolation in Domain Parsers:** `MatrixDomainParser` tests must explicitly test all 3 `DisplayScale` enum options (`ORIGINAL`, `NORMALIZED_100`, `CUSTOM`) to verify mathematical score scaling and bound definitions (`display_scale_min`/`display_scale_max`), as well as Fail-Fast validation on missing custom bounds.
- **Blueprint Dispatch Loop Block Order Contract:** In test fixtures instantiating `OutputProfile` or `OutputProfile.model_construct` for `BlueprintTransformer`, `target_block_order` must be populated with `_DEFAULT_TARGET_BLOCK_ORDER` to ensure downstream SDUI blocks (`GROUPED_EXTENSIONS_BLOCK`, `AUTHENTICITY_EVALUATION_BLOCK`, etc.) are dispatched during report synthesis.
- **OpenAPI Schema Generation & Standalone Script Testing:** `backend_v2/scripts/generate_openapi.py` safely writes to `docs/swagger/openapi.json` without side effects. Standalone scripts that execute outside the `backend_v2` module structure should have their unit tests verified directly with `pytest` alongside the standard linting and typing quality gates.
- **OpenAPI Schema Dynamic Enum Exposure:** Regenerating OpenAPI via `generate_openapi.py` captures newly added domain enums (`DisplayScale`, `TargetBlockType`) directly into `components/schemas` and updates collection items references (`#/components/schemas/TargetBlockType`), ensuring downstream Dart/TypeScript client generators remain strictly synchronized with Pydantic V2 backend models.
- **Freezed Model Default Enum Value Parity:** When migrating a Freezed field from `List<String>` to `List<TargetBlockType>`, `@Default(...)` expressions must simultaneously be converted from string literals to native Dart enum values to avoid compile-time type assignment failures.
- **Frontend Systemic Constants Centralization:** All UI boundary constraints (e.g. `maxExtensionItems` slider bounds 1-20, absolute max 100, default 3) MUST be centralized in `SystemUiConstraints` enum in `enums.dart` to prevent magic numbers across widget trees.
- **Fail-Fast Client Firewall vs Fallbacks:** Eradicating `unknownEnumValue` fallback parameters from Freezed models forces unrecognized server payloads to throw `CheckedFromJsonException` caught by `AppErrorBoundary` instead of silently coercing to defaults.
- **CheckedFromJsonException Assertion on Freezed Models:** In Flutter unit tests testing Fail-Fast deserialization on Freezed models with `disallowUnrecognizedKeys: true` and strict enums, invalid or unmapped values throw `CheckedFromJsonException` rather than `FormatException` or silent nulls.
- **Cross-Stack Integration Scope Isolation:** Phase 0 integration gates must validate the domain boundaries modified during Phase 0 (`lib/features/studio/models/`) while reserving un-decomposed view structures (`output_profile_crud_view.dart`) for Phase 1 decomposition to prevent cross-phase test collision.
- **Topological Evaluator Callback Contract Parity:** `TopologicalEvaluator.evaluate_graph` passes `(pending_nodes, states)` to its `batch_evaluation_callback`. Mock callbacks in integration tests must accept `current_states: dict[str, AtomExecutionState]` to avoid `TypeError` when evaluating waves.
- **Standalone Script Coverage Testing in Isolation:** When running `backend_audit_loop.py` on standalone helper scripts (e.g., `generate_openapi.py`), test suites must exercise both top-level execution functions and the `if __name__ == '__main__':` entrypoint to meet the strict 90% coverage threshold without relying on side effects.
- **Characterization Testing for Legacy God Widgets:** Establishing a Golden Master widget test before refactoring monolithic UI files requires mocking the entire Riverpod provider tree (including `outputProfileFormProvider`, `studioClientProvider`, `loggerServiceProvider`, and related lookup providers) and testing both happy path rendering and error boundary handling.
- **Riverpod Family Provider Overrides in Widget Tests:** When overriding Riverpod family providers in widget tests (such as `workflowAvailableExtensionsProvider(currentWorkflowId)`), argument matchers like `any()` are invalid and cause runtime `ArgumentError`; explicit parameter bindings (e.g., `workflowAvailableExtensionsProvider('wf_test')` and `workflowAvailableExtensionsProvider('')`) are required.
- **LayoutBuilder Constraints in Widget Testing:** In Flutter widget testing of responsive layouts with `LayoutBuilder`, `MediaQueryData(size: ...)` alone does not constrain the physical canvas; setting `tester.view.physicalSize = const Size(1920, 1080)` and `tester.view.devicePixelRatio = 1.0` with `addTearDown` cleanup is required to properly trigger wide-screen branches (e.g., 3-pane `Row` vs `ListView`).
- **DotEnv Initialization in Widget Tests:** Notifier callbacks that call `ref.read(loggerServiceProvider)` trigger logger initialization which accesses `DotEnv.env`. Mocking `loggerServiceProvider.overrideWithValue(mockLogger)` in `ProviderScope.overrides` isolates widget tests from global environment variables.
- **Global Studio View Parity on Freezed Migrations:** When migrating a Freezed model field from nullable `int?` to non-nullable `int` or from `String` to `Enum`, all legacy views consuming that model (e.g., `profile_editor_view.dart` as well as `output_profile_crud_view.dart`) must have their dropdown values and slider bounds synchronized with `SystemUiConstraints` to prevent Dart analyzer compilation errors during global `--build` audits.

## Remaining
- **Phase 1-B (Plan 11):** 3-tab scaffold decomposition (`output_profile_crud_view.dart` decomposed into ≤200-line shell + 3 tabs: `profile_general_tab.dart`, `profile_scoring_tab.dart`, `profile_layouts_tab.dart`).
- **Phases 2-5 Detailed Planning (Plans 12-15):** Generate executable plans via `/tier0-create-plan` and execute Phases 2-5.
- **Post-Implementation Gates:** Golden Master restoration audit, Proxy sunset, Tier 2 Hardening Backend & Frontend, Pre-delete audit, Semantic coverage (>90%), and Live E2E verification (`test_integration_real_llm.py`).
- **Knowledge Item & Architecture Sync:** Create KIs for new SSOTs and execute `/tier7-describe-architecture` and `/tier8-audit-epic`.

## Resume Command
```bash
/tier0-research-plan @[docs\epic\tasks_EPIC_144\11_p1_tab_scaffold_decomposition.md] @[docs\epic\EPIC_144_tracker.md]
```
