# Implementation Plan: Report Tables SSOT, Causal Export Streaming, Row Data Status Decoupling, ML-Ready Tabular Metrics & Database Reseed

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Objective
Establish complete Single Source of Truth (SSOT) parity, causal completeness, tabular transparency, machine learning readiness, and mathematical rigor across Quorum report tables and tabular exports by:
1. Eliminating naming divergence between `ReportMatrixColumn.LABEL` ("Logiikkamatriisi") and `ReportAtomColumn.MATRIX` ("Matriisi" -> "Logiikkamatriisi") in backend localization files (`fi.json`, `en.json`).
2. Streaming dynamic causal graph propositions (`CausalNodeDTO` from `CausalDiscoveryEngine`) into `ExportForensicAtomDTO` and `ExportDenormalizedFlatRowDTO` under `matrix_label = "Kausaalipäättely"`, populating `causal_status`, `blame_parent_id`, and `dependent_count` in Excel Tab 2 (`Raakadata`) and rectangular CSV.
3. Hardening the mathematical representation of claim evaluations for machine learning: ensuring that criteria hit ratios (specifically 1 passed claim out of 2 evaluated claims) are explicitly paired with clean numeric columns (`hits: int`, `total_atoms: int`, `hit_ratio: float`, `raw_score: float`, `scale_max: float`, `normalized_score: float`) in Excel and CSV.
4. Hardening Tab 2 (`Raakadata`) and CSV exports for machine learning batch analytics: enriching `ReportAtomColumn`, `ExportForensicAtomDTO`, and `ExportDenormalizedFlatRowDTO` with language-agnostic numerical columns (`is_inverse: int` [0/1] and `points_awarded: float` [1.0/0.0]), ensuring ML pipelines aggregate affirmative capability hits without parsing localized text strings or confounding clean anti-pattern tests with positive points.
5. Decoupling affirmative capability scores from inverse negative evidence findings in the UI "Rividata & Taulukot" (Row Data & Tables) view: enriching `ReportRowItemDTO` and `ReportRowItem` with `is_inverse_evidence: bool = False`, propagating this flag from `report_dto.results` in `ReportService.get_report_rows`, and replacing the naked integer score in `execution_reports_view.dart` with semantic status badges (`+1 p` / `0 p` for affirmative capabilities vs `Puhdas` / `⚠️ Negatiivinen löydös` for anti-pattern detectors).
6. Locking the canonical 5-column default baseline (`["label", "distribution", "row_explanation", "criteria", "normalized_score"]`) in Studio Output Profile domain models, DTOs, and synchronizing specifically and exhaustively all 6 output profiles in `seed_data.json`.
7. Safeguarding execution artifact continuity for `exe_c50e968fc9c04906` prior to executing the local database hard reset and reseeding protocol via `uv run python backend_v2/seed/run_seed.py local` to wipe local persistence, purge orphaned artifacts, and re-hydrate the database from `seed_data.json`.

---

## User Review Required
> [!IMPORTANT]
> - **Execution Artifact Continuity Preservation:** `run_seed.py local` drops TinyDB tables and executes `shutil.rmtree` on `data/files/executions/`. To prevent the deletion of `exe_c50e968fc9c04906` (which is needed for Step 6.3 forensic validation), Phase 5 backs up `exe_c50e968fc9c04906` to `scratch/` before the seeder runs, and restores it immediately after re-seeding.
> - **Causal Row Placement:** Dynamic causal propositions (specifically the 28 propositions extracted in `exe_c50e968fc9c04906`) will be appended to Excel Tab 2 (`Raakadata`) and CSV rows under `Logiikkamatriisi` = `"Kausaalipäättely"`. This prevents empty causal columns without creating parallel schemas or a third tab.
> - **Machine Learning (ML) Readability in Tabular Exports:** In Excel Tab 2 and rectangular CSV, two dedicated numerical columns are added:
>   1. `is_inverse: int` (0 = affirmative capability, 1 = inverse/anti-pattern detector).
>   2. `points_awarded: float` (1.0 for passed affirmative capability, 0.0 for failed capability OR clean anti-pattern).
>   This guarantees that ML pipelines compute genuine capability score hits via `df['points_awarded'].sum() == hits` and total defects via `(df['is_inverse'] * (1 - df['result_status'])).sum()`, eliminating reliance on localized text matching (`claim_type`).
> - **Single Source of Truth (SSOT) Header Parity:** All column headers across Tab 1, Tab 2, and CSV are resolved strictly through `ReportHeaderResolver` in `backend_v2/services/localization.py` using typed enums (`ReportMatrixColumn` and `ReportAtomColumn`) mapped to `fi.json` and `en.json`. No ad-hoc header dictionaries exist in the codebase.
> - **Decoupling Affirmative Points from Negative Evidence in UI Row Data:** In the UI "Rividata & Taulukot" tab, anti-pattern detectors display semantic badges (`Puhdas` when clean, `⚠️ Negatiivinen löydös` when defect detected) instead of naked integer points (`1` / `0`), eliminating confusion where anti-patterns appeared as points scored.
- **Dumb Painter Invariant (Zero Presentation Math & Inference):** Across all four presentation targets (Flutter UI, PDF Jinja2 templates, Excel workbooks, and CSV streams), zero calculation, scoring math, or semantic inference takes place. The backend pre-computes all metrics (`points_awarded`, `is_inverse`, `result_status`, `hit_ratio`, `normalized_score`) and delivers them via immutable Pydantic V2 DTOs. Presentation targets act exclusively as "Dumb Painters" rendering pre-resolved data without local computation.

