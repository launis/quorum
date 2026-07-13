# Epic 94: Frontend SDUI Synchronization (Flutter V2) - Tracker

**Objective:** Synchronize the Flutter Frontend's Dart 3 Freezed models, Riverpod state managers, and Widget rendering components with the new Backend ReportDataDto contract.

## Tasks Execution List

- [x] `[OK]` Phase 1: Freezed Models Synchronization (Execute `docs/epic/tasks_EPIC_94_Frontend_SDUI_Synchronization/phase_1_models.md`)
- [x] `[OK]` Phase 2: Riverpod State Providers (Execute `docs/epic/tasks_EPIC_94_Frontend_SDUI_Synchronization/phase_2_providers.md`)
- [x] `[OK]` Phase 3: SDUI Widget Rendering Components (Execute `docs/epic/tasks_EPIC_94_Frontend_SDUI_Synchronization/phase_3_sdui_widgets.md`)
- [x] `[OK]` Tier 2 Hardening (Run `/tier2-hardening-frontend` targeted at the newly created `models` and `providers` directories to modernize to Freezed strictness)
- [ ] `[NOK]` Phase 4: Proxy Sunset & Consumer Migration (Codebase-wide search/replace old import paths to bypass proxies before deleting legacy `ReportDataDTO` and `ScorecardDTO` models)
- [ ] `[NOK]` Pre-Delete Audit (Verify no orphaned dependencies remain and completely DELETED the original legacy models and views)
- [ ] `[NOK]` Baseline Parity & Zero-Loss Audit (Mathematically verify that the final test count and coverage match or exceed the Phase 1 baseline)
- [ ] `[NOK]` Knowledge Item Generation (Create a KI in the IDE's Knowledge Base documenting the new SDUI Freezed Model structures and O(1) Riverpod caching)
- [ ] `[NOK]` Update Directory Reference Laws (Ensure `.agents/rules/04_directory_reference.md` reflects the sunset of legacy models and the strict UI decoupling).

---

## Instructions for the Execution Agent
1. When you start, load the context by running the resume command provided below.
2. You MUST strictly execute each `[NOK]` step sequentially using the `/tier2-execute` workflow for the `phase_X.md` files.
3. At the end of your session (after a set of files or logical chunk), you MUST update the `[ ]` to `[x]` in this tracker, update the Session Handover Context block below, and update the `--workflow` / `--target` parameters in the resume command before concluding.

---

# Session Handover Context
**Achieved**: Completed Tier 2 Hardening for BOTH `client_app_v2/lib/features/execution/models` and `client_app_v2/lib/features/execution/providers`. Removed `silent_json_fallbacks` and implemented strict `AppException.validation` Fail-Fast crashes for missing base data (e.g., null ReportDataDto). Tests and audit loops are fully passing (GREEN).
**Learned**: Riverpod providers returning nullable types still require downstream consumers to Fail-Fast manually when fetching data via `ref.watch`. `ProviderException` correctly wraps `AppException` internally within Riverpod's testing container and `throwsA(predicate(...))` is the safest way to assert it.
**Remaining**: Phase 4: Proxy Sunset & Consumer Migration (Codebase-wide search/replace old import paths to bypass proxies before deleting legacy `ReportDataDTO` and `ScorecardDTO` models).

## Next Session Resume Command
`To resume execution, start a NEW chat session and run:`
`/tier5-resume --workflow=/tier3-feature-refactor --target="docs/epic/EPIC_94_Frontend_SDUI_Synchronization_tracker.md" --achieved="Tier 2 Hardening for SDUI models and providers complete" --learned="Riverpod null-state requires explicit Exception throwing for Fail-Fast" --remaining="Phase 4: Proxy Sunset & Consumer Migration" --rules="c:\src\quorum\.agents\rules\00-antigravity-core.md, c:\src\quorum\.agents\rules\02_flutter_desktop.md"`
