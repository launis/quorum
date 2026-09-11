# Task Tracker: Matrix Studio XML Preview, TDA Debug Logging & XAI IA Restructuring

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_matrix_sensor_prompt_builder.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[C:\Users\risto\.gemini\antigravity-ide\brain\56fb23f3-2925-4744-9c2d-1e4665893a11\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Step 1 Constraint (`the_duct_tape_ban`): Zero silent exception swallowing, zero context wiping, and zero naked string concatenation accumulators.
- [x] Step 2 Constraint (`pydantic_v2_strictness`): Enforce ConfigDict(strict=True, extra="forbid") on updated simulation models.
- [x] Step 3 Constraint (`logfire_delegation_mandate`): Debug logs must remain isolated in data/files/executions/{execution_id}/llm_debug_prompts.md without leaking raw PII into stdout.
- [ ] Step 4 Constraint (`dynamic_vs_static_localization_ssot_mandate`): Pure Axis 1 structural chrome in Flutter ARB files, dynamic labels in database models.
- [ ] Step 5 Constraint (`desktop_pro_tool_interaction` & `universal_horizontal_overflow_immunity_mandate`): Zero RenderFlex overflow down to 360px viewport, hover states, keyboard shortcuts, and syntax-highlighted tabs.
- [ ] Step 6 Constraint (`universal_ssot_and_normalization_mandate`): Pure frontend UI grouping for Macro vs Micro extensions with zero backend schema fragmentation.
- [ ] Step 7 Constraint (`zero_compromise_quality_gate`): 100% test pass rate across backend and frontend audit loops.
- [ ] Step 8 Constraint (`tier2_hardening_knowledge`): Strict XML rule_block hierarchy, 5-field metadata.json synchronization, zero unverified paths.
- [ ] Step 9 Constraint (`timeless_as_built_mandate`): Pure timeless present-tense descriptions of current system reality; zero historical phases, Epics, or dates.

## Execution Tasks

- [x] **Step 1: Pre-Implementation Technical Debt Cleanups**
  - [x] Merge `default_validation_context` with `validation_context` in `llm_task_executor.py:148`.
  - [x] Migrate `write_debug_prompt_log` and `write_llm_telemetry_log` to async with `_get_debug_file_lock()` in `llm_debug_logger.py`.
  - [x] Update callers to `await write_debug_prompt_log` in `strategies/llm.py` and `await write_llm_telemetry_log` in `llm_task_executor.py`.
  - [x] Modernize unit tests with `@pytest.mark.asyncio`, concurrent lock test under `asyncio.TaskGroup`, and telemetry tests in `test_llm_debug_logger.py`.
  - [x] Update telemetry failure test with `new_callable=AsyncMock` in `test_llm_task_executor.py`.
  - [x] Wrap `createTestWidget` in `ProviderScope` in `scale_editor_modal_test.dart`.
  - [x] Quality gates passed: backend audit loop (100% pass, 100% coverage), flutter test (14/14 passed).
  - [x] Atomic git commit: `49c4cb2d fix(llm): serialize debug prompt logging and preserve validation context`.

- [x] **Step 2: Backend DTO Expansion & Simulation Prompt Compilation**
  - [x] Update `PromptBlockSimulationRequest` in `backend_v2/models/dtos/studio.py` (`target_scale_score`, `target_locale`, `context_text`).
  - [x] Update `simulate_prompt_block` in `backend_v2/api/routers/studio/prompt_blocks.py` to pass full DTO.
  - [x] Update `simulate_prompt_block` method signature and logic in `backend_v2/services/studio/simulation_service.py` to invoke `MatrixSensorPromptBuilder.build_compiled_prompt()`.
  - [x] Update internal `simulate_step:263` in `simulation_service.py` to pass DTO.
  - [x] Modernize all callers and assertions in `backend_v2/tests/unit/services/studio/test_simulation_service.py` and `backend_v2/tests/unit/models/dtos/test_studio.py`.
  - [x] Run backend audit loop quality gate (100% pass, 97% coverage, 0 AST warnings).

- [x] **Step 3: Full-Stack LLM Task Executor Debug Prompt Logging**
  - [x] Add `log_structured_task_prompt()` to `backend_v2/utils/llm_debug_logger.py`.
  - [x] Hook into `execute_structured_task()` in `backend_v2/services/llm_task_executor.py` for development mode.
  - [x] Update `ExtractiveSensorService._single_ensemble_call(call_idx: int)` to pass `sub_task=f"extractive_sensor_bo3_call_{call_idx}"`.
  - [x] Run backend audit loop quality gate (100% pass, strict TDD coverage met).

- [ ] **Step 4: Flutter Localization Strings Update**
  - [ ] Add `xaiHighlightsTitle`, `previewScalePromptTooltip`, `previewPromptTitle`, and tab keys to `client_app_v2/lib/l10n/app_en.arb` and `app_fi.arb`.
  - [ ] Run `flutter gen-l10n`.

- [ ] **Step 5: Flutter Scale Editor Modal XML Preview Dialog**
  - [ ] Convert `ScaleEditorModal` to `ConsumerStatefulWidget` in `scale_editor_modal.dart`.
  - [ ] Add "Esikatsele kehote" action button and 3-tab XML preview dialog.
  - [ ] Update controller and studio client to pass `targetScaleScore` and `targetLocale`.
  - [ ] Verify with widget tests.

- [ ] **Step 6: Flutter XAI Extensions Block Card IA Restructuring**
  - [ ] Restructure `XaiExtensionsBlockCard` into Macro Synthesis vs Micro Atom sections in `xai_extensions_block_card.dart`.
  - [ ] Add `// SSOT: Macro/Micro categorization for XAI extensions` comment block.
  - [ ] Update `xai_extensions_block_card_test.dart` asserting headers and 360px overflow resistance.
  - [ ] Run flutter audit loop quality gate.

- [ ] **Step 7: Automated Quality Gates & Verification**
  - [ ] Run full backend audit loop.
  - [ ] Run full flutter audit loop.
  - [ ] Run SDUI semantic parity test.

- [ ] **Step 8: Knowledge Base Hardening & Metadata Synchronization**
  - [ ] Update `ki_matrix_sensor_prompt_builder.md` and `metadata.json`.
  - [ ] Update `ki_desktop_pro_tool_studio_ux.md` and `metadata.json`.
  - [ ] Update `ki_system_audit_trail_xai.md` and `metadata.json`.

- [ ] **Step 9: Timeless As-Built Architecture Documentation**
  - [ ] Update `docs/architecture/04_server_driven_ui_and_presentation.md`.
  - [ ] Update `docs/architecture/05_resilience_and_observability.md`.
  - [ ] Update `docs/architecture/09_llm_prompt_orchestration_and_matrix_evaluation.md`.
