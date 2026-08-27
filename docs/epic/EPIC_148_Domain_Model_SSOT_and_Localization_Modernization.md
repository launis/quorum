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

# EPIC 148: Domain Model SSOT & Presentation Localization Modernization

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Objective
EPIC 148 standardizes and modernizes Quorum's domain data models and localization architecture across Python backend services, the SQLite/JSON seed vault, and the Flutter desktop client. The epic establishes five core capabilities:
1. Establish the **Epistemic Separation Paradigm** for theory grounding: prune redundant `EPISTEMIC ANCHOR:` prompt tails across all 13 matrix blocks in `seed_data.json`, format pure `<theory_context>` XML citations without raw URL token leakage during prompt compilation, and preserve structured `TheoryGrounding` metadata exclusively for UI/PDF presentation.
2. Eradicate redundant `default_locale` attributes across backend and frontend `I18nText` data models and 500 instances in `seed_data.json`, shifting language fallback resolution dynamically to execution context parameters (`target_locale`, with global fallback `"en"`).
3. Modernize `OutputProfile` and Server-Driven UI (SDUI) localization by migrating static UI dictionaries (`metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`) out of the backend database into frontend `.arb` resource files (for Flutter UI Chrome) and `backend_v2/l10n/*.json` (for PDF/SDUI presentation rendering), transforming `MetadataAdapter` into structured key-value envelopes, replacing legacy V1 `layouts` arrays with strongly-typed `matrix_synthesis_groups`, and completely eradicating the underlying `OutputLayoutBlock` Zombie DTO across Python and Flutter (`the_no_legacy_mandate`).
4. Execute the 4-phase **Atomic Migration Protocol** to ensure strict Pydantic V2 (`extra="forbid"`) and Flutter Freezed compatibility without silent fallbacks, duct-tape validators, or broken test fixtures.
5. Establish the **Tri-Tier SDUI Presentation Parity Architecture** (AST guardrails, Jinja AST attribute validators, and Golden Master cross-platform semantic testing) ensuring that PDF Jinja2 template rendering (`report_template.jinja2`) and Flutter desktop UI rendering (`sdui_blocks_renderer.dart`) maintain 100% semantic, structural, and localization parity across specifically all 17 `AnySduiBlock` types with zero silent drops or unlocalized ghost texts.

### 1.2 Problem Statement & Root Cause Analysis
1. **Theory Grounding Dual Injection & Prompt Bloat (Chapter 2)**: In `@[backend_v2/seed/seed_data.json#L336-L6900]`, epistemic and academic grounding anchors are duplicated across both `PromptBlock.ai_description` (as freeform `EPISTEMIC ANCHOR:` text blocks) and `PromptBlock.theory_grounding` (as structured `TheoryGrounding` DTOs). When `MatrixSensorPromptBuilder` compiles prompts, it injects both the raw text description and the structured object with raw URLs (`source_url`), triggering prompt duplication, URL token bloat, XML syntax corruption risks, and Single Source of Truth (SSOT) drift.
2. **`I18nText.default_locale` Redundancy (Chapter 3)**: In `@[backend_v2/models/core_base.py#L39-L140]`, `@[client_app_v2/lib/shared/models/i18n_text.dart]`, and across 500 records in `seed_data.json`, every `I18nText` object hardcodes `"default_locale": "fi"`. This conflates static dictionary storage with dynamic runtime resolution, creates internal validation contradictions with the global `"en"` fallback rule, and bloats database payloads across 1300+ test fixtures.
3. **`OutputProfile` Presentation Drift & Dual-Axis Localization Conflicts (Chapter 5)**: In `@[backend_v2/seed/seed_data.json#L9180-L9570]`, `OutputProfile` persists hundreds of lines of static UI label translations in backend dictionaries (`metric_mappings`, `matrix_column_labels`, `user_role_mappings`). `MetadataAdapter` concatenates labels with values in Python strings, violating the "Dumb Painter" principle and creating localization drift. Per the Dual-Axis Localization paradigm (`ki_dual_axis_localization_architecture.md`), static UI Chrome strings belong exclusively in Flutter `.arb` files, while server-side report generation strings belong in `backend_v2/l10n/*.json`. Furthermore, `OutputProfile.layouts` retains obsolete V1 fields (`preset_view`, `text_delivery_mode`, `steps: []`) rather than declaring clean matrix synthesis groups. In Quorum's Server-Driven UI (SDUI) architecture, all blocks (`METADATA_BLOCK`, `EXECUTIVE_SUMMARY_BLOCK`, `SYNTHESIS_TEXT_BLOCK`, `MATRIX_GRAPHS_BLOCK`, `GROUPED_EXTENSIONS_BLOCK`, `PENALTIES_BLOCK`, `MATRIX_SUMMARY_TABLE_BLOCK`, `VARIANCE_VALIDATION_BLOCK`, `AUTHENTICITY_EVALUATION_BLOCK`, `PRINTABLE_SOURCES_BLOCK`, `GLOBAL_SCORE_BLOCK`, `AUDIT_TRAIL_BLOCK`) exist on the exact same flat, modular level where rendering order and block presence are 100% dynamically customizable via `OutputProfile.target_block_order` in the UI. The distinction between syntheses is strictly about **Synthesis Scope** (Global Executive Summary vs. Matrix Group Comparative Syntheses), not a structural hierarchy. `OutputProfile.matrix_synthesis_groups` defaults to `default_factory=list` because valid profile variants (specifically: Executive Brief vs. Holistic Audit), non-matrix workflows, and server-minted Studio drafts legitimately contain 0 matrix groups, while `MatrixSynthesisGroup.target_blocks` strictly enforces `min_length=1` and `OutputProfile` enforces contextual `@model_validator` coherence when `MATRIX_GRAPHS_BLOCK` is active.
4. **Fragility Under `extra="forbid"`, Active Development Lifecycle & Clean Slate Database Wipe Mandate (Chapter 6)**: Pydantic V2 models enforce `strict=True` and `extra="forbid"`, while Flutter Freezed models enforce `@JsonSerializable(disallowUnrecognizedKeys: true)`. In accordance with Quorum's fundamental Zero-Legacy Architecture (`the_no_legacy_mandate`, `local_data_ephemeral_nature`, `zero_legacy_fallback_hacks`), legacy runtime and production database records (`db_v2.json`, historical Firestore/TinyDB executions) are not preserved through stateful, disposable migration scripts or duct-tape `@model_validator(mode="before")` parsing shims. Instead, EPIC 148 enforces an explicit **Clean Slate Deployment Mandate**: all legacy live/runtime database collections and executions are intentionally wiped and re-seeded cleanly from the modernized `backend_v2/seed/seed_data.json` Single Source of Truth (`uv run python backend_v2/seed/run_seed.py local`). Furthermore, because the project is in active pre-production development where the monorepo codebase, test fixtures, and local database are continuously reset, re-seeded, and synchronized in lockstep (**Monorepo Atomic Migration Protocol**), production-grade client deployment gating (specifically: `X-Min-Client-Version` middleware) is intentionally out of scope and deferred to future production release milestones.
5. **Presentation & Localization Drift between PDF Jinja2 and Flutter UI**: `report_template.jinja2` contains hardcoded Finnish text (`N/A (Ei arvioitu):` on L159), hardcoded English footer pagination (`"Page " counter(page) " of " counter(pages);`), hardcoded section labels (`Warning:`, `Meta Costs`, `Meta Tokens`, `(Lähde: ...)`), and lazy fallback ternaries (`if l10n is defined else '...'`), risking unlocalized ghost strings in English PDF reports. Furthermore, while `PdfReportService` configures `undefined=jinja2.StrictUndefined`, retaining `if l10n is defined else ...` ternaries bypasses `StrictUndefined` and masks missing localization keys with unlocalized fallback strings. Eradicating all fallback ternaries in favor of direct `{{ l10n.<key> }}` attribute lookups enforces mathematical Fail-Fast validation (`the_duct_tape_ban`, `anti_lazy_fallback_mandate`), halting compilation if any translation key is missing. Furthermore, `report_template.jinja2` lacks an AST guardrail ensuring exhaustive coverage of all `AnySduiBlock` types, allowing new block types added to Python and Flutter to be silently omitted from PDF outputs without raising an error.
6. **Execution-Tier UI Hardcoded Strings & UI Scope Boundary**: Several critical user-facing execution widgets in Flutter (`human_override_dialog.dart`, `execution_report_view.dart`, `specialist_section.dart`) contain raw, hardcoded Finnish and English strings instead of resolving through `.arb` localization tables (`AppLocalizations`). *Scope Boundary Note*: EPIC 148 strictly addresses Execution-tier UI and SDUI presentation localization parity. Broader UI Chrome localization for Studio, Lexicon, and Admin/Builder views is intentionally scoped as a Non-Goal for this Epic and will be addressed in a future dedicated UI localization Epic.

---

## 2. Scope & File Modification Boundary

