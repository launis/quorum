# Implementation Plan - Logic Matrix, Excel and CSV Parity Architecture

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## 1. Executive Summary

### 1.1 Objective
Unify Quorum's presentation and export pipelines to achieve cross-surface parity between the Logic Matrix (`SduiMatrixTableBlock` in Flutter UI and PDF), Quorum Studio Output Profile configuration (`MatrixSummaryTableCard`), and spreadsheet/flat file exports (`Excel` and `CSV`), backed by a Single Source of Truth (SSOT) multilingual localization architecture with a centralized typed header resolver.

### 1.2 Core Architectural Invariants
1. **Multilingual SSOT Sovereignty:** All column headers, sheet titles, and claim type labels across all presentation and export surfaces (Flutter UI, WeasyPrint PDF, Excel Tab 1, Excel Tab 2, and CSV) MUST resolve exclusively from the central localization files `@[backend_v2/l10n/fi.json#L71-L83]` and `@[backend_v2/l10n/en.json#L71-L83]` via `LocalizationService.translate(key, locale)` and `ReportHeaderResolver`. In-code shadow dictionaries (specifically `_EXCEL_KEYS`) are strictly prohibited and eradicated.
2. **Centralized Typed Header SSOT:** All table columns across presentation and export layers are backed by typed enums `ReportMatrixColumn` and `ReportAtomColumn` in `@[backend_v2/models/enums.py#L893-L897]` and resolved via `ReportHeaderResolver` in `@[backend_v2/services/localization.py#L114-L377]`. Services, templates, and adapters must never use raw string literals or dynamic string formatting for column identifiers.
3. **Screen UI and PDF (Presentation Layer):** Remain compact and aggregated at the matrix axis level (`MatrixScorecardRowDTO`), dynamically displaying only the columns specified in `OutputProfile.matrix_visible_columns` to avoid sensory overload.
4. **Excel Tab 1 ("Yhteenveto" / Matrix Summary Completeness):** In contrast to Flutter UI and PDF presentations which allow hiding specific columns, Excel Tab 1 ALWAYS includes all standard matrix columns (specifically and exhaustively all 9 members of `ReportMatrixColumn`) using identical `matrix_col_{col}` localization keys without visual omission.
5. **Excel Tab 2 ("Raakadata" / Raw Evaluated Atoms Completeness):** Provides a complete rectangular forensic table containing every evaluated atom across all 9 members of `ReportAtomColumn` (specifically: `matrix_label`, `context_target`, `level`, `level_name`, `criterion`, `claim_type`, `result_status`, `quotes`, `ai_reasoning`). Dead placeholder columns (`AI-sääntö`, `Käytetyt lähteet`, `Luottamusarvio`, `Perustelun pituus`) are permanently eradicated. Essential context fields (`Kohdedokumentti`, `Taso`, `Tason nimi`, `Arviointikriteeri`, `Väitetyyppi`, `Tulos (Status)`, `Tekstin havainto`, `AI-perustelu`) are populated deterministically. `Tulos (Status)` is strictly a binary integer: `1` or `0`.
6. **CSV Export Completeness:** Transforms from a legacy single-row machine vector into a tabular raw atom dataset matching Excel Tab 2, resolving identical SSOT column headers via `ReportAtomColumn` and including all atom rows, encoded in UTF-8-SIG for instant compatibility with spreadsheet applications.
7. **Zero Naked Dicts and Strict DTO State Transit:** All row models, presentation exports, and export results MUST be 100% strictly typed Pydantic V2 DTOs (`ExportForensicAtomDTO`, `ExportMatrixSummaryRowDTO`, `ExportPayloadDTO`) in `@[backend_v2/models/dtos/export.py]` [NEW]. All loose row dictionaries, ad-hoc dictionary mutation accumulators (`matrix_metrics = {}`), and anonymous state tuples (`tuple[bytes, str]`) across `export_service.py` and `report_service.py` are strictly eradicated.
8. **Mathematical Dumb Painter Projection Invariant (Anti-Synthetic Row Law):** Export services (`ExportService`) operate strictly as 100% pure Dumb Painters. They are mathematically forbidden from synthesizing, extrapolating, or inventing phantom rows, synthetic summary records, or ad-hoc metrics. Excel Tab 1 row count is invariant: `actual_summary_rows == len(matrices)`. Excel Tab 2 and CSV row count is invariant: `actual_atom_rows == len(report_dto.results)`. Column headers are strictly bounded to `ReportMatrixColumn` (9 members) and `ReportAtomColumn` (9 members). Any attempt to inject un-evaluated rows, shadow columns, or heuristic synthetic metrics is mathematically blocked by strict Pydantic V2 `extra='forbid'` schemas and verified by deterministic row-count equality tests.
9. **Cross-Platform Studio Configuration SSOT Parity (Dual-Axis Convergence):** Quorum Studio's Output Profile configuration UI (`MatrixSummaryTableCard` in Flutter) MUST display column selection chips with labels 1:1 identical to the resulting report and spreadsheet column headers. In `client_app_v2/lib/l10n/app_fi.arb` and `app_en.arb`, all 9 `studioMatrixCol*` keys MUST match the canonical strings from `backend_v2/l10n/fi.json` and `en.json` (`matrix_col_*`). Discrepancies between configuration labels and export headers (specifically: calling a column 'Ulottuvuus' in Studio but 'Logiikkamatriisi' in export) are strictly prohibited and prevented by cross-platform parity tests.
10. **Slug Fallback Eradication Mandate (Zero-Slug-Fallback Law):** Using `slug` as a fallback for missing display labels or human-readable names (`?? block.slug`, `: bp.slug`) is strictly prohibited across the entire codebase. Domain entities (Workflows, Steps, PromptBlocks, Matrices) must define clean human-readable names via `I18nText` (`label` / `name`). Machine slugs exist exclusively as technical URL/routing identifiers, never as presentation substitutes.
11. **Unified I18nText Dumb Painter Pipeline Invariant (Zero-Guessing Localization Law):** User-configured graph/chart titles (specifically `MatrixSynthesisGroup.title: I18nText` configured in Quorum Studio) are persisted strictly as multilingual dictionaries (`translations: {'en': 'Executive Cognitive Radar', 'fi': 'Johdon kognitiivinen tutka'}`) and flow through the sovereign Pydantic SDUI pipeline (`MatrixGraphsAdapter.build()` via `grp.title.resolve(locale)`). The pipeline is mathematically deterministic: it reads the requested locale directly from the `I18nText` DTO with zero LLM translation calls, zero heuristic guessing, zero machine slug fallbacks, and zero ad-hoc string formatting, delivering identical Dumb Painter SDUI payloads to both Flutter UI and WeasyPrint PDF.

---

## 2. Target Boundaries & Scope

### 2.1 Target Files
- `@[backend_v2/models/enums.py#L893-L897]` [MODIFY]
- `@[backend_v2/models/dtos/export.py]` [NEW]
- `@[backend_v2/models/dtos/__init__.py]` [MODIFY]
- `@[backend_v2/services/flattener.py]` [DELETE]
- `@[backend_v2/models/dtos/flat_record.py]` [DELETE]
- `@[backend_v2/tests/conftest.py]` [MODIFY]
- `@[backend_v2/l10n/fi.json#L71-L83]` [MODIFY]
- `@[backend_v2/l10n/en.json#L71-L83]` [MODIFY]
- `@[client_app_v2/lib/l10n/app_fi.arb#L980-L1396]` [MODIFY]
- `@[client_app_v2/lib/l10n/app_en.arb#L1524-L2068]` [MODIFY]
- `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart#L10-L93]` [MODIFY]
- `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L12-L285]` [MODIFY]
- `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L62-L78]` [MODIFY]
- `@[backend_v2/services/localization.py#L114-L377]` [MODIFY]
- `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py#L51-L101]` [MODIFY]
- `@[backend_v2/services/export_service.py#L55-L74]` [MODIFY]
- `@[backend_v2/services/export_service.py#L77-L317]` [MODIFY]
- `@[backend_v2/services/report_service.py#L299-L458]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_export_service.py#L111-L153]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_export_service.py#L156-L183]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_export_service.py#L186-L215]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_export_service.py#L283-L297]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_export_service.py#L300-L358]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_export_service.py#L361-L478]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_export_service.py#L481-L493]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_export_service.py#L515-L593]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_export_service.py#L596-L659]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_export_service.py#L662-L737]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_export_service.py#L740-L781]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_report_service.py#L227-L260]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_report_service.py#L485-L522]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_report_service.py#L648-L690]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_report_service.py#L693-L753]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_report_service.py#L756-L811]` [MODIFY]
- `@[backend_v2/tests/unit/services/test_report_service_synthesis_args.py#L26-L109]` [MODIFY]
- `@[backend_v2/tests/unit/test_flattener.py]` [DELETE]
- `@[backend_v2/tests/unit/models/dtos/test_flat_record.py]` [DELETE]
- `@[backend_v2/tests/unit/test_report_headers_l10n_parity.py]` [NEW]

