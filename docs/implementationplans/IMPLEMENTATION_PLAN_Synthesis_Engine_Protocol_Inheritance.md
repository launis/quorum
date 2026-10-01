> **STATUS: READY FOR EXECUTION**

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
</required_context_rules>

# Implementation Plan: Unified ExecutionEngine Protocol Inheritance & Type Hardening (F-03 & Engine Parity)

## 1. Executive Summary & Problem Description

### Current State (Finding F-03 & Engine Parity)
Quorum's execution engines implement the centralized `ExecutionEngine(Protocol)` interface (`@[backend_v2/services/orchestrator/engines/base.py#L11-L31]`).
In the physical codebase, execution engines diverged into an asymmetrical state:
- `TDAEngine(ExecutionEngine)` (`@[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]`): Inherits from the protocol, but its `execute()` method lacks the PEP 698 `@override` annotation.
- `PromptEngine(ExecutionEngine)` (`@[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L74]`): Inherits from the protocol, but its `execute()` method lacks the PEP 698 `@override` annotation. Furthermore, `PromptEngine` invokes `running_event.set()` prematurely prior to acquiring the semaphore lock, violating the `atomic_telemetry_signaling_mandate`.
- `SynthesisEngine` (`@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`): States in its docstring that it implements the protocol, but its class definition is bare `class SynthesisEngine:` without explicit Protocol inheritance, without `@override` annotation, and without `running_event` telemetry signaling.

This plan comprehensively harmonizes the entire `ExecutionEngine` triad (`TDAEngine`, `PromptEngine`, `SynthesisEngine`) and their test suites into 100% symmetrical and type-safe compliance.

---

## 2. Target Scope & Boundaries

### 2.1 Target Files
- `[MODIFY] @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L74]`
- `[MODIFY] @[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]`

### 2.2 Context / Read-Only Files
- `@[backend_v2/services/orchestrator/engines/base.py#L11-L31]` (SSOT `ExecutionEngine(Protocol)`)
- `@[backend_v2/services/orchestrator/engines/__init__.py]` (Public engine exports)
- `@[backend_v2/models/dtos/engine.py#L61-L132]` (`EngineExecutionRequest`)
- `@[backend_v2/services/orchestrator/dag_executor.py#L160-L187]` (`_resolve_execution_engine` returning `ExecutionEngine`)
- `@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1010]` (`LLMNodeStrategy` execution)

---

## 3. Five-Axis System 2 Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]` | Banned duck-typing without formal Protocol inheritance, missing PEP 698 `@override` on `execute()`, and omitted `running_event` telemetry signaling inside the semaphore lock. | Formal `class SynthesisEngine(ExecutionEngine):` inheritance with PEP 698 `@override` on `execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:`, and atomic `if request.running_event: request.running_event.set()` signaling inside `async with request.semaphore_cm:`. | Pruned unnecessary wrapper classes, intermediate adapter layers, and speculative engine factories. Uses direct protocol inheritance from `ExecutionEngine`. | `issubclass(SynthesisEngine, ExecutionEngine)` is `True`; `isinstance(engine, ExecutionEngine)` is `True`; MyPy strict passes cleanly; `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/synthesis_engine.py --test`. |
| `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L74]` | Banned missing PEP 698 `@override` on `execute()`, and premature `running_event.set()` outside the semaphore lock context. | PEP 698 `@override` decorator on `execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:`, and atomic `if request.running_event: request.running_event.set()` signaling relocated inside `async with request.semaphore_cm:`. | Pruned unnecessary layers; direct 2-line relocation inside semaphore context. | MyPy strict passes cleanly; `pytest backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py` passes 100%. |
| `@[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]` | Banned missing PEP 698 `@override` on `execute()`. | PEP 698 `@override` decorator on `execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:`. | Direct decorator addition without altering internal graph execution mechanics. | MyPy strict passes cleanly; `pytest backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py` passes 100%. |
| `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]` | Banned defensive `.get("error_code")` dict lookups in test assertions across error-handling tests, banned naked `dict[str, Any]` in `make_atom` test helper, and omitted ISTQB test coverage for Protocol subclassing, instance typing, and semaphore telemetry signaling. | Direct typed dictionary assertions `assert exc_info.value.details["error_code"] == ErrorCodes.SYNTHESIS_ENGINE_ERROR.value`, typed `DraftExtractedAtom` in `make_atom` test helper, formal `issubclass` and `isinstance` Protocol verification, and dedicated negative partition tests for null concurrency limiters. | Pruned redundant mock classes or multi-layer test fixtures; reuses existing `base_request` fixture and `mock_executor` with typed `AsyncMock`. | `pytest backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py` passes 100% with >= 90% branch coverage (16/16 tests passing). |
| `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]` | Banned omitted ISTQB test coverage for Protocol subclassing and instance typing. | Dedicated `test_prompt_engine_implements_protocol()` asserting `issubclass(PromptEngine, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`. | Reuses existing `mock_executor` fixture without extra test scaffolding. | `pytest backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py` passes 100% (6/6 tests passing). |
| `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]` | Banned defensive `.get()` dictionary lookups in test assertions (`eg_kwargs.get(...)`, `kwargs.get(...)`), and omitted ISTQB test coverage for Protocol subclassing and instance typing. | Direct subscript dictionary assertions (`assert eg_kwargs["execution_id"] == ...`), positive key membership checks, and dedicated `test_tda_engine_implements_protocol()` asserting `issubclass(TDAEngine, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`. | Reuses existing `mock_compiler` fixture without extra test scaffolding. | `pytest backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py` passes 100% (10/10 tests passing). |

