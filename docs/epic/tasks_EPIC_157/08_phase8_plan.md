# Phase 8: Universal Quality Gate Stage 10 Integration & Full-Duplex Client Parity

**Overview:** Wire `scripts/audit_dict_eradication.py backend_v2 --strict` as Stage 10/10 of `scripts/backend_audit_loop.py` and type the Flutter producers and consumers of retyped backend fields under full-duplex DTO parity.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L543-L556] Phase 8: Universal Quality Gate Stage 10 Integration & Full-Duplex Client Parity

**Target Files:**
- `[MODIFY]` @[scripts/backend_audit_loop.py#L282-L477]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]
- `[MODIFY]` @[scripts/audit_dto_parity.py]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/step_simulation.dart#L60-L70]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart#L12-L45]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/mcp_gateway.dart#L14-L22]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 7 eradicated DynamicRepoMethod and InMemoryBlueprintTransformerRepository and hardened QGR014 at FATAL severity.</action>
    <action>Look forward: Verify that wiring Stage 10/10 in backend_audit_loop.py and synchronizing Flutter models locks client-server parity before suppression eradication in Phases 9-10.</action>
    <constraint>If DTO parity fails or Stage 10 fails to halt CI on violations, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/08_phase8_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>backend_audit_loop.py executes 10/10 mandatory stages cleanly.</item>
    <item>audit_dict_eradication.py backend_v2 --strict runs as Stage 10/10.</item>
    <item>Flutter Studio simulation models mirror backend IngressInputValue and open schema types.</item>
    <item>uv run python scripts/flutter_audit_loop.py client_app_v2/ --build passes.</item>
    <item>uv run python scripts/audit_dto_parity.py passes.</item>
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
    <anti_target>Do NOT modify client_app_v2 execution record models during Phase 8 (quarantined strictly for Phase 12).</anti_target>
    <anti_target>Do NOT remove # noqa or # type: ignore comments during Phase 8 (quarantined strictly for Phases 9-10).</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute 10-Stage Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Execute Dict Audit: `uv run python scripts/audit_dict_eradication.py backend_v2 --strict`.</action>
    <action>Execute Flutter Audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
    <action>Execute DTO Parity: `uv run python scripts/audit_dto_parity.py`.</action>
  </validation_gate>
</execution_protocol>
```
