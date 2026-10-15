# IMPLEMENTATION PLAN: Dynamic Causal Discovery Studio Integration, Causal Cohesion BARS Matrix, and Holistic Workflow AI Steering

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

## Objective
Seamlessly integrate autonomous causal discovery into Quorum's architectural stack by:
1. Enforcing 100% architectural symmetry across all 4 execution engines (specifically and exhaustively: `EngineType.TDA`, `EngineType.SYNTHESIS`, `EngineType.PROMPT`, `EngineType.CAUSAL_DISCOVERY`): Causal Discovery steps are treated strictly as first-class visible steps in Quorum Studio without hidden step filtering or ad-hoc toggle switches. Downstream specialist cards configure their causal source explicitly via a clean, typed dropdown selector (`causal_source_step_id`), with Full-Duplex Reactive Synchronization between `depends_on` and `causal_source_step_id`, preserving full WYSIWYG transparency and Single Source of Truth integrity.
2. Authoring a first-class affirmative BARS 1–5 scale matrix for causal argument cohesion (`matrix_causal_cohesion`, `blk_c0a1e50000000001`) directly in `backend_v2/seed/seed_data.json` with 5 deterministic TDA assertion IDs (`tda_c0a1e50000000001` through `tda_c0a1e50000000005`). This matrix is a pure system-evaluated metric matrix, strictly excluded from all LLM `criteria_block_ids` (preserving the 0-token contract, avoiding prompt bloat, eliminating duplicate atom collisions, and avoiding lexical quote errors). It is evaluated deterministically from topological graph metrics via a dedicated, pure, stateless calculation service `CausalCohesionEvaluator` (strictly adhering to `ki_god_code_prevention.md` and keeping `dag_executor.py` pure). Cohesion evaluation is idempotent per causal discovery step and gated by an in-memory set guard `_evaluated_causal_sources: set[str]` in `DAGExecutor`, preventing duplicate evaluation and race conditions when multiple Zone B specialists (specifically: `sr_4d2272d8b4864847` and `sr_f1c1d71000000002`) reference the same `causal_source_step_id` (`sr_c4a5a1d15c00438a`). Furthermore, `dag_executor.py#L1323-L1363` automatically reconciles context updates and merges `GlobalContextVarsDTO.evaluative_matrices` incrementally within its atomic `_update_lock` event reduction loop without modifying `state_reducer.py`.
3. Moving all threshold constants and default matrix IDs to `backend_v2/settings.py` (SSOT) to eradicate magic numbers and hardcoded default database IDs from execution logic.
4. Enforcing Zero Naked Dicts (EPIC_149 / EPIC_152) by emitting typed `GlobalContextVarsDTO` event payloads in `TraceEvent` for context updates.
5. Adding AI Steering Evaluation (`sp_06c1d71000000001`, Tekoälyohjauksen Arvioija) into the "Kokonaisvaltainen Auditointi" workflow (`wf_9d68c573802341db`) in `backend_v2/seed/seed_data.json` as Step 10, pre-wired with `"causal_source_step_id": "sr_c4a5a1d15c00438a"` and `"depends_on": ["sr_f0a26d17cc9b48a7", "sr_c4a5a1d15c00438a"]`.
6. Establishing the Master Archetype Principle: `wf_9d68c573802341db` ("Kokonaisvaltainen Auditointi") serves as the sovereign reference template containing the full superset of evaluative dimensions (AI steering, causal analysis, factual integrity, process ownership, cognitive reflection) from which specialized sub-workflows (specifically: `wf_06a1d71000000001` "Tekoälyn Käytön ja Ohjauksen Auditointi") are derived and calibrated.
7. Binding the new causal cohesion BARS matrix to `UnifiedScoringEngine` across both "Kokonaisvaltainen Auditointi" and "Tekoälyn Käytön ja Ohjauksen Auditointi" so that argument cohesion yields official competence scores in Quorum Studio and tabular exports.
8. Setting initial strictness level for "Kokonaisvaltainen Auditointi" (`wf_9d68c573802341db`) to `default_strictness_level: 0` (0% Vapaa / Free, linear baseline evaluation) in `backend_v2/seed/seed_data.json`.
9. Hiding "Lähdeluettelo ja viitteet" (bibliography / references) from the report structure of "Kokonaisvaltainen Auditointi" profile (`prf_5d6e7f8091a2b3c4`) in `backend_v2/seed/seed_data.json` by removing `"printable_sources_block"` from `target_block_order` and setting `"show_sources_summary_box": false`.
10. Ensuring Workflow Cloning Relational Parity: When cloning workflows via `client_app_v2/lib/features/studio/utils/workflow_cloner.dart` or `backend_v2/services/studio/workflow_service.py` (`clone_workflow`), remap `causal_source_step_id` using the newly generated step ID mapping (eradicating lazy `?? oldCausalSource` fallbacks and failing fast with `WORKFLOW_CLONE_FAILED` on missing keys), and validate that any non-empty `causal_source_step_id` exists in `validNewIds` and `depends_on`, preventing fatal HTTP 422 `VALIDATION_FAILED` crashes on saving cloned workflows.
11. Studio Append-to-Zone-B Lifecycle Governance & Defensive Dropdown Guard: Pruning ad-hoc step reordering controls (satisfying the 30% Deletion Invariant) in favor of Quorum Studio's deterministic Append-to-Zone-B model (`_findFirstZoneCIndex` excluding `EngineType.causalDiscovery`), where chronological authoring naturally places upstream causal steps ahead of consuming specialist steps (`allSteps.sublist(0, index)`). `WorkflowStepCard` implements a defensive `initialValue` guard (`(stepDef.causalSourceStepId != null && allowedCausalIds.contains(stepDef.causalSourceStepId)) ? stepDef.causalSourceStepId : null`) on `DropdownButtonFormField`, preventing Flutter assertion red-screen crashes on historical or malformed data.
12. Enforcing No-Fallback Evaluator Signature: Enforcing mandatory, strictly typed `matrix_block_id: str` (no `| None = None` or lazy default coalescing) in `CausalCohesionEvaluator.evaluate_causal_cohesion`, dynamically binding `atom.matrix_id = matrix_block_id`, upholding `zero_service_layer_fallbacks` and `the_duct_tape_ban`.

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **@[backend_v2/settings.py#L54-L968]** | Hardcoded magic threshold floats (`0.40, 0.60, 0.80, 0.90, 0.20, 0.10, 0.05`) in scoring logic. | Centralized SSOT configuration in `Settings`: `causal_cohesion_matrix_block_id`, `causal_cohesion_l2_threshold` .. `l5_threshold`, `causal_cohesion_l3_isolation_max` .. `l5_isolation_max`. | Pruned speculative dynamic weighting matrices; pure numeric constants. | AST strict verification and settings instantiation test. |
| **[NEW] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]** | Monolithic bloat in `dag_executor.py` violating `ki_god_code_prevention.md`, hardcoded DB ID (`"blk_c0a1e50000000001"`), zero-node graph score inflation to BARS 5.0, LLM token leakage, arbitrary atom IDs breaking SDUI table rendering, optional default parameter `matrix_block_id: str \| None = None` forcing lazy fallback duct-tape. | Pure, stateless `CausalCohesionEvaluator` reading thresholds from centralized configuration. Enforces `total_nodes > 0` for Levels 2–5, grounding zero-node graphs strictly to BARS 1.00 Novice floor. Enforces the Cumulative Guttman Invariant ($L_1 \subset L_2 \subset L_3 \subset L_4 \subset L_5$). Mandatory, strictly typed `matrix_block_id: str` without default value. Dynamically binds `atom.matrix_id = matrix_block_id` across all emitted `AtomResultDTO` instances. Locks deterministic `CAUSAL_COHESION_TDA_IDS` (`tda_c0a1e50000000001` through `tda_c0a1e50000000005`) mapped to Levels 1–5 as `tda_id`. Returns typed `CausalCohesionEvaluationDTO` containing `atom_results`, `level_stats` (`dict[str, LevelStatsDTO]`), and `score_result` computed via `UnifiedScoringEngine` using workflow `strictness_level`. Adheres to `validate_cognitive_vs_system_state` (`contextual_override=True, source_quote=None`). | Pruned default fallback coalescing chains; single pure compute service; pruned abstract factory or multi-layer strategy hierarchy. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/causal_cohesion_evaluator.py --test --ast-strict`. |
| **@[backend_v2/services/orchestrator/dag_executor.py#L129-L281]** | Monolithic evaluation bloat, enum `.value` check (`atom.status.value == "PASSED"`), concurrent Zone B race condition executing fusion twice and polluting `execution_trace` with 10 duplicate atoms, naked dict in `TraceEvent` (`content={"evaluative_matrices": ...}`), erroneous assumptions about modifying `state_reducer.py`. | Idempotent causal source set guard `_evaluated_causal_sources: set[str]` in `DAGExecutor.execute()`. Cohesion evaluated strictly once per causal source graph. Check `atom.status == ExecutionStatus.PASSED`. Emit typed `GlobalContextVarsDTO(evaluative_matrices={eval_dto.matrix_block_id: eval_dto.score_result.score})` in `TraceEvent` with `metadata=TraceEventMetadataDTO(is_context_update=True)` (Zero Naked Dicts, EPIC_149/152). In `dag_executor.py#L1323-L1363`, the existing `_update_lock` context update handler automatically reconciles `TraceEvent(metadata=TraceEventMetadataDTO(is_context_update=True), content=GlobalContextVarsDTO(...))` and merges `parsed_gvars.evaluative_matrices` into `global_context_vars.evaluative_matrices` atomically; combined with `_evaluated_causal_sources`, idempotency is guaranteed without requiring edits to `state_reducer.py`. | Pruned orchestrator-level calculation helpers and pruned spurious edits to `state_reducer.py`; `DAGExecutor` remains pure execution controller with simple in-memory set tracking. | `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py --test --ast-strict`. |
| **@[backend_v2/seed/seed_data.json#L20230-L20260]** | Adding deterministic matrix to LLM `criteria_block_ids`, unregistered PromptBlock collections, raw XML tags inside prompt blocks, arbitrary TDA IDs breaking SDUI table distribution mapping. | Opaque Stripe ID standard (`blk_c0a1e50000000001`), Track A BARS developmental scale (1.0 to 5.0) with 5 deterministic TDA assertions (`tda_c0a1e50000000001` through `tda_c0a1e50000000005`), all `inverse_evidence: false`. Bind to profiles `prf_5d6e7f8091a2b3c4` and `prf_06b1d71000000001`, but strictly **EXCLUDE from LLM `criteria_block_ids`** (0-token contract). | 0 duplicate LLM extraction atoms; pure presentation binding; pruned redundant duplicate prompt blocks. | `uv run python scripts/audit_database_atoms.py --strict` (0 errors). |
| **@[backend_v2/seed/seed_data.json#L20250-L20550]** | Unspecified step index, missing causal source in Master Archetype, hardcoded step counts, missing funnel dependencies, arbitrary initial strictness level (50%). | Insert `sr_f1c1d71000000002` (AI Steering) as **Step 10** in `wf_9d68c573802341db` with `"causal_source_step_id": "sr_c4a5a1d15c00438a"` and `"depends_on": ["sr_f0a26d17cc9b48a7", "sr_c4a5a1d15c00438a"]`. Wire into funnel `sr_5f3dd7712a7f4bb3`. Set initial evaluation strictness `"default_strictness_level": 0` (0% Vapaa / Free linear baseline). | Pruned bifurcated workflow templates; single sovereign reference workflow. | `uv run python backend_v2/seed/run_seed.py local --dry-run`. |
| **@[backend_v2/seed/seed_data.json#L23200-L23400]** | Adding matrix block IDs to `matrix_visible_columns` causing `ValueError` in `matrix_summary_table_adapter.py#L74-L80` (where visible columns are strictly `ReportMatrixColumn` enum members), unwanted references / bibliography section in holistic audit report. | Add a dedicated matrix comparison group in `matrix_synthesis_groups` containing `blk_7d8e9f0a1b2c3d4e` and `blk_c0a1e50000000001` in `prf_5d6e7f8091a2b3c4` and `prf_06b1d71000000001`, while strictly preserving `STANDARD_MATRIX_VISIBLE_COLUMNS` in `matrix_visible_columns`. In `prf_5d6e7f8091a2b3c4`, remove `"printable_sources_block"` from `target_block_order` (hiding 'Lähdeluettelo ja viitteet' from report structure) and set `"show_sources_summary_box": false`. | Pruned separate presentation adapters; standard profile schema. | `uv run python backend_v2/seed/run_seed.py local --dry-run`. |
| **@[backend_v2/tests/unit/services/test_competency_workflows_seed.py#L54-L63]** | Missing return type on line 53 `load_seed_data()` causing 20 MyPy strict errors (`[no-untyped-def]`). | Annotate `load_seed_data() -> dict[str, Any]:` in Phase 1 before running seed tests. | Pruned redundant helper shims; pure typed fixture. | `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/test_competency_workflows_seed.py --test --ast-strict`. |
| **@[backend_v2/tests/unit/services/test_competency_workflows_seed.py#L69-L158]** | Hardcoded 13-step assertion (`assert len(mono_wf.steps) == 13`), hardcoded 6-group assertion, missing `sr_f1c1d71000000002` in line 121 check. | Master Archetype Principle: Assert exact 14-step topology for `wf_9d68c573802341db`, include `sr_f1c1d71000000002` in `zone_b_step_ids`, update line 121 check to `step.id in ('sr_4d2272d8b4864847', 'sr_f1c1d71000000002')`, assert 7 matrix groups in `mono_prf`, assert `sr_5f3dd7712a7f4bb3` depends on all 9 Zone B specialists, and assert `"printable_sources_block" not in mono_prf.target_block_order`. | Pruned redundant parallel test fixtures; maintain single authoritative seed topology regression test. | `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/test_competency_workflows_seed.py --test --ast-strict`. |
| **@[backend_v2/tests/unit/services/test_competency_workflows_seed.py#L301-L323]** | Hardcoded strictness assertion rejecting 0% (`assert wf_model.default_strictness_level in (50, 70)`). | Assert `wf_model.default_strictness_level in (0, 50, 70)` and verify `wf_9d68c573802341db.default_strictness_level == 0`. | Pruned speculative strictness overrides; assert calibrated seed default. | `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/test_competency_workflows_seed.py --test --ast-strict`. |
| **@[backend_v2/tests/unit/services/studio/test_workflow_service.py#L963-L986]** | Missing line bounds in Target Files, missing row in 5-Column Table, untested `causal_source_step_id` cloning behavior in `StudioWorkflowService`. | Append unit test `test_clone_workflow_remaps_causal_source_step_id` asserting that cloning a workflow containing a specialist step with `causal_source_step_id` remaps the causal pointer to the new step ID and passes `StepRule.validate_step_rule_consistency`. | Pruned redundant mock configurations; reuse existing in-memory fixtures. | `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/studio/test_workflow_service.py --test --ast-strict`. |
| **@[client_app_v2/lib/features/studio/utils/workflow_cloner.dart#L65-L146]** | Omitting `causal_source_step_id` from cloning, or using lazy fallback `idMap[old] ?? old` that retains pre-clone step IDs and causes silent cross-workflow contamination or 422 errors on save. | Phase B executes direct remapping: `step['causal_source_step_id'] = idMap[oldCausalSource]`. If unmapped, fail immediately with `AppException(WORKFLOW_CLONE_FAILED)`. Phase C strictly validates that `causal_source_step_id` exists in `validNewIds` and `depends_on`. | Pruned lazy fallback coalescence (`??`); pure Fail-Fast key-level structural remapping. | Unit test in `workflow_cloner_test.dart` verifying causal source remapping and validation. |
| **@[backend_v2/services/studio/workflow_service.py#L331-L449]** | Omitting `causal_source_step_id` from `new_step` update in `clone_workflow`, causing `StepRule.validate_step_rule_consistency` 422 failures. | Remap `causal_source_step_id` via `sr_mapping[step_cfg.causal_source_step_id]` preserving relational integrity with `new_depends`. | Pruned complex graph cloners; single dictionary lookup. | Unit test in `test_workflow_service.py` asserting cloned workflow with causal source passes validation and persists cleanly. |
| **@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart#L1-L190]** | Hiding or filtering infrastructure engines from the step cards list, premature Zone C cut-off via raw `isSystemCore` checks, raw `TextStyle` instantiations (lines 141, 160), unguarded `.substring(0, 16)` calls (lines 43, 73), unverified `_deleteStep` cascade. | 100% Engine Symmetry: render ALL workflow steps as first-class visible cards in Zone B/C without filtering; determine Zone C strictly by non-causal system core funnel steps (`bp.isSystemCore && bp.engineType != EngineType.causalDiscovery`); maintain `_deleteStep` cascading referential integrity (cleaning `dependsOn` and resetting `causalSourceStepId`); sequential 1-based card display numbering using `Theme.of(context).textTheme`; safe opaque ID generation. | Pruned step-hiding filters, shadow collections, or bifurcated display pipelines. Pruned speculative reordering machinery: Studio's natural Append-to-Zone-B lifecycle preserves topological construction without drag handles or re-routing logic. | Widget test in `workflow_steps_tab_test.dart` verifying visible rendering and deletion cascade. |
| **@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L1-L591]** | Raw `TextStyle` (20 instances), partial dependency syncing on dropdown changes, deselecting chips without clearing `causalSourceStepId` causing 422 `VALIDATION_FAILED` crashes on backend persistence, passing unchecked `stepDef.causalSourceStepId` to `DropdownButtonFormField` when absent from `items`, triggering fatal Flutter red-screen `AssertionError`. | 100% Theme Sovereignty; Full-Duplex Reactive Synchronization: dropdown changes atomically prune old causal ID and append new ID to `dependsOn`; unchecking chip for active causal source auto-resets `causalSourceStepId = null`. Guard `initialValue`: if `causalSourceStepId` is not in allowed upstream causal steps (`allSteps.sublist(0, index)`), evaluate safely as `null`. Dynamic dropdown rendering on eligible non-causal steps when upstream causal discovery steps exist. | Pruned ad-hoc toggle switches, hardcoded blueprint ID lists, hidden step state synchronization shims, or magic background mutations. Pruned complex fallback error views; simple safe value selection. | Multi-scenario widget tests in `workflow_step_card_test.dart` asserting bidirectional sync and 0 validation errors. |
| **@[client_app_v2/lib/l10n/app_fi.arb#L1910-L1935]** | Hardcoded string literals in Dart widgets, missing localization keys in Finnish schema. | Strict Dual-Axis Localization: Axis 1 compile-time `.arb` strings for `studioWorkflowCausalSourceLabel` ("Kausaalipäättelyn lähde") and `studioWorkflowCausalSourceNone` ("Ei käytössä"). | Pruned unnecessary runtime translation helpers or fallback string dictionaries. | `flutter gen-l10n` build execution and `audit_flutter_theme_sovereignty.py`. |
| **@[client_app_v2/lib/l10n/app_en.arb#L2620-L2645]** | Asymmetrical translations, English fallback omission in localization schema. | Strict Dual-Axis Localization: Axis 1 compile-time `.arb` strings for `studioWorkflowCausalSourceLabel` ("Causal Discovery Source") and `studioWorkflowCausalSourceNone` ("None") with 100% Finnish parity. | Pruned manual string lookup shims. | `flutter gen-l10n` build execution and `audit_flutter_theme_sovereignty.py`. |
| **[NEW] @[backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py]** | Tautological mocking, happy-path-only testing, unasserted side-effects. | Comprehensive ISTQB boundary tests across all 5 BARS levels (1.0 to 5.0), cyclic graph defect grounding (exact 1.07 score at 70% strictness), zero-node edge case (exact 1.00 Novice floor), multi-step concurrent execution idempotency (preventing duplicate atom emission), dynamic `matrix_block_id` binding verification, and `UnifiedScoringEngine` integration. | Pruned redundant mock classes; use pure compute functions and in-memory fixtures. | Automated AST mutation testing and `backend_audit_loop.py --test --ast-strict` with 100% pass rate. |
| **[NEW] @[client_app_v2/test/features/studio/utils/workflow_cloner_test.dart]** | Untested causal source remapping in Dart cloner, risk of undetected `??` fallback regressions. | Unit tests verifying: 1) Cloned workflow remaps `causal_source_step_id` to new step ID, 2) Unmapped or invalid causal source step throws `AppException` with code `WORKFLOW_CLONE_FAILED`. | Standard unit test harness. | `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/utils/workflow_cloner_test.dart`. |
| **[NEW] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_steps_tab_test.dart]** | Missing widget test coverage for `WorkflowStepsTab`. | Widget tests verifying: 1) Causal discovery steps rendered as visible cards, 2) Zone C correctly identified by non-causal core steps, 3) `_deleteStep` cleanly cascading to prune `dependsOn` and reset `causalSourceStepId`. | Standard test harness; pruned duplicate test setups. | `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/widgets/workflow/workflow_steps_tab_test.dart`. |
| **@[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart#L450-L530]** | Skipped widget tests, untested dropdown callbacks, missing pumpAndSettle cycles, untested chip desynchronization edge cases. | Multi-scenario widget tests asserting: 1) Dropdown swap from Step A to Step B prunes Step A from `dependsOn`, 2) Unchecking active causal chip resets `causalSourceStepId` to `null`, 3) Dropdown defensive value guard resolves to `null` on invalid causal IDs. | Pruned duplicate test setup wrappers; re-use standardized `createTestWidget` harness. | `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart`. |

---

## Scope & Target Boundaries

### Target Files
- `[MODIFY] @[backend_v2/settings.py#L54-L968]` - Add SSOT threshold settings: `causal_cohesion_matrix_block_id`, `causal_cohesion_l2_threshold` .. `l5_threshold`, `causal_cohesion_l3_isolation_max` .. `l5_isolation_max`.
- `[NEW] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]` - Pure stateless calculation service implementing BARS 1–5 causal cohesion evaluation from topological metrics, strictly decoupled from `dag_executor.py` (`ki_god_code_prevention.md`). Enforces `total_nodes > 0` for Levels 2–5, locks deterministic `CAUSAL_COHESION_TDA_IDS`, declares mandatory non-nullable `matrix_block_id: str`, dynamically assigns `atom.matrix_id = matrix_block_id`, delegates score calculation to `UnifiedScoringEngine`, and returns `CausalCohesionEvaluationDTO`.
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor.py#L129-L281]` - Clean technical debt (line 163 enum check), add `_evaluated_causal_sources: set[str]` execution guard in `DAGExecutor.execute()`, delegate fusion evaluation to `CausalCohesionEvaluator` strictly once per causal discovery source, append atoms, and emit typed `GlobalContextVarsDTO` in `TraceEvent` with `metadata=TraceEventMetadataDTO(is_context_update=True)`. Existing `dag_executor.py#L1323-L1363` automatically reconciles context updates into `global_context_vars.evaluative_matrices` atomically without requiring edits to `state_reducer.py`.
- `[MODIFY] @[backend_v2/seed/seed_data.json#L20230-L20260]` - Add `matrix_causal_cohesion` PromptBlock (`blk_c0a1e50000000001`) with deterministic TDA assertion IDs (`tda_c0a1e50000000001` through `tda_c0a1e50000000005`). Note: strictly excluded from all LLM `criteria_block_ids`.
- `[MODIFY] @[backend_v2/seed/seed_data.json#L20250-L20550]` - Add step `sr_f1c1d71000000002` (Tekoälyohjauksen Arvioija) as Step 10 to `wf_9d68c573802341db` with causal pre-wiring, wire into funnel `sr_5f3dd7712a7f4bb3`, and set `"default_strictness_level": 0`.
- `[MODIFY] @[backend_v2/seed/seed_data.json#L23200-L23400]` - Add dedicated matrix comparison group in `matrix_synthesis_groups` containing `blk_7d8e9f0a1b2c3d4e` and `blk_c0a1e50000000001` in `prf_5d6e7f8091a2b3c4` and `prf_06b1d71000000001`, preserving `STANDARD_MATRIX_VISIBLE_COLUMNS` in `matrix_visible_columns`. In `prf_5d6e7f8091a2b3c4`, remove `"printable_sources_block"` from `target_block_order` and set `"show_sources_summary_box": false`.
- `[MODIFY] @[backend_v2/tests/unit/services/test_competency_workflows_seed.py#L54-L63]` - Annotate `load_seed_data() -> dict[str, Any]:` on line 53 to resolve 20 MyPy strict errors.
- `[MODIFY] @[backend_v2/tests/unit/services/test_competency_workflows_seed.py#L69-L158]` - Update `test_baseline_monolithic_workflow_preserved` to assert 14 steps, 9 Zone B specialists, line 121 check, 7 matrix groups, and excluded printable sources block.
- `[MODIFY] @[backend_v2/tests/unit/services/test_competency_workflows_seed.py#L301-L323]` - Update `test_output_profiles_scoring_configuration` to assert `wf_model.default_strictness_level in (0, 50, 70)` and `wf_9d68c573802341db.default_strictness_level == 0`.
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L963-L986]` - Add unit test `test_clone_workflow_remaps_causal_source_step_id` asserting cloned workflow with `causal_source_step_id` preserves relational integrity and passes backend validation.
- `[MODIFY] @[client_app_v2/lib/features/studio/utils/workflow_cloner.dart#L65-L146]` - Phase B executes direct remapping: `step['causal_source_step_id'] = idMap[oldCausalSource]`. If unmapped, fail immediately with `AppException(WORKFLOW_CLONE_FAILED)` (eradicating `?? oldCausalSource` fallback). Phase C strictly validates that `causal_source_step_id` exists in `validNewIds` and `depends_on`.
- `[MODIFY] @[backend_v2/services/studio/workflow_service.py#L331-L449]` - Add `causal_source_step_id` remapping via `sr_mapping[step_cfg.causal_source_step_id]` to `clone_workflow`.
- `[MODIFY] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart#L1-L190]` - Clean 2 raw `TextStyle` instances, ensure 100% visible step cards (zero step filtering), update Zone C index calculation, maintain `_deleteStep` cascading referential integrity, and use safe opaque ID generation on L43/L73.
- `[MODIFY] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L1-L591]` - Clean all 20 raw `TextStyle` instances (100% Theme Sovereignty), add explicit typed `causalSourceStepId` dropdown selector with Full-Duplex Reactive Synchronization (dropdown changes prune old causal ID; chip deselection auto-resets `causalSourceStepId = null`), and add defensive `initialValue` guard against non-upstream IDs.
- `[MODIFY] @[client_app_v2/lib/l10n/app_fi.arb#L1910-L1935]` - Add Finnish localization keys for causal source selector label and empty option.
- `[MODIFY] @[client_app_v2/lib/l10n/app_en.arb#L2620-L2645]` - Add English localization keys for causal source selector label and empty option.
- `[NEW] @[backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py]` - Unit tests for deterministic BARS evaluation from causal graph metrics, multi-step concurrent execution idempotency, dynamic `matrix_block_id` binding verification, and `UnifiedScoringEngine` integration.
- `[NEW] @[client_app_v2/test/features/studio/utils/workflow_cloner_test.dart]` - Add unit test verifying `causal_source_step_id` is remapped to new ID and validated with fail-fast exception on unmapped sources.
- `[NEW] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_steps_tab_test.dart]` - Widget tests asserting `WorkflowStepsTab` card visibility, Zone C indexing, and `_deleteStep` cascading referential integrity.
- `[MODIFY] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart#L450-L530]` - Widget tests asserting causal source selector dropdown behavior, selection swaps, defensive guard against invalid IDs, and chip deselection auto-reset.

---

## Technical Specifications & Architecture

### 1. New BARS Matrix: `matrix_causal_cohesion` (`blk_c0a1e50000000001`)
- **Category:** `matrix`, **Type:** `float`, **Slug:** `matrix_causal_cohesion`
- **Label:** `{"fi": "Argumentaation Kausaalinen Eheys ja Koheesio", "en": "Causal Reasoning & Argument Cohesion"}`
- **Description:** `{"fi": "Arvioi argumentaation rakenteellista eheyttä, päättelyketjujen koheesiota, kehäpäätelmien puuttumista ja irtonaisten väitteiden vähäisyyttä.", "en": "Evaluates argument structural integrity, inferential cohesion, cycle avoidance, and isolated claim absence."}`
- **Scales (1.0 to 5.0) & Deterministic TDA Assertions:**
  - **1.0:** Fragmentoitunut (Heikko) - Kehäpäätelmiä tai alle 40% looginen koheesio. Bound to deterministic TDA assertion ID `tda_c0a1e50000000001`.
  - **2.0:** Katkeileva (Välttävä) - Koheesio 40–59%, useita orpoja premissiketjuja. Bound to deterministic TDA assertion ID `tda_c0a1e50000000002`.
  - **3.0:** Looginen perusrunko (Kohtalainen) - Koheesio 60–79%, peruspremissit kytketty johtopäätöksiin, vähän saarekkeita. Bound to deterministic TDA assertion ID `tda_c0a1e50000000003`.
  - **4.0:** Systemaattinen verkko (Vahva) - Koheesio 80–89%, syvällinen ja johdonmukainen argumenttirakenne. Bound to deterministic TDA assertion ID `tda_c0a1e50000000004`.
  - **5.0:** Monitasoinen synteesi (Erinomainen) - Koheesio >= 90%, 0 kehää, alle 5% saarekkeita, laaja kytkeytyneisyys. Bound to deterministic TDA assertion ID `tda_c0a1e50000000005`.
- **Evaluation Mechanism & Zero-Token Invariant:** `matrix_causal_cohesion` is a pure system-evaluated metric matrix. It MUST be **strictly excluded from all LLM `criteria_block_ids`** to guarantee 0 additional LLM tokens, eliminate prompt bloat, prevent lexical quote hallucination, and prevent duplicate atom collisions. Evaluated deterministically via pure, stateless service `CausalCohesionEvaluator` (`backend_v2/services/orchestrator/causal_cohesion_evaluator.py`) reading thresholds from centralized configuration.
- **DTO Contract:**
  ```python
  class CausalCohesionEvaluationDTO(BaseModel):
      model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
      matrix_block_id: str
      atom_results: list[AtomResultDTO]
      level_stats: dict[str, LevelStatsDTO]
      score_result: ScoringResultDTO
  ```
- **Service Method Signature:**
  ```python
  def evaluate_causal_cohesion(
      self,
      audit: AntiFluffAuditDTO,
      total_nodes: int,
      strictness_level: StrictnessLevel,
      matrix_block_id: str,
  ) -> CausalCohesionEvaluationDTO:
      ...
  ```
  Note: `matrix_block_id` is mandatory and strictly non-nullable (`str`), with zero default fallbacks or `or` coalescing chains.
- **SDUI Distribution Column Binding & Cumulative Guttman Invariant:** In `CausalCohesionEvaluator`, lock:
  ```python
  CAUSAL_COHESION_TDA_IDS: tuple[str, ...] = (
      "tda_c0a1e50000000001",
      "tda_c0a1e50000000002",
      "tda_c0a1e50000000003",
      "tda_c0a1e50000000004",
      "tda_c0a1e50000000005",
  )
  ```
  Each emitted `AtomResultDTO` has `tda_id = CAUSAL_COHESION_TDA_IDS[level - 1]` and `matrix_id = matrix_block_id`. This guarantees that `MatrixDomainParser` matches each BARS level in `pb_meta.scales.claims.tda_assertions` against `step_evals_map[tda.tda_id]` and that `MatrixSummaryTableAdapter` renders the 5-item distribution column (`[✓, ✓, ✓, ✗, ✗]`) with 100% precision. The evaluator enforces the Cumulative Guttman Invariant ($L_1 \subset L_2 \subset L_3 \subset L_4 \subset L_5$) where Level $k$ can only pass if Level $k-1$ also passed.
- **Idempotent DAG Fusion Execution:** In `dag_executor.py`, track evaluated causal discovery sources in `_evaluated_causal_sources: set[str] = set()`. When a step declaring `causal_source_step_id` completes, check:
  ```python
  if step_obj.causal_source_step_id not in self._evaluated_causal_sources:
      self._evaluated_causal_sources.add(step_obj.causal_source_step_id)
      eval_dto = self._causal_cohesion_evaluator.evaluate_causal_cohesion(
          audit=fusion_res.anti_fluff_audit,
          total_nodes=len(upstream_graph.nodes),
          strictness_level=workflow.default_strictness_level,
          matrix_block_id=get_settings().causal_cohesion_matrix_block_id,
      )
      events.extend(
          TraceEvent(
              step_name=step_obj.causal_source_step_id,
              event_type="output",
              content=atom,
          )
          for atom in eval_dto.atom_results
      )
      events.append(
          TraceEvent(
              step_name=step_obj.causal_source_step_id,
              event_type="decision",
              metadata=TraceEventMetadataDTO(is_context_update=True),
              content=GlobalContextVarsDTO(
                  evaluative_matrices={eval_dto.matrix_block_id: eval_dto.score_result.score}
              ),
          )
      )
  ```
  This eliminates duplicate evaluation, trace pollution, and race conditions when multiple specialist steps run concurrently in Zone B. In `dag_executor.py#L1323-L1363`, the existing `_update_lock` context update handler automatically reconciles `TraceEvent(metadata=TraceEventMetadataDTO(is_context_update=True), content=GlobalContextVarsDTO(...))` and merges `parsed_gvars.evaluative_matrices` into `global_context_vars.evaluative_matrices` atomically without requiring edits to `state_reducer.py`.

### 2. Studio UX & 100% Engine Symmetry (Option A)
- **Zero Step Filtering:** In `WorkflowStepsTab`, all workflow steps are rendered as first-class cards in Zone B/C. Technical causal discovery engine steps (`engineType == EngineType.causalDiscovery`) remain fully visible, allowing inspection and editing of their inputs (`input_mappings`) and dependencies.
- **Append-to-Zone-B Lifecycle and Pruned Speculative Reordering:**
  - In Quorum Studio, step authoring operates under a deterministic Append-to-Zone-B model: `_addStep` locates Zone C via `_findFirstZoneCIndex(steps)` and inserts new steps at the end of Zone B.
  - `_findFirstZoneCIndex` identifies Zone C strictly by non-causal core steps (`bp.isSystemCore && bp.engineType != EngineType.causalDiscovery`), ensuring causal discovery steps remain in Zone B.
  - When authoring a workflow where an evaluative step consumes a causal graph, the author adds the causal step first (landing at the then-current Zone B tail) and subsequently adds the specialist step (specifically: AI Steering Evaluator), which lands after the causal step. The causal step is thus naturally upstream in `allSteps.sublist(0, index)` and immediately selectable in the specialist's dropdown.
  - Speculative drag-and-drop step reordering controls or complex graph re-routing engines are strictly pruned as over-engineering (Complexity Slayer 30% Deletion Invariant).
- **Explicit Causal Source Selector & Defensive Value Guard:** In `WorkflowStepCard`, in strict adherence to `frontend_zero_db_hardcoding_mandate` (zero hardcoded database/blueprint IDs in Flutter widgets), the card dynamically checks if upstream steps in `allSteps.sublist(0, index)` contain any causal discovery steps (`blueprint.engineType == EngineType.causalDiscovery`) and the current step is not itself a causal discovery step (`currentBlueprint?.engineType != EngineType.causalDiscovery`):
  - An explicit dropdown `DropdownButtonFormField<String?>` for `causalSourceStepId` is rendered with label `l10n.studioWorkflowCausalSourceLabel`.
  - The dropdown lists all upstream steps in `allSteps` whose blueprint specifies `engineType == EngineType.causalDiscovery`, plus an explicit "None" (`null`) option.
  - **Defensive Value Guard:** The dropdown's effective value is computed defensively against `allSteps.sublist(0, index)`:
    ```dart
    final allowedCausalIds = upstreamCausalSteps.map((s) => s.id).toSet();
    final effectiveValue = (stepDef.causalSourceStepId != null && allowedCausalIds.contains(stepDef.causalSourceStepId))
        ? stepDef.causalSourceStepId
        : null;
    ```
    If `causalSourceStepId` points to an invalid or non-upstream step ID (from corrupted historical data), the dropdown safely falls back to `null` ("Ei käytössä" / "None") without throwing Flutter's runtime `AssertionError`.
- **Full-Duplex Reactive Synchronization:**
  - When switching the causal dropdown from Step A to Step B: sets `causalSourceStepId = Step B`, atomically removes `Step A` from `dependsOn`, and appends `Step B` to `dependsOn`.
  - When selecting "None" in the dropdown: sets `causalSourceStepId = null` and removes the old causal step ID from `dependsOn`.
  - When deselecting a dependency chip in `previousSteps`: if the deselected `prevId == stepDef.causalSourceStepId`, automatically resets `causalSourceStepId = null` to prevent backend HTTP 422 `VALIDATION_FAILED` crashes on `StepRule.validate_step_rule_consistency`.
  - When a step is deleted in `WorkflowStepsTab`: `_deleteStep` cascades to filter `dependsOn` and reset `causalSourceStepId = null` if matching the deleted step.
- **Theme & String Safety:** All 22 raw `TextStyle` occurrences across `workflow_steps_tab.dart` and `workflow_step_card.dart` are replaced with `Theme.of(context).textTheme`. Unchecked `.substring(0, 16)` operations on UUIDs in `workflow_steps_tab.dart` are guarded by safe opaque ID generation.

### 3. Holistic Workflow AI Steering Integration
- In `wf_9d68c573802341db` ("Kokonaisvaltainen Auditointi"), insert step `sr_f1c1d71000000002` deterministically as **Step 10** (Zone B Specialist #9, directly after Step 9 `sr_b4c328df1c4141c6` and directly before Step 11 `sr_5f3dd7712a7f4bb3` XAI Reporter):
  - `task_blueprint: "sp_06c1d71000000001"` (Tekoälyohjauksen Arvioija)
  - `causal_source_step_id: "sr_c4a5a1d15c00438a"`
  - `depends_on: ["sr_f0a26d17cc9b48a7", "sr_c4a5a1d15c00438a"]`
  - `input_mappings: {"product_text": "$inputs.product_text", "chat_log": "$inputs.chat_log", "reflection_text": "$inputs.reflection_text"}`
  - `is_synthesis_source: true`
- Wire `sr_f1c1d71000000002` into the funnel aggregation step `sr_5f3dd7712a7f4bb3` (`depends_on`).
- Add a dedicated 2D matrix comparison group in `matrix_synthesis_groups` containing HACM matrix (`blk_7d8e9f0a1b2c3d4e`) and `matrix_causal_cohesion` (`blk_c0a1e50000000001`) in profiles `prf_5d6e7f8091a2b3c4` and `prf_06b1d71000000001`, while strictly preserving `STANDARD_MATRIX_VISIBLE_COLUMNS` in `matrix_visible_columns`.
- Update `test_competency_workflows_seed.py` assertions across lines 53–62, 68–148, and 291–311 to match the 14-step topology with 9 Zone B specialists, line 121 dependency check for `sr_f1c1d71000000002`, 7 matrix groups in `mono_prf`, and default strictness level 0.

### 4. Workflow Strictness & Report Structure Seed Governance
- **Holistic Audit Initial Strictness Level (0% Vapaa):** In `wf_9d68c573802341db` ("Kokonaisvaltainen Auditointi"), configure `"default_strictness_level": 0`. Under `ki_unified_matrix_scoring_strictness.md`, strictness level 0 (0% Vapaa / Free) corresponds to the baseline linear scoring exponent $e(0) = 1.00$, allowing raw unpenalized baseline evaluations while remaining editable in Quorum Studio Tab 4 (WorkflowStrictnessTab).
- **Holistic Audit Report Structure Exclusion (Lähdeluettelo ja viitteet):** In profile `prf_5d6e7f8091a2b3c4` ("Holistic Audit" / "Kokonaisvaltainen Auditointi"), remove `"printable_sources_block"` from `target_block_order` and set `"show_sources_summary_box": false`. This ensures that in Quorum Studio Tab 4 (ProfileLayoutsTab / Raportin rakenne), the "Lähdeluettelo ja viitteet" switch is toggled OFF by default, excluding bibliography and citations from the rendered SDUI report and PDF exports.

### 5. Workflow Cloning Relational Integrity
- **Isomorphic Graph Cloning in Studio:**
  When a workflow is cloned, every step ID is remapped from `sr_old` to `sr_new`. If a step references another step via `causal_source_step_id`, this pointer must be transformed under the same bijective mapping $f: V \to V'$.
- **Client Cloner (`client_app_v2/lib/features/studio/utils/workflow_cloner.dart`):**
  - **Phase B (Re-routing & Fail-Fast Lookup):** Add explicit remapping for `causal_source_step_id`, eradicating lazy `?? oldCausalSource` fallback:
    ```dart
    final oldCausalSource = step['causal_source_step_id']?.toString();
    if (oldCausalSource != null && oldCausalSource.isNotEmpty) {
      final newCausalSource = idMap[oldCausalSource];
      if (newCausalSource == null) {
        throw const AppException(
          type: 'https://api.quorum.fi/errors/workflow-clone-failed',
          title: 'Clone Failed',
          status: 400,
          detail: 'Causal source step ID could not be remapped.',
          extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
        );
      }
      step['causal_source_step_id'] = newCausalSource;
    }
    ```
  - **Phase C (Fail-Fast Validation):** Validate that if `causal_source_step_id` is non-null and non-empty, it exists in `validNewIds` AND exists in the step's updated `depends_on` array. If either condition fails, raise `AppException` with code `WORKFLOW_CLONE_FAILED`.
- **Backend Service (`backend_v2/services/studio/workflow_service.py`):**
  - In `clone_workflow` (lines 331–443), remap `causal_source_step_id`:
    ```python
    new_causal_source = (
        sr_mapping[step_cfg.causal_source_step_id]
        if step_cfg.causal_source_step_id and step_cfg.causal_source_step_id in sr_mapping
        else step_cfg.causal_source_step_id
    )
    new_step = step_cfg.model_copy(
        update={
            "id": sr_mapping[step_cfg.id],
            "depends_on": new_depends,
            "input_mappings": new_mappings,
            "causal_source_step_id": new_causal_source,
        }
    )
    ```
  This preserves relational consistency with `StepRule.validate_step_rule_consistency`, preventing HTTP 422 errors on clone save.

---

## System 2 Five-Axis Architectural Deconstruction

### 1. Target Scope & Boundaries (Scope Inquisitor)
- **Blast Radius Quarantine:** Direct code modifications are strictly constrained to 7 implementation files (`settings.py`, `causal_cohesion_evaluator.py`, `dag_executor.py`, `workflow_cloner.dart`, `workflow_service.py`, `workflow_steps_tab.dart`, `workflow_step_card.dart`), 2 test files with exact line bounds (`test_competency_workflows_seed.py#L53-L62`, `test_competency_workflows_seed.py#L68-L148`, `test_competency_workflows_seed.py#L291-L311`, `test_workflow_service.py#L963-L986`), 4 new/updated test files (`test_causal_cohesion_scoring.py`, `workflow_cloner_test.dart`, `workflow_steps_tab_test.dart`, `workflow_step_card_test.dart`), seed configuration (`seed_data.json`), and 2 localization files (`app_fi.arb`, `app_en.arb`).
- **Zero Scope Creep:** Causal discovery engine internals (`causal_discovery_engine.py`, `sliding_window_linker.py`, `topological_evaluator.py`) are strictly quarantined as Read-Only. No mutations to graph construction, Markov wave traversals, or token window parameters are permitted.
- **Master Archetype Isolation:** Workflow updates are limited strictly to `wf_9d68c573802341db` ("Kokonaisvaltainen Auditointi") to establish it as the sovereign superset reference. Specialist sub-workflows (specifically: `wf_06a1d71000000001`) remain intact.

### 2. Eradicated Duct-Tape (Duct-Tape Prosecutor - Under-Engineering Ban)
- **Eliminated Monolithic God Code:** Extracted deterministic evaluation out of `dag_executor.py` into pure service `causal_cohesion_evaluator.py`, strictly honoring `ki_god_code_prevention.md`.
- **Eliminated Multi-Step Race Condition & Duplicate Atoms:** Prevented Zone B concurrent specialists from running fusion evaluation multiple times via an in-memory idempotency set guard `_evaluated_causal_sources: set[str]` in `DAGExecutor`.
- **Eliminated Hardcoded Identifiers & Magic Constants:** Removed default DB ID `"blk_c0a1e50000000001"` and magic floats `0.40, 0.60, ...` from method signatures and code bodies; all constants reside in SSOT configuration.
- **Eliminated Naked Dictionaries in Event Sourcing:** Replaced raw `dict` payload in `TraceEvent.content` with strictly typed `GlobalContextVarsDTO(evaluative_matrices={eval_dto.matrix_block_id: eval_dto.score_result.score})` adhering to `zero_service_layer_fallbacks` and EPIC_149/152.
- **Eliminated Enum `.value` Checking:** In `dag_executor.py#L163`, string comparison `atom.status.value == "PASSED"` is replaced with strict native enum comparison `atom.status == ExecutionStatus.PASSED`.
- **Eliminated Evaluator Lazy Fallback Chains & Dynamic Binding:** In `causal_cohesion_evaluator.py`, method signature requires mandatory non-nullable `matrix_block_id: str`, banning default coalescing. Dynamically binds `atom.matrix_id = matrix_block_id` across all emitted `AtomResultDTO` instances.
- **Eliminated Unmapped Clone Pointers & Lazy Fallback:** Both `workflow_cloner.dart` and `workflow_service.py` remap `causal_source_step_id` during step cloning. In `workflow_cloner.dart`, eradicated `?? oldCausalSource` lazy fallback, throwing `AppException` with `WORKFLOW_CLONE_FAILED` immediately if unmapped.
- **Eliminated Unchecked Dropdown Values in Flutter:** In `workflow_step_card.dart`, `initialValue` is guarded defensively against `allSteps.sublist(0, index)`, preventing Flutter `AssertionError` crashes on corrupt data.
- **Prevented Matrix Table Column Pollution Fatal Bug:** Eradicated the proposal to inject matrix block IDs into `matrix_visible_columns`. In `matrix_summary_table_adapter.py#L74-L80`, `matrix_visible_columns` iterates `ReportMatrixColumn` enum members (`label`, `distribution`, `row_explanation`, `criteria`, `normalized_score`). Injecting block IDs triggers `ValueError` -> `AppException(ErrorCodes.VALIDATION_FAILED, status_code=422)`, crashing report rendering. Block IDs are bound strictly to `matrix_synthesis_groups` (`target_blocks`).
- **Eliminated MyPy Strict Seed Test Debt:** Fixed missing return type annotation on line 53 of `test_competency_workflows_seed.py` (`load_seed_data() -> dict[str, Any]:`), eliminating 20 MyPy strict errors (`[no-untyped-def]` / `[no-untyped-call]`).
- **Eradicated Raw TextStyles:** In `workflow_steps_tab.dart` (2 instances) and `workflow_step_card.dart` (20 instances), all 22 raw `TextStyle` instantiations are eradicated in favor of `Theme.of(context).textTheme` tokens, enforcing 100% Flutter Theme Sovereignty.
- **Guarded Substring Clippings:** Replaced unguarded `.substring(0, 16)` operations on lines 43 and 73 in `workflow_steps_tab.dart` with length-safe opaque ID generation.
- **Banned Hidden Step Filtering:** Eradicated ad-hoc list filters hiding `causalDiscovery` steps from the user interface; all execution steps are fully visible and editable.
- **Zero-Node BARS 1.0 Novice Floor Defense:** Enforced `total_nodes > 0` condition for Levels 2–5 in `CausalCohesionEvaluator`. Empty submissions (`total_nodes == 0`) evaluate Level 1 as `PASSED` and Levels 2–5 as `FAILED`, grounding strictly to BARS 1.00 Novice floor (exact 1.07 score at 70% strictness, 1.27 at 0% linear) and eradicating 5.0 score inflation.
- **Eliminated LLM Prompt Bloat & Duplicate Atoms:** Strictly excluded `matrix_causal_cohesion` from LLM `criteria_block_ids`, preserving the 0-token contract.
- **Calibrated Default Strictness Alignment:** Configured `wf_9d68c573802341db` to start at `default_strictness_level: 0` (0% Vapaa) in seed data, eliminating arbitrary 50% defaults for holistic audit runs.
- **Clean Report Structure:** Excluded `"printable_sources_block"` from `prf_5d6e7f8091a2b3c4.target_block_order`, eliminating clutter in executive reports that do not require external academic bibliography cards.

### 3. Approved Best Practice (Type Constitutionalist - Sovereign Target)
- **BARS Developmental Competence Model (Track A):** Authoring `matrix_causal_cohesion` as an affirmative BARS developmental matrix (1.0 to 5.0) where all 5 levels enforce `inverse_evidence: false` and `aggregation_mode: "ALL_MUST_COMPLY"`, preserving the Cumulative Guttman Invariant ($L_1 \subset L_2 \subset L_3 \subset L_4 \subset L_5$).
- **Pure Stateless Calculation Service:** `CausalCohesionEvaluator` encapsulates all graph metrics evaluation and BARS level threshold logic cleanly decoupled from orchestrators.
- **Deterministic 0-Token Evaluation:** Computing matrix evaluation directly from topological graph telemetry (`logical_cohesion_score`, `cycle_detected`, `isolated_concept_count`) in `AntiFluffAuditDTO`, incurring zero additional LLM inference tokens or latency.
- **Single Sovereign Scoring Pipeline:** Delegating evaluated `LevelStatsDTO` directly to `UnifiedScoringEngine` within `CausalCohesionEvaluator` using workflow `default_strictness_level`, enforcing identical continuous strictness power-curve dampening ($e(s)$) without parallel scoring engines.
- **Isomorphic Graph Cloning:** Re-routing both edge dependencies (`depends_on`) and relational attributes (`causal_source_step_id`) under the same ID map, backed by Phase C referential validation.
- **Dual-Axis Localization SSOT:** Sourcing UI dropdown labels strictly from compile-time Axis 1 `.arb` catalogs, and dynamic workflow/profile metadata from Axis 2 `I18nText` database fields.

### 4. Pruned Over-Engineering (Complexity Slayer - 30% Deletion Test)
- **30% Deletion Invariant:** If 30% of new code is deleted, what gets cut and what breaks?
  - Cut: Speculative step reordering controls (drag handles, move buttons, complex graph re-routing engines), secondary scoring engines, hidden step filters, magic background state synchronizers, or dedicated specialist toggle controllers.
  - Result: Studio's established **Append-to-Zone-B** authoring flow naturally orders steps chronologically: adding a causal step first, followed by a specialist step, naturally satisfies `allSteps.sublist(0, index)`. 1 single pure computation service created (`CausalCohesionEvaluator`). All functionality operates via native Pydantic V2 DTOs, standard `DropdownButtonFormField` components, and established `UnifiedScoringEngine` pipelines.
- **Zero Shadow Collections:** Reusing canonical PromptBlock and StepRule collections without inventing intermediate wrappers.

### 5. Fail-Fast Proof Anchors (Incorruptible Judge - Deterministic Verification)
- **Automated AST Strictness:** Enforced via `scripts/backend_audit_loop.py` with `--ast-strict` verifying clean imports, zero naked dicts, and strict Pydantic model configurations.
- **Mathematical Seed Linter:** Validating 100% in-memory referential integrity and schema compliance via `scripts/audit_database_atoms.py --strict` with zero errors.
- **Flutter Theme Sovereignty Gate:** Validating 100% token adherence via `scripts/audit_flutter_theme_sovereignty.py`.
- **Markdown Boundary Verification:** Passing `scripts/audit_markdown_boundaries.py` with zero MBD violations.

---

## Falsification & Red-Teaming Analysis

### Failure Mode 1: Empty Graph / Zero-Node Division by Zero & Score Inflation
- **Attack Vector:** An input deliverable contains zero extractable atomic claims, producing a graph with `total_nodes == 0`.
- **Vulnerability:** Setting `cohesion = 1.0, isolated_ratio = 0.0` causes Levels 2–5 to evaluate as `PASSED`, awarding 5.0 / 5.0 (Full Mastery) to an empty submission.
- **Hardened Mitigation:** In `CausalCohesionEvaluator`, Levels 2–5 enforce `total_nodes > 0`. When `total_nodes == 0`, Levels 2–5 evaluate to `FAILED`, while Level 1 evaluates to `PASSED`, safely grounding the score to the exact BARS 1.00 Novice floor.

### Failure Mode 2: Cyclic Dependency Deadlock & Defect Grounding
- **Attack Vector:** Adversarial source text containing circular claims (Claim A causes Claim B, Claim B causes Claim A) triggers circular reasoning.
- **Vulnerability:** Unshielded topological evaluation deadlocks or crashes during traversal.
- **Hardened Mitigation:** Pre-flight NetworkX cycle detection flags `cycle_detected = True` in `AntiFluffAuditDTO`. In `CausalCohesionEvaluator`, `cycle_detected == True` immediately fails Levels 2–5, grounding the evaluation score strictly to BARS 1.0 Defect floor (exact 1.07 score at 70% strictness) and documenting the circular reasoning in the XAI audit trail.

### Failure Mode 3: Studio UI Dropdown State Desynchronization & Deletion Cascades
- **Attack Vector:** User selects an upstream causal discovery step in the dropdown, but subsequent step deletion in the workflow leaves orphaned dependencies.
- **Vulnerability:** Specialist step depends on a deleted causal step ID, causing DAG compiler validation failures during execution.
- **Hardened Mitigation:** When any step is deleted in `WorkflowStepsTab`, `_deleteStep` cascades to filter `dependsOn` arrays and reset `causalSourceStepId` to `null` if the deleted step matches, preventing dangling references.

### Failure Mode 4: Inverted Rubric Paradox on BARS Scale
- **Attack Vector:** Configuring Level 1 novice criteria with `inverse_evidence: true` under the mistaken assumption that Level 1 represents presence of errors.
- **Vulnerability:** High-performing candidates demonstrating Level 4–5 mastery are penalized on Level 1 for not producing novice errors, while deficient candidates receive artificial score inflation.
- **Hardened Mitigation:** `matrix_causal_cohesion` is explicitly classified under Track A (Developmental Progressive Competence) with `inverse_evidence: false` across all 5 levels. Level 1 awards positive baseline points, preserving the Cumulative Guttman Invariant.

### Failure Mode 5: StepRule Causal Source Dependency Invariant Violation on Swaps and Deselection
- **Attack Vector:** User switches dropdown from Step A to Step B, leaving Step A orphaned in `dependsOn`; or user unchecks dependency chip for Step A while Step A is the active causal source.
- **Vulnerability:** When saving workflow, Pydantic `@model_validator(mode="after")` `validate_step_rule_consistency` on `StepRule` raises `AppException(ErrorCodes.VALIDATION_FAILED, status_code=422)`, crashing workflow updates.
- **Hardened Mitigation:** In `WorkflowStepCard`, dropdown `onChanged` atomically prunes the former causal ID and appends the new ID to `dependsOn`. Chip `onSelected` checks if the deselected `prevId == stepDef.causalSourceStepId` and auto-resets `causalSourceStepId = null`.

### Failure Mode 6: Zone C Funnel Anchor Desynchronization
- **Attack Vector:** Inserting `sr_f1c1d71000000002` (AI Steering) into `wf_9d68c573802341db` without wiring it into the downstream aggregation funnel `sr_5f3dd7712a7f4bb3`.
- **Vulnerability:** XAI Reporter and Scoring Engine fail to evaluate or synthesize AI Steering evidence, silently omitting `matrix_hacm` and `matrix_causal_cohesion` from the executive report.
- **Hardened Mitigation:** Funnel step `sr_5f3dd7712a7f4bb3` (`depends_on`) is explicitly updated in `seed_data.json` to include `sr_f1c1d71000000002`, guaranteeing that the aggregation step waits for and consumes AI Steering outputs before synthesis generation.

### Failure Mode 7: AtomResultDTO Cognitive Validation Invariant Violation on System Metrics
- **Attack Vector:** Emitting `AtomResultDTO` for topological graph cohesion with `status = ExecutionStatus.PASSED` and `source_quote = None` without setting `contextual_override = True`.
- **Vulnerability:** Pydantic `@model_validator(mode="after")` `validate_cognitive_vs_system_state` in `backend_v2/models/dtos/atom_result.py#L140-L160` strictly enforces that any `PASSED` atom without a lexical `source_quote` must explicitly have `contextual_override = True` and non-empty `evaluation_reasoning`. Omission raises a Pydantic `ValueError`, violently aborting workflow execution.
- **Hardened Mitigation:** In `CausalCohesionEvaluator`, all topological metric `AtomResultDTO` instances are constructed strictly adhering to `validate_cognitive_vs_system_state`: when `PASSED`, `contextual_override = True`, `source_quote = None`, and `evaluation_reasoning = f"Topological causal cohesion score {score:.2f} satisfies Level {level} threshold"`; when `FAILED`, `contextual_override = False`, `source_quote = None`, and `evaluation_reasoning = f"Topological causal cohesion score {score:.2f} does not satisfy Level {level} threshold"`.

### Failure Mode 8: TDAEngine LLM Call Collision & Broken 0-Token Contract
- **Attack Vector:** Adding `blk_c0a1e50000000001` to `criteria_block_ids` of LLM blueprints (`sp_192910b5f5a34c79` or `sp_bd0b3054fe664960`).
- **Vulnerability:** `TDAEngine` invokes LLM extraction over topological assertions, wasting tokens, generating duplicate atoms that collide with `CausalCohesionEvaluator`, and risking lexical validation failures.
- **Hardened Mitigation:** `blk_c0a1e50000000001` is strictly excluded from all LLM `criteria_block_ids`. It is evaluated purely via `CausalCohesionEvaluator` in `dag_executor.py` and bound only to presentation profiles (`matrix_synthesis_groups`).

### Failure Mode 9: Matrix Summary Table Column Pollution via Block IDs
- **Attack Vector:** Injecting PromptBlock IDs (`blk_c0a1e50000000001`, `blk_7d8e9f0a1b2c3d4e`) into `OutputProfile.matrix_visible_columns`.
- **Vulnerability:** In `backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py#L74-L80`, `matrix_visible_columns` is iterated and coerced via `ReportMatrixColumn(col)`. Adding block IDs raises `ValueError` -> `AppException(ErrorCodes.VALIDATION_FAILED, status_code=422)`, completely crashing report and SDUI rendering.
- **Hardened Mitigation:** Block IDs are configured strictly in `matrix_synthesis_groups` (`target_blocks`). `matrix_visible_columns` strictly preserves `STANDARD_MATRIX_VISIBLE_COLUMNS` (`['label', 'distribution', 'row_explanation', 'criteria', 'normalized_score']`).

### Failure Mode 10: Zone B Concurrent Multi-Step Causal Fusion Race Condition & Duplicate Atoms
- **Attack Vector:** In `wf_9d68c573802341db`, `sr_4d2272d8b4864847` (Causal Analyst) and `sr_f1c1d71000000002` (AI Steering) both reference `causal_source_step_id: "sr_c4a5a1d15c00438a"` and run concurrently in Zone B via `asyncio.TaskGroup`.
- **Vulnerability:** When both steps complete, `dag_executor.py` triggers cohesion evaluation twice, pushing 10 `AtomResultDTO` instances to `execution_trace` (5 duplicate atoms) and generating two competing `TraceEvent` updates for `global_context_vars.evaluative_matrices["blk_c0a1e50000000001"]`.
- **Hardened Mitigation:** In `DAGExecutor.execute()`, maintain `_evaluated_causal_sources: set[str] = set()`. Only execute `CausalCohesionEvaluator` if `step_obj.causal_source_step_id not in _evaluated_causal_sources`. In `dag_executor.py`, `_evaluated_causal_sources` guarantees single-pass evaluation, and lines 1349–1354 merge `evaluative_matrices` incrementally into `global_context_vars`.

### Failure Mode 11: SDUI Distribution Column Desynchronization on Non-Deterministic Atom IDs
- **Attack Vector:** Emitting `AtomResultDTO` with random UUIDs or generic slugs (`atom_1`).
- **Vulnerability:** `MatrixDomainParser.parse()` looks up `pb_meta.scales.claims.tda_assertions` (`tda.tda_id`) against `step_evals_map[tda.tda_id]`. If the IDs do not match, `step_evals_map.get(tda.tda_id)` returns `None`, causing `MatrixSummaryTableAdapter` to render blank or all-failed checkmarks in the `distribution` column.
- **Hardened Mitigation:** In `seed_data.json`, `blk_c0a1e50000000001` explicitly defines `tda_c0a1e50000000001` through `tda_c0a1e50000000005`. In `CausalCohesionEvaluator`, `CAUSAL_COHESION_TDA_IDS` locks these exact IDs 1:1 to BARS Levels 1–5 as `tda_id`.

### Failure Mode 12: Clone Cascade Rejection (Fatal HTTP 422 on Cloned Workflows)
- **Attack Vector:** An admin in Quorum Studio clones the newly enriched "Kokonaisvaltainen Auditointi" workflow (`wf_9d68c573802341db`). Step 10 ("AI Steering", `sr_f1c1d71000000002`) has `causal_source_step_id: "sr_c4a5a1d15c00438a"` and `depends_on: ["sr_f0a26d17cc9b48a7", "sr_c4a5a1d15c00438a"]`.
- **Vulnerability:** `workflow_cloner.dart` and `workflow_service.py` assign new IDs for steps, updating `depends_on` to new IDs. But `causal_source_step_id` remains the old pre-clone ID (`"sr_c4a5a1d15c00438a"`). Backend Pydantic validation executes `StepRule.validate_step_rule_consistency`, detects that `causal_source_step_id not in depends_on`, and rejects the save with HTTP 422 `VALIDATION_FAILED`.
- **Hardened Mitigation:** Both `workflow_cloner.dart` and `workflow_service.py` remap `causal_source_step_id` to the new ID, and Phase C validates that `causal_source_step_id in depends_on` and `causal_source_step_id in validNewIds`.

### Failure Mode 13: Historical / Malformed Blueprint Dropdown Assertion Crash (Red-Screen)
- **Attack Vector:** An existing custom workflow contains a specialist step with a corrupted or manually edited `causal_source_step_id` that does not point to an upstream step in `sublist(0, index)`.
- **Vulnerability:** `WorkflowStepCard` passes the raw `stepDef.causalSourceStepId` as `initialValue` to `DropdownButtonFormField`. Because the ID is absent from `items`, Flutter's internal assert (`items.where((i) => i.value == value).length == 1`) fails, triggering a red crash screen across Quorum Studio.
- **Hardened Mitigation:** `WorkflowStepCard` guards `initialValue`: if `causalSourceStepId` is not present in `upstreamCausalSteps`, it evaluates to `null` ("Ei käytössä" / "None"), rendering safely without assertion errors.

### Failure Mode 14: Silent Matrix ID Drift via Evaluator Fallback
- **Attack Vector:** A developer refactors `causal_cohesion_evaluator.py` or calls it without passing `matrix_block_id`.
- **Vulnerability:** Method defaults to global fallback ID. In workflows using custom cohesion matrices, the evaluator binds atoms to the global default block, corrupting the SDUI distribution table.
- **Hardened Mitigation:** Method signature strictly requires non-nullable `matrix_block_id: str` without default value. Calling without `matrix_block_id` triggers `TypeError` at compile time and runtime.

---

```xml
<execution_protocol>
  <step id="1" name="PRE_IMPLEMENTATION_CLEANUPS">
    <action>In @[backend_v2/tests/unit/services/test_competency_workflows_seed.py#L54-L63], annotate function line 53 `def load_seed_data() -> dict[str, Any]:` to eliminate 20 MyPy strict `[no-untyped-def]` and `[no-untyped-call]` typechecker errors.</action>
    <action>In @[backend_v2/settings.py#L54-L968], add SSOT configuration fields: `causal_cohesion_matrix_block_id: str = "blk_c0a1e50000000001"`, `causal_cohesion_l2_threshold: float = 0.40`, `causal_cohesion_l3_threshold: float = 0.60`, `causal_cohesion_l4_threshold: float = 0.80`, `causal_cohesion_l5_threshold: float = 0.90`, `causal_cohesion_l3_isolation_max: float = 0.20`, `causal_cohesion_l4_isolation_max: float = 0.10`, `causal_cohesion_l5_isolation_max: float = 0.05`.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L129-L281], replace enum `.value` comparison (`if atom.status.value == "PASSED":`) on line 163 with strict native check `if atom.status == ExecutionStatus.PASSED:` to comply with `strict_enum_hydration_and_validation`.</action>
    <action>In @[client_app_v2/lib/features/studio/utils/workflow_cloner.dart#L65-L146], add strict `causal_source_step_id` remapping to Phase B using direct `idMap` lookup (throwing `AppException` with code `WORKFLOW_CLONE_FAILED` if unmapped, eradicating `?? oldCausalSource` fallback) and add relational consistency assertion to Phase C (validating that `causal_source_step_id` exists in `validNewIds` and `depends_on`).</action>
    <action>In @[backend_v2/services/studio/workflow_service.py#L331-L449], add `causal_source_step_id` remapping via `sr_mapping[step_cfg.causal_source_step_id]` to `clone_workflow`.</action>
    <action>In @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L963-L986] and [NEW] @[client_app_v2/test/features/studio/utils/workflow_cloner_test.dart], add unit tests asserting cloned workflows remap `causal_source_step_id` and pass validation.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart#L1-L190], replace raw `TextStyle` instantiations on lines 141 and 160 with `Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)` and `bodyMedium` tokens to ensure 100% Theme Sovereignty, and protect `.substring(0, 16)` on lines 43 and 73 with safe length checks.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L1-L591], replace all 20 raw `TextStyle` instantiations (lines 103, 121, 164, 172, 188, 198, 260, 268, 285, 315, 323, 340, 358, 363, 372, 423, 428, 440, 503, 508) with `Theme.of(context).textTheme` tokens to ensure 100% Theme Sovereignty.</action>
    <constraint invariant="touched_scope_tech_debt_mandate">All discovered debt in target files must be eradicated in Phase 1 before domain feature modification.</constraint>
  </step>

  <step id="2" name="SEED_DATA_VAULT_MUTATION">
    <action>Create timestamped backup of `backend_v2/seed/seed_data.json` inside `backend_v2/seed/backups/`.</action>
    <action>Add PromptBlock `blk_c0a1e50000000001` (`matrix_causal_cohesion`) with 5 BARS scales and 5 deterministic TDA assertions (`tda_c0a1e50000000001` through `tda_c0a1e50000000005`) to @[backend_v2/seed/seed_data.json#L20230-L20260]. Note: strictly excluded from all LLM `criteria_block_ids`.</action>
    <action>Add step `sr_f1c1d71000000002` (Tekoälyohjauksen Arvioija, blueprint `sp_06c1d71000000001`) deterministically as Step 10 to workflow `wf_9d68c573802341db` ("Kokonaisvaltainen Auditointi") in @[backend_v2/seed/seed_data.json#L20250-L20550] with `"causal_source_step_id": "sr_c4a5a1d15c00438a"` and `"depends_on": ["sr_f0a26d17cc9b48a7", "sr_c4a5a1d15c00438a"]`.</action>
    <action>In workflow `wf_9d68c573802341db` in @[backend_v2/seed/seed_data.json#L20250-L20550], set `"default_strictness_level": 0` (0% Vapaa / Free linear baseline evaluation).</action>
    <action>Update funnel step `sr_5f3dd7712a7f4bb3` in `wf_9d68c573802341db` in @[backend_v2/seed/seed_data.json#L20250-L20550] to depend on `sr_f1c1d71000000002`.</action>
    <action>Add a dedicated matrix comparison group in `matrix_synthesis_groups` containing `blk_7d8e9f0a1b2c3d4e` and `blk_c0a1e50000000001` in `prf_5d6e7f8091a2b3c4` and `prf_06b1d71000000001` in @[backend_v2/seed/seed_data.json#L23200-L23400], preserving `STANDARD_MATRIX_VISIBLE_COLUMNS` in `matrix_visible_columns`. In `prf_5d6e7f8091a2b3c4`, remove `"printable_sources_block"` from `target_block_order` (hiding "Lähdeluettelo ja viitteet" from report structure) and set `"show_sources_summary_box": false`.</action>
    <action>In @[backend_v2/tests/unit/services/test_competency_workflows_seed.py#L69-L158], update `test_baseline_monolithic_workflow_preserved` to assert 14 steps in `mono_wf.steps`, add `sr_f1c1d71000000002` to `zone_b_step_ids` (making 9 Zone B specialists), update line 121 check to `if step.id in ("sr_4d2272d8b4864847", "sr_f1c1d71000000002"):`, assert 7 matrix groups in `mono_prf.matrix_synthesis_groups`, assert `sr_5f3dd7712a7f4bb3` depends on all 9 Zone B specialists, and assert `"printable_sources_block" not in mono_prf.target_block_order`.</action>
    <action>In @[backend_v2/tests/unit/services/test_competency_workflows_seed.py#L301-L323], update `test_output_profiles_scoring_configuration` on line 311 to assert `wf_model.default_strictness_level in (0, 50, 70)` and verify `wf_9d68c573802341db.default_strictness_level == 0`.</action>
    <action>Execute pre-flight in-memory validation via `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict`.</action>
    <action>Apply seed sync to development database via `uv run python backend_v2/seed/run_seed.py local`.</action>
    <constraint invariant="seed_vault_protocol">All IDs must strictly match Opaque Stripe ID pattern (specifically `blk_c0a1e50000000001` and `sr_f1c1d71000000002`). Zero slug relational references.</constraint>
  </step>

  <step id="3" name="BACKEND_DETERMINISTIC_BARS_EVALUATION">
    <action>Create pure, stateless service [NEW] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py] with DTO `CausalCohesionEvaluationDTO` (`matrix_block_id: str`, `atom_results: list[AtomResultDTO]`, `level_stats: dict[str, LevelStatsDTO]`, `score_result: ScoringResultDTO`) and method `evaluate_causal_cohesion(audit: AntiFluffAuditDTO, total_nodes: int, strictness_level: StrictnessLevel, matrix_block_id: str) -> CausalCohesionEvaluationDTO` with mandatory `matrix_block_id: str` (no `| None = None`), reading thresholds from Settings configuration (SSOT), preventing bloat in `dag_executor.py` (`ki_god_code_prevention.md`).</action>
    <action>In `CausalCohesionEvaluator`, implement deterministic mathematical threshold evaluation enforcing `total_nodes > 0` for Levels 2–5 and the Cumulative Guttman Invariant ($L_1 \subset L_2 \subset L_3 \subset L_4 \subset L_5$) where Level $k$ can only pass if Level $k-1$ also passed (Level 1 Novice floor: always PASSED; Level 2: `total_nodes > 0 and not cycle_detected and cohesion >= config.causal_cohesion_l2_threshold`; Level 3: `l2_passed and cohesion >= config.causal_cohesion_l3_threshold and isolated_ratio <= config.causal_cohesion_l3_isolation_max`; Level 4: `l3_passed and cohesion >= config.causal_cohesion_l4_threshold and isolated_ratio <= config.causal_cohesion_l4_isolation_max`; Level 5: `l4_passed and cohesion >= config.causal_cohesion_l5_threshold and isolated_ratio <= config.causal_cohesion_l5_isolation_max`), handling zero-node edge case (`if total_nodes == 0: Level 1 PASSED, Levels 2..5 FAILED`, grounding strictly to BARS 1.00 Novice floor: 1.07 score at 70% strictness, 1.27 at 0% linear).</action>
    <action>In `CausalCohesionEvaluator`, lock `CAUSAL_COHESION_TDA_IDS = ("tda_c0a1e50000000001", "tda_c0a1e50000000002", "tda_c0a1e50000000003", "tda_c0a1e50000000004", "tda_c0a1e50000000005")`. Construct `AtomResultDTO` instances with `tda_id = CAUSAL_COHESION_TDA_IDS[level - 1]` and dynamic `matrix_id = matrix_block_id`, strictly adhering to `validate_cognitive_vs_system_state` (enforcing `contextual_override=True` with non-empty `evaluation_reasoning` on `PASSED` states, `contextual_override=False` on `FAILED` states, and `source_quote=None`). Construct `level_stats: dict[str, LevelStatsDTO]` and invoke `UnifiedScoringEngine().calculate(stats={float(k): v for k, v in level_stats.items()}, math_min=1.0, math_max=5.0, strictness_level=strictness_level)` to produce `score_result`.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L129-L281], instantiate `CausalCohesionEvaluator` and initialize `_evaluated_causal_sources: set[str] = set()` in `execute()`. When a step declaring `causal_source_step_id` completes, check `if step_obj.causal_source_step_id not in self._evaluated_causal_sources:`. Evaluate cohesion strictly once per causal source graph via `audit=fusion_res.anti_fluff_audit, total_nodes=len(upstream_graph.nodes), strictness_level=workflow.default_strictness_level, matrix_block_id=get_settings().causal_cohesion_matrix_block_id`, append `eval_dto.atom_results` as output events, and mark `step_obj.causal_source_step_id` in `_evaluated_causal_sources`.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L129-L281], after computing `eval_dto`, emit a `TraceEvent` with `step_name=step_obj.causal_source_step_id`, `event_type="decision"`, `metadata=TraceEventMetadataDTO(is_context_update=True)`, and typed payload `content=GlobalContextVarsDTO(evaluative_matrices={eval_dto.matrix_block_id: eval_dto.score_result.score})` to update `global_context_vars.evaluative_matrices` before downstream funnel and reporter execution (Zero Naked Dicts, EPIC_149/152). In `dag_executor.py#L1323-L1363`, verify that the existing `_update_lock` context update loop reconciles `parsed_gvars.evaluative_matrices` into `global_context_vars.evaluative_matrices` without requiring edits to `state_reducer.py`.</action>
    <action>Write unit tests in [NEW] @[backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py] verifying mathematical score mappings across all 5 BARS thresholds, zero-node Novice floor grounding (exact 1.07 score at 70% strictness, 1.27 at 0% linear), cyclic graph defect grounding (exact 1.07 score at 70% strictness), multi-step concurrent execution idempotency (asserting exactly 5 atoms emitted and 1 trace update when 2 specialists share a causal source), dynamic `matrix_block_id` binding verification, and `UnifiedScoringEngine` integration.</action>
    <action>Run backend audit gate via `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/causal_cohesion_evaluator.py backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py --test --ast-strict`.</action>
    <constraint invariant="zero_service_layer_fallbacks">No naked dictionaries. Use strictly typed DTO models (GlobalContextVarsDTO, CausalTdaFusionResultDTO, CausalCohesionEvaluationDTO, LevelStatsDTO, ScoringResultDTO).</constraint>
  </step>

  <step id="4" name="FRONTEND_LOCALIZATION_AND_STUDIO_STEP_SYMMETRY">
    <action>Add Finnish localization keys in @[client_app_v2/lib/l10n/app_fi.arb#L1910-L1935]: `studioWorkflowCausalSourceLabel` ("Kausaalipäättelyn lähde") and `studioWorkflowCausalSourceNone` ("Ei käytössä").</action>
    <action>Add English localization keys in @[client_app_v2/lib/l10n/app_en.arb#L2620-L2645]: `studioWorkflowCausalSourceLabel` ("Causal Discovery Source") and `studioWorkflowCausalSourceNone` ("None").</action>
    <action>Run `flutter gen-l10n` inside `client_app_v2/` via `run_command`.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart#L1-L190], enforce 100% visible step cards by rendering all steps in `allSteps` without filtering out `causalDiscovery` steps.</action>
    <action>Update `_findFirstZoneCIndex` in @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart#L1-L190] to identify Zone C strictly by non-causal system core funnel anchor blueprints (`bp.isSystemCore && bp.engineType != EngineType.causalDiscovery`), guaranteeing that new steps appended via `_addStep` land at the end of Zone B. Confirm zero speculative reordering machinery.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart#L1-L190], verify that `_deleteStep` maintains cascading referential integrity by filtering `dependsOn` and resetting `causalSourceStepId` to `null` if matching the deleted step ID.</action>
    <action>Create [NEW] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_steps_tab_test.dart] widget test verifying: 1) Causal discovery steps rendered as visible cards, 2) Zone C correctly identified by non-causal core steps, 3) `_deleteStep` cleanly cascading to prune `dependsOn` and reset `causalSourceStepId`.</action>
    <action>Run flutter audit gate via `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/widgets/workflow/workflow_steps_tab_test.dart`.</action>
    <constraint invariant="dual_axis_localization">Never hardcode user-facing strings in Dart source code. All strings must be resolved via AppLocalizations.</constraint>
  </step>

  <step id="5" name="FRONTEND_SPECIALIST_CAUSAL_SOURCE_SELECTOR">
    <action>In @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L1-L591], add an explicit `DropdownButtonFormField<String?>` for `causalSourceStepId` dynamically whenever upstream steps in `allSteps.sublist(0, index)` contain any causal discovery steps (`engineType == EngineType.causalDiscovery`) and current step is not causal discovery, strictly adhering to `frontend_zero_db_hardcoding_mandate` (zero hardcoded blueprint IDs).</action>
    <action>Populate dropdown items with upstream steps where blueprint `engineType == EngineType.causalDiscovery`, plus an explicit "None" (`null`) option.</action>
    <action>In `WorkflowStepCard`, implement defensive `initialValue` guard: `(stepDef.causalSourceStepId != null && allowedCausalIds.contains(stepDef.causalSourceStepId)) ? stepDef.causalSourceStepId : null`, preventing Flutter `AssertionError` crashes if the current step references an invalid or non-upstream causal ID.</action>
    <action>Implement Full-Duplex Reactive Synchronization in dropdown `onChanged`: when switching from Step A to Step B, atomically remove `Step A` from `dependsOn` and append `Step B` to `dependsOn`; when selecting "None", set `causalSourceStepId = null` and remove the former causal ID from `dependsOn`.</action>
    <action>Implement Full-Duplex Reactive Synchronization in chip `onSelected`: when deselecting a dependency chip, if the deselected `prevId == stepDef.causalSourceStepId`, automatically reset `causalSourceStepId = null` to prevent backend HTTP 422 `VALIDATION_FAILED` crashes.</action>
    <action>Update widget tests in @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart#L450-L530] asserting dropdown rendering, defensive fallback on invalid IDs, causal source swap dependency pruning, and chip deselection auto-reset without hidden steps.</action>
    <action>Run flutter audit gate via `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart`.</action>
    <constraint invariant="theme_sovereignty">All styling must use Theme.of(context).colorScheme tokens and AppSpacing constants. Zero hardcoded colors.</constraint>
  </step>

  <step id="6" name="UNIVERSAL_QUALITY_GATE_AND_CROSS_SYSTEM_AUDIT">
    <action>Execute full backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test --ast-strict`.</action>
    <action>Execute full flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
    <action>Execute database verification: `uv run python scripts/audit_database_atoms.py --strict`.</action>
    <action>Verify markdown boundaries on this plan: `uv run python scripts/audit_markdown_boundaries.py --file implementation_plan.md`.</action>
    <constraint invariant="zero_tolerance_audit_loop">100% test pass rate required. No skipped tests or advisory warning suppressions.</constraint>
  </step>
</execution_protocol>
```

---

## Verification Scenarios (ISTQB)

### 1. Positive Scenario: High Cohesion Full Mastery (BARS 5.0)
- **Input:** Execution run with `AntiFluffAuditDTO(logical_cohesion_score=0.92, cycle_detected=False, isolated_concept_count=2, unsupported_claims_count=0)` on a graph with 50 total nodes (isolated ratio = 4.0% <= 5%).
- **Expected Output:** `CausalCohesionEvaluator` marks BARS Levels 1, 2, 3, 4, 5 all as `PASSED`; `UnifiedScoringEngine` computes competence score 5.00 across all strictness modes; report table renders `matrix_causal_cohesion` with full positive points; `TraceEvent` emits `GlobalContextVarsDTO(evaluative_matrices={...})`.

### 2. Positive Scenario: Strong Cohesion (BARS 4.0 Threshold)
- **Input:** Execution run with `AntiFluffAuditDTO(logical_cohesion_score=0.84, cycle_detected=False, isolated_concept_count=5, unsupported_claims_count=1)` on a graph with 40 total nodes (isolated ratio = 12.5% > 5%).
- **Expected Output:** BARS Levels 1, 2, 3, 4 evaluate to `PASSED`; Level 5 evaluates to `FAILED` (due to isolated ratio > 5%); `UnifiedScoringEngine` computes competence score 3.17 at calibrated default strictness 70% (3.41 at 50% normal strictness, 3.67 linear at 0%).

### 3. Positive Scenario: Moderate Cohesion (BARS 3.0 Threshold)
- **Input:** Execution run with `AntiFluffAuditDTO(logical_cohesion_score=0.68, cycle_detected=False, isolated_concept_count=8, unsupported_claims_count=2)` on a graph with 30 total nodes.
- **Expected Output:** BARS Levels 1, 2, 3 evaluate to `PASSED`; Levels 4 and 5 evaluate to `FAILED`; `UnifiedScoringEngine` computes competence score 2.01 at calibrated default strictness 70% (2.27 at 50% normal strictness, 2.60 linear at 0%).

### 4. Positive Scenario: Discontinuous Cohesion (BARS 2.0 Threshold)
- **Input:** Execution run with `AntiFluffAuditDTO(logical_cohesion_score=0.48, cycle_detected=False, isolated_concept_count=12, unsupported_claims_count=4)` on a graph with 25 total nodes.
- **Expected Output:** BARS Levels 1 and 2 evaluate to `PASSED`; Levels 3, 4, 5 evaluate to `FAILED`; `UnifiedScoringEngine` computes competence score 1.35 at calibrated default strictness 70% (1.53 at 50% normal strictness, 1.80 linear at 0%).

### 5. Negative Scenario: Cyclic Reasoning Defect Grounding (BARS 1.0 Floor)
- **Input:** Execution run with `AntiFluffAuditDTO(logical_cohesion_score=0.35, cycle_detected=True, isolated_concept_count=18, unsupported_claims_count=6)`.
- **Expected Output:** BARS Level 1 evaluates to `PASSED` (Novice floor), Levels 2–5 evaluate to `FAILED`; `UnifiedScoringEngine` computes competence score exactly 1.07 at calibrated default strictness 70% (linear ratio 6.7%, curved ratio 1.7%, 1.0 / 15.0 weighted points); XAI log documents cycle detection and fragmentation penalty.

### 6. Negative Scenario: Severe Fragmentation Without Cycles (BARS 1.0 Floor)
- **Input:** Execution run with `AntiFluffAuditDTO(logical_cohesion_score=0.28, cycle_detected=False, isolated_concept_count=20, unsupported_claims_count=8)`.
- **Expected Output:** BARS Level 1 evaluates to `PASSED` (Novice floor), Levels 2–5 evaluate to `FAILED`; `UnifiedScoringEngine` computes score 1.07 at 70% strictness (1.14 at 50%, 1.27 linear).

### 7. Edge Case: Empty Graph / Zero Nodes Grounding to BARS 1.0 Novice Floor
- **Input:** Execution run where graph has 0 nodes (`total_nodes == 0`).
- **Expected Output:** `CausalCohesionEvaluator` enforces `total_nodes > 0` for Levels 2–5; with `total_nodes == 0`, Level 1 evaluates to `PASSED` (Novice floor) and Levels 2–5 evaluate to `FAILED` (1 / 15 weighted points, normalized ratio $1/15 \approx 0.0667$); `UnifiedScoringEngine` computes competence score exactly 1.07 at 70% calibrated default strictness (1.27 at 0% linear baseline), safely grounded to BARS 1.0 Novice floor without `ZeroDivisionError` or 5.0 score inflation.

### 8. Studio UI Scenario: Causal Source Dropdown Selects Upstream Causal Step
- **Input:** User opens Quorum Studio, selects "AI Steering" step card in `wf_9d68c573802341db`, and selects upstream causal step `sr_c4a5a1d15c00438a` from the `causalSourceStepId` dropdown.
- **Expected Output:** Card sets `stepDef.causalSourceStepId = "sr_c4a5a1d15c00438a"` and ensures `"sr_c4a5a1d15c00438a"` is present in `stepDef.dependsOn`; both steps remain 100% visible and ordered in the Zone B card list.

### 9. Studio UI Scenario: Causal Source Dropdown Cleared to None
- **Input:** User selects "None" in the `causalSourceStepId` dropdown on "AI Steering".
- **Expected Output:** Card sets `stepDef.causalSourceStepId = null` and removes `"sr_c4a5a1d15c00438a"` from `stepDef.dependsOn`; serialization validates with Pydantic and Freezed schemas.

### 10. Studio UI Scenario: All 4 Engine Steps Symmetrically Visible
- **Input:** User inspects `WorkflowStepsTab` in Quorum Studio for any workflow containing `PromptEngine`, `TDAEngine`, `CausalDiscoveryEngine`, and `SynthesisEngine` steps.
- **Expected Output:** Every step renders as its own card with visible blueprint, ID, dependencies, and input mappings without any artificial hidden step filtering.

### 11. Studio UI Scenario: Dropdown Swap Prunes Previous Causal Dependency
- **Input:** User changes `causalSourceStepId` dropdown on a specialist step from Causal Step A (`sr_c4a5a1d15c00438a`) to Causal Step B (`sr_other_causal`).
- **Expected Output:** Card sets `stepDef.causalSourceStepId = "sr_other_causal"`, removes `"sr_c4a5a1d15c00438a"` from `stepDef.dependsOn`, and appends `"sr_other_causal"` to `stepDef.dependsOn` without leaving orphaned dependencies.

### 12. Studio UI Scenario: Deselecting Dependency Chip Auto-Resets Causal Source
- **Input:** Specialist step has `causalSourceStepId == "sr_c4a5a1d15c00438a"` and `"sr_c4a5a1d15c00438a"` in `dependsOn`. User unchecks the dependency chip for `"sr_c4a5a1d15c00438a"`.
- **Expected Output:** Card removes `"sr_c4a5a1d15c00438a"` from `stepDef.dependsOn` and automatically resets `stepDef.causalSourceStepId = null`, preventing HTTP 422 `VALIDATION_FAILED` crashes on backend persistence.

### 13. Studio UI Scenario: Step Deletion Cascades Referential Integrity
- **Input:** User deletes upstream causal step `sr_c4a5a1d15c00438a` in `WorkflowStepsTab`.
- **Expected Output:** `_deleteStep` iterates over all remaining steps, removes `sr_c4a5a1d15c00438a` from their `dependsOn` arrays, and resets `causalSourceStepId = null` wherever it was referenced, preventing dangling references.

### 14. Seed Governance Scenario: Holistic Audit Initial Strictness Level 0%
- **Input:** Validation of `wf_9d68c573802341db` loaded from `backend_v2/seed/seed_data.json`.
- **Expected Output:** `Workflow.model_validate(wf).default_strictness_level == 0`; Quorum Studio Tab 4 (Arvioinnin ankaruus) slider initializes at 0% Vapaa (exponent 1.00 linear baseline).

### 15. Seed Governance Scenario: Report Structure Printable Sources Block Excluded
- **Input:** Validation of `prf_5d6e7f8091a2b3c4` loaded from `backend_v2/seed/seed_data.json`.
- **Expected Output:** `OutputProfile.model_validate(prf).target_block_order` contains 9 blocks without `"printable_sources_block"`; `"show_sources_summary_box" == false`; Quorum Studio Tab 4 (Raportin rakenne) renders "Lähdeluettelo ja viitteet" switch toggled OFF.

### 16. Multi-Step Causal Fusion Scenario: Idempotency and Zero Atom Duplication in Zone B
- **Input:** Execution of `wf_9d68c573802341db` where both `sr_4d2272d8b4864847` (Causal Analyst) and `sr_f1c1d71000000002` (AI Steering) reference `causal_source_step_id: "sr_c4a5a1d15c00438a"` and execute concurrently in Zone B via `asyncio.TaskGroup`.
- **Expected Output:** `DAGExecutor._evaluated_causal_sources` tracks `"sr_c4a5a1d15c00438a"`; `CausalCohesionEvaluator` executes exactly once; `execution_trace` contains exactly 5 `AtomResultDTO` instances for `blk_c0a1e50000000001` (zero duplicates); dynamic `matrix_block_id` is assigned to each atom; exactly one context update `TraceEvent` is emitted for `global_context_vars.evaluative_matrices["blk_c0a1e50000000001"]`.

### 17. SDUI Table Parity Scenario: 5-Level BARS Distribution Column Rendering
- **Input:** `ReportService` and `MatrixSummaryTableAdapter` render `matrix_summary_table` for `blk_c0a1e50000000001`.
- **Expected Output:** `MatrixDomainParser` resolves `step_evals_map` using deterministic IDs `tda_c0a1e50000000001` through `tda_c0a1e50000000005`; `MatrixSummaryTableAdapter` renders the `distribution` column with exactly 5 checkmarks/crosses corresponding to candidate performance without fallback lookups or blank rows.

### 18. Workflow Clone Relational Parity Scenario
- **Input:** Admin clones `wf_9d68c573802341db` containing `sr_f1c1d71000000002` (which depends on and references `causal_source_step_id: "sr_c4a5a1d15c00438a"`).
- **Expected Output:** Both Dart `WorkflowCloner` and Python `StudioWorkflowService` generate valid new step IDs; the cloned specialist step has its `causal_source_step_id` remapped to the new causal step ID (or throws `WORKFLOW_CLONE_FAILED` if unmapped); `StepRule.validate_step_rule_consistency` passes with zero 422 errors; repository persists cloned workflow cleanly.

### 19. Studio Step Authoring Topology & Append Lifecycle Scenario
- **Input:** In Quorum Studio, author creates a workflow, adds a causal discovery step (landing at the end of Zone B), and subsequently adds a specialist step (landing after the causal step).
- **Expected Output:** Causal step is placed upstream in `allSteps.sublist(0, index)` and is immediately selectable in the specialist card's dropdown; dropdown defensive value guard prevents Flutter assertion errors; no drag-and-drop or reordering controls are required.

### 20. Evaluator Strict Typing Invariance Scenario
- **Input:** Invoking `CausalCohesionEvaluator.evaluate_causal_cohesion` without `matrix_block_id` or with `None`.
- **Expected Output:** MyPy `--strict` and Python runtime raise `TypeError`; evaluator enforces explicit caller binding with zero default fallback.
