# Phase 13: Zero-Bypass Final Gate & Knowledge Synchronization

**Overview:** Re-run every census command of the Test Persistence Census Table and the Residual Ledger through the 10-stage `scripts/backend_audit_loop.py` and `scripts/flutter_audit_loop.py`, verifying all ceilings are 0, and synchronize the Knowledge Base.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L632-L642] Phase 13: Zero-Bypass Final Gate & Knowledge Synchronization

**Target Files:**
- `[MODIFY]` @[scripts/audit_warning_baseline.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify all 12 prior phases completed with 100% test and audit gate pass rates.</action>
    <action>Look forward: Verify final lock of all residual ceilings to 0 in audit_warning_baseline.py and execute /tier7-describe-architecture knowledge synchronization.</action>
    <constraint>If any census command returns non-zero, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/13_phase13_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Census commands A, B, C, I, D, F, K, X, N, T, P, M, R, and S return 0.</item>
    <item>Final lock in scripts/audit_warning_baseline.py asserts all residual ceilings at strictly 0.</item>
    <item>uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict passes all 10 stages clean.</item>
    <item>uv run python scripts/flutter_audit_loop.py client_app_v2/ --build passes.</item>
    <item>Execute knowledge synchronization command /tier7-describe-architecture.</item>
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
    <anti_target>Do NOT introduce ad-hoc census exemptions or elevate any ceiling above 0.</anti_target>
    <anti_target>Do NOT modify runtime application business logic during final baseline locking.</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census Suite: All census checks report 0 residual violations.</action>
    <action>Execute 10-Stage Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` passes 10/10 stages.</action>
    <action>Execute Flutter Audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` passes.</action>
  </validation_gate>
</execution_protocol>
```
