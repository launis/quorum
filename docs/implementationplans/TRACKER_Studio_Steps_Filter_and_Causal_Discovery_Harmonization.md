# Tracker: Admin Studio Steps Filter & Causal Discovery Harmonization

@[docs/implementationplans/IMPLEMENTATION_PLAN_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md]

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

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md]`
  - [x] Step 1: TECHNICAL DEBT ERADICATION & ARB LOCALIZATION
  - [ ] Step 2: SSOT ENUM DEFINITION & CROSS-LANGUAGE PARITY
  - [ ] Step 3: SEED VAULT CAUSAL BLUEPRINT CONSOLIDATION
  - [ ] Step 4: BACKEND SERVICE & ROUTER SERVER-SIDE FILTERING
  - [ ] Step 5: FLUTTER CLIENT, CONTROLLER & DUMB PAINTER VIEW
  - [ ] Step 6: TWO-STAGE QUALITY GATE AUDIT & PERSISTENCE VERIFICATION
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] --gate backend`.
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/api/routers/studio/steps.py]
  - [ ] @[backend_v2/services/studio/workflow_service.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] --gate frontend`.
  - [ ] @[client_app_v2/lib/core/models/enums.dart]
  - [ ] @[client_app_v2/lib/core/api/studio_client.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/studio_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] @[ki_god_code_prevention.md] @[ki_workflow_context_governance.md] @[ki_desktop_pro_tool_studio_ux.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document server-side filtering delegation in StudioWorkflowService and Dumb Painter rendering in StudioDashboardView with clean architectural boundaries.
     - `@[ki_workflow_context_governance.md]`: Document the canonical universal causal discovery blueprint (`sp_c4a5a1d15c00438a` / `step_causal_discovery`), dynamic input topology agnosticism, and complete consolidation of legacy static steps `sp_01`..`sp_06`.
     - `@[ki_desktop_pro_tool_studio_ux.md]`: Document the interactive `SegmentedButton<StepFilterScope>` standard in Admin Studio Steps Tab, state management via `StepsController.setScope()`, and parameterized localization for error alerts.
     - `@[ki_zero_permissive_typing.md]`: Document the cross-language `StepFilterScope` enum SSOT with `@JsonEnum()`/`@JsonValue` in Dart and `StrEnum` in Python, strictly enforced via automated bidirectional parity tests.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to verify all touched Studio routes, services, and view test paths are correctly cataloged.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/01_system_context_and_invariants.md` and `docs/architecture/03_execution_runtime_and_orchestration.md` describing the universal causal discovery blueprint and server-driven specialist vs core step segregation in present tense without historical language or plan IDs.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

1. **Strict Execution Protocol**:
   - The execution agent MUST follow the plan's `<execution_protocol>` step-by-step from Step 1 to Step 6.
   - In Continuous Full-Auto Mode (`/tier2-execute --full-auto`), proceed autonomously across steps as long as quality gates pass 100%, halting immediately upon any gate failure or when triggering context handover.
   - In Step-by-Step Mode (`/tier2-execute`), execute exactly one step and pause for user verification.

2. **Atomic Commits & Quality Gates**:
   - After completing each step, run the relevant audit loop (`uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict` for Python, `uv run python scripts/flutter_audit_loop.py <target_path> --build` for Flutter).
   - Once all automated checks pass, instruct the user to execute an atomic `git commit` using strict Conventional Commits syntax with English descriptions.

3. **Post-Implementation Hardening**:
   - Following completion of all 6 steps, execute post-implementation hardening either autonomously via `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] --gate backend` and `--gate frontend`, or interactively via `/tier2-hardening-backend` and `/tier2-hardening-frontend`.
   - Update the checkboxes for each production file in `### Post-Implementation Gates` as hardening audits pass.

4. **Session Handover Protocol**:
   - If context amnesia thresholds are reached (>8 user prompts, 3 atomic commits, or >5 complex files modified), execute `/tier5-session-handover` to serialize progress into `# Session Handover Context`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| `REQ-STP-001` | Eradicate pre-flight technical debt `DGR003` in `studio_dashboard_view.dart` by adding localized ARB string `studioViewsMintDraftError` | Step 1 | [x] Complete |
