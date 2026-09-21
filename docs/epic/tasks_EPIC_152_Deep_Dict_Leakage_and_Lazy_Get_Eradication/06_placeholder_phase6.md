<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>

# Phase 6: SDUI Boundary & Presentation Pipeline Hardening

**Overview:** Hardening the Server-Driven UI (SDUI) presentation pipeline, presentation adapters, render services, and Flutter API client boundaries. Eliminates `UiSection` completely from the codebase (Complexity Slayer 30% Deletion), extracts presentation rules into strongly typed frozen DTOs (`PrintableSourcesRulesDTO`, `XaiAestheticsRulesDTO`, `PenaltiesRulesDTO`, `VarianceRulesDTO`), eradicates `model.model_dump()` type laundering across `sdui_mapper_service.py`, replaces anonymous tuples with `RenderExecutionResultDTO`, establishes `FlatExecutionRecordDTO`, tightens FastAPI router response schemas (`ReportView`, `GenericStatusResponseDTO`), enforces strictly typed Freezed client models with zero permissive `Map<String, dynamic>` returns, eradicates system-wide emojis across Jinja2/HTML templates and Flutter ARB telemetry strings in favor of native Flutter Material icons, resolves 14 SDUI test reflection instances in `test_blueprint.py`, and executes the Global `BaseDTO` and `BaseResponseDTO` Immutability Lockdown (`frozen=True`) Convergence Gate across all 40+ inheriting DTOs.
**Source:** @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] Phase 6: SDUI Boundary & Presentation Pipeline Hardening

## Five-Axis Architectural Directives Table