### 2.1 TARGET Files (Editable)
- `[MODIFY]` `@[backend_v2/seed/seed_data.json#L336-L6900]` (PromptBlocks: Sanitize all 13 matrices by removing `EPISTEMIC ANCHOR:` tails)
- `[MODIFY]` `@[backend_v2/seed/seed_data.json#L9180-L9570]` (OutputProfiles: Prune `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`; replace `layouts` with `matrix_synthesis_groups`)
- `[MODIFY]` `@[backend_v2/seed/seed_data.json]` (Prune 500 instances of `default_locale` across seed vault per `Step 2.3` / `vault_mutation_protocol`, and populate authentic Finnish translations for 4 prompt block text fields lacking `fi` in `prompt_blocks[88]` and `prompt_blocks[89]`)
- `[MODIFY]` `@[backend_v2/models/core_base.py#L39-L140]`, `@[backend_v2/models/v2_core.py#L918-L934]`, and `@[backend_v2/models/v2_core.py#L937-L1076]` (Remove `default_locale` and `default_factory=dict` from `I18nText`, enforcing required `translations: Annotated[dict[str, str], Field(...)]` validated strictly via `@field_validator("translations")` without `object.__setattr__` frozen mutations, and updating `resolve()`; eradicate `class OutputLayoutBlock(V2CoreBase)` and remove from `__all__`; remove legacy `layouts` and dictionary mappings from `OutputProfile` and define `MatrixSynthesisGroup` domain model per `the_no_legacy_mandate`)
- `[MODIFY]` `@[backend_v2/models/dtos/output_profile.py]` (Remove `OutputLayoutBlock` import; remove `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts`; add `matrix_synthesis_groups` across `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO`)
- `[MODIFY]` `@[backend_v2/tests/unit/test_enum_parity.py]` (Retire `test_preset_view_parity()` and `test_text_delivery_mode_parity()` AST assertions targeting deleted `OutputLayoutBlock`)
- `[MODIFY]` `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L26-L75]` and `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L77-L208]` (Eradicate `_create_ephemeral_block` helper and fake IDs; format pure `<theory_context>\n{citation}\n</theory_context>` and `<matrix_objective>` via direct `TemplateProcessor.safe_interpolate()` assembly)
- `[MODIFY]` `@[client_app_v2/lib/shared/models/i18n_text.dart]` and generated `.freezed.dart` / `.g.dart` (Annotate Freezed factory constructor explicitly with `@JsonSerializable(disallowUnrecognizedKeys: true)`; remove `defaultLocale` and `@Default` from Freezed model, enforcing `required Map<String, String> translations`; add `isEmpty`, `isNotEmpty`, `has(langCode)` helpers; update `get(String? langCode, {String fallback = 'en'})` method with Fail-Fast `AppException.validation`)
- `[MODIFY]` `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]` (Remove redundant ternaries `locale == 'fi' ? get('fi') : get('en')` and pass `locale` directly to `get(locale)`)
- `[MODIFY]` `@[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart]` (Remove redundant ternaries and pass `locale` directly to `get(locale)`)
- `[MODIFY]` `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]` (Migrate hardcoded Finnish UI text, buttons, labels, and SnackBar error messages to `AppLocalizations`)
- `[MODIFY]` `@[client_app_v2/lib/features/execution/views/execution_report_view.dart]` (Migrate hardcoded tooltips and action labels to `AppLocalizations`)
- `[MODIFY]` `@[client_app_v2/lib/shared/widgets/specialist_section.dart]` (Migrate hardcoded header string to `AppLocalizations`)
- `[MODIFY]` `@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]` (Populate execution-tier localization keys)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart]` (Remove `defaultLocale` state tracking and bind text editing directly to `translations` map)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]` (Replace ad-hoc `isEmptyI18n()` helper with SSOT `i18nText.isEmpty`)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart]` (Replace hardcoded `Color(0xFF2E7D32)` with `Theme.of(context).colorScheme.primary` and replace generic `throw Exception(...)` with `throw AppException.validation(...)`)
- `[MODIFY]` `@[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart]` (Purge manual `url.substring(0, 40)` clipping in favor of declarative `TextOverflow.ellipsis`)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/models/output_profile.dart]` and generated `.freezed.dart` / `.g.dart` (Eradicate `OutputLayoutBlock` Freezed class; declare `MatrixSynthesisGroup` Freezed model with explicit `@JsonSerializable(disallowUnrecognizedKeys: true)`; update `OutputProfile` Freezed model: remove `metricMappings`, `matrixColumnLabels`, `userRoleMappings`, `extensionLabels`, and `layouts`; add `matrixSynthesisGroups`)
- `[MODIFY]` `@[client_app_v2/test/features/studio/models/output_profile_test.dart]` (Replace `OutputLayoutBlock` JSON parsing tests with `MatrixSynthesisGroup` serialization tests and negative ISTQB partition tests asserting that legacy keys `layouts`, `metric_mappings`, `user_role_mappings`, `extension_labels` on `OutputProfile` and `preset_view`, `steps` on `MatrixSynthesisGroup` throw `CheckedFromJsonException`)
- `[MODIFY]` `@[backend_v2/l10n/en.json]` and `@[backend_v2/l10n/fi.json]` (Populate complete static translation tables for Backend SSOT report generation including all 17 metric mapping keys, user roles, matrix columns, extension labels, `na_not_evaluated_label`, `sources_and_bibliography_title`, `warning_label`, `source_label`, `sduiMetadataCosts`, `sduiMetadataTokens`, `col_quotes`, `report_title`, and formatting rules)
- `[MODIFY]` `@[backend_v2/services/localization.py]` (Extend with type-safe formatting helpers: `format_date()`, `format_decimal()`, `format_score()`, `format_percent()`, and `format_cost()`)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/metadata_adapter.py]` (Refactor to emit pre-localized SDUI blocks using `LocalizationService` for labels, dates, costs, and tokens)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/variance_adapter.py]`, `@[backend_v2/services/sdui/adapters/authenticity_adapter.py]`, `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]` (Refactor to decouple from `profile.metric_mappings` / `user_role_mappings`, eliminate `hasattr()` / `.get()` duct-tape, and resolve static labels and numeric formatting via `LocalizationService`)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]` and `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]` (Consume `matrix_synthesis_groups` instead of legacy `layouts`, resolving column headers via `LocalizationService`, eradicating `model_copy(update=)` in favor of explicit `MatrixScorecardRowDTO` instantiation)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/warning_card_adapter.py]` (Eradicate module-level `I18N_WARNING_STARVATION` instance containing deprecated `default_locale="en"`; resolve warning message dynamically via `LocalizationService`)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` (Eradicate hardcoded `PRINTABLE_SOURCES_RULES` translation dictionary and lazy ternary fallback `locale if locale in ('fi', 'en') else 'en'`; resolve headers strictly via `LocalizationService`)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]` (Refactor extension label resolution to decouple from `profile.extension_labels`, resolve strictly via `LocalizationService`, and eradicate silent `except ValueError: continue` nielut in favor of explicit enum membership validation)
- `[MODIFY]` `@[backend_v2/services/pdf_generator.py]` (Verify and lock `undefined=jinja2.StrictUndefined` environment configuration; register Fail-Fast helper `_raise_unrecognized_sdui_block` in `self.env.globals["raise_unrecognized_sdui_block"]`, enforce pre-flight assertion on `inner_sdui_blocks`)
- `[MODIFY]` `@[backend_v2/templates/report_template.jinja2]` (Ensure all table column headers, metadata labels, and legends resolve strictly via pre-localized DTOs and `l10n` context dictionary; purge hardcoded Finnish string `N/A (Ei arvioitu)` on L159; update footer pagination to language-neutral `counter(page) " / " counter(pages);` (`1 / 5`); purge hardcoded strings `Warning:`, `Meta Costs`, `Meta Tokens`, `(Lähde: ...)`; purge lazy fallback ternaries `if l10n is defined else '...'` across all 11 instances in favor of direct `{{ l10n.<key> }}` references backed by `StrictUndefined`; purge legacy HTML error card `V2 ARCHITECTURE VIOLATION`; add strict `{% else %}` unknown block handler calling `raise_unrecognized_sdui_block`)
- `[MODIFY]` `@[backend_v2/worker.py#L593-L1364]` (Update background synthesis job loop to iterate over `profile.matrix_synthesis_groups`)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]` (Update studio layout editor to bind to `matrix_synthesis_groups`)
- `[NEW]` `@[backend_v2/tests/fixtures/sdui_golden_master.json]` (Comprehensive synthetic SDUI test dataset containing instances of specifically all 17 `AnySduiBlock` variants with citations, titles, and localized metadata)
- `[NEW]` `@[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]` (AST guardrail suite locking pure theory grounding invariants)
- `[NEW]` `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]` (AST guardrail suite asserting zero occurrences of `default_locale`, `EPISTEMIC ANCHOR:`, and legacy `layouts` dictionaries in seed vault)
- `[MODIFY]` `@[backend_v2/tests/unit/test_localization.py]` (Extend existing unit test suite verifying `LocalizationService` translation lookups, fallback behaviors, and formatting helpers)
- `[NEW]` `@[backend_v2/tests/unit/test_backend_l10n_internal_parity.py]` (Parity test suite asserting 1:1 key parity between `backend_v2/l10n/en.json` and `backend_v2/l10n/fi.json`, and asserting all `l10n.*` references in `report_template.jinja2` exist in backend dictionaries)
- `[NEW]` `@[backend_v2/tests/unit/test_sdui_template_parity.py]` (Presentation parity test suite: AST lohkokattavuusvahti asserting 100% handling in Jinja and Dart, Jinja AST field attribute validator, and BeautifulSoup semantic DOM extractor)
- `[NEW]` `@[client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart]` (Flutter widget test verifying that `SduiBlocksRenderer` renders all semantic elements of `sdui_golden_master.json`)
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` and `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]` (Update test assertions for pure `<theory_context>` XML formatting)
- `[MODIFY]` `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_workflows.py]`, `@[backend_v2/tests/unit/services/test_blueprint.py]` (Migrate test fixtures to new `I18nText` and `OutputProfile` schemas and remove obsolete `metric_mappings` mocks)
- `[NEW]` `@[client_app_v2/test/shared/models/i18n_text_test.dart]` (Unit test suite asserting Flutter `I18nText` Fail-Fast `AppException.validation`, fallback resolution, CheckedFromJsonException on missing translations key, negative ISTQB partition testing throwing `CheckedFromJsonException` on legacy `default_locale` key, and `isEmpty`/`isNotEmpty`/`has` helpers)
- `[MODIFY]` `@[client_app_v2/test/features/studio/views/widgets/profile/tabs/profile_layouts_tab_test.dart]` (Update Flutter widget test suite to bind to `matrixSynthesisGroups`)
- `[MODIFY]` `@[client_app_v2/test/models/matrix_claim_test.dart]` (Update assertions to test `I18nText` without `defaultLocale`)
- `[MODIFY]` `@[client_app_v2/test/features/studio/models/workflow_test.dart]` (Update workflow mock fixtures for modernized `I18nText` schema)
- `[MODIFY]` `@[client_app_v2/test/features/execution/models/matrix_scorecard_dto_test.dart]` (Update scorecard mock fixtures for modernized `I18nText` schema)
- `[MODIFY]` `@[.agents/rules/01-python-backend.md]` (Update `frozen_state_mutability` rule block to explicitly ban `setattr(...)`, `object.__setattr__(...)`, and `__setattr__()` mutations on Pydantic models and frozen entities)
- `[MODIFY]` `@[scripts/_ast_guardrails.py]` (Extend QGR001 in `QuorumGuardrailVisitor.visit_Call` to ban `setattr` and `object.__setattr__` mutation calls across codebase)

### 2.2 CONTEXT Files (Read-Only)
- `@[backend_v2/models/v2_core.py#L112-L125]` (`TheoryGrounding` schema SSOT)
- `@[backend_v2/settings.py]` (Backend global configuration SSOT)

---

## 3. Technical Debt Itemization & Pre-Implementation Remediation

### 3.1 Layered Technical Debt Remediation Architecture (`touched_scope_tech_debt_mandate`)
Per `touched_scope_tech_debt_mandate` and the 5-Tier Regression Defense Architecture (`five_tier_regression_defense_mandate`), all technical debt and anti-patterns across touched target files and their immediate 1-hop dependencies MUST be itemized and remediated as explicit pre-requisite cleanups in **Phase 1** *before* introducing structural domain mutations or functional feature logic in subsequent phases.

Specifically and exhaustively, all technical debt cleanups are deterministically allocated into **Phase 1 Pre-requisite Cleanups** across four comprehensive scopes:
1. **Prompt & Theory Grounding Scope**: Eradicate banned `.get()` duck-typing and silent empty string fallbacks in `I18nText` validation/resolution logic (`v2_core.py#L101-L191`), purge redundant ternaries (`locale == 'fi' ? get('fi') : get('en')`) in Flutter execution widgets (`atom_matrix_table_widget.dart`, `matrix_row_item_widget.dart`), purge ephemeral block factories (`_create_ephemeral_block`) and fake block IDs in `matrix_sensor_prompt_builder.py`, and eliminate raw URL prompt leakage.
2. **SDUI Presentation Adapters Scope**: Eradicate module-level `I18N_WARNING_STARVATION` in `warning_card_adapter.py` (migrating to dynamic `LocalizationService` resolution to prevent import-time crashes), eradicate hardcoded `PRINTABLE_SOURCES_RULES` and lazy fallback ternaries in `printable_sources_adapter.py`, eradicate `model_copy(update=)` on scorecard rows in `matrix_graphs_adapter.py` in favor of explicit `MatrixScorecardRowDTO` instantiation, eradicate silent `except ValueError: continue` nielut in `xai_highlights_adapter.py` in favor of typed enum validation, and eradicate `hasattr()` / `.get()` duck-typing across `variance_adapter.py`, `authenticity_adapter.py`, and `executive_summary_adapter.py`.
3. **Flutter UI Chrome & Presentation Widgets Scope**: Replace hardcoded `Color(0xFF2E7D32)` with `Theme.of(context).colorScheme.primary` and generic `throw Exception(...)` with `throw AppException.validation(...)` in `profile_editor_view.dart`, replace manual `url.substring(0, 40)` clipping with declarative `TextOverflow.ellipsis` in `xai_evidence_box.dart`, replace local `isEmptyI18n()` helper with SSOT `i18nText.isEmpty` in `output_profile_controller.dart`, and migrate execution-tier UI hardcoded text in `human_override_dialog.dart`, `execution_report_view.dart`, and `specialist_section.dart` to `AppLocalizations`.
4. **AST Guardrail Engine & Backend Invariants Scope**: Extend rule `QGR001` in `scripts/_ast_guardrails.py` to ban `setattr(...)` and `object.__setattr__(...)` in-place model mutations across the codebase, and update `.agents/rules/01-python-backend.md` (`frozen_state_mutability`) to lock this architectural ban.

