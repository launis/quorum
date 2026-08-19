# Phase 2: Visual Block Builder

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 2 "Visual Block Builder" (L383-L494)
**Scope:** Frontend Flutter/Dart UI logic and block widgets

## 1. Executive Summary & Problem Statement

In Phase 1, `output_profile_crud_view.dart` was successfully decomposed into a clean 3-tab shell (`ProfileGeneralTab`, `ProfileScoringTab`, `ProfileLayoutsTab`). However, Tab 3 (`ProfileLayoutsTab`) currently delegates layout editing to `layout_editor_card.dart` (642 lines), which relies on technical dropdown enums, comma-separated `steps` text fields, and monolithic multi-tab layout cards. Furthermore, `target_block_order` is rendered as a raw detached `ReorderableListView`.

Phase 2 replaces `layout_editor_card.dart` with an **Adaptive Visual Block Builder** within `ProfileLayoutsTab` (`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]`). Each configurable block type is represented by a dedicated, single-responsibility widget registered via the **Registry Map pattern** (`BlockCardRegistry`) to enforce the **God Code Prevention mandate** (`@[ki_god_code_prevention.md]`) and eliminate monolithic `switch/if-else` branching.

---

## 2. Architectural Blueprint & Target Block Catalog

All block visibility is driven by the Universal Baseline Toggle SSOT: presence/absence in `payload.targetBlockOrder: List<TargetBlockType>` (`@[client_app_v2/lib/features/studio/models/output_profile.dart]`).

### Target Block Type UI Matrix:

| TargetBlockType | Card Widget | Mode | Internal State / Configuration Domain |
| :--- | :--- | :--- | :--- |
| `metadataBlock` | `MetadataBlockCard` | Config Card | Checkboxes for visible metadata fields: `date`, `organization`, `user`, `scoring_engine`, `strictness`, `cost`, `tokens`. Mutates `payload.visibleMetadata`. |
| `executiveSummaryBlock` | `BaseBlockCard` (simple toggle) | Toggle Card | Universal toggle only (preface configured in Tab 1, role mappings modal in Tab 1). |
| `synthesisTextBlock` | `SynthesisTextBlockCard` | Config Card | Pipeline synthesis (`synthesis_block_id` selection) vs On-the-Fly synthesis (`tone_instruction`, `preamble_text` via `synthesis` config). |
| `matrixGraphsBlock` | `MatrixGraphsBlockCard` | Deep Collection Builder | 1–N graph items in `payload.layouts` with `preset_view ∈ {metrics1d, compare2d, matrix3d, textOnly}`. Accordion inline editing, context-adaptive X/Y/Z axis dropdowns (`targetBlocks`), and `+ Add Graph` button. |
| `groupedExtensionsBlock` | `XaiExtensionsBlockCard` | Config Card | Interactive `FilterChip` pills for block-level & workflow-level extensions, and `maxExtensionItems` hybrid Slider (1–20 clamped) + `TextFormField` (1–100 validated) per V10. |
| `penaltiesBlock` | `SimpleToggleBlockCard` | Simple Toggle | Universal baseline toggle only (penalties are computed by backend engine). |
| `matrixSummaryTableBlock` | `MatrixSummaryTableCard` | Deep Config Card | Single `OutputLayoutBlock` in `payload.layouts` with `preset_view == matrixSummary`. `FilterChip` toggles for `matrixVisibleColumns`, column labels `matrixColumnLabels`, and optional `targetBlocks` axis filter. |
| `varianceValidationBlock` | `SimpleToggleBlockCard` | Simple Toggle | Universal baseline toggle only (computed metrics). |
| `authenticityEvaluationBlock` | `SimpleToggleBlockCard` | Simple Toggle | Universal baseline toggle only (computed metrics). |
| `printableSourcesBlock` | `BibliographyBlockCard` | Config Card | Universal toggle + formatting toggles. |
| `globalScoreBlock` | *System Block* | Fixed / Hidden | Managed by system, not configurable in Studio palette. |
| `auditTrailBlock` | *System Block* | Fixed / Hidden | Managed by system, not configurable in Studio palette. |
| `jargonRatioBlock` | *System Block* | Fixed / Hidden | Managed by system, not configurable in Studio palette. |

---

## 3. Target Files & Modifications

