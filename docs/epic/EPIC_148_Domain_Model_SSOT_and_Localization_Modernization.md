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
  <knowledge_item>@[ki_sdui_dumb_painter.md]</knowledge_item>
</required_context_rules>

# EPIC 148: Domain Model SSOT & Presentation Localization Modernization

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Objective
EPIC 148 standardizes and modernizes Quorum's domain data models and localization architecture across Python backend services, the SQLite/JSON seed vault, and the Flutter desktop client. The epic establishes five core capabilities:
1. Establish the **Epistemic Separation Paradigm** for theory grounding: prune redundant `EPISTEMIC ANCHOR:` prompt tails across all 13 matrix blocks in `seed_data.json`, format pure `<theory_context>` XML citations without raw URL token leakage during prompt compilation, and preserve structured `TheoryGrounding` metadata exclusively for UI/PDF presentation.
2. Eradicate redundant `default_locale` attributes across backend and frontend `I18nText` data models and 500 instances in `seed_data.json`, shifting language fallback resolution dynamically to execution context parameters (`target_locale`, with global fallback `"en"`).
3. Modernize `OutputProfile` and Server-Driven UI (SDUI) localization by migrating static UI dictionaries (`metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`) out of the backend database into frontend `.arb` resource files, transforming `MetadataAdapter` into structured key-value envelopes, and replacing legacy V1 `layouts` arrays with strongly-typed `matrix_synthesis_groups`.
4. Execute the 4-phase **Atomic Migration Protocol** to ensure strict Pydantic V2 (`extra="forbid"`) and Flutter Freezed compatibility without silent fallbacks, duct-tape validators, or broken test fixtures.
5. Establish the **Tri-Tier SDUI Presentation Parity Architecture** (AST guardrails, Jinja AST attribute validators, and Golden Master cross-platform semantic testing) ensuring that PDF Jinja2 template rendering (`report_template.jinja2`) and Flutter desktop UI rendering (`sdui_blocks_renderer.dart`) maintain 100% semantic, structural, and localization parity across specifically all 17 `AnySduiBlock` types with zero silent drops or unlocalized ghost texts.

### 1.2 Problem Statement & Root Cause Analysis
1. **Theory Grounding Dual Injection & Prompt Bloat (Chapter 2)**: In `@[backend_v2/seed/seed_data.json#L336-L6900]`, epistemic and academic grounding anchors are duplicated across both `PromptBlock.ai_description` (as freeform `EPISTEMIC ANCHOR:` text blocks) and `PromptBlock.theory_grounding` (as structured `TheoryGrounding` DTOs). When `MatrixSensorPromptBuilder` compiles prompts, it injects both the raw text description and the structured object with raw URLs (`source_url`), triggering prompt duplication, URL token bloat, XML syntax corruption risks, and Single Source of Truth (SSOT) drift.
2. **`I18nText.default_locale` Redundancy (Chapter 3)**: In `@[backend_v2/models/v2_core.py#L101-L191]`, `@[client_app_v2/lib/shared/models/i18n_text.dart]`, and across 500 records in `seed_data.json`, every `I18nText` object hardcodes `"default_locale": "fi"`. This conflates static dictionary storage with dynamic runtime resolution, creates internal validation contradictions with the global `"en"` fallback rule, and bloats database payloads across 1300+ test fixtures.
3. **`OutputProfile` Presentation Drift & Dual-Axis Localization Conflicts (Chapter 5)**: In `@[backend_v2/seed/seed_data.json#L9180-L9570]`, `OutputProfile` persists hundreds of lines of static UI label translations in backend dictionaries (`metric_mappings`, `matrix_column_labels`, `user_role_mappings`). `MetadataAdapter` concatenates labels with values in Python strings, violating the "Dumb Painter" principle and creating localization drift against Flutter `.arb` files. Furthermore, `OutputProfile.layouts` retains obsolete V1 fields (`preset_view`, `text_delivery_mode`, `steps: []`) rather than declaring clean matrix synthesis groups.
4. **Fragility Under `extra="forbid"` & Deployment Sequence Crash / Strictness Paradox (Chapter 6)**: Pydantic V2 models enforce `strict=True` and `extra="forbid"`, while Flutter Freezed models enforce `@JsonSerializable(disallowUnrecognizedKeys: true)`. Removing fields without an atomic multi-step migration script immediately causes cascading `ValidationError` failures across 1300+ test fixtures and corrupts local database state (`db_v2.json`). Furthermore, as audited in `feature_audit_deployment_sequence_crash.md`, if the backend database/DTOs and frontend client are updated out of sync in production, un-updated clients crash with `CheckedFromJsonException`. Quorum enforces a Two-Tier Strategy: the Atomic Migration Protocol across the monorepo codebase in development, and the 3-step Deployment Synchronization Protocol (Forced Update Gate `X-Min-Client-Version` -> Atomic Backend + Seed Rollout -> Client Ingress Sanitization) for production releases.
5. **Presentation & Localization Drift between PDF Jinja2 and Flutter UI**: `report_template.jinja2` contains hardcoded Finnish text (`N/A (Ei arvioitu):` on L159) and lazy fallback ternaries (`if l10n is defined else '...'`), risking unlocalized ghost strings in English PDF reports. Furthermore, `report_template.jinja2` lacks an AST guardrail ensuring exhaustive coverage of all `AnySduiBlock` types, allowing new block types added to Python and Flutter to be silently omitted from PDF outputs without raising an error.

---

## 2. Scope & File Modification Boundary

