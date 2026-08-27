# Phase 4: AST Guardrails, Parity Suites & Final Audit

**Phase Title:** Phase 4: AST Guardrails, Parity Suites & Final Audit
**Objective:** Implement comprehensive AST guardrails and presentation parity test suites locking theory grounding, seed vault purity, backend L10n internal 1:1 language parity, Jinja template field attribute validity, unrecognized block type fail-fast handling, and cross-platform SDUI Golden Master semantic rendering parity between PDF Jinja2 DOM and Flutter desktop widgets across specifically all 17 `AnySduiBlock` types.

**Source Reference:** @[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md#L527-L561] (Phase 4: AST Guardrails, Parity Suites & Final Audit)

**Expected Target Files:**
- `[MODIFY]` @[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_seed_architectural_guardrails.py]
- `[NEW]` @[backend_v2/tests/unit/test_backend_l10n_internal_parity.py]
- `[NEW]` @[backend_v2/tests/fixtures/sdui_golden_master.json]
- `[NEW]` @[backend_v2/tests/unit/test_sdui_template_parity.py]
- `[NEW]` @[client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT &amp; PRE-FLIGHT AUDIT">
    <action>Look backward: Read the actual codebase state left by Phase 3. Verify OutputProfile and SDUI adapters are modernized, all 2,148 backend tests and 224 Flutter tests pass.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/tests/unit/] and @[client_app_v2/test/features/execution/views/widgets/].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_148_tracker.md]), and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] AST guardrails extended and passing in @[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py] (asserting 0 matrix blocks contain `EPISTEMIC ANCHOR:` and all 13 have non-null `theory_grounding` with valid citation and source URL, and MatrixSensorPromptBuilder AST uses pure citation_reference without raw URL dumping).
    - [x] AST guardrails extended and passing in @[backend_v2/tests/unit/test_seed_architectural_guardrails.py] (asserting 0 occurrences of `default_locale` across entire seed vault, 100% bilingual parity across all 500 I18nText records, 0 legacy translation dictionaries in OutputProfile, and active `matrix_synthesis_groups`).
    - [x] Backend internal localization parity test implemented and passing in [NEW] @[backend_v2/tests/unit/test_backend_l10n_internal_parity.py] (asserting 1:1 key parity between `en.json` and `fi.json`, 100% of Jinja `l10n.*` references exist, and 0 dead unreferenced keys).
    - [x] Synthetic SDUI test dataset created in [NEW] @[backend_v2/tests/fixtures/sdui_golden_master.json] containing populated instances of specifically all 17 `AnySduiBlock` variants.
    - [x] Presentation parity test suite implemented and passing in [NEW] @[backend_v2/tests/unit/test_sdui_template_parity.py] (AST block exhaustiveness guardrail, Jinja AST field attribute validator, unrecognized block Fail-Fast assertion, `StrictUndefined` missing l10n key assertion, and BeautifulSoup semantic DOM test).
    - [x] Flutter SDUI golden master parity test implemented and passing in [NEW] @[client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart] (verifying 1:1 semantic text, citation, badge, and table parity against Jinja DOM output).
    - [x] Full backend global quality loop passes: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
    - [x] Full Flutter global quality loop passes: `uv run python scripts/flutter_audit_loop.py client_app_v2 --test`.
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
    <!-- [MODIFY] backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py -->
    <!-- [MODIFY] backend_v2/tests/unit/test_seed_architectural_guardrails.py -->
    <!-- [NEW] backend_v2/tests/unit/test_backend_l10n_internal_parity.py -->
    <!-- [NEW] backend_v2/tests/fixtures/sdui_golden_master.json -->
    <!-- [NEW] backend_v2/tests/unit/test_sdui_template_parity.py -->
    <!-- [NEW] client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart -->
  </touched_artifacts>

  <anti_targets>
    - Do NOT weaken strict Pydantic `extra="forbid"` or Freezed `disallowUnrecognizedKeys: true` in parity fixtures.
    - Do NOT allow default fallback wildcards (`_ =>`) in SDUI renderer pattern match.
    - Treat read-only context references as immutable:
      - @[backend_v2/models/v2_core.py#L101-L114] (`TheoryGrounding` schema SSOT)
      - @[backend_v2/settings.py] (Backend global configuration SSOT)
  </anti_targets>

  <test_contracts>
    <test name="test_backend_l10n_internal_parity" category="positive">
      <input>backend_v2/l10n/en.json vs backend_v2/l10n/fi.json vs report_template.jinja2</input>
      <expected>1:1 internal key parity between backend languages; 100% of Jinja l10n.* references exist; zero dead unreferenced keys</expected>
    </test>
    <test name="test_all_sdui_blocks_handled_in_jinja_and_dart" category="positive">
      <input>sdui.py, report_template.jinja2, sdui_blocks_renderer.dart</input>
      <expected>100% of AnySduiBlock union variants are handled in both Jinja macro branches and Dart switch pattern match</expected>
    </test>
    <test name="test_jinja_sdui_golden_master_rendering" category="positive">
      <input>sdui_golden_master.json</input>
      <expected>Generates HTML via PdfReportService, verifies all 17 blocks render headings, paragraphs, citations, badges, tables, 1 / 5 pagination, and na_not_evaluated_label with BeautifulSoup</expected>
    </test>
    <test name="test_flutter_sdui_golden_master_rendering" category="positive">
      <input>sdui_golden_master.json</input>
      <expected>Headless widget test verifies SduiBlocksRenderer renders all text nodes, citations, badges, tables with 1:1 semantic parity</expected>
    </test>
    <test name="test_jinja_ast_attribute_validity" category="positive">
      <input>report_template.jinja2 AST</input>
      <expected>100% of accessed block.* field attributes exist on corresponding Pydantic AnySduiBlock models</expected>
    </test>
    <test name="test_jinja_raises_app_exception_on_unrecognized_block_type" category="error_path">
      <input>ReportDataDTO with unsupported synthetic block_type="unsupported_quantum_widget"</input>
      <expected>PdfReportService.generate_execution_html() invokes raise_unrecognized_sdui_block, logs RFC 7807 error and raises AppException(CONFIGURATION_ERROR or VALIDATION_FAILED)</expected>
    </test>
    <test name="test_pdf_generator_strict_undefined_missing_l10n_key_raises" category="error_path">
      <input>PdfReportService.generate_execution_html() with injected empty or incomplete _translations dictionary</input>
      <expected>Jinja2 UndefinedError is raised on missing translation key, caught by service, logged with RFC 7807 and raised as AppException(status_code=500, INTERNAL_SERVER_ERROR)</expected>
    </test>
    <test name="test_seed_matrices_have_no_epistemic_anchor_in_ai_description" category="positive">
      <input>seed_data.json</input>
      <expected>0 occurrences of EPISTEMIC ANCHOR: across all 13 matrices</expected>
    </test>
    <test name="test_seed_has_no_default_locale" category="positive">
      <input>seed_data.json</input>
      <expected>0 occurrences of "default_locale" across entire seed vault</expected>
    </test>
    <test name="test_seed_i18n_has_100_percent_bilingual_parity" category="positive">
      <input>seed_data.json</input>
      <expected>100% of all 500 I18nText records in seed_data.json possess valid, non-empty "en" and "fi" translations</expected>
    </test>
    <test name="test_seed_output_profile_has_no_legacy_dictionaries" category="positive">
      <input>seed_data.json</input>
      <expected>0 occurrences of legacy translation dictionaries in OutputProfile</expected>
    </test>
  </test_contracts>

  <tri_axis_dialectical_audit>
    <prosecution>
      <challenge>AST guardrails and cross-platform golden master parity suites are complex to maintain and risk freezing cosmetic template changes with brittle DOM assertions.</challenge>
      <deletion_test>If 30% of tests were deleted, removing the Jinja AST attribute validator and BeautifulSoup DOM test would save maintenance overhead without breaking core serialization.</deletion_test>
    </prosecution>
    <defense>
      <counter_proof>Without AST guardrails, future agents will re-introduce legacy dictionary lookups, broken Jinja attribute accesses (`block.missing_attr`), or unhandled polymorphic block types in Flutter, crashing client rendering silently. The BeautifulSoup test verifies semantic presence (headings, tables, badges) rather than rigid pixel layout, preventing regressions without fragility.</counter_proof>
    </defense>
    <realist>
      <interrogation>Are the golden master fixtures testing authentic heterogeneous state payloads? Yes, `sdui_golden_master.json` defines populated instances of specifically all 17 `AnySduiBlock` types with realistic text, citations, and scores, testing both languages (`en`, `fi`).</interrogation>
      <blast_radius>Ensures zero surviving duct tape in Jinja2 templates (`StrictUndefined`) and Flutter switches (`no default wildcards`).</blast_radius>
    </realist>
    <verdict>APPROVED. Implement all 4 test suites and golden master fixtures to lock Epic 148 architectural contracts permanently.</verdict>
  </tri_axis_dialectical_audit>

  <step id="1" name="PRE-IMPLEMENTATION SWEEP &amp; AST GUARDRAILS (THEORY GROUNDING &amp; SEED VAULT)">
    <action>Audit and extend @[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py] to verify:
      1. `test_seed_matrices_have_no_epistemic_anchor_in_ai_description`: 0 matrix blocks contain `"EPISTEMIC ANCHOR:"`.
      2. `test_seed_matrices_have_valid_theory_grounding`: All 13 matrix blocks have non-null `theory_grounding` with valid `citation_reference` and `source_url`.
      3. `test_matrix_sensor_prompt_builder_ast_uses_pure_theory_citation`: AST verifies `model_dump_json` is not invoked on `theory_grounding`.
      4. `test_source_verification_hook_registered_and_safe`: AST verifies hook registration and 0 mock keys.
    </action>
    <action>Audit and extend @[backend_v2/tests/unit/test_seed_architectural_guardrails.py] to verify:
      1. `test_seed_has_no_default_locale`: 0 occurrences of `"default_locale"` across the entire `seed_data.json` file.
      2. `test_seed_i18n_has_100_percent_bilingual_parity`: 100% of all 500 `I18nText` records possess non-empty `"en"` and `"fi"` translations.
      3. `test_output_profiles_zero_legacy_dictionaries_and_valid_matrix_synthesis_groups`: 0 occurrences of `metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`, or `layouts` in `OutputProfile` records, and valid `matrix_synthesis_groups` with 16-hex Opaque IDs.
    </action>
    <assertion>`uv run pytest backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py backend_v2/tests/unit/test_seed_architectural_guardrails.py` passes cleanly.</assertion>
  </step>

  <step id="2" name="BACKEND INTERNAL LOCALIZATION PARITY SUITE">
    <action>Create [NEW] @[backend_v2/tests/unit/test_backend_l10n_internal_parity.py] enforcing:
      1. `test_backend_json_has_100_percent_internal_language_parity`: 1:1 key parity between `backend_v2/l10n/en.json` and `backend_v2/l10n/fi.json` (zero missing or asymmetric keys).
      2. `test_jinja_template_all_l10n_references_exist_in_backend_dictionaries`: Regular expression scanner parsing `backend_v2/templates/report_template.jinja2` for all `l10n.<key>` references and asserting 100% exist in both `en.json` and `fi.json`.
      3. `test_backend_json_has_no_dead_unreferenced_keys`: Scans all Python SDUI adapters (`backend_v2/services/sdui/adapters/*.py`), `backend_v2/services/pdf_generator.py`, and `backend_v2/templates/report_template.jinja2` to verify every key in `en.json` is actively referenced (zero orphaned dead keys).
    </action>
    <assertion>`uv run pytest backend_v2/tests/unit/test_backend_l10n_internal_parity.py` passes cleanly.</assertion>
  </step>

  <step id="3" name="SDUI GOLDEN MASTER TEST FIXTURE (ALL 17 ANYSDUIBLOCK TYPES)">
    <action>Create [NEW] @[backend_v2/tests/fixtures/sdui_golden_master.json] containing a comprehensive, fully populated `ReportDataDTO` instance with:
      - `execution_id`: "exec_0123456789abcdef"
      - `workflow_name`: "Comprehensive SDUI Golden Master"
      - `profile_name`: `{"translations": {"en": "Executive Assessment Profile", "fi": "Johdon arviointiprofiili"}}`
      - `organization_name`: "Quorum Cognitive Enterprise"
      - `printed_at`: "2026-08-27T12:00:00Z"
      - `inner_sdui_blocks`: Populated instances of specifically all 17 `AnySduiBlock` types:
        1. `HeroInsightBlock` (`block_type="hero_insight"`)
        2. `ParagraphBlock` (`block_type="paragraph"`)
        3. `BulletListBlock` (`block_type="bullet_list"`)
        4. `AlertBlock` (`block_type="alert_box"`)
        5. `AccordionBlock` (`block_type="accordion"`) with nested children
        6. `MarkdownBlock` (`block_type="markdown"`)
        7. `SduiQuoteCard` (`block_type="quote_card"`)
        8. `SduiWarningCard` (`block_type="warning_card"`)
        9. `SduiNACard` (`block_type="n_a_card"`)
        10. `SduiGridBlock` (`block_type="grid"`) with child blocks
        11. `SduiMetadataBlock` (`block_type="metadata"`)
        12. `SduiRadarChartBlock` (`block_type="3d_matrix"`) with scorecard rows
        13. `SduiScatterPlotBlock` (`block_type="2d_compare"`) with scorecard rows
        14. `SduiMatrixTableBlock` (`block_type="matrix_summary"`) with visible columns & scorecard rows
        15. `SduiMetrics1DBlock` (`block_type="1d_metrics"`) with scorecard rows
        16. `SduiScoreCardBlock` (`block_type="score_card"`)
        17. `SduiAuditTrailBlock` (`block_type="audit_trail"`)
    </action>
    <assertion>JSON fixture parses strictly against `ReportDataDTO.model_validate_json()` with 0 validation errors.</assertion>
  </step>

  <step id="4" name="SDUI TEMPLATE PRESENTATION PARITY &amp; FAIL-FAST SUITE (BACKEND)">
    <action>Create [NEW] @[backend_v2/tests/unit/test_sdui_template_parity.py] enforcing:
      1. `test_all_sdui_blocks_handled_in_jinja_and_dart`: Static AST analysis comparing `AnySduiBlock` union variants in `backend_v2/models/view/sdui.py`, `render_sdui_blocks` branches in `backend_v2/templates/report_template.jinja2`, and `switch (block)` cases in `client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart`, asserting 100% handling parity across all 17 blocks without wildcards.
      2. `test_jinja_ast_attribute_validity`: AST parser inspecting all `block.<attr>` accesses in `backend_v2/templates/report_template.jinja2` against the Pydantic fields of the corresponding `AnySduiBlock` class in `backend_v2/models/view/sdui.py`.
      3. `test_jinja_raises_app_exception_on_unrecognized_block_type`: Asserts that passing a synthetic unhandled block type with `block_type="unsupported_quantum_widget"` to `PdfReportService.generate_execution_html()` triggers `raise_unrecognized_sdui_block`, logs RFC 7807 error, and raises `AppException(status_code=500, CONFIGURATION_ERROR)`.
      4. `test_pdf_generator_strict_undefined_missing_l10n_key_raises`: Asserts that rendering a template with an incomplete localization dictionary triggers Jinja2 `UndefinedError` and halts with `AppException(status_code=500, INTERNAL_SERVER_ERROR)`.
      5. `test_jinja_sdui_golden_master_rendering`: Loads `backend_v2/tests/fixtures/sdui_golden_master.json`, renders HTML via `PdfReportService.generate_execution_html()` for both `en` and `fi`, and uses `BeautifulSoup` to assert that all 17 block types render their expected DOM tags, classes, citations `[1]`, badges, tables, and localized strings.
    </action>
    <assertion>`uv run pytest backend_v2/tests/unit/test_sdui_template_parity.py` passes cleanly.</assertion>
  </step>

  <step id="5" name="FLUTTER SDUI GOLDEN MASTER PARITY WIDGET TEST &amp; UNIVERSAL QUALITY GATE">
    <action>Create [NEW] @[client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart] enforcing:
      1. Loads `backend_v2/tests/fixtures/sdui_golden_master.json` fixture directly.
      2. Deserializes into `ReportDataDTO` / `List<SduiBlockDTO>`.
      3. Renders `SduiBlocksRenderer` within a localized `MaterialApp` widget test environment for both `Locale('en')` and `Locale('fi')`.
      4. Verifies 1:1 semantic text, citation chips, warning cards, quote cards, matrix tables, accordions, and badges exist in the rendered widget tree.
      5. Verifies that no unrecognized block exceptions occur.
    </action>
    <action>Execute full Universal Quality Gate:
      1. Backend Quality Loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
      2. Flutter Quality Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --test`
    </action>
    <assertion>All 2,150+ Python tests and 225+ Flutter tests pass with 0 errors and >90% coverage.</assertion>
  </step>

  <validation_gate>
    <assertion>Run backend quality loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</assertion>
    <assertion>Run Flutter quality loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`</assertion>
  </validation_gate>
</execution_protocol>
```

