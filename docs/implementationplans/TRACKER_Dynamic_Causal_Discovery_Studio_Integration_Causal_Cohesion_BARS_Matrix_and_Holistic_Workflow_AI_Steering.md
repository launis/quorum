# Tracker: Dynamic Causal Discovery Studio Integration, Causal Cohesion BARS Matrix, and Holistic Workflow AI Steering

@[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_Causal_Discovery_Studio_Integration_Causal_Cohesion_BARS_Matrix_and_Holistic_Workflow_AI_Steering.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_Causal_Discovery_Studio_Integration_Causal_Cohesion_BARS_Matrix_and_Holistic_Workflow_AI_Steering.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_Causal_Discovery_Studio_Integration_Causal_Cohesion_BARS_Matrix_and_Holistic_Workflow_AI_Steering.md] @[docs/implementationplans/TRACKER_Dynamic_Causal_Discovery_Studio_Integration_Causal_Cohesion_BARS_Matrix_and_Holistic_Workflow_AI_Steering.md]`
  - [x] Step 1: Pre-Implementation Cleanups
  - [x] Step 2: Seed Data Vault Mutation
  - [x] Step 3: Backend Deterministic BARS Evaluation
  - [x] Step 4: Frontend Localization and Studio Step Symmetry
  - [x] Step 5: Frontend Specialist Causal Source Selector
  - [x] Step 6: Universal Quality Gate and Cross-System Audit
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_Causal_Discovery_Studio_Integration_Causal_Cohesion_BARS_Matrix_and_Holistic_Workflow_AI_Steering.md] @[docs/implementationplans/TRACKER_Dynamic_Causal_Discovery_Studio_Integration_Causal_Cohesion_BARS_Matrix_and_Holistic_Workflow_AI_Steering.md]`

### Post-Implementation Gates
- [x] **[OK] Golden Master & Test Restoration Audit**: Verified no @pytest.mark.skip or commented-out tests exist in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Successfully passed `backend_audit_loop.py backend_v2 --test --ast-strict` with 5,348 passed tests, 97.76% coverage, Ruff clean, MyPy strict clean, and AST strict guardrails passed.
  - [x] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]
  - [x] @[backend_v2/services/orchestrator/dag_executor.py]
  - [x] @[backend_v2/services/studio/workflow_service.py]
  - [x] @[backend_v2/settings.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Successfully passed `flutter_audit_loop.py client_app_v2/ --build` with code generation, Dart guardrails, formatting, and 0 analyzer errors.
  - [x] @[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]
  - [x] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]
  - [x] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart]
