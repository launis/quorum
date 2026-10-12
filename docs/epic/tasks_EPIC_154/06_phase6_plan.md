# Phase 6: Tabular Export & Rectangular Flat CSV Parity

**Overview:** Extend Quorum's tabular and flat export pipelines to achieve forensic symmetry between Excel Tab 2 ("Raw Data") and rectangular multi-row CSV streaming. Register explicit enum members `CAUSAL_STATUS`, `BLAME_PARENT_ID`, and `DEPENDENT_COUNT` in `ReportAtomColumn` within `backend_v2/models/enums.py`. Declare authoritative Finnish and English localization strings in `backend_v2/l10n/fi.json` and `en.json`. Extend `ReportHeaderResolver` in `backend_v2/services/localization.py` to resolve causal column headers and append them to denormalized CSV headers, expanding CSV column count from 17 to 20. Extend `ExportForensicAtomDTO` and `ExportDenormalizedFlatRowDTO` in `backend_v2/models/dtos/export.py` with typed atom-level causal fields. Update `ExportService` in `backend_v2/services/export_service.py` to enrich canonical "Raw Data" rows and stream rectangular multi-row atom CSV datasets in UTF-8-SIG preserving the Anti-Synthetic Row Invariant. Synchronously update 1-hop parity tests (`test_report_headers_l10n_parity.py`, `test_localization.py`, and `models/test_enums.py`) asserting 12 atom columns and 20 CSV headers to prevent regression cascades.

**Source:** @[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md] Section 3, Phase 6: Tabular Export & Rectangular Flat CSV Parity

