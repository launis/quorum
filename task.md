# Task Tracking: Scoring Double-Inversion Elimination, Multi-Input Context Targets & Quote Extraction

Implementation Plan: `docs/implementationplans/IMPLEMENTATION_PLAN_Scoring_Double_Inversion_Elimination_Context_Targets_and_Quote_Extraction.md`

- [x] **Phase 1: Pre-Implementation Technical Debt Cleanups (QGR016, Banned .get(), Broad Except & Python 2 Syntax)**
  - [x] Step 1.1: Verify Python 2 exception syntax fixes in `tda_engine.py` and `matrix_scorecard.py` (VERIFIED_EXISTING)
  - [x] Step 1.2: Eradicate banned `.get("status")` and `.get("contextual_override")` in `matrix_scorecard.py`
  - [x] Step 1.3: Clean up QGR016 and banned `.get()` lookups in `matrix_hook.py` (lines 246, 248, 274, 301, 317, 327, 397, 454)
  - [x] Step 1.4: Clean up QGR016, banned `.get()`, and broad `except Exception:` in `matrix_domain_parser.py` (lines 118, 378, 407, 412, 420, 486, 492-529)
  - [x] Step 1.5: Clean up QGR016 and banned `.get()` in `topological_evaluator.py` (lines 108, 149)
  - [x] Step 1.6: Clean up QGR016 inline semaphore fallback in `enriched_dag_executor.py` (line 95)
  - [x] Step 1.7: Clean up QGR016 ternary fallbacks in `result_projector.py` (lines 85-90)
  - [x] Step 1.8: Run AST guardrail check and backend audit loop to verify 0 QGR016 violations

- [x] **Phase 2: Eliminate Double-Inversion Bug in Matrix Hook**
  - [x] Step 2.1: Surgically update `matrix_hook.py` (lines 351–377) to eliminate `is_satisfied = not tda.inverse_evidence`
  - [x] Step 2.2: Verify with unit test `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py -k "test_matrix_scoring_hook"`

- [x] **Phase 3: Context Target Input Resolution, Flutter Model Parity & Clean-Slate Local Seeding**
  - [x] Step 3.1: Verify `MatrixPromptBlock.target_input_key` in `backend_v2/models/domain/prompt_blocks.py`
  - [x] Step 3.2: Add `@JsonKey(name: 'target_input_key') String? targetInputKey` to `PromptBlock.matrix` in `client_app_v2/lib/features/studio/models/prompt_block.dart`
  - [x] Step 3.3: Run Flutter build runner to regenerate Freezed and JsonSerializable code
  - [x] Step 3.4: Preserve `targetInputKey` in `client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart`
  - [x] Step 3.5: Populate `target_input_key` across all 13 matrix prompt blocks in `backend_v2/seed/seed_data.json`
  - [x] Step 3.6: Add `matrix_target_all` and `matrix_target_chat_log` translations in `fi.json` and `en.json`
  - [x] Step 3.7: Execute clean-slate local seeding (`uv run python backend_v2/seed/run_seed.py local`)
  - [x] Step 3.8: Replace legacy first-item break loop in `matrix_domain_parser.py` with three-tier deterministic resolution
  - [x] Step 3.9: Run backend audit loop and flutter domain parity test

- [x] **Phase 4: Sensor Quote Extraction Pipeline, AtomEvaluationResultDTO & Language-Agnostic Caching Prefix**
  - [x] Step 4.1: Define `AtomEvaluationResultDTO` in `backend_v2/models/dtos/dag_models.py` and add `source_quote` to `AtomExecutionState`
  - [x] Step 4.2: Update `BooleanEvaluationResult` in `extractive_sensor_service.py` with `source_quote` and sentence-boundary truncation validator
  - [x] Step 4.3: Add `<evidence_extraction_mandate>` in `backend_v2/models/prompts/matrix_evaluation.py`
  - [x] Step 4.4: Update `LANGUAGE_MANDATE` Exception 2 in `backend_v2/models/prompts/global_mandates.py`
  - [x] Step 4.5: Ensure language-agnostic 100% static prefix in `matrix_sensor_prompt_builder.py`
  - [x] Step 4.6: Update `extractive_sensor_service.py` to emit `dict[str, AtomEvaluationResultDTO]`
  - [x] Step 4.7: Update `enriched_dag_executor.py` and `topological_evaluator.py` to transit `AtomEvaluationResultDTO`
  - [x] Step 4.8: Update `result_projector.py` to project `source_quote` and enforce `contextual_override = False` when quote present
  - [x] Step 4.9: Run quality gates on affected orchestrator files

- [x] **Phase 5: ISTQB Unit & Integration Test Expansion**
  - [x] Step 5.1: Expand scoring hook tests in `backend_v2/tests/unit/hooks/test_scoring.py`
  - [x] Step 5.2: Expand parser tests in `backend_v2/tests/unit/services/test_matrix_domain_parser.py`
  - [x] Step 5.3: Add sensor quote extraction and consensus tests in `test_extractive_sensor_service.py`
  - [x] Step 5.4: Add `AtomEvaluationResultDTO` and max_length tests in `test_dag_models.py`
  - [x] Step 5.5: Update mock fixtures across `test_enriched_dag_executor.py`, `test_topological_evaluator.py`, and integration tests

- [ ] **Phase 6: Global Audit, Clean Slate Trace Replay & SDUI Parity Validation**
  - [ ] Step 6.1: Run full backend audit loop across scoring hooks, parser, and sensor orchestrator
  - [ ] Step 6.2: Run SDUI semantic parity test (`backend_v2/tests/integration/test_sdui_semantic_parity.py`)
  - [ ] Step 6.3: Run Flutter audit loop on domain parity and SDUI matrix table widget
  - [ ] Step 6.4: Execute offline trace replay verification against `exe_88267cb7b3cf4718ae76b7dbce04a92e`
