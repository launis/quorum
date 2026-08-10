# EPIC 136: Comprehensive Test Expansion & AST Guardrails

## Objective
Establish a robust, mathematically verifiable test suite across Quorum's backend to prevent regressions related to concurrency bottlenecks, AST-level pacing logic removal, and LLM context window exploitation.

## Scope
- **Target Directories:** `backend_v2/tests/unit/`
- **Focus Areas:**
  - `provider.py`, `dag_executor.py`, and `worker.py` AST integrity
  - Pacing & Semaphore bottlenecks
  - LLM Mock Context Bounds `ContextWindowExceededError`

## Proposed Changes

### [NEW] `@[c:\src\quorum\backend_v2\tests\unit\test_ast_pacing_audit.py]`
- Implementation of a strict `ast` inspection suite.

### [NEW] `@[c:\src\quorum\backend_v2\tests\unit\test_concurrency_fuzzer.py]`
- Heavy concurrency behavioral fuzzing for Semaphore bound validation.

### [NEW] `@[c:\src\quorum\backend_v2\tests\unit\test_llm_context_bounds.py]`
- Mock Context Limit testing simulating Vertex AI ContextWindowExceededError.

```xml
<execution_protocol level="0_create_plan">
  <step id="1" name="AST Static Analysis Audit Test">
    <action>Create a deterministic Pytest suite using Python's native `ast` module.</action>
    <action>Scan `backend_v2/llm/provider.py`, `backend_v2/services/orchestrator/dag_executor.py`, and `backend_v2/worker.py` AST nodes.</action>
    <action>Assert that `asyncio.Semaphore`, `asyncio.TaskGroup`, and `enqueue_job` mechanics are physically present in the code. This ensures if an AI agent or developer removes pacing logic, this AST test instantly fails the CI/CD build.</action>
    <constraint invariant="zero_legacy_fallback_hacks">Ensure no fallback logic allows bypassing the AST check.</constraint>
  </step>
  
  <step id="2" name="Semaphore &amp; Pacing Fuzz Tests">
    <action>Instantiate the `LLMClient` with a mock LiteLLM provider in `test_concurrency_fuzzer.py`.</action>
    <action>Fire 50 concurrent `asyncio.TaskGroup` generation requests against the system simultaneously.</action>
    <action>Assert mathematically that no more than `settings.max_concurrent_llm_steps` requests actually execute at exactly the same time, preventing infinite retry loops and deadlock traps.</action>
    <constraint invariant="system_concurrency_ssot">All global execution limits MUST reference `settings.py` strictly. Enforce Two-Tier Semaphore Architecture.</constraint>
  </step>

  <step id="3" name="LLM Mock Context Limit Bounds Testing">
    <action>Simulate Vertex AI throwing `ContextWindowExceededError` (using `litellm.exceptions.ContextWindowExceededError`) inside `test_llm_context_bounds.py`.</action>
    <action>Assert that the backend properly intercepts this as a `AGENT_EXECUTION_CRITICAL` App Exception instead of silently falling into a recursive infinite retry loop. The mock must be called exactly once to prove no retries occur.</action>
    <action>Ensure the `AppErrorBoundary` cleanly halts the trace.</action>
  </step>

  <step id="4" name="Verification &amp; E2E Gates">
    <action>Run backend linting and typing audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`</action>
    <action>Windows/PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`</action>
  </step>
</execution_protocol>
```
