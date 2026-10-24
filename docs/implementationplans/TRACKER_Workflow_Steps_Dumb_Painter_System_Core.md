# Tracker: Workflow Steps Dumb Painter & System Core Classification

@[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Steps_Dumb_Painter_System_Core.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Steps_Dumb_Painter_System_Core.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Steps_Dumb_Painter_System_Core.md] @[docs/implementationplans/TRACKER_Workflow_Steps_Dumb_Painter_System_Core.md]`
  - [x] Step 1: PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUP
  - [x] Step 2: SSOT ENUM DEFINITION & CROSS-LANGUAGE PARITY
  - [x] Step 3: DOMAIN MODEL & DTO INTEGRATION
  - [x] Step 4: SEED VAULT HARMONIZATION
  - [x] Step 5: DECOUPLED WORKFLOW BLUEPRINTS PROVIDER
  - [ ] Step 6: FRONTEND DUMB PAINTER REFACTORING
  - [ ] Step 7: TEST EXPANSION & QUALITY GATES
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Steps_Dumb_Painter_System_Core.md] @[docs/implementationplans/TRACKER_Workflow_Steps_Dumb_Painter_System_Core.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_Workflow_Steps_Dumb_Painter_System_Core.md] --gate backend`.
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/models/domain/step.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_Workflow_Steps_Dumb_Painter_System_Core.md] --gate frontend`.
  - [ ] @[client_app_v2/lib/core/models/enums.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/workflow.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/studio_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Workflow_Steps_Dumb_Painter_System_Core.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Steps_Dumb_Painter_System_Core.md] @[ki_god_code_prevention.md] @[ki_workflow_context_governance.md] @[ki_desktop_pro_tool_studio_ux.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the Dumb Painter presentation pattern in `WorkflowStepCard` and `WorkflowStepsTab`, ensuring client widgets are pure visual renderers with zero heuristic branching or client-side index math (`index == 0`, `index > 0 && isSystemCoreStep`).
     - `@[ki_workflow_context_governance.md]`: Document `StepZone` enum SSOT (`zone_a`, `zone_b`, `zone_c`), explicit zone embedding on `Step` and `NodeStrategy`, and eradication of client-side index heuristics in favor of Server-Driven UI Dumb Painter layout. Document `allBlueprintsProvider` scope isolation (`StepFilterScope.all`) decoupling workflow authoring from Studio Dashboard filter state.
     - `@[ki_desktop_pro_tool_studio_ux.md]`: Document visual system core badge retention and Zone B specialist control layout for Causal Discovery nodes in Studio Workflow Builder.
     - `@[ki_zero_permissive_typing.md]`: Document 100% cross-language enum parity for `StepZone` between Python `enums.py` and Dart `enums.dart`, with zero fallback zones or raw string defaults.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register new test files (`client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_dumb_painter_test.dart`).
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` (specifically `02_domain_ontology_and_data_contracts.md` and `04_presentation_and_sdui_adapters.md`) describing newly established invariants in present tense without historical language or plan IDs.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Steps_Dumb_Painter_System_Core.md] @[docs/implementationplans/TRACKER_Workflow_Steps_Dumb_Painter_System_Core.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

1. **Strict Execution Protocol**:
   - The execution agent MUST follow the plan's execution protocol step-by-step from Step 1 to Step 7.
   - In Continuous Full-Auto Mode (`/tier2-execute --full-auto`), proceed autonomously across steps as long as quality gates pass 100%, halting immediately upon any gate failure or when triggering context handover.
   - In Step-by-Step Mode (`/tier2-execute`), execute exactly one step and pause for user verification.

2. **Atomic Commits & Quality Gates**:
   - After completing each step, run the relevant audit loop (`uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict` for Python, `uv run python scripts/flutter_audit_loop.py <target_path> --build` for Flutter).
   - Once all automated checks pass, instruct the user to execute an atomic `git commit` using strict Conventional Commits syntax with English descriptions.

3. **Post-Implementation Hardening**:
   - Following completion of all 7 steps, execute post-implementation hardening either autonomously via `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_Workflow_Steps_Dumb_Painter_System_Core.md] --gate backend` and `--gate frontend`, or interactively via `/tier2-hardening-backend` and `/tier2-hardening-frontend`.
   - Update the checkboxes for each production file in `### Post-Implementation Gates` as hardening audits pass.

4. **Session Handover Protocol**:
   - If context amnesia thresholds are reached (>8 user prompts, 3 atomic commits, or >5 complex files modified), execute `/tier5-session-handover` to serialize progress into `# Session Handover Context`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| `REQ-ZON-001` | Remediate pre-flight technical debt in `workflow_steps_tab.dart` (DGR008), `workflow_builder_view.dart` (DGR007), and `backend_v2/models/enums.py` (TD_DICT_GET) | Step 1 | [x] Completed |
| `REQ-ZON-002` | Define SSOT enum `StepZone` (`zone_a`, `zone_b`, `zone_c`) with `@JsonEnum()` in Dart and `StrEnum` in Python | Step 2 | [x] Completed |
| `REQ-ZON-003` | Validate 100% cross-language member parity for `StepZone` via `test_enum_parity.py` | Step 2 | [x] Completed |
| `REQ-ZON-004` | Embed `zone` on backend domain model `Step` with default `StepZone.ZONE_B` | Step 3 | [x] Completed |
| `REQ-ZON-005` | Embed `zone` on Flutter `NodeStrategy` across all 3 unions (`llm`, `logic`, `causalDiscovery`) with default `StepZone.zoneB` | Step 3 | [x] Completed |
| `REQ-ZON-006` | Assign explicit `"zone"` properties to all foundational system core steps in `seed_data.json` and verify via dry-run and atom audits | Step 4 | [x] Completed |
| `REQ-ZON-007` | Re-seed local development database `db_v2.json` with updated blueprint zone classifications | Step 4 | [x] Completed |
| `REQ-ZON-008` | Implement `allBlueprintsProvider` in `studio_controller.dart` fetching `StepFilterScope.all` with cache invalidation on save/delete | Step 5 | [x] Completed |
| `REQ-ZON-009` | Decouple `WorkflowBuilderView` from dashboard filter scope by watching `allBlueprintsProvider` | Step 5 | [x] Completed |
| `REQ-ZON-010` | Refactor `WorkflowStepCard` to derive `isSystemCoreStep`, `isZoneA`, and `isZoneC` strictly from `currentBlueprint` as a pure Dumb Painter | Step 6 | [ ] Pending |
| `REQ-ZON-011` | Refactor `_findFirstZoneCIndex` in `WorkflowStepsTab` to use positive `StepZone.zoneC` matching without engine-type exclusions | Step 6 | [ ] Pending |
| `REQ-ZON-012` | Implement comprehensive widget test `workflow_step_card_dumb_painter_test.dart` covering Zone B Causal Discovery system core protections and fallback behavior | Step 7 | [ ] Pending |
| `REQ-ZON-013` | Pass all unit tests, widget tests, two-stage quality gates (`backend_audit_loop.py`, `flutter_audit_loop.py`), and live E2E causal discovery integration gate | Step 7 | [ ] Pending |

# Session Handover Context

## Achieved
- Completed Tier 0 System 2 Research & Analysis of `IMPLEMENTATION_PLAN_Workflow_Steps_Dumb_Painter_System_Core.md`.
- Executed pre-flight technical debt audit: identified and cataloged 8 items (3 in `enums.py`, 2 in `workflow_steps_tab.dart`, 3 in `workflow_builder_view.dart`) into `Phase 1: Pre-Implementation Cleanups`.
- Hardened 5-Column Directives Table and execution protocol with AST-exact line bounds and strict invariants.
- Generated Standalone Plan Tracker `TRACKER_Workflow_Steps_Dumb_Painter_System_Core.md` with granular step execution status, file-level hardening checklists, and Requirements Traceability Matrix.

## Learned
- In `seed_data.json`, 5 foundational steps carry `is_system_core: true`: Input Processing (`sp_db849f9790984585` -> Zone A), XAI Reporter (`sp_192910b5f5a34c79` -> Zone C), Scoring Engine (`sp_d245365e4a274b9e` -> Zone C), Synthesis Generation (`sp_7a8b9c0d1e2f3a4b` -> Zone C), and Causal Discovery (`sp_c4a5a1d15c00438a` -> Zone B).
- In `workflow_step_card.dart`, `isSystemCoreStep` was previously conflated with `index > 0`, causing Causal Discovery to render as a Zone C automatic anchor box. Pure Dumb Painter derivation from `currentBlueprint.zone` cleanly decouples functional layout from system core mutability locks.

## Remaining
- Step 1: Pre-Implementation Technical Debt Cleanup
- Step 2: SSOT Enum Definition & Cross-Language Parity
- Step 3: Domain Model & DTO Integration
- Step 4: Seed Vault Harmonization
- Step 5: Decoupled Workflow Blueprints Provider
- Step 6: Frontend Dumb Painter Refactoring
- Step 7: Test Expansion & Quality Gates
- Post-Implementation Hardening (Backend & Frontend)
- Tier 7 As-Built Architectural Documentation Sync
- Tier 8 System 2 Red-Team Plan Audit

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Steps_Dumb_Painter_System_Core.md] @[docs/implementationplans/TRACKER_Workflow_Steps_Dumb_Painter_System_Core.md]
```
