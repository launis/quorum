# Phase 1: Sub-Tab Information Architecture & Scaffold Decomposition

**Overview:** Decompose the 896-line monolithic `output_profile_crud_view.dart` into a streamlined 3-tab `DefaultTabController` scaffold matching the visual idiom of `WorkflowBuilderView` (`ProfileGeneralTab`, `ProfileScoringTab`, `ProfileLayoutsTab`), establishing pre-refactoring Golden Master coverage and eradicating legacy untyped parameters and hardcoded design tokens.
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/profile_general_tab.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/profile_scoring_tab.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/profile_layouts_tab.dart]
- `[NEW]` @[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 0. Verify that @[client_app_v2/lib/features/studio/models/output_profile.dart] and enums compile cleanly.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_144_Output_Profile_Studio_UI_Modernization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] Baseline Golden Master widget test created in `[NEW]` @[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart] and verified green.
    - [ ] Monolithic view @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] decomposed into DefaultTabController scaffold with 3 clean tabs (&lt;200 lines per file).
    - [ ] Tab 1 (General &amp; Preface) implemented in `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/profile_general_tab.dart].
    - [ ] Tab 2 (Scoring &amp; Scales) implemented in `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/profile_scoring_tab.dart].
    - [ ] Tab 3 (Report Structure container) implemented in `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/profile_layouts_tab.dart].
    - [ ] Untyped `AsyncValue<List<dynamic>>` parameters eradicated in favor of `AsyncValue<List<PromptBlock>>`, `AsyncValue<List<Workflow>>`, and `AsyncValue<List<NodeStrategy>>` (V3 fix).
    - [ ] Hardcoded green color `Color(0xFF2E7D32)` replaced with theme tokens (V4 fix).
    - [ ] Hardcoded EdgeInsets and SizedBox pixel dimensions replaced with `AppSpacing` tokens (V5 fix).
    - [ ] SizedBox.shrink() XAI visibility hiding replaced with programmatic list filtering (V2 fix).
    - [ ] All widget and controller tests pass cleanly.
  </dod_checklist>

  <required_context_rules>
    - @[.agents/rules/00-antigravity-core.md]
    - @[.agents/rules/02_flutter_desktop.md]
    - @[.agents/rules/04_directory_reference.md]
    - @[ki_god_code_prevention.md]
    - @[ki_sdui_adapter_pattern.md]
    - @[ki_tripartite_pipeline_architecture.md]
    - @[ki_dual_axis_localization_architecture.md]
    - @[ki_strict_sdui_serialization.md]
    - @[ki_flat_polymorphic_pipeline.md]
    - @[ki_sdui_matrix_synthesis.md]
    - @[ki_global_config_sovereignty.md]
    - @[ki_ai_testing_standards.md]
    - @[ki_ast_guardrail_testing.md]
    - @[ki_python_314_concurrency_strictness.md]
    - @[ki_epic_lifecycle_workflow.md]
    - @[ki_synthesis_payload_compression.md]
    - @[ki_dag_engine_dto_projection_rules.md]
    - @[ki_matrix_boolean_evaluation_strictness.md]
  </required_context_rules>

  <anti_targets>
    - Do NOT dump new private helper methods into @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] (enforce God Code Prevention &lt;200 lines).
    - Do NOT create block cards under `widgets/profile/blocks/` in Phase 1 (deferred to Phase 2).
    - Do NOT use raw pixel values or hardcoded Color literals.
    - Do NOT use `SizedBox.shrink()` to hide UI elements.
  </anti_targets>

  <step id="1" name="Pre-Refactoring Golden Master Widget Test Baseline">
    <action>Create `[NEW]` @[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart] capturing baseline widget rendering, form field presence, and save/delete lifecycle before file decomposition.</action>
    <action>Run baseline audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart --test`.</action>
    <constraint invariant="remedial_refactoring_coverage">Must verify test coverage before modifying legacy monolithic view.</constraint>
    <test_contracts>
      <test name="test_output_profile_crud_view_renders_form_fields" category="positive">
        <input>OutputProfile with valid mock dependencies in ProviderScope</input>
        <expected>Renders AppBar title, tabs, and form input controls without rendering exceptions</expected>
      </test>
    </test_contracts>
  </step>

  <step id="2" name="Tab 1: ProfileGeneralTab Implementation">
    <action>Create `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/profile_general_tab.dart] as a dedicated HookConsumerWidget:
1. Workflow binding selector (`DropdownButtonFormField<String>`).
2. Profile name and description (`I18nTextField`).
3. Custom report preface / introduction rich text (`I18nTextField`).
4. Advanced expandable accordion for opaque `id` and semantic `slug`.
5. Strictly type all controller states and use `AppSpacing` tokens throughout.
    </action>
    <constraint invariant="anti_god_file_dumping">Dedicated single-responsibility widget strictly under 200 lines.</constraint>
  </step>

  <step id="3" name="Tab 2: ProfileScoringTab Implementation">
    <action>Create `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/profile_scoring_tab.dart] as a dedicated HookConsumerWidget:
1. Strictness level slider / segmented selector (Level 1 to 5).
2. Scoring Strategy selector (`waterfall`, `average`, `weighted_average`, `pure_math`).
3. Display Scale selector (`original`, `custom`, `normalized_100`).
4. Enforce design tokens and desktop hover cursors.
    </action>
    <constraint invariant="anti_god_file_dumping">Dedicated single-responsibility widget strictly under 200 lines.</constraint>
  </step>

  <step id="4" name="Tab 3: ProfileLayoutsTab Scaffold Container Implementation">
    <action>Create `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/profile_layouts_tab.dart] as a dedicated HookConsumerWidget providing the tab container for report blocks, wrapping reorderable block lists and delegating layout blocks.</action>
    <constraint invariant="anti_god_file_dumping">Dedicated single-responsibility widget strictly under 200 lines.</constraint>
  </step>

  <step id="5" name="Modernize OutputProfileCrudView Scaffold">
    <action>Refactor @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]:
<demolish>
REMOVE: local function `buildIdentityPane()` (L244-L726).
REMOVE: local function `buildTargetBlockOrderPane()` (L755-L796).
REMOVE: untyped `AsyncValue<List<dynamic>>` parameters (V3).
REMOVE: hardcoded color `Color(0xFF2E7D32)` (V4).
REMOVE: raw pixel padding `EdgeInsets.symmetric(horizontal: 16.0)` and `SizedBox(width: 20, height: 20)` (V5).
REMOVE: `SizedBox.shrink()` XAI element hiding (V2).
</demolish>
1. Replace 3-column row with `DefaultTabController(length: 3, ...)` with TabBar showing icons and labels matching `WorkflowBuilderView`:
   - Tab 1: 📋 General &amp; Preface
   - Tab 2: ⚖️ Scoring &amp; Scales
   - Tab 3: 📐 Report Structure
2. Wire `ProfileGeneralTab`, `ProfileScoringTab`, and `ProfileLayoutsTab` into TabBarView.
3. Strongly type all provider parameters (`PromptBlock`, `Workflow`, `NodeStrategy`).
4. Ensure total file length is strictly under 200 lines.
    </action>
    <constraint invariant="anti_god_file_dumping">File size must be strictly under 200 lines.</constraint>
  </step>

  <validation_gate>
    <action>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build</action>
    <action>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart --test</action>
    <action>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/controllers/output_profile_controller_test.dart --test</action>
  </validation_gate>
</execution_protocol>
```
