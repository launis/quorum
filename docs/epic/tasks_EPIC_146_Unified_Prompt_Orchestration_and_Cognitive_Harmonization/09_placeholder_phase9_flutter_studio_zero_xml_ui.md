# Phase 9: Flutter Studio Zero-XML UI Modernization

**Overview:** Update Flutter Studio PromptBlockBuilderView form dispatcher using Dart 3 pattern matching to render Zero-XML structured form inputs (Objective, Evaluation Rules dynamic list, Banned Concepts dynamic list, Role Enforcement, and live Compiled Prompt Preview), streamline step builder criteria selection, and update localizations.
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/step_builder_view.dart]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md#L372-L378] Phase 9: Flutter Studio Zero-XML UI Modernization

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 8. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart] and @[client_app_v2/lib/features/studio/views/step_builder_view.dart].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `prompt_block_builder_view.dart` updated with Dart 3 switch expression destructuring for polymorphic blocks.
    - [ ] Zero-XML form sections rendered for Objective, Evaluation Rules list, Banned Concepts list, and Role Enforcement.
    - [ ] Live compiled prompt preview modal/sheet integrated.
    - [ ] Step criteria block selection list streamlined in `step_builder_view.dart`.
    - [ ] Localization strings added in `app_en.arb` and `app_fi.arb`.
    - [ ] Quality gate `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart --build` passes.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_matrix_boolean_evaluation_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_pipeline.md]</knowledge_item>
    <knowledge_item>@[ki_strict_sdui_serialization.md]</knowledge_item>
    <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_adapter_pattern.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/step_builder_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT ask users to input XML tags manually in UI forms.
    - Do NOT use hardcoded hex colors or magic double spacing.
  </anti_targets>

  <step id="1" name="Zero-XML UI Forms &amp; View Alignment">
    <action>In @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]: Update form dispatcher using Dart 3 pattern matching to render structured form sections for Zero-XML fields.</action>
    <action>In @[client_app_v2/lib/features/studio/views/step_builder_view.dart]: Streamline step criteria block selection list.</action>
    <action>Add localization keys in `client_app_v2/lib/l10n/app_en.arb` and `client_app_v2/lib/l10n/app_fi.arb` and run `cd client_app_v2; flutter gen-l10n`.</action>
  </step>

  <validation_gate>
    <action>Generate Localization: `cd client_app_v2; flutter gen-l10n`</action>
    <action>Execute Frontend Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart --build`</action>
  </validation_gate>
</execution_protocol>
```
