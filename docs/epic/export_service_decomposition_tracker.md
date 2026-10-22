# ExportService Decomposition Tracker (Two-Epoch Strangler Fig Protocol)

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Overview
Decomposition of monolithic `@[backend_v2/services/export_service.py#L65-L589]` (590 lines, originally 1,124 lines, Archetype B: Presentation / Streaming / Formatter) into the cohesive domain package `backend_v2/services/export/` using the Two-Epoch Strangler Fig Protocol. Baseline test coverage: 95% (39 passing unit tests).

---

## Phase Execution Status

### Phase 1: Leaf Metadata Resolver & Excel Styler Extraction
**Plan:** @[docs/epic/tasks_export_service/phase1_leaf_and_styler_extraction.md]
- [x] **[OK] Execution:** /tier2-execute @[docs/epic/tasks_export_service/phase1_leaf_and_styler_extraction.md] @[docs/epic/export_service_decomposition_tracker.md]
  - [x] Step 1: Create Metadata Resolver Submodule
  - [x] Step 2: Create Excel Styler Submodule
  - [x] Step 3: Proxy Delegation in Export Service
  - [x] Step 4: Verify Quality Gates
- [x] **[OK] Audit:** uv run python scripts/backend_audit_loop.py backend_v2/services/export_service.py --test

### Phase 2: Tabular Row & Dataset Builders Extraction
**Plan:** @[docs/epic/tasks_export_service/phase2_row_builders_extraction.md]
- [x] **[OK] Execution:** /tier2-execute @[docs/epic/tasks_export_service/phase2_row_builders_extraction.md] @[docs/epic/export_service_decomposition_tracker.md]
  - [x] Step 1: Create Summary Builder Submodule
  - [x] Step 2: Create Atom Row Builder Submodule
  - [x] Step 3: Proxy Delegation in Export Service
  - [x] Step 4: Verify Quality Gates
- [x] **[OK] Audit:** uv run python scripts/backend_audit_loop.py backend_v2/services/export_service.py --test

### Phase 3: Excel & CSV Exporters Extraction
**Plan:** @[docs/epic/tasks_export_service/phase3_exporters_extraction.md]
- [x] **[OK] Execution:** /tier2-execute @[docs/epic/tasks_export_service/phase3_exporters_extraction.md] @[docs/epic/export_service_decomposition_tracker.md]
  - [x] Step 1: Create Excel Exporter Submodule
  - [x] Step 2: Create CSV Exporter Submodule
  - [x] Step 3: Proxy Delegation in Export Service
  - [x] Step 4: Verify Quality Gates
- [x] **[OK] Audit:** uv run python scripts/backend_audit_loop.py backend_v2/services/export_service.py --test

### Phase 4: Atomic Package Cutover & Guardrails Lockdown
**Plan:** @[docs/epic/tasks_export_service/phase4_package_cutover_and_guardrails.md]
- [x] (2a2a586c3) **[OK] Execution:** /tier2-execute @[docs/epic/tasks_export_service/phase4_package_cutover_and_guardrails.md] @[docs/epic/export_service_decomposition_tracker.md]
  - [x] Step 1: Consumer Import Rewiring
  - [x] Step 2: Modularize Test Suite
  - [x] Step 3: Atomic Package Cutover
  - [x] Step 4: Guardrail Lockdown and Smoke Test
- [x] **[OK] Audit:** uv run python scripts/backend_audit_loop.py backend_v2/services/export/ --test

---

### Post-Implementation Gates

#### Tier 2 Hardening (Backend)
- [ ] **[NOK] Tier 2 Hardening (Backend):** Post-cutover type and schema hardening on isolated sub-modules
  - [x] [NEW] @[backend_v2/services/export/metadata_resolver.py]
  - [x] [NEW] @[backend_v2/services/export/excel_styler.py]
  - [x] [NEW] @[backend_v2/services/export/summary_builder.py]
  - [x] [NEW] @[backend_v2/services/export/atom_row_builder.py]
  - [ ] [NEW] @[backend_v2/services/export/excel_exporter.py]
  - [ ] [NEW] @[backend_v2/services/export/csv_exporter.py]
  - [ ] [NEW] @[backend_v2/services/export/__init__.py]
  - [ ] @[backend_v2/services/report_service.py]
  - [ ] @[backend_v2/api/dependencies.py]

