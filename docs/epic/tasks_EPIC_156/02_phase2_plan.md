# Phase 2: Test Suite Mock Eradication, Fake Repository Parity & Concurrency Stress Gate (QGR014)

**Overview:** Audit and enhance in-memory repository fakes, batch refactor all unit and integration test fixtures across `backend_v2/tests/` to eliminate 319 deceptive `AsyncMock` and `MagicMock` instances under QGR014, promote QGR014 to FATAL severity in `scripts/_ast_guardrails.py`, and implement the automated async concurrency stress test suite.

**Target Files:**
- `[MODIFY]` `@[backend_v2/tests/fakes/in_memory_repositories.py]`
- `[MODIFY]` `@[scripts/_ast_guardrails.py]`
- `[NEW]` `@[backend_v2/tests/unit/orchestrator/test_concurrency_stress.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/workers/test_execution_worker.py]`
- `[MODIFY]` `@[backend_v2/tests/integration/test_e2e_orchestration.py]`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 1 established QGR024, QGR025, clean imports, and the 8-stage audit loop, reducing warnings to 1,208 and achieving 0 FATAL errors in domain code.</action>
    <action>Look forward: Verify that enhancing in-memory fakes provides complete functional replacements for all 319 QGR014 mock occurrences across tests before QGR014 is locked to FATAL severity.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_156_Universal_AST_Strictness_and_Advisory_Warning_Eradication.md]) and the Tracker document (@[docs/epic/EPIC_156_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_156/02_phase2_plan.md] @[docs/epic/EPIC_156_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>In-memory repository fakes in backend_v2/tests/fakes/in_memory_repositories.py fully implement all repository interfaces with snapshot isolation and deterministic fault injection.</item>
    <item>All 319 QGR014 deceptive mock occurrences across backend_v2/tests/ replaced with stateful In-Memory fakes.</item>
    <item>QGR014 promoted to FATAL severity in scripts/_ast_guardrails.py with 0 violations across backend_v2/tests/.</item>
    <item>Total codebase warnings reduced from 1,208 to 889 warnings.</item>
    <item>Concurrency stress test suite implemented in backend_v2/tests/unit/orchestrator/test_concurrency_stress.py running 50+ concurrent atoms with zero deadlocks.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Domain service duct-tape cleanups under QGR020, QGR012, QGR016, QGR002 (quarantined for Phase 3).</anti_target>
    <anti_target>Inverting default audit loop strictness flag (quarantined for Phase 4).</anti_target>
    <anti_target>Database container dependencies for unit tests: use pure in-memory stateful fakes exclusively.</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[scripts/_ast_guardrails.py]</backend>
  </touched_artifacts>

  <step id="2.1" name="Audit and Enhance In-Memory Repository Fakes">
    <action>In `@[backend_v2/tests/fakes/in_memory_repositories.py]`, inspect and verify `InMemoryWorkflowRepository`, `InMemoryExecutionRecordRepository`, `InMemoryOutputProfileRepository`, and `InMemorySystemSettingsRepository`.</action>
    <action>Ensure full implementation of all methods defined in `IRepository` contracts with thread-safe dictionary stores, snapshot isolation, and deterministic `inject_fault(method_name, exception)` support.</action>
    <constraint invariant="deceptive_persistence_mocking_ban">Fakes MUST simulate genuine persistence roundtrips, Pydantic schema validation, and state mutations.</constraint>
  </step>

  <step id="2.2" name="Batch Refactor Unit and Integration Test Fixtures">
    <action>Batch A: In `backend_v2/tests/unit/services/`, replace `AsyncMock(spec=...)` and `MagicMock()` fixtures with instantiated in-memory repository fakes.</action>
    <action>Batch B: In `backend_v2/tests/unit/orchestrator/` and `backend_v2/tests/unit/workers/`, replace repository mocks with clean dependency injection of in-memory fakes.</action>
    <action>Batch C: In `backend_v2/tests/integration/`, replace mock-based setup fixtures with stateful in-memory fakes.</action>
    <action>Batch D: Purge `@patch` decorators targeting repository interfaces across all test modules.</action>
    <constraint invariant="the_zero_compromise_pledge">Zero tolerance for deceptive green tests that bypass persistence verification.</constraint>
  </step>

  <step id="2.3" name="Promote QGR014 to FATAL Severity">
    <action>In `@[scripts/_ast_guardrails.py]`, update the visitor method for QGR014 to unconditionally assign FATAL severity.</action>
    <action>Execute AST guardrails across `backend_v2/tests`: verify 0 violations of QGR014.</action>
    <action>Verify total codebase warning count drops from 1,208 to 889 warnings.</action>
    <constraint invariant="neuro_symbolic_grounding_mandate">Prove mock eradication mathematically through AST verification.</constraint>
  </step>

  <step id="2.4" name="Implement Concurrency Stress Test Suite">
    <action>Create [NEW] `@[backend_v2/tests/unit/orchestrator/test_concurrency_stress.py]` implementing an automated high-concurrency stress harness.</action>
    <action>Spawn 50+ concurrent atom simulations executing within managed `asyncio.TaskGroup` contexts.</action>
    <action>Simulate high-frequency memory-state updates, verifying zero deadlocks, zero lock starvation, and deterministic state transitions.</action>
    <constraint invariant="system_concurrency_ssot">Managed TaskGroup execution must maintain lock integrity under high load.</constraint>
  </step>

  <test_contracts>
    <test name="test_in_memory_workflow_repo_persistence_roundtrip" category="positive">
      <input>Save workflow to InMemoryWorkflowRepository, then get_by_id</input>
      <expected>Returns exact domain model with updated state</expected>
    </test>
    <test name="test_in_memory_repo_fault_injection" category="error_path">
      <input>Configure inject_fault('save', DatabaseConnectionError()), then call save</input>
      <expected>Raises DatabaseConnectionError deterministically</expected>
    </test>
    <test name="test_qgr014_asyncmock_on_repo_raises_fatal" category="positive">
      <input>Test file with repo = AsyncMock(spec=IWorkflowRepository)</input>
      <expected>QuorumGuardrailVisitor emits FATAL violation for QGR014</expected>
    </test>
    <test name="test_concurrency_stress_50_atoms_no_deadlock" category="boundary">
      <input>50 concurrent simulated atom tasks in asyncio.TaskGroup</input>
      <expected>All 50 tasks complete successfully with zero deadlocks</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute QGR014 verification: `uv run python scripts/_ast_guardrails.py backend_v2/tests --strict`</action>
    <action>Execute full test suite in touched domains: `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py backend_v2/tests/unit/orchestrator/test_concurrency_stress.py`</action>
    <action>Execute warning baseline ledger: `uv run python scripts/audit_warning_baseline.py` (Assert: 0 FATAL errors, total warnings &lt;= 889)</action>
    <action>Execute 8-stage audit loop on test fakes: `uv run python scripts/backend_audit_loop.py backend_v2/tests/fakes/in_memory_repositories.py --test`</action>
  </validation_gate>
</execution_protocol>
```
