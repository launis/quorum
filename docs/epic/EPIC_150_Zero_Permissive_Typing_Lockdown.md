<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

# EPIC 150: Zero Permissive Typing Lockdown

---

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective

Achieve **absolute mathematical zero** permissive typing patterns across the entire Quorum backend codebase. This Epic eliminates all remaining `dict[str, Any]` annotations in service/domain transit, eradicates `isinstance(..., dict)` duck-typing, removes all `# noqa: QGR` inline suppressions, and hardens AST guardrails to `FATAL` severity with explicit boundary exemptions — creating a closed-loop prevention ecosystem where permissive typing patterns are structurally impossible to introduce.

### Problem Statement

Epic 149 (`@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]`) successfully established the Pydantic V2 foundation across 7 phases: typed repositories, DTOs, hook registries, orchestration strategies, service layers, typed cache boundaries, and initial AST guardrail hardening. However, a deterministic codebase-wide scan (2026-08-31) reveals **significant residual violations** that Epic 149's scope did not fully address:

| Violation Type | Total Count | Target Origin |
| :--- | :--- | :--- |
| `dict[str, Any]` type annotations (non-test production files) | **516** | Models, LLM adapters, services, hooks, worker, database, utils |
| `isinstance(..., dict)` duck-typing checks | **152** | Hooks, services, repositories, LLM provider, models |
| `# noqa: QGR` inline suppressions | **130** | All domains (QGR001 reflection, QGR002 .get(), QGR003 broad except, QGR007 ConfigDict, QGR012 isinstance) |
| Unsuppressed `hasattr`/`getattr` reflection calls | **77** | LLM client/provider, logging, registry, database drivers, worker |
| Raw dict message fixtures in test files (`{"role": ...}`) | **187** | 20 test files across `backend_v2/tests/` |
| Dict subscript assertions in test files (`[n]["role"]`, `[n]["content"]`) | **103** | 16 test files across `backend_v2/tests/` |

### Boundary Exemption Classification

Not all 516 `dict[str, Any]` annotations or reflection calls are domain violations. The `no_naked_dicts_in_state` rule in `@[.agents/rules/00-antigravity-core.md]` explicitly permits `dict` at "absolute external persistence and network boundaries." To prevent category conflation, this Epic establishes a **formal, mathematically verified Multi-Category Exemption Register**:

#### 1. `dict[str, Any]` Type Annotation Exemptions (Persistence & Driver Boundaries — 102 total):

| File | Count | Exemption Rationale |
| :--- | :--- | :--- |
| `@[backend_v2/database/interfaces.py]` | 55 | Protocol definitions for raw DB driver operations |
| `@[backend_v2/database/wrapper.py]` | 19 | Internal DB abstraction layer |
| `@[backend_v2/exceptions.py]` | 13 | RFC-7807 problem detail formatting infrastructure |
| `@[backend_v2/database/tinydb_driver.py]` | 6 | TinyDB internal persistence implementation |
| `@[backend_v2/database/firestore_driver.py]` | 5 | Firestore internal persistence implementation |
| `@[backend_v2/database/driver.py]` | 4 | Abstract driver protocol |
| **TOTAL EXEMPT ANNOTATIONS** | **102** | **Zero dict leakage past repository reconstitution boundary** |

**Effective ACTIONABLE `dict[str, Any]` scope**: 516 − 102 = **414 actionable violations** across production files.

#### 2. Reflection (`hasattr`/`getattr`) Boundary Exemptions:

| File | Count | Exemption Rationale |
| :--- | :--- | :--- |
| `@[backend_v2/logging_config.py]` | 12 | Python stdlib `LogRecord` attribute access and terminal stream reconfiguration |
| `@[backend_v2/llm/provider.py]` | ~6 | Third-party LiteLLM SDK response payload attribute probing (`_hidden_params`, `model_extra`, `status_code`) |

#### 3. Duck-Typing (`isinstance`) Boundary Exemptions:

| File | Count | Exemption Rationale |
| :--- | :--- | :--- |
| `@[backend_v2/api/routers/execution/executions.py]` | 1 | FastAPI HTTP transport serialization boundary (`isinstance(content, (dict, list))`) |

#### 4. Static Settings & Configuration Registry Classification:

| File | Count | Exemption Rationale |
| :--- | :--- | :--- |
| `@[backend_v2/settings.py]` | 2 | Static model strategies dictionary and JSON schema definition loader |

### Strategic Scope

This Epic enforces the **Surgical Eradication** pattern: each phase targets a specific architectural layer, eliminates all violations within that layer, runs the quality gate, and commits atomically before proceeding. Unlike Epic 149 (which built foundational DTOs), this Epic is purely **destructive** — it removes anti-patterns, eliminates suppressions, and locks the AST guardrails.

### Dependency

- **Depends on**: `@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]` (all 7 phases COMPLETED, all post-implementation hardening gates COMPLETED).

### Zero-Fallback & Zero-Legacy Compatibility Mandate

No fallback features, backward compatibility shims, or support for historical execution runs may be implemented during this Epic. Specifically and exhaustively:

