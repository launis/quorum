# Phase 5: Long-Range Causal Horizon Expansion & Global Context Anchor Header for Root Axioms (WP3)

**Overview:** Upgrade `SlidingWindowLinker` to anchor deliverable root axioms ($InDegree(v)=0$) as a persistent Global Context Anchor header block across subsequent sliding windows, eliminating the document length-dependent long-tail truncation defect while enforcing dynamic budget allocation ($W_{min}=12, K_{eff} \le 8, M_{win} \le 20$). Implement Algorithm 1 dual fault attribution separating multi-segment warrant failures into `CausalRootCauseType.WARRANT_GROUNDING_FAILURE`.

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L325-L336] Phase 5: Long-Range Causal Horizon Expansion & Global Context Anchor Header for Root Axioms (WP3)

**Target Files:**
- `[MODIFY]` @[backend_v2/settings.py#L54-L972]
- `[MODIFY]` @[backend_v2/models/dtos/dag_models.py#L30-L69]
- `[MODIFY]` @[backend_v2/models/dtos/causal_discovery.py#L59-L66]
- `[MODIFY]` @[backend_v2/services/orchestrator/sliding_window_linker.py#L49-L72]
- `[MODIFY]` @[backend_v2/services/orchestrator/sliding_window_linker.py#L120-L365]
- `[MODIFY]` @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L79-L290]
- `[MODIFY]` @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L94-L149]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py#L42-L370]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py]

## Five-Column Architectural Directives

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Settings Linker Capacity**<br>`@[backend_v2/settings.py#L54-L972]` | Hardcoding magic limits (8, 12, 20) inside linker functions; omitting boundary constraints on capacity fields. | Explicit `linker_max_global_root_axioms: Annotated[int, Field(ge=0, le=20, description="Max persistent deliverable root axioms injected into window headers")] = 8` and `linker_min_window_atoms_quota: Annotated[int, Field(ge=1, le=20, description="Minimum current window atom quota before root axiom injection")] = 12`. | Reject dynamic PID controllers or speculative adaptive throttlers; bind to deterministic static SSOT limits. | `Settings` schema validation; unit test asserting configuration limits. |
| **CausalEdge DAG Domain Model**<br>`@[backend_v2/models/dtos/dag_models.py#L30-L69]` | Passing untyped string warrants; mutating edges in-place; omitting pre-validation for multi-segment tuples. | Strongly typed `warrant_quotes: Annotated[tuple[str, ...] \| None, BeforeValidator(coerce_source_quotes_tuple), Field(default=None, description="Verbatim source quotes grounding the Toulmin inferential warrant.")] = None` under `ConfigDict(extra="forbid", strict=True, frozen=True)`. | Avoid multi-layer warrant hierarchies (backing, qualifier, rebuttal) until domain requirements necessitate them. | Pydantic `ValidationError` on malformed warrant types; unit tests verifying immutable tuple coercion. |
| **CausalEdge DTO Contract**<br>`@[backend_v2/models/dtos/causal_discovery.py#L59-L66]` | Dropping warrant quotes during DTO projection; converting tuples to raw strings via ad-hoc formatting. | Strongly typed `warrant_quotes: Annotated[tuple[str, ...] \| None, BeforeValidator(coerce_source_quotes_tuple), Field(default=None, description="Verbatim source quotes grounding the Toulmin inferential warrant.")] = None` on `CausalEdgeDTO`. | Reject parallel edge schemas; preserve unified DTO contract. | Roundtrip validation with `CausalGraphPayloadDTO`; referential integrity validator pass. |
| **Sliding Window Linker DTO**<br>`@[backend_v2/services/orchestrator/sliding_window_linker.py#L49-L72]` | Permitting unvalidated string lists for warrants; duck-typing LLM structured responses. | Typed `warrant_quotes: Annotated[tuple[str, ...] \| None, BeforeValidator(coerce_source_quotes_tuple), Field(default=None, description="Optional verbatim quotes from source text grounding the Toulmin inferential warrant.")] = None` on `LinkerEdgeDTO`. | Avoid redundant intermediate warrant wrapper DTOs. | LLM structured output parsing against `LinkerResponseDTO` with Pydantic validation. |
| **Sliding Window Linker Engine**<br>`@[backend_v2/services/orchestrator/sliding_window_linker.py#L120-L365]` | Quadratic full-pairwise attention; unbounded prompt inflation exceeding window capacity; ignoring historical root axioms; mutating atoms during linking. | Dynamic root axiom header allocation: guaranteed minimum quota $W_{min} = 12$, dynamic allocation $K_{eff} = \min(K_{max}, \max(0, M_{win} - W_{current}))$, candidate sorting by `(-OutDegree(v), atom.source_sequence_index)`, hard budget guard $M_{win} \le 20$, and Toulmin warrant transit to `CausalEdge`. | Reject recursive multi-pass tree reconcilers or external graph caches for in-flight sliding windows. | Unit tests asserting $M_{win} \le 20$ hard guard under high candidate pressure ($>20$ root axioms); deterministic alias resolution. |
| **Causal Discovery Engine**<br>`@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py#L42-L370]` | Dropping warrant quotes when projecting `CausalEdge` to `CausalEdgeDTO`; omitting deliverable input keys transit to linker. | Transit `warrant_quotes=edge.warrant_quotes` in `causal_edges` list assembly; transit deliverable input key scoping to linker. | Avoid secondary edge filtering passes or speculative graph pruning steps. | Integration verification in `test_causal_discovery_engine.py` asserting warrant quotes preservation. |
| **Causal Cohesion Evaluator**<br>`@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L79-L290]`<br>`@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L94-L149]` | Conflating inferential warrant breakdowns with independent node premise failures; loose string status comparisons; heuristic fault tagging. | Algorithm 1 dual fault attribution: separate intrinsic node flaws (`CausalRootCauseType.NODE_FAILURE`) from inferential warrant/edge failures (`CausalRootCauseType.WARRANT_GROUNDING_FAILURE`) with warrant quote details. | Avoid probabilistic belief network solvers; enforce deterministic topological graph traversal. | Unit tests in `test_causal_cohesion_scoring.py` verifying Algorithm 1 dual fault attribution. |
| **Sliding Window Linker Test Suite**<br>`@[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py]` | Tautological mocks asserting static responses; testing only happy-path single-window scenarios; omitting boundary partitions. | ISTQB boundary value analysis verifying $W_{min}=12, K_{eff} \le 8, M_{win} \le 20$, candidate sorting, and multi-segment warrant extraction. | Avoid live LLM calls during unit tests; enforce deterministic mock fixtures. | 100% test pass rate via `uv run pytest backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py`. |
| **Causal Cohesion Scoring Test Suite**<br>`@[backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py]` | Omission of multi-segment warrant failure test partitions; asserting outdated behavior. | Comprehensive unit tests verifying Algorithm 1 dual fault attribution, warrant grounding failure separation, and Cumulative Guttman Invariant preservation. | Avoid duplicate graph fixture generation; utilize shared `_create_test_graph` helper. | 100% test pass rate via `uv run pytest backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUPS">
    <action>Look backward: Verify multi-segment lexical validation and strictness decoupling are operational in @[backend_v2/services/orchestrator/anchor_validation_service.py] and @[backend_v2/models/domain/workflow.py].</action>
    <action>Look forward: Verify baseline state in @[backend_v2/services/orchestrator/sliding_window_linker.py#L120-L365] and @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L79-L290] before implementing persistent root axiom header injection.</action>
    <action>Clean up constructor defaults in @[backend_v2/services/orchestrator/sliding_window_linker.py#L120-L365]: Ensure constructor parameters resolve from injected settings or global settings rather than unanchored literals.</action>
    <constraint invariant="universal_fail_fast">If alignment is broken or files are missing, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/05_phase5_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/settings.py#L54-L972]</backend>
    <backend>@[backend_v2/models/dtos/dag_models.py#L30-L69]</backend>
    <backend>@[backend_v2/models/dtos/causal_discovery.py#L59-L66]</backend>
    <backend>@[backend_v2/services/orchestrator/sliding_window_linker.py#L49-L72]</backend>
    <backend>@[backend_v2/services/orchestrator/sliding_window_linker.py#L120-L365]</backend>
    <backend>@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L79-L290]</backend>
    <backend>@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L94-L149]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py#L42-L370]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`linker_max_global_root_axioms: Annotated[int, Field(ge=0, le=20)] = 8` and `linker_min_window_atoms_quota: Annotated[int, Field(ge=1, le=20)] = 12` added to `Settings` in @[backend_v2/settings.py#L54-L972].</item>
    <item>`warrant_quotes: Annotated[tuple[str, ...] | None, BeforeValidator(coerce_source_quotes_tuple), Field(default=None)] = None` added to `CausalEdge` in @[backend_v2/models/dtos/dag_models.py#L30-L69] and `CausalEdgeDTO` in @[backend_v2/models/dtos/causal_discovery.py#L59-L66].</item>
    <item>`warrant_quotes: Annotated[tuple[str, ...] | None, BeforeValidator(coerce_source_quotes_tuple), Field(default=None)] = None` added to `LinkerEdgeDTO` in @[backend_v2/services/orchestrator/sliding_window_linker.py#L49-L72].</item>
    <item>Bounded deliverable root axiom header injection implemented in @[backend_v2/services/orchestrator/sliding_window_linker.py#L120-L365] with dynamic budget allocation: $W_{min} = 12$, dynamic root axiom allocation $K_{eff} = \min(8, \max(0, M_{win} - W_{current}))$, candidate sorting by `(-OutDegree(v), atom_index_asc)`, and hard budget guard $M_{win} \le 20$.</item>
    <item>`CausalDiscoveryEngine` in @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py#L42-L370] projects `warrant_quotes` from `CausalEdge` into `CausalEdgeDTO` and preserves deliverable input key scoping.</item>
    <item>Algorithm 1 dual fault attribution implemented in @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L79-L290] and @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L94-L149], attributing multi-segment warrant validation failures to `CausalRootCauseType.WARRANT_GROUNDING_FAILURE`.</item>
    <item>Unit tests in @[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py] and @[backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py] pass 100%.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_opaque_id_hydration.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_generation_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT introduce quadratic full-pairwise attention across all claims; strictly preserve sliding window locality with budget guard $M_{win} \le 20$.</anti_target>
    <anti_target>Do NOT mutate downstream export presentation or UI widgets in Phase 5.</anti_target>
    <anti_target>Do NOT use anonymous state tuples for causal edge or node representation.</anti_target>
    <anti_target>Do NOT use hardcoded integer literals for window capacity or root axiom limits outside settings SSOT.</anti_target>
  </anti_targets>

  <step id="1" name="CONFIGURE LINKER SETTINGS &amp; BUDGET CAPACITY LIMITS">
    <action>In @[backend_v2/settings.py#L54-L972]: Add `linker_max_global_root_axioms: Annotated[int, Field(ge=0, le=20, description="Max persistent deliverable root axioms injected into window headers")] = 8` to govern maximum persistent deliverable root axioms injected into window headers.</action>
    <action>In @[backend_v2/settings.py#L54-L972]: Add `linker_min_window_atoms_quota: Annotated[int, Field(ge=1, le=20, description="Minimum current window atom quota before root axiom injection")] = 12` to guarantee current window atom reservation.</action>
    <constraint invariant="system_concurrency_ssot">All global limits and capacity parameters must reference `settings.py` SSOT.</constraint>
  </step>

  <step id="2" name="SUPPORT MULTI-SEGMENT TOULMIN WARRANTS IN CAUSAL EDGES &amp; DTOS">
    <action>In @[backend_v2/models/dtos/dag_models.py#L30-L69]: Add `warrant_quotes: Annotated[tuple[str, ...] | None, BeforeValidator(coerce_source_quotes_tuple), Field(default=None, description="Verbatim source quotes grounding the Toulmin inferential warrant.")] = None` to `CausalEdge` model.</action>
    <action>In @[backend_v2/models/dtos/causal_discovery.py#L59-L66]: Add `warrant_quotes: Annotated[tuple[str, ...] | None, BeforeValidator(coerce_source_quotes_tuple), Field(default=None, description="Verbatim source quotes grounding the Toulmin inferential warrant.")] = None` to `CausalEdgeDTO`.</action>
    <action>In @[backend_v2/services/orchestrator/sliding_window_linker.py#L49-L72]: Add `warrant_quotes: Annotated[tuple[str, ...] | None, BeforeValidator(coerce_source_quotes_tuple), Field(default=None, description="Optional verbatim quotes from source text grounding the Toulmin inferential warrant.")] = None` to `LinkerEdgeDTO`.</action>
    <constraint invariant="zero_permissive_typing">Transit warrants as typed `tuple[str, ...] | None` using `coerce_source_quotes_tuple` instead of raw loose strings or unannotated collections.</constraint>
  </step>

  <step id="3" name="IMPLEMENT BOUNDED ROOT AXIOM HEADER IN SLIDING WINDOW LINKER">
    <action>In @[backend_v2/services/orchestrator/sliding_window_linker.py#L120-L365]: Implement deliverable root axiom candidate selection: track processed atoms and discovered incoming edges in `master_deps`. For window index $i > 0$, identify deliverable root axioms ($\text{InDegree}(v) == 0$) not already present in the current window.</action>
    <action>In @[backend_v2/services/orchestrator/sliding_window_linker.py#L120-L365]: Enforce dynamic quota allocation: compute current window size $W_{current} = \text{len}(window\_atoms)$, dynamic root axiom allocation $K_{eff} = \min(K_{max}, \max(0, M_{win} - W_{current}))$, candidate sorting by `(-OutDegree(v), atom.source_sequence_index)`, and slice to top $K_{eff}$ anchors.</action>
    <action>In @[backend_v2/services/orchestrator/sliding_window_linker.py#L120-L365]: Inject selected root axioms as a static `--- GLOBAL CONTEXT ANCHORS (ROOT AXIOMS) ---` block prepended to `claims_text`, register in `AliasEngine`, and map dependencies to `CausalEdge` preserving `warrant_quotes`.</action>
    <action>In @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py#L42-L370]: Update `CausalDiscoveryEngine.execute` to transit `warrant_quotes=edge.warrant_quotes` from `CausalEdge` into `CausalEdgeDTO`.</action>
    <constraint invariant="the_zero_compromise_pledge">Total atoms in prompt payload must never exceed `linker_max_atoms_per_window` ($M_{win} \le 20$).</constraint>
  </step>

  <step id="4" name="IMPLEMENT ALGORITHM 1 DUAL FAULT ATTRIBUTION IN CAUSAL COHESION EVALUATOR">
    <action>In @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L79-L290] and @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L94-L149]: Enhance `CausalCohesionEvaluator.diagnose_root_causes` to separate multi-segment warrant validation failure into `CausalRootCauseType.WARRANT_GROUNDING_FAILURE` distinct from node proposition extraction failures.</action>
    <action>In @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L94-L149]: Incorporate warrant quote details into diagnostic explanation when `CausalEdgeDTO.warrant_quotes` is present on the failing dependency edge.</action>
    <constraint invariant="universal_fail_fast">Fault attribution must follow strictly typed enum relations without heuristic guessing.</constraint>
  </step>

  <step id="5" name="EXPAND CAUSAL LINKER &amp; COHESION TEST SUITES">
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py]: Verify deterministic root axiom selection, dynamic budget allocation ($W_{min}=12, K_{eff} \le 8$), out-degree candidate sorting, multi-segment warrant extraction in `LinkerEdgeDTO`, and sliding window atom capacity limits.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py]: Verify Algorithm 1 dual fault attribution separating warrant grounding failures from node failures across edge scenarios.</action>
    <constraint invariant="universal_quality_gate">Test suites must achieve 100% pass rate with zero AST warnings.</constraint>
  </step>

  <test_contracts>
    <test name="test_sliding_window_linker_root_axiom_header_quota" category="positive">
      <input>window with 10 current atoms and 12 eligible root axioms</input>
      <expected>8 root axioms injected (budget = 18 &lt;= 20); sorted by OutDegree desc and sequence index asc</expected>
    </test>
    <test name="test_sliding_window_linker_budget_guard_exceeded" category="boundary">
      <input>window with 16 current atoms and 10 eligible root axioms</input>
      <expected>at most 4 root axioms injected so that total &lt;= 20</expected>
    </test>
    <test name="test_sliding_window_linker_zero_root_axioms" category="boundary">
      <input>window with 12 current atoms and 0 eligible root axioms</input>
      <expected>0 root axioms injected; window claims evaluated cleanly</expected>
    </test>
    <test name="test_sliding_window_linker_full_capacity_window" category="boundary">
      <input>window with 20 current atoms and 15 eligible root axioms</input>
      <expected>0 root axioms injected (K_eff = 0), strictly preserving hard budget guard M_win &lt;= 20</expected>
    </test>
    <test name="test_sliding_window_linker_warrant_quotes_transit" category="positive">
      <input>structured LLM response containing multi-segment warrant_quotes on dependency edge</input>
      <expected>transited cleanly into CausalEdge.warrant_quotes as immutable tuple</expected>
    </test>
    <test name="test_causal_cohesion_algorithm_1_dual_fault_attribution_warrant_failure" category="positive">
      <input>sound upstream premise (PASSED) with broken inferential warrant or edge in edge_root_causes</input>
      <expected>attributed to CausalRootCauseType.WARRANT_GROUNDING_FAILURE</expected>
    </test>
    <test name="test_causal_cohesion_algorithm_1_dual_fault_attribution_node_failure" category="negative">
      <input>refuted upstream premise (FAILED) cascading downstream</input>
      <expected>attributed to CausalRootCauseType.NODE_FAILURE</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute linker unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py`.</action>
    <action>Execute cohesion scoring tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py`.</action>
    <action>Execute backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/sliding_window_linker.py backend_v2/services/orchestrator/causal_cohesion_evaluator.py backend_v2/settings.py backend_v2/models/dtos/dag_models.py backend_v2/models/dtos/causal_discovery.py --test --ast-strict`.</action>
    <action>Verify markdown boundaries: `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_158/05_phase5_plan.md`.</action>
    <action>Verify planner output: `uv run python scripts/audit_planner_output.py --epic docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md --plan-dir docs/epic/tasks_EPIC_158/`.</action>
  </validation_gate>
</execution_protocol>

```