#### Tier 2 Hardening (Frontend)
- [x] **[SKIPPED] Tier 2 Hardening (Frontend):** No Flutter files modified in this backend decomposition.

#### Quality & Safety Gates
- [x] **[OK] Golden Master & Test Restoration Audit:** Characterization test baseline verified at 95% line coverage with 39 passing tests (expanded to 84 modularized tests across export package).
- [x] **[OK] Pre-Delete Audit:** Verified 0 remaining imports of `backend_v2.services.export_service` before deleting proxy file.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit:** Verified Excel styling, 13-column summary rows, 14-column atom rows, and 22-column CSV streams match 100% byte and schema parity.
- [ ] **[NOK] As-Built Architectural Sync:** Synchronize architecture docs via parameterized `/tier7-describe-architecture docs/epic/export_service_decomposition_tracker.md docs/epic/EPIC_EXPORT_DECOMPOSITION.md @[ki_god_code_prevention.md]`.

---

### Final Epic Audit
- [ ] **[NOK] Final Epic Audit:** /tier8-audit-epic docs/epic/export_service_decomposition_tracker.md

---

## Instructions for the Execution Agent
1. **Epoch 1 Strict Lift-and-Shift**: In Phase 1 through Phase 3, extract functions and methods verbatim with zero signature or behavior changes. Keep existing unit tests 100% green against `export_service.py` proxy.
2. **Atomic Cutover Protocol**: In Phase 4, atomically create `backend_v2/services/export/__init__.py`, delete `backend_v2/services/export_service.py`, and rewire 1-hop consumers in `report_service.py` and `dependencies.py` per `symbol_migration_map.md`.
3. **Epoch 2 Post-Cutover Hardening**: Only after Phase 4 is complete and the proxy is deleted, resolve the 12-Item Tech Debt checklist (specifically: untyped `type(content) is dict` in `extract_causal_result`) during Tier 2 Hardening on the isolated sub-modules.

---

## Requirements Traceability Matrix

| Requirement ID | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Extract depth-0 metadata resolution functions to metadata_resolver.py | Phase 1, Step 1 | [x] |
| REQ-002 | Extract openpyxl corporate styling to excel_styler.py | Phase 1, Step 2 | [x] |
| REQ-003 | Wire proxy delegations in export_service.py for Phase 1 leaf symbols | Phase 1, Step 3 | [x] |
| REQ-004 | Verify quality gates and existing 39 unit tests for Phase 1 | Phase 1, Step 4 | [x] |
| REQ-005 | Extract 13-column summary builder to summary_builder.py | Phase 2, Step 1 | [x] |
| REQ-006 | Extract shared atom dataset builder to atom_row_builder.py | Phase 2, Step 2 | [x] |
| REQ-007 | Wire proxy delegations in export_service.py for Phase 2 builders | Phase 2, Step 3 | [x] |
| REQ-008 | Verify quality gates and existing 39 unit tests for Phase 2 | Phase 2, Step 4 | [x] |
| REQ-009 | Extract Excel workbook generation to excel_exporter.py | Phase 3, Step 1 | [x] |
| REQ-010 | Extract CSV flat streaming to csv_exporter.py | Phase 3, Step 2 | [x] |
| REQ-011 | Wire proxy delegations in export_service.py for Phase 3 exporters | Phase 3, Step 3 | [x] |
| REQ-012 | Verify quality gates and existing 39 unit tests for Phase 3 | Phase 3, Step 4 | [x] |
| REQ-013 | Rewire 1-hop consumer imports in report_service.py and dependencies.py | Phase 4, Step 1 | [x] |
| REQ-014 | Modularize monolithic test suite into per-submodule test files | Phase 4, Step 2 | [x] |
| REQ-015 | Execute atomic package cutover creating export/__init__.py and deleting export_service.py | Phase 4, Step 3 | [x] |
| REQ-016 | Register export_service.py under QGR017 lockdown and update directory reference | Phase 4, Step 4 | [x] |

---

# Session Handover Context

