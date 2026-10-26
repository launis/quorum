<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Symbol & Blast-Radius Migration Map: `backend_v2/services/orchestrator/strategies/llm.py`

## 1. Executive Summary & Monolith Archetype Profile
- **Source Monolith**: `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]` (1,091 lines, 1 class `LLMNodeStrategy` with 4 methods, 4 module constants, 1 PEP 695 type alias).
- **Target Domain Package**: `backend_v2/services/orchestrator/strategies/llm_strategy/`
- **Monolith Archetype**: **Archetype D — Macro Orchestrator & Concurrency Core** (`LLMNodeStrategy.execute` spans 872 lines `#L220-L1091` as an imperative sequential orchestration pipeline).
- **Test Baseline (`[BASELINE]`)**: 45 passing unit tests (`test_llm.py`, `test_llm_cost_tracking.py`, `test_llm_strategy.py`), **94% line coverage** (511 statements, 33 missed). Exceeds the 75% minimum coverage gate (`Phase 0` skipped).
- **Invariant Set ($\mathcal{I}_{orig}$)**:
  1. **Two-Tier Concurrency Guard**: `LLMNodeStrategy.execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`) explicitly rejects `semaphore` and `running_event` in `kwargs` with `AppValidationError` (`ErrorCodes.VALIDATION_ERROR`) and bounds anomaly retries via `get_settings().llm_max_retries`.
  2. **Stateless Sub-Services**: Zero execution-scoped mutable state attributes (`self.<attr> = ...`) across coroutines; `self._deps` and `self._engine` are bound immutably in `LLMNodeStrategy.__init__` (`@[backend_v2/services/orchestrator/strategies/llm.py#L93-L105]`).
  3. **RFC 7807 Dual-Reporting & DLP Parity**: Every `ConfigurationError`, `ResourceNotFoundError`, `StateTransitionError`, and `AppValidationError` is preceded by structured `logger.error` logging using Opaque Stripe IDs without serializing raw user prompts or PII.
  4. **OpenTelemetry Span Parity**: `tracer.start_as_current_span("orchestrator.strategy.llm")` wraps step execution and records `quorum.step.id`, `quorum.step.name`, `quorum.step.type`, `quorum.step.tier`, `quorum.step.tokens`, and `quorum.step.duration_s`.

---

## 2. AST Symbol-to-Target Module Mapping

