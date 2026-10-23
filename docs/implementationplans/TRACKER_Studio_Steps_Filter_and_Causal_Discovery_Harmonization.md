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

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md]`
  - [x] Step 1: TECHNICAL DEBT ERADICATION & ARB LOCALIZATION
  - [x] Step 2: SSOT ENUM DEFINITION & CROSS-LANGUAGE PARITY
  - [x] Step 3: SEED VAULT CAUSAL BLUEPRINT CONSOLIDATION
  - [x] Step 4: BACKEND SERVICE & ROUTER SERVER-SIDE FILTERING
  - [x] Step 5: FLUTTER CLIENT, CONTROLLER & DUMB PAINTER VIEW
  - [x] Step 6: TWO-STAGE QUALITY GATE AUDIT & PERSISTENCE VERIFICATION
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] --gate backend`.
  - [x] @[backend_v2/models/enums.py]
  - [x] @[backend_v2/api/routers/studio/steps.py]
  - [x] @[backend_v2/services/studio/workflow_service.py]
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
| `REQ-STP-003` | Define SSOT enum `StepFilterScope` (`specialists`, `system_core`, `all`) with full cross-language parity in Python and Dart | Step 2 | [x] Complete |
| `REQ-STP-004` | Add bidirectional unit parity test and missing member negative test in `test_enum_parity.py` | Step 2 | [x] Complete |
| `REQ-STP-005` | Harmonize canonical universal Causal Discovery blueprint `sp_c4a5a1d15c00438a` with dynamic input agnosticism in `seed_data.json` | Step 3 | [x] Complete |
| `REQ-STP-006` | Prune redundant duplicate blueprints `sp_01b1d7100000ca01` through `sp_06b1d7100000ca06` from Seed Vault and sync local database | Step 3 | [x] Complete |
| `REQ-STP-007` | Implement server-side scope filtering in `StudioWorkflowService.list_steps` via exhaustive Python 3.12+ `match scope:` | Step 4 | [x] Complete |
| `REQ-STP-008` | Expose `scope` query parameter on `GET /studio/steps/` router delegating to `StudioWorkflowService` with negative test coverage | Step 4 | [x] Complete |
| `REQ-STP-009` | Wire `StudioClient.getSteps({StepFilterScope scope})` to pass `scope` query parameter to backend | Step 5 | [x] Complete |
| `REQ-STP-010` | Update `StepsController` with `_scope` state, `currentScope` getter, and `setScope` method triggering backend re-fetch | Step 5 | [x] Complete |
| `REQ-STP-011` | Render interactive `SegmentedButton<StepFilterScope>` in `_buildStepsTab` and render blueprints as pure Dumb Painter | Step 5 | [x] Complete |
| `REQ-STP-012` | Implement comprehensive widget test `studio_dashboard_steps_tab_test.dart` verifying filter transitions and empty states | Step 5 | [x] Complete |
| `REQ-STP-013` | Execute Two-Stage Quality Gate audits (`backend_audit_loop.py` with `--ast-strict`, `flutter_audit_loop.py` with `--build`, technical debt audit) | Step 6 | [x] Complete |

# Session Handover Context

## Achieved
- Successfully implemented all 6 steps of `IMPLEMENTATION_PLAN_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md` in Full-Auto Continuous Mode.
- Step 1: Remediated pre-flight technical debt (`DGR003` in `studio_dashboard_view.dart`, `TD_ISTQB_NEGATIVE` in `test_steps.py`).
- Step 2: Established cross-language SSOT `StepFilterScope` enum in Python and Dart with automated bidirectional AST parity tests.
- Step 3: Pruned 6 redundant static causal steps (`sp_01`..`sp_06`) and consolidated into canonical universal blueprint `sp_c4a5a1d15c00438a` (`step_causal_discovery`), validated via dry-run and atom audits, reseeded local database.
- Step 4: Implemented server-side scope filtering in `StudioWorkflowService.list_steps` via exhaustive `match scope:` and exposed `scope` query parameter on `GET /studio/steps/` with 100% test coverage.
- Step 5: Updated `StudioClient.getSteps`, `StepsController.setScope()`, and rendered interactive `SegmentedButton<StepFilterScope>` in `StudioDashboardView` with Dumb Painter architecture and comprehensive widget tests.
- Step 6: Verified full backend audit loop with strict AST guardrails (10/10 gates passed, 0 violations, >90% coverage), Flutter audit loop with build runner, zero technical debt across 6 targets and 1-hop callers, and verified markdown boundaries.

## Learned
- In `backend_audit_loop.py`, invoking the loop directly on integration test files triggers `pytest-cov` warning `module-not-imported` since tests aren't imported as library modules; invoking the loop on domain targets runs their associated unit tests with precise coverage mapping.
- Flutter `SegmentedButton` with Dumb Painter pattern provides instant, deterministic server-side filtering without leaking presentation filtering or state mutation into UI widgets.

## Remaining
- Post-Implementation Gates:
  - Golden Master & Test Restoration Audit
  - Tier 2 Hardening (Backend): `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] --gate backend`
  - Tier 2 Hardening (Frontend): `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] --gate frontend`
  - Pre-Delete Audit & Semantic Coverage Verification
- Documentation & Knowledge Item Update:
  - As-Built Architectural Sync (`/tier7-describe-architecture`)
- Final Plan Audit:
  - System 2 Red-Team Audit (`/tier8-audit-plan`)

## Resume Command
```powershell
uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md] --gate backend
```