### 3.2 Exhaustive Technical Debt Inventory
Specifically and exhaustively, the following 25 technical debt items are identified for remediation:
1. **Duplicate Theory Anchors in Seed Vault (Chapter 2)**: All 13 matrix blocks in `seed_data.json` duplicate bibliographic text in `ai_description`, creating token bloat and risk of semantic drift.
2. **Missing CDATA Breakout Shielding on Theory Context Prompts**: `MatrixSensorPromptBuilder` formats `<theory_context>` and `<matrix_objective>` via raw f-string interpolation without `TemplateProcessor.safe_interpolate()` CDATA Breakout Shielding, risking XML injection and prompt syntax corruption.
3. **URL Token Bloat & Prompt Leakage**: Raw `source_url` strings are emitted in LLM prompt payloads rather than reserved exclusively for client UI rendering and PDF reports.
4. **Redundant `default_locale` in `I18nText` (Chapter 3)**: 500 `I18nText` blocks in `seed_data.json` declare `"default_locale": "fi"`, conflicting with runtime context-driven language selection. Empirical audit verifies that all 500 records already contain valid, non-empty `"en"` translations (0 missing `"en"`, 496 with both `"fi"` and `"en"`, 4 with only `"en"`).
5. **Static UI Dictionaries in Database (Chapter 5)**: `OutputProfile` contains `metric_mappings`, `user_role_mappings`, and `extension_labels` (and `OutputLayoutBlock` contains `matrix_column_labels`) in backend persistence, violating Dual-Axis Localization.
6. **Backend String Concatenation in `MetadataAdapter`**: `MetadataAdapter` combines translated labels with values in Python strings, breaking the Dumb Painter paradigm.
7. **Obsolete V1 `layouts` Arrays**: `OutputProfile.layouts` retains deprecated fields (`preset_view`, `text_delivery_mode`, `steps: []`, `matrix_column_labels`) instead of a focused `matrix_synthesis_groups` structure.
8. **Worker Couplings on `layouts`**: `worker.py` and SDUI adapters depend on `profile.layouts` for synthesis loop routing.
9. **Flutter Freezed Schema Drift**: `i18n_text.dart` and `output_profile.dart` Freezed models reflect deprecated fields, requiring regeneration via `build_runner`.
10. **Test Fixture Schema Drift & Deterministic Scripted Migration (Chapter 6)**: 1,166 occurrences of `default_locale` across 90 test files in `backend_v2/tests/` (including `test_blueprint.py`, `test_llm.py`, `test_dag_executor.py`, `test_matrix_graphs_adapter.py`, `test_studio.py`, `test_variance_adapter.py`, `test_worker_synthesis.py`, `test_simulation_service.py`, `test_epic_chain_e2e.py`, and `test_scoring.py`) and 157 occurrences of `defaultLocale` across 25 Flutter test files hardcode `default_locale` or legacy profile layout keys. To prevent Context Amnesia and token exhaustion from opening 90+ files during Tier 2 execution, these are modernized via deterministic AST/regex scratch scripts (`scratch/migrate_backend_i18n_fixtures.py` and `scratch/migrate_flutter_i18n_fixtures.py`).
11. **Missing AST Guardrails for Seed Vault Purity**: The test suite lacks static AST assertions preventing re-introduction of `default_locale` or `EPISTEMIC ANCHOR:` tails.
12. **Unsynchronized Local Database State**: `db_v2.json` must be re-seeded atomically after `seed_data.json` mutations.
13. **Flutter `I18nText` & `MatrixSynthesisGroup` Fail-Fast Freezed Strictness, Negative ISTQB Partition Testing & Widget Ternary Drift**: `i18n_text.dart` and `output_profile.dart` must declare explicit `@JsonSerializable(disallowUnrecognizedKeys: true)` annotations on all Freezed factory constructors (`I18nText`, `MatrixSynthesisGroup`, `OutputProfile`, `SynthesisConfigDTO`) to enforce Defense-in-Depth code-level schema strictness and prevent reliance solely on implicit `build.yaml` options. `i18n_text.dart` must define `required Map<String, String> translations` without `@Default` to prevent masking missing deserialization keys, `get()` must throw `AppException.validation` on missing translations instead of returning `''`, and dedicated negative ISTQB test suites (`i18n_text_test.dart` and `output_profile_test.dart`) must explicitly verify that passing legacy keys (`default_locale`, `layouts`, `metric_mappings`, `user_role_mappings`, `extension_labels`, `preset_view`) triggers `CheckedFromJsonException`, while `atom_matrix_table_widget.dart` and `matrix_row_item_widget.dart` hardcode `locale == 'fi' ? get('fi') : get('en')` instead of delegating directly to `get(locale)`.
14. **Studio Ad-Hoc `isEmptyI18n` Functions**: `output_profile_controller.dart` implements local ad-hoc `isEmptyI18n()` functions due to missing SSOT `isEmpty`/`isNotEmpty` properties on `I18nText`.
15. **Banned Python `.get()` Duck-Typing, Silent Fallbacks & Frozen Mutation Anti-Pattern in `I18nText`**: `backend_v2/models/v2_core.py#L101-L191` uses `.get()` duck-typing and silent fallback returns (`return ""`, `fallback=""`). These must be completely eradicated in favor of explicit `in` membership checks, sanitized non-empty validation in `@field_validator("translations")` (strictly avoiding `@model_validator(mode="after")` and `object.__setattr__` frozen mutations), required `translations: Annotated[dict[str, str], Field(...)]` (no `default_factory=dict`), and Fail-Fast `AppException` error propagation.
16. **SDUI Adapter & Studio Presentation Technical Debt**: SDUI adapters and studio views contain anti-patterns including hardcoded translation dictionaries in `PrintableSourcesAdapter`, lazy locale ternaries (`locale if locale in ('fi', 'en') else 'en'`), unvalidated `model_copy(update=)` in `MatrixGraphsAdapter` (which must be eradicated and replaced with explicit `MatrixScorecardRowDTO` instantiation), silent exception swallowing in `XaiHighlightsAdapter` (`except ValueError: continue` which must be replaced with typed enum membership checks), hardcoded `Color(0xFF2E7D32)` and `throw Exception` in `profile_editor_view.dart`, manual `substring(0, 40)` clipping in `xai_evidence_box.dart`, and tight couplings to `profile.metric_mappings` / `profile.extension_labels`.
17. **Critical Import-Time Crash in `WarningCardAdapter`**: `@[backend_v2/services/sdui/adapters/warning_card_adapter.py]` instantiates `I18N_WARNING_STARVATION = I18nText(default_locale="en", ...)` at module level. When `default_locale` is removed from `I18nText` (`extra="forbid"`), the backend will crash on import during Phase 2 test runs unless `WarningCardAdapter` is migrated to `LocalizationService` atomically in Phase 2 Step 2.1.
18. **Hardcoded Strings, English Footer & Lazy Fallback Ternaries in Jinja PDF Template**: `backend_v2/templates/report_template.jinja2` hardcodes Finnish string `N/A (Ei arvioitu):` on L159, hardcodes English footer pagination `"Page " counter(page) " of " counter(pages);` on L11, hardcodes labels (`Warning:`, `Meta Costs`, `Meta Tokens`, `(Lähde: ...)`, `Lainaukset (quotes)`), and uses `if l10n is defined else '...'` across 11 occurrences (L225, L238, L242, L244, L251, L256, L319-324, L434, L435), causing unlocalized ghost strings in English PDF reports and circumventing `StrictUndefined`. All fallback ternaries must be eradicated in favor of direct `l10n.<key>` lookups, and missing translation keys must immediately raise `AppException(INTERNAL_SERVER_ERROR)`.
19. **Missing AST Guardrails for SDUI Presentation Parity**: The test suite lacks a static AST guardrail asserting that 100% of `AnySduiBlock` variants are handled in both `report_template.jinja2` and `sdui_blocks_renderer.dart`, allowing silent drops when new blocks are introduced.
20. **Missing Cross-Platform Semantic Golden Master Parity Test**: There is no automated test asserting that the exact same SDUI payload renders identical semantic text, headings, citations, and numbers across both PDF Jinja HTML and Flutter desktop widgets.
21. **Missing Finnish Translations in Synthesis Seed Blocks**: 4 text fields in `seed_data.json` (`prompt_blocks[88].label`, `prompt_blocks[88].description`, `prompt_blocks[89].label`, `prompt_blocks[89].description`) contain only `"en"` translations and lack `"fi"` keys. Authentic Finnish translations must be populated during seed vault modernization to achieve 100% bilingual parity.
22. **Hardcoded Finnish & English Strings in Flutter Execution UI**: `client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart`, `execution_report_view.dart`, and `specialist_section.dart` hardcode Finnish dialog titles (`👨‍⚖️ Yliohjaa päätös`), form labels (`Uusi arvosana`, `Perustelu yliohjaukselle`), action buttons (`Lisää todiste`, `Peruuta`, `Tallenna Override`, `Lataa Excel`), tooltips (`Lataa Frozen Context`), and validation snackbars (`Perustelu on pakollinen.`), breaching enterprise localization parity.
23. **Zombie DTO Eradication (`OutputLayoutBlock`)**: `OutputLayoutBlock` (11 fields, Literals) in `v2_core.py`, `output_profile.py`, and `output_profile.dart` becomes dead code with 0 runtime callers upon `layouts` deprecation. Leaving it violates `the_no_legacy_mandate` and pollutes context windows. It must be explicitly deleted across Python and Flutter, and AST assertions in `test_enum_parity.py` retired.
24. **Matrix Synthesis Group Degenerate Target Prevention & Contextual Profile Coherence**: `MatrixSynthesisGroup.target_blocks` must enforce `min_length=1` to guarantee that declared synthesis groups target at least one matrix, preventing degenerate LLM synthesis prompts. `OutputProfile` must enforce via `@model_validator(mode="after")` that if `TargetBlockType.MATRIX_GRAPHS_BLOCK` is present in `target_block_order`, `matrix_synthesis_groups` is non-empty.
25. **AST Guardrail Gap & Rule Enforcement for Frozen Model In-Place Mutations**: `scripts/_ast_guardrails.py` (QGR001) only checks `getattr` and `hasattr`. It must be extended to ban `setattr(...)` and `object.__setattr__(...)`, while `.agents/rules/01-python-backend.md` (`frozen_state_mutability`) must be updated to explicitly lock this ban against frozen Pydantic models.

---

## 4. Architectural Impact & Compliance Matrix

### 4.1 Deprecations & Sunset List (`What We Will REMOVE`)
| Deprecated Symbol / Pattern | Location | Replacement / Disposition |
| :--- | :--- | :--- |
| `EPISTEMIC ANCHOR:` prompt tails | `@[backend_v2/seed/seed_data.json#L336-L6900]` | **PURGED**. Retained exclusively in structured `theory_grounding` field. |
| Raw `source_url` in LLM prompts | `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]` | **OMITTED** from LLM prompt payload; retained in DTOs for UI/PDF rendering. |
| `I18nText.default_locale` | `@[backend_v2/models/v2_core.py]`, `@[client_app_v2/lib/shared/models/i18n_text.dart]` | **PURGED**. Replaced by dynamic runtime parameter `target_locale` with `"en"` fallback. |
| `I18nText` `@Default` / `default_factory=dict` on `translations` | `@[backend_v2/models/v2_core.py]`, `@[client_app_v2/lib/shared/models/i18n_text.dart]` | **PURGED**. Replaced by `required Map<String, String> translations` (Dart) and `translations: dict[str, str] = Field(...)` (Python) to guarantee Fail-Fast deserialization. |
| `I18nText.get(fallback="")` & `.get()` duck-typing | `@[backend_v2/models/core_base.py#L39-L140]` | **PURGED**. Replaced by explicit `if key in dict:` membership checks and strict `resolve()`. |
| `OutputProfile.metric_mappings` | `@[backend_v2/seed/seed_data.json#L9180-L9570]`, `@[backend_v2/models/v2_core.py#L937-L1076]` | **PURGED**. Replaced by frontend `.arb` files (UI Chrome) and `backend_v2/l10n/*.json` (PDF/SDUI rendering). |
| `OutputProfile.user_role_mappings` | `@[backend_v2/seed/seed_data.json#L9180-L9570]`, `@[backend_v2/models/v2_core.py#L937-L1076]` | **PURGED**. Replaced by frontend `.arb` files (UI Chrome) and `backend_v2/l10n/*.json` (PDF/SDUI rendering). |
| `OutputProfile.extension_labels` | `@[backend_v2/seed/seed_data.json#L9180-L9570]`, `@[backend_v2/models/v2_core.py#L937-L1076]` | **PURGED**. Replaced by frontend `.arb` files (UI Chrome) and `backend_v2/l10n/*.json` (PDF/SDUI rendering). |
| `OutputProfile.layouts` | `@[backend_v2/seed/seed_data.json#L9180-L9570]`, `@[backend_v2/models/v2_core.py#L937-L1076]` | **PURGED**. Replaced by clean `matrix_synthesis_groups` domain model. |
| `class OutputLayoutBlock(V2CoreBase)` & Freezed class | `@[backend_v2/models/v2_core.py#L937-L1076]`, `@[backend_v2/models/dtos/output_profile.py]`, `@[client_app_v2/lib/features/studio/models/output_profile.dart]` | **PURGED**. Completely deleted from Python domain, `__all__` export, DTOs, and Dart Freezed (`the_no_legacy_mandate`). |
| `OutputLayoutBlock` AST parity assertions (`test_preset_view_parity`, `test_text_delivery_mode_parity`) | `@[backend_v2/tests/unit/test_enum_parity.py#L86-L98,L121-L134]` | **PURGED**. Retired along with deleted layout model. |
| `model_copy(update=)` in SDUI presentation adapters | `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]` | **PURGED**. Replaced by explicit `MatrixScorecardRowDTO` instantiation to preserve strict Pydantic validation. |
| Hardcoded `Color(0xFF2E7D32)` in Studio / Widgets | `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L135]` | **PURGED**. Replaced by `Theme.of(context).colorScheme.primary`. |
| Manual `url.substring()` clipping | `@[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart#L344]` | **PURGED**. Replaced by declarative `TextOverflow.ellipsis`. |
| Silent `except ValueError: continue` nielut | `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py#L98]` | **PURGED**. Replaced by explicit `XaiExtensionType` enum membership verification. |

### 4.2 Retained SSOT Invariants (`What We Will RETAIN`)
1. **Qualitative Coaching Philosophy (`prompt_preservation_mandate`)**: Prompt texts in `seed_data.json` (specifically `OBJECTIVE:`, `ROLE:`, `TASK:`, `MANDATE:`, `<role_enforcement>`, and `<banned_concepts>` sections) are strictly preserved verbatim.
2. **Deterministic UI/PDF Provenance**: `PromptBlock.theory_grounding` retains full metadata (`source_url`, `citation_reference`) for Server-Driven UI (SDUI) and PDF report rendering.
3. **Pydantic V2 Strictness (`strict_pydantic_v2_rust`)**: All DTOs and models enforce `ConfigDict(strict=True, extra="forbid")`.
4. **Dual-Axis Localization SSOT**: Backend manages dynamic data translation; frontend manages static structural labels via `.arb` files.
5. **Universal Zero-Legacy & Clean Slate Database Reset Mandate (`the_no_legacy_mandate`, `local_data_ephemeral_nature`)**: Quorum strictly enforces universal Zero-Legacy across all environments (development, staging, production). Backwards-compatibility shims, legacy layout structures, and fallback chains are strictly prohibited in domain models and API contracts. In accordance with `feature_audit_clean_slate_db_wipe.md`, **no stateful database migration scripts or historical data patches are implemented**. All historical live and runtime database records (`db_v2.json`, Firestore collections) are intentionally destroyed/wiped. All schema evolutions (Pydantic V2 DTOs, Dart Freezed models, Seed Vault, and test fixtures) are executed as atomic, synchronized transactions (`Atomic Migration Protocol`). The database state is deterministically initialized on a clean slate via `uv run python backend_v2/seed/run_seed.py local` directly from the sanitized `seed_data.json` vault. Dedicated client version deployment gates (`X-Min-Client-Version` middleware) are acknowledged for post-development release infrastructure but are intentionally excluded from active development workflows.
6. **Flat Modular SDUI Presentation & Synthesis Scope Parity**: All report blocks (`METADATA_BLOCK`, `EXECUTIVE_SUMMARY_BLOCK`, `SYNTHESIS_TEXT_BLOCK`, `MATRIX_GRAPHS_BLOCK`, `GROUPED_EXTENSIONS_BLOCK`, `PENALTIES_BLOCK`, `MATRIX_SUMMARY_TABLE_BLOCK`, `VARIANCE_VALIDATION_BLOCK`, `AUTHENTICITY_EVALUATION_BLOCK`, `PRINTABLE_SOURCES_BLOCK`, `GLOBAL_SCORE_BLOCK`, `AUDIT_TRAIL_BLOCK`) reside on the exact same flat, modular plane where rendering order and presence are 100% dynamically customizable via `OutputProfile.target_block_order`. The distinction between Executive Summary and Matrix Synthesis is strictly about Synthesis Scope (Global vs Group-specific), not a fixed rendering hierarchy. Studio users can freely drag and drop or reorder blocks in `target_block_order`.

---

## 5. Phased Implementation Plan

### Phase 1: Theory Grounding & Epistemic Anchor Sanitization (Chapter 2)

#### Pre-Implementation Technical Debt Cleanups (Comprehensive Touched Scope Sweep - Phase 1 Pre-requisite)
Before modifying prompt builder logic, mutating seed payloads, or executing structural schema migrations, execute the following technical debt sweeps and baseline assertions across specifically all touched targets:

