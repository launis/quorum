# Phase 6: Presentation Projection, Tabular Export, OpenAPI & Frontend UI Presentation Synchronization (WP1 & WP3)

**Overview:** Synchronize presentation projection, tabular export streaming (CSV and Excel), Jinja2 PDF templates, OpenAPI schema artifacts, and Studio UI controls with the multi-segment quote schema and decoupled lexical strictness controls. Note that Client Freezed DTO schemas are synchronized in Phase 2; Phase 6 focuses strictly on presentation widgets, adapters, and export compilation.

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L337-L355] Phase 6: Presentation Projection, Tabular Export, OpenAPI & Frontend UI Presentation Synchronization (WP1 & WP3)

**Target Files:**
- `[MODIFY]` @[backend_v2/services/export_service.py]
- `[MODIFY]` @[backend_v2/services/export_evidence_formatter.py]
- `[MODIFY]` @[backend_v2/scripts/generate_openapi.py]
- `[MODIFY]` @[docs/swagger/openapi.json]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]
- `[MODIFY]` @[backend_v2/templates/report_template.jinja2]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535]
- `[MODIFY]` @[backend_v2/tests/unit/test_report_headers_l10n_parity.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_pdf_generator.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 2 Freezed DTO models are compiled and Phase 4/5 backend services are operational.</action>
    <action>Look forward: Verify baseline state in export services, Jinja2 template, and Flutter UI widgets before synchronizing multi-segment citation presentation.</action>
    <constraint invariant="universal_fail_fast">If alignment is broken or files are missing, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/06_phase6_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/services/export_service.py]</backend>
    <backend>@[backend_v2/services/export_evidence_formatter.py]</backend>
    <backend>@[backend_v2/scripts/generate_openapi.py]</backend>
    <backend>@[docs/swagger/openapi.json]</backend>
    <backend>@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]</backend>
    <backend>@[backend_v2/templates/report_template.jinja2]</backend>
    <backend>@[backend_v2/tests/unit/test_report_headers_l10n_parity.py]</backend>
    <backend>@[backend_v2/tests/unit/test_pdf_generator.py]</backend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>Tabular export services in @[backend_v2/services/export_service.py] and @[backend_v2/services/export_evidence_formatter.py] updated to format multi-segment quotes with `" [...] ".join(source_quotes)`.</item>
    <item>SDUI XAI highlights in @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py] and printable sources in @[backend_v2/services/sdui/adapters/printable_sources_adapter.py] updated to render multi-segment citations.</item>
    <item>Jinja2 PDF report template @[backend_v2/templates/report_template.jinja2] updated at line 478 to `{{ quote.source_quotes | join(' [...] ') if quote.source_quotes else '' }}`, eliminating empty citation omissions in PDF generation.</item>
    <item>OpenAPI schema generator in @[backend_v2/scripts/generate_openapi.py] synchronized and @[docs/swagger/openapi.json] regenerated.</item>
    <item>Independent continuous slider for lexical verification strictness implemented in @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart] with localization in @[client_app_v2/lib/l10n/app_fi.arb] and @[client_app_v2/lib/l10n/app_en.arb].</item>
    <item>UI widgets in @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart] and @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535] updated to render `"${node.sourceQuotes?.join(' [...] ') ?? ''}"`.</item>
    <item>Tests in @[backend_v2/tests/unit/test_report_headers_l10n_parity.py] and @[backend_v2/tests/unit/test_pdf_generator.py] pass 100%.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_opaque_id_hydration.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_generation_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT perform client-side semantic inference or quote slicing in Flutter UI widgets; strictly adhere to Dumb Painter SDUI.</anti_target>
    <anti_target>Do NOT use raw Color, raw TextStyle, or hardcoded SizedBox in touched Flutter widgets.</anti_target>
    <anti_target>Do NOT omit joining delimiter `" [...] "` when serializing multi-segment citation tuples to tabular rows or presentation text.</anti_target>
  </anti_targets>

  <step id="1" name="SYNCHRONIZE TABULAR EXPORT STREAMING SERVICES">
    <action>In @[backend_v2/services/export_service.py]: Format multi-segment quotes as `" [...] ".join(source_quotes)` in `ExportForensicAtomDTO` generation.</action>
    <action>In @[backend_v2/services/export_evidence_formatter.py]: Ensure robust handling of multi-segment tuples using standardized delimiter `" [...] ".join(quotes)` across CSV and Excel exports.</action>
    <constraint invariant="the_zero_compromise_pledge">Preserve rectangular CSV export formatting and prevent column shifting.</constraint>
  </step>

  <step id="2" name="UPDATE SDUI HIGHLIGHTS &amp; PRINTABLE SOURCES ADAPTERS">
    <action>In @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]: Format multi-segment citations using delimiter `" [...] ".join(source_quotes)`.</action>
    <action>In @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]: Format multi-segment citations in printable sources, iterating over `eq.source_quotes`.</action>
    <constraint invariant="dumb_painter_sdui_architecture">Enforce Dumb Painter backend layout assembly for all presentation outputs.</constraint>
  </step>

  <step id="3" name="REMEDIATE JINJA2 PDF EVIDENCE EMISSION">
    <action>In @[backend_v2/templates/report_template.jinja2]: Update quote rendering at line 478 from scalar `{{ quote.quote }}` to multi-segment delimiter `{{ quote.source_quotes | join(' [...] ') if quote.source_quotes else '' }}`, eliminating silent empty quote omissions in PDF output.</action>
    <constraint invariant="universal_fail_fast">Generated PDF reports must contain non-empty citation text for verified atoms.</constraint>
  </step>

  <step id="4" name="REGENERATE OPENAPI SPECIFICATION ARTIFACT">
    <action>In @[backend_v2/scripts/generate_openapi.py]: Verify OpenAPI generator reflects `source_quotes: tuple[str, ...] | None` and `default_lexical_strictness_level`.</action>
    <action>In @[docs/swagger/openapi.json]: Regenerate OpenAPI specification artifact to maintain contract parity.</action>
    <constraint invariant="anti_semantic_drift_renaming">OpenAPI specification must accurately reflect Pydantic V2 schema serialization.</constraint>
  </step>

  <step id="5" name="IMPLEMENT STUDIO LEXICAL STRICTNESS SLIDER">
    <action>In @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]: Implement independent continuous slider for lexical verification strictness with range [0, 100], decoupled from scoring dampening.</action>
    <action>In @[client_app_v2/lib/l10n/app_fi.arb] and @[client_app_v2/lib/l10n/app_en.arb]: Add studio strictness localization keys and descriptive tooltips.</action>
    <constraint invariant="flutter_theme_sovereignty">Slider and labels must strictly utilize theme typography and tokens.</constraint>
  </step>

  <step id="6" name="UPDATE CLIENT CITATION &amp; CAUSAL INSPECTOR WIDGETS">
    <action>In @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]: Update quote rendering on line 563 to `"${q.sourceQuotes?.join(' [...] ') ?? ''}"`.</action>
    <action>In @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535]: Update lines 499-500 null check and line 530 scalar quote interpolation to `node.sourceQuotes?.join(' [...] ') ?? ''`.</action>
    <constraint invariant="flutter_theme_sovereignty">Preserve Flutter Theme Sovereignty and clean null-safe string interpolation.</constraint>
  </step>

  <step id="7" name="EXECUTE PRESENTATION &amp; CLIENT AUDIT GATES">
    <action>In @[backend_v2/tests/unit/test_report_headers_l10n_parity.py] and @[backend_v2/tests/unit/test_pdf_generator.py]: Verify report header localization parity and assert that rendered PDF contains verified multi-segment evidence citations.</action>
    <action>Execute Flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
    <constraint invariant="universal_quality_gate">All presentation and client tests must pass 100%.</constraint>
  </step>

  <test_contracts>
    <test name="test_export_service_multi_segment_quote_delimiter" category="positive">
      <input>ExportForensicAtomDTO with source_quotes=('Part 1', 'Part 2')</input>
      <expected>Tabular formatted quote: 'Part 1 [...] Part 2'</expected>
    </test>
    <test name="test_pdf_generator_renders_multi_segment_quotes" category="positive">
      <input>ReportDataDTO containing atoms with multi-segment quotes</input>
      <expected>Rendered PDF HTML contains 'Part 1 [...] Part 2' without attribute error</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute report header localization parity tests: `uv run pytest backend_v2/tests/unit/test_report_headers_l10n_parity.py`.</action>
    <action>Execute PDF generator unit tests: `uv run pytest backend_v2/tests/unit/test_pdf_generator.py`.</action>
    <action>Execute Flutter client audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
  </validation_gate>
</execution_protocol>
```
