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
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
</required_context_rules>

# EPIC 148: Domain Model SSOT & Presentation Localization Modernization

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Objective
EPIC 148 standardizes and modernizes Quorum's domain data models and localization architecture across Python backend services, the SQLite/JSON seed vault, and the Flutter desktop client. The epic consolidates Chapters 2, 3, 5, and 6 of `docs/arkkitehtuurin_parannuskohteet.md` to:
1. Establish the **Epistemic Separation Paradigm** for theory grounding: prune redundant `EPISTEMIC ANCHOR:` prompt tails across all 13 matrix blocks in `seed_data.json`, format pure `<theory_context>` XML citations without raw URL token leakage during prompt compilation, and preserve structured `TheoryGrounding` metadata exclusively for UI/PDF presentation.
2. Eradicate redundant `default_locale` attributes across backend and frontend `I18nText` data models and 500 instances in `seed_data.json`, shifting language fallback resolution dynamically to execution context parameters (`target_locale`, with global fallback `"en"`).
3. Modernize `OutputProfile` and Server-Driven UI (SDUI) localization by migrating static UI dictionaries (`metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`) out of the backend database into frontend `.arb` resource files, transforming `MetadataAdapter` into structured key-value envelopes, and replacing legacy V1 `layouts` arrays with strongly-typed `matrix_synthesis_groups`.
4. Execute the 5-phase **Atomic Migration Protocol** to ensure strict Pydantic V2 (`extra="forbid"`) and Flutter Freezed compatibility without silent fallbacks, duct-tape validators, or broken test fixtures.

### 1.2 Problem Statement & Root Cause Analysis
1. **Theory Grounding Dual Injection & Prompt Bloat (Luku 2)**: In `@[backend_v2/seed/seed_data.json#L336-L6900]`, epistemic and academic grounding anchors are duplicated across both `PromptBlock.ai_description` (as freeform `EPISTEMIC ANCHOR:` text blocks) and `PromptBlock.theory_grounding` (as structured `TheoryGrounding` DTOs). When `MatrixSensorPromptBuilder` compiles prompts, it injects both the raw text description and the structured object with raw URLs (`source_url`), triggering prompt duplication, URL token bloat, XML syntax corruption risks, and Single Source of Truth (SSOT) drift.
2. **`I18nText.default_locale` Redundancy (Luku 3)**: In `@[backend_v2/models/v2_core.py#L99-L189]`, `@[client_app_v2/lib/shared/models/i18n_text.dart]`, and across 500 records in `seed_data.json`, every `I18nText` object hardcodes `"default_locale": "fi"`. This conflates static dictionary storage with dynamic runtime resolution, creates internal validation contradictions with the global `"en"` fallback rule, and bloats database payloads across 1300+ test fixtures.
3. **`OutputProfile` Presentation Drift & Dual-Axis Localization Conflicts (Luku 5)**: In `@[backend_v2/seed/seed_data.json#L9180-L9570]`, `OutputProfile` persists hundreds of lines of static UI label translations in backend dictionaries (`metric_mappings`, `matrix_column_labels`, `user_role_mappings`). `MetadataAdapter` concatenates labels with values in Python strings, violating the "Dumb Painter" principle and creating localization drift against Flutter `.arb` files. Furthermore, `OutputProfile.layouts` retains obsolete V1 fields (`preset_view`, `text_delivery_mode`, `steps: []`) rather than declaring clean matrix synthesis groups.
4. **Fragility Under `extra="forbid"` (Luku 6)**: Pydantic V2 models enforce `strict=True` and `extra="forbid"`. Removing fields without an atomic multi-step migration script immediately causes cascading `ValidationError` failures across 1300+ test fixtures and corrupts local database state (`db_v2.json`).

---

## 2. Scope & File Modification Boundary

