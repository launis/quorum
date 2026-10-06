# Phase 5: Test Persistence Migration — Orchestrator & DAG

**Overview:** Migrate 161 census A assignments, 10 census B attribute replacements, 2 fixtures, 152 census D keyword-injected repository mocks, 11 census I fake imports, and 1 census X `cast(Any, ...)` across DAG executor, strategy, and concurrency tests.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L479-L505] Phase 5: Test Persistence Migration — Orchestrator & DAG

**Target Files:**
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py#L20-L22]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py#L19-L57]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_dag_taskgroup.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_concurrency_fuzzer.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_logic.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_chat_inflation.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]

### Pre-Implementation Cleanups (Discovered Technical Debt)
1. **Mock-Emulation Fake Usage & Dynamic Attribute Replacement**:
   - 161 census A assignments configuring `.return_value` or `.side_effect` on repository identifiers across 14 files: `test_dag_executor.py` (41), `test_dag_executor_atom_ceiling.py` (5), `test_dag_executor_mcp_audit.py` (2), `test_dag_executor_mcp_concurrency.py` (3), `test_dag_executor_preflight.py` (7), `test_rag_preflight_service.py` (1), `test_synthesis_distiller.py` (2), `strategies/test_llm.py` (61), `strategies/test_llm_cost_tracking.py` (6), `strategies/test_logic.py` (7), `test_dag_executor_prompt_blocks.py` (9), `test_dag_taskgroup.py` (5), `test_concurrency_fuzzer.py` (10), and `test_logic.py` (2).
   - 10 census B attribute replacements assigning `AsyncMock(...)` or `MagicMock(...)` to repository attributes across 5 files: `test_dag_executor.py` (4), `test_dag_executor_atom_ceiling.py` (2), `test_dag_executor_preflight.py` (1), `strategies/test_llm.py` (2), and `test_dag_taskgroup.py` (1).
   - 11 census I files importing `InMemoryBlueprintTransformerRepository`: specifically `test_dag_executor.py`, `test_dag_executor_mcp_audit.py`, `test_dag_executor_mcp_concurrency.py`, `test_dag_executor_preflight.py`, `test_rag_preflight_service.py`, `strategies/test_llm.py`, `strategies/test_llm_cost_tracking.py`, `test_dag_executor_prompt_blocks.py`, `test_dag_taskgroup.py`, `test_concurrency_fuzzer.py`, and `test_logic.py`.
2. **Keyword-Injected Repository Mocks**:
   - 152 census D keyword-injected repository mocks (`exec_repo=AsyncMock(...)`, `workflow_repo=AsyncMock(...)`, `system_repo=AsyncMock(...)`) across 14 files: `test_dag_executor.py` (44), `test_dag_executor_atom_ceiling.py` (2), `test_dag_executor_mcp_audit.py` (6), `test_dag_executor_preflight.py` (10), `test_synthesis_distiller.py` (8), `strategies/test_llm.py` (24), `strategies/test_logic.py` (8), `test_dag_taskgroup.py` (8), `strategies/test_base.py` (8), `strategies/test_node_strategy_registry.py` (8), `strategies/test_registry.py` (8), `test_dag_executor_telemetry.py` (8), `test_rag_preflight_chat_inflation.py` (2), and `test_synthesis_distiller_wiring.py` (8).
3. **Unverified AsyncMock Fixtures & Untyped Dictionaries**:
   - 2 repository fixtures returning unverified `AsyncMock` or dictionary mock bags: `test_dag_executor_atom_ceiling.py#L20-L22` (`mock_repo`) and `test_dag_executor_mcp_concurrency.py#L19-L57` (`mock_repos`).
4. **Type Suppression & Permissive Cast Eradication**:
   - 1 census X `cast(Any, None)` at line 115 in `backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py` to bypass Pydantic model validation.


## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py#L20-L22]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py#L19-L57]`, `@[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py#L111-L136]` | Banned returning unconfigured `AsyncMock()` from `mock_repo` fixture. Banned returning untyped dictionaries with mock side effects in `mock_repos`. Banned `cast(Any, None)` in `test_rag_preflight_service.py#L115`. | Define typed repository fixtures returning `InMemoryUnifiedWorkflowRepository` and `InMemorySystemRepository`. Seed real `Workflow` and `Step` domain models natively. Assign `None` natively to optional `task_blueprint`. | Pruned dynamic mock dictionary synthesis; instantiate canonical in-memory repository fakes. | Localized pytest passes. Census X = 0. Fixtures return typed instances. |
| `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`, `@[backend_v2/tests/unit/test_dag_taskgroup.py]` | Banned 10 Census B dynamic attribute replacements (`mock_repo.<attr> = AsyncMock(...)`). Banned overriding `update_execution` with ad-hoc closures (`flaky_update_execution`). | Seed users, executions, and steps natively into `InMemoryUnifiedWorkflowRepository`. Use `repo.inject_fault("update_execution", AppException(...), trigger_count=1)` or `repo.fault_context()` for deterministic failure testing. | Pruned ad-hoc monkeypatching of repository methods; rely on stateful in-memory stores with built-in fault injection. | Census B matches = 0 on target files. Localized pytest passes. |
| `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]`, `@[backend_v2/tests/unit/test_dag_taskgroup.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_chat_inflation.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]` | Banned 152 Census D keyword-injected repository mocks (`exec_repo=AsyncMock(...)`, `workflow_repo=MagicMock(...)`) in `StrategyDependencies(...)`, `DAGExecutor(...)`, and `RAGPreflightService(...)`. | Pass typed instances of `InMemoryUnifiedWorkflowRepository` (and sub-repositories) satisfying all 8 `StrategyDependencies` repository interfaces. | Pruned repetitive mock instantiation in test dependency setups; use unified typed fake. | Census D matches = 0 on target files. Localized pytest passes. |
| `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]` | Banned Census A method `.return_value` and `.side_effect` assignments on `InMemoryBlueprintTransformerRepository`. Banned Census I imports of the deprecated fake. | Seed test entities using typed repository write methods (`create_workflow`, `save_workflow`, `create_step`, `create_execution`, `save_output_profile`, `create_user`, `create_system_config`). Replace imports with `InMemoryUnifiedWorkflowRepository`. | Pruned dynamic mock method synthesis; rely on typed Rust-accelerated Pydantic snapshot stores. | Census A matches = 0 on target files. Census I matches = 0 on target files. Localized pytest passes. |
| `@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]`, `@[backend_v2/tests/unit/test_dag_taskgroup.py]`, `@[backend_v2/tests/unit/test_concurrency_fuzzer.py]`, `@[backend_v2/tests/unit/test_logic.py]` | Banned Census A assignments across high-concurrency and fuzzing test suites. Banned Census I imports of deprecated fake. | Seed workflows, steps, and prompt blocks into `InMemoryUnifiedWorkflowRepository`. Validate concurrency safety under `asyncio.TaskGroup` using thread-safe in-memory stores. Replace imports with `InMemoryUnifiedWorkflowRepository`. | Pruned loose mock return values in concurrency stress tests. | Census A matches = 0 on target files. Census I matches = 0 on target files. Localized pytest passes. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT &amp; PERSISTENCE CENSUS PROBE">
    <action>Look backward: Verify Phase 4 completed successfully with 100% test contracts passed, zero AST violations, Census A=0, B=0, C=0, I=0, D=0 across 23 Phase 4 target files, and residual ceilings ratcheted down in scripts/audit_warning_baseline.py.</action>
    <action>Baseline persistence census probe: Execute Census A, B, C, I, D, X across the 20 Phase 5 target files and verify exact baseline occurrences: Census A=161, Census B=10, Census C=0, Census I=11 files, Census D=152, Census X=1, Fixtures=2 returning AsyncMock or untyped dictionary.</action>
    <action>Look forward: Verify that migrating DAG orchestrator, strategy, and concurrency test persistence doubles to stateful in-memory fakes isolates remaining mocks strictly to Workers and Integration tests in Phase 6.</action>
    <constraint invariant="universal_fail_fast">If prior phase contracts fail or baseline census metrics mismatch, STOP immediately and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/05_phase5_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <step id="1" name="REPOSITORY FIXTURES MODERNIZATION &amp; MCP CONCURRENCY FAKES">
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py#L20-L22]: Replace def mock_repo() -> MagicMock: with typed fixture returning InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py#L19-L57]: Modernize def mock_repos() -> dict[str, Any]: to instantiate InMemoryUnifiedWorkflowRepository, seed workflow and step via typed domain methods (create_workflow, save_workflow), replace untyped dictionary side effects with typed domain entities, and return typed repository instances in the dictionary. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py#L111-L136]: Eradicate Census X by replacing task_blueprint=cast(Any, None) at line 115 with task_blueprint=None. Modernize mock_workflow_repo and mock_system_repo fixtures to return InMemoryWorkflowRepository and InMemorySystemRepository. Replace import of InMemoryBlueprintTransformerRepository.</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py`.</action>
    <constraint invariant="deceptive_persistence_mocking_ban">Every modernized repository fixture MUST return a functional in-memory fake with state isolation rather than an unverified AsyncMock.</constraint>
    <constraint invariant="the_zero_compromise_pledge">cast(Any, None) must be completely eradicated; optional task_blueprint must evaluate natively without type laundering.</constraint>
  </step>

  <step id="2" name="CENSUS B ATTRIBUTE REPLACEMENTS &amp; DETERMINISTIC FAULT INJECTION">
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]: Eradicate all 4 Census B attribute replacements: replace mock_repo.get_user = AsyncMock(...) at line 76 with typed user seeding via await mock_repo.create_user(User(...)); replace mock_repo.update_execution = AsyncMock(side_effect=Exception("Database connection lost")) at line 829 with mock_repo.inject_fault("update_execution", Exception("Database connection lost"), trigger_count=1); replace mock_repo.update_execution = AsyncMock(side_effect=flaky_update_execution) at lines 1332 and 1425 with mock_repo.inject_fault("update_execution", AppException(message="Failed to commit execution trace", details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED}, status_code=500), trigger_count=1).</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]: Eradicate 2 Census B attribute replacements: replace mock_repo.update_execution = AsyncMock() at line 74 with real in-memory execution update; replace mock_repo.get_model_registry = AsyncMock() at line 99 with typed model registry seeding.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]: Eradicate Census B attribute replacement mock_repo.get_step_by_id = AsyncMock(...) at line 312 by seeding the step into mock_repo via create_step.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]: Eradicate 2 Census B attribute replacements: replace mock_repo.get_step = AsyncMock(...) at line 700 with typed step seeding; replace mock_repo.update_execution = AsyncMock() at line 936 with real in-memory execution update.</action>
    <action>In @[backend_v2/tests/unit/test_dag_taskgroup.py]: Eradicate Census B attribute replacement mock_repo.update_execution = AsyncMock(side_effect=flaky_update_execution) at line 439 with mock_repo.inject_fault("update_execution", AppException(message="Failed to commit execution trace", details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED}, status_code=500), trigger_count=1).</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py backend_v2/tests/unit/test_dag_taskgroup.py`.</action>
    <constraint invariant="deceptive_persistence_mocking_ban">Zero attribute replacements or monkeypatched repository methods permitted. Fault injection must strictly use BaseInMemoryRepository.inject_fault() or fault_context().</constraint>
  </step>

  <step id="3" name="KEYWORD-INJECTED REPOSITORY MOCKS ERADICATION (CENSUS D)">
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]: Eradicate all 44 keyword-injected repository mocks across DAGExecutor and StrategyDependencies constructor calls, passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]: Eradicate 2 keyword-injected repository mocks at lines 41 and 44, passing typed mock_repo fixture.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]: Eradicate all 6 keyword-injected repository mocks in StrategyDependencies and DAGExecutor, passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]: Eradicate all 10 keyword-injected repository mocks in StrategyDependencies and DAGExecutor, passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]: Eradicate all 8 keyword-injected repository mocks in StrategyDependencies, passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]: Eradicate all 24 keyword-injected repository mocks in StrategyDependencies, passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]: Eradicate all 8 keyword-injected repository mocks in StrategyDependencies, passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/test_dag_taskgroup.py]: Eradicate all 8 keyword-injected repository mocks in StrategyDependencies, passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]: Eradicate all 8 keyword-injected repository mocks in StrategyDependencies (lines 21-28), passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]: Eradicate all 8 keyword-injected repository mocks in StrategyDependencies (lines 23-30), passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py]: Eradicate all 8 keyword-injected repository mocks in StrategyDependencies (lines 23-30), passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py]: Eradicate all 8 keyword-injected repository mocks in DAGExecutor (lines 29-36), passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_chat_inflation.py]: Eradicate 2 keyword-injected repository mocks in RAGPreflightService (lines 99-100), passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]: Eradicate all 8 keyword-injected repository mocks in StrategyDependencies (lines 45-52), passing typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>Execute localized unit tests across all 14 modified files to verify all tests pass cleanly.</action>
    <constraint invariant="the_duct_tape_ban">No naked AsyncMock or MagicMock instances passed as repository dependencies. All keyword-injected dependencies must be instances of BaseInMemoryRepository.</constraint>
  </step>

  <step id="4" name="ORCHESTRATOR &amp; STRATEGY PERSISTENCE EMULATION-FAKE MIGRATION (CENSUS A &amp; I)">
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]: Migrate 41 Census A return_value assignments on repository fakes to typed seeding of InMemoryUnifiedWorkflowRepository (create_workflow, save_workflow, create_step, create_execution, save_output_profile, create_user, create_system_config). Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]: Migrate 5 Census A return_value assignments to typed seeding of Workflow and Step models into mock_repo.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]: Migrate 2 Census A return_value assignments to typed seeding. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]: Migrate 7 Census A return_value assignments to typed seeding of Workflow and Step models. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]: Migrate 61 Census A return_value assignments to typed seeding of workflows, steps, prompt blocks, output profiles, and execution records. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]: Migrate 6 Census A return_value assignments to typed seeding of workflows, steps, and system configs. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]: Migrate 7 Census A return_value assignments to typed seeding of workflows and steps into InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]: Migrate 2 Census A return_value assignments to typed seeding of workflows and steps.</action>
    <action>Execute localized unit tests across all 8 modified files to verify all tests pass cleanly.</action>
    <constraint invariant="repository_reconstitution_mandate">All repository lookups in orchestrator and strategy tests must return strictly typed domain models from snapshot storage.</constraint>
    <constraint invariant="the_no_legacy_mandate">Zero imports of InMemoryBlueprintTransformerRepository allowed across modified orchestrator files.</constraint>
  </step>

  <step id="5" name="CONCURRENCY, FUZZER &amp; LOGIC SUITES PERSISTENCE MIGRATION (CENSUS A &amp; I)">
    <action>In @[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]: Migrate 9 Census A return_value assignments to typed seeding of workflows, steps, and prompt blocks into InMemoryUnifiedWorkflowRepository. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/test_dag_taskgroup.py]: Migrate 5 Census A return_value assignments to typed seeding of workflows, steps, and executions into InMemoryUnifiedWorkflowRepository. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/test_concurrency_fuzzer.py]: Migrate 10 Census A return_value assignments to typed seeding of workflows, steps, and executions into InMemoryUnifiedWorkflowRepository. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/test_logic.py]: Migrate 2 Census A return_value assignments to typed seeding of workflows and steps into InMemoryUnifiedWorkflowRepository. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>Execute localized unit tests across all 4 modified files to verify all tests pass cleanly.</action>
    <constraint invariant="free_threading_concurrency">Concurrency and fuzzer suites must execute against thread-safe in-memory repositories under asyncio.TaskGroup without state race conditions.</constraint>
  </step>

  <step id="6" name="TWO-STAGE TESTING PIPELINE &amp; ZERO-BYPASS VERIFICATION GATE">
    <action>Execute Census A probe on the 20 Phase 5 target files, asserting exactly 0 matches.</action>
    <action>Execute Census B probe on the 20 Phase 5 target files, asserting exactly 0 matches.</action>
    <action>Execute Census C probe on the 20 Phase 5 target files, asserting exactly 0 matches.</action>
    <action>Execute Census I probe on the 20 Phase 5 target files, asserting exactly 0 matches.</action>
    <action>Execute Census D probe on the 20 Phase 5 target files, asserting exactly 0 matches.</action>
    <action>Execute Census X probe on the 20 Phase 5 target files, asserting exactly 0 matches.</action>
    <action>Execute global backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Execute SDUI semantic parity gate: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <action>Ratchet down CURRENT_RESIDUAL_CEILINGS in scripts/audit_warning_baseline.py to reflect eradicated Census D matches (lowering ceiling by 152 from 173 to 21).</action>
    <constraint invariant="fragmented_quality_gates_prevention">Completion requires passing global backend audit loop, SDUI semantic parity, and zero residual census matches across all 20 target files.</constraint>
  </step>

  <dod_checklist>
    <item>Census commands A, B, C, I, D, and X restricted to the 20 target files return 0 matches.</item>
    <item>All 2 repository fixtures returning AsyncMock or untyped dictionaries are replaced with typed in-memory repository instances.</item>
    <item>All 161 Census A .return_value and .side_effect assignments on repository fakes are replaced with typed seeding.</item>
    <item>All 10 Census B attribute replacements across the 5 target files are replaced with typed seeding or inject_fault().</item>
    <item>All 11 Census I imports of InMemoryBlueprintTransformerRepository are migrated to InMemoryUnifiedWorkflowRepository.</item>
    <item>All 152 Census D keyword-injected repository mocks are replaced with stateful in-memory repository instances.</item>
    <item>Census X cast(Any, None) in test_rag_preflight_service.py is eradicated.</item>
    <item>Residual debt ceilings in scripts/audit_warning_baseline.py are ratcheted down monotonically (Census D ceiling lowered by 152).</item>
    <item>Universal audit loop uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict passes cleanly with 0 AST violations and 0 MyPy issues.</item>
    <item>Cross-Domain SDUI Semantic Parity gate passes cleanly via uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py.</item>
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
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT delete DynamicRepoMethod or InMemoryBlueprintTransformerRepository during Phase 5 (quarantined strictly for Phase 7).</anti_target>
    <anti_target>Do NOT modify worker tests during Phase 5 (quarantined strictly for Phase 6).</anti_target>
    <anti_target>Do NOT add new fields or optional attributes to DTOs or domain models as drive-by fixes (ban drive-by schema mutations).</anti_target>
    <anti_target>Do NOT use duck-typing, naked dictionaries, or permissive fallback chains in modernized tests.</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census A, B, C, I, D, X check on Phase 5 targets asserting 0 matches.</action>
    <action>Execute Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Execute SDUI Semantic Parity: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
  </validation_gate>
</execution_protocol>
```
