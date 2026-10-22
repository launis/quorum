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
Decomposition of monolithic `@[backend_v2/services/export_service.py#L62-L1123]` (1,124 lines, Archetype B: Presentation / Streaming / Formatter) into the cohesive domain package `backend_v2/services/export/` using the Two-Epoch Strangler Fig Protocol. Baseline test coverage: 95% (39 passing unit tests).

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

### Phase 3: Excel & CSV Exporters Extraction (Header Placeholder)
**Plan:** @[docs/epic/tasks_export_service/phase3_exporters_extraction.md]
- [ ] **[NOK] Execution:** /tier2-execute @[docs/epic/tasks_export_service/phase3_exporters_extraction.md] @[docs/epic/export_service_decomposition_tracker.md]
  - [ ] Step 1: Full Strangler Reinvokation Gate
  - [ ] Step 2: Create Excel Exporter Submodule
  - [ ] Step 3: Create CSV Exporter Submodule
  - [ ] Step 4: Proxy Delegation and Quality Gate
- [ ] **[NOK] Audit:** uv run python scripts/backend_audit_loop.py backend_v2/services/export_service.py --test

### Phase 4: Atomic Package Cutover & Guardrails Lockdown (Header Placeholder)
**Plan:** @[docs/epic/tasks_export_service/phase4_package_cutover_and_guardrails.md]
- [ ] **[NOK] Execution:** /tier2-execute @[docs/epic/tasks_export_service/phase4_package_cutover_and_guardrails.md] @[docs/epic/export_service_decomposition_tracker.md]
  - [ ] Step 1: Full Strangler Reinvokation Gate
  - [ ] Step 2: Consumer Import Rewiring
  - [ ] Step 3: Modularize Test Suite
  - [ ] Step 4: Atomic Package Cutover
  - [ ] Step 5: Guardrail Lockdown and Smoke Test
- [ ] **[NOK] Audit:** uv run python scripts/backend_audit_loop.py backend_v2/services/export/ --test

---

### Post-Implementation Gates

#### Tier 2 Hardening (Backend)
- [ ] **[NOK] Tier 2 Hardening (Backend):** Post-cutover type and schema hardening on isolated sub-modules
  - [ ] [NEW] @[backend_v2/services/export/metadata_resolver.py]
  - [ ] [NEW] @[backend_v2/services/export/excel_styler.py]
  - [ ] [NEW] @[backend_v2/services/export/summary_builder.py]
  - [ ] [NEW] @[backend_v2/services/export/atom_row_builder.py]
  - [ ] [NEW] @[backend_v2/services/export/excel_exporter.py]
  - [ ] [NEW] @[backend_v2/services/export/csv_exporter.py]
  - [ ] [NEW] @[backend_v2/services/export/__init__.py]
  - [ ] @[backend_v2/services/export_service.py]
  - [ ] @[backend_v2/services/report_service.py]
  - [ ] @[backend_v2/api/dependencies.py]

#### Tier 2 Hardening (Frontend)
- [x] **[SKIPPED] Tier 2 Hardening (Frontend):** No Flutter files modified in this backend decomposition.

#### Quality & Safety Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit:** Characterization test baseline verified at 95% line coverage with 39 passing tests.
- [ ] **[NOK] Pre-Delete Audit:** Verified 0 remaining imports of `backend_v2.services.export_service` before deleting proxy file.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit:** Verified Excel styling, 13-column summary rows, 14-column atom rows, and 22-column CSV streams match 100% byte and schema parity.
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
| REQ-009 | Re-invoke Tier 3 planner gate for Phase 3 detailed expansion | Phase 3, Step 1 | [ ] |
| REQ-010 | Extract Excel workbook generation to excel_exporter.py | Phase 3, Step 2 | [ ] |
| REQ-011 | Extract CSV flat streaming to csv_exporter.py | Phase 3, Step 3 | [ ] |
| REQ-012 | Wire proxy delegations in export_service.py for Phase 3 exporters | Phase 3, Step 4 | [ ] |
| REQ-013 | Re-invoke Tier 3 planner gate for Phase 4 detailed expansion | Phase 4, Step 1 | [ ] |
| REQ-014 | Rewire 1-hop consumer imports in report_service.py and dependencies.py | Phase 4, Step 2 | [ ] |
| REQ-015 | Modularize monolithic test suite into per-submodule test files | Phase 4, Step 3 | [ ] |
| REQ-016 | Execute atomic package cutover creating export/__init__.py and deleting export_service.py | Phase 4, Step 4 | [ ] |
| REQ-017 | Register export_service.py under QGR017 lockdown and update directory reference | Phase 4, Step 5 | [ ] |