### 2.2 Context Files [READ-ONLY]
- `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart#L15-L50]`
- `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]`
- `@[backend_v2/models/dtos/matrix_scorecard.py#L188-L345]`
- `@[backend_v2/models/dtos/atom_result.py#L78-L161]`
- `@[backend_v2/templates/report_template.jinja2#L336-L440]`

---

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

Before introducing new parity logic, active anti-patterns in `@[backend_v2/services/export_service.py#L77-L317]` and its callers must be eliminated:
1. **Bifurcated Localization Map:** `_EXCEL_KEYS` in `export_service.py` duplicates translation strings in code. All export keys must be centralized into `@[backend_v2/l10n/fi.json#L71-L83]` and `@[backend_v2/l10n/en.json#L71-L83]`.
2. **Dead Extraction Helper:** `_extract_claim_rule()` attempts to extract `ai_description` from prompt blocks for individual atom evaluations, which yields an empty string across all runs. It must be deleted.
3. **Dead Column Constants:** `excelHeaderAiRule` ("AI-sääntö"), `excelHeaderUsedSources` ("Käytetyt lähteet"), `excelHeaderConfidence` ("Luottamusarvio"), and `excelHeaderReasoningLength` ("Perustelun pituus") must be removed.
4. **Incomplete Summary Columns:** Tab 1 currently hardcodes only 3 columns. While Flutter UI and PDF presentations allow hiding specific columns via `OutputProfile.matrix_visible_columns`, Excel Tab 1 must be refactored to unconditionally output ALL 9 `ReportMatrixColumn` members using SSOT `matrix_col_{col}` headers for complete analytical auditing.
5. **Dead Test Helper Import:** `backend_v2/tests/unit/services/test_export_service.py` imports dead helper `_extract_claim_rule`, and lines `@[backend_v2/tests/unit/services/test_export_service.py#L111-L153]` (`test_extract_claim_rule`) assert its extraction behavior. Both the import and the test must be deleted to prevent import errors once `_extract_claim_rule` is eradicated.
6. **Legacy Single-Row CSV Assertions & Export Return Unpacking Modernization:** `@[backend_v2/tests/unit/services/test_export_service.py#L283-L297]` and `@[backend_v2/tests/unit/services/test_export_service.py#L481-L493]` assert the obsolete single-row format from `FlatFileService`. They must be updated to assert multi-row rectangular atom records with `ReportAtomColumn` headers. Additionally, all 9 test cases in `test_export_service.py` calling `service.export_excel(...)` or `service.export_flat_csv(...)` (`#L156-L183`, `#L186-L215`, `#L283-L297`, `#L300-L358`, `#L361-L478`, `#L481-L493`, `#L515-L593`, `#L596-L659`, `#L662-L737`) currently perform anonymous 2-tuple unpacking (`bytes, filename = ...`); they must be updated to consume typed `ExportPayloadDTO` (`payload.content_bytes`, `payload.filename`), eliminating anonymous state tuples per `ban_anonymous_state_tuples`.
7. **Eradication of FlatFileService & FlatExecutionRecordDTO Dict Mutation Accumulators:** `FlatFileService.flatten_results()` accumulates unvalidated dictionary mutations (`matrix_metrics: dict[...]`), and `FlatExecutionRecordDTO.to_csv_dict()` performs loose dictionary merging for single-row CSV output. Both services and models, along with their unit tests, are slated for complete eradication in Phase 4 when CSV export transitions to typed `ExportForensicAtomDTO` rectangular streaming.
8. **Early Import in conftest.py:** `@[backend_v2/tests/conftest.py]` line 13 imports `FlatExecutionRecordDTO` as a top-level fixture dependency. When `flat_record.py` is deleted, this must be switched to import `ExportPayloadDTO` from `backend_v2.models.dtos.export` to prevent cascade test startup failures.
9. **Stale Mock Return Values in Report Service Tests:** Mock fixtures across all 5 test functions in `@[backend_v2/tests/unit/services/test_report_service.py#L227-L260]`, `@[backend_v2/tests/unit/services/test_report_service.py#L485-L522]`, `@[backend_v2/tests/unit/services/test_report_service.py#L648-L690]`, `@[backend_v2/tests/unit/services/test_report_service.py#L693-L753]`, `@[backend_v2/tests/unit/services/test_report_service.py#L756-L811]` and `@[backend_v2/tests/unit/services/test_report_service_synthesis_args.py#L26-L109]` configure `export_service.export_excel.return_value = (b"excel_bytes", "report.xlsx")` and `export_service.export_flat_csv = MagicMock(return_value=(b"csv_bytes", "report.csv"))`. These must all be updated to return typed `ExportPayloadDTO` instances to eliminate anonymous tuple unpack errors when `ReportService` consumes the payload.
10. **Flutter Studio Output Profile Terminological Drift:** In `@[client_app_v2/lib/l10n/app_fi.arb#L1308-L1396]` and `@[client_app_v2/lib/l10n/app_en.arb#L1983-L2068]`, Output Profile column configuration chips use legacy labels ('Ulottuvuus' instead of 'Logiikkamatriisi', 'Rivisyy / Peruste' instead of 'Selitys', 'Normitettu' instead of 'Normalisoitu pisteytys', 'Pistemäärä' instead of 'Pisteet'). These must be synchronized to match Backend SSOT strings 1:1.
11. **MetadataBlockCard Raw Key Leakage:** `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart#L10-L93]` renders raw un-localized keys (`date`, `organization`, `user`, `scoring_engine`, `strictness`, `cost`, `tokens`) directly via `Text(field)`. It must be refactored to use a dedicated `getFieldLabel(BuildContext context, String field)` helper resolving localized strings from `AppLocalizations`.
12. **MatrixGraphItemEditor Hardcoded English & ID Leakage:** `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L12-L285]` lines 78 and 246 hardcode English locale resolution (`group.title.translations['en']`, `block.label.translations['en'] ?? block.slug`), ignoring active Finnish UI locale, and line 272 leaks raw block IDs (`blk_...`) into chip labels. It must be refactored to resolve active locale via `group.title.get(localeCode, fallback: 'en')` and `block.label.get(localeCode, fallback: 'en')` with zero slug fallback, rendering clean user-defined titles.
13. **XAI Extension Labels Terminological Divergence:** Output profile XAI extensions in `app_fi.arb` and `app_en.arb` drift from backend `xai_ext_*` reporting keys (specifically: 'Paholaisen asianajaja' vs 'Falsifikaatio', 'Sävy' vs 'Emotionaalinen sävy', 'AI:n Varmuus' vs 'Luottamus', 'Teoriayhteys' vs 'Teorialinkitys', 'Valmennusvinkki' vs 'Valmennus', 'Lähde-ID' vs 'Lähdetunniste', 'Kontekstuaalinen ohitus' vs 'Kontekstuaalinen yliajo', 'Lähdeviite' vs 'Sitaatti'). They must be synchronized to establish 1:1 SSOT parity.
14. **WorkflowStepCard Slug Fallback Eradication:** `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L62-L78]` line 75 falls back to `bp.slug` if label is missing (`label.isNotEmpty ? label : bp.slug`). Per Invariant 10, machine slugs must never serve as presentation fallbacks; the method must return `label` directly.

---

