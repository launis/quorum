# EPIC 150 AUDIT REPORT: Zero Permissive Typing Lockdown

## Executive Summary
This document serves as the formal System 2 Red-Team Audit Report for **Epic 150: Zero Permissive Typing Lockdown** (`@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md]`).

- **Audit Date**: 2026-08-31
- **Audit Role**: Principal Enterprise Architect & System Red Team
- **Target Epic**: `@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md]`
- **Boundary Verification Status**: PASSED (`scripts/audit_markdown_boundaries.py` returned code 0).
- **Mathematical Scope Verified**:
  - `dict[str, Any]` in non-test production code: **516** total.
  - Multi-Category Persistence Boundary Exemptions: exactly **102** across 6 files (`interfaces.py`, `wrapper.py`, `driver.py`, `tinydb_driver.py`, `firestore_driver.py`, `exceptions.py`).
  - Actionable `dict[str, Any]` target count: **414**.
  - `isinstance(..., dict)` checks in non-test code: **152**.
  - `# noqa: QGR` inline suppressions in non-test code: **130**.
  - Test fixture raw dict messages (`{"role": ...}`): **187**.
  - Test fixture dictionary subscript assertions: **103** lines.

---

## 1. Five-Axis System 2 Deconstruction

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **LLM Prompt & Response Core**:<br>`@[backend_v2/models/prompt.py]`<br>`@[backend_v2/models/llm.py]`<br>`@[backend_v2/llm/provider.py]`<br>`@[backend_v2/llm/adapters/]` | Eliminates `list[dict[str, Any]]` message structures, `.get("role")` fallbacks, and LiteLLM response object attribute reflection (`getattr`/`hasattr`). | Strict `LLMMessageDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)`, `PromptMetadataDTO`, and `ProviderMetadataDTO`. `.model_dump()` executed exclusively at LiteLLM boundary. | Avoided creating separate adapter-specific prompt wrappers. Reused SSOT `OpenAIToolCallDTO` from `@[backend_v2/models/domain/mcp.py]`. | Negative boundary partition unit tests in `test_prompt.py` (missing fields, extra fields, type strictness). `backend_audit_loop.py` on `llm/`. |
| **Service & Studio Simulation**:<br>`@[backend_v2/services/studio/simulation_service.py]`<br>`@[backend_v2/api/routers/studio/]`<br>`@[backend_v2/services/progress.py]`<br>`@[backend_v2/core/registry.py]` | Eliminates `dict[str, Any]` return signatures, `mock_inputs: dict[str, Any]`, and untyped `ProgressState.result/details`. | Direct instantiation of existing SSOT models: `WorkflowSimulationResponse`, `StepSimulationResponse`, `PromptBlockSimulationResponse` (`@[backend_v2/models/dtos/studio.py]`), and `TaskMetadataDTO`. | **Complexity Slayer**: Rejected speculative `SimulationResultDTO` generic blob and rejected crossing CQRS boundaries with `ExecutionRecord`. | Verified direct DTO instance attribute assertions in `test_simulation_service.py` and `test_progress.py`. |
| **Worker & Telemetry**:<br>`@[backend_v2/worker.py#L250-L290]`<br>`@[backend_v2/models/domain/metadata.py]` | Eliminates 8 `QGR003` broad except suppressions, untyped `TypeAdapter(dict[str, Any])` chaining, and chained `.get()` fallback lookups on telemetry. | Direct hydration of `TraceEventMetadataEnvelope` (`@[backend_v2/models/dtos/trace.py]`) containing typed `StepMetadataDTO` and `TokenUsage`. RFC-7807 structured logging on DLQ handlers. | Preserved worker monolithic structure under `data_and_file_preservation_mandate` (acknowledged God File debt) while surgically fixing typing and QGRs. | Regression test `test_worker_synthesis.py` and `test_finops_telemetry.py`. |
| **Hooks & Orchestration**:<br>`@[backend_v2/hooks/]` (17 files)<br>`@[backend_v2/services/orchestrator/]` (19 files) | Eliminates 130 `# noqa: QGR` suppressions and 152 `isinstance(..., dict)` checks. Ban on silent fallback `pass` in scoring and DAG execution. | 3-Tiered Anti-Duck-Typing Protocol: (1) Direct DTO attribute access, (2) Guarded `TypeAdapter` hydration with `AppException(VALIDATION_FAILED, 422)`, (3) Discriminated Union / Category pre-filtering. | Avoided double-validation loops; state flowing through DAG already validated by `ExecutionInputsDTO` / `GlobalContextVarsDTO`. | AST scan `scripts/_ast_guardrails.py backend_v2/hooks/ backend_v2/services/orchestrator/ --strict`. |
| **AST Guardrail Engine**:<br>`@[scripts/_ast_guardrails.py]`<br>`@[scripts/backend_audit_loop.py]` | Eliminates tolerance for `WARNING` severity on reflection and duck-typing in non-exempt files. | `QGR001`, `QGR002`, `QGR012` set to universal `FATAL` severity with explicit Multi-Category Exemption Set (`interfaces.py`, `wrapper.py`, `driver.py`, `tinydb_driver.py`, `firestore_driver.py`, `exceptions.py`, `logging_config.py`). | Simple path/filename set lookup in visitor without reflection. | Deterministic invariant one-liners returning exactly 0 violations for QGR suppressions and un-exempt duck-typing. |

