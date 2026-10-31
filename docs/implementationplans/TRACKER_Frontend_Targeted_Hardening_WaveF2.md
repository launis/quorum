# Tracker: Targeted Frontend Hardening Wave F2 (Freezed Domain & DTO Models + Riverpod Controllers & Providers)

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

**Plan:** @[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md] (Askel 5.2: Vaihe 4b - Wave F2)

- [ ] **[NOK] Execution:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF2.md --gate frontend --model gemini-4-argon-medium --continue-on-failure`

### Post-Implementation Gates

- [x] **[SKIPPED] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF2.md]" --gate backend --model gemini-4-argon-medium` (Zero backend targets in frontend targeted hardening).
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF2.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend {target}'"`
  - [ ] @[client_app_v2/lib/features/execution/models/atom_result_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_metadata.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_metrics_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_record.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_step.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_summary_snapshot.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/synthesis_config_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/tda_state.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/trace_context_carrier.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/workflow_inputs.dart]
  - [ ] @[client_app_v2/lib/features/reports/models/report_artifact.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/blueprint_config.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/gcp_location.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/llm_platform.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/model_config.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/output_profile.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/prompt_block.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/step_simulation.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/workflow.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/workflow_simulation.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/workflow_ui_schema.dart]
  - [ ] @[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]
  - [ ] @[client_app_v2/lib/features/execution/controllers/execution_controller.dart]
  - [ ] @[client_app_v2/lib/features/execution/providers/atom_result_provider.dart]
  - [ ] @[client_app_v2/lib/features/execution/providers/hydrated_reference_provider.dart]
  - [ ] @[client_app_v2/lib/features/execution/providers/report_data_v2_provider.dart]
  - [ ] @[client_app_v2/lib/features/reports/controllers/report_artifact_controller.dart]
  - [ ] @[client_app_v2/lib/features/settings/presentation/settings_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/blueprint_editor_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/model_registry_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/studio_controller.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify unit test coverage across all 44 hardened Wave F2 Freezed models and Riverpod controllers.

### Final Verification Quality Gate
- [ ] **[NOK]** Universal Frontend Quality Gate:
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build
  ```

---

# Session Handover Context

## Achieved
* Initialized **Targeted Frontend Hardening Wave F2 (`44` targets)** covering Execution Freezed Models (`18` files), Studio & Reports Freezed Models + Cloner Utils (`14` files), and Riverpod Controllers & State Providers (`12` files).

## Learned
* All Freezed DTO models must enforce 1:1 field parity with Backend Pydantic V2 schemas (`audit_dto_parity.py`) and 32-hex RFC 9562 `PrefixedUUID7` identifiers without fallback defaults.

## Resume Command
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF2.md --gate frontend --model gemini-4-argon-medium --continue-on-failure
```

## Remaining
* Execute `auto_hardening_runner.py` across all 44 targets in Wave F2 and proceed to Wave F3 (`@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF3.md]`).