---

# Session Handover Context

## Achieved
- Extracted exact AST symbol boundaries for monolithic `@[backend_v2/services/export_service.py#L62-L1123]` (1,124 lines).
- Verified baseline test suite: 39 unit tests passing with 95% line coverage (no Phase 0 coverage bootstrap needed).
- Generated complete `docs/epic/tasks_export_service/symbol_migration_map.md` tracking all 14 extracted symbols and 1-hop consumers.
- Generated Single-File Full Strangler Mode detailed implementation plans for Phase 1 (`phase1_leaf_and_styler_extraction.md`) and Phase 2 (`phase2_row_builders_extraction.md`), plus header placeholders for Phase 3 and Phase 4.
- Created TRK001-TRK006 compliant master tracker at `docs/epic/export_service_decomposition_tracker.md`.
- Completed Phase 1: Extracted `backend_v2/services/export/metadata_resolver.py` (97% coverage) and `backend_v2/services/export/excel_styler.py` (100% coverage) with proxy delegations in `export_service.py`. All 52 tests passing, 10/10 quality gate stages green.
- Completed Phase 2: Extracted `backend_v2/services/export/summary_builder.py` (98% coverage) and `backend_v2/services/export/atom_row_builder.py` (95% coverage) with proxy delegations in `export_service.py`. All 64 tests passing (39 existing + 25 sub-module unit tests), 10/10 quality gate stages green. Preserved single-pipeline dynamic causal proposition streaming under `matrix_label = "Kausaalipäättely"`.

## Learned
- AST decorator line offset: `@staticmethod` and `@classmethod` decorators place `node_start` on the decorator line (specifically: line 73 for `_build_matrix_atom_maps`), which must match MBD004 exactly.
- Multi-method spanning line bounds are strictly forbidden by MBD004; all bounds must reference single AST nodes or the parent class.
- The monolithic test file `test_export_service.py` is 2,194 lines and will be modularized into 7 focused test files during Phase 4 cutover.
- In `I18nText`, the `'en'` translation key is mandatory by schema validation (`AppException` 400 if missing).
- In `CausalNodeDTO`, the quote attribute is `source_quotes: tuple[str, ...] | None`, and `FairScoringBreakdownDTO` enforces mathematical identity `raw == deduplicated + dampened_savings` with required `independent_error_count` and `cascading_fault_count`.

## Resume Command
/tier3-god-code-decomposition --reinvoke @[docs/epic/tasks_export_service/phase3_exporters_extraction.md] @[docs/epic/export_service_decomposition_tracker.md]

## Remaining
- [x] Execute Phase 1: Leaf Metadata Resolver & Excel Styler Extraction (`/tier2-execute`)
- [x] Execute Phase 2: Tabular Row & Dataset Builders Extraction (`/tier2-execute`)
- [ ] Re-invoke `/tier3-god-code-decomposition` to hydrate detailed plans for Phase 3 and Phase 4
- [ ] Execute Phase 3: Excel & CSV Exporters Extraction
- [ ] Execute Phase 4: Atomic Package Cutover & AST Guardrail QGR017 Lockdown
- [ ] Execute Epoch 2 Tier 2 Hardening across extracted sub-modules
