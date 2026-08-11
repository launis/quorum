# EPIC 139: Strict Service Layer Type Checking (Replacing hasattr Duck Typing)

## 1. Goal Description & Background (Objective & Problem Statement)

**Objective**: Replace all remaining instances of the banned `hasattr` duck typing pattern within the `backend_v2/services/` layer with mathematically strict `isinstance` checks, Pydantic `BaseModel` reflection, or explicitly injected `Protocol` definitions.

**Problem Statement**: 
The `hasattr()` function allows lazy Duck Typing (structural assumption). According to Quorum's architectural rules (`01-python-backend.md`, rule `strict_pydantic_v2_rust`), Duck Typing is strictly forbidden because it bypasses the Fail-Fast architecture. Relying on `hasattr` to guess the structure of an incoming payload, dependency, or third-party error object masks silent state corruption and makes static analysis (MyPy/Ruff) impossible.

We have identified 9 highly sensitive core files in the Service Layer that still rely on `hasattr`:
1. `usage_service.py` (Dependency Injection protocols for the DB layer)
2. `sdui/adapters/variance_adapter.py` (SDUI Cache parsing)
3. `sdui/adapters/authenticity_adapter.py` (SDUI Cache parsing)
4. `orchestrator/synthesis_distiller.py` (I18nText resolution and Synthesis Blocks)
5. `orchestrator/strategies/llm_execution/prompt_factory.py` (Recursive schema reflection)
6. `orchestrator/strategies/llm_execution/context_builder.py` (Data dumping)
7. `orchestrator/strategies/llm.py` (Third-party tool parsing)
8. `llm_task_executor.py` (LLM error token tracking)
9. `execution.py` (SDUI Scale mapping)

These files represent the most complex "God Object" ecosystems in the application (DAG Engine, SDUI Synthesis, LLM Pipelines). Modifying them requires surgical precision and massive automated integration testing to prevent a catastrophic "Blast Radius".

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)
- **`hasattr(obj, "__dict__")`**: Deep recursive reflection in `prompt_factory.py` will be removed entirely.
- **`hasattr(self.audit_repo, "upsert_usage_aggregate")`**: Implicit dependency injection assumption will be removed.
- **`hasattr(s, "score")`**: Implicit DTO parsing will be removed.

### Retained SSOT Invariants (`What We Will RETAIN`)
- The internal structure of the DAG Execution engine will remain unchanged, only the validation gates are tightened.
- `Pydantic V2` strict typing remains the primary firewall. 

### Compliance & Modernity Gates
- **Zero-Compromise Fail-Fast**: Replacing `hasattr` with `isinstance` forces the system to either match the explicit type or crash loudly.
- **Protocol-Driven Worker Architecture**: Dependencies (specifically `audit_repo`) MUST implement explicit Python `typing.Protocol` classes.

### Producer-Consumer Integration Check
This change strictly enforces the Producer-Consumer contract. The consumer (specifically `execution.py`) will no longer guess if the producer sent the right data. It will assert the exact structural type using `isinstance` against the exact Pydantic domain models.

## 3. Phased Execution Plan (Implementation Strategy)

```xml
<execution_block>
<step id="1" name="Phase 1: Database &amp; Usage Dependency Injection (Protocol Binding)">
    <action>Define `UsageAuditRepositoryProtocol` in `interfaces.py` to mathematically guarantee the existence of `upsert_usage_aggregate` and `get_usage_records`.</action>
    <action>Update `usage_service.py` to type `self.audit_repo` against this Protocol and remove all 4 instances of `hasattr`.</action>
    <constraint invariant="strict_pydantic_v2_rust">Dependencies must be explicitly typed using Protocols, not duck typed.</constraint>
</step>
<step id="2" name="Phase 2: SDUI Synthesis &amp; Adapter Type Enforcements">
    <action>Update `variance_adapter.py` and `authenticity_adapter.py` to use strict `isinstance` against the cache model.</action>
    <action>Update `execution.py` to use strict `isinstance` against the scale model instead of `hasattr(s, "score")`.</action>
    <action>Update `synthesis_distiller.py` to use `isinstance(claim.label, I18nText)` and `isinstance` against the synthesis block model.</action>
    <constraint invariant="universal_fail_fast">SDUI mappers must crash if the incorrect DTO is provided, not silently skip processing.</constraint>
</step>
<step id="3" name="Phase 3: DAG Engine Recursive Reflection &amp; LLM Core (High Risk)">
    <action>Update `prompt_factory.py` and `context_builder.py`. Replace dangerous `hasattr(obj, "__dict__")` and `hasattr(obj, "model_dump")` with safe Pydantic V2 reflection: `isinstance(obj, BaseModel)` and utilizing `.model_dump()`.</action>
    <action>Update `llm.py` and `llm_task_executor.py` to use strict Pydantic parsing for 3rd-party error objects instead of raw `hasattr` branching.</action>
    <constraint invariant="orchestrator_god_object_fragility">This phase modifies the core DAG engine and LLM pipelines. A full execution trace audit is mandatory.</constraint>
</step>
</execution_block>
```

### Phase 1: Database & Usage Dependency Injection
#### [MODIFY] @[c:\src\quorum\backend_v2\database\interfaces.py]
#### [MODIFY] @[c:\src\quorum\backend_v2\services\usage_service.py]

### Phase 2: SDUI Synthesis & Adapter Type Enforcements
#### [MODIFY] @[c:\src\quorum\backend_v2\services\sdui\adapters\variance_adapter.py]
#### [MODIFY] @[c:\src\quorum\backend_v2\services\sdui\adapters\authenticity_adapter.py]
#### [MODIFY] @[c:\src\quorum\backend_v2\services\execution.py]
#### [MODIFY] @[c:\src\quorum\backend_v2\services\orchestrator\synthesis_distiller.py]

### Phase 3: DAG Engine Recursive Reflection & LLM Core (High Risk)
#### [MODIFY] @[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm_execution\prompt_factory.py]
#### [MODIFY] @[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm_execution\context_builder.py]
#### [MODIFY] @[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]
#### [MODIFY] @[c:\src\quorum\backend_v2\services\llm_task_executor.py]


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
  - @[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]
  - @[c:\Users\risto\.gemini\antigravity-ide\knowledge\epic_lifecycle_workflow\artifacts\ki_epic_lifecycle_workflow.md]
</required_knowledge_items>
```
