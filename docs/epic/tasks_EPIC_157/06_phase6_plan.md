# Phase 6: Test Persistence Migration — Workers, API & Integration

**Overview:** Migrate the remaining 198 Census A assignments, 21 Census D keyword-injected repository mocks, and 50/51 Census F string-target repository patches across worker, API, and integration test suites, binding each patch return_value to typed in-memory repositories.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L506-L528] Phase 6: Test Persistence Migration — Workers, API & Integration

**Target Files (15 files):**
- `[MODIFY]` @[backend_v2/tests/unit/workers/test_execution_worker.py]
- `[MODIFY]` @[backend_v2/tests/unit/workers/test_report_worker.py]
- `[MODIFY]` @[backend_v2/tests/unit/workers/test_synthesis_reducers.py]
- `[MODIFY]` @[backend_v2/tests/unit/workers/test_synthesis_worker.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker_synthesis.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_finops_telemetry.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_progress.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]
- `[MODIFY]` @[backend_v2/tests/integration/test_epic_chain_e2e.py]
- `[MODIFY]` @[backend_v2/tests/test_fastdev_frozen.py]
- `[MODIFY]` @[backend_v2/tests/test_worker_models_used.py]
- `[MODIFY]` @[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]
- `[MODIFY]` @[backend_v2/tests/integration/test_tavily_live.py]

### Pre-Implementation Cleanups (Discovered Technical Debt)
1. **Mock-Emulation Fake Usage & Dynamic Attribute Replacement**:
   - 198 Census A assignments configuring `.return_value` or `.side_effect` on repository identifiers across 13 files: `test_execution_worker.py` (33), `test_report_worker.py` (3), `test_synthesis_reducers.py` (3), `test_synthesis_worker.py` (7), `test_worker.py` (90), `test_worker_synthesis.py` (24), `test_worker_synthesis_accumulation.py` (9), `test_finops_telemetry.py` (1), `test_progress.py` (1), `test_rest_only_pipeline_boundary.py` (2), `test_epic_chain_e2e.py` (20), `test_fastdev_frozen.py` (2), and `test_worker_models_used.py` (3).
   - 13 Census I files importing `InMemoryBlueprintTransformerRepository`: specifically `test_execution_worker.py`, `test_report_worker.py`, `test_synthesis_reducers.py`, `test_synthesis_worker.py`, `test_worker.py`, `test_worker_synthesis.py`, `test_worker_synthesis_accumulation.py`, `test_finops_telemetry.py`, `test_progress.py`, `test_rest_only_pipeline_boundary.py`, `test_epic_chain_e2e.py`, `test_fastdev_frozen.py`, and `test_worker_models_used.py`.
2. **Keyword-Injected Repository Mocks**:
   - 21 Census D keyword-injected repository mocks (`exec_repo=AsyncMock()`, `workflow_repo=AsyncMock()`, `comp_repo=AsyncMock()`, `prompt_block_repo=AsyncMock()`, `output_profile_repo=AsyncMock()`, `identity_repo=AsyncMock()`, `audit_repo=AsyncMock()`) across 2 integration files: `test_tavily_e2e_full_pipeline.py` (14) and `test_tavily_live.py` (7).
3. **String-Target Repository Patches**:
   - 50/51 Census F string-target repository patches (`patch("...UnifiedWorkflowRepository")`) across 6 worker test files: `test_worker.py` (22), `test_worker_synthesis.py` (16), `test_report_worker.py` (5), `test_synthesis_worker.py` (4), `test_synthesis_reducers.py` (3), and `test_worker_synthesis_accumulation.py` (1).