## 4. 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/models/enums.py#L893-L897]`** | Banned ad-hoc string literals and magic column names across presentation and export layers. | Mandatory typed `ReportMatrixColumn(StrEnum)`, `ReportAtomColumn(StrEnum)`, and `ReportSheetKey(StrEnum)` with `@property def l10n_key(self) -> str:` mapping. | Pruned nested subclasses or multi-class hierarchies; plain `StrEnum` instances encapsulate all column and sheet taxonomy. | Pytest: `test_report_headers_l10n_parity.py` validates all members map to valid non-empty translation keys. |
| **`@[backend_v2/models/dtos/export.py]` [NEW]** | Banned untyped row dictionaries, anonymous tuples (`tuple[bytes, str]`), synthetic phantom rows, and naked dict accumulators in export services. | Mandatory immutable Pydantic V2 DTOs: `ExportForensicAtomDTO` (strictly 9 fields matching `ReportAtomColumn`), `ExportMatrixSummaryRowDTO` (strictly 9 fields matching `ReportMatrixColumn`), and `ExportPayloadDTO` (for export returns) with `ConfigDict(strict=True, extra="forbid", frozen=True)`. Zero synthetic attributes permitted. | Pruned loose dictionary creation, dead columns (`ai_rule`, `confidence`), and intermediate dict mutation layers; direct mapping to `ReportAtomColumn` and `ReportMatrixColumn`. | Pytest: unit tests in `test_export_service.py` and `test_report_headers_l10n_parity.py` assert strict field validation, frozen immutability, `extra="forbid"` rejection of ad-hoc keys, and mathematical row-count invariance (`len(rows) == len(input_dtos)`). |
| **`@[backend_v2/services/flattener.py]` [DELETE] & `@[backend_v2/models/dtos/flat_record.py]` [DELETE]** | Banned legacy single-row machine vectors and unannotated dictionary mutation accumulators (`matrix_metrics = {}`). | Completely eradicate `FlatFileService` and `FlatExecutionRecordDTO` in Phase 4; replace with direct `ExportForensicAtomDTO` streaming in `ExportService.export_flat_csv()`. | Pruned 133 lines of dead flattener code, raw dictionary accumulators, and obsolete tests (`test_flattener.py`, `test_flat_record.py`). | AST Guardrail: verify physical file deletion; zero imports of `FlatFileService` or `FlatExecutionRecordDTO` remain across repo. |
| **`@[backend_v2/tests/conftest.py]`** | Banned broken test imports resulting from deleting legacy DTO modules. | Update early import in `backend_v2/tests/conftest.py` from `FlatExecutionRecordDTO` to `from backend_v2.models.dtos.export import ExportPayloadDTO as _ExportPayloadDTO; _ = _ExportPayloadDTO`. | Pruned stale test setup dependencies; guarantees zero test harness import failures across test suite. | Python Import Audit: `scripts/backend_audit_loop.py` verifies zero broken imports during test suite startup. |
| **`@[backend_v2/models/dtos/__init__.py]`** | Banned obsolete DTO exports in package root. | Update `__all__` in `backend_v2/models/dtos/__init__.py` to replace `flat_record` with `export`. | Pruned dead package re-export; guarantees clean module namespace. | Python Import Audit: `scripts/backend_audit_loop.py` verifies zero broken imports. |
| **`@[backend_v2/services/localization.py#L114-L377]`** | Banned raw string key construction (`f"matrix_col_{col}"`) and scattered dictionary lookups across services. | Mandatory `ReportHeaderResolver` resolving localized headers for `ReportMatrixColumn`, `ReportAtomColumn`, and `ReportSheetKey` via `LocalizationService.translate()`. | Pruned dynamic formatters; resolver methods take typed enums directly with zero reflection. | Pytest: `test_report_headers_l10n_parity.py` verifies identical strings returned for matching column concepts. |
| **`@[backend_v2/l10n/fi.json#L71-L83]` & `@[backend_v2/l10n/en.json#L71-L83]`** | Banned in-code shadow dictionaries (`_EXCEL_KEYS`) and un-localized export strings. | Mandatory centralized SSOT export keys declared in both `fi.json` and `en.json` with 100% key parity, plus metadata_date key. | Pruned duplicate keys; existing `matrix_col_*` reused for matrix columns, `export_col_*` declared for atoms. | Parity test: `test_report_headers_l10n_parity.py` asserts zero orphan keys across both languages. |
| **`@[client_app_v2/lib/l10n/app_fi.arb#L1308-L1396]` & `@[client_app_v2/lib/l10n/app_en.arb#L1983-L2068]`** | Banned terminological divergence between Quorum Studio configuration chips and resulting report/export headers. | Synchronize all 9 `studioMatrixCol*` keys in `app_fi.arb` and `app_en.arb` to match `backend_v2/l10n/fi.json` and `en.json` 1:1; strip legacy technical suffixes from `meta*` keys (lines 1308-1314 / 1983-1989); synchronize `xai*` keys (lines 980-992 / 1524-1536) to match `xai_ext_*` SSOT headers, regenerating localizations via `flutter gen-l10n`. | Pruned separate UI terminology mappings; exact 1:1 string equality eliminates cognitive dissonance. | Pytest: `test_report_headers_l10n_parity.py` validates 100% bidirectional parity between Flutter `.arb` studio keys and Backend `.json` matrix column keys, metadata fields, and XAI extension labels. |
| **`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart#L10-L93]`** | Banned rendering raw un-localized variable names (`date`, `organization`, `user`, `scoring_engine`, `strictness`, `cost`, `tokens`) in Quorum Studio UI chips via `Text(field)`. | Implement `getFieldLabel(BuildContext context, String field)` helper mapping each field to its clean localized label from `AppLocalizations` (`metaDate`, `metaOrganization`, `metaUser`, `metaScoringEngine`, `metaStrictness`, `metaCost`, `metaTokens`). | Pruned ad-hoc string formatting; clean switch statement encapsulates 1:1 mapping. | Flutter Test: widget test verifies all 7 FilterChip widgets render localized display labels matching AppLocalizations without raw keys. |
| **`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L12-L285]`** | Banned hardcoded English locale resolution (`group.title.translations['en']`, `block.label.translations['en'] ?? block.slug`), falling back to machine slug, and leaking raw database IDs (`${block.id}`) into FilterChip labels. | Resolve group title and block title dynamically using current locale via `group.title.get(localeCode, fallback: 'en')` and `block.label.get(localeCode, fallback: 'en')` with zero slug fallback, and render clean title in FilterChip label with tooltip for block identifier. | Pruned hardcoded locale assumptions and slug fallbacks; dynamic resolution guarantees native multi-language rendering. | Flutter Test: widget test asserts localized group title and block name are displayed in Finnish without raw UUID suffix or machine slug. |
| **`@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L62-L78]`** | Banned falling back to machine identifier `bp.slug` when displaying blueprint step label (`label.isNotEmpty ? label : bp.slug`). | Remove `: bp.slug` fallback in `getBlueprintLabel(String stepId)`; return `label` directly per Invariant 10 Zero-Slug-Fallback Law. | Pruned defensive fallback chain; enforces valid human-readable `I18nText` labels across all workflow steps. | Flutter Test: widget test verifies step card displays clean localized label without falling back to machine slug. |
| **`@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py#L51-L101]`** | Banned raw string lists for standard matrix columns and manual string concatenation for column translation keys. | Mandatory binding of `STANDARD_COLUMNS` to `ReportMatrixColumn` members and resolution of `col_labels` via `ReportHeaderResolver`. | Pruned duplicate list definitions; `STANDARD_COLUMNS = [c.value for c in ReportMatrixColumn]` guarantees SSOT consistency. | Pytest: `test_matrix_summary_table_adapter.py` asserts all 9 standard columns resolve valid I18nText labels. |
| **`@[backend_v2/services/export_service.py#L55-L74]` (Cleanups)** | Banned shadow tuples (`_EXCEL_KEYS`), dead functions (`_extract_claim_rule`), and empty placeholder columns (`excelHeaderAiRule`). | Completely delete `_EXCEL_KEYS`, `_EXCEL_HEADERS_FI`, `_EXCEL_HEADERS_EN`, and `_extract_claim_rule()`; delegate all headers to `ReportHeaderResolver`. | Pruned 42 lines of dead code and shadow state; zero local translation dictionaries remain. | AST Guardrail: `scripts/backend_audit_loop.py` verifies absence of dead constants and clean imports. |
| **`@[backend_v2/services/export_service.py#L77-L317]` (Tab 1 Projection)** | Banned 3-column hardcoded summary tables and coupling analytical spreadsheet exports to presentation UI visibility filters. | Unconditionally project all 9 `ReportMatrixColumn` members onto Excel Tab 1 using typed `ExportMatrixSummaryRowDTO` instances with localized headers via `ReportHeaderResolver.get_matrix_column_header()`, returning `ExportPayloadDTO`. | Pruned redundant filtering loops; Tab 1 directly iterates through `ReportMatrixColumn` members. | Pytest: `test_export_excel_tab1_ssot_localization` asserts exactly 9 columns match `ReportMatrixColumn` headers in fi and en. |
| **`@[backend_v2/services/export_service.py#L77-L317]` (Tab 2 Atoms)** | Banned defensive fallbacks (populating empty placeholders on missing matrix) and non-binary status strings. | Build complete rectangular atom dataset with 9 `ReportAtomColumn` members, strictly binary status (`1` or `0`), and typed `ExportForensicAtomDTO` instances with Fail-Fast `AppException(404)` on missing matrix. | Shared `_build_atom_rows()` builder reused by both Tab 2 and CSV export, eradicating duplicate iteration logic. | Pytest: `test_export_excel_tab2_ssot_localization` verifies 9 columns, binary status, and Fail-Fast on missing matrix. |
| **`@[backend_v2/services/export_service.py#L77-L317]` (CSV Streaming)** | Banned legacy single-row machine vectors and untyped flat dictionaries in CSV exports. | Refactored `export_flat_csv()` to output multi-row tabular dataset streaming `ExportForensicAtomDTO` instances matching Tab 2 with `ReportAtomColumn` headers in UTF-8-SIG encoding, returning `ExportPayloadDTO`. | Pruned `FlatFileService` dependency from export pipeline; CSV reuses `_build_atom_rows()` directly. | Pytest: `test_export_flat_csv_tabular_multi_row` asserts multi-row structure and UTF-8-SIG encoding. |
| **`@[backend_v2/services/report_service.py#L299-L458]`** | Banned parameter omissions, anonymous tuple unpacking (`excel_bytes, _ = ...`), and inconsistent context between Excel and CSV generation. | Consume `ExportPayloadDTO` directly from `export_excel()` and `export_flat_csv()`, saving `payload.content_bytes` and passing `matrices=transformer.last_evaluative_matrices` and `locale=report.locale` identically. | Pruned intermediate state mapping and tuple unpacking; direct save of `payload.content_bytes`. | Pytest: `backend_v2/tests/unit/services/test_report_service.py` executes full pipeline without parameter errors. |
| **`@[backend_v2/tests/unit/services/test_report_service.py#L227-L260]`**, **`@[backend_v2/tests/unit/services/test_report_service.py#L485-L522]`**, **`@[backend_v2/tests/unit/services/test_report_service.py#L648-L690]`**, **`@[backend_v2/tests/unit/services/test_report_service.py#L693-L753]`**, **`@[backend_v2/tests/unit/services/test_report_service.py#L756-L811]` & `@[backend_v2/tests/unit/services/test_report_service_synthesis_args.py#L26-L109]`** | Banned stale mock return tuples (`(b"excel_bytes", "report.xlsx")`) causing tuple attribute crashes in test suites. | Update mock return values across all 5 test functions in report service unit tests and synthesis args tests to return typed `ExportPayloadDTO` instances. | Pruned obsolete 2-tuple return values in mock configurations. | Pytest: `test_report_service.py` and `test_report_service_synthesis_args.py` pass 100% green. |
| **`@[backend_v2/tests/unit/services/test_export_service.py#L111-L153]`**, **`@[backend_v2/tests/unit/services/test_export_service.py#L156-L183]`**, **`@[backend_v2/tests/unit/services/test_export_service.py#L186-L215]`**, **`@[backend_v2/tests/unit/services/test_export_service.py#L283-L297]`**, **`@[backend_v2/tests/unit/services/test_export_service.py#L300-L358]`**, **`@[backend_v2/tests/unit/services/test_export_service.py#L361-L478]`**, **`@[backend_v2/tests/unit/services/test_export_service.py#L481-L493]`**, **`@[backend_v2/tests/unit/services/test_export_service.py#L515-L593]`**, **`@[backend_v2/tests/unit/services/test_export_service.py#L596-L659]`**, **`@[backend_v2/tests/unit/services/test_export_service.py#L662-L737]` & `@[backend_v2/tests/unit/services/test_export_service.py#L740-L781]`** | Banned broken test imports, dead helper tests, obsolete column assertions (`"Kriteeri (UI)"`), and anonymous 2-tuple return unpacking in test cases. | Delete `_extract_claim_rule` import and `test_extract_claim_rule`; update all column assertions to match `ReportAtomColumn` and `ReportMatrixColumn` SSOT keys; update all 9 tests calling `export_excel` or `export_flat_csv` to consume typed `ExportPayloadDTO` (`payload.content_bytes`, `payload.filename`). | Pruned 44 lines of dead test code; modernized all test fixtures to assert rectangular tabular records with zero tuple unpacking. | Quality Gate: `uv run pytest backend_v2/tests/unit/services/test_export_service.py` passes 100% green. |
| **`@[backend_v2/tests/unit/test_report_headers_l10n_parity.py]` [NEW]** | Banned unchecked translation key drift, synthetic row generation, and ad-hoc column injection. | Dedicated test file mathematically asserting: (1) 100% bidirectional key parity for `ReportMatrixColumn`, `ReportAtomColumn`, and `ReportSheetKey`; (2) 100% parity between Flutter `.arb` Studio configuration keys and Backend `.json` matrix column keys; (3) Mathematical Dumb Painter Invariance: Excel Tab 1 row count equals `len(matrices)` and columns equal `ReportMatrixColumn`; Tab 2 and CSV row count equals `len(report_dto.results)` and columns equal `ReportAtomColumn`; (4) Strict Pydantic V2 rejection: attempting to instantiate `ExportForensicAtomDTO` or `ExportMatrixSummaryRowDTO` with any undeclared field raises `ValidationError`. | Pure zero-mock unit test; reads JSON and ARB files directly from disk without database dependencies. | CI Completion Gate: Automated audit gate in `backend_audit_loop.py` executes parity test asserting exact mathematical cardinality (`len(output_rows) == len(input_entities)`). |