---

## 4. Execution Protocol & Action Steps

<execution_protocol>
  <phase id="1" name="PRE_IMPLEMENTATION_CLEANUPS">
    <step id="1.1" name="FIX_SYNTHESIS_TEST_ASSERTION_REFLECTION">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, remove `from typing import Any` and import `DraftExtractedAtom` from `backend_v2.models.domain.blackboard` to enforce zero permissive typing imports.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L29-L43]`, refactor `make_atom` test helper to return typed `DraftExtractedAtom` instead of naked `dict[str, Any]` to comply with `ki_zero_permissive_typing.md`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L108-L121]`, eliminate defensive dictionary lookup `.get("error_code")` and replace with direct typed dictionary access `assert exc_info.value.details["error_code"] == ErrorCodes.SYNTHESIS_ENGINE_ERROR.value` to comply with `ki_zero_permissive_typing.md`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L167-L180]`, eliminate defensive dictionary lookup `.get("error_code")` and replace with direct typed dictionary access `assert exc_info.value.details["error_code"] == ErrorCodes.SYNTHESIS_ENGINE_ERROR.value` to comply with `ki_zero_permissive_typing.md`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L183-L199]`, eliminate defensive dictionary lookup `.get("error_code")` and replace with direct typed dictionary access `assert exc_info.value.details["error_code"] == "CUSTOM_ERROR"` to comply with `ki_zero_permissive_typing.md`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L434-L453]`, add explicit `assert exc_info.value.details is not None` and `assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value` to enforce Fail-Fast schema assertions.</action>
    </step>
    <step id="1.2" name="FIX_TDA_ENGINE_TEST_ASSERTION_REFLECTION">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py#L76-L133]`, eliminate defensive `.get("progress_callback")` lookups in mock callbacks and replace with positive key membership guards.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py#L76-L133]`, eliminate defensive dictionary lookups `eg_kwargs.get("execution_id")` and `eg_kwargs.get("step_id")` and replace with direct subscript assertions `assert eg_kwargs["execution_id"] == engine_request.context.execution_id` and `assert eg_kwargs["step_id"] == engine_request.step.id`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py#L329-L371]`, eliminate defensive dictionary lookup `eg_kwargs.get("matrix_context")` and replace with direct subscript assertion `passed_matrix_context = eg_kwargs["matrix_context"]`.</action>
    </step>
  </phase>

  <phase id="2" name="ENGINE_PROTOCOL_INHERITANCE_AND_OVERRIDE">
    <step id="2.1" name="INHERIT_EXECUTION_ENGINE_PROTOCOL">
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`, import `override` from `typing` and import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base`.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`, update class definition to `class SynthesisEngine(ExecutionEngine):`.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L51-L286]`, decorate `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:` with `@override`.</action>
    </step>
    <step id="2.2" name="ATOMIC_TELEMETRY_SIGNALING">
      <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L51-L286]`, signal `if request.running_event: request.running_event.set()` strictly inside `async with request.semaphore_cm:` immediately before dispatching `self._executor.execute_structured_task` per `ki_execution_engine_protocol.md`.</action>
    </step>
  </phase>

  <phase id="3" name="PROMPT_AND_TDA_ENGINE_HARMONIZATION">
    <step id="3.1" name="HARMONIZE_PROMPT_ENGINE">
      <action>In `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L74]`, import `override` from `typing` and decorate `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:` with `@override`.</action>
      <action>In `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L18-L74]`, relocate `if request.running_event: request.running_event.set()` strictly inside `async with request.semaphore_cm:` immediately before `self.task_executor.execute_structured_task` to comply with `ki_execution_engine_protocol.md`.</action>
    </step>
    <step id="3.2" name="HARMONIZE_TDA_ENGINE">
      <action>In `@[backend_v2/services/orchestrator/engines/tda_engine.py#L38-L270]`, import `override` from `typing` and decorate `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:` with `@override`.</action>
    </step>
  </phase>

  <phase id="4" name="TEST_EXPANSION_AND_ISTQB_PARTITIONS">
    <step id="4.1" name="ADD_SYNTHESIS_ENGINE_PROTOCOL_TESTS">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base` and `ErrorCodes` from `backend_v2.exceptions`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, add `test_synthesis_engine_implements_protocol()` asserting `issubclass(SynthesisEngine, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, add `test_synthesis_engine_signals_running_event()` asserting `running_event.is_set()` is True after execution with a provided `running_event`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, add `test_synthesis_engine_null_concurrency_guards()` asserting execution succeeds without error when `semaphore=None` and `running_event=None` to mathematically verify `request.semaphore_cm` nullcontext wrapping.</action>
    </step>
    <step id="4.2" name="ADD_PROMPT_ENGINE_PROTOCOL_TESTS">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]`, import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]`, add `test_prompt_engine_implements_protocol()` asserting `issubclass(PromptEngine, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`.</action>
    </step>
    <step id="4.3" name="ADD_TDA_ENGINE_PROTOCOL_TESTS">
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]`, import `ExecutionEngine` from `backend_v2.services.orchestrator.engines.base`.</action>
      <action>In `@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]`, add `test_tda_engine_implements_protocol()` asserting `issubclass(TDAEngine, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`.</action>
    </step>
  </phase>

  <phase id="5" name="UNIVERSAL_QUALITY_GATE_VERIFICATION">
    <step id="5.1" name="RUN_BACKEND_AUDIT_LOOP">
      <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/synthesis_engine.py backend_v2/services/orchestrator/engines/prompt_engine.py backend_v2/services/orchestrator/engines/tda_engine.py --test` to verify Ruff formatting, MyPy strict typecheck, AST guardrails, and Pytest coverage across all three engines.</action>
      <action>Execute `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Synthesis_Engine_Protocol_Inheritance.md` to verify markdown boundaries and table-protocol parity.</action>
    </step>
  </phase>

  <phase id="6" name="KNOWLEDGE_BASE_AND_ARCHITECTURE_SYNCHRONIZATION">
    <step id="6.1" name="UPDATE_KNOWLEDGE_ITEM_PROTOCOL">
      <action>In `@[ki_execution_engine_protocol.md]`, update and complement the invariant specifications to explicitly require and enforce the standardized 7-point invariant across all execution engines, specifically and exhaustively: `TDAEngine`, `PromptEngine`, `SynthesisEngine`, and all future engine implementations.</action>
    </step>
    <step id="6.2" name="EXECUTE_TIER7_ARCHITECTURE_DESCRIPTION">
      <action>Execute `/tier7-describe-architecture @[docs/architecture/03_cognitive_orchestration_engine.md]` to synchronize As-Built architectural documentation for Section 2.14, formalizing that every execution engine (`TDAEngine`, `PromptEngine`, `SynthesisEngine`, and future engine additions) uniformly implements `ExecutionEngine(Protocol)`, adheres to PEP 698 `@override`, executes atomic telemetry signaling inside `async with request.semaphore_cm:`, and maintains strict statelessness.</action>
    </step>
  </phase>
</execution_protocol>

---

## 5. Falsification & Red-Teaming Matrix

| Risk ID | Hypothesized Failure Mode | Likelihood | Impact | Architectural Countermeasure & Falsification Anchor |
| :--- | :--- | :--- | :--- | :--- |
| **RISK-01** | `execute()` signature diverges from `ExecutionEngine.execute()` Protocol definition causing MyPy strict error under `@override`. | Low | High | Signature parity verified: both require `(self, request: EngineExecutionRequest) -> EngineExecutionResult`. Verified by MyPy strict in `backend_audit_loop.py` across all three engines. |
| **RISK-02** | `running_event.set()` called prematurely outside the acquired semaphore lock, misreporting queued state as active running state. | Medium | High | Explicit mandate: `if request.running_event: request.running_event.set()` MUST reside strictly inside `async with request.semaphore_cm:`. Verified by `test_synthesis_engine_signals_running_event` and `test_prompt_engine.py`. |
| **RISK-03** | Test assertion `.get("error_code")` silently passes with `None` if error dictionary structure changes. | Low | Medium | Pre-implementation cleanup replaces `.get("error_code")` across all 3 test functions with direct subscript `details["error_code"]`, enforcing Fail-Fast `KeyError` if schema deviates. |
| **RISK-04** | Runtime `issubclass(Engine, ExecutionEngine)` fails if `ExecutionEngine` is not `@runtime_checkable` or not a direct base. | Low | Critical | `ExecutionEngine` is decorated with `@runtime_checkable` in `base.py`, and all three engines explicitly declare `class Engine(ExecutionEngine):`. Verified by protocol tests in all three test files. |
| **RISK-05** | Null concurrency limiters crash with `AttributeError` when `semaphore=None` or `running_event=None`. | Low | High | `request.semaphore_cm` natively wraps null semaphores in `contextlib.nullcontext()`, and `running_event` is guarded by an explicit null check before calling `.set()`. Verified by `test_synthesis_engine_null_concurrency_guards`. |
| **RISK-06** | `make_atom` helper returning `DraftExtractedAtom` causes runtime deserialization error if test fixture relies on dict semantics. | Low | Low | `GlobalAtomBlackboard` accepts `dict[str, DraftAtomList]` where `DraftAtomList.atoms` is `list[DraftExtractedAtom]`. Pydantic natively accepts typed model instances in place of dicts. Verified by 100% pass of existing 13 test cases under `DraftExtractedAtom`. |
| **RISK-07** | `isinstance(..., Mapping)` duck-typing in `tda_engine.py#L94` triggers AST guardrail `QGR012`. | Low | Low | Advisory AST warning `QGR012` is isolated to pre-flight circuit-breaker fallback in `tda_engine.py`. Domain execution path uses typed `ContextVariablesDTO`. Recorded as technical debt for subsequent model consolidation without expanding active plan scope boundary. |

---

## 6. Mathematical Quality Gates & Verification

Following implementation, Quorum's mandatory backend audit is executed across the entire engine triad:

```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/synthesis_engine.py backend_v2/services/orchestrator/engines/prompt_engine.py backend_v2/services/orchestrator/engines/tda_engine.py --test
```

### Acceptance Criteria:
1. `issubclass(SynthesisEngine, ExecutionEngine)` returns `True` and `isinstance(synthesis_engine, ExecutionEngine)` returns `True`.
2. `issubclass(PromptEngine, ExecutionEngine)` returns `True` and `isinstance(prompt_engine, ExecutionEngine)` returns `True`.
3. `issubclass(TDAEngine, ExecutionEngine)` returns `True` and `isinstance(tda_engine, ExecutionEngine)` returns `True`.
4. MyPy strict validates `@override` decorators and method signatures across all three engines with 100% type safety.
5. Unit tests in `test_synthesis_engine.py` (16 tests), `test_prompt_engine.py` (6 tests), and `test_tda_engine.py` (10 tests) pass 100% (total 32/32 tests passing, branch coverage >= 90%).
6. `audit_markdown_boundaries.py` validates the plan with 0 errors (MBD001-MBD009).

---

## 7. Knowledge Item (KI) & Architectural Documentation Synchronization Instructions

### 7.1. Unified ExecutionEngine SSOT Invariant Contract
All existing execution engines (specifically and exhaustively: `TDAEngine`, `PromptEngine`, `SynthesisEngine`) and all future engine implementations MUST strictly adhere to the following unified architectural contract:

1. **Explicit Protocol Inheritance (Zero Duck-Typing):**
   - Every engine MUST inherit directly from the centralized protocol: `class EngineName(ExecutionEngine):` (`@[backend_v2/services/orchestrator/engines/base.py#L11-L31]`). Implicit duck-typing or docstring-only references without class-level inheritance are strictly prohibited.
   - Classes MUST satisfy `issubclass(EngineName, ExecutionEngine)` and `isinstance(engine, ExecutionEngine)`.

2. **PEP 698 `@override` Method Contract:**
   - The engine execution method MUST strictly follow:
     ```python
     @override
     async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
         ...
     ```
   - MyPy strict type checking MUST verify 100% signature parity for method name, arguments, and return types without variance.

3. **Atomic Telemetry Signaling Inside Semaphore Lock (`atomic_telemetry_signaling_mandate`):**
   - Telemetry status signaling via `if request.running_event: request.running_event.set()` MUST occur atomically **inside** the acquired semaphore lock (`async with request.semaphore_cm:`), immediately before launching the physical LLM or sensor task.
   - Signaling prior to acquiring the semaphore or outside the lock context is strictly prohibited to prevent tasks from reporting `ExecutionStatus.RUNNING` in persistence stores or SSE streams while waiting in asyncio concurrency queues.

4. **Bi-Directional Concurrency Null-Safety (`nullcontext`):**
   - Engines MUST manage semaphores exclusively via the DTO context manager: `async with request.semaphore_cm:`. This guarantees that if `semaphore=None` (in unconstrained execution or unit tests), execution does not fail with `AttributeError` but is safely wrapped in `contextlib.nullcontext()`.
   - `request.running_event` MUST be guarded by an explicit null check `if request.running_event:` prior to invoking `.set()`.

5. **100% Inter-Invocation Statelessness (`stateless_engine_immutability_mandate`):**
   - Engine instances MUST remain completely stateless. No run-specific execution state, tenant context, or dynamic caches may be retained on instance attributes (`self`). All required execution state is passed exclusively via the `request: EngineExecutionRequest` parameter.

6. **Anti-Corruption Layer (ACL) and RFC 7807 Dual-Reporting (`engine_exception_acl`):**
   - Engines MUST encapsulate execution errors so that raw internal exceptions (validation errors, provider network failures) do not leak unhandled to the orchestrator. Errors MUST be mapped to appropriate `AppException` instances and logged via structured `logger.error` including Trace IDs.

7. **Zero Permissive Typing and DTO Integrity:**
   - Engines ingest strictly `EngineExecutionRequest` and return `EngineExecutionResult` (`ConfigDict(strict=True, extra="forbid", frozen=True)`). Using raw dictionaries (`dict[str, Any]`) or `**kwargs` parameters in engine boundaries is strictly prohibited.

8. **Tripartite Pipeline Phase Isolation and Orthogonal Strategy Decoupling (`ki_tripartite_pipeline_architecture.md`):**
   - Execution engines (`TDAEngine`, `PromptEngine`, `SynthesisEngine`) operate as pure computational engines (`ExecutionEngine`), orthogonally decoupled from FinOps model tiers (`model_strategy`: `"fast"`, `"reasoning"`, `"deep"`).
   - Engines adhere strictly to tripartite phase boundaries: they contain zero Dumb Painter SDUI layout assembly or visual presentation math (which belong exclusively to Phase 3).
   - Inter-boundary communication occurs exclusively via immutable, strongly typed DTO envelopes (`EngineExecutionRequest`, `EngineExecutionResult`) with zero naked dictionaries and zero deprecated `v2_core.py` imports.

---

### 7.2. Knowledge Item Synchronization (`ki_execution_engine_protocol.md`)
Following implementation, `@[ki_execution_engine_protocol.md]` is updated as follows:
- Extend the `atomic_telemetry_signaling_mandate` to explicitly govern all three execution engines (`TDAEngine`, `PromptEngine`, `SynthesisEngine`) and future engine additions, forbidding telemetry signaling outside the semaphore lock.
- Mandate PEP 698 `@override` annotations and explicit `ExecutionEngine` protocol inheritance (`class Engine(ExecutionEngine):`).
- Document that `SynthesisEngine` implements full protocol inheritance and atomic telemetry signaling, achieving complete engine layer parity.

---

### 7.3. As-Built Architecture Synchronization (`/tier7-describe-architecture`)
Following implementation, As-Built documentation is synchronized via:

```bash
/tier7-describe-architecture docs/architecture/03_cognitive_orchestration_engine.md
```

#### Synchronization Scope & Mandates:
- **Target:** `@[docs/architecture/03_cognitive_orchestration_engine.md]` Section `2.14. ExecutionEngine Protocol & Strategy Dispatch`.
- **Timeless As-Built Narration:** Section documents current state in pure present tense without project history, phase numbers, or artificial Law labels:
  - All execution engines (`TDAEngine`, `PromptEngine`, `SynthesisEngine`, and future additions) implement `ExecutionEngine(Protocol)`.
  - All engines use PEP 698 `@override` annotations and execute telemetry signaling (`running_event.set()`) atomically within the acquired semaphore lock.
  - Engine input and output interfaces are 100% strongly typed DTO contracts (`EngineExecutionRequest` / `EngineExecutionResult`) with comprehensive concurrency null-safety.