1. **No `Union[NewModel, dict]` transitional types**: Every refactored field MUST accept ONLY the new typed model. Temporary unions with `dict` are STRICTLY FORBIDDEN.
2. **No `.get(key, default)` fallback chains**: If a required field is missing, the system MUST crash via `AppException` with RFC-7807 structured logging. Silent defaults are PROHIBITED.
3. **No `try/except` dictionary coercion**: Catching `KeyError`, `TypeError`, or `ValidationError` to silently fall back to raw dictionary access is PROHIBITED.
4. **No historical run migration**: Old execution records stored in the database that do not conform to the new strict schemas are permanently abandoned. Clean-slate re-seeding (`uv run python backend_v2/seed/run_seed.py local`) is the ONLY supported recovery path.
5. **No conditional type branching**: Code paths containing `if isinstance(data, dict): ... elif isinstance(data, SomeModel): ...` that maintain parallel dict/model processing are PROHIBITED. All data MUST flow through a single typed pathway.
6. **No `hasattr`/`getattr` discovery**: Runtime attribute probing to determine whether an object is a dict or a model is PROHIBITED. Type identity MUST be known statically at every callsite.

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)

| Symbol / Pattern | Current Location | Disposition |
| :--- | :--- | :--- |
| `list[dict[str, Any]]` on `CompiledPrompt.static_messages` | `@[backend_v2/models/prompt.py]` | REPLACED by `[NEW]` created `list[LLMMessageDTO]` |
| `list[dict[str, Any]]` on `CompiledPrompt.dynamic_messages` | `@[backend_v2/models/prompt.py]` | REPLACED by `[NEW]` created `list[LLMMessageDTO]` |
| `dict[str, Any]` on `CompiledPrompt.metadata` | `@[backend_v2/models/prompt.py]` | REPLACED by `[NEW]` defined `PromptMetadataDTO` (fields: `token_proxy_score: float \| None`, `cache_key: str \| None`, `routing_tags: list[str] \| None`) |
| `list[dict[str, Any]]` return type on `to_flat_messages()`, `to_static_flat()`, `to_dynamic_flat()` | `@[backend_v2/models/prompt.py]` | REPLACED by `[NEW]` created `list[LLMMessageDTO]` (adapters call `.model_dump()` exclusively at LiteLLM boundary) |
| `.get("role")`, `.get("content")` fallbacks in `_merge_flat` | `@[backend_v2/models/prompt.py]` | REPLACED by direct `msg.role`, `msg.content` attribute access |
| `list[dict[str, Any]]` on `LLMResponse.messages` | `@[backend_v2/models/llm.py]` | REPLACED by `[NEW]` created `list[LLMMessageDTO] \| None` |
| `list[dict[str, Any]]` on `LLMResponse.tool_calls` | `@[backend_v2/models/llm.py]` | REPLACED by `list[OpenAIToolCallDTO] \| None` (SSOT from `@[backend_v2/models/domain/mcp.py]`) |
| `provider_metadata: dict[str, Any]` on `LLMResponse` | `@[backend_v2/models/llm.py]` | REPLACED by `[NEW]` defined `ProviderMetadataDTO` (fields: `finish_reason: str \| None`, `model_extra: dict[str, Any] \| None` mapped at LiteLLM boundary) |
| Raw dict message literals `{"role": ..., "content": ...}` in test fixtures (~187 lines) | 20 test files across `backend_v2/tests/` | REPLACED by `[NEW]` created `LLMMessageDTO` instances / `make_llm_message()` in Phase 0 |
| Dict subscript assertions `flat[n]["role"]`, `flat[n]["content"]` (~103 lines) | 16 test files across `backend_v2/tests/` | REPLACED by dot-notation `flat[n].role`, `flat[n].content` in Phase 0 |
| `metadata: dict[str, Any] \| None` on `TaskDefinition` | `@[backend_v2/core/registry.py#L52]` | REPLACED by `[NEW]` defined `TaskMetadataDTO \| None` |
| `result: dict[str, Any] \| None` on `ProgressState` | `@[backend_v2/services/progress.py#L34]` | REPLACED by typed optional fields |
| `details: dict[str, Any] \| None` on `ProgressState` | `@[backend_v2/services/progress.py#L35]` | REPLACED by typed optional fields |
| `details: dict[str, Any] \| None` params on `ProgressTracker` ABC | `@[backend_v2/services/progress.py]` | REPLACED by typed `ProgressState` |
| All 130 `# noqa: QGR` inline suppressions | 30+ files across `backend_v2/` | INTENTIONALLY DROPPED (zero remaining) |
| All 152 `isinstance(..., dict)` checks in non-exempt files | Hooks, services, orchestrator, repositories | REPLACED by: (1) Direct DTO attribute access, (2) Guarded `TypeAdapter(Model).validate_python()` with `try/except ValidationError -> AppException(VALIDATION_FAILED)` conversion, or (3) Discriminated Union / category pre-filtering for polymorphic DAG state |
| All unsuppressed `hasattr`/`getattr` in non-exempt files | LLM client/provider, registry, database drivers | REPLACED by typed attribute access or explicit Protocol methods |

### Retained SSOT Invariants (What We Will RETAIN)

| Invariant | Anchor |
| :--- | :--- |
| All Pydantic V2 DTOs with `ConfigDict(strict=True, extra="forbid")` | `@[.agents/rules/01-python-backend.md]` |
| `ExecutionInputsDTO`, `GlobalContextVarsDTO`, `HookDeltaDTO` | `@[backend_v2/models/dtos/hook_state.py]` — already typed in Epic 149 Phase 3B |
| Repository reconstitution returning typed Domain models | `@[backend_v2/database/repositories/]` — already typed in Epic 149 Phase 2 |
| `TypedCacheService` with zombie cache auto-eviction | `@[backend_v2/services/cache/typed_cache.py]` — already typed in Epic 149 Phase 6 |
| Database driver/interface persistence boundary exemptions | `@[backend_v2/database/interfaces.py]`, `@[backend_v2/database/wrapper.py]` — EXEMPT |
| Logging infrastructure stdlib exemptions | `@[backend_v2/logging_config.py]` — EXEMPT |

