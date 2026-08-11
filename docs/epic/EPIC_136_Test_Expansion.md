# Epic 136: Comprehensive Test Expansion & AST Guardrails — Implementation Plan

> **Parent Epic**: [EPIC_136_Test_Expansion.md](file:///c:/src/quorum/docs/epic/EPIC_136_Test_Expansion.md)

## Research Findings Summary

| # | Finding | Severity | Action |
|---|---------|----------|--------|
| 1 | AST assertions validated against codebase — all 6 construct locations confirmed | ✅ Valid | No change needed |
| 2 | `semaphore_max_concurrency` does not exist in [Settings.py](file:///c:/src/quorum/backend_v2/Settings.py) | 🔴 Critical | Fix reference to `max_concurrent_llm_steps` |
| 3 | DLQ resilience already proven by [test_dag_taskgroup.py](file:///c:/src/quorum/backend_v2/tests/unit/test_dag_taskgroup.py) | 🟡 Overlap | Refocus Step 2 on semaphore counting |
| 4 | `polyfactory` is NOT property-based testing | 🟡 Semantic | Correct terminology |
| 5 | Zero negative test cases specified (violates `anti_happy_path_mandate`) | 🔴 Critical | Add mandatory negative tests |
| 6 | Step 4 CI/CD command uses bash syntax | 🟡 Platform | Fix for PowerShell |
| 7 | Context bounds test IS genuinely novel | ✅ Valid | Proceed as-is |
| 8 | `html.escape` not present in codebase — AST guardrail would fail immediately | 🔴 Critical | Remove assertion or convert to aspirational guardrail |
| 9 | `hasattr` ban would cause 14+ false positives in existing services layer | 🔴 Critical | Scope ban exclusively to `backend_v2/api/` (Controllers) |
| 10 | Concurrency fuzzer patches wrong mock target — `litellm.acompletion` vs `provider.router.acompletion` | 🔴 Critical | Fix mock target to `provider.router.acompletion` |
| 11 | Context bounds negative test #2 overlaps with existing [test_adaptive_retry.py](file:///c:/src/quorum/backend_v2/tests/unit/llm/test_adaptive_retry.py) | 🟡 Overlap | Differentiate scope explicitly |
| 12 | `_safe_commit` is a nested function, not a class method — requires AST `FunctionDef` scanning | 🟡 Semantic | Add AST scanning

## Task Breakdown & Context Quarantine Strategy

To prevent context amnesia during the implementation of these extensive architectural tests, the execution phase MUST utilize the **Handover & Resume Protocol** to break down the work:

1. **Terminate Phase**: After completing a logical step or when context limits approach, execute `/tier5-session-handover`. The AI will summarize learned information (successes, challenges, architectural decisions) and update the tracker file (specifically: `@[c:\src\quorum\task.md]` under `# Session Handover Context`).
2. **New Session**: The user opens a completely new AI chat, resetting the context window to 100% capacity.
3. **Resume (Wakeup)**: The user inputs the generated `/tier5-resume --target=... --workflow=...` command as the first message in the new chat.
4. **Continue**: The new AI instance activates the RESUME & BOOTSTRAPPER protocol. It automatically loads architectural rules, reads the lessons from the tracker file, checks Git state, and seamlessly starts the next phase without context loss.

<execution_block>
<step id="1" name="Phase 1: AST Guardrails (Concurrency &amp; Domain Security)">
    <action>Create deterministic AST inspection guardrails ensuring critical concurrency and pacing constructs are never removed. Assert `asyncio.Semaphore` node in `backend_v2/llm/provider.py` and `backend_v2/services/orchestrator/dag_executor.py`. Assert `asyncio.TaskGroup` node in `backend_v2/services/orchestrator/dag_executor.py`, `backend_v2/worker.py`, and `backend_v2/services/execution.py`. Assert `enqueue_job` attribute call in `backend_v2/worker.py` and `backend_v2/services/execution.py`.</action>
    <action>Implement concurrency negative tests: 1. Missing Construct Detection (no `asyncio.Semaphore`). 2. False Positive Prevention (`Semaphore` as string literal).</action>
    <constraint invariant="ast_scanning_accuracy">AST scanner MUST NOT use naive string matching (`str.find`). It must recursively parse `ast.ImportFrom` nodes to build an alias map, detecting both `ast.Attribute` and `ast.Name` exactly.</constraint>
    <action>Create deterministic AST inspection guardrails for domain security. Assert `LLMClient.from_strategy` initialization. Assert `_safe_commit` (AsyncFunctionDef) in workflow loops. Assert `fastapi.responses.StreamingResponse` in streaming endpoints. Assert Pydantic strictness (`ConfigDict(strict=True, extra="forbid")`) specifically in ALL models defined under `backend_v2/models/`. Ban unstructured `run_chat()` specifically inside ALL files under `backend_v2/services/orchestrator/`.</action>
    <action>Implement domain security negative tests: 1. Banned Node Detection (`hasattr(obj, "field")` in `backend_v2/api/`). 2. False Positive Prevention (`hasattr` in `backend_v2/services/execution.py`).</action>
    <constraint invariant="strict_pydantic_v2_rust">The `hasattr` ban is strictly scoped to `backend_v2/api/` (Controller/Router layer) only.</constraint>
    <action>Execute local verification: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_ast_concurrency_guardrails.py --test` and `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_ast_domain_security_guardrails.py --test`.</action>
    <action>Execute `/tier5-session-handover` to start a new session for Phase 2, preventing Context Amnesia.</action>
</step>
<step id="2" name="Phase 2: Concurrency Fuzzer &amp; Context Boundary Tests">
    <action>Start the new session by executing `/tier5-resume` using the payload provided at the end of Phase 1.</action>
    <action>Create `backend_v2/tests/unit/test_concurrency_fuzzer.py` to prove Two-Tier Semaphore Architecture. Monkeypatch `max_concurrent_llm_steps` to 2. Explicitly instantiate a fresh instance of `DAGExecutor` (from `backend_v2/services/orchestrator/dag_executor.py`) inside the test function after monkeypatching. Clear caches in pytest setup/teardown (`_semaphores`, `_router_cache`, `_httpx_clients`).</action>
    <action>Patch `provider.router.acompletion` with a mock that implements an up/down atomic counter using `asyncio.Event()`. Fire 10 concurrent tasks via `asyncio.TaskGroup`. Assert `peak_concurrent &lt;= max_concurrent_llm_steps`.</action>
    <action>Implement fuzzer negative tests: 1. Boundary — Zero Concurrency (raises TimeoutError). 2. Boundary — Exceeding Physical Limit (tasks run without queuing delay).</action>
    <action>Create `backend_v2/tests/unit/test_llm_context_bounds.py` to prove `ContextWindowExceededError` maps to `AGENT_EXECUTION_CRITICAL` with Fail-Fast. Patch `provider.router.acompletion` to raise `litellm.ContextWindowExceededError` with strict args to prevent logger crash. Assert it catches mapped error and mock was called exactly once.</action>
    <action>Implement context bounds negative tests: 1. Non-Context 400 Error (maps to AGENT_RESPONSE_MALFORMED). 2. Transient 503 Error Path (maps to custom ServiceUnavailableError, asserts mock call_count > 1 to prove Tenacity resilience loop triggered).</action>
    <action>Execute local verification: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_concurrency_fuzzer.py --test` and `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_llm_context_bounds.py --test`.</action>
    <action>Execute global completion gates: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.</action>
</step>
</execution_block>

## 2. Architectural Impact & Compliance Matrix

- **Deprecations & Sunset List**: None explicitly listed.
- **Retained SSOT Invariants**: `max_concurrent_llm_steps`, `strict_pydantic_v2_rust`, `xml_structural_sovereignty_mandate`.
- **Compliance Gates**: `uv run python scripts/backend_audit_loop.py`

### Phase 1: AST Guardrails (Concurrency & Domain Security)
#### [NEW] @[backend_v2/tests/unit/test_ast_concurrency_guardrails.py]
#### [NEW] @[backend_v2/tests/unit/test_ast_domain_security_guardrails.py]

### Phase 2: Concurrency Fuzzer & Context Boundary Tests
#### [NEW] @[backend_v2/tests/unit/test_concurrency_fuzzer.py]
#### [NEW] @[backend_v2/tests/unit/test_llm_context_bounds.py]

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

## 5. Required Knowledge Items (KI Registry)

<required_knowledge_items>
  @[C:\Users\risto\.gemini\antigravity-ide\knowledge\ai_testing_standards\artifacts\ki_ai_testing_standards.md]
  @[C:\Users\risto\.gemini\antigravity-ide\knowledge\agent_context_quarantine\artifacts\ki_agent_context_quarantine.md]
  @[C:\Users\risto\.gemini\antigravity-ide\knowledge\neuro_symbolic_agentic_workflow\artifacts\ki_neuro_symbolic_agentic_workflow.md]
  @[.agents/rules/00-antigravity-core.md]
  @[.agents/rules/01-python-backend.md]
  @[.agents/rules/05_llm_architecture.md]
</required_knowledge_items>
