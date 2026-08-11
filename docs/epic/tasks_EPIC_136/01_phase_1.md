# Implementation Plan: Phase 1: AST Guardrails (Concurrency & Domain Security)

<required_context_rules>
  @[c:\src\quorum\.agents\rules\00-antigravity-core.md]
  @[c:\src\quorum\.agents\rules\01-python-backend.md]
  @[c:\src\quorum\.agents\rules\05_llm_architecture.md]
  @[C:\Users\risto\.gemini\antigravity-ide\knowledge\ai_testing_standards\artifacts\ki_ai_testing_standards.md]
  @[C:\Users\risto\.gemini\antigravity-ide\knowledge\agent_context_quarantine\artifacts\ki_agent_context_quarantine.md]
  @[C:\Users\risto\.gemini\antigravity-ide\knowledge\neuro_symbolic_agentic_workflow\artifacts\ki_neuro_symbolic_agentic_workflow.md]
</required_context_rules>

<anti_targets>
- Do NOT modify the actual implementation of `asyncio.Semaphore` or `asyncio.TaskGroup` in the source code.
- Do NOT purge `hasattr` from the `backend_v2/services/` layer; the ban is strictly scoped to `backend_v2/api/`.
</anti_targets>

<dod_checklist>
- [ ] AST scanning assertions do not use `str.find` for imports.
- [ ] Negative tests exist for missing constructs and false positives (including Pydantic strictness and `run_chat`).
- [ ] `hasattr` ban scope is successfully restricted to `backend_v2/api/`.
- [ ] Aspirational test for `html.escape` is added and skipped.
- [ ] `backend_audit_loop.py` passes for all new tests.
</dod_checklist>

<execution_protocol>
<step id="1" name="Phase 1: AST Guardrails (Concurrency & Domain Security)">
    <action>Create deterministic AST inspection guardrails ensuring critical concurrency and pacing constructs are never removed. Assert `asyncio.Semaphore` node in `backend_v2/llm/provider.py` and `backend_v2/services/orchestrator/dag_executor.py`. Assert `asyncio.TaskGroup` node in `backend_v2/services/orchestrator/dag_executor.py`, `backend_v2/worker.py`, and `backend_v2/services/execution.py`. Assert `enqueue_job` attribute call in `backend_v2/worker.py` and `backend_v2/services/execution.py`.</action>
    <action>Implement concurrency negative tests: 1. Missing Construct Detection (no `asyncio.Semaphore`). 2. False Positive Prevention (`Semaphore` as string literal).</action>
    <constraint invariant="ast_scanning_accuracy">AST scanner MUST NOT use naive string matching (`str.find`). It must recursively parse `ast.ImportFrom` nodes to build an alias map, detecting both `ast.Attribute` and `ast.Name` exactly.</constraint>
    <action>Create deterministic AST inspection guardrails for domain security. Assert `LLMClient.from_strategy` initialization. Assert `_safe_commit` (AsyncFunctionDef) in workflow loops. Assert `fastapi.responses.StreamingResponse` in streaming endpoints. Assert Pydantic strictness (`ConfigDict(strict=True, extra="forbid")`) specifically in ALL models defined under `backend_v2/models/`. Ban unstructured `run_chat()` specifically inside ALL files under `backend_v2/services/orchestrator/`.</action>
    <action>Implement domain security negative tests: 1. Banned Node Detection (`hasattr(obj, "field")` in `backend_v2/api/`). 2. False Positive Prevention (`hasattr` in `backend_v2/services/execution.py`). 3. Missing Pydantic Strictness (model missing `ConfigDict` or `extra="forbid"`). 4. Banned `run_chat` Attribute Call.</action>
    <constraint invariant="strict_pydantic_v2_rust">The `hasattr` ban is strictly scoped to `backend_v2/api/` (Controller/Router layer) only.</constraint>
    <action>Add an aspirational, skipped test (`@pytest.mark.skip(reason="Awaiting prompt sanitization implementation")`) that asserts the presence of `html.escape` payload sanitization, fulfilling the Epic's documented Q4 resolution.</action>
    <action>Execute local verification: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_ast_concurrency_guardrails.py --test` and `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_ast_domain_security_guardrails.py --test`.</action>
    <action>Execute `/tier5-session-handover` to start a new session for Phase 2, preventing Context Amnesia.</action>
</step>
<validation_gate>
    <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_ast_concurrency_guardrails.py --test`</action>
    <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_ast_domain_security_guardrails.py --test`</action>
</validation_gate>
</execution_protocol>

### Target Files
- `@[c:\src\quorum\backend_v2\tests\unit\test_ast_concurrency_guardrails.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\test_ast_domain_security_guardrails.py]`
