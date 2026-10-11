# Phase 7: Global Quality Gate & Final Verification

**Overview:** Execute Quorum's complete quality gate verification pipeline across all Python backend, Flutter client, AST guardrail, Theme Sovereignty, dictionary eradication, and Markdown boundary standards. Execute `scripts/backend_audit_loop.py` with strict AST and pytest validation, run `scripts/flutter_audit_loop.py` with the Freezed build runner, run `scripts/audit_flutter_theme_sovereignty.py` asserting zero raw colors or naked TextStyles, verify AST guardrail compliance via `scripts/_ast_guardrails.py` and `scripts/audit_dict_eradication.py`, execute markdown boundary auditing on all documents, and perform the live E2E REST API integration gate.

**Source:** @[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md] Section 3, Phase 7: Global Quality Gate & Final Verification

**Target Files:**
- `[VALIDATION] @[scripts/backend_audit_loop.py]`
- `[VALIDATION] @[scripts/flutter_audit_loop.py]`
- `[VALIDATION] @[scripts/audit_flutter_theme_sovereignty.py]`
- `[VALIDATION] @[scripts/_ast_guardrails.py]`
- `[VALIDATION] @[scripts/audit_dict_eradication.py]`
- `[VALIDATION] @[scripts/audit_markdown_boundaries.py]`
- `[VALIDATION] @[backend_v2/tests/integration/test_integration_real_llm.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[scripts/backend_audit_loop.py]`, `@[scripts/flutter_audit_loop.py]` | Skipping automated audit loops or claiming changes are too small to test. | Execute full automated audit testing: `backend_audit_loop.py` with Ruff, MyPy, and Pytest, and `flutter_audit_loop.py` with Freezed build runner. | Manual manual-only testing checklists without deterministic tooling. | Zero non-zero exit codes across both audit loops. |
| `@[scripts/audit_flutter_theme_sovereignty.py]` | Hardcoded hex colors, raw `Color(0x...)`, `Colors.*`, or naked `TextStyle(...)`. | 100% Theme Sovereignty: all colors derive from `Theme.of(context).colorScheme` or `AppSemanticColors`, typography from `Theme.of(context).textTheme`. | Permissive visual linting suppressions. | `audit_flutter_theme_sovereignty.py` exits 0 with 0 findings. |
| `@[scripts/_ast_guardrails.py]`, `@[scripts/audit_dict_eradication.py]` | Naked dictionaries in state transit, raw dict fixtures violating `QGR029`. | AST strict guardrail enforcement: zero naked dictionaries, Pydantic `extra='forbid'`, and Polyfactory fixtures. | Advisory-only warning suppressions. | Static AST scanners exit 0. |
| `@[scripts/audit_markdown_boundaries.py]` | Ambiguous documentation ("e.g.", "etc.", "such as", "like"), truncated XML blocks, broken AST bounds. | 100% compliance with MBD001-MBD009 markdown boundary rules. | Informal plan prose. | `audit_markdown_boundaries.py` exits 0 across all plan files. |
| `@[backend_v2/tests/integration/test_integration_real_llm.py]` | Untested live LLM API pipelines. | Execute final Live E2E REST API Verification Gate with `$env:RUN_LIVE_E2E="true"`. | Mock-only verification of real LLM parsing. | Pytest exits 0 for live E2E run. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 6. Verify all implementation and test files exist and pass localized unit tests.</action>
    <action>Look forward: Verify if all global completion gates, Theme Sovereignty, and AST guardrails pass 100% before closing Epic 154.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]) and the Tracker document (@[docs/epic/EPIC_154_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_154/07_phase7_plan.md] @[docs/epic/EPIC_154_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>backend_audit_loop.py passes 100% across all touched backend files with --test and --ast-strict.</item>
    <item>flutter_audit_loop.py passes 100% across client with --build.</item>
    <item>audit_flutter_theme_sovereignty.py passes 100% across client_app_v2 verifying zero raw colors or naked TextStyles.</item>
    <item>_ast_guardrails.py passes 100% verifying QGR029 Polyfactory fixture compliance and zero naked dicts.</item>
    <item>audit_dict_eradication.py passes 100% verifying zero naked dicts across all causal DTOs.</item>
    <item>audit_markdown_boundaries.py passes 100% on EPIC_154_Dynamic_Causal_Discovery_Engine.md and all plan files.</item>
    <item>Final Live E2E REST API Verification Gate passes with $env:RUN_LIVE_E2E="true".</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
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
    <forbidden>Do not bypass failing tests with skip markers or test suppression flags.</forbidden>
    <forbidden>Do not suppress AST guardrail errors with noqa comments.</forbidden>
    <forbidden>Do not approve Phase 7 without executing all quality gate scripts.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[scripts/backend_audit_loop.py]</backend>
    <frontend>@[scripts/flutter_audit_loop.py]</frontend>
  </touched_artifacts>

  <step id="7.1" name="BACKEND_AUDIT_EXECUTION">
    <action>In @[scripts/backend_audit_loop.py], execute: uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict. Verify Ruff formatting, MyPy strict typing, clean imports, AST guardrails, and Pytest suites exit with code 0.</action>
    <constraint invariant="backend_audit_execution">Zero tolerance for failing tests or type check violations.</constraint>
  </step>

  <step id="7.2" name="FLUTTER_AUDIT_EXECUTION">
    <action>In @[scripts/flutter_audit_loop.py], execute: uv run python scripts/flutter_audit_loop.py client_app_v2/ --build. Verify Freezed code generation, Flutter analyze, and Flutter test suites exit with code 0.</action>
    <constraint invariant="flutter_audit_execution">Build runner must generate Freezed models cleanly with zero unrecognized key failures.</constraint>
  </step>

  <step id="7.3" name="THEME_SOVEREIGNTY_VERIFICATION">
    <action>In @[scripts/audit_flutter_theme_sovereignty.py], execute: uv run python scripts/audit_flutter_theme_sovereignty.py client_app_v2/. Verify zero raw Color(0x...), Colors.*, or naked TextStyle(...) violations in SduiCausalGraphWidget, CausalInspectorModal, or any other widget.</action>
    <constraint invariant="theme_sovereignty">All colors and typography derive from Theme.of(context).</constraint>
  </step>

  <step id="7.4" name="AST_GUARDRAIL_AND_FIXTURE_AUDIT">
    <action>In @[scripts/_ast_guardrails.py], execute: uv run python scripts/_ast_guardrails.py. Verify QGR029 Polyfactory fixture compliance and zero naked dictionary violations across all new and modified Python files.</action>
    <constraint invariant="the_zero_compromise_pledge">Zero naked dictionaries in state transit or test fixtures.</constraint>
  </step>

  <step id="7.5" name="DICTIONARY_ERADICATION_AUDIT">
    <action>In @[scripts/audit_dict_eradication.py], execute: uv run python scripts/audit_dict_eradication.py. Verify zero naked dictionaries across backend_v2/models/dtos/causal_discovery.py and all orchestrator engines.</action>
    <constraint invariant="the_zero_compromise_pledge">All transit payloads must be strictly typed Pydantic V2 DTOs.</constraint>
  </step>

  <step id="7.6" name="MARKDOWN_BOUNDARY_AUDITING">
    <action>In @[scripts/audit_markdown_boundaries.py], execute: uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md. Verify zero MBD001-MBD009 boundary or ambiguity violations across the parent Epic and all generated plan files in docs/epic/tasks_EPIC_154/.</action>
    <constraint invariant="anti_ambiguity_mandate">Zero ambiguous language or malformed XML tags in markdown documents.</constraint>
  </step>

  <step id="7.7" name="FINAL_LIVE_E2E_REST_API_VERIFICATION_GATE">
    <action>In @[backend_v2/tests/integration/test_integration_real_llm.py], if LIVE credentials are configured, execute the final Live E2E REST API Verification Gate: $env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py.</action>
    <constraint invariant="universal_fail_fast">Live LLM execution verifies end-to-end extraction and causal discovery pipeline.</constraint>
  </step>

  <test_contracts>
    <test name="test_backend_audit_loop_exits_zero" category="positive">
      <input>uv run python scripts/backend_audit_loop.py backend_v2/ --test</input>
      <expected>exit code 0</expected>
    </test>
    <test name="test_flutter_audit_loop_exits_zero" category="positive">
      <input>uv run python scripts/flutter_audit_loop.py client_app_v2/ --build</input>
      <expected>exit code 0</expected>
    </test>
    <test name="test_theme_sovereignty_audit_exits_zero" category="positive">
      <input>uv run python scripts/audit_flutter_theme_sovereignty.py client_app_v2/</input>
      <expected>exit code 0, 0 violations</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/ --test</action>
    <action>Execute: uv run python scripts/flutter_audit_loop.py client_app_v2/ --build</action>
    <action>Execute: uv run python scripts/audit_flutter_theme_sovereignty.py client_app_v2/</action>
  </validation_gate>
</execution_protocol>
