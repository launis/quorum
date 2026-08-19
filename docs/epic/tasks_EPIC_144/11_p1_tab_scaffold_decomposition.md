# Phase 1-B: 3-Tab Scaffold Decomposition

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 1, "Tab Architecture & UI Scaffold" (L368-L430) and 6-Step Pipeline Step 5 (L256-L260)
**Scope:** Frontend Flutter/Dart views only

**Overview:** Decompose the 899-line monolithic `output_profile_crud_view.dart` into a 3-tab `TabBarView` architecture: General Tab, Scoring & Extensions Tab, and Layouts Tab. Each extracted tab widget MUST be ≤200 lines per the God Code Prevention mandate.

**Target Files:**
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]`
- `[MODIFY]` `@[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart]`

**Context Files (Read-Only):**
- `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]` — Form state controller (`outputProfileFormProvider`)
- `@[client_app_v2/lib/features/studio/models/output_profile.dart]` — Freezed model
- `@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]` — Nested layout editor

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Plan 10 (Golden Master Baseline) is complete — characterization tests pass green.</action>
    <action>Look forward: Verify @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] is still the monolithic ~899-line file and has NOT been decomposed yet.</action>
    <constraint>If Golden Master tests do not pass, STOP. Do NOT decompose without a behavioral safety net.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\02_flutter_desktop.md]</rule>
    <rule>@[.agents\rules\04_directory_reference.md]</rule>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_ast_guardrail_testing.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/ — Do NOT touch any Python files</file>
    <file>client_app_v2/lib/features/studio/controllers/ — Do NOT modify controllers in this plan</file>
    <file>client_app_v2/lib/features/studio/models/ — Do NOT modify Freezed models (already done in Plan 07)</file>
  </anti_targets>

  <dod_checklist>
    <item>output_profile_crud_view.dart reduced to a TabBar/TabBarView shell ≤200 lines.</item>
    <item>[NEW] profile_general_tab.dart contains profile identity fields (id, slug, workflowId, name, description, customPreface) — ≤200 lines.</item>
    <item>[NEW] profile_scoring_tab.dart contains scoring & extensions configuration (displayScale, strictnessLevel, scoringStrategy, visibleMetadata, maxExtensionItems, visibleBlockExtensions, visibleWorkflowExtensions) — ≤200 lines.</item>
    <item>[NEW] profile_layouts_tab.dart contains layout editor and targetBlockOrder configuration — ≤200 lines.</item>
    <item>Eradicate Phase 9 anti-patterns: untyped AsyncValue&lt;List&lt;dynamic&gt;&gt; (R82), hardcoded hex colors (R83), hardcoded padding doubles (R84), and silent shrink widgets (R81).</item>
    <item>Golden Master characterization tests in output_profile_crud_view_test.dart updated for tab navigation and passing 100% green.</item>
    <item>Flutter analyze reports zero new lints or warnings in modified/new files.</item>
  </dod_checklist>

  <step id="1" name="MAP MONOLITHIC VIEW STRUCTURE &amp; FIELD BOUNDARIES">
    <action>Analyze @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] (899 lines) to establish exact field allocation across the 3 tabs:

**Tab 1 - General (`ProfileGeneralTab`):**
- Profile ID (`TextFormField`, read-only)
- URL Slug (`TextFormField`, updating `payload.slug`)
- Workflow Selector (`DropdownButtonFormField&lt;String&gt;`, listing workflows from `workflowsControllerProvider`, updating `payload.workflowId`)
- Display Name (`I18nTextField`, updating `payload.name`)
- Description (`I18nTextField`, updating `payload.description`)
- Custom Preface (`I18nTextField`, updating `payload.customPreface`)

**Tab 2 - Scoring &amp; Extensions (`ProfileScoringTab`):**
- Display Scale (`DropdownButton&lt;DisplayScale&gt;`, updating `payload.displayScale`)
- Strictness Level (`DropdownButton&lt;int&gt;` with `StrictnessLevel` options, updating `payload.strictnessLevel`)
- Scoring Strategy (`DropdownButton&lt;ScoringStrategy?&gt;`, updating `payload.scoringStrategy`)
- Identity Metadata (`CheckboxListTile`s for `visibleMetadata`: date, organization, user, scoring_engine, strictness, cost, tokens)
- Max Extension Items (`TextFormField` with integer validation, updating `payload.maxExtensionItems`)
- Block-Level Extensions (`CheckboxListTile`s for `visibleBlockExtensions` filtered by `workflowAvailableExtensionsProvider(workflowId)`)
- Workflow-Level Extensions (`CheckboxListTile`s for `visibleWorkflowExtensions`)

**Tab 3 - Report Structure / Layouts (`ProfileLayoutsTab`):**
- Workflow Unselected Warning Card (shown when `workflowId.isEmpty`)
- OutputLayoutBlock List Editor (`LayoutEditorCard`, passing `layouts`, `allowedBlockIds`, `promptBlocksState`)
- Target Block Order (`ReorderableListView` for `payload.targetBlockOrder`)</action>
    <constraint>Do NOT modify any code during Step 1. This is analysis only.</constraint>
  </step>

  <step id="2" name="EXTRACT GENERAL TAB">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart]:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Tab 1: Profile identity, URL slug, workflow binding, and rich text preface.
class ProfileGeneralTab extends ConsumerWidget {
  final String id;
  const ProfileGeneralTab({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.watch(outputProfileFormProvider(id));
    final workflowsState = ref.watch(workflowsControllerProvider);

    final payload = formState.value;
    if (payload == null) return const SizedBox.shrink();

    void updatePayload(OutputProfile p) {
      ref.read(outputProfileFormProvider(id).notifier).updatePayload(p);
    }

    return ListView(
      padding: AppSpacing.p16,
      children: [
        Card(
          child: Padding(
            padding: AppSpacing.p16,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextFormField(
                  initialValue: payload.id,
                  decoration: InputDecoration(
                    labelText: l10n.profileIdLabel,
                    border: const OutlineInputBorder(),
                  ),
                  readOnly: true,
                ),
                AppSpacing.h16,
                TextFormField(
                  initialValue: payload.slug,
                  decoration: InputDecoration(
                    labelText: l10n.urlSlugLabel,
                    border: const OutlineInputBorder(),
                  ),
                  onChanged: (val) {
                    updatePayload(payload.copyWith(slug: val.trim()));
                  },
                ),
                AppSpacing.h16,
                switch (workflowsState) {
                  AsyncData(value: final rawWorkflows) =&gt; Builder(
                    builder: (context) {
                      final workflows = rawWorkflows.cast&lt;Workflow&gt;();
                      String? currentValue = payload.workflowId.isNotEmpty
                          ? payload.workflowId
                          : null;
                      final bool hasValidValue =
                          currentValue != null &amp;&amp;
                          (workflows.any((w) =&gt; w.id == currentValue) ||
                              currentValue == '');
                      return DropdownButtonFormField&lt;String&gt;(
                        initialValue: hasValidValue ? currentValue : null,
                        isExpanded: true,
                        decoration: InputDecoration(
                          labelText: l10n.workflowIdBindingLabel,
                          border: const OutlineInputBorder(),
                        ),
                        hint: Text(l10n.selectWorkflowHint),
                        items: [
                          DropdownMenuItem(
                            value: '',
                            child: Text(
                              l10n.noneDefaultLabel,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          ...workflows.map((flow) {
                            final flowId = flow.id;
                            final localeCode = Localizations.localeOf(context).languageCode;
                            final displayName = flow.name.get(localeCode);
                            return DropdownMenuItem(
                              value: flowId,
                              child: Text(
                                '$displayName ($flowId)',
                                overflow: TextOverflow.ellipsis,
                              ),
                            );
                          }),
                        ],
                        onChanged: (val) {
                          if (val != null) {
                            updatePayload(payload.copyWith(workflowId: val));
                          }
                        },
                      );
                    },
                  ),
                  AsyncLoading() =&gt; const Center(child: CircularProgressIndicator()),
                  AsyncError(:final error) =&gt; Text(
                    l10n.studioViewsErrorLoadingWorkflows(error.toString()),
                  ),
                },
                AppSpacing.h16,
                I18nTextField(
                  label: l10n.profileDisplayNameLabel,
                  initialData: payload.name,
                  onChanged: (val) {
                    updatePayload(payload.copyWith(name: val));
                  },
                ),
                AppSpacing.h16,
                I18nTextField(
                  label: l10n.profileDescriptionLabel,
                  initialData: payload.description,
                  onChanged: (val) {
                    final isEmpty =
                        val.translations.isEmpty ||
                        val.translations.values.every((v) =&gt; v.trim().isEmpty);
                    updatePayload(
                      payload.copyWith(description: isEmpty ? null : val),
                    );
                  },
                ),
                AppSpacing.h16,
                I18nTextField(
                  label: l10n.customPrefaceLabel,
                  initialData: payload.customPreface,
                  onChanged: (val) {
                    final isEmpty =
                        val.translations.isEmpty ||
                        val.translations.values.every((v) =&gt; v.trim().isEmpty);
                    updatePayload(
                      payload.copyWith(customPreface: isEmpty ? null : val),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
```</action>
    <constraint invariant="200_line_cap">This file MUST be ≤200 lines.</constraint>
    <constraint invariant="zero_behavioral_change">Form fields render identically to their current functionality with zero regressions.</constraint>
  </step>

  <step id="3" name="EXTRACT SCORING TAB">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart]:
