# Tracker: Targeted Frontend Hardening Wave F4 (Quorum Studio Master Views, Profile Block Editors & Workflow Canvas Widgets)

@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md] (Askel 5.4: Vaihe 4b - Wave F4)

- [ ] **[NOK] Execution:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md --gate frontend --model gemini-4-argon-medium --continue-on-failure`

### Post-Implementation Gates

- [x] **[SKIPPED] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md]" --gate backend --model gemini-4-argon-medium` (Zero backend targets in frontend targeted hardening).
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend {target}'"`
  - [ ] @[client_app_v2/lib/features/studio/views/blueprint_editor_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/components/clone_entity_button.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/matrices_master_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/matrix_editor_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/model_registry_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/output_profile_list_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/profile_editor_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/step_builder_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/workflows_master_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/contrastive_pair_editor.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/dag_canvas_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/dynamic_item_list_editor.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/expected_input_editor_box.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/i18n_text_field.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/inspector_pane.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/linguistic_shield_banner.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/prompt_preview_dialog.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/row_editor_modal.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/studio_master_header.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/tag_chip_input.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_inputs_tab.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/xai/fallback_error_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/xai/matrix_observability_accordion.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/base_block_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/executive_summary_block_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/metadata_block_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/variance_block_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify widget test coverage, Studio Unified Visual Design System adherence, and 100% theme sovereignty across all 53 hardened Wave F4 Studio views and editors.

### Final Verification Quality Gate
- [ ] **[NOK]** Universal Frontend Quality Gate:
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build
  ```

---

# Session Handover Context

## Achieved
* Initialized **Targeted Frontend Hardening Wave F4 (`53` targets)** covering Studio Master Views & Core Components (`16` files), Studio Widgets, Dialogs & Workflow Tabs (`21` files), and Output Profile Block Cards & Tabs (`16` files).

## Learned
* All Studio CRUD views and profile tabs must strictly adhere to `studio_unified_visual_design_system` (`02_flutter_desktop.md`) and read-only `PrefixedUUID7` entity ID invariants (`id_backend_authority_and_frontend_read_only_mandate`).

## Resume Command
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md --gate frontend --model gemini-4-argon-medium --continue-on-failure
```

## Remaining
* Execute `auto_hardening_runner.py` across all 53 targets in Wave F4 and run the global `flutter_audit_loop.py client_app_v2/ --build` verification gate.
