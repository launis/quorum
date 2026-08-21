# Phase 4: Studio Workflow & Step Blueprint UX Restructuring (3-Zone Management & Core Protection)

**Overview:** Restructures Studio Workflow Builder step view into 3 distinct zones (Zone A Input Anchor, Zone B Dynamic Specialists, Zone C Pipeline Funnel Anchors), enforces system core protection in Step Blueprint Library, adds dual-axis localized ARB strings, and eliminates hardcoded Finnish text and magic numbers.
**Source:** @[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md#L193-L251] Phase 4: Studio Workflow & Step Blueprint UX Restructuring (3-Zone Management & Core Protection)
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb#L1075-L1125]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb#L1620-L1670]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L1-L335]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L108-L140]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L219-L295]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 3. Verify that backend services and APIs are fully functional.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true for Flutter studio workflow views and step builder views.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] Localized strings added to `app_fi.arb` and `app_en.arb` for 3-zone workflow management and core badges.
    - [ ] `WorkflowStepCard` displays 3 distinct, categorized sections with localized explanatory text and zero hardcoded strings.
    - [ ] Blueprint locking and delete prohibition implemented for system core steps in `WorkflowStepCard` and `StepBuilderView`.
    - [ ] Hardcoded hex colors and magic numbers removed from `step_builder_view.dart`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_neuro_symbolic_agentic_workflow.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
  </required_context_rules>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/step_builder_view.dart]</frontend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT hardcode user-facing strings or hex colors in Flutter widgets.
    - Do NOT bypass Riverpod provider patterns.
  </anti_targets>

  <step id="1" name="Deferred Phase Implementation">
    <action>[DEFERRED_TO_TIER_1_RE_PLANNING] Detailed execution steps will be generated upon completion of Phase 2 based on updated codebase state. Refer to Epic source: @[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md#L193-L251].</action>
  </step>

  <validation_gate>
    <action>Execute Flutter Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart --test`</action>
    <action>Execute Step Builder Audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/step_builder_view.dart --test`</action>
  </validation_gate>
</execution_protocol>
```