### Compliance & Modernity Gates

1. **Zero Legacy State Support Mandate**: No backward compatibility. Clean slate DB re-seeding (`uv run python backend_v2/seed/run_seed.py local`).
2. **Pydantic V2 Strictness**: `ConfigDict(strict=True, extra="forbid")` on ALL `[NEW]` created DTOs (`LLMMessageDTO`, `PromptMetadataDTO`, `ProviderMetadataDTO`, `TaskMetadataDTO`). Reject generic `SimulationResultDTO` and reject reusing `ExecutionRecord` for Studio simulations — use existing SSOT models (`WorkflowSimulationResponse`, `StepSimulationResponse`, `PromptBlockSimulationResponse` from `models/dtos/studio.py`).
3. **Zero Suppressions Policy**: Zero `# noqa: QGR` inline suppressions allowed in production code after completion.
4. **AST Guardrail FATAL Enforcement**: `QGR001` (reflection), `QGR002` (.get fallbacks), `QGR012` (isinstance dict) at `FATAL` severity for ALL non-test, non-exempt files.
5. **RFC-7807 Dual-Reporting & Guarded Hydration**: All DLQ exception handlers and domain validation conversion points MUST include structured `logger.error` with `ErrorCodes`. Raw Pydantic `ValidationError` MUST NOT bubble unhandled to FastAPI's generic 500 handler; domain boundaries hydrating untrusted state MUST encapsulate validation in `AppException(ErrorCodes.VALIDATION_FAILED, status_code=422)` with `format_validation_error()`. The `details` dictionary inside `AppException` is architecturally exempt (defined in `exceptions.py`).
6. **Polymorphic DAG Safety**: Heterogeneous DAG states (`StepOutputDTO.payload`, `SynthesisPayloadCompressor`) MUST NOT be validated against monomorphic models without category pre-filtering (`block.category_id`) or Discriminated Union TypeAdapters.
7. **God Code Prevention**: No DTO file exceeds 200 LOC. New DTOs co-located with primary consumer.
8. **Zero Test Fixture Strictness Bypass**: No raw dicts in test suites. Test fixtures must construct 100% typed DTO models natively.

### Producer-Consumer Integration Check

| Producer | Consumer | Contract |
| :--- | :--- | :--- |
| `[NEW]` created `LLMMessageDTO` (defined in Phase 0, `@[backend_v2/models/llm.py]`) | `CompiledPrompt`, all 5 LLM adapters, 32 test suites, `caching_service.py`, `prompt_compiler.py`, `prompt_factory.py` | `.model_dump()` ONLY at LiteLLM SDK boundary |
| `[NEW]` created `PromptMetadataDTO` (defined in Phase 1, `@[backend_v2/models/prompt.py]`) | `CompiledPrompt`, `caching_service.py` | Typed attributes, no raw dicts |
| `[NEW]` created `ProviderMetadataDTO` (defined in Phase 1, `@[backend_v2/models/llm.py]`) | `LLMResponse`, `provider.py` | Typed attributes |
| `[NEW]` created `TaskMetadataDTO` (defined in Phase 2, `@[backend_v2/core/registry.py]`) | `TaskRegistry`, `worker.py` job dispatch | Direct attribute access, no `.get()` |
| `ProgressState` (refined, `@[backend_v2/services/progress.py]`) | `DatabaseProgressTracker`, `InMemoryProgressTracker`, `worker.py` | Typed fields, `.model_dump()` at SSE JSON boundary only |
| `WorkflowSimulationResponse`, `StepSimulationResponse`, `PromptBlockSimulationResponse` (`@[backend_v2/models/dtos/studio.py]`) | `StudioSimulationService`, Studio Routers (`workflows.py`, `steps.py`, `prompt_blocks.py`), Flutter Studio UI | Strongly typed service return types without raw `dict[str, Any]` |
| AST Guardrail boundary exemptions | `@[scripts/_ast_guardrails.py]` | Explicit path-based exemption set |

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 0: Test Fixture & JSON Data Atomic Pre-Hardening (~35 files, 1 session)

**Objective**: Establish `[NEW]` `LLMMessageDTO` foundation, create centralized test message factories in `conftest.py`, migrate all ~187 raw dict test fixtures to typed models, and convert ~103 dictionary subscript assertions (`flat[n]["role"]`) to dot-notation attribute access (`flat[n].role`). This pre-emptively eradicates the "Immediate Wall of Red" before production strictness is applied.

**Target Files:**
1. **Foundation Model**:
   - `@[backend_v2/models/llm.py]` — Define `[NEW]` immutable `LLMMessageDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)`, fields: `role: str`, `content: str`, `tool_calls: list[OpenAIToolCallDTO] | None = None` (reusing SSOT from `@[backend_v2/models/domain/mcp.py]`), `tool_call_id: str | None = None`, `name: str | None = None`.
2. **Centralized Test Factories**:
   - `@[backend_v2/tests/conftest.py]` — Add `make_llm_message(role: str, content: str, **kwargs) -> LLMMessageDTO` and `polyfactory` message providers.
3. **Static JSON Test Data & Fixtures**:
   - `@[backend_v2/tests/test_data/]` (`e2e_new_trace.json`, `exe_c0bc_inputs.json`, `report_data_dto_fixture.json`) — Validate against new DTO schemas; strip legacy untyped keys.
   - `@[backend_v2/tests/fixtures/sdui_golden_master.json]` — Verify semantic schema parity with strict DTO boundaries.
