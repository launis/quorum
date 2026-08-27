<!--
  EPIC 148 TRACKING DOCUMENT
  Standardized multi-phase Epic tracking document generated from implementation plans.
  Source Epic: @[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md]
  Task Directory: @[docs/epic/tasks_EPIC_148/]
-->

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_error_handling_and_fail_fast_rfc7807.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
</required_context_rules>

# EPIC 148 Tracker: Domain Model SSOT & Presentation Localization Modernization

## Phase Execution Status

### Phase 1: Theory Grounding & Epistemic Anchor Sanitization
**Plan:** @[docs/epic/tasks_EPIC_148/01_phase1_theory_grounding_and_epistemic_anchor_sanitization.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_148/01_phase1_theory_grounding_and_epistemic_anchor_sanitization.md] @[docs/epic/EPIC_148_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_148/01_phase1_theory_grounding_and_epistemic_anchor_sanitization.md] @[docs/epic/EPIC_148_tracker.md]`
  - [x] Step 1: Pre-Implementation Technical Debt Sweeps & AST Guardrail Extension
  - [x] Step 2: Backup Seed Vault (vault_mutation_protocol)
  - [x] Step 3: Deterministic Seed Vault Sanitization across all 13 Matrix Blocks
  - [x] Step 4: Format Pure <theory_context> in MatrixSensorPromptBuilder via Direct TemplateProcessor Assembly
  - [x] Step 5: Unit Tests for Theory Grounding Prompt Builder
- [x] **[OK] Test Coverage Assertions:** Verified 100% statement coverage on `matrix_sensor_prompt_builder.py` and 92% on `_ast_guardrails.py`.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_148/01_phase1_theory_grounding_and_epistemic_anchor_sanitization.md] @[docs/epic/EPIC_148_tracker.md]`

---

### Phase 2: ATOMIC I18nText Modernization & Systemic Fixture Migration
**Plan:** @[docs/epic/tasks_EPIC_148/02_phase2_atomic_i18n_text_modernization_and_systemic_fixture_migration.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_148/02_phase2_atomic_i18n_text_modernization_and_systemic_fixture_migration.md] @[docs/epic/EPIC_148_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_148/02_phase2_atomic_i18n_text_modernization_and_systemic_fixture_migration.md] @[docs/epic/EPIC_148_tracker.md]`
  - [x] Step 1: Python Domain Model Modernization in v2_core.py & WarningCardAdapter Migration
  - [x] Step 2: Flutter Freezed Model Update, 1-Hop Widget Cleanups & Unit Tests
  - [x] Step 3: Deterministic Pruning of default_locale in seed_data.json & 100% Bilingual Seeding
  - [x] Step 4: Deterministic Bulk Migration of Test Fixtures via Scratch Scripts
  - [x] Step 5: Re-seed Database & Atomic Quality Gate Verification
- [x] **[OK] Test Coverage Assertions:** Verified 100% statement coverage on `warning_card_adapter.py`, `sdui.py`, `core_base.py`, and `matrix_scorecard.py`. All 2,153 Python tests and 225 Flutter tests passing.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_148/02_phase2_atomic_i18n_text_modernization_and_systemic_fixture_migration.md] @[docs/epic/EPIC_148_tracker.md]`

---

### Phase 3: ATOMIC OutputProfile, SDUI Dumb Painter & Localization Parity
**Plan:** @[docs/epic/tasks_EPIC_148/03_placeholder_phase3_output_profile_sdui_dumb_painter_and_localization_parity.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_148/03_placeholder_phase3_output_profile_sdui_dumb_painter_and_localization_parity.md] @[docs/epic/EPIC_148_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_148/03_placeholder_phase3_output_profile_sdui_dumb_painter_and_localization_parity.md] @[docs/epic/EPIC_148_tracker.md]`
  - [x] (292a2859) Step 1: Pre-Implementation Technical Debt Cleanups & Static Translation Tables
  - [x] (a548f83b) Step 2: Python Domain Model & DTO Modernization (v2_core.py & output_profile.py)
  - [x] (850ca821) Step 3: Flutter Freezed Model Update (output_profile.dart) & Studio UI Cleanups
  - [x] (f162d4e6) Step 4: SDUI Presentation Adapters, Worker & Jinja2 PDF Template (Dumb Painters)
  - [x] Step 5: Seed Vault OutputProfile Migration, Test Fixture Updates & Universal Quality Gate Verification
- [x] **[OK] Test Coverage Assertions:** Verified 100% statement coverage across all 6 presentation adapters, 0 legacy dictionaries in seed_data.json, 100% l10n parity in en.json/fi.json, and full pass across 2,135 backend unit tests and 224 Flutter tests.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_148/03_placeholder_phase3_output_profile_sdui_dumb_painter_and_localization_parity.md] @[docs/epic/EPIC_148_tracker.md]`

---

### Phase 4: AST Guardrails, Parity Suites & Final Audit
**Plan:** @[docs/epic/tasks_EPIC_148/04_placeholder_phase4_ast_guardrails_parity_suites_and_final_audit.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_148/04_placeholder_phase4_ast_guardrails_parity_suites_and_final_audit.md] @[docs/epic/EPIC_148_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_148/04_placeholder_phase4_ast_guardrails_parity_suites_and_final_audit.md] @[docs/epic/EPIC_148_tracker.md]`
  - [x] Step 1: Pre-Implementation Sweep & AST Guardrails (Theory Grounding & Seed Vault)
  - [x] Step 2: Backend Internal Localization Parity Suite
  - [x] Step 3: SDUI Golden Master Test Fixture (All 17 AnySduiBlock Types)
  - [x] Step 4: SDUI Template Presentation Parity & Fail-Fast Suite (Backend)
  - [x] Step 5: Flutter SDUI Golden Master Parity Widget Test & Universal Quality Gate
- [x] **[OK] Test Coverage Assertions:** Verified 100% bilingual parity across all 458 I18nText seed records, 100% symmetry across backend en.json/fi.json with 0 dead unreferenced keys, 17/17 AnySduiBlock types verified across AST, Jinja template, and Dart renderer, and both backend (2,164 tests, 90% coverage) and Flutter (234 tests) audit loops completely passing.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_148/04_placeholder_phase4_ast_guardrails_parity_suites_and_final_audit.md] @[docs/epic/EPIC_148_tracker.md]`

---

### Integration Checkpoint: Full-Stack Validation
- [x] **[OK] Backend Parity & Quality Loop**: Full execution of `uv run python scripts/backend_audit_loop.py backend_v2 --test` passing Ruff, MyPy, and Pytest coverage gates (>90%).
- [x] **[OK] Flutter Client Build & Unit Suite**: Full execution of `uv run python scripts/flutter_audit_loop.py client_app_v2 --test` passing formatting, analysis, and all 234 widget/unit tests.
- [x] **[OK] Cross-Platform Presentation Parity**: Automated verification of SDUI Golden Master rendering across Jinja PDF DOM and Flutter widget tree across all 17 `AnySduiBlock` types.