| Target Scope & Boundaries | Eradicated Duct-Tape | Approved Best Practice | Pruned Over-Engineering (30% Deletion Test) | Verification & Fail-Fast (Proof Anchor) |
|---|---|---|---|---|
| `backend_v2/models/view/sdui.py` | Legacy `UiSection` class with `data: Any`, `SectionType`, `ReportView.sections: list[UiSection]`, and `ReportView.metrics: dict[str, Any] \| None`. | Complete demolition of `UiSection` and `ReportView.sections`. Define strongly typed `ReportViewMetricsDTO` with explicit bounds (`global_score`, `strictness_level`, `total_word_count`). Flutter client consumes `ReportView.inner_sdui_blocks: list[AnySduiBlock]`. | Delete dead backward-compatibility section model and polymorphic `Any` data container. | `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` and unit tests in `test_sdui_mapper_service.py`. |
| `backend_v2/models/dtos/sdui_rules.py` & SDUI Adapters (`printable_sources_adapter.py`, `penalties_adapter.py`, `variance_adapter.py`) | Naked dictionary configuration rules: `PRINTABLE_SOURCES_RULES: dict[str, Any]`, `PENALTIES_RULES: dict[str, dict[str, Any]]`, and `VARIANCE_RULES: dict[str, dict[str, VisualIntent]]`. | Define frozen Pydantic V2 DTOs: `PrintableSourcesRulesDTO`, `XaiAestheticsRulesDTO`, `PenaltiesRulesDTO`, and `VarianceRulesDTO` in `sdui_rules.py`. Bind adapters strictly to these immutable schema contracts. | Prune manual string dictionary traversal and nested dictionary subscripting. | Unit tests in `test_blueprint.py` asserting exact SDUI block generation from typed rules. |
| `backend_v2/services/sdui_mapper_service.py` | `metrics: dict[str, Any] = {}`, `[trace.model_dump(mode="json") for trace in report.mcp_tool_audit]`, and `SduiNACard(...).model_dump(mode="json")` type laundering. | Directly instantiate typed `ReportViewMetricsDTO`. Append typed `SduiNACard` instances directly into `inner_sdui_blocks: list[AnySduiBlock]`. Pass typed `MCPAuditTrace` instances directly without dictionary conversion. | Delete intermediate dictionary laundering loops and `UiSection` envelope assembly. | Unit tests in `test_sdui_mapper_service.py` asserting typed DTO transit and zero naked dictionaries. |
| `backend_v2/services/execution/legacy_render_service.py`, `facade.py`, `flattener.py`, `export_service.py` | `get_sdui_view(...) -> dict[str, Any]:` returning `view.model_dump(mode="json")`, anonymous 3-tuple in `render_execution`, and `flatten_results -> dict[str, Any]`. | Return `ReportView` directly. Define `[NEW]` `RenderExecutionResultDTO` replacing the anonymous 3-tuple. Define `[NEW]` `FlatExecutionRecordDTO` in `flat_record.py` with `to_csv_dict()` method for `export_service.py`. | Delete redundant `.model_dump(mode="json")` serialization roundtrips in service layer. | Unit tests in `test_legacy_render_service.py` and `test_flattener.py`. |
| `backend_v2/api/routers/execution/executions.py` | `get_execution_sdui(...) -> Any:`, line 381 `if isinstance(content, (dict, list)): # noqa: QGR012`, and `-> dict[str, str]` in `override_atom` and `reject_evidence_quote`. | Annotate `get_execution_sdui(...) -> ReportView:`. Use pattern matching on `RenderExecutionResultDTO.content` (`JobAcceptedDTO`, `FlatExecutionRecordDTO`, `ReportDataDTO`, `bytes`, `str`) with zero QGR suppressions. Return strongly typed `GenericStatusResponseDTO`. | Eradicate transport duck-typing and raw dictionary literal responses. | Unit tests in `test_executions.py` asserting typed response models and status codes. |
| `client_app_v2/` API Clients & Models (`reports_client.dart`, `execution_client.dart`, `report_artifact_controller.dart`, `report_data_v2_dto.dart`) | `Future<Map<String, dynamic>>` API client returns, secondary isolate decoding, line 64 `(Epic 91 Phase 4)` comment, and line 1 `// ignore_for_file: invalid_annotation_target`. | Return strongly typed Freezed models `Future<ReportDataDto>` and `Future<GenericStatusResponseDto>`. Direct controller binding without duplicate isolate decoding. Standard `@JsonKey` annotations. | Delete permissive client map parsing and manual dictionary casting. | `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/core/api/reports_client.dart`. |
| `client_app_v2/` Presentation Hardening (`sdui_matrix_table_widget.dart`, `matrix_scorecard_dto.dart`) | Direct `axis.name` rendering bypassing `axis.labelI18n: I18nText`, hardcoded English fallback strings on missing `l10n`, line 16 `SizedBox.shrink()` on empty data, and unmemoized `atomsByLevel` getter reallocations. | Semantic Dual-Axis localization `axis.labelI18n.get(locale)`. Non-null `AppLocalizations.of(context)!` access. Layout widget `const SizedBox()`. Memoized level grouping map in `MatrixScorecardDto`. | Delete empty layout hiding, heap churn in render loops, and localization fallback strings. | `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart`. |
| Universal Emoji Eradication (`report_template.jinja2`, `dashboard_pdf.html`, `app_fi.arb`, `app_en.arb`, `xai_axis_telemetry_grid.dart`) | Hardcoded emojis (`💡`, `⚠️`, `💬`, `⚖️`, `🔍`, `🛠️`, `🎭`, `📚`) in PDF templates and 10 Flutter ARB telemetry title keys (`reportQuoteTitle`, `reportSemanticExplanationTitle`, `reportFrameworkReference`, etc.). | Eradicate emojis from Jinja2/HTML templates; use semantic CSS badge styling. Eradicate emojis from all 10 ARB localization strings. Bind telemetry headers in `xai_axis_telemetry_grid.dart` directly to native Flutter Material icons. | Eradicate cross-platform glyph rendering defects (tofu boxes) and emoji pollution across analytical payloads. | `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` and `backend_audit_loop.py`. |
| Unit Test Reflection Eradication (`test_blueprint.py`, `test_executions.py`) | 14x dynamic reflection calls `getattr(b, "block_type", "")`, `getattr(grid_block.items[0], "text", "")`, `getattr(axis, "block_id", None)`, `getattr(block, "axes", [])`. | Direct static dot-notation attribute access on typed SDUI block models (`SduiBlockBase`, `DataGridBlock`, `AnySduiBlock`). | Eradicate reflection helpers concealing schema typing defects in test fixtures. | `uv run pytest backend_v2/tests/unit/services/test_blueprint.py` with zero QGR001 violations. |
| Global Immutability Lockdown Convergence Gate (`backend_v2/models/dtos/base.py`) | `BaseDTO` and `BaseResponseDTO` with mutable defaults (`frozen` absent from `model_config`). | Update `BaseDTO.model_config` and `BaseResponseDTO.model_config` to add `frozen=True` and `extra="forbid"`, locking all 40+ inheriting DTO subclasses across Quorum as strictly immutable. | Eliminate mutable DTO state vectors across all pipeline phases. | `uv run python scripts/backend_audit_loop.py backend_v2 --test` verifying zero Strictness Shock regressions. |

