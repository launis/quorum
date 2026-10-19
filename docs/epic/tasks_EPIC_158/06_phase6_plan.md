# Phase 6: Presentation Projection, Tabular Export, OpenAPI & Frontend UI Presentation Synchronization (WP1 & WP3)

**Overview:** Synchronize presentation projection, tabular export streaming (CSV and Excel), Jinja2 PDF templates, OpenAPI schema artifacts, and Studio UI controls with the multi-segment quote schema and decoupled lexical strictness controls. Note that Client Freezed DTO schemas are synchronized in Phase 2; Phase 6 focuses strictly on presentation widgets, adapters, and export compilation.

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L337-L355] Phase 6: Presentation Projection, Tabular Export, OpenAPI & Frontend UI Presentation Synchronization (WP1 & WP3)

**Target Files:**
- `[MODIFY]` @[backend_v2/services/export_service.py#L62-L1123]
- `[MODIFY]` @[backend_v2/services/export_evidence_formatter.py#L46-L77]
- `[MODIFY]` @[backend_v2/scripts/generate_openapi.py#L33-L74]
- `[MODIFY]` @[docs/swagger/openapi.json]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py#L54-L188]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L99-L341]
- `[MODIFY]` @[backend_v2/templates/report_template.jinja2]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535]
- `[MODIFY]` @[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L82-L147]
- `[MODIFY]` @[backend_v2/tests/unit/test_pdf_generator.py#L231-L317]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_export_evidence_formatter.py#L69-L78]

## Five-Column Architectural Directives

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Export Service Tabular Rows**<br>`@[backend_v2/services/export_service.py#L62-L1123]` | Converting multi-segment tuples to scalar strings by dropping subsequent items or formatting with unpredictable raw newlines; emitting unstandardized quote strings in CSV rows causing column shifting. | Format multi-segment quotes as `" [...] ".join(source_quotes)` in both `_build_atom_rows` and `_build_denormalized_rows` when constructing `ExportForensicAtomDTO` and tabular data payloads. | Reject building custom delimiter parsing engines or per-file formatting flags; rely strictly on standardized `" [...] "` delimiter. | Unit test verifying multi-segment quotes formatted with `" [...] "` in Excel and CSV atom rows. |
| **Tabular Export Evidence Formatter**<br>`@[backend_v2/services/export_evidence_formatter.py#L46-L77]` | Hardcoding numbered multiline citations `[1] Quote 1\n[2] Quote 2` in tabular Excel/CSV cells causing line breaks and cell deformation; failing to handle empty or None quote tuples cleanly. | Format multi-quote collections using standardized delimiter `" [...] ".join(cleaned_items)` in `format_text_observations`, preserving rectangular tabular cell geometry. | Avoid complex multiline cell wrapping or synthetic footnote indices for tabular exports. | Unit test in `test_export_evidence_formatter.py` asserting clean `" [...] "` joined string output. |
| **OpenAPI Schema Generator**<br>`@[backend_v2/scripts/generate_openapi.py#L33-L74]` | Manual schema synchronization; committing stale OpenAPI specifications; ignoring new DTO fields specifically: `default_lexical_strictness_level` and `source_quotes`. | Programmatic regeneration of `docs/swagger/openapi.json` from FastAPI app via `generate_openapi_schema`, reflecting Pydantic V2 schema parity. | Reject manual swagger patching or shadow JSON editing. | Script execution producing valid JSON matching `docs/swagger/openapi.json`. |
| **OpenAPI Schema Artifact**<br>`@[docs/swagger/openapi.json]` | Stale API specification desynchronized from backend models; missing `source_quotes` and `default_lexical_strictness_level` contracts. | Full-duplex synchronization of OpenAPI specification artifact with authoritative Pydantic V2 models. | Avoid bifurcated or version-branched API specifications. | Verification that `docs/swagger/openapi.json` contains `default_lexical_strictness_level` and `source_quotes`. |
| **SDUI XAI Highlights Adapter**<br>`@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py#L54-L188]` | Omission of multi-segment quote display or scalar fallback; dropping secondary source quote segments in XAI insight badges. | Format multi-segment evidence quotes using standardized `" [...] ".join(source_quotes)` delimiter when projecting forensic atoms to SDUI blocks. | Reject client-side quote concatenation; enforce Dumb Painter layout assembly. | Unit test asserting multi-segment citation string in projected SDUI block payload. |
| **SDUI Printable Sources Adapter**<br>`@[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L99-L341]` | Truncating multi-segment evidence quotes to `matched_quotes[0]`; fragmenting contiguous multi-segment citations into disconnected snippets. | Iterate over `eq.source_quotes` or join with `" [...] "` in printable source citations, rendering full multi-segment provenance context. | Avoid synthetic footnote numbering or nested source cards in printable layout. | Unit test verifying full multi-segment text present in printable sources SDUI blocks. |
| **Jinja2 PDF Report Template**<br>`@[backend_v2/templates/report_template.jinja2]` | Silent omission of evidence quotes when scalar `quote.quote` is empty; broken quote rendering in PDF exports. | Update line 478 to `{{ quote.source_quotes \| join(' [...] ') if quote.source_quotes else '' }}`, guaranteeing non-empty multi-segment citation rendering. | Avoid complex Jinja2 macros or custom Python filters for simple quote joining. | Unit test in `test_pdf_generator.py` asserting multi-segment quote present in generated HTML/PDF. |
| **Studio Workflow Strictness Tab**<br>`@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]` | Coupling lexical verification strictness to scoring dampening; missing slider controls for `defaultLexicalStrictnessLevel`; violating Flutter Theme Sovereignty with raw colors. | Independent continuous slider for lexical verification strictness [0, 100], discrete preset chips (Flexible, Calibrated, Strict, Absolute), dynamic semantic consequence card, and 100% Theme Sovereignty. | Avoid complex interactive graph previews inside the strictness configuration tab. | Flutter audit loop (`flutter_audit_loop.py client_app_v2/ --build`) passing 100%. |
| **Bilingual Localization Bundles**<br>`@[client_app_v2/lib/l10n/app_fi.arb]`<br>`@[client_app_v2/lib/l10n/app_en.arb]` | Hardcoded English/Finnish strings in UI widgets; missing 1:1 cross-language key parity; missing descriptive metadata tooltips. | 1:1 bilingual ARB entries for all lexical strictness controls, presets, consequence descriptions, semantic labels, and citation modal headers. | Avoid unannotated localization entries or redundant dialect variants. | Parity test in `test_report_headers_l10n_parity.py` asserting 1:1 cross-platform key resolution. |
| **SDUI Matrix Table Widget**<br>`@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]` | Raw `TextStyle(...)` instantiation at line 566 violating theme sovereignty; scalar quote rendering ignoring `sourceQuotes` array. | Refactor line 566 to `Theme.of(context).textTheme.bodySmall?.copyWith(...)` and update quote interpolation at line 563 to `"${q.sourceQuotes?.join(' [...] ') ?? ''}"`. | Avoid client-side regex parsing or string manipulation on quote text. | Flutter analyze and widget test pass via `flutter_audit_loop.py`. |
| **Causal Inspector Modal**<br>`@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535]` | Scalar quote checks `node.quote != null` dropping multi-segment quotes; rendering only scalar quote text in causal evidence cards. | Update lines 499-500 null check and line 530 text rendering to `(node.sourceQuotes != null && node.sourceQuotes!.isNotEmpty)` and `node.sourceQuotes!.join(' [...] ')`. | Avoid client-side node mutation or multi-tab citation navigation inside inspector. | Flutter build and widget tests pass without regressions. |
| **Report Headers & L10n Parity Test Suite**<br>`@[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L82-L147]` | Desynchronized metadata mappings between backend and frontend ARB files; omission of `metaLexicalStrictness` in cross-platform parity tests. | Add `("metaLexicalStrictness", "metadata_lexical_strictness")` to `metadata_mappings` in `test_cross_platform_studio_ui_arb_parity`. | Avoid ad-hoc fixture parsing; rely on centralized `ReportHeaderResolver`. | `uv run pytest backend_v2/tests/unit/test_report_headers_l10n_parity.py` passing 100%. |
| **PDF Generator Test Suite**<br>`@[backend_v2/tests/unit/test_pdf_generator.py#L231-L317]` | Incomplete PDF rendering tests verifying only scalar quotes; omitting multi-segment citation emission assertions. | Add `test_pdf_generator_renders_multi_segment_quotes` verifying that multi-segment quotes joined with `" [...] "` are present in rendered HTML/PDF. | Avoid live PDF rendering to disk or binary rasterization during unit tests. | `uv run pytest backend_v2/tests/unit/test_pdf_generator.py` passing 100%. |
| **Export Evidence Formatter Test Suite**<br>`@[backend_v2/tests/unit/services/test_export_evidence_formatter.py#L69-L78]` | Stale assertions expecting multiline numbered quotes `[1] Quote 1\n[2] Quote 2`; failing when standardized `" [...] "` delimiter is applied. | Update `test_format_text_observations_multi_quote_list` to assert `"Quote 1 [...] Quote 2"` matching tabular export standard. | Avoid testing irrelevant tabular styling details. | `uv run pytest backend_v2/tests/unit/services/test_export_evidence_formatter.py` passing 100%. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUPS">
    <action>Look backward: Verify Phase 2 Freezed DTO models are compiled and Phase 4/5 backend services are operational.</action>
    <action>Look forward: Verify baseline state in export services, Jinja2 template, and Flutter UI widgets before synchronizing multi-segment citation presentation.</action>
    <action>Eradicate Theme Sovereignty Debt in @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]: Refactor line 566 raw `TextStyle(...)` instantiation to `Theme.of(context).textTheme.bodySmall?.copyWith(...)`.</action>
    <action>Eradicate Truncation Debt in @[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L99-L341]: Refactor single-segment quote slicing `matched_quotes[0]` to format cohesive multi-segment quotes using `" [...] ".join(eq.source_quotes)` when `eq.source_quotes` is present.</action>
    <action>Eradicate Delimiter Debt in @[backend_v2/services/export_evidence_formatter.py#L46-L77]: Refactor numbered multiline citations `[1] ...\n[2] ...` with raw newlines to standardized delimiter `" [...] ".join(cleaned_items)`.</action>
    <action>Eradicate Stale Test Assertions in @[backend_v2/tests/unit/services/test_export_evidence_formatter.py#L69-L78]: Update assertions expecting multiline numbered format to expect `" [...] "` joined strings.</action>
    <constraint invariant="universal_fail_fast">If alignment is broken or files are missing, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/06_phase6_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/services/export_service.py#L62-L1123]</backend>
    <backend>@[backend_v2/services/export_evidence_formatter.py#L46-L77]</backend>
    <backend>@[backend_v2/scripts/generate_openapi.py#L33-L74]</backend>
    <backend>@[docs/swagger/openapi.json]</backend>
    <backend>@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py#L54-L188]</backend>
    <backend>@[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L99-L341]</backend>
    <backend>@[backend_v2/templates/report_template.jinja2]</backend>
    <backend>@[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L82-L147]</backend>
    <backend>@[backend_v2/tests/unit/test_pdf_generator.py#L231-L317]</backend>
    <backend>@[backend_v2/tests/unit/services/test_export_evidence_formatter.py#L69-L78]</backend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>Tabular export services in @[backend_v2/services/export_service.py#L62-L1123] and @[backend_v2/services/export_evidence_formatter.py#L46-L77] updated to format multi-segment quotes with `" [...] ".join(source_quotes)`.</item>
    <item>SDUI XAI highlights in @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py#L54-L188] and printable sources in @[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L99-L341] updated to render multi-segment citations.</item>
    <item>Jinja2 PDF report template @[backend_v2/templates/report_template.jinja2] updated at line 478 to `{{ quote.source_quotes | join(' [...] ') if quote.source_quotes else '' }}`, eliminating empty citation omissions in PDF generation.</item>
    <item>OpenAPI schema generator in @[backend_v2/scripts/generate_openapi.py#L33-L74] synchronized and @[docs/swagger/openapi.json] regenerated.</item>
    <item>Independent continuous slider for lexical verification strictness implemented in @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart] with localization in @[client_app_v2/lib/l10n/app_fi.arb] and @[client_app_v2/lib/l10n/app_en.arb].</item>
    <item>UI widgets in @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart] and @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535] updated to render `"${node.sourceQuotes?.join(' [...] ') ?? ''}"`.</item>
    <item>Tests in @[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L82-L147], @[backend_v2/tests/unit/test_pdf_generator.py#L231-L317], and @[backend_v2/tests/unit/services/test_export_evidence_formatter.py#L69-L78] pass 100%.</item>
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
    <action>In @[backend_v2/services/export_service.py#L62-L1123]: Format multi-segment quotes as `" [...] ".join(source_quotes)` in `ExportForensicAtomDTO` generation across `_build_atom_rows` and `_build_denormalized_rows`.</action>
    <action>In @[backend_v2/services/export_evidence_formatter.py#L46-L77]: Ensure robust handling of multi-segment tuples using standardized delimiter `" [...] ".join(cleaned_items)` in `format_text_observations` across CSV and Excel exports.</action>
    <constraint invariant="the_zero_compromise_pledge">Preserve rectangular CSV export formatting and prevent column shifting.</constraint>
  </step>

  <step id="2" name="UPDATE SDUI HIGHLIGHTS &amp; PRINTABLE SOURCES ADAPTERS">
    <action>In @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py#L54-L188]: Format multi-segment citations using delimiter `" [...] ".join(source_quotes)` when projecting forensic atoms to SDUI blocks.</action>
    <action>In @[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L99-L341]: Format multi-segment citations in printable sources, iterating over `eq.source_quotes` or joining with `" [...] "` to render complete multi-segment provenance context.</action>
    <constraint invariant="dumb_painter_sdui_architecture">Enforce Dumb Painter backend layout assembly for all presentation outputs.</constraint>
  </step>

  <step id="3" name="REMEDIATE JINJA2 PDF EVIDENCE EMISSION">
    <action>In @[backend_v2/templates/report_template.jinja2]: Update quote rendering at line 478 from scalar `{{ quote.quote }}` to multi-segment delimiter `{{ quote.source_quotes | join(' [...] ') if quote.source_quotes else '' }}`, eliminating silent empty quote omissions in PDF output.</action>
    <constraint invariant="universal_fail_fast">Generated PDF reports must contain non-empty citation text for verified atoms.</constraint>
  </step>

  <step id="4" name="REGENERATE OPENAPI SPECIFICATION ARTIFACT">
    <action>In @[backend_v2/scripts/generate_openapi.py#L33-L74]: Verify OpenAPI generator reflects `source_quotes: tuple[str, ...] | None` and `default_lexical_strictness_level`.</action>
    <action>In @[docs/swagger/openapi.json]: Regenerate OpenAPI specification artifact to maintain contract parity.</action>
    <constraint invariant="anti_semantic_drift_renaming">OpenAPI specification must accurately reflect Pydantic V2 schema serialization.</constraint>
  </step>

  <step id="5" name="IMPLEMENT STUDIO LEXICAL STRICTNESS SLIDER">
    <action>In @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]: Implement independent continuous slider for lexical verification strictness with range [0, 100], discrete preset chips (Flexible, Calibrated, Strict, Absolute), and dynamic semantic consequence card, decoupled from scoring dampening.</action>
    <action>In @[client_app_v2/lib/l10n/app_fi.arb] and @[client_app_v2/lib/l10n/app_en.arb]: Add studio strictness localization keys, preset titles, and descriptive consequence strings with 1:1 cross-language parity.</action>
    <constraint invariant="flutter_theme_sovereignty">Slider and labels must strictly utilize theme typography and tokens.</constraint>
  </step>

  <step id="6" name="UPDATE CLIENT CITATION &amp; CAUSAL INSPECTOR WIDGETS">
    <action>In @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]: Update quote rendering on line 563 to `"${q.sourceQuotes?.join(' [...] ') ?? ''}"` and ensure theme-compliant typography.</action>
    <action>In @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535]: Update lines 499-500 null check and line 530 scalar quote interpolation to `node.sourceQuotes?.join(' [...] ') ?? ''`.</action>
    <constraint invariant="flutter_theme_sovereignty">Preserve Flutter Theme Sovereignty and clean null-safe string interpolation.</constraint>
  </step>

  <step id="7" name="EXECUTE PRESENTATION &amp; CLIENT AUDIT GATES">
    <action>In @[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L82-L147]: Verify report header localization parity and assert `metaLexicalStrictness` metadata parity between Backend JSON and Flutter ARB.</action>
    <action>In @[backend_v2/tests/unit/test_pdf_generator.py#L231-L317]: Assert that rendered PDF contains verified multi-segment evidence citations.</action>
    <action>In @[backend_v2/tests/unit/services/test_export_evidence_formatter.py#L69-L78]: Update and execute tests for formatted multi-segment citation observations.</action>
    <action>Execute Flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
    <constraint invariant="universal_quality_gate">All presentation and client tests must pass 100%.</constraint>
  </step>

  <test_contracts>
    <test name="test_export_service_multi_segment_quote_delimiter" category="positive">
      <input>ExportForensicAtomDTO with source_quotes=('Part 1', 'Part 2')</input>
      <expected>Tabular formatted quote: 'Part 1 [...] Part 2'</expected>
    </test>
    <test name="test_export_evidence_formatter_multi_segment_citations" category="positive">
      <input>Observation items with multi-segment quotes ('Quote 1', 'Quote 2')</input>
      <expected>Formatted observation string: 'Quote 1 [...] Quote 2'</expected>
    </test>
    <test name="test_export_evidence_formatter_empty_tuple_safeguard" category="boundary">
      <input>Observation items with empty source_quotes=()</input>
      <expected>Graceful fallback to empty or stripped string without crashing</expected>
    </test>
    <test name="test_pdf_generator_renders_multi_segment_quotes" category="positive">
      <input>ReportDataDTO containing atoms with multi-segment quotes</input>
      <expected>Rendered PDF HTML contains 'Part 1 [...] Part 2' without attribute error</expected>
    </test>
    <test name="test_report_headers_l10n_parity_lexical_strictness" category="positive">
      <input>Cross-platform metadata parity evaluation including metaLexicalStrictness</input>
      <expected>100% parity between Python backend metadata keys and Flutter ARB keys</expected>
    </test>
    <test name="test_sdui_printable_sources_multi_segment_provenance" category="positive">
      <input>PrintableSourcesAdapter rendering evidence quotes with source_quotes=('Clause A', 'Clause B')</input>
      <expected>Rendered source citation includes 'Clause A [...] Clause B'</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute report header localization parity tests: `uv run pytest backend_v2/tests/unit/test_report_headers_l10n_parity.py`.</action>
    <action>Execute PDF generator unit tests: `uv run pytest backend_v2/tests/unit/test_pdf_generator.py`.</action>
    <action>Execute export evidence formatter unit tests: `uv run pytest backend_v2/tests/unit/services/test_export_evidence_formatter.py`.</action>
    <action>Execute Flutter client audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
  </validation_gate>
</execution_protocol>
```