## Achieved
- Extracted exact AST symbol boundaries for monolithic `@[backend_v2/services/export_service.py#L65-L589]` (590 lines, originally 1,124 lines).
- Verified baseline test suite: 39 unit tests passing with 95% line coverage (no Phase 0 coverage bootstrap needed).
- Generated complete `docs/epic/tasks_export_service/symbol_migration_map.md` tracking all 14 extracted symbols and 1-hop consumers.
- Completed Phase 1: Extracted `backend_v2/services/export/metadata_resolver.py` (97% coverage) and `backend_v2/services/export/excel_styler.py` (100% coverage) with proxy delegations in `export_service.py`. All 52 tests passing, 10/10 quality gate stages green.
- Completed Phase 2: Extracted `backend_v2/services/export/summary_builder.py` (98% coverage) and `backend_v2/services/export/atom_row_builder.py` (95% coverage) with proxy delegations in `export_service.py`. All 64 tests passing, 10/10 quality gate stages green. Preserved single-pipeline dynamic causal proposition streaming under `matrix_label = "Kausaalipäättely"`.
- Completed Phase 3: Extracted `backend_v2/services/export/excel_exporter.py` (95% coverage) and `backend_v2/services/export/csv_exporter.py` (93% coverage) with proxy delegations in `export_service.py`. Created dedicated unit test suites `test_excel_exporter.py` (8 passing tests) and `test_csv_exporter.py` (7 passing tests). Maintained 100% green status on all 39 baseline tests in `test_export_service.py`, 10/10 stages across both `export_service.py` (90% coverage) and `backend_v2/services/export/` (96.20% package coverage).
- Completed Phase 4: Executed Atomic Package Cutover. Created `backend_v2/services/export/__init__.py` package facade with DI wiring and redundant aliased exports (`__all__`), rewired consumer imports (`report_service.py`, `dependencies.py`, `test_report_headers_l10n_parity.py`), decomposed monolithic test file into 7 modularized test suites (84 total tests under `backend_v2/tests/unit/services/export/`), physically deleted `backend_v2/services/export_service.py` and `test_export_service.py`, enforced AST Guardrail `QGR017` lockdown with 11 passing guardrail tests in `scripts/_ast_guardrails.py`, and updated `.agents/rules/04_directory_reference.md`. Verified 10/10 quality gate stages and 97.94% package coverage.
- Completed Epoch 2 Tier 2 Hardening on Target 1 (`backend_v2/services/export/metadata_resolver.py`): Eradicated `type(content) is dict` tech debt using typed pattern matching on `CausalTdaFusionResultDTO | CausalGraphPayloadDTO`, added RFC 7807 `exc_info=True` on `resolve_matrix_label`, fixed `backend_audit_loop.py` single-file target parsing, verified 181-rule audit matrix and 10/10 quality gate stages with 95.19% coverage (11 passing tests), committed in `b82620507`.
- Completed Epoch 2 Tier 2 Hardening on Target 2 (`backend_v2/services/export/excel_styler.py`): Verified 181-rule audit matrix, expanded `test_excel_styler.py` with ISTQB boundary tests (empty list, nonexistent sheets, max width 50 cap, empty sheet width 12 padding), verified 10/10 quality gate stages with 100% coverage (6 passing tests), committed in `5b4af39af`.
- Completed Epoch 2 Tier 2 Hardening on Target 3 (`backend_v2/services/export/summary_builder.py`): Verified 181-rule audit matrix, eradicated dead `lbl = m.name` fallback in favor of `I18nText.resolve()` schema invariant, expanded `test_summary_builder.py` with locale resolution tests, verified 10/10 quality gate stages with 100% coverage (5 passing tests), committed in `21f638fbd`.
- Completed Epoch 2 Tier 2 Hardening on Target 4 (`backend_v2/services/export/atom_row_builder.py`): Verified 181-rule audit matrix, expanded `test_atom_row_builder.py` with ISTQB negative and fallback boundary tests (scorecard claim_label fallback in denormalized rows, metadata level/criterion fallback in denormalized rows, metadata inverse evidence fallback across both builders), verified 10/10 quality gate stages with 100% coverage (8 passing tests), committed in `b58d3676a`.

