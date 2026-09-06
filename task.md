# Task Tracker: Prompt Architecture Harmonization

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_generation_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[docs/implementationplans/IMPLEMENTATION_PLAN_Prompt_Architecture_Harmonization.md]

## Pre-Flight Checklist (<constraint> tags)
- [ ] Constraint: `root_cause_first_over_reseed_mandate` - All corrupting data paths and legacy fallback debt must be excised before building new logic.
- [ ] Constraint: `static_first_dynamic_last_topology` - STATIC_LINGUISTIC_PROTOCOL must contain zero f-string interpolations. All dynamic parameters reside strictly inside build_linguistic_parameters.
- [ ] Constraint: `anti_ambiguity_mandate` - Do not use ambiguous terminology in comments or prompt definitions.
- [ ] Constraint: `tripartite_pipeline_architecture` - Execution layer prompts must contain zero Server-Driven UI instructions and zero coaching tone instructions.
- [ ] Constraint: `zero_service_layer_fallbacks` - Synthesis directives are derived 100% dynamically from database OutputProfile during runtime execution. No runtime fallback registries are created.
- [ ] Constraint: `anti_duplication` - Legacy prompt files at models/prompts root must be removed immediately after subpackage relocation.
- [ ] Constraint: `the_duct_tape_ban` - Never truncate text mid-sentence or slice strings with text[:limit] without sentence boundary analysis.
- [ ] Constraint: `dumb_painter_sdui` - UI widgets strictly bind and emit DTO state; no semantic logic or fallback synthesis is performed in Dart layers.
- [ ] Constraint: `universal_fail_fast` - Do not swallow missing configurations silently; fail fast with OUTPUT_PROFILE_INCOMPLETE.
- [ ] Constraint: `two_stage_testing` - Execute isolated unit tests first, followed by the global quality gate audit loop.
- [ ] Constraint: `multi_session_handover` - This is a multi-session plan. Mandatory /tier5-session-handover checkpoints after Steps 1-3, Steps 4-5, Steps 6-7, and Steps 8-9.

## Execution Tasks

- [x] (VERIFIED_EXISTING) **Step 1: Pre-Implementation Cleanups and Seed Preparation**
  - [x] Audit and resolve 7 technical debt items across boundaries.
  - [x] Backup `backend_v2/seed/seed_data.json` per `03_seed_vault.md`.
  - [x] Sanitize `output_profiles` in `seed_data.json` (convert 9 directives to English `str`, set length constraints).
  - [x] Fix matrix synthesis groups in `seed_data.json` (view_type 1d_metrics -> 2d_compare for 2-block groups).
  - [x] Sanitize or isolate orphan prompt block `blk_eeea566da4ab45f9`.
  - [x] Update Flutter widgets (`matrix_graph_item_editor.dart`, `executive_summary_block_card.dart`, `matrix_graphs_block_card.dart`).
  - [x] Update `output_profile_service.py` to raise `ResourceNotFoundError` when workflows list empty.
  - [x] Purge `DESC_TRANSLATION_MANDATE` from `backend_v2/models/dtos/synthesis.py` field descriptions.
  - [x] Anchor length constraints in SSOT constants.
  - [x] In-memory seed dry-run and re-seed execution.

- [x] (VERIFIED_EXISTING) **Step 2: Scaffolding Subpackages and Common Layer**
  - [x] Create `common/`, `execution/`, `synthesis/` directories.
  - [x] Create `models/prompts/common/__init__.py`.
  - [x] Create `models/prompts/common/field_prompts.py`.
  - [x] Create `models/prompts/common/global_mandates.py` (purified).
  - [x] Create `models/prompts/common/linguistic_directives.py` (`STATIC_LINGUISTIC_PROTOCOL` & `build_linguistic_parameters`).

- [x] (VERIFIED_EXISTING) **Step 3: Execution Layer Relocation and Purification**
  - [x] Create `models/prompts/execution/__init__.py`.
  - [x] Create `models/prompts/execution/matrix_evaluation.py`.
  - [x] Create `models/prompts/execution/hook_prompts.py` (pure execution hooks).
  - [x] Create `models/prompts/execution/mcp_prompts.py`.

- [x] (VERIFIED_EXISTING) **Step 4: Synthesis Layer Relocation and Purification**
  - [x] Create `models/prompts/synthesis/__init__.py`.
  - [x] Create `models/prompts/synthesis/style_directives.py`.
  - [x] Create `models/prompts/synthesis/sdui_directives.py` (purified of role extraction).
  - [x] Create `models/prompts/synthesis/synthesis_directives.py`.
  - [x] Create `backend_v2/services/factories/output_profile_factory.py`.