| `REQ-STP-002` | Eradicate pre-flight technical debt `TD_ISTQB_NEGATIVE` in `test_steps.py` by adding negative test partitions for 404, 403, and 422 HTTP responses | Step 1 | [x] Complete |
| `REQ-STP-003` | Define SSOT enum `StepFilterScope` (`specialists`, `system_core`, `all`) with full cross-language parity in Python and Dart | Step 2 | [ ] Pending |
| `REQ-STP-004` | Add bidirectional unit parity test and missing member negative test in `test_enum_parity.py` | Step 2 | [ ] Pending |
| `REQ-STP-005` | Harmonize canonical universal Causal Discovery blueprint `sp_c4a5a1d15c00438a` with dynamic input agnosticism in `seed_data.json` | Step 3 | [ ] Pending |
| `REQ-STP-006` | Prune redundant duplicate blueprints `sp_01b1d7100000ca01` through `sp_06b1d7100000ca06` from Seed Vault and sync local database | Step 3 | [ ] Pending |
| `REQ-STP-007` | Implement server-side scope filtering in `StudioWorkflowService.list_steps` via exhaustive Python 3.12+ `match scope:` | Step 4 | [ ] Pending |
| `REQ-STP-008` | Expose `scope` query parameter on `GET /studio/steps/` router delegating to `StudioWorkflowService` with negative test coverage | Step 4 | [ ] Pending |
| `REQ-STP-009` | Wire `StudioClient.getSteps({StepFilterScope scope})` to pass `scope` query parameter to backend | Step 5 | [ ] Pending |
| `REQ-STP-010` | Update `StepsController` with `_scope` state, `currentScope` getter, and `setScope` method triggering backend re-fetch | Step 5 | [ ] Pending |
| `REQ-STP-011` | Render interactive `SegmentedButton<StepFilterScope>` in `_buildStepsTab` and render blueprints as pure Dumb Painter | Step 5 | [ ] Pending |
| `REQ-STP-012` | Implement comprehensive widget test `studio_dashboard_steps_tab_test.dart` verifying filter transitions and empty states | Step 5 | [ ] Pending |
| `REQ-STP-013` | Execute Two-Stage Quality Gate audits (`backend_audit_loop.py` with `--ast-strict`, `flutter_audit_loop.py` with `--build`, technical debt audit) | Step 6 | [ ] Pending |

# Session Handover Context

## Achieved
- Completed Tier 0 Research & Analysis of the implementation plan (`IMPLEMENTATION_PLAN_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md`) with 0 AST boundary findings and full architectural sign-off.
- Generated Tier 1 Execution Tracker (`TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md`) establishing 1:1 step tracking, granular production hardening checklists, and bidirectional requirements traceability.
- Validated structural integrity and parity via `audit_tracker_output.py` and `audit_plan_tracker_parity.py`.

## Learned
- Dynamic topology agnosticism in `CausalDiscoveryEngine` enables complete pruning of 6 static, duplicate step records (`sp_01`..`sp_06`), leaving a single universal blueprint (`sp_c4a5a1d15c00438a`).
- Adherence to Option A (Pure Backend-Driven / Dumb Painter) ensures Flutter UI remains completely free of client-side list filtering, delegating filtering to `StudioWorkflowService.list_steps`.
- Pre-flight technical debt audit detected 4 raw string literals (`DGR003`) in `studio_dashboard_view.dart` and lack of negative test partitions (`TD_ISTQB_NEGATIVE`) in `test_steps.py` and `test_enum_parity.py`, scheduled for remediation in Step 1.

## Remaining
- Step 1: Technical debt eradication & ARB localization in `studio_dashboard_view.dart`, `app_*.arb`, and `test_steps.py`.
- Step 2: SSOT `StepFilterScope` enum definition and cross-language parity testing in `enums.py`, `enums.dart`, and `test_enum_parity.py`.
- Step 3: Seed Vault causal blueprint consolidation and database synchronization in `seed_data.json` and integration tests.
- Step 4: Backend service and router server-side filtering in `workflow_service.py` and `steps.py`.
- Step 5: Flutter client, controller, and Dumb Painter view integration in `studio_client.dart`, `studio_controller.dart`, and `studio_dashboard_view.dart`.
- Step 6: Two-Stage Quality Gate audit and persistence verification across backend and frontend suites.
- Post-Implementation Gates: Golden Master audit, Tier 2 Hardening (Backend & Frontend), Pre-Delete audit, Semantic Coverage audit, As-Built Architectural Sync (`/tier7-describe-architecture`), and Final Plan Audit (`/tier8-audit-plan`).

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md]
```
