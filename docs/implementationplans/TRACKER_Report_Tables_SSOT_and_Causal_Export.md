# Tracker: Report Tables SSOT, Causal Export Streaming, Row Data Status Decoupling, ML-Ready Tabular Metrics & Database Reseed

@[docs/implementationplans/IMPLEMENTATION_PLAN_Report_Tables_SSOT_and_Causal_Export.md]

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

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Report_Tables_SSOT_and_Causal_Export.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Report_Tables_SSOT_and_Causal_Export.md] @[docs/implementationplans/TRACKER_Report_Tables_SSOT_and_Causal_Export.md]`
  - [x] Step 1.1: Register ML-Ready Columns in ReportAtomColumn Enum
  - [x] Step 1.2: Synchronize Export Column Matrix and ML Headers in Localization Files
  - [x] Step 1.3: Update Denormalized CSV Header SSOT in ReportHeaderResolver
  - [x] Step 1.4: Fix Hardcoded Column Lookups in Unit Tests
  - [x] Step 2.1: Enrich Export Forensic DTOs with is_inverse and points_awarded
  - [x] Step 2.2: Stream Causal Graph Nodes and Populate ML Columns in Atom Rows
  - [x] Step 2.3: Stream Causal Graph Nodes and Populate ML Columns in Flat CSV Rows
  - [x] Step 2.4: Unit Testing ML Columns and Causal Export Population
  - [x] Step 3.1: Enrich ReportRowItem DTO and Freezed Model with is_inverse_evidence
  - [x] Step 3.2: Propagate is_inverse_evidence in ReportService.get_report_rows
  - [x] Step 3.3: Declare Semantic Row Status Localizations
  - [x] Step 3.4: Render Semantic Status Badges in Flutter ExecutionReportsView
  - [x] Step 3.5: Unit Test Row Item Inverse Evidence Propagation
  - [ ] Step 4.1: Define Standard Matrix Visible Columns SSOT in Backend and Flutter
  - [ ] Step 4.2: Synchronize All Output Profiles in Seed Vault
  - [ ] Step 4.3: Verify Output Profile and SDUI Parity Tests
  - [ ] Step 5.1: Two-Phase Pre-Flight In-Memory Seed Validation
  - [ ] Step 5.2: Execution Artifact Pre-Flight Backup and Local Database Hard Reset
  - [ ] Step 5.3: Validate Post-Seeding Database State
  - [ ] Step 6.1: Execute Global Backend Audit Gate
  - [ ] Step 6.2: Execute Flutter Audit Loop
  - [ ] Step 6.3: Verify Real Artifact Export and Row Data View Against Past Execution
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Report_Tables_SSOT_and_Causal_Export.md] @[docs/implementationplans/TRACKER_Report_Tables_SSOT_and_Causal_Export.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files.
  - [ ] @[backend_v2/models/domain/output_profile.py]
  - [ ] @[backend_v2/models/dtos/export.py]
  - [ ] @[backend_v2/models/dtos/output_profile.py]
  - [ ] @[backend_v2/models/dtos/report_artifact.py]
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/services/export_service.py]
  - [ ] @[backend_v2/services/localization.py]
  - [ ] @[backend_v2/services/report_service.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified @-referenced production Flutter files.
  - [ ] @[client_app_v2/lib/features/reports/models/report_artifact.dart]
  - [ ] @[client_app_v2/lib/features/reports/views/execution_reports_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/output_profile.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Report_Tables_SSOT_and_Causal_Export.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Report_Tables_SSOT_and_Causal_Export.md] @[ki_god_code_prevention.md] @[ki_dumb_painter_sdui.md] @[ki_dual_axis_localization_architecture.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_dumb_painter_sdui.md]`: Document Dumb Painter presentation compliance across Flutter UI, PDF templates, Excel Tab 2, and rectangular CSV streams. Codify the decoupling of affirmative capability points from inverse negative evidence findings via `is_inverse_evidence` and semantic badges (`+1 p` / `0 p` vs `Puhdas` / `⚠️ Negatiivinen löydös`).
     - `@[ki_dual_axis_localization_architecture.md]`: Document the unification of `ReportMatrixColumn.LABEL` and `ReportAtomColumn.MATRIX` under the SSOT key `"Logiikkamatriisi"` in `fi.json` and `"Logic Matrix"` in `en.json`, expanding `ReportAtomColumn` and `get_all_denormalized_csv_headers` to 22 columns via `ReportHeaderResolver`.
     - `@[ki_zero_permissive_typing.md]`: Document the addition of ML-ready numeric indicators (`is_inverse: int` [0/1] and `points_awarded: float` [1.0/0.0]) in `ExportForensicAtomDTO` and `ExportDenormalizedFlatRowDTO`, establishing mathematical scoring identity `sum(points_awarded) == hits` for affirmative matrix atoms.
     - `@[ki_god_code_prevention.md]`: Document single-pipeline streaming of unmapped dynamic causal graph propositions (`CausalNodeDTO`) into canonical Tab 2 atom rows under `matrix_label = "Kausaalipäättely"` without creating separate files or parallel presentation adapters.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` if any modules or DTO boundaries have evolved.
  3. **Pillar Documentation Sync:**
     - Update timeless present-tense narratives in `docs/architecture/03_execution_telemetry_reporting.md` and `docs/architecture/04_sdui_frontend_presentation.md` reflecting SSOT column resolution, ML-ready export metrics, and semantic row status decoupling without historical language or plan IDs.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Report_Tables_SSOT_and_Causal_Export.md] @[docs/implementationplans/TRACKER_Report_Tables_SSOT_and_Causal_Export.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Strict Execution Mode**: Do not modify domain files without slash command invocation `/tier2-execute`.
- **Quality Gates**: After each logical step, run `uv run python scripts/backend_audit_loop.py <target_path> --test` for Python files and `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build` for Flutter files.
- **Atomic Commits**: Run atomic git commits with Conventional Commits syntax following successful quality gate runs.
- **Double-Entry Bookkeeping**: Mark each completed step with `[x]` in this tracker and keep `# Session Handover Context` synchronized.

