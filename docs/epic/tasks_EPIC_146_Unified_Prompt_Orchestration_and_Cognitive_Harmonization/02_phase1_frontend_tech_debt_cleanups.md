# Phase 1: Pre-Requisite Technical Debt Cleanups (Frontend Studio Views)

**Overview:** Remediate 1-hop technical debt and legacy anti-patterns across Studio UI views and modals: eliminate dynamic step typing, GoRouter extra passing, when-branching, SizedBox.shrink, translation fallback chains, hardcoded hex colors, inlined language ternaries, ad-hoc ID generators, and hardcoded spacing doubles.
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L23-L38]
- `[MODIFY]` @[client_app_v2/lib/router/router.dart#L226-L232]
- `[MODIFY]` @[client_app_v2/lib/router/router.dart#L284-L298]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L445]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L509]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L243]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L390-L395]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L569-L573]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1 Backend. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L23-L38], @[client_app_v2/lib/router/router.dart#L297], and @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L243].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `final dynamic step;` replaced with `final String stepId;` in @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L23-L38].
    - [ ] GoRouter `$extra ?? const {}` removed for `StepBuilderView` in @[client_app_v2/lib/router/router.dart#L284-L298] and `TypedGoRoute<StepEditRoute>(path: 'step/edit/:id')`, routing purely by `stepId` (`StepEditRoute(id: ...)` in @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L445] and @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L509]).
    - [ ] `formState.when(...)` replaced with Dart 3 native `switch (formState)` pattern matching in @[client_app_v2/lib/features/studio/views/step_builder_view.dart].
    - [ ] `const SizedBox.shrink()` (line 557) eradicated and replaced with Fail-Fast validation.
    - [ ] Translation fallback chains `translations[currentLocale] ?? translations['fi'] ?? ...` in @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L569-L573] eradicated and replaced with Fail-Fast `AppException.validation`.
    - [ ] Hardcoded hex color `const Color(0xFF2E7D32)` in @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L243] replaced with `Theme.of(context).colorScheme.primaryContainer`.
    - [ ] Inlined language ternary in @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L390-L395] migrated to `l10n.matrixCategoryLockedHelper`.
    - [ ] Hardcoded tooltips migrated to `.arb` localization and fallback chain at line 103 eradicated.
    - [ ] Timestamp ID generator in `prompt_block_builder_view.dart` replaced with standard UUID generator.
    - [ ] Modals (@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart], @[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]) hardcoded strings migrated to `app_en.arb` and `app_fi.arb`, ad-hoc UUIDs replaced with `TDAAssertion.create()`, and spacing doubles replaced with `AppSpacing`.
    - [ ] Spacing doubles in @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart] replaced with `AppSpacing` tokens.
    - [ ] Localization and flutter quality gate `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/step_builder_view.dart --build` passes.
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
    <frontend>@[client_app_v2/lib/features/studio/views/step_builder_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/router/router.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `client_app_v2/lib/features/studio/models/prompt_block.dart` Freezed models in Phase 1 (reserved for Phase 4).
    - Do NOT modify Python backend files in this frontend plan.
    - Do NOT add loose fallback defaults or `SizedBox.shrink()` when data is missing.
  </anti_targets>

  <step id="1" name="Step Builder View & Router Cleanups">
    <action>In @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L23-L38], replace `final dynamic step;` and `if (step is NodeStrategy) ... else if (step is Map) ...` with `final String stepId;`.</action>
    <demolish>REMOVE: `final dynamic step;` and runtime dynamic type checks at @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L23-L38]. REPLACE WITH: strictly typed `final String stepId;`.</demolish>
    <action>In @[client_app_v2/lib/router/router.dart#L226-L232] and @[client_app_v2/lib/router/router.dart#L284-L298], eliminate `$extra ?? const {}` passing for `StepBuilderView`, routing purely by `stepId` (`TypedGoRoute<StepEditRoute>(path: 'step/edit/:id')` and `StepBuilderView(stepId: id)`). Update callers in @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L445] and @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L509] to pass `id` directly (`StepEditRoute(id: draft.id).go(context)` and `StepEditRoute(id: blueprintId).go(context)`).</action>
    <demolish>REMOVE: `$extra ?? const {}` object passing at @[client_app_v2/lib/router/router.dart#L297]. REPLACE WITH: pure ID routing parameter `StepBuilderView(stepId: id)`.</demolish>
    <action>In @[client_app_v2/lib/features/studio/views/step_builder_view.dart], replace `formState.when(...)` with Dart 3 native `switch (formState)` pattern matching.</action>
    <demolish>REMOVE: `formState.when(...)` pattern at @[client_app_v2/lib/features/studio/views/step_builder_view.dart]. REPLACE WITH: Dart 3 native `switch (formState)`.</demolish>
    <action>In @[client_app_v2/lib/features/studio/views/step_builder_view.dart], eradicate `const SizedBox.shrink()` (line 557), replacing with Fail-Fast validation.</action>
    <demolish>REMOVE: `const SizedBox.shrink()` at @[client_app_v2/lib/features/studio/views/step_builder_view.dart]. REPLACE WITH: Fail-Fast validation.</demolish>
    <action>In @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L569-L573], eradicate banned fallback chains `translations[currentLocale] ?? translations['fi'] ?? translations['en'] ?? toolId` (lines 569-573, 764-766, 851-853), replacing with Fail-Fast `AppException.validation`.</action>
    <demolish>REMOVE: `translations[currentLocale] ?? translations['fi'] ?? translations['en'] ?? toolId` at @[client_app_v2/lib/features/studio/views/step_builder_view.dart#L569-L573]. REPLACE WITH: Fail-Fast `AppException.validation`.</demolish>
    <constraint invariant="go_router_extra_ban">Routing must pass only string IDs; target views pull state cleanly via Riverpod.</constraint>
  </step>

  <step id="2" name="Prompt Block Builder View Cleanups">
    <action>In @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L243], eliminate hardcoded hex color `const Color(0xFF2E7D32)`, replacing with `Theme.of(context).colorScheme.primaryContainer`.</action>
    <demolish>REMOVE: `const Color(0xFF2E7D32)` at @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L243]. REPLACE WITH: `Theme.of(context).colorScheme.primaryContainer`.</demolish>
    <action>In @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L390-L395], eliminate inlined language ternary, migrating to `l10n.matrixCategoryLockedHelper`.</action>
    <demolish>REMOVE: inlined language ternary at @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L390-L395]. REPLACE WITH: `l10n.matrixCategoryLockedHelper`.</demolish>
    <action>In @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart], migrate hardcoded tooltips (`'Back to Studio'`, `'Simulate Prompt'`) to `.arb` localization.</action>
    <action>In @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart], eliminate fallback chain `trans['fi'] ?? trans['en'] ?? payload.id` (line 103).</action>
    <demolish>REMOVE: `trans['fi'] ?? trans['en'] ?? payload.id` fallback chain at @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]. REPLACE WITH: Fail-Fast validation.</demolish>
    <action>In @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart], replace timestamp ID `'blk_${DateTime.now().millisecondsSinceEpoch}'` with standard UUID generator.</action>
    <demolish>REMOVE: timestamp ID generation `'blk_${DateTime.now().millisecondsSinceEpoch}'` at @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]. REPLACE WITH: standard UUID generator.</demolish>
    <constraint invariant="design_token_absolute_rule">Colors and spacing must use theme tokens and AppSpacing.</constraint>
  </step>

  <step id="3" name="Modals & Components Hygiene">
    <action>In @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart] and @[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart], migrate all hardcoded UI strings to `app_en.arb` and `app_fi.arb`.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart], replace ad-hoc ID creation `'tda_${Uuid().v4().replaceAll('-', '')}'` with `TDAAssertion.create()`.</action>
    <demolish>REMOVE: ad-hoc ID creation `'tda_${Uuid().v4().replaceAll('-', '')}'` at @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]. REPLACE WITH: `TDAAssertion.create()`.</demolish>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart] and @[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart], replace magic spacing doubles with `AppSpacing` tokens.</action>
    <action>In @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart], replace magic spacing doubles with `AppSpacing` tokens.</action>
    <action>Update @[client_app_v2/lib/l10n/app_en.arb] and @[client_app_v2/lib/l10n/app_fi.arb] with new localization entries and run `cd client_app_v2; flutter gen-l10n`.</action>
    <constraint invariant="no_magic_strings_l10n">All UI text must be evaluated via AppLocalizations.</constraint>
  </step>

  <validation_gate>
    <action>Generate Localization: `cd client_app_v2; flutter gen-l10n`</action>
    <action>Execute Frontend Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/step_builder_view.dart --build`</action>
    <action>Execute Flutter Tests: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/components/bars_matrix_builder_test.dart --test`</action>
  </validation_gate>
</execution_protocol>
```
