# Task Tracking: Complete Root-Cause Elimination of Permissive Typing Bypasses

- [x] **Phase 1: Pre-Implementation Cleanups & AST Guardrail Directives Locking**
  - [x] Harden QGR012 severity to FATAL in `scripts/_ast_guardrails.py` for all non-test paths (including database/repositories)
  - [x] Lock `no_naked_dicts_in_state` and `polymorphic_dag_payload_handling` in `.agents/rules/01-python-backend.md`
  - [x] Update SSOT table and guidance in `ki_ast_guardrail_engine.md`
  - [x] Run AST guardrail tests & backend audit loop

- [x] **Phase 2: Elimination of `match/case dict` and Hydration Duct-Tape**
  - [x] Refactor `backend_v2/services/studio/output_profile_service.py` (`data: OutputProfile`, delete `case dict()` & `case {"id": ...}`)
  - [x] Refactor `backend_v2/services/progress.py` (replace `match/case dict()` with typed conditional flatten)
  - [x] Refactor `backend_v2/services/studio/prompt_block_service.py` (delete `case {"id": ...}`)
  - [x] Refactor `backend_v2/services/studio/workflow_service.py` (delete all 3 `case {"id": ...}`)
  - [x] Run tests & backend audit loop

- [x] **Phase 3: Typed Prompt Messages & LLM Adapter Remediation (`QGR002`) — ATOMIC BATCH**
  - [x] Refactor `backend_v2/models/prompt.py` (`CompiledPrompt` validation & role merging)
  - [x] Refactor `backend_v2/llm/adapters/base_adapter.py` (direct `msg.role` and `msg.content` via `ChatMessageDTO`)
  - [x] Refactor `backend_v2/llm/adapters/ai_studio_adapter.py` (direct `msg.role` and `msg.content` via `ChatMessageDTO`)
  - [x] Refactor `backend_v2/llm/adapters/vertex_adapter.py` (direct `msg.role` and `msg.content` via `ChatMessageDTO`)
  - [x] Refactor `backend_v2/services/orchestrator/prompt_compiler_adapter.py` (accept `list[ChatMessageDTO]`, typed returns, explicit facade)
  - [x] Run prompt compiler adapter & caching integration unit tests

- [x] **Phase 4: Reflection, Exception & Schema Rigor (`QGR001`, `QGR003`, `QGR007`)**
  - [x] Refactor `backend_v2/main.py` (`isinstance(pool, ArqRedis | FakeRedis)`)
  - [x] Refactor `backend_v2/services/orchestrator/context_router.py` (expand unit test coverage to 92%)
  - [x] Verify `backend_v2/core/registry.py` and `backend_v2/services/cache/typed_cache.py`
  - [x] Run tests & backend audit loop (All 4 targets passed)

- [ ] **Phase 5: Hooks Layer Typed DTOs (`QGR012` — 17 Files, 50 suppressions)**
  - [x] Sub-Phase 5A: Scoring Hooks (4 files: matrix_hook, falsifier_hook, normalization_hook, passivity_hook)
  - [ ] Sub-Phase 5B: Validation, Ingress & Data Hooks (8 files: validation, input_processing, integrity, hydration, linguistics, llm, source_verification_hook, references)
  - [ ] Sub-Phase 5C: Peripheral & Metadata Hooks (5 files: metadata, metrics, archival, dlq_guard, interaction_hook)

- [ ] **Phase 6: Services & Orchestrator Layer Typed DTOs (`QGR012` — 19 Files, 82 suppressions)**
  - [ ] Sub-Phase 6A: Core Orchestrator (5 files: llm, execution_time_resolver, context_builder, matrix_explanation_service, prompt_compiler)
  - [ ] Sub-Phase 6B: DAG, Synthesis & Extraction (7 files: dag_executor, synthesis_payload_compressor, matrix_domain_parser, context_router, extraction_schema_factory, rag_preflight_service, matrix_reducer)
  - [ ] Sub-Phase 6C: Remaining Services (7 files: blueprint.py (11 QGR012!), execution.py, synthesis_engine, tda_engine, localization_compiler, synthesis_distiller, document_extraction)

- [ ] **Phase 7: Repository Refactoring & `cast(Any, ...)` Elimination**
  - [ ] Refactor `backend_v2/database/repositories/execution.py` (4 QGR012 via TypeAdapter, remove suppressions)
  - [ ] Eliminate `cast(Any, ...)` across backend_v2 (run_worker.py, core/registry.py, services/execution.py, strategies/llm.py)
  - [ ] Run all verification scripts (Zero QGR, Zero isinstance dict, Zero match/case dict, AST strict gate, SDUI parity, backend audit loop)