4. **Exhaustive Test Fixtures & Assertion Migration (20+ test files, ~187 raw dict lines, ~103 subscript assertion lines)**:
   - `@[backend_v2/tests/unit/models/test_prompt.py]` — Replace 10 raw dict constructor calls and 7 `flat[n]["role"]` assertions with `LLMMessageDTO` and `flat[n].role`.
   - `@[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]` — Migrate 38 raw dict fixtures and 1 assertion.
   - `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]` — Migrate 22 raw dict fixtures and 1 assertion.
   - `@[backend_v2/tests/unit/llm/adapters/test_anthropic_adapter.py]` — Migrate 12 raw dict fixtures and 19 `flat[n]["role"]` assertions to attribute access.
   - `@[backend_v2/tests/unit/llm/adapters/test_base_adapter.py]` — Migrate 5 raw dict fixtures.
   - `@[backend_v2/tests/unit/llm/adapters/test_deepseek_adapter.py]` — Migrate 3 raw dict fixtures.
   - `@[backend_v2/tests/unit/llm/adapters/test_mock_adapter.py]` — Migrate 3 raw dict fixtures.
   - `@[backend_v2/tests/unit/llm/adapters/test_openai_adapter.py]` — Migrate 3 raw dict fixtures.
   - `@[backend_v2/tests/test_vertex_adapter_caching_system_role.py]` — Migrate 2 raw dict fixtures.
   - `@[backend_v2/tests/unit/llm/test_client.py]` — Migrate 15 raw dict message calls.
   - `@[backend_v2/tests/unit/llm/test_caching_service.py]` — Migrate 4 raw dict message calls.
   - `@[backend_v2/tests/unit/llm/test_structured_retry.py]` — Migrate 2 raw dict fixtures.
   - `@[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]` — Migrate 15 `messages=` raw dict fixtures and 1 subscript assertion.
   - `@[backend_v2/tests/unit/services/mcp/test_tool_loop_sanitization.py]` — Migrate 9 raw dict fixtures and 2 subscript assertions.
   - `@[backend_v2/tests/unit/services/test_llm_task_executor.py]` & `@[backend_v2/tests/unit/test_llm_task_executor.py]` — Migrate 16 message fixtures and 22 assertion lines.
   - `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` & `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]` — Update 33 assertion lines.
   - `@[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler_adapter.py]` — Update 7 assertion lines.
   - `@[backend_v2/tests/unit/hooks/test_interaction_hook.py]` — Update 5 subscript assertions.
   - `@[backend_v2/tests/unit/services/test_chat_parser.py]` — Update 4 subscript assertions.
   - `@[backend_v2/tests/unit/hooks/test_input_processing.py]` — Migrate 2 raw dict fixtures.
   - `@[backend_v2/tests/unit/models/dtos/test_prompt_context.py]` — Migrate 2 raw dict fixtures and 1 subscript assertion.
   - `@[backend_v2/tests/unit/test_finops_telemetry.py]` — Migrate 3 raw dict fixtures.
   - `@[backend_v2/tests/integration/test_caching_integration.py]` — Migrate 7 raw dict fixtures and 2 subscript assertions.
   - `@[backend_v2/tests/unit/services/test_source_verification_service.py]` — Update 1 subscript assertion.
   - `@[backend_v2/tests/unit/test_progress.py]` & `@[backend_v2/tests/unit/core/test_registry.py]` — Pre-stage mock structures for upcoming `ProgressState` and `TaskMetadataDTO` transitions.

**Mandatory ISTQB Negative Boundary Partition Tests (for `LLMMessageDTO` in `test_prompt.py`):**
1. *Missing required field partition*: Instantiating `LLMMessageDTO(content="text")` without `role` MUST raise `pydantic.ValidationError`.
2. *Extra field rejection partition*: Instantiating `LLMMessageDTO(role="user", content="text", extra_field=123)` MUST raise `pydantic.ValidationError` via `extra="forbid"`.
3. *Type strictness partition*: Instantiating `LLMMessageDTO(role=123, content="text")` or `LLMMessageDTO(role="user", content=None)` MUST raise `pydantic.ValidationError` via `strict=True`.

**Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/test_prompt.py backend_v2/tests/unit/llm/ backend_v2/tests/unit/services/test_llm_task_executor.py --test`

---

### Phase 1: LLM Message DTO & Prompt Infrastructure (~10 files, 2-3 sessions)

**Objective**: Refactor the entire production LLM prompt compilation, adapter, and provider pipeline to eliminate all `list[dict[str, Any]]` message lists, define `[NEW]` `PromptMetadataDTO` and `ProviderMetadataDTO`, and resolve reflection on LiteLLM response objects. Lock `to_flat_messages()`, `to_static_flat()`, and `to_dynamic_flat()` to return `list[LLMMessageDTO]`.

**Target Files:**
- `@[backend_v2/models/prompt.py]` — Define `[NEW]` `PromptMetadataDTO(BaseModel)` with typed fields: `token_proxy_score: float | None = None`, `cache_key: str | None = None`, `routing_tags: list[str] | None = None`. Refactor `CompiledPrompt` to use `list[LLMMessageDTO]` for `static_messages`/`dynamic_messages` and `PromptMetadataDTO` for `metadata`. Update `_merge_flat`, `to_static_flat`, `to_dynamic_flat`, `to_flat_messages`, `_forbid_system_in_dynamic` to direct attribute access returning `list[LLMMessageDTO]`.
- `@[backend_v2/models/llm.py]` — Define `[NEW]` `ProviderMetadataDTO(BaseModel)` with typed fields (`finish_reason: str | None = None`, `model_extra: dict[str, Any] | None = None`). Refactor `LLMResponse` to replace `messages: list[dict[str, Any]] | None` with `list[LLMMessageDTO] | None`, `tool_calls: list[dict[str, Any]] | None` with `list[OpenAIToolCallDTO] | None` (from `@[backend_v2/models/domain/mcp.py]`), and `provider_metadata` with `ProviderMetadataDTO`.
- `@[backend_v2/llm/provider.py]` — Complete scope: eliminate 18 `dict[str, Any]` annotations, 12 `isinstance(dict)` checks, and all `model_dump` laundering. Explicitly isolate LiteLLM SDK response introspection (`_hidden_params`, `model_extra`, `status_code`) at the provider boundary using explicit SDK Protocol mapping.
- `@[backend_v2/llm/adapters/base_adapter.py]` — Eliminate 3 QGR002 suppressions and 4 `isinstance(dict)` checks. Convert `prepare_caching_payload` to accept `CompiledPrompt` and call `.model_dump()` strictly at the LiteLLM SDK boundary.
- `@[backend_v2/llm/adapters/ai_studio_adapter.py]` — Eliminate 2 QGR002 and 1 QGR003 suppressions. Narrow exception to `(ConnectionError, TimeoutError)`.
- `@[backend_v2/llm/adapters/vertex_adapter.py]` — Eliminate 2 QGR002 and 1 QGR003 suppressions.
- `@[backend_v2/llm/adapters/anthropic_adapter.py]` — Eliminate 1 `isinstance(dict)` check and 8 `dict[str, Any]` annotations.
- `@[backend_v2/llm/adapters/openai_adapter.py]` — Eliminate remaining QGR suppressions and 5 `dict[str, Any]` annotations.
- `@[backend_v2/llm/client.py]` — Eliminate 11 `dict[str, Any]` annotations and 6 `hasattr`/`getattr` on LiteLLM response objects via direct typed attribute access.
- `@[backend_v2/llm/ingress_pipeline.py]` — Eliminate 3 `isinstance(dict)` checks.
- `@[backend_v2/llm/mock.py]` — Eliminate 1 `isinstance(dict)` check.

**Pre-Implementation Cleanups:**
- `@[backend_v2/utils/math_utils.py]`: Add `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` to `StrictnessConfig`.
- `@[backend_v2/llm/caching_service.py]`: Update all consumers of `to_flat_messages()` to handle `LLMMessageDTO` return type.

**Critical Risk Mitigation (LiteLLM SDK Boundary)**:
All consumers of `CompiledPrompt.to_flat_messages()`, `to_static_flat()`, `to_dynamic_flat()` MUST be traced via `grep_search` before modification. Adapters call `[msg.model_dump() for msg in compiled.to_flat_messages()]` EXCLUSIVELY at the LiteLLM SDK invocation boundary.

**Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/llm/ backend_v2/models/prompt.py backend_v2/models/llm.py --test`

---

### Phase 2: Service & Studio Layer DTO Elimination (~22 files, 3-4 sessions)

**Objective**: Eliminate all `dict[str, Any]` annotations from the service layer, progress tracking, studio services, and worker telemetry. Refine existing `ProgressState` model and create `[NEW]` `TaskMetadataDTO`. For Studio simulation, refactor `StudioSimulationService` to directly instantiate and return existing SSOT response models (`WorkflowSimulationResponse`, `StepSimulationResponse`, `PromptBlockSimulationResponse`) — rejecting both monolithic `SimulationResultDTO` over-engineering and `ExecutionRecord` CQRS domain crossing.

> [!NOTE]
> **GOD FILE ACKNOWLEDGMENT (`worker.py` - 1,497 LOC)**: Per `@[ki_god_code_prevention.md]`, `worker.py` exceeds the 200 LOC boundary. Under `data_and_file_preservation_mandate`, this Epic performs SURGICAL typing and QGR suppression cleanups only (eliminating 8 QGR003 suppressions, 21 `dict[str, Any]` annotations, and replacing L260-L285 telemetry `.get()` with typed `TraceEventMetadataEnvelope`, `StepMetadataDTO`, and `TokenUsage`). Full architectural decomposition into protocol-driven sub-workers is acknowledged as existing technical debt and explicitly deferred to a dedicated God Code decomposition Epic.

