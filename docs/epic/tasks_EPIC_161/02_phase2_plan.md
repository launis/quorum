<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

# Phase 2: Orchestration, Contrastive Deficit Injection & Synthesis Convergence

**Overview:** Create [NEW] `MatrixFailureDeficitDTO` and [NEW] `CausalSynthesisBriefDTO` defined in `@[backend_v2/models/dtos/synthesis.py]` (`ConfigDict(strict=True, extra="forbid", frozen=True)`). Upgrade `MatrixExplanationService.assemble_matrices_to_explain` (`@[backend_v2/services/orchestrator/matrix_explanation_service.py#L56-L311]`) and `LightweightMatrixOutput` (`@[backend_v2/models/dtos/lightweight_matrix.py#L27-L42]` and `@[backend_v2/models/dtos/lightweight_matrix.py#L125-L177]`) to preserve full verbatim quotes without slicing when `max_synthesis_quote_length <= 0`, pass `max_items=effective_max_quotes if effective_max_quotes > 0 else len(quote_candidates)` into `ranked_round_robin_select` (`@[backend_v2/utils/ranked_round_robin.py#L13-L80]`), retain all `unmet_deficits` when `effective_max_unmet <= 0`, and capture full `evaluation_reasoning`, `is_inverse_evidence`, transitive parent-to-child `ExecutionStatus.N_A` short-circuit lineage (`short_circuited_by_claims` resolved from `@[backend_v2/services/orchestrator/topological_evaluator.py#L56-L175]`), `tda.anti_patterns` (`@[backend_v2/models/domain/matrix.py#L66-L77]`), and `ContrastivePairDTO` anchors (`@[backend_v2/models/domain/matrix.py#L94-L129]`) across all `FAILED` and `N_A` deficits within the `300,000`-character Fail-Fast ceiling (`@[backend_v2/services/orchestrator/synthesis_distiller.py#L43-L115]`). Converge Phase 1 in-DAG `SynthesisEngine` (`@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L58-L301]`) by injecting `matrix_reducer_output.reduced_atoms` (`@[backend_v2/services/orchestrator/matrix_reducer.py#L121-L239]` and `@[backend_v2/models/dtos/atom_evaluation.py#L43-L67]`) alongside `global_atom_blackboard` (`@[backend_v2/models/domain/blackboard.py#L133-L184]` populated in `@[backend_v2/services/orchestrator/rag_preflight_service.py#L134-L305]`), fan out `CausalSynthesisBriefDTO` across all four parallel synthesis tasks in `@[backend_v2/workers/synthesis_worker.py#L92-L664]`, `@[backend_v2/workers/synthesis_tasks.py#L61-L137]`, `@[backend_v2/workers/synthesis_tasks.py#L140-L241]`, `@[backend_v2/workers/synthesis_tasks.py#L244-L333]`, and `@[backend_v2/workers/synthesis_tasks.py#L336-L427]`, unify `create_row_explanations_task` onto the shared `CognitiveTier.BALANCED` `client: LLMClient` instance, and remove the conflicting `<global_length_constraint_chars>` + `<section_budget>` double-injection in `@[backend_v2/workers/synthesis_worker.py#L92-L664]` (lines `311–314`) so each task obeys only its own `<section_budget>` (unbounded if `0` or `None`).

