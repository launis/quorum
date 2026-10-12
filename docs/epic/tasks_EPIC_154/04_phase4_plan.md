# Phase 4: DAG Router & Optional Chained Fusion Integration

**Overview:** Register `CausalDiscoveryEngine` in the typed `ENGINE_REGISTRY` under `EngineType` member CAUSAL_DISCOVERY, wire wave-based DAG execution in `backend_v2/services/orchestrator/dag_executor.py` for upstream discovery and downstream TDA fusion, implement `transform_causal_nodes_to_atoms` converting defined `CausalNodeDTO` to immutable `FlattenedAtom` instances, populate `global_context_vars.shuffled_atoms` under `_update_lock` for `LLMNodeStrategy` and `TDAEngine`, enforce data starvation Fail-Fast (`ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION`), enforce the Scoring Hook Separation Contract, implement the five stakeholder benefit pipelines, register Polyfactory test factories in `backend_v2/tests/factories/model_factories.py`, and build comprehensive integration tests in `backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py`.

**Source:** @[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md] Section 3, Phase 4: DAG Router & Optional Fusion Integration

**Target Files:**
- `[MODIFY] @[backend_v2/services/orchestrator/engines/registry.py#L35-L60]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor.py#L577-L1679]`
- `[NEW] @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`
- `[MODIFY] @[backend_v2/tests/factories/model_factories.py#L403-L417]`
- `[MODIFY] @[backend_v2/tests/factories/test_model_factories.py#L39-L46]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/engines/test_registry.py#L58-L65]`
- `[DELETE] @[backend_v2/tests/unit/services/orchestrator/engines/test_engine_registry.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| [MODIFY] `@[backend_v2/services/orchestrator/engines/registry.py#L35-L60]` | Procedural engine resolution branching, loose string dispatching, or catching missing engine types with generic exceptions. | Register `CausalDiscoveryEngine` in `ENGINE_REGISTRY` under `EngineType.CAUSAL_DISCOVERY`. Factory `build_execution_engine` deterministically constructs `CausalDiscoveryEngine(prompt_compiler)`. | Speculative multi-parameter dependency injection or dynamic reflection factories. | Unit tests in `test_registry.py` asserting `EngineType.CAUSAL_DISCOVERY` resolves to `CausalDiscoveryEngine` with `telemetry_strategy_label == "causal"`. |
| [MODIFY] `@[backend_v2/services/orchestrator/dag_executor.py#L577-L1679]` | Heuristic step-order guessing, mutating `FlattenedAtom` with nonexistent fields (`text`, `quote`, `paragraph_ref`), bypassing `global_context_vars.shuffled_atoms` during fusion, silent recovery on starved upstream discovery, invoking `apply_scoring_logic_hook` in standalone workflows without criteria matrices. | Transform `CausalNodeDTO` to `FlattenedAtom` strictly mapping `atom_id=node.node_id`, `question=node.claim`, `anchor_target=node.paragraph_ref or ""`, `extraction_rule=node.source_quote or ""`. Enforce `CAUSAL_DISCOVERY_DATA_STARVATION` Fail-Fast if upstream produces 0 nodes. Inject into `global_context_vars.shuffled_atoms` under `_update_lock`. Compute five stakeholder benefits and emit `CausalTdaFusionResultDTO`. | Speculative intermediary blackboard wrappers, duplicate graph caching, parallel scoring pipelines. | `backend_audit_loop.py` on `dag_executor.py`, integration tests in `test_causal_tda_fusion.py` asserting Pydantic validation and `AppException`. |
| [NEW] `@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]` | Raw dictionary fixtures violating AST guardrail `QGR029`, unasserted mocks, missing negative partitions for data starvation, missing boundary tests for empty node collections. | Comprehensive ISTQB test suite covering positive fusion chaining, empty node data starvation, missing upstream step validation, fair scoring deduplication arithmetic, prescriptive remediation, anti-fluff audit, and standalone workflow execution. | Flaky multi-process network integration tests or real LLM calls during unit testing. | `backend_audit_loop.py` passing 100% with 0 AST warnings and strict type checking. |
| [MODIFY] `@[backend_v2/tests/factories/model_factories.py#L403-L417]`, `@[backend_v2/tests/factories/test_model_factories.py#L39-L46]` | Untyped dictionary fixtures in test suites violating AST guardrail `QGR029`. | Define `CausalNodeDTOFactory` and `CausalGraphPayloadDTOFactory` in `model_factories.py`. Register in `ALL_FACTORIES` in `test_model_factories.py`. | Over-parameterized factory callbacks or circular foreign key generators. | `pytest backend_v2/tests/factories/test_model_factories.py` asserting valid instantiation roundtrip. |
| [MODIFY] `@[backend_v2/tests/unit/services/orchestrator/engines/test_registry.py#L58-L65]`, `[DELETE] @[backend_v2/tests/unit/services/orchestrator/engines/test_engine_registry.py]` | Duplicate test file maintenance overhead and obsolete assertion expecting `EngineType.CAUSAL_DISCOVERY` to raise an unsupported `AppException`. | Delete duplicate `test_engine_registry.py`. In `test_registry.py`, update `test_build_execution_engine_causal_discovery_returns_causal_discovery_engine` and assert `EngineType.CAUSAL_DISCOVERY in ENGINE_REGISTRY`. | Redundant duplicate test suites covering the same factory. | `pytest backend_v2/tests/unit/services/orchestrator/engines/test_registry.py` passing 100%. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 3. Verify `CausalDiscoveryEngine` exists in `backend_v2/services/orchestrator/engines/causal_discovery_engine.py` and passes its unit tests.</action>
    <action>Look forward: Verify if DAG executor wiring correctly populates `global_context_vars.shuffled_atoms` for downstream TDA consumption, satisfying contracts for Phase 5 SDUI presentation.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]) and the Tracker document (@[docs/epic/EPIC_154_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_154/04_phase4_plan.md] @[docs/epic/EPIC_154_tracker.md]`.</directive>
  </step>

  <step id="4.0" name="PRE_IMPLEMENTATION_CLEANUPS">
    <action>Delete redundant duplicate test file [DELETE] @[backend_v2/tests/unit/services/orchestrator/engines/test_engine_registry.py] and consolidate all engine registry test coverage into @[backend_v2/tests/unit/services/orchestrator/engines/test_registry.py#L58-L65].</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/engines/test_registry.py#L58-L65], replace the test expecting EngineType.CAUSAL_DISCOVERY to be unsupported with a positive assertion verifying EngineType.CAUSAL_DISCOVERY resolves to CausalDiscoveryEngine, and verify unmapped engine types raise AppException with ErrorCodes.VALIDATION_FAILED.</action>
    <constraint invariant="the_no_legacy_mandate">Eradicate duplicate test files and obsolete negative assertions before implementing new registrations.</constraint>
  </step>

  <step id="4.1" name="REGISTER_CAUSAL_DISCOVERY_ENGINE_IN_REGISTRY">
    <action>In @[backend_v2/services/orchestrator/engines/registry.py#L35-L60], bind EngineType member CAUSAL_DISCOVERY in ENGINE_REGISTRY to instantiate CausalDiscoveryEngine(prompt_compiler). Verify build_execution_engine(EngineType.CAUSAL_DISCOVERY, prompt_compiler) returns CausalDiscoveryEngine instance.</action>
    <constraint invariant="single_pipeline_invariant_mandate">Engine dispatch flows through the single deterministic registry factory.</constraint>
  </step>

  <step id="4.2" name="WAVE_BASED_TASK_GROUP_EXECUTION_INTEGRATION">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L577-L1679], integrate causal discovery execution into Kahn's wave-based TaskGroup: upstream causal discovery steps execute in Wave N, writing output CausalGraphPayloadDTO into exec_record.execution_trace and projector snapshot. In Wave N+1, downstream fusion steps resolve step.causal_source_step_id to read the upstream output.</action>
    <constraint invariant="python_314_concurrency_strictness">Execute waves via asyncio.TaskGroup with atomic state transitions under _update_lock.</constraint>
  </step>

  <step id="4.3" name="TRANSFORM_CAUSAL_NODES_TO_ATOMS_AND_INJECT_GLOBAL_CONTEXT">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L577-L1679], implement transform_causal_nodes_to_atoms(nodes: list[CausalNodeDTO]) -&gt; list[FlattenedAtom]. Map each CausalNodeDTO to a FlattenedAtom instance strictly using atom_id=node.node_id, question=node.claim, anchor_target=node.paragraph_ref or "", extraction_rule=node.source_quote or "", adhering to V2CoreBase with ConfigDict(strict=True, extra="forbid", frozen=True).</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L577-L1679], when step.causal_source_step_id is set, resolve upstream CausalGraphPayloadDTO from execution_trace or projector snapshot. Transform nodes via transform_causal_nodes_to_atoms, populate global_context_vars = global_context_vars.model_copy(update={"shuffled_atoms": atoms}), and commit to exec_record.metadata.global_context_vars.shuffled_atoms under _update_lock to feed downstream LLMNodeStrategy and TDAEngine.</action>
    <constraint invariant="the_zero_compromise_pledge">Preserve FlattenedAtom strict contract with zero permissive type fallbacks.</constraint>
  </step>

  <step id="4.4" name="DATA_STARVATION_FAIL_FAST_ENFORCEMENT">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L577-L1679], verify that if step.causal_source_step_id is declared, but the upstream step output has 0 nodes or failed, Fail-Fast triggers immediately with AppException(message="Upstream causal discovery step produced 0 valid proposition nodes for downstream evaluation.", status_code=500, details={"error_code": ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION}).</action>
    <constraint invariant="universal_fail_fast">Zero silent empty evaluations; fail loudly when upstream data is starved.</constraint>
  </step>

  <step id="4.5" name="SCORING_HOOK_SEPARATION_AND_STAKEHOLDER_BENEFITS">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L577-L1679], enforce Scoring Hook Separation: standalone non-matrix causal discovery workflows omit apply_scoring_logic_hook to prevent false-positive crashes on empty evaluative matrices. apply_scoring_logic_hook executes exclusively in workflows containing Phase 1B criteria matrix evaluation.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L577-L1679], implement compute_causal_tda_fusion_result(graph: CausalGraphPayloadDTO, evaluative_matrices: dict[str, float] | None = None, evaluated_atoms: list[AtomResultDTO] | None = None, dampening_factor: float | None = None) -&gt; CausalTdaFusionResultDTO executing five stakeholder benefit pipelines: Root Cause Attribution (blame_parent_ids), Anti-Fluff Shield (AntiFluffAuditDTO), Prescriptive Remediation (PrescriptiveRemediationDTO), Visual XAI Data Projection (node overlay statuses), and Fair Scoring Deduplication (softening secondary cascading penalties via causal_secondary_fault_dampening from settings).</action>
    <constraint invariant="zero_service_layer_fallbacks">Enforce strict typing across all five benefit calculations.</constraint>
  </step>

  <step id="4.6" name="POLYFACTORY_FIXTURES_AND_FUSION_INTEGRATION_TESTS">
    <action>In @[backend_v2/tests/factories/model_factories.py#L403-L417], define CausalNodeDTOFactory(ModelFactory[CausalNodeDTO]) and CausalGraphPayloadDTOFactory(ModelFactory[CausalGraphPayloadDTO]) complying with AST guardrail QGR029.</action>
    <action>In @[backend_v2/tests/factories/test_model_factories.py#L39-L46], register CausalNodeDTOFactory and CausalGraphPayloadDTOFactory in ALL_FACTORIES to assert valid instantiation roundtrip.</action>
    <action>In [NEW] @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py], implement comprehensive integration and unit tests verifying: test_causal_to_tda_fusion_transforms_nodes_to_flattened_atoms, test_transform_causal_nodes_empty_list_returns_empty_list, test_transform_causal_nodes_with_none_quote_transforms_cleanly, test_causal_fusion_starvation_empty_nodes_raises_app_exception, test_causal_fusion_missing_upstream_step_raises_app_exception, test_causal_fusion_populates_global_context_vars_shuffled_atoms, test_fair_scoring_deduplication_applies_dampening, test_fair_scoring_identity_violation_raises_value_error, test_prescriptive_remediation_identifies_root_causes, test_anti_fluff_audit_identifies_isolated_concepts, test_standalone_causal_workflow_omits_scoring_hook.</action>
    <constraint invariant="universal_fail_fast">Ensure all fixtures adhere to QGR029 with zero naked dictionaries.</constraint>
  </step>

  <dod_checklist>
    <item>Duplicate test file test_engine_registry.py deleted and consolidated into test_registry.py.</item>
    <item>CausalDiscoveryEngine registered in ENGINE_REGISTRY in backend_v2/services/orchestrator/engines/registry.py under EngineType member CAUSAL_DISCOVERY.</item>
    <item>NodeExecutor in dag_executor.py resolves CausalDiscoveryEngine deterministically via build_execution_engine(step_def.engine_type, self.deps.prompt_compiler).</item>
    <item>Wave-based TaskGroup execution integrates upstream discovery in Wave N and downstream TDA fusion in Wave N+1.</item>
    <item>transform_causal_nodes_to_atoms implemented converting CausalNodeDTO instances into FlattenedAtom instances strictly mapping atom_id, question, anchor_target, extraction_rule enforcing ConfigDict(strict=True, extra="forbid", frozen=True).</item>
    <item>DAGExecutor resolves step.causal_source_step_id, transforms causal nodes, and populates global_context_vars.shuffled_atoms and exec_record.metadata.global_context_vars.shuffled_atoms under _update_lock.</item>
    <item>Data starvation Fail-Fast raises AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION) if upstream discovery produces 0 nodes.</item>
    <item>Scoring Hook Separation Contract enforced: standalone causal workflows omit apply_scoring_logic_hook; fusion workflows execute it exclusively when evaluative_matrices is populated.</item>
    <item>compute_causal_tda_fusion_result implements five stakeholder benefit pipelines: Root Cause Attribution, Anti-Fluff Shield, Prescriptive Remediation, Visual XAI Data Projection, Fair Scoring Deduplication.</item>
    <item>Polyfactory factories CausalNodeDTOFactory and CausalGraphPayloadDTOFactory added to backend_v2/tests/factories/model_factories.py complying with QGR029 and tested in test_model_factories.py.</item>
    <item>All 11 integration and boundary tests in test_causal_tda_fusion.py pass 100%.</item>
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
    <forbidden>Do not pass hallucinated fields (text, quote, paragraph_ref) to FlattenedAtom; must strictly pass atom_id, question, anchor_target, extraction_rule.</forbidden>
    <forbidden>Do not bypass global_context_vars.shuffled_atoms during fusion chaining.</forbidden>
    <forbidden>Do not attach apply_scoring_logic_hook to standalone causal workflows lacking criteria matrices.</forbidden>
    <forbidden>Do not use raw dictionaries for test fixtures; enforce Polyfactory QGR029 compliance.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/engines/registry.py#L35-L60]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py#L577-L1679]</backend>
    <backend>[NEW] @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]</backend>
    <backend>@[backend_v2/tests/factories/model_factories.py#L403-L417]</backend>
    <backend>@[backend_v2/tests/factories/test_model_factories.py#L39-L46]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/engines/test_registry.py#L58-L65]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/services/orchestrator/engines/test_engine_registry.py]</backend>
  </touched_artifacts>

  <test_contracts>
    <test name="test_causal_to_tda_fusion_transforms_nodes_to_flattened_atoms" category="positive">
      <input>list of 3 CausalNodeDTO instances passed to transform_causal_nodes_to_atoms</input>
      <expected>returns list of 3 FlattenedAtom instances with exact atom_id=node.node_id, question=node.claim, anchor_target=node.paragraph_ref, extraction_rule=node.source_quote</expected>
    </test>
    <test name="test_transform_causal_nodes_empty_list_returns_empty_list" category="boundary">
      <input>empty list [] passed to transform_causal_nodes_to_atoms</input>
      <expected>returns empty list []</expected>
    </test>
    <test name="test_transform_causal_nodes_with_none_quote_transforms_cleanly" category="boundary">
      <input>CausalNodeDTO with source_quote=None, paragraph_ref=None</input>
      <expected>returns FlattenedAtom with anchor_target="", extraction_rule=""</expected>
    </test>
    <test name="test_causal_fusion_starvation_empty_nodes_raises_app_exception" category="error_path">
      <input>DAG execution where upstream causal step produced CausalGraphPayloadDTO with nodes=[]</input>
      <expected>raises AppException with ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION</expected>
    </test>
    <test name="test_causal_fusion_missing_upstream_step_raises_app_exception" category="error_path">
      <input>DAG execution with step.causal_source_step_id pointing to missing step</input>
      <expected>raises AppException with ErrorCodes.VALIDATION_FAILED</expected>
    </test>
    <test name="test_causal_fusion_populates_global_context_vars_shuffled_atoms" category="positive">
      <input>DAG execution with step.causal_source_step_id set</input>
      <expected>downstream global_context_vars.shuffled_atoms is populated with FlattenedAtom list</expected>
    </test>
    <test name="test_fair_scoring_deduplication_applies_dampening" category="positive">
      <input>CausalTdaFusionResultDTO with independent errors and cascading faults</input>
      <expected>deduplicated_penalty_points == raw_penalty_points - dampened_savings_points with dampening factor 0.25</expected>
    </test>
    <test name="test_fair_scoring_identity_violation_raises_value_error" category="error_path">
      <input>FairScoringBreakdownDTO instantiation where raw_penalty_points != deduplicated + dampened</input>
      <expected>raises ValueError with scoring identity violation message</expected>
    </test>
    <test name="test_prescriptive_remediation_identifies_root_causes" category="positive">
      <input>CausalGraphPayloadDTO with root causes unlocking downstream cascading failures</input>
      <expected>returns PrescriptiveRemediationDTO instances for root cause nodes with non-empty unlocks_node_ids</expected>
    </test>
    <test name="test_anti_fluff_audit_identifies_isolated_concepts" category="positive">
      <input>CausalGraphPayloadDTO with isolated claims lacking links</input>
      <expected>AntiFluffAuditDTO with isolated_concept_count == len(isolated_node_ids) and logical_cohesion_score properly dampened</expected>
    </test>
    <test name="test_standalone_causal_workflow_omits_scoring_hook" category="boundary">
      <input>Workflow with StepType.CAUSAL_DISCOVERY and zero criteria matrices</input>
      <expected>executes successfully without invoking apply_scoring_logic_hook or raising validation errors on empty matrices</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/registry.py --test</action>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test</action>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/tests/factories/model_factories.py --test</action>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py --test</action>
    <action>Execute: uv run python scripts/_ast_guardrails.py to verify QGR029 compliance on model_factories.py</action>
    <action>Execute: uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_154/04_phase4_plan.md</action>
  </validation_gate>
</execution_protocol>