Extract displayScale, strictnessLevel, scoringStrategy, visibleMetadata, maxExtensionItems, visibleBlockExtensions, and visibleWorkflowExtensions.
The maxExtensionItems input MUST validate `parsed &gt;= 1 &amp;&amp; parsed &lt;= 100` and display `l10n.extensionItemsMustBeIntError` on error.</action>
    <constraint invariant="200_line_cap">This file MUST be ≤200 lines.</constraint>
  </step>

  <step id="4" name="EXTRACT LAYOUTS TAB">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]:
Extract the workflow empty check warning card, `LayoutEditorCard`, and `ReorderableListView` for `targetBlockOrder`.</action>
    <constraint invariant="200_line_cap">This file MUST be ≤200 lines.</constraint>
  </step>

  <step id="5" name="REFACTOR CRUD VIEW TO TAB SHELL">
    <action>Modify @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] to become a lightweight shell:
1. Wrap the Scaffold in `DefaultTabController(length: 3, ...)`.
2. Add `bottom: TabBar(tabs: [Tab(text: l10n.profileTabGeneral), Tab(text: l10n.profileTabXai), Tab(text: l10n.profileTabLayouts)])` to the AppBar.
3. Replace the body with `Form(key: formKey, child: TabBarView(children: [ProfileGeneralTab(id: id), ProfileScoringTab(id: id), ProfileLayoutsTab(id: id)]))`.
4. Keep the AppBar save and delete actions, replacing hardcoded colors (`Color(0xFF2E7D32)`) with Theme tokens and hardcoded EdgeInsets with `AppSpacing`.
5. DELETE all extracted form field widgets and helper methods from this file.</action>
    <constraint invariant="200_line_cap">The refactored file MUST be ≤200 lines.</constraint>
    <constraint invariant="zero_behavioral_change">Save, delete, form validation, and data persistence remain 100% intact.</constraint>
  </step>

  <step id="6" name="UPDATE &amp; VERIFY GOLDEN MASTER TESTS">
    <action>Update @[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart] to assert tab switching for fields on Tab 2 (Extensions/Scoring) and Tab 3 (Layouts).