1. **Prompt & Theory Grounding Scope**:
   - **Audit `v2_core.py#L101-L191` & Remove Banned `.get()` Duck-Typing**: Eliminate `.get()` dictionary lookups in `I18nText` validation and resolution logic, replacing them with explicit `in` membership checks and sanitized non-empty assertions.
   - **Audit Flutter Execution Widgets & Remove Redundant Ternaries**: Prepare `atom_matrix_table_widget.dart` and `matrix_row_item_widget.dart` by replacing hardcoded `locale == 'fi' ? get('fi') : get('en')` ternaries with direct `get(locale)` delegation.
   - **Purge Ephemeral Block Factories & Fake IDs**: Eradicate `_create_ephemeral_block` helper and fake IDs (`blk_1111...`, `blk_2222...`, `blk_3333...`) in `matrix_sensor_prompt_builder.py`, assembling static instructions directly via `TemplateProcessor.safe_interpolate()`.
   - **Verify AST Baseline for Prompt Builder**: Assert that `MatrixSensorPromptBuilder` currently calls `model_dump_json()` and prepare AST test assertions in `test_ast_theory_grounding_guardrails.py` to prevent regression.

2. **SDUI Presentation Adapters Scope**:
   - **Synchronous Module-Level Constant Migration (`warning_card_adapter.py`)**: Eliminate module-level `I18N_WARNING_STARVATION = I18nText(default_locale="en", ...)` to prevent import-time Pydantic `ValidationError` upon `default_locale` removal, resolving warning messages dynamically via `LocalizationService.translate('alert_starvation_insufficient_data', context.locale)`.
   - **Eradicate Hardcoded Translation Dictionaries & Lazy Ternaries in `PrintableSourcesAdapter`**: Remove `PRINTABLE_SOURCES_RULES` dictionary and lazy fallback `locale = context.locale if context.locale in ("fi", "en") else "en"`, resolving header titles strictly via `LocalizationService.translate("sources_and_bibliography_title", context.locale)`.
   - **Eradicate `model_copy(update=)` in `MatrixGraphsAdapter`**: Replace `axes = [axis.model_copy(update={"inner_sdui_blocks": []}) for axis in axes]` with explicit `MatrixScorecardRowDTO` instantiation, ensuring full Pydantic validation:
     ```python
     axes = [
         MatrixScorecardRowDTO(
             axis_name=axis.axis_name,
             score=axis.score,
             score_normalized=axis.score_normalized,
             score_color=axis.score_color,
             confidence_badge=axis.confidence_badge,
             raw_quote=axis.raw_quote,
             row_explanation=axis.row_explanation,
             distribution_shape=axis.distribution_shape,
             inner_sdui_blocks=[],
         )
         for axis in axes
     ]
     ```
   - **Decouple `XaiHighlightsAdapter` & Eradicate Silent Nielut**: Migrate extension accordion titles to resolve strictly through `LocalizationService.translate(f"ext_{ext_enum.value.lower()}", context.locale)`. Eradicate silent `except ValueError: logger.warning(...); continue` in favor of explicit enum membership validation (`if item.extension_type not in XaiExtensionType._value2member_map_:`), logging an RFC 7807 error before skipping.
   - **Decouple `VarianceAdapter`, `AuthenticityAdapter`, `ExecutiveSummaryAdapter`**: Eradicate `hasattr()` and `.get()` duck-typing, resolving labels and numeric formatting strictly via `LocalizationService`.

3. **Flutter UI Chrome & Presentation Widgets Scope**:
   - **`profile_editor_view.dart`**: Replace hardcoded `backgroundColor: const Color(0xFF2E7D32)` with `backgroundColor: Theme.of(context).colorScheme.primary`, and replace generic `throw Exception("Workflow ID is missing")` with `throw AppException.validation(l10n.workflowIdMissingError);`.
   - **`xai_evidence_box.dart`**: Purge manual `url.substring(0, 40)` clipping in favor of declarative `TextOverflow.ellipsis`.
   - **`output_profile_controller.dart`**: Replace local ad-hoc `isEmptyI18n(text)` with SSOT property `text?.isEmpty ?? true`.
   - **Execution UI Hardcoded Strings Sweep**: Migrate hardcoded Finnish and English strings in `human_override_dialog.dart`, `execution_report_view.dart`, and `specialist_section.dart` to `AppLocalizations` (`app_en.arb` and `app_fi.arb`).

4. **AST Guardrail Engine & Backend Invariants Scope**:
   - **AST Guardrail Extension (`scripts/_ast_guardrails.py`)**: Extend rule `QGR001` in `QuorumGuardrailVisitor.visit_Call` to detect and fail fast on `ast.Name(id="getattr" | "hasattr" | "setattr")` and `ast.Attribute(value=ast.Name(id="object"), attr="__setattr__")`, preventing frozen mutation anti-patterns across the codebase.
   - **Rule Synchronization (`01-python-backend.md`)**: Update `frozen_state_mutability` in `.agents/rules/01-python-backend.md` to explicitly ban in-place model mutations using `setattr(...)`, `object.__setattr__(...)`, or `__setattr__()` on Pydantic models or frozen domain entities.

#### Step 1.1: Backup Seed Vault (`vault_mutation_protocol`)
Ensure directory `backend_v2/seed/backups/` exists and execute backup command:
`New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_epic148_cleanup.json`

#### Step 1.2: Deterministic Seed Vault Sanitization across all 13 Matrix Blocks
Surgically sanitize the `ai_description` field across specifically and exhaustively all 13 matrices in `@[backend_v2/seed/seed_data.json#L336-L6900]`:
1. `blk_440a5fef9331451b` (matrix_toulmin): Remove `EPISTEMIC ANCHOR:\nToulmin, S. E. (2003)...`
2. `blk_f921c7c0989b47e8` (matrix_bloom): Remove `EPISTEMIC ANCHOR:\nAnderson, L. W., & Krathwohl...`
3. `blk_109dab5b6b3f403a` (matrix_kahneman): Remove `EPISTEMIC ANCHOR:\nKahneman, D. (2011)...`
4. `blk_53f32679aa514fcb` (matrix_goodhart): Remove `EPISTEMIC ANCHOR:\nStumborg, M. F., et al...`
5. `blk_fb15f8dcf23f4865` (matrix_archivist): Remove `EPISTEMIC ANCHOR:\nARMA International...`
6. `blk_c5804a9143c34cb1` (matrix_causal_analyst): Remove `EPISTEMIC ANCHOR:\nPearl, J. 'The Book of Why...`
7. `blk_b476f89fb732448c` (matrix_falsifier): Remove `EPISTEMIC ANCHOR:\nKarl Popper's Theory of Falsification...`
8. `blk_ff72c2d79edb4ebf` (matrix_judge): Remove `EPISTEMIC ANCHOR:\nW. Edwards Deming...`
9. `blk_6b8c766185294f7e` (matrix_xai_reporter): Remove `EPISTEMIC ANCHOR:\nDARPA XAI Program (2017)...`
10. `blk_80732a33fe1947ee` (matrix_taskguard): Remove `EPISTEMIC ANCHOR:\nAnchored in the OWASP Top 10...`
11. `blk_c3bc5f3eb8e74110` (matrix_causal_abductive): Remove `EPISTEMIC ANCHOR:\nAnchored in Judea Pearl's 'The Book of Why'...`
12. `blk_f6e286f050c94d60` (matrix_taskxai_clarity): Remove `EPISTEMIC ANCHOR:\nAnchored in Zachary C. Lipton's 'The Mythos of Model Interpretability'...`
13. `blk_22e3598e06414409` (matrix_epistemic_humility): Remove `EPISTEMIC ANCHOR:\nGrounded in Kahneman's Dual Process Theory...`

Preserve all `OBJECTIVE:`, `ROLE:`, `TASK:`, `MANDATE:`, `<role_enforcement>`, and `<banned_concepts>` sections intact per `prompt_preservation_mandate`.

#### Step 1.3: Format Pure `<theory_context>` in `MatrixSensorPromptBuilder` via Direct `TemplateProcessor` Assembly (Zero Ephemeral Blocks)
In `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L26-L75]` and `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L77-L208]`:
Refactor theory grounding and matrix objective injection in `MatrixSensorPromptBuilder.build_caching_prefix`:
1. **Eradicate `_create_ephemeral_block` & Fake Block IDs**: Completely delete the `_create_ephemeral_block` helper method and purge all artificial `blk_1111...`, `blk_2222...`, `blk_3333...` IDs. Creating fake in-memory `SystemRulePromptBlock` entities violates domain modeling sovereignty, causes duplicitous `<STATIC_INSTRUCTION>` tag nesting via `LocalizationCompiler`, and triggers fatal `ValidationError` crashes once `default_locale` is removed from `I18nText`.
2. **Direct TemplateProcessor Interpolation**: Assemble the static system instructions directly from `GLOBAL_MANDATES_XML`, `MATRIX_SENSOR_SYSTEM_PROMPT`, and conditionally interpolated `<matrix_objective>` / `<theory_context>` XML sections. Enforce the universal **Zero-XML Paradigm** (`compiler_xml_sovereignty_mandate` & `zero_xml_ui_paradigm`): all UI and database fields store exclusively pure, unadorned text, while the builder performs Just-in-Time XML tag framing and CDATA encapsulation with Breakout Shielding (`_apply_breakout_shield` replacing `]]>` with `]]]]><![CDATA[>`), completely excluding URL token bloat:
```python
@staticmethod
def build_caching_prefix(
    context_text: str,
    matrix_context: MatrixEvaluationContext | None = None,
) -> CompiledPrompt:
    """Builds the cacheable prefix containing system instructions and context.

    Args:
        context_text: The source text (specifically: transcript, article).
        matrix_context: Context containing optional framework/evaluation rules.

    Returns:
        CompiledPrompt with static system instructions and source text context.
    """
    # 1. Base Layer: Global Mandates & Matrix Sensor System Prompt
    system_sections = [
        GLOBAL_MANDATES_XML.strip(),
        MATRIX_SENSOR_SYSTEM_PROMPT.strip(),
    ]

    # 2. Contextual Rules: Matrix Objective & Theory Grounding (Just-in-Time CDATA formatting)
    if matrix_context:
        if matrix_context.matrix_objective and matrix_context.matrix_objective.strip():
            # Just-in-time CDATA encapsulation for matrix objective text
            obj_content = TemplateProcessor.safe_interpolate(
                "<matrix_objective>\n{obj}\n</matrix_objective>",
                obj=matrix_context.matrix_objective.strip(),
            )
            system_sections.append(obj_content)

        if matrix_context.theory_grounding and matrix_context.theory_grounding.citation_reference:
            citation = matrix_context.theory_grounding.citation_reference.strip()
            if citation:
                # Just-in-time CDATA encapsulation for pure academic citation (omitting raw URLs)
                theory_content = TemplateProcessor.safe_interpolate(
                    "<theory_context>\n{citation}\n</theory_context>",
                    citation=citation,
                )
                system_sections.append(theory_content)

    system_content = "\n\n".join(system_sections)
    context_content = TemplateProcessor.safe_interpolate("<context>\n{c}\n</context>", c=context_text)

    return CompiledPrompt(
        static_messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": context_content},
        ],
        dynamic_messages=[],
    )
```
*Note on Runtime CDATA Output*: `TemplateProcessor.safe_interpolate` automatically wraps interpolated keyword arguments in `<![CDATA[...]]>`, producing the deterministic output:
```xml
<theory_context>
<![CDATA[Anderson, L. W., & Krathwohl, D. R. (2001). A taxonomy for learning, teaching, and assessing.]]>
</theory_context>
```
*Architectural Invariant on Prompt Caching & Message Segregation*:
- **Static Prefix Integrity (`static_messages`)**: The source text (`context_content`, specifically the transcript or source article document) is identical across all parallel TDA evaluation chunks/waves for a given workflow execution. Placing it alongside static system rules in `static_messages` forms an immutable prefix (both system directives and source text context) that is pre-cached once in Vertex AI / Anthropic (`LLMCachingService.pre_cache_document`). This achieves a 100% cache hit rate for all parallel evaluation waves.
- **Dynamic Message Isolation (`dynamic_messages`)**: Per-batch evaluation claims, causal dependency states, and questions are assembled strictly in `build_compiled_prompt` and placed exclusively into `dynamic_messages=[{"role": "user", "content": user_content}]`. This guarantees that dynamic batch variations never invalidate the static document cache.
- **GCP Vertex AI Specification**: Vertex AI Context Caching (`CachedContent`) requires conversational context (`user`/`model` turns). Emitting `context_content` as a static user message ensures full compliance with GCP cached content API specifications without runtime failure.

