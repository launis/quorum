# Phase 2: Adaptive Visual Block Builder & UI Patterns

**Overview:** Refactor `layout_editor_card.dart` into an Adaptive Visual Block Builder within the Report Structure tab (`ProfileLayoutsTab`). Implement dedicated single-responsibility block cards under `client_app_v2/lib/features/studio/views/widgets/profile/blocks/` registered via `BlockCardRegistry` map, with dual-input hybrid slider clamping for `max_extension_items` and universal baseline block visibility toggles.
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/profile_layouts_tab.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/base_block_card.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/synthesis_text_block_card.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1. Verify that @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] renders 3 tabs and `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/profile_layouts_tab.dart] is wired.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_144_Output_Profile_Studio_UI_Modernization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `BlockCardRegistry` implemented in `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart] mapping all `TargetBlockType` keys to dedicated card builder functions.
    - [ ] `BaseBlockCard` implemented in `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/base_block_card.dart] enforcing the Universal Baseline toggle ("Include this block in the final report") mapped exclusively to `target_block_order`.
    - [ ] `MatrixGraphsBlockCard` implemented in `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart] with Collection Builder (1-N sub-items, inline accordion, 4 graph presets: 1D, 2D, 3D, Text Only, and "+ Add Graph" button).
    - [ ] `MatrixSummaryTableCard` implemented in `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart] as an independent card for `preset_view == "matrix_summary"`.
    - [ ] `SynthesisTextBlockCard` implemented in `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/synthesis_text_block_card.dart] supporting Option A (Pipeline) and Option B (On-the-Fly) synthesis configurations.
    - [ ] `XaiExtensionsBlockCard` implemented in `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart] with Dual-Input Hybrid pattern (slider clamping to 1-20 and companion text input validating 1-100 without null fallbacks).
    - [ ] `MetadataBlockCard` and `BibliographyBlockCard` implemented in `[NEW]` dedicated cards with field checkboxes and formatting toggles.
    - [ ] `SimpleToggleBlockCard` implemented in `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart] for Penalties, Variance Validation, and Authenticity Evaluation blocks.
    - [ ] Comma-separated `steps` text field and sub-tab segmented buttons deleted from @[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart].
    - [ ] All block card files are strictly under 200 lines per file.
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
    - Do NOT hardcode block cards inline inside `profile_layouts_tab.dart` (must use registry pattern).
    - Do NOT allow raw text inputs for comma-separated `steps` IDs.
    - Do NOT use `?? 21` or `?? 3` fallbacks on non-nullable `maxExtensionItems`.
    - Do NOT create separate `include_X: bool` flags on OutputProfile (use `target_block_order` SSOT).
  </anti_targets>

  <step id="1" name="Block Card Registry & Base Block Card">
    <action>Create `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/base_block_card.dart] implementing shared visual wrapper with expandable header and Universal Baseline toggle ("Include this block in the final report") that adds/removes the block's `TargetBlockType` from `profile.targetBlockOrder`.</action>
    <action>Create `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart] implementing `Map<TargetBlockType, Widget Function(BuildContext, OutputProfile, WidgetRef)>` to dispatch rendering of each block card without if-else or switch monoliths.</action>
    <constraint invariant="strategy_pattern_mandate">Registry map pattern with eager instantiation.</constraint>
  </step>

  <step id="2" name="Matrix Graphs Block Card (Collection Builder)">
    <action>Create `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart]:
1. Renders 1-N graph sub-items (each an `OutputLayoutBlock` with `preset_view ∈ {1d_metrics, 2d_compare, 3d_matrix, text_only}`).
2. Inline accordion editing for each sub-item.
3. Visual preset selection (1D Metrics, 2D Compare, 3D Bubble, Text Only).
4. Context-Adaptive Axis dropdowns (3 axes for 3D, 2 for 2D, 1 for 1D, 0 for Text Only).
5. I18n title field and `text_delivery_mode` SegmentedButton.
6. `"+ Add Graph"` `FilledButton.icon` at bottom of sub-list.
    </action>
    <constraint invariant="anti_god_file_dumping">Dedicated single-responsibility widget strictly under 200 lines.</constraint>
  </step>

  <step id="3" name="Matrix Summary Table Block Card">
    <action>Create `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart]:
1. Dedicated card for `OutputLayoutBlock` with `preset_view == "matrix_summary"`.
2. `FilterChip` pills for `matrix_visible_columns` (`label`, `atomic_breakdown`, `row_explanation`, `normalized_score`, `score`, `quotes`).
3. I18n text fields for `matrix_column_labels` per visible column.
4. Optional `target_blocks` multi-select (default: `["*"]`).
    </action>
    <constraint invariant="anti_god_file_dumping">Dedicated single-responsibility widget strictly under 200 lines.</constraint>
  </step>

  <step id="4" name="Synthesis Text Block Card">
    <action>Create `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/synthesis_text_block_card.dart]:
1. Dual-mode selector: Option A (Pipeline Way - select `synthesis_block_id`) vs Option B (On-the-Fly - `tone_instruction` and `preamble_text`).
2. Multilingual rich text editor for `preamble_text`.
    </action>
    <constraint invariant="anti_god_file_dumping">Dedicated single-responsibility widget strictly under 200 lines.</constraint>
  </step>

  <step id="5" name="XAI Extensions Block Card (Dual-Input Hybrid & Clamping)">
    <action>Create `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart]:
1. FilterChip pills for selecting active XAI extension categories.
2. Dual-Input Hybrid Pattern for `max_extension_items`:
   - Slider operating on non-nullable `profile.maxExtensionItems` clamped via `rawVal.clamp(SystemUiConstraints.maxExtensionItemsSliderMin.value, SystemUiConstraints.maxExtensionItemsSliderMax.value).toDouble()`.
   - Companion `TextFormField` numerical override validating `1 <= val <= 100` via `FormFieldValidator`.
    </action>
    <constraint invariant="slider_assertion_guard">Safe clamping prevents Slider assertion crash on high-threshold backend profiles.</constraint>
  </step>

  <step id="6" name="Metadata, Bibliography & Simple Toggle Block Cards">
    <action>Create `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart] with checkboxes for visible metadata fields (`date`, `organization`, `user`, `scoring_engine`, `strictness`).</action>
    <action>Create `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart] with formatting toggles (`grouped_by_matrix`, `anonymous_mode`).</action>
    <action>Create `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart] for Penalties, Variance Validation, and Authenticity Evaluation blocks.</action>
    <action>Update `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/profile_layouts_tab.dart] and @[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart] to integrate with the new block cards via `BlockCardRegistry`.</action>
  </step>

  <validation_gate>
    <action>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build</action>
    <action>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/widgets/profile/layout_editor_card_test.dart --test</action>
    <action>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart --test</action>
  </validation_gate>
</execution_protocol>
```
