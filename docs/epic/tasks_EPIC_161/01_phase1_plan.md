<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

# Phase 1: Pre-Implementation Technical Debt Cleanups & Typed Topological Envelope Foundation

**Overview:** Execute scoped Boy Scout technical debt cleanups in `@[backend_v2/services/blueprint.py#L127-L698]` (removing raw `if type(content) is dict:` inspection in favor of strict `StepOutputDTO` and `TypeAdapter` validation) and wire the PostgreSQL 19 3-way Toulmin SQL join `@[backend_v2/database/postgres/graph_adapter.py#L347-L431]` (`CteReasoningStrategy.find_falsified_claims`) returning `list[FalsifiedClaimMatch]` (`@[backend_v2/models/domain/proposition_graph.py#L343-L391]`) into `@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465]` and `@[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py#L211-L363]`. Enrich `DistilledEvaluation` (`@[backend_v2/models/domain/synthesis.py#L131-L155]`), `ReducedAtomDTO` (`@[backend_v2/models/dtos/atom_evaluation.py#L43-L67]`), `CausalRootCauseDiagnosisDTO`, and `CausalTdaFusionResultDTO` (`@[backend_v2/models/dtos/causal_discovery.py]`), raise `max_synthesis_reasoning_length` from `300` to `1500` characters in `@[backend_v2/settings.py]` so `step_3_evaluate_anti_patterns` and `step_4_final_conclusion` of `ReasoningStepDTO` (`@[backend_v2/models/dtos/atom_evaluation.py#L21-L40]`) survive compression intact, and remediate asymmetric distillation and topological deficit sorting in `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L105-L179]`, `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L135-L140]`, and `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L182-L393]`.

