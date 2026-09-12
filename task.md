# Task Tracker: Dynamic Studio-Configured Variance Validation Architecture (Zero Duct-Tape)

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[c:\Users\risto\.gemini\antigravity-ide\brain\57b1f10f-6c53-4974-bf56-d948e98351fc\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Step 0: Clean up existing test technical debt so test suite compiles without MyPy errors.
- [x] Step 1: Maintain 100% strict Pydantic V2 typing (ConfigDict(strict=True, extra="forbid")).
- [x] Step 2: Enforce Dual-Axis localization and Freezed 1:1 parity with Python snake_case.
- [x] Step 3: Preserve local database modifications and maintain JSON schema integrity.
- [x] Step 4: Fail-fast with clear AppException if variance validation is requested but target block is missing or not evaluated.
- [x] Step 5: 100% tests green, 0 linter warnings, 0 type errors.

## Execution Tasks
- [x] **Step 0: PRE_IMPLEMENTATION_CLEANUPS**
  - [x] 0.1: Fix `ExecutionRecord` instantiations in `test_worker_synthesis.py` (lines 55, 216) to include `progress=None, status_message=None`
  - [x] 0.2: Fix `_find_profile_syntheses` return type handling in `test_worker_synthesis.py`
  - [x] 0.3: Guard `expected_snippet` assertion with `assert expected_snippet is not None` in `test_worker_synthesis.py`
  - [x] 0.4: Verify `test_worker_synthesis.py` passes MyPy with zero errors
- [x] **Step 1: BACKEND_MODELS_AND_DTO_UPDATE**
  - [x] 1.1: Add `variance_target_block: str | None = None` to `OutputProfile` (`backend_v2/models/v2_core.py`)
  - [x] 1.2: Add `@model_validator(mode="after")` to `OutputProfile` enforcing `variance_target_block` when variance validation is active
  - [x] 1.3: Add `variance_target_block` to DTOs in `backend_v2/models/dtos/output_profile.py` (`OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, `OutputProfileResponseDTO`)
  - [x] 1.4: Update mock profile test fixtures (`test_blueprint_sdui_crash.py`, `test_blueprint.py`, `test_worker.py`, `test_output_profile.py`) to declare `variance_target_block`
- [x] **Step 2: FRONTEND_FREEZED_MODEL_AND_STUDIO_CARD_UPDATE**
  - [x] 2.1: Add `@JsonKey(name: 'variance_target_block') String? varianceTargetBlock` to `OutputProfile` in `output_profile.dart`
  - [x] 2.2: Run Freezed code generation via `flutter_audit_loop.py`
  - [x] 2.3: Update `VarianceBlockCard` to accept `allowedBlockIds` and `promptBlocksState`, adding `DropdownButtonFormField<String>`
  - [x] 2.4: Forward `allowedBlockIds` and `promptBlocksState` in `BlockCardRegistry`
  - [x] 2.5: Add localized keys `profileVarianceTargetBlockLabel` and `profileVarianceTargetBlockHint` in `app_en.arb` and `app_fi.arb` and run `flutter gen-l10n`
  - [x] 2.6: Update `block_card_registry_test.dart` to pass required arguments to `VarianceBlockCard`
- [x] **Step 3: SEED_DATA_SYNCHRONIZATION**
  - [x] 3.1: Set `"variance_target_block": "blk_53f32679aa514fcb"` on `prf_5d6e7f8091a2b3c4`, `prf_02b1d71000000002`, `prf_03b1d71000000003` in `seed_data.json`
  - [x] 3.2: Set `"variance_target_block": "blk_fb15f8dcf23f4865"` on `prf_05b1d71000000005` in `seed_data.json`
  - [x] 3.3: Verify seed vault with `run_seed.py local --dry-run` and `audit_database_atoms.py`
- [x] **Step 4: WORKER_DIRECT_EXTRACTION_REFACTOR**
  - [x] 4.1: Delete `_DETECTOR_STEP_MARKERS` tuple completely from `backend_v2/worker.py`
  - [x] 4.2: Retrieve `target_block_id = active_profile_dto.variance_target_block` and extract `out_content[target_block_id]` in `worker.py`
  - [x] 4.3: Enforce Fail-Fast with `AppException` if variance validation is requested but `variance_target_block` is missing
- [x] **Step 5: ISTQB_TEST_EXPANSION_AND_AUDIT_VERIFICATION**
  - [x] 5.1: Update `_setup_mock_repo_for_metrics` to set `variance_target_block="blk_53f32679aa514fcb"`
  - [x] 5.2: Verify positive test: `test_worker_synthesis_extracts_metrics_for_coach_goodhart_step`
  - [x] 5.3: Add negative test: `test_worker_synthesis_missing_variance_target_block_raises_configuration_error`
  - [x] 5.4: Add negative test: `test_worker_synthesis_unevaluated_target_block_handled_gracefully`
  - [x] 5.5: Run full backend and frontend audit loops

# Session Handover Context
- **Achieved:**
  1. Elevated `variance_target_block` into a first-class, dynamic configuration attribute across Python Pydantic V2 models (`OutputProfile`, DTOs) and Flutter Dart Freezed models with 1:1 serialization contracts.
  2. Implemented Fail-Fast `@model_validator(mode="after")` on `OutputProfile` ensuring that if variance validation is active (`TargetBlockType.VARIANCE_VALIDATION_BLOCK` or `XaiExtensionType.VARIANCE_VALIDATION`), `variance_target_block` must be declared.
  3. Extended Quorum Studio UI: `VarianceBlockCard` now features a reactive `DropdownButtonFormField<String>` bound to workflow matrix blocks with Dual-Axis localization (`app_en.arb`, `app_fi.arb`).
  4. Synchronized `seed_data.json` with authoritative target block IDs (`blk_53f32679aa514fcb`, `blk_fb15f8dcf23f4865`), verified with 0 errors via `audit_database_atoms.py` and `run_seed.py local --dry-run`.
  5. Purged legacy heuristic duct-tape `_DETECTOR_STEP_MARKERS` and arbitrary block scanning from `backend_v2/worker.py`, replacing it with strict deterministic target block extraction directly from `out_content[target_block_id]`.
  6. Implemented ISTQB negative and positive unit tests in `test_worker_synthesis.py`.
  7. All quality gates pass: Ruff, MyPy strict, AST Guardrails, Flutter analyze, Flutter test, and SDUI semantic parity.
- **Learnings:**
  - `OutputProfile` default `target_block_order` should not include `VARIANCE_VALIDATION_BLOCK` by default unless `variance_target_block` is populated, ensuring default factory instantiation does not trigger validation failure. Tests requiring variance rendering must explicitly include `VARIANCE_VALIDATION_BLOCK` in `target_block_order`.
- **Remaining:** None. All tasks in plan completed.