**Source:** @[docs/epic/EPIC_161_topological_synthesis_cohesion.md#L187-L196] Phase 2: Orchestration, Contrastive Deficit Injection & Synthesis Convergence

**Target Files:**
- `[MODIFY] @[backend_v2/models/dtos/synthesis.py]`
- `[MODIFY] @[backend_v2/models/dtos/lightweight_matrix.py#L27-L42]`
- `[MODIFY] @[backend_v2/models/dtos/lightweight_matrix.py#L125-L177]`
- `[MODIFY] @[backend_v2/services/orchestrator/matrix_explanation_service.py#L56-L311]`
- `[MODIFY] @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L58-L301]`
- `[MODIFY] @[backend_v2/workers/synthesis_worker.py#L92-L664]`
- `[MODIFY] @[backend_v2/workers/synthesis_tasks.py#L61-L137]`
- `[MODIFY] @[backend_v2/workers/synthesis_tasks.py#L140-L241]`
- `[MODIFY] @[backend_v2/workers/synthesis_tasks.py#L244-L333]`
- `[MODIFY] @[backend_v2/workers/synthesis_tasks.py#L336-L427]`
- `[MODIFY] @[backend_v2/models/prompts/synthesis/synthesis_directives.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_synthesis_worker.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/models/dtos/lightweight_matrix.py#L27-L42]`**<br>**`@[backend_v2/models/dtos/lightweight_matrix.py#L125-L177]`**<br>**`@[backend_v2/models/dtos/synthesis.py]`**<br>**`@[backend_v2/utils/ranked_round_robin.py#L13-L80]`**<br>**`@[backend_v2/services/orchestrator/matrix_explanation_service.py#L56-L311]`** | Eradicate compressing `ExecutionStatus.FAILED` atoms into bare localized claim titles (lines `198–296` and `243–252`) while discarding `evaluation_reasoning`, `ContrastivePairDTO` (`@[backend_v2/models/domain/matrix.py#L94-L129]`), `anti_patterns` (`@[backend_v2/models/domain/matrix.py#L66-L77]`), `is_inverse_evidence`, and `ExecutionStatus.N_A` (`short_circuit_reason_tda_ids` from `@[backend_v2/services/orchestrator/topological_evaluator.py#L56-L175]`, lines `156–162`). Eradicate hardcoded `15`-char minimum quote length (line `132`), `300`-char quote slicing (lines `86`, `133`), and `5`-item caps (lines `257–270`) when `OutputProfile` overrides are `None`. | Create [NEW] `MatrixFailureDeficitDTO` (`ConfigDict(extra="forbid", strict=True, frozen=True)`) defined in `@[backend_v2/models/dtos/synthesis.py]` containing `claim: str`, `status: Literal["FAILED", "N_A"]`, `scale_score: int`, `evaluation_reasoning: str \| None`, `is_inverse_evidence: bool`, `short_circuited_by_claims: list[str]` (transitively formatted with upstream blocker parent claim + parent `evaluation_reasoning`), `anti_patterns: list[str]`, `contrastive_rejected: str \| None`, and `contrastive_acceptable: str \| None` across all `FAILED` and `N_A` deficits on `MatrixExplanationContextDTO`. Read `min_synthesis_quote_length` from `Settings` and pass `len(quote_candidates)` to `ranked_round_robin_select` when `effective_max_quotes <= 0`. | Do NOT filter out contrastive pairs or anti-patterns by scale level or impose artificial per-row deficit caps when `OutputProfile` limits are unset (`None`). | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/matrix_explanation_service.py --test --ast-strict` + unit tests verifying full unbounded deficit/quote retention, contrastive pair injection, and transitive parent-to-child `N_A` blocker reasoning hydration. |
| **`@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L58-L301]`**<br>**`@[backend_v2/services/orchestrator/matrix_reducer.py#L121-L239]`**<br>**`@[backend_v2/models/dtos/atom_evaluation.py#L43-L67]`** | Eradicate the Phase 1 `SynthesisEngine` bug where `matrix_reducer_output.reduced_atoms` is computed (lines `101–188`) but never injected into `user_message_parts` (lines `170–188` of `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L58-L301]`), and eradicate stripping `depends_on_tda_ids`, `short_circuit_reason_tda_ids`, and `is_inverse_evidence` from `ReducedAtomDTO`. | Inject `matrix_reducer_output.reduced_atoms` (aliased via `AliasEngine` from `@[backend_v2/utils/alias_engine.py]`) into `SynthesisEngine.execute()` alongside `raw_extensions` and `global_atom_blackboard` (`@[backend_v2/models/domain/blackboard.py#L133-L184]`). | Do NOT maintain divergent epistemic contracts between Phase 1 in-DAG `SynthesisEngine` and Phase 2 `SynthesisWorker`. Both must consume reduced evaluations and short-circuit lineage. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/synthesis_engine.py --test --ast-strict` + unit test asserting `reduced_atoms` reasoning, quotes, and short-circuit lineage appear in the compiled prompt payload. |
| **`@[backend_v2/workers/synthesis_worker.py#L92-L664]`**<br>**`@[backend_v2/workers/synthesis_tasks.py#L61-L137]`**<br>**`@[backend_v2/workers/synthesis_tasks.py#L140-L241]`**<br>**`@[backend_v2/workers/synthesis_tasks.py#L244-L333]`**<br>**`@[backend_v2/workers/synthesis_tasks.py#L336-L427]`**<br>**`@[backend_v2/models/prompts/synthesis/synthesis_directives.py]`** | Eradicate passing `causal_diagnosis_text` only to `create_executive_summary_task` (lines `394–468` and `436` of `@[backend_v2/workers/synthesis_worker.py#L92-L664]`) while starving `create_matrix_sections_tasks`, `create_xai_highlights_task`, and `create_row_explanations_task` (lines `406–413` of `synthesis_tasks.py`) of causal and Toulmin falsification context. Eradicate the conflicting `<global_length_constraint_chars>` + `<section_budget>` double-injection in `synthesis_worker.py` (lines `311–314`) and the downgraded `CognitiveTier.FAST` client instantiation in `create_row_explanations_task` (lines `370–375`). | Create [NEW] `CausalSynthesisBriefDTO` defined in `@[backend_v2/models/dtos/synthesis.py]` (combining resolved `CausalRootCauseDiagnosisDTO` chains, `FalsifiedClaimMatch` Toulmin rebuttals, and post-hoc fidelity penalties) and inject it in `synthesis_worker.py` into all four synthesis task constructors (`create_executive_summary_task`, `create_matrix_sections_tasks`, `create_xai_highlights_task`, `create_row_explanations_task`) governed by static XML mandates in `synthesis_directives.py`. Pass the shared `CognitiveTier.BALANCED` `client: LLMClient` instance into `create_row_explanations_task`, and remove `<global_length_constraint_chars>` from `base_dynamic_parts` so each task obeys only its own `<section_budget>` (unbounded when `0` or `None`). | Do NOT add extra sequential LLM calls or post-processing LLM rewrite passes in `synthesis_worker.py`; preserve the single-wave `asyncio.TaskGroup` fan-out architecture. | `uv run python scripts/backend_audit_loop.py backend_v2/workers/ --test --ast-strict` + unit tests verifying all 4 synthesis tasks receive the resolved `CausalSynthesisBriefDTO`, share the `CognitiveTier.BALANCED` client, and obey only their own `<section_budget>`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 1 completion in @[backend_v2/models/domain/synthesis.py#L131-L155], @[backend_v2/models/dtos/atom_evaluation.py#L43-L67], @[backend_v2/services/orchestrator/matrix_reducer.py#L121-L239], and @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465].</action>
    <action>Look forward: Read @[backend_v2/models/dtos/synthesis.py], @[backend_v2/models/dtos/lightweight_matrix.py#L27-L42], @[backend_v2/models/dtos/lightweight_matrix.py#L125-L177], @[backend_v2/utils/ranked_round_robin.py#L13-L80], @[backend_v2/services/orchestrator/matrix_explanation_service.py#L56-L311], @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L58-L301], @[backend_v2/workers/synthesis_worker.py#L92-L664], and @[backend_v2/workers/synthesis_tasks.py#L61-L137] through @[backend_v2/workers/synthesis_tasks.py#L336-L427].</action>
    <constraint invariant="four_layer_clean_stack_hierarchy">Keep static XML mandates in @[backend_v2/models/prompts/synthesis/synthesis_directives.py] (Layer 1) 100% static for prompt caching; inject dynamic `CausalSynthesisBriefDTO` and `MatrixFailureDeficitDTO` payloads exclusively at the tail user message (Layer 4).</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_161_topological_synthesis_cohesion.md] and @[docs/epic/EPIC_161_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_161/02_phase2_plan.md] @[docs/epic/EPIC_161_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/models/dtos/synthesis.py]</backend>
    <backend>@[backend_v2/models/dtos/lightweight_matrix.py]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_explanation_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/synthesis_engine.py]</backend>
    <backend>@[backend_v2/workers/synthesis_worker.py]</backend>
    <backend>@[backend_v2/workers/synthesis_tasks.py]</backend>
    <backend>@[backend_v2/models/prompts/synthesis/synthesis_directives.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_synthesis_worker.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>[NEW] `MatrixFailureDeficitDTO` and [NEW] `CausalSynthesisBriefDTO` defined in @[backend_v2/models/dtos/synthesis.py] with `ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` fields.</item>
    <item>`MatrixExplanationService.assemble_matrices_to_explain` (@[backend_v2/services/orchestrator/matrix_explanation_service.py#L56-L311]) and `@[backend_v2/models/dtos/lightweight_matrix.py#L27-L42]` / `@[backend_v2/models/dtos/lightweight_matrix.py#L125-L177]` populate `MatrixFailureDeficitDTO` with full `evaluation_reasoning`, `is_inverse_evidence`, transitive `short_circuited_by_claims` (upstream parent claim + parent `evaluation_reasoning`), `anti_patterns` (@[backend_v2/models/domain/matrix.py#L66-L77]), and `ContrastivePairDTO` (@[backend_v2/models/domain/matrix.py#L94-L129]) anchors across all `FAILED` and `N_A` deficits, pass `len(quote_candidates)` into `ranked_round_robin_select` (@[backend_v2/utils/ranked_round_robin.py#L13-L80]) when `effective_max_quotes <= 0`, and slice quotes/deficits only when explicit positive bounds (`> 0`) are configured.</item>
    <item>Phase 1 in-DAG `SynthesisEngine.execute` (@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L58-L301]) serializes `matrix_reducer_output.reduced_atoms` (from @[backend_v2/services/orchestrator/matrix_reducer.py#L121-L239] and @[backend_v2/models/dtos/atom_evaluation.py#L43-L67], aliased via @[backend_v2/utils/alias_engine.py]) into `user_message_parts` alongside `raw_extensions` and `global_atom_blackboard` (@[backend_v2/models/domain/blackboard.py#L133-L184]).</item>
    <item>`synthesis_worker.py` (@[backend_v2/workers/synthesis_worker.py#L92-L664]) constructs `CausalSynthesisBriefDTO` (combining human-readable claim fault chains from @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465] and `FalsifiedClaimMatch` Toulmin rebuttals from @[backend_v2/database/postgres/graph_adapter.py#L347-L431] and @[backend_v2/models/domain/proposition_graph.py#L343-L391]), injects it into `create_executive_summary_task` (@[backend_v2/workers/synthesis_tasks.py#L61-L137]), `create_matrix_sections_tasks` (@[backend_v2/workers/synthesis_tasks.py#L140-L241]), `create_xai_highlights_task` (@[backend_v2/workers/synthesis_tasks.py#L244-L333]), and `create_row_explanations_task` (@[backend_v2/workers/synthesis_tasks.py#L336-L427]), passes the shared `CognitiveTier.BALANCED` `client: LLMClient` instance into `create_row_explanations_task`, and removes `<global_length_constraint_chars>` from `base_dynamic_parts` so each task obeys exclusively its own `<section_budget>` (unbounded if `0` or `None`).</item>
    <item>Static XML reasoning mandates `<causal_tda_diagnosis_mandate>` and `<contrastive_frontier_mandate>` defined in @[backend_v2/models/prompts/synthesis/synthesis_directives.py].</item>
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
    <anti_target>Do NOT filter out `ContrastivePairDTO` or `anti_patterns` by scale level or enforce artificial per-row deficit caps when `OutputProfile` limits are unset (`None`).</anti_target>
    <anti_target>Do NOT pass raw Opaque Stripe IDs (`tda_...`, `blk_...`, `stp_...`) into LLM prompts; always resolve to localized claim titles or translate via @[backend_v2/utils/alias_engine.py].</anti_target>
    <anti_target>Do NOT add extra sequential LLM calls outside the single-wave `asyncio.TaskGroup` in @[backend_v2/workers/synthesis_worker.py#L92-L664].</anti_target>
  </anti_targets>

  <demolish>
    <item target="@[backend_v2/services/orchestrator/matrix_explanation_service.py#L56-L311]">Eradicate the bare claim-title-only `ExecutionStatus.FAILED` branch, ignored `ExecutionStatus.N_A` branch, hardcoded `if len(cleaned) >= 15:` minimum quote filter at line 132, unconditional `cleaned[:max_quote_len]` slicing at lines 86 and 133, and unconditional `[:effective_max_unmet]` slicing at lines 243-270 of `assemble_matrices_to_explain`.</item>
    <item target="@[backend_v2/workers/synthesis_worker.py#L92-L664] &amp; @[backend_v2/workers/synthesis_tasks.py#L336-L427]">Eradicate the task-isolated opaque node ID string formatting for `causal_diagnosis_text` at lines 394-433, the conflicting `<global_length_constraint_chars>` injection in `base_dynamic_parts` at lines 311-314, and the downgraded `CognitiveTier.FAST` client instantiation inside `create_row_explanations_task` at lines 370-375.</item>
  </demolish>

  <step id="2.1" name="Full Contrastive Deficit Injection, Unbounded Quote/Deficit Retention &amp; Transitive N_A Parent Hydration (MatrixExplanationService)">
    <action>In @[backend_v2/models/dtos/synthesis.py], create [NEW] `MatrixFailureDeficitDTO` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with fields `claim: str`, `status: Literal["FAILED", "N_A"]`, `scale_score: int`, `evaluation_reasoning: str | None`, `is_inverse_evidence: bool`, `short_circuited_by_claims: list[str]`, `anti_patterns: list[str]`, `contrastive_rejected: str | None`, and `contrastive_acceptable: str | None`, and wire it into `MatrixExplanationContextDTO` alongside @[backend_v2/models/dtos/lightweight_matrix.py#L27-L42] and @[backend_v2/models/dtos/lightweight_matrix.py#L125-L177].</action>
    <action>In @[backend_v2/services/orchestrator/matrix_explanation_service.py#L56-L311] (specifically lines 86, 132, 133, 198-296, 216-242, and 243-270), upgrade `MatrixExplanationService.assemble_matrices_to_explain` to resolve `min_synthesis_quote_length` from `Settings` (replacing hardcoded `15` at line 132), slice quotes only when `max_quote_len > 0`, pass `max_items=effective_max_quotes if effective_max_quotes > 0 else len(quote_candidates)` into `ranked_round_robin_select` (@[backend_v2/utils/ranked_round_robin.py#L13-L80]), slice `unmet_deficits` only when `effective_max_unmet > 0`, capture full `evaluation_reasoning` and `is_inverse_evidence` from `AtomResultDTO` / `ReducedAtomDTO`, transitively resolve `ExecutionStatus.N_A` (`short_circuit_reason_tda_ids` from @[backend_v2/services/orchestrator/topological_evaluator.py#L56-L175], lines 156-162) into localized upstream blocker claim names paired with the upstream blocker parent's `evaluation_reasoning` (`[Blocked Claim] <-- SHORT-CIRCUITED BY PREREQUISITE FAILURE: [Parent Claim: <parent evaluation_reasoning>]`), and attach `tda.contrastive_example` (`ContrastivePairDTO` from @[backend_v2/models/domain/matrix.py#L94-L129]) and `tda.anti_patterns` (@[backend_v2/models/domain/matrix.py#L66-L77]) across all `FAILED` and `N_A` deficits within the `300,000`-character Fail-Fast ceiling in @[backend_v2/services/orchestrator/synthesis_distiller.py#L43-L115].</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py], update legacy 5-item/300-char test assertions (`anti_tdd_trap`) and add positive, boundary, and negative unit tests verifying full unbounded deficit/quote retention by default (`0`), explicit `OutputProfile` cap enforcement when `> 0`, full contrastive pair and anti-pattern injection across all failed/short-circuited scales, and transitive parent-to-child `N_A` blocker reasoning hydration.</action>
    <constraint invariant="mathematical_extrema_anchoring">Derive scale boundaries dynamically from the matrix block scales collection; never hardcode scale integers.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/synthesis.py backend_v2/models/dtos/lightweight_matrix.py backend_v2/services/orchestrator/matrix_explanation_service.py --test --ast-strict</audit_command>
  </step>

  <step id="2.2" name="Phase 1 In-DAG SynthesisEngine Convergence">
    <action>In @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L58-L301] (specifically lines 78-215, 101-188, and 170-188), serialize `matrix_reducer_output.reduced_atoms` (from @[backend_v2/services/orchestrator/matrix_reducer.py#L121-L239] and @[backend_v2/models/dtos/atom_evaluation.py#L43-L67]) with `AliasEngine` aliases (@[backend_v2/utils/alias_engine.py]) into `user_message_parts` alongside `raw_extensions` and `global_atom_blackboard` (@[backend_v2/models/domain/blackboard.py#L133-L184] populated in @[backend_v2/services/orchestrator/rag_preflight_service.py#L134-L305], lines 276-305).</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py], add unit tests verifying `reduced_atoms` reasoning, quotes, inverse evidence flags, and short-circuit lineage are serialized into the compiled user message with deterministic `AliasEngine` aliases and zero raw Opaque Stripe IDs.</action>
    <constraint invariant="alias_engine_llm_isolation_mandate">Never pass raw `tda_...` UUIDs into the compiled prompt; translate all atom identifiers via `AliasEngine`.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/synthesis_engine.py --test --ast-strict</audit_command>
  </step>

  <step id="2.3" name="Phase 2 Unified CausalSynthesisBriefDTO Fan-Out, CognitiveTier.BALANCED Client Parity &amp; Single Section-Budget Sovereignty">
    <action>In @[backend_v2/models/dtos/synthesis.py], create [NEW] `CausalSynthesisBriefDTO` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) encapsulating resolved root-cause fault chains (`root_cause_claim -> failing_node_claim` from @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py#L392-L465]), `FalsifiedClaimMatch` Toulmin rebuttals (`rebuttal_claim -> invalidated_warrant -> falsified_claim` from @[backend_v2/database/postgres/graph_adapter.py#L347-L431] and @[backend_v2/models/domain/proposition_graph.py#L343-L391]), and post-hoc fidelity penalties, with a deterministic markdown/XML serializer for prompt tail injection.</action>
    <action>In @[backend_v2/models/prompts/synthesis/synthesis_directives.py], add static XML mandates `<causal_tda_diagnosis_mandate>` and `<contrastive_frontier_mandate>` instructing the LLM to ground executive summaries, matrix section narratives, XAI highlights, and row explanations in the resolved causal chains, Toulmin rebuttals, and contrastive deficits.</action>
    <action>In @[backend_v2/workers/synthesis_worker.py#L92-L664] (lines 311-314, 328-333, 394-473, and 436) and @[backend_v2/workers/synthesis_tasks.py#L61-L137], @[backend_v2/workers/synthesis_tasks.py#L140-L241], @[backend_v2/workers/synthesis_tasks.py#L244-L333], and @[backend_v2/workers/synthesis_tasks.py#L336-L427] (lines 336-413), remove `<global_length_constraint_chars>` from `base_dynamic_parts` so each task obeys exclusively its own `<section_budget>` tag (injected only when `> 0`; unbounded when `0` or `None`), pass the shared `CognitiveTier.BALANCED` `client: LLMClient` instance into `create_row_explanations_task`, and pass the formatted `CausalSynthesisBriefDTO` into all four parallel task constructors (`create_executive_summary_task`, `create_matrix_sections_tasks`, `create_xai_highlights_task`, and `create_row_explanations_task`).</action>
    <action>In @[backend_v2/tests/unit/workers/test_synthesis_worker.py], add unit tests asserting all four synthesis tasks receive the resolved `CausalSynthesisBriefDTO` containing human-readable claim texts and `FalsifiedClaimMatch` Toulmin rebuttals, share the `CognitiveTier.BALANCED` client instance, and receive only their own `<section_budget>` tag without `<global_length_constraint_chars>` double-injection.</action>
    <constraint invariant="ephemeral_caching_topology">Keep `_SYSTEM_INSTRUCTION` in `synthesis_directives.py` 100% static; inject `CausalSynthesisBriefDTO` exclusively into the tail `user` message of each task.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/models/prompts/synthesis/synthesis_directives.py backend_v2/workers/synthesis_worker.py backend_v2/workers/synthesis_tasks.py --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_assemble_matrices_to_explain_retains_all_deficits_and_contrastive_pairs_across_all_scales" category="positive">
      <input>Matrix row with achieved_score=2 and 6 failed atoms across scales 2, 3, and 4, plus 8 passed quotes of 600 chars under default unbounded settings (0)</input>
      <expected>MatrixExplanationContextDTO retains all 6 unmet_deficits with full evaluation_reasoning, anti_patterns, contrastive_rejected, and contrastive_acceptable across scales 2, 3, and 4, and retains all 8 quotes at full 600-char length</expected>
    </test>
    <test name="test_assemble_matrices_to_explain_transitively_hydrates_na_parent_claim_and_reasoning" category="positive">
      <input>AtomResultDTO with status=ExecutionStatus.N_A, evaluation_reasoning=None, short_circuit_reason_tda_ids=["tda_parent"], where "tda_parent" is FAILED with claim="Parent Claim" and evaluation_reasoning="Step 4: Failed due to missing metric"</input>
      <expected>MatrixFailureDeficitDTO for the N_A atom contains status="N_A" and short_circuited_by_claims formatted with both "Parent Claim" and "Step 4: Failed due to missing metric"</expected>
    </test>
    <test name="test_assemble_matrices_to_explain_max_score_row_has_zero_unmet_deficits" category="boundary">
      <input>Matrix row where achieved_score equals computed_max (5 of 5)</input>
      <expected>unmet_deficits is empty</expected>
    </test>
    <test name="test_matrix_failure_deficit_dto_invalid_status_raises_validation_error" category="negative">
      <input>MatrixFailureDeficitDTO instantiated with status="PASSED"</input>
      <expected>Raises pydantic.ValidationError</expected>
    </test>
    <test name="test_synthesis_engine_execute_injects_aliased_reduced_atoms_into_user_message" category="positive">
      <input>SynthesisEngine.execute called with MatrixReducerOutput containing PASSED, FAILED, and N_A ReducedAtomDTO entries with evaluation_reasoning and short_circuit_reason_tda_ids</input>
      <expected>Compiled user message contains aliased reduced_atoms reasoning and short-circuit lineage with zero raw tda_ UUIDs</expected>
    </test>
    <test name="test_synthesis_worker_fans_out_causal_synthesis_brief_to_all_four_tasks" category="positive">
      <input>generate_profile_synthesis_and_pdf_task with CausalTdaFusionResultDTO containing resolved root_cause_claim, failing_node_claim, and FalsifiedClaimMatch</input>
      <expected>create_executive_summary_task, create_matrix_sections_tasks, create_xai_highlights_task, and create_row_explanations_task all receive the formatted CausalSynthesisBriefDTO in their user payload</expected>
    </test>
    <test name="test_causal_synthesis_brief_dto_extra_fields_raises_validation_error" category="error_path">
      <input>CausalSynthesisBriefDTO.model_validate with unknown extra attribute</input>
      <expected>Raises pydantic.ValidationError (extra="forbid")</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run localized unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py backend_v2/tests/unit/workers/test_synthesis_worker.py`.</action>
    <action>Run Phase 2 backend quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/dtos/synthesis.py backend_v2/models/dtos/lightweight_matrix.py backend_v2/models/prompts/synthesis/synthesis_directives.py backend_v2/services/orchestrator/matrix_explanation_service.py backend_v2/services/orchestrator/engines/synthesis_engine.py backend_v2/workers/synthesis_worker.py backend_v2/workers/synthesis_tasks.py --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