---

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies (specifically `OutputLayoutBlock` and legacy `layouts` callers).
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` on modified backend files:
  - [ ] @[backend_v2/l10n/en.json]
  - [ ] @[backend_v2/l10n/fi.json]
  - [x] @[backend_v2/models/core_base.py]
  - [x] @[backend_v2/models/dtos/matrix_scorecard.py]
  - [x] @[backend_v2/models/dtos/output_profile.py]
  - [x] @[backend_v2/models/state.py]
  - [x] @[backend_v2/models/v2_core.py]
  - [ ] @[backend_v2/seed/seed_data.json]
  - [ ] @[backend_v2/services/localization.py]
  - [ ] @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]
  - [ ] @[backend_v2/services/pdf_generator.py]
  - [ ] @[backend_v2/services/sdui/adapters/authenticity_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/executive_summary_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/metadata_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/variance_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/warning_card_adapter.py]
  - [ ] @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]
  - [ ] @[backend_v2/templates/report_template.jinja2]
  - [ ] @[backend_v2/worker.py]
  - [ ] @[scripts/_ast_guardrails.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` on modified Flutter files:
  - [ ] @[client_app_v2/lib/features/execution/views/execution_report_view.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/output_profile.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/profile_editor_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]
  - [ ] @[client_app_v2/lib/l10n/app_en.arb]
  - [ ] @[client_app_v2/lib/l10n/app_fi.arb]
  - [ ] @[client_app_v2/lib/shared/models/i18n_text.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/specialist_section.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies or unreferenced symbols remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.

---

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, create/update relevant Knowledge Items (KIs), and update `.agents/rules/04_directory_reference.md`.

---

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

---

## Instructions for the Execution Agent
1. **Atomic Commit Mandate**: After ANY successful run of the `universal_quality_gate` audit script that passes, you MUST explicitly instruct the user to perform an atomic `git commit` BEFORE proceeding to the next file or logic block. Specify exact relative file paths. Git commit messages MUST ALWAYS be written in English.
2. **Clean Slate Seeding Mandate**: When database seeds or models are modified, re-seed the local environment using `uv run python backend_v2/seed/run_seed.py local`.
3. **Workspace Relative Syntax**: All file references MUST use `@-reference` syntax (specifically: `@[backend_v2/models/v2_core.py]`).
4. **Workflow Execution Pipeline**: You MUST update the `/tier5-resume` or `/tier0-research-plan` (or `/tier0-create-plan` if the plan is missing) command at the bottom of this tracker before handing over the session. Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue. The mandatory workflow loop is: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute -> /tier8-audit-plan`. You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands. Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`. Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating.

---

## Requirements Traceability Matrix

| Req ID | Epic Source Section | Description | Plan & Step Mapping | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-TG-01** | §1.1.1, §3.2.1, §5.1 | Sanitize all 13 matrix blocks in `seed_data.json` by removing duplicate `EPISTEMIC ANCHOR:` tails; preserve qualitative prompt coaching texts verbatim | Phase 1, Step 3 | Completed |
| **REQ-TG-02** | §1.1.1, §3.2.2, §5.1 | Eradicate `_create_ephemeral_block` helper and fake IDs (`blk_1111...`, `blk_2222...`) in `MatrixSensorPromptBuilder` | Phase 1, Step 4 | Completed |
| **REQ-TG-03** | §1.1.1, §3.2.3, §5.1 | Format pure `<theory_context>` and `<matrix_objective>` XML blocks via direct `TemplateProcessor.safe_interpolate()` CDATA Breakout Shielding | Phase 1, Step 4 | Completed |
| **REQ-TG-04** | §1.1.1, §3.2.3, §5.1 | Omit raw `source_url` from LLM prompt payloads to prevent token bloat while retaining it in `TheoryGrounding` DTO for UI/PDF presentation | Phase 1, Step 4 | Completed |
| **REQ-TG-05** | §3.1.4, §3.2.25 | Extend rule `QGR001` in `scripts/_ast_guardrails.py` to ban `setattr(...)` and `object.__setattr__(...)` in-place model mutations | Phase 1, Step 1 | Completed |
| **REQ-TG-06** | §3.1.4, §3.2.25 | Update `.agents/rules/01-python-backend.md` (`frozen_state_mutability`) to lock architectural ban against frozen model in-place mutations | Phase 1, Step 1 | Completed |
| **REQ-TG-07** | §5.1.4 | Backup seed vault to `backend_v2/seed/backups/seed_data_pre_epic148_cleanup.json` prior to any surgical edits | Phase 1, Step 2 | Completed |
| **REQ-TG-08** | §5.1.4, §6 (TC-TG-01..06) | Unit tests in `test_matrix_sensor_prompt_builder.py` verifying pure CDATA theory formatting and XML injection protection | Phase 1, Step 5 | Completed |
| **REQ-I18N-01** | §1.1.2, §3.2.4, §5.2.1 | Remove `default_locale` from `I18nText` in `backend_v2/models/core_base.py`; enforce required `translations: Annotated[dict[str, str], Field(...)]` without `default_factory=dict` | Phase 2, Step 1 | Completed |
| **REQ-I18N-02** | §3.1.1, §3.2.15, §5.2.1 | Implement `@field_validator("translations")` classmethod in `I18nText` for key sanitization and non-empty baseline `'en'` check without `object.__setattr__` frozen mutations | Phase 2, Step 1 | Completed |
| **REQ-I18N-03** | §3.1.1, §3.2.15, §5.2.1 | Refactor `I18nText.resolve()` to enforce Fail-Fast validation using regex locale parsing and explicit dictionary membership assertions (`in`) instead of `.get()` duck-typing | Phase 2, Step 1 | Completed |
| **REQ-I18N-04** | §3.1.2, §3.2.17, §5.2.1 | Synchronous module-level constant migration in `warning_card_adapter.py` to eliminate `I18N_WARNING_STARVATION` and resolve dynamically via `LocalizationService` | Phase 2, Step 1 | Completed |
| **REQ-I18N-05** | §1.1.2, §3.2.9, §5.2.2 | Update `I18nText` Freezed model in `i18n_text.dart` with explicit `@JsonSerializable(disallowUnrecognizedKeys: true)`, remove `defaultLocale`, enforce required `translations` without `@Default` | Phase 2, Step 2 | Completed |
| **REQ-I18N-06** | §3.2.13, §5.2.2 | Add `isEmpty`, `isNotEmpty`, `has(langCode)` helpers and Fail-Fast `get(langCode)` throwing `AppException.validation` in `i18n_text.dart` | Phase 2, Step 2 | Completed |
| **REQ-I18N-07** | §3.1.1, §3.2.13, §5.2.2 | Remove redundant `locale == 'fi' ? get('fi') : get('en')` ternaries in `atom_matrix_table_widget.dart` and `matrix_row_item_widget.dart` | Phase 2, Step 2 | Completed |
| **REQ-I18N-08** | §1.2.6, §3.1.3, §3.2.22, §5.2.2 | Migrate hardcoded execution-tier strings to `AppLocalizations` in `human_override_dialog.dart`, `execution_report_view.dart`, and `specialist_section.dart` | Phase 2, Step 2 | Completed |
| **REQ-I18N-09** | §3.1.3, §3.2.22, §5.2.2 | Populate execution-tier localization keys in `client_app_v2/lib/l10n/app_en.arb` and `app_fi.arb` | Phase 2, Step 2 | Completed |
| **REQ-I18N-10** | §3.1.3, §3.2.13, §5.2.2 | Modernize Studio widgets: `i18n_text_field.dart` (bind translations), `output_profile_controller.dart` (use SSOT `isEmpty`), `profile_editor_view.dart` (primary theme color & `AppException`), `xai_evidence_box.dart` (`TextOverflow.ellipsis`) | Phase 2, Step 2 | Completed |
| **REQ-I18N-11** | §5.2.2, §6 (TC-I18N-FLUTTER-01..07) | Create unit test suite `client_app_v2/test/shared/models/i18n_text_test.dart` asserting Fail-Fast validation, fallback resolution, and negative ISTQB partition rejection of `default_locale` | Phase 2, Step 2 | Completed |
| **REQ-I18N-12** | §1.1.2, §3.2.4, §3.2.21, §5.2.3 | Prune 500 instances of `"default_locale"` in `seed_data.json` via scratch script and populate 4 authentic Finnish translations for `prompt_blocks[88]` and `prompt_blocks[89]` | Phase 2, Step 3 | Completed |
| **REQ-I18N-13** | §3.2.10, §5.2.4 | Deterministic bulk migration of 1,166 backend test fixture references across 90 test files in `backend_v2/tests/` via `scratch/migrate_backend_i18n_fixtures.py` | Phase 2, Step 4 | Completed |
| **REQ-I18N-14** | §3.2.10, §5.2.4 | Deterministic bulk migration of 157 Flutter test references across 25 files in `client_app_v2/test/` via `scratch/migrate_flutter_i18n_fixtures.py` | Phase 2, Step 4 | Completed |
| **REQ-I18N-15** | §5.2.5 | Re-seed local development database (`uv run python backend_v2/seed/run_seed.py local`) and verify Phase 2 quality gates | Phase 2, Step 5 | Completed |
| **REQ-PROF-01** | §1.1.3, §3.2.5, §5.3.1 | Populate complete backend static translation tables in `backend_v2/l10n/en.json` and `fi.json` for all 17 metric mapping keys, user roles, matrix columns, extension labels, and template labels | Phase 3, Step 1 | Completed |
| **REQ-PROF-02** | §5.3.1 | Extend `LocalizationService` in `backend_v2/services/localization.py` with type-safe formatting helpers (`format_date`, `format_decimal`, `format_score`, `format_percent`, `format_cost`) | Phase 3, Step 1 | Completed |
| **REQ-PROF-03** | §1.1.3, §3.2.7, §3.2.24, §5.3.2 | Declare `MatrixSynthesisGroup` domain model in `v2_core.py` with `min_length=1` target blocks and add `matrix_synthesis_groups` with contextual validator to `OutputProfile` | Phase 3, Step 2 | Completed |
| **REQ-PROF-04** | §1.1.3, §3.2.5, §3.2.23, §5.3.2 | Prune `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts` from `OutputProfile` and completely eradicate `OutputLayoutBlock` class across Python and Flutter | Phase 3, Step 2 | Completed |
| **REQ-PROF-05** | §3.2.23, §5.3.2 | Retire AST parity checks (`test_preset_view_parity`, `test_text_delivery_mode_parity`) in `test_enum_parity.py` targeting deleted `OutputLayoutBlock` | Phase 3, Step 2 | Completed |
| **REQ-PROF-06** | §5.3.2 | Update `OutputProfile` DTOs in `backend_v2/models/dtos/output_profile.py` to replace `layouts` with `matrix_synthesis_groups` | Phase 3, Step 2 | Completed |
| **REQ-PROF-07** | §5.3.2 | Declare `MatrixSynthesisGroup` Freezed model with explicit `@JsonSerializable(disallowUnrecognizedKeys: true)` and update `OutputProfile` in `client_app_v2/lib/features/studio/models/output_profile.dart` | Phase 3, Step 3 | Completed |
| **REQ-PROF-08** | §5.3.2, §6 (TC-PROFILE-FLUTTER-01..03) | Update `client_app_v2/test/features/studio/models/output_profile_test.dart` with negative ISTQB tests asserting legacy keys (`layouts`, `metric_mappings`, `preset_view`) throw `CheckedFromJsonException` | Phase 3, Step 3 | Completed |
| **REQ-PROF-09** | §3.1.2, §3.2.6, §3.2.16, §5.3.3 | Refactor SDUI adapters (`metadata_adapter.py`, `variance_adapter.py`, `authenticity_adapter.py`, `executive_summary_adapter.py`, `matrix_graphs_adapter.py`, `matrix_summary_table_adapter.py`, `printable_sources_adapter.py`, `xai_highlights_adapter.py`) to consume `LocalizationService` and `matrix_synthesis_groups` as pre-localized Dumb Painters | Phase 3, Step 4 | Completed |
| **REQ-PROF-10** | §1.2.5, §3.2.18, §5.3.3 | Sanitize `report_template.jinja2` and `PdfReportService`: lock `StrictUndefined`, register `raise_unrecognized_sdui_block`, update footer pagination (`1 / 5`), purge hardcoded Finnish/English strings, purge all 11 fallback ternaries `if l10n is defined else '...'` | Phase 3, Step 4 | Completed |
| **REQ-PROF-11** | §3.2.8, §5.3.3 | Update background worker in `backend_v2/worker.py` and Flutter studio layouts tab in `profile_layouts_tab.dart` to iterate over `matrix_synthesis_groups` | Phase 3, Step 4 | Completed |
| **REQ-PROF-12** | §5.3.4 | Migrate `OutputProfile` records in `seed_data.json#L9180-L9570` to `matrix_synthesis_groups` and remove legacy dictionaries | Phase 3, Step 5 | Completed |
| **REQ-PROF-13** | §5.3.4 | Update test fixtures in `backend_v2/tests/` that mock `OutputProfile` or instantiate `OutputLayoutBlock` | Phase 3, Step 5 | Completed |
| **REQ-PROF-14** | §5.3.5 | Re-seed local development database (`uv run python backend_v2/seed/run_seed.py local`) and verify Phase 3 quality gates | Phase 3, Step 5 | Completed |
| **REQ-GRD-01** | §3.2.11, §5.4.1 | Create AST guardrail suite `test_ast_theory_grounding_guardrails.py` asserting 0 matrices have `EPISTEMIC ANCHOR:` and all 13 have valid `TheoryGrounding` | Phase 4, Step 1 | Completed |
| **REQ-GRD-02** | §3.2.11, §5.4.1 | Create AST guardrail suite `test_seed_architectural_guardrails.py` asserting 0 occurrences of `default_locale`, 100% bilingual parity, and 0 legacy profile dictionaries | Phase 4, Step 1 | Completed |
| **REQ-GRD-03** | §5.4.1, §6 (TC-L10N-02) | Create backend internal localization parity suite `test_backend_l10n_internal_parity.py` asserting 1:1 key parity between `en.json` and `fi.json`, 100% Jinja `l10n.*` reference coverage, and 0 dead keys | Phase 4, Step 2 | Completed |
| **REQ-GRD-04** | §1.1.5, §3.2.20, §5.4.1 | Create synthetic SDUI test dataset `backend_v2/tests/fixtures/sdui_golden_master.json` containing populated instances of specifically all 17 `AnySduiBlock` types | Phase 4, Step 3 | Completed |
| **REQ-GRD-05** | §1.1.5, §3.2.19, §5.4.1 | Create presentation parity test suite `test_sdui_template_parity.py` asserting 100% block exhaustiveness in Jinja & Dart, Jinja AST field validity, unrecognized block Fail-Fast, and BeautifulSoup semantic DOM rendering | Phase 4, Step 4 | Completed |
| **REQ-GRD-06** | §1.1.5, §3.2.20, §5.4.1 | Create Flutter SDUI golden master parity test `client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart` verifying 1:1 semantic text, citation, badge, and table parity against Jinja DOM output | Phase 4, Step 5 | Completed |
| **REQ-GRD-07** | §5.4.2 | Execute full global quality loops (`backend_audit_loop.py` and `flutter_audit_loop.py`) | Phase 4, Step 5 | Completed |

---

# Session Handover Context

## Achieved
- Formatted and generated standardized multi-phase Epic tracking document `@[docs/epic/EPIC_148_tracker.md]`.
- Mapped all 4 phases from `@[docs/epic/tasks_EPIC_148/]` into granular execution steps and double-entry bookkeeping Requirements Traceability Matrix (36 granular requirements REQ-TG-01..08, REQ-I18N-01..15, REQ-PROF-01..14, REQ-GRD-01..07).
- Executed `/tier0-research-plan` on Phase 1 (`@[docs/epic/tasks_EPIC_148/01_phase1_theory_grounding_and_epistemic_anchor_sanitization.md]`):
  - Neuro-symbolic planner audit (`audit_planner_output.py`) verified 100% boundary preservation across all 15 line bounds, 56 targets, 51 AST bounds, and 14 KIs.
  - Performed Touched Scope Technical Debt sweep: discovered missing `depends_on=()` in `FlattenedAtom` instantiations in `test_matrix_sensor_prompt_builder.py` and updated the implementation plan accordingly.
  - Refined AST guardrail extension `QGR001` scope to target domain code while excluding test fixtures.
- Executed `/tier2-execute` on Phase 1:
  - Cleaned typing debt in `test_matrix_sensor_prompt_builder.py` with `depends_on=()` to satisfy strict MyPy typing.
  - Extended AST guardrail `QGR001` in `scripts/_ast_guardrails.py` to ban `setattr(...)` and `object.__setattr__(...)` across all non-test python code, and added unit tests in `test_ast_guardrails.py`.
  - Updated `frozen_state_mutability` in `.agents/rules/01-python-backend.md` locking in-place mutation bans.
  - Backed up seed vault to `backend_v2/seed/backups/seed_data_pre_epic148_cleanup.json`.
  - Verified 13 matrix blocks in `seed_data.json` are cleanly sanitized without `EPISTEMIC ANCHOR:` tails, preserving human coaching prompts.
  - Refactored `MatrixSensorPromptBuilder.build_caching_prefix` to format pure `<theory_context>` and `<matrix_objective>` XML via `TemplateProcessor.safe_interpolate()` with CDATA Breakout Shielding, omitting raw URLs.
  - Eradicated `_create_ephemeral_block` helper and artificial IDs (`blk_1111...`, `blk_2222...`, `blk_3333...`).
  - Added XML injection shield and CDATA tests (TC-TG-01..06) in `test_matrix_sensor_prompt_builder.py`.
  - Fixed dictionary `.get()` fallback on line 169 in `matrix_sensor_prompt_builder.py` to comply with AST rule `QGR002`.
  - Passed Universal Quality Gate with 100% statement coverage on `matrix_sensor_prompt_builder.py` and 92% on `_ast_guardrails.py`.
  - Re-seeded local development database cleanly (`uv run python backend_v2/seed/run_seed.py local`).
- Executed `/tier8-audit-plan` on Phase 1:
  - Verified 100% compliance against plan requirements, demolitions, AST guardrails, and test contracts.
  - Generated audit artifact `red_team_audit_epic148_phase1.md`.
  - Ran global backend audit loop `uv run python scripts/backend_audit_loop.py backend_v2/ --test` with 2,148 tests passing cleanly.
  - Phase 1 marked as `[x] [OK]` across all gates (Red-Teaming, Execution, Coverage, Audit).
- Executed `/tier0-research-plan` on Phase 2 (`@[docs/epic/tasks_EPIC_148/02_phase2_atomic_i18n_text_modernization_and_systemic_fixture_migration.md]`):
  - Neuro-symbolic planner audit (`audit_planner_output.py`) verified 100% boundary preservation (15/15 line bounds, 56 targets, 51 AST bounds, 14 KIs).
  - Touched Scope Technical Debt & Integration Sweep:
    - Identified that `WarningCardAdapter` dynamically calls `LocalizationService.translate('alert_starvation_insufficient_data', context.locale)`, but the translation key was missing from backend static dictionary files (`backend_v2/l10n/en.json` and `backend_v2/l10n/fi.json`).
    - Added `backend_v2/l10n/en.json`, `backend_v2/l10n/fi.json`, and `backend_v2/tests/unit/models/test_v2_core.py` to target files, touched artifacts, and Step 1 actions.
    - Verified Flutter 1-hop execution widgets and Studio widgets for precise line bounds.
  - Phase 2 marked as `[x] [OK]` for Red-Teaming.
- Executed `/tier2-execute` on Phase 2:
  - **Step 1 (Python Domain Model & Decoupling)**:
    - Moved `I18nText` to `backend_v2/models/core_base.py` (re-exported in `v2_core.py`), removed `default_locale`, made `translations` required without defaults, and enforced Fail-Fast `resolve()` / `get()`.
    - Created decoupled DTO module `backend_v2/models/dtos/matrix_scorecard.py` containing `MatrixScorecardRowDTO`, `ScorecardAtomDTO`, `HumanOverrideDTO`, `HumanOverrideRequest`, `TDAPending`, `TDAEvaluated`, `TDADlq`, `TDAStateUnion`.
    - Resolved circular import between `v2_core.py` and `sdui.py` cleanly through `matrix_scorecard.py`.
    - Refactored `WarningCardAdapter` in `backend_v2/services/sdui/adapters/warning_card_adapter.py` to translate `'alert_starvation_insufficient_data'` via `LocalizationService` and raise `ErrorCodes.CONFIGURATION_ERROR`.
    - Populated translation tables in `backend_v2/l10n/en.json` and `fi.json`.
  - **Step 2 (Flutter Freezed Model & UI Cleanups)**:
    - Modernized `client_app_v2/lib/shared/models/i18n_text.dart` (`@JsonSerializable(disallowUnrecognizedKeys: true)` without `defaultLocale`, added `isEmpty`/`isNotEmpty`/`has()`/`get()`).
    - Cleaned all Studio views, controllers, and 1-hop execution widgets.
    - Added comprehensive Flutter unit test suite `client_app_v2/test/shared/models/i18n_text_test.dart` (7/7 tests passing).
    - Ran `flutter_audit_loop.py` (0 analyzer issues) and verified all 225 Flutter tests passing.
  - **Step 3 (Deterministic Pruning of seed_data.json)**:
    - Pruned 500 legacy `default_locale` keys from `seed_data.json` via scratch script and verified 100% bilingual Finnish translations for `prompt_blocks[88]` and `prompt_blocks[89]`.
    - Re-seeded local development database cleanly (`uv run python backend_v2/seed/run_seed.py local`).
  - **Step 4 (Deterministic Bulk Migration of Test Fixtures)**:
    - Bulk migrated 90 Python test files (1,166 fixture occurrences) and 25+ Flutter test files (157 fixture occurrences).
  - **Step 5 (Universal Quality Gate & Full Verification)**:
    - Added dedicated unit test coverage for `core_base.py` and `dtos/matrix_scorecard.py`.
    - Ran `backend_audit_loop.py` achieving 100% coverage across all touched targets.
    - Verified full backend test suite: **2,153 tests passed** (0 failures).
    - Verified full frontend test suite: **225 tests passed** (0 failures).
  - Phase 2 marked as `[x] [OK]` for Execution and Test Coverage Assertions.
- Executed `/tier0-research-plan` on Phase 3 (`@[docs/epic/tasks_EPIC_148/03_placeholder_phase3_output_profile_sdui_dumb_painter_and_localization_parity.md]`):
  - Neuro-symbolic planner audit (`audit_planner_output.py`) verified 100% boundary preservation (15/15 line bounds, 56 targets, 54 AST bounds, 14 KIs).
  - Executed Panel of Experts System 2 analysis across Python backend, LLM prompt compilation, Flutter Dumb Painter architecture, and ISTQB test verification.
  - Transformed placeholder task into full 5-step executable implementation plan with granular steps, demolish specifications, and ISTQB test contracts.
  - Phase 3 marked as `[x] [OK]` for Red-Teaming.
- Executed `/tier2-execute` on Phase 3:
  - **Step 1 (Tech Debt Cleanups & Static Translation Tables)**:
    - Completed technical debt cleanups in `backend_v2/models/core_base.py`, `backend_v2/models/dtos/matrix_scorecard.py`, and `client_app_v2/lib/features/studio/views/profile_editor_view.dart`.
    - Extended `LocalizationService` in `backend_v2/services/localization.py` with type-safe formatting helpers (`format_date`, `format_decimal`, `format_score`, `format_percent`, `format_cost`) and unit tests.
    - Populated all static translation tables in `backend_v2/l10n/en.json` and `fi.json`.
    - Git Commit: `292a2859`.
  - **Step 2 (Python Domain Model & DTO Modernization + Seed Migration)**:
    - Declared `MatrixSynthesisGroup` in `backend_v2/models/v2_core.py`.
    - Modernized `OutputProfile` in `backend_v2/models/v2_core.py` (added `matrix_synthesis_groups`, contextual cross-field validator `validate_matrix_graphs_coherence`, purged `layouts`, `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`).
    - Eradicated `OutputLayoutBlock` class across the Python codebase.
    - Modernized DTOs in `backend_v2/models/dtos/output_profile.py`.
    - Retired obsolete AST parity checks in `backend_v2/tests/unit/test_enum_parity.py`.
    - Migrated `output_profiles[0]` in `backend_v2/seed/seed_data.json` to 3 comparative matrix synthesis groups.
    - Git Commit: `a548f83b`.
  - **Step 3 (Flutter Freezed Model Update & Studio UI Modernization)**:
    - Declared `MatrixSynthesisGroup` Freezed class in `client_app_v2/lib/features/studio/models/output_profile.dart`.
    - Modernized `OutputProfile` Freezed class (purged legacy dictionaries and `layouts`, added `@Default([]) List<MatrixSynthesisGroup> matrixSynthesisGroups`).
    - Modernized Studio UI components: `profile_layouts_tab.dart`, `matrix_graphs_block_card.dart`, `matrix_graph_item_editor.dart`, `matrix_summary_table_card.dart`.
    - Added negative ISTQB unit tests in `output_profile_test.dart` and updated `profile_layouts_tab_test.dart`.
    - Ran Flutter code generation and audit loop: 0 errors, 225 Flutter tests passing.
    - Git Commit: `850ca821`.
  - **Step 4 (SDUI Presentation Adapters, Worker & Jinja2 PDF Template Sanitization)**:
    - Modernized presentation adapters in `backend_v2/services/sdui/adapters/` (`metadata_adapter.py`, `variance_adapter.py`, `authenticity_adapter.py`, `executive_summary_adapter.py`, `matrix_graphs_adapter.py`, `matrix_summary_table_adapter.py`, `printable_sources_adapter.py`, `xai_highlights_adapter.py`) to pre-localize labels, costs, and dates via `LocalizationService`.
    - Modernized worker task `generate_profile_synthesis_and_pdf_task` in `backend_v2/worker.py` to iterate over `matrix_synthesis_groups`.
    - Sanitized `report_template.jinja2` (purged 11 fallback ternaries, compact footer pagination, registered `raise_unrecognized_sdui_block`).
    - Resolved circular dependency between `v2_core.py` and `state.py` by placing `ExecutionCoreFields.model_rebuild()` in `state.py`.
    - Modernized adapter unit test suites (54 adapter tests passing, 23 PDF generator & worker synthesis tests passing with 99% coverage on `pdf_generator.py`).
    - Quality gate `scripts/backend_audit_loop.py` passed with 0 errors across all step 4 targets.
    - Git Commit: `f162d4e6`.
  - **Step 5 (Seed Vault OutputProfile Migration, Test Fixture Updates & Universal Quality Gate Verification)**:
    - Modernized all remaining unit test fixtures across `test_blueprint.py`, `test_blueprint_sdui_crash.py`, `test_matrix_domain_parser.py`, `test_output_profile_service.py`, `test_workflow_service.py`, `test_output_profiles.py`, `test_scoring.py`, `strategies/test_llm.py`, `test_synthesis_distiller_wiring.py`, `test_synthesis_distiller_hook.py`, `test_api_clone_endpoints.py`, `test_concurrency_fuzzer.py`, `test_dag_executor_prompt_blocks.py`, `test_llm_context_bounds.py`, `test_tier4_bug_fixes.py`, `test_tier4_profile_dto_bug.py`.
    - Enforced strict Opaque Stripe ID validation (`pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$"`) on `MatrixSynthesisGroup.id` in `backend_v2/models/v2_core.py`.
    - Updated `seed_data.json` synthesis groups to 16-hex Opaque IDs (`grp_440a5fef9331451b`, `grp_c5804a9143c34cb1`, `grp_6b8c766185294f7e`).
    - Migrated Flutter ID generators in `matrix_graphs_block_card.dart` and `layout_editor_card.dart` to generate 16-hex Opaque IDs via `Uuid()`.
    - Updated architectural guardrail tests in `test_seed_architectural_guardrails.py` asserting 0 legacy dictionaries and 100% presence of dynamic metric keys in `en.json` and `fi.json`.
    - Cleanly re-seeded local development database (`uv run python backend_v2/seed/run_seed.py local`).
    - Cleaned unused imports and test variables in Flutter (`output_profile_controller.dart`, `block_card_registry_test.dart`).
    - Executed Universal Quality Gate audits:
      - Backend Audit Loop (`backend_audit_loop.py backend_v2 --test`): Ruff, MyPy, AST Guardrails, Jinja template validation, Seed validation, and Pytest (2,135 passed, 0 failed, 90% coverage).
      - Flutter Audit Loop (`flutter_audit_loop.py client_app_v2 --test`): Formatting, Analyzer, and Flutter test suite (224 passed, 0 failed).
    - Phase 3 marked as `[x] [OK]` for Execution and Test Coverage Assertions.
- Executed Server-Side ID Generation Mandate & Request/Response DTO Separation Plan:
  - **DTO Schema Separation**: Created dedicated `*CreateDTO` and `*UpdateDTO` models in `backend_v2/models/dtos/studio.py` (`WorkflowCreateDTO`, `OutputProfileCreateDTO`, `PromptBlockCreateDTO`, `StepRuleCreateDTO`, `MatrixSynthesisGroupCreateDTO`) with strict `extra="forbid"`, banning client-supplied `id` fields.
  - **Server ID Authority**: Updated `SystemConfigService`, `WorkflowService`, and `OutputProfileService` in `backend_v2/services/studio/` to generate canonical 16-hex Opaque Stripe IDs (`uuid.uuid4().hex[:16]`).
  - **Router Hardening**: Updated `backend_v2/api/routers/output_profiles.py` to use `OutputProfileCreateDTO` and return `OutputProfileResponseDTO`.
  - **AST Guardrail Engine (QGR011)**: Added `QGR011` AST rule in `scripts/_ast_guardrails.py` banning `id` field declarations on `*CreateDTO` classes. Added AST test suite in `backend_v2/tests/unit/scripts/test_ast_guardrails.py`.
  - **Frontend Decoupling**: Purged client-side ID generation and `Uuid().v4()` calls from Flutter Studio views (`prompt_block_builder_view.dart`, `step_builder_view.dart`, `matrix_graphs_block_card.dart`, `layout_editor_card.dart`, `workflow_steps_tab.dart`).
- Executed `/tier8-audit-plan` on Phase 3:
  - **Neuro-Symbolic & AST Boundary Verification**: Planner output audit script `scripts/audit_planner_output.py` verified 100% boundary preservation across all 15 line bounds, 56 targets, 54 AST bounds, and 14 KIs.
  - **Destructive Purge & Demolish Verification**: Confirmed complete eradication of `OutputLayoutBlock` and purged dictionary lookups (`metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, `layouts`) with 0 matches across the repository.
  - **Dumb Painter & StrictUndefined Audit**: Verified `LocalizationService` pre-formatting methods (`format_date`, `format_decimal`, `format_score`, `format_percent`, `format_cost`), Jinja2 `StrictUndefined` environment configuration, and fail-fast `raise_unrecognized_sdui_block` handler.
  - **Universal Quality Gate Executions**:
    - Backend Audit Loop (`backend_audit_loop.py backend_v2 --test`): Ruff linting/formatting, MyPy strict type checking, AST guardrails, Jinja template validation, seed dry-run, and full Pytest suite (**2,148 tests passed**, 25 skipped, 0 failed).
    - Flutter Audit Loop (`flutter_audit_loop.py client_app_v2 --test`): Dart formatting, Dart analyzer (0 issues), and Flutter test suite (**224 tests passed**, 1 skipped, 0 failed).
    - Supply Chain Security: 0 banned third-party AI packages detected (`langchain`, `llamaindex`, `crewai`, `autogen`, `semantic-kernel`).
  - **Audit Artifact Generated**: Created comprehensive System 2 audit report `red_team_audit_epic148_phase3.md` in the artifact directory containing the full Traceability Matrix, Tri-Axis Dialectical Audit, and Zero-Defect Verdict.
  - Phase 3 marked as `[x] [OK]` across all gates (Red-Teaming, Execution, Coverage, Audit).
- Executed Flutter Dynamic Workflow Title & Label Resolution via `I18nText` Modernization:
  - **DashboardView Title Resolution**: Modernized `workflowDisplay` and `_getVariantDisplayName` in `client_app_v2/lib/features/execution/views/dashboard_view.dart` to use `I18nText.fromJson(rawMap).get(locale)`, eliminating legacy `default_locale` lookups and resolving runtime validation error crashes on dashboard load.
  - **NewExecutionView Resolution**: Modernized workflow selector sidebar title/description, dynamic header, questionnaire definition labels, and print variant selector titles/descriptions in `client_app_v2/lib/features/execution/views/new_execution_view.dart` using `I18nText.fromJson`.
  - **DynamicStartScreen, StudioDashboardView & WorkflowSelector Modernization**: Updated `dynamic_start_screen.dart`, `studio_dashboard_view.dart`, and `workflow_selector.dart` to resolve dynamic localized strings strictly via `I18nText.fromJson(rawMap).get(locale)`.
  - **Obsolete File Deletion**: Eradicated legacy dead file `client_app_v2/lib/utils/i18n_resolver.dart`.
  - **Universal Quality Gate**: Passed `scripts/flutter_audit_loop.py client_app_v2` (0 errors) and all 231 Flutter unit and widget tests (`flutter test`).
- Executed `/tier0-research-plan` on Phase 4 (`@[docs/epic/tasks_EPIC_148/04_placeholder_phase4_ast_guardrails_parity_suites_and_final_audit.md]`):
  - Neuro-symbolic planner audit (`audit_planner_output.py`) verified 100% boundary preservation (15/15 line bounds, 56 targets, 54 AST bounds, 14 KIs).
  - Executed Panel of Experts System 2 analysis across Python backend, LLM prompt compilation, Flutter Dumb Painter architecture, and ISTQB test verification.
  - Transformed placeholder task into full 5-step executable implementation plan with granular steps, demolish specifications, Tri-Axis Dialectical Audit, and ISTQB test contracts.
  - Resolved `audit_markdown_boundaries.py` findings: updated `TheoryGrounding` AST node line bounds to `@[backend_v2/models/v2_core.py#L101-L114]` and eradicated ambiguous language (`e.g.`).
  - Ran `audit_markdown_boundaries.py` and `audit_planner_output.py` achieving 100% pass across all markdown boundaries and character-level constraints.
  - Phase 4 marked as `[x] [OK]` for Red-Teaming.
- Executed `/tier2-execute` on Phase 4:
  - **Step 1 (Pre-Implementation Sweep & AST Guardrails - Theory Grounding & Seed Vault)**:
    - Extended `backend_v2/tests/unit/test_seed_architectural_guardrails.py` asserting 0 occurrences of `default_locale` across entire seed vault, 100% bilingual Finnish parity across all 458 `I18nText` records, 0 legacy dictionaries in `OutputProfile`, and verified 16-hex Opaque Stripe IDs on all `matrix_synthesis_groups`.
    - Ran `uv run pytest backend_v2/tests/unit/test_seed_architectural_guardrails.py` (8/8 passed).
  - **Step 2 (Backend Internal Localization Parity Suite)**:
    - Created `backend_v2/tests/unit/test_backend_l10n_internal_parity.py` with 3 comprehensive test contracts: `test_backend_json_has_100_percent_internal_language_parity`, `test_jinja_template_all_l10n_references_exist_in_backend_dictionaries`, and `test_backend_json_has_no_dead_unreferenced_keys`.
    - Sanitized `backend_v2/templates/report_template.jinja2` binding dynamic l10n expressions (`l10n.report_title`, `l10n.warning_label`, `l10n.na_not_evaluated_label`, `l10n.sduiMetadataCosts`, `l10n.sduiMetadataTokens`).
    - Updated `backend_v2/services/sdui/adapters/printable_sources_adapter.py` to use `LocalizationService.translate("sources_and_bibliography_title", locale)`.
    - Purged dead unreferenced keys from `backend_v2/l10n/en.json` and `fi.json`, achieving 100% 1:1 symmetry across exactly 75 valid keys.
    - Ran `uv run pytest backend_v2/tests/unit/test_backend_l10n_internal_parity.py` (3/3 passed).
  - **Step 3 (SDUI Golden Master Test Fixture - All 17 AnySduiBlock Types)**:
    - Created synthetic SDUI test dataset `backend_v2/tests/fixtures/sdui_golden_master.json` containing populated, valid instances of specifically all 17 `AnySduiBlock` types.
    - Updated `QuoteEvidenceDTO` in `backend_v2/models/dtos/quote_evidence.py` to allow deserializing pre-resolved cached DTOs when `info.context is None`.
    - Verified `ReportDataDTO.model_validate_json()` validates fixture without error.
  - **Step 4 (SDUI Template Presentation Parity & Fail-Fast Suite - Backend)**:
    - Created `backend_v2/tests/unit/test_sdui_template_parity.py` implementing 5 test contracts: `test_all_sdui_blocks_handled_in_jinja_and_dart` (static AST verifying all 17 blocks handled in both Jinja macro and Dart switch), `test_jinja_ast_attribute_validity` (validating Jinja AST property accesses against Pydantic models), `test_jinja_raises_app_exception_on_unrecognized_block_type` (RFC 7807 Fail-Fast assertion), `test_pdf_generator_strict_undefined_missing_l10n_key_raises` (`StrictUndefined` enforcement), and `test_jinja_sdui_golden_master_rendering` (BeautifulSoup DOM verification for `en` and `fi`).
    - Added `ErrorTraceEvent` import and `AdapterContext.model_rebuild()` in `backend_v2/services/sdui/adapters/base_adapter.py`.
    - Updated assertions in `backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_adapter.py` to match localized dictionary titles.
    - Ran `uv run pytest backend_v2/tests/unit/test_sdui_template_parity.py` (5/5 passed) and all Phase 4 backend test suites (20/20 passed).
  - **Step 5 (Flutter SDUI Golden Master Parity Widget Test & Quality Gate)**:
    - Created `client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart` validating Freezed JSON deserialization across all 17 `AnySduiBlock` types and verifying headless widget rendering with 1:1 semantic text, badge, chart, and table assertions in English and Finnish.
    - Executed Universal Quality Gates:
      - Backend Audit Loop (`backend_audit_loop.py backend_v2 --test`): Ruff linting/formatting, MyPy strict type checking, AST guardrails, Jinja template validation, seed dry-run, and full Pytest suite (**2,164 tests passed**, 25 skipped, 0 failed, **90% test coverage**).
      - Flutter Audit Loop (`flutter_audit_loop.py client_app_v2 --test`): Dart formatting, Dart analyzer (0 issues), and Flutter test suite (**234 tests passed**, 1 skipped, 0 failed).
  - Phase 4 marked as `[x] [OK]` for Execution and Test Coverage Assertions.
- Executed `/tier8-audit-plan` on Phase 4:
  - **Planner Fidelity & AST Boundaries**: Verified 100% boundary preservation (15/15 line bounds, 56 targets, 54 AST bounds, 14 KIs) via `scripts/audit_planner_output.py`.
  - **Test Suite Verification**: Verified all 20 Phase 4 tests passing cleanly across AST guardrails (4/4), seed architectural guardrails (8/8), internal localization parity (3/3), and SDUI template presentation parity (5/5).
  - **Flutter SDUI Golden Master Parity**: Verified Freezed deserialization and 1:1 semantic widget tree rendering across all 17 `AnySduiBlock` types in `client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart` (3/3 tests passing).
  - **Linter & Docstring Gate**: Verified `uv run python -m ruff check --select D,E501` passes with 0 errors.
  - **Universal Quality Gate Executions**:
    - Backend Audit Loop: Ruff, MyPy, AST guardrails (QGR000-QGR011), Jinja validation, seed dry-run, and full Pytest suite (**2,164 tests passed**, 25 skipped, 0 failed, 90% test coverage).
    - Flutter Audit Loop: Dart formatting, Dart analyzer (0 issues), and Flutter test suite (**234 tests passed**, 1 skipped, 0 failed).
    - Supply Chain Security: 0 banned third-party AI packages detected (`langchain`, `llamaindex`, `crewai`, `autogen`, `semantic-kernel`).
  - **Audit Artifact Generated**: Created comprehensive System 2 audit report `red_team_audit_epic148_phase4.md` in the artifact directory containing the full Traceability Matrix, Tri-Axis Dialectical Audit, and Zero-Defect Verdict.
  - Phase 4 marked as `[x] [OK]` across all gates (Red-Teaming, Execution, Coverage, Audit). All 4 Phases of EPIC-148 are now complete.
- Executed `/tier2-hardening-backend` on Batch 1 (Domain Models & DTOs):
  - Audited, hardened, and verified 5 files: `@[backend_v2/models/core_base.py]`, `@[backend_v2/models/dtos/matrix_scorecard.py]`, `@[backend_v2/models/dtos/output_profile.py]`, `@[backend_v2/models/state.py]`, and `@[backend_v2/models/v2_core.py]`.
  - Neuro-symbolic audit matrices strictly verified for all 5 targets (157/157 rules passed with 0 violations and 0 suppressions).
  - Universal Quality Gate passed cleanly with 100% AST compliance, MyPy strict typing, and >90% coverage across all 5 targets.

## Learned
- **Phase 1 Insights & Invariants**:
  - `MatrixSensorPromptBuilder` in `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]` builds static system instructions cleanly in under 1ms without needing in-memory prompt block adaptation or ephemeral IDs.
  - Direct assembly via `TemplateProcessor.safe_interpolate()` with CDATA Breakout Shielding (`_apply_breakout_shield`) provides mathematically bulletproof XML injection protection for `<theory_context>` and `<matrix_objective>`.
  - `QGR001` statically bans `setattr(...)` and `object.__setattr__(...)` across all non-test python code, ensuring frozen model immutability.
  - `QGR002` AST rule strictly flags dictionary `.get()` with default fallbacks; explicit membership assertions (`if key in dict`) must be used for alias resolution.
  - Global backend test suite (2,148 tests) runs cleanly and validates cross-domain stability after Phase 1 sanitization.
- **Phase 2 Insights & Invariants**:
  - `I18nText` modernization purges `default_locale` across Pydantic V2 and Freezed models, requiring explicit `Field(...)` / `required Map<String, String> translations` without `@Default` or `default_factory=dict`.
  - Moving `I18nText` to `backend_v2/models/core_base.py` and scorecard DTOs to `backend_v2/models/dtos/matrix_scorecard.py` decouples presentation DTOs from `v2_core.py`, eliminating cyclical import traps with `backend_v2/models/view/sdui.py` in Python 3.14 / Pydantic V2.
  - `model_rebuild(_types_namespace=...)` calls in `v2_core.py` and `state.py` must explicitly provide all forward-referenced DTO types (`AnySduiBlock`, `MCPAuditTrace`, `MatrixScorecardRowDTO`).
  - Elimination of module-level `I18N_WARNING_STARVATION` in `warning_card_adapter.py` prevents import-time `ValidationError` crashes, but requires pre-populating `'alert_starvation_insufficient_data'` in `backend_v2/l10n/en.json` and `fi.json`.
  - Automated scratch scripts (`scratch/prune_default_locale_seed.py`, `scratch/migrate_backend_i18n_fixtures.py`, `scratch/migrate_flutter_i18n_fixtures.py`) successfully migrated all 1,166 backend and 157 Flutter fixture occurrences deterministically.
- **Phase 3 Insights & Invariants**:
  - `OutputProfile` modernization replaces `layouts: list[OutputLayoutBlock]` with `matrix_synthesis_groups: list[MatrixSynthesisGroup]`, eliminating the `OutputLayoutBlock` zombie DTO across Python and Flutter (`the_no_legacy_mandate`).
  - Strict Pydantic cross-field validator `@model_validator(mode="after") def validate_matrix_graphs_coherence(self)` asserts that IF `TargetBlockType.MATRIX_GRAPHS_BLOCK` is in `target_block_order`, THEN `len(matrix_synthesis_groups) >= 1`. All mock fixtures returning `OutputProfile` dictionaries or objects MUST include valid `matrix_synthesis_groups`.
  - Enforce Opaque Stripe ID standard: `MatrixSynthesisGroup.id` MUST strictly adhere to `pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$"`. Slugs are strictly forbidden as identifiers.
  - In `blueprint.py`, `scoring_strategy` and `s_strat` attributes on steps must be resolved with safe fallback inspection to handle both Enum instances and raw mock strings (`getattr(s_strat, "value", s_strat)`).
  - Static UI dictionaries (`metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`) are permanently extracted from backend persistence into `backend_v2/l10n/*.json` (for backend SDUI generation) and Flutter `.arb` (for client UI chrome).
  - SDUI adapters act as pure Dumb Painters: the backend pre-formats and pre-localizes all labels, dates, costs, scores, and percentages via `LocalizationService`, ensuring Jinja2 HTML templates and Flutter renderers never perform inline calculations or fallback guessing.
  - Removing `state.py` imports from `v2_core.py` and executing `ExecutionCoreFields.model_rebuild()` directly in `state.py` eliminates import graph cycles during pytest collection under Python 3.14.
  - **Server-Generated ID Authority & Request/Response DTO Separation Mandate**:
    - Creation Ban on Client IDs: Clients (Flutter UI and external REST API consumers) MUST NEVER provide an `id` field when creating new root resources (`Workflow`, `OutputProfile`, `Step`, `PromptBlock`) or sub-elements (`StepRule`, `MatrixSynthesisGroup`).
    - DTO Schema Separation: All `*CreateDTO` models MUST NOT contain an `id` field (`extra="forbid"` rejects any incoming `id`).
    - Backend ID Authority: The backend exclusively generates canonical, randomized 16-hex Opaque Stripe IDs (`uuid.uuid4().hex[:16]`).
    - Frontend Decoupling: All client-side `Uuid().v4()` calls and ID-generation fallbacks are eliminated from Flutter Studio views and models.
    - AST Guardrail (`QGR011`): Static AST verification in Phase 4 ensures no `*CreateDTO` contains an `id` field and domain models enforce standard Opaque Stripe ID patterns.
- **Flutter Dynamic Title & Label Resolution Insights**:
  - Eliminating `default_locale` from the backend persistence and domain models requires client UI layers to avoid raw dictionary indexing (`nameMap['translations']?[nameMap['default_locale']]`).
  - All dynamic label lookups in Flutter MUST use the Single Source of Truth `I18nText.fromJson(Map<String, dynamic>.from(rawMap)).get(locale)`.
- **Phase 4 Insights & Invariants**:
  - `AnySduiBlock` union variants in `backend_v2/models/view/sdui.py` define specifically all 17 polymorphic block types, coupled 1:1 with `SduiBlockDTO` in `client_app_v2/lib/shared/models/sdui_block_dto.dart` and `report_template.jinja2`.
  - Presentation Parity Golden Master (`backend_v2/tests/fixtures/sdui_golden_master.json`) must contain fully populated instances of all 17 block types to validate BeautifulSoup HTML DOM rendering and headless Flutter widget tree rendering with 1:1 semantic text, citation, and badge parity.
  - Backend translation tables (`backend_v2/l10n/en.json` and `backend_v2/l10n/fi.json`) must possess 100% internal 1:1 key parity and cover 100% of `report_template.jinja2` `l10n.*` references without dead or orphaned keys.
  - Fail-Fast `raise_unrecognized_sdui_block` handler bound in `PdfReportService` environment guarantees that unhandled synthetic blocks halt PDF compilation with RFC 7807 structured errors rather than falling back silently.
  - `TheoryGrounding` schema SSOT is anchored at `@[backend_v2/models/v2_core.py#L101-L114]` (re-exported cleanly across domain layers).
  - Markdown AST scanner (`audit_markdown_boundaries.py`) strictly enforces MBD001 (banning ambiguous `e.g.`) and MBD004 (verifying physical class/function line bounds in `@-references`).
- **Tier 2 Backend Hardening (Batch 1 - Domain Models & DTOs)**:
  - `core_base.py`: Enforcing `__all__ = ["I18nText", "V2CoreBase"]` and `exc_info=True` on `logger.error` guarantees RFC 7807 Fail-Fast trace logging.
  - `matrix_scorecard.py`: Declaring full `__all__` and converting all fields to PEP 593 `Annotated` syntax guarantees strict typing and decouples scorecards from `v2_core.py`.
  - `output_profile.py`: Server-side ID authority verified by `QGR011` AST guardrail; all fields annotated and custom scale bounds validated.
  - `state.py`: Consolidating `ExecutionCoreFields` and `ExecutionRecord` rebuilds into a single typed local namespace avoids overriding forward-referenced types.
  - `v2_core.py`: Replacing `.get("exact_quotes", [])` with explicit check in `validate_override_logic` eliminates `QGR002` violations.

## Discovered Technical Debt (Resolved in Phase 3 & Inter-Phase Bugfixes)
1. **`client_app_v2/lib/features/studio/views/profile_editor_view.dart#L124-L134`**: Resolved - replaced generic exception with `AppException.validation` and bound background color to primary theme.
2. **`backend_v2/models/core_base.py#L39`**: Resolved - wrapped description in `Field(description=...)` under 120 chars.
3. **`backend_v2/models/dtos/matrix_scorecard.py`**: Resolved - added module and union wrapper docstrings.
4. **`client_app_v2/lib/features/studio/controllers/output_profile_controller.dart`**: Resolved - removed unused `i18n_text.dart` import.
5. **`client_app_v2/test/features/studio/views/widgets/profile/blocks/block_card_registry_test.dart`**: Resolved - cleaned unused local `updatedProfile` variable.
6. **`client_app_v2/lib/utils/i18n_resolver.dart`**: Resolved - removed obsolete dead file throwing non-standard `FormatException`.

## Remaining
- Complete Post-Implementation Gates:
  1. **Backend Tier 2 Hardening (Batch 2)**: Execute `/tier2-hardening-backend @[docs/epic/EPIC_148_tracker.md]` across remaining backend services and adapters:
     - `@[backend_v2/services/localization.py]`
     - `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]`
     - `@[backend_v2/services/pdf_generator.py]`
     - `@[backend_v2/services/sdui/adapters/authenticity_adapter.py]`
     - `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]`
     - `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]`
     - `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`
     - `@[backend_v2/services/sdui/adapters/metadata_adapter.py]`
     - `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`
     - `@[backend_v2/services/sdui/adapters/variance_adapter.py]`
     - `@[backend_v2/services/sdui/adapters/warning_card_adapter.py]`
     - `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]`
     - `@[backend_v2/worker.py]`
     - `@[scripts/_ast_guardrails.py]`
  2. **Frontend Tier 2 Hardening**: Execute `/tier2-hardening-frontend @[docs/epic/EPIC_148_tracker.md]` across all 12 modified Flutter files.
  3. **Golden Master & Test Restoration Audit**: Verify zero commented-out or bypassed tests across touched domains.
  4. **Proxy Sunset & Consumer Migration**: Final audit verifying zero dead legacy imports or `OutputLayoutBlock` callers remain.
  5. **As-Built Architectural Sync**: Execute `/tier7-describe-architecture` to synchronize directory references and update Knowledge Items.
  6. **Final Reverse Epic Audit**: Execute `/tier8-audit-epic @[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md]` to verify full Epic closure against codebase reality.

## Resume Command
```powershell
# Option A: Continue Tier 2 Backend Hardening (Batch 2: Services & SDUI Adapters)
/tier5-resume --target="@[docs/epic/EPIC_148_tracker.md], [backend_v2/services]" --workflow=/tier2-hardening-backend --rules="00-antigravity-core.md, 01-python-backend.md"

# Option B: Context Reset & Session Handover (if opening fresh window)
/tier5-session-handover @[docs/epic/EPIC_148_tracker.md]
```




