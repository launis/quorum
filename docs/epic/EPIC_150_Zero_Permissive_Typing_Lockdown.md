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

| Violation Type | Remaining Count | Origin |
| :--- | :--- | :--- |
| `dict[str, Any]` type annotations (non-test production files) | **516** | Models, LLM adapters, services, hooks, worker, database, utils |
| `isinstance(..., dict)` duck-typing checks | **152** | Hooks, services, repositories, LLM provider, models |
| `# noqa: QGR` inline suppressions | **130** | All domains (QGR001 reflection, QGR002 .get(), QGR003 broad except, QGR007 ConfigDict, QGR012 isinstance) |
| Unsuppressed `hasattr`/`getattr` reflection calls | **77** | LLM client, logging, registry, database drivers, worker |

### Boundary Exemption Classification

Not all 516 `dict[str, Any]` annotations are violations. The `no_naked_dicts_in_state` rule in `@[.agents/rules/00-antigravity-core.md]` explicitly permits `dict` at "absolute external persistence and network boundaries." This Epic establishes a **formal, mathematically verified Exemption Register**:

**EXEMPT Files (persistence/transport/stdlib boundary — dict[str, Any] architecturally correct):**

| File | Count | Exemption Rationale |
| :--- | :--- | :--- |
| `@[backend_v2/database/interfaces.py]` | 55 | Protocol definitions for raw DB driver operations |
| `@[backend_v2/database/wrapper.py]` | 19 | Internal DB abstraction layer |
| `@[backend_v2/database/driver.py]` | 4 | Abstract driver protocol |
| `@[backend_v2/database/tinydb_driver.py]` | 6 | TinyDB internal implementation |
| `@[backend_v2/database/firestore_driver.py]` | 5 | Firestore internal implementation |
| `@[backend_v2/logging_config.py]` | 12 (`hasattr`/`getattr`) | Python stdlib `LogRecord` attribute access API |
| `@[backend_v2/exceptions.py]` | 13 | Exception formatting infrastructure |
| `@[backend_v2/api/routers/execution/executions.py]` | 1 (`isinstance`) | FastAPI HTTP transport serialization boundary |
| **TOTAL EXEMPT** | **~115** | |

**Effective TARGET scope**: 516 - 115 = **~401 actionable violations** across ~50 production files.

### Strategic Scope

This Epic enforces the **Surgical Eradication** pattern: each phase targets a specific architectural layer, eliminates all violations within that layer, runs the quality gate, and commits atomically before proceeding. Unlike Epic 149 (which built foundational DTOs), this Epic is purely **destructive** — it removes anti-patterns, eliminates suppressions, and locks the AST guardrails.

### Dependency

- **Depends on**: `@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]` (all 7 phases COMPLETED, all post-implementation hardening gates COMPLETED).

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)

