# Phase 4: Studio Modals, Dialogs UX Hardening & E2E Quality Gates

**Overview:** Complete Quorum's desktop modal hardening and end-to-end quality gate verification as mandated in `@[ki_desktop_pro_tool_studio_ux.md]`. Intercept modal dismissals with `PopScope(canPop: false)` and serialization-based dirty checking to shield against uncommitted state loss, eradicate all modal SnackBar alerts in favor of inline canvas error banners, enforce modal min/max geometry bounds (480-1400px), author a comprehensive negative ISTQB test suite for `HumanOverrideDialog`, and execute the universal Flutter audit loop and Dart guardrails.
**Source:** @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md#L374-L411] Phase 4: Studio Modals, Dialogs UX Hardening & E2E Quality Gates
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L62-77]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/profile_editor_view.dart]
- `[NEW]` @[client_app_v2/test/features/execution/views/widgets/human_override_dialog_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/widgets/step_simulation_dialog_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 1, Phase 2, and Phase 3 completed zero permissive typing, SDUI performance optimization, and master view virtualization.</action>
    <action>Look forward: Verify that all Studio dialogs, editors, and quality gates pass 100% without deprecation or lint warnings.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_153_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute @[docs/epic/tasks_EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing/04_placeholder_phase4.md] @[docs/epic/EPIC_153_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>HumanOverrideDialog implements PopScope(canPop: false), focus unblur, and serialization dirty check (jsonEncode != initialJson).</item>
    <item>Zero modal SnackBar calls across touched dialogs (ScaffoldMessenger.showSnackBar replaced with inline error banners).</item>
    <item>Modal dimensions constrained between 480px min-width and 1400px max-width.</item>
    <item>Auto-scroll to first invalid FocusNode implemented in ScaleEditorModal and StepSimulationDialog via Scrollable.ensureVisible.</item>
    <item>ProfileEditorView form body bounded to centered 1200px max-width containment.</item>
    <item>[NEW] test suite @[client_app_v2/test/features/execution/views/widgets/human_override_dialog_test.dart] authored and passing all ISTQB boundary partitions.</item>
    <item>Full quality gate passes: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/ --build and Dart guardrails assert 0 violations.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do NOT allow uncommitted dialog edits to evaporate when user presses Escape or clicks outside modal barrier.</forbidden>
    <forbidden>Do NOT show SnackBars inside modal sheets or dialogs (absolute modal SnackBar ban).</forbidden>
    <forbidden>Do NOT touch studio_dashboard_view.dart (out of scope, registered as future technical debt).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/profile_editor_view.dart]</frontend>
  </touched_artifacts>

  <step id="4.1" name="HumanOverrideDialog Hardening &amp; Test Suite">
    <action>In @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L62-77]:</action>
    <action>- Implement PopScope(canPop: false, onPopInvokedWithResult: ...) routing to _handleDismiss().</action>
    <action>- Synchronous FocusScope.of(context).unfocus() prior to exit check.</action>
    <action>- Serialization-based dirty check comparing current draft DTO jsonEncode(_buildRequestDto().toJson()) != _initialRequestJson (verifying changes across _selectedStatus, _reasonController.text.trim(), and _quotes).</action>
    <action>- Replace modal ScaffoldMessenger.of(context).showSnackBar() with inline canvas error banner (colorScheme.errorContainer).</action>
    <action>- Enforce modal bounds ConstrainedBox(constraints: const BoxConstraints(minWidth: 480, maxWidth: 1400, minHeight: 600)).</action>
    <action>- Replace mutable bool _isLoading = false with atomic submission lock bool _isSaving = false.</action>
    <action>Author [NEW] @[client_app_v2/test/features/execution/views/widgets/human_override_dialog_test.dart] with mandatory negative ISTQB partitions: empty reason validation error rendered inline without SnackBar; PopScope discard confirmation when text buffer is dirty vs immediate pop when pristine; atomic button disable during in-flight save.</action>
    <demolish>REMOVE: `ScaffoldMessenger.of(context).showSnackBar(...)` in @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L62-77]. REPLACE WITH: inline canvas error banner.</demolish>
  </step>

  <step id="4.2" name="Studio Modals &amp; Complex Editors Hardening">
    <action>In @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart] and @[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart]:</action>
    <action>- Enforce auto-scroll to first invalid FocusNode via Scrollable.ensureVisible.</action>
    <action>- Enforce modal bounds ConstrainedBox(minWidth: 480, maxWidth: 1400, minHeight: 600).</action>
    <action>- Enforce inline error surfaces (absolute SnackBar ban inside modals).</action>
    <action>In @[client_app_v2/lib/features/studio/views/profile_editor_view.dart]:</action>
    <action>- Wrap single-column form body in centered 1200px max-width containment.</action>
    <action>- Verify relational sub-collection card header flexbox triad (Expanded title + AppSpacing.w16 + Row actions) and language-neutral indexing (#${index + 1}).</action>
    <demolish>REMOVE: modal SnackBars in @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart] and @[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart]. REPLACE WITH: inline error surfaces.</demolish>
  </step>

  <step id="4.3" name="Universal Quality Gates &amp; Static Guardrails">
    <action>Run build_runner: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/ --build.</action>
    <action>Run Dart static guardrails gate on touched feature targets: uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/execution/views/widgets/ client_app_v2/lib/features/studio/views/ client_app_v2/lib/core/api/ asserting zero DGR001 (across target domains), zero DGR002 in sdui_blocks_renderer.dart, and zero Freezed .when() violations.</action>
    <action>Run complete widget and API client test suites: sdui_matrix_table_widget_test.dart, xai_axis_telemetry_grid_test.dart, sdui_blocks_renderer_test.dart, human_override_dialog_test.dart, model_registry_view_test.dart, studio_client_test.dart.</action>
    <action>Verify bilingual localization parity: cd client_app_v2; flutter gen-l10n.</action>
  </step>

  <test_contracts>
    <test name="test_human_override_dialog_dirty_state_shows_discard_prompt" category="boundary">
      <input>User modifies reason text field and presses Escape</input>
      <expected>PopScope intercepts pop and displays discard confirmation dialog</expected>
    </test>
    <test name="test_human_override_dialog_pristine_state_pops_immediately" category="positive">
      <input>User opens dialog and presses Escape without making edits</input>
      <expected>Dialog dismisses immediately without confirmation prompt</expected>
    </test>
    <test name="test_human_override_dialog_empty_reason_shows_inline_error" category="error_path">
      <input>User clicks save button with empty reason field</input>
      <expected>Inline form field validation error appears; zero SnackBars triggered</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <!-- Deterministic full Flutter audit loop -->
    <action>Run audit loop: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/ --build</action>
    <!-- Dart guardrails gate -->
    <action>Run guardrails: uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/execution/views/widgets/ client_app_v2/lib/features/studio/views/ client_app_v2/lib/core/api/</action>
    <!-- Targeted widget test execution -->
    <action>Run human override test: cd client_app_v2; flutter test test/features/execution/views/widgets/human_override_dialog_test.dart</action>
    <action>Run scale editor modal test: cd client_app_v2; flutter test test/features/studio/views/widgets/scale_editor_modal_test.dart</action>
    <action>Run step simulation dialog test: cd client_app_v2; flutter test test/features/studio/widgets/step_simulation_dialog_test.dart</action>
  </validation_gate>
</execution_protocol>
```
