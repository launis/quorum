# Phase 6: Comprehensive Quality Gates & Regression Verification

**Overview:** Execute comprehensive two-stage backend audit loops, verify Flutter client build and test suite integrity, audit markdown boundary preservation across all documentation artifacts, and execute the mandatory live LLM end-to-end integration test to prove zero real-world regression in graph evaluation and matrix synthesis.

**Source:** @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md#L348-L359] Phase 6: Comprehensive Quality Gates & Regression Verification

**Target Files:**
- `[MODIFY]` @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md] | Stale pre-implementation AST line boundaries (`#Lnn-mm`) left un-synchronized across phases; ignoring MBD004 findings. | AST-exact markdown line boundary synchronization across all 7 phases, ensuring `audit_markdown_boundaries.py` passes with zero violations. | Zero manual line counting; programmatic synchronization via physical AST inspection and `audit_markdown_boundaries.py`. | `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md` exits with code 0 and 0 findings. |
| Localized Decoupled Subsystem (`@[backend_v2/models/dtos/engine.py]`, `@[backend_v2/services/orchestrator/dag_executor.py]`) | Running generic pytest without strict AST guardrails or skipping formatting and typecheck audits on modified files. | Stage 1 localized audit loop enforcing Ruff formatting, strict MyPy typing, AST guardrail rules (QGR000-QGR027), and localized Pytest pass. | Targeted audit loop without running slow unrelated test modules during localized check. | `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/engine.py backend_v2/services/orchestrator/engines/ backend_v2/services/orchestrator/strategies/ backend_v2/services/orchestrator/two_pass_atomizer.py backend_v2/services/orchestrator/enriched_dag_executor.py backend_v2/services/orchestrator/sliding_window_linker.py backend_v2/services/orchestrator/dag_executor.py --test --ast-strict` passes 100%. |
| Concurrency Bounds & Fuzzer Regression (`@[backend_v2/tests/unit/test_concurrency_fuzzer.py]`) | "Fake Green" passing of concurrency tests without running Stage A upper bound verification and Stage B dynamic semaphore pool limit assertions. | Strict execution of Stage A and Stage B concurrency fuzzer test suites asserting peak concurrent calls adhere to `LiteLLMProvider` dynamic semaphore pool SSOT across [1, 2, 5, 10] partitions. | Reuse existing fuzzer suites without writing redundant mock harnesses. | `uv run pytest backend_v2/tests/unit/test_concurrency_fuzzer.py backend_v2/tests/unit/test_ast_concurrency_guardrails.py -v` exits with code 0. |
| Full Backend & Flutter Client Completion Gate (`backend_v2/`, `client_app_v2/`) | Declaring phase completion without full-suite regression testing; skipping Flutter build when backend step state machine transitions (Step 5.3 synchronous `RUNNING`) changed. | Full Two-Stage global completion gate: 5,085+ backend tests with >=90% line coverage and complete Flutter build with zero Freezed or compilation regressions. | Standardized global audit scripts (`backend_audit_loop.py`, `flutter_audit_loop.py`) without custom wrappers. | `uv run python scripts/backend_audit_loop.py backend_v2/ --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` exit with code 0. |
| Live Real LLM E2E Integration Pipeline (`@[backend_v2/tests/integration/test_integration_real_llm.py]`) | Relying solely on mocked LLM fixtures without testing live network execution, real DAG decomposition, atom evaluation, and matrix report generation against external providers. | Live E2E test execution with `$env:RUN_LIVE_E2E="true"` testing real PDF ingestion, FastAPI request handling, Arq background worker DAG processing, and report generation to `PASSED` status. | Zero custom E2E scripts; utilize standardized `test_integration_real_llm.py` with automated TcpFakeServer / uvicorn / Arq worker bootstrap. | `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py -v` exits with code 0. |

## Pre-Implementation Cleanups