| Symbol Name | AST Kind & Source Line Bounds | Target Module (Epoch 1) | Visibility / Export Facade |
| :--- | :--- | :--- | :--- |
| `_SCHEMA_BLOCK_MATRIX`, `_SCHEMA_BLOCK_TEXT`, `_SCHEMA_BLOCK_EXTENSION`, `_SCHEMA_BLOCK_SYSTEM` | Module `Constant` (`#L77-L80`) | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` | Re-exported in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` |
| `NodeStatePayload` | PEP 695 `TypeAlias` (`#L82-L82`) | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` | Re-exported in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` |
| `LLMNodeStrategy._dlq_handle_debug_log_error` | `@staticmethod def` (`@[backend_v2/services/orchestrator/strategies/llm.py#L107-L114]`) | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` (`dlq_handle_debug_log_error`) | Delegated on `LLMNodeStrategy._dlq_handle_debug_log_error` in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` |
| `LLMNodeStrategy._extract_step_context_metadata` | `def` (`@[backend_v2/services/orchestrator/strategies/llm.py#L116-L218]`) | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` (`extract_step_context_metadata`) | Delegated on `LLMNodeStrategy._extract_step_context_metadata` in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` |
| `LLMNodeStrategy.execute` — Stage 1 (Ingress unpacking, `SourceDocumentPacker`, `V2Step` & `PromptBlock` resolution, `run_pre_hooks`, `OutputProfile` & `target_locale` validation) | Imperative Stage 1 of `@override async def execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`, lines 241–470) | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` (`BlueprintStageResult`, `execute_blueprint_and_pre_hooks_stage`) | Invoked by `LLMNodeStrategy.execute` in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` |
| `LLMNodeStrategy.execute` — Stage 2 (`schema_map`, `ContextBuilder.build`, `shuffled_atoms` validation, `PromptFactory.build`, `<execution_parameters>`, `ChunkingService.chunk_payload`, `SourceDocumentContext` validation, `dynamic_schema` compilation) | Imperative Stage 2 of `@override async def execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`, lines 471–715) | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/prompt_and_schema_stage.py]` (`PromptAndSchemaStageResult`, `execute_prompt_and_schema_stage`) | Invoked by `LLMNodeStrategy.execute` in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` |
| `LLMNodeStrategy.execute` — Stage 3 (`LLMClient.from_tier`, `execute_mcp_retrieval`, `EngineExecutionRequest` retry loop, `engine.execute`, `run_post_hooks`, anomaly retry state persistence) | Imperative Stage 3 of `@override async def execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`, lines 716–1013) | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]` (`EngineRetryStageResult`, `execute_engine_retry_stage`) | Invoked by `LLMNodeStrategy.execute` in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` |
| `LLMNodeStrategy.execute` — Stage 4 (`profiler_metrics`, `StepExecutionMetadataDTO`, `_audit_signature`, `StepTraceMetadataDTO`, `TraceEvent` list assembly) | Imperative Stage 4 of `@override async def execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`, lines 1014–1091) | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/trace_event_stage.py]` (`build_llm_step_trace_events`) | Invoked by `LLMNodeStrategy.execute` in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` |
| `LLMNodeStrategy` | `class LLMNodeStrategy(NodeStrategy)` (`@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]`) | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` (`< 220` lines) | Re-exported in `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` and `@[backend_v2/services/orchestrator/strategies/__init__.py]` |

---

## 3. 1-Hop Caller Blast-Radius Inventory (Epoch 1 Phase 4 Cutover)

| Caller Category | File Path & AST Boundaries | Current Import / Reference | Target Rewired Import / Reference |
| :--- | :--- | :--- | :--- |
| Production Strategy Package Root | `@[backend_v2/services/orchestrator/strategies/__init__.py]` | `from .llm import LLMNodeStrategy` | `from .llm_strategy import LLMNodeStrategy as LLMNodeStrategy` |
| Production Strategy Registry | `@[backend_v2/services/orchestrator/strategies/registry.py#L42-L60]` | `from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy` | `from backend_v2.services.orchestrator.strategies.llm_strategy import LLMNodeStrategy` |
| Unit Test — AST Dispatch Guardrails | `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L412-L420]`, `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L437-L449]` | `Path("backend_v2/services/orchestrator/strategies/llm.py")` | Scan all `.py` files in `Path("backend_v2/services/orchestrator/strategies/llm_strategy")` |
| Unit Test — DAG Executor | `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L345-L421]` | `patch("backend_v2.services.orchestrator.strategies.llm.LLMNodeStrategy.execute", new_callable=AsyncMock)` | `patch("backend_v2.services.orchestrator.strategies.llm_strategy.LLMNodeStrategy.execute", new_callable=AsyncMock)` |
| Unit Test — Strategy Registry | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py#L44-L50]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py#L44-L50]` | `from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy` | `from backend_v2.services.orchestrator.strategies.llm_strategy import LLMNodeStrategy` |
| Unit Test — Shuffled Atoms Regression | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py#L139-L156]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py#L159-L251]` | `from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy` and `patch("backend_v2.services.orchestrator.strategies.llm....")` | `from backend_v2.services.orchestrator.strategies.llm_strategy import LLMNodeStrategy` and `patch("backend_v2.services.orchestrator.strategies.llm_strategy....")` |
| Unit Test — Cost Tracking | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L144-L276]` | `from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy` and `patch("backend_v2.services.orchestrator.strategies.llm....")` | `from backend_v2.services.orchestrator.strategies.llm_strategy import LLMNodeStrategy` and `patch("backend_v2.services.orchestrator.strategies.llm_strategy....")` |
| Unit Test — Output Profile Directives | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_strategy.py#L147-L303]` | `from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy` | `from backend_v2.services.orchestrator.strategies.llm_strategy import LLMNodeStrategy` |
| Monolithic Unit Test Suite (Split in Phase 4) | `[DELETE] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]` (3,597 lines, 42 tests) | `from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy` | Split into 5 modular test suites (`< 450` lines each) under `backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/` |
| AST Guardrail Script | `@[scripts/_ast_guardrails.py#L1892-L1992]`, `@[scripts/_ast_guardrails.py#L1994-L2212]` | `RESIDUAL_FUTURE_PHASE_QGR028_FILES` entry `"backend_v2/services/orchestrator/strategies/llm.py"` | Update `RESIDUAL_FUTURE_PHASE_QGR028_FILES` to stage module paths and lock `backend_v2.services.orchestrator.strategies.llm` in `QGR017` |
| Dict Eradication & Ruff Config | `@[scripts/audit_dict_eradication.py]`, `@[pyproject.toml]` | `"backend_v2/services/orchestrator/strategies/llm.py"` in `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` / `per-file-ignores` | Remove `"backend_v2/services/orchestrator/strategies/llm.py"` once all new sub-modules comply with `<= 120` char line length |
