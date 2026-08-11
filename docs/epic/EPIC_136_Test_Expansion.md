# Epic 136: Comprehensive Test Expansion & AST Guardrails — Implementation Plan

> **Parent Epic**: [EPIC_136_Test_Expansion.md](file:///c:/src/quorum/docs/epic/EPIC_136_Test_Expansion.md)

## Research Findings Summary

| # | Finding | Severity | Action |
|---|---------|----------|--------|
| 1 | AST assertions validated against codebase — all 6 construct locations confirmed | ✅ Valid | No change needed |
| 2 | `settings.semaphore_max_concurrency` does not exist in [settings.py](file:///c:/src/quorum/backend_v2/settings.py#L100-L120) | 🔴 Critical | Fix reference to `max_concurrent_llm_steps` |
| 3 | DLQ resilience already proven by [test_dag_taskgroup.py](file:///c:/src/quorum/backend_v2/tests/unit/test_dag_taskgroup.py) | 🟡 Overlap | Refocus Step 2 on semaphore counting |
| 4 | `polyfactory` is NOT property-based testing | 🟡 Semantic | Correct terminology |
| 5 | Zero negative test cases specified (violates `anti_happy_path_mandate`) | 🔴 Critical | Add mandatory negative tests |
| 6 | Step 4 CI/CD command uses bash syntax | 🟡 Platform | Fix for PowerShell |
| 7 | Context bounds test IS genuinely novel | ✅ Valid | Proceed as-is |
| 8 | `html.escape` not present in codebase — AST guardrail would fail immediately | 🔴 Critical | Remove assertion or convert to aspirational guardrail |
| 9 | `hasattr` ban would cause 14+ false positives in existing services layer | 🔴 Critical | Scope ban exclusively to `backend_v2/api/` (Controllers) |
| 10 | Concurrency fuzzer patches wrong mock target — `litellm.acompletion` vs `provider.router.acompletion` | 🔴 Critical | Fix mock target to `provider.router.acompletion` |
| 11 | Context bounds negative test #2 overlaps with existing [test_adaptive_retry.py](file:///c:/src/quorum/backend_v2/tests/unit/llm/test_adaptive_retry.py) | 🟡 Overlap | Differentiate scope explicitly |
| 12 | `_safe_commit` is a nested function, not a class method — requires AST `FunctionDef` scanning | 🟡 Semantic | Add AST scanning clarification |

---

## Proposed Changes

<execution_protocol>
    <step id="1a_test_ast_concurrency">
        <target_file>backend_v2/tests/unit/test_ast_concurrency_guardrails.py</target_file>
        <action>
            Create deterministic AST inspection guardrails ensuring critical concurrency and pacing constructs are never removed.
            
            Positive Tests:
            - Assert `asyncio.Semaphore` node present in `backend_v2/llm/provider.py` and `backend_v2/services/orchestrator/dag_executor.py`
            - Assert `asyncio.TaskGroup` node present in `backend_v2/services/orchestrator/dag_executor.py`, `backend_v2/worker.py`, and `backend_v2/services/execution.py`
            - Assert `enqueue_job` attribute call present in `backend_v2/worker.py` and `backend_v2/services/execution.py`
            
            Mandatory Negative Tests:
            1. Missing Construct Detection: Create string WITHOUT `asyncio.Semaphore`, assert AST scanner FAILS.
            2. False Positive Prevention: Create string with `Semaphore` as string literal, assert scanner passes.
            
            Critical Implementation Notes:
            - AST scanner MUST NOT use naive string matching (`str.find`). It must recursively parse `ast.ImportFrom` nodes to build an alias map, detecting both `ast.Attribute` and `ast.Name` exactly.
        </action>
    </step>
    
    <step id="1b_test_ast_domain_security">
        <target_file>backend_v2/tests/unit/test_ast_domain_security_guardrails.py</target_file>
        <action>
            Create deterministic AST inspection guardrails ensuring domain purity and architectural security constructs are strictly enforced.
            
            Positive Tests:
            - Assert `LLMClient.from_strategy` is used for LLM initializations.
            - Assert `_safe_commit` is called in workflow loops. Note: `_safe_commit` is a nested `async def`, so the AST scanner MUST search for `ast.AsyncFunctionDef` nodes with `name == "_safe_commit"` within the parsed tree, in addition to `ast.Call`.
            - Assert `StreamingResponse` is used in streaming endpoints.
            - Assert Pydantic strictness: Assert that critical domain models define `ConfigDict(strict=True)` or `extra="forbid"`. Do NOT ban `.get()` at the AST level to prevent CI/CD false positives with `os.environ.get`.
            - Assert Structured Execution Mandate: Ban unstructured `run_chat()` inside `backend_v2/services/orchestrator/`.
            
            Mandatory Negative Tests:
            1. Banned Node Detection: Create string containing `hasattr(obj, "field")` scoped to Controller layer, assert AST scanner FAILS.
            
            Critical Implementation Notes:
            - REMOVED: `html.escape` assertion. Implemented as an aspirational test with `@pytest.mark.skip(reason="Awaiting prompt sanitization implementation")`.
            - SCOPED: `hasattr` ban is strictly scoped to `backend_v2/api/` (Controller/Router layer) only.
            - AST scanner MUST NOT use naive string matching (`str.find`). It must recursively parse `ast.ImportFrom` nodes to build an alias map, detecting both `ast.Attribute` and `ast.Name` exactly.
        </action>
    </step>
    
    <step id="2_test_concurrency">
        <target_file>backend_v2/tests/unit/test_concurrency_fuzzer.py</target_file>
        <action>
            Create test to prove the Two-Tier Semaphore Architecture mathematically bounds concurrent execution at the Provider-level HTTP semaphore (`LiteLLMProvider._semaphores`).
            
            Architecture:
            1. Monkeypatch `settings.max_concurrent_llm_steps` to 2.
            2. CRITICAL STATE LEAK PREVENTION: Clear caches in pytest setup/teardown: `LiteLLMProvider._semaphores.clear()`, `LiteLLMProvider._router_cache.clear()`, and `LiteLLMProvider._httpx_clients.clear()`.
            3. Patch `provider.router.acompletion` (NOT `litellm.acompletion`) with a mock that implements an up/down atomic counter (`in_flight += 1; await asyncio.sleep(0.05); in_flight -= 1`).
            4. Fire 10 concurrent tasks. Do NOT use `asyncio.Barrier` (causes deadlocks). Track peak counter safely in memory.
            5. Assert `peak_concurrent <= settings.max_concurrent_llm_steps` (=2).
            
            Mandatory Negative Tests:
            1. Boundary — Zero Concurrency: Set `max_concurrent_llm_steps = 0`, execute inside `asyncio.wait_for(..., timeout=0.2)`, assert it raises `TimeoutError`.
            2. Boundary — Exceeding Physical Limit: Set limit exceeding task count (e.g. 20), assert all tasks run without queuing delay.
            
            Note: Use `polyfactory` with `ModelFactory.__random__ = Random(42)` for deterministic mock inputs.
        </action>
    </step>
    
    <step id="3_test_context_bounds">
        <target_file>backend_v2/tests/unit/test_llm_context_bounds.py</target_file>
        <action>
            Create test to prove `ContextWindowExceededError` is mapped to `AgentExecutionError(AGENT_EXECUTION_CRITICAL)` with Fail-Fast (no retry loops).
            
            Positive Test:
            1. Patch `provider.router.acompletion` to raise `litellm.ContextWindowExceededError`. Instantiate with strict args: `message="Context exceeded"`, `model="gpt-4"`, `llm_provider="openai"` to prevent logger crash.
            2. Assert `pytest.raises(AgentExecutionError)` catches the mapped error.
            3. Assert `provider.router.acompletion` was called EXACTLY once (proving Tenacity retries are bypassed).
            4. Assert `exc.details["error_code"]` equals `ErrorCodes.AGENT_EXECUTION_CRITICAL` (RFC 7807 Dual-Reporting).
            
            Mandatory Negative Tests:
            1. Non-Context 400 Error: Patch to raise generic 400 error WITHOUT "context" or "token". Assert it maps to `AGENT_RESPONSE_MALFORMED` (not `AGENT_EXECUTION_CRITICAL`).
            2. Transient 503 Error Path: Patch to raise `litellm.ServiceUnavailableError`. Assert it maps to custom `ServiceUnavailableError` (not AgentExecutionError). Assert mock `call_count > 1` proving Tenacity resilience loop triggered (this explicitly differentiates from `test_adaptive_retry.py` which uses `RateLimitError`).
        </action>
    </step>
    
    <step id="4_verification">
        <target_file>terminal</target_file>
        <action>
            Execute the global completion gates:
            uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_ast_concurrency_guardrails.py --test
            uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_ast_domain_security_guardrails.py --test
            uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_concurrency_fuzzer.py --test
            uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_llm_context_bounds.py --test
            uv run python scripts/backend_audit_loop.py backend_v2/ --test
        </action>
    </step>
</execution_protocol>

---

## Open Questions

> [!IMPORTANT]
> **Q1: Should we delete the existing [test_worker_dlq_fallback.py](file:///c:/src/quorum/backend_v2/tests/unit/test_worker_dlq_fallback.py)?**
> It's only 28 lines and its DLQ assertion overlaps with the broader [test_dag_taskgroup.py](file:///c:/src/quorum/backend_v2/tests/unit/test_dag_taskgroup.py). However, it tests a different layer (worker-level `render_profile_job` vs DAG-level step isolation). Recommend: **Keep it** — different architectural layers deserve independent tests even if the behavioral contract is the same.
> **STATUS: APPROVED BY USER**

> [!IMPORTANT]
> **Q2: Should the concurrency fuzzer test the Provider-level HTTP semaphore (`_semaphores`) separately?**
> The current plan only tests the DAG-level semaphore (`max_concurrent_llm_steps`). Testing the Provider's internal HTTP semaphore would require deeper provider instantiation mocking. Recommend: **Defer to a follow-up Epic** to keep this Epic scoped at 3 files.
> **STATUS: APPROVED BY USER**

> [!WARNING]
> **Q3 (NEW): The `hasattr` ban scope reduction is a significant deviation from the Epic's original intent.**
> The Epic mandated banning `hasattr` across "Service and Controller layers". Research found 14+ legitimate usages that would require individual refactoring. Should this full cleanup be: (A) Tracked as an immediate follow-up Epic, or (B) Treated as acceptable technical debt for now?
> **Recommendation (Future-proof & Straightforward): Option A.** Refactoring 14+ files in this Epic creates a high risk of regression and breaks the Single Responsibility of this "Test Expansion" Epic. The straightforward solution is to scope the AST ban exclusively to the Controller layer (`backend_v2/api/`) for now to prevent new duck-typing at the API boundary, while immediately opening a follow-up Epic to systematically purge `hasattr` from the Services layer. This maintains strict domain purity (`strict_pydantic_v2_rust`) long-term without destabilizing the current work.
> **STATUS: APPROVED BY USER**

> [!WARNING]
> **Q4 (NEW): The `html.escape` assertion removal is an unresolved security gap.**
> The Epic's original intent was to enforce payload sanitization. The construct doesn't exist yet, meaning the security guardrail has no backing implementation. Should this be: (A) Tracked as a P0 security Epic for immediate implementation, or (B) Added as a commented-out aspirational test with a `@pytest.mark.skip(reason="Awaiting prompt sanitization implementation")`?
> **Recommendation (Future-proof & Straightforward): Option B.** Writing the test now and marking it `@pytest.mark.skip` acts as a permanent, executable architectural anchor. It is straightforward because it fulfills the current Epic's goal (expanding the test suite) without blocking execution on a missing feature. It is future-proof because the skipped test serves as a persistent reminder of the security debt (`xml_structural_sovereignty_mandate`) that cannot be ignored by future agents.
> **STATUS: APPROVED BY USER**

## Required Context Rules for Execution

```xml
<required_context_rules>
  @[.agents/rules/00-antigravity-core.md]
  @[.agents/rules/01-python-backend.md]
  @[.agents/rules/05_llm_architecture.md]
</required_context_rules>
```