| Symbol / Pattern | Current Location | Disposition |
| :--- | :--- | :--- |
| `list[dict[str, Any]]` on `CompiledPrompt.static_messages` | `@[backend_v2/models/prompt.py]` | REPLACED by `list[LLMMessageDTO]` |
| `list[dict[str, Any]]` on `CompiledPrompt.dynamic_messages` | `@[backend_v2/models/prompt.py]` | REPLACED by `list[LLMMessageDTO]` |
| `dict[str, Any]` on `CompiledPrompt.metadata` | `@[backend_v2/models/prompt.py]` | REPLACED by typed `typed metadata fields` |
| `.get("role")`, `.get("content")` fallbacks in `_merge_flat` | `@[backend_v2/models/prompt.py]` | REPLACED by direct `msg.role`, `msg.content` attribute access |
| `metadata: dict[str, Any] | None` on `TaskDefinition` | `@[backend_v2/core/registry.py#L52]` | REPLACED by `TaskMetadataDTO | None` |
| `result: dict[str, Any] | None` on `ProgressState` | `@[backend_v2/services/progress.py#L34]` | REPLACED by typed optional fields |
| `details: dict[str, Any] | None` on `ProgressState` | `@[backend_v2/services/progress.py#L35]` | REPLACED by typed optional fields |
| `details: dict[str, Any] | None` params on `ProgressTracker` ABC | `@[backend_v2/services/progress.py]` | REPLACED by typed `ProgressState` |
| All 130 `# noqa: QGR` inline suppressions | 30+ files across `backend_v2/` | INTENTIONALLY DROPPED (zero remaining) |
| All 152 `isinstance(..., dict)` checks in non-exempt files | Hooks, services, orchestrator, repositories | REPLACED by `TypeAdapter` validation or direct DTO attribute access |
| All unsuppressed `hasattr`/`getattr` in non-exempt files | LLM client, registry, database drivers | REPLACED by typed attribute access or explicit Protocol methods |

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
2. **Pydantic V2 Strictness**: `ConfigDict(strict=True, extra="forbid")` on ALL new DTOs (`LLMMessageDTO`, `TaskMetadataDTO`, `typed metadata fields`, `SimulationResultDTO`).
3. **Zero Suppressions Policy**: Zero `# noqa: QGR` inline suppressions allowed in production code after completion.
4. **AST Guardrail FATAL Enforcement**: `QGR001` (reflection), `QGR002` (.get fallbacks), `QGR012` (isinstance dict) at `FATAL` severity for ALL non-test, non-exempt files.
5. **RFC-7807 Dual-Reporting**: All DLQ exception handlers must include structured `logger.error` with `ErrorCodes`.
6. **God Code Prevention**: No DTO file exceeds 200 LOC. New DTOs co-located with primary consumer.

### Producer-Consumer Integration Check

| Producer | Consumer | Contract |
| :--- | :--- | :--- |
| `LLMMessageDTO` (new, `@[backend_v2/models/llm.py]`) | `CompiledPrompt`, all 5 LLM adapters, `caching_service.py`, `prompt_compiler.py`, `prompt_factory.py` | `.model_dump()` ONLY at LiteLLM SDK boundary |
| `TaskMetadataDTO` (new, `@[backend_v2/core/registry.py]`) | `TaskRegistry`, `worker.py` job dispatch | Direct attribute access, no `.get()` |
| `ProgressState` (refined, `@[backend_v2/services/progress.py]`) | `DatabaseProgressTracker`, `InMemoryProgressTracker`, `worker.py` | Typed fields, `.model_dump()` at SSE JSON boundary only |
| AST Guardrail boundary exemptions | `@[scripts/_ast_guardrails.py]` | Explicit path-based exemption set |

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: LLM Message DTO & Prompt Infrastructure (~10 files, 2-3 sessions)

**Objective**: Create `LLMMessageDTO` and refactor the entire LLM prompt compilation, adapter, and provider pipeline to eliminate all `list[dict[str, Any]]` message lists and reflection on LiteLLM response objects.

**Target Files:**
- `@[backend_v2/models/llm.py]` — Define `LLMMessageDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)`, fields: `role: str`, `content: str`, `tool_calls: list[ToolCallDTO] | None = None`, `tool_call_id: str | None = None`, `name: str | None = None`.
- `@[backend_v2/models/prompt.py]` — Refactor `CompiledPrompt` to use `list[LLMMessageDTO]`. Update `_merge_flat`, `to_static_flat`, `to_dynamic_flat`, `to_flat_messages`, `_forbid_system_in_dynamic` to direct attribute access.
- `@[backend_v2/llm/provider.py]` — Eliminate 12 `isinstance(dict)` checks and all `model_dump` laundering.
- `@[backend_v2/llm/adapters/base_adapter.py]` — Eliminate 3 QGR002 suppressions and 4 `isinstance(dict)` checks.
- `@[backend_v2/llm/adapters/ai_studio_adapter.py]` — Eliminate 2 QGR002 and 1 QGR003 suppressions. Narrow exception to `(ConnectionError, TimeoutError)`.
- `@[backend_v2/llm/adapters/vertex_adapter.py]` — Eliminate 2 QGR002 and 1 QGR003 suppressions.
- `@[backend_v2/llm/adapters/anthropic_adapter.py]` — Eliminate 1 `isinstance(dict)` check.
- `@[backend_v2/llm/adapters/openai_adapter.py]` — Eliminate remaining QGR suppressions.
- `@[backend_v2/llm/client.py]` — Eliminate 6 `hasattr`/`getattr` on LiteLLM `LiteLLM response objects` via direct typed attribute access.
- `@[backend_v2/llm/ingress_pipeline.py]` — Eliminate 3 `isinstance(dict)` checks.
- `@[backend_v2/llm/mock.py]` — Eliminate 1 `isinstance(dict)` check.

