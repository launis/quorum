# Tracker: Targeted Frontend Hardening Wave F1 (Core, Network, API Clients, Error Boundaries, Theme, Shell & Shared Models)

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

**Plan:** @[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md] (Askel 5.1: Vaihe 4b - Wave F1)

- [ ] **[NOK] Execution:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md --gate frontend --model gemini-4-argon-medium --continue-on-failure`

### Post-Implementation Gates

- [x] **[SKIPPED] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md]" --gate backend --model gemini-4-argon-medium` (Zero backend targets in frontend targeted hardening).
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend {target}'"`
  - [ ] @[client_app_v2/lib/main.dart]
  - [ ] @[client_app_v2/lib/app.dart]
  - [ ] @[client_app_v2/lib/app_config.dart]
  - [ ] @[client_app_v2/lib/firebase_options.dart]
  - [ ] @[client_app_v2/lib/router/router.dart]
  - [ ] @[client_app_v2/lib/router/scaffold_with_nav.dart]
  - [ ] @[client_app_v2/lib/features/shell/presentation/scaffold_with_nav.dart]
  - [ ] @[client_app_v2/lib/features/shell/presentation/widgets/admin_sidebar.dart]
  - [ ] @[client_app_v2/lib/theme/app_colors.dart]
  - [ ] @[client_app_v2/lib/theme/app_durations.dart]
  - [ ] @[client_app_v2/lib/theme/app_theme.dart]
  - [ ] @[client_app_v2/lib/core/api/execution_client.dart]
  - [ ] @[client_app_v2/lib/core/api/reports_client.dart]
  - [ ] @[client_app_v2/lib/core/api/sse_client.dart]
  - [ ] @[client_app_v2/lib/core/api/studio_client.dart]
  - [ ] @[client_app_v2/lib/core/api/workflow_client.dart]
  - [ ] @[client_app_v2/lib/core/network/api_client.dart]
  - [ ] @[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart]
  - [ ] @[client_app_v2/lib/core/network/interceptors/dio_logger_interceptor.dart]
  - [ ] @[client_app_v2/lib/core/network/interceptors/error_interceptor.dart]
  - [ ] @[client_app_v2/lib/core/network/interceptors/locale_interceptor.dart]
  - [ ] @[client_app_v2/lib/core/environment/env.dart]
  - [ ] @[client_app_v2/lib/core/error/app_error_boundary.dart]
  - [ ] @[client_app_v2/lib/core/error/app_error_ext.dart]
  - [ ] @[client_app_v2/lib/core/error/app_exception.dart]
  - [ ] @[client_app_v2/lib/core/error/validation_error_reason.dart]
  - [ ] @[client_app_v2/lib/core/logging/app_logger_observer.dart]
  - [ ] @[client_app_v2/lib/core/logging/logger_service.dart]
  - [ ] @[client_app_v2/lib/core/models/enums.dart]
  - [ ] @[client_app_v2/lib/core/models/generic_status_response_dto.dart]
  - [ ] @[client_app_v2/lib/core/models/prompt_block_category.dart]
  - [ ] @[client_app_v2/lib/core/state/mutation.dart]
  - [ ] @[client_app_v2/lib/core/theme/app_spacing.dart]
  - [ ] @[client_app_v2/lib/core/ui/error_view.dart]
  - [ ] @[client_app_v2/lib/core/ui/splash_screen.dart]
  - [ ] @[client_app_v2/lib/core/utils/safe_isolate.dart]
  - [ ] @[client_app_v2/lib/utils/json_converters.dart]
  - [ ] @[client_app_v2/lib/utils/riverpod_extensions.dart]
  - [ ] @[client_app_v2/lib/shared/models/i18n_text.dart]
  - [ ] @[client_app_v2/lib/shared/models/sdui_block_dto.dart]
  - [ ] @[client_app_v2/lib/features/settings/domain/models/app_settings_state.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify unit and widget test coverage across all 41 hardened Wave F1 modules.

### Final Verification Quality Gate
- [ ] **[NOK]** Universal Frontend Quality Gate:
  ```powershell
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build
  ```

---

# Session Handover Context

## Achieved
* Initialized **Targeted Frontend Hardening Wave F1 (`41` targets)** covering Root, Routing, Shell, Theme (`11` files), Core API Clients & Dio Network Interceptors (`10` files), and Core Error Boundaries, Logging, Models, Utils & Shared DTOs (`20` files).

## Learned
* `auto_hardening_runner.py` leverages `data/hardening_cache.json` SHA-256 composite digests across target `.dart` files, their paired `client_app_v2/test/` unit/widget tests, and `.agents/rules/` to short-circuit already-hardened unchanged targets in `0.0s` while enforcing full `flutter_audit_loop.py` and `audit_flutter_theme_sovereignty.py` gates on all modified targets.

## Resume Command
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF1.md --gate frontend --model gemini-4-argon-medium --continue-on-failure
```

## Remaining
* Execute `auto_hardening_runner.py` across all 41 targets in Wave F1 and proceed to Wave F2 (`@[docs/implementationplans/TRACKER_Frontend_Targeted_Hardening_WaveF2.md]`).