1. `[CLEANUP]` Ensure Phases 1 through 5 are committed and passing with zero uncommitted changes (`git status`).
2. `[CLEANUP]` Verify ports 8000 and 6379 are not locked by dangling background processes prior to running live E2E testing.
3. `[CLEANUP]` Verify required test PDF fixtures (`keskusteluhistoria.pdf`, `lopputuote.pdf`, `reflektiodokumentti.pdf`) exist in `docs/jwdatat/`.

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
    <item>Stage A and Stage B concurrency fuzzer test suites in test_concurrency_fuzzer.py pass 100% verifying provider semaphore SSOT limits.</item>
    <item>Global completion gate uv run python scripts/backend_audit_loop.py backend_v2/ --test passes 100% with >=90% test coverage.</item>
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
    <test name="test_concurrency_fuzzer_rejects_zero_limit" category="negative">
      <input>Setting semaphore limit to 0 or exceeding provider pool</input>
      <expected>Pydantic ValidationError or Fail-Fast AppException(ErrorCodes.VALIDATION_FAILED)</expected>
    </test>
    <test name="test_markdown_boundaries_detects_mismatched_lines" category="negative">
      <input>Markdown document with outdated line bound reference</input>
      <expected>audit_markdown_boundaries.py returns exit code 1 with MBD004 fatal finding</expected>
    </test>
  </test_contracts>

  <step id="6.1" name="EXECUTE_GLOBAL_QUALITY_GATE">
    <action>Stage 1 (localized): Execute `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/engine.py backend_v2/services/orchestrator/engines/ backend_v2/services/orchestrator/strategies/ backend_v2/services/orchestrator/two_pass_atomizer.py backend_v2/services/orchestrator/enriched_dag_executor.py backend_v2/services/orchestrator/sliding_window_linker.py backend_v2/services/orchestrator/dag_executor.py --test --ast-strict` and `uv run pytest backend_v2/tests/unit/test_concurrency_fuzzer.py backend_v2/tests/unit/test_ast_concurrency_guardrails.py -v` targeting @[backend_v2/models/dtos/engine.py], @[backend_v2/services/orchestrator/dag_executor.py], and @[backend_v2/tests/unit/test_concurrency_fuzzer.py] to verify Ruff formatting, strict MyPy typing, AST guardrails, and localized Pytest passing.</action>
    <action>Stage 2 (global completion gate): Execute `uv run python scripts/backend_audit_loop.py backend_v2/ --test` followed by `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` targeting `backend_v2/` and `client_app_v2/` to prove zero cross-domain regressions (the Flutter client consumes `ExecutionStatus` values whose emission sequence changes in Step 5.3).</action>
  </step>

  <step id="6.2" name="EXECUTE_MARKDOWN_BOUNDARIES_AUDIT">
    <action>In @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md], synchronize all shifted AST line boundaries resulting from Phase 1 through Phase 5 code modifications to match physical ClassDef and FunctionDef spans across the codebase.</action>
    <action>Execute `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md` targeting @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md] to ensure markdown reference integrity with 0 findings.</action>
  </step>

  <step id="6.3" name="EXECUTE_MANDATORY_LIVE_E2E_VERIFICATION">
    <action>Execute `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py -v` targeting @[backend_v2/tests/integration/test_integration_real_llm.py] (or on Linux/macOS: `RUN_LIVE_E2E=true uv run pytest backend_v2/tests/integration/test_integration_real_llm.py -v`) to confirm zero regressions in live end-to-end execution.</action>
  </step>

  <validation_gate>
    <action>Assert exit code 0 from uv run python scripts/backend_audit_loop.py backend_v2/ --test</action>
    <action>Assert exit code 0 from uv run python scripts/flutter_audit_loop.py client_app_v2/ --build</action>
    <action>Assert exit code 0 from uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md</action>
    <action>Assert exit code 0 from live E2E real LLM test backend_v2/tests/integration/test_integration_real_llm.py</action>
  </validation_gate>
</execution_protocol>
```
