# Phase 4: DAG Router & Optional Chained Fusion Integration

**Overview:** Register `CausalDiscoveryEngine` in the typed `ENGINE_REGISTRY` under `EngineType` member CAUSAL_DISCOVERY, wire wave-based DAG execution in `backend_v2/services/orchestrator/dag_executor.py` for upstream discovery and downstream TDA fusion, implement `transform_causal_nodes_to_atoms` converting defined `CausalNodeDTO` to immutable `FlattenedAtom` instances, populate `global_context_vars.shuffled_atoms` under `_update_lock` for `LLMNodeStrategy` and `TDAEngine`, enforce data starvation Fail-Fast (`ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION`), enforce the Scoring Hook Separation Contract, implement the five stakeholder benefit pipelines, register Polyfactory test factories in `backend_v2/tests/factories/model_factories.py`, and build comprehensive integration tests in `backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py`.

**Source:** @[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md] Section 3, Phase 4: DAG Router & Optional Fusion Integration

**Target Files:**
- `[NEW] @[backend_v2/services/orchestrator/engines/registry.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor.py]`
- `[NEW] @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`
- `[MODIFY] @[backend_v2/tests/factories/model_factories.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| [NEW] `@[backend_v2/services/orchestrator/engines/registry.py]`, `@[backend_v2/services/orchestrator/dag_executor.py]` | Heuristic step-order detection, runtime flag branching, passing atoms directly to `request.shuffled_atoms` while bypassing `global_context_vars.shuffled_atoms` (triggering `LLMNodeStrategy` crash). Attaching `apply_scoring_logic_hook` to standalone causal runs causing crash on missing evaluative matrices. | Register `CausalDiscoveryEngine` in `ENGINE_REGISTRY` under `EngineType` member CAUSAL_DISCOVERY. In Wave N+1, DAG executor resolves `step.causal_source_step_id`, transforms upstream `CausalGraphPayloadDTO.nodes` to `FlattenedAtom` via `transform_causal_nodes_to_atoms`, and populates `global_context_vars = global_context_vars.model_copy(update={"shuffled_atoms": atoms})` under `_update_lock`. Standalone causal workflows omit `apply_scoring_logic_hook`; fusion workflows aggregate scores directly from `evaluative_matrices`. | Nondeterministic engine picking, automatic graph merging without declared contracts, bypassing `GlobalContextVarsDTO`. | Integration test in `test_causal_tda_fusion.py` asserting Pydantic `FlattenedAtom` schema validation and `GlobalContextVarsDTO` transit; `backend_audit_loop.py`. |
| [NEW] `@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`, `@[backend_v2/tests/factories/model_factories.py]` | Raw dictionary fixtures violating AST guardrail `QGR029`, unasserted mock calls, missing negative partition tests for data starvation. | Polyfactory factories (`CausalNodeDTOFactory`, `CausalGraphPayloadDTOFactory`) in `model_factories.py`. Integration tests asserting Fail-Fast with `CAUSAL_DISCOVERY_DATA_STARVATION` on empty upstream nodes, and verifying five stakeholder benefits. | Flaky multi-process network integration tests. | `backend_audit_loop.py` and `_ast_guardrails.py` passing QGR029. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 3. Verify `CausalDiscoveryEngine` exists in `backend_v2/services/orchestrator/engines/causal_discovery_engine.py` and passes its unit tests.</action>
    <action>Look forward: Verify if DAG executor wiring correctly populates `global_context_vars.shuffled_atoms` for downstream TDA consumption, satisfying contracts for Phase 5 SDUI presentation.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]) and the Tracker document (@[docs/epic/EPIC_154_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_154/04_phase4_plan.md] @[docs/epic/EPIC_154_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>CausalDiscoveryEngine registered in ENGINE_REGISTRY in [NEW] backend_v2/services/orchestrator/engines/registry.py under EngineType member CAUSAL_DISCOVERY.</item>
    <item>NodeExecutor in dag_executor.py resolves CausalDiscoveryEngine deterministically via build_execution_engine(step_def.engine_type, self.deps.prompt_compiler).</item>
    <item>Wave-based TaskGroup execution integrates upstream discovery in Wave N and downstream TDA fusion in Wave N+1.</item>
    <item>transform_causal_nodes_to_atoms implemented converting CausalNodeDTO instances into FlattenedAtom instances enforcing ConfigDict(strict=True, extra="forbid", frozen=True).</item>
    <item>DAGExecutor resolves step.causal_source_step_id, transforms causal nodes, and populates global_context_vars.shuffled_atoms and exec_record.metadata.global_context_vars.shuffled_atoms under _update_lock.</item>
    <item>Data starvation Fail-Fast raises AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION) if upstream discovery produces 0 nodes.</item>
    <item>Scoring Hook Separation Contract enforced: standalone causal workflows omit apply_scoring_logic_hook; fusion workflows execute it exclusively when evaluative_matrices is populated.</item>
    <item>Five stakeholder benefit pipelines implemented: Root Cause Attribution, Anti-Fluff Shield, Prescriptive Remediation, Visual XAI Data Projection, Fair Scoring Deduplication.</item>
    <item>Polyfactory factories CausalNodeDTOFactory and CausalGraphPayloadDTOFactory added to backend_v2/tests/factories/model_factories.py complying with QGR029.</item>
    <item>Integration tests in test_causal_tda_fusion.py pass 100%.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do not pass ExtractedAtom instances to TDAEngine; must transform to FlattenedAtom.</forbidden>
    <forbidden>Do not bypass global_context_vars.shuffled_atoms during fusion chaining.</forbidden>
    <forbidden>Do not attach apply_scoring_logic_hook to standalone causal workflows lacking criteria matrices.</forbidden>
    <forbidden>Do not use raw dictionaries for test fixtures; enforce Polyfactory QGR029 compliance.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>[NEW] @[backend_v2/services/orchestrator/engines/registry.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
    <backend>@[backend_v2/tests/factories/model_factories.py]</backend>
  </touched_artifacts>

  <step id="4.1" name="REGISTER_CAUSAL_DISCOVERY_ENGINE_IN_REGISTRY">
    <action>In [NEW] @[backend_v2/services/orchestrator/engines/registry.py], bind EngineType member CAUSAL_DISCOVERY in ENGINE_REGISTRY to instantiate CausalDiscoveryEngine(prompt_compiler). Verify build_execution_engine(EngineType member CAUSAL_DISCOVERY, prompt_compiler) returns CausalDiscoveryEngine instance.</action>
    <constraint invariant="single_pipeline_invariant_mandate">Engine dispatch flows through the single deterministic registry factory.</constraint>
  </step>

  <step id="4.2" name="WAVE_BASED_TASK_GROUP_EXECUTION_INTEGRATION">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py], integrate causal discovery execution into Kahn's wave-based TaskGroup: upstream causal discovery steps execute in Wave N, writing output CausalGraphPayloadDTO into exec_record.step_states[step_id]. In Wave N+1, downstream fusion steps resolve step.causal_source_step_id to read the upstream output.</action>
    <constraint invariant="python_314_concurrency_strictness">Execute waves via asyncio.TaskGroup with atomic state transitions under _update_lock.</constraint>
  </step>

  <step id="4.3" name="TRANSFORM_CAUSAL_NODES_TO_ATOMS_AND_INJECT_GLOBAL_CONTEXT">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py], implement transform_causal_nodes_to_atoms(nodes: list[CausalNodeDTO]) -&gt; list[FlattenedAtom]. Map each CausalNodeDTO to a FlattenedAtom instance with atom_id=node.node_id, text=node.claim, quote=node.source_quote, paragraph_ref=node.paragraph_ref, adhering to V2CoreBase with ConfigDict(strict=True, extra="forbid", frozen=True).</action>
    <action>When step.causal_source_step_id is set, resolve upstream CausalGraphPayloadDTO from step_states[step.causal_source_step_id]. Transform nodes via transform_causal_nodes_to_atoms, populate global_context_vars = global_context_vars.model_copy(update={"shuffled_atoms": atoms}), and commit to exec_record.metadata.global_context_vars.shuffled_atoms under _update_lock to feed downstream LLMNodeStrategy and TDAEngine.</action>
    <constraint invariant="the_zero_compromise_pledge">Preserve FlattenedAtom strict contract with zero permissive type fallbacks.</constraint>
  </step>

  <step id="4.4" name="DATA_STARVATION_FAIL_FAST_ENFORCEMENT">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py], verify that if step.causal_source_step_id is declared, but the upstream step output has 0 nodes or failed, Fail-Fast triggers immediately with AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION, "Upstream causal discovery step produced 0 valid proposition nodes for downstream evaluation.").</action>
    <constraint invariant="universal_fail_fast">Zero silent empty evaluations; fail loudly when upstream data is starved.</constraint>
  </step>

  <step id="4.5" name="SCORING_HOOK_SEPARATION_AND_STAKEHOLDER_BENEFITS">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py], enforce Scoring Hook Separation: standalone non-matrix causal discovery workflows omit apply_scoring_logic_hook to prevent false-positive crashes on empty evaluative matrices. apply_scoring_logic_hook executes exclusively in workflows containing Phase 1B criteria matrix evaluation.</action>
    <action>Execute five stakeholder benefit pipelines: Root Cause Attribution (blame_parent_ids), Anti-Fluff Shield (AntiFluffAuditDTO), Prescriptive Remediation (PrescriptiveRemediationDTO), Visual XAI Data Projection (node overlay statuses), and Fair Scoring Deduplication (softening secondary cascading penalties via causal_secondary_fault_dampening).</action>
    <constraint invariant="zero_service_layer_fallbacks">Enforce strict typing across all five benefit calculations.</constraint>
  </step>

  <step id="4.6" name="POLYFACTORY_FIXTURES_AND_FUSION_INTEGRATION_TESTS">
    <action>In @[backend_v2/tests/factories/model_factories.py], define CausalNodeDTOFactory(ModelFactory[CausalNodeDTO]) and CausalGraphPayloadDTOFactory(ModelFactory[CausalGraphPayloadDTO]) complying with AST guardrail QGR029.</action>
    <action>In [NEW] @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py], implement integration tests verifying: test_causal_to_tda_fusion_transforms_nodes_to_flattened_atoms, test_causal_fusion_starvation_raises_app_exception, test_causal_fusion_populates_global_context_vars_shuffled_atoms, test_fair_scoring_deduplication_applies_dampening, test_standalone_causal_workflow_omits_scoring_hook.</action>
    <constraint invariant="universal_fail_fast">Ensure all fixtures adhere to QGR029 with zero naked dictionaries.</constraint>
  </step>

  <test_contracts>
    <test name="test_causal_to_tda_fusion_transforms_nodes_to_flattened_atoms" category="positive">
      <input>list of 3 CausalNodeDTO instances passed to transform_causal_nodes_to_atoms</input>
      <expected>returns list of 3 FlattenedAtom instances with exact atom_id, text, quote, paragraph_ref</expected>
    </test>
    <test name="test_causal_fusion_starvation_raises_app_exception" category="error_path">
      <input>DAG execution where upstream causal step produced CausalGraphPayloadDTO with nodes=[]</input>
      <expected>raises AppException with ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION</expected>
    </test>
    <test name="test_causal_fusion_populates_global_context_vars_shuffled_atoms" category="positive">
      <input>DAG execution with step.causal_source_step_id set</input>
      <expected>downstream hook_state.global_context_vars.shuffled_atoms is populated with FlattenedAtom list</expected>
    </test>
    <test name="test_fair_scoring_deduplication_applies_dampening" category="positive">
      <input>CausalTdaFusionResultDTO with independent errors and cascading faults</input>
      <expected>deduplicated_penalty_points == raw_penalty_points - dampened_savings_points with dampening factor 0.25</expected>
    </test>
    <test name="test_standalone_causal_workflow_omits_scoring_hook" category="boundary">
      <input>Workflow with StepType.CAUSAL_DISCOVERY and zero criteria matrices</input>
      <expected>executes successfully without invoking apply_scoring_logic_hook or raising validation errors on empty matrices</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test</action>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py --test</action>
    <action>Execute: uv run python scripts/_ast_guardrails.py to verify QGR029 compliance on model_factories.py</action>
  </validation_gate>
</execution_protocol>