#### Step 1.4: Unit Tests & Quality Gate for Phase 1
1. In `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` and `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]`: Update test assertions to verify clean `<theory_context>` and `<matrix_objective>` CDATA-shielded pure citation XML structure without raw URLs, without legacy `<STATIC_INSTRUCTION>` wrapping, and assert protection against XML injection characters (`<`, `>`, `&`, `]]>`) via test case `test_build_caching_prefix_theory_grounding_xml_injection_shield` (TC-TG-06).
2. Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py --test`.

---

### Phase 2: ATOMIC `I18nText` Modernization & Systemic Fixture Migration (Chapter 3)
*Atomic Transaction Mandate*: Steps 2.1 through 2.5 MUST be executed as a single coherent cycle before triggering the Quality Gate, guaranteeing zero `extra="forbid"` crashes across the 1300+ test suite and database seed.

#### Step 2.1: Python Domain Model Update (`v2_core.py`)
In `@[backend_v2/models/core_base.py#L39-L140]`:
1. Remove `default_locale` field from `I18nText`.
2. Define `translations: Annotated[dict[str, str], Field(description="Dictionary mapping locale code to translated string, specifically: {'fi': 'Teksti', 'en': 'Text'}." )]` without `default_factory=dict`, ensuring that instantiation without translations raises a Pydantic `ValidationError`.
3. Eradicate `@model_validator(mode="after")` and all `object.__setattr__` frozen mutation duct-tape. Implement a strictly typed `@field_validator("translations")` classmethod to sanitize all locale keys (`strip().lower()`) and validate non-empty string values before checking the baseline `"en"` Lingua Franca existence, returning the canonicalized dictionary directly into Pydantic V2's immutable Rust construction pipeline:
   ```python
    @field_validator("translations")
    @classmethod
    def validate_translations(cls, v: dict[str, str]) -> dict[str, str]:
        """Validates that English translation is always present and all translations are non-empty.

        Normalizes all locale keys by trimming whitespace and converting to lowercase before
        verifying baseline Lingua Franca ('en') presence and value non-emptiness.

        Args:
            v: The raw translations dictionary.

        Returns:
            The canonicalized dictionary with sanitized keys and values.

        Raises:
            ValueError: If 'en' is missing/empty, any translation contains only whitespace,
                        or a translation value is not a valid string.
        """
        if not v:
            raise ValueError("I18nText translations dictionary cannot be empty.")

        # 1. Sanitize and validate all translation entries first
        cleaned: dict[str, str] = {}
        for raw_key, raw_val in v.items():
            if not isinstance(raw_key, str) or not raw_key.strip():
                raise ValueError(f"I18nText locale key must be a non-empty string. Received key: {raw_key!r}")

            if not isinstance(raw_val, str) or not raw_val.strip():
                norm_key = raw_key.strip().lower()
                raise ValueError(f"I18nText translation for locale '{norm_key}' must be a non-empty string.")

            cleaned[raw_key.strip().lower()] = raw_val.strip()

        # 2. Enforce baseline fallback: canonical 'en' translation must ALWAYS exist and be non-empty
        if "en" not in cleaned or not cleaned["en"]:
            raise ValueError(
                "I18nText must contain a valid English ('en') translation as a baseline fallback. "
                f"Provided keys: {list(cleaned.keys())}"
            )

        return cleaned
   ```
4. Refactor `resolve()` method to enforce the Universal Fail-Fast mandate (`the_duct_tape_ban`, `zero_service_layer_fallbacks`, & `dynamic_translation_fail_fast`), utilizing regex locale parsing (`re.split(r"[-_]", ...)`) and explicit dictionary membership assertions (`in`) instead of `.get()` duck-typing:
   ```python
   def resolve(self, target_locale: str | None = None, fallback_locale: str = "en") -> str:
       """Strictly typed Fail-Fast resolution of localized text without .get() duck-typing.

       Args:
           target_locale: The requested locale code (specifically: 'fi', 'fi-FI', 'fi_FI', 'sv').
           fallback_locale: The baseline fallback locale (defaults to 'en').

       Returns:
           The resolved non-empty localized string.

       Raises:
           AppException: If neither target_locale nor fallback_locale can be resolved to a non-empty string.
       """
       # 1. Attempt Target Locale Match
       if target_locale:
           target_lang = re.split(r"[-_]", target_locale)[0].lower()
           if target_lang in self.translations:
               val = self.translations[target_lang]
               if val:
                   return val

       # 2. Attempt Fallback Locale Match
       fallback_lang = re.split(r"[-_]", fallback_locale)[0].lower()
       if fallback_lang in self.translations:
           fallback_val = self.translations[fallback_lang]
           if fallback_val:
               return fallback_val

       # 3. Fail-Fast: Structural Translation Error
       msg = (
           f"Fail-Fast Localization Error: Missing translation for target_locale='{target_locale}' "
           f"and fallback_locale='{fallback_locale}'. Available: {list(self.translations.keys())}"
       )
       logger.error("[I18nText] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
       raise AppException(
           message=msg,
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
       )
   ```
5. Deprecate and remove legacy `I18nText.get(lang_code, fallback="")` (purging default empty string returns) in favor of direct delegation to `resolve()`.
6. **Synchronous Module-Level Constant Migration (`warning_card_adapter.py`)**: To prevent import-time Pydantic `ValidationError` upon `default_locale` removal during the Phase 2 test suite execution, immediately migrate `WarningCardAdapter` in `@[backend_v2/services/sdui/adapters/warning_card_adapter.py]` to eliminate `I18N_WARNING_STARVATION` and resolve the warning message dynamically via `LocalizationService.translate('alert_starvation_insufficient_data', context.locale)`.
7. **Rule Synchronization (`01-python-backend.md`)**: Update `frozen_state_mutability` in `@[.agents/rules/01-python-backend.md]` to explicitly ban in-place model mutations using `setattr(...)`, `object.__setattr__(...)`, or `__setattr__()` on Pydantic models or frozen domain entities, mandating pre-instantiation `@field_validator` data sanitization and `.model_copy(update=...)` for state transitions.
8. **AST Guardrail Engine Extension (`scripts/_ast_guardrails.py`)**: Extend rule `QGR001` in `@[scripts/_ast_guardrails.py]` (`QuorumGuardrailVisitor.visit_Call`) to detect and fail fast on `ast.Name(id="getattr" | "hasattr" | "setattr")` and `ast.Attribute(value=ast.Name(id="object"), attr="__setattr__")`, preventing frozen mutation anti-patterns across the codebase.

#### Step 2.2: Flutter Freezed Model Update (`i18n_text.dart`), 1-Hop Caller Cleanups & Unit Tests
1. In `@[client_app_v2/lib/shared/models/i18n_text.dart]`:
   - Annotate factory constructor explicitly with `@JsonSerializable(disallowUnrecognizedKeys: true)` to enforce Defense-in-Depth code-level schema strictness and prevent silent deserialization of deprecated legacy keys.
   - Remove `@JsonKey(name: 'default_locale') @Default('en') String defaultLocale` from `I18nText` Freezed model.
   - Define `required Map<String, String> translations` without `@Default` (strictly purging `@Default` to guarantee that missing or null `translations` keys fail fast with `CheckedFromJsonException` during deserialization):
     ```dart
     @freezed
     abstract class I18nText with _$I18nText {
       const I18nText._();

       @JsonSerializable(disallowUnrecognizedKeys: true)
       const factory I18nText({
         required Map<String, String> translations,
       }) = _I18nText;

       factory I18nText.fromJson(Map<String, dynamic> json) =>
           _$I18nTextFromJson(json);
     ```
   - Add SSOT state helpers (`isEmpty`, `isNotEmpty`, `has(langCode)`):
     ```dart
     /// Returns true if translations map is empty or all values are empty whitespace.
     bool get isEmpty =>
         translations.isEmpty ||
         translations.values.every((v) => v.trim().isEmpty);

     /// Returns true if at least one non-empty translation exists.
     bool get isNotEmpty => !isEmpty;

     /// Checks if a non-empty translation exists for the given language code.
     bool has(String? langCode) {
       if (langCode == null || langCode.isEmpty) return false;
       final normalized = langCode.split(RegExp(r'[-_]')).first.toLowerCase();
       final val = translations[normalized];
       return val != null && val.trim().isNotEmpty;
     }
     ```
   - Update `get(String? langCode, {String fallback = 'en'})` method to enforce the Universal Fail-Fast mandate (`dynamic_translation_fail_fast`). In accordance with the Red Screen of Death audit, any missing translation throws `AppException.validation`, which is safely caught and contained by `AppExceptionBoundary` (rendering a localized Diagnostic Node box instead of an unhandled Red Screen crash):
     ```dart
     String get(String? langCode, {String fallback = 'en'}) {
       if (langCode != null && langCode.isNotEmpty) {
         final normalized = langCode.split(RegExp(r'[-_]')).first.toLowerCase();
         final val = translations[normalized];
         if (val != null && val.trim().isNotEmpty) {
           return val.trim();
         }
       }

       final fallbackNormalized = fallback.split(RegExp(r'[-_]')).first.toLowerCase();
       final fallbackVal = translations[fallbackNormalized];
       if (fallbackVal != null && fallbackVal.trim().isNotEmpty) {
         return fallbackVal.trim();
       }

       throw AppException.validation(
         'Fail-Fast Localization Error: Missing translation for langCode=$langCode, fallback=$fallback. Available: ${translations.keys.toList()}',
       );
     }
     ```
2. Clean up 1-hop callers, Execution UI widgets, and Studio components:
   - In `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L187-L193]` and `#L332-L333`: Replace ternary `locale == 'fi' ? m.labelI18n.get('fi') : m.labelI18n.get('en')` with `m.labelI18n.get(locale)`.
   - In `@[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart#L52-L54]`: Replace ternary `locale == 'fi' ? matrix.labelI18n.get('fi') : matrix.labelI18n.get('en')` with `matrix.labelI18n.get(locale)`.
   - In `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]`: Migrate all hardcoded Finnish UI text, buttons, labels, and SnackBar error messages to `AppLocalizations` (`l10n.humanOverrideDialogTitle`, `l10n.humanOverrideNewScoreLabel`, `l10n.humanOverrideReasonLabel`, `l10n.humanOverrideAddEvidenceBtn`, `l10n.cancel`, `l10n.humanOverrideSaveBtn`, `l10n.delete`, `l10n.humanOverrideReasonRequiredError`, `l10n.humanOverrideSaveFailedError`).
   - In `@[client_app_v2/lib/features/execution/views/execution_report_view.dart]`: Migrate hardcoded tooltips and action labels (L277 `l10n.downloadFrozenContextTooltip`, L308 `l10n.downloadExcelLabel`) to `AppLocalizations`.
   - In `@[client_app_v2/lib/shared/widgets/specialist_section.dart#L1983]`: Migrate `const Text("Tietoa Mittarista")` to `Text(l10n.aboutMetricTitle)`.
   - In `@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]`: Add corresponding translation keys for all migrated Execution-tier strings.
   - In `@[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart]`: Remove `defaultLocale` state tracking and bind text editing directly to `translations` map.
   - In `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart#L239-L260]`: Replace local `isEmptyI18n(text)` with `text?.isEmpty ?? true`.
   - In `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L135]`: Replace hardcoded `backgroundColor: const Color(0xFF2E7D32)` with `backgroundColor: Theme.of(context).colorScheme.primary`, and replace generic `throw Exception("Workflow ID is missing")` on L125 with `throw AppException.validation(l10n.workflowIdMissingError);`.
   - In `@[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart#L344]`: Purge manual `url.substring(0, 40)` clipping in favor of declarative `TextOverflow.ellipsis`.
   - Note on Error Containment: All widget tree evaluations of `I18nText.get()` operate under the protection of root-level `AppExceptionBoundary` in `app.dart` (and sub-tree boundaries in Studio views), ensuring that any validation failure displays an auditable Diagnostic Node rather than corrupting memory or crashing the process.
3. Create unit test suite `[NEW]` `@[client_app_v2/test/shared/models/i18n_text_test.dart]` with explicit positive and negative ISTQB partition test cases:
   - **TC-I18N-FLUTTER-01**: Target locale match (`get('fi')` returns Finnish text).
   - **TC-I18N-FLUTTER-02**: Lingua Franca fallback (`get('sv')` falls back to `'en'`).
   - **TC-I18N-FLUTTER-03**: Missing translation Fail-Fast (`get('fr', fallback: 'en')` throws `AppException.validation`).
   - **TC-I18N-FLUTTER-04**: Whitespace/Empty translation Fail-Fast (throws `AppException.validation`).
   - **TC-I18N-FLUTTER-05**: State helpers (`isEmpty`, `isNotEmpty`, `has('en')`).
   - **TC-I18N-FLUTTER-06** (Negative Partition): `I18nText.fromJson` with legacy `default_locale` key throws `CheckedFromJsonException` via `disallowUnrecognizedKeys: true`:
     ```dart
     test('Negative Partition: I18nText.fromJson with legacy default_locale throws CheckedFromJsonException', () {
       final legacyJson = {
         'default_locale': 'en',
         'translations': {'en': 'Hello'},
       };
       expect(
         () => I18nText.fromJson(legacyJson),
         throwsA(isA<CheckedFromJsonException>()),
         reason: 'disallowUnrecognizedKeys must reject legacy default_locale field',
       );
     });
     ```
   - **TC-I18N-FLUTTER-07** (Negative Partition): `I18nText.fromJson` without `translations` key throws `CheckedFromJsonException` via `required Map<String, String>` without `@Default`.
4. Run Flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/shared/models/i18n_text.dart --build`.

#### Step 2.3: Deterministic Pruning of `default_locale` across 500 Instances & 100% Bilingual Seeding
*Vault Mutation Exception & Fail-Fast Integrity Protocol*: This bulk 500-instance migration requires an explicit exception to the `inline_terminal_scripting` ban. Write and execute an atomic Python script in the scratch directory (`scratch/prune_default_locale_seed.py`) to strip all `"default_locale": "..."` keys from `backend_v2/seed/seed_data.json` while preserving authentic translation payloads:
1. **Zero-Chimera & Strict Pruning Mandate**: The script MUST strictly remove `"default_locale"` keys without inventing synthetic data. Copying `"fi"` text into missing `"en"` keys is STRICTLY BANNED (`the_duct_tape_ban`, `anti_lazy_fallback_mandate`) as it creates corrupted Chimera Data.
2. **Pre-Flight Validation & Zero Missing 'en' Assertion**: Empirical codebase audit confirms that all 500 records in `seed_data.json` already contain non-empty `"en"` translations (0 missing `"en"`). The pruning script MUST programmatically assert `len(translations) > 0` and `"en" in translations` for every record, and MUST Fail-Fast with exit code 1 if any record lacks a valid `"en"` entry.
3. **Populate 4 Missing Finnish Translations**: Populate authentic Finnish translations (`"fi"`) for `prompt_blocks[88].label` (`"Johdon valmennussynteesi"`), `prompt_blocks[88].description` (`"Johdon valmentajan synteesilohko"`), `prompt_blocks[89].label` (`"Analyyttinen graafisynteesi"`), and `prompt_blocks[89].description` (`"Analyyttisen graafin synteesilohko"`), achieving 100% bilingual (`fi` + `en`) completeness across all 500 records in the seed vault.
4. **Execution Invariants**: The script MUST: (a) parse via `json.load()`, (b) recursively delete `default_locale`, (c) output formatted JSON matching CRLF line endings, and (d) verify JSON integrity via `json.loads()` dry run.

#### Step 2.4: Deterministic Bulk Migration of Test Fixtures via Atomic Scratch Scripts (Context Amnesia Prevention)
*Context Amnesia Firewall & Bulk Migration Protocol*: To prevent Tier 2 LLM execution failure, hallucination cascades, and token exhaustion from opening 90+ test files into the agent's context window, mechanical fixture updates MUST be executed via deterministic Python scratch scripts rather than manual conversational edits:

1. **Backend Fixture Migration (`scratch/migrate_backend_i18n_fixtures.py`)**:
   - Recursively scans all `.py` files in `backend_v2/tests/` (1,166 occurrences across 90 files).
   - Strips `default_locale` keyword arguments and dictionary keys:
     - Kwarg substitution: `re.sub(r'default_locale\s*=\s*["\'][^"\']+["\']\s*,?\s*', '', content)`
     - Dictionary key substitution: `re.sub(r'["\']default_locale["\']\s*:\s*["\'][^"\']+["\']\s*,?\s*', '', content)`
   - Performs syntax validation via `ast.parse(modified_content)` on every file before writing to disk, failing fast if syntax is corrupted.
   - Formats all modified files using `uv run ruff format backend_v2/tests/`.

2. **Flutter Fixture Migration (`scratch/migrate_flutter_i18n_fixtures.py`)**:
   - Scans all `.dart` files in `client_app_v2/test/` and `client_app_v2/lib/features/studio/` (157 occurrences across 25 test files and 12 widgets).
   - Strips `defaultLocale:\s*['"][^'"]+['"]\s*,?` kwargs from `I18nText` instantiations.
   - Normalizes empty/bare `I18nText(defaultLocale: 'en')` and `const I18nText(defaultLocale: 'en')` to `I18nText(translations: {'en': 'Test'})` or `const I18nText(translations: {'en': ''})` to satisfy the strict `required Map<String, String> translations` schema without runtime validation failure.
   - Verifies compilation and formats via `dart format client_app_v2/test/`.

#### Step 2.5: Re-seed Database & Atomic Quality Gate Verification
1. Re-seed local development database: `uv run python backend_v2/seed/run_seed.py local`.
2. Run backend quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/tests/ --test`.
3. Run Flutter quality gate: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/ --build`.

---

### Phase 3: ATOMIC `OutputProfile`, SDUI Dumb Painter & Localization Parity (Chapter 5)
*Atomic Transaction Mandate*: Steps 3.1 through 3.5 MUST be executed as a single coherent cycle before triggering the Quality Gate, ensuring backend DTOs, Flutter Freezed models, seed data, and adapters compile with 100% parity. This enforces the **Monorepo Atomic Migration Protocol** (preventing the `Strictness Paradox` in development) and aligns with the production **Clean Slate Deployment Protocol** (Forced Update Gate `X-Min-Client-Version` -> Atomic Backend Database Wipe & Seed Rollout -> Client Ingress Sanitization). Note that all SDUI adapter and widget technical debt items were pre-emptively resolved during Phase 1 Pre-requisite Cleanups per `touched_scope_tech_debt_mandate`.

#### Step 3.1: Backend Static L10n Dictionaries & LocalizationService Formatting
1. **Complete Backend Static Translation Tables (`@[backend_v2/l10n/en.json]` and `@[backend_v2/l10n/fi.json]`)**:
   - Add all 17 `metric_mappings` keys (`metadata_user`, `metadata_organization`, `metadata_scoring_engine`, `metadata_strictness`, `variance_mechanical`, `variance_cognitive`, `variance_total`, `variance_fallback_explanation`, `alignment_verdict`, `alignment_aligned`, `alignment_misaligned`, `jargon_score`, `authenticity_level`, `level_high`, `level_medium`, `level_low`, `authenticity_fallback_explanation`).
   - Add `user_role_mappings` keys (`role_passenger`, `role_navigator`, `role_driver`, `role_architect`).
   - Add `matrix_column_labels` keys (`col_label`, `col_distribution`, `col_row_explanation`, `col_quotes`, `col_normalized_score`, `col_score`).
   - Add `extension_labels` keys (`ext_variance_validation`, `ext_authenticity_evaluation`).
   - Add template presentation keys (`na_not_evaluated_label`, `sources_and_bibliography_title`, `warning_label`, `source_label`, `sduiMetadataCosts`, `sduiMetadataTokens`, `report_title`).
2. **Extend `LocalizationService` (`@[backend_v2/services/localization.py]`) with Formatting Helpers**:
   - `format_date(dt: datetime, locale: str) -> str`: fi: `26.08.2026 klo 06:44`, en: `2026-08-26 06:44`.
   - `format_score(value: float, locale: str) -> str`: fi: `3,50`, en: `3.50`.
   - `format_percent(ratio: float, locale: str) -> str`: fi: `85,2 %`, en: `85.2%`.
   - `format_cost(amount: float, locale: str) -> str`: fi: `0,04 $`, en: `$0.04` (Enforces strict token cost notation in USD per LLM provider billing conventions, localized with Finnish decimal comma and postfix currency symbol).
3. **Update Unit Tests `[MODIFY]` `@[backend_v2/tests/unit/test_localization.py]`**:
   - Verify translation lookups, missing key Fail-Fast `AppException(VALIDATION_FAILED)` behavior, and formatting helpers across locales (`fi`, `en`).

#### Step 3.2: Modernize `OutputProfile` & DTO Schemas (Backend & Frontend)
1. **Backend Domain & DTOs (`v2_core.py` & `models/dtos/output_profile.py`)**:
   - In `@[backend_v2/models/v2_core.py]`:
     - Declare `MatrixSynthesisGroup(V2CoreBase)`:
       ```python
       class MatrixSynthesisGroup(V2CoreBase):
           """Logical group of matrices synthesized together into 2D visualizations or narratives."""
           id: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9_\-]+$", description="Unique group identifier")
           title: I18nText = Field(..., description="Localized group title")
           target_blocks: list[str] = Field(
               min_length=1,
               description="Target matrix block IDs (specifically: ['blk_123', 'blk_456'])",
           )
           synthesis_directive: str | None = Field(default=None, description="Optional synthesis directive override")
       ```
     - In `OutputProfile`:
       - Remove `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts`.
       - Add `matrix_synthesis_groups: list[MatrixSynthesisGroup] = Field(default_factory=list, description="Optional matrix synthesis groups for 2D/3D comparative graphs")`.
       - Add contextual Fail-Fast cross-field validator:
         ```python
         @model_validator(mode="after")
         def validate_matrix_graphs_coherence(self) -> Self:
             """Enforces that matrix synthesis groups exist IF matrix graphs are in target_block_order.

             Returns:
                 The validated OutputProfile instance.

             Raises:
                 ValueError: If MATRIX_GRAPHS_BLOCK is present in target_block_order but matrix_synthesis_groups is empty.
             """
             if (
                 TargetBlockType.MATRIX_GRAPHS_BLOCK in self.target_block_order
                 and not self.matrix_synthesis_groups
             ):
                 raise ValueError(
                     f"OutputProfile '{self.id}': target_block_order includes MATRIX_GRAPHS_BLOCK, "
                     "but matrix_synthesis_groups is empty. At least 1 MatrixSynthesisGroup is required."
                 )
             return self
         ```
     - **DELETE `class OutputLayoutBlock(V2CoreBase)` (L1114-L1146)**: Completely eradicate `OutputLayoutBlock` from `v2_core.py` and remove `"OutputLayoutBlock"` from `__all__` on L78 (`the_no_legacy_mandate`).
   - In `@[backend_v2/models/dtos/output_profile.py]`:
     - Remove `OutputLayoutBlock` import on L24.
     - Replace `layouts` with `matrix_synthesis_groups: list[MatrixSynthesisGroup]` on `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO`.
   - In `@[backend_v2/tests/unit/test_enum_parity.py]`:
     - Remove `test_preset_view_parity()` (L86-L99) and `test_text_delivery_mode_parity()` (L121-L134) AST assertions targeting deleted `OutputLayoutBlock`.

2. **Flutter Freezed Model (`output_profile.dart`)**:
   - In `@[client_app_v2/lib/features/studio/models/output_profile.dart]`:
     - Declare `MatrixSynthesisGroup` Freezed model with explicit `@JsonSerializable(disallowUnrecognizedKeys: true)` annotation:
       ```dart
       @Freezed(equal: false)
       abstract class MatrixSynthesisGroup with _$MatrixSynthesisGroup {
         const MatrixSynthesisGroup._();

         @JsonSerializable(disallowUnrecognizedKeys: true)
         const factory MatrixSynthesisGroup({
           required String id,
           required I18nText title,
           required List<String> targetBlocks,
           String? synthesisDirective,
         }) = _MatrixSynthesisGroup;

         factory MatrixSynthesisGroup.fromJson(Map<String, dynamic> json) =>
             _$MatrixSynthesisGroupFromJson(json);
       }
       ```
     - Update `OutputProfile` Freezed model: remove `metricMappings`, `matrixColumnLabels`, `userRoleMappings`, `extensionLabels`, and `layouts`; add `matrixSynthesisGroups` (preserving `@JsonSerializable(disallowUnrecognizedKeys: true)`).
     - **DELETE `OutputLayoutBlock` Freezed class (L12-L42)** and clean up generated `.freezed.dart` / `.g.dart` artifacts.
   - In `@[client_app_v2/test/features/studio/models/output_profile_test.dart]`:
     - Replace `OutputLayoutBlock` JSON parsing tests with `MatrixSynthesisGroup` serialization tests.
     - Add explicit Negative Partition ISTQB tests asserting that passing purged legacy keys to `OutputProfile.fromJson` or `MatrixSynthesisGroup.fromJson` throws `CheckedFromJsonException`:
       ```dart
       test('Negative Partition: OutputProfile.fromJson with legacy layouts throws CheckedFromJsonException', () {
         final legacyJson = {
           'id': 'op_1234567890abcdef',
           'workflow_id': 'wf_9d68c573802341db',
           'name': {'translations': {'en': 'Profile'}},
           'layouts': [{'preset_view': 'default'}],
         };
         expect(
           () => OutputProfile.fromJson(legacyJson),
           throwsA(isA<CheckedFromJsonException>()),
           reason: 'disallowUnrecognizedKeys must reject legacy layouts array',
         );
       });

       test('Negative Partition: OutputProfile.fromJson with legacy metric_mappings throws CheckedFromJsonException', () {
         final legacyJson = {
           'id': 'op_1234567890abcdef',
           'workflow_id': 'wf_9d68c573802341db',
           'name': {'translations': {'en': 'Profile'}},
           'metric_mappings': {'metric_1': {'translations': {'en': 'Metric'}}},
         };
         expect(
           () => OutputProfile.fromJson(legacyJson),
           throwsA(isA<CheckedFromJsonException>()),
           reason: 'disallowUnrecognizedKeys must reject legacy metric_mappings dictionary',
         );
       });

       test('Negative Partition: MatrixSynthesisGroup.fromJson with legacy preset_view throws CheckedFromJsonException', () {
         final legacyJson = {
           'id': 'msg_1',
           'title': {'translations': {'en': 'Group 1'}},
           'target_blocks': ['blk_1'],
           'preset_view': 'default',
         };
         expect(
           () => MatrixSynthesisGroup.fromJson(legacyJson),
           throwsA(isA<CheckedFromJsonException>()),
           reason: 'disallowUnrecognizedKeys must reject legacy preset_view in MatrixSynthesisGroup',
         );
       });
       ```
   - Run Flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`.