---

## 5. Execution Protocol

```xml
<execution_protocol>
  <phase id="1" name="Centralized Typed Headers and SSOT Multilingual Keys">
    <step id="1.1" name="Define Typed Report Column Enums, DTOs, and Header Resolver">
      <description>Declare ReportMatrixColumn, ReportAtomColumn, and ReportSheetKey in enums.py, implement ExportForensicAtomDTO, ExportMatrixSummaryRowDTO, and ExportPayloadDTO in export.py, and implement ReportHeaderResolver in localization.py.</description>
      <target>@[backend_v2/models/enums.py#L893-L897]</target>
      <target>@[backend_v2/models/dtos/export.py] [NEW]</target>
      <target>@[backend_v2/services/localization.py#L114-L377]</target>
      <action>
        Add ReportMatrixColumn StrEnum to `backend_v2/models/enums.py` with members:
        - LABEL = "label" (l10n_key = "matrix_col_label")
        - CONTEXT_TARGET = "context_target" (l10n_key = "matrix_col_context_target")
        - DISTRIBUTION = "distribution" (l10n_key = "matrix_col_distribution")
        - ROW_EXPLANATION = "row_explanation" (l10n_key = "matrix_col_row_explanation")
        - CRITERIA = "criteria" (l10n_key = "matrix_col_criteria")
        - QUOTES = "quotes" (l10n_key = "matrix_col_quotes")
        - SOURCE = "source" (l10n_key = "matrix_col_source")
        - NORMALIZED_SCORE = "normalized_score" (l10n_key = "matrix_col_normalized_score")
        - SCORE = "score" (l10n_key = "matrix_col_score")
        Add ReportAtomColumn StrEnum to `backend_v2/models/enums.py` with members:
        - MATRIX = "matrix" (l10n_key = "export_col_matrix")
        - CONTEXT_TARGET = "context_target" (l10n_key = "export_col_context_target")
        - LEVEL = "level" (l10n_key = "export_col_level")
        - LEVEL_NAME = "level_name" (l10n_key = "export_col_level_name")
        - CRITERION = "criterion" (l10n_key = "export_col_criterion")
        - CLAIM_TYPE = "claim_type" (l10n_key = "export_col_claim_type")
        - RESULT_STATUS = "result_status" (l10n_key = "export_col_result_status")
        - QUOTES = "quotes" (l10n_key = "export_col_quotes")
        - AI_REASONING = "ai_reasoning" (l10n_key = "export_col_ai_reasoning")
        Add ReportSheetKey StrEnum to `backend_v2/models/enums.py` with members:
        - SUMMARY = "summary" (l10n_key = "export_sheet_summary")
        - RAW_DATA = "raw_data" (l10n_key = "export_sheet_raw_data")
        Export all three enums in __all__ in `backend_v2/models/enums.py`.
        Create `backend_v2/models/dtos/export.py` defining:
        - ExportForensicAtomDTO(V2CoreBase) with strict frozen ConfigDict(strict=True, extra="forbid", frozen=True), fields matching all 9 ReportAtomColumn members: matrix_label: str, context_target: str, level: int, level_name: str, criterion: str, claim_type: str, result_status: int (strictly binary integer 1 or 0), quotes: str, ai_reasoning: str.
        - ExportMatrixSummaryRowDTO(V2CoreBase) with strict frozen ConfigDict(strict=True, extra="forbid", frozen=True), fields matching all 9 ReportMatrixColumn members: label: str, context_target: str, distribution: str, row_explanation: str, criteria: str, quotes: str, source: str, normalized_score: float | str, score: float | str.
        - ExportPayloadDTO(V2CoreBase) with strict frozen ConfigDict(strict=True, extra="forbid", frozen=True), fields: content_bytes: bytes, filename: str, mime_type: str.
        Implement ReportHeaderResolver in `backend_v2/services/localization.py` providing typed helper methods:
        - get_matrix_column_header(col: ReportMatrixColumn, locale: str = "en") -> str
        - get_atom_column_header(col: ReportAtomColumn, locale: str = "en") -> str
        - get_all_matrix_headers(locale: str = "en") -> dict[ReportMatrixColumn, str]
        - get_all_atom_headers(locale: str = "en") -> list[str]
        - get_sheet_name(sheet: ReportSheetKey, locale: str = "en") -> str
        Export ReportHeaderResolver in __all__ in `backend_v2/services/localization.py`.
      </action>
      <constraint invariant="zero_string_literals">All report and export column lookups must be typed through ReportMatrixColumn and ReportAtomColumn enums, and row items must be encapsulated in ExportForensicAtomDTO, ExportMatrixSummaryRowDTO, and ExportPayloadDTO.</constraint>
    </step>

    <step id="1.2" name="Centralize Export Localization Keys in SSOT L10n Files and Synchronize Studio ARB Labels">
      <description>Declare canonical export column, sheet, and claim type keys in backend_v2/l10n JSON files, and synchronize client_app_v2/lib/l10n ARB files for 100% Studio UI parity across matrix columns, metadata fields, and XAI extensions.</description>
      <target>@[backend_v2/l10n/fi.json#L71-L83]</target>
      <target>@[backend_v2/l10n/en.json#L71-L83]</target>
      <target>@[client_app_v2/lib/l10n/app_fi.arb#L1308-L1396]</target>
      <target>@[client_app_v2/lib/l10n/app_en.arb#L1983-L2068]</target>
      <action>
        Append canonical export keys and metadata_date to `backend_v2/l10n/fi.json` and `backend_v2/l10n/en.json`:
        - "export_col_matrix": "Matriisi" / "Matrix"
        - "export_col_context_target": "Arvioinnin kohde" / "Evaluation Target"
        - "export_col_level": "Taso" / "Level"
        - "export_col_level_name": "Tason nimi" / "Level Name"
        - "export_col_criterion": "Arviointikriteeri" / "Evaluation Criterion"
        - "export_col_claim_type": "Väitetyyppi" / "Claim Type"
        - "export_col_result_status": "Tulos (Status)" / "Result (Status)"
        - "export_col_quotes": "Tekstin havainto" / "Text Observation"
        - "export_col_ai_reasoning": "AI-perustelu" / "AI Reasoning"
        - "export_sheet_summary": "Yhteenveto" / "Summary"
        - "export_sheet_raw_data": "Raakadata" / "Raw Data"
        - "export_claim_positive": "Positiivinen kyvykkyys" / "Positive Competence"
        - "export_claim_inverse": "Virhedetektori / Anti-pattern" / "Error Detector / Anti-pattern"
        - "metadata_date": "Päivämäärä" / "Date"
        Synchronize Flutter Studio Output Profile labels in `client_app_v2/lib/l10n/app_fi.arb`:
        - Matrix Columns: "studioMatrixColLabel": "Logiikkamatriisi", "studioMatrixColContextTarget": "Arvioinnin kohde", "studioMatrixColDistribution": "Jakauma", "studioMatrixColRowExplanation": "Selitys", "studioMatrixColCriteria": "Kriteeri", "studioMatrixColQuotes": "Tekstin havainto", "studioMatrixColSource": "Lähdeviite", "studioMatrixColNormalized": "Normalisoitu pisteytys", "studioMatrixColScore": "Pisteet"
        - Metadata Fields: "metaDate": "Päivämäärä", "metaOrganization": "Organisaatio", "metaUser": "Käyttäjä", "metaScoringEngine": "Arviointimoottori", "metaStrictness": "Tiukkuusaste", "metaCost": "Kustannukset", "metaTokens": "Tokenit"
        - XAI Extension Labels: "xaiJustification": "Perustelu", "xaiCoachingTip": "Valmennus", "xaiDevilsAdvocate": "Falsifikaatio", "xaiMissingContext": "Puuttuva konteksti", "xaiRiskFlag": "Riskilippu", "xaiRemediation": "Korjaustoimenpiteet", "xaiSentiment": "Emotionaalinen sävy", "xaiTheoryLink": "Teorialinkitys", "xaiConfidence": "Luottamus", "xaiSourceCitation": "Sitaatti", "xaiContextualOverride": "Kontekstuaalinen yliajo", "xaiSourceId": "Lähdetunniste"
        Synchronize Flutter Studio Output Profile labels in `client_app_v2/lib/l10n/app_en.arb`:
        - Matrix Columns: "studioMatrixColLabel": "Logic Matrix", "studioMatrixColContextTarget": "Evaluation Target", "studioMatrixColDistribution": "Distribution", "studioMatrixColRowExplanation": "Explanation", "studioMatrixColCriteria": "Criteria", "studioMatrixColQuotes": "Text Observation", "studioMatrixColSource": "Source Citation", "studioMatrixColNormalized": "Normalized Score", "studioMatrixColScore": "Score"
        - Metadata Fields: "metaDate": "Date", "metaOrganization": "Organization", "metaUser": "User", "metaScoringEngine": "Scoring Engine", "metaStrictness": "Strictness", "metaCost": "Cost", "metaTokens": "Tokens"
        - XAI Extension Labels: "xaiJustification": "Justification", "xaiCoachingTip": "Coaching", "xaiDevilsAdvocate": "Falsification", "xaiMissingContext": "Missing Context", "xaiRiskFlag": "Risk Flag", "xaiRemediation": "Remediation Steps", "xaiSentiment": "Emotional Sentiment", "xaiTheoryLink": "Theory Link", "xaiConfidence": "Confidence", "xaiSourceCitation": "Citation", "xaiContextualOverride": "Contextual Override", "xaiSourceId": "Source ID"
      </action>
      <constraint invariant="multilingual_ssot">All user-visible export and studio configuration labels must be declared with 100% key and semantic parity across fi.json, en.json, app_fi.arb, and app_en.arb.</constraint>
    </step>

    <step id="1.3" name="Update Flutter Studio Output Settings Cards for SSOT Parity">
      <description>Refactor MetadataBlockCard to resolve localized field labels via getFieldLabel, refactor MatrixGraphItemEditor to use dynamic locale resolution and clean chip labels with zero slug fallback, and eradicate slug fallback in WorkflowStepCard.</description>
      <target>@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart#L10-L93]</target>
      <target>@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L12-L285]</target>
      <target>@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L62-L78]</target>
      <action>
        In `client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart`:
        - Add static `getFieldLabel(BuildContext context, String field) -> String` mapping 'date' -> l10n.metaDate, 'organization' -> l10n.metaOrganization, 'user' -> l10n.metaUser, 'scoring_engine' -> l10n.metaScoringEngine, 'strictness' -> l10n.metaStrictness, 'cost' -> l10n.metaCost, 'tokens' -> l10n.metaTokens.
        - Replace `label: Text(field)` with `label: Text(getFieldLabel(context, field))` on FilterChip line 73.
        In `client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart`:
        - In line 78, replace hardcoded English lookup `group.title.translations['en'] ?? group.title.translations.values.firstOrNull ?? 'Group ${index + 1}'` with dynamic locale resolution `group.title.get(Localizations.localeOf(context).languageCode, fallback: 'en')` so the ExpansionTile title renders the user's custom chart title in the active UI locale without guessing.
        - Replace line 246 `final label = block.label.translations['en'] ?? block.slug;` with dynamic locale resolution `final localeCode = Localizations.localeOf(context).languageCode; final label = block.label.get(localeCode, fallback: 'en');`, completely eradicating the `block.slug` fallback per Invariant 10 Zero-Slug-Fallback Law.
        - Replace line 272 `label: Text('$label (${block.id})')` with `label: Text(label)` and `tooltip: block.id`.
        In `client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart`:
        - In `getBlueprintLabel(String stepId)` line 75, eradicate `: bp.slug` fallback, returning `label` directly per Invariant 10 Zero-Slug-Fallback Law.
      </action>
      <constraint invariant="clean_studio_ux">No raw database IDs, technical variable keys, or machine slug fallbacks displayed to users in Quorum Studio configuration cards.</constraint>
    </step>

    <step id="1.4" name="Eradicate Shadow Localization Tuples and Dead Helper">
      <description>Remove shadow _EXCEL_KEYS tuple and dead _extract_claim_rule function from export_service.py, and remove dead import and test from test_export_service.py.</description>
      <target>@[backend_v2/services/export_service.py#L55-L74]</target>
      <target>@[backend_v2/tests/unit/services/test_export_service.py#L111-L153]</target>
      <action>
        Delete _extract_claim_rule() from `backend_v2/services/export_service.py`.
        Delete _EXCEL_KEYS, _EXCEL_HEADERS_FI, and _EXCEL_HEADERS_EN from `backend_v2/services/export_service.py`.
        Import ReportHeaderResolver, ReportMatrixColumn, ReportAtomColumn, and ReportSheetKey in `backend_v2/services/export_service.py`.
        Delete _extract_claim_rule from imports in `backend_v2/tests/unit/services/test_export_service.py`.
        Delete test_extract_claim_rule() test case from `backend_v2/tests/unit/services/test_export_service.py`.
      </action>
      <constraint invariant="zero_shadow_dictionaries">No shadow localization mappings allowed in Python services.</constraint>
    </step>
  </phase>

  <phase id="2" name="Excel Tab 1 Complete Standard Matrix Summary Parity">
    <step id="2.1" name="Implement Full Standard Column Projection on Tab 1">
      <description>Project MatrixScorecardRowDTO instances to Tab 1 using all 9 members of ReportMatrixColumn encapsulated in ExportMatrixSummaryRowDTO with ReportHeaderResolver.</description>
      <target>@[backend_v2/services/export_service.py#L77-L317]</target>
      <action>
        Populate Tab 1 rows in `backend_v2/services/export_service.py` directly from matrices: list[MatrixScorecardRowDTO] using localized sheet name ReportHeaderResolver.get_sheet_name(ReportSheetKey.SUMMARY, locale).
        Tab 1 unconditionally exports all 9 ReportMatrixColumn members regardless of UI visibility settings.
        Ensure exact 1:1 Dumb Painter projection: Tab 1 row count equals len(matrices) with zero synthetic, phantom, or invented rows.
        Encapsulate each row as a validated ExportMatrixSummaryRowDTO instance before serializing to DataFrame:
        - ReportMatrixColumn.LABEL: m.label_i18n.resolve(target_locale=locale) or m.name
        - ReportMatrixColumn.CONTEXT_TARGET: m.context_target_label.resolve(target_locale=locale) if m.context_target_label else (m.context_target or "")
        - ReportMatrixColumn.DISTRIBUTION: ", ".join(f"{lvl}: {val}" for lvl, val in m.level_breakdown.items()) if m.level_breakdown else ""
        - ReportMatrixColumn.ROW_EXPLANATION: m.row_explanation or ""
        - ReportMatrixColumn.CRITERIA: f"{m.true_atoms or 0}/{m.total_atoms or 0}"
        - ReportMatrixColumn.QUOTES: m.cited_text_quote or ""
        - ReportMatrixColumn.SOURCE: m.cited_source_title or m.cited_source_id or ""
        - ReportMatrixColumn.NORMALIZED_SCORE: m.normalized_score if m.normalized_score is not None else ""
        - ReportMatrixColumn.SCORE: f"{m.score} / {m.scale_max}" if m.score is not None and m.scale_max is not None else (m.score if m.score is not None else "")
        Return ExportPayloadDTO(content_bytes=output.getvalue(), filename=f"execution_export_{target_id}.xlsx", mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet").
      </action>
      <constraint invariant="analytical_export_completeness">Tab 1 must always export all 9 standard columns for full analytical completeness, decoupling analytical spreadsheet export from presentation UI/PDF visibility filters.</constraint>
    </step>

    <step id="2.2" name="Wire MatrixSummaryTableAdapter to Typed ReportMatrixColumn">
      <description>Refactor MatrixSummaryTableAdapter to resolve column labels via ReportHeaderResolver.</description>
      <target>@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py#L51-L101]</target>
      <action>
        Update `backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py` to declare STANDARD_COLUMNS = [c.value for c in ReportMatrixColumn].
        Populate col_labels mapping each visible column to I18nText using ReportHeaderResolver.get_matrix_column_header for "fi" and "en":
        col_labels[col] = I18nText(
            translations={
                "fi": ReportHeaderResolver.get_matrix_column_header(ReportMatrixColumn(col), "fi"),
                "en": ReportHeaderResolver.get_matrix_column_header(ReportMatrixColumn(col), "en"),
            }
        )
      </action>
      <constraint invariant="typed_adapter_resolution">MatrixSummaryTableAdapter must consume typed ReportMatrixColumn members.</constraint>
    </step>
  </phase>

  <phase id="3" name="Excel Tab 2 Forensic Atom Table Optimization">
    <step id="3.1" name="Build Complete Rectangular Atom Dataset on Tab 2">
      <description>Construct tabular raw data rows containing complete atom details with binary results using ReportAtomColumn headers and ExportForensicAtomDTO instances via shared _build_atom_rows().</description>
      <target>@[backend_v2/services/export_service.py#L77-L317]</target>
      <action>
        Implement _build_atom_rows(self, report_dto, matrices, locale, blocks_by_id, matrix_title_lookup) -> list[ExportForensicAtomDTO] helper method on ExportService in `backend_v2/services/export_service.py`.
        Build atom_meta_lookup from matrices: list[MatrixScorecardRowDTO] mapping each atom_id to its parent matrix row and ScorecardAtomDTO.
        Ensure exact 1:1 Dumb Painter projection: Tab 2 row count equals len(report_dto.results) with zero synthetic, phantom, or extrapolated rows.
        Iterate over report_dto.results to construct ExportForensicAtomDTO instances with deterministic fields:
        1. ReportAtomColumn.MATRIX: parent matrix localized label. If matrix_id cannot be found in matrices or blocks_by_id, raise AppException(404, ErrorCodes.RESOURCE_NOT_FOUND).
        2. ReportAtomColumn.CONTEXT_TARGET: context_target_label or context_target.
        3. ReportAtomColumn.LEVEL: s_atom.level integer if found else 0.
        4. ReportAtomColumn.LEVEL_NAME: s_atom.level_name string if found else "".
        5. ReportAtomColumn.CRITERION: ref.resolved_claim or (s_atom.claim_label if s_atom else "").
        6. ReportAtomColumn.CLAIM_TYPE: LocalizationService.translate("export_claim_inverse", locale) if is_inverse else LocalizationService.translate("export_claim_positive", locale).
        7. ReportAtomColumn.RESULT_STATUS: 1 if atom.status == ExecutionStatus.PASSED else 0 (strictly binary integer).
        8. ReportAtomColumn.QUOTES: exact quote string or empty string.
        9. ReportAtomColumn.AI_REASONING: evaluation reasoning string or empty string.
        Write sheet with localized sheet name ReportHeaderResolver.get_sheet_name(ReportSheetKey.RAW_DATA, locale).
      </action>
      <constraint invariant="binary_status_guarantee">Result status must always be integer 1 or 0.</constraint>
    </step>
  </phase>

  <phase id="4" name="CSV Tabular Atom Export Parity">
    <step id="4.1" name="Implement Tabular Raw Data CSV Streaming with SSOT Headers">
      <description>Refactor export_flat_csv to output the complete raw atom table in CSV format using ReportAtomColumn headers, ExportForensicAtomDTO instances, and UTF-8-SIG encoding, returning ExportPayloadDTO.</description>
      <target>@[backend_v2/services/export_service.py#L77-L317]</target>
      <action>
        Update export_flat_csv signature in `backend_v2/services/export_service.py` to accept matrices: list[MatrixScorecardRowDTO] | None = None, locale: str = "fi", and execution_id: str | None = None, returning ExportPayloadDTO.
        Reuse _build_atom_rows() to obtain list[ExportForensicAtomDTO] with identical ReportAtomColumn headers.
        Ensure exact 1:1 Dumb Painter projection: CSV row count equals len(report_dto.results) with zero synthetic, phantom, or extrapolated rows.
        Serialize rows using csv.writer directly from DTO values without raw dictionary accumulators.
        Encode output in utf-8-sig to ensure Excel on Windows correctly displays Scandinavian characters without encoding dialogs.
        Return ExportPayloadDTO(content_bytes=output.getvalue().encode("utf-8-sig"), filename=f"execution_export_{target_id}.csv", mime_type="text/csv").
      </action>
      <constraint invariant="csv_atom_parity">CSV output must be a multi-row rectangular table identical to Tab 2, returning an ExportPayloadDTO.</constraint>
    </step>

    <step id="4.2" name="Eradicate FlatFileService and FlatExecutionRecordDTO">
      <description>Delete obsolete single-row flattener service and naked-dictionary DTO.</description>
      <target>@[backend_v2/services/flattener.py] [DELETE]</target>
      <target>@[backend_v2/models/dtos/flat_record.py] [DELETE]</target>
      <target>@[backend_v2/tests/conftest.py]</target>
      <target>@[backend_v2/models/dtos/__init__.py]</target>
      <action>
        Delete `backend_v2/services/flattener.py`.
        Delete `backend_v2/models/dtos/flat_record.py`.
        Delete obsolete tests `backend_v2/tests/unit/test_flattener.py` and `backend_v2/tests/unit/models/dtos/test_flat_record.py`.
        Update `backend_v2/tests/conftest.py` early import line 13 to import `from backend_v2.models.dtos.export import ExportPayloadDTO as _ExportPayloadDTO; _ = _ExportPayloadDTO`.
        Update `backend_v2/models/dtos/__init__.py` to replace "flat_record" with "export" in __all__.
      </action>
      <constraint invariant="zero_naked_dicts">Eradicate all unannotated dictionary mutation accumulators and obsolete single-row flattener services.</constraint>
    </step>
  </phase>

  <phase id="5" name="ReportService Wiring and Storage Integration">
    <step id="5.1" name="Update ReportService Calls for CSV Generation and Payload Consumption">
      <description>Consume ExportPayloadDTO directly in ReportService and pass matrices and locale into export_flat_csv.</description>
      <target>@[backend_v2/services/report_service.py#L299-L458]</target>
      <target>@[backend_v2/tests/unit/services/test_report_service.py#L227-L260]</target>
      <target>@[backend_v2/tests/unit/services/test_report_service.py#L485-L522]</target>
      <target>@[backend_v2/tests/unit/services/test_report_service.py#L648-L690]</target>
      <target>@[backend_v2/tests/unit/services/test_report_service.py#L693-L753]</target>
      <target>@[backend_v2/tests/unit/services/test_report_service.py#L756-L811]</target>
      <target>@[backend_v2/tests/unit/services/test_report_service_synthesis_args.py#L26-L109]</target>
      <action>
        Update self.export_service.export_excel and export_flat_csv calls in generate_report_artifacts inside `backend_v2/services/report_service.py` to consume ExportPayloadDTO directly:
        - excel_payload = await self.export_service.export_excel(execution=execution, report_dto=report_dto, matrices=transformer.last_evaluative_matrices, locale=report.locale, execution_id=report.execution_id)
        - await self.storage.save(excel_path, excel_payload.content_bytes)
        - csv_payload = self.export_service.export_flat_csv(execution=execution, report_dto=report_dto, matrices=transformer.last_evaluative_matrices, locale=report.locale, execution_id=report.execution_id)
        - await self.storage.save(csv_path, csv_payload.content_bytes)
        Eradicate all anonymous tuple unpacking across export invocation points.
        Update test mocks across all 5 test functions in `backend_v2/tests/unit/services/test_report_service.py` (lines 237-239, 497-499, 661-663, 706-708, and 772-774) and in `backend_v2/tests/unit/services/test_report_service_synthesis_args.py` (lines 64-65) to return ExportPayloadDTO instead of 2-tuples for export_excel and export_flat_csv.
      </action>
      <constraint invariant="parameter_completeness">All export formats must receive identical execution and matrix context, returning strongly typed ExportPayloadDTO instances.</constraint>
    </step>
  </phase>

  <phase id="6" name="Unit Testing and Quality Gate Verification">
    <step id="6.1" name="Create Dedicated Report Header and Cross-Surface Parity Test">
      <description>Verify 100% key parity, absence of orphan keys, cross-platform Studio UI parity, mathematical Dumb Painter row/column invariance, and Pydantic extra='forbid' validation across Dumb Painter SDUI (DataGridBlock), Excel, CSV, and Flutter Studio ARB files with zero interim dictionaries.</description>
      <target>@[backend_v2/tests/unit/test_report_headers_l10n_parity.py] [NEW]</target>
      <action>
        Assert every member of ReportMatrixColumn has valid non-empty translations in both fi.json and en.json.
        Assert every member of ReportAtomColumn has valid non-empty translations in both fi.json and en.json.
        Assert every member of ReportSheetKey has valid non-empty translations in both fi.json and en.json.
        Assert Cross-Platform Studio UI Parity: Parse client_app_v2/lib/l10n/app_fi.arb and client_app_v2/lib/l10n/app_en.arb alongside backend_v2/l10n/fi.json and backend_v2/l10n/en.json, asserting that: (a) all 9 studioMatrixCol* labels match matrix_col_* SSOT headers 1:1; (b) all 7 meta* labels in MetadataBlockCard.availableMetadataFields match metadata_* / sduiMetadata* SSOT labels 1:1; (c) all 12 xai* extension labels match xai_ext_* SSOT labels 1:1.
        Assert Cross-Surface Parity: Verify that header strings resolved for Dumb Painter SDUI DataGridBlock match 1:1 with Excel columns and CSV headers via ReportHeaderResolver in both fi and en.
        Assert DTO Field Mapping Parity: Verify that ExportMatrixSummaryRowDTO and ExportForensicAtomDTO fields map directly to ReportMatrixColumn and ReportAtomColumn without interim dictionaries.
        Assert ReportHeaderResolver returns identical strings for matching column concepts across all output targets in `backend_v2/tests/unit/test_report_headers_l10n_parity.py`.
        Assert Mathematical Dumb Painter Invariance (Anti-Synthetic Row Gate): Verify that for any input matrices (length N) and report_dto.results (length M), Excel Tab 1 contains exactly N data rows with exactly 9 columns matching ReportMatrixColumn, Excel Tab 2 contains exactly M data rows with exactly 9 columns matching ReportAtomColumn, and CSV contains exactly M data rows with exactly 9 columns matching ReportAtomColumn (zero synthetic rows, zero phantom lines, zero omitted rows).
        Assert Pydantic Strict Extra Forbid Gate: Verify that attempting to instantiate ExportForensicAtomDTO, ExportMatrixSummaryRowDTO, or ExportPayloadDTO with any undeclared attribute raises ValidationError, preventing runtime synthetic attribute injection.
      </action>
      <constraint invariant="cross_surface_header_parity">All surfaces (Dumb Painter SDUI, Excel, CSV, Flutter Studio ARB) must use identical column headers and direct Pydantic DTO projections with zero dictionaries.</constraint>
    </step>

    <step id="6.2" name="Update and Expand ExportService Unit Tests for SSOT L10n">
      <description>Verify dynamic Tab 1 projection, Tab 2 atom columns, SSOT multilingual headers, multi-row CSV export, and exact mathematical row/column cardinality invariance.</description>
      <target>@[backend_v2/tests/unit/services/test_export_service.py#L156-L183]</target>
      <target>@[backend_v2/tests/unit/services/test_export_service.py#L186-L215]</target>
      <target>@[backend_v2/tests/unit/services/test_export_service.py#L283-L297]</target>
      <target>@[backend_v2/tests/unit/services/test_export_service.py#L300-L358]</target>
      <target>@[backend_v2/tests/unit/services/test_export_service.py#L361-L478]</target>
      <target>@[backend_v2/tests/unit/services/test_export_service.py#L481-L493]</target>
      <target>@[backend_v2/tests/unit/services/test_export_service.py#L515-L593]</target>
      <target>@[backend_v2/tests/unit/services/test_export_service.py#L596-L659]</target>
      <target>@[backend_v2/tests/unit/services/test_export_service.py#L662-L737]</target>
      <target>@[backend_v2/tests/unit/services/test_export_service.py#L740-L781]</target>
      <action>
        Add test_export_excel_tab1_ssot_localization asserting Tab 1 columns match ReportHeaderResolver in both fi and en in `backend_v2/tests/unit/services/test_export_service.py`.
        Add test_export_excel_tab2_ssot_localization asserting Tab 2 headers match ReportAtomColumn keys in fi and en, and result status is strictly 0 or 1 in `backend_v2/tests/unit/services/test_export_service.py`.
        Update test_export_flat_csv_success and test_export_flat_csv_default_execution_id to assert multi-row rectangular atom table with ReportAtomColumn headers and utf-8-sig encoding in `backend_v2/tests/unit/services/test_export_service.py`.
        Update test_export_excel_emits_exact_9_rows_summary_and_claim_classifications to assert new SSOT column headers (Arviointikriteeri instead of Kriteeri (UI)) in `backend_v2/tests/unit/services/test_export_service.py`.
        Modernize all callers in `backend_v2/tests/unit/services/test_export_service.py` (specifically: test_export_excel_success_fi, test_export_excel_success_en_with_prompt_block_repo, test_export_excel_with_report_dto_results_atoms, test_export_excel_with_all_extensions_and_blocks, test_export_excel_with_prompt_block_repo_resolves_matrix_names_and_inverse_claims_positive, and test_export_excel_with_failed_inverse_claim_emits_status_zero_negative) to consume typed ExportPayloadDTO (payload.content_bytes, payload.filename), eradicating anonymous 2-tuple unpacking.
        Assert Mathematical Cardinality Invariance in test_export_excel_emits_exact_9_rows_summary_and_claim_classifications: verify Tab 1 data row count == len(matrices) and Tab 2 data row count == len(report_dto.results).
        Assert Mathematical Cardinality Invariance in test_export_flat_csv_success: verify CSV line count minus 1 == len(report_dto.results).
        Verify test_export_excel_missing_matrix_in_repo_raises_fail_fast_negative passes asserting AppException(404, RESOURCE_NOT_FOUND) in `backend_v2/tests/unit/services/test_export_service.py`.
        Execute backend audit loop with strict AST guardrails.
      </action>
      <constraint invariant="audit_loop_pass">All tests must pass with zero ruff or mypy errors.</constraint>
    </step>
  </phase>
</execution_protocol>
```