### New Files to Create:
1. `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/base_block_card.dart]` (≤200 lines):
   - Canonical container widget wrapping every block card with header icon, localized title, drag handle, and Universal Baseline Switch: `Include this block in the final report`.
   - Toggling the switch dispatches atomic addition/removal of the block's `TargetBlockType` to/from `payload.targetBlockOrder`.
2. `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart]` (≤200 lines):
   - Static registry `Map<TargetBlockType, Widget Function(BuildContext context, String profileId, OutputProfile payload, void Function(OutputProfile) updatePayload, Set<String> allowedBlockIds, AsyncValue<List<PromptBlock>> promptBlocksState)>`.
   - Eagerly maps each configurable block type to its dedicated builder without runtime switch-case cascades.
3. `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart]` (≤200 lines):
   - Visual card for `metadataBlock` allowing granular checklist toggling of `payload.visibleMetadata`.
4. `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/synthesis_text_block_card.dart]` (≤200 lines):
   - Visual card for `synthesisTextBlock` exposing Pipeline synthesis block selection vs on-the-fly synthesis parameters.
5. `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart]` (≤200 lines):
   - Collection Builder for matrix graph entries in `payload.layouts`. Accordion inline editing, 4 graph preset selectors (1D Table, 2D Grid, 3D Matrix, Text Only), adaptive axes dropdowns, and `+ Add Graph` action.
6. `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart]` (≤200 lines):
   - Dedicated card for `matrixSummaryTableBlock`. `FilterChip` column selectors (`matrixVisibleColumns`), I18n column label overrides (`matrixColumnLabels`), and axis filters (`targetBlocks`).
7. `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart]` (≤200 lines):
   - Visual card for `groupedExtensionsBlock`. `FilterChip` extension toggles and the V10 hybrid Slider/TextFormField pattern for `maxExtensionItems`.
8. `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart]` (≤200 lines):
   - Visual card for `printableSourcesBlock` (Bibliography).
9. `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart]` (≤120 lines):
   - Reusable baseline card for pure-computed blocks (`penaltiesBlock`, `varianceValidationBlock`, `authenticityEvaluationBlock`, `executiveSummaryBlock`).
10. `[NEW]` `@[client_app_v2/test/features/studio/views/widgets/profile/blocks/block_card_registry_test.dart]` (≤200 lines):
    - Comprehensive unit tests asserting complete registry mapping for all `TargetBlockType` values, toggle behavior, and negative unmapped safety assertions.

### Existing Files to Modify:
1. `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]` (≤200 lines):
   - Refactor from legacy `LayoutEditorCard` wrapper to Flat Master Block List driven by `payload.targetBlockOrder` and `BlockCardRegistry`.
   - Incorporates drag-and-drop reordering of active report blocks.
2. `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]` (≤200 lines or Sunset):
   - Deprecate / streamline legacy card to redirect to `ProfileLayoutsTab` or remove redundant sub-widgets.
3. `[MODIFY]` `@[client_app_v2/test/features/studio/views/widgets/profile/layout_editor_card_test.dart]`:
   - Update tests to test `ProfileLayoutsTab` and new visual block cards.
4. `[MODIFY]` `@[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart]`:
   - Update Golden Master characterization tests to assert Tab 3 block builder rendering and interactive configuration.

---