#### Step 3.3: Refactor SDUI Adapters, Worker & Jinja2 PDF Template (Dumb Painters)
1. **Refactor SDUI Adapters to Produce Pre-Localized DTO Blocks**:
   - In `@[backend_v2/services/sdui/adapters/metadata_adapter.py]`: Produce pre-localized `metadata_lines` and `costs`/`tokens` strings using `LocalizationService.translate()` and `format_cost()` / `format_date()` functions.
   - In `@[backend_v2/services/sdui/adapters/variance_adapter.py]`, `@[backend_v2/services/sdui/adapters/authenticity_adapter.py]`, `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]`: Decouple completely from `profile.metric_mappings` / `user_role_mappings` database fields. Resolve titles, labels, and numbers via `LocalizationService`.
   - In `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]` and `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`: Consume `profile.matrix_synthesis_groups` instead of the legacy `layouts` structure. Resolve column headers strictly via `LocalizationService`.
   - In `@[backend_v2/services/sdui/adapters/warning_card_adapter.py]`, `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`, `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]`: Complete migration to `LocalizationService` without local dictionaries or fallback ternaries.
2. **Jinja2 / WeasyPrint (PDF) & Flutter Client Parity (Dumb Painters)**:
   - In `@[backend_v2/services/pdf_generator.py]`:
     - Verify and lock `undefined=jinja2.StrictUndefined` environment configuration in `PdfReportService.__init__` (`Environment(loader=FileSystemLoader(str(template_dir)), undefined=jinja2.StrictUndefined)`).
     - Register global Fail-Fast helper `_raise_unrecognized_sdui_block(block_type)` in `PdfReportService.__init__` bound explicitly to `self.env.globals["raise_unrecognized_sdui_block"] = _raise_unrecognized_sdui_block`:
       ```python
       def _raise_unrecognized_sdui_block(block_type: str) -> None:
           msg = f"Unrecognized SDUI block type '{block_type}' encountered during PDF rendering."
           logger.error(
               "[PdfReportService] %s: %s",
               ErrorCodes.VALIDATION_FAILED.name,
               msg,
               extra={"block_type": block_type},
           )
           raise AppException(
               message=msg,
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "block_type": block_type},
           )

       self.env.globals["raise_unrecognized_sdui_block"] = _raise_unrecognized_sdui_block
       ```
     - In `PdfReportService.generate_execution_html()`: Add pre-flight assertion that `report_dto.inner_sdui_blocks` is non-empty, raising `AppException(VALIDATION_FAILED)` if empty or missing.
   - In `@[backend_v2/templates/report_template.jinja2]`:
     - Renders pre-localized `ReportDataDTO` directly without separate dictionary lookup.
     - Update CSS `@page @bottom-center` footer pagination to universal language-neutral compact format:
       ```css
       @page {
           size: A4;
           margin: 1.5cm;
           @bottom-center {
               content: counter(page) " / " counter(pages);
               font-family: 'Inter', sans-serif;
               font-size: 9px;
               color: #888;
           }
       }
       ```
     - Purge hardcoded Finnish string `N/A (Ei arvioitu):` on L159 and replace with `{{ l10n.na_not_evaluated_label }}`.
     - Purge hardcoded labels: replace `Warning:` on L152 with `{{ l10n.warning_label }}:`, `Meta Costs`/`Meta Tokens` on L197/202 with `{{ l10n.sduiMetadataCosts }}`/`{{ l10n.sduiMetadataTokens }}`, `(Lähde: ...)` on L385 with `({{ l10n.source_label }}: ...)`.
     - Purge lazy fallback ternaries (`if l10n is defined else '...'`) on L225, L238, L242, L244, L251, L256, L319-324, L434, L435 in favor of direct `l10n.<key>` references backed by `StrictUndefined` (specifically: `{{ l10n.scorecard_global_average }}`, `{{ l10n.systemAuditTrailLabel }}`, `{{ l10n.pdfAuditDuration }}`).
     - Purge legacy HTML fallback card (`V2 ARCHITECTURE VIOLATION`) on L447-453 in favor of Python-level pre-flight Fail-Fast exception.
     - Add strict `{% else %}` branch in `render_sdui_blocks` macro that invokes `{{ raise_unrecognized_sdui_block(block.block_type if block.block_type is defined else 'UNDEFINED') }}`, instantly halting PDF compilation on unhandled polymorphic blocks.
   - In `@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]`:
     - Renders pre-localized `AnySduiBlock` elements directly via exhaustive Dart 3 pattern matching `switch (block)` without default wildcards (`_ =>`). Flutter's `app_en.arb` and `app_fi.arb` are reserved strictly for UI Chrome (buttons, dialogs, themes).
