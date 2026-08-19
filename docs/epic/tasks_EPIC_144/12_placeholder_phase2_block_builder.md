# Phase 2: Visual Block Builder (DEFERRED)

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 2 "Visual Block Builder" (L432-L510)
**Status:** PLACEHOLDER — Detailed plan will be generated after Phase 1 is complete.

**Overview:** Replace the existing text-based `target_block_order` editor with a Visual Block Builder — a drag-and-drop Kanban-style interface that renders the full `TargetBlockType` palette as draggable cards with preview sections.

**Target Files:**
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/base_block_card.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/synthesis_text_block_card.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart]`
- `[MODIFY/NEW from Plan 11]` `client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart`

**Prerequisites:** Phase 1 (Plans 10-11) must be complete.

```xml
<execution_protocol>
  <step id="0" name="DEFERRED">
    <action>This plan is a placeholder. Detailed execution steps will be generated after Phase 1 completion.</action>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\02_flutter_desktop.md]</rule>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/ — Do NOT touch Python files in this phase</file>
  </anti_targets>

  <dod_checklist>
    <item>DEFERRED — Will be populated during detailed planning.</item>
  </dod_checklist>

  <validation_gate>
    <check>DEFERRED — Will be populated during detailed planning.</check>
  </validation_gate>
</execution_protocol>
```
