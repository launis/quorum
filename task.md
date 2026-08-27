# Task Execution Tracker: Theory Grounding Dual Injection Elimination, Engine Dispatch & NodeExecutor Decomposition

## Phase 0: PRE-REQUISITE CLEANUP & STALE MOCK REMOVAL
- [x] Step 0.1: Remove stale mock in `test_llm_cost_tracking.py`
- [x] Step 0.2: Clean `LLMNodeStrategy` technical debt (strict enums, eliminate duck-typing, remove silent pass)

## Phase 1: PROMPT BUILDER REFACTOR & UNIT TESTS
- [x] Step 1.1: Isolate prompt builder theory grounding logic in `matrix_sensor_prompt_builder.py`
- [x] Step 1.2: Update matrix sensor prompt builder unit tests (`test_matrix_sensor_prompt_builder.py`)
- [x] Step 1.3: Update root unit test `test_matrix_sensor_prompt_builder.py`

## Phase 2: ENGINE DECOMPOSITION, STRATEGY REGISTRY & DAG CONCURRENCY
- [x] Step 2.1: Declare `StrategyDependencies` and context injection in `strategies/base.py`
- [x] Step 2.2: Implement `PromptEngine` for structured tasks in `engines/prompt_engine.py` and export in `engines/__init__.py`
- [x] Step 2.3: Declare canonical `StepType(StrEnum)` in `enums.py` and `Step.type` in `v2_core.py`
- [x] Step 2.4: Implement polymorphic strategy registry in `strategies/registry.py` (`NODE_STRATEGY_REGISTRY`, `NodeStrategyFactory`)
- [x] Step 2.5: Fail-Fast prompt block batch resolution in `interfaces.py` and `repositories/components/prompt_block.py`
- [x] Step 2.6: Decompose `NodeExecutor` and implement DAG executor atomic accumulators in `dag_executor.py`
- [x] Step 2.7: Align `LLMNodeStrategy` payload compilation and injected blocks consumption in `strategies/llm.py`
- [x] Step 2.8: Create test suites (`test_prompt_engine.py`, `test_node_strategy_registry.py`, `test_dag_executor_mcp_concurrency.py`, `test_prompt_block.py`) and migrate test mocks to typed Pydantic models

## Phase 3: GHOST EXECUTION ELIMINATION & SOURCE VERIFICATION HARDENING
- [x] Step 3.1: Declare `SourceVerificationInputsDTO` in `source_extraction_schema.py` and harden `source_verification_service.py`
- [x] Step 3.2: Register `source_verification_hook` with `@hook_registry.register` and defensive short-circuit envelope
- [x] Step 3.3: Unit tests and hook test suite (`test_source_verification_service.py`, `test_source_verification_hook.py`)

## Phase 4: DETERMINISTIC SEED MIGRATION
- [x] Step 4.1: Create timestamped backup of `seed_data.json` in `backend_v2/seed/backups/`
- [x] Step 4.2: Surgically sanitize `ai_description` across all 13 matrices in `seed_data.json` removing duplicate `EPISTEMIC ANCHOR:` tails
- [x] Step 4.3: Verify seed JSON integrity and reseed local database (`run_seed.py local`)

## Phase 5: AST GUARDRAILS & GLOBAL QUALITY GATE
- [x] Step 5.1: Implement AST Theory Grounding Guardrails in `test_ast_theory_grounding_guardrails.py`
- [x] Step 5.2: Execute global backend audit loop (`backend_audit_loop.py backend_v2 --test`)

---

## Learnings & Architectural Notes
- `TemplateProcessor.safe_interpolate` wraps `<theory_context>\n{c}\n</theory_context>` cleanly without escaping URLs or leaving broken XML tags.
- `NodeStrategyFactory` strictly uses `NODE_STRATEGY_REGISTRY[step_type]` mapping, failing fast with `ErrorCodes.CONFIGURATION_ERROR` if an unsupported step type is requested.
- `DAGExecutor.run_step_wrapper` synchronizes `mcp_tool_audit` and `generated_schemas` accumulation under `async with _update_lock:`, preventing race conditions during parallel `asyncio.TaskGroup` step runs.
- `SourceVerificationHook` returns a complete `SourceVerificationResultDTO` envelope with `total_claims=0` when inputs are empty or whitespace-only, preventing ghost LLM executions and maintaining strict schema expectations downstream.
- Reseeding `db_v2.json` with sanitized matrix prompt blocks confirms 90 prompt blocks, 13 matrices with valid `TheoryGrounding` DTOs, and zero `EPISTEMIC ANCHOR:` duplicate tails.
