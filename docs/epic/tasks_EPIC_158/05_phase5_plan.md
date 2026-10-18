# Phase 5: Long-Range Causal Horizon Expansion & Global Context Anchor Header for Root Axioms (WP3)

**Overview:** Upgrade `SlidingWindowLinker` to anchor deliverable root axioms ($InDegree(v)=0$) as a persistent Global Context Anchor header block across subsequent sliding windows, eliminating the document length-dependent long-tail truncation defect while enforcing dynamic budget allocation ($W_{min}=12, K_{eff} \le 8, M_{win} \le 20$). Implement Algorithm 1 dual fault attribution separating multi-segment warrant failures into `CausalRootCauseType.WARRANT_GROUNDING_FAILURE`.

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L325-L336] Phase 5: Long-Range Causal Horizon Expansion & Global Context Anchor Header for Root Axioms (WP3)

**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/sliding_window_linker.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]
- `[MODIFY]` @[backend_v2/settings.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify multi-segment lexical validation and strictness decoupling are operational in @[backend_v2/services/orchestrator/anchor_validation_service.py] and @[backend_v2/models/domain/workflow.py].</action>
    <action>Look forward: Verify baseline state in @[backend_v2/services/orchestrator/sliding_window_linker.py] and @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py] before implementing persistent root axiom header injection.</action>
    <constraint invariant="universal_fail_fast">If alignment is broken or files are missing, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/05_phase5_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/sliding_window_linker.py]</backend>
    <backend>@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]</backend>
    <backend>@[backend_v2/settings.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`linker_max_global_root_axioms: int = 8` added to `Settings` in @[backend_v2/settings.py].</item>
    <item>Bounded deliverable root axiom header injection implemented in @[backend_v2/services/orchestrator/sliding_window_linker.py] with dynamic budget allocation: $W_{min} = 12$, dynamic root axiom allocation $K_{eff} = \min(8, \max(0, M_{win} - W_{current}))$, candidate sorting by `(-OutDegree(v), atom_index_asc)`, and hard budget guard $M_{win} \le 20$.</item>
    <item>Support for multi-segment Toulmin warrants $\lambda(W_{P'C}) = 1$ added to `CausalEdge` creation in @[backend_v2/services/orchestrator/sliding_window_linker.py].</item>
    <item>Algorithm 1 dual fault attribution implemented in @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py], attributing multi-segment warrant validation failures to `CausalRootCauseType.WARRANT_GROUNDING_FAILURE`.</item>
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
  </anti_targets>

  <step id="1" name="CONFIGURE LINKER SETTINGS &amp; BUDGET LIMITS">
    <action>In @[backend_v2/settings.py]: Add setting `linker_max_global_root_axioms: int = 8` to govern maximum persistent deliverable root axioms injected into window headers.</action>
    <constraint invariant="system_concurrency_ssot">All global limits and capacity parameters must reference `settings.py` SSOT.</constraint>
  </step>

  <step id="2" name="IMPLEMENT BOUNDED ROOT AXIOM HEADER IN SLIDING WINDOW LINKER">
    <action>In @[backend_v2/services/orchestrator/sliding_window_linker.py]: Implement deliverable root axiom detection ($InDegree(v)=0$). Enforce dynamic quota allocation: guaranteed minimum current window quota $W_{min} = 12$, dynamic root axiom allocation $K_{eff} = \min(8, \max(0, M_{win} - W_{current}))$, candidate sorting by `(-OutDegree(v), atom_index_asc)`, and hard budget guard $M_{win} \le 20$. Inject selected root axioms as a static header block.</action>
    <constraint invariant="the_zero_compromise_pledge">Total atoms in prompt payload must never exceed `linker_max_atoms_per_window`.</constraint>
  </step>

  <step id="3" name="SUPPORT MULTI-SEGMENT TOULMIN WARRANTS IN CAUSAL EDGES">
    <action>In @[backend_v2/services/orchestrator/sliding_window_linker.py]: Update causal edge instantiation to accept and preserve multi-segment warrant citations $\lambda(W_{P'C}) = 1$ in `CausalEdge` records.</action>
    <constraint invariant="zero_permissive_typing">Transit warrants as typed `tuple[str, ...] | None` instead of raw loose strings.</constraint>
  </step>

  <step id="4" name="IMPLEMENT ALGORITHM 1 DUAL FAULT ATTRIBUTION">
    <action>In @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]: Enhance BARS evaluation to separate multi-segment warrant validation failure into `CausalRootCauseType.WARRANT_GROUNDING_FAILURE` distinct from node proposition extraction failures.</action>
    <constraint invariant="universal_fail_fast">Fault attribution must follow strictly typed enum relations without heuristic guessing.</constraint>
  </step>

  <step id="5" name="EXPAND CAUSAL LINKER &amp; COHESION TEST SUITES">
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py]: Verify deterministic root axiom selection, dynamic budget allocation ($W_{min}=12, K_{eff} \le 8$), and sliding window atom capacity limits.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py]: Verify Algorithm 1 dual fault attribution between node and warrant failures.</action>
    <constraint invariant="universal_quality_gate">Test suites must achieve 100% pass rate with zero AST warnings.</constraint>
  </step>

  <test_contracts>
    <test name="test_sliding_window_linker_root_axiom_header_quota" category="positive">
      <input>window with 10 current atoms and 12 eligible root axioms</input>
      <expected>8 root axioms injected (budget = 18 <= 20); sorted by OutDegree desc</expected>
    </test>
    <test name="test_sliding_window_linker_budget_guard_exceeded" category="boundary">
      <input>window with 16 current atoms and 10 eligible root axioms</input>
      <expected>at most 4 root axioms injected so that total <= 20</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute linker unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py`.</action>
    <action>Execute cohesion scoring tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py`.</action>
    <action>Execute backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/sliding_window_linker.py backend_v2/services/orchestrator/causal_cohesion_evaluator.py --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