## Learned
- AST decorator line offset: `@staticmethod` and `@classmethod` decorators place `node_start` on the decorator line (specifically: line 77 for `_build_matrix_atom_maps`), which must match MBD004 exactly.
- Multi-method spanning line bounds are strictly forbidden by MBD004; all bounds must reference single AST nodes or the parent class (`ExportService: #L65-L589`).
- In `I18nText`, the `'en'` translation key is mandatory by schema validation (`AppException` 400 if missing).
- `I18nText.resolve()` guarantees returning a non-empty string or raising `AppException`; downstream callers do not need defensive `if not lbl: lbl = m.name` duct-tape.
- In `CausalNodeDTO`, the quote attribute is `source_quotes: tuple[str, ...] | None`, and `FairScoringBreakdownDTO` enforces mathematical identity `raw == deduplicated + dampened_savings` with required `independent_error_count` and `cascading_fault_count`.
- `ExecutionStepState` enforces strict `extra='forbid'`, so causal output payloads must be attached via `TraceEvent(step_name="causal_discovery", event_type="output", content=causal_payload)` on `exec_record.execution_trace`.
- `TDAAssertion` enforces `min_length=10` on `concept_description`.
- `MatrixPromptBlock` requires at least 1 scale item in `scales`.
- `ExportPayloadDTO` binary payload attribute is `content_bytes` (not `content`), and `AppException` error code is accessed via `error_code` (not `code`).
- Deleting `export_service.py` and creating `export/__init__.py` in the same step prevents duplicate module collisions in Python/MyPy and enables clean QGR017 enforcement.
- Logfire plugin eagerly imports telemetry on pytest startup in single-file audits, which can artificially depress initial file coverage unless executed cleanly or without premature imports.
- In `AtomResultDTO`, `source_quotes` is strictly mandatory unless `contextual_override` or `is_inverse_evidence` is True.
- In `ReportDataDTO`, referential integrity validation strictly requires that all atom `tda_id`s in `results` have corresponding keys in `hydrated_references`.

## Resume Command
/tier5-resume --target="@[docs/epic/export_service_decomposition_tracker.md]" --workflow="/tier2-hardening-backend" --rules="01-python-backend.md"

## Remaining
- [x] Execute Phase 1: Leaf Metadata Resolver & Excel Styler Extraction (`/tier2-execute`)
- [x] Execute Phase 2: Tabular Row & Dataset Builders Extraction (`/tier2-execute`)
- [x] Hydrate detailed plans for Phase 3 and Phase 4 (`/tier3-god-code-decomposition`)
- [x] Execute Phase 3: Excel & CSV Exporters Extraction (`/tier2-execute`)
- [x] Execute Phase 4: Atomic Package Cutover & AST Guardrail QGR017 Lockdown (`/tier2-execute`)
- [ ] Execute Epoch 2 Tier 2 Hardening across extracted sub-modules (`/tier2-hardening-backend`)
  - [x] @[backend_v2/services/export/metadata_resolver.py]
  - [x] @[backend_v2/services/export/excel_styler.py]
  - [x] @[backend_v2/services/export/summary_builder.py]
  - [x] @[backend_v2/services/export/atom_row_builder.py]
  - [ ] @[backend_v2/services/export/excel_exporter.py]
  - [ ] @[backend_v2/services/export/csv_exporter.py]
  - [ ] @[backend_v2/services/export/__init__.py]
  - [ ] @[backend_v2/services/report_service.py]
  - [ ] @[backend_v2/api/dependencies.py]

### Hardening State Snapshot
- **TARGETS** (9):
  1. `backend_v2/services/export/metadata_resolver.py`
  2. `backend_v2/services/export/excel_styler.py`
  3. `backend_v2/services/export/summary_builder.py`
  4. `backend_v2/services/export/atom_row_builder.py`
  5. `backend_v2/services/export/excel_exporter.py`
  6. `backend_v2/services/export/csv_exporter.py`
  7. `backend_v2/services/export/__init__.py`
  8. `backend_v2/services/report_service.py`
  9. `backend_v2/api/dependencies.py`
- **DONE** (4):
  1. `backend_v2/services/export/metadata_resolver.py`
  2. `backend_v2/services/export/excel_styler.py`
  3. `backend_v2/services/export/summary_builder.py`
  4. `backend_v2/services/export/atom_row_builder.py`
- **REMAINING** (5):
  1. `backend_v2/services/export/excel_exporter.py`
  2. `backend_v2/services/export/csv_exporter.py`
  3. `backend_v2/services/export/__init__.py`
  4. `backend_v2/services/report_service.py`
  5. `backend_v2/api/dependencies.py`

