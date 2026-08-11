# EPIC 139: Strict Service Layer Type Checking (Replacing hasattr Duck Typing)

## 1. Goal Description & Background (Objective & Problem Statement)

**Objective**: Replace all remaining instances of the banned `hasattr` duck typing pattern within the `backend_v2/services/` layer with mathematically strict `isinstance` checks, Pydantic `BaseModel` reflection, or explicitly injected `Protocol` definitions.

**Problem Statement**: 
The `hasattr()` function allows lazy Duck Typing (structural assumption). According to Quorum's architectural rules (`01-python-backend.md`, rule `strict_pydantic_v2_rust`), Duck Typing is strictly forbidden because it bypasses the Fail-Fast architecture. Relying on `hasattr` to guess the structure of an incoming payload, dependency, or third-party error object masks silent state corruption and makes static analysis (MyPy/Ruff) impossible.

We have identified 9 highly sensitive core files in the Service Layer that still rely on `hasattr`:
1. `backend_v2/services/usage_service.py` (Dependency Injection protocols for the DB layer)
2. `backend_v2/services/sdui/adapters/variance_adapter.py` (SDUI Cache parsing)
3. `backend_v2/services/sdui/adapters/authenticity_adapter.py` (SDUI Cache parsing)
4. `backend_v2/services/orchestrator/synthesis_distiller.py` (I18nText resolution and Synthesis Blocks)
5. `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py` (Recursive schema reflection)
6. `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py` (Data dumping)
7. `backend_v2/services/orchestrator/strategies/llm.py` (Third-party tool parsing)
8. `backend_v2/services/llm_task_executor.py` (LLM error token tracking)
9. `backend_v2/services/execution.py` (SDUI Scale mapping)

These files represent the most complex "God Object" ecosystems in the application (DAG Engine, SDUI Synthesis, LLM Pipelines). Modifying them requires surgical precision and massive automated integration testing to prevent a catastrophic "Blast Radius".

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)
- **`hasattr(obj, "__dict__")`**: Deep recursive reflection in `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py` will be removed entirely.
- **`hasattr(self.audit_repo, "upsert_usage_aggregate")`**: Implicit dependency injection assumption will be removed.
- **`hasattr(s, "score")`**: Implicit DTO parsing will be removed.

### Retained SSOT Invariants (`What We Will RETAIN`)
- The internal structure of the DAG Execution engine will remain unchanged, only the validation gates are tightened.
- `Pydantic V2` strict typing remains the primary firewall. 

### Compliance & Modernity Gates
- **Zero-Compromise Fail-Fast**: Replacing `hasattr` with `isinstance` forces the system to either match the explicit type or crash loudly.
- **Protocol-Driven Worker Architecture**: Dependencies (specifically `audit_repo`) MUST implement explicit Python `typing.Protocol` classes.

### Producer-Consumer Integration Check
This change strictly enforces the Producer-Consumer contract. The consumer (specifically `backend_v2/services/execution.py`) will no longer guess if the producer sent the right data. It will assert the exact structural type using `isinstance` against the exact Pydantic domain models.

## 3. Phased Execution Plan (Implementation Strategy)

