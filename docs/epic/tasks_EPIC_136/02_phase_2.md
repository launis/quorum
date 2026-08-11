# Implementation Plan: Phase 2: Concurrency Fuzzer & Context Boundary Tests

<required_context_rules>
  @[c:\src\quorum\.agents\rules\00-antigravity-core.md]
  @[c:\src\quorum\.agents\rules\01-python-backend.md]
  @[c:\src\quorum\.agents\rules\05_llm_architecture.md]
  @[C:\Users\risto\.gemini\antigravity-ide\knowledge\ai_testing_standards\artifacts\ki_ai_testing_standards.md]
  @[C:\Users\risto\.gemini\antigravity-ide\knowledge\agent_context_quarantine\artifacts\ki_agent_context_quarantine.md]
  @[C:\Users\risto\.gemini\antigravity-ide\knowledge\neuro_symbolic_agentic_workflow\artifacts\ki_neuro_symbolic_agentic_workflow.md]
</required_context_rules>

<execution_protocol>
<step id="2" name="Phase 2: Concurrency Fuzzer & Context Boundary Tests">
    <action>Start the new session by executing `/tier5-resume` using the payload provided at the end of Phase 1.</action>
    <action>Create `backend_v2/tests/unit/test_concurrency_fuzzer.py` to prove Two-Tier Semaphore Architecture. Monkeypatch `max_concurrent_llm_steps` to 2. Explicitly instantiate a fresh instance of `DAGExecutor` (from `backend_v2/services/orchestrator/dag_executor.py`) inside the test function after monkeypatching. Clear caches in pytest setup/teardown (`_semaphores`, `_router_cache`, `_httpx_clients`).</action>
    <action>Patch `provider.router.acompletion` with a mock that implements an up/down atomic counter using `asyncio.Event()`. Fire 10 concurrent tasks via `asyncio.TaskGroup`. Assert `peak_concurrent <= max_concurrent_llm_steps`.</action>
    <action>Implement fuzzer negative tests: 1. Boundary — Zero Concurrency (raises TimeoutError). 2. Boundary — Exceeding Physical Limit (tasks run without queuing delay).</action>
    <action>Create `backend_v2/tests/unit/test_llm_context_bounds.py` to prove `ContextWindowExceededError` maps to `AGENT_EXECUTION_CRITICAL` with Fail-Fast. Patch `provider.router.acompletion` to raise `litellm.ContextWindowExceededError` with strict args to prevent logger crash. Assert it catches mapped error and mock was called exactly once.</action>
    <action>Implement context bounds negative tests: 1. Non-Context 400 Error (maps to AGENT_RESPONSE_MALFORMED). 2. Transient 503 Error Path (maps to custom ServiceUnavailableError, asserts mock call_count > 1 to prove Tenacity resilience loop triggered).</action>
    <action>Execute local verification: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_concurrency_fuzzer.py --test` and `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_llm_context_bounds.py --test`.</action>
    <action>Execute global completion gates: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.</action>
</step>
<validation_gate>
    <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_concurrency_fuzzer.py --test`</action>
    <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_llm_context_bounds.py --test`</action>
    <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`</action>
</validation_gate>
</execution_protocol>

### Target Files
- `@[c:\src\quorum\backend_v2\tests\unit\test_concurrency_fuzzer.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\test_llm_context_bounds.py]`
