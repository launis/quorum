# Phase 2: Concrete Engine Purity & Protocol Harmonization

**Overview:** Purify and harmonize `PromptEngine`, `SynthesisEngine`, and `TDAEngine` into pure compute engines implementing `ExecutionEngine(Protocol)` with PEP 698 `@override`, eliminate all engine-level semaphore wrapping and `running_event` signaling, update engine unit test suites with protocol `issubclass` and `isinstance` assertions, and rebase the concurrency fuzzer test suite (`test_concurrency_fuzzer.py`) onto the `LiteLLMProvider` dynamic semaphore pool SSOT (Stage A upper bound proof).

**Source:** @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md#L76-L108] Phase 2: Concrete Engine Purity & Protocol Harmonization

**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/prompt_engine.py#L19-L72]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L37-L296]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/tda_engine.py#L35-L234]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_concurrency_fuzzer.py]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L19-L72]` (`PromptEngine`) | `async with request.semaphore_cm:`, `request.running_event.set()`, and missing PEP 698 `@override`. | Direct invocation of `self.task_executor.execute_structured_task` at root function scope; explicit `@override` decorator. | Pruned redundant semaphore wrapping and telemetry event mutation inside leaf engine. | `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py -v`. Protocol subclass/isinstance assertions pass 100%. |
| `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L37-L296]` (`SynthesisEngine`) | Duck-typing bare class (`class SynthesisEngine:`), missing `@override`, and `async with request.semaphore_cm:`. | Formal protocol inheritance `class SynthesisEngine(ExecutionEngine):`, PEP 698 `@override`, direct execution without semaphore locks. | Pruned redundant top-level semaphore acquisition; formal protocol contract enforcement. | `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py -v`. Protocol subclass/isinstance assertions pass 100%. |
| `@[backend_v2/services/orchestrator/engines/tda_engine.py#L35-L234]` (`TDAEngine`) | Missing `@override`, `request.running_event.set()`, passing `semaphore=request.semaphore` to sub-executors (`TwoPassAtomizer`, `EnrichedDagExecutor`). | PEP 698 `@override` on `execute()`, direct compute pipeline delegating concurrency to `LiteLLMProvider`. | Eradicated multi-hop semaphore parameter drilling into child executors. | `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py -v`. Protocol inheritance and clean execution assertions pass. |
| `@[backend_v2/tests/unit/test_concurrency_fuzzer.py]` (Provider Concurrency Proof) | DAG-level `max_concurrent_llm_steps` peak assertions and a deadlock-timeout boundary test bound to a semaphore that ceases to exist. | Peak concurrency proven against the provider SSOT across three ISTQB partitions in Stage A (`peak_concurrent <= expected_limit`). Parametrized `semaphore_max_concurrency` over closed set [1, 2, 5, 10]. | Zero new test infrastructure; existing fixtures and the `mock_acompletion` peak counter are reused. | `uv run pytest backend_v2/tests/unit/test_concurrency_fuzzer.py -v`. |

## Pre-Implementation Cleanups