**Pre-Implementation Cleanups:**
- `@[backend_v2/utils/math_utils.py]`: Add `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` to `StrictnessConfig`.
- `@[backend_v2/llm/caching_service.py]`: Update all consumers of `to_flat_messages()` to handle `LLMMessageDTO` return type.

**Critical Risk Mitigation (LiteLLM SDK Boundary)**:
All consumers of `CompiledPrompt.to_flat_messages()`, `to_static_flat()`, `to_dynamic_flat()` MUST be traced via `grep_search` before modification. Adapters call `[msg.model_dump() for msg in compiled.to_flat_messages()]` EXCLUSIVELY at the LiteLLM SDK invocation boundary.

**Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/llm/ backend_v2/models/prompt.py backend_v2/models/llm.py --test`

---

### Phase 2: Service & Studio Layer DTO Elimination (~20 files, 3-4 sessions)

**Objective**: Eliminate all `dict[str, Any]` annotations from the service layer, progress tracking, studio services, and worker telemetry. Refine existing `ProgressState` model and create `TaskMetadataDTO`, `SimulationResultDTO`.

**Target Files:**
- `@[backend_v2/services/progress.py]` — Refine existing `ProgressState` to eliminate `result: dict[str, Any]` and `details: dict[str, Any]`. Refactor `ProgressTracker` ABC and both implementations.
- `@[backend_v2/core/registry.py]` — Define `TaskMetadataDTO` co-located. Type `TaskDefinition.metadata` as `TaskMetadataDTO | None`.
- `@[backend_v2/services/studio/simulation_service.py]` — Define `SimulationResultDTO` co-located. Replace `dict[str, Any]` return types and `mock_inputs: dict[str, Any]` parameters.
- `@[backend_v2/services/studio/workflow_service.py]` — Replace `draft_dict: dict[str, Any]` and `new_steps: list[dict[str, Any]]` with typed domain model instantiation.
- `@[backend_v2/services/studio/system_config_service.py]` — Replace `draft_dict: dict[str, Any]` with typed `SystemConfigModelRegistry` and `SystemConfigMCPGateways`.
- `@[backend_v2/services/studio/prompt_block_service.py]` — Replace `draft_dict: dict[str, Any]` with typed `PromptBlockBase`.
- `@[backend_v2/services/studio/output_profile_service.py]` — Replace `draft_dict: dict[str, Any]` with typed `OutputProfile`.
- `@[backend_v2/services/execution.py]` — Eliminate remaining 6 `dict[str, Any]` annotations.
- `@[backend_v2/services/llm_task_executor.py]` — Eliminate 5 `dict[str, Any]` annotations.
- `@[backend_v2/services/flattener.py]` — Eliminate 3 `dict[str, Any]` annotations.
- `@[backend_v2/services/blueprint.py]` — Eliminate 1 QGR001 reflection and 11 QGR012 suppressions.
- `@[backend_v2/services/mcp/mcp_tool_loop.py]` — Eliminate 3 `dict[str, Any]` and QGR suppressions.
- `@[backend_v2/worker.py]` — Remove 8 QGR003 suppressions and 7 `isinstance(dict)` checks. Add RFC-7807 structured logging to DLQ handlers. Replace L260-L285 telemetry `.get()` with typed `StepMetadataDTO` and `TokenUsage`.

**Pre-Implementation Cleanups:**
- `@[backend_v2/utils/redis_patcher.py]`: Eliminate 7 `hasattr()` reflection calls. Create typed `FakeRedis` class.
- `@[backend_v2/utils/dict_utils.py]`: Verify callers — if ONLY called from persistence/driver boundary, exempt; otherwise refactor.
- `@[backend_v2/models/dtos/system.py#L49]`: Add explicit exemption comment to `ClientErrorPayload.context_data: dict[str, Any]` (transport boundary).

**Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/services/ backend_v2/core/ backend_v2/worker.py --test`

---

### Phase 3: Hooks, Orchestrator & Repository Suppression Eradication (~40 files, 4-5 sessions)

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
- `@[backend_v2/database/repositories/execution.py]` (4 QGR012)
- `@[backend_v2/database/repositories/component.py]` (2 isinstance)
- `@[backend_v2/database/repositories/components/matrix.py]` (2 isinstance)
- `@[backend_v2/database/repositories/audit.py]` (1 isinstance)
- `@[backend_v2/database/repositories/workflow.py]` (1 isinstance)

**Target Files (Domain Models, ~15 isinstance):**
- `@[backend_v2/models/domain/inputs.py]` (4), `@[backend_v2/models/domain/mechanical_anchors.py]` (3), `@[backend_v2/models/dtos/evaluation_steps.py]` (2), `@[backend_v2/models/dtos/quote_evidence.py]` (2), `@[backend_v2/models/state.py]` (2), `@[backend_v2/models/domain/archivist.py]` (1), `@[backend_v2/models/dtos/matrix_scorecard.py]` (1)

**Replacement Patterns:**
- `isinstance(payload, dict)` replaced by `TypeAdapter(ExpectedModel).validate_python(payload)` or direct DTO attribute access
- `# noqa: QGR012 [REASON: ...]` removed; underlying pattern refactored to typed access
- `# noqa: QGR003 [REASON: ...]` on DLQ handlers replaced with RFC-7807 `logger.error(..., extra={"error_code": ErrorCodes.*.value})` + explicit `raise` or DLQ yield
- `# noqa: QGR001 [REASON: ...]` on reflection replaced with typed method delegation or Protocol methods

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

**Quality Gate**: Full-stack 3-stage iterative verification (see Definition of Done).

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)

