# Phase 4: Flutter Studio Client Harmonization

**Overview:** Update frontend enums with SystemUiConstraints.tdaConceptMinLength(10), update Freezed model MatrixClaim by removing aiDescription, enforce 32 hex char tdaId format, align modal dialogs and BARS matrix builder, and run Freezed code generation.
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/core/models/enums.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/prompt_block.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]

Source: @[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md#L229-L242] Phase 4: Flutter Studio Client Harmonization

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 3. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[client_app_v2/lib/core/models/enums.dart] and @[client_app_v2/lib/features/studio/models/prompt_block.dart].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `tdaConceptMinLength(10)` added to `SystemUiConstraints` enum in @[client_app_v2/lib/core/models/enums.dart].
    - [ ] `required String aiDescription` removed from `MatrixClaim` in @[client_app_v2/lib/features/studio/models/prompt_block.dart].
    - [ ] `TDAAssertion.create` factory updated to produce 32 hex chars (`tda_$uuidHex`).
    - [ ] Freezed code generation executed via `dart run build_runner build --delete-conflicting-outputs`.
    - [ ] Scale editor modal, row editor modal, BARS matrix builder, and prompt block builder view aligned with new models.
    - [ ] Quality gate `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build` passes.
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
    <frontend>@[client_app_v2/lib/core/models/enums.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/prompt_block.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]</frontend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT re-introduce `aiDescription` in Dart models.
    - Do NOT mix Python backend edits in this plan.
    - Do NOT create ad-hoc UUID strings without `TDAAssertion.create()`.
  </anti_targets>

  <step id="1" name="Centralized Enums &amp; Freezed Models Update">
    <action>Modify @[client_app_v2/lib/core/models/enums.dart]: Add `tdaConceptMinLength(10)` to `SystemUiConstraints` enum.</action>
    <action>Modify @[client_app_v2/lib/features/studio/models/prompt_block.dart]: Replace `tdaId: 'tda_${uuidHex.substring(0, 16)}'` with `tdaId: 'tda_$uuidHex'` in `TDAAssertion.create`, and remove `required String aiDescription` from `MatrixClaim` Freezed model.</action>
    <demolish>REMOVE: `aiDescription` from `MatrixClaim` Freezed model at @[client_app_v2/lib/features/studio/models/prompt_block.dart]. REPLACE WITH: 1:1 parity with backend `MatrixClaim`.</demolish>
    <action>Run build runner: `dart run build_runner build --delete-conflicting-outputs`.</action>
  </step>

  <step id="2" name="Studio Views Alignment &amp; Modal Hygiene">
    <action>Modify @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]: Instantiate `MatrixClaim` with `label` and `tdaAssertions` containing default `TDAAssertion.create()`, route editing directly to assertion `conceptDescription`, and enforce validator `value.trim().length >= SystemUiConstraints.tdaConceptMinLength.value`.</action>
    <action>Modify @[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]: Align with new models.</action>
    <action>Modify @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]: Replace display of `claim.aiDescription` with `claim.tdaAssertions.first.conceptDescription`.</action>
    <action>Modify @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]: Update default `MatrixClaim` instantiation to omit `aiDescription` and supply valid `tdaAssertions`.</action>
  </step>

  <validation_gate>
    <action>Execute Frontend Code Generation: `dart run build_runner build --delete-conflicting-outputs`</action>
    <action>Execute Frontend Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build`</action>
  </validation_gate>
</execution_protocol>
```