1. `[CLEANUP]` Ensure Phase 1 cleanups are committed and passing before beginning Phase 2.
2. `[CLEANUP]` Delete obsolete test `test_prompt_engine_respects_semaphore` in `test_prompt_engine.py` (L127-L140).
3. `[CLEANUP]` Remove `running_event` assertions from `test_prompt_engine_executes_successfully` in `test_prompt_engine.py`.
4. `[CLEANUP]` Remove explicit `asyncio.Semaphore(1)` instantiation from `base_request` fixture in `test_synthesis_engine.py`.
5. `[CLEANUP]` Remove `running_event` assertions (L134-136) from `test_tda_engine_execute_success` and clean `engine_request` fixture in `test_tda_engine.py`.
6. `[CLEANUP]` Remove explicit `semaphore` and `running_event` instantiations from `base_request` fixture in `test_tda_engine_causal_matrix.py` (L53-54).

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1. Verify `SynthesisEngine` ValueError instances and context fallback chains have been eliminated.</action>
    <action>Look forward: Verify that purifying `PromptEngine`, `SynthesisEngine`, and `TDAEngine` into stateless pure compute engines satisfies `ExecutionEngine` Protocol symmetry.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md]) and the Tracker document (@[docs/epic/EPIC_155_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_155/02_phase2_plan.md] @[docs/epic/EPIC_155_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>PromptEngine implements PEP 698 @override on execute() and removes running_event and semaphore_cm wrapping.</item>
    <item>SynthesisEngine formally inherits ExecutionEngine(Protocol) and implements PEP 698 @override on execute().</item>
    <item>TDAEngine implements PEP 698 @override on execute() and removes running_event and semaphore parameter drilling.</item>
    <item>Unit tests in test_prompt_engine.py, test_synthesis_engine.py, and test_tda_engine.py assert issubclass(..., ExecutionEngine) and isinstance(engine, ExecutionEngine) return True.</item>
    <item>test_prompt_engine_respects_semaphore is deleted from test_prompt_engine.py.</item>
    <item>Stage A of test_concurrency_fuzzer.py proves peak concurrency never exceeds provider limit across partitions [1, 2, 5, 10].</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT remove semaphore or running_event from EngineExecutionRequest DTO during Phase 2 (quarantined strictly for Phase 5).</anti_target>
    <anti_target>Do NOT modify TwoPassAtomizer or EnrichedDagExecutor signatures during Phase 2 (quarantined strictly for Phase 3).</anti_target>
    <anti_target>Do NOT modify NodeStrategy.execute signatures during Phase 2 (quarantined strictly for Phase 4).</anti_target>
    <anti_target>Do NOT modify DAGExecutor.run_step_wrapper during Phase 2 (quarantined strictly for Phase 5).</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/engines/prompt_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/synthesis_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/tda_engine.py]</backend>
  </touched_artifacts>

  <contract_freeze>
    <interface name="ExecutionEngine Protocol Implementations">
      <signature>async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:</signature>
      <constraint>PromptEngine, SynthesisEngine, and TDAEngine must all adhere to the exact ExecutionEngine Protocol signature with PEP 698 @override.</constraint>
    </interface>
  </contract_freeze>

  <test_contracts>
    <test name="test_prompt_engine_implements_protocol" category="positive">
      <input>PromptEngine class and instance</input>
      <expected>issubclass(PromptEngine, ExecutionEngine) is True and isinstance(engine, ExecutionEngine) is True</expected>
    </test>
    <test name="test_synthesis_engine_implements_protocol" category="positive">
      <input>SynthesisEngine class and instance</input>
      <expected>issubclass(SynthesisEngine, ExecutionEngine) is True and isinstance(engine, ExecutionEngine) is True</expected>
    </test>
    <test name="test_tda_engine_implements_protocol" category="positive">
      <input>TDAEngine class and instance</input>
      <expected>issubclass(TDAEngine, ExecutionEngine) is True and isinstance(engine, ExecutionEngine) is True</expected>
    </test>
    <test name="test_concurrency_fuzzer_peak_limit_stage_a" category="boundary">
      <input>parametrized semaphore_max_concurrency in [1, 2, 5, 10] with rpm_limit=1000</input>
      <expected>peak_concurrent &lt;= expected_limit (upper bound proof)</expected>
    </test>
    <test name="test_concurrency_fuzzer_low_rpm_limit_stage_a" category="boundary">
      <input>rpm_limit=20</input>
      <expected>peak_concurrent &lt;= semaphore_low_rpm_limit</expected>
    </test>
    <test name="test_concurrency_settings_reject_zero_limits" category="error_path">
      <input>Settings(semaphore_max_concurrency=0)</input>
      <expected>raises pydantic.ValidationError</expected>
    </test>
  </test_contracts>

  <step id="2.1" name="PURIFY_AND_HARMONIZE_PROMPT_ENGINE">
    <action>In `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L19-L72]`, import `override` from `typing` and decorate `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:` with `@override`.</action>
    <action>In `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L19-L72]`, remove `if request.running_event: request.running_event.set()` at L59-L60.</action>
    <action>In `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L19-L72]`, remove `async with request.semaphore_cm:` block at L62 and invoke `self.task_executor.execute_structured_task` directly at root function indentation.</action>
  </step>

  <step id="2.2" name="PURIFY_AND_HARMONIZE_SYNTHESIS_ENGINE">
    <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L37-L296]`, import `override` from `typing` and import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base`.</action>
    <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L37-L296]`, update class definition to `class SynthesisEngine(ExecutionEngine):`.</action>
    <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L37-L296]`, decorate `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:` with `@override`.</action>
    <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L37-L296]`, remove `async with request.semaphore_cm:` block at L225 and invoke `self._executor.execute_structured_task` directly.</action>
    <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L37-L296]`, ensure zero `running_event` references exist.</action>
  </step>

  <step id="2.3" name="PURIFY_AND_HARMONIZE_TDA_ENGINE">
    <action>In `@[backend_v2/services/orchestrator/engines/tda_engine.py#L35-L234]`, import `override` from `typing` and decorate `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:` with `@override`.</action>
    <action>In `@[backend_v2/services/orchestrator/engines/tda_engine.py#L35-L234]`, remove `if request.running_event: request.running_event.set()` at L65-L66.</action>
    <action>In `@[backend_v2/services/orchestrator/engines/tda_engine.py#L35-L234]`, remove `semaphore=request.semaphore` from `atomizer.execute_phase_0` call at L162.</action>
    <action>In `@[backend_v2/services/orchestrator/engines/tda_engine.py#L35-L234]`, remove `semaphore=request.semaphore` from `dag_executor.execute_graph` call at L197.</action>
  </step>

  <step id="2.4" name="UPDATE_ORCHESTRATOR_ENGINE_UNIT_TESTS">
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]`, remove all `semaphore` and `running_event` fixtures, mock injections, and assertions asserting `running_event.is_set()`, and DELETE `test_prompt_engine_respects_semaphore` (L127-L140) because the behavior it asserts (engine-level semaphore gating) is intentionally eradicated; provider-level gating is proven by Step 2.5.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]`, import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base` and add `test_prompt_engine_implements_protocol()` asserting `issubclass(PromptEngine, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, remove all `semaphore` and `running_event` fixtures and tests verifying `null_concurrency_guards` or event signaling.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base` and add `test_synthesis_engine_implements_protocol()` asserting `issubclass(SynthesisEngine, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]`, remove `running_event` assertions and `semaphore` fixtures (fixture L70-L71; assertions L134-L136).</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]`, import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base` and add `test_tda_engine_implements_protocol()` asserting `issubclass(TDAEngine, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`.</action>
    <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py]`, remove `semaphore` and `running_event` instantiation (L53-L54).</action>
  </step>

  <step id="2.5" name="REBASE_CONCURRENCY_FUZZER_ON_PROVIDER_SSOT">
    <action>Stage A (lands in coupled commit with Step 2.1): In `@[backend_v2/tests/unit/test_concurrency_fuzzer.py]`, rewrite `test_concurrency_fuzzer_peak_limit` (L160) to parametrize `semaphore_max_concurrency` over the closed set [1, 2, 5, 10] patched through `backend_v2.llm.provider.get_settings` with an RPM limit of 1000, asserting `peak_concurrent <= expected_limit` (upper bound proof). RPM partitions are parametrized via a fixture factory modulating `rpm_limit` in `SystemConfigModelRegistry` tier definitions. Construct `Settings(semaphore_max_concurrency=0, ...)` directly in `test_concurrency_settings_reject_zero_limits` to prove Fail-Fast validation without `model_copy(update=...)` bypass. In `test_concurrency_fuzzer_exceeding_physical_limit` (L276), assert `peak_concurrent <= 3` for `rpm_limit=30` and `peak_concurrent <= semaphore_low_rpm_limit` for `rpm_limit=20`.</action>
    <action>Stage B (lands in coupled commit with Step 5.3): Once the DAG executor macro-semaphore is removed, tighten the peak assertions in `test_concurrency_fuzzer_peak_limit` and `test_concurrency_fuzzer_exceeding_physical_limit` to exact equality: `assert peak_concurrent == min(expected_limit, 10)` across all partitions, mathematically proving both upper bound enforcement and actual throughput increase.</action>
  </step>

  <validation_gate>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/ --test --ast-strict`</action>
    <action>Run `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine_causal_matrix.py -v`</action>
    <action>Run `uv run pytest backend_v2/tests/unit/test_concurrency_fuzzer.py -v`</action>
    <action>Assert issubclass(PromptEngine, ExecutionEngine) is True</action>
    <action>Assert issubclass(SynthesisEngine, ExecutionEngine) is True</action>
    <action>Assert issubclass(TDAEngine, ExecutionEngine) is True</action>
  </validation_gate>
</execution_protocol>

```