### 2.1 TARGET Files (Editable)
- `[MODIFY]` `@[backend_v2/seed/seed_data.json#L336-L6900]` (PromptBlocks: Sanitize all 13 matrices by removing `EPISTEMIC ANCHOR:` tails)
- `[MODIFY]` `@[backend_v2/seed/seed_data.json#L9180-L9570]` (OutputProfiles: Prune `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`; replace `layouts` with `matrix_synthesis_groups`)
- `[MODIFY]` `@[backend_v2/seed/seed_data.json]` (Prune 500 instances of `default_locale` across seed vault per `Step 2.3` / `vault_mutation_protocol`)
- `[MODIFY]` `@[backend_v2/models/v2_core.py#L101-L191]` and `@[backend_v2/models/v2_core.py#L1148-L1269]` (Remove `default_locale` and `default_factory=dict` from `I18nText`, enforcing required `translations: dict[str, str] = Field(...)` and updating `resolve()`; remove legacy `layouts` and dictionary mappings from `OutputProfile` and define `MatrixSynthesisGroup` domain model)
- `[MODIFY]` `@[backend_v2/models/dtos/output_profile.py]` (Remove `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts`; add `matrix_synthesis_groups`)
- `[MODIFY]` `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L30-L52]` and `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L54-L112]` (Eradicate `_create_ephemeral_block` helper and fake IDs; format pure `<theory_context>\n{citation}\n</theory_context>` and `<matrix_objective>` via direct `TemplateProcessor.safe_interpolate()` assembly)
- `[MODIFY]` `@[client_app_v2/lib/shared/models/i18n_text.dart]` and generated `.freezed.dart` / `.g.dart` (Remove `defaultLocale` and `@Default` from Freezed model, enforcing `required Map<String, String> translations`; add `isEmpty`, `isNotEmpty`, `has(langCode)` helpers; update `get(String? langCode, {String fallback = 'en'})` method with Fail-Fast `AppException.validation`)
- `[MODIFY]` `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]` (Remove redundant ternaries `locale == 'fi' ? get('fi') : get('en')` and pass `locale` directly to `get(locale)`)
- `[MODIFY]` `@[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart]` (Remove redundant ternaries and pass `locale` directly to `get(locale)`)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart]` (Remove `defaultLocale` state tracking and bind text editing directly to `translations` map)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]` (Replace ad-hoc `isEmptyI18n()` helper with SSOT `i18nText.isEmpty`)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart]` (Replace hardcoded `Color(0xFF2E7D32)` with `Theme.of(context).colorScheme.primary` and replace generic `throw Exception(...)` with `throw AppException.validation(...)`)
- `[MODIFY]` `@[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart]` (Purge manual `url.substring(0, 40)` clipping in favor of declarative `TextOverflow.ellipsis`)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/models/output_profile.dart]` and generated `.freezed.dart` / `.g.dart` (Update Freezed model: remove `metricMappings`, `matrixColumnLabels`, `userRoleMappings`, `extensionLabels`; replace `layouts` with `matrixSynthesisGroups`)
- `[MODIFY]` `@[backend_v2/l10n/en.json]` and `@[backend_v2/l10n/fi.json]` (Populate complete static translation tables for Backend SSOT report generation including all 17 metric mapping keys, user roles, matrix columns, extension labels, and formatting rules)
- `[MODIFY]` `@[backend_v2/services/localization.py]` (Extend with type-safe formatting helpers: `format_date()`, `format_decimal()`, `format_score()`, `format_percent()`, and `format_cost()`)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/metadata_adapter.py]` (Refactor to emit pre-localized SDUI blocks using `LocalizationService` for labels, dates, costs, and tokens)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/variance_adapter.py]`, `@[backend_v2/services/sdui/adapters/authenticity_adapter.py]`, `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]` (Refactor to decouple from `profile.metric_mappings` / `user_role_mappings`, eliminate `hasattr()` / `.get()` duct-tape, and resolve static labels and numeric formatting via `LocalizationService`)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]` and `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]` (Consume `matrix_synthesis_groups` instead of legacy `layouts`, resolving column headers via `LocalizationService`, eradicating `model_copy(update=)` in favor of explicit `MatrixScorecardRowDTO` instantiation)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/warning_card_adapter.py]` (Eradicate module-level `I18N_WARNING_STARVATION` instance containing deprecated `default_locale="en"`; resolve warning message dynamically via `LocalizationService`)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` (Eradicate hardcoded `PRINTABLE_SOURCES_RULES` translation dictionary and lazy ternary fallback `locale if locale in ('fi', 'en') else 'en'`; resolve headers strictly via `LocalizationService`)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]` (Refactor extension label resolution to decouple from `profile.extension_labels`, resolve strictly via `LocalizationService`, and eradicate silent `except ValueError: continue` nielut in favor of explicit enum membership validation)
- `[MODIFY]` `@[backend_v2/templates/report_template.jinja2]` (Ensure all table column headers, metadata labels, and legends resolve strictly via pre-localized DTOs and `l10n` context dictionary; purge hardcoded Finnish string `N/A (Ei arvioitu)` on L159; purge lazy fallback ternaries `if l10n is defined else '...'`; add strict unknown block error handling)
- `[MODIFY]` `@[backend_v2/worker.py#L591-L1359]` (Update background synthesis job loop to iterate over `profile.matrix_synthesis_groups`)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]` (Update studio layout editor to bind to `matrix_synthesis_groups`)
- `[NEW]` `@[backend_v2/tests/fixtures/sdui_golden_master.json]` (Comprehensive synthetic SDUI test dataset containing instances of specifically all 17 `AnySduiBlock` variants with citations, titles, and localized metadata)
- `[NEW]` `@[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]` (AST guardrail suite locking pure theory grounding invariants)
- `[NEW]` `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]` (AST guardrail suite asserting zero occurrences of `default_locale`, `EPISTEMIC ANCHOR:`, and legacy `layouts` dictionaries in seed vault)
- `[MODIFY]` `@[backend_v2/tests/unit/test_localization.py]` (Extend existing unit test suite verifying `LocalizationService` translation lookups, fallback behaviors, and formatting helpers)
- `[NEW]` `@[backend_v2/tests/unit/test_l10n_backend_flutter_parity.py]` (Parity test suite asserting 1:1 key parity between `backend_v2/l10n/*.json` and `client_app_v2/lib/l10n/*.arb`)
- `[NEW]` `@[backend_v2/tests/unit/test_sdui_template_parity.py]` (Presentation parity test suite: AST lohkokattavuusvahti asserting 100% handling in Jinja and Dart, Jinja AST field attribute validator, and BeautifulSoup semantic DOM extractor)
- `[NEW]` `@[client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart]` (Flutter widget test verifying that `SduiBlocksRenderer` renders all semantic elements of `sdui_golden_master.json`)
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` and `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]` (Update test assertions for pure `<theory_context>` XML formatting)
- `[MODIFY]` `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_workflows.py]`, `@[backend_v2/tests/unit/services/test_blueprint.py]` (Migrate test fixtures to new `I18nText` and `OutputProfile` schemas and remove obsolete `metric_mappings` mocks)
- `[NEW]` `@[client_app_v2/test/shared/models/i18n_text_test.dart]` (Unit test suite asserting Flutter `I18nText` Fail-Fast `AppException.validation`, fallback resolution, CheckedFromJsonException on missing translations key, and `isEmpty`/`isNotEmpty`/`has` helpers)
- `[MODIFY]` `@[client_app_v2/test/features/studio/views/widgets/profile/tabs/profile_layouts_tab_test.dart]` and `@[client_app_v2/test/]` fixtures (Update Flutter widget test suite and mock `I18nText` instances to match new schemas and non-empty translations)

### 2.2 CONTEXT Files (Read-Only)
- `@[backend_v2/models/v2_core.py#L194-L207]` (`TheoryGrounding` schema SSOT)
- `@[backend_v2/settings.py]` (Backend global configuration SSOT)

---

## 3. Technical Debt Itemization & Pre-Implementation Remediation

Specifically and exhaustively, the following 20 technical debt items are identified for remediation:
1. **Duplicate Theory Anchors in Seed Vault (Chapter 2)**: All 13 matrix blocks in `seed_data.json` duplicate bibliographic text in `ai_description`, creating token bloat and risk of semantic drift.
2. **Missing CDATA Breakout Shielding on Theory Context Prompts**: `MatrixSensorPromptBuilder` formats `<theory_context>` and `<matrix_objective>` via raw f-string interpolation without `TemplateProcessor.safe_interpolate()` CDATA Breakout Shielding, risking XML injection and prompt syntax corruption.
3. **URL Token Bloat & Prompt Leakage**: Raw `source_url` strings are emitted in LLM prompt payloads rather than reserved exclusively for client UI rendering and PDF reports.
4. **Redundant `default_locale` in `I18nText` (Chapter 3)**: 500 `I18nText` blocks in `seed_data.json` declare `"default_locale": "fi"`, conflicting with runtime context-driven language selection.
5. **Static UI Dictionaries in Database (Chapter 5)**: `OutputProfile` contains `metric_mappings`, `user_role_mappings`, and `extension_labels` (and `OutputLayoutBlock` contains `matrix_column_labels`) in backend persistence, violating Dual-Axis Localization.
6. **Backend String Concatenation in `MetadataAdapter`**: `MetadataAdapter` combines translated labels with values in Python strings, breaking the Dumb Painter paradigm.
7. **Obsolete V1 `layouts` Arrays**: `OutputProfile.layouts` retains deprecated fields (`preset_view`, `text_delivery_mode`, `steps: []`, `matrix_column_labels`) instead of a focused `matrix_synthesis_groups` structure.
8. **Worker Couplings on `layouts`**: `worker.py` and SDUI adapters depend on `profile.layouts` for synthesis loop routing.
9. **Flutter Freezed Schema Drift**: `i18n_text.dart` and `output_profile.dart` Freezed models reflect deprecated fields, requiring regeneration via `build_runner`.
10. **Test Fixture Schema Drift (Chapter 6)**: 1300+ test assertions in `backend_v2/tests/test_worker.py`, `backend_v2/tests/test_worker_synthesis.py`, `backend_v2/tests/test_workflows.py`, and `backend_v2/tests/services/test_blueprint.py` hardcode `default_locale` or legacy profile layout keys.
11. **Missing AST Guardrails for Seed Vault Purity**: The test suite lacks static AST assertions preventing re-introduction of `default_locale` or `EPISTEMIC ANCHOR:` tails.
12. **Unsynchronized Local Database State**: `db_v2.json` must be re-seeded atomically after `seed_data.json` mutations.
13. **Flutter `I18nText` Fail-Fast & Widget Ternary Drift**: `i18n_text.dart` must define `required Map<String, String> translations` without `@Default` to prevent masking missing deserialization keys, and `get()` must throw `AppException.validation` on missing translations instead of returning `''`, while `atom_matrix_table_widget.dart` and `matrix_row_item_widget.dart` hardcode `locale == 'fi' ? get('fi') : get('en')` instead of delegating directly to `get(locale)`.
14. **Studio Ad-Hoc `isEmptyI18n` Functions**: `output_profile_controller.dart` implements local ad-hoc `isEmptyI18n()` functions due to missing SSOT `isEmpty`/`isNotEmpty` properties on `I18nText`.
15. **Banned Python `.get()` Duck-Typing & Silent Fallbacks in `I18nText`**: `backend_v2/models/v2_core.py#L101-L191` uses `.get()` duck-typing and silent fallback returns (`return ""`, `fallback=""`). These must be completely eradicated in favor of explicit `in` membership checks, sanitized non-empty validation in `@model_validator(mode="after")`, required `translations: dict[str, str] = Field(...)` (no `default_factory=dict`), and Fail-Fast `AppException` error propagation.
16. **SDUI Adapter & Studio Presentation Technical Debt**: SDUI adapters and studio views contain anti-patterns including hardcoded translation dictionaries in `PrintableSourcesAdapter`, lazy locale ternaries (`locale if locale in ('fi', 'en') else 'en'`), unvalidated `model_copy(update=)` in `MatrixGraphsAdapter` (which must be eradicated and replaced with explicit `MatrixScorecardRowDTO` instantiation), silent exception swallowing in `XaiHighlightsAdapter` (`except ValueError: continue` which must be replaced with typed enum membership checks), hardcoded `Color(0xFF2E7D32)` and `throw Exception` in `profile_editor_view.dart`, manual `substring(0, 40)` clipping in `xai_evidence_box.dart`, and tight couplings to `profile.metric_mappings` / `profile.extension_labels`.
17. **Critical Import-Time Crash in `WarningCardAdapter`**: `@[backend_v2/services/sdui/adapters/warning_card_adapter.py]` instantiates `I18N_WARNING_STARVATION = I18nText(default_locale="en", ...)` at module level. When `default_locale` is removed from `I18nText` (`extra="forbid"`), the backend will crash on import during Phase 2 test runs unless `WarningCardAdapter` is migrated to `LocalizationService` atomically in Phase 2 Step 2.1.
18. **Hardcoded Finnish Strings & Lazy Fallback Ternaries in Jinja PDF Template**: `backend_v2/templates/report_template.jinja2#L159` hardcodes `<strong style="color: #757575;">N/A (Ei arvioitu):</strong>` and uses `if l10n is defined else '...'` on L225, L238, L242, and L244, causing unlocalized ghost strings in English PDF reports.
19. **Missing AST Guardrails for SDUI Presentation Parity**: The test suite lacks a static AST guardrail asserting that 100% of `AnySduiBlock` variants are handled in both `report_template.jinja2` and `sdui_blocks_renderer.dart`, allowing silent drops when new blocks are introduced.
20. **Missing Cross-Platform Semantic Golden Master Parity Test**: There is no automated test asserting that the exact same SDUI payload renders identical semantic text, headings, citations, and numbers across both PDF Jinja HTML and Flutter desktop widgets.

---

## 4. Architectural Impact & Compliance Matrix

### 4.1 Deprecations & Sunset List (`What We Will REMOVE`)
| Deprecated Symbol / Pattern | Location | Replacement / Disposition |
| :--- | :--- | :--- |
| `EPISTEMIC ANCHOR:` prompt tails | `@[backend_v2/seed/seed_data.json#L336-L6900]` | **PURGED**. Retained exclusively in structured `theory_grounding` field. |
| Raw `source_url` in LLM prompts | `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]` | **OMITTED** from LLM prompt payload; retained in DTOs for UI/PDF rendering. |
| `I18nText.default_locale` | `@[backend_v2/models/v2_core.py]`, `@[client_app_v2/lib/shared/models/i18n_text.dart]` | **PURGED**. Replaced by dynamic runtime parameter `target_locale` with `"en"` fallback. |
| `I18nText` `@Default` / `default_factory=dict` on `translations` | `@[backend_v2/models/v2_core.py]`, `@[client_app_v2/lib/shared/models/i18n_text.dart]` | **PURGED**. Replaced by `required Map<String, String> translations` (Dart) and `translations: dict[str, str] = Field(...)` (Python) to guarantee Fail-Fast deserialization. |
| `I18nText.get(fallback="")` & `.get()` duck-typing | `@[backend_v2/models/v2_core.py#L101-L191]` | **PURGED**. Replaced by explicit `if key in dict:` membership checks and strict `resolve()`. |
| `OutputProfile.metric_mappings` | `@[backend_v2/seed/seed_data.json#L9180-L9570]`, `@[backend_v2/models/v2_core.py#L1148-L1269]` | **PURGED**. Replaced by frontend `.arb` static localization files. |
| `OutputLayoutBlock.matrix_column_labels` | `@[backend_v2/models/v2_core.py#L1114-L1145]` | **PURGED**. Implicitly removed via `OutputProfile.layouts` deprecation. |
| `OutputProfile.user_role_mappings` | `@[backend_v2/seed/seed_data.json#L9180-L9570]`, `@[backend_v2/models/v2_core.py#L1148-L1269]` | **PURGED**. Replaced by frontend `.arb` static localization files. |
| `OutputProfile.extension_labels` | `@[backend_v2/seed/seed_data.json#L9180-L9570]`, `@[backend_v2/models/v2_core.py#L1148-L1269]` | **PURGED**. Replaced by frontend `.arb` static localization files. |
| `OutputProfile.layouts` | `@[backend_v2/seed/seed_data.json#L9180-L9570]`, `@[backend_v2/models/v2_core.py#L1148-L1269]` | **PURGED**. Replaced by clean `matrix_synthesis_groups` domain model. |
| `model_copy(update=)` in SDUI presentation adapters | `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]` | **PURGED**. Replaced by explicit `MatrixScorecardRowDTO` instantiation to preserve strict Pydantic validation. |
| Hardcoded `Color(0xFF2E7D32)` in Studio / Widgets | `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L135]` | **PURGED**. Replaced by `Theme.of(context).colorScheme.primary`. |
| Manual `url.substring()` clipping | `@[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart#L344]` | **PURGED**. Replaced by declarative `TextOverflow.ellipsis`. |
| Silent `except ValueError: continue` nielut | `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py#L98]` | **PURGED**. Replaced by explicit `XaiExtensionType` enum membership verification. |

### 4.2 Retained SSOT Invariants (`What We Will RETAIN`)
1. **Qualitative Coaching Philosophy (`prompt_preservation_mandate`)**: Prompt texts in `seed_data.json` (specifically `OBJECTIVE:`, `ROLE:`, `TASK:`, `MANDATE:`, `<role_enforcement>`, and `<banned_concepts>` sections) are strictly preserved verbatim.
2. **Deterministic UI/PDF Provenance**: `PromptBlock.theory_grounding` retains full metadata (`theoretical_framework`, `academic_citation`, `grounding_type`, `source_url`) for Server-Driven UI (SDUI) and PDF report rendering.
3. **Pydantic V2 Strictness (`strict_pydantic_v2_rust`)**: All DTOs and models enforce `ConfigDict(strict=True, extra="forbid")`.
4. **Dual-Axis Localization SSOT**: Backend manages dynamic data translation; frontend manages static structural labels via `.arb` files.
5. **Universal Zero-Legacy & Atomic Synchronization Mandate (`the_no_legacy_mandate`)**: Quorum strictly enforces universal Zero-Legacy across all environments (development, staging, production). Backwards-compatibility shims, legacy layout structures, and fallback chains are strictly prohibited in domain models and API contracts. All schema evolutions (Pydantic V2 DTOs, Dart Freezed models, Seed Vault, and test fixtures) are executed as atomic, synchronized transactions (`Atomic Migration Protocol`). Local database state is deterministically re-seeded via `uv run python backend_v2/seed/run_seed.py local` without maintaining deprecated schema paths.

---

## 5. Phased Implementation Plan

### Phase 1: Theory Grounding & Epistemic Anchor Sanitization (Chapter 2)

#### Pre-Implementation Technical Debt Cleanups (Phase 1 Pre-requisite)
Before modifying prompt builder logic or mutating seed payloads, execute the following technical debt sweeps and baseline assertions across touched targets:
1. **Audit `v2_core.py#L101-L191` & Remove Banned `.get()` Duck-Typing**: Eliminate `.get()` dictionary lookups in `I18nText` validation and resolution logic, replacing them with explicit `in` membership checks and sanitized non-empty assertions.
2. **Audit Flutter Execution Widgets & Remove Redundant Ternaries**: Prepare `atom_matrix_table_widget.dart` and `matrix_row_item_widget.dart` by identifying hardcoded `locale == 'fi' ? get('fi') : get('en')` ternaries for replacement with direct `get(locale)` delegation.
3. **Verify AST Baseline for Prompt Builder**: Assert that `MatrixSensorPromptBuilder` currently calls `model_dump_json()` and prepare AST test assertions in `test_ast_theory_grounding_guardrails.py` to prevent regression.

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
In `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L30-L52]` and `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L54-L112]`:
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

#### Step 1.4: Unit Tests & Quality Gate for Phase 1
1. In `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` and `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]`: Update test assertions to verify clean `<theory_context>` and `<matrix_objective>` CDATA-shielded pure citation XML structure without raw URLs, without legacy `<STATIC_INSTRUCTION>` wrapping, and assert protection against XML injection characters (`<`, `>`, `&`, `]]>`) via test case `test_build_caching_prefix_theory_grounding_xml_injection_shield` (TC-TG-06).
2. Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py --test`.

---

### Phase 2: ATOMIC `I18nText` Modernization & Systemic Fixture Migration (Chapter 3)
*Atomic Transaction Mandate*: Steps 2.1 through 2.5 MUST be executed as a single coherent cycle before triggering the Quality Gate, guaranteeing zero `extra="forbid"` crashes across the 1300+ test suite and database seed.

#### Step 2.1: Python Domain Model Update (`v2_core.py`)
In `@[backend_v2/models/v2_core.py#L101-L191]`:
1. Remove `default_locale` field from `I18nText`.
2. Define `translations: dict[str, str] = Field(description="Dictionary mapping locale code to translated string, specifically: {'fi': 'Teksti', 'en': 'Text'}.")` without `default_factory=dict`, ensuring that instantiation without translations raises a Pydantic `ValidationError`.
3. Update `@model_validator(mode="after") def validate_i18n` to sanitize all locale keys (`strip().lower()`), enforce that all translation values are stripped non-empty strings, and ensure `"en"` is strictly present via `"en" not in self.translations` without `.get()` duck-typing:
   ```python
   @model_validator(mode="after")
   def validate_i18n(self) -> I18nText:
       """Validates that English translation is always present and all translations are non-empty.

       Raises:
           AppException: If 'en' is missing/empty or any translation contains only whitespace.

       Returns:
           The validated I18nText instance.
       """
       # 1. Enforce baseline fallback: 'en' translation must ALWAYS exist and be non-empty.
       if "en" not in self.translations or not self.translations["en"].strip():
           msg = (
               "I18nText must contain a valid English ('en') translation as a baseline fallback. "
               f"Payload: {self.translations}"
           )
           logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
           raise AppException(
               message=msg,
               status_code=status.HTTP_400_BAD_REQUEST,
               details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
           )

       # 2. Sanitize and validate all translation entries
       cleaned: dict[str, str] = {}
       for locale_key, text_val in self.translations.items():
           if not isinstance(text_val, str) or not text_val.strip():
               msg = f"I18nText translation for locale '{locale_key}' must be a non-empty string."
               logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
               raise AppException(
                   message=msg,
                   status_code=status.HTTP_400_BAD_REQUEST,
                   details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
               )
           cleaned[locale_key.strip().lower()] = text_val.strip()

       object.__setattr__(self, "translations", cleaned)
       return self
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

#### Step 2.2: Flutter Freezed Model Update (`i18n_text.dart`), 1-Hop Caller Cleanups & Unit Tests
1. In `@[client_app_v2/lib/shared/models/i18n_text.dart]`:
   - Remove `@JsonKey(name: 'default_locale') @Default('en') String defaultLocale` from `I18nText` Freezed model.
   - Define `required Map<String, String> translations` without `@Default` (strictly purging `@Default` to guarantee that missing or null `translations` keys fail fast with `CheckedFromJsonException` during deserialization):
     ```dart
     @freezed
     abstract class I18nText with _$I18nText {
       const I18nText._();

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
2. Clean up 1-hop callers and Studio components:
   - In `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L187-L193]` and `#L332-L333`: Replace ternary `locale == 'fi' ? m.labelI18n.get('fi') : m.labelI18n.get('en')` with `m.labelI18n.get(locale)`.
   - In `@[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart#L52-L54]`: Replace ternary `locale == 'fi' ? matrix.labelI18n.get('fi') : matrix.labelI18n.get('en')` with `matrix.labelI18n.get(locale)`.
   - In `@[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart]`: Remove `defaultLocale` state tracking and bind text editing directly to `translations` map.
   - In `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart#L239-L260]`: Replace local `isEmptyI18n(text)` with `text?.isEmpty ?? true`.
   - In `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L135]`: Replace hardcoded `backgroundColor: const Color(0xFF2E7D32)` with `backgroundColor: Theme.of(context).colorScheme.primary`, and replace generic `throw Exception("Workflow ID is missing")` on L125 with `throw AppException.validation(l10n.workflowIdMissingError);`.
   - In `@[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart#L344]`: Purge manual `url.substring(0, 40)` clipping in favor of declarative `TextOverflow.ellipsis`.
   - Note on Error Containment: All widget tree evaluations of `I18nText.get()` operate under the protection of root-level `AppExceptionBoundary` in `app.dart` (and sub-tree boundaries in Studio views), ensuring that any validation failure displays an auditable Diagnostic Node rather than corrupting memory or crashing the process.
3. Create unit test suite `[NEW]` `@[client_app_v2/test/shared/models/i18n_text_test.dart]` testing target match, English fallback, Fail-Fast on missing/whitespace translations, CheckedFromJsonException on missing translations key, and state helpers.
4. Run Flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/shared/models/i18n_text.dart --build`.

#### Step 2.3: Deterministic Pruning of `default_locale` across 500 Instances in `seed_data.json`
*Vault Mutation Exception*: This bulk 500-instance migration requires an explicit exception to the `inline_terminal_scripting` ban. Write and execute an atomic Python script in the scratch directory (`scratch/prune_default_locale_seed.py`) to strip all `"default_locale": "..."` keys from `backend_v2/seed/seed_data.json` while preserving all other keys. The script MUST: (a) parse via `json.load()`, (b) recursively delete `default_locale`, (c) output formatted JSON matching CRLF line endings, and (d) verify JSON integrity via `json.loads()` dry run.

#### Step 2.4: Systemic Test Fixtures Migration across 1300+ Test Cases
Write and execute an atomic AST/regex migration script `scratch/migrate_i18n_test_fixtures.py` targeting all `.py` files in `backend_v2/tests/` containing string literal `default_locale` (resolved dynamically via `grep_search` at execution time) to strip `default_locale` kwargs and dictionary entries.

#### Step 2.5: Re-seed Database & Atomic Quality Gate Verification
1. Re-seed local development database: `uv run python backend_v2/seed/run_seed.py local`.
2. Run backend quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/tests/ --test`.
3. Run Flutter quality gate: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/ --build`.

---

### Phase 3: ATOMIC `OutputProfile`, SDUI Dumb Painter & Localization Parity (Chapter 5)
*Atomic Transaction Mandate*: Steps 3.1 through 3.5 MUST be executed as a single coherent cycle before triggering the Quality Gate, ensuring backend DTOs, Flutter Freezed models, seed data, and adapters compile with 100% parity. This enforces the **Monorepo Atomic Migration Protocol** (preventing the `Strictness Paradox` in development) and aligns with the production **Deployment Synchronization Protocol** (Forced Update Gate `X-Min-Client-Version` -> Atomic Backend + Seed Rollout -> Client Ingress Sanitization).

#### Pre-Implementation Technical Debt Cleanups (SDUI Adapters Sweep - Phase 3 Pre-requisite)
Before modifying backend DTOs or refactoring profile layout logic, execute the following technical debt sweeps across all touched SDUI presentation adapters:
1. **Verify `WarningCardAdapter` Migration**: Confirm that `WarningCardAdapter` module-level constant was cleanly migrated to `LocalizationService.translate("alert_starvation_insufficient_data", context.locale)` in Phase 2 Step 2.1.
2. **Eradicate Hardcoded Translation Dictionaries & Lazy Ternaries in `PrintableSourcesAdapter`**: Remove `PRINTABLE_SOURCES_RULES` dictionary and lazy fallback `locale = context.locale if context.locale in ("fi", "en") else "en"`. Resolve the header title strictly via `LocalizationService.translate("sources_and_bibliography_title", context.locale)`.
3. **Eradicate `model_copy(update=)` in `MatrixGraphsAdapter`**: Replace `axes = [axis.model_copy(update={"inner_sdui_blocks": []}) for axis in axes]` with explicit `MatrixScorecardRowDTO` instantiation, ensuring full Pydantic validation:
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
4. **Decouple `XaiHighlightsAdapter` & Eradicate Silent Nielut**: Migrate extension accordion titles to resolve strictly through `LocalizationService.translate(f"ext_{ext_enum.value.lower()}", context.locale)`. Eradicate silent `except ValueError: logger.warning(...); continue` on L98 in favor of explicit enum membership validation (`if item.extension_type not in XaiExtensionType._value2member_map_:`), logging an RFC 7807 error or skipping safely before attempting instantiation.

#### Step 3.1: Backend Static L10n Dictionaries & LocalizationService Formatting
1. **Complete Backend Static Translation Tables (`@[backend_v2/l10n/en.json]` and `@[backend_v2/l10n/fi.json]`)**:
   - Add all 17 `metric_mappings` keys (`metadata_user`, `metadata_organization`, `metadata_scoring_engine`, `metadata_strictness`, `variance_mechanical`, `variance_cognitive`, `variance_total`, `variance_fallback_explanation`, `alignment_verdict`, `alignment_aligned`, `alignment_misaligned`, `jargon_score`, `authenticity_level`, `level_high`, `level_medium`, `level_low`, `authenticity_fallback_explanation`).
   - Add `user_role_mappings` keys (`role_passenger`, `role_navigator`, `role_driver`, `role_architect`).
   - Add `matrix_column_labels` keys (`col_label`, `col_distribution`, `col_row_explanation`, `col_quotes`, `col_normalized_score`, `col_score`).
   - Add `extension_labels` keys (`ext_variance_validation`, `ext_authenticity_evaluation`).
2. **Extend `LocalizationService` (`@[backend_v2/services/localization.py]`) with Formatting Helpers**:
   - `format_date(dt: datetime, locale: str) -> str`: fi: `26.08.2026 klo 06:44`, en: `2026-08-26 06:44`.
   - `format_score(value: float, locale: str) -> str`: fi: `3,50`, en: `3.50`.
   - `format_percent(ratio: float, locale: str) -> str`: fi: `85,2 %`, en: `85.2%`.
   - `format_cost(amount: float, locale: str) -> str`: fi: `0,04 $`, en: `$0.04` (Enforces strict token cost notation in USD per LLM provider billing conventions, localized with Finnish decimal comma and postfix currency symbol).
3. **Update Unit Tests `[MODIFY]` `@[backend_v2/tests/unit/test_localization.py]`**:
   - Verify translation lookups, missing key Fail-Fast `AppException(VALIDATION_FAILED)` behavior, and formatting helpers across locales (`fi`, `en`).

#### Step 3.2: Modernize `OutputProfile` & DTO Schemas (Backend & Frontend)
1. **Backend Domain & DTOs (`v2_core.py` & `models/dtos/output_profile.py`)**:
   - In `@[backend_v2/models/v2_core.py#L1148-L1269]`:
     ```python
     class MatrixSynthesisGroup(V2CoreBase):
         """Logical group of matrices synthesized together into 2D visualizations or narratives."""
         id: str = Field(..., description="Unique group identifier")
         title: I18nText = Field(..., description="Localized group title")
         target_blocks: list[str] = Field(default_factory=list, description="Target matrix block IDs")
         synthesis_directive: str | None = Field(default=None, description="Optional synthesis directive override")
     ```
   - In `OutputProfile` (`v2_core.py` and `models/dtos/output_profile.py`):
     - Remove `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts`.
     - Add `matrix_synthesis_groups: list[MatrixSynthesisGroup] = Field(default_factory=list)`.
2. **Flutter Freezed Model (`output_profile.dart`)**:
   - In `@[client_app_v2/lib/features/studio/models/output_profile.dart]`:
     - Declare `MatrixSynthesisGroup` Freezed model.
     - Update `OutputProfile` Freezed model to match backend schema.
   - Run Flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`.

#### Step 3.3: Refactor SDUI Adapters, Worker & Jinja2 PDF Template (Dumb Painters)
1. **Refactor SDUI Adapters to Produce Pre-Localized DTO Blocks**:
   - In `@[backend_v2/services/sdui/adapters/metadata_adapter.py]`: Produce pre-localized `metadata_lines` and `costs`/`tokens` strings using `LocalizationService.translate()` and `format_cost()` / `format_date()` functions.
   - In `@[backend_v2/services/sdui/adapters/variance_adapter.py]`, `@[backend_v2/services/sdui/adapters/authenticity_adapter.py]`, `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]`: Decouple completely from `profile.metric_mappings` / `user_role_mappings` database fields. Resolve titles, labels, and numbers via `LocalizationService`.
   - In `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]` and `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`: Consume `profile.matrix_synthesis_groups` instead of the legacy `layouts` structure. Resolve column headers strictly via `LocalizationService`.
   - In `@[backend_v2/services/sdui/adapters/warning_card_adapter.py]`, `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`, `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]`: Complete migration to `LocalizationService` without local dictionaries or fallback ternaries.
2. **Jinja2 / WeasyPrint (PDF) & Flutter Client Parity (Dumb Painters)**:
   - In `@[backend_v2/services/pdf_generator.py]`:
     - Register global Fail-Fast helper `raise_unrecognized_sdui_block(block_type)` in `PdfReportService.__init__` which logs an RFC 7807 structured error and raises `AppException(message=..., status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "block_type": ...})`.
     - In `PdfReportService.generate_execution_html()`: Add pre-flight assertion that `report_dto.inner_sdui_blocks` is non-empty, raising `AppException(VALIDATION_FAILED)` if empty or missing.
   - In `@[backend_v2/templates/report_template.jinja2]`:
     - Renders pre-localized `ReportDataDTO` directly without separate dictionary lookup.
     - Purge hardcoded Finnish string `N/A (Ei arvioitu):` on L159 and replace with `{{ l10n.na_not_evaluated_label }}`.
     - Purge lazy fallback ternaries (`if l10n is defined else '...'`) on L225, L238, L242, L244 in favor of strict `l10n.<key>` references backed by `StrictUndefined`.
     - Purge legacy HTML fallback card (`V2 ARCHITECTURE VIOLATION`) on L447-453 in favor of Python-level pre-flight Fail-Fast exception.
     - Add strict `{% else %}` branch in `render_sdui_blocks` macro that invokes `{{ raise_unrecognized_sdui_block(block.block_type if block.block_type is defined else 'UNDEFINED') }}`, instantly halting PDF compilation on unhandled polymorphic blocks.
   - In `@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]`:
     - Renders pre-localized `AnySduiBlock` elements directly via exhaustive Dart 3 pattern matching `switch (block)` without default wildcards (`_ =>`). Flutter's `app_en.arb` and `app_fi.arb` are reserved strictly for UI Chrome (buttons, dialogs, themes).
3. **Update Background Worker & Flutter Studio View**:
   - In `@[backend_v2/worker.py#L591-L1359]`: Iterate over `profile.matrix_synthesis_groups` for matrix synthesis generation.
   - In `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]`: Bind to `matrixSynthesisGroups` model.

#### Step 3.4: Seed Vault `OutputProfile` Migration & Test Fixture Updates
1. Update `OutputProfile` records in `@[backend_v2/seed/seed_data.json#L9180-L9570]` by removing legacy dictionary fields and converting `layouts` to `matrix_synthesis_groups`.
2. Migrate all test fixtures in `backend_v2/tests/` that mock `OutputProfile` (specifically and exhaustively: `test_blueprint.py`, `test_worker_synthesis.py`, `test_variance_adapter.py`) to the new schema.

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
   - `test_seed_output_profile_has_no_legacy_dictionaries`: Assert 0 occurrences of `metric_mappings`, `matrix_column_labels`, and `user_role_mappings` in `OutputProfile` records.
   - `test_seed_output_profile_uses_matrix_synthesis_groups`: Assert `matrix_synthesis_groups` is present and non-empty.
3. Create [NEW] `@[backend_v2/tests/unit/test_l10n_backend_flutter_parity.py]`:
   - `test_backend_json_matches_flutter_arb_keys`: Assert 1:1 key parity between `backend_v2/l10n/*.json` and `client_app_v2/lib/l10n/*.arb`.
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
| **TC-I18N-FLUTTER-01** (Flutter: Target Match) | `test_i18n_text_get_target_locale` | `I18nText(translations: {'fi': 'Käyttäjä', 'en': 'User'})`, `get('fi')` | Returns `'Käyttäjä'` |
| **TC-I18N-FLUTTER-02** (Flutter: Fallback English Default) | `test_i18n_text_get_fallback_en` | `I18nText(translations: {'fi': 'Käyttäjä', 'en': 'User'})`, `get('sv')` | Returns `'User'` (fallback) |
| **TC-I18N-FLUTTER-03** (Flutter: Fail-Fast Missing Target & Fallback) | `test_i18n_text_get_missing_throws_app_exception` | `I18nText(translations: {'de': 'Benutzer'})`, `get('fr', fallback: 'en')` | Throws `AppException.validation` with available keys list |
| **TC-I18N-FLUTTER-04** (Flutter: Fail-Fast Whitespace / Empty String) | `test_i18n_text_get_whitespace_throws_app_exception` | `I18nText(translations: {'fi': '   ', 'en': ''})`, `get('fi')` | Throws `AppException.validation` (no silent empty string bypass) |
| **TC-I18N-FLUTTER-05** (Flutter: Helpers isEmpty & isNotEmpty) | `test_i18n_text_is_empty_helpers` | `I18nText(translations: {'en': '  '})`, `I18nText(translations: {'en': 'User'})` | `isEmpty == true`, `isNotEmpty == false`, `has('en') == false` |
| **TC-I18N-FLUTTER-06** (Flutter: Fail-Fast Deserialization on Missing Key) | `test_i18n_text_from_json_missing_translations_throws` | `jsonDecode('{}')` or `jsonDecode('{"translations": null}')` | Throws `CheckedFromJsonException` / `FormatException` |
| **TC-SDUI-01** (Metadata: Key-Value Output) | `test_metadata_adapter_emits_structured_keys` | Context with `user_name="Matti Meikäläinen"` | SDUI payload contains `{key: "user", value: "Matti Meikäläinen"}` without hardcoded Finnish label |
| **TC-SDUI-02** (Synthesis Groups: Group Dispatch) | `test_worker_iterates_matrix_synthesis_groups` | Profile with 2 `MatrixSynthesisGroup` objects | Emits 2 discrete synthesis tasks targeted at group member matrices |
| **TC-SDUI-03** (Matrix Graphs: Explicit Row DTO Instantiation) | `test_matrix_graphs_adapter_instantiates_row_dtos_without_model_copy` | Adapter input with `text_delivery_mode="titles_only"` | Produces valid `MatrixScorecardRowDTO` instances with `inner_sdui_blocks=[]` without calling `model_copy(update=)` |
| **TC-L10N-01** (Localization Service: Lookups & Fail-Fast) | `test_localization_service_translate_and_formatting` | `LocalizationService.translate("metadata_user", "fi")`, `format_cost(12.5, "fi")` | Returns `"Käyttäjä"` and `"12,50 $"`; missing key raises `AppException(VALIDATION_FAILED)` |
| **TC-L10N-02** (L10n Parity: Backend JSON vs Flutter ARB) | `test_backend_json_matches_flutter_arb_keys` | `backend_v2/l10n/*.json` vs `client_app_v2/lib/l10n/*.arb` | 1:1 key parity between Backend and Flutter static translation keys |
| **TC-SDUI-PARITY-01** (AST Guardrail: SDUI Block Exhaustiveness in Jinja & Dart) | `test_all_sdui_blocks_handled_in_jinja_and_dart` | `sdui.py`, `report_template.jinja2`, `sdui_blocks_renderer.dart` | 100% of `AnySduiBlock` union variants are handled in both Jinja macro branches and Dart switch pattern match |
| **TC-SDUI-PARITY-02** (Backend PDF Jinja Golden Master Semantic DOM Rendering) | `test_jinja_sdui_golden_master_rendering` | `sdui_golden_master.json` | Generates HTML via `PdfReportService`, verifies all 17 blocks render headings, paragraphs, citations, badges, tables with BeautifulSoup |
| **TC-SDUI-PARITY-03** (Flutter SDUI Golden Master Semantic Widget Rendering) | `test_flutter_sdui_golden_master_rendering` | `sdui_golden_master.json` | Headless widget test verifies `SduiBlocksRenderer` renders all text nodes, citations, badges, tables with 1:1 semantic parity |
| **TC-SDUI-PARITY-04** (AST Guardrail: Jinja Template Field Attribute Validity) | `test_jinja_ast_attribute_validity` | `report_template.jinja2` AST | 100% of accessed `block.*` field attributes exist on corresponding Pydantic `AnySduiBlock` models |
| **TC-SDUI-PARITY-05** (Fail-Fast: Jinja Unrecognized SDUI Block) | `test_jinja_raises_app_exception_on_unrecognized_block_type` | `ReportDataDTO` with unsupported synthetic `block_type="unsupported_quantum_widget"` | `PdfReportService.generate_execution_html()` logs RFC 7807 error and raises `AppException(VALIDATION_FAILED)` |
| **TC-AST-10** (AST Guardrail: Epistemic Anchor Purge) | `test_seed_matrices_have_no_epistemic_anchor_in_ai_description` | `seed_data.json` | 0 occurrences of `EPISTEMIC ANCHOR:` across all 13 matrices |
| **TC-AST-11** (AST Guardrail: Default Locale Purge) | `test_seed_has_no_default_locale` | `seed_data.json` | 0 occurrences of `"default_locale"` across entire seed vault |
| **TC-AST-12** (AST Guardrail: OutputProfile Clean Dictionaries) | `test_seed_output_profile_has_no_legacy_dictionaries` | `seed_data.json` | 0 occurrences of legacy translation dictionaries in OutputProfile |

---

## 7. Definition of Done (DoD) & Verification Plan

### 7.1 Definition of Done (DoD) Checklist
- [ ] `seed_data.json` backup recorded in `backend_v2/seed/backups/`.
- [ ] All 13 matrix blocks in `seed_data.json` sanitized by removing duplicate `EPISTEMIC ANCHOR:` tails; qualitative prompt definitions preserved verbatim.
- [ ] `MatrixSensorPromptBuilder.build_caching_prefix` formats pure `<theory_context>` and `<matrix_objective>` XML blocks with `TemplateProcessor.safe_interpolate()` CDATA Breakout Shielding, omitting raw URLs from LLM prompt payloads.
- [ ] `default_locale` removed from `I18nText` in `backend_v2/models/v2_core.py` and `client_app_v2/lib/shared/models/i18n_text.dart`; `translations` defined as strictly required (`Field(...)` in Python, `required Map<String, String>` without `@Default` in Dart); `isEmpty`, `isNotEmpty`, `has()`, and Fail-Fast `get()` implemented in Flutter.
- [ ] 500 occurrences of `"default_locale"` pruned from `backend_v2/seed/seed_data.json`.
- [ ] 1300+ test fixtures migrated in `backend_v2/tests/` to eliminate `default_locale` and legacy `metric_mappings` mocks.
- [ ] 1-hop callers in Flutter execution widgets (`atom_matrix_table_widget.dart`, `matrix_row_item_widget.dart`), `i18n_text_field.dart`, `profile_editor_view.dart` (`Color` & `throw Exception`), `xai_evidence_box.dart` (`substring`), and `output_profile_controller.dart` modernized.
- [ ] `OutputProfile` modernized: `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts` replaced with `matrix_synthesis_groups` in `v2_core.py`, `models/dtos/output_profile.py`, and `output_profile.dart`.
- [ ] Backend static translation tables in `backend_v2/l10n/en.json` and `fi.json` populated with all 17 metric mapping keys, user roles, matrix columns, extension labels, and formatting rules.
- [ ] `LocalizationService` extended with `format_date`, `format_decimal`, `format_score`, `format_percent`, and `format_cost` helpers.
- [ ] SDUI Adapters Technical Debt Swept: `WarningCardAdapter` (`I18N_WARNING_STARVATION`), `VarianceAdapter` (`hasattr`, `.get()`), `AuthenticityAdapter` (`.get()`), `PrintableSourcesAdapter` (rules dictionary, ternary fallback), `XaiHighlightsAdapter` (silent `except ValueError` nielu), and `MatrixGraphsAdapter` (`model_copy(update=)` eradicated) cleaned of anti-patterns and migrated to `LocalizationService`.
- [ ] `MetadataAdapter`, `VarianceAdapter`, `AuthenticityAdapter`, `ExecutiveSummaryAdapter`, `MatrixGraphsAdapter`, `MatrixSummaryTableAdapter`, `report_template.jinja2`, and `worker.py` refactored to consume `LocalizationService` and `matrix_synthesis_groups` as pre-localized SDUI blocks.
- [ ] `report_template.jinja2` and `PdfReportService` sanitized: `raise_unrecognized_sdui_block` Fail-Fast helper registered; legacy HTML fallback card purged; hardcoded Finnish string `N/A (Ei arvioitu)` on L159 replaced with `{{ l10n.na_not_evaluated_label }}`; lazy fallback ternaries `if l10n is defined else '...'` purged in favor of strict `l10n.<key>` references backed by `StrictUndefined`.
- [ ] `sdui_golden_master.json` fixture created containing populated instances of all 17 `AnySduiBlock` variants.
- [ ] SDUI presentation parity test suite implemented and passing in `backend_v2/tests/unit/test_sdui_template_parity.py` (AST block exhaustiveness guardrail, Jinja AST field attribute validator, unrecognized block Fail-Fast assertion, and BeautifulSoup semantic DOM test).
- [ ] Flutter SDUI golden master parity test implemented and passing in `client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart`.
- [ ] Flutter Freezed models generated via `build_runner` and Studio profile tab updated.
- [ ] Local test database re-seeded via `uv run python backend_v2/seed/run_seed.py local`.
- [ ] AST guardrails implemented and passing in `test_ast_theory_grounding_guardrails.py` and `test_seed_architectural_guardrails.py`.
- [ ] Backend-Flutter translation parity test implemented and passing in `backend_v2/tests/unit/test_l10n_backend_flutter_parity.py`.
- [ ] Unit tests for `LocalizationService` updated and passing in `backend_v2/tests/unit/test_localization.py`.
- [ ] Flutter unit tests implemented and passing in `client_app_v2/test/shared/models/i18n_text_test.dart`.
- [ ] Full backend audit loop passes: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
- [ ] Full Flutter audit loop passes: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.

### 7.2 Verification Execution Commands
```powershell
# 1. Run Unit Tests for Theory Grounding, I18nText, L10n & Presentation Parity (Backend & Flutter)
uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py backend_v2/tests/unit/test_localization.py backend_v2/tests/unit/test_l10n_backend_flutter_parity.py backend_v2/tests/unit/test_sdui_template_parity.py
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

