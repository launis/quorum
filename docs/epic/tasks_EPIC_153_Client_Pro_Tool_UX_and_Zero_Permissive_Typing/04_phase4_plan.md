# Phase 4: Studio Modals, Dialogs UX Hardening & E2E Quality Gates

**Overview:** Complete Quorum's desktop modal hardening and end-to-end quality gate verification as mandated in `@[ki_desktop_pro_tool_studio_ux.md]`. Intercept modal dismissals with `PopScope(canPop: false)` and serialization-based dirty checking (`jsonEncode != initialJson`) to shield against uncommitted state loss, eradicate all modal SnackBar alerts in favor of inline canvas error banners, enforce modal min/max geometry bounds (480-1400px), implement auto-scroll to invalid fields via `Scrollable.ensureVisible`, wrap `ProfileEditorView` in centered 1200px containment, author a comprehensive negative ISTQB test suite for `HumanOverrideDialog`, and execute the universal Flutter audit loop and Dart guardrails.
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
    <action>Look backward: Verify that Phase 1 established typed domain models, Phase 2 eliminated SDUI cell calculation thrashing, and Phase 3 virtualized all 4 Quorum Studio master list views.</action>
    <action>Look forward: Verify that all Studio dialogs, editors, and quality gates pass 100% without deprecation or lint warnings.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_153_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute @[docs/epic/tasks_EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing/04_phase4_plan.md] @[docs/epic/EPIC_153_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>Pre-implementation technical debt cleanups in Step 4.0 eradicate raw grey colors in HumanOverrideDialog, purge SizedBox.shrink() concealment in ProfileEditorView, and eliminate modal AlertDialog error surfaces in StepSimulationDialog.</item>
    <item>HumanOverrideDialog implements PopScope(canPop: false), focus unblur, serialization dirty check (jsonEncode != initialJson), 480-1400px bounds, and atomic submission lock.</item>
    <item>Zero modal SnackBar calls across touched dialogs (ScaffoldMessenger.showSnackBar replaced with inline error banners).</item>
    <item>Modal dimensions constrained between 480px min-width and 1400px max-width across HumanOverrideDialog, ScaleEditorModal, and StepSimulationDialog.</item>
    <item>Auto-scroll to first invalid FocusNode implemented in ScaleEditorModal and StepSimulationDialog via Scrollable.ensureVisible.</item>
    <item>ProfileEditorView form body bounded to centered 1200px max-width containment with relational sub-collection card header flexbox triad and language-neutral indexing (#${index + 1}).</item>
    <item>[NEW] test suite @[client_app_v2/test/features/execution/views/widgets/human_override_dialog_test.dart] authored and passing all 6 negative and positive ISTQB boundary partitions.</item>
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
    <forbidden>Do NOT use SizedBox.shrink() to hide unrendered extension options in ProfileEditorView (violates DGR002).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/profile_editor_view.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/test/features/execution/views/widgets/human_override_dialog_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/studio/widgets/step_simulation_dialog_test.dart]</frontend>
  </touched_artifacts>

  <step id="4.0" name="Pre-Implementation Technical Debt Cleanups">
    <action>In @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L1-L251] (specifically preserving @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L62-77]):</action>
    <action>- Replace hardcoded grey colors (Colors.grey.shade50 at #L181, Colors.grey.shade300 at #L183, Colors.grey at #L175) with Material 3 theme tokens (colorScheme.surfaceContainerLow, colorScheme.outlineVariant, colorScheme.onSurfaceVariant).</action>
    <action>- Replace mutable bool _isLoading = false with atomic submission lock bool _isSaving = false (#L29, #L59, #L88, #L234, #L239).</action>
    <action>In @[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L1-L680] (anchored to #L417-L520):</action>
    <action>- Eradicate all instances of const SizedBox.shrink() at #L475 and #L484 (violates sized_box_shrink_ban and DGR002) by filtering available and block extension lists via .where(...) prior to .map(...) in the visibleBlockExtensions section.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart#L1-L410] (anchored to #L82-L95):</action>
    <action>- Replace modal AlertDialog popups on error (showDialog(builder: (errCtx) => AlertDialog(...))) with inline canvas error banners using theme.colorScheme.errorContainer.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart#L1-L1015] (anchored to #L196-L209):</action>
    <action>- Replace modal AlertDialog error popup in _previewScalePrompt() with an inline canvas error banner using colorScheme.errorContainer.</action>
    <demolish>REMOVE: `const SizedBox.shrink()` at #L475/#L484 in @[client_app_v2/lib/features/studio/views/profile_editor_view.dart] and modal AlertDialog error popups in @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart] and @[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart]. REPLACE WITH: declarative `.where(...)` collections and inline canvas error banners.</demolish>
  </step>

  <step id="4.1" name="HumanOverrideDialog Hardening &amp; Test Suite">
    <action>In @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L1-L251] (specifically preserving @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L62-77]):</action>
    <action>- Implement modern PopScope(canPop: false, onPopInvokedWithResult: (didPop, result) { if (!didPop) _handleDismiss(); }) wrapping the dialog tree (#L96-L248).</action>
    <action>- Implement synchronous FocusScope.of(context).unfocus() inside _handleDismiss() prior to exit check.</action>
    <action>- Schedule dirty check evaluation inside WidgetsBinding.instance.addPostFrameCallback to ensure child focus-loss listeners flush.</action>
    <action>- Implement serialization-based dirty check: compare current draft DTO jsonEncode(_buildRequestDto().toJson()) != _initialRequestJson (capturing changes across _selectedStatus, _reasonController.text.trim(), and _quotes).</action>
    <action>- If pristine, dismiss cleanly via Navigator.of(context).pop(false). If dirty, display discard confirmation AlertDialog using l10n.discardChangesConfirmTitle, l10n.discardChangesConfirmMessage, l10n.keepEditingButtonLabel, and l10n.discardButtonLabel.</action>
    <action>- Replace modal ScaffoldMessenger.of(context).showSnackBar() calls with inline canvas error banner (colorScheme.errorContainer).</action>
    <action>- Enforce modal bounds ConstrainedBox(constraints: const BoxConstraints(minWidth: 480, maxWidth: 1400, minHeight: 600)) (#L98-L100).</action>
    <action>- Implement atomic submission lock in _submitOverride(): if (_isSaving) return; _isSaving = true; and disable submit and cancel buttons during save (#L51-L90, #L233-L247).</action>
    <action>- Wire Cancel button and AppBar close action to _handleDismiss().</action>
    <action>Author [NEW] @[client_app_v2/test/features/execution/views/widgets/human_override_dialog_test.dart] with mandatory ISTQB partitions:</action>
    <action>- Test 1: Empty reason validation error rendered inline without SnackBar.</action>
    <action>- Test 2: PopScope discard confirmation when text buffer is dirty vs immediate pop when pristine.</action>
    <action>- Test 3: Dropdown rating status change marks state dirty and triggers discard prompt on dismiss.</action>
    <action>- Test 4: Quotes list addition/deletion marks state dirty and triggers discard prompt on dismiss.</action>
    <action>- Test 5: Atomic button disable (_isSaving) during in-flight save operation.</action>
    <action>- Test 6: Successful override submission calls executionClient.overrideAtom with HumanOverrideRequestDto and pops with true.</action>
    <demolish>REMOVE: `ScaffoldMessenger.of(context).showSnackBar(...)` in @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L62-77]. REPLACE WITH: inline canvas error banner.</demolish>
  </step>

  <step id="4.2" name="Studio Modals &amp; Complex Editors Hardening">
    <action>In @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart#L1-L1015] (anchored to #L103-L210 &amp; #L761-L833):</action>
    <action>- Enforce auto-scroll to first invalid FocusNode via Scrollable.ensureVisible: when _formKey.currentState!.validate() fails, locate the first invalid field context or FocusNode and execute Scrollable.ensureVisible(targetContext, duration: const Duration(milliseconds: 300), curve: Curves.easeOut) instead of blind animateTo(0).</action>
    <action>- Verify modal bounds ConstrainedBox(constraints: const BoxConstraints(minWidth: 480, maxWidth: 1400, minHeight: 600)) (#L797-L802).</action>
    <action>- Replace showDialog AlertDialog on simulation preview failure (#L196-L209) with an inline error banner on the modal canvas.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart#L1-L410] (anchored to #L50-L147 &amp; #L190-L268):</action>
    <action>- Enforce canonical modal bounds BoxConstraints(minWidth: 480, maxWidth: 1400, minHeight: 600) (#L106-L111).</action>
    <action>- Implement PopScope(canPop: false, onPopInvokedWithResult: ...) and serialization-based dirty check on expected input controllers and context text against initial snapshot (#L103-L131).</action>
    <action>- Enforce auto-scroll to first invalid input: when form validation fails, scroll to the invalid input via Scrollable.ensureVisible.</action>
    <action>- Ensure simulation errors render strictly inline via colorScheme.errorContainer banner (zero modal AlertDialogs or SnackBars).</action>
    <action>In @[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L1-L680] (anchored to #L224-L260):</action>
    <action>- Wrap single-column form body in centered 1200px max-width containment: Align(alignment: Alignment.topCenter, child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 1200), child: ListView(...))) (#L224-L260).</action>
    <action>- Verify relational sub-collection card header flexbox triad (Expanded title + AppSpacing.w16 + Row actions) and language-neutral indexing (#${index + 1}).</action>
    <action>Update test suites @[client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart] and @[client_app_v2/test/features/studio/widgets/step_simulation_dialog_test.dart] to assert auto-scroll and inline error banner behavior.</action>
    <demolish>REMOVE: modal SnackBars and modal AlertDialogs in @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart] and @[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart]. REPLACE WITH: inline error surfaces.</demolish>
  </step>

  <step id="4.3" name="Universal Quality Gates &amp; Static Guardrails">
    <action>Run build_runner: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/ --build.</action>
    <action>Run Dart static guardrails gate on touched feature targets: uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/execution/views/widgets/ client_app_v2/lib/features/studio/views/ client_app_v2/lib/core/api/ asserting zero DGR001 (across target domains), zero DGR002 in sdui_blocks_renderer.dart and profile_editor_view.dart, and zero Freezed .when() violations.</action>
    <action>Run complete widget and API client test suites:</action>
    <action>- cd client_app_v2; flutter test test/features/execution/views/widgets/human_override_dialog_test.dart</action>
    <action>- cd client_app_v2; flutter test test/features/studio/views/widgets/scale_editor_modal_test.dart</action>
    <action>- cd client_app_v2; flutter test test/features/studio/widgets/step_simulation_dialog_test.dart</action>
    <action>- cd client_app_v2; flutter test test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart</action>
    <action>- cd client_app_v2; flutter test test/features/execution/views/widgets/xai_axis_telemetry_grid_test.dart</action>
    <action>- cd client_app_v2; flutter test test/features/execution/views/widgets/sdui_blocks_renderer_test.dart</action>
    <action>- cd client_app_v2; flutter test test/features/studio/views/workflows_master_view_test.dart</action>
    <action>- cd client_app_v2; flutter test test/features/studio/views/matrices_master_view_test.dart</action>
    <action>- cd client_app_v2; flutter test test/features/studio/views/output_profile_list_view_test.dart</action>
    <action>- cd client_app_v2; flutter test test/features/studio/views/mcp_gateways_master_view_test.dart</action>
    <action>- cd client_app_v2; flutter test test/features/studio/views/widgets/studio_master_header_test.dart</action>
    <action>- cd client_app_v2; flutter test test/core/api/studio_client_test.dart</action>
    <action>Verify bilingual localization parity: cd client_app_v2; flutter gen-l10n.</action>
  </step>

  <five_column_directives>
    <!-- 5-Column Architectural Directives Table -->
    | 1. Target Scope &amp; Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification &amp; Fail-Fast (Proof Anchor) |
    | :--- | :--- | :--- | :--- | :--- |
    | **HumanOverrideDialog** `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L1-L251]` (anchored to `#[L62-77]`) | Unintercepted modal dismiss (Esc/barrier tap silently dropping reason/quotes), hardcoded `Colors.grey` tokens, mutable `_isLoading` flag, modal `ScaffoldMessenger.showSnackBar()`. | `PopScope(canPop: false)` with `FocusScope.unfocus()` and `addPostFrameCallback` blur flush, serialization dirty check (`jsonEncode != initialJson`), inline error banner (`colorScheme.errorContainer`), Material 3 theme tokens (`colorScheme.surfaceContainerLow`, `outlineVariant`), atomic `_isSaving` lock, and `ConstrainedBox(minWidth: 480, maxWidth: 1400, minHeight: 600)`. | Direct `PopScope` integration and standard Riverpod consumer state; zero external dialog wrapper dependencies. | Author [NEW] `client_app_v2/test/features/execution/views/widgets/human_override_dialog_test.dart` passing 6 positive/negative ISTQB test partitions; 0 unhandled exceptions. |
    | **ScaleEditorModal** `@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart#L1-L1015]` (anchored to `#[L103-L210]` &amp; `#[L761-L833]`) | Blind `_scrollController.animateTo(0)` on validation failure, modal `showDialog(AlertDialog)` on prompt simulation failure. | Auto-scroll to first invalid `FocusNode` via `Scrollable.ensureVisible` (300ms, easeOut), inline error banner on preview failure, and pro-tool bounds (`minWidth: 480, maxWidth: 1400, minHeight: 600`). | Reuse existing Form validation state and focus hierarchy; zero speculative custom focus managers. | `cd client_app_v2; flutter test test/features/studio/views/widgets/scale_editor_modal_test.dart` passes 100% green. |
    | **StepSimulationDialog** `@[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart#L1-L410]` (anchored to `#[L50-L147]` &amp; `#[L190-L268]`) | Unintercepted modal dismiss, modal `showDialog(AlertDialog)` on simulation error, narrow constraints (`maxWidth: 1100, minHeight: 550`). | `PopScope(canPop: false)` with dirty checking on input controllers and context text, inline error banner (`colorScheme.errorContainer`), auto-scroll to invalid expected inputs, and canonical bounds (`minWidth: 480, maxWidth: 1400, minHeight: 600`). | Pure `ConsumerStatefulWidget` using standard Flutter controllers; zero unnecessary custom state stores. | `cd client_app_v2; flutter test test/features/studio/widgets/step_simulation_dialog_test.dart` passes 100% green. |
    | **ProfileEditorView** `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L1-L680]` (anchored to `#[L224-L260]` &amp; `#[L417-L520]`) | `const SizedBox.shrink()` concealment (violates `sized_box_shrink_ban` and `DGR002`), unconstrained form canvas stretching across 4K displays. | Declarative `.where(...)` filtering prior to `.map(...)` in `visibleBlockExtensions`, centered 1200px containment `Align(alignment: Alignment.topCenter, child: ConstrainedBox(constraints: BoxConstraints(maxWidth: 1200), child: ListView(...)))`, and language-neutral indexing (`#${index + 1}`). | Zero custom layout managers or empty placeholder widgets; direct standard Flutter Flex and Alignment containment. | `uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/studio/views/profile_editor_view.dart` reports 0 `DGR002` violations. |
  </five_column_directives>

  <test_contracts>
    <test name="test_human_override_dialog_dirty_state_shows_discard_prompt" category="boundary">
      <input>User modifies reason text field and presses Escape or Cancel</input>
      <expected>PopScope intercepts pop and displays discard confirmation dialog; selecting Continue retains dialog, selecting Discard closes</expected>
    </test>
    <test name="test_human_override_dialog_pristine_state_pops_immediately" category="positive">
      <input>User opens dialog and presses Escape or Cancel without making edits</input>
      <expected>Dialog dismisses immediately without confirmation prompt</expected>
    </test>
    <test name="test_human_override_dialog_empty_reason_shows_inline_error" category="error_path">
      <input>User clicks save button with empty reason field</input>
      <expected>Inline form field validation error appears; zero SnackBars triggered; overrideAtom not called</expected>
    </test>
    <test name="test_human_override_dialog_rating_change_marks_dirty" category="boundary">
      <input>User changes rating dropdown from PASSED to FAILED and triggers dismiss</input>
      <expected>PopScope intercepts pop and displays discard confirmation dialog</expected>
    </test>
    <test name="test_human_override_dialog_quotes_mutation_marks_dirty" category="boundary">
      <input>User deletes a quote or adds a quote and triggers dismiss</input>
      <expected>PopScope intercepts pop and displays discard confirmation dialog</expected>
    </test>
    <test name="test_human_override_dialog_in_flight_lock" category="boundary">
      <input>User triggers save with valid payload</input>
      <expected>Buttons are disabled via _isSaving lock; overrideAtom invoked with HumanOverrideRequestDto; modal pops with true on success</expected>
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
