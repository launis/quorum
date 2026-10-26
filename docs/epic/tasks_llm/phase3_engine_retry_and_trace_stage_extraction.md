<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 3: Engine Retry Loop, MCP Tool Retrieval & TraceEvent Stage Extraction (`phase3_engine_retry_and_trace_stage_extraction.md`)

## 1. Objective
Execute Phase 3 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]`:
1. Extract Stage 3 of `LLMNodeStrategy.execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`: `LLMClient.from_tier` binding, `execute_mcp_retrieval` tool loop invocation, and the bounded `while retry_count <= MAX_RETRIES:` loop constructing `EngineExecutionRequest`, awaiting `engine.execute`, normalizing `engine_result` into `final_dict`, running `run_post_hooks`, and persisting anomaly retry state updates) into `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]` (`< 350` lines) returning an immutable `@dataclass(frozen=True) class EngineRetryStageResult`.
2. Extract Stage 4 of `LLMNodeStrategy.execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`: `profiler_metrics` & `StepExecutionMetadataDTO` merging, `_audit_signature` stamping, `StepTraceMetadataDTO` & `TraceEventMetadataDTO` hydration, and final `TraceEvent` list assembly) into `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/trace_event_stage.py]` (`< 150` lines).
3. Update `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]` to delegate Stage 3 and Stage 4 of `execute` to `engine_retry_stage.py` and `trace_event_stage.py` with explicit redundant re-exports, and create unit tests in `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]` and `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_trace_event_stage.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]` | `EngineRetryStageResult` and `execute_engine_retry_stage` encapsulating `LLMClient.from_tier`, `execute_mcp_retrieval`, `EngineExecutionRequest` construction, `engine.execute`, `run_post_hooks`, and anomaly retry loop (`< 350` lines) |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/trace_event_stage.py]` | `build_llm_step_trace_events` encapsulating telemetry metric merging, `StepTraceMetadataDTO` construction, and `TraceEvent` emission (`< 150` lines) |
| `[MODIFY]` | `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]` | Delegate Stage 3 and Stage 4 of `execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`) to `execute_engine_retry_stage` and `build_llm_step_trace_events` with explicit redundant re-exports |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py]` | Register `backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py` in `RESIDUAL_FUTURE_PHASE_QGR028_FILES` during Epoch 1 pure structural lift-and-shift |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]` | Unit tests for `execute_engine_retry_stage` covering MCP retrieval, synthesis/text/matrix engine dispatch, post-hooks, and anomaly retry loop |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_trace_event_stage.py]` | Unit tests for `build_llm_step_trace_events` covering `StepTraceMetadataDTO`, `profiler_metrics`, `_audit_signature`, and `usage` propagation |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create Engine Retry Stage and TraceEvent Stage Sub-Modules">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py during Phase 3 while backend_v2/services/orchestrator/strategies/llm.py exists on disk.</constraint>
    <constraint invariant="topological_leaf_first_extraction_mandate">Neither engine_retry_stage.py nor trace_event_stage.py may import from backend_v2.services.orchestrator.strategies.llm or exceed 350 lines.</constraint>
    <action>
      1. Add `"backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py"` to `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]` for the verbatim Epoch 1 lift-and-shift of anomaly retry `ExecutionRecord` updates.
      2. Create `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]` (`< 350` lines, all lines `<= 120` chars) with `__all__ = ["EngineRetryStageResult", "execute_engine_retry_stage"]`:
         - Define `@dataclass(frozen=True) class EngineRetryStageResult` encapsulating: `hook_state: HookState`, `final_dict: dict[str, NodeStatePayload]`, `post_events: list[TraceEvent]`, `engine_result: EngineExecutionResult | None`, and `mcp_audit_traces: list[MCPAuditTrace]`.
         - Implement `async def execute_engine_retry_stage(...) -> EngineRetryStageResult` encapsulating Stage 3 of `LLMNodeStrategy.execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`), accepting optional `request_cls`, `mcp_retrieval_fn`, `settings_getter`, and `step_logger` parameters defaulted to `EngineExecutionRequest`, `execute_mcp_retrieval`, `get_settings`, and module `logger` so facade-level test patches in `test_llm.py` intercept calls transparently.
      3. Create `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/trace_event_stage.py]` (`< 150` lines, all lines `<= 120` chars) with `__all__ = ["build_llm_step_trace_events"]`:
         - Implement `def build_llm_step_trace_events(...) -> list[TraceEvent]` encapsulating Stage 4 of `LLMNodeStrategy.execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`).
    </action>
  </step>

  <step id="2" name="Delegate Engine Retry and TraceEvent Stages in LLMNodeStrategy and Add Unit Tests">
    <constraint invariant="explicit_reexport_mandate">Use explicit redundant import aliases (from module import Symbol as Symbol) in llm.py.</constraint>
    <action>
      1. Update `@[backend_v2/services/orchestrator/strategies/llm.py#L85-L1091]` to import `EngineRetryStageResult` and `execute_engine_retry_stage` from `backend_v2.services.orchestrator.strategies.llm_strategy.engine_retry_stage` and `build_llm_step_trace_events` from `backend_v2.services.orchestrator.strategies.llm_strategy.trace_event_stage` using explicit redundant aliases.
      2. Replace Stage 3 and Stage 4 inside `LLMNodeStrategy.execute` (`@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1091]`) with calls to `await execute_engine_retry_stage(...)` and `build_llm_step_trace_events(...)`, shrinking `llm.py` to a thin facade (`< 220` lines).
      3. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]` and `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_trace_event_stage.py]`.
    </action>
  </step>

  <step id="3" name="Run Phase 3 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on both new sub-modules and llm.py.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_strategy/trace_event_stage.py --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test --ast-strict` to verify all 45 baseline tests pass with `>= 90%` coverage.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_execute_anomaly_retry_flow">
      Verifies that execute_engine_retry_stage retries engine execution when post-hooks request llm_anomaly_retry_requested and updates step_states on ExecutionRecord.
    </contract>
    <contract type="positive" name="test_llm_strategy_propagates_engine_usage_to_trace_event">
      Verifies that build_llm_step_trace_events propagates engine_result.usage and profiler_metrics into the emitted TraceEvent.
    </contract>
    <contract type="negative" name="test_execute_fails_fast_when_no_engine_configured">
      Verifies that execute_engine_retry_stage raises ConfigurationError when LLMNodeStrategy is invoked with engine=None.
    </contract>
  </test_contracts>
</execution_protocol>
```
