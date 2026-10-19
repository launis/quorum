# Phase 7: Empirical Offline Benchmark & Regression Gate (WP4)

**Overview:** Execute the comprehensive verification suite, offline ablation benchmark ($N=220$), and live integration gates to mathematically prove error reduction ($\widehat{FOR} \le 2.00\%$, $\overline{\kappa} \ge 0.9800$, $r_{iso}^{deliv} \le 0.200$, zero chimera leaks).

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L356-L367] Phase 7: Empirical Offline Benchmark & Regression Gate (WP4)

<!-- Defined in scripts/run_ablation_benchmark.py: AblationPropositionDTO, AblationAtomEvaluationDTO -->

**Target Files:**
- `[NEW]` @[backend_v2/tests/integration/test_multi_segment_causal_e2e.py]
- `[MODIFY]` @[scripts/run_e2e_variance_test.py#L831-L876]
- `[MODIFY]` @[scripts/run_e2e_variance_test.py#L1547-L1950]
- `[MODIFY]` @[scripts/run_e2e_variance_test.py#L1953-L2112]
- `[MODIFY]` @[scripts/run_ablation_benchmark.py#L84-L96]
- `[MODIFY]` @[scripts/run_ablation_benchmark.py#L108-L122]
- `[MODIFY]` @[scripts/run_ablation_benchmark.py#L492-L544]
- `[MODIFY]` @[scripts/run_ablation_benchmark.py#L546-L669]

## Five-Column Architectural Directives

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Ablation Benchmark Truthiness & Evaluation**<br>`@[scripts/run_ablation_benchmark.py#L546-L669]` | Evaluating truthiness of `GateMatchResultDTO` instance returned by `AnchorValidationService._is_lexically_valid`; treating non-empty DTO as truthy boolean and masking chimera leaks (`is_chimera = not is_quote_valid` evaluating to False). | Explicit extraction of `.is_valid` from `GateMatchResultDTO` (`match_res = AnchorValidationService._is_lexically_valid(...)`, `is_quote_valid = match_res.is_valid`, `is_chimera = not is_quote_valid`), guaranteeing Popperian null hypothesis rejection. | Avoid wrapping lexical match results in redundant boolean converter classes; access `.is_valid` directly. | Unit tests in `test_run_ablation_benchmark.py` verifying chimera identification for unanchored quotes. |
| **Ablation Proposition & Atom Evaluation DTOs**<br>`@[scripts/run_ablation_benchmark.py#L84-L96]`<br>`@[scripts/run_ablation_benchmark.py#L108-L122]` | Scalar string quote constraints `synthetic_quote: str \| None` and `source_quote: str \| None`; dropping multi-segment citation support in research benchmark driver. | Modernize `AblationPropositionDTO` and `AblationAtomEvaluationDTO` to support multi-segment quotes via `synthetic_quotes: tuple[str, ...] \| None` and `source_quotes: tuple[str, ...] \| None` with `coerce_source_quotes_tuple`. | Avoid separate parallel DTO hierarchies for scalar vs multi-segment ablation; use single unified DTO contract. | Pydantic validation tests asserting multi-segment tuple parsing and immutability. |
| **Execution Kelvollisuus & Multi-Segment Grounding**<br>`@[scripts/run_e2e_variance_test.py#L831-L876]` | Checking only execution status and data starvation in `validate_execution_kelvollisuus`; ignoring multi-segment quote validity and allowing unanchored chimeras to pass silently. | Enhance `validate_execution_kelvollisuus` to assert that all atom evaluations carrying `source_quotes` satisfy lexical verification against corpus text buffers with zero chimera leakage. | Avoid duplicate corpus loaders in variance checker; utilize existing text extraction and `AnchorValidationService`. | Automated assertion in `run_variance_test` raising failure if unanchored chimeras are accepted. |
| **Variance Runner Benchmark CLI & Delegation**<br>`@[scripts/run_e2e_variance_test.py#L1547-L1950]`<br>`@[scripts/run_e2e_variance_test.py#L1953-L2112]` | Requiring manual invocation of disparate scripts; lacking centralized CLI parameter to execute and assert the offline ablation benchmark directly from variance runner. | Implement `verify_offline_ablation_benchmark` in `run_e2e_variance_test.py` and expose `--run-ablation` CLI argument, executing the 220 proposition frame benchmark and asserting pass rate $\ge 56.4\%$ and $0/21$ chimeras. | Avoid reimplementing benchmark logic inside `run_e2e_variance_test.py`; delegate cleanly to `AblationBenchmarkRunner`. | CLI execution `uv run python scripts/run_e2e_variance_test.py --run-ablation` exiting with code 0. |
| **Multi-Segment Proposition Frame Generation**<br>`@[scripts/run_ablation_benchmark.py#L492-L544]` | Generating only single-sentence synthetic quotes; omitting multi-segment non-contiguous citation frames in standardized 220-atom evaluation suite. | Generate proposition frames containing 1–3 non-contiguous ordered segments with monotonic ordering ($s_1 < e_1 < s_2 < e_2 \le s_1 + 1\,000$) and 21 synthetic chimera probes. | Avoid non-deterministic randomized quote generation; use reproducible deterministic pseudorandom hashing. | Benchmark execution verifying $N=220$ atoms with exact partition verification. |
| **Multi-Segment Causal E2E Integration Suite**<br>`[NEW] @[backend_v2/tests/integration/test_multi_segment_causal_e2e.py]` | Omission of full-stack integration verification; testing multi-segment quotes, root axioms, decoupled strictness, and SDUI presentation only in isolation. | Implement end-to-end integration test suite exercising: (1) DAG execution with multi-segment evidence quotes; (2) Persistent root axiom header linking; (3) Decoupled lexical strictness tolerance calibration; (4) SDUI, PDF, and tabular export generation. | Avoid live cloud network calls or slow sleep loops; utilize in-memory mock providers and deterministic fixtures. | `uv run pytest backend_v2/tests/integration/test_multi_segment_causal_e2e.py` passing 100%. |
| **Automated Quality Gates & Live E2E Real LLM Test**<br>`@[backend_v2/tests/integration/test_integration_real_llm.py]` | Declaring phase complete without executing global completion gates; bypassing live LLM test due to execution time. | Execute full backend audit loop (`backend_audit_loop.py backend_v2/ --test --ast-strict`), full Flutter audit loop (`flutter_audit_loop.py client_app_v2/ --build`), and mandatory live E2E gate (`test_integration_real_llm.py`). | Avoid skipping AST guardrails or running localized subsets as completion gates. | 100% clean check across all quality gates and live real-LLM E2E pass. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUPS">
    <action>Look backward: Verify all backend services, seed data, presentation adapters, and client UI widgets from Phases 1 through 6 are fully implemented and compiling.</action>
    <action>Look forward: Verify test harness environment before executing heavy offline benchmarks and real LLM integration tests.</action>
    <action>Eradicate Truthiness Bug in @[scripts/run_ablation_benchmark.py#L546-L669]: Refactor line 627 `is_quote_valid = AnchorValidationService._is_lexically_valid(...)` to explicitly extract `.is_valid` from `GateMatchResultDTO`, ensuring `is_chimera = not is_quote_valid` operates on a strict boolean.</action>
    <action>Modernize Ablation DTOs in @[scripts/run_ablation_benchmark.py#L84-L96] and @[scripts/run_ablation_benchmark.py#L108-L122]: Add `synthetic_quotes: tuple[str, ...] | None = None` and `source_quotes: tuple[str, ...] | None = None` with canonical `coerce_source_quotes_tuple` to support multi-segment quotes in research benchmarks.</action>
    <constraint invariant="universal_fail_fast">If any prerequisite phase is unverified, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/07_phase7_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <backend>[NEW] @[backend_v2/tests/integration/test_multi_segment_causal_e2e.py]</backend>
    <tooling>@[scripts/run_e2e_variance_test.py#L831-L876]</tooling>
    <tooling>@[scripts/run_e2e_variance_test.py#L1547-L1950]</tooling>
    <tooling>@[scripts/run_e2e_variance_test.py#L1953-L2112]</tooling>
    <tooling>@[scripts/run_ablation_benchmark.py#L84-L96]</tooling>
    <tooling>@[scripts/run_ablation_benchmark.py#L108-L122]</tooling>
    <tooling>@[scripts/run_ablation_benchmark.py#L492-L544]</tooling>
    <tooling>@[scripts/run_ablation_benchmark.py#L546-L669]</tooling>
  </touched_artifacts>

  <dod_checklist>
    <item>Truthiness bug in @[scripts/run_ablation_benchmark.py#L546-L669] eradicated by extracting `GateMatchResultDTO.is_valid`.</item>
    <item>Ablation DTOs in @[scripts/run_ablation_benchmark.py#L84-L96] and @[scripts/run_ablation_benchmark.py#L108-L122] modernized to support multi-segment quotes via `source_quotes: tuple[str, ...] | None`.</item>
    <item>Execution kelvollisuus in @[scripts/run_e2e_variance_test.py#L831-L876] updated to verify multi-segment quote grounding without chimera leakage.</item>
    <item>Variance benchmark runner in @[scripts/run_e2e_variance_test.py#L1547-L1950] and `@[scripts/run_e2e_variance_test.py#L1953-L2112]` updated with `verify_offline_ablation_benchmark` and `--run-ablation` CLI option.</item>
    <item>Offline ablation benchmark ($N=220$) in @[scripts/run_ablation_benchmark.py#L492-L544] achieves $\ge 56.4\,\%$ acceptance with zero chimera leaks ($0/21$).</item>
    <item>Integration test suite [NEW] @[backend_v2/tests/integration/test_multi_segment_causal_e2e.py] implemented and passing 100%.</item>
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
    <anti_target>Do NOT evaluate truthiness of Pydantic DTO instances without extracting explicit boolean fields.</anti_target>
  </anti_targets>

  <step id="1" name="IMPLEMENT END-TO-END MULTI-SEGMENT INTEGRATION TEST">
    <action>In [NEW] @[backend_v2/tests/integration/test_multi_segment_causal_e2e.py]: Implement end-to-end integration tests exercising: (1) DAG execution with multi-segment evidence quotes; (2) Persistent root axiom header linking; (3) Decoupled lexical strictness tolerance calibration; (4) SDUI, PDF, and tabular export generation; and (5) ISTQB negative partitions covering bounding span violations, inverted order, and cross-document chimeras.</action>
    <constraint invariant="universal_quality_gate">Test must execute without warnings and verify stateful roundtrip persistence.</constraint>
  </step>

  <step id="2" name="EXECUTE OFFLINE ABLATION BENCHMARK &amp; VARIANCE SUITE">
    <action>In @[scripts/run_e2e_variance_test.py#L831-L876]: Update `validate_execution_kelvollisuus` to assert that all atom evaluations with `source_quotes` pass lexical grounding without chimera leakage.</action>
    <action>In @[scripts/run_e2e_variance_test.py#L1547-L1950] and `@[scripts/run_e2e_variance_test.py#L1953-L2112]`: Implement `verify_offline_ablation_benchmark` and add `--run-ablation` CLI option to execute the 220 proposition frame benchmark.</action>
    <action>In @[scripts/run_ablation_benchmark.py#L492-L544] and `@[scripts/run_ablation_benchmark.py#L546-L669]`: Generate multi-segment proposition frames and execute offline benchmark verifying pass rate $\ge 56.4\%$ and zero chimera leaks ($0/21$).</action>
    <constraint invariant="strict_physical_anchoring_mandate">Zero chimera acceptance tolerance ($\text{Specificity}_{lex} = 1.000$).</constraint>
  </step>

  <step id="3" name="EXECUTE FULL AUDIT GATES &amp; MANDATORY LIVE E2E TEST">
    <action>In @[backend_v2/tests/integration/test_integration_real_llm.py]: Execute mandatory live E2E test gate with $env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py.</action>
    <action>Execute full backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Execute full Flutter audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
    <constraint invariant="universal_quality_gate">All automated completion gates must pass 100%.</constraint>
  </step>

  <test_contracts>
    <test name="test_multi_segment_causal_e2e_dag_execution" category="positive">
      <input>Full DAG execution with multi-segment evidence quotes (2-3 non-contiguous sentences)</input>
      <expected>All atoms evaluated, source_quotes persisted as tuples, and verified with GateMatchResultDTO.is_valid=True</expected>
    </test>
    <test name="test_multi_segment_causal_e2e_root_axiom_header_linking" category="positive">
      <input>SlidingWindowLinker execution with candidate deliverable root axioms</input>
      <expected>Global context anchor header injected, dynamic quota allocated (W_min=12, K_eff<=8), and warrant_quotes persisted</expected>
    </test>
    <test name="test_multi_segment_causal_e2e_strictness_calibration" category="positive">
      <input>Workflow execution at default_lexical_strictness_level=50 vs 100</input>
      <expected>Strictness 50 permits Snowball morphology; strictness 100 rejects morphology fail-fast</expected>
    </test>
    <test name="test_multi_segment_causal_e2e_report_and_export_generation" category="positive">
      <input>Report generation for execution with multi-segment quotes</input>
      <expected>SDUI blocks, Jinja2 HTML, and tabular exports contain non-empty ' [...] ' formatted citations</expected>
    </test>
    <test name="test_multi_segment_causal_e2e_negative_chimera_and_ordering_rejection" category="negative">
      <input>Adversarial atoms with distance >1000 chars, inverted order, or cross-document chimera</input>
      <expected>AnchorValidationService rejects all adversarial probes with is_valid=False (0 chimera leaks)</expected>
    </test>
    <test name="test_multi_segment_causal_e2e_negative_warrant_grounding_failure" category="negative">
      <input>Causal edge with unanchored or invalid warrant quote</input>
      <expected>CausalCohesionEvaluator diagnoses WARRANT_GROUNDING_FAILURE distinguishing it from NODE_FAILURE</expected>
    </test>
    <test name="test_offline_ablation_benchmark_pass_rate" category="positive">
      <input>220 benchmark proposition frames via verify_offline_ablation_benchmark</input>
      <expected>Pass rate >= 56.4% and zero chimera leaks (0/21) under Configuration 1</expected>
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
