# Phase 6: SDUI Boundary & Presentation Pipeline Hardening

**Overview:** Structured placeholder plan for Phase 6. Hardening SDUI models, legacy render service, SDUI mapper service, and Flutter client API consumers. Complete demolition of legacy UiSection and extraction of presentation rules into strongly typed DTOs.
**Source:** @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] Phase 6: SDUI Boundary & Presentation Pipeline Hardening
**Target Files:**
- `[MODIFY]` @[backend_v2/models/view/sdui.py]
- `[MODIFY]` @[backend_v2/services/sdui_mapper_service.py]
- `[MODIFY]` @[backend_v2/services/execution/legacy_render_service.py]
- `[NEW]` @[backend_v2/models/dtos/sdui_rules.py]
- `[NEW]` @[backend_v2/tests/unit/services/execution/test_legacy_render_service.py]
- `[MODIFY]` @[client_app_v2/lib/core/api/reports_client.dart]
- `[MODIFY]` @[client_app_v2/lib/core/api/execution_client.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 5 hardened prompt compiler and DAG executor DTOs.</action>
    <action>Look forward: Verify that Phase 7 live E2E tests validate complete UI and backend SDUI rendering.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/06_placeholder_phase6.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>Legacy model UiSection is completely demolished from @[backend_v2/models/view/sdui.py].</item>
    <item>SDUI presentation rules extracted into [NEW] @[backend_v2/models/dtos/sdui_rules.py] defining PrintableSourcesRulesDTO, PenaltiesRulesDTO, VarianceRulesDTO, and XaiAestheticsRulesDTO.</item>
    <item>Legacy render service operates exclusively with RenderExecutionResultDTO, StepOutputContentDTO, and ReportViewMetricsDTO.</item>
    <item>Flutter client models in reports_client.dart and execution_client.dart adhere strictly to typed contracts.</item>
    <item>Unit test suite established in [NEW] @[backend_v2/tests/unit/services/execution/test_legacy_render_service.py].</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
    <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do NOT alter raw Flutter widget styling or theme configurations.</forbidden>
    <forbidden>Do NOT re-introduce fallback dictionary parsing in SDUI adapters.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/models/view/sdui.py]</backend>
    <backend>@[backend_v2/services/sdui_mapper_service.py]</backend>
    <backend>@[backend_v2/services/execution/legacy_render_service.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/sdui_rules.py]</backend>
    <frontend>@[client_app_v2/lib/core/api/reports_client.dart]</frontend>
    <frontend>@[client_app_v2/lib/core/api/execution_client.dart]</frontend>
  </touched_artifacts>

  <step id="6.1" name="SDUI Model Modernization &amp; UiSection Demolition">
    <action>Demolish UiSection in @[backend_v2/models/view/sdui.py].</action>
    <action>Create [NEW] @[backend_v2/models/dtos/sdui_rules.py] defining PrintableSourcesRulesDTO, PenaltiesRulesDTO, VarianceRulesDTO, and XaiAestheticsRulesDTO.</action>
    <demolish>REMOVE: `UiSection` in @[backend_v2/models/view/sdui.py]. REPLACE WITH: typed SDUI block components.</demolish>
  </step>

  <step id="6.2" name="Legacy Render Service &amp; SDUI Mapper Hardening">
    <action>Refactor @[backend_v2/services/execution/legacy_render_service.py] and @[backend_v2/services/sdui_mapper_service.py] to use RenderExecutionResultDTO, StepOutputContentDTO, and ReportViewMetricsDTO.</action>
    <action>Create [NEW] @[backend_v2/tests/unit/services/execution/test_legacy_render_service.py] to lock render contracts.</action>
  </step>

  <step id="6.3" name="Client App Reports &amp; Execution Client Parity">
    <action>Update @[client_app_v2/lib/core/api/reports_client.dart] and @[client_app_v2/lib/core/api/execution_client.dart] to match strictly typed backend contracts.</action>
  </step>

  <validation_gate>
    <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/models/view/sdui.py --test</action>
    <action>Run flutter audit loop: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/core/api/reports_client.dart</action>
  </validation_gate>
</execution_protocol>
```