**Source:** @[docs/epic/EPIC_161_topological_synthesis_cohesion.md#L173-L185] Phase 1: Pre-Implementation Technical Debt Cleanups & Typed Topological Envelope Foundation

**Target Files:**
- `[MODIFY] @[backend_v2/services/blueprint.py#L127-L698]`
- `[MODIFY] @[backend_v2/database/postgres/graph_adapter.py#L347-L431]`
- `[MODIFY] @[backend_v2/models/domain/proposition_graph.py#L343-L391]`
- `[MODIFY] @[backend_v2/models/dtos/causal_discovery.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L38-L87]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py#L211-L363]`
- `[MODIFY] @[backend_v2/models/domain/synthesis.py#L131-L155]`
- `[MODIFY] @[backend_v2/models/dtos/atom_evaluation.py#L21-L40]`
- `[MODIFY] @[backend_v2/models/dtos/atom_evaluation.py#L43-L67]`
- `[MODIFY] @[backend_v2/services/orchestrator/matrix_reducer.py#L121-L239]`
- `[MODIFY] @[backend_v2/settings.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L105-L179]`
- `[MODIFY] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L135-L140]`
- `[MODIFY] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L182-L393]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_blueprint.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_causal_tda_fusion_unit.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/services/blueprint.py#L127-L698]`** | Eradicate `if type(content) is dict:` in lines `584–592` of `@[backend_v2/services/blueprint.py#L127-L698]` scanning `execution.execution_trace` for `causal_result` via raw dictionary type checks. | Extract `CausalTdaFusionResultDTO` via strict `StepOutputDTO` and `TypeAdapter(CausalTdaFusionResultDTO \| CausalGraphPayloadDTO)` validation in `@[backend_v2/services/blueprint.py#L127-L698]`. | Do NOT build a parallel trace parser; validate structured step output envelopes directly at the boundary. | `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test --ast-strict` + unit tests in `@[backend_v2/tests/unit/services/test_blueprint.py]`. |
| **`@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L38-L87]`**<br>**`@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465]`**<br>**`@[backend_v2/database/postgres/graph_adapter.py#L347-L431]`**<br>**`@[backend_v2/models/domain/proposition_graph.py#L343-L391]`**<br>**`@[backend_v2/models/dtos/causal_discovery.py]`**<br>**`@[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py#L211-L363]`** | Eradicate emitting unresolved node IDs (`root_cause_parent_id`, `failing_node_id`) without human-readable claim text, and eradicate leaving `CteReasoningStrategy.find_falsified_claims()` (`FalsifiedClaimMatch`) uncalled in dead-code isolation. | Enrich `CausalRootCauseDiagnosisDTO` with resolved `root_cause_claim: str`, `failing_node_claim: str`, and `warrant_relation: Literal["supports", "rebuts", "warrants"]`. Wire `find_falsified_claims()` into the causal fusion stage so `CausalTdaFusionResultDTO` carries `falsified_claims: list[FalsifiedClaimMatch]`. | Do NOT build a new graph database engine or recursive Python graph walker; leverage the existing PostgreSQL 19 3-way SQL join (`find_falsified_claims`) and existing `compute_causal_tda_fusion_result` node index. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py --test --ast-strict` + unit tests in `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_causal_tda_fusion_unit.py]` and `@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`. |
| **`@[backend_v2/models/domain/synthesis.py#L131-L155]`**<br>**`@[backend_v2/models/dtos/atom_evaluation.py#L21-L40]`**<br>**`@[backend_v2/models/dtos/atom_evaluation.py#L43-L67]`**<br>**`@[backend_v2/services/orchestrator/matrix_reducer.py#L121-L239]`**<br>**`@[backend_v2/settings.py]`**<br>**`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L105-L179]`**<br>**`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L135-L140]`**<br>**`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L182-L393]`** | Eradicate dropping `depends_on_tda_ids`, `short_circuit_reason_tda_ids`, and `is_inverse_evidence` during `_clean_and_distill_payload` (lines `239–352` and `298–333`) and `reduce_matrix`. Eradicate slicing `semantic_reasoning` at `300` chars (lines `268–270`, `340–342`), which cuts off `step_3_evaluate_anti_patterns` and `step_4_final_conclusion` from `ReasoningStepDTO`, and eradicate dropping quote-less `FAILED`/`N_A` atoms (lines `265–266`, `336–338`). Eradicate sorting deficits by `-len(e.exact_quotes)` (always `0` for `FAILED`/`N_A` per `@[backend_v2/models/dtos/atom_result.py#L139-L172]`). | Raise `max_synthesis_reasoning_length` to `1500` in `@[backend_v2/settings.py]` (line `296`). Enrich `DistilledEvaluation` (`ConfigDict(extra="forbid", strict=True, frozen=True)`) with `depends_on_tda_ids: list[str]`, `short_circuit_reason_tda_ids: list[str]`, `is_inverse_evidence: bool`, and `topological_out_degree: int`, and enrich `ReducedAtomDTO` with `depends_on_tda_ids: list[str]`, `short_circuit_reason_tda_ids: list[str]`, and `is_inverse_evidence: bool`. Retain all `FAILED`/`N_A`/`is_inverse_evidence` evaluations in `_clean_and_distill_payload` and sort `deficits` by `(-int(e.is_inverse_evidence), -e.topological_out_degree, len(e.short_circuit_reason_tda_ids), atom_id)`. | Do NOT create a separate compressor service or secondary distillation pass. Mutate `DistilledEvaluation`, `ReducedAtomDTO`, `settings.py`, and `_prune_and_stratify_evaluations` in-place within the single compressor pipeline. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --test --ast-strict` + BVA unit tests in `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py]`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the current implementation of @[backend_v2/services/blueprint.py#L127-L698], @[backend_v2/models/domain/synthesis.py#L131-L155], @[backend_v2/models/dtos/atom_evaluation.py#L21-L40], @[backend_v2/models/dtos/atom_evaluation.py#L43-L67], @[backend_v2/models/dtos/atom_result.py#L82-L172], @[backend_v2/models/dtos/atom_result.py#L139-L172], @[backend_v2/services/orchestrator/topological_evaluator.py#L56-L175], @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L105-L179], @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L182-L393], and @[backend_v2/services/orchestrator/synthesis_distiller.py#L43-L115].</action>
    <action>Look forward: Verify that Step 1.1 eradicates raw dict type checks and wires the PostgreSQL 19 3-way Toulmin falsification join before Step 1.2 enriches the DTO schemas and Step 1.3 implements Asymmetric Epistemic Distillation and topological deficit sorting.</action>
    <constraint invariant="universal_fail_fast">All enriched Pydantic V2 models MUST enforce ConfigDict(strict=True, extra="forbid", frozen=True) with 100% Full-Duplex Serialization Parity.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_161_topological_synthesis_cohesion.md] and @[docs/epic/EPIC_161_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_161/01_phase1_plan.md] @[docs/epic/EPIC_161_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/services/blueprint.py]</backend>
    <backend>@[backend_v2/database/postgres/graph_adapter.py]</backend>
    <backend>@[backend_v2/models/domain/proposition_graph.py]</backend>
    <backend>@[backend_v2/models/dtos/causal_discovery.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]</backend>
    <backend>@[backend_v2/models/domain/synthesis.py]</backend>
    <backend>@[backend_v2/models/dtos/atom_evaluation.py]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_reducer.py]</backend>
    <backend>@[backend_v2/settings.py]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_blueprint.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_causal_tda_fusion_unit.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>Raw `if type(content) is dict:` inspection loop in lines 584-592 of @[backend_v2/services/blueprint.py#L127-L698] eradicated and replaced with strict `StepOutputDTO` and `TypeAdapter(CausalTdaFusionResultDTO | CausalGraphPayloadDTO)` projection.</item>
    <item>Dead-code PostgreSQL 19 3-way Toulmin SQL join `CteReasoningStrategy.find_falsified_claims` (@[backend_v2/database/postgres/graph_adapter.py#L347-L431]) returning `list[FalsifiedClaimMatch]` (@[backend_v2/models/domain/proposition_graph.py#L343-L391]) wired into @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465] and @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py#L211-L363].</item>
    <item>`DistilledEvaluation` (@[backend_v2/models/domain/synthesis.py#L131-L155]) enriched with `depends_on_tda_ids: list[str]`, `short_circuit_reason_tda_ids: list[str]`, `is_inverse_evidence: bool`, and `topological_out_degree: int` under `ConfigDict(strict=True, extra="forbid", frozen=True)`.</item>
    <item>`ReducedAtomDTO` (@[backend_v2/models/dtos/atom_evaluation.py#L43-L67]) enriched with `depends_on_tda_ids: list[str]`, `short_circuit_reason_tda_ids: list[str]`, and `is_inverse_evidence: bool`, and populated in `MatrixReducer.reduce_matrix` (@[backend_v2/services/orchestrator/matrix_reducer.py#L121-L239]).</item>
    <item>`CausalRootCauseDiagnosisDTO` and `CausalTdaFusionResultDTO` (@[backend_v2/models/dtos/causal_discovery.py] and @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465]) enriched with `root_cause_claim: str`, `failing_node_claim: str`, `warrant_relation: Literal["supports", "rebuts", "warrants"]`, and `falsified_claims: list[FalsifiedClaimMatch]`.</item>
    <item>`max_synthesis_reasoning_length` in @[backend_v2/settings.py] (line 296) raised from `300` to `1500` characters so `step_3_evaluate_anti_patterns` and `step_4_final_conclusion` from `ReasoningStepDTO` (@[backend_v2/models/dtos/atom_evaluation.py#L21-L40]) survive compression intact.</item>
    <item>`SynthesisPayloadCompressor._clean_and_distill_payload` (@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L182-L393]) updated to bypass empty-quote dropout when `status in (ExecutionStatus.FAILED, ExecutionStatus.N_A)` or `is_inverse_evidence` is `True`, compute `topological_out_degree`, and preserve `depends_on_tda_ids`, `short_circuit_reason_tda_ids`, and `is_inverse_evidence`.</item>
    <item>Degenerate deficit sort key at @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L135-L140] inside `_prune_and_stratify_evaluations` (@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L105-L179]) replaced for `deficits` by `(-int(item.is_inverse_evidence), -item.topological_out_degree, len(item.short_circuit_reason_tda_ids), atom_id)`.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT create a separate compressor service or secondary distillation pass outside @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L105-L179] and @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L182-L393].</anti_target>
    <anti_target>Do NOT build a new graph database engine or recursive Python graph walker; use the existing PostgreSQL 19 3-way SQL join (`CteReasoningStrategy.find_falsified_claims` in @[backend_v2/database/postgres/graph_adapter.py#L347-L431]) and existing node index in @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465].</anti_target>
    <anti_target>Do NOT modify Flutter `.dart` files or Jinja2 PDF templates in Phase 1; UI and SDUI rendering parity is isolated strictly to Phase 3.</anti_target>
  </anti_targets>

  <demolish>
    <item target="@[backend_v2/services/blueprint.py#L127-L698]">Eradicate the inline `if type(content) is dict:` trace inspection loop at lines 584-592.</item>
    <item target="@[backend_v2/settings.py] &amp; @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L182-L393]">Eradicate the `300`-character Micro-CoT tail guillotine (`max_synthesis_reasoning_length = 300`) and empty-quote dropout on `ExecutionStatus.FAILED` and `ExecutionStatus.N_A` evaluations at lines 265-270 and 336-342.</item>
    <item target="@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L135-L140]">Eradicate the degenerate quote-length sort key `(-quotes_count, atom_id)` on `deficits`.</item>
  </demolish>

  <step id="1.1" name="Scoped Boy Scout Technical Debt Cleanups &amp; Toulmin Falsification Wiring">
    <action>In @[backend_v2/services/blueprint.py#L127-L698], remove the raw `if type(content) is dict:` inspection loop at lines 584-592 and replace it with strict `StepOutputDTO` and `TypeAdapter(CausalTdaFusionResultDTO | CausalGraphPayloadDTO)` projection.</action>
    <action>In @[backend_v2/database/postgres/graph_adapter.py#L347-L431], @[backend_v2/models/domain/proposition_graph.py#L343-L391], @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L38-L87], @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465], and @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py#L211-L363], wire the dead-code PostgreSQL 19 3-way Toulmin SQL join `CteReasoningStrategy.find_falsified_claims` returning `list[FalsifiedClaimMatch]` into the causal TDA fusion stage so `CausalTdaFusionResultDTO` carries `falsified_claims: list[FalsifiedClaimMatch]`.</action>
    <action>In @[backend_v2/tests/unit/services/test_blueprint.py], add unit tests verifying typed `CausalTdaFusionResultDTO` envelope projection without raw dictionary type checks.</action>
    <constraint invariant="polymorphic_dag_payload_handling">Downstream payload consumers MUST validate heterogeneous DAG state via strict Pydantic V2 Discriminated Unions or TypeAdapters with ZERO `if type(content) is dict:` checks.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py backend_v2/services/orchestrator/dag_executor/step_execution_stage.py --test --ast-strict</audit_command>
  </step>

  <step id="1.2" name="DTO &amp; Schema Enrichment (Full-Duplex Serialization Parity)">
    <action>In @[backend_v2/models/domain/synthesis.py#L131-L155], enrich `DistilledEvaluation` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with `depends_on_tda_ids: list[str]`, `short_circuit_reason_tda_ids: list[str]`, `is_inverse_evidence: bool`, and `topological_out_degree: int` using PEP 593 `Annotated` field definitions.</action>
    <action>In @[backend_v2/models/dtos/atom_evaluation.py#L21-L40] and @[backend_v2/models/dtos/atom_evaluation.py#L43-L67], verify `ReasoningStepDTO` 4-step Micro-CoT preservation and enrich `ReducedAtomDTO` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with `depends_on_tda_ids: list[str]`, `short_circuit_reason_tda_ids: list[str]`, and `is_inverse_evidence: bool`.</action>
    <action>In @[backend_v2/services/orchestrator/matrix_reducer.py#L121-L239], populate `depends_on_tda_ids`, `short_circuit_reason_tda_ids`, and `is_inverse_evidence` on each `ReducedAtomDTO` constructed in `MatrixReducer.reduce_matrix` from upstream `AtomResultDTO` (@[backend_v2/models/dtos/atom_result.py#L82-L172] and @[backend_v2/services/orchestrator/topological_evaluator.py#L56-L175]).</action>
    <action>In @[backend_v2/models/dtos/causal_discovery.py] and @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465], enrich `CausalRootCauseDiagnosisDTO` and `CausalTdaFusionResultDTO` with resolved `root_cause_claim: str`, `failing_node_claim: str`, `warrant_relation: Literal["supports", "rebuts", "warrants"]`, and `falsified_claims: list[FalsifiedClaimMatch]`.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_causal_tda_fusion_unit.py] and @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py], add positive and negative unit tests verifying `root_cause_claim`, `failing_node_claim`, `warrant_relation`, and `falsified_claims` hydration and full-duplex serialization parity.</action>
    <constraint invariant="full_duplex_serialization_parity_mandate">Synchronous hydration and `model_validate()` / `model_dump(exclude_none=True)` parity MUST hold across all writers and readers of `DistilledEvaluation`, `ReducedAtomDTO`, and `CausalTdaFusionResultDTO`.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/models/domain/synthesis.py backend_v2/models/dtos/atom_evaluation.py backend_v2/models/dtos/causal_discovery.py backend_v2/services/orchestrator/matrix_reducer.py --test --ast-strict</audit_command>
  </step>

  <step id="1.3" name="Asymmetric Epistemic Distillation, Micro-CoT Tail Preservation &amp; Topological Deficit Stratification">
    <action>In @[backend_v2/settings.py] (line 296), raise `max_synthesis_reasoning_length` from `300` to `1500` characters so `step_3_evaluate_anti_patterns` and `step_4_final_conclusion` from `ReasoningStepDTO` (@[backend_v2/models/dtos/atom_evaluation.py#L21-L40]) survive intact within the `300,000`-character budget enforced in @[backend_v2/services/orchestrator/synthesis_distiller.py#L43-L115].</action>
    <action>In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L182-L393] (specifically lines 239-352, 265-270, 298-333, and 336-342), update `_clean_and_distill_payload` to bypass the empty-quote dropout check when `status in (ExecutionStatus.FAILED, ExecutionStatus.N_A)` or `is_inverse_evidence` is `True` (since `validate_cognitive_vs_system_state` at @[backend_v2/models/dtos/atom_result.py#L139-L172] forces `source_quotes = None` for `FAILED` and `N_A` atoms), compute `topological_out_degree` (count of downstream atoms listing `atom_id` in `depends_on_tda_ids` or `short_circuit_reason_tda_ids`), and preserve `depends_on_tda_ids`, `short_circuit_reason_tda_ids`, and `is_inverse_evidence`.</action>
    <action>In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L105-L179] (specifically `sort_key` at @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L135-L140]), replace the degenerate deficit sort key in `_prune_and_stratify_evaluations` so `deficits` sort deterministically by `(-int(item.is_inverse_evidence), -item.topological_out_degree, len(item.short_circuit_reason_tda_ids), atom_id)` while `strengths` continue sorting by `(-len(item.exact_quotes), atom_id)`.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py], implement ISTQB Boundary Value Analysis and Equivalence Partitioning unit tests verifying 1500-char Micro-CoT tail retention (`step_3` and `step_4`), zero-loss retention of quote-less `FAILED` and `N_A` evaluations, and topological priority sorting of deficits.</action>
    <constraint invariant="anti_happy_path_mandate">Include at least 2 negative or boundary test cases for every positive test case in `test_synthesis_payload_compressor.py`.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/settings.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_clean_and_distill_payload_retains_failed_and_na_without_quotes" category="positive">
      <input>EvaluatedAtomDTO instances with status=ExecutionStatus.FAILED and ExecutionStatus.N_A, exact_quotes=[], short_circuit_reason_tda_ids=["tda_parent"], and 900-char 4-step Micro-CoT evaluation_reasoning</input>
      <expected>DistilledEvaluation instances retained with full 900-char semantic_reasoning (preserving step_3_evaluate_anti_patterns and step_4_final_conclusion), short_circuit_reason_tda_ids=["tda_parent"], and topological_out_degree computed accurately</expected>
    </test>
    <test name="test_clean_and_distill_payload_reasoning_length_boundary_1500_chars" category="boundary">
      <input>EvaluatedAtomDTO instances with evaluation_reasoning lengths at 1499, 1500, and 1501 characters</input>
      <expected>1499 and 1500 character strings preserved without truncation; 1501 character string sliced deterministically at 1500 characters</expected>
    </test>
    <test name="test_clean_and_distill_payload_drops_passed_atom_with_empty_quotes_and_no_reasoning" category="negative">
      <input>EvaluatedAtomDTO with status=ExecutionStatus.PASSED, exact_quotes=[], evaluation_reasoning=None, is_inverse_evidence=False</input>
      <expected>Evaluation is excluded from distilled output list</expected>
    </test>
    <test name="test_prune_and_stratify_evaluations_prioritizes_inverse_evidence_and_out_degree" category="positive">
      <input>Deficit list containing alphabetical atom "a0" (out_degree=0, is_inverse_evidence=False), root blocker "z9" (out_degree=4, is_inverse_evidence=False), and poison hit "m5" (out_degree=1, is_inverse_evidence=True) under tight deficit_budget</input>
      <expected>Sorted deficit order places "m5" first (is_inverse_evidence=True), "z9" second (topological_out_degree=4), and "a0" last</expected>
    </test>
    <test name="test_distilled_evaluation_extra_field_raises_validation_error" category="error_path">
      <input>DistilledEvaluation.model_validate with unpermitted extra key</input>
      <expected>Raises pydantic.ValidationError (extra="forbid")</expected>
    </test>
    <test name="test_causal_tda_fusion_resolves_claim_texts_and_falsified_claims" category="positive">
      <input>PropositionGraph with root parent node, failing child node, WarrantEdge(relation_type="warrants"), and FalsifiedClaimMatch from CteReasoningStrategy.find_falsified_claims</input>
      <expected>CausalTdaFusionResultDTO contains non-empty root_cause_claim, failing_node_claim, warrant_relation="warrants", and populated falsified_claims list</expected>
    </test>
    <test name="test_causal_root_cause_diagnosis_invalid_warrant_relation_raises_validation_error" category="negative">
      <input>CausalRootCauseDiagnosisDTO instantiated with warrant_relation="invalid_relation"</input>
      <expected>Raises pydantic.ValidationError</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run localized unit tests: `uv run pytest backend_v2/tests/unit/services/test_blueprint.py backend_v2/tests/unit/services/orchestrator/dag_executor/test_causal_tda_fusion_unit.py backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py`.</action>
    <action>Run Phase 1 backend quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/synthesis.py backend_v2/models/dtos/atom_evaluation.py backend_v2/models/dtos/causal_discovery.py backend_v2/services/blueprint.py backend_v2/services/orchestrator/matrix_reducer.py backend_v2/services/orchestrator/synthesis_payload_compressor.py backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py backend_v2/services/orchestrator/dag_executor/step_execution_stage.py backend_v2/settings.py --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```