```xml
<execution_block>
<step id="1" name="Phase 1: Database &amp; Usage Dependency Injection (Protocol Binding)">
    <action>Define `UsageAuditRepositoryProtocol` in `backend_v2/database/interfaces.py` to mathematically guarantee the existence of `upsert_usage_aggregate` and `get_usage_records`. **CRITICAL:** You MUST decorate the protocol with `@typing.runtime_checkable` to allow `isinstance()` checks without raising TypeError.</action>
    <action>Update `backend_v2/services/usage_service.py` to type `self.audit_repo` against this Protocol and remove all 4 instances of `hasattr`.</action>
    <constraint invariant="strict_pydantic_v2_rust">Dependencies must be explicitly typed using Protocols, not duck typed.</constraint>
    <action>Execute `/tier5-session-handover` to start a new session for Phase 2, preventing Context Amnesia.</action>
</step>
<step id="2" name="Phase 2: SDUI Synthesis &amp; Adapter Type Enforcements">
    <action>Start the new session by executing `/tier5-resume` using the payload provided at the end of Phase 1.</action>
    <action>Update `backend_v2/services/sdui/adapters/variance_adapter.py` and `backend_v2/services/sdui/adapters/authenticity_adapter.py` to use strict `isinstance` against the cache model.</action>
    <action>Update `backend_v2/services/execution.py` to use strict `isinstance` against the scale model instead of `hasattr(s, "score")`.</action>
    <action>Update `backend_v2/services/orchestrator/synthesis_distiller.py` to use `isinstance(claim.label, I18nText)` and `isinstance` against the synthesis block model.</action>
    <action>Write explicit negative tests for `backend_v2/tests/unit/services/sdui/adapters/test_variance_adapter.py` and `backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py` that intentionally feed incorrect Data Transfer Objects (specifically: native dicts) and assert that they Fail-Fast by raising `TypeError` or `ValueError`.</action>
    <constraint invariant="universal_fail_fast">SDUI mappers must crash if the incorrect DTO is provided, not silently skip processing.</constraint>
    <action>Execute `/tier5-session-handover` to start a new session for Phase 3, preventing Context Amnesia.</action>
</step>
<step id="3" name="Phase 3: DAG Engine Recursive Reflection &amp; LLM Core (High Risk)">
    <action>Start the new session by executing `/tier5-resume` using the payload provided at the end of Phase 2.</action>
    <action>Update `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py` and `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`. Replace dangerous `hasattr(obj, "__dict__")` and `hasattr(obj, "model_dump")` with safe Pydantic V2 reflection: `isinstance(obj, BaseModel)` and utilizing `.model_dump()`. **CRITICAL:** Ensure the recursive reflection explicitly handles native collections (`list` and `dict`) using `isinstance(obj, (list, dict))` so that `.model_dump()` is only called on actual `BaseModel` instances, preventing runtime recursion crashes.</action>
    <action>Update `backend_v2/services/orchestrator/strategies/llm.py` and `backend_v2/services/llm_task_executor.py` to use strict Pydantic parsing for 3rd-party error objects instead of raw `hasattr` branching.</action>
    <constraint invariant="orchestrator_god_object_fragility">This phase modifies the core DAG engine and LLM pipelines. A full execution trace audit is mandatory.</constraint>
</step>
</execution_block>
```

### Phase 1: Database & Usage Dependency Injection
#### [MODIFY] @[backend_v2/database/interfaces.py]
#### [MODIFY] @[backend_v2/services/usage_service.py]

### Phase 2: SDUI Synthesis & Adapter Type Enforcements
#### [MODIFY] @[backend_v2/services/sdui/adapters/variance_adapter.py]
#### [MODIFY] @[backend_v2/services/sdui/adapters/authenticity_adapter.py]
#### [MODIFY] @[backend_v2/services/execution.py]
#### [MODIFY] @[backend_v2/services/orchestrator/synthesis_distiller.py]
#### [MODIFY] @[backend_v2/tests/unit/services/sdui/adapters/test_variance_adapter.py]
#### [MODIFY] @[backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py]

### Phase 3: DAG Engine Recursive Reflection & LLM Core (High Risk)
#### [MODIFY] @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py]
#### [MODIFY] @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]
#### [MODIFY] @[backend_v2/services/orchestrator/strategies/llm.py]
#### [MODIFY] @[backend_v2/services/llm_task_executor.py]


## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done
- ZERO occurrences of `hasattr` exist within the `backend_v2/services/` directory.
- `usage_service.py` dependencies are strictly bound by a `Protocol`.
- All `isinstance` checks are backed by explicit DTO imports.

### Automated Unit Tests
- Must run after every single Phase (File modification batch):
  `uv run python scripts/backend_audit_loop.py backend_v2/services/ --test`

### Manual Verification
- N/A. This is a pure backend architectural refactor.

### MANDATORY Final E2E REST API Verification Gate
Due to the modification of `prompt_factory.py` (which builds the foundational LLM prompts), the E2E Live LLM test MUST pass to ensure no prompt structure was destroyed.
```bash
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

## 5. Required Knowledge Items (KI Registry)

```xml
<required_knowledge_items>
  - @[.agents/rules/00-antigravity-core.md]
  - @[.agents/rules/01-python-backend.md]
  - @[C:\Users\risto\.gemini\antigravity-ide\knowledge\ai_testing_standards\artifacts\ki_ai_testing_standards.md]
  - @[C:\Users\risto\.gemini\antigravity-ide\knowledge\tripartite_pipeline_architecture\artifacts\ki_tripartite_pipeline_architecture.md]
  - @[C:\Users\risto\.gemini\antigravity-ide\knowledge\execution_engine_protocol\artifacts\ki_execution_engine_protocol.md]
</required_knowledge_items>
```
