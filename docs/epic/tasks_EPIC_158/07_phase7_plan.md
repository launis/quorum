# Phase 7: Empirical Offline Benchmark & Regression Gate (WP4)

**Overview:** Execute the comprehensive verification suite, offline ablation benchmark ($N=220$), and live integration gates to mathematically prove error reduction ($\widehat{FOR} \le 2.00\%$, $\overline{\kappa} \ge 0.9800$, $r_{iso}^{deliv} \le 0.200$, zero chimera leaks).

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L356-L366] Phase 7: Empirical Offline Benchmark & Regression Gate (WP4)

**Target Files:**
- `[NEW]` @[backend_v2/tests/integration/test_multi_segment_causal_e2e.py]
- `[MODIFY]` @[scripts/run_e2e_variance_test.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify all backend services, seed data, presentation adapters, and client UI widgets from Phases 1 through 6 are fully implemented and compiling.</action>
    <action>Look forward: Verify test harness environment before executing heavy offline benchmarks and real LLM integration tests.</action>
    <constraint invariant="universal_fail_fast">If any prerequisite phase is unverified, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/07_phase7_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <backend>[NEW] @[backend_v2/tests/integration/test_multi_segment_causal_e2e.py]</backend>
    <tooling>@[scripts/run_e2e_variance_test.py]</tooling>
  </touched_artifacts>

  <dod_checklist>
    <item>Integration test suite [NEW] @[backend_v2/tests/integration/test_multi_segment_causal_e2e.py] implemented and passing 100%.</item>
    <item>Variance benchmark runner @[scripts/run_e2e_variance_test.py] updated and offline ablation benchmark ($N=220$) achieves $\ge 56.4\,\%$ acceptance with zero chimera leaks ($0/21$).</item>
    <item>Full backend audit loop passes with zero AST or typing errors: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</item>
    <item>Full Flutter client audit passes: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</item>
    <item>Mandatory Live E2E gate executes successfully: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
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
    <anti_target>Do NOT bypass live E2E testing or suppress benchmark variance failures.</anti_target>
    <anti_target>Do NOT alter production seed prompts or domain tolerances to artificially pass tests.</anti_target>
  </anti_targets>

  <step id="1" name="IMPLEMENT END-TO-END MULTI-SEGMENT INTEGRATION TEST">
    <action>In [NEW] @[backend_v2/tests/integration/test_multi_segment_causal_e2e.py]: Create integration test verifying: (1) DAG execution with multi-segment evidence quotes; (2) Persistent root axiom header linking; (3) Decoupled lexical strictness tolerance calibration; (4) Report generation with verified multi-segment quotes.</action>
    <constraint invariant="universal_quality_gate">Test must execute without warnings and verify stateful roundtrip persistence.</constraint>
  </step>

  <step id="2" name="EXECUTE OFFLINE ABLATION BENCHMARK &amp; VARIANCE SUITE">
    <action>In @[scripts/run_e2e_variance_test.py]: Update benchmark runner to exercise multi-segment verification and execute offline benchmark over 220 proposition frames, verifying acceptance rate $\ge 56.4\,\%$ and zero chimera leaks ($0/21$).</action>
    <constraint invariant="strict_physical_anchoring_mandate">Zero chimera acceptance tolerance ($\text{Specificity}_{lex} = 1.000$).</constraint>
  </step>

  <step id="3" name="EXECUTE FULL AUDIT GATES &amp; MANDATORY LIVE E2E TEST">
    <action>Execute full backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Execute full Flutter audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
    <action>Execute mandatory live E2E test: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.</action>
    <constraint invariant="universal_quality_gate">All automated completion gates must pass 100%.</constraint>
  </step>

  <test_contracts>
    <test name="test_offline_ablation_benchmark_pass_rate" category="positive">
      <input>220 benchmark proposition frames</input>
      <expected>At least 124 frames pass (>= 56.4%) and 0 chimera leaks out of 21 adversarial probes</expected>
    </test>
    <test name="test_live_e2e_real_llm_execution" category="positive">
      <input>Real LLM execution with RUN_LIVE_E2E=true</input>
      <expected>Full DAG execution completes and persists valid report data</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute full backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Execute full Flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
    <action>Execute mandatory live E2E gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.</action>
  </validation_gate>
</execution_protocol>
```