**Target Files:**
- `@[backend_v2/services/progress.py]` — Refine existing `ProgressState` to eliminate 30 `dict[str, Any]` annotations (specifically `result: dict[str, Any]` and `details: dict[str, Any]`). Refactor `ProgressTracker` ABC and both implementations.
- `@[backend_v2/core/registry.py]` — Define `[NEW]` `TaskMetadataDTO` co-located. Type `TaskDefinition.metadata` as `TaskMetadataDTO | None`, eliminating 10 `dict[str, Any]` annotations.
- `@[backend_v2/services/studio/simulation_service.py]` — Eliminate `dict[str, Any]` return types and `mock_inputs: dict[str, Any]` parameters. Refactor `simulate_workflow()` to return `WorkflowSimulationResponse`, `simulate_step()` to return `StepSimulationResponse`, and `simulate_prompt_block()` to return `PromptBlockSimulationResponse`.
- `@[backend_v2/api/routers/studio/workflows.py]`, `@[backend_v2/api/routers/studio/steps.py]`, `@[backend_v2/api/routers/studio/prompt_blocks.py]` — Remove intermediate `model_validate()` dictionary conversions on simulation endpoints; return strongly typed simulation DTOs directly from service layer.
- `@[backend_v2/services/studio/workflow_service.py]` — Replace `draft_dict: dict[str, Any]` and `new_steps: list[dict[str, Any]]` with typed domain model instantiation.
- `@[backend_v2/services/studio/system_config_service.py]` — Replace `draft_dict: dict[str, Any]` with typed `SystemConfigModelRegistry` and `SystemConfigMCPGateways`.
- `@[backend_v2/services/studio/prompt_block_service.py]` — Replace `draft_dict: dict[str, Any]` with typed `PromptBlockBase`.
- `@[backend_v2/services/studio/output_profile_service.py]` — Replace `draft_dict: dict[str, Any]` with typed `OutputProfile`.
- `@[backend_v2/services/execution.py]` — Eliminate remaining 6 `dict[str, Any]` annotations.
- `@[backend_v2/services/llm_task_executor.py]` — Eliminate 5 `dict[str, Any]` annotations.
- `@[backend_v2/services/flattener.py]` — Eliminate 3 `dict[str, Any]` annotations.
- `@[backend_v2/services/blueprint.py]` — Eliminate 1 QGR001 reflection and 11 QGR012 suppressions.
- `@[backend_v2/services/mcp/mcp_tool_loop.py]` — Eliminate 3 `dict[str, Any]` and QGR suppressions.
- `@[backend_v2/worker.py]` — Remove 8 QGR003 suppressions and 21 `dict[str, Any]` annotations. Add RFC-7807 structured logging to DLQ handlers. Replace L260-L285 telemetry `.get()` with typed `TraceEventMetadataEnvelope` (containing `StepMetadataDTO`) and `TokenUsage`.
- `@[backend_v2/tests/unit/test_progress.py]` — Finalize migration of all progress tracking tests to typed `ProgressState`.
- `@[backend_v2/tests/unit/core/test_registry.py]` — Finalize migration of task registry tests to `[NEW]` `TaskMetadataDTO`.
- `@[backend_v2/tests/unit/services/studio/test_simulation_service.py]` — Update assertions to verify direct simulation DTO instance attributes instead of dictionary keys.

**Pre-Implementation Cleanups:**
- `@[backend_v2/utils/redis_patcher.py]`: Eliminate 7 `hasattr()` reflection calls. Create typed `FakeRedis` class.
- `@[backend_v2/utils/dict_utils.py]`: Verify callers — if ONLY called from persistence/driver boundary, mark as internal driver utility; otherwise purge unneeded helper methods.
- `@[backend_v2/settings.py]`: Classify static config parsing boundaries (lines 282, 560).
- `@[backend_v2/models/dtos/system.py#L49]`: Add explicit exemption comment to `ClientErrorPayload.context_data: dict[str, Any]` (transport boundary).

**Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/services/ backend_v2/core/ backend_v2/worker.py --test`

---

### Phase 3: Hooks, Orchestrator & Repository Suppression Eradication (~40 files, 5-7 sessions)

**Objective**: Remove all `# noqa: QGR` inline suppressions and all `isinstance(..., dict)` duck-typing checks across hooks, orchestrator, repositories, and domain models.

**Target Files (Hooks, 17 files, ~50 QGR012 suppressions):**
- `@[backend_v2/hooks/scoring/falsifier_hook.py]` (5 dict[str,Any], 3 QGR012)
- `@[backend_v2/hooks/scoring/matrix_hook.py]` (1 dict[str,Any], 5 QGR012)
- `@[backend_v2/hooks/scoring/normalization_hook.py]` (1 dict[str,Any], 3 QGR012)
- `@[backend_v2/hooks/scoring/passivity_hook.py]` (1 dict[str,Any], 3 QGR012)
- `@[backend_v2/hooks/validation.py]`, `@[backend_v2/hooks/llm.py]`, `@[backend_v2/hooks/dlq_guard.py]`, `@[backend_v2/hooks/input_processing.py]`, `@[backend_v2/hooks/integrity.py]`, `@[backend_v2/hooks/source_verification_hook.py]`, `@[backend_v2/hooks/atom_flattening.py]`, `@[backend_v2/hooks/context_mapper.py]`, `@[backend_v2/hooks/archival.py]`, `@[backend_v2/hooks/security.py]`, `@[backend_v2/hooks/hydration.py]`, `@[backend_v2/hooks/metadata.py]`, `@[backend_v2/hooks/metrics.py]`

**Target Files (Orchestrator, 19 files, ~82 suppressions):**
- `@[backend_v2/services/orchestrator/dag_executor.py]` (8 dict[str,Any], 2 QGR003, 3 QGR012)
- `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]` (6 dict[str,Any])
- `@[backend_v2/services/orchestrator/prompt_compiler.py]` (3 dict[str,Any])
- `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]` (3 dict[str,Any], 1 QGR001)
- `@[backend_v2/services/orchestrator/context_router.py]` (1 QGR007, 2 QGR012)
- `@[backend_v2/services/orchestrator/matrix_reducer.py]` (3 dict[str,Any])
- `@[backend_v2/services/orchestrator/strategies/llm.py]` (9 dict[str,Any], 2 QGR003, 19 QGR012)
- `@[backend_v2/services/orchestrator/strategies/base.py]` (2 dict[str,Any])
- `@[backend_v2/services/orchestrator/strategies/logic.py]` (2 dict[str,Any])
- `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]` (8 dict[str,Any])
- `@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py]` (3 dict[str,Any])
- `@[backend_v2/services/orchestrator/enriched_dag_executor.py]` (1 QGR003)
- `@[backend_v2/services/orchestrator/two_pass_atomizer.py]` (1 QGR003)
- `@[backend_v2/services/orchestrator/synthesis_distiller.py]`, `@[backend_v2/services/orchestrator/matrix_explanation_service.py]`, `@[backend_v2/services/orchestrator/rag_preflight_service.py]`, `@[backend_v2/services/orchestrator/localization_compiler.py]`, `@[backend_v2/services/orchestrator/extraction_schema_factory.py]`, `@[backend_v2/services/orchestrator/anchor_validation_service.py]`

