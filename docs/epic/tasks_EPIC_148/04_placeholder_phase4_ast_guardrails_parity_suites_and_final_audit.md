# Phase 4: AST Guardrails, Parity Suites & Final Audit

**Phase Title:** Phase 4: AST Guardrails, Parity Suites & Final Audit
**Objective:** Implement comprehensive AST guardrails and presentation parity test suites locking theory grounding, seed vault purity, backend L10n internal 1:1 language parity, Jinja template field attribute validity, unrecognized block type fail-fast handling, and cross-platform SDUI Golden Master semantic rendering parity between PDF Jinja2 DOM and Flutter desktop widgets across specifically all 17 `AnySduiBlock` types.

**Source Reference:** @[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md#L527-L561] (Phase 4: AST Guardrails, Parity Suites & Final Audit)

**Expected Target Files:**
- `[NEW]` @[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py]
- `[NEW]` @[backend_v2/tests/unit/test_seed_architectural_guardrails.py]
- `[NEW]` @[backend_v2/tests/unit/test_backend_l10n_internal_parity.py]
- `[NEW]` @[backend_v2/tests/fixtures/sdui_golden_master.json]
- `[NEW]` @[backend_v2/tests/unit/test_sdui_template_parity.py]
- `[NEW]` @[client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 3. Verify OutputProfile and SDUI adapters are modernized and quality gates pass.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/tests/unit/] and @[client_app_v2/test/features/execution/views/widgets/].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] AST guardrails implemented and passing in [NEW] @[backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py] (asserting 0 matrix blocks contain `EPISTEMIC ANCHOR:` and all 13 have non-null `theory_grounding`).
    - [x] AST guardrails implemented and passing in [NEW] @[backend_v2/tests/unit/test_seed_architectural_guardrails.py] (asserting 0 occurrences of `default_locale`, 100% bilingual parity across all 500 records, 0 legacy translation dictionaries in OutputProfile, and active `matrix_synthesis_groups`).
    - [x] Backend internal localization parity test implemented and passing in [NEW] @[backend_v2/tests/unit/test_backend_l10n_internal_parity.py] (asserting 1:1 key parity between `en.json` and `fi.json`, 100% of Jinja `l10n.*` references exist, and 0 dead unreferenced keys).
    - [x] Synthetic SDUI test dataset created in [NEW] @[backend_v2/tests/fixtures/sdui_golden_master.json] containing populated instances of specifically all 17 `AnySduiBlock` variants.
    - [x] Presentation parity test suite implemented and passing in [NEW] @[backend_v2/tests/unit/test_sdui_template_parity.py] (AST block exhaustiveness guardrail, Jinja AST field attribute validator, unrecognized block Fail-Fast assertion, `StrictUndefined` missing l10n key assertion, and BeautifulSoup semantic DOM test).
    - [x] Flutter SDUI golden master parity test implemented and passing in [NEW] @[client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart] (verifying 1:1 semantic text, citation, badge, and table parity against Jinja DOM output).
    - [x] Full backend global quality loop passes: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
    - [x] Full Flutter global quality loop passes: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`.
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
    <!-- [NEW] backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py -->
    <!-- [NEW] backend_v2/tests/unit/test_seed_architectural_guardrails.py -->
    <!-- [NEW] backend_v2/tests/unit/test_backend_l10n_internal_parity.py -->
    <!-- [NEW] backend_v2/tests/fixtures/sdui_golden_master.json -->
    <!-- [NEW] backend_v2/tests/unit/test_sdui_template_parity.py -->
    <!-- [NEW] client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart -->
  </touched_artifacts>

  <anti_targets>
    - Do NOT weaken strict Pydantic `extra="forbid"` or Freezed `disallowUnrecognizedKeys: true` in parity fixtures.
    - Do NOT allow default fallback wildcards (`_ =>`) in SDUI renderer pattern match.
    - Treat read-only context references as immutable:
      - @[backend_v2/models/v2_core.py#L194-L207] (`TheoryGrounding` schema SSOT)
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
      <expected>PdfReportService.generate_execution_html() invokes raise_unrecognized_sdui_block, logs RFC 7807 error and raises AppException(VALIDATION_FAILED)</expected>
    </test>
    <test name="test_pdf_generator_strict_undefined_missing_l10n_key_raises" category="error_path">
      <input>PdfReportService.generate_execution_html() with injected empty or incomplete _translations dictionary</input>
      <expected>Jinja2 UndefinedError is raised on missing translation key, caught by service, logged with RFC 7807 and raised as AppException(status_code=500, INTERNAL_SERVER_ERROR)</expected>
    </test>
    <test name="test_execution_views_use_app_localizations" category="positive">
      <input>human_override_dialog.dart, execution_report_view.dart, specialist_section.dart</input>
      <expected>All user-facing strings, buttons, tooltips, dialogs, and snackbars resolve strictly via AppLocalizations without raw hardcoded text</expected>
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

  <step id="1" name="[DEFERRED IN TIER 1] Detailed execution instructions will be generated upon Phase 2 completion">
    <action>Invoke `/tier1-planner @[docs/epic/EPIC_148_Domain_Model_SSOT_and_Localization_Modernization.md]` after Phase 2 is verified to generate detailed XML execution steps for Phase 3 and Phase 4.</action>
  </step>

  <validation_gate>
    <assertion>Run backend quality loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</assertion>
    <assertion>Run Flutter quality loop: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`</assertion>
  </validation_gate>
</execution_protocol>
```