**Target Files:**
- `[NEW]` @[backend_v2/models/dtos/sdui_rules.py]
- `[NEW]` @[backend_v2/models/dtos/render.py]
- `[NEW]` @[backend_v2/models/dtos/flat_record.py]
- `[NEW]` @[backend_v2/tests/unit/services/execution/test_legacy_render_service.py]
- `[MODIFY]` @[backend_v2/models/view/sdui.py#L142-L193]
- `[MODIFY]` @[backend_v2/models/dtos/base.py#L22-L45]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L93-L339]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/penalties_adapter.py#L60-L127]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/variance_adapter.py#L74-L339]
- `[MODIFY]` @[backend_v2/services/sdui_mapper_service.py#L46-L115]
- `[MODIFY]` @[backend_v2/services/execution/legacy_render_service.py#L142-L314]
- `[MODIFY]` @[backend_v2/services/execution/facade.py#L169-L195]
- `[MODIFY]` @[backend_v2/services/flattener.py#L21-L69]
- `[MODIFY]` @[backend_v2/services/export_service.py#L237-L260]
- `[MODIFY]` @[backend_v2/api/routers/execution/executions.py#L265-L518]
- `[PRE-RESOLVED]` @[backend_v2/services/document_extraction.py]
- `[MODIFY]` @[backend_v2/templates/report_template.jinja2#L131-L308]
- `[MODIFY]` @[backend_v2/templates/dashboard_pdf.html#L180-L198]
- `[MODIFY]` @[client_app_v2/lib/core/api/reports_client.dart#L62-L65]
- `[MODIFY]` @[client_app_v2/lib/core/api/execution_client.dart#L52-L75]
- `[MODIFY]` @[client_app_v2/lib/features/reports/controllers/report_artifact_controller.dart#L28-L32]
- `[MODIFY]` @[client_app_v2/lib/features/execution/controllers/report_controller.dart#L22-L60]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart#L1-L72]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart#L14-L593]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart#L181-L191]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart#L60-L248]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb#L803-L818]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb#L1127-L1170]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint.py#L382-L1636]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_sdui_mapper_service.py#L37-L97]
- `[MODIFY]` @[backend_v2/tests/unit/test_flattener.py#L17-L96]
- `[MODIFY]` @[backend_v2/tests/unit/api/routers/execution/test_executions.py#L78-L100]
- `[MODIFY]` @[client_app_v2/test/features/execution/controllers/report_controller_test.dart#L12-L38]
- `[MODIFY]` @[client_app_v2/test/features/execution/controllers/execution_controller_test.dart#L35-L55]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 5 hardened prompt compiler and DAG executor DTOs with 0 fatal AST violations and passing tests.</action>
    <action>Look forward: Verify that Phase 7 live E2E tests validate complete UI and backend SDUI rendering with zero dictionary leakage.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/06_placeholder_phase6.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>Legacy model UiSection and ReportView.sections are completely demolished from @[backend_v2/models/view/sdui.py].</item>
    <item>ReportViewMetricsDTO defined in @[backend_v2/models/view/sdui.py] with strict bounds and typed fields.</item>
    <item>SDUI presentation rules extracted into [NEW] @[backend_v2/models/dtos/sdui_rules.py] defining PrintableSourcesRulesDTO, PenaltiesRulesDTO, VarianceRulesDTO, and XaiAestheticsRulesDTO.</item>
    <item>Adapters in @[backend_v2/services/sdui/adapters/] operate strictly with frozen rule DTOs.</item>
    <item>SDUI mapper service @[backend_v2/services/sdui_mapper_service.py] operates with 0 .model_dump() type laundering and 0 UiSection instances.</item>
    <item>Legacy render service @[backend_v2/services/execution/legacy_render_service.py] and facade @[backend_v2/services/execution/facade.py] return strongly typed ReportView directly with 0 dictionary serialization roundtrips.</item>
    <item>Anonymous 3-tuple in render_execution replaced with strongly typed [NEW] RenderExecutionResultDTO in @[backend_v2/models/dtos/render.py].</item>
    <item>FlatFileService in @[backend_v2/services/flattener.py] returns strongly typed [NEW] FlatExecutionRecordDTO in @[backend_v2/models/dtos/flat_record.py].</item>
    <item>Router @[backend_v2/api/routers/execution/executions.py] defines response_model=ReportView on get_execution_sdui and eliminates line 381 # noqa: QGR012.</item>
    <item>Endpoints override_atom and reject_evidence_quote return strongly typed GenericStatusResponseDTO instead of raw dictionaries.</item>
    <item>Flutter client models in reports_client.dart and execution_client.dart return strongly typed Freezed DTOs (ReportDataDto, GenericStatusResponseDto) with 0 permissive Map&lt;String, dynamic&gt; returns.</item>
    <item>Flutter report_data_v2_dto.dart has // ignore_for_file: invalid_annotation_target removed.</item>
    <item>Flutter sdui_matrix_table_widget.dart enforces Dual-Axis localization axis.labelI18n.get(locale), non-null l10n, and replaces SizedBox.shrink() with const SizedBox().</item>
    <item>Flutter matrix_scorecard_dto.dart memoizes atomsByLevel getter to eliminate heap churn.</item>
    <item>Universal emoji eradication completed across report_template.jinja2, dashboard_pdf.html, and all 10 telemetry keys in app_fi.arb and app_en.arb.</item>
    <item>Flutter xai_axis_telemetry_grid.dart binds telemetry headers directly to native Flutter Material icons.</item>
    <item>All 14 dynamic reflection calls (getattr, hasattr) in test_blueprint.py eradicated in favor of direct dot-notation access.</item>
    <item>Unit test suite established in [NEW] @[backend_v2/tests/unit/services/execution/test_legacy_render_service.py].</item>
    <item>Global BaseDTO and BaseResponseDTO immutability lockdown (frozen=True, extra="forbid") verified in @[backend_v2/models/dtos/base.py] with 0 Strictness Shock regressions across all 40+ DTO subclasses.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
    <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do NOT alter raw Flutter widget styling or theme configurations.</forbidden>
    <forbidden>Do NOT re-introduce fallback dictionary parsing in SDUI adapters.</forbidden>
    <forbidden>Do NOT allow loose extra fields on DTOs; ConfigDict(strict=True, extra="forbid", frozen=True) is mandatory.</forbidden>
    <forbidden>Do NOT use anonymous multi-value state tuples; encapsulate return payloads in dedicated Pydantic V2 DTOs.</forbidden>
    <forbidden>Do NOT use SizedBox.shrink() to hide UI elements on empty data.</forbidden>
    <forbidden>Do NOT emit emojis or unicode escape sequences into SDUI adapters, Jinja2 templates, or localization files.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/models/view/sdui.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/sdui_rules.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/render.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/flat_record.py]</backend>
    <backend>@[backend_v2/models/dtos/base.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/penalties_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/variance_adapter.py]</backend>
    <backend>@[backend_v2/services/sdui_mapper_service.py]</backend>
    <backend>@[backend_v2/services/execution/legacy_render_service.py]</backend>
    <backend>@[backend_v2/services/execution/facade.py]</backend>
    <backend>@[backend_v2/services/flattener.py]</backend>
    <backend>@[backend_v2/services/export_service.py]</backend>
    <backend>@[backend_v2/api/routers/execution/executions.py]</backend>
    <templates>@[backend_v2/templates/report_template.jinja2]</templates>
    <templates>@[backend_v2/templates/dashboard_pdf.html]</templates>
    <frontend>@[client_app_v2/lib/core/api/reports_client.dart]</frontend>
    <frontend>@[client_app_v2/lib/core/api/execution_client.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/reports/controllers/report_artifact_controller.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/controllers/report_controller.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]</frontend>
    <localization>@[client_app_v2/lib/l10n/app_fi.arb]</localization>
    <localization>@[client_app_v2/lib/l10n/app_en.arb]</localization>
    <tests>@[backend_v2/tests/unit/services/test_blueprint.py]</tests>
    <tests>@[backend_v2/tests/unit/services/test_sdui_mapper_service.py]</tests>
    <tests>@[backend_v2/tests/unit/test_flattener.py]</tests>
    <tests>[NEW] @[backend_v2/tests/unit/services/execution/test_legacy_render_service.py]</tests>
    <tests>@[backend_v2/tests/unit/api/routers/execution/test_executions.py]</tests>
    <tests>@[client_app_v2/test/features/execution/controllers/report_controller_test.dart]</tests>
    <tests>@[client_app_v2/test/features/execution/controllers/execution_controller_test.dart]</tests>
  </touched_artifacts>

  <pre_implementation_technical_debt_cleanups>
    <cleanup id="DEBT-6.1">Demolish UiSection and SectionType in @[backend_v2/models/view/sdui.py], removing data: Any permissive field.</cleanup>
    <cleanup id="DEBT-6.2">Remove dead ReportView.sections array from @[backend_v2/models/view/sdui.py].</cleanup>
    <cleanup id="DEBT-6.3">Replace ReportView.metrics: dict[str, Any] | None with strongly typed ReportViewMetricsDTO in @[backend_v2/models/view/sdui.py].</cleanup>
    <cleanup id="DEBT-6.4">Eradicate metrics: dict[str, Any] = {} and all .model_dump(mode="json") type laundering in @[backend_v2/services/sdui_mapper_service.py].</cleanup>
    <cleanup id="DEBT-6.5">Replace get_sdui_view(...) -> dict[str, Any] in @[backend_v2/services/execution/legacy_render_service.py] and @[backend_v2/services/execution/facade.py] with typed -> ReportView.</cleanup>
    <cleanup id="DEBT-6.6">Replace anonymous 3-tuple in render_execution with strongly typed RenderExecutionResultDTO in [NEW] @[backend_v2/models/dtos/render.py].</cleanup>
    <cleanup id="DEBT-6.7">Replace flatten_results -> dict[str, Any] in @[backend_v2/services/flattener.py] with strongly typed FlatExecutionRecordDTO.</cleanup>
    <cleanup id="DEBT-6.8">Remove -> Any: and line 381 # noqa: QGR012 suppression in @[backend_v2/api/routers/execution/executions.py].</cleanup>
    <cleanup id="DEBT-6.9">Replace dict[str, str] return on override_atom and reject_evidence_quote with GenericStatusResponseDTO.</cleanup>
    <cleanup id="DEBT-6.10">Eradicate Future&lt;Map&lt;String, dynamic&gt;&gt; returns in @[client_app_v2/lib/core/api/reports_client.dart] and @[client_app_v2/lib/core/api/execution_client.dart].</cleanup>
    <cleanup id="DEBT-6.11">Remove (Epic 91 Phase 4) comment from @[client_app_v2/lib/core/api/execution_client.dart] and // ignore_for_file: invalid_annotation_target from @[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart].</cleanup>
    <cleanup id="DEBT-6.12">Eradicate line 16 SizedBox.shrink(), line 61 unlocalized axis.name, and lines 576-591 hardcoded English fallback strings in @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart].</cleanup>
    <cleanup id="DEBT-6.13">Eradicate 14 dynamic reflection calls (getattr, hasattr) in @[backend_v2/tests/unit/services/test_blueprint.py].</cleanup>
    <cleanup id="DEBT-6.14">Modernize @[client_app_v2/lib/features/execution/controllers/report_controller.dart] 1-hop caller polling loop to consume typed Future&lt;ReportDataDto&gt; or encapsulate polling in execution_client.</cleanup>
    <cleanup id="DEBT-6.15">Update @[backend_v2/tests/unit/api/routers/execution/test_executions.py] line 82 assertion from 'sections' in data to 'inner_sdui_blocks' in data and 'sections' not in data.</cleanup>
  </pre_implementation_technical_debt_cleanups>

  <step id="6.1" name="SDUI Model Modernization, UiSection Demolition &amp; Rules DTO Creation">
    <action>Demolish UiSection and SectionType in @[backend_v2/models/view/sdui.py].</action>
    <action>Remove sections: list[UiSection] from ReportView in @[backend_v2/models/view/sdui.py].</action>
    <action>Define [NEW] ReportViewMetricsDTO in @[backend_v2/models/view/sdui.py] with fields: global_score: float | None = None, strictness_level: float | None = None, total_word_count: int | None = None.</action>
    <action>Update ReportView.metrics to ReportViewMetricsDTO | None = None.</action>
    <action>Create [NEW] @[backend_v2/models/dtos/sdui_rules.py] defining PrintableSourcesRulesDTO, XaiAestheticsRulesDTO, PenaltiesRulesDTO, and VarianceRulesDTO with strict=True, extra="forbid", frozen=True.</action>
    <action>Refactor @[backend_v2/services/sdui/adapters/printable_sources_adapter.py] to type PRINTABLE_SOURCES_RULES as PrintableSourcesRulesDTO.</action>
    <action>Refactor @[backend_v2/services/sdui/adapters/penalties_adapter.py] to type PENALTIES_RULES as PenaltiesRulesDTO.</action>
    <action>Refactor @[backend_v2/services/sdui/adapters/variance_adapter.py] to type VARIANCE_RULES as VarianceRulesDTO.</action>
    <demolish>REMOVE: `UiSection` in @[backend_v2/models/view/sdui.py]. REPLACE WITH: typed SDUI block components.</demolish>
    <constraint invariant="the_zero_compromise_pledge">Enforce strict Pydantic V2 schemas with ConfigDict(strict=True, extra='forbid', frozen=True).</constraint>
  </step>

  <step id="6.2" name="SDUI Mapper Service Hardening &amp; Type Laundering Eradication">
    <action>Modify @[backend_v2/services/sdui_mapper_service.py] to delete sections: list[UiSection] = [] and all UiSection instantiations.</action>
    <action>Directly append typed SduiNACard instances into inner_sdui_blocks: list[AnySduiBlock] with zero .model_dump(mode="json") conversion.</action>
    <action>Initialize metrics as typed ReportViewMetricsDTO(global_score=report.global_score, strictness_level=report.strictness_level) instead of metrics: dict[str, Any] = {}.</action>
    <action>Eradicate [trace.model_dump(mode="json") for trace in report.mcp_tool_audit] type laundering; preserve typed MCPAuditTrace instances directly.</action>
    <action>Construct ReportView with view_id=execution_id, metrics=metrics, status_theme=status_theme, inner_sdui_blocks=report.inner_sdui_blocks.</action>
    <constraint invariant="service_layer_hydration_firewall">Zero dictionary conversions in service layer; operate 100% on typed models.</constraint>
  </step>

  <step id="6.3" name="Service Layer Render, Facade &amp; Flattener DTO Hardening">
    <action>Create [NEW] @[backend_v2/models/dtos/render.py] defining RenderExecutionResultDTO(content: bytes | str | FlatExecutionRecordDTO | ReportDataDTO | JobAcceptedDTO, media_type: str, filename: str | None = None) with ConfigDict(strict=True, extra="forbid", frozen=True).</action>
    <action>Create [NEW] @[backend_v2/models/dtos/flat_record.py] defining FlatExecutionRecordDTO(execution_id: str, workflow_id: str, status: str, global_score: float | None = None, has_warning: bool = False, matrix_metrics: dict[str, str | float | int | bool | None] = Field(default_factory=dict)) with ConfigDict(strict=True, extra="forbid", frozen=True) and to_csv_dict() helper.</action>
    <action>Modify @[backend_v2/services/execution/legacy_render_service.py]: change get_sdui_view to return ReportView directly without view.model_dump(mode="json").</action>
    <action>Modify @[backend_v2/services/execution/legacy_render_service.py]: change render_execution to return RenderExecutionResultDTO instead of anonymous 3-tuple.</action>
    <action>Modify @[backend_v2/services/execution/facade.py]: change get_sdui_view signature to async def get_sdui_view(self, initiator: TokenData, execution_id: str) -> ReportView:.</action>
    <action>Modify @[backend_v2/services/flattener.py]: update FlatFileService.flatten_results to return FlatExecutionRecordDTO.</action>
    <action>Modify @[backend_v2/services/export_service.py]: update export_execution_results_csv to consume flat_data.to_csv_dict().</action>
    <constraint invariant="ban_anonymous_state_tuples">Anonymous multi-value state tuples are strictly banned; encapsulate multi-field returns in dedicated DTOs.</constraint>
  </step>

  <step id="6.4" name="Router Ingress/Egress Type Hardening &amp; Status DTOs">
    <action>Create GenericStatusResponseDTO in @[backend_v2/models/dtos/base.py] (or dtos) with status: str = "ok", message: str.</action>
    <action>Modify @[backend_v2/api/routers/execution/executions.py]: update get_execution_sdui return annotation to -> ReportView:.</action>
    <action>Modify @[backend_v2/api/routers/execution/executions.py]: replace line 381 if isinstance(content, (dict, list)): # noqa: QGR012 with strict pattern matching on RenderExecutionResultDTO.content, removing QGR012 suppression.</action>
    <action>Modify @[backend_v2/api/routers/execution/executions.py]: update override_atom and reject_evidence_quote return annotations to -> GenericStatusResponseDTO: and return GenericStatusResponseDTO(message=...).</action>
    <constraint invariant="universal_fail_fast">Enforce Fail-Fast at router boundary with strict response models.</constraint>
  </step>

  <step id="6.5" name="Flutter Client API, Freezed Model Parity &amp; Presentation Hardening">
    <action>Create [NEW] @[client_app_v2/lib/core/models/generic_status_response_dto.dart] with @freezed annotation.</action>
    <action>Modify @[client_app_v2/lib/core/api/reports_client.dart]: update getReportSdui to Future&lt;ReportDataDto&gt; getReportSdui(String reportId) decoding via ReportDataDto.fromJson.</action>
    <action>Modify @[client_app_v2/lib/features/reports/controllers/report_artifact_controller.dart]: update reportSdui provider to consume client.getReportSdui(reportId) directly.</action>
    <action>Modify @[client_app_v2/lib/core/api/execution_client.dart]: update renderExecution to Future&lt;ReportDataDto&gt;, update overrideAtom to Future&lt;GenericStatusResponseDto&gt;, and remove (Epic 91 Phase 4) comment from line 64.</action>
    <action>Modify @[client_app_v2/lib/features/execution/controllers/report_controller.dart]: update polling loop to consume strongly typed Future&lt;ReportDataDto&gt; from execution_client without raw map parsing.</action>
    <action>Modify @[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]: remove // ignore_for_file: invalid_annotation_target.</action>
    <action>Modify @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]: replace line 16 SizedBox.shrink() with const SizedBox(), replace line 61 axis.name with axis.labelI18n.get(locale), and replace lines 576-591 hardcoded English fallbacks with non-null AppLocalizations.of(context)!.</action>
    <action>Modify @[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]: memoize atomsByLevel getter to eliminate heap churn during rebuilds.</action>
    <action>Run flutter audit loop build runner: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/core/api/reports_client.dart --build.</action>
    <constraint invariant="cross_language_enum_parity">Backend DTOs and Flutter Freezed models must maintain 1:1 serialization parity.</constraint>
  </step>

  <step id="6.6" name="Universal Emoji Eradication in Templates, ARB Strings &amp; Widgets">
    <action>Modify @[backend_v2/templates/report_template.jinja2]: eradicate emojis on lines 131, 134, and 303; replace with semantic CSS badge styling.</action>
    <action>Modify @[backend_v2/templates/dashboard_pdf.html]: eradicate emojis on lines 183 and 192.</action>
    <action>Modify @[client_app_v2/lib/l10n/app_fi.arb] lines 803-818: remove emojis from all 10 telemetry keys (reportQuoteTitle, reportSemanticExplanationTitle, reportFrameworkReference, reportCoachingTitle, reportFalsificationTitle, reportMissingContextTitle, reportRiskFlagTitle, reportRemediationStepsTitle, reportEmotionalSentimentTitle, reportTheoryLinkTitle).</action>
    <action>Modify @[client_app_v2/lib/l10n/app_en.arb] lines 1127-1170: remove emojis from all 10 telemetry keys.</action>
    <action>Modify @[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]: bind telemetry section headers directly to native Flutter Material icons (Icons.format_quote, Icons.lightbulb_outline, Icons.gavel, Icons.build, Icons.warning, Icons.search, Icons.psychology, Icons.menu_book).</action>
    <action>Regenerate Flutter localizations and run flutter audit loop: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart.</action>
    <constraint invariant="sdui_contract_fracture_prevention">Verify 1:1 semantic parity between Flutter UI and generated PDF.</constraint>
  </step>

  <step id="6.7" name="Unit Test Suite Migration &amp; Co-Located SDUI Reflection Eradication">
    <action>Modify @[backend_v2/tests/unit/services/test_blueprint.py]: eradicate all 14 getattr/hasattr dynamic reflection calls (lines 408, 995-1006, 1289-1296, 1631, 1633); assert directly via static dot-notation.</action>
    <action>Modify @[backend_v2/tests/unit/services/test_sdui_mapper_service.py]: update assertions to test ReportViewMetricsDTO and direct AnySduiBlock embedding with UiSection eradicated.</action>
    <action>Modify @[backend_v2/tests/unit/test_flattener.py]: update assertions to validate FlatExecutionRecordDTO and its to_csv_dict() method.</action>
    <action>Create [NEW] @[backend_v2/tests/unit/services/execution/test_legacy_render_service.py]: test ReportView direct return and RenderExecutionResultDTO format rendering.</action>
    <action>Modify @[backend_v2/tests/unit/api/routers/execution/test_executions.py]: update assertions for ReportView (asserting "inner_sdui_blocks" in data and "sections" not in data) and GenericStatusResponseDTO returns.</action>
    <action>Update Flutter tests: @[client_app_v2/test/features/execution/controllers/report_controller_test.dart] and @[client_app_v2/test/features/execution/controllers/execution_controller_test.dart].</action>
    <constraint invariant="tdd_mandate">Test suite must pass 100% with zero dynamic reflection and zero AST violations.</constraint>
  </step>

  <step id="6.8" name="Global BaseDTO &amp; BaseResponseDTO Immutability Lockdown Convergence Gate">
    <action>Modify @[backend_v2/models/dtos/base.py]: update BaseDTO.model_config to ConfigDict(populate_by_name=True, strict=True, extra="forbid", frozen=True).</action>
    <action>Modify @[backend_v2/models/dtos/base.py]: update BaseResponseDTO.model_config to ConfigDict(strict=True, extra="forbid", frozen=True).</action>
    <action>Execute full backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2 --test.</action>
    <action>Verify zero Strictness Shock regressions across all 40+ inheriting DTO models and test fixtures.</action>
    <constraint invariant="universal_ssot_and_normalization_mandate">DTOs must be strictly immutable across all pipeline boundaries.</constraint>
  </step>

  <validation_gate>
    <action>Run SDUI semantic parity integration test: uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py</action>
    <action>Run backend audit loop on SDUI models: uv run python scripts/backend_audit_loop.py backend_v2/models/view/sdui.py --test</action>
    <action>Run backend audit loop on render service: uv run python scripts/backend_audit_loop.py backend_v2/services/execution/legacy_render_service.py --test</action>
    <action>Run flutter audit loop on reports client: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/core/api/reports_client.dart</action>
    <action>Run full backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2 --test</action>
  </validation_gate>
</execution_protocol>
```
