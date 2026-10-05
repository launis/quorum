# Phase 4: Test Persistence Migration — Services, Studio, Execution & Database

**Overview:** Migrate 419 census A assignments, 45 census B attribute replacements, 7 census C object patches, 6 fixtures, 269 census D keyword-injected repository mocks, migrate 2 import-only files, delete `dict_to_obj`, and replace driver-level mocks with a real `TinyDBDriver` over `tmp_path`.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L444-L473] Phase 4: Test Persistence Migration — Services, Studio, Execution & Database

**Target Files:**
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint.py#L141-L164]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_execution.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_execution_resumability.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_report_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_chat_parser.py#L20-L23]
- `[MODIFY]` @[backend_v2/tests/unit/services/execution/test_ingress_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/execution/test_lifecycle_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_output_profile_service.py#L18-L20]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L42-L44]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L47-L49]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L52-L54]
- `[MODIFY]` @[backend_v2/tests/unit/test_auth.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_security.py#L20-L22]
- `[MODIFY]` @[backend_v2/tests/unit/test_usage_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_repo_deletion.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_repositories_v2.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_dependencies.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/execution/test_override_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/execution/test_stream_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_system_config_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_agent.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_task_blueprint.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/execution/test_legacy_render_service.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 3 migrated all hook and LLM persistence doubles to typed in-memory repositories.</action>
    <action>Look forward: Verify that migrating services, studio, and execution tests isolates remaining mocks to orchestrator (Phase 5) and workers (Phase 6).</action>
    <constraint>If any service regression or unmapped repository call occurs, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/04_phase4_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Census commands A, B, C, I, and D restricted to the 23 target files return 0 matches.</item>
    <item>dict_to_obj helper is deleted and Select-String reports 0 occurrences across backend_v2/tests.</item>
    <item>Real TinyDBDriver over tmp_path verifies repository persistence in test_repositories_v2.py.</item>
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
    <anti_target>Do NOT delete DynamicRepoMethod or InMemoryBlueprintTransformerRepository during Phase 4 (quarantined strictly for Phase 7).</anti_target>
    <anti_target>Do NOT modify orchestrator or worker persistence doubles during Phase 4 (quarantined strictly for Phases 5-6).</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census A, B, C, I, D check on Phase 4 targets asserting 0 matches.</action>
    <action>Execute dict_to_obj elimination verification across tests.</action>
    <action>Execute Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
