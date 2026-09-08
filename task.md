# Task Tracker: Dynamic Profile-Governed Penalties & Tripartite Harmonization (Zero-Fallback Architecture)

<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_adapter_pattern.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[C:\Users\risto\.gemini\antigravity-ide\brain\3680a9b5-579a-4799-9bb4-1e513a4082b2\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Constraint: `anti_duplication` - Ensure zero dangling imports of `ScoringPenalty` across the entire codebase.
- [x] Constraint: `zero_service_layer_fallbacks` - Fields must be non-nullable float (never float | None) on persistence and response models to prevent downstream fallback chains.
- [x] Constraint: `zero_permissive_typing` - Ensure `model_config = ConfigDict(strict=True, extra="forbid")` remains intact on all modified models.
- [x] Constraint: `sdui_contract_fracture_prevention` - Verify 1:1 serialization naming between Python `snake_case` and Dart `camelCase`.
- [x] Constraint: `live_database_mutation` - Never modify `data/db_v2.json` directly. Edit `seed_data.json` and sync via seeder.
- [x] Constraint: `the_duct_tape_ban` - Maintain raw truth purity in Phase 1 execution data; zero text mutilation or irreversible destructive math in DAG steps.
- [x] Constraint: `universal_fail_fast` - Raise explicit `AppException` with `ErrorCodes.VALIDATION_FAILED` if state structure is corrupted.
- [x] Constraint: `zero_service_layer_fallbacks` - Zero tolerance for fallback operators (or, .get, or global settings). If profile data is missing, fail fast.
- [x] Constraint: `sdui_adapter_dumb_painter` - Pass pre-calculated `penalties_applied` into `AdapterContext`.
- [x] Constraint: `cross_language_mapping_mandate` - All static localization keys defined in `en.json` and `fi.json`; no hardcoded Finnish strings in Python code.
- [x] Constraint: `monolithic_god_widgets` - Keep widgets modular; use existing `AppSpacing` and `Theme.of(context)` tokens.

## Execution Tasks

- [x] **Phase 1: Technical Debt Pre-Requisites and Schema Harmonization**
  - [x] Step 1.1: Demolish Dead ScoringPenalty Enum (`backend_v2/models/enums.py`).
  - [x] Step 1.2: Extend Output Profile Schemas Backend Zero-Fallback (`backend_v2/models/dtos/output_profile.py`, `backend_v2/models/v2_core.py`).
  - [x] Step 1.3: Extend Output Profile Freezed Model Frontend Zero-Fallback (`client_app_v2/lib/features/studio/models/output_profile.dart`).
  - [x] Step 1.4: Seed Data Profile Alignment (`backend_v2/seed/seed_data.json`).
  - [x] Quality Gate: Run backend and flutter audit loops for Phase 1.

- [x] **Phase 2: Phase 1 Execution Hook Refactoring**
  - [x] Step 2.1: Refactor Passivity Hook Purity (`backend_v2/hooks/scoring/passivity_hook.py`).
  - [x] Step 2.2: Harmonize Scoring Hook Passivity Detection Zero-Fallback (`backend_v2/hooks/scoring/falsifier_hook.py`).
  - [x] Quality Gate: Run backend audit loop for Phase 2.

- [x] **Phase 3: Phase 3 SDUI and Blueprint Dynamic Penalties**
  - [x] Step 3.1: Dynamic Profile Penalty Calculation Zero-Fallback (`backend_v2/services/blueprint.py`).
  - [x] Step 3.2: Localized Penalties Adapter Zero-Fallback (`backend_v2/services/sdui/adapters/penalties_adapter.py`).
  - [x] Step 3.3: Add Localization Keys Backend (`backend_v2/l10n/fi.json`, `backend_v2/l10n/en.json`).
  - [x] Quality Gate: Run backend audit loop and SDUI parity test for Phase 3.

- [x] **Phase 4: Flutter Studio UI Integration**
  - [x] Step 4.1: Add Localization Keys Frontend (`client_app_v2/lib/l10n/app_fi.arb`, `client_app_v2/lib/l10n/app_en.arb`).
  - [x] Step 4.2: Integrate Controls into Profile Scoring Tab (`client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart`).
  - [x] Quality Gate: Run flutter audit loop for Phase 4.

- [x] **Phase 5: Quality Gates and Verification**
  - [x] Step 5.1: Unit Test Expansion Backend (`backend_v2/tests/unit/hooks/test_scoring.py`, `backend_v2/tests/unit/services/sdui/adapters/test_penalties_adapter.py`, `backend_v2/tests/unit/services/test_blueprint.py`).
  - [x] Step 5.2: Execute Quality Gates (Backend audit loop, Flutter audit loop, Seed dry-run, Live E2E variance verification).

## Session Handover Context
- **Achieved**: All 5 phases completed and verified 100% under Continuous Full-Auto Mode.
  - Demolished dead `ScoringPenalty` Enum.
  - Extended backend schemas (`OutputProfile`, `OutputProfileCreateDTO`, `OutputProfileResponseDTO`, `OutputProfileUpdateDTO`) and Flutter Freezed model with non-nullable default `0.0` penalties (`security_penalty`, `post_hoc_penalty`, `passivity_penalty`).
  - Updated `seed_data.json` profile with `0.0` default penalties and verified via dry-run seeder.
  - Preserved raw execution purity in `passivity_hook.py` (emits `HookDeltaDTO(delta={"passivity_detected": True})` without mutating raw scores or prepending strings).
  - Recorded observation tokens (`PENALTY_SECURITY`, `PENALTY_POST_HOC`, `PENALTY_PASSIVITY`) in `falsifier_hook.py`.
  - Calibrated dynamic profile deductions in `blueprint.py` (`effective_penalty = min(total, 0.40)`).
  - Built localized `PenaltiesAdapter` with `PENALTIES_RULES` aesthetics mapping and Finnish/English `AlertBlock` rendering.
  - Added localization keys to backend JSONs and frontend ARB files.
  - Added "Automaattiset pistevähennykset" Card to `profile_scoring_tab.dart`.
  - Quality gates verified: 3033 backend tests passing (94.22% coverage), Flutter audit loop 0 issues, seeder dry-run passed, SDUI semantic parity passed, live E2E variance test passed (0.0% variance, Fleiss Kappa 1.0000).
- **Learned**: Profile-governed scoring penalties isolate observation registration (Phase 1) from presentation synthesis and scoring calibration (Phase 3), achieving complete tripartite pipeline decoupling and zero-fallback strict typing.
- **Remaining**: Implementation complete. Ready for atomic git commit.