---

## 2. Red-Team Falsification & Critical Risk Vectors

### Vector 1: The "Immediate Wall of Red" Test Suite Cascade
- **Attack Scenario**: If `CompiledPrompt.to_flat_messages()` or `to_static_flat()` are changed to return `list[LLMMessageDTO]` while test suites and adapter callers still expect `list[dict[str, Any]]` or use `flat[0]["role"]`, 32 test files will fail instantly, creating an un-debuggable test cascade.
- **Countermeasure & Proof Anchor**: Phase 0 **Atomic Pre-Hardening**. `LLMMessageDTO` and centralized test factories (`make_llm_message()`) are established in Phase 0. All 187 test fixture dictionaries and 103 subscript assertion lines are converted to dot-notation attributes in Phase 0 *before* production code in Phase 1 is modified.

### Vector 2: Unhandled `ValidationError` Ingress 500 Crashing
- **Attack Scenario**: Converting untrusted ingress `isinstance(payload, dict)` checks to direct Pydantic hydration could cause uncaught `pydantic.ValidationError` to bubble to FastAPI's generic 500 Internal Server Error handler, violating RFC-7807 compliance.
- **Countermeasure & Proof Anchor**: Phase 3 mandates the Guarded Hydration Pattern: every ingress boundary validating untrusted JSON payloads wraps validation in `try/except ValidationError as e:` and translates to `AppException(message=f"Validation failed: {format_validation_error(e)}", status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})` with structured `logger.error`.

### Vector 3: Polymorphic DAG Heterogeneous Payload Corruption
- **Attack Scenario**: Calling monomorphic `TypeAdapter(SingleModel).validate_python(event.content)` on heterogeneous DAG output payloads (`StepOutputDTO.payload`, which can be `list[AtomResultDTO]`, `str`, `int`, `dict`, or SDUI blocks) will crash downstream hooks like `SynthesisPayloadCompressor`.
- **Countermeasure & Proof Anchor**: Phase 3 explicitly enforces category pre-filtering (`if block.category_id == PromptBlockCategory.MATRIX:`) before hydrating specific schemas, OR utilizes Discriminated Union TypeAdapters per `polymorphic_dag_payload_handling`.

---

## 3. Scope & Quantitative Verification Summary

| Metric | Target Baseline | Exemptions | Actionable Scope | Target Invariant |
| :--- | :--- | :--- | :--- | :--- |
| `dict[str, Any]` | 516 | 102 (persistence/driver/exceptions) | 414 | 0 in domain/service code |
| `isinstance(..., dict)` | 152 | 1 (FastAPI execution router) | 151 | 0 in domain/service code |
| `# noqa: QGR` | 130 | 0 | 130 | 0 codebase-wide |
| `hasattr`/`getattr` | 77 | 18 (logging & LiteLLM provider) | 59 | 0 in domain/service code |
| Raw Dict Test Fixtures | 187 | 0 | 187 | 0 in test suites |
| Subscript Assertions | 103 | 0 | 103 | 0 in test suites |

---

## 4. Architectural Recommendation & Sign-Off

The Epic document `@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md]` has undergone rigorous System 2 deconstruction, boundary audit, and anti-happy-path red-teaming. It is **APPROVED** and ready for decomposition via `/tier1-planner`.