1. **Zero `# noqa: QGR` suppressions** across ALL non-test production files in `backend_v2/`.
2. **Zero `isinstance(..., dict)` checks** in non-exempt production files.
3. **Zero unsuppressed `hasattr`/`getattr` reflection** in non-exempt production files.
4. **Zero `dict[str, Any]` annotations** in service, hook, orchestrator, model, and LLM layers (persistence boundary exemptions documented).
5. **AST guardrails `QGR001`, `QGR002`, `QGR012` at `FATAL` severity** for all non-test, non-exempt files.
6. **`LLMMessageDTO`** replaces all `list[dict[str, Any]]` in `CompiledPrompt`.
7. **All DLQ exception handlers** have RFC-7807 structured logging.
8. **Knowledge Item `ki_zero_permissive_typing.md`** created and indexed.
9. **Architectural rules synchronized** in `@[.agents/rules/01-python-backend.md]`.

### Automated Unit Tests

```powershell
# Phase 1 gate
uv run python scripts/backend_audit_loop.py backend_v2/llm/ backend_v2/models/prompt.py backend_v2/models/llm.py --test

# Phase 2 gate
uv run python scripts/backend_audit_loop.py backend_v2/services/ backend_v2/core/ backend_v2/worker.py --test

# Phase 3 gate
uv run python scripts/backend_audit_loop.py backend_v2/hooks/ backend_v2/services/orchestrator/ backend_v2/database/repositories/ --test

# Phase 4 gate (full backend)
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
