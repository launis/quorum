# Phase 6: Test Persistence Migration — Workers, API & Integration

**Overview:** Migrate the remaining 198 census A assignments, 21 census D keyword-injected repository mocks, and 50 census F string-target repository patches across worker, API, and integration test suites, binding each patch return_value to typed in-memory repositories.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L501-L523] Phase 6: Test Persistence Migration — Workers, API & Integration

**Target Files:**
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

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 5 completed all orchestrator and DAG test persistence migrations.</action>
    <action>Look forward: Verify that migrating worker and integration test patches achieves Census A = 0, Census I = 0, Census D = 0, Census F = 0 across the entire test suite, satisfying the mandatory pre-condition for Phase 7 mock-emulation sunset.</action>
    <constraint>If any unmapped repository import or patch target remains, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/06_phase6_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Census commands A, B, C, and I over backend_v2/tests excluding fakes return 0 matches.</item>
    <item>Census commands D, F, and K over the full backend_v2/tests tree return 0 matches.</item>
    <item>Universal audit loop uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict passes.</item>
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
  </anti_targets>

  <validation_gate>
    <action>Execute Global Census A, B, C, I scan over backend_v2/tests/ asserting 0 matches outside fakes.</action>
    <action>Execute Global Census D, F, K scan over backend_v2/tests/ asserting 0 matches.</action>
    <action>Execute Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
