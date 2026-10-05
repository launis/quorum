# Phase 5: Test Persistence Migration — Orchestrator & DAG

**Overview:** Migrate 162 census A assignments, 10 census B attribute replacements, 2 fixtures, 152 census D keyword-injected repository mocks, and 1 census X `cast(Any, ...)` across DAG executor, strategy, and concurrency tests.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L474-L500] Phase 5: Test Persistence Migration — Orchestrator & DAG

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

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 4 migrated service, studio, execution, and database test persistence doubles to typed in-memory repositories.</action>
    <action>Look forward: Verify that migrating orchestrator and DAG test persistence doubles isolates the final persistence mocks to worker tests in Phase 6.</action>
    <constraint>If any DAG execution failure or unmapped step state occurs, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/05_phase5_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Census commands A, B, C, I, D, and X restricted to the 20 target files return 0 matches.</item>
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
    <anti_target>Do NOT delete DynamicRepoMethod or InMemoryBlueprintTransformerRepository during Phase 5 (quarantined strictly for Phase 7).</anti_target>
    <anti_target>Do NOT modify worker tests during Phase 5 (quarantined strictly for Phase 6).</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census A, B, C, I, D, X check on Phase 5 targets asserting 0 matches.</action>
    <action>Execute Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
