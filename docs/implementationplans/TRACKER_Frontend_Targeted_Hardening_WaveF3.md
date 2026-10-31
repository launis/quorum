# Tracker: Targeted Frontend Hardening Wave F3 (Execution, Reports & Shared SDUI / Presentation Widgets)

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

**Plan:** @[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md] (Askel 5.3: Vaihe 4b - Wave F3)

- [ ] **[NOK] Execution:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF3.md --gate frontend --model gemini-4-argon-medium --continue-on-failure`

### Post-Implementation Gates

- [x] **[SKIPPED] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF3.md]" --gate backend --model gemini-4-argon-medium` (Zero backend targets in frontend targeted hardening).
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF3.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend {target}'"`
  - [ ] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/dashboard_view.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/execution_view.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/new_execution_view.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/diagnostic_scorecard_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/matrix_row_item_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/report_renderer_v2_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/sdui_alert_box_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/sdui_grid_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/sdui_node_renderer.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart]
  - [ ] @[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart]
  - [ ] @[client_app_v2/lib/features/reports/views/execution_reports_view.dart]
  - [ ] @[client_app_v2/lib/features/reports/views/widgets/report_artifact_card.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/audit_trail_viewer.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/comparison_matrix.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/deep_dive_expander.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/dynamic_form.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/execution_timeline.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/feedback_section.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/file_input_field.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/file_uploader.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/generic_grid.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/global_error_view.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/log_viewer.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/logic_matrix_chart.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/logic_radar_chart.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/omni_input_box.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/output_renderer.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/pdf_export_guide_dialog.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/pre_mortem_card.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/quadrant_matrix_chart.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/result_dashboard.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/schema_mapper.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/score_card.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/score_card_radar.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/specialist_section.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/unified_metric_gauge.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/validation_timeline_widget.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/workflow_selector.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify widget test coverage and 100% theme sovereignty across all 47 hardened Wave F3 views and SDUI widgets.

### Final Verification Quality Gate
- [ ] **[NOK]** Universal Frontend Quality Gate:
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build
  ```

---

# Session Handover Context

## Achieved
* Initialized **Targeted Frontend Hardening Wave F3 (`47` targets)** covering Execution & Reports Views and SDUI Widgets (`21` files) and Shared Cross-Domain Widgets (`26` files).

## Learned
* All SDUI and Execution presentation widgets must maintain 1:1 semantic parity with PDF templates (`test_sdui_semantic_parity.py`) and zero hardcoded `Color(0x...)` / `Colors.*` constants (`audit_flutter_theme_sovereignty.py`).

## Resume Command
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF3.md --gate frontend --model gemini-4-argon-medium --continue-on-failure
```

## Remaining
* Execute `auto_hardening_runner.py` across all 47 targets in Wave F3 and proceed to Wave F4 (`@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF4.md]`).