### 2.1 TARGET Files (Editable)
- `[MODIFY]` `@[backend_v2/seed/seed_data.json]` (Sanitize all 13 matrices by removing `EPISTEMIC ANCHOR:` tails; prune 500 instances of `default_locale`; prune `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels` from `OutputProfile`; replace `layouts` with `matrix_synthesis_groups`)
- `[MODIFY]` `@[backend_v2/models/v2_core.py#L99-L189]` and `@[backend_v2/models/v2_core.py#L1146-L1267]` (Remove `default_locale` from `I18nText` and update `resolve()`; remove legacy `layouts` and dictionary mappings from `OutputProfile` and define `MatrixSynthesisGroup` domain model)
- `[MODIFY]` `@[backend_v2/models/dtos/output_profile.py]` (Remove `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts`; add `matrix_synthesis_groups`)
- `[MODIFY]` `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L54-L112]` (Format pure `<theory_context>\n{citation}\n</theory_context>` XML block, omitting raw URLs)
- `[MODIFY]` `@[client_app_v2/lib/shared/models/i18n_text.dart]` and generated `.freezed.dart` / `.g.dart` (Remove `defaultLocale` from Freezed model; add `isEmpty`, `isNotEmpty`, `has(langCode)` helpers; update `get(String? langCode, {String fallback = 'en'})` method with Fail-Fast `AppException.validation`)
- `[MODIFY]` `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]` (Remove redundant ternaries `locale == 'fi' ? get('fi') : get('en')` and pass `locale` directly to `get(locale)`)
- `[MODIFY]` `@[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart]` (Remove redundant ternaries and pass `locale` directly to `get(locale)`)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart]` (Remove `defaultLocale` state tracking and bind text editing directly to `translations` map)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]` (Replace ad-hoc `isEmptyI18n()` helper with SSOT `i18nText.isEmpty`)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/models/output_profile.dart]` and generated `.freezed.dart` / `.g.dart` (Update Freezed model: remove `metricMappings`, `matrixColumnLabels`, `userRoleMappings`, `extensionLabels`; replace `layouts` with `matrixSynthesisGroups`)
- `[MODIFY]` `@[backend_v2/l10n/en.json]` and `@[backend_v2/l10n/fi.json]` (Populate complete static translation tables for Backend SSOT report generation including all 17 metric mapping keys, user roles, matrix columns, extension labels, and formatting rules)
- `[MODIFY]` `@[backend_v2/services/localization.py]` (Extend with type-safe formatting helpers: `format_date()`, `format_decimal()`, `format_score()`, `format_percent()`, and `format_cost()`)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/metadata_adapter.py]` (Refactor to emit pre-localized SDUI blocks using `LocalizationService` for labels, dates, costs, and tokens)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/variance_adapter.py]`, `@[backend_v2/services/sdui/adapters/authenticity_adapter.py]`, `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]` (Refactor to decouple from `profile.metric_mappings` / `user_role_mappings` and resolve static labels and numeric formatting via `LocalizationService`)
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]` and `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]` (Consume `matrix_synthesis_groups` instead of legacy `layouts`, resolving column headers via `LocalizationService`)
- `[MODIFY]` `@[backend_v2/templates/report_template.jinja2]` (Ensure all table column headers, metadata labels, and legends resolve strictly via pre-localized DTOs and `l10n` context dictionary)
- `[MODIFY]` `@[backend_v2/worker.py#L591-L1359]` (Update background synthesis job loop to iterate over `profile.matrix_synthesis_groups`)
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]` (Update studio layout editor to bind to `matrix_synthesis_groups`)
- `[NEW]` `@[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]` (AST guardrail suite locking pure theory grounding invariants)
- `[NEW]` `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]` (AST guardrail suite asserting zero occurrences of `default_locale`, `EPISTEMIC ANCHOR:`, and legacy `layouts` dictionaries in seed vault)
- `[NEW]` `@[backend_v2/tests/unit/services/test_localization_service.py]` (Unit test suite verifying `LocalizationService` translation lookups, fallback behaviors, and formatting helpers)
- `[NEW]` `@[backend_v2/tests/unit/test_l10n_backend_flutter_parity.py]` (Parity test suite asserting 1:1 key parity between `backend_v2/l10n/*.json` and `client_app_v2/lib/l10n/*.arb`)
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` and `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]` (Update test assertions for pure `<theory_context>` XML formatting)
- `[MODIFY]` `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_workflows.py]`, `@[backend_v2/tests/unit/services/test_blueprint.py]` (Migrate test fixtures to new `I18nText` and `OutputProfile` schemas and remove obsolete `metric_mappings` mocks)
- `[NEW]` `@[client_app_v2/test/shared/models/i18n_text_test.dart]` (Unit test suite asserting Flutter `I18nText` Fail-Fast `AppException.validation`, fallback resolution, and `isEmpty`/`isNotEmpty`/`has` helpers)
- `[MODIFY]` `@[client_app_v2/test/features/studio/views/widgets/profile/tabs/profile_layouts_tab_test.dart]` and `@[client_app_v2/test/]` fixtures (Update Flutter widget test suite and mock `I18nText` instances to match new schemas and non-empty translations)

### 2.2 CONTEXT Files (Read-Only)
- `@[backend_v2/models/v2_core.py#L192-L205]` (`TheoryGrounding` schema SSOT)
- `@[backend_v2/settings.py]` (Backend global configuration SSOT)
- `@[docs/arkkitehtuurin_parannuskohteet.md]` (Architectural Improvement Roadmap Reference)

---

## 3. Technical Debt Itemization & Pre-Implementation Remediation

Specifically and exhaustively, the following 14 technical debt items are identified for remediation:
1. **Duplicate Theory Anchors in Seed Vault**: All 13 matrix blocks in `seed_data.json` duplicate bibliographic text in `ai_description`, creating token bloat and risk of semantic drift.
2. **Raw JSON Injected in Static System Prompts**: `MatrixSensorPromptBuilder` calls `theory_grounding.model_dump_json()`, injecting raw JSON into system rule blocks.
3. **URL Token Bloat & Prompt Leakage**: Raw `source_url` strings are emitted in LLM prompt payloads rather than reserved exclusively for client UI rendering and PDF reports.
4. **Redundant `default_locale` in `I18nText`**: 500 `I18nText` blocks in `seed_data.json` declare `"default_locale": "fi"`, conflicting with runtime context-driven language selection.
5. **Static UI Dictionaries in Database**: `OutputProfile` contains `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, and `extension_labels` in backend persistence, violating Dual-Axis Localization.
6. **Backend String Concatenation in `MetadataAdapter`**: `MetadataAdapter` combines translated labels with values in Python strings, breaking the Dumb Painter paradigm.
7. **Obsolete V1 `layouts` Arrays**: `OutputProfile.layouts` retains deprecated fields (`preset_view`, `text_delivery_mode`, `steps: []`) instead of a focused `matrix_synthesis_groups` structure.
8. **Worker Couplings on `layouts`**: `worker.py` and SDUI adapters depend on `profile.layouts` for synthesis loop routing.
9. **Flutter Freezed Schema Drift**: `i18n_text.dart` and `output_profile.dart` Freezed models reflect deprecated fields, requiring regeneration via `build_runner`.
10. **Test Fixture Schema Drift**: 1300+ test assertions in `backend_v2/tests/` hardcode `default_locale` or legacy profile layout keys.
11. **Missing AST Guardrails for Seed Vault Purity**: The test suite lacks static AST assertions preventing re-introduction of `default_locale` or `EPISTEMIC ANCHOR:` tails.
12. **Unsynchronized Local Database State**: `db_v2.json` must be re-seeded atomically after `seed_data.json` mutations.
13. **Flutter `I18nText` Silent Fallback & Widget Ternary Drift**: `i18n_text.dart` returns `''` on missing translations instead of throwing `AppException.validation`, while `atom_matrix_table_widget.dart` and `matrix_row_item_widget.dart` hardcode `locale == 'fi' ? get('fi') : get('en')` instead of delegating directly to `get(locale)`.
14. **Studio Ad-Hoc `isEmptyI18n` Functions**: `output_profile_controller.dart` implements local ad-hoc `isEmptyI18n()` functions due to missing SSOT `isEmpty`/`isNotEmpty` properties on `I18nText`.

---

## 4. Architectural Impact & Compliance Matrix

### 4.1 Deprecations & Sunset List (`What We Will REMOVE`)
| Deprecated Symbol / Pattern | Location | Replacement / Disposition |
| :--- | :--- | :--- |
| `EPISTEMIC ANCHOR:` prompt tails | `@[backend_v2/seed/seed_data.json#L336-L6900]` | **PURGED**. Retained exclusively in structured `theory_grounding` field. |
| Raw `source_url` in LLM prompts | `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]` | **OMITTED** from LLM prompt payload; retained in DTOs for UI/PDF rendering. |
| `I18nText.default_locale` | `@[backend_v2/models/v2_core.py]`, `@[client_app_v2/lib/shared/models/i18n_text.dart]` | **PURGED**. Replaced by dynamic runtime parameter `target_locale` with `"en"` fallback. |
| `OutputProfile.metric_mappings` | `@[backend_v2/seed/seed_data.json]`, `@[backend_v2/models/v2_core.py]` | **PURGED**. Replaced by frontend `.arb` static localization files. |
| `OutputProfile.matrix_column_labels` | `@[backend_v2/seed/seed_data.json]`, `@[backend_v2/models/v2_core.py]` | **PURGED**. Replaced by frontend `.arb` static localization files. |
| `OutputProfile.user_role_mappings` | `@[backend_v2/seed/seed_data.json]`, `@[backend_v2/models/v2_core.py]` | **PURGED**. Replaced by frontend `.arb` static localization files. |
| `OutputProfile.extension_labels` | `@[backend_v2/seed/seed_data.json]`, `@[backend_v2/models/v2_core.py]` | **PURGED**. Replaced by frontend `.arb` static localization files. |
| `OutputProfile.layouts` | `@[backend_v2/seed/seed_data.json]`, `@[backend_v2/models/v2_core.py]` | **PURGED**. Replaced by clean `matrix_synthesis_groups` domain model. |

### 4.2 Retained SSOT Invariants (`What We Will RETAIN`)
1. **Qualitative Coaching Philosophy (`prompt_preservation_mandate`)**: Prompt texts in `seed_data.json` (specifically `OBJECTIVE:`, `ROLE:`, `TASK:`, `MANDATE:`, `<role_enforcement>`, and `<banned_concepts>` sections) are strictly preserved verbatim.
2. **Deterministic UI/PDF Provenance**: `PromptBlock.theory_grounding` retains full metadata (`theoretical_framework`, `academic_citation`, `grounding_type`, `source_url`) for Server-Driven UI (SDUI) and PDF report rendering.
3. **Pydantic V2 Strictness (`strict_pydantic_v2_rust`)**: All DTOs and models enforce `ConfigDict(strict=True, extra="forbid")`.
4. **Dual-Axis Localization SSOT**: Backend manages dynamic data translation; frontend manages static structural labels via `.arb` files.

---

## 5. Phased Implementation Plan

### Phase 1: Theory Grounding & Epistemic Anchor Sanitization (Luku 2)

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

#### Step 1.3: Format Pure `<theory_context>` in `MatrixSensorPromptBuilder` with CDATA Breakout Shielding
In `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L54-L112]`:
Refactor theory grounding and matrix objective injection in `MatrixSensorPromptBuilder.build_caching_prefix`:
Replace `ai_desc=matrix_context.theory_grounding.model_dump_json()` with pure citation XML formatting using `TemplateProcessor.safe_interpolate()` (enforcing CDATA encapsulation, Breakout Shielding, and excluding URL token bloat):
```python
if matrix_context:
    if matrix_context.matrix_objective:
        obj_content = TemplateProcessor.safe_interpolate(
            "<matrix_objective>\n{obj}\n</matrix_objective>",
            obj=matrix_context.matrix_objective,
        )
        blocks.append(
            MatrixSensorPromptBuilder._create_ephemeral_block(
                block_id="blk_2222222222222222",
                category_id=PromptBlockCategory.SYSTEM_RULE,
                ai_desc=obj_content,
            )
        )
    if matrix_context.theory_grounding and matrix_context.theory_grounding.citation_reference:
        citation = matrix_context.theory_grounding.citation_reference.strip()
        if citation:
            theory_content = TemplateProcessor.safe_interpolate(
                "<theory_context>\n{citation}\n</theory_context>",
                citation=citation,
            )
            blocks.append(
                MatrixSensorPromptBuilder._create_ephemeral_block(
                    block_id="blk_3333333333333333",
                    category_id=PromptBlockCategory.SYSTEM_RULE,
                    ai_desc=theory_content,
                )
            )
```

#### Step 1.4: Unit Tests & Quality Gate for Phase 1
1. In `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` and `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]`: Update test assertions to verify `<theory_context>` CDATA-shielded pure citation XML structure without raw URLs and assert protection against XML injection characters (`<`, `>`, `&`, `]]>`).
2. Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py --test`.

---

### Phase 2: `I18nText.default_locale` Eradication (Luku 3)

#### Step 2.1: Python Domain Model Update (`v2_core.py`)
In `@[backend_v2/models/v2_core.py#L99-L189]`:
1. Remove `default_locale` field from `I18nText`.
2. Refactor `resolve()` method to enforce the Universal Fail-Fast mandate (`the_duct_tape_ban` & `dynamic_translation_fail_fast`):
   ```python
   def resolve(self, target_locale: str | None = None, fallback_locale: str = "en") -> str:
       """Strictly typed Fail-Fast resolution of localized text.

       Args:
           target_locale: The requested locale code (e.g., 'fi', 'fi-FI', 'sv').
           fallback_locale: The baseline fallback locale (defaults to 'en').

       Returns:
           The resolved non-empty localized string.

       Raises:
           AppException: If neither target_locale nor fallback_locale can be resolved to a non-empty string.
       """
       if target_locale:
           target_lang = target_locale.split("-")[0].lower()
           val = self.translations.get(target_lang)
           if val and val.strip():
               return val.strip()

       fallback_lang = fallback_locale.split("-")[0].lower()
       fallback_val = self.translations.get(fallback_lang)
       if fallback_val and fallback_val.strip():
           return fallback_val.strip()

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
3. Deprecate and remove/refactor legacy `I18nText.get()` to delegate directly to `resolve()` without empty string fallback defaults.

#### Step 2.2: Flutter Freezed Model Update (`i18n_text.dart`), 1-Hop Caller Cleanups & Test Suite
1. In `@[client_app_v2/lib/shared/models/i18n_text.dart]`:
   - Remove `@JsonKey(name: 'default_locale') @Default('en') String defaultLocale` from `I18nText` Freezed model.
   - Update `translations` default to `@Default(<String, String>{}) Map<String, String> translations`.
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
       final normalized = langCode.split('-').first.toLowerCase();
       final val = translations[normalized];
       return val != null && val.trim().isNotEmpty;
     }
     ```
   - Update `get(String? langCode, {String fallback = 'en'})` method to enforce the Universal Fail-Fast mandate (`dynamic_translation_fail_fast`):
     ```dart
     String get(String? langCode, {String fallback = 'en'}) {
       if (langCode != null && langCode.isNotEmpty) {
         final normalized = langCode.split('-').first.toLowerCase();
         final val = translations[normalized];
         if (val != null && val.trim().isNotEmpty) {
           return val.trim();
         }
       }

       final fallbackNormalized = fallback.split('-').first.toLowerCase();
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
3. Create unit test suite `@[client_app_v2/test/shared/models/i18n_text_test.dart]` testing:
   - Target match resolution (`get('fi')` -> `'Käyttäjä'`).
   - Lingua franca fallback resolution (`get('sv', fallback: 'en')` -> `'User'`).
   - Fail-Fast `AppException.validation` on missing target and fallback translations.
   - Fail-Fast `AppException.validation` on empty/whitespace-only translations.
   - `isEmpty`, `isNotEmpty`, and `has()` helper evaluation.
4. Run Flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/shared/models/i18n_text.dart --build`.

#### Step 2.3: Deterministic Pruning of `default_locale` across 500 Instances in `seed_data.json`
Write and execute an atomic Python script in the scratch directory to strip all `"default_locale": "..."` keys from `backend_v2/seed/seed_data.json` while preserving all other keys.

#### Step 2.4: Test Fixtures Migration across 1300+ Test Cases
Write and execute an atomic regex/AST migration script to strip `default_locale` kwargs and dictionary entries from `backend_v2/tests/` fixtures.

#### Step 2.5: Quality Gate for Phase 2
Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/tests/ --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/test/ --build`.

---

### Phase 3: Backend PDF Localization Parity, SDUI Adapters & OutputProfile Modernization (Luku 5)

#### Step 3.1: Backend Static L10n Dictionaries & LocalizationService Formatting
1. **Täydennä Backendin staattiset käännöstiedostot (`@[backend_v2/l10n/en.json]` ja `@[backend_v2/l10n/fi.json]`)**:
   - Lisää kaikki 17 `metric_mappings`-avainta (`metadata_user`, `metadata_organization`, `metadata_scoring_engine`, `metadata_strictness`, `variance_mechanical`, `variance_cognitive`, `variance_total`, `variance_fallback_explanation`, `alignment_verdict`, `alignment_aligned`, `alignment_misaligned`, `jargon_score`, `authenticity_level`, `level_high`, `level_medium`, `level_low`, `authenticity_fallback_explanation`).
   - Lisää `user_role_mappings`-avaimet (`role_passenger`, `role_navigator`, `role_driver`, `role_architect`).
   - Lisää `matrix_column_labels`-avaimet (`col_label`, `col_distribution`, `col_row_explanation`, `col_quotes`, `col_normalized_score`, `col_score`).
   - Lisää `extension_labels`-avaimet (`ext_variance_validation`, `ext_authenticity_evaluation`).
2. **Laajenna `LocalizationService` (`@[backend_v2/services/localization.py]`) Formatting-apureilla**:
   - `format_date(dt: datetime, locale: str) -> str`: fi: `26.08.2026 klo 06:44`, en: `2026-08-26 06:44`.
   - `format_score(value: float, locale: str) -> str`: fi: `3,50`, en: `3.50`.
   - `format_percent(ratio: float, locale: str) -> str`: fi: `85,2 %`, en: `85.2%`.
   - `format_cost(amount: float, locale: str) -> str`: fi: `0,04 $` (tai `0,04 €`), en: `$0.04`.
3. **Luo Yksikkötestit `@[backend_v2/tests/unit/services/test_localization_service.py]`**:
   - Varmistaa käännöshaut, puuttuvien avainten Fail-Fast `AppException(VALIDATION_FAILED)` -käyttäytymisen sekä `format_date`, `format_score`, `format_percent` ja `format_cost` -muotoilujen oikeellisuuden eri lokaaleilla (`fi`, `en`).

#### Step 3.2: Refactor SDUI Adapters, Worker & Jinja2 PDF Template (Dumb Painters)
1. **Refaktoroi SDUI-adapterit Pre-Lokalisoitujen DTO-lohkojen tuottamiseen**:
   - In `@[backend_v2/services/sdui/adapters/metadata_adapter.py]`: Tuottaa valmiiksi lokalisoidut `metadata_lines`- ja `costs`/`tokens`-merkkijonot käyttäen `LocalizationService.translate()` ja `format_cost()` / `format_date()` -funktioita.
   - In `@[backend_v2/services/sdui/adapters/variance_adapter.py]`, `@[backend_v2/services/sdui/adapters/authenticity_adapter.py]`, `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]`: Eristetään täysin `profile.metric_mappings` / `user_role_mappings` -tietokantakentistä. Käytetään `LocalizationService`-palvelua otsikoille ja luvuille.
   - In `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]` ja `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]`: Kulutetaan `profile.matrix_synthesis_groups` `layouts`-rakenteen sijaan. Sarakeotsikot ratkaistaan backendissä valmiiksi `LocalizationService`:n kautta.
2. **Jinja2 / WeasyPrint (PDF) & Flutter Client Pariteetti (Dumb Painters)**:
   - `@[backend_v2/templates/report_template.jinja2]` piirtää valmiiksi lokalisoidun `ReportDataDTO`:n suoraan ilman erillistä sanakirjatulkkausta.
   - Flutterin `sdui_blocks_renderer.dart` piirtää valmiiksi lokalisoidut `AnySduiBlock`-lohkot suoraan. Flutterin `app_en.arb` ja `app_fi.arb` säilytetään puhtaina vain UI Chromelle (painikkeet, dialogit, teemat).
3. **Päivitä Taustatyö & Flutter Studio View**:
   - In `@[backend_v2/worker.py#L591-L1359]`: Iteroi `profile.matrix_synthesis_groups` -ryhmien yli matriisisynteesien generoinnissa.
   - In `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]`: Bindaus `matrixSynthesisGroups`-malliin.

#### Step 3.3: Modernize `OutputProfile` & DTO Schemas (Backend & Frontend)
1. **Backend Domain & DTOs (`v2_core.py` & `models/dtos/output_profile.py`)**:
   - In `@[backend_v2/models/v2_core.py#L1146-L1267]`:
     ```python
     class MatrixSynthesisGroup(V2CoreBase):
         """Logical group of matrices synthesized together into 2D visualizations or narratives."""
         id: str = Field(..., description="Unique group identifier")
         title: I18nText = Field(..., description="Localized group title")
         target_blocks: list[str] = Field(default_factory=list, description="Target matrix block IDs")
         synthesis_directive: str | None = Field(default=None, description="Optional synthesis directive override")
     ```
   - In `OutputProfile` (`v2_core.py` ja `models/dtos/output_profile.py`):
     - Poista `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, ja `layouts`.
     - Lisää `matrix_synthesis_groups: list[MatrixSynthesisGroup] = Field(default_factory=list)`.
2. **Flutter Freezed Model (`output_profile.dart`)**:
   - In `@[client_app_v2/lib/features/studio/models/output_profile.dart]`:
     - Deklaroi `MatrixSynthesisGroup` Freezed model.
     - Päivitä `OutputProfile` Freezed model vastaamaan backendin skeemaa.
   - Aja Flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`.

#### Step 3.4: Seed Vault `OutputProfile` Migration
Päivitä `OutputProfile`-tietueet tiedostossa `@[backend_v2/seed/seed_data.json#L9180-L9570]` poistamalla legacy-sanakirjakentät ja muuttamalla `layouts` muotoon `matrix_synthesis_groups`.

---

### Phase 4: Atomic Fixture Migration, Seed Re-seeding & AST Guardrails (Luku 6)

#### Step 4.1: Deterministic Test Fixtures Migration across 1300+ Test Cases
Suorita atominen AST-/Regex-migraatioskripti `scratch/migrate_seed_and_fixtures.py` poistamaan `default_locale`-, `metric_mappings`- ja vanhat `layouts`-kentät kaikista `backend_v2/tests/` -tiedostoista (mukaan lukien `test_blueprint.py`, `test_worker_synthesis.py`, `test_variance_adapter.py`).

#### Step 4.2: Re-seed Local Database
Varmista JSON-integriteetti ja aja paikallinen uudelleensiemennys:
`uv run python backend_v2/seed/run_seed.py local`.

#### Step 4.3: Create AST Guardrail & L10n Parity Suites
1. Luo [NEW] `@[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]`:
   - `test_seed_matrices_have_no_epistemic_anchor_in_ai_description`: 0 matriisilohkolla on `"EPISTEMIC ANCHOR:"`.
   - `test_seed_matrices_have_valid_theory_grounding`: Kaikilla 13 matriisilohkolla on ei-null `theory_grounding`.
   - `test_matrix_sensor_prompt_builder_ast_uses_pure_theory_citation`: AST varmistaa, ettei `theory_grounding`-oliosta kutsuta `model_dump_json()`.
2. Luo [NEW] `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]`:
   - `test_seed_has_no_default_locale`: 0 esiintymää sanasta `"default_locale"` koko `seed_data.json`-tiedostossa.
   - `test_seed_output_profile_has_no_legacy_dictionaries`: 0 esiintymää kentistä `metric_mappings`, `matrix_column_labels`, `user_role_mappings` `OutputProfile`-tietueissa.
   - `test_seed_output_profile_uses_matrix_synthesis_groups`: Varmistaa, että `matrix_synthesis_groups` on olemassa ja ei-tyhjä.
3. Luo [NEW] `@[backend_v2/tests/unit/test_l10n_backend_flutter_parity.py]`:
   - `test_backend_json_matches_flutter_arb_keys`: Varmistaa 1:1 avainpariteetin `backend_v2/l10n/*.json` ja `client_app_v2/lib/l10n/*.arb` välillä.

#### Step 4.4: Full Audit Gate Verification
1. Aja backendin laatuportti: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
2. Aja Flutterin laatuportti: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.

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
| **TC-I18N-FLUTTER-01** (Flutter: Target Match) | `test_i18n_text_get_target_locale` | `I18nText(translations: {'fi': 'Käyttäjä', 'en': 'User'})`, `get('fi')` | Returns `'Käyttäjä'` |
| **TC-I18N-FLUTTER-02** (Flutter: Fallback English Default) | `test_i18n_text_get_fallback_en` | `I18nText(translations: {'fi': 'Käyttäjä', 'en': 'User'})`, `get('sv')` | Returns `'User'` (fallback) |
| **TC-I18N-FLUTTER-03** (Flutter: Fail-Fast Missing Target & Fallback) | `test_i18n_text_get_missing_throws_app_exception` | `I18nText(translations: {'de': 'Benutzer'})`, `get('fr', fallback: 'en')` | Throws `AppException.validation` with available keys list |
| **TC-I18N-FLUTTER-04** (Flutter: Fail-Fast Whitespace / Empty String) | `test_i18n_text_get_whitespace_throws_app_exception` | `I18nText(translations: {'fi': '   ', 'en': ''})`, `get('fi')` | Throws `AppException.validation` (no silent empty string bypass) |
| **TC-I18N-FLUTTER-05** (Flutter: Helpers isEmpty & isNotEmpty) | `test_i18n_text_is_empty_helpers` | `I18nText(translations: {})`, `I18nText(translations: {'en': '  '})` | `isEmpty == true`, `isNotEmpty == false`, `has('en') == false` |
| **TC-SDUI-01** (Metadata: Key-Value Output) | `test_metadata_adapter_emits_structured_keys` | Context with `user_name="Matti Meikäläinen"` | SDUI payload contains `{key: "user", value: "Matti Meikäläinen"}` without hardcoded Finnish label |
| **TC-SDUI-02** (Synthesis Groups: Group Dispatch) | `test_worker_iterates_matrix_synthesis_groups` | Profile with 2 `MatrixSynthesisGroup` objects | Emits 2 discrete synthesis tasks targeted at group member matrices |
| **TC-L10N-01** (Localization Service: Lookups & Fail-Fast) | `test_localization_service_translate_and_formatting` | `LocalizationService.translate("metadata_user", "fi")`, `format_cost(12.5, "fi")` | Returns `"Käyttäjä"` ja `"12,50 $"`; missing key raises `AppException(VALIDATION_FAILED)` |
| **TC-L10N-02** (L10n Parity: Backend JSON vs Flutter ARB) | `test_backend_json_matches_flutter_arb_keys` | `backend_v2/l10n/*.json` vs `client_app_v2/lib/l10n/*.arb` | 1:1 key parity between Backend and Flutter static translation keys |
| **TC-AST-10** (AST Guardrail: Epistemic Anchor Purge) | `test_seed_matrices_have_no_epistemic_anchor_in_ai_description` | `seed_data.json` | 0 occurrences of `EPISTEMIC ANCHOR:` across all 13 matrices |
| **TC-AST-11** (AST Guardrail: Default Locale Purge) | `test_seed_has_no_default_locale` | `seed_data.json` | 0 occurrences of `"default_locale"` across entire seed vault |
| **TC-AST-12** (AST Guardrail: OutputProfile Clean Dictionaries) | `test_seed_output_profile_has_no_legacy_dictionaries` | `seed_data.json` | 0 occurrences of legacy translation dictionaries in OutputProfile |

---

## 7. Definition of Done (DoD) & Verification Plan

### 7.1 Definition of Done (DoD) Checklist
- [ ] `seed_data.json` backup recorded in `backend_v2/seed/backups/`.
- [ ] All 13 matrix blocks in `seed_data.json` sanitized by removing duplicate `EPISTEMIC ANCHOR:` tails; qualitative prompt definitions preserved verbatim.
- [ ] `MatrixSensorPromptBuilder.build_caching_prefix` formats pure `<theory_context>` and `<matrix_objective>` XML blocks with `TemplateProcessor.safe_interpolate()` CDATA Breakout Shielding, omitting raw URLs from LLM prompt payloads.
- [ ] `default_locale` removed from `I18nText` in `backend_v2/models/v2_core.py` and `client_app_v2/lib/shared/models/i18n_text.dart`; `isEmpty`, `isNotEmpty`, `has()`, and Fail-Fast `get()` implemented in Flutter.
- [ ] 500 occurrences of `"default_locale"` pruned from `backend_v2/seed/seed_data.json`.
- [ ] 1300+ test fixtures migrated in `backend_v2/tests/` to eliminate `default_locale` and legacy `metric_mappings` mocks.
- [ ] 1-hop callers in Flutter execution widgets (`atom_matrix_table_widget.dart`, `matrix_row_item_widget.dart`), `i18n_text_field.dart`, and `output_profile_controller.dart` modernized.
- [ ] `OutputProfile` modernized: `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts` replaced with `matrix_synthesis_groups` in `v2_core.py`, `models/dtos/output_profile.py`, and `output_profile.dart`.
- [ ] Backend static translation tables in `backend_v2/l10n/en.json` and `fi.json` populated with all 17 metric mapping keys, user roles, matrix columns, extension labels, and formatting rules.
- [ ] `LocalizationService` extended with `format_date`, `format_decimal`, `format_score`, `format_percent`, and `format_cost` helpers.
- [ ] `MetadataAdapter`, `VarianceAdapter`, `AuthenticityAdapter`, `ExecutiveSummaryAdapter`, `MatrixGraphsAdapter`, `MatrixSummaryTableAdapter`, `report_template.jinja2`, and `worker.py` refactored to consume `LocalizationService` and `matrix_synthesis_groups` as pre-localized SDUI blocks.
- [ ] Flutter Freezed models generated via `build_runner` and Studio profile tab updated.
- [ ] Local test database re-seeded via `uv run python backend_v2/seed/run_seed.py local`.
- [ ] AST guardrails implemented and passing in `test_ast_theory_grounding_guardrails.py` and `test_seed_architectural_guardrails.py`.
- [ ] Backend-Flutter translation parity test implemented and passing in `backend_v2/tests/unit/test_l10n_backend_flutter_parity.py`.
- [ ] Unit tests for `LocalizationService` implemented and passing in `backend_v2/tests/unit/services/test_localization_service.py`.
- [ ] Flutter unit tests implemented and passing in `client_app_v2/test/shared/models/i18n_text_test.dart`.
- [ ] Full backend audit loop passes: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
- [ ] Full Flutter audit loop passes: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.

### 7.2 Verification Execution Commands
```powershell
# 1. Run Unit Tests for Theory Grounding, I18nText & L10n Parity (Backend & Flutter)
uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py backend_v2/tests/unit/services/test_localization_service.py backend_v2/tests/unit/test_l10n_backend_flutter_parity.py
uv run python scripts/flutter_audit_loop.py client_app_v2/test/shared/models/i18n_text_test.dart --build

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