**Target Files:**
- `[MODIFY] @[backend_v2/models/enums.py#L939-L958]`
- `[MODIFY] @[backend_v2/l10n/fi.json#L128-L146]`
- `[MODIFY] @[backend_v2/l10n/en.json#L128-L146]`
- `[MODIFY] @[backend_v2/services/localization.py#L382-L491]`
- `[MODIFY] @[backend_v2/models/dtos/export.py#L48-L76]`
- `[MODIFY] @[backend_v2/models/dtos/export.py#L99-L135]`
- `[MODIFY] @[backend_v2/services/export_service.py#L437-L574]`
- `[MODIFY] @[backend_v2/services/export_service.py#L576-L749]`
- `[MODIFY] @[backend_v2/services/export_service.py#L751-L912]`
- `[MODIFY] @[backend_v2/services/export_service.py#L914-L1034]`
- `[MODIFY] @[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L150-L163]`
- `[MODIFY] @[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L166-L189]`
- `[MODIFY] @[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L256-L387]`
- `[MODIFY] @[backend_v2/tests/unit/test_localization.py#L255-L276]`
- `[MODIFY] @[backend_v2/tests/unit/models/test_enums.py#L115-L144]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_export_service.py#L834-L865]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/enums.py#L939-L958]`, `@[backend_v2/l10n/fi.json#L128-L146]`, `@[backend_v2/l10n/en.json#L128-L146]`, `@[backend_v2/services/localization.py#L382-L491]` | Unlocalized column headers, missing ReportAtomColumn enums, loose dict mutation accumulators, hardcoded 9-column assertion cascade failures in 1-hop parity tests. | Register enum members on `ReportAtomColumn` (`CAUSAL_STATUS`, `BLAME_PARENT_ID`, `DEPENDENT_COUNT`) with localization keys in `fi.json` and `en.json` resolved via `ReportHeaderResolver`. Expand `get_all_denormalized_csv_headers()` from 17 to 20 columns. | Disjoint parallel Excel worksheets ("Causal Graph", "Causal Diagnostics"), pivot table generators, and dynamic CSV dialect negotiation. | Unit tests in `test_localization.py` and `models/test_enums.py` asserting 12 columns; `backend_audit_loop.py`. |
| `@[backend_v2/models/dtos/export.py#L48-L76]`, `@[backend_v2/models/dtos/export.py#L99-L135]`, `@[backend_v2/services/export_service.py#L437-L574]`, `@[backend_v2/services/export_service.py#L576-L749]`, `@[backend_v2/services/export_service.py#L751-L912]`, `@[backend_v2/services/export_service.py#L914-L1034]` | Legacy 2-line machine vector assumption, synthetic run-level summary rows injected into atom streams, unannotated dict mutation loops, writing "None" string literals into CSV/Excel cells. | Enrich `ExportForensicAtomDTO` and `ExportDenormalizedFlatRowDTO` with typed atom-level causal fields (`causal_status`, `blame_parent_id`, `dependent_count`). `ExportService.export_flat_csv` streams a multi-row rectangular atom dataset (`len(flat_dtos) == len(report_dto.results)`) in UTF-8-SIG adhering strictly to the Anti-Synthetic Row Invariant. | Secondary export formats (XML, Parquet) or asynchronous background CSV streaming queues. | Unit tests in `test_export_service.py` asserting exact row count equality and typed DTO returns. |
| `@[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L150-L163]`, `@[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L166-L189]`, `@[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L256-L387]`, `@[backend_v2/tests/unit/test_localization.py#L255-L276]`, `@[backend_v2/tests/unit/models/test_enums.py#L115-L144]`, `@[backend_v2/tests/unit/services/test_export_service.py#L834-L865]` | Skipping 1-hop caller test updates resulting in cascade test failures across the test suite. | Synchronously update `test_report_headers_l10n_parity.py` asserting `len(ReportAtomColumn) == 12`, `len(sheet2_rows[0]) == 12`, `len(reader[0]) == 20`, and `expected_atom_fields` containing causal attributes. | Commenting out or skipping broken tests with `@pytest.mark.skip`. | All four test suites pass 100% via `pytest`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 5. Verify `SduiCausalGraphBlock` is registered and passes template and semantic parity tests.</action>
    <action>Look forward: Verify if extending `ReportAtomColumn` and export DTOs preserves the 100% rectangular multi-row CSV streaming contract and passes 1-hop parity test suites.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]) and the Tracker document (@[docs/epic/EPIC_154_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_154/06_phase6_plan.md] @[docs/epic/EPIC_154_tracker.md]`.</directive>
  </step>

  <step id="1" name="PRE_IMPLEMENTATION_CLEANUPS">
    <action>In @[backend_v2/services/export_service.py#L914-L1034], update export_flat_csv docstring from streaming 17 denormalized columns to streaming 20 denormalized columns.</action>
    <action>In @[backend_v2/services/localization.py#L382-L491], update ReportHeaderResolver.get_all_denormalized_csv_headers docstring from Resolves all 17 denormalized CSV headers to Resolves all 20 denormalized CSV headers.</action>
    <action>In @[backend_v2/tests/unit/services/test_export_service.py#L834-L865], verify test fixture setup and baseline test execution before schema modifications.</action>
    <constraint invariant="zero_duct_tape">Audit and align all existing docstrings and baseline test invariants prior to schema extensions.</constraint>
  </step>

  <dod_checklist>
    <item>CAUSAL_STATUS, BLAME_PARENT_ID, and DEPENDENT_COUNT registered in ReportAtomColumn in backend_v2/models/enums.py (expanding count to 12).</item>
    <item>Authoritative translations added to backend_v2/l10n/fi.json and en.json for export_col_causal_status, export_col_blame_parent_id, export_col_dependent_count.</item>
    <item>ReportHeaderResolver in backend_v2/services/localization.py updated to resolve causal headers and append them to get_all_denormalized_csv_headers() (expanding CSV header count from 17 to 20).</item>
    <item>ExportForensicAtomDTO and ExportDenormalizedFlatRowDTO in backend_v2/models/dtos/export.py extended with typed causal fields: causal_status, blame_parent_id, dependent_count.</item>
    <item>ExportService canonical Raw Data worksheet (Tab 2) enriched with causal columns during fusion runs.</item>
    <item>ExportService.export_flat_csv streams rectangular multi-row atom datasets matching Excel Tab 2 row count in UTF-8-SIG with zero synthetic rows.</item>
    <item>test_report_headers_l10n_parity.py synchronously updated asserting len(ReportAtomColumn) == 12, len(sheet2_rows[0]) == 12, and len(reader[0]) == 20.</item>
    <item>test_localization.py, models/test_enums.py, and test_export_service.py pass 100% asserting 12 atom column headers and 20 CSV columns.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do not create separate, disjoint Excel worksheets ("Causal Graph", "Causal Diagnostics").</forbidden>
    <forbidden>Do not inject synthetic summary vectors into rectangular atom CSV streams.</forbidden>
    <forbidden>Do not use untyped dictionary mutation loops in ExportService.</forbidden>
    <forbidden>Do not skip failing 1-hop parity tests; update assertions to 12 columns.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/models/enums.py#L939-L958]</backend>
    <backend>@[backend_v2/l10n/fi.json#L128-L146]</backend>
    <backend>@[backend_v2/l10n/en.json#L128-L146]</backend>
    <backend>@[backend_v2/services/localization.py#L382-L491]</backend>
    <backend>@[backend_v2/models/dtos/export.py#L48-L76]</backend>
    <backend>@[backend_v2/models/dtos/export.py#L99-L135]</backend>
    <backend>@[backend_v2/services/export_service.py#L437-L574]</backend>
    <backend>@[backend_v2/services/export_service.py#L576-L749]</backend>
    <backend>@[backend_v2/services/export_service.py#L751-L912]</backend>
    <backend>@[backend_v2/services/export_service.py#L914-L1034]</backend>
    <backend>@[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L150-L163]</backend>
    <backend>@[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L166-L189]</backend>
    <backend>@[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L256-L387]</backend>
    <backend>@[backend_v2/tests/unit/test_localization.py#L255-L276]</backend>
    <backend>@[backend_v2/tests/unit/models/test_enums.py#L115-L144]</backend>
    <backend>@[backend_v2/tests/unit/services/test_export_service.py#L834-L865]</backend>
  </touched_artifacts>

  <step id="6.1" name="ENUM_AND_LOCALIZATION_KEYS_REGISTRATION">
    <action>In @[backend_v2/models/enums.py#L939-L958], add CAUSAL_STATUS = "causal_status", BLAME_PARENT_ID = "blame_parent_id", and DEPENDENT_COUNT = "dependent_count" to ReportAtomColumn.</action>
    <action>In @[backend_v2/l10n/fi.json#L128-L146], add: "export_col_causal_status": "Kausaalistatus", "export_col_blame_parent_id": "Juurisyyn tunnus", "export_col_dependent_count": "Riippuvuuksien lkm".</action>
    <action>In @[backend_v2/l10n/en.json#L128-L146], add: "export_col_causal_status": "Causal Status", "export_col_blame_parent_id": "Root Cause ID", "export_col_dependent_count": "Dependent Count".</action>
    <constraint invariant="dual_axis_localization_architecture">Axis 2 semantic data localization managed strictly via ReportHeaderResolver and JSON files.</constraint>
  </step>

  <step id="6.2" name="REPORT_HEADER_RESOLVER_EXPANSION">
    <action>In @[backend_v2/services/localization.py#L382-L491], update ReportHeaderResolver: extend get_all_denormalized_csv_headers() to append translated headers for export_col_causal_status, export_col_blame_parent_id, export_col_dependent_count, expanding CSV column count from 17 to 20. Extend atom header resolution to map new ReportAtomColumn members.</action>
    <constraint invariant="single_pipeline_invariant_mandate">All header resolution flows strictly through ReportHeaderResolver SSOT.</constraint>
  </step>

  <step id="6.3" name="EXPORT_DTO_SCHEMA_EXTENSION">
    <action>In @[backend_v2/models/dtos/export.py#L48-L76], extend ExportForensicAtomDTO with: causal_status: Annotated[str | None, Field(default=None, description="Topological argument status (validated, cascading_fault, root_cause, orphan)")] = None, blame_parent_id: Annotated[str | None, Field(default=None, description="Upstream root cause identifier if cascading fault")] = None, dependent_count: Annotated[int | None, Field(default=None, description="Number of downstream propositions dependent on this node")] = None.</action>
    <action>In @[backend_v2/models/dtos/export.py#L99-L135], extend ExportDenormalizedFlatRowDTO with the identical typed fields (causal_status, blame_parent_id, dependent_count).</action>
    <constraint invariant="the_zero_compromise_pledge">Preserve ConfigDict(strict=True, extra="forbid", frozen=True) on all export DTOs.</constraint>
  </step>

  <step id="6.4" name="EXPORT_SERVICE_ENRICHMENT_AND_RECTANGULAR_CSV_STREAMING">
    <action>In @[backend_v2/services/export_service.py#L437-L574] and @[backend_v2/services/export_service.py#L751-L912], enrich canonical Raw Data worksheet (Tab 2) rows with causal fields when causal_result is present.</action>
    <action>In @[backend_v2/services/export_service.py#L576-L749] and @[backend_v2/services/export_service.py#L914-L1034], in export_flat_csv stream rectangular multi-row atom datasets matching Excel Tab 2 row count (len(flat_dtos) == len(report_dto.results)) encoded in UTF-8-SIG with zero synthetic summary rows.</action>
    <constraint invariant="dumb_painter_sdui">Excel and CSV exports maintain 100% row and column parity adhering to the Anti-Synthetic Row Invariant.</constraint>
  </step>

  <step id="6.5" name="SYNCHRONIZE_ONE_HOP_PARITY_TEST_SUITES">
    <action>In @[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L150-L163], @[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L166-L189], and @[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L256-L387], update len(ReportAtomColumn) == 12, len(sheet2_rows[0]) == 12, update CSV header assertion assert len(reader[0]) == 20 (previously 17), and add causal_status, blame_parent_id, dependent_count to expected_atom_fields.</action>
    <action>In @[backend_v2/tests/unit/test_localization.py#L255-L276], assert len(atom_headers) == len(ReportAtomColumn) == 12 and verify ReportHeaderResolver.get_all_denormalized_csv_headers returns 20 columns.</action>
    <action>In @[backend_v2/tests/unit/models/test_enums.py#L115-L144], assert new enum member localization keys for ReportAtomColumn (export_col_causal_status, export_col_blame_parent_id, export_col_dependent_count).</action>
    <action>In @[backend_v2/tests/unit/services/test_export_service.py#L834-L865], add test asserting Tab 2 and CSV causal enrichment parity when causal fusion data is present and when absent.</action>
    <constraint invariant="universal_fail_fast">Zero test regressions across 1-hop parity suites.</constraint>
  </step>

  <test_contracts>
    <test name="test_report_atom_column_has_12_members" category="positive">
      <input>ReportAtomColumn enum</input>
      <expected>len(ReportAtomColumn) == 12 including CAUSAL_STATUS, BLAME_PARENT_ID, DEPENDENT_COUNT</expected>
    </test>
    <test name="test_denormalized_csv_headers_has_20_columns" category="positive">
      <input>ReportHeaderResolver.get_all_denormalized_csv_headers("en")</input>
      <expected>len == 20, ending with ["Causal Status", "Root Cause ID", "Dependent Count"]</expected>
    </test>
    <test name="test_export_flat_csv_row_count_matches_results" category="positive">
      <input>ReportDataDTO with 5 evaluated atoms</input>
      <expected>CSV stream has exactly 6 rows (1 header + 5 atom rows), zero synthetic summary rows</expected>
    </test>
    <test name="test_export_causal_enrichment_parity" category="positive">
      <input>ExecutionRecord with CausalTdaFusionResultDTO in execution_trace</input>
      <expected>Excel Tab 2 and CSV stream rows contain populated causal_status, blame_parent_id, dependent_count matching graph</expected>
    </test>
    <test name="test_export_forensic_atom_dto_extra_field_raises_validation_error" category="error_path">
      <input>ExportForensicAtomDTO with unknown field</input>
      <expected>raises ValidationError (extra='forbid')</expected>
    </test>
    <test name="test_export_denormalized_flat_row_dto_extra_field_raises_validation_error" category="error_path">
      <input>ExportDenormalizedFlatRowDTO with unknown field</input>
      <expected>raises ValidationError (extra='forbid')</expected>
    </test>
    <test name="test_export_flat_csv_fails_non_passed_status" category="error_path">
      <input>ExecutionRecord with status=FAILED</input>
      <expected>raises AppException(status_code=400, "Execution must be in PASSED state")</expected>
    </test>
    <test name="test_export_flat_csv_fails_empty_results" category="boundary">
      <input>ReportDataDTO with results=[]</input>
      <expected>raises AppException(status_code=400, "Execution has no scoreable atoms")</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute: uv run pytest backend_v2/tests/unit/test_report_headers_l10n_parity.py</action>
    <action>Execute: uv run pytest backend_v2/tests/unit/test_localization.py</action>
    <action>Execute: uv run pytest backend_v2/tests/unit/models/test_enums.py</action>
    <action>Execute: uv run pytest backend_v2/tests/unit/services/test_export_service.py</action>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/services/export_service.py --test --ast-strict</action>
    <action>Execute: uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_154/06_phase6_plan.md</action>
  </validation_gate>
</execution_protocol>