- [x] **[OK] Pre-Delete Audit**: Verified no orphaned symbols or broken dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verified line coverage >90% (97.76% overall, 100% on CausalCohesionEvaluator).

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Dynamic_Causal_Discovery_Studio_Integration_Causal_Cohesion_BARS_Matrix_and_Holistic_Workflow_AI_Steering.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_Causal_Discovery_Studio_Integration_Causal_Cohesion_BARS_Matrix_and_Holistic_Workflow_AI_Steering.md] @[ki_god_code_prevention.md] @[ki_topological_engine.md] @[ki_unified_matrix_scoring_strictness.md] @[ki_workflow_context_governance.md] @[ki_zero_permissive_typing.md] @[ki_dag_engine_dto_projection_rules.md] @[ki_dual_axis_localization_architecture.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the decomposition and isolation of causal cohesion evaluation into pure, stateless service `CausalCohesionEvaluator` (`backend_v2/services/orchestrator/causal_cohesion_evaluator.py`), keeping `dag_executor.py` decoupled from calculation complexity.
     - `@[ki_topological_engine.md]`: Document the deterministic evaluation of topological graph metrics (`logical_cohesion_score`, `cycle_detected`, `isolated_concept_count`) from `AntiFluffAuditDTO` into BARS 1–5 scale levels, with cycle defect grounding and zero-node Novice floor protection.
     - `@[ki_unified_matrix_scoring_strictness.md]`: Document integration of `matrix_causal_cohesion` into `UnifiedScoringEngine` with workflow `default_strictness_level` (calibrated 0% baseline for holistic audit), and the Cumulative Guttman Invariant ($L_1 \subset L_2 \subset L_3 \subset L_4 \subset L_5$).
     - `@[ki_workflow_context_governance.md]`: Document 100% engine symmetry in Studio (visible Causal Discovery steps), Append-to-Zone-B authoring flow, Full-Duplex Reactive Synchronization between `causal_source_step_id` and `depends_on`, defensive dropdown value guards, and cascading step deletion referential integrity.
     - `@[ki_zero_permissive_typing.md]`: Document `CausalCohesionEvaluationDTO`, eradication of naked dicts in `TraceEvent` for context updates (`GlobalContextVarsDTO`), mandatory non-nullable `matrix_block_id: str` without lazy fallbacks, and typed `ExecutionStatus.PASSED` enum checks.
     - `@[ki_dag_engine_dto_projection_rules.md]`: Document `_evaluated_causal_sources: set[str]` execution guard in `DAGExecutor` preventing race conditions and duplicate atom emission when multiple Zone B specialists reference the same causal source, and atomic `_update_lock` context reconciliation without `state_reducer.py` mutation.
     - `@[ki_dual_axis_localization_architecture.md]`: Document Axis 1 compile-time `.arb` localization for Studio causal source dropdown (`studioWorkflowCausalSourceLabel`, `studioWorkflowCausalSourceNone`) with 100% Finnish/English parity, and 100% Flutter Theme Sovereignty (eradication of all 22 raw `TextStyle` instantiations).
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register `backend_v2/services/orchestrator/causal_cohesion_evaluator.py` under orchestrator services.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/02_matrix_reasoning_and_evaluation.md`, `docs/architecture/03_cognitive_orchestration_engine.md`, and `docs/architecture/04_server_driven_ui_and_presentation.md` describing newly established invariants in present tense without historical language or plan IDs.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_Causal_Discovery_Studio_Integration_Causal_Cohesion_BARS_Matrix_and_Holistic_Workflow_AI_Steering.md] @[docs/implementationplans/TRACKER_Dynamic_Causal_Discovery_Studio_Integration_Causal_Cohesion_BARS_Matrix_and_Holistic_Workflow_AI_Steering.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Strict Execution Mode**: Do not write domain code without slash command invocation `/tier2-execute` or `/tier2-execute --full-auto`.
- **Quality Gates**: After each logical step, run `uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict` for Python files and `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build` for Flutter files.
- **Atomic Commits**: Follow Conventional Commits syntax (`<type>(<scope>): <imperative summary in lowercase>`) and commit modified files atomically after passing quality gates.
- **Double-Entry Bookkeeping**: Mark completed steps with `[x]` in this tracker and keep `# Session Handover Context` updated.
- **Execution Mode**: The plan has already been vetted through Tier 0 research; run with `/tier2-execute --full-auto`.

## Requirements Traceability Matrix
| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Pre-Implementation Cleanups & SSOT Settings Thresholds (annotate load_seed_data return type, add SSOT settings fields in settings.py, and fix ExecutionStatus enum check in dag_executor.py) | Step 1 | Done |
| REQ-002 | Workflow Cloning Relational Integrity & Causal Source Remapping (remap causal_source_step_id in workflow_cloner.dart and workflow_service.py with fail-fast validation) | Step 1 | Done |
| REQ-003 | Flutter Theme Sovereignty & Safe ID Truncation (replace all 22 raw TextStyle instantiations with Theme tokens and guard substring clippings in workflow_steps_tab.dart and workflow_step_card.dart) | Step 1 | Done |
| REQ-004 | Seed Data PromptBlock BARS Matrix Mutation (add matrix_causal_cohesion blk_c0a1e50000000001 with 5 BARS scales and deterministic TDA assertions tda_c0a1e50000000001..05, excluded from LLM criteria_block_ids) | Step 2 | Done |
| REQ-005 | Seed Data Holistic Workflow AI Steering Integration (add sr_f1c1d71000000002 at position 10 in wf_9d68c573802341db with causal pre-wiring, wire into funnel sr_5f3dd7712a7f4bb3, and set default_strictness_level: 0) | Step 2 | Done |
| REQ-006 | Seed Data Matrix Synthesis Groups & Report Layout Configuration (add comparison group in prf_5d6e7f8091a2b3c4 and prf_06b1d71000000001, exclude printable_sources_block from target_block_order, and set show_sources_summary_box: false) | Step 2 | Done |
| REQ-007 | Seed Regression Tests & Calibration Baseline Parity (update test_competency_workflows_seed.py assertions for 14-node workflow topology, 9 Zone B specialists, 7 matrix groups, and 0% strictness level) | Step 2 | Done |
| REQ-008 | Pure Stateless CausalCohesionEvaluator Service (implement CausalCohesionEvaluator with mandatory non-nullable matrix_block_id, Cumulative Guttman Invariant, zero-node Novice floor grounding, and UnifiedScoringEngine delegation) | Step 3 | Done |
| REQ-009 | Idempotent DAG Fusion Execution & Context Updates (implement _evaluated_causal_sources guard in DAGExecutor and emit typed GlobalContextVarsDTO TraceEvent for context updates) | Step 3 | Done |
| REQ-010 | Causal Cohesion BARS Unit Tests (write comprehensive unit tests in test_causal_cohesion_scoring.py verifying all 5 BARS thresholds, zero-node grounding, cyclic defect grounding, concurrent execution idempotency, and dynamic matrix binding) | Step 3 | Done |
| REQ-011 | Dual-Axis Studio Localization Parity (add studioWorkflowCausalSourceLabel and studioWorkflowCausalSourceNone keys to app_fi.arb and app_en.arb, and run flutter gen-l10n) | Step 4 | Done |
| REQ-012 | Studio 100% Engine Card Symmetry & Append-to-Zone-B Lifecycle (ensure all execution nodes are visible in WorkflowStepsTab, update _findFirstZoneCIndex, and maintain cascading referential integrity on node removal) | Step 4 | Done |
| REQ-013 | Studio Specialist Causal Source Selector & Defensive Value Guard (add DropdownButtonFormField for causalSourceStepId in WorkflowStepCard, implement defensive initialValue guard, and enforce Full-Duplex Reactive Synchronization) | Step 5 | Done |
| REQ-014 | Studio Causal Source Widget Tests (update workflow_step_card_test.dart verifying dropdown rendering, defensive value guard, dependency synchronization, and chip deselection auto-reset) | Step 5 | Done |
| REQ-015 | Universal Quality Gate & Cross-System Completion Gate (execute backend_audit_loop.py, flutter_audit_loop.py, audit_database_atoms.py, and audit_markdown_boundaries.py) | Step 6 | Done |

# Session Handover Context

## Achieved
- Step 1: Pre-Implementation Cleanups & SSOT Settings Thresholds (commit `3abdd4207`).
- Step 2: Seed Data Vault Mutation & Topology Integration (commit `b4e8c95af`).
- Step 3: Backend Deterministic BARS Evaluation & Idempotent Fusion (commit `61670d531`).
- Step 4: Frontend Localization and Studio Step Symmetry (commit `b5c3feabe`).
- Step 5: Frontend Specialist Causal Source Selector & Full-Duplex Reactive Sync (commit `72fe68b14`).
- Step 6: Universal Quality Gate & Cross-System Audit (all 5,348 backend unit tests passing, 97.76% coverage, Flutter audit and test suite passing, database atom audit 0 errors, markdown boundaries 0 errors).

## Learned
- Causal discovery steps must be treated as first-class visible steps in Quorum Studio with 100% engine symmetry, using Studio's natural Append-to-Zone-B model to guarantee upstream ordering without speculative drag-and-drop machinery.
- BARS causal cohesion matrix (`matrix_causal_cohesion`, `blk_c0a1e50000000001`) is a pure system-evaluated metric matrix evaluated deterministically from topological graph metrics, strictly excluded from LLM `criteria_block_ids` (0-token contract).
- Idempotency guard `_evaluated_causal_sources: set[str]` in `DAGExecutor` prevents concurrent Zone B specialists from duplicating evaluation or polluting `execution_trace`.
- Mandatory non-nullable `matrix_block_id: str` in `CausalCohesionEvaluator` upholds `zero_service_layer_fallbacks` and prevents silent matrix ID drift.
- Workflow cloning requires remapping `causal_source_step_id` with fail-fast validation, eradicating lazy `??` fallbacks and preventing fatal HTTP 422 errors on clone persistence.
- AST markdown boundary audit (`scripts/audit_markdown_boundaries.py`) verifies exact node boundaries on `.py` line references and SSOT enum consistency.

## Remaining
- Post-Execution System 2 Red-Team Audit via `/tier8-audit-plan`.

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Dynamic_Causal_Discovery_Studio_Integration_Causal_Cohesion_BARS_Matrix_and_Holistic_Workflow_AI_Steering.md] @[docs/implementationplans/TRACKER_Dynamic_Causal_Discovery_Studio_Integration_Causal_Cohesion_BARS_Matrix_and_Holistic_Workflow_AI_Steering.md]
```
