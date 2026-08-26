# Phase 3: ATOMIC OutputProfile, SDUI Dumb Painter & Localization Parity

**Phase Title:** Phase 3: ATOMIC OutputProfile, SDUI Dumb Painter & Localization Parity
**Objective:** Modernize `OutputProfile` and Server-Driven UI (SDUI) localization by migrating static UI dictionaries (`metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`) out of the backend database into frontend `.arb` resource files and `backend_v2/l10n/*.json`, replace legacy `layouts` with `matrix_synthesis_groups`, eradicate `OutputLayoutBlock` class across Python and Flutter, refactor SDUI presentation adapters and Jinja2 PDF templates to act as pre-localized Dumb Painters, and lock `StrictUndefined` rendering parity.

**Source Reference:** @[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md#L328-L525] (Phase 3: ATOMIC OutputProfile, SDUI Dumb Painter & Localization Parity)

**Expected Target Files:**
- `[MODIFY]` @[backend_v2/l10n/en.json]
- `[MODIFY]` @[backend_v2/l10n/fi.json]
- `[MODIFY]` @[backend_v2/services/localization.py]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L1114-L1145]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L1148-L1269]
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_enum_parity.py]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/output_profile.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/models/output_profile_test.dart]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/metadata_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/variance_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/authenticity_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/executive_summary_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]
- `[MODIFY]` @[backend_v2/services/pdf_generator.py]
- `[MODIFY]` @[backend_v2/templates/report_template.jinja2]
- `[MODIFY]` @[backend_v2/worker.py#L591-L1359]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/views/widgets/profile/tabs/profile_layouts_tab_test.dart]
- `[MODIFY]` @[backend_v2/seed/seed_data.json#L9180-L9570]
- `[MODIFY]` @[backend_v2/tests/unit/test_localization.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker_synthesis.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_workflows.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 2. Verify I18nText is fully modernized and database is seeded cleanly.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/models/v2_core.py#L1114-L1145], @[backend_v2/models/v2_core.py#L1148-L1269], @[backend_v2/models/dtos/output_profile.py], @[client_app_v2/lib/features/studio/models/output_profile.dart], and @[backend_v2/seed/seed_data.json#L9180-L9570].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] Backend static translation tables in @[backend_v2/l10n/en.json] and @[backend_v2/l10n/fi.json] populated with all 17 metric mapping keys, user roles, matrix columns, extension labels, `na_not_evaluated_label`, `sources_and_bibliography_title`, `warning_label`, `source_label`, `sduiMetadataCosts`, `sduiMetadataTokens`, `col_quotes`, `report_title`, and formatting rules.
    - [x] `LocalizationService` in @[backend_v2/services/localization.py] extended with `format_date`, `format_decimal`, `format_score`, `format_percent`, and `format_cost` helpers.
    - [x] `OutputProfile` modernized: `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts` replaced with `matrix_synthesis_groups` in @[backend_v2/models/v2_core.py#L1148-L1269], @[backend_v2/models/dtos/output_profile.py], and @[client_app_v2/lib/features/studio/models/output_profile.dart]; `MatrixSynthesisGroup` Freezed factory constructor annotated with `@JsonSerializable(disallowUnrecognizedKeys: true)`; `OutputLayoutBlock` class and `__all__` export completely eradicated across Python and Flutter (`the_no_legacy_mandate`).
    - [x] `test_enum_parity.py` updated in @[backend_v2/tests/unit/test_enum_parity.py] to retire AST parity checks (`test_preset_view_parity`, `test_text_delivery_mode_parity`) for deleted `OutputLayoutBlock`.
    - [x] SDUI adapters in @[backend_v2/services/sdui/adapters/metadata_adapter.py], @[backend_v2/services/sdui/adapters/variance_adapter.py], @[backend_v2/services/sdui/adapters/authenticity_adapter.py], @[backend_v2/services/sdui/adapters/executive_summary_adapter.py], @[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py], @[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py], @[backend_v2/services/sdui/adapters/printable_sources_adapter.py], and @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py] refactored to consume `LocalizationService` and `matrix_synthesis_groups` as pre-localized SDUI blocks.
    - [x] `report_template.jinja2` and `PdfReportService` in @[backend_v2/templates/report_template.jinja2] and @[backend_v2/services/pdf_generator.py] sanitized: `undefined=jinja2.StrictUndefined` environment configuration locked; `_raise_unrecognized_sdui_block` registered on `self.env.globals["raise_unrecognized_sdui_block"]`; universal compact footer pagination `counter(page) " / " counter(pages);` (`1 / 5`) configured; legacy HTML fallback card purged; hardcoded Finnish string `N/A (Ei arvioitu)` replaced with `{{ l10n.na_not_evaluated_label }}`; hardcoded strings purged; lazy fallback ternaries `if l10n is defined else '...'` purged across all 11 instances in favor of direct `l10n.<key>` references backed by `StrictUndefined`.
    - [x] Background worker in @[backend_v2/worker.py#L591-L1359] and Flutter studio layouts tab in @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart] updated to iterate over `matrix_synthesis_groups`.
    - [x] `OutputProfile` records in @[backend_v2/seed/seed_data.json#L9180-L9570] migrated to `matrix_synthesis_groups` and legacy dictionaries removed.
    - [x] Test fixtures in `backend_v2/tests/` updated for modernized `OutputProfile` schema.
    - [x] Local test database re-seeded via `uv run python backend_v2/seed/run_seed.py local`.
    - [x] Quality gates pass: `uv run python scripts/backend_audit_loop.py backend_v2 --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.
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
    <backend>@[backend_v2/l10n/en.json]</backend>
    <backend>@[backend_v2/l10n/fi.json]</backend>
    <backend>@[backend_v2/services/localization.py]</backend>
    <backend>@[backend_v2/models/v2_core.py]</backend>
    <backend>@[backend_v2/models/dtos/output_profile.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/metadata_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/variance_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/authenticity_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]</backend>
    <backend>@[backend_v2/services/pdf_generator.py]</backend>
    <backend>@[backend_v2/templates/report_template.jinja2]</backend>
    <backend>@[backend_v2/worker.py]</backend>
    <backend>@[backend_v2/seed/seed_data.json]</backend>
    <frontend>@[client_app_v2/lib/features/studio/models/output_profile.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]</frontend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT keep `OutputLayoutBlock` as a legacy proxy model (`the_no_legacy_mandate`).
    - Do NOT use fallback ternaries (`if l10n is defined else ...`) in `report_template.jinja2`.
    - Do NOT modify `I18nText` model (already finalized in Phase 2).
    - Treat read-only context references as immutable:
      - @[backend_v2/models/v2_core.py#L194-L207] (`TheoryGrounding` schema SSOT)
      - @[backend_v2/settings.py] (Backend global configuration SSOT)
  </anti_targets>

  <test_contracts>
    <test name="test_metadata_adapter_emits_structured_keys" category="positive">
      <input>Context with user_name="Matti Meikäläinen"</input>
      <expected>SDUI payload contains {key: "user", value: "Matti Meikäläinen"} without hardcoded Finnish label</expected>
    </test>
    <test name="test_worker_iterates_matrix_synthesis_groups" category="positive">
      <input>Profile with 2 MatrixSynthesisGroup objects</input>
      <expected>Emits 2 discrete synthesis tasks targeted at group member matrices</expected>
    </test>
    <test name="test_matrix_graphs_adapter_instantiates_row_dtos_without_model_copy" category="positive">
      <input>Adapter input with text_delivery_mode="titles_only"</input>
      <expected>Produces valid MatrixScorecardRowDTO instances with inner_sdui_blocks=[] without calling model_copy(update=)</expected>
    </test>
    <test name="test_localization_service_translate_and_formatting" category="positive">
      <input>LocalizationService.translate("metadata_user", "fi"), format_cost(12.5, "fi")</input>
      <expected>Returns "Käyttäjä" and "12,50 $"; missing key raises AppException(VALIDATION_FAILED)</expected>
    </test>
    <test name="test_output_profile_legacy_layouts_throws" category="error_path">
      <input>OutputProfile JSON containing 'layouts': [...]</input>
      <expected>Throws CheckedFromJsonException</expected>
    </test>
    <test name="test_output_profile_legacy_metric_mappings_throws" category="error_path">
      <input>OutputProfile JSON containing 'metric_mappings': {...}</input>
      <expected>Throws CheckedFromJsonException</expected>
    </test>
    <test name="test_matrix_synthesis_group_legacy_preset_view_throws" category="error_path">
      <input>MatrixSynthesisGroup JSON containing 'preset_view': 'default'</input>
      <expected>Throws CheckedFromJsonException</expected>
    </test>
  </test_contracts>

  <step id="1" name="Pre-Implementation Technical Debt Cleanups & Static Translation Tables">
    <action>In @[backend_v2/models/core_base.py#L39]: Wrap description in `Field(description=...)` to ensure line length conforms to PEP 8 standard (<= 120 characters).</action>
    <action>In @[backend_v2/models/dtos/matrix_scorecard.py]: Add comprehensive module docstring and docstrings for union wrappers (`TDAPending`, `TDAEvaluated`, `TDADlq`).</action>
    <action>In @[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L124-L135]: Replace generic `throw Exception("Workflow ID is missing")` with `throw AppException.validation(l10n.workflowIdMissingError)` and replace hardcoded `backgroundColor: const Color(0xFF2E7D32)` with `backgroundColor: Theme.of(context).colorScheme.primary`.</action>
    <action>In @[backend_v2/l10n/en.json] and @[backend_v2/l10n/fi.json]: Populate complete backend static translation tables for:
      - 17 metric mapping keys: `metadata_user`, `metadata_organization`, `metadata_scoring_engine`, `metadata_strictness`, `variance_mechanical`, `variance_cognitive`, `variance_total`, `variance_fallback_explanation`, `alignment_verdict`, `alignment_aligned`, `alignment_misaligned`, `jargon_score`, `authenticity_level`, `level_high`, `level_medium`, `level_low`, `authenticity_fallback_explanation`.
      - 4 user role mapping keys: `role_passenger`, `role_navigator`, `role_driver`, `role_architect`.
      - 6 matrix column label keys: `col_label`, `col_distribution`, `col_row_explanation`, `col_quotes`, `col_normalized_score`, `col_score`.
      - 11 XAI extension label keys: `ext_variance_validation`, `ext_authenticity_evaluation`, `ext_citation`, `ext_justification`, `ext_falsification`, `ext_theory_link`, `ext_risk_flag`, `ext_coaching`, `ext_missing_context`, `ext_remediation_steps`, `ext_emotional_sentiment`, `ext_confidence`.
      - Template presentation keys: `na_not_evaluated_label`, `sources_and_bibliography_title`, `warning_label`, `source_label`, `sduiMetadataCosts`, `sduiMetadataTokens`, `report_title`.
    </action>
    <action>In @[backend_v2/services/localization.py]: Extend `LocalizationService` with formatting helpers:
      - `format_date(dt: datetime, locale: str) -> str`: fi: `26.08.2026 klo 06:44`, en: `2026-08-26 06:44`.
      - `format_decimal(value: float, locale: str, decimals: int = 2) -> str`: fi: `3,50`, en: `3.50`.
      - `format_score(value: float, locale: str) -> str`: fi: `3,50`, en: `3.50`.
      - `format_percent(ratio: float, locale: str) -> str`: fi: `85,2 %`, en: `85.2%`.
      - `format_cost(amount: float, locale: str) -> str`: fi: `0,04 $`, en: `$0.04` (Enforces USD formatting with localized decimal comma and postfix symbol).
    </action>
    <action>In @[backend_v2/tests/unit/test_localization.py]: Add comprehensive unit test coverage for translation lookups, missing key Fail-Fast `AppException(VALIDATION_FAILED)` behavior, and formatting helpers across locales (`fi`, `en`).</action>
  </step>

  <step id="2" name="Python Domain Model & DTO Modernization (v2_core.py & output_profile.py)">
    <action>In @[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md#L1-L20]: Reference canonical rules and KIs.</action>
    <action>In @[backend_v2/models/v2_core.py#L1114-L1145]: Declare `MatrixSynthesisGroup(V2CoreBase)` with fields `id: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9_\-]+$")`, `title: I18nText`, `target_blocks: list[str] = Field(min_length=1)`, and `synthesis_directive: str | None = Field(default=None)`.</action>
    <action>In @[backend_v2/models/v2_core.py#L1148-L1269]: Modernize `OutputProfile`:
      - Remove `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts`.
      - Add `matrix_synthesis_groups: list[MatrixSynthesisGroup] = Field(default_factory=list, description="Optional matrix synthesis groups for 2D/3D comparative graphs")`.
      - Add contextual Fail-Fast cross-field validator `@model_validator(mode="after") def validate_matrix_graphs_coherence(self) -> Self` asserting that IF `TargetBlockType.MATRIX_GRAPHS_BLOCK` is in `target_block_order`, THEN `len(matrix_synthesis_groups) >= 1`.</action>
    <action>In @[backend_v2/models/v2_core.py]: Remove `"OutputLayoutBlock"` from `__all__` export list.</action>
    <action>In @[backend_v2/models/dtos/output_profile.py]:
      - Remove `OutputLayoutBlock` import.
      - Remove `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts` across `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO`.
      - Add `matrix_synthesis_groups: Annotated[list[MatrixSynthesisGroup], Field(default_factory=list)]` across all DTO models.
    </action>
    <action>In @[backend_v2/tests/unit/test_enum_parity.py#L86-L98]: Retire AST parity assertions targeting deleted `OutputLayoutBlock` (`test_preset_view_parity` and `test_text_delivery_mode_parity`).</action>
    <demolish>REMOVE: `class OutputLayoutBlock(V2CoreBase)` in @[backend_v2/models/v2_core.py#L1114-L1145].</demolish>
    <demolish>REMOVE: `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, and `layouts` in `OutputProfile` at @[backend_v2/models/v2_core.py#L1148-L1269].</demolish>
  </step>

  <step id="3" name="Flutter Freezed Model Update (output_profile.dart) & Studio UI Cleanups">
    <action>In @[client_app_v2/lib/features/studio/models/output_profile.dart]:
      - Declare `MatrixSynthesisGroup` Freezed model with explicit `@JsonSerializable(disallowUnrecognizedKeys: true)` annotation:
        `required String id`, `required I18nText title`, `required List<String> targetBlocks`, `String? synthesisDirective`.
      - Update `OutputProfile` Freezed model: remove `metricMappings`, `matrixColumnLabels`, `userRoleMappings`, `extensionLabels`, and `layouts`; add `@Default([]) List<MatrixSynthesisGroup> matrixSynthesisGroups`.
    </action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]: Update tab rendering to bind cleanly to `payload.matrixSynthesisGroups`.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart] and `matrix_graph_item_editor.dart`: Update graph layout editor card and item editors to configure `MatrixSynthesisGroup` objects instead of `OutputLayoutBlock`.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart]: Update summary table configuration card to operate directly without relying on `payload.layouts`.</action>
    <action>In @[client_app_v2/test/features/studio/models/output_profile_test.dart]:
      - Replace `OutputLayoutBlock` JSON parsing tests with `MatrixSynthesisGroup` serialization tests.
      - Add negative ISTQB partition test cases asserting that passing legacy keys (`layouts`, `metric_mappings`, `user_role_mappings`, `extension_labels` to `OutputProfile.fromJson` or `preset_view`, `steps` to `MatrixSynthesisGroup.fromJson`) throws `CheckedFromJsonException`.
    </action>
    <action>In @[client_app_v2/test/features/studio/views/widgets/profile/tabs/profile_layouts_tab_test.dart]: Update widget tests to use modernized `OutputProfile` schema.</action>
    <action>Run Flutter code generation: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`.</action>
    <demolish>REMOVE: `OutputLayoutBlock` Freezed class in @[client_app_v2/lib/features/studio/models/output_profile.dart].</demolish>
    <demolish>REMOVE: `metricMappings`, `matrixColumnLabels`, `userRoleMappings`, `extensionLabels`, and `layouts` in `OutputProfile` at @[client_app_v2/lib/features/studio/models/output_profile.dart].</demolish>
  </step>

  <step id="4" name="SDUI Presentation Adapters, Worker & Jinja2 PDF Template (Dumb Painters)">
    <action>In @[backend_v2/services/sdui/adapters/metadata_adapter.py]: Produce pre-localized `metadata_lines` and `costs`/`tokens` strings using `LocalizationService.translate()`, `format_cost()`, and `format_date()`.</action>
    <action>In @[backend_v2/services/sdui/adapters/variance_adapter.py]: Decouple completely from `profile.metric_mappings` and `profile.extension_labels`; resolve titles, labels, and metrics via `LocalizationService.translate()`; eliminate `hasattr` duck-typing.</action>
    <action>In @[backend_v2/services/sdui/adapters/authenticity_adapter.py]: Decouple from `profile.metric_mappings` and `profile.extension_labels`; resolve labels via `LocalizationService.translate()`; eliminate `hasattr` duck-typing.</action>
    <action>In @[backend_v2/services/sdui/adapters/executive_summary_adapter.py]: Decouple from `profile.user_role_mappings`; resolve role labels dynamically via `LocalizationService.translate()`.</action>
    <action>In @[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]: Consume `profile.matrix_synthesis_groups` instead of legacy `layouts`; instantiate `MatrixScorecardRowDTO` instances directly without `model_copy(update=)`.</action>
    <action>In @[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]: Adapt to top-level `TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK`; resolve column headers via `LocalizationService.translate()`.</action>
    <action>In @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]: Purge local `PRINTABLE_SOURCES_RULES` dictionary; resolve header via `LocalizationService.translate("sources_and_bibliography_title", locale)`.</action>
    <action>In @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]: Resolve extension labels via `LocalizationService.translate(f"ext_{ext_type_str}", locale)`.</action>
    <action>In @[backend_v2/services/pdf_generator.py]:
      - Verify and lock `undefined=jinja2.StrictUndefined` environment configuration.
      - Register Fail-Fast helper `_raise_unrecognized_sdui_block(block_type)` on `self.env.globals["raise_unrecognized_sdui_block"]`.
      - In `generate_execution_html()`: Assert `report_dto.inner_sdui_blocks` is non-empty, raising `AppException(VALIDATION_FAILED)` if empty or missing.
    </action>
    <action>In @[backend_v2/templates/report_template.jinja2]:
      - Update `@page @bottom-center` footer pagination to universal compact format `content: counter(page) " / " counter(pages);`.
      - Purge hardcoded Finnish string `N/A (Ei arvioitu):` on L159 in favor of `{{ l10n.na_not_evaluated_label }}`.
      - Purge hardcoded strings: `Warning:` -> `{{ l10n.warning_label }}:`, `Meta Costs` / `Meta Tokens` -> `{{ l10n.sduiMetadataCosts }}` / `{{ l10n.sduiMetadataTokens }}`, `(Lähde: ...)` -> `({{ l10n.source_label }}: ...)`.
      - Purge all 11 lazy fallback ternaries `if l10n is defined else ...` in favor of direct `l10n.<key>` references backed by `StrictUndefined`.
      - Purge legacy HTML fallback card (`V2 ARCHITECTURE VIOLATION`) in favor of pre-flight Python Fail-Fast exception.
      - Add strict `{% else %}` branch in `render_sdui_blocks` macro that invokes `{{ raise_unrecognized_sdui_block(block.block_type if block.block_type is defined else 'UNDEFINED') }}`.
    </action>
    <action>In @[backend_v2/worker.py#L591-L1359]: Update `generate_profile_synthesis_and_pdf_task` to iterate over `active_profile_dto.matrix_synthesis_groups` for matrix synthesis generation.</action>
    <demolish>REMOVE: `PRINTABLE_SOURCES_RULES` translation dictionary in @[backend_v2/services/sdui/adapters/printable_sources_adapter.py].</demolish>
  </step>

  <step id="5" name="Seed Vault OutputProfile Migration, Test Fixture Updates & Universal Quality Gate Verification">
    <action>Backup seed vault: `New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_phase3_cleanup.json`.</action>
    <action>In @[backend_v2/seed/seed_data.json#L9180-L9570]:
      - Remove `user_role_mappings`, `metric_mappings`, `extension_labels`, and `layouts` from `output_profiles[0]`.
      - Add `matrix_synthesis_groups` containing 3 comparative group definitions (`group_0_2d_compare`, `group_1_2d_compare`, `group_2_2d_compare`).
    </action>
    <action>In `backend_v2/tests/`: Update all test fixtures that mock `OutputProfile` or instantiate `OutputLayoutBlock` (specifically and exhaustively: `test_blueprint.py`, `test_matrix_domain_parser.py`, `test_output_profile_service.py`, `test_matrix_summary_table_adapter.py`, `test_matrix_graphs_adapter.py`, `test_worker_synthesis.py`, `test_variance_adapter.py`, `test_worker.py`, `test_workflows.py`).</action>
    <action>Re-seed local development database: `uv run python backend_v2/seed/run_seed.py local`.</action>
    <action>Execute Universal Quality Gate for Backend: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
    <action>Execute Universal Quality Gate for Frontend: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.</action>
  </step>

  <validation_gate>
    <assertion>Run backend quality loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</assertion>
    <assertion>Run Flutter quality loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`</assertion>
  </validation_gate>
</execution_protocol>
```
