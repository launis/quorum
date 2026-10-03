# Phase 2: Test Suite Mock Eradication, Fake Repository Parity & Concurrency Stress Gate (QGR014)

**Overview:** Audit and enhance in-memory repository fakes, batch refactor all unit and integration test fixtures across `backend_v2/tests/` to eliminate 319 deceptive `AsyncMock` and `MagicMock` instances under QGR014, promote QGR014 to FATAL severity in `scripts/_ast_guardrails.py`, and implement the automated async concurrency stress test suite.

**Target Files:**
- `[MODIFY]` `@[backend_v2/tests/fakes/in_memory_repositories.py]`
- `[MODIFY]` `@[scripts/_ast_guardrails.py]`
- `[MODIFY]` `@[scripts/audit_warning_baseline.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py]`
- `[NEW]` `@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`
- `[NEW]` `@[backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py]`
- `[MODIFY]` `@[backend_v2/tests/integration/test_epic_chain_e2e.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/workers/test_execution_worker.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_execution.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_report_service.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/execution/test_ingress_service.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/execution/test_override_service.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/execution/test_facade.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_execution_resumability.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_blueprint.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_report_service_synthesis_args.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_execution_render_bug.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/studio/test_workflow_service.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/workers/test_report_worker.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_atom_flattening.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_passivity_hook.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_scoring.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_archival.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_matrix_hook.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_atom_sampling_determinism.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_input_processing.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_worker.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_worker_synthesis.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_dependencies.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_logic.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_finops_telemetry.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_progress.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/test_client.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/test_structured_retry.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_auth.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_concurrency_fuzzer.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_dag_taskgroup.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_llm_context_bounds.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_llm_dependency.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_usage_service.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]`
- `[MODIFY]` `@[backend_v2/tests/test_fastdev_frozen.py]`
- `[MODIFY]` `@[backend_v2/tests/test_worker_models_used.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_matrix_slice_engine.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/tests/fakes/in_memory_repositories.py]` | Duck-typing checks, specifically `hasattr(item.status, "value")`; returning mutable references from storage without deep cloning; unverified in-memory dictionary modifications bypassing Pydantic validation. | Enforce Rust-accelerated snapshot isolation: deep-clone all entities via `type(item).model_validate(item.model_dump(mode="python"), strict=False)` guaranteeing `repo.get(id) is not repo.get(id)` and `repo.get(id) == repo.get(id)`; provide deterministic `inject_fault(method_name, exception, trigger_count)` and scoped async context manager `fault_context()`. | Pruned custom reflection shims and complex transaction managers; rely on dictionary stores with Pydantic deep cloning and typed method signatures. | `uv run pytest backend_v2/tests/unit/fakes/test_in_memory_repositories.py` |
| `@[scripts/_ast_guardrails.py]` | Permissive `WARNING` severity on repository variable assignments (`mock_repo = AsyncMock()`); false-positive substring matching where `"_repo" in target.id` flags non-repository variables, specifically `mock_report` and `mock_report_dto`. | Unconditionally assign FATAL severity to all QGR014 violations (`visit_Call` spec mocks, `@patch` repository targets, and `visit_Assign` mock repository assignments); refine `visit_Assign` to exclude variables containing `"report"` or `"response"` (`and not ("report" in target_id_lower or "response" in target_id_lower)`). | Pruned complex variable-flow tracing; enforce static AST pattern matching on AST Call and Assign nodes. | `uv run python scripts/_ast_guardrails.py backend_v2/tests --strict` |
| `@[scripts/audit_warning_baseline.py]` | Outdated warning ceiling (`CURRENT_WARNING_CEILING = 1254`) allowing warning count to re-inflate; unverified warning count drift. | Update `CURRENT_WARNING_CEILING` to 934, reflecting the eradication of all 319 QGR014 advisory warnings; assert 0 FATAL violations across all 896 backend modules. | Pruned external database backends; lightweight CLI tool reading violations into typed report DTO. | `uv run python scripts/audit_warning_baseline.py` |
| `[NEW] @[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]` | Untested fake repository infrastructure; unverified snapshot isolation; missing fault injection unit coverage. | Comprehensive positive, boundary, and error partition test suite verifying snapshot isolation, CRUD persistence, pre-flight model validation, and deterministic fault injection across all 16 fake repositories. | Pruned redundant test wrappers; test repository fakes directly using native Pydantic domain models. | `uv run pytest backend_v2/tests/unit/fakes/test_in_memory_repositories.py -v` |
| `[NEW] @[backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py]` | Untested async concurrency under high atom loads; risk of race conditions, deadlocks, and zombie tasks in `TaskGroup`. | Spawn 50+ and 100+ concurrent simulated atom tasks within managed `asyncio.TaskGroup` contexts; simulate high-frequency memory-state updates under `_update_lock`; test fault injection triggering clean `ExceptionGroup` cancellation without zombie tasks. | Pruned external mock servers; purely in-memory async concurrency fuzzer testing event loop and lock integrity. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py -v` |
| `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` | Outdated unit test assertions expecting WARNING severity for QGR014 variable assignments; missing false-positive defense assertions. | Update test assertions to assert FATAL severity for `mock_repo = AsyncMock()`; add explicit test case proving `mock_report = MagicMock()` generates 0 violations. | Pruned ad-hoc AST generation; test via `scan_source_code_for_guardrails()`. | `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -k test_qgr014` |
| `@[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py]` | Test fixture expecting ceiling of 1254 instead of updated 934 ceiling. | Update test fixtures and assertions to validate the updated warning ceiling of 934. | Pruned redundant mock configurations; use typed Pydantic DTO instances. | `uv run pytest backend_v2/tests/unit/scripts/test_audit_warning_baseline.py` |
| Batch A: Services Layer (`@[backend_v2/tests/unit/services/test_execution.py]`, `@[backend_v2/tests/unit/services/test_report_service.py]`, `@[backend_v2/tests/unit/services/execution/test_ingress_service.py]`, `@[backend_v2/tests/unit/services/execution/test_override_service.py]`, `@[backend_v2/tests/unit/services/execution/test_facade.py]`, `@[backend_v2/tests/unit/services/test_execution_resumability.py]`, `@[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py]`, `@[backend_v2/tests/unit/services/test_blueprint.py]`, `@[backend_v2/tests/unit/services/test_report_service_synthesis_args.py]`, `@[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]`, `@[backend_v2/tests/unit/services/test_execution_render_bug.py]`, `@[backend_v2/tests/unit/services/studio/test_workflow_service.py]`) | 135 instances of deceptive `AsyncMock()` and `MagicMock()` repository fixtures returning unvalidated dictionaries or passing without real state mutation. | Replace all repository mocks with instantiated in-memory repository fakes (`InMemoryExecutionRepository`, `InMemoryWorkflowRepository`, `InMemoryOutputProfileRepository`, `InMemoryPromptBlockRepository`). | Pruned manual mock return value configurations; save genuine domain models into fakes. | `uv run python scripts/_ast_guardrails.py backend_v2/tests/unit/services/ --strict` |
| Batch B: Orchestrator & Workers Layer (`@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/workers/test_execution_worker.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`, `@[backend_v2/tests/unit/workers/test_report_worker.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`) | 45 instances of `mock_repo = MagicMock()` and `@patch` decorators in orchestrator and worker tests. | Replace repository mocks with dependency injection of `InMemoryUnifiedWorkflowRepository` or instantiated in-memory repository fakes; eliminate all `@patch` decorators targeting repository interfaces. | Pruned multi-layer patch chains; inject unified repository fake into worker and executor contexts. | `uv run python scripts/_ast_guardrails.py backend_v2/tests/unit/services/orchestrator/ backend_v2/tests/unit/workers/ --strict` |
| Batch C: Integration Layer (`@[backend_v2/tests/integration/test_epic_chain_e2e.py]`) | 24 instances of `mock_exec_repo = AsyncMock()`, `mock_workflow_repo = AsyncMock()` in E2E golden master and pipeline tests. | Replace mock repositories with instantiated in-memory repository fakes (`InMemoryExecutionRepository`, `InMemoryWorkflowRepository`, `InMemoryOutputProfileRepository`, `InMemoryPromptBlockRepository`). | Pruned manual mock method wiring; execute full stateful pipeline roundtrip against fakes. | `uv run python scripts/_ast_guardrails.py backend_v2/tests/integration/test_epic_chain_e2e.py --strict` |
| Batch D: Hooks Layer (`@[backend_v2/tests/unit/hooks/test_atom_flattening.py]`, `@[backend_v2/tests/unit/hooks/test_passivity_hook.py]`, `@[backend_v2/tests/unit/hooks/test_scoring.py]`, `@[backend_v2/tests/unit/hooks/test_archival.py]`, `@[backend_v2/tests/unit/hooks/test_matrix_hook.py]`, `@[backend_v2/tests/unit/hooks/test_atom_sampling_determinism.py]`, `@[backend_v2/tests/unit/hooks/test_input_processing.py]`) | 46 instances of mock prompt block and workflow repositories in hook tests. | Replace `mock_pb_repo = AsyncMock()` and `mock_repo = AsyncMock()` with `InMemoryPromptBlockRepository()` and `InMemoryWorkflowRepository()`. | Pruned mock helper methods; pre-populate fakes with strongly typed `PromptBlock` and `Step` fixtures. | `uv run python scripts/_ast_guardrails.py backend_v2/tests/unit/hooks/ --strict` |
| Batch E: Root Unit Tests & LLM Layer (`@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_dependencies.py]`, `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]`, `@[backend_v2/tests/unit/test_logic.py]`, `@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]`, `@[backend_v2/tests/unit/test_finops_telemetry.py]`, `@[backend_v2/tests/unit/test_progress.py]`, `@[backend_v2/tests/unit/llm/test_client.py]`, `@[backend_v2/tests/unit/llm/test_structured_retry.py]`, `@[backend_v2/tests/unit/test_auth.py]`, `@[backend_v2/tests/unit/test_concurrency_fuzzer.py]`, `@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]`, `@[backend_v2/tests/unit/test_dag_taskgroup.py]`, `@[backend_v2/tests/unit/test_llm_context_bounds.py]`, `@[backend_v2/tests/unit/test_llm_dependency.py]`, `@[backend_v2/tests/unit/test_usage_service.py]`, `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]`, `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]`, `@[backend_v2/tests/test_fastdev_frozen.py]`, `@[backend_v2/tests/test_worker_models_used.py]`) | 67 instances of deceptive mock repository variables across root unit tests and LLM integration fixtures. | Replace all repository mocks with instantiated in-memory repository fakes; eliminate all residual `@patch` decorators targeting repository interfaces. | Pruned fragmented test mocks; standardize on single SSOT fake repository suite. | `uv run python scripts/_ast_guardrails.py backend_v2/tests/unit/ --strict` |
| False-Positive Defenses (`@[backend_v2/tests/unit/scripts/test_matrix_slice_engine.py]`) | 2 false-positive QGR014 violations on `mock_report = MagicMock()` due to `"_repo"` matching `mock_report`. | Refined `_ast_guardrails.py` visitor resolves false positives without modifying the test logic. | Pruned arbitrary variable renaming; fix root cause in AST guardrail visitor. | `uv run python scripts/_ast_guardrails.py backend_v2/tests/unit/scripts/test_matrix_slice_engine.py --strict` |

## Phase 2: Pre-Implementation Cleanups

All technical debt identified across touched files and 1-hop callers is quarantined and queued for pre-implementation resolution:
1. **AST False-Positive Remediation (`scripts/_ast_guardrails.py`)**: In `visit_Assign`, `target.id` containing `_repo` matches `mock_report = MagicMock()` in `test_matrix_slice_engine.py:98,116`, `mock_report_dto = MagicMock()` in `test_execution.py:819,935,1914,2762`, and `mock_report_service = MagicMock()` in `test_rest_only_pipeline_boundary.py:214,246`. Add `and not ("report" in target_id_lower or "response" in target_id_lower)` to exclude non-repository variables from QGR014. Cleaned in Step 2.3.
2. **AST Rule Documentation Sync (`scripts/_ast_guardrails.py`)**: Line 1893 incorrectly documents QGR014 as "Hardcoded Finnish Vocabulary in System Directives Ban". Update to "QGR014: AsyncMock / MagicMock on repository interfaces in tests (FATAL)". Cleaned in Step 2.3.
3. **Dedicated Fake Repository Unit Tests (`[NEW] @[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`)**: Build comprehensive test harness asserting snapshot isolation, CRUD persistence roundtrips, and deterministic fault injection across all 16 fake repositories. Cleaned in Step 2.1.
4. **Warning Ceiling Synchronization (`scripts/audit_warning_baseline.py`)**: Update `CURRENT_WARNING_CEILING` from 1,254 down to 934, asserting monotonic warning reduction. Cleaned in Step 2.3.
5. **Batch Elimination of 319 Deceptive Repository Mocks**: Systematically refactor all 53 test files across Batches A through E, replacing `AsyncMock`, `MagicMock`, and `@patch` decorators with strongly typed in-memory repository fakes. Cleaned in Step 2.2.
6. **Concurrency Stress Test Harness (`[NEW] @[backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py]`)**: Build high-concurrency async harness testing 50+ and 100+ concurrent simulated atoms in `asyncio.TaskGroup` with bracketless `except*` error trapping. Cleaned in Step 2.4.

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
    <item>Dedicated unit test suite for fake repositories implemented in backend_v2/tests/unit/fakes/test_in_memory_repositories.py passing 100%.</item>
    <item>All 319 QGR014 deceptive mock occurrences across all 53 test files in backend_v2/tests/ replaced with stateful In-Memory fakes.</item>
    <item>AST false-positive exclusion for report and response variables implemented in scripts/_ast_guardrails.py.</item>
    <item>QGR014 promoted to FATAL severity in scripts/_ast_guardrails.py with 0 violations across backend_v2/tests/.</item>
    <item>Total codebase warnings reduced from 1,253 to 934 warnings, with CURRENT_WARNING_CEILING updated to 934 in scripts/audit_warning_baseline.py.</item>
    <item>Concurrency stress test suite implemented in backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py running 50+ and 100+ concurrent atoms with zero deadlocks and clean ExceptionGroup cancellation.</item>
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
    <backend>@[scripts/audit_warning_baseline.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_repositories.py]</backend>
  </touched_artifacts>

  <step id="2.1" name="Audit and Enhance In-Memory Repository Fakes &amp; Unit Test Harness">
    <action>In `@[backend_v2/tests/fakes/in_memory_repositories.py]`, audit and verify all 16 repository fake classes (`InMemoryWorkflowRepository`, `InMemoryExecutionRepository`, `InMemoryOutputProfileRepository`, `InMemorySystemRepository`, `InMemoryAuditRepository`, `InMemoryIdentityRepository`, `InMemoryComponentRepository`, `InMemoryPromptBlockRepository`, `InMemoryAgentRepository`, `InMemoryTaskBlueprintRepository`, `InMemoryKnowledgeRepository`, `InMemoryMatrixRepository`, `InMemoryRoleRepository`, `InMemoryExecutionPersonaRepository`, `InMemoryExtractionProtocolRepository`, `InMemoryUnifiedWorkflowRepository`).</action>
    <action>Ensure full implementation of all methods defined in `IRepository` contracts with thread-safe dictionary stores, snapshot isolation deep-cloning via `type(item).model_validate(item.model_dump(mode="python"), strict=False)`, and deterministic `inject_fault(method_name, exception, trigger_count)` support.</action>
    <action>Create [NEW] `@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]` asserting snapshot isolation (`repo.get(id) is not repo.get(id)` and `repo.get(id) == repo.get(id)`), genuine CRUD persistence, pre-flight model validation, and deterministic fault injection across all 16 fake repositories.</action>
    <constraint invariant="deceptive_persistence_mocking_ban">Fakes MUST simulate genuine persistence roundtrips, Pydantic schema validation, and state mutations.</constraint>
  </step>

  <step id="2.2" name="Batch Refactor Unit and Integration Test Fixtures (Sub-package by Sub-package)">
    <action>Batch A: In `backend_v2/tests/unit/services/` (specifically and exhaustively: `@[backend_v2/tests/unit/services/test_execution.py]`, `@[backend_v2/tests/unit/services/test_report_service.py]`, `@[backend_v2/tests/unit/services/execution/test_ingress_service.py]`, `@[backend_v2/tests/unit/services/execution/test_override_service.py]`, `@[backend_v2/tests/unit/services/execution/test_facade.py]`, `@[backend_v2/tests/unit/services/test_execution_resumability.py]`, `@[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py]`, `@[backend_v2/tests/unit/services/test_blueprint.py]`, `@[backend_v2/tests/unit/services/test_report_service_synthesis_args.py]`, `@[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]`, `@[backend_v2/tests/unit/services/test_execution_render_bug.py]`, `@[backend_v2/tests/unit/services/studio/test_workflow_service.py]`), replace `AsyncMock(spec=...)` and `MagicMock()` fixtures with instantiated in-memory repository fakes (`InMemoryExecutionRepository`, `InMemoryWorkflowRepository`, `InMemoryOutputProfileRepository`, `InMemoryPromptBlockRepository`).</action>
    <action>Batch B: In `backend_v2/tests/unit/services/orchestrator/` and `backend_v2/tests/unit/workers/` (specifically and exhaustively: `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/workers/test_execution_worker.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`, `@[backend_v2/tests/unit/workers/test_report_worker.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`), replace repository mocks with clean dependency injection of `InMemoryUnifiedWorkflowRepository` or instantiated in-memory repository fakes; eliminate all `@patch` decorators targeting repository interfaces.</action>
    <action>Batch C: In `backend_v2/tests/integration/` (specifically: `@[backend_v2/tests/integration/test_epic_chain_e2e.py]`), replace all mock repository variables (`mock_exec_repo`, `mock_workflow_repo`, `mock_prompt_block_repo`, `mock_output_profile_repo`, `mock_comp_repo`, `mock_system_repo`) with stateful in-memory fakes.</action>
    <action>Batch D: In `backend_v2/tests/unit/hooks/` (specifically and exhaustively: `@[backend_v2/tests/unit/hooks/test_atom_flattening.py]`, `@[backend_v2/tests/unit/hooks/test_passivity_hook.py]`, `@[backend_v2/tests/unit/hooks/test_scoring.py]`, `@[backend_v2/tests/unit/hooks/test_archival.py]`, `@[backend_v2/tests/unit/hooks/test_matrix_hook.py]`, `@[backend_v2/tests/unit/hooks/test_atom_sampling_determinism.py]`, `@[backend_v2/tests/unit/hooks/test_input_processing.py]`), replace `mock_pb_repo = AsyncMock()`, `mock_repo = AsyncMock()` with `InMemoryPromptBlockRepository()` and `InMemoryWorkflowRepository()`.</action>
    <action>Batch E: In root unit tests and LLM layer (specifically and exhaustively: `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_dependencies.py]`, `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]`, `@[backend_v2/tests/unit/test_logic.py]`, `@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]`, `@[backend_v2/tests/unit/test_finops_telemetry.py]`, `@[backend_v2/tests/unit/test_progress.py]`, `@[backend_v2/tests/unit/llm/test_client.py]`, `@[backend_v2/tests/unit/llm/test_structured_retry.py]`, `@[backend_v2/tests/unit/test_auth.py]`, `@[backend_v2/tests/unit/test_concurrency_fuzzer.py]`, `@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]`, `@[backend_v2/tests/unit/test_dag_taskgroup.py]`, `@[backend_v2/tests/unit/test_llm_context_bounds.py]`, `@[backend_v2/tests/unit/test_llm_dependency.py]`, `@[backend_v2/tests/unit/test_usage_service.py]`, `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]`, `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]`, `@[backend_v2/tests/test_fastdev_frozen.py]`, `@[backend_v2/tests/test_worker_models_used.py]`), replace all mock repository fixtures and purge `@patch` decorators targeting repository interfaces across all test modules.</action>
    <constraint invariant="the_zero_compromise_pledge">Zero tolerance for deceptive green tests that bypass persistence verification.</constraint>
  </step>

  <step id="2.3" name="Promote QGR014 to FATAL Severity &amp; Tighten AST False-Positive Defenses">
    <action>In `@[scripts/_ast_guardrails.py]`, update `visit_Assign` and `visit_Call` to unconditionally assign FATAL severity to all QGR014 violations.</action>
    <action>In `@[scripts/_ast_guardrails.py]`, refine `visit_Assign` variable matching to exclude `report` and `response` variables (`mock_report`, `mock_report_dto`), eliminating false-positive violations in `@[backend_v2/tests/unit/scripts/test_matrix_slice_engine.py]` without masking genuine repository fixtures.</action>
    <action>In `@[scripts/_ast_guardrails.py]`, update the CLI help text string for QGR014 to "QGR014: AsyncMock / MagicMock on repository interfaces in tests (FATAL)".</action>
    <action>In `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, update existing QGR014 tests to assert FATAL severity and add an explicit false-positive defense assertion proving `mock_report = MagicMock()` emits 0 violations.</action>
    <action>In `@[scripts/audit_warning_baseline.py]` and `@[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py]`, update `CURRENT_WARNING_CEILING` from 1,254 down to 934.</action>
    <action>Execute AST guardrails across `backend_v2/tests`: mathematically verify 0 violations of QGR014.</action>
    <action>Verify total codebase warning count drops from 1,253 to 934 warnings.</action>
    <constraint invariant="neuro_symbolic_grounding_mandate">Prove mock eradication mathematically through AST verification.</constraint>
  </step>

  <step id="2.4" name="Implement Concurrency Stress Test Suite">
    <action>Create [NEW] `@[backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py]` implementing an automated high-concurrency stress harness.</action>
    <action>Spawn 50+ and 100+ concurrent simulated atom tasks executing within managed `asyncio.TaskGroup` contexts.</action>
    <action>Simulate high-frequency memory-state updates under `_update_lock`, verifying zero deadlocks, zero lock starvation, and deterministic state transitions.</action>
    <action>Implement ISTQB negative error partition: inject faults via `inject_fault` during high concurrency, asserting clean `TaskGroup` cancellation with bracketless `except*` and zero zombie tasks.</action>
    <constraint invariant="system_concurrency_ssot">Managed TaskGroup execution must maintain lock integrity under high load.</constraint>
  </step>

  <test_contracts>
    <test name="test_in_memory_workflow_repo_persistence_roundtrip" category="positive">
      <input>Save workflow to InMemoryWorkflowRepository, then get_by_id</input>
      <expected>Returns exact domain model with updated state</expected>
    </test>
    <test name="test_in_memory_repo_fault_injection" category="error_path">
      <input>Configure inject_fault('save_workflow', DatabaseConnectionError()), then call save_workflow</input>
      <expected>Raises DatabaseConnectionError deterministically</expected>
    </test>
    <test name="test_in_memory_repo_snapshot_isolation" category="positive">
      <input>Retrieve model from repo, mutate local variable, re-fetch from repo</input>
      <expected>Original stored model remains unmutated; repo.get(id) is not repo.get(id)</expected>
    </test>
    <test name="test_qgr014_asyncmock_on_repo_raises_fatal" category="positive">
      <input>Test file with repo = AsyncMock(spec=IWorkflowRepository)</input>
      <expected>QuorumGuardrailVisitor emits FATAL violation for QGR014</expected>
    </test>
    <test name="test_qgr014_assign_mock_repo_raises_fatal" category="positive">
      <input>Test file with mock_repo = AsyncMock()</input>
      <expected>QuorumGuardrailVisitor emits FATAL violation for QGR014</expected>
    </test>
    <test name="test_qgr014_mock_report_false_positive_defense" category="boundary">
      <input>Test file with mock_report = MagicMock()</input>
      <expected>QuorumGuardrailVisitor emits 0 violations for QGR014</expected>
    </test>
    <test name="test_concurrency_stress_50_atoms_no_deadlock" category="boundary">
      <input>50 concurrent simulated atom tasks in asyncio.TaskGroup</input>
      <expected>All 50 tasks complete successfully with zero deadlocks within timeout</expected>
    </test>
    <test name="test_concurrency_stress_fault_injection_cancels_cleanly" category="error_path">
      <input>50 concurrent atom tasks where task 25 injects an AppException</input>
      <expected>TaskGroup raises ExceptionGroup and cancels sibling tasks without zombies</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute QGR014 verification: `uv run python scripts/_ast_guardrails.py backend_v2/tests --strict`</action>
    <action>Execute full test suite in touched domains: `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py backend_v2/tests/unit/scripts/test_audit_warning_baseline.py backend_v2/tests/unit/fakes/test_in_memory_repositories.py backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py`</action>
    <action>Execute warning baseline ledger: `uv run python scripts/audit_warning_baseline.py` (Assert: 0 FATAL errors, total warnings &lt;= 934)</action>
    <action>Execute 8-stage audit loop on test fakes: `uv run python scripts/backend_audit_loop.py backend_v2/tests/fakes/in_memory_repositories.py --test --ast-strict`</action>
    <action>Execute markdown boundary verification: `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_156/02_phase2_plan.md`</action>
  </validation_gate>
</execution_protocol>
```