3. **Update Background Worker & Flutter Studio View**:
   - In `@[backend_v2/worker.py#L593-L1364]`: Iterate over `profile.matrix_synthesis_groups` for matrix synthesis generation.
   - In `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]`: Bind to `matrixSynthesisGroups` model.

#### Step 3.4: Seed Vault `OutputProfile` Migration & Test Fixture Updates
1. Update `OutputProfile` records in `@[backend_v2/seed/seed_data.json#L9180-L9570]` by removing legacy dictionary fields and converting `layouts` to `matrix_synthesis_groups`.
2. Migrate all test fixtures in `backend_v2/tests/` that mock `OutputProfile` or instantiate `OutputLayoutBlock` (specifically and exhaustively: `test_blueprint.py`, `test_matrix_domain_parser.py`, `test_output_profile_service.py`, `test_matrix_summary_table_adapter.py`, `test_matrix_graphs_adapter.py`, `test_worker_synthesis.py`, `test_variance_adapter.py`) to construct `OutputProfile(matrix_synthesis_groups=[...])` instead of `layouts=[OutputLayoutBlock(...)]`.

#### Step 3.5: Re-seed Database & Atomic Quality Gate Verification
1. Re-seed local development database: `uv run python backend_v2/seed/run_seed.py local`.
2. Run backend quality gate: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
3. Run Flutter quality gate: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.

---

### Phase 4: AST Guardrails, Parity Suites & Final Audit (Chapter 6)

#### Step 4.1: Create AST Guardrail & L10n / Presentation Parity Suites
1. Create [NEW] `@[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]`:
   - `test_seed_matrices_have_no_epistemic_anchor_in_ai_description`: Assert 0 matrix blocks contain `"EPISTEMIC ANCHOR:"`.
   - `test_seed_matrices_have_valid_theory_grounding`: Assert all 13 matrix blocks have non-null `theory_grounding`.
   - `test_matrix_sensor_prompt_builder_ast_uses_pure_theory_citation`: AST asserts `model_dump_json()` is not called on `theory_grounding`.
2. Create [NEW] `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]`:
   - `test_seed_has_no_default_locale`: Assert 0 occurrences of `"default_locale"` across the entire `seed_data.json` file.
   - `test_seed_i18n_has_100_percent_bilingual_parity`: Assert that 100% of all `I18nText` records in `seed_data.json` possess valid, non-empty `"en"` and `"fi"` translations (zero missing keys).
   - `test_seed_output_profile_has_no_legacy_dictionaries`: Assert 0 occurrences of `metric_mappings`, `matrix_column_labels`, and `user_role_mappings` in `OutputProfile` records.
   - `test_seed_output_profile_uses_matrix_synthesis_groups`: Assert `matrix_synthesis_groups` is present and non-empty.
3. Create [NEW] `@[backend_v2/tests/unit/test_backend_l10n_internal_parity.py]`:
   - `test_backend_json_has_100_percent_internal_language_parity`: Assert 1:1 key parity between `backend_v2/l10n/en.json` and `backend_v2/l10n/fi.json`.
   - `test_jinja_template_all_l10n_references_exist_in_backend_dictionaries`: AST/Regex scanner asserting that 100% of `l10n.<key>` references in `backend_v2/templates/report_template.jinja2` exist in both `en.json` and `fi.json` (zero missing translation keys).
   - `test_backend_json_has_no_dead_unreferenced_keys`: Assert all keys in `en.json` and `fi.json` are actively consumed in `report_template.jinja2` or SDUI adapters.
4. Create [NEW] `@[backend_v2/tests/fixtures/sdui_golden_master.json]`:
   - Define a shared synthetic `ReportDataDTO` payload containing 1 concrete instance of specifically all 17 `AnySduiBlock` types with populated titles, markdown text, numeric scores, citations `[C1, C2]`, badge arrays, metadata key-values, quote texts, and table rows.
5. Create [NEW] `@[backend_v2/tests/unit/test_sdui_template_parity.py]`:
   - `test_all_sdui_blocks_handled_in_jinja_and_dart`: AST guardrail reading `sdui.py`, `report_template.jinja2`, and `sdui_blocks_renderer.dart` to assert 100% block type handling parity across Python Pydantic, Jinja2 template branches, and Dart Freezed pattern match.
   - `test_jinja_ast_attribute_validity`: Jinja2 AST parser asserting all attribute accesses on `block.*` exist as valid fields on corresponding Pydantic models.
   - `test_jinja_raises_app_exception_on_unrecognized_block_type`: Asserts that passing an unhandled synthetic SDUI block type to `PdfReportService.generate_execution_html()` raises `AppException(VALIDATION_FAILED)` and halts PDF rendering.
   - `test_jinja_sdui_golden_master_rendering`: Semantic DOM test rendering `sdui_golden_master.json` through `PdfReportService.generate_execution_html()` and using `BeautifulSoup` to verify that all headings, markdown paragraphs, citations, badges, and table cells exist in the generated HTML.
6. Create [NEW] `@[client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart]`:
   - Flutter widget test loading `sdui_golden_master.json` and rendering via `SduiBlocksRenderer` with `locale = const Locale('fi')` and `Locale('en')`, asserting that all semantic text nodes, citations, badges, and headers exist in the rendered widget tree with 1:1 parity against Jinja DOM output.

#### Step 4.2: Full Global Quality Gate Verification
1. Run backend global quality gate: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
2. Run Flutter global quality gate: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.

---

## 6. ISTQB Equivalence Partitions & Boundary Scenarios Matrix

