<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

# Phase 4: Verification & E2E Integration Gate

**Overview:** Execute comprehensive unit, ISTQB Boundary Value Analysis (BVA), Equivalence Partitioning (`heterogeneous_payload_testing_mandate`), AST guardrail verification (`@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`), Cross-Domain SDUI Semantic Parity (`@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`), Touched-Scope + 1-Hop Technical Debt verification (`scripts/audit_technical_debt.py`), and the mandatory live E2E REST API verification gate (`@[backend_v2/tests/integration/test_integration_real_llm.py]`).

**Source:** @[docs/epic/EPIC_161_topological_synthesis_cohesion.md#L206-L229] Phase 4: Verification & E2E Integration Gate

**Target Files:**
- `[MODIFY] @[backend_v2/tests/integration/test_sdui_semantic_parity.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
- `[MODIFY] @[backend_v2/tests/integration/test_integration_real_llm.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`** | Eradicate untested cross-domain fields between Backend SDUI DTOs (`SduiMatrixSummaryTableBlock`, `SduiCausalGraphBlock`), Jinja2 PDF templates (`report_template.jinja2`), and Flutter Freezed models (`sdui_block_dto.dart`). | Assert 1:1 semantic parity for `short_circuited_by_claims` and `falsified_warrant_claims` across Python SDUI blocks, rendered Jinja2 HTML/PDF output, and Dart Freezed serialization in `@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`. | Reuse the existing tripartite parity test harness in `test_sdui_semantic_parity.py` without building duplicate test runners. | `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`. |
| **`@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`** | Eradicate regression risk of raw `if type(content) is dict:` checks returning in `blueprint.py`, bare claim-title deficit flattening returning in `matrix_explanation_service.py`, or hardcoded clipper magic numbers returning outside `settings.py`. | Verify AST guardrail enforcement in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` and zero technical debt across all touched files and 1-hop callers via `scripts/audit_technical_debt.py`. | Rely on the centralized `scripts/_ast_guardrails.py` and `scripts/audit_technical_debt.py` verifiers. | `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py`. |
| **`@[backend_v2/tests/integration/test_integration_real_llm.py]`** | Eradicate closing an Epic without verifying live end-to-end topological synthesis cohesion, [NEW] `MatrixFailureDeficitDTO`, and [NEW] `CausalSynthesisBriefDTO` defined in `@[backend_v2/models/dtos/synthesis.py]` under real LLM execution. | Assert full pipeline completion and topological synthesis cohesion in `@[backend_v2/tests/integration/test_integration_real_llm.py]` and execute the global backend and Flutter audit loops. | Execute against the canonical live E2E integration test suite. | `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phases 1, 2, and 3 are 100% complete and committed in @[docs/epic/EPIC_161_tracker.md].</action>
    <action>Look forward: Read @[backend_v2/tests/integration/test_sdui_semantic_parity.py], @[backend_v2/tests/unit/scripts/test_ast_guardrails.py], and @[backend_v2/tests/integration/test_integration_real_llm.py].</action>
    <constraint invariant="fragmented_quality_gates_prevention">Execute both isolated integration suites and the global completion gates (`backend_audit_loop.py backend_v2/ --test` and `flutter_audit_loop.py client_app_v2/ --build`).</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_161_topological_synthesis_cohesion.md] and @[docs/epic/EPIC_161_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_161/04_phase4_plan.md] @[docs/epic/EPIC_161_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/tests/integration/test_sdui_semantic_parity.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</backend>
    <backend>@[backend_v2/tests/integration/test_integration_real_llm.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>Cross-Domain SDUI Semantic Parity suite (`@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`) updated and passing 100% for `short_circuited_by_claims` and `falsified_warrant_claims` across Python, Jinja2 PDF, and Flutter Freezed models.</item>
    <item>AST guardrail test suite (`@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`) and touched-scope technical debt auditor (`scripts/audit_technical_debt.py`) passing with 0 violations.</item>
    <item>Global Backend Quality Gate (`scripts/backend_audit_loop.py backend_v2/ --test`) and Global Flutter Quality Gate (`scripts/flutter_audit_loop.py client_app_v2/ --build`) passing 100%.</item>
    <item>Live E2E REST API verification gate (`@[backend_v2/tests/integration/test_integration_real_llm.py]`) passing 100%.</item>
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
    <anti_target>Do NOT add `@pytest.mark.skip` or comment out failing tests (`anti_test_skipping_mandate`).</anti_target>
    <anti_target>Do NOT write tautological mocks (`tautological_mocking_ban`) or global stdlib root patches (`scoped_mock_and_fault_isolation_mandate`).</anti_target>
  </anti_targets>

  <demolish>
    <item target="@[backend_v2/tests/integration/test_sdui_semantic_parity.py]">Eradicate any legacy test fixtures assuming disembodied bottom-of-report `SduiNACard` placement for inline matrix row short-circuits.</item>
  </demolish>

  <step id="4.1" name="Cross-Domain SDUI Semantic Parity &amp; Heterogeneous Payload Verification">
    <action>In @[backend_v2/tests/integration/test_sdui_semantic_parity.py], add parity assertions verifying that `short_circuited_by_claims` and `falsified_warrant_claims` serialize identically across Backend `SduiMatrixSummaryTableBlock` / `SduiCausalGraphBlock`, Jinja2 `report_template.jinja2` PDF output, and Flutter `sdui_block_dto.dart` Freezed models.</action>
    <constraint invariant="heterogeneous_payload_testing_mandate">Verify all 4 ISTQB Equivalence Partitions (structured JSON/DTO, list collections, pure string/markdown, and scalars/falsy inputs) across `SynthesisPayloadCompressor` and SDUI mappers.</constraint>
    <audit_command>uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py</audit_command>
  </step>

  <step id="4.2" name="AST Guardrail &amp; Touched-Scope Technical Debt Verification">
    <action>In @[backend_v2/tests/unit/scripts/test_ast_guardrails.py], add regression assertions verifying zero `if type(content) is dict:` checks in `blueprint.py` and full AST guardrail compliance across all modified orchestrator, worker, and SDUI modules.</action>
    <action>Execute the Touched-Scope + 1-Hop Technical Debt Auditor across all modified subsystems.</action>
    <constraint invariant="ast_guardrail_mandate">Zero QGR or DGR guardrail violations across the entire repository.</constraint>
    <audit_command>uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py</audit_command>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets backend_v2/services/orchestrator/ backend_v2/services/sdui/ backend_v2/services/blueprint.py backend_v2/services/web_fetcher.py backend_v2/hooks/archival.py backend_v2/workers/ --include-one-hop</audit_command>
  </step>

  <step id="4.3" name="Mandatory Live E2E REST API Verification Gate">
    <action>In @[backend_v2/tests/integration/test_integration_real_llm.py], verify end-to-end execution of topological synthesis cohesion ([NEW] `MatrixFailureDeficitDTO` and [NEW] `CausalSynthesisBriefDTO` defined in @[backend_v2/models/dtos/synthesis.py], zero-loss Micro-CoT reasoning and quote retention, and inline SDUI short-circuit lineage) and run the global backend and Flutter completion gates.</action>
    <constraint invariant="zero_tolerance_audit_loop">Both global quality gates (`backend_audit_loop.py` and `flutter_audit_loop.py`) and the live E2E suite must pass 100% before closing Phase 4.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test</audit_command>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build</audit_command>
    <audit_command>$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py</audit_command>
  </step>

  <test_contracts>
    <test name="test_sdui_semantic_parity_short_circuit_and_toulmin_fields_match_across_python_jinja_dart" category="positive">
      <input>Full ReportDataDTO with populated short_circuited_by_claims and falsified_warrant_claims</input>
      <expected>100% field and value parity across Python SDUI DTOs, rendered Jinja2 HTML, and Dart Freezed model keys</expected>
    </test>
    <test name="test_sdui_semantic_parity_missing_template_binding_fails_fast" category="negative">
      <input>Simulated unrendered SDUI field on SduiMatrixSummaryTableBlock</input>
      <expected>Parity assertion raises AssertionError</expected>
    </test>
    <test name="test_ast_guardrails_rejects_raw_type_is_dict_in_blueprint" category="negative">
      <input>AST snippet containing `if type(content) is dict:`</input>
      <expected>Flagged as fatal AST guardrail violation</expected>
    </test>
    <test name="test_integration_real_llm_preserves_topological_deficits_and_causal_brief" category="positive">
      <input>Live E2E workflow execution with topological dependencies and matrix evaluation</input>
      <expected>Completed report contains synthesized row explanations, XAI highlights, and SDUI blocks reflecting resolved causal chains and full deficits within the 300,000-char ceiling</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run SDUI Semantic Parity and AST Guardrail suites: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py backend_v2/tests/unit/scripts/test_ast_guardrails.py`.</action>
    <action>Run Global Backend Audit Loop: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`.</action>
    <action>Run Global Flutter Audit Loop: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
    <action>Run Live E2E REST API Verification Gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.</action>
  </validation_gate>
</execution_protocol>
```