4. **Untracked Cast & Reflection Debt**:
   - 1 untracked `typing.cast(AsyncMock, usage_service.audit_repo)` at line 196 in `backend_v2/tests/unit/test_finops_telemetry.py`.
   - Ad-hoc unverified `side_effect` exception injection bypassing deterministic `inject_fault()`: `test_execution_worker.py#L500` (`update_execution.side_effect = OSError(...)`), `test_progress.py#L86` (`update_execution.side_effect = Exception(...)`), `test_synthesis_reducers.py#L535` (`get_execution.side_effect = OSError(...)`), and `test_worker.py#L1108` (`get_execution.side_effect = RuntimeError(...)`).
   - Ad-hoc unverified `side_effect` step routing closures in `test_worker_synthesis.py` (lines 133, 265, 667, 751, 824, 924, 999, 1096) and `test_worker_synthesis_accumulation.py#L45` (`get_step_by_id.side_effect = ...`) bypassing native step seeding.

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]`, `@[backend_v2/tests/integration/test_tavily_live.py]` | Banned 21 Census D keyword-injected repository mocks (`exec_repo=AsyncMock()`, `workflow_repo=AsyncMock()`, `comp_repo=AsyncMock()`, `prompt_block_repo=AsyncMock()`, `output_profile_repo=AsyncMock()`, `identity_repo=AsyncMock()`, `audit_repo=AsyncMock()`) in `HookDependencies`. | Pass typed `InMemoryUnifiedWorkflowRepository` and `InMemorySystemRepository` instances satisfying all 8 `HookDependencies` repository interfaces. | Pruned repetitive mock instantiation in test dependency setups; use unified typed fake. | Census D matches = 0 repo-wide. Localized pytest passes. |
| `@[backend_v2/tests/unit/test_finops_telemetry.py]`, `@[backend_v2/tests/unit/test_progress.py]`, `@[backend_v2/tests/test_fastdev_frozen.py]` | Banned Census A method `.return_value` assignments on `InMemoryBlueprintTransformerRepository`. Banned `typing.cast(AsyncMock, ...)`. Banned overriding `update_execution.side_effect` with ad-hoc closures. | Seed usage records, executions, and model registries natively into `InMemorySystemRepository` and `InMemoryUnifiedWorkflowRepository`. Use `fake_repo.inject_fault("update_execution", ...)` for deterministic error injection. Verify real state mutations. | Pruned dynamic mock method synthesis and cast laundering; rely on stateful in-memory stores. | Census A matches = 0 on target files. Census I matches = 0 on target files. Localized pytest passes. |
| `@[backend_v2/tests/unit/workers/test_execution_worker.py]`, `@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]`, `@[backend_v2/tests/test_worker_models_used.py]`, `@[backend_v2/tests/integration/test_epic_chain_e2e.py]` | Banned Census A method `.return_value` assignments on `mock_repo.get_workflow`, `mock_repo.get_execution`, `repo.get_all_output_profiles`. Banned inspecting unverified `mock_repo.update_execution.call_args`. | Seed workflows, executions, prompt blocks, and output profiles via typed write methods (`create_workflow`, `create_execution`, `save_output_profile`, `save_prompt_block`). Verify state persistence via `await repo.get_execution(...)`. | Pruned call-args inspection; verify actual roundtrip state mutations in snapshot memory stores. | Census A matches = 0 on target files. Census I matches = 0 on target files. Localized pytest passes. |
| `@[backend_v2/tests/unit/workers/test_report_worker.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]` | Banned Census A assignments. Banned Census F string-target patches returning unverified mocks (`mock_repo_class.return_value = InMemoryBlueprintTransformerRepository()`). Banned ad-hoc `side_effect = OSError(...)`. | Instantiate `repo = InMemoryUnifiedWorkflowRepository()`, seed domain models natively, bind `return_value=repo` in `patch("backend_v2.workers.*.UnifiedWorkflowRepository", return_value=repo)`. Use `repo.inject_fault("get_execution", ...)` for deterministic failure testing. | Pruned dynamic method synthesis; bind verified stateful fakes directly to worker repository patches. | Census A matches = 0 on target files. Census I matches = 0 on target files. Localized pytest passes. |
| `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]` | Banned Census A assignments. Banned `@patch("...UnifiedWorkflowRepository")` decorators producing `AsyncMock` facades. Banned `mock_repo.get_step_by_id.side_effect = ...` ad-hoc step routing. | Seed workflows, executions, and steps natively into `InMemoryUnifiedWorkflowRepository`. Bind `return_value=repo` on all worker patches. Seed steps via `repo.create_step(step)` or `repo.seed_raw_step(step)` for deterministic step resolution. | Pruned loose mock return values and ad-hoc side-effect closures in worker synthesis suites. | Census A matches = 0 on target files. Census I matches = 0 on target files. Localized pytest passes. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT &amp; PERSISTENCE CENSUS PROBE">
    <action>Look backward: Verify Phase 5 completed successfully with 100% test contracts passed, zero AST violations, Census A=0, B=0, C=0, I=0, D=0, X=0 across 20 Phase 5 target files, and residual ceilings ratcheted down in scripts/audit_warning_baseline.py.</action>
    <action>Baseline persistence census probe: Execute Census A, B, C, I, D, F, K, X across the 15 Phase 6 target files and verify exact baseline occurrences: Census A=198 (true repository occurrences across 13 files), Census B=0, Census C=0, Census I=13 files (104 occurrences), Census D=21 (14 in pipeline, 7 in live), Census F=50/51 (50 Epic baseline / 51 total regex matches across 6 worker test suites: test_worker.py 22, test_worker_synthesis.py 16, test_report_worker.py 5, test_synthesis_worker.py 4, test_synthesis_reducers.py 3, test_worker_synthesis_accumulation.py 1), Census K=0, Census X=0 (plus 1 untracked AsyncMock cast in test_finops_telemetry.py).</action>
    <action>Look forward: Verify that migrating worker, API, and integration test persistence doubles to stateful in-memory fakes achieves Census A=0 and Census I=0 across all test suites outside fakes, and Census D=0 repo-wide, satisfying the mandatory pre-condition for Phase 7 mock-emulation sunset.</action>
    <constraint invariant="universal_fail_fast">If prior phase contracts fail or baseline census metrics mismatch, STOP immediately and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/06_phase6_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <step id="1" name="KEYWORD-INJECTED REPOSITORY MOCKS ERADICATION (CENSUS D)">
    <action>In @[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]: Eradicate all 14 keyword-injected repository mocks in HookDependencies (lines 70-76 and lines 181-187), passing typed InMemoryUnifiedWorkflowRepository and InMemorySystemRepository instances.</action>
    <action>In @[backend_v2/tests/integration/test_tavily_live.py]: Eradicate all 7 keyword-injected repository mocks in HookDependencies (lines 117-123), passing typed InMemoryUnifiedWorkflowRepository and InMemorySystemRepository instances.</action>
    <action>Execute localized integration tests: `uv run pytest backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py backend_v2/tests/integration/test_tavily_live.py`.</action>
    <constraint invariant="the_duct_tape_ban">No naked AsyncMock or MagicMock instances passed as repository dependencies. All keyword-injected dependencies must be instances of BaseInMemoryRepository.</constraint>
    <constraint invariant="deceptive_persistence_mocking_ban">Every modernized repository dependency must return a functional in-memory fake with state isolation rather than an unverified AsyncMock.</constraint>
  </step>

  <step id="2" name="FINOPS, PROGRESS &amp; FASTDEV PERSISTENCE MIGRATION (CENSUS A &amp; I)">
    <action>In @[backend_v2/tests/unit/test_finops_telemetry.py]: Replace InMemoryBlueprintTransformerRepository in usage_service fixture (lines 22-23) with InMemorySystemRepository. Eradicate Census A assignment at line 197 and Census X cast at line 196 (typing.cast(AsyncMock, usage_service.audit_repo)) by saving prior_records natively via usage_service.audit_repo. Replace imports of InMemoryBlueprintTransformerRepository with InMemorySystemRepository.</action>
    <action>In @[backend_v2/tests/unit/test_progress.py]: Replace InMemoryBlueprintTransformerRepository at lines 41 and 85 with InMemoryUnifiedWorkflowRepository. Seed execution via await fake_repo.create_execution(mock_record). Eradicate Census A assignment at line 86 by replacing fake_repo.update_execution.side_effect = Exception("DB Connection Lost") with fake_repo.inject_fault("update_execution", Exception("DB Connection Lost"), trigger_count=1). Replace mock call_args assertions with real state persistence assertions on await fake_repo.get_execution("exe_123"). Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/test_fastdev_frozen.py]: Replace InMemoryBlueprintTransformerRepository at line 33 with InMemorySystemRepository. Eradicate Census A assignments at lines 35-36 by seeding model registry via await mock_repo.create_system_config(SystemConfig.model_validate(registry_data)). Replace import of InMemoryBlueprintTransformerRepository with InMemorySystemRepository.</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/test_finops_telemetry.py backend_v2/tests/unit/test_progress.py backend_v2/tests/test_fastdev_frozen.py`.</action>
    <constraint invariant="the_zero_compromise_pledge">cast(Any, ...) and unannotated mock method assignments must be completely eradicated.</constraint>
    <constraint invariant="deceptive_persistence_mocking_ban">State mutations must be verified against actual in-memory repository persistence rather than unverified mock call counts.</constraint>
  </step>

  <step id="3" name="EXECUTION WORKER &amp; PIPELINE BOUNDARY PERSISTENCE MIGRATION (CENSUS A &amp; I)">
    <action>In @[backend_v2/tests/unit/workers/test_execution_worker.py]: Migrate 33 Census A return_value assignments on repository fakes to typed seeding of InMemoryUnifiedWorkflowRepository (create_workflow, create_execution, save_output_profile). Eradicate mock update_execution assertions; assert state persistence on updated ExecutionRecord via await mock_repo.get_execution(execution_id). Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]: Migrate 2 Census A return_value assignments (lines 158-159) to typed seeding of mock_workflow and mock_record into InMemoryUnifiedWorkflowRepository. Note that lines 221-222 and 251 configure ReportService mocks (get_report_service) which are retained as router service mocks per Section 2.2 item 4 of Epic 157. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/test_worker_models_used.py]: Migrate 3 Census A return_value assignments (lines 28, 43, 56) to typed seeding of mock_workflow and mock_record into InMemoryUnifiedWorkflowRepository. Verify models_used is preserved upon real get_execution. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/integration/test_epic_chain_e2e.py]: Migrate 20 Census A return_value assignments to typed seeding of ExecutionRecord, Workflow, OutputProfile, and PromptBlockBase into InMemoryUnifiedWorkflowRepository. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/workers/test_execution_worker.py backend_v2/tests/unit/test_rest_only_pipeline_boundary.py backend_v2/tests/test_worker_models_used.py backend_v2/tests/integration/test_epic_chain_e2e.py`.</action>
    <constraint invariant="repository_reconstitution_mandate">All repository lookups in worker and integration tests must return strictly typed domain models from snapshot storage.</constraint>
    <constraint invariant="the_no_legacy_mandate">Zero imports of InMemoryBlueprintTransformerRepository allowed across modified worker and integration test files.</constraint>
  </step>

  <step id="4" name="SYNTHESIS WORKERS &amp; REDUCERS PERSISTENCE MIGRATION (CENSUS A, F &amp; I)">
    <action>In @[backend_v2/tests/unit/workers/test_report_worker.py]: Migrate 3 Census A return_value assignments and 5 Census F string patches. Replace InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository. Seed execution records via await repo.create_execution(record); for not-found test, do not seed execution. Bind return_value=repo directly in patch("backend_v2.workers.report_worker.UnifiedWorkflowRepository", return_value=repo). Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/workers/test_synthesis_reducers.py]: Migrate 3 Census A return_value assignments and 3 Census F string patches. Replace InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository. Seed execution records with typed ExecutionRecord. Replace mock_repo.get_execution.side_effect = OSError("DB unavailable") with repo.inject_fault("get_execution", OSError("DB unavailable"), trigger_count=1). Bind return_value=repo in patch("backend_v2.workers.synthesis_reducers.UnifiedWorkflowRepository", return_value=repo). Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/workers/test_synthesis_worker.py]: Migrate 7 Census A return_value assignments and 4 Census F string patches. Replace InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository. Seed executions, workflows, and output profiles via typed write methods. Bind return_value=repo in patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=repo). Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/workers/test_report_worker.py backend_v2/tests/unit/workers/test_synthesis_reducers.py backend_v2/tests/unit/workers/test_synthesis_worker.py`.</action>
    <constraint invariant="deceptive_persistence_mocking_ban">Zero unverified mock facades permitted in worker patches. Every string-target repository patch must bind return_value to an InMemoryUnifiedWorkflowRepository instance.</constraint>
  </step>

  <step id="5" name="MAIN WORKER &amp; WORKER SYNTHESIS SUITES PERSISTENCE MIGRATION (CENSUS A, F &amp; I)">
    <action>In @[backend_v2/tests/unit/test_worker.py]: Migrate 90 Census A return_value assignments and 22 Census F string patches. Replace InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository. Seed workflows, executions, prompt blocks, and output profiles via typed write methods. Bind return_value=repo on all patch calls targeting UnifiedWorkflowRepository. Use repo.inject_fault(...) for error handling tests. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/test_worker_synthesis.py]: Migrate 24 Census A return_value assignments and 16 Census F string patches. Replace @patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository") decorators and context managers with typed in-memory fake injection binding return_value=repo where repo = InMemoryUnifiedWorkflowRepository(). Seed workflows, steps, and executions natively, eliminating ad-hoc get_step_by_id side-effect closures in favor of real step lookups via repo.create_step(step) or repo.seed_raw_step(step). Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]: Migrate 9 Census A return_value assignments and 1 Census F string patch. Replace InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository. Seed execution and steps into repo. Bind return_value=repo in patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=repo). Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/test_worker.py backend_v2/tests/unit/test_worker_synthesis.py backend_v2/tests/unit/test_worker_synthesis_accumulation.py`.</action>
    <constraint invariant="free_threading_concurrency">Worker synthesis suites must execute against thread-safe in-memory repositories under asyncio.TaskGroup without state race conditions.</constraint>
  </step>

  <step id="6" name="TWO-STAGE TESTING PIPELINE &amp; ZERO-BYPASS VERIFICATION GATE">
    <action>Execute Census A probe across backend_v2/tests excluding tests/unit/fakes/, asserting exactly 0 matches.</action>
    <action>Execute Census I probe across backend_v2/tests excluding tests/unit/fakes/, asserting exactly 0 matches.</action>
    <action>Execute Census D probe across the entire backend_v2/tests tree, asserting exactly 0 matches.</action>
    <action>Execute Census F probe across backend_v2/tests, asserting that all string patches bind return_value to an InMemoryUnifiedWorkflowRepository instance.</action>
    <action>Execute Census B, C, K, X probes on target files, asserting exactly 0 matches.</action>
    <action>Ratchet down CURRENT_RESIDUAL_CEILINGS in scripts/audit_warning_baseline.py to reflect eradicated Census D matches (lowering ceiling by 21 from 21 to 0).</action>
    <action>Execute global backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Execute SDUI semantic parity gate: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <constraint invariant="fragmented_quality_gates_prevention">Completion requires passing global backend audit loop, SDUI semantic parity, and zero residual census matches across all 15 target files.</constraint>
  </step>

  <dod_checklist>
    <item>Census command A over backend_v2/tests excluding tests/unit/fakes/ returns 0 matches.</item>
    <item>Census command I over backend_v2/tests excluding tests/unit/fakes/ returns 0 matches.</item>
    <item>Census command D over the full backend_v2/tests tree returns 0 matches (all 21 eradicated).</item>
    <item>All 50/51 Census F string patches bind return_value to typed InMemoryUnifiedWorkflowRepository instances.</item>
    <item>All 198 Census A .return_value and .side_effect assignments on repository fakes across the 15 target files are eradicated.</item>
    <item>All 13 Census I imports of InMemoryBlueprintTransformerRepository across target files are migrated to InMemoryUnifiedWorkflowRepository or InMemorySystemRepository.</item>
    <item>Residual debt ceilings in scripts/audit_warning_baseline.py are ratcheted down monotonically (Census D ceiling lowered by 21 to 0).</item>
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
    <anti_target>Do NOT delete DynamicRepoMethod or InMemoryBlueprintTransformerRepository during Phase 6 (quarantined strictly for Phase 7).</anti_target>
    <anti_target>Do NOT modify backend_v2/tests/unit/fakes/test_in_memory_repositories.py during Phase 6 (quarantined strictly for Phase 7).</anti_target>
    <anti_target>Do NOT add new fields or optional attributes to DTOs or domain models as drive-by fixes (ban drive-by schema mutations).</anti_target>
    <anti_target>Do NOT use duck-typing, naked dictionaries, or permissive fallback chains in modernized tests.</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census A and I check across backend_v2/tests excluding tests/unit/fakes/ asserting 0 matches.</action>
    <action>Execute Census D check across backend_v2/tests asserting 0 matches.</action>
    <action>Execute Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Execute SDUI Semantic Parity: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
  </validation_gate>
</execution_protocol>
```