**Target Files (Repositories, 5 files, ~10 isinstance):**
- `@[backend_v2/database/repositories/execution.py]` (4 QGR012, 6 dict[str,Any])
- `@[backend_v2/database/repositories/component.py]` (2 isinstance, 6 dict[str,Any])
- `@[backend_v2/database/repositories/components/matrix.py]` (2 isinstance, 3 dict[str,Any])
- `@[backend_v2/database/repositories/audit.py]` (1 isinstance, 4 dict[str,Any])
- `@[backend_v2/database/repositories/workflow.py]` (1 isinstance, 7 dict[str,Any])

**Target Files (Domain Models, ~15 isinstance):**
- `@[backend_v2/models/domain/inputs.py]` (4), `@[backend_v2/models/domain/mechanical_anchors.py]` (3), `@[backend_v2/models/dtos/evaluation_steps.py]` (2), `@[backend_v2/models/dtos/quote_evidence.py]` (2), `@[backend_v2/models/state.py]` (2), `@[backend_v2/models/domain/archivist.py]` (1), `@[backend_v2/models/dtos/matrix_scorecard.py]` (1), `@[backend_v2/models/v2_core.py]` (10 dict[str,Any], 1 QGR012)

**Replacement Patterns (3-Tiered Anti-Duck-Typing Protocol):**
1. **Direct DTO Attribute Access (Preferred)**: When upstream state is already a typed Pydantic DTO (specifically `state.inputs.raw_inputs`, `state.inputs.dynamic_inputs`, or `state.global_context_vars`), replace `isinstance(data, dict)` with direct dot-notation access (`model.field`).
2. **Guarded Model Hydration (Untrusted / Ingress Boundaries)**: When validating untrusted incoming dictionaries or unstructured state, NEVER let raw Pydantic `ValidationError` bubble unhandled into FastAPI's generic 500 handler. Encapsulate validation in RFC-7807 `AppException` (the `details` dict is exempt in `exceptions.py`):
   ```python
   try:
       model = TypeAdapter(ExpectedModel).validate_python(payload)
   except ValidationError as e:
       logger.error("[Domain] Validation failed for %s: %s", ExpectedModel.__name__, e, extra={"error_code": ErrorCodes.VALIDATION_FAILED.value})
       raise AppException(
           message=f"Validation failed for {ExpectedModel.__name__}: {format_validation_error(e)}",
           status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
           details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
       ) from e
   ```
3. **Discriminated Union / Category Pre-Filtering (Polymorphic DAG States)**: For heterogeneous states (`StepOutputDTO.payload`, `SynthesisPayloadCompressor`), do NOT validate against a single monomorphic model. Pre-filter by step category (`if pb.category_id == PromptBlockCategory.MATRIX:`) before hydrating specific schemas, OR validate via Discriminated Union `TypeAdapter[LightweightMatrixOutput | list[AtomResultDTO] | str]`.
4. **Suppression Elimination**: Remove all `# noqa: QGR012`, `# noqa: QGR002`, and `# noqa: QGR001` inline comments.
5. **DLQ Handler Strictness**: Replace `# noqa: QGR003` on DLQ handlers with RFC-7807 `logger.error(..., extra={"error_code": ErrorCodes.*.value})` + explicit `raise` or DLQ yield.

**Quality Gate**: `uv run python scripts/_ast_guardrails.py backend_v2/hooks/ backend_v2/services/orchestrator/ backend_v2/database/repositories/ --strict`

---

### Phase 4: AST Hardening & Governance Lockdown (~5 files, 1-2 sessions)

**Objective**: Harden the AST guardrail engine to `FATAL` severity for all non-test, non-exempt files. Create `ki_zero_permissive_typing.md` Knowledge Item. Synchronize architectural rules. Run full-stack verification.

**Target Files:**
- `@[scripts/_ast_guardrails.py]` — Harden `QGR001`, `QGR002`, `QGR012` to `FATAL` for ALL non-test files. Add explicit boundary exemption set: `{"interfaces.py", "wrapper.py", "driver.py", "tinydb_driver.py", "firestore_driver.py", "logging_config.py", "exceptions.py"}`.
- `@[.agents/rules/01-python-backend.md]` — Update `no_naked_dicts_in_state`, `duck_typing_token_shield_ban`, `strict_attribute_integrity` to mandate absolute zero tolerance.
- Knowledge Item: `ki_zero_permissive_typing.md` — Create dedicated KI documenting Zero Permissive Typing architecture, DTO replacement patterns, boundary exemptions, and AST prevention mechanisms.
- Knowledge Item: `@[ki_ast_guardrail_engine.md]` — Update SSOT table: `QGR001`, `QGR002`, `QGR012` universally `FATAL` with documented boundary exemptions.
- `@[scripts/backend_audit_loop.py]` — Update Stage 4 AST guardrail invocation to enforce `--strict` mode with zero-tolerance exit code.
- `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` — Add regression unit test ensuring raw dict prompt messages and reflection in domain layers are statically rejected.

**Quality Gate**: Full-stack 3-stage iterative verification (see Definition of Done).

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)