| Scenario ID | Test Name | Input State | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **TC-TG-01** (Happy Path: Pure Citation) | `test_build_caching_prefix_with_context` | `TheoryGrounding(source_url="https://arma.org", citation_reference="ARMA Principles")` | Static prompt contains `<theory_context>\nARMA Principles\n</theory_context>` (no raw URL in prompt) |
| **TC-TG-02** (Boundary: Null Citation) | `test_build_caching_prefix_theory_grounding_none_citation` | `TheoryGrounding(source_url="https://arma.org", citation_reference=None)` | Ephemeral block is not appended, avoiding empty XML tags |
| **TC-TG-03** (Boundary: Empty Citation) | `test_build_caching_prefix_theory_grounding_empty_citation` | `TheoryGrounding(source_url="https://arma.org", citation_reference="")` | Ephemeral block is not appended, avoiding empty XML tags |
| **TC-TG-04** (Boundary: Whitespace-only) | `test_build_caching_prefix_theory_grounding_whitespace_only` | `TheoryGrounding(source_url="https://arma.org", citation_reference="   \n\t")` | Ephemeral block is not appended, avoiding whitespace-only tags |
| **TC-TG-05** (Boundary: URL Exclusion) | `test_build_caching_prefix_theory_grounding_omits_raw_urls` | `TheoryGrounding(source_url="https://secret-domain.org/doc", citation_reference="Valid Citation")` | Static prompt does NOT contain `"https://secret-domain.org"` (zero token bloat / URL leakage) |
| **TC-TG-06** (Security: CDATA XML Injection Shield) | `test_build_caching_prefix_theory_grounding_xml_injection_shield` | `TheoryGrounding(citation_reference="Author (2020) <tag> & ]]> </theory_context><injected>")` | Static prompt wraps citation in `<![CDATA[...]]>` and safely breaks `]]>` without closing tag early |
| **TC-I18N-01** (Happy Path: Target Match) | `test_i18n_text_resolve_target_locale` | `I18nText(translations={"fi": "Käyttäjä", "en": "User"})`, `target_locale="fi"` | Returns `"Käyttäjä"` |
| **TC-I18N-02** (Fallback: English Default) | `test_i18n_text_resolve_fallback_en` | `I18nText(translations={"fi": "Käyttäjä", "en": "User"})`, `target_locale="sv"` | Returns `"User"` (fallback) |
| **TC-I18N-03** (Fail-Fast: Missing Target & Fallback) | `test_i18n_text_resolve_missing_raises_app_exception` | `I18nText(translations={"de": "Benutzer"})`, `target_locale="fr"`, `fallback_locale="en"` | Raises `AppException(VALIDATION_FAILED)` with RFC 7807 logging |
| **TC-I18N-04** (Fail-Fast: Whitespace / Empty Strings) | `test_i18n_text_resolve_whitespace_raises_app_exception` | `I18nText(translations={"fi": "   ", "en": ""})`, `target_locale="fi"` | Raises `AppException(VALIDATION_FAILED)` (no silent empty string bypass) |
| **TC-I18N-05** (Fail-Fast: Missing Translations Field) | `test_i18n_text_missing_translations_raises_validation_error` | `I18nText()` (instantiation without translations) | Raises Pydantic `ValidationError` (no default factory bypass) |
| **TC-I18N-06** (Sanitization: Case-Insensitive English Baseline) | `test_i18n_text_sanitizes_uppercase_keys` | `I18nText(translations={"EN": "User", "FI": "Käyttäjä"})` | Validates successfully; canonical `translations` map is `{"en": "User", "fi": "Käyttäjä"}` |
| **TC-I18N-07** (Sanitization: Whitespace Key Stripping) | `test_i18n_text_sanitizes_whitespace_padded_keys` | `I18nText(translations={"  en  ": "User", "  fi  ": "Käyttäjä"})` | Validates successfully; canonical `translations` map is `{"en": "User", "fi": "Käyttäjä"}` |
| **TC-I18N-FLUTTER-01** (Flutter: Target Match) | `test_i18n_text_get_target_locale` | `I18nText(translations: {'fi': 'Käyttäjä', 'en': 'User'})`, `get('fi')` | Returns `'Käyttäjä'` |
| **TC-I18N-FLUTTER-02** (Flutter: Fallback English Default) | `test_i18n_text_get_fallback_en` | `I18nText(translations: {'fi': 'Käyttäjä', 'en': 'User'})`, `get('sv')` | Returns `'User'` (fallback) |
| **TC-I18N-FLUTTER-03** (Flutter: Fail-Fast Missing Target & Fallback) | `test_i18n_text_get_missing_throws_app_exception` | `I18nText(translations: {'de': 'Benutzer'})`, `get('fr', fallback: 'en')` | Throws `AppException.validation` with available keys list |
| **TC-I18N-FLUTTER-04** (Flutter: Fail-Fast Whitespace / Empty String) | `test_i18n_text_get_whitespace_throws_app_exception` | `I18nText(translations: {'fi': '   ', 'en': ''})`, `get('fi')` | Throws `AppException.validation` (no silent empty string bypass) |
| **TC-I18N-FLUTTER-05** (Flutter: Helpers isEmpty & isNotEmpty) | `test_i18n_text_is_empty_helpers` | `I18nText(translations: {'en': '  '})`, `I18nText(translations: {'en': 'User'})` | `isEmpty == true`, `isNotEmpty == false`, `has('en') == false` |
| **TC-I18N-FLUTTER-06** (Negative Partition: Fail-Fast Legacy default_locale) | `test_i18n_text_from_json_legacy_default_locale_throws` | `jsonDecode('{"default_locale": "en", "translations": {"en": "Text"}}')` | Throws `CheckedFromJsonException` (disallowUnrecognizedKeys: true rejection) |
| **TC-I18N-FLUTTER-07** (Negative Partition: Fail-Fast Missing translations Key) | `test_i18n_text_from_json_missing_translations_throws` | `jsonDecode('{}')` or `jsonDecode('{"translations": null}')` | Throws `CheckedFromJsonException` (no @Default bypass) |
| **TC-PROFILE-FLUTTER-01** (Negative Partition: OutputProfile Legacy layouts) | `test_output_profile_legacy_layouts_throws` | `OutputProfile` JSON containing `'layouts': [...]` | Throws `CheckedFromJsonException` |
| **TC-PROFILE-FLUTTER-02** (Negative Partition: OutputProfile Legacy metric_mappings) | `test_output_profile_legacy_metric_mappings_throws` | `OutputProfile` JSON containing `'metric_mappings': {...}` | Throws `CheckedFromJsonException` |
| **TC-PROFILE-FLUTTER-03** (Negative Partition: MatrixSynthesisGroup Legacy preset_view) | `test_matrix_synthesis_group_legacy_preset_view_throws` | `MatrixSynthesisGroup` JSON containing `'preset_view': 'default'` | Throws `CheckedFromJsonException` |
| **TC-SDUI-01** (Metadata: Key-Value Output) | `test_metadata_adapter_emits_structured_keys` | Context with `user_name="Matti Meikäläinen"` | SDUI payload contains `{key: "user", value: "Matti Meikäläinen"}` without hardcoded Finnish label |
| **TC-SDUI-02** (Synthesis Groups: Group Dispatch) | `test_worker_iterates_matrix_synthesis_groups` | Profile with 2 `MatrixSynthesisGroup` objects | Emits 2 discrete synthesis tasks targeted at group member matrices |
| **TC-SDUI-03** (Matrix Graphs: Explicit Row DTO Instantiation) | `test_matrix_graphs_adapter_instantiates_row_dtos_without_model_copy` | Adapter input with `text_delivery_mode="titles_only"` | Produces valid `MatrixScorecardRowDTO` instances with `inner_sdui_blocks=[]` without calling `model_copy(update=)` |
| **TC-L10N-01** (Localization Service: Lookups & Fail-Fast) | `test_localization_service_translate_and_formatting` | `LocalizationService.translate("metadata_user", "fi")`, `format_cost(12.5, "fi")` | Returns `"Käyttäjä"` and `"12,50 $"`; missing key raises `AppException(VALIDATION_FAILED)` |
| **TC-L10N-02** (Backend L10n Internal Language & Jinja Parity) | `test_backend_l10n_internal_parity` | `backend_v2/l10n/en.json` vs `backend_v2/l10n/fi.json` vs `report_template.jinja2` | 1:1 internal key parity between backend languages; 100% of Jinja `l10n.*` references exist; zero dead unreferenced keys |
| **TC-SDUI-PARITY-01** (AST Guardrail: SDUI Block Exhaustiveness in Jinja & Dart) | `test_all_sdui_blocks_handled_in_jinja_and_dart` | `sdui.py`, `report_template.jinja2`, `sdui_blocks_renderer.dart` | 100% of `AnySduiBlock` union variants are handled in both Jinja macro branches and Dart switch pattern match |
| **TC-SDUI-PARITY-02** (Backend PDF Jinja Golden Master Semantic DOM Rendering) | `test_jinja_sdui_golden_master_rendering` | `sdui_golden_master.json` | Generates HTML via `PdfReportService`, verifies all 17 blocks render headings, paragraphs, citations, badges, tables, `1 / 5` pagination, and `na_not_evaluated_label` with BeautifulSoup |
| **TC-SDUI-PARITY-03** (Flutter SDUI Golden Master Semantic Widget Rendering) | `test_flutter_sdui_golden_master_rendering` | `sdui_golden_master.json` | Headless widget test verifies `SduiBlocksRenderer` renders all text nodes, citations, badges, tables with 1:1 semantic parity |
| **TC-SDUI-PARITY-04** (AST Guardrail: Jinja Template Field Attribute Validity) | `test_jinja_ast_attribute_validity` | `report_template.jinja2` AST | 100% of accessed `block.*` field attributes exist on corresponding Pydantic `AnySduiBlock` models |
| **TC-SDUI-PARITY-05** (Fail-Fast: Jinja Unrecognized SDUI Block) | `test_jinja_raises_app_exception_on_unrecognized_block_type` | `ReportDataDTO` with unsupported synthetic `block_type="unsupported_quantum_widget"` | `PdfReportService.generate_execution_html()` invokes `raise_unrecognized_sdui_block`, logs RFC 7807 error and raises `AppException(VALIDATION_FAILED)` |
| **TC-SDUI-PARITY-06** (Fail-Fast: StrictUndefined Missing l10n Key) | `test_pdf_generator_strict_undefined_missing_l10n_key_raises` | `PdfReportService.generate_execution_html()` with injected empty or incomplete `_translations` dictionary | Jinja2 `UndefinedError` is raised on missing translation key, caught by service, logged with RFC 7807 and raised as `AppException(status_code=500, INTERNAL_SERVER_ERROR)` (zero silent empty string or unlocalized ghost string fallback) |
| **TC-EXEC-L10N-01** (Execution UI Localization Parity) | `test_execution_views_use_app_localizations` | `human_override_dialog.dart`, `execution_report_view.dart`, `specialist_section.dart` | All user-facing strings, buttons, tooltips, dialogs, and snackbars resolve strictly via `AppLocalizations` without raw hardcoded text |
| **TC-AST-10** (AST Guardrail: Epistemic Anchor Purge) | `test_seed_matrices_have_no_epistemic_anchor_in_ai_description` | `seed_data.json` | 0 occurrences of `EPISTEMIC ANCHOR:` across all 13 matrices |
| **TC-AST-11** (AST Guardrail: Default Locale Purge) | `test_seed_has_no_default_locale` | `seed_data.json` | 0 occurrences of `"default_locale"` across entire seed vault |
| **TC-AST-12** (AST Guardrail: Seed Bilingual Parity) | `test_seed_i18n_has_100_percent_bilingual_parity` | `seed_data.json` | 100% of all 500 `I18nText` records in `seed_data.json` possess valid, non-empty `"en"` and `"fi"` translations |
| **TC-AST-13** (AST Guardrail: OutputProfile Clean Dictionaries) | `test_seed_output_profile_has_no_legacy_dictionaries` | `seed_data.json` | 0 occurrences of legacy translation dictionaries in OutputProfile |

---

## 7. Definition of Done (DoD) & Verification Plan

### 7.1 Definition of Done (DoD) Checklist
- [ ] `seed_data.json` backup recorded in `backend_v2/seed/backups/`.
- [ ] All 13 matrix blocks in `seed_data.json` sanitized by removing duplicate `EPISTEMIC ANCHOR:` tails; qualitative prompt definitions preserved verbatim.
- [ ] `MatrixSensorPromptBuilder.build_caching_prefix` formats pure `<theory_context>` and `<matrix_objective>` XML blocks with `TemplateProcessor.safe_interpolate()` CDATA Breakout Shielding, omitting raw URLs from LLM prompt payloads.
- [ ] `default_locale` removed from `I18nText` in `backend_v2/models/v2_core.py` and `client_app_v2/lib/shared/models/i18n_text.dart`; `I18nText` Freezed factory constructor explicitly annotated with `@JsonSerializable(disallowUnrecognizedKeys: true)`; `translations` defined as strictly required (`Field(...)` in Python, `required Map<String, String>` without `@Default` in Dart); `isEmpty`, `isNotEmpty`, `has()`, and Fail-Fast `get()` implemented in Flutter.
- [ ] 500 occurrences of `"default_locale"` pruned from `backend_v2/seed/seed_data.json` with Zero-Chimera Fail-Fast validation.
- [ ] Authentic Finnish translations populated for 4 synthesis text fields in `prompt_blocks[88]` and `prompt_blocks[89]`, achieving 100% bilingual parity across all 500 seed records.
- [ ] 1,166 test fixture references across 90 test files migrated in `backend_v2/tests/` to eliminate `default_locale` and legacy `metric_mappings` mocks.
- [ ] 1-hop callers in Flutter execution widgets (`atom_matrix_table_widget.dart`, `matrix_row_item_widget.dart`), `i18n_text_field.dart`, `profile_editor_view.dart` (`Color` & `throw Exception`), `xai_evidence_box.dart` (`substring`), and `output_profile_controller.dart` modernized.
- [ ] Execution-tier Flutter widgets (`human_override_dialog.dart`, `execution_report_view.dart`, `specialist_section.dart`) migrated to `AppLocalizations` and corresponding keys populated in `app_en.arb` and `app_fi.arb`.
- [ ] `OutputProfile` modernized: `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts` replaced with `matrix_synthesis_groups` in `v2_core.py`, `models/dtos/output_profile.py`, and `output_profile.dart`; `MatrixSynthesisGroup` Freezed factory constructor annotated with `@JsonSerializable(disallowUnrecognizedKeys: true)`; `OutputLayoutBlock` class and `__all__` export completely eradicated across Python and Flutter (`the_no_legacy_mandate`).
- [ ] `test_enum_parity.py` updated to retire AST parity checks (`test_preset_view_parity`, `test_text_delivery_mode_parity`) for deleted `OutputLayoutBlock`.
- [ ] Backend static translation tables in `backend_v2/l10n/en.json` and `fi.json` populated with all 17 metric mapping keys, user roles, matrix columns, extension labels, `na_not_evaluated_label`, `sources_and_bibliography_title`, `warning_label`, `source_label`, `sduiMetadataCosts`, `sduiMetadataTokens`, `col_quotes`, `report_title`, and formatting rules.
- [ ] `LocalizationService` extended with `format_date`, `format_decimal`, `format_score`, `format_percent`, and `format_cost` helpers.
- [ ] SDUI Adapters Technical Debt Swept: `WarningCardAdapter` (`I18N_WARNING_STARVATION`), `VarianceAdapter` (`hasattr`, `.get()`), `AuthenticityAdapter` (`.get()`), `PrintableSourcesAdapter` (rules dictionary, ternary fallback), `XaiHighlightsAdapter` (silent `except ValueError` nielu), and `MatrixGraphsAdapter` (`model_copy(update=)` eradicated) cleaned of anti-patterns and migrated to `LocalizationService`.
- [ ] `MetadataAdapter`, `VarianceAdapter`, `AuthenticityAdapter`, `ExecutiveSummaryAdapter`, `MatrixGraphsAdapter`, `MatrixSummaryTableAdapter`, `report_template.jinja2`, and `worker.py` refactored to consume `LocalizationService` and `matrix_synthesis_groups` as pre-localized SDUI blocks.
- [ ] `report_template.jinja2` and `PdfReportService` sanitized: `undefined=jinja2.StrictUndefined` environment configuration locked; `_raise_unrecognized_sdui_block` Fail-Fast helper registered on `self.env.globals["raise_unrecognized_sdui_block"]`; universal compact footer pagination `counter(page) " / " counter(pages);` (`1 / 5`) configured; legacy HTML fallback card purged; hardcoded Finnish string `N/A (Ei arvioitu)` on L159 replaced with `{{ l10n.na_not_evaluated_label }}`; hardcoded strings (`Warning:`, `Meta Costs`, `Meta Tokens`, `(Lähde: ...)`) purged; lazy fallback ternaries `if l10n is defined else '...'` purged across all 11 instances in favor of direct `l10n.<key>` references backed by `StrictUndefined`.
- [ ] `sdui_golden_master.json` fixture created containing populated instances of all 17 `AnySduiBlock` variants.
- [ ] SDUI presentation parity test suite implemented and passing in `backend_v2/tests/unit/test_sdui_template_parity.py` (AST block exhaustiveness guardrail, Jinja AST field attribute validator, unrecognized block Fail-Fast assertion, `StrictUndefined` missing l10n key assertion, and BeautifulSoup semantic DOM test).
- [ ] Flutter SDUI golden master parity test implemented and passing in `client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart`.
- [ ] Flutter Freezed models generated via `build_runner` and Studio profile tab updated.
- [ ] Local test database re-seeded via `uv run python backend_v2/seed/run_seed.py local`.
- [ ] AST guardrails implemented and passing in `test_ast_theory_grounding_guardrails.py` and `test_seed_architectural_guardrails.py`.
- [ ] Backend internal localization parity test implemented and passing in `backend_v2/tests/unit/test_backend_l10n_internal_parity.py`.
- [ ] Unit tests for `LocalizationService` updated and passing in `backend_v2/tests/unit/test_localization.py`.
- [ ] Flutter unit tests implemented and passing in `client_app_v2/test/shared/models/i18n_text_test.dart`.
- [ ] Full backend audit loop passes: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
- [ ] Full Flutter audit loop passes: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.

### 7.2 Verification Execution Commands
```powershell
# 1. Run Unit Tests for Theory Grounding, I18nText, L10n & Presentation Parity (Backend & Flutter)
uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py backend_v2/tests/unit/test_localization.py backend_v2/tests/unit/test_backend_l10n_internal_parity.py backend_v2/tests/unit/test_sdui_template_parity.py
uv run python scripts/flutter_audit_loop.py client_app_v2/test/shared/models/i18n_text_test.dart --build
uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart --build

# 2. Run AST Guardrail Suites
uv run pytest backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py backend_v2/tests/unit/test_seed_architectural_guardrails.py

# 3. Run Backend Quality Loop
uv run python scripts/backend_audit_loop.py backend_v2 --test

# 4. Run Flutter Quality Loop
uv run python scripts/flutter_audit_loop.py client_app_v2 --build
```

---

## 8. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document (@[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md#L1-L20]) for the authoritative registry of active rules and Knowledge Items.


