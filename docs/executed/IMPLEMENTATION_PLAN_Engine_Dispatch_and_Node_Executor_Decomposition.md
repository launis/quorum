<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
</required_context_rules>

# Implementation Plan: Engine Dispatch & NodeExecutor Decomposition

**Overview:** Refactor the execution engine architecture in `backend_v2/services/orchestrator/` to cleanly decouple NodeStrategy instantiation, cognitive engine resolution, and structured LLM prompt execution. Implement targeted prompt block fetching (`get_prompt_blocks_by_ids`) in `PromptBlockRepository` to eliminate table scans, inject fetched prompt blocks via `StrategyContext` (Dependency Injection) to completely eliminate duplicate DB queries, extract `PromptEngine` for non-matrix structured LLM steps, decompose `NodeExecutor` into clean Single Responsibility methods (`_resolve_execution_engine`, `_create_strategy`) with centralized dependency injection, eliminate copy-paste parameter duplication, migrate all unit test repository mocks from legacy dictionaries to strict Pydantic V2 domain model instances, and enforce strict Fail-Fast invariants across Quorum V2/V3.

**Target Files:**
- `[MODIFY]` @[backend_v2/database/interfaces.py#L677-L740]
- `[MODIFY]` @[backend_v2/database/repositories/components/prompt_block.py#L50-L115]
- `[NEW]` @[backend_v2/services/orchestrator/engines/prompt_engine.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/__init__.py#L1-L15]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/base.py#L50-L284]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/logic.py#L19-L177]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L56-L782]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L115-L375]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py#L25-L65]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L266]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L287-L347]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py#L1-L564]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py#L1-L100]
- `[MODIFY]` @[backend_v2/tests/unit/test_logic.py#L1-L177]

Source: Clean Stack 2026 Model, Polymorphic Rule Routing (@[ki_polymorphic_rule_routing.md]), and AI Testing Standards (@[ki_ai_testing_standards.md])

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT &amp; TECHNICAL DEBT CHECK">
    <action>Look backward: Verify baseline state in @[backend_v2/database/repositories/components/prompt_block.py#L50-L115], @[backend_v2/services/orchestrator/dag_executor.py#L115-L375], @[backend_v2/services/orchestrator/strategies/llm.py#L56-L782], @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L219], and @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L25-L220].</action>
    <action>Verify test baseline: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test` to confirm the exact failing test in `test_llm_cost_tracking.py` caused by stale patch target `@patch("...tda_engine.get_settings")`.</action>
    <constraint invariant="anti_hallucination_guard">Verify AST boundaries and line counts of all touched files before editing.</constraint>
    <constraint invariant="ki_god_code_prevention">Ensure PromptEngine is placed in its own dedicated module under `backend_v2/services/orchestrator/engines/prompt_engine.py` (line count target &lt; 150 lines). Ensure `NodeExecutor` methods in `dag_executor.py` are cleanly decomposed into isolated SRP helpers rather than growing the file.</constraint>
    <constraint invariant="touched_scope_tech_debt_tracking">The following tech debt items were identified in @[backend_v2/services/orchestrator/strategies/llm.py#L361-L644] during Tier 0 research and are mandated for pre-requisite cleanup in Step 1 per `scoped_boy_scout_rule`: (1) `getattr(step, "input_mappings", None)` at L505, L546 — violates `the_zero_compromise_pledge`; (2) `getattr(step, "mcp_tools", None)` and `hasattr(tool, "function")` at L553-L560 — violates `the_zero_compromise_pledge`; (3) `b.category_id == "matrix"` at L361, L393 — violates `strict_enum_routing_enforcement` (must use `PromptBlockCategory.MATRIX`); (4) silent `except Exception: pass` at L516-517 and L539-540 — violates `the_duct_tape_ban`; (5) `getattr(step, "expected_sdui_type", "grid")` at L573, L644 — violates `zero_service_layer_fallbacks`.</constraint>
  </step>

  <step id="1" name="PRE-REQUISITE TECHNICAL DEBT CLEANUP">
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L148]: Remove outdated mock `@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")` and align mocks with the actual modern architecture of `TDAEngine` and `LLMNodeStrategy`.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py#L361-L644]: Remediate all identified technical debt and anti-patterns per `scoped_boy_scout_rule`:
      1. Enum Routing Parity (L361, L393): Replace raw string comparison `b.category_id == "matrix"` with `b.category_id == PromptBlockCategory.MATRIX` and `any(b.category_id == PromptBlockCategory.MATRIX for b in criteria_blocks_models)`.
      2. Clean Execution Record Retrieval &amp; Error Handling (L508-L542): Replace silent `except Exception: pass` blocks with explicit `logger.warning` RFC 7807 structured logging on `exec_repo.get_execution()` and `SourceDocumentContext` serialization. Remove stray `pass` at L542.
      3. Explicit Dynamic Keys Resolution (L504-L506, L545-L550): Eliminate `getattr(step, "input_mappings", None)` duck typing. Resolve allowed dynamic keys directly from the `input_mappings` argument passed into `LLMNodeStrategy.execute()` combined with `context.expected_inputs`.
      4. Typed MCP Tools Parsing (L553-L562): Eliminate `getattr(step, "mcp_tools", None)` and `hasattr(tool, "function")`. Iterate directly over `step.allowed_mcp_tools` (`list[str]`) from the `Step` model and format prefixes deterministically.
      5. Remove Magic Defaults (L573, L644): Eliminate `getattr(step, "expected_sdui_type", "grid")`.
    </action>
    <action>Execute `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py` to mathematically verify baseline tests pass after cleanup.</action>
    <constraint invariant="scoped_boy_scout_rule">Clean technical debt exclusively in target files touched by this task before introducing domain additions.</constraint>
    <constraint invariant="the_duct_tape_ban">Zero silent exception swallowing or pass blocks allowed.</constraint>
    <constraint invariant="the_zero_compromise_pledge">Zero getattr/hasattr duck typing on domain models.</constraint>
  </step>

  <step id="2" name="TARGETED REPOSITORY BATCH QUERY &amp; PROMPT ENGINE IMPLEMENTATION">
    <action>In @[backend_v2/database/interfaces.py#L677-L740]: Add `async def get_prompt_blocks_by_ids(self, block_ids: list[str]) -> list[PromptBlock]: ...` to `IPromptBlockRepository` Protocol.</action>
    <action>In @[backend_v2/database/repositories/components/prompt_block.py#L50-L115]: Implement `get_prompt_blocks_by_ids(self, block_ids: list[str]) -> list[PromptBlock]`:
      1. Fast-path: if `not block_ids`: return `[]` immediately without DB round-trip.
      2. Query driver using `Filter("id", "in", block_ids)`: `data = await self.driver.query("prompt_blocks", filters=[Filter("id", "in", block_ids)])`.
      3. Parse into domain models via `PromptBlockAdapter.validate_python(b, strict=False)`.
      4. Raise `AppException(status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})` on malformed records with Fail-Fast logging.
    </action>
    <action>Create new file `backend_v2/services/orchestrator/engines/prompt_engine.py` implementing the `ExecutionEngine` protocol (`execute(request: EngineExecutionRequest) -> EngineExecutionResult`):
      1. Signal `running_event.set()` if `request.running_event` is provided.
      2. Enforce Fail-Fast validation on mandatory parameters:
         - If `request.compiled_schema is None`: raise `AppException(status_code=500, message="PromptEngine requires a valid 'compiled_schema'.", details={"error_code": "PROMPT_ENGINE_ERROR"})`.
         - If `request.hydrated_messages is None` or empty: raise `AppException(status_code=500, message="PromptEngine requires non-empty 'hydrated_messages'.", details={"error_code": "PROMPT_ENGINE_ERROR"})`.
      3. Instantiate `LLMTaskExecutor` with `validation_context={"execution_id": request.context.execution_id, "step_id": request.step.id, "strictness_level": request.context.strictness_level}`.
      4. Wrap execution inside `async with request.semaphore:` and call `await self._llm_executor.execute_structured_task(client=request.bound_client, messages=request.hydrated_messages, response_model=request.compiled_schema)`.
      5. Extract validated Pydantic model dump: `validated_output = validated_dto.model_dump(mode="json")`.
      6. Return `EngineExecutionResult(results=[], hydrated_references={}, synthesis_output=validated_output, trace_events=[], usage=usage)`. Token metadata injection (`_step_metadata.token_usage`) is NOT done here — it is handled centrally by `LLMNodeStrategy.execute()` at @[backend_v2/services/orchestrator/strategies/llm.py#L758-L763], matching `TDAEngine` and `SynthesisEngine` behavior.
      7. Re-raise `AppException` without double-wrapping; wrap unexpected exceptions in `AppException(status_code=500, details={"error_code": "PROMPT_ENGINE_ERROR"})` with RFC 7807 dual-logging.
    </action>
    <action>In @[backend_v2/services/orchestrator/engines/__init__.py#L1-L15]: Re-export `PromptEngine` in `__all__ = ["ExecutionEngine", "TDAEngine", "SynthesisEngine", "PromptEngine"]` per `explicit_reexport_mandate`.</action>
    <constraint invariant="ki_god_code_prevention">Keep `prompt_engine.py` strictly focused on SRP structured task execution (&lt; 140 lines).</constraint>
    <constraint invariant="universal_fail_fast">Zero fallbacks or default dicts. Missing schema or messages MUST crash immediately with AppException.</constraint>
    <constraint invariant="no_full_table_scans">Ban full-table scans for step-level execution. All block fetches MUST use targeted `get_prompt_blocks_by_ids`.</constraint>
  </step>

  <step id="3" name="DECOMPOSE NODE EXECUTOR, INJECT DEPENDENCIES &amp; TARGETED PROMPT BLOCKS">
    <action>In @[backend_v2/services/orchestrator/strategies/base.py#L50-L284]:
      1. Add `prompt_blocks: list[PromptBlock] = Field(default_factory=list)` to `StrategyContext` model, enabling single-fetch Dependency Injection from `NodeExecutor` to `LLMNodeStrategy`.
      2. Define `StrategyDependencies` container (`@dataclass(frozen=True)`) containing all 9 shared repository/compiler dependencies + optional `arq_pool`, adhering to `typed_dependency_container_mandate`.
      3. Update `NodeStrategy.__init__(self, deps: StrategyDependencies)` to accept `deps` and assign attributes.
    </action>
    <action>In @[backend_v2/services/orchestrator/strategies/logic.py#L19-L177] and @[backend_v2/services/orchestrator/strategies/llm.py#L56-L782]: Update constructors to accept `deps: StrategyDependencies` (and `engine: ExecutionEngine` on `LLMNodeStrategy`).</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L115-L375]:
      1. Update `NodeExecutor.__init__(self, deps: StrategyDependencies) -> None` to accept the single typed container `self.deps = deps`.
      2. Update `DAGExecutor.__init__` to instantiate `self.deps = StrategyDependencies(...)` and pass `self.node_executor = NodeExecutor(deps=self.deps)`.
      3. In `NodeExecutor.execute()`:
         - Aggregate all required prompt block IDs for the active step: `step_def.role_block_id`, `step_def.extraction_protocol_block_id`, `step_def.execution_persona_block_id`, and `step_def.criteria_block_ids`.
         - If workflow definition is available, also collect block IDs required across workflow steps for schema mapping: `all_required_block_ids = list(dict.fromkeys(collected_ids))`.
         - Single-point fetch: `loaded_prompt_blocks = await self.deps.prompt_block_repo.get_prompt_blocks_by_ids(all_required_block_ids)` (1 targeted DB call, 0 full-table scans).
         - Pass `loaded_prompt_blocks` to `_resolve_execution_engine(step_def, loaded_prompt_blocks)` to determine engine type in memory with ZERO extra database queries.
         - Inject `loaded_prompt_blocks` into `StrategyContext(..., prompt_blocks=loaded_prompt_blocks)`.
      4. Add helper method `def _resolve_execution_engine(self, step_def: Step, prompt_blocks: list[PromptBlock]) -> ExecutionEngine`:
         - Determine engine type deterministically based on step taxonomy and already-fetched prompt blocks:
           - If `step_def.model_strategy == "synthesis"` (or step contains synthesis prompt blocks): return `SynthesisEngine(LLMTaskExecutor(self.deps.prompt_compiler))`.
           - Filter criteria blocks from already-injected `prompt_blocks`: `criteria_blocks = [b for b in prompt_blocks if b.id in step_def.criteria_block_ids]`.
           - Check block categories using strict enum comparisons: `is_matrix_step = any(b.category_id == PromptBlockCategory.MATRIX or isinstance(b, MatrixPromptBlock) for b in criteria_blocks)`.
           - If `is_matrix_step`: return `TDAEngine(self.deps.prompt_compiler)`.
           - Else (non-matrix structured prompt step): return `PromptEngine(LLMTaskExecutor(self.deps.prompt_compiler))`.
      5. Add factory method `def _create_strategy(self, step_def: Step, engine: ExecutionEngine | None = None, arq_pool: Any | None = None) -> NodeStrategy`:
         - Resolve `deps = dataclasses.replace(self.deps, arq_pool=arq_pool) if arq_pool else self.deps`.
         - Map `step_def.type` via an explicit strategy factory registry/dispatch mapping:
           - When `step_def.type == "logic"`: return `LogicNodeStrategy(deps=deps)`.
           - When `step_def.type == "llm"`:
             - If `engine is None`: raise `AppException(status_code=500, message="LLMNodeStrategy requires a resolved ExecutionEngine.", details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})`.
             - Return `LLMNodeStrategy(deps=deps, engine=engine)`.
           - When `step_def.type` is unrecognized: raise `AppException(status_code=500, message=f"Unknown step type '{step_def.type}'", details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})`.
      6. Refactor `NodeExecutor.execute()` flow:
         - Resolve engine: `engine = self._resolve_execution_engine(step_def, loaded_prompt_blocks) if step_def.type == "llm" else None`.
         - Create strategy: `strategy_impl = self._create_strategy(step_def, engine=engine, arq_pool=arq_pool)`.
         - Execute `await strategy_impl.assert_quota(org_id=org_id)`.
         - Delegate directly to `await strategy_impl.execute(step=step, projector=projector, context=context, frozen_ctx=frozen_ctx, trace=trace, semaphore=semaphore, running_event=running_event, progress_callback=progress_callback)`.
    </action>
    <constraint invariant="strategy_pattern_mandate">Eliminate procedural if/else chains with duplicated repository arguments. Consolidate strategy resolution through a clean Strategy+Registry factory with explicit AppException handling for unknown types.</constraint>
    <constraint invariant="strict_enum_routing_enforcement">Enforce PromptBlockCategory.MATRIX enum routing across engine resolution; ban raw string comparisons.</constraint>
    <constraint invariant="typed_dependency_container_mandate">Encapsulate multi-dependency groupings into StrategyDependencies container.</constraint>
    <constraint invariant="targeted_prompt_block_fetching_and_di">MANDATORY SINGLE-FETCH DI: NodeExecutor fetches targeted prompt blocks via `get_prompt_blocks_by_ids()` exactly ONCE and injects them into `_resolve_execution_engine()` and `StrategyContext.prompt_blocks`. Zero redundant DB round-trips allowed.</constraint>
    <constraint invariant="zero_service_layer_fallbacks">Ban .get() on domain models; query typed PromptBlock domain models directly and access .id to ensure Fail-Fast key validation.</constraint>
    <constraint invariant="executor_taxonomy_decoupling">Enforce strict decoupling between macro workflow orchestration (`DAGExecutor` / `NodeExecutor` / `NodeStrategyFactory`) and downstream atom graph evaluation (`EnrichedDagExecutor`). `EnrichedDagExecutor` is instantiated solely by `TDAEngine(llm_executor, client)` and MUST NOT be coupled to `StrategyDependencies` or `NodeExecutor`.</constraint>
  </step>

  <step id="4" name="ALIGN LLM NODE STRATEGY PAYLOAD COMPILATION &amp; CONSUME INJECTED BLOCKS">
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py#L56-L782]:
      1. Eliminate duplicate DB fetch: Replace `all_prompt_blocks_raw = await self.prompt_block_repo.get_all_prompt_blocks()` with direct consumption of injected prompt blocks:
         `block_map = {b.id: b for b in context.prompt_blocks if b.id}`.
      2. Validate that all required step prompt blocks (`role_block_id`, `extraction_protocol_block_id`, `execution_persona_block_id`, `criteria_block_ids`) exist in `block_map`; raise Fail-Fast `ConfigurationError` / `AppException(VALIDATION_FAILED)` if any are missing.
      3. Ensure `global_schema` is unconditionally compiled for non-matrix steps even when `frozen_ctx` is None or schema caching is active, so `compiled_schema` is guaranteed non-None for `PromptEngine`. Attach the compiled JSON schema to `TraceEvent.metadata["generated_schema"] = global_schema.model_json_schema()` to avoid in-place shared dictionary mutation across concurrent tasks; `DAGExecutor` will merge it atomically under `_update_lock`.
      4. When preparing `EngineExecutionRequest`:
         - For `is_synthesis_step`: pass `compiled_schema=dynamic_schema`, `hydrated_messages=[static_msg]`, `system_prompt=""`.
         - For `is_matrix_step`: pass `compiled_schema=None`, `hydrated_messages=None`, `system_prompt=user_payload`, `shuffled_atoms=hydrated_shuffled_atoms`.
         - For non-matrix structured prompt step (`PromptEngine` target):
           - Compile static instructions from non-matrix prompt blocks via `self.compiler.compile_static_instructions(criteria_blocks, target_locale)`.
           - Assemble 4-layer cacheable envelope: `hydrated_messages=[{"role": "system", "content": static_instructions}, {"role": "user", "content": user_payload}]`.
           - Pass `compiled_schema=global_schema`, `hydrated_messages=hydrated_messages`, `system_prompt=user_payload`.
      5. When processing `engine_result`:
         - If `engine_result.synthesis_output is not None`: assign `final_dict = engine_result.synthesis_output`.
         - Else: assign `final_dict = {"results": [r.model_dump(mode="json") for r in engine_result.results], "hydrated_references": {k: v.model_dump(mode="json") for k, v in engine_result.hydrated_references.items()}}`.
    </action>
    <constraint invariant="static_first_caching_topology">Ensure static prompt instructions form the system prefix, with user payloads isolated at the tail in hydrated_messages.</constraint>
    <constraint invariant="no_naked_dicts_in_state">Ensure all serialized DTO items use explicit Pydantic model_dump(mode="json") rather than loose manual dictionaries.</constraint>
  </step>

  <!-- ⚡ SESSION HANDOVER CHECKPOINT: After completing Steps 0-4 and executing an atomic git commit, the executing agent MUST invoke `/tier5-session-handover` before proceeding to Step 5. Context window saturation from modifying 6 production files (interfaces.py, prompt_block.py, base.py, logic.py, llm.py, dag_executor.py) mandates a fresh context for test modifications. -->

  <step id="5" name="ESTABLISH TEST SUITES &amp; ISTQB NEGATIVE COVERAGE (TYPED MOCK ISOLATION)">
    <action>In @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py#L25-L65]:
      - Add unit test `test_get_prompt_blocks_by_ids_success`: verify query filter with `Filter("id", "in", ids)` and returned typed `PromptBlock` models.
      - Add unit test `test_get_prompt_blocks_by_ids_empty_list`: verify immediate return of `[]` without calling driver.
      - Add unit test `test_get_prompt_blocks_by_ids_validation_failure`: verify `AppException(VALIDATION_FAILED)` on corrupt block data.
    </action>
    <action>Create [NEW] @[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py] with comprehensive ISTQB-aligned test scenarios:
      - `test_prompt_engine_success_structured_task`: Positive partition verifying Pydantic schema validation, token usage aggregation, and `EngineExecutionResult` population.
      - `test_prompt_engine_fail_fast_missing_schema`: Negative partition verifying `AppException(PROMPT_ENGINE_ERROR)` when `compiled_schema=None`.
      - `test_prompt_engine_fail_fast_missing_messages`: Negative partition verifying `AppException(PROMPT_ENGINE_ERROR)` when `hydrated_messages=None`.
      - `test_prompt_engine_fail_fast_empty_messages`: Negative partition verifying `AppException(PROMPT_ENGINE_ERROR)` when `hydrated_messages=[]`.
      - `test_prompt_engine_reraises_app_exception`: Negative partition verifying external LLM `AppException` is propagated without double-wrapping.
      - `test_prompt_engine_concurrency_semaphore_and_running_event`: Concurrency partition verifying `semaphore` acquisition and `running_event.set()` signal.
    </action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L287-L347]:
      - Update `NodeExecutor` fixtures to pass `StrategyDependencies`.
      - Migrate repository mock return values from raw dicts to strict Pydantic models: configure `mock_repo.get_step_by_id.return_value` to return `Step.model_validate(...)` or `Step(...)`.
      - Explicitly configure `prompt_block_repo.get_prompt_blocks_by_ids = AsyncMock(return_value=[...])` returning typed `PromptBlock` models (`SystemRulePromptBlock`, `MatrixPromptBlock`).
      - Add `test_node_executor_injects_tda_engine_for_matrix_step`: Verify `TDAEngine` is selected when criteria blocks contain `category_id == PromptBlockCategory.MATRIX`.
      - Add `test_node_executor_injects_prompt_engine_for_non_matrix_step`: Verify `PromptEngine` is selected when criteria blocks contain only non-matrix blocks.
      - Add `test_node_executor_single_fetch_prompt_blocks_di`: Verify `prompt_block_repo.get_prompt_blocks_by_ids` is called exactly ONCE per step execution.
      - Update `test_node_executor_injects_synthesis_engine` to verify `SynthesisEngine` resolution with typed `Step` and `PromptBlock` fixtures.
    </action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py#L1-L564]:
      - Update `llm_strategy` fixture to pass `StrategyDependencies`.
      - Remediate Testing Drift across all mock setups: migrate `mock_repo.get_output_profile_by_id`, `mock_repo.get_workflow`, `mock_repo.get_step_by_id`, and `mock_repo.get_prompt_blocks_by_ids` from dictionary return values to typed Pydantic models (`OutputProfile`, `Workflow`, `Step`, `PromptBlock`).
      - Configure `StrategyContext(..., prompt_blocks=[...])` in strategy tests to verify direct consumption of injected prompt blocks without repository calls.
      - Add unit tests verifying `LLMNodeStrategy` passes `compiled_schema` and `hydrated_messages` when executing non-matrix steps with `PromptEngine`.
    </action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py#L1-L100] and @[backend_v2/tests/unit/test_logic.py#L1-L177]:
      - Update `logic_strategy` fixtures to pass `StrategyDependencies`.
      - Migrate `mock_repo.get_step_by_id.return_value` from raw dict `step_def` to typed `Step.model_validate(step_def)`.
    </action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L266]:
      - Update `llm_strategy` instantiations to pass `StrategyDependencies` and `StrategyContext(..., prompt_blocks=[...])`.
      - Migrate `mock_repo.get_workflow.return_value` to typed `Workflow(...)` instance.
    </action>
    <constraint invariant="anti_happy_path_mandate">Enforce minimum of 2 negative equivalence partitions per new engine/strategy path.</constraint>
    <constraint invariant="typed_mock_isolation_mandate">All mock return values for repositories and engines across test suites MUST be strictly typed Pydantic V2 model instances (Step, Workflow, OutputProfile, PromptBlock, EngineExecutionResult). Raw dictionary mocks are strictly prohibited to prevent testing drift, silent MagicMock false-positives, and uncaught schema regressions.</constraint>
  </step>

  <step id="6" name="QUALITY GATES &amp; BOUNDARY VERIFICATION">
    <action>Run AST Guardrails: `uv run pytest backend_v2/tests/unit/guardrails/`</action>
    <action>Run Database Unit Tests: `uv run pytest backend_v2/tests/unit/database/repositories/components/test_prompt_block.py`</action>
    <action>Run Unit Test Suite: `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py backend_v2/tests/unit/services/orchestrator/test_dag_executor.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py backend_v2/tests/unit/test_logic.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py`</action>
    <action>Run Orchestrator Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`</action>
    <action>Verify line counts and God Code limits: confirm all modified/new files remain within architectural boundaries.</action>
    <action>Execute atomic Git commit in English.</action>
  </step>
</execution_protocol>
```

## Definition of Done (DoD) Checklist

- [ ] `test_llm_cost_tracking.py` stale mock patch removed and test passes.
- [ ] Technical debt in `llm.py` eliminated in Step 1: silent `except Exception: pass` removed with structured logging, `getattr`/`hasattr` duck-typing removed, and `PromptBlockCategory.MATRIX` enum comparison enforced.
- [ ] `IPromptBlockRepository` protocol and `PromptBlockRepositoryImpl` extended with `get_prompt_blocks_by_ids(block_ids: list[str]) -> list[PromptBlock]`.
- [ ] Full-table scan `get_all_prompt_blocks()` completely eliminated from `NodeExecutor` and `LLMNodeStrategy`.
- [ ] Single-point targeted fetch implemented in `NodeExecutor.execute()` with prompt blocks injected into `StrategyContext(..., prompt_blocks=...)`.
- [ ] `PromptEngine` created in `backend_v2/services/orchestrator/engines/prompt_engine.py` implementing `ExecutionEngine` protocol with strict Fail-Fast validation.
- [ ] `PromptEngine` exported in `backend_v2/services/orchestrator/engines/__init__.py`.
- [ ] `StrategyDependencies` container defined in `backend_v2/services/orchestrator/strategies/base.py` and adopted across `NodeStrategy`, `LogicNodeStrategy`, and `LLMNodeStrategy`.
- [ ] `NodeExecutor` in `dag_executor.py` decomposed into `_resolve_execution_engine()` and `_create_strategy()` with single `LLMNodeStrategy` call-site using `StrategyDependencies`.
- [ ] `NodeExecutor.execute()` routes matrix criteria to `TDAEngine`, synthesis to `SynthesisEngine`, and prompt tasks to `PromptEngine` using typed `PromptBlock` models (`b.id`) in memory without redundant database queries.
- [ ] `LLMNodeStrategy` in `llm.py` consumes injected `context.prompt_blocks`, compiles `global_schema` and `hydrated_messages` for `PromptEngine` targets, and handles `engine_result.synthesis_output` generically with strict `model_dump(mode="json")`.
- [ ] Unit tests for `get_prompt_blocks_by_ids` added to `test_prompt_block.py`.
- [ ] Comprehensive unit test suite `test_prompt_engine.py` established with ISTQB negative partitions.
- [ ] `test_dag_executor.py`, `test_llm.py`, `test_logic.py`, and `test_llm_cost_tracking.py` updated with `StrategyDependencies`, `StrategyContext.prompt_blocks`, and engine selection tests.
- [ ] All `AsyncMock` and repository mock return values across test suites migrated from legacy raw dictionaries to strict Pydantic V2 model instances (`Step`, `PromptBlock`, `OutputProfile`, `Workflow`).
- [ ] Full backend audit loop passes: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`.
- [ ] All file line counts verified against `ki_god_code_prevention.md` limits.

## Verification Plan

### Automated Tests
1. Run AST Guardrail tests:
   `uv run pytest backend_v2/tests/unit/guardrails/`
2. Run Repository Unit Tests:
   `uv run pytest backend_v2/tests/unit/database/repositories/components/test_prompt_block.py`
3. Run Specific Strategy and Engine Tests:
   `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py backend_v2/tests/unit/services/orchestrator/test_dag_executor.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py backend_v2/tests/unit/test_logic.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py`
4. Run Orchestrator Unit Tests & Audit Loop:
   `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`

### Manual Verification
1. Verify live DAG execution of mixed workflows containing both `step_input_processing` (non-matrix `PromptEngine` step) and `Analyst` / `Archivist` (matrix `TDAEngine` steps) via integration runner:
   `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