---

## 6. Architectural Safeguards & Verification Plan

### 6.1 Verification Commands
1. **Iterative Local Testing:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/test_export_service.py backend_v2/tests/unit/test_report_headers_l10n_parity.py -v
   ```
2. **Backend Quality Gate:**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/services/export_service.py --test --ast-strict
   ```
3. **Full Backend Suite Gate:**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/test_report_service.py --test
   ```
4. **Mandatory Final E2E REST API Verification Gate:**
   ```powershell
   $env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
   ```

### 6.2 Anti-Happy-Path Test Scenarios
- **Scenario 1 (Unsupported Locale Fallback):** If an unknown locale code is passed (specifically 'de' or 'fr'), `LocalizationService` and `ReportHeaderResolver` must deterministically fall back to the default language ("en") without throwing exceptions or emitting untranslated keys.
- **Scenario 2 (OutputProfile visibility decoupled from export):** Even when an OutputProfile restricts visible columns for UI and PDF presentation, Excel Tab 1 still unconditionally includes all 9 members of `ReportMatrixColumn` without omissions.
- **Scenario 3 (Atoms with unresolvable matrix_id):** An atom whose `matrix_id` does not match any entry in `matrices` and cannot be resolved from the repository must trigger Fail-Fast `AppException(404, ErrorCodes.RESOURCE_NOT_FOUND)` with structured RFC 7807 logging, strictly forbidding silent default placeholders.
- **Scenario 4 (Special characters in quotes):** Quotes containing quotation marks, semicolons, and newlines must be escaped via RFC 4180 rules in the CSV output.
- **Scenario 5 (Anti-Synthetic Row Injection Gate):** If a rogue developer attempts to append ad-hoc synthetic rows (specifically: synthetic aggregations, heuristic summary rows, or un-evaluated atom placeholders) to Excel Tab 1, Excel Tab 2, or CSV, the mathematical cardinality assertions (`len(rows) == len(domain_inputs)`) in `test_report_headers_l10n_parity.py` and `test_export_service.py` fail fast with an assertion error. If any undeclared field is passed to `ExportForensicAtomDTO` or `ExportMatrixSummaryRowDTO`, Pydantic V2 raises `ValidationError(extra_forbidden)` immediately.
- **Scenario 6 (Studio UI ARB Parity Drift Gate):** If a developer alters a `studioMatrixCol*` string in `app_fi.arb` or `app_en.arb` without matching `backend_v2/l10n/fi.json` or `en.json`, `test_report_headers_l10n_parity.py` fails fast in CI, mathematically preventing terminological divergence between Studio UI configuration and report/export outputs.

---

## 7. Knowledge Items & Rules Synchronization Directives

### 7.1 Knowledge Items (KI) Updates
1. **`@[ki_dumb_painter_sdui.md]`:**
   - Document cross-surface Dumb Painter parity across SDUI (`DataGridBlock`), Excel (Tab 1 & Tab 2), and CSV tabular streaming.
   - Codify the strict Dumb Consumer invariant: all export and presentation surfaces receive pre-computed, immutable Pydantic V2 DTOs (`ExportMatrixSummaryRowDTO`, `ExportForensicAtomDTO`, `ExportPayloadDTO`) with zero local inference, zero mathematical calculation, and zero intermediary dictionary accumulators.
2. **`@[ki_dual_axis_localization_architecture.md]`:**
   - Register `ReportHeaderResolver` and typed Enums (`ReportMatrixColumn`, `ReportAtomColumn`, `ReportSheetKey`) as the Single Source of Truth (SSOT) for reporting, tabular export headers, and Flutter Studio configuration chips.
   - Document the eradication of in-code shadow translation dictionaries (`_EXCEL_KEYS`, `_EXCEL_HEADERS_FI`) and the 1:1 synchronization of Flutter `studioMatrixCol*` ARB keys with Backend `matrix_col_*` JSON keys.
3. **`@[ki_zero_permissive_typing.md]`:**
   - Codify the complete eradication of `FlatExecutionRecordDTO` and `FlatFileService`.
   - Document the ban on disguised naked dictionaries using wide scalar unions (`dict[str, str | float | int | bool | None]`).
   - Register the new immutable Pydantic V2 DTOs: `ExportForensicAtomDTO`, `ExportMatrixSummaryRowDTO`, and `ExportPayloadDTO` in `backend_v2/models/dtos/export.py`.

### 7.2 System Rules Updates (`.agents/rules/`)
1. **`@[.agents/rules/04_directory_reference.md]`:**
   - Register new module: `backend_v2/models/dtos/export.py` (`ExportPayloadDTO`, `ExportForensicAtomDTO`, `ExportMatrixSummaryRowDTO`).
   - Deregister deleted legacy modules: `backend_v2/services/flattener.py` and `backend_v2/models/dtos/flat_record.py`.
2. **`@[.agents/rules/01-python-backend.md]`:**
   - Ensure rules strictly mandate DTO-only payloads for all file export services (`ExportService`), explicitly banning dictionary mutation accumulators in CSV and Excel generators.
3. **`@[.agents/rules/02_flutter_desktop.md]`:**
   - Mandate 1:1 terminological parity between Flutter Studio configuration cards (`MatrixSummaryTableCard`) and Backend SSOT reporting headers.

---

## 8. Tier 7 Architectural Documentation Invocation

Upon completion of Phase 6 testing and quality gate verification, execute the following fully parameterized `/tier7-describe-architecture` command:

```powershell
/tier7-describe-architecture @[docs/implementationplans/TRACKER_Logic_Matrix_Excel_and_CSV_Parity_Architecture.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Logic_Matrix_Excel_and_CSV_Parity_Architecture.md] @[ki_dumb_painter_sdui.md] @[ki_dual_axis_localization_architecture.md] @[ki_zero_permissive_typing.md] @[ki_god_code_prevention.md]
```

### Directives for Tier 7 Agent:
1. **Target KIs to Synchronize:**
   - `ki_dumb_painter_sdui.md`: Update Dumb Painter architecture to include cross-surface spreadsheet, CSV raw tabular streaming, and Studio configuration parity.
   - `ki_dual_axis_localization_architecture.md`: Document `ReportHeaderResolver` and typed Enums (`ReportMatrixColumn`, `ReportAtomColumn`, `ReportSheetKey`) as SSOT across Flutter ARB and Backend JSON.
   - `ki_zero_permissive_typing.md`: Document eradication of `FlatExecutionRecordDTO` and introduction of `ExportPayloadDTO`, `ExportForensicAtomDTO`, `ExportMatrixSummaryRowDTO`.
   - `ki_god_code_prevention.md`: Codify the decomposition of export formatting from monolithic flattener dictionaries into typed, single-responsibility DTO streaming.
2. **Directory Reference Sync:**
   - Update `@[.agents/rules/04_directory_reference.md]` to register `backend_v2/models/dtos/export.py` and remove deleted `flattener.py` and `flat_record.py`.
3. **Pillar Documentation Sync (`docs/architecture/`):**
   - Seamlessly integrate the updated theoretical foundation into `docs/architecture/03_execution_telemetry_reporting.md` and `docs/architecture/04_sdui_frontend_presentation.md`.
   - Adhere strictly to the timeless present-tense mandate: describe purely, directly, and authoritatively what the system currently has and how it operates in present tense, with 0 project phases, 0 Epic IDs, 0 dates, 0 historical language, and 0 Law/Enforcement labels.
