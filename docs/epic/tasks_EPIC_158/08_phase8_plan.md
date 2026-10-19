# Phase 8: As-Built Architectural Documentation & Scientific Manuscript Synchronization (`@[docs/tiede.md]`)

**Overview:** Execute the post-implementation `/tier7-describe-architecture` audit to synchronize target Knowledge Items, timeless architecture pillars, directory references, and update `@[docs/tiede.md]` with rigorous academic prose, formal mathematical definitions, theorems, and verified empirical proofs.

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L367-L382] Phase 8: As-Built Architectural Documentation & Scientific Manuscript Synchronization (`@[docs/tiede.md]`)

**Target Files:**
- `[MODIFY]` @[.agents/rules/04_directory_reference.md#L25-L30]
- `[MODIFY]` @[.agents/rules/04_directory_reference.md#L62-L72]
- `[MODIFY]` @[.agents/rules/04_directory_reference.md#L118-L122]
- `[MODIFY]` @[docs/tiede.md#L66-L83]
- `[MODIFY]` @[docs/tiede.md#L84-L93]
- `[MODIFY]` @[docs/tiede.md#L214-L222]
- `[MODIFY]` @[docs/tiede.md#L236-L241]
- `[MODIFY]` @[docs/tiede.md#L876-L936]

## Five-Column Architectural Directives

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Integration Test Directory Reference**<br>`@[.agents/rules/04_directory_reference.md#L25-L30]` | Omitting newly created integration test `backend_v2/tests/integration/test_multi_segment_causal_e2e.py` from directory reference rule; untyped or informal test naming. | Formally register `backend_v2/tests/integration/test_multi_segment_causal_e2e.py` under the Python Backend Integration Tests directory index in `04_directory_reference.md`. | Avoid speculative directory paths or duplicate index references. | `backend_audit_loop.py` clean import and directory reference validation. |
| **Forensic DTO Directory Reference**<br>`@[.agents/rules/04_directory_reference.md#L62-L72]` | Leaving `quote_evidence.py` unindexed in DTOs collection; relying on ad-hoc import paths for multi-segment contracts. | Formally register `quote_evidence.py` under `backend_v2/models/dtos/` as the canonical SSOT for forensic evidence quote structures (`QuoteEvidenceDTO`, `GateMatchResultDTO`). | Avoid redundant DTO aliases or shadow models. | Full-duplex DTO parity check (`audit_dto_parity.py`) validates alignment. |
| **Benchmark Script Directory Reference**<br>`@[.agents/rules/04_directory_reference.md#L118-L122]` | Omitting `run_ablation_benchmark.py` from scripts index; treating benchmark as temporary scratch file. | Formally register `scripts/run_ablation_benchmark.py (Offline Multi-Segment & Chimera Ablation Benchmark Suite)` in `04_directory_reference.md`. | Prune redundant CLI wrappers or unindexed script aliases. | `audit_clean_imports.py` and quality gate execution pass cleanly. |
| **Scientific Manuscript Definition 1 Multi-Segment Vector**<br>`@[docs/tiede.md#L66-L83]` | Single scalar string span assumption ($\mathcal{C}_i \subset \Sigma^*$); permissive ellipses splicing; ungrounded cross-document quote stitching. | Formalize Definition 1 with ordered bounding span vector $\vec{\mathcal{C}}_i = (\mathcal{C}_{i,1}, \dots, \mathcal{C}_{i,m})$ where $1 \le m \le 3$, monotonic ordering $s_1 < e_1 < s_2 < e_2 \le s_1 + 1\,000$, and buffer boundary isolation across source documents. | Ban unbounded multi-segment lists ($m > 3$) or cross-document multi-span merges. | LaTeX syntax verification via `test_tiede_latex_syntax_validity` test contract. |
| **Theorem on Lexical Specificity Invariant**<br>`@[docs/tiede.md#L84-L93]` | Speculative specificity claims without formal mathematical proof; assuming string matching alone solves semantic entailment. | State and prove Theorem on Lexical Specificity Invariant $\text{Specificity}_{lex} = 1.000$ under bounded spans and monotonic ordering, bounding chimera leakage to $\epsilon_{lexical} \to 0$ and separating physical containment from semantic entailment. | Avoid bloated formal proofs requiring undecidable semantic logic; maintain clean separation between physical containment and semantic entailment. | Empirical verification against 220-atom offline ablation benchmark metrics ($0/21$ chimeras, $\text{Spec}_{lex} = 1.000$). |
| **Section 4.1.1 Gate 5 Epistemic Decoupling**<br>`@[docs/tiede.md#L214-L222]` | Conflating scoring dampening exponent $\zeta_{score}$ with lexical matching threshold $\zeta_{lex}$; blocking morphological stemming under strict scoring. | Formalize Section 4.1.1 Gate 5 Epistemic Decoupling separating lexical strictness $\zeta_{lex} \in [0, 100]$ from scoring strictness $\zeta_{score} \in [0, 100]$, parameterizing independent thresholds where $\zeta_{lex} < 85$ enables Snowball stemming regardless of scoring rigor. | Ban dynamic per-atom floating threshold negotiations; maintain deterministic 4-tier step schedule. | Verified by `test_strictness_decoupling_high_scoring_allows_morphology` in `test_anchor_validation_service.py`. |
| **Section 4.2 Bounded Deliverable Root Axiom Anchoring**<br>`@[docs/tiede.md#L236-L241]` | Unconstrained sliding-window truncation leaving foundational axioms stranded; unbounded header injection blowing context budgets. | Formalize Section 4.2 Bounded Deliverable Root Axiom Anchoring $K_{axiom}^{max} = 8$ with dynamic quota allocation $W_{min} = 12, K_{eff} = \min(8, \max(0, 20 - W_{current})), M_{win} \le 20$ and deterministic sorting by $(-OutDegree(v), atom\_index\_asc)$, preserving the Local Causal Markov Condition. | Ban recursive graph traversal inside prompt compilation; linker operates as a single deterministic topological pass. | Verified by `test_sliding_window_linker.py` and `test_causal_cohesion_scoring.py`. |
| **Section 8 Empirical Benchmark & False Omission Reduction**<br>`@[docs/tiede.md#L876-L936]` | Reporting speculative or outdated benchmark numbers; omitting reduction in False Omission Rate. | Incorporate verified Phase 7 benchmark findings in Section 8: reduction of $\widehat{\text{FOR}}$ from $13.33\%$ to $\le 2.00\%$ ($FOR_{omission} \to 0.00\%$, $FOR_{rejection} \to 0.00\%$), offline ablation pass rate $58.2\% \ge 56.4\%$, and $\bar{\kappa} \ge 0.9800$. | Avoid bloated uncurated log dumps; present concise, mathematically grounded empirical tables matching Table 7 and 7b. | Verified by `run_ablation_benchmark.py` and `test_multi_segment_causal_e2e.py`. |
| **Parameterized Tier 7 Execution Directives**<br>`@[docs/epic/tasks_EPIC_158/08_phase8_plan.md]` | Bare, unparameterized `/tier7-describe-architecture` calls; manual direct editing of `docs/architecture/01_` through `04_` during coding workflows. | Fully parameterize `/tier7-describe-architecture [NEW] @[docs/epic/EPIC_158_tracker.md] @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md] @[ki_structured_forensic_quotes.md] @[ki_topological_engine.md] @[ki_unified_matrix_scoring_strictness.md] @[ki_prompt_orchestration_and_matrix_evaluation.md]` with explicit directives for target KIs, directory references, and architecture pillars. | Ban modifying unrelated KIs or regenerating untouched architecture documents. | Verification gate asserts updated `metadata.json` timestamps on all 4 target KIs and clean syntax on all outputs. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUPS">
    <action>Look backward: Verify Phase 7 empirical benchmark and live integration tests passed with 100% adherence to invariants.</action>
    <action>Look forward: Verify baseline state in @[.agents/rules/04_directory_reference.md] and @[docs/tiede.md] before synchronizing documentation and scientific manuscripts.</action>
    <action>Audit baseline line boundaries in @[.agents/rules/04_directory_reference.md#L25-L30], @[.agents/rules/04_directory_reference.md#L62-L72], and @[.agents/rules/04_directory_reference.md#L118-L122] to ensure clean insertion points.</action>
    <action>Audit baseline sections in @[docs/tiede.md#L66-L83], @[docs/tiede.md#L84-L93], @[docs/tiede.md#L214-L222], @[docs/tiede.md#L236-L241], and @[docs/tiede.md#L876-L936] to ensure clean LaTeX theorem and empirical table alignment.</action>
    <constraint invariant="universal_fail_fast">If Phase 7 benchmarks failed, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/08_phase8_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <rules>@[.agents/rules/04_directory_reference.md#L25-L30]</rules>
    <rules>@[.agents/rules/04_directory_reference.md#L62-L72]</rules>
    <rules>@[.agents/rules/04_directory_reference.md#L118-L122]</rules>
    <documentation>@[docs/tiede.md#L66-L83]</documentation>
    <documentation>@[docs/tiede.md#L84-L93]</documentation>
    <documentation>@[docs/tiede.md#L214-L222]</documentation>
    <documentation>@[docs/tiede.md#L236-L241]</documentation>
    <documentation>@[docs/tiede.md#L876-L936]</documentation>
  </touched_artifacts>

  <dod_checklist>
    <item>Newly created integration test `backend_v2/tests/integration/test_multi_segment_causal_e2e.py` registered in @[.agents/rules/04_directory_reference.md#L25-L30].</item>
    <item>Modernized DTO module `quote_evidence.py` registered in @[.agents/rules/04_directory_reference.md#L62-L72].</item>
    <item>Ablation benchmark script `run_ablation_benchmark.py` registered in @[.agents/rules/04_directory_reference.md#L118-L122].</item>
    <item>Scientific manuscript @[docs/tiede.md#L66-L83] synchronized with Definition 1 ordered bounding span vector $\vec{\mathcal{C}}_i = (\mathcal{C}_{i,1}, \dots, \mathcal{C}_{i,m})$ where $1 \le m \le 3$, monotonic ordering $s_1 < e_1 < s_2 < e_2 \le s_1 + 1\,000$, and buffer boundary isolation.</item>
    <item>Theorem on Lexical Specificity Invariant $\text{Specificity}_{lex} = 1.000$ formalized in @[docs/tiede.md#L84-L93].</item>
    <item>Gate 5 Epistemic Decoupling separating $\zeta_{lex}$ from $\zeta_{score}$ formalized in @[docs/tiede.md#L214-L222].</item>
    <item>Bounded Deliverable Root Axiom Anchoring ($K_{axiom}^{max} = 8, W_{min} = 12, M_{win} \le 20$) formalized in @[docs/tiede.md#L236-L241].</item>
    <item>Verified Phase 7 empirical benchmark findings (reduction of $\widehat{\text{FOR}}$ from $13.33\%$ to $\le 2.00\%$, pass rate $58.2\% \ge 56.4\%$, $\bar{\kappa} \ge 0.9800$) formalized in @[docs/tiede.md#L876-L936].</item>
    <item>Target Knowledge Items synchronized with updated timestamps: `ki_structured_forensic_quotes.md`, `ki_topological_engine.md`, `ki_unified_matrix_scoring_strictness.md`, and `ki_prompt_orchestration_and_matrix_evaluation.md`.</item>
    <item>Timeless architecture pillars synchronized in present tense: `01_system_context_and_invariants.md`, `03_cognitive_orchestration_engine.md`, and `04_server_driven_ui_and_presentation.md`.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
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
    <anti_target>Do NOT document code using historical progressions, phases, or narrative development stages in `docs/architecture/`.</anti_target>
    <anti_target>Do NOT introduce ungrounded mathematical proofs or speculative benchmark numbers into `docs/tiede.md`.</anti_target>
    <anti_target>Do NOT manually edit architecture pillars during coding workflows; route updates exclusively via parameterized Tier 7 audit.</anti_target>
  </anti_targets>

  <step id="1" name="UPDATE DIRECTORY REFERENCE RULE">
    <action>In @[.agents/rules/04_directory_reference.md#L25-L30]: Register newly created integration test suite `backend_v2/tests/integration/test_multi_segment_causal_e2e.py` under the Python Backend Integration Tests directory index.</action>
    <action>In @[.agents/rules/04_directory_reference.md#L62-L72]: Register modernized forensic quote DTO module `quote_evidence.py` under the Schemas &amp; DTOs dtos/ module index.</action>
    <action>In @[.agents/rules/04_directory_reference.md#L118-L122]: Register `run_ablation_benchmark.py (Offline Multi-Segment &amp; Chimera Ablation Benchmark Suite)` under the scripts/ module index.</action>
    <constraint invariant="dual_axis_documentation_mandate">Rules and directory references must reflect physical filesystem state.</constraint>
  </step>

  <step id="2" name="SYNCHRONIZE SCIENTIFIC MANUSCRIPT (TIEDE.MD)">
    <action>In @[docs/tiede.md#L66-L83]: Formalize Definition 1 ordered bounding span vector $\vec{\mathcal{C}}_i = (\mathcal{C}_{i,1}, \dots, \mathcal{C}_{i,m})$ where $1 \le m \le 3$, monotonic ordering $s_1 < e_1 < s_2 < e_2 \le s_1 + 1\,000$, and buffer boundary isolation across source documents.</action>
    <action>In @[docs/tiede.md#L84-L93]: Formalize Theorem on Lexical Specificity Invariant $\text{Specificity}_{lex} = 1.000$ under bounded spans and monotonic ordering, bounding chimera leakage to $\epsilon_{lexical} \to 0$.</action>
    <action>In @[docs/tiede.md#L214-L222]: Formalize Section 4.1.1 Gate 5 Epistemic Decoupling separating lexical strictness $\zeta_{lex}$ from scoring strictness $\zeta_{score}$, documenting independent parameters on `Workflow`.</action>
    <action>In @[docs/tiede.md#L236-L241]: Formalize Section 4.2 Bounded Deliverable Root Axiom Anchoring $K_{axiom}^{max} = 8$ with dynamic quota allocation $W_{min} = 12, K_{eff} = \min(8, \max(0, 20 - W_{current})), M_{win} \le 20$ preserving the Local Causal Markov Condition.</action>
    <action>In @[docs/tiede.md#L876-L936]: Incorporate verified Phase 7 benchmark findings in Section 8: reduction of $\widehat{\text{FOR}}$ from $13.33\%$ to $\le 2.00\%$ ($FOR_{omission} \to 0.00\%$, $FOR_{rejection} \to 0.00\%$), offline ablation pass rate $58.2\% \ge 56.4\%$, and $\bar{\kappa} \ge 0.9800$.</action>
    <constraint invariant="english_language_mandate">Scientific manuscript must be written in academic English with rigorous LaTeX syntax parity.</constraint>
  </step>

  <step id="3" name="EXECUTE TIER 7 AS-BUILT ARCHITECTURE AUDIT">
    <action>In @[docs/epic/tasks_EPIC_158/08_phase8_plan.md]: Execute parameterized Tier 7 describe-architecture command: `/tier7-describe-architecture [NEW] @[docs/epic/EPIC_158_tracker.md] @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md] @[ki_structured_forensic_quotes.md] @[ki_topological_engine.md] @[ki_unified_matrix_scoring_strictness.md] @[ki_prompt_orchestration_and_matrix_evaluation.md]`.</action>
    <action>Verify synchronization of target KIs: `ki_structured_forensic_quotes.md`, `ki_topological_engine.md`, `ki_unified_matrix_scoring_strictness.md`, and `ki_prompt_orchestration_and_matrix_evaluation.md`.</action>
    <action>Verify synchronization of timeless architecture pillars in present tense without historical or phase language: `01_system_context_and_invariants.md`, `03_cognitive_orchestration_engine.md`, and `04_server_driven_ui_and_presentation.md`.</action>
    <action>Assert all 4 target KIs updated with accurate `metadata.json` timestamps and clean syntax.</action>
    <constraint invariant="dual_axis_documentation_mandate">Synchronize target KIs, directory references, and architecture pillars without manual direct editing of pillars during coding workflows.</constraint>
  </step>

  <test_contracts>
    <test name="test_tiede_latex_syntax_validity" category="positive">
      <input>Scan docs/tiede.md for balanced math environments, bracket pairs, and equation tags</input>
      <expected>All math formulas, theorems, and definitions render cleanly without syntax errors</expected>
    </test>
    <test name="test_tiede_unbalanced_math_detector_negative" category="negative">
      <input>Inject unbalanced LaTeX math delimiter into temporary copy of docs/tiede.md</input>
      <expected>Syntax verification tool detects unbalanced delimiter and raises validation failure</expected>
    </test>
    <test name="test_directory_reference_drift_detector_negative" category="negative">
      <input>Verify detection of missing test file or unindexed DTO in .agents/rules/04_directory_reference.md</input>
      <expected>Directory audit script flags unindexed integration test or missing DTO reference</expected>
    </test>
    <test name="test_decoupled_strictness_parameter_regression_negative" category="negative">
      <input>Verify rejection if Workflow or Studio DTO attempts to couple lexical and scoring strictness</input>
      <expected>Pydantic validation enforces separate sovereign fields with independent bounds [0, 100]</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Verify all 4 target KIs updated with valid `metadata.json` timestamps.</action>
    <action>Verify `docs/tiede.md` equations and empirical tables render cleanly.</action>
    <action>Verify `docs/architecture/` documents contain zero historical progression terms, phase names, or Epic IDs.</action>
    <action>Verify `.agents/rules/04_directory_reference.md` reflects physical repository state.</action>
  </validation_gate>
</execution_protocol>
```