## Requirements Traceability Matrix
| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Register ML-Ready Columns in ReportAtomColumn Enum | Step 1.1 | Completed |
| REQ-002 | Synchronize Export Column Matrix and ML Headers in Localization Files | Step 1.2 | Completed |
| REQ-003 | Update Denormalized CSV Header SSOT in ReportHeaderResolver | Step 1.3 | Completed |
| REQ-004 | Fix Hardcoded Column Lookups in Unit Tests | Step 1.4 | Completed |
| REQ-005 | Enrich Export Forensic DTOs with is_inverse and points_awarded | Step 2.1 | Completed |
| REQ-006 | Stream Causal Graph Nodes and Populate ML Columns in Atom Rows | Step 2.2 | Completed |
| REQ-007 | Stream Causal Graph Nodes and Populate ML Columns in Flat CSV Rows | Step 2.3 | Completed |
| REQ-008 | Unit Testing ML Columns and Causal Export Population | Step 2.4 | Completed |
| REQ-009 | Enrich ReportRowItem DTO and Freezed Model with is_inverse_evidence | Step 3.1 | Completed |
| REQ-010 | Propagate is_inverse_evidence in ReportService.get_report_rows | Step 3.2 | Completed |
| REQ-011 | Declare Semantic Row Status Localizations | Step 3.3 | Completed |
| REQ-012 | Render Semantic Status Badges in Flutter ExecutionReportsView | Step 3.4 | Completed |
| REQ-013 | Unit Test Row Item Inverse Evidence Propagation | Step 3.5 | Completed |
| REQ-014 | Define Standard Matrix Visible Columns SSOT in Backend and Flutter | Step 4.1 | Pending |
| REQ-015 | Synchronize All Output Profiles in Seed Vault | Step 4.2 | Pending |
| REQ-016 | Verify Output Profile and SDUI Parity Tests | Step 4.3 | Pending |
| REQ-017 | Two-Phase Pre-Flight In-Memory Seed Validation | Step 5.1 | Pending |
| REQ-018 | Execution Artifact Pre-Flight Backup and Local Database Hard Reset | Step 5.2 | Pending |
| REQ-019 | Validate Post-Seeding Database State | Step 5.3 | Pending |
| REQ-020 | Execute Global Backend Audit Gate | Step 6.1 | Pending |
| REQ-021 | Execute Flutter Audit Loop | Step 6.2 | Pending |
| REQ-022 | Verify Real Artifact Export and Row Data View Against Past Execution | Step 6.3 | Pending |

# Session Handover Context
## Achieved
- Plan created, researched, red-teamed, and validated under Tier 0 Research Plan protocol.
- Established 1:1 bidirectional plan-tracker parity contracts across 22 execution steps and 11 production hardening targets.

## Learned
- Column naming unification from `"Matriisi"` to `"Logiikkamatriisi"` requires dynamic lookup resolution via `ReportHeaderResolver` in `test_export_service.py` (line 667).
- Machine learning pipelines require decoupled numeric indicators (`is_inverse: int`, `points_awarded: float`) to prevent clean anti-pattern checks from being counted as affirmative capability points.
- Pre-flight backup of `data/files/executions/exe_c50e968fc9c04906` is mandatory before `run_seed.py local` wipes the execution directory via `shutil.rmtree`.

## Remaining
- Step 1.1 through Step 6.3 pending execution under `/tier2-execute --full-auto`.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Report_Tables_SSOT_and_Causal_Export.md] @[docs/implementationplans/TRACKER_Report_Tables_SSOT_and_Causal_Export.md]
```
