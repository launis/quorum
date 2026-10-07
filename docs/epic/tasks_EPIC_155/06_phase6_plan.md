# Phase 6: Comprehensive Quality Gates & Regression Verification

**Overview:** Execute comprehensive two-stage backend audit loops, verify Flutter client build and test suite integrity, audit markdown boundary preservation across all documentation artifacts, and execute the mandatory live LLM end-to-end integration test to prove zero real-world regression in graph evaluation and matrix synthesis.

**Source:** @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md#L191-L202] Phase 6: Comprehensive Quality Gates & Regression Verification

**Target Files:**
- `[MODIFY]` @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| Whole repository test gates | "Fake Green" localized testing without global verification. Skipping Flutter client validation when backend status sequences change. | Two-Stage Testing Pipeline: Localized audit loop followed by global completion gate across backend and Flutter client. Mandatory live real LLM E2E verification. | Zero speculative test skipping; full automated regression gate. | `backend_audit_loop.py backend_v2/ --test`, `flutter_audit_loop.py client_app_v2/ --build`, and live E2E real LLM test pass 100%. |

## Pre-Implementation Cleanups

1. `[CLEANUP]` Ensure Phases 1 through 5 are committed and passing.
2. `[CLEANUP]` Verify working directory is clean (`git status`) before executing completion gates.

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 5. Verify all engines, sub-executors, strategies, and orchestrators are decoupled from in-memory concurrency primitives.</action>
    <action>Look forward: Verify that the physical codebase compiles cleanly across both Python and Flutter surfaces and passes full-scale automated and live E2E validation gates.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md]) and the Tracker document (@[docs/epic/EPIC_155_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_155/06_phase6_plan.md] @[docs/epic/EPIC_155_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>Localized backend audit loop passes on all touched orchestrator modules with --ast-strict.</item>
    <item>Global completion gate uv run python scripts/backend_audit_loop.py backend_v2/ --test passes 100%.</item>
    <item>Client completion gate uv run python scripts/flutter_audit_loop.py client_app_v2/ --build passes 100%.</item>
    <item>audit_markdown_boundaries.py verifies docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md with zero findings.</item>
    <item>Live real LLM E2E integration test passes with $env:RUN_LIVE_E2E="true".</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT modify domain code or Pydantic models during Phase 6 (verification-only phase).</anti_target>
    <anti_target>Do NOT bypass or skip failing tests with @pytest.mark.skip or xfail.</anti_target>
  </anti_targets>

  <touched_artifacts>
  </touched_artifacts>

  <test_contracts>
    <test name="test_e2e_real_llm_execution_succeeds" category="positive">
      <input>Real LLM integration test payload via test_integration_real_llm.py</input>
      <expected>full workflow execution succeeds end-to-end with valid SDUI report generation</expected>
    </test>
    <test name="test_markdown_boundaries_zero_violations" category="boundary">
      <input>EPIC_155_Engine_Concurrency_Decoupling.md markdown AST</input>
      <expected>audit_markdown_boundaries.py returns exit code 0 with 0 findings</expected>
    </test>
  </test_contracts>

  <step id="6.1" name="EXECUTE_GLOBAL_QUALITY_GATE">
    <action>Stage 1 (localized): Execute `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/engine.py backend_v2/services/orchestrator/engines/ backend_v2/services/orchestrator/strategies/ backend_v2/services/orchestrator/two_pass_atomizer.py backend_v2/services/orchestrator/enriched_dag_executor.py backend_v2/services/orchestrator/sliding_window_linker.py backend_v2/services/orchestrator/dag_executor.py --test --ast-strict` to verify Ruff formatting, strict MyPy typing, AST guardrails, and localized Pytest passing.</action>
    <action>Stage 2 (global completion gate): Execute `uv run python scripts/backend_audit_loop.py backend_v2/ --test` followed by `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` to prove zero cross-domain regressions (the Flutter client consumes `ExecutionStatus` values whose emission sequence changes in Step 5.3).</action>
  </step>

  <step id="6.2" name="EXECUTE_MARKDOWN_BOUNDARIES_AUDIT">
    <action>Execute `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md` to ensure markdown reference integrity.</action>
  </step>

  <step id="6.3" name="EXECUTE_MANDATORY_LIVE_E2E_VERIFICATION">
    <action>Execute `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py` (or on Linux/macOS: `RUN_LIVE_E2E=true uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`) to confirm zero regressions in live end-to-end execution.</action>
  </step>

  <validation_gate>
    <action>Assert exit code 0 from uv run python scripts/backend_audit_loop.py backend_v2/ --test</action>
    <action>Assert exit code 0 from uv run python scripts/flutter_audit_loop.py client_app_v2/ --build</action>
    <action>Assert exit code 0 from uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md</action>
    <action>Assert exit code 0 from live E2E real LLM test</action>
  </validation_gate>
</execution_protocol>
```
