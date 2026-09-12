# Task Tracker: Harmonize User Role and Active Guidance (Goodhart) Matrix

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[c:\Users\risto\.gemini\antigravity-ide\brain\9dc6ba62-8cf6-4d0c-9706-4fe34cb727ce\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [ ] Constraint 1 (strict_enum_l10n_mapping): Do not use `.lower()` string manipulation on enum values. Use `RoleClassification.l10n_key` or `EXECUTIVE_SUMMARY_RULES` directly.
- [ ] Constraint 2 (zero_defaults_mandate): Non-critical metadata fields may default to None; core fields remain required.
- [ ] Constraint 3 (cross_domain_dto_parity): Backend Pydantic DTO fields must strictly correspond 1:1 with Flutter Freezed model fields.
- [ ] Constraint 4 (ban_heuristic_identifier_matching): Do not use keyword matching or step names to locate the matrix. Target explicitly via `active_profile_dto.user_role_target_block`.
- [ ] Constraint 5 (dumb_painter_ui): The adapter outputs pure SDUI `ParagraphBlock` instances; Flutter client remains an un-opinionated Dumb Painter.
- [ ] Constraint 6 (live_database_mutation): Do not edit db_v2.json directly. Structural edits must occur exclusively in `seed_data.json` before running `run_seed.py`.
- [ ] Constraint 7 (sdui_contract_fracture_prevention): Modifying any SDUI model, adapter, template, or renderer requires synchronously running `test_sdui_semantic_parity.py`.

## Execution Tasks
- [x] **Step 1: TECHNICAL DEBT CLEANUP & TEST FIXTURE EXPANSION**
  - [x] 1.1: Refactor `RoleClassification.l10n_key` in `backend_v2/models/enums.py` to eliminate `.get(self, "")` in favor of direct dictionary indexing `_L10N_MAP[self]`.
  - [x] 1.2: Add camelCase translation keys `rolePassenger`, `roleNavigator`, `roleDriver`, `roleArchitect` in `backend_v2/l10n/fi.json` and `backend_v2/l10n/en.json`.
  - [x] 1.3: Refactor `ExecutiveSummaryAdapter` to replace `parsed_role.value.lower()` with `parsed_role.l10n_key`.
  - [x] 1.4: Expand `test_executive_summary_adapter.py` with negative ISTQB test partitions.
  - [x] 1.5: Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py --test`.
- [x] **Step 2: DEPRECATE STOCHASTIC ROLE GENERATION IN PROMPTS & DTOS**
  - [x] 2.1: Remove user role extraction and role translation from `SYNTHESIS_SDUI_MANDATES` in `backend_v2/models/prompts/synthesis/sdui_directives.py`.
  - [x] 2.2: Make `user_role` and `user_role_justification` optional on `ExecutiveSummarySectionResult` in `backend_v2/models/dtos/synthesis.py`.
  - [x] 2.3: Make `user_role` and `user_role_justification` optional on `SynthesisOutputDTO` in `backend_v2/models/dtos/synthesis.py`.
  - [x] 2.4: Update tests in `backend_v2/tests/unit/models/dtos/test_synthesis.py`.
- [x] **Step 3: OUTPUTPROFILE SCHEMA EXPANSION & DTO PARITY**
  - [x] 3.1: Add `user_role_target_block` to `OutputProfile` in `backend_v2/models/v2_core.py`.
  - [x] 3.2: Add `user_role_target_block` to Create, Update, and Response DTOs in `backend_v2/models/dtos/output_profile.py`.
  - [x] 3.3: Add `user_role_target_block` to Freezed model in `client_app_v2/lib/features/studio/models/output_profile.dart`.
  - [x] 3.4: Run Freezed code generation via `flutter_audit_loop.py`.
- [x] **Step 4: DETERMINISTIC WORKER TRACE EXTRACTION**
  - [x] 4.1: Deterministically extract target block raw_score and compute role in `backend_v2/worker.py`.
  - [x] 4.2: Update `backend_v2/tests/unit/test_worker_synthesis.py`.
- [x] **Step 5: SDUI ADAPTER MATRIX BINDING & RICH BADGE RENDERING**
  - [x] 5.1: Implement dual-tier role badge resolution in `ExecutiveSummaryAdapter`.
  - [x] 5.2: Add dedicated unit tests for matrix scale name lookup and boundary clamping in `test_executive_summary_adapter.py`.
- [ ] **Step 6: SEED DATA VAULT HARMONIZATION & SEEDING**
  - [ ] 6.1: Update scale names of `blk_53f32679aa514fcb` in `backend_v2/seed/seed_data.json`.
  - [ ] 6.2: Add `"user_role_target_block": "blk_53f32679aa514fcb"` to profiles `prf_5d6e7f8091a2b3c4`, `prf_01b1d71000000001`, `prf_01b1d71000000002`, `prf_01b1d71000000003`.
  - [ ] 6.3: Run seed validation and sync.
- [ ] **Step 7: GLOBAL AUDIT LOOPS & SDUI SEMANTIC PARITY VERIFICATION**
  - [ ] 7.1: Run full backend audit loop.
  - [ ] 7.2: Run Flutter client domain parity test.
  - [ ] 7.3: Run SDUI semantic parity integration test.