## 4. Execution Protocol (XML Sandwich Schema)

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify Phase 1 (Plans 10 and 11) is signed off and Golden Master widget tests pass green.</action>
    <action>Verify @[client_app_v2/lib/core/models/enums.dart] contains all TargetBlockType and SystemUiConstraints values from Plan 07.</action>
    <constraint>Zero regression against Phase 1 Golden Master baseline. All new files MUST be ≤200 lines.</constraint>
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
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/ — Do NOT touch Python backend files in Phase 2</file>
    <file>client_app_v2/lib/features/studio/models/ — Do NOT modify Freezed models (already finalized in Phase 0)</file>
    <file>client_app_v2/lib/core/models/enums.dart — Do NOT modify enums (already finalized in Phase 0)</file>
  </anti_targets>

  <dod_checklist>
    <item>BaseBlockCard implemented with universal visibility switch (R58, R59).</item>
    <item>BlockCardRegistry implemented mapping all TargetBlockType values to builder widgets via Strategy/Registry pattern (R58).</item>
    <item>9 dedicated block cards implemented under blocks directory, each ≤200 lines (R59).</item>
    <item>MatrixGraphsBlockCard implemented with Collection Builder and accordion inline editing (R60).</item>
    <item>MatrixSummaryTableCard implemented as standalone block editor with FilterChip column toggles (R61).</item>
    <item>XaiExtensionsBlockCard implemented with hybrid Slider/TextFormField clamping against SystemUiConstraints (R62, V10).</item>
    <item>ProfileLayoutsTab refactored to render the Visual Block Builder with drag-and-drop reordering (R58, R59).</item>
    <item>All modified and new Dart files strictly ≤200 lines per God Code Prevention mandate.</item>
    <item>Widget test suite in block_card_registry_test.dart, layout_editor_card_test.dart, and output_profile_crud_view_test.dart pass 100% green.</item>
    <item>Flutter audit loop passes with zero lints, zero warnings, and zero type errors.</item>
  </dod_checklist>

  <step id="1" name="CREATE BASE BLOCK CARD">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/base_block_card.dart]:
      - Reusable container card with Material 3 styling, outline border, elevation: 0.
      - Header Row: leading block icon, localized block title (Bold, 15px), trailing reorder drag handle, and Switch for Universal Baseline Toggle: "Include this block in report".
      - When switch is toggled: if true, appends TargetBlockType to payload.targetBlockOrder; if false, removes it.
      - Optional expandable body child for blocks with internal configuration (hidden/collapsed when switch is off).
    </action>
    <constraint invariant="universal_fail_fast">Must enforce non-null TargetBlockType and handle state mutations via ref.read(outputProfileFormProvider(profileId).notifier).updatePayload.</constraint>
  </step>

  <step id="2" name="CREATE SIMPLE TOGGLE BLOCK CARD &amp; BIBLIOGRAPHY BLOCK CARD">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart]:
      - Clean implementation for computed blocks (penaltiesBlock, varianceValidationBlock, authenticityEvaluationBlock, executiveSummaryBlock) delegating directly to BaseBlockCard with description subtitle and no nested form fields.
    </action>
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart]:
      - Card for printableSourcesBlock with BaseBlockCard wrapper.
    </action>
  </step>

  <step id="3" name="CREATE METADATA &amp; SYNTHESIS TEXT BLOCK CARDS">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart]:
      - Card for metadataBlock.
      - Body contains FilterChip or CheckboxListTile selectors for visibleMetadata (date, organization, user, scoring_engine, strictness, cost, tokens).
      - Updates payload.visibleMetadata.
    </action>
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/synthesis_text_block_card.dart]:
      - Card for synthesisTextBlock.
      - Mode A (Pipeline Way): Dropdown to select synthesis_block_id from available prompt blocks.
      - Mode B (On-the-Fly): I18nTextField for tone_instruction and preamble_text.
      - Updates payload.synthesis and payload.toneInstruction.
    </action>
  </step>

  <step id="4" name="CREATE XAI EXTENSIONS BLOCK CARD">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart]:
      - Card for groupedExtensionsBlock.
      - Body: FilterChip wrap pills for block-level and workflow-level XaiExtensionType options filtered by workflowAvailableExtensionsProvider.
      - Hybrid Slider + TextFormField for maxExtensionItems with safe clamping against SystemUiConstraints per V10 canonical implementation.
      - Updates payload.visibleBlockExtensions, payload.visibleWorkflowExtensions, and payload.maxExtensionItems.
    </action>
    <constraint invariant="universal_fail_fast">Must clamp slider value via rawVal.clamp(sliderMin, sliderMax).toDouble() to prevent Flutter assertion crash on >20 values.</constraint>
  </step>

  <step id="5" name="CREATE MATRIX SUMMARY TABLE CARD">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart]:
      - Standalone card for matrixSummaryTableBlock (preset_view == matrixSummary).
      - Column Visibility: FilterChip pills for matrixVisibleColumns (label, atomic_breakdown, row_explanation, normalized_score, score, quotes).
      - Column Labels: I18nTextField entries for matrixColumnLabels per visible column.
      - Axis filter: Multi-select dropdown for targetBlocks (defaults to ["*"]).
      - Updates the matching OutputLayoutBlock in payload.layouts.
    </action>
  </step>

  <step id="6" name="CREATE MATRIX GRAPHS BLOCK CARD (COLLECTION BUILDER)">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart]:
      - Collection Builder for matrix graph entries in payload.layouts (where preset_view ∈ {metrics1d, compare2d, matrix3d, textOnly}).
      - Lists 1–N graph sub-items with accordion ExpansionTile / Card for inline editing.
      - 4 Visual Preset Selectors (SegmentedButton or ChoiceChips): 1D Table, 2D Grid, 3D Matrix, Text Only.
      - Context-Adaptive X/Y/Z axis dropdowns (1 dropdown for 1D, 2 for 2D, 3 for 3D, 0 for textOnly) populated from allowed PromptBlocks.
      - Duplicate axis detection validator preventing same block selection across X/Y/Z.
      - "+ Add Graph" FilledButton.icon at the bottom to append new OutputLayoutBlock(presetView: PresetView.metrics1d).
      - Delete icon on each sub-item to remove from payload.layouts.
    </action>
    <constraint invariant="god_code_prevention">Sub-components must be cleanly extracted to keep the file strictly ≤200 lines.</constraint>
  </step>

  <step id="7" name="IMPLEMENT BLOCK CARD REGISTRY">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart]:
      - Define BlockCardRegistry with static Map&lt;TargetBlockType, Widget Function(...)&gt; mapping all 13 TargetBlockType members.
      - Provide getBlockCard(TargetBlockType type, ...) method with strict Fail-Fast assertion / fallback rendering.
    </action>
  </step>

  <step id="8" name="REFACTOR PROFILE LAYOUTS TAB TO FLAT VISUAL BLOCK BUILDER">
    <action>Modify @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]:
      - Replace legacy LayoutEditorCard call with Visual Block Builder list.
      - Section 1: Workflow Unselected Warning Card (if payload.workflowId.isEmpty).
      - Section 2: Active Report Blocks ReorderableListView rendering each TargetBlockType in payload.targetBlockOrder via BlockCardRegistry.
      - Section 3: Inactive / Available Blocks Drawer or Palette allowing users to add disabled blocks back into targetBlockOrder.
    </action>
    <action>Deprecate / simplify @[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart] to satisfy backward compatibility or remove obsolete code.</action>
  </step>

  <step id="9" name="IMPLEMENT COMPREHENSIVE WIDGET TESTS &amp; REGRESSION GATE">
    <action>Create [NEW] @[client_app_v2/test/features/studio/views/widgets/profile/blocks/block_card_registry_test.dart]:
      - Test that every TargetBlockType renders its corresponding card without crashing.
      - Test Universal Baseline Toggle adds and removes TargetBlockType from targetBlockOrder.
      - Test MatrixGraphsBlockCard adds, edits, and removes graph layouts.
      - Test XaiExtensionsBlockCard clamps slider to 20 without assertion error when maxExtensionItems is 50.
      - Negative test: unknown TargetBlockType throws or renders ErrorWidget.
    </action>
    <action>Update @[client_app_v2/test/features/studio/views/widgets/profile/layout_editor_card_test.dart] and @[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart].</action>
    <action>Execute Flutter quality gate: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build` and `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio --test`.</action>
  </step>
</execution_protocol>
```

