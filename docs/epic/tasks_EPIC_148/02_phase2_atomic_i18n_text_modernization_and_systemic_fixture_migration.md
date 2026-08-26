# Phase 2: ATOMIC I18nText Modernization & Systemic Fixture Migration

**Overview:** Modernize `I18nText` by purging `default_locale` and `@Default`/`default_factory=dict` across backend Pydantic V2 and Flutter Freezed models, enforce required `translations` with strict `@field_validator` and Fail-Fast `resolve()` / `get()`, migrate `warning_card_adapter.py` module-level constant to dynamic `LocalizationService`, prune 500 instances of `default_locale` from `seed_data.json` while populating 4 missing Finnish translations, execute deterministic bulk migration of 1,166 backend test fixtures across 90 files and 157 Flutter fixtures via scratch scripts, and update 1-hop execution widgets and Studio views.
**Target Files:**
- `[MODIFY]` @[backend_v2/models/v2_core.py#L101-L191]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/warning_card_adapter.py]
- `[MODIFY]` @[client_app_v2/lib/shared/models/i18n_text.dart]
- `[MODIFY]` @[backend_v2/seed/seed_data.json]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/execution_report_view.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/widgets/specialist_section.dart]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/profile_editor_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart]
- `[NEW]` @[client_app_v2/test/shared/models/i18n_text_test.dart]
- `[MODIFY]` @[client_app_v2/test/models/matrix_claim_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/models/workflow_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/execution/models/matrix_scorecard_dto_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1. Verify theory grounding prompt builder is clean and test suites pass.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/models/v2_core.py#L101-L191], @[backend_v2/services/sdui/adapters/warning_card_adapter.py], and @[client_app_v2/lib/shared/models/i18n_text.dart].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] `default_locale` removed from `I18nText` in @[backend_v2/models/v2_core.py#L101-L191]; `translations` defined as required `Field(...)` without `default_factory=dict`; `@field_validator("translations")` classmethod implemented for key sanitization and non-empty baseline `'en'` check without `object.__setattr__` frozen mutations; `resolve()` updated with regex locale splitting and Fail-Fast `AppException(VALIDATION_FAILED)`.
    - [x] Synchronous module-level constant migration in @[backend_v2/services/sdui/adapters/warning_card_adapter.py] completed to eliminate `I18N_WARNING_STARVATION = I18nText(default_locale="en", ...)` and resolve warning dynamically via `LocalizationService`.
    - [x] `I18nText` Freezed model in @[client_app_v2/lib/shared/models/i18n_text.dart] updated with explicit `@JsonSerializable(disallowUnrecognizedKeys: true)`, `defaultLocale` removed, `required Map<String, String> translations` enforced without `@Default`, and `isEmpty`, `isNotEmpty`, `has()`, and Fail-Fast `get()` implemented.
    - [x] 1-hop callers and execution UI widgets modernized: @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart], @[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart], @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart], @[client_app_v2/lib/features/execution/views/execution_report_view.dart], @[client_app_v2/lib/shared/widgets/specialist_section.dart], @[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart], @[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart], @[client_app_v2/lib/features/studio/views/profile_editor_view.dart], and @[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart].
    - [x] Localization keys populated in @[client_app_v2/lib/l10n/app_en.arb] and @[client_app_v2/lib/l10n/app_fi.arb].
    - [x] Unit test suite [NEW] @[client_app_v2/test/shared/models/i18n_text_test.dart] created with positive and negative ISTQB partition test cases (TC-I18N-FLUTTER-01 through TC-I18N-FLUTTER-07).
    - [x] 500 occurrences of `"default_locale"` pruned from @[backend_v2/seed/seed_data.json] via deterministic scratch script (`scratch/prune_default_locale_seed.py`), and 4 authentic Finnish translations populated for `prompt_blocks[88]` and `prompt_blocks[89]`.
    - [x] 1,166 backend test fixture references across 90 test files in `backend_v2/tests/` and 157 Flutter test references across 25 files migrated via deterministic scratch scripts (`scratch/migrate_backend_i18n_fixtures.py` and `scratch/migrate_flutter_i18n_fixtures.py`).
    - [x] Local development database re-seeded: `uv run python backend_v2/seed/run_seed.py local`.
    - [x] Quality gates pass: `uv run python scripts/backend_audit_loop.py backend_v2/tests/ --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/test/ --build`.
  </dod_checklist>

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

  <touched_artifacts>
    <backend>@[backend_v2/models/v2_core.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/warning_card_adapter.py]</backend>
    <backend>@[backend_v2/seed/seed_data.json]</backend>
    <frontend>@[client_app_v2/lib/shared/models/i18n_text.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/execution_report_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/shared/widgets/specialist_section.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/profile_editor_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart]</frontend>
    <!-- [NEW] client_app_v2/test/shared/models/i18n_text_test.dart -->
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `OutputProfile.layouts` or delete `OutputLayoutBlock` in Phase 2 (strictly reserved for atomic Phase 3).
    - Do NOT modify `backend_v2/services/pdf_generator.py` or `report_template.jinja2` in Phase 2 (strictly reserved for atomic Phase 3).
    - Do NOT copy `"fi"` text into missing `"en"` keys during seed pruning (Zero-Chimera mandate).
    - Treat read-only context references as immutable:
      - @[backend_v2/models/v2_core.py#L194-L207] (`TheoryGrounding` schema SSOT)
      - @[backend_v2/settings.py] (Backend global configuration SSOT)
  </anti_targets>

  <test_contracts>
    <test name="test_i18n_text_resolve_target_locale" category="positive">
      <input>I18nText(translations={"fi": "Käyttäjä", "en": "User"}), target_locale="fi"</input>
      <expected>Returns "Käyttäjä"</expected>
    </test>
    <test name="test_i18n_text_resolve_fallback_en" category="positive">
      <input>I18nText(translations={"fi": "Käyttäjä", "en": "User"}), target_locale="sv"</input>
      <expected>Returns "User" (fallback)</expected>
    </test>
    <test name="test_i18n_text_resolve_missing_raises_app_exception" category="error_path">
      <input>I18nText(translations={"de": "Benutzer"}), target_locale="fr", fallback_locale="en"</input>
      <expected>Raises AppException(VALIDATION_FAILED) with RFC 7807 logging</expected>
    </test>
    <test name="test_i18n_text_resolve_whitespace_raises_app_exception" category="error_path">
      <input>I18nText(translations={"fi": "   ", "en": ""}), target_locale="fi"</input>
      <expected>Raises AppException(VALIDATION_FAILED) (no silent empty string bypass)</expected>
    </test>
    <test name="test_i18n_text_missing_translations_raises_validation_error" category="error_path">
      <input>I18nText() (instantiation without translations)</input>
      <expected>Raises Pydantic ValidationError (no default factory bypass)</expected>
    </test>
    <test name="test_i18n_text_sanitizes_uppercase_keys" category="positive">
      <input>I18nText(translations={"EN": "User", "FI": "Käyttäjä"})</input>
      <expected>Validates successfully; canonical translations map is {"en": "User", "fi": "Käyttäjä"}</expected>
    </test>
    <test name="test_i18n_text_sanitizes_whitespace_padded_keys" category="positive">
      <input>I18nText(translations={"  en  ": "User", "  fi  ": "Käyttäjä"})</input>
      <expected>Validates successfully; canonical translations map is {"en": "User", "fi": "Käyttäjä"}</expected>
    </test>
    <test name="test_i18n_text_get_target_locale" category="positive">
      <input>I18nText(translations: {'fi': 'Käyttäjä', 'en': 'User'}), get('fi')</input>
      <expected>Returns 'Käyttäjä'</expected>
    </test>
    <test name="test_i18n_text_get_fallback_en" category="positive">
      <input>I18nText(translations: {'fi': 'Käyttäjä', 'en': 'User'}), get('sv')</input>
      <expected>Returns 'User' (fallback)</expected>
    </test>
    <test name="test_i18n_text_get_missing_throws_app_exception" category="error_path">
      <input>I18nText(translations: {'de': 'Benutzer'}), get('fr', fallback: 'en')</input>
      <expected>Throws AppException.validation with available keys list</expected>
    </test>
    <test name="test_i18n_text_get_whitespace_throws_app_exception" category="error_path">
      <input>I18nText(translations: {'fi': '   ', 'en': ''}), get('fi')</input>
      <expected>Throws AppException.validation (no silent empty string bypass)</expected>
    </test>
    <test name="test_i18n_text_is_empty_helpers" category="boundary">
      <input>I18nText(translations: {'en': '  '}), I18nText(translations: {'en': 'User'})</input>
      <expected>isEmpty == true, isNotEmpty == false, has('en') == false</expected>
    </test>
    <test name="test_i18n_text_from_json_legacy_default_locale_throws" category="error_path">
      <input>jsonDecode('{"default_locale": "en", "translations": {"en": "Text"}}')</input>
      <expected>Throws CheckedFromJsonException (disallowUnrecognizedKeys: true rejection)</expected>
    </test>
    <test name="test_i18n_text_from_json_missing_translations_throws" category="error_path">
      <input>jsonDecode('{}') or jsonDecode('{"translations": null}')</input>
      <expected>Throws CheckedFromJsonException (no @Default bypass)</expected>
    </test>
  </test_contracts>

  <step id="1" name="Python Domain Model Modernization in v2_core.py &amp; WarningCardAdapter Migration">
    <action>In @[backend_v2/models/v2_core.py#L101-L191]:
      1. Remove `default_locale` field from `I18nText`.
      2. Define `translations: Annotated[dict[str, str], Field(description="Dictionary mapping locale code to translated string, specifically: {'fi': 'Teksti', 'en': 'Text'}." )]` without `default_factory=dict`.
      3. Eradicate `@model_validator(mode="after")` and all `object.__setattr__` frozen mutations. Implement `@field_validator("translations")` classmethod to sanitize all locale keys (`strip().lower()`) and validate non-empty string values before verifying `'en'` Lingua Franca existence.
      4. Refactor `resolve()` method to enforce Fail-Fast validation using regex locale parsing and explicit dictionary membership assertions (`in`) instead of `.get()` duck-typing.
      5. Deprecate and remove legacy `I18nText.get(lang_code, fallback="")` in favor of direct delegation to `resolve()`.
    </action>
    <demolish>REMOVE: `default_locale` field and `@model_validator(mode="after")` in `I18nText` at @[backend_v2/models/v2_core.py#L101-L191].</demolish>
    <action>In @[backend_v2/services/sdui/adapters/warning_card_adapter.py]:
      Eliminate module-level `I18N_WARNING_STARVATION = I18nText(default_locale="en", ...)` to prevent import-time Pydantic `ValidationError` upon `default_locale` removal, resolving warning messages dynamically via `LocalizationService.translate('alert_starvation_insufficient_data', context.locale)`.
    </action>
    <demolish>REMOVE: module-level `I18N_WARNING_STARVATION` constant at @[backend_v2/services/sdui/adapters/warning_card_adapter.py]. REPLACE WITH: dynamic `LocalizationService` resolution.</demolish>
  </step>

  <step id="2" name="Flutter Freezed Model Update, 1-Hop Widget Cleanups &amp; Unit Tests">
    <action>In @[client_app_v2/lib/shared/models/i18n_text.dart]:
      - Annotate factory constructor explicitly with `@JsonSerializable(disallowUnrecognizedKeys: true)`.
      - Remove `@JsonKey(name: 'default_locale') @Default('en') String defaultLocale` from `I18nText` Freezed model.
      - Define `required Map<String, String> translations` without `@Default`.
      - Add SSOT state helpers (`isEmpty`, `isNotEmpty`, `has(langCode)`).
      - Update `get(String? langCode, {String fallback = 'en'})` method to throw `AppException.validation` on missing translation.
    </action>
    <demolish>REMOVE: `defaultLocale` and `@Default` on `translations` in @[client_app_v2/lib/shared/models/i18n_text.dart].</demolish>
    <action>Clean up 1-hop callers, Execution UI widgets, and Studio components:
      - In @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L187-L193] and @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L332-L333]: Replace ternary `locale == 'fi' ? m.labelI18n.get('fi') : m.labelI18n.get('en')` with `m.labelI18n.get(locale)`.
      - In @[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart#L52-L54]: Replace ternary `locale == 'fi' ? matrix.labelI18n.get('fi') : matrix.labelI18n.get('en')` with `matrix.labelI18n.get(locale)`.
      - In @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]: Migrate hardcoded Finnish UI text, buttons, labels, and SnackBar error messages to `AppLocalizations`.
      - In @[client_app_v2/lib/features/execution/views/execution_report_view.dart]: Migrate hardcoded tooltips and action labels to `AppLocalizations`.
      - In @[client_app_v2/lib/shared/widgets/specialist_section.dart]: Migrate `const Text("Tietoa Mittarista")` to `Text(l10n.aboutMetricTitle)`.
      - In @[client_app_v2/lib/l10n/app_en.arb] and @[client_app_v2/lib/l10n/app_fi.arb]: Add corresponding translation keys.
      - In @[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart]: Remove `defaultLocale` state tracking and bind text editing directly to `translations` map.
      - In @[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart#L239-L260]: Replace local `isEmptyI18n(text)` with `text?.isEmpty ?? true`.
      - In @[client_app_v2/lib/features/studio/views/profile_editor_view.dart]: Replace hardcoded `backgroundColor: const Color(0xFF2E7D32)` with `backgroundColor: Theme.of(context).colorScheme.primary`, and replace generic `throw Exception` with `throw AppException.validation(l10n.workflowIdMissingError);`.
      - In @[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart]: Purge manual `url.substring(0, 40)` clipping in favor of declarative `TextOverflow.ellipsis`.
    </action>
    <action>Create [NEW] @[client_app_v2/test/shared/models/i18n_text_test.dart] implementing test contracts TC-I18N-FLUTTER-01 through TC-I18N-FLUTTER-07.</action>
    <action>Run Flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/shared/models/i18n_text.dart --build`</action>
  </step>

  <step id="3" name="Deterministic Pruning of default_locale in seed_data.json &amp; 100% Bilingual Seeding">
    <action>Write and execute atomic Python script in scratch directory (`scratch/prune_default_locale_seed.py`) to strip all `"default_locale": "..."` keys from @[backend_v2/seed/seed_data.json] while preserving authentic translation payloads:
      1. Programmatically assert `len(translations) > 0` and `"en" in translations` for every record, failing fast if any record lacks a valid `"en"` entry.
      2. Populate authentic Finnish translations (`"fi"`) for `prompt_blocks[88].label` (`"Johdon valmennussynteesi"`), `prompt_blocks[88].description` (`"Johdon valmentajan synteesilohko"`), `prompt_blocks[89].label` (`"Analyyttinen graafisynteesi"`), and `prompt_blocks[89].description` (`"Analyyttisen graafin synteesilohko"`).
      3. Recursively delete `"default_locale"` keys and output formatted JSON matching CRLF line endings, verifying JSON integrity via `json.loads()` dry run.
    </action>
    <demolish>REMOVE: 500 instances of `"default_locale"` across @[backend_v2/seed/seed_data.json].</demolish>
  </step>

  <step id="4" name="Deterministic Bulk Migration of Test Fixtures via Scratch Scripts">
    <action>Execute deterministic Python scratch scripts for bulk test fixture migration:
      1. Run `scratch/migrate_backend_i18n_fixtures.py` across `backend_v2/tests/` to strip `default_locale` kwargs and dictionary keys across 1,166 occurrences in 90 test files, verifying syntax via `ast.parse` and formatting with `uv run ruff format backend_v2/tests/`.
      2. Run `scratch/migrate_flutter_i18n_fixtures.py` across `client_app_v2/test/` and `client_app_v2/lib/features/studio/` to strip `defaultLocale` kwargs and normalize empty instantiations, formatting with `dart format client_app_v2/test/`.
      3. Update specific test assertions in @[client_app_v2/test/models/matrix_claim_test.dart], @[client_app_v2/test/features/studio/models/workflow_test.dart], and @[client_app_v2/test/features/execution/models/matrix_scorecard_dto_test.dart].
    </action>
  </step>

  <step id="5" name="Re-seed Database &amp; Atomic Quality Gate Verification">
    <action>Re-seed local development database: `uv run python backend_v2/seed/run_seed.py local`</action>
  </step>

  <validation_gate>
    <assertion>Run backend quality loop: `uv run python scripts/backend_audit_loop.py backend_v2/tests/ --test`</assertion>
    <assertion>Run Flutter quality loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/ --build`</assertion>
  </validation_gate>
</execution_protocol>
```