---

## Scope & Target Boundaries

### Target Files (Modifications & Creations)
- `[MODIFY]` @[backend_v2/models/enums.py#L939-L958] - Add `IS_INVERSE = "is_inverse"` and `POINTS_AWARDED = "points_awarded"` to `ReportAtomColumn`.
- `[MODIFY]` @[backend_v2/l10n/fi.json#L128-L144] - Synchronize `export_col_matrix` to `"Logiikkamatriisi"`, declare `export_col_is_inverse` as `"Käänteinen ehto"`, declare `export_col_points_awarded` as `"Saadut pisteet"`, and declare `export_causal_matrix_label` and `export_causal_level_name`.
- `[MODIFY]` @[backend_v2/l10n/en.json#L128-L144] - Synchronize `export_col_matrix` to `"Logic Matrix"`, declare `export_col_is_inverse` as `"Inverse Claim"`, declare `export_col_points_awarded` as `"Points Awarded"`, and declare English equivalents.
- `[MODIFY]` @[backend_v2/models/dtos/export.py#L48-L76] - Enrich `ExportForensicAtomDTO` with `is_inverse: Annotated[int, Field(ge=0, le=1, description="Binary flag: 1 if inverse/anti-pattern detector, 0 if affirmative capability")]` and `points_awarded: Annotated[float, Field(ge=0.0, le=1.0, description="Affirmative score points awarded (1.0 for passed capability, 0.0 for inverse or failed)")]`.
- `[MODIFY]` @[backend_v2/models/dtos/export.py#L99-L135] - Enrich `ExportDenormalizedFlatRowDTO` with `is_inverse: Annotated[int, Field(ge=0, le=1)]` and `points_awarded: Annotated[float, Field(ge=0.0, le=1.0)]`.
- `[MODIFY]` @[backend_v2/services/localization.py#L447-L478] - In `get_all_denormalized_csv_headers`, include `export_col_is_inverse` and `export_col_points_awarded` (expanding CSV from 20 to 22 columns).
- `[MODIFY]` @[backend_v2/services/export_service.py#L447-L584] - In `_build_atom_rows`, populate `is_inverse` and `points_awarded` alongside unmapped causal propositions.
- `[MODIFY]` @[backend_v2/services/export_service.py#L586-L759] - In `_build_denormalized_rows`, populate `is_inverse` and `points_awarded` for all rows.
- `[MODIFY]` @[backend_v2/models/dtos/report_artifact.py#L66-L79] - Enrich `ReportRowItemDTO` with `is_inverse_evidence: Annotated[bool, Field(default=False, description="True if assertion evaluates absence of negative evidence (anti-pattern/defect).")] = False`.
- `[MODIFY]` @[backend_v2/services/report_service.py#L601-L639] - In `get_report_rows`, populate `is_inverse_evidence=atom.is_inverse_evidence` when constructing `ReportRowItemDTO`.
- `[MODIFY]` @[client_app_v2/lib/features/reports/models/report_artifact.dart#L47-L65] - Enrich `ReportRowItem` Freezed model with `@JsonKey(name: 'is_inverse_evidence') @Default(false) bool isInverseEvidence` and re-generate via build runner.
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb#L1855-L1860] - Declare `tableColumnScoreOrStatus`, `reportRowStatusClean`, `reportRowStatusDefectDetected`, `reportRowStatusAffirmativeHit`, and `reportRowStatusAffirmativeMiss`.
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb#L2568-L2573] - Declare English equivalents for row status badges.
- `[MODIFY]` @[client_app_v2/lib/features/reports/views/execution_reports_view.dart#L870-L913] - Update `_buildRowsTab` column header to `l10n.tableColumnScoreOrStatus` and render semantic badges distinguishing affirmative scores from negative findings.
- `[MODIFY]` @[backend_v2/models/domain/output_profile.py#L36-L353] - Declare `STANDARD_MATRIX_VISIBLE_COLUMNS` constant and bind as schema default.
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py#L37-L268] - Enforce `STANDARD_MATRIX_VISIBLE_COLUMNS` default in `OutputProfileCreateDTO` (@[backend_v2/models/dtos/output_profile.py#L37-L268]), `OutputProfileUpdateDTO` (@[backend_v2/models/dtos/output_profile.py#L271-L492]), and `OutputProfileResponseDTO` (@[backend_v2/models/dtos/output_profile.py#L495-L645]).
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/output_profile.dart] - Synchronize `matrixVisibleColumns` default to `['label', 'distribution', 'row_explanation', 'criteria', 'normalized_score']` and re-build Freezed models.
- `[MODIFY]` @[backend_v2/seed/seed_data.json#L21575-L22205] - Synchronize specifically and exhaustively all 6 output profiles (`prf_5d6e7f8091a2b3c4`, `prf_01b1d71000000001`, `prf_02b1d71000000002`, `prf_03b1d71000000003`, `prf_04b1d71000000004`, `prf_05b1d71000000005`) to `matrix_visible_columns = ["label", "distribution", "row_explanation", "criteria", "normalized_score"]`.
- `[MODIFY]` @[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L49-L57] - Assert `export_col_matrix` equals `"Logiikkamatriisi"` and update canonical enum length assertions to `len(ReportAtomColumn) == 14`.
- `[MODIFY]` @[backend_v2/tests/unit/services/test_export_service.py#L607-L670] - Fix hardcoded `"Matriisi"` assertion to `"Logiikkamatriisi"` via `ReportHeaderResolver`, assert `len(ReportAtomColumn) == 14`, and add unit tests asserting causal nodes and ML-ready columns appear with populated metrics.
- `[MODIFY]` @[backend_v2/tests/unit/services/test_report_service.py#L326-L342] - Update `test_get_report_rows` to assert `is_inverse_evidence` propagation for both affirmative and inverse atoms.

### Context Files (Strictly Read-Only)
- `[READ-ONLY]` @[backend_v2/models/enums.py] - SSOT definitions of `ReportMatrixColumn`, `ReportAtomColumn`, and `ReportSheetKey`.
- `[READ-ONLY]` @[backend_v2/services/localization.py] - `ReportHeaderResolver` implementation.
- `[READ-ONLY]` @[backend_v2/models/dtos/export.py] - `ExportForensicAtomDTO`, `ExportMatrixSummaryRowDTO`, `ExportDenormalizedFlatRowDTO`.
- `[READ-ONLY]` @[backend_v2/models/dtos/atom_result.py] - `AtomResultDTO` and `HydratedAtomDTO`.
- `[READ-ONLY]` @[backend_v2/templates/report_template.jinja2] - Jinja2 PDF table column layout.
- `[READ-ONLY]` @[backend_v2/seed/run_seed.py] - Seeder implementation and validation buffers.
- `[READ-ONLY]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart] - Studio 8-column chip configuration.

---

## 5-Column Architectural Directives

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **@[backend_v2/models/enums.py#L939-L958]**, **@[backend_v2/l10n/fi.json#L128-L144]**, **@[backend_v2/l10n/en.json#L128-L144]**, & **@[backend_v2/services/localization.py#L447-L478]** | Terminology drift between Tab 1 (`matrix_col_label`: `"Logiikkamatriisi"`) and Tab 2 (`export_col_matrix`: `"Matriisi"`), and absence of numeric ML indicators for inverse claims. | Synchronize `export_col_matrix` to `"Logiikkamatriisi"` (FI) / `"Logic Matrix"` (EN), declare `ReportAtomColumn.IS_INVERSE` and `ReportAtomColumn.POINTS_AWARDED`, and define `"export_causal_matrix_label"` and `"export_causal_level_name"` with 100% key parity. | Zero new ad-hoc dictionaries or untyped shims; strictly map all column headers through `ReportHeaderResolver` SSOT. | `test_report_matrix_columns_translation_completeness` and `test_report_atom_columns_translation_completeness` in `test_report_headers_l10n_parity.py`. |
| **@[backend_v2/services/export_service.py#L447-L584]** (`_build_atom_rows`) & **@[backend_v2/models/dtos/export.py#L48-L76]** | Confounding affirmative capability points with clean anti-pattern checks in Excel Tab 2 (`result_status == 1`), requiring ML models to parse localized text strings. | Add `is_inverse: int` (0 or 1) and `points_awarded: float` (1.0 or 0.0) to `ExportForensicAtomDTO`, ensuring `points_awarded == 0.0` for anti-patterns and causal nodes, and append all unmapped `CausalNodeDTO` nodes under `matrix_label = "Kausaalipäättely"`. | Zero new Excel worksheets or parallel presentation adapters; append ML metrics and unmapped causal propositions directly to canonical Tab 2 atom rows. | `test_export_excel_includes_causal_propositions_with_metrics` asserting 14-column completeness and `df['points_awarded'].sum() == hits`. |
| **@[backend_v2/services/export_service.py#L586-L759]** (`_build_denormalized_rows`) & **@[backend_v2/models/dtos/export.py#L99-L135]** | Missing explicit numeric score contribution columns in rectangular CSV, forcing external batch pipelines to parse Finnish or English `claim_type`. | Stream unmapped `CausalNodeDTO` nodes and all evaluated atoms into `ExportDenormalizedFlatRowDTO` with explicit numeric metrics (`hits: int`, `total_atoms: int`, `hit_ratio: float`, `raw_score: float`, `scale_max: float`, `normalized_score: float`, `is_inverse: int`, `points_awarded: float`). | Zero bifurcated CSV pipelines; unify all flat-file streaming through typed 22-column `ExportDenormalizedFlatRowDTO`. | `test_export_csv_includes_causal_propositions` asserting 22-column rectangular completeness and numeric claim hit metrics. |
| **@[backend_v2/models/dtos/report_artifact.py#L66-L79]**, **@[backend_v2/services/report_service.py#L601-L639]**, **@[client_app_v2/lib/features/reports/models/report_artifact.dart#L47-L65]**, & **@[client_app_v2/lib/features/reports/views/execution_reports_view.dart#L870-L913]** | Rendering bare integer `1` for passed anti-pattern checks, misleading users into assuming 1 violation occurred or 1 affirmative point was awarded. | Enrich `ReportRowItemDTO` and `ReportRowItem` with `is_inverse_evidence: bool = False`, propagate directly from `AtomResultDTO.is_inverse_evidence`, and render semantic status badges (`+1 p` / `0 p` vs `Puhdas` / `⚠️ Negatiivinen löydös`) in `_buildRowsTab`. | Zero client-side heuristic string parsing ("starts with BANNED PATTERN"); resolve evaluation nature strictly through typed DTO boolean `is_inverse_evidence`. | `test_get_report_rows` unit test verifying `is_inverse_evidence` propagation and Flutter audit loop build passing. |
| **@[backend_v2/models/domain/output_profile.py#L36-L353]**, **@[backend_v2/models/dtos/output_profile.py#L37-L268]** & **@[client_app_v2/lib/features/studio/models/output_profile.dart]** | Inconsistent `matrix_visible_columns` default containing `"raw_score"` instead of `"criteria"` and missing shared constant across Python and Dart. | Declare `STANDARD_MATRIX_VISIBLE_COLUMNS: list[str] = ["label", "distribution", "row_explanation", "criteria", "normalized_score"]` and bind as default in Domain, DTO, and Flutter models. | Zero speculative column resolver classes; enforce column defaults strictly at Pydantic schema and Freezed level. | Pydantic validation asserting `ConfigDict(strict=True, extra="forbid")`, Flutter audit loop build passing, and `test_matrix_summary_table_adapter_success`. |
| **@[backend_v2/seed/seed_data.json#L21575-L22205]** | Divergent `matrix_visible_columns` across seed output profiles and risk of accidental mutation of qualitative prompt texts. | Synchronize specifically and exhaustively all 6 output profiles to `["label", "distribution", "row_explanation", "criteria", "normalized_score"]` while preserving prompt texts 100%. | Zero runtime migration scripts; execute surgical MCP multi-replace edits directly on the seed vault. | `validate_all_seed_collections()` via `run_seed.py local --dry-run` and `audit_database_atoms.py --strict`. |
| **@[backend_v2/tests/unit/services/test_export_service.py#L607-L670]** | Hardcoded string assertion `row["Matriisi"]` at line 667 that breaks upon localization unification. | Update assertion to resolve column header dynamically via `ReportHeaderResolver.get_atom_column_header(ReportAtomColumn.MATRIX, "fi")`. | Zero test mocking workarounds; assert real dataframe column headers from SSOT. | Unit test execution `test_export_excel_with_prompt_block_repo_resolves_matrix_names_and_inverse_claims_positive` passing 100%. |
| **@[data/files/executions/exe_c50e968fc9c04906]** & Database Hard Reset | Blind local database wipe deleting `data/files/executions/exe_c50e968fc9c04906` prior to verification Step 6.3. | Pre-flight backup of `exe_c50e968fc9c04906` directory to `scratch/` prior to `run_seed.py local`, and post-seeding restoration for forensic verification. | Zero permanent disk duplication; isolate temporary backup strictly in `scratch/`. | Step 6.3 execution re-export script validating 28 causal rows and numeric metrics on `exe_c50e968fc9c04906`. |

---

## Execution Protocol

```xml
<execution_protocol>
  <phase id="1" name="Pre-Implementation Cleanups, L10n SSOT Unification &amp; ML Column Registration">
    <step id="1.1" name="Register ML-Ready Columns in ReportAtomColumn Enum">
      <action>
        In `backend_v2/models/enums.py`, update `ReportAtomColumn`:
        Add members:
        `IS_INVERSE = "is_inverse"`
        `POINTS_AWARDED = "points_awarded"`
        Retain canonical enum order placing `IS_INVERSE` and `POINTS_AWARDED` immediately adjacent to `CLAIM_TYPE` and `RESULT_STATUS`.
      </action>
      <constraint invariant="variable_and_schema_preservation_mandate">
        Do not use loose string aliases. Declare explicit StrEnum values and derive `l10n_key` strictly via `f"export_col_{self.value}"`.
      </constraint>
    </step>

    <step id="1.2" name="Synchronize Export Column Matrix and ML Headers in Localization Files">
      <action>
        Update `backend_v2/l10n/fi.json` and `backend_v2/l10n/en.json` to eliminate localization drift:
        1. In `backend_v2/l10n/fi.json`:
           - Update `export_col_matrix` from `"Matriisi"` to `"Logiikkamatriisi"`.
           - Add `"export_col_is_inverse": "Käänteinen ehto"`.
           - Add `"export_col_points_awarded": "Saadut pisteet"`.
           - Add `"export_causal_matrix_label": "Kausaalipäättely"` and `"export_causal_level_name": "Propositio"`.
        2. In `backend_v2/l10n/en.json`:
           - Update `export_col_matrix` from `"Matrix"` to `"Logic Matrix"`.
           - Add `"export_col_is_inverse": "Inverse Claim"`.
           - Add `"export_col_points_awarded": "Points Awarded"`.
           - Add `"export_causal_matrix_label": "Causal Inference"` and `"export_causal_level_name": "Proposition"`.
      </action>
      <constraint invariant="variable_and_schema_preservation_mandate">
        Retain 100% key parity between `fi.json` and `en.json`.
      </constraint>
    </step>
    
    <step id="1.3" name="Update Denormalized CSV Header SSOT in ReportHeaderResolver">
      <action>
        In `backend_v2/services/localization.py` -> `get_all_denormalized_csv_headers`:
        Include `export_col_is_inverse` and `export_col_points_awarded` in the returned ordered header list, expanding canonical CSV headers from 20 to 22 columns.
      </action>
      <constraint invariant="single_pipeline_invariant_mandate">
        All CSV column headers must continue to be generated exclusively through `ReportHeaderResolver`.
      </constraint>
    </step>

    <step id="1.4" name="Fix Hardcoded Column Lookups in Unit Tests">
      <action>
        1. In `backend_v2/tests/unit/services/test_export_service.py` at line 667:
           Replace hardcoded lookup `assert row["Matriisi"] == ...` with dynamic SSOT resolution:
           `atom_col_name = ReportHeaderResolver.get_atom_column_header(ReportAtomColumn.MATRIX, "fi")`
           `assert row[atom_col_name] == "Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)"`
        2. In `backend_v2/tests/unit/test_report_headers_l10n_parity.py`:
           Update assertions verifying `len(ReportAtomColumn) == 14` and `len(atom_headers) == 14`.
        3. In `backend_v2/tests/unit/services/test_export_service.py` line 1280:
           Update `assert len(ReportAtomColumn) == 14` and assert `ReportAtomColumn.IS_INVERSE.value == "is_inverse"` and `ReportAtomColumn.POINTS_AWARDED.value == "points_awarded"`.
        Run localized test suite:
        `uv run pytest backend_v2/tests/unit/test_report_headers_l10n_parity.py backend_v2/tests/unit/test_localization.py -v`
      </action>
      <constraint invariant="universal_quality_gates">
        All tests in `test_report_headers_l10n_parity.py` and `test_localization.py` must pass with zero failures.
      </constraint>
    </step>
  </phase>

  <phase id="2" name="Causal Streaming, Numeric ML Column Hardening &amp; Export Parity">
    <step id="2.1" name="Enrich Export Forensic DTOs with is_inverse and points_awarded">
      <action>
        1. In `backend_v2/models/dtos/export.py`, update `ExportForensicAtomDTO`:
           Add fields:
           `is_inverse: Annotated[int, Field(ge=0, le=1, description="Binary flag: 1 if inverse/anti-pattern detector, 0 if affirmative capability")]`
           `points_awarded: Annotated[float, Field(ge=0.0, le=1.0, description="Affirmative score points awarded (1.0 for passed capability, 0.0 for inverse or failed)")]`
        2. In `backend_v2/models/dtos/export.py`, update `ExportDenormalizedFlatRowDTO`:
           Add fields:
           `is_inverse: Annotated[int, Field(ge=0, le=1)]`
           `points_awarded: Annotated[float, Field(ge=0.0, le=1.0)]`
      </action>
      <constraint invariant="the_zero_compromise_pledge">
        All DTOs must maintain `ConfigDict(strict=True, extra="forbid", frozen=True)` with typed validation constraints.
      </constraint>
    </step>

    <step id="2.2" name="Stream Causal Graph Nodes and Populate ML Columns in Atom Rows">
      <action>
        In `backend_v2/services/export_service.py`, update `_build_atom_rows`:
        1. For evaluative atoms from `report_dto.results`:
           - Compute `is_inverse = 1 if is_inverse_claim else 0`.
           - Compute `points_awarded = 1.0 if (atom.status == ExecutionStatus.PASSED and not is_inverse_claim) else 0.0`.
           - Populate `is_inverse=is_inverse` and `points_awarded=points_awarded` on each constructed `ExportForensicAtomDTO`.
        2. For unmapped causal graph nodes:
           - Construct and append `ExportForensicAtomDTO` with:
             - `matrix_label = LocalizationService.translate("export_causal_matrix_label", locale)`
             - `context_target = ""`
             - `level = 1`
             - `level_name = LocalizationService.translate("export_causal_level_name", locale)`
             - `criterion = node.claim`
             - `claim_type = LocalizationService.translate("export_claim_positive", locale)`
             - `is_inverse = 0`
             - `points_awarded = 0.0` (causal propositions do not inject synthetic affirmative matrix points)
             - `result_status = 1 if node.status == ExecutionStatus.PASSED else 0`
             - `quotes = format_text_observations(node.source_quote)`
             - `ai_reasoning = ""`
             - `causal_status = causal_meta.causal_status`
             - `blame_parent_id = causal_meta.blame_parent_id`
             - `dependent_count = causal_meta.dependent_count`
      </action>
      <constraint invariant="the_zero_compromise_pledge">
        Do not use loose dictionary accumulators or `.get(key, default)`. All constructed entities must strictly validate against `ExportForensicAtomDTO`.
      </constraint>
    </step>

    <step id="2.3" name="Stream Causal Graph Nodes and Populate ML Columns in Flat CSV Rows">
      <action>
        In `backend_v2/services/export_service.py`, update `_build_denormalized_rows`:
        1. Mirror the `is_inverse` and `points_awarded` computation from `_build_atom_rows`.
        2. Append an `ExportDenormalizedFlatRowDTO` for each unmapped causal node with matrix-level placeholders:
           - `execution_id = execution_id`
           - `matrix_label = LocalizationService.translate("export_causal_matrix_label", locale)`
           - `context_target = ""`
           - `distribution = ""`
           - `hits = 1 if node.status == ExecutionStatus.PASSED else 0`
           - `total_atoms = 1`
           - `hit_ratio = 1.0 if node.status == ExecutionStatus.PASSED else 0.0`
           - `raw_score = 1.0 if node.status == ExecutionStatus.PASSED else 0.0`
           - `scale_max = 1.0`
           - `normalized_score = 100.0 if node.status == ExecutionStatus.PASSED else 0.0`
           - `is_inverse = 0`
           - `points_awarded = 0.0`
           - Atom fields populated identically to Step 2.2.
      </action>
      <constraint invariant="single_pipeline_invariant_mandate">
        Do not create parallel CSV writing branches. CSV generation must continue to flow through `ExportDenormalizedFlatRowDTO` and `writer.writerow()`.
      </constraint>
    </step>

    <step id="2.4" name="Unit Testing ML Columns and Causal Export Population">
      <action>
        In `backend_v2/tests/unit/services/test_export_service.py`:
        1. Add unit test `test_export_excel_includes_causal_propositions_with_metrics`: Verify that when an execution contains a `CausalGraphPayloadDTO`, Excel Tab 2 contains 14 columns, including `is_inverse` and `points_awarded`, with `matrix_label == "Kausaalipäättely"`, non-empty `causal_status`, `blame_parent_id`, and `dependent_count == 1`.
        2. Add unit test `test_export_csv_includes_causal_and_ml_columns`: Verify that CSV output lines contain exactly 22 columns with populated `is_inverse` (0/1) and `points_awarded` (1.0/0.0).
        3. Assert mathematical invariant: For any evaluative matrix, `sum(row['points_awarded'])` over affirmative claims equals the matrix's `hits` value.
        Run tests: `uv run pytest backend_v2/tests/unit/services/test_export_service.py -k "causal or export" -v`
      </action>
      <constraint invariant="deceptive_persistence_mocking_ban">
        Assert real values returned in dataframes and CSV reader streams, verifying that `points_awarded` matches the exact numeric scoring invariant.
      </constraint>
    </step>
  </phase>

  <phase id="3" name="Tabular UI Row Data Status Decoupling &amp; Semantic Badges">
    <step id="3.1" name="Enrich ReportRowItem DTO and Freezed Model with is_inverse_evidence">
      <action>
        1. In `backend_v2/models/dtos/report_artifact.py`, update `ReportRowItemDTO`:
           Add field:
           `is_inverse_evidence: Annotated[bool, Field(default=False, description="True if assertion evaluates absence of negative evidence (anti-pattern/defect).")] = False`
        2. In `client_app_v2/lib/features/reports/models/report_artifact.dart`, update `ReportRowItem`:
           Add field:
           `@JsonKey(name: 'is_inverse_evidence') @Default(false) bool isInverseEvidence,`
        3. Run Flutter build runner to re-generate Freezed and JsonSerializable code:
           `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/reports/models/report_artifact.dart --build`
      </action>
      <constraint invariant="ban_drive_by_schema_mutations">
        Enforce Full-Duplex Serialization Parity: Python and Flutter definitions must match 1:1 on `@JsonKey(name: 'is_inverse_evidence')`.
      </constraint>
    </step>

    <step id="3.2" name="Propagate is_inverse_evidence in ReportService.get_report_rows">
      <action>
        In `backend_v2/services/report_service.py` -> `get_report_rows`:
        Pass `is_inverse_evidence=atom.is_inverse_evidence` into `ReportRowItemDTO` instantiation.
      </action>
      <constraint invariant="the_zero_compromise_pledge">
        Do not hardcode or infer from string names. Read directly from typed `atom.is_inverse_evidence`.
      </constraint>
    </step>

    <step id="3.3" name="Declare Semantic Row Status Localizations">
      <action>
        1. In `client_app_v2/lib/l10n/app_fi.arb`, add:
           `"tableColumnScoreOrStatus": "Pisteet / Tila",`
           `"reportRowStatusClean": "Puhdas",`
           `"reportRowStatusDefectDetected": "Negatiivinen löydös",`
           `"reportRowStatusAffirmativeHit": "+1 p",`
           `"reportRowStatusAffirmativeMiss": "0 p"`
        2. In `client_app_v2/lib/l10n/app_en.arb`, add:
           `"tableColumnScoreOrStatus": "Score / Status",`
           `"reportRowStatusClean": "Clean",`
           `"reportRowStatusDefectDetected": "Defect Detected",`
           `"reportRowStatusAffirmativeHit": "+1 pt",`
           `"reportRowStatusAffirmativeMiss": "0 pt"`
      </action>
      <constraint invariant="dual_axis_localization_mandate">
        Enforce compile-time .arb parity between Finnish and English without hardcoded strings.
      </constraint>
    </step>

    <step id="3.4" name="Render Semantic Status Badges in Flutter ExecutionReportsView">
      <action>
        In `client_app_v2/lib/features/reports/views/execution_reports_view.dart` -> `_buildRowsTab`:
        1. Update the middle column header:
           `DataColumn(label: Text(l10n.tableColumnScoreOrStatus)),`
        2. Replace the second cell `DataCell(Text('${row.score.toInt()}'))` with a semantic badge builder:
           - For inverse evidence (`row.isInverseEvidence == true`):
             - When `row.score >= 1.0` (clean, no defect): Render a subtle chip with `Icons.shield_outlined`, `colorScheme.surfaceContainerHighest`, and text `l10n.reportRowStatusClean`.
             - When `row.score == 0.0` (defect detected): Render an alert chip with `Icons.warning_amber_rounded`, `colorScheme.errorContainer`, border `colorScheme.error`, and text `l10n.reportRowStatusDefectDetected`.
           - For affirmative evidence (`row.isInverseEvidence == false`):
             - When `row.score >= 1.0` (capability verified): Render a success chip with `Icons.check_circle_outline`, `colorScheme.primaryContainer`, and bold text `l10n.reportRowStatusAffirmativeHit`.
             - When `row.score == 0.0` (not exhibited): Render a neutral chip with `colorScheme.surfaceContainerLow` and text `l10n.reportRowStatusAffirmativeMiss`.
      </action>
      <constraint invariant="flutter_theme_sovereignty">
        Do not use hardcoded Color literals. Strictly resolve all styling through `Theme.of(context).colorScheme`.
      </constraint>
    </step>

    <step id="3.5" name="Unit Test Row Item Inverse Evidence Propagation">
      <action>
        In `backend_v2/tests/unit/services/test_report_service.py`, update `test_get_report_rows`:
        Assert that when `report_dto.results` contains both an affirmative atom (`is_inverse_evidence=False`) and an inverse atom (`is_inverse_evidence=True`), `get_report_rows` outputs `ReportRowItemDTO` instances preserving the exact boolean value.
        Run test: `uv run pytest backend_v2/tests/unit/services/test_report_service.py -k "test_get_report_rows" -v`
      </action>
      <constraint invariant="universal_quality_gates">
        All assertions must pass cleanly.
      </constraint>
    </step>
  </phase>

  <phase id="4" name="Default Presentation Columns Hardening &amp; Seed Vault Synchronization">
    <step id="4.1" name="Define Standard Matrix Visible Columns SSOT in Backend and Flutter">
      <action>
        1. In `backend_v2/models/domain/output_profile.py` and `backend_v2/models/dtos/output_profile.py`:
           - Declare constant:
             `STANDARD_MATRIX_VISIBLE_COLUMNS: list[str] = ["label", "distribution", "row_explanation", "criteria", "normalized_score"]`
           - Set this constant as the field default on `matrix_visible_columns: list[str] = Field(default_factory=lambda: list(STANDARD_MATRIX_VISIBLE_COLUMNS))`.
           - Ensure model validators continue to enforce that all items in `matrix_visible_columns` match valid `ReportMatrixColumn` members Fail-Fast.
        2. In `client_app_v2/lib/features/studio/models/output_profile.dart`:
           - Update default for `matrixVisibleColumns` to `['label', 'distribution', 'row_explanation', 'criteria', 'normalized_score']`.
           - Run Flutter audit loop to re-generate Freezed models: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`.
      </action>
      <constraint invariant="ban_drive_by_schema_mutations">
        Do not add loose optional attributes. Maintain 1:1 cross-domain parity between Python and Dart Freezed schemas.
      </constraint>
    </step>

    <step id="4.2" name="Synchronize All Output Profiles in Seed Vault">
      <action>
        In `backend_v2/seed/seed_data.json`, update the `matrix_visible_columns` property of specifically and exhaustively all 6 output profiles:
        1. `prf_5d6e7f8091a2b3c4` (Executive Summary)
        2. `prf_01b1d71000000001` (Workflow 1 Profile)
        3. `prf_02b1d71000000002` (Workflow 2 Profile)
        4. `prf_03b1d71000000003` (Workflow 3 Profile)
        5. `prf_04b1d71000000004` (Workflow 4 Profile)
        6. `prf_05b1d71000000005` (Workflow 5 Profile)
        Set each to: `["label", "distribution", "row_explanation", "criteria", "normalized_score"]`.
      </action>
      <constraint invariant="prompt_preservation_mandate">
        Do not modify prompt texts, system instructions, or descriptions. Modify exclusively the `matrix_visible_columns` string arrays.
      </constraint>
    </step>

    <step id="4.3" name="Verify Output Profile and SDUI Parity Tests">
      <action>
        Run existing output profile and SDUI matrix table tests to confirm zero regressions:
        `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_matrix_summary_table_adapter.py backend_v2/tests/unit/services/test_output_profile_studio_parity.py -v`
      </action>
      <constraint invariant="universal_quality_gates">
        All adapter and profile tests must pass cleanly.
      </constraint>
    </step>
  </phase>

  <phase id="5" name="Local Database Hard Reset &amp; Reseeding Protocol">
    <step id="5.1" name="Two-Phase Pre-Flight In-Memory Seed Validation">
      <action>
        Execute in-memory dry run and atom database audit to assert that `seed_data.json` complies 100% with Pydantic V2 schemas before wiping the database:
        1. `uv run python backend_v2/seed/run_seed.py local --dry-run`
        2. `uv run python scripts/audit_database_atoms.py --strict`
      </action>
      <constraint invariant="the_zero_compromise_pledge">
        Both commands must return exit code 0. If any validation fails, do not proceed with database wipe.
      </constraint>
    </step>

    <step id="5.2" name="Execution Artifact Pre-Flight Backup and Local Database Hard Reset">
      <action>
        Safeguard physical execution artifacts @[data/files/executions/exe_c50e968fc9c04906] and execute local seeding:
        1. Copy @[data/files/executions/exe_c50e968fc9c04906] to `<appDataDir>\brain\<conversation-id>\scratch\exe_c50e968fc9c04906` to prevent seeder `shutil.rmtree` wipe.
        2. Execute the local hard reset and seeding command via `run_command`:
           `uv run python backend_v2/seed/run_seed.py local`
        3. Restore @[data/files/executions/exe_c50e968fc9c04906] from `scratch/` into `data/files/executions/exe_c50e968fc9c04906`.
      </action>
      <constraint invariant="hard_reset_mandate">
        Target strictly the local environment (`local`). Production, dev, or staging targets are prohibited.
      </constraint>
    </step>

    <step id="5.3" name="Validate Post-Seeding Database State">
      <action>
        Verify that the seed validation audit loop passes cleanly after re-hydration:
        `uv run python scripts/backend_audit_loop.py backend_v2/seed/ --test`
      </action>
      <constraint invariant="post_execution_quality_gate">
        The seeding verification audit must complete with exit code 0.
      </constraint>
    </step>
  </phase>

  <phase id="6" name="Global Verification Gate">
    <step id="6.1" name="Execute Global Backend Audit Gate">
      <action>
        Execute the comprehensive backend audit script:
        `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`
      </action>
      <constraint invariant="backend_audit_execution">
        Ruff formatting, MyPy strict typing, clean imports, and all Pytest unit tests must pass 100%.
      </constraint>
    </step>

    <step id="6.2" name="Execute Flutter Audit Loop">
      <action>
        Execute the comprehensive Flutter audit script:
        `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/reports/ --build`
      </action>
      <constraint invariant="flutter_audit_execution">
        Flutter analyze, format, and Freezed code generation must pass 100%.
      </constraint>
    </step>

    <step id="6.3" name="Verify Real Artifact Export and Row Data View Against Past Execution">
      <action>
        Run a scratch script to re-generate Excel and CSV exports for @[data/files/executions/exe_c50e968fc9c04906] and assert:
        1. Tab 2 contains both evaluative matrix criteria AND the 28 causal propositions under `Logiikkamatriisi` = `"Kausaalipäättely"`.
        2. Column `Kausaalistatus`, `Juurisyyn tunnus`, and `Riippuvuuksien lkm` contain valid populated values for causal nodes.
        3. Column 1 header is `"Logiikkamatriisi"` on both Tab 1 and Tab 2.
        4. Columns `hits`, `total_atoms`, and `hit_ratio` contain pure numeric values, verifying the claim hit ratio semantics (specifically 1 passed claim out of 2 evaluated claims yielding `0.50`).
        5. Columns `is_inverse` (0/1) and `points_awarded` (1.0/0.0) contain pure numerical values, satisfying mathematical identity: `sum(points_awarded) == hits` for each logic matrix.
        6. Verify that `get_report_rows` for report `rep_2ea65cdc33624853` returns `is_inverse_evidence=True` for all banned pattern claims, confirming that the UI displays `Puhdas` / `⚠️ Negatiivinen löydös` badges instead of confusing naked integer `1` / `0` scores.
      </action>
      <constraint invariant="temporary_workspace_sandbox">
        Execute scratch script exclusively in `<appDataDir>\brain\<conversation-id>\scratch\`.
      </constraint>
    </step>
  </phase>
</execution_protocol>
```

---

## Verification Plan

### Automated Test Gates
1. **Localization Parity:** `uv run pytest backend_v2/tests/unit/test_report_headers_l10n_parity.py`
2. **Export Service Unit Suite:** `uv run pytest backend_v2/tests/unit/services/test_export_service.py`
3. **Report Service Row Item Suite:** `uv run pytest backend_v2/tests/unit/services/test_report_service.py -k "test_get_report_rows"`
4. **SDUI Table Adapter Suite:** `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_matrix_summary_table_adapter.py`
5. **Seed In-Memory Preflight:** `uv run python backend_v2/seed/run_seed.py local --dry-run`
6. **Database Atom Audit:** `uv run python scripts/audit_database_atoms.py --strict`
7. **Post-Seeding Validation:** `uv run python scripts/backend_audit_loop.py backend_v2/seed/ --test`
8. **Global Backend Audit Gate:** `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`
9. **Flutter Code Generation & Analysis:** `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/reports/ --build`

### Manual Forensic Verification
- Inspect generated `report.xlsx` and `report.csv` using Python in `scratch/`:
  - Assert `df_tab2[df_tab2['Logiikkamatriisi'] == 'Kausaalipäättely']` has 28 rows.
  - Assert `df_tab2['Kausaalistatus'].dropna()` is non-empty.
  - Assert `df_tab1.columns[1] == 'Logiikkamatriisi'` and `df_tab2.columns[0] == 'Logiikkamatriisi'`.
  - Assert `df_tab1['Osumasuhde']` (or `hit_ratio`) is a numeric float (specifically `0.50`), corresponding to the criteria column value `"1/2"`.
  - Assert Tab 2 has 14 columns and CSV has 22 columns with populated `is_inverse` (0 or 1) and `points_awarded` (1.0 or 0.0).
  - Assert mathematical identity: `df_tab2[df_tab2['Käänteinen ehto'] == 0]['Saadut pisteet'].sum() == df_tab1['Osumat'].sum()`.
- Inspect "Rividata & Taulukot" tab in `ExecutionReportsView`:
  - Verify that affirmative capability rows display `+1 p` (green check) or `0 p` (neutral).
  - Verify that inverse anti-pattern rows display `Puhdas` (shield badge) when no violation occurred, and `⚠️ Negatiivinen löydös` (warning badge) when a violation was committed.