1. **Zero `# noqa: QGR` suppressions** across ALL non-test production files in `backend_v2/`.
2. **Zero `isinstance(..., dict)` checks** in non-exempt production files.
3. **Zero unsuppressed `hasattr`/`getattr` reflection** in non-exempt production files.
4. **Zero `dict[str, Any]` annotations** in service, hook, orchestrator, model, and LLM layers (persistence boundary exemptions documented: exactly 102 exempt across 6 database/exception files).
5. **Zero raw dictionary literals (`{"role": ...}`) in test fixtures** across `backend_v2/tests/` (all ~187 migrated to `LLMMessageDTO`).
6. **All test assertions use dot-notation attribute access** (`flat[n].role`) instead of dictionary subscript indexing (all ~103 migrated).
7. **AST guardrails `QGR001`, `QGR002`, `QGR012` at `FATAL` severity** for all non-test, non-exempt files.
8. **`LLMMessageDTO` and `[NEW]` created `PromptMetadataDTO`** replace all `list[dict[str, Any]]` and `dict[str, Any]` in `CompiledPrompt` and its flattening methods.
9. **All DLQ exception handlers** have RFC-7807 structured logging.
10. **Knowledge Item `ki_zero_permissive_typing.md`** created and indexed.
11. **Architectural rules synchronized** in `@[.agents/rules/01-python-backend.md]`.

### Automated Unit Tests

```powershell
# Phase 0 gate (test fixture & DTO foundation pre-hardening)
uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/test_prompt.py backend_v2/tests/unit/llm/ backend_v2/tests/unit/services/test_llm_task_executor.py --test

# Phase 1 gate (production LLM prompt & adapters)
uv run python scripts/backend_audit_loop.py backend_v2/llm/ backend_v2/models/prompt.py backend_v2/models/llm.py --test

# Phase 2 gate (services, studio & telemetry)
uv run python scripts/backend_audit_loop.py backend_v2/services/ backend_v2/core/ backend_v2/worker.py --test

# Phase 3 gate (hooks, orchestrator & repositories)
uv run python scripts/backend_audit_loop.py backend_v2/hooks/ backend_v2/services/orchestrator/ backend_v2/database/repositories/ --test

# Phase 4 gate (full backend verification)
uv run python scripts/backend_audit_loop.py backend_v2/ --test
```

### AST Guardrails & Structural Tests

```powershell
# Zero-violation global AST scan
uv run python scripts/_ast_guardrails.py backend_v2/ --strict

# AST guardrail unit tests
uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py backend_v2/tests/unit/scripts/test_backend_audit_loop.py

# All AST domain guardrails
uv run pytest backend_v2/tests/unit/test_ast_concurrency_guardrails.py backend_v2/tests/unit/test_ast_domain_security_guardrails.py backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py backend_v2/tests/unit/test_ast_scale_guardrails.py backend_v2/tests/unit/test_ast_theory_grounding_guardrails.py
```

### Zero-Verification Deterministic Invariant Checks

```powershell
# Must return exactly 0
uv run python -c "import os, re; matches = [f for r, _, fs in os.walk('backend_v2') if 'tests' not in r for f in fs if f.endswith('.py') for line in open(f'{r}/{f}', encoding='utf-8') if re.search(r'#\s*noqa:\s*QGR', line)]; print('QGR noqas:', len(matches)); assert len(matches) == 0"

# Must return exactly 0 (non-exempt files)
uv run python -c "import os, re; EXEMPT = {'interfaces.py','wrapper.py','driver.py','tinydb_driver.py','firestore_driver.py'}; matches = [f'{r}/{f}' for r, _, fs in os.walk('backend_v2') if 'tests' not in r for f in fs if f.endswith('.py') and f not in EXEMPT for i, line in enumerate(open(f'{r}/{f}', encoding='utf-8'), 1) if re.search(r'isinstance\s*\([^,]+,\s*dict\s*\)', line)]; print('isinstance dict:', len(matches)); assert len(matches) == 0"

# Must return exactly 102 (exempt files only)
uv run python -c "import os, re; EXEMPT = {'interfaces.py','wrapper.py','driver.py','tinydb_driver.py','firestore_driver.py','exceptions.py'}; matches = [(f'{r}/{f}', i) for r, _, fs in os.walk('backend_v2') if 'tests' not in r for f in fs if f.endswith('.py') and f in EXEMPT for i, line in enumerate(open(f'{r}/{f}', encoding='utf-8'), 1) if re.search(r'dict\s*\[\s*str\s*,\s*Any\s*\]', line)]; print('Exempt dict[str, Any]:', len(matches)); assert len(matches) == 102"
```

### Manual Verification Steps

1. Clean-slate database re-seed: `uv run python backend_v2/seed/run_seed.py local`
2. SDUI Semantic Parity: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py -v`

### MANDATORY Final E2E REST API Verification Gate

```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 5. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.

### New Knowledge Items to Create

| KI Name | Purpose | Phase |
| :--- | :--- | :--- |
| `ki_zero_permissive_typing.md` | Documents Zero Permissive Typing architecture, DTO replacement patterns, boundary exemptions, AST prevention | Phase 4 |

### Rules to Update

| Rule File | Update | Phase |
| :--- | :--- | :--- |
| `@[.agents/rules/01-python-backend.md]` | `no_naked_dicts_in_state`, `duck_typing_token_shield_ban`, `strict_attribute_integrity` — absolute zero tolerance mandate | Phase 4 |
| `@[ki_ast_guardrail_engine.md]` | SSOT table: `QGR001`, `QGR002`, `QGR012` universally `FATAL` | Phase 4 |