Re-run the Golden Master characterization test suite:
`uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart --test`</action>
    <constraint>ALL 10 Golden Master tests MUST pass green.</constraint>
  </step>

  <step id="7" name="LINE COUNT VERIFICATION">
    <action>Verify all 4 files satisfy the ≤200 line cap:
```powershell
Get-Content client_app_v2\lib\features\studio\views\output_profile_crud_view.dart | Measure-Object -Line
Get-Content client_app_v2\lib\features\studio\views\widgets\profile\tabs\profile_general_tab.dart | Measure-Object -Line
Get-Content client_app_v2\lib\features\studio\views\widgets\profile\tabs\profile_scoring_tab.dart | Measure-Object -Line
Get-Content client_app_v2\lib\features\studio\views\widgets\profile\tabs\profile_layouts_tab.dart | Measure-Object -Line
```</action>
    <constraint invariant="200_line_cap">ALL 4 files MUST report ≤200 lines. If any exceeds 200, further decompose into sub-widgets.</constraint>
  </step>

  <validation_gate>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/output_profile_crud_view.dart --build</check>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart --test — Golden Master parity</check>
    <check>All 4 target files ≤200 lines</check>
    <check>flutter analyze reports zero new lints in modified/new files</check>
  </validation_gate>
</execution_protocol>
```