---

## 5. Verification & Test Strategy

### Automated Test Matrix:
1. **Block Registry Parity Test:** Verify all 13 `TargetBlockType` values map to valid builder functions in `BlockCardRegistry`.
2. **Universal Toggle Test:** Assert clicking toggle switch adds/removes target block from `target_block_order`.
3. **Matrix Graphs Collection Builder Test:** Assert adding graph layout appends to `layouts`, switching preset adjusts required axis dropdowns, and duplicate axes trigger validation error.
4. **Slider Clamping Boundary Test (V10 / R80):** Assert `max_extension_items = 50` initializes slider to 20.0 without throwing Flutter assertion crash.
5. **Golden Master Parity Test:** Full regression test in `output_profile_crud_view_test.dart` passes 100% green across all 3 tabs.

---

## 6. Definition of Done (DoD) Checklist

- [x] `BaseBlockCard` created with Universal Baseline switch (`base_block_card.dart`).
- [x] `BlockCardRegistry` created with eager Strategy mapping (`block_card_registry.dart`).
- [x] 8 dedicated block cards created under `blocks/` directory (`metadata_block_card.dart`, `synthesis_text_block_card.dart`, `matrix_graphs_block_card.dart`, `matrix_summary_table_card.dart`, `xai_extensions_block_card.dart`, `bibliography_block_card.dart`, `simple_toggle_block_card.dart`).
- [x] `ProfileLayoutsTab` refactored to render the Visual Block Builder with `ReorderableListView`.
- [x] Every modified/created Dart file is strictly ≤200 lines per `ki_god_code_prevention.md`.
- [x] All unit and widget tests pass 100% green via `flutter_audit_loop.py`.