- [x] (VERIFIED_EXISTING) **Step 5: Root Barrel Re-export and Legacy Purge**
  - [x] Update `backend_v2/models/prompts/__init__.py`.
  - [x] Delete legacy root files in `backend_v2/models/prompts/`.
  - [x] Delete `backend_v2/tests/unit/models/prompts/test_synthesis_registry.py`.
  - [x] Verify `test_prompts_init.py`.

- [x] (VERIFIED_EXISTING) **Step 6: Two-Tier Length Budget Engine and DTO Expansion**
  - [x] Implement `backend_v2/services/length_budget_enforcer.py`.
  - [x] Add unit tests in `backend_v2/tests/unit/services/test_length_budget_enforcer.py`.
  - [x] Update `v2_core.py`, `domain/output_profile.py`, and `dtos/output_profile.py` for English `str` directives & length constraints.
  - [x] Implement cardinality `@model_validator` on `MatrixSynthesisGroup`.
  - [x] Implement group ID uniqueness `@model_validator` on `OutputProfile`.
  - [x] Bind factory in `output_profile_service.py:create_output_profile_draft`.
  - [x] Eliminate `seen_axes` in `matrix_graphs_adapter.py`.

- [x] **Step 7: Studio UI Directive Segregation and Length Inputs**
  - [x] Prune 1:1 section directives from `ProfileGeneralTab` Card 3.
  - [x] Retain 4 matrix view type directives with `profileMatrixViewDirectivesTitle`.
  - [x] Update Dart Freezed models in `output_profile.dart` (`String?` directives + length constraints).
  - [x] Run `build_runner`.
  - [x] Update block cards with English `TextFormField` & length inputs.
  - [x] Update `matrix_graph_item_editor.dart` (ban auto-clamp, radio 1D, quota chip disable).
  - [x] Update `matrix_graphs_block_card.dart` (`ReorderableListView` + Up/Down buttons).
  - [x] Update `.arb` files and Flutter unit tests.

- [ ] **Step 8: Caller Harmonization and Budget Injection**
  - [ ] Update `matrix_sensor_prompt_builder.py`.
  - [ ] Update `prompt_factory.py`.
  - [ ] Update `worker.py` (purge `resolve_i18n`, inject `<section_budget>`, budget enforcer, Fail-Fast).
  - [ ] Normalize imports in 1-hop caller modules.

- [ ] **Step 9: AST Guardrails and Test Suite Validation**
  - [ ] Update `test_ast_prompt_xml_sovereignty.py`.
  - [ ] Update and run all unit, integration, and parity test suites.
  - [ ] Run backend and flutter audit loops.

## # Session Handover Context
- **Achieved:**
  - Steps 1 through 7 of `IMPLEMENTATION_PLAN_Prompt_Architecture_Harmonization.md` implemented and verified.
  - Converted all 9 prompt directives in Flutter Freezed `OutputProfile` from `I18nText?` to `String?` and added 3 section length constraints (`rowExplanationLengthConstraint`, `xaiLengthConstraint`, `varianceLengthConstraint`).
  - Re-generated Freezed models via `build_runner` with zero issues.
  - Studio UI directive segregation: pruned 1:1 section directives from `ProfileGeneralTab` Card 3; retained 4 reusable view type directives as single-language English `TextFormField`s with `profileMatrixViewDirectivesTitle`.
  - Updated Tab 3 section cards (`ExecutiveSummaryBlockCard`, `MatrixSummaryTableCard`, `XaiExtensionsBlockCard`, `VarianceBlockCard`) with single-language English `TextFormField`s and dedicated numeric length constraint inputs.
  - Upgraded `MatrixGraphsBlockCard` to `ReorderableListView` with `ReorderableDragStartListener` drag handles and Up/Down `IconButton` controls.
  - Passed all unit tests in `profile_general_tab_test.dart`, `profile_section_config_tab_test.dart`, and `matrix_graph_editor_test.dart` (10/10 passed).
  - Flutter audit loop passed with 0 issues (code 0).
- **Learned:**
  - `scrollUntilVisible` in Flutter widget tests fails with `Bad state: Too many elements` if multiple Scrollables exist on screen without passing an explicit `scrollable:` finder. In desktop viewports (`physicalSize = const Size(1920, 3000)` and `devicePixelRatio = 1.0`), scrolling via `tester.drag(find.byType(ListView), const Offset(0, -600))` brings lower cards cleanly into the viewport.
  - Flutter `MaterialApp` in unit tests defaults to `supportedLocales.first` (`Locale('en')`) unless explicit `locale:` is passed.
  - Step 8: Caller Harmonization and Budget Injection completed (`matrix_sensor_prompt_builder.py`, `prompt_factory.py`, `translation_service.py`, `worker.py` purged `resolve_i18n`, injected `<section_budget>` and `enforce_sentence_boundary_budget`, Fail-Fast `OUTPUT_PROFILE_INCOMPLETE` on missing substantive directives, 100% audit passed).
- **Remaining:**
  - Step 9: AST Guardrails and Test Suite Validation.
