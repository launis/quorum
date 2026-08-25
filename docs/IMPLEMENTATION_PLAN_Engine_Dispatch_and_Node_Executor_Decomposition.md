<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
</required_context_rules>

# Implementation Plan: Engine Dispatch & NodeExecutor Decomposition

**Overview:** Refactor the execution engine architecture in `backend_v2/services/orchestrator/` to cleanly decouple NodeStrategy instantiation, cognitive engine resolution, and structured LLM prompt execution. Extract `PromptEngine` for non-matrix structured LLM steps, decompose `NodeExecutor` into clean Single Responsibility methods (`_resolve_execution_engine`, `_create_strategy`) with centralized dependency injection, eliminate copy-paste parameter duplication, and enforce strict Fail-Fast invariants across Quorum V2/V3.

**Target Files:**
- `[NEW]` @[backend_v2/services/orchestrator/engines/prompt_engine.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/__init__.py#L1-L15]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/base.py#L57-L284]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/logic.py#L19-L177]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L56-L782]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L115-L375]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L266]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L287-L347]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py#L54-L564]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py#L1-L100]
- `[MODIFY]` @[backend_v2/tests/unit/test_logic.py#L1-L177]

Source: Clean Stack 2026 Model & Polymorphic Rule Routing (@[ki_polymorphic_rule_routing.md])

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT &amp; TECHNICAL DEBT CHECK">
    <action>Look backward: Verify baseline state in @[backend_v2/services/orchestrator/dag_executor.py#L115-L375], @[backend_v2/services/orchestrator/strategies/llm.py#L56-L782], @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L219], and @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L25-L220].</action>
    <action>Verify test baseline: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test` to confirm the exact failing test in `test_llm_cost_tracking.py` caused by stale patch target `@patch("...tda_engine.get_settings")`.</action>
    <constraint invariant="anti_hallucination_guard">Verify AST boundaries and line counts of all touched files before editing.</constraint>
    <constraint invariant="ki_god_code_prevention">Ensure PromptEngine is placed in its own dedicated module under `backend_v2/services/orchestrator/engines/prompt_engine.py` (line count target &lt; 150 lines). Ensure `NodeExecutor` methods in `dag_executor.py` are cleanly decomposed into isolated SRP helpers rather than growing the file.</constraint>
    <constraint invariant="touched_scope_tech_debt_tracking">The following tech debt items were identified in @[backend_v2/services/orchestrator/strategies/llm.py#L504-L560] during Tier 0 research and are flagged for a dedicated `/tier2-hardening-backend` pass (NOT blocking this plan): (1) `getattr(step, "input_mappings", None)` at L504, L546 — violates `the_zero_compromise_pledge`; (2) `getattr(step, "mcp_tools", None)` at L553 — same; (3) `hasattr(tool, "function")` at L560 — explicitly banned; (4) `b.category_id == "matrix"` at L361, L393 — violates `strict_enum_routing_enforcement` (must use `PromptBlockCategory.MATRIX`); (5) `except Exception: pass` at L515-517 — violates `the_duct_tape_ban`.</constraint>
  </step>

  <step id="1" name="PRE-REQUISITE TECHNICAL DEBT CLEANUP">
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L148]: Remove outdated mock `@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")` and align mocks with the actual modern architecture of `TDAEngine` and `LLMNodeStrategy`.</action>
    <action>Execute `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py` to mathematically verify the test passes.</action>
    <constraint invariant="scoped_boy_scout_rule">Clean technical debt exclusively in target files touched by this task before introducing domain additions.</constraint>
  </step>

  <step id="2" name="CREATE PROMPT ENGINE IMPLEMENTATION">
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
  </step>

  <step id="3" name="DECOMPOSE NODE EXECUTOR &amp; RESOLVE STRATEGY IN DAG EXECUTOR">
    <action>In @[backend_v2/services/orchestrator/strategies/base.py#L57-L284]: Define `StrategyDependencies` container (`@dataclass(frozen=True)`) containing all 9 shared repository/compiler dependencies + optional `arq_pool`, adhering to `typed_dependency_container_mandate`. Update `NodeStrategy.__init__(self, deps: StrategyDependencies)` to accept `deps` and assign attributes.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/logic.py#L19-L177] and @[backend_v2/services/orchestrator/strategies/llm.py#L56-L782]: Update constructors to accept `deps: StrategyDependencies` (and `engine: ExecutionEngine` on `LLMNodeStrategy`).</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L115-L375]:
      1. Update `NodeExecutor.__init__(self, deps: StrategyDependencies) -> None` to accept the single typed container `self.deps = deps`.
      2. Update `DAGExecutor.__init__` to instantiate `self.deps = StrategyDependencies(...)` and pass `self.node_executor = NodeExecutor(deps=self.deps)`.
      3. Add helper method `async def _resolve_execution_engine(self, step_def: Step) -> ExecutionEngine`:
         - If `step_def.model_strategy == "synthesis"`: return `SynthesisEngine(LLMTaskExecutor(self.deps.prompt_compiler))`.
         - Otherwise, fetch ALL prompt blocks via `all_blocks_raw = await self.deps.prompt_block_repo.get_all_prompt_blocks()`, filter to the step's criteria: `criteria_raw = [b for b in all_blocks_raw if b.get("id") in step_def.criteria_block_ids]`.
           - Validate each using `PromptBlockAdapter.validate_python(raw_block, strict=False)`.
           - Check if any validated block is an instance of `MatrixPromptBlock` or has `category_id == PromptBlockCategory.MATRIX`.
           - If `is_matrix_step`: return `TDAEngine(self.deps.prompt_compiler)`.
           - Else (non-matrix structured step): return `PromptEngine(LLMTaskExecutor(self.deps.prompt_compiler))`.
      4. Add factory method `async def _create_strategy(self, step_def: Step, arq_pool: Any | None = None) -> NodeStrategy`:
         - Resolve `deps = dataclasses.replace(self.deps, arq_pool=arq_pool) if arq_pool else self.deps`.
         - If `step_def.type == "logic"`: return `LogicNodeStrategy(deps=deps)`.
         - Else: resolve `engine = await self._resolve_execution_engine(step_def)` and return `LLMNodeStrategy(deps=deps, engine=engine)`.
      5. Refactor `NodeExecutor.execute()` to call `strategy_impl = await self._create_strategy(step_def, arq_pool=arq_pool)`, execute `await strategy_impl.assert_quota(org_id=org_id)`, and delegate directly to `await strategy_impl.execute(...)`.
    </action>
    <constraint invariant="strategy_pattern_mandate">Eliminate long match/case statements with duplicated repository arguments. Consolidate LLMNodeStrategy instantiation to a single call-site.</constraint>
    <constraint invariant="typed_dependency_container_mandate">Encapsulate multi-dependency groupings into StrategyDependencies container.</constraint>
    <constraint invariant="accepted_trade_off_double_fetch">ACCEPTED TRADE-OFF: `_resolve_execution_engine()` fetches criteria blocks (small targeted subset) to determine engine type. `LLMNodeStrategy.execute()` subsequently fetches ALL prompt blocks for workflow-level schema mapping. This bounded redundancy is accepted for architectural decoupling clarity.</constraint>
  </step>

  <step id="4" name="ALIGN LLM NODE STRATEGY PAYLOAD COMPILATION">
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py#L56-L782]:
      1. Ensure `global_schema` is unconditionally compiled for non-matrix steps even when `frozen_ctx` is None or schema caching is active, so `compiled_schema` is guaranteed non-None for `PromptEngine`. If `frozen_ctx` is present, populate `frozen_ctx.generated_schemas[step.id] = global_schema.model_json_schema()`.
      2. When preparing `EngineExecutionRequest`:
         - For `is_synthesis_step`: pass `compiled_schema=dynamic_schema`, `hydrated_messages=[static_msg]`, `system_prompt=""`.
         - For `is_matrix_step`: pass `compiled_schema=None`, `hydrated_messages=None`, `system_prompt=user_payload`, `shuffled_atoms=hydrated_shuffled_atoms`.
         - For non-matrix structured prompt step (`PromptEngine` target):
           - Compile static instructions from non-matrix prompt blocks via `self.compiler.compile_static_instructions(criteria_blocks, target_locale)`.
           - Assemble 4-layer cacheable envelope: `hydrated_messages=[{"role": "system", "content": static_instructions}, {"role": "user", "content": user_payload}]`.
           - Pass `compiled_schema=global_schema`, `hydrated_messages=hydrated_messages`, `system_prompt=user_payload`.
      3. When processing `engine_result`:
         - If `engine_result.synthesis_output is not None`: assign `final_dict = engine_result.synthesis_output`.
         - Else: assign `final_dict = {"results": [r.model_dump() for r in engine_result.results], "hydrated_references": {k: v.model_dump() for k, v in engine_result.hydrated_references.items()}}`.
    </action>
    <constraint invariant="static_first_caching_topology">Ensure static prompt instructions form the system prefix, with user payloads isolated at the tail in hydrated_messages.</constraint>
  </step>

  <!-- ⚡ SESSION HANDOVER CHECKPOINT: After completing Steps 0-4 and executing an atomic git commit, the executing agent MUST invoke `/tier5-session-handover` before proceeding to Step 5. Context window saturation from modifying 4 production files (base.py, logic.py, llm.py, dag_executor.py) mandates a fresh context for test modifications. -->

  <step id="5" name="ESTABLISH TEST SUITES &amp; ISTQB NEGATIVE COVERAGE">
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
      - Add `test_node_executor_injects_tda_engine_for_matrix_step`: Verify `TDAEngine` is selected when criteria blocks contain `category_id == "matrix"`.
      - Add `test_node_executor_injects_prompt_engine_for_non_matrix_step`: Verify `PromptEngine` is selected when criteria blocks contain only non-matrix blocks.
      - Update `test_node_executor_injects_synthesis_engine` to verify `SynthesisEngine` resolution.
    </action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py#L54-L564]:
      - Update `llm_strategy` fixture to pass `StrategyDependencies`.
      - Add unit tests verifying `LLMNodeStrategy` passes `compiled_schema` and `hydrated_messages` when executing non-matrix steps with `PromptEngine`.
    </action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py#L1-L100] and @[backend_v2/tests/unit/test_logic.py#L1-L177]:
      - Update `logic_strategy` fixtures to pass `StrategyDependencies`.
    </action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L58-L266]:
      - Update `llm_strategy` instantiations to pass `StrategyDependencies`.
    </action>
    <constraint invariant="anti_happy_path_mandate">Enforce minimum of 2 negative equivalence partitions per new engine/strategy path.</constraint>
  </step>

  <step id="6" name="QUALITY GATES &amp; BOUNDARY VERIFICATION">
    <action>Run AST Guardrails: `uv run pytest backend_v2/tests/unit/guardrails/`</action>
    <action>Run Unit Test Suite: `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py backend_v2/tests/unit/services/orchestrator/test_dag_executor.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py backend_v2/tests/unit/test_logic.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py`</action>
    <action>Run Orchestrator Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`</action>
    <action>Verify line counts and God Code limits: confirm all modified/new files remain within architectural boundaries.</action>
    <action>Execute atomic Git commit in English.</action>
  </step>
</execution_protocol>
```

## Definition of Done (DoD) Checklist

- [ ] `test_llm_cost_tracking.py` stale mock patch removed and test passes.
- [ ] `PromptEngine` created in `backend_v2/services/orchestrator/engines/prompt_engine.py` implementing `ExecutionEngine` protocol with strict Fail-Fast validation.
- [ ] `PromptEngine` exported in `backend_v2/services/orchestrator/engines/__init__.py`.
- [ ] `StrategyDependencies` container defined in `backend_v2/services/orchestrator/strategies/base.py` and adopted across `NodeStrategy`, `LogicNodeStrategy`, and `LLMNodeStrategy`.
- [ ] `NodeExecutor` in `dag_executor.py` decomposed into `_resolve_execution_engine()` and `_create_strategy()` with single `LLMNodeStrategy` call-site using `StrategyDependencies`.
- [ ] `NodeExecutor.execute()` routes matrix criteria to `TDAEngine`, synthesis to `SynthesisEngine`, and prompt tasks to `PromptEngine`.
- [ ] `LLMNodeStrategy` in `llm.py` compiles `global_schema` and `hydrated_messages` for `PromptEngine` targets and handles `engine_result.synthesis_output` generically.
- [ ] Comprehensive unit test suite `test_prompt_engine.py` established with ISTQB negative partitions.
- [ ] `test_dag_executor.py`, `test_llm.py`, `test_logic.py`, and `test_llm_cost_tracking.py` updated with `StrategyDependencies` and engine selection tests.
- [ ] Full backend audit loop passes: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`.
- [ ] All file line counts verified against `ki_god_code_prevention.md` limits.

## Verification Plan

### Automated Tests
1. Run AST Guardrail tests:
   `uv run pytest backend_v2/tests/unit/guardrails/`
2. Run Specific Strategy and Engine Tests:
   `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py backend_v2/tests/unit/services/orchestrator/test_dag_executor.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py backend_v2/tests/unit/test_logic.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py`
3. Run Orchestrator Unit Tests & Audit Loop:
   `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`

### Manual Verification
1. Verify live DAG execution of mixed workflows containing both `step_input_processing` (non-matrix `PromptEngine` step) and `Analyst` / `Archivist` (matrix `TDAEngine` steps) via integration runner:
   `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
