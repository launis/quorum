<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
  <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
</required_context_rules>

# EPIC 149: Clean Pydantic V2 Full-Codebase Transition and Anti-Drift Hardening

---

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective
Eliminate ALL raw dictionary anti-patterns, reflection duck-typing (`getattr`/`hasattr`), loose union types (`Model | dict[str, Any]`), and silent defaults from the Quorum backend, achieving a 100% type-driven architecture where every state transition, hook result, and repository response flows through strictly validated Pydantic V2 models (`ConfigDict(strict=True, extra="forbid")`).

### Problem Statement
Despite strict architectural rules in `@[.agents/rules/00-antigravity-core.md]` and `@[.agents/rules/01-python-backend.md]` (`zero_service_layer_fallbacks`, `the_zero_compromise_pledge`, `no_naked_dicts_in_state`), a systematic `grep_search` audit (August 2026) revealed **~55+ production files** containing anti-patterns across **9 distinct archetypes**. This technical debt forces:

1. **Every downstream consumer** to write defensive `isinstance(x, dict)` branches (50+ instances in `services/`, 26+ in `hooks/`).
2. **Every service method** accessing `initiator.organization_id` to use `getattr(initiator, "organization_id", None)` (15 instances in `@[backend_v2/services/execution.py]` alone).
3. **Every repository consumer** to call `Model.model_validate(raw_dict)` ad-hoc instead of receiving typed domain models directly.
4. **Silent locale masking** where `target_locale="en"` default in `@[backend_v2/models/v2_core.py]#L1421` allows executions to silently run in the wrong language.

### Strategic Scope
This Epic enforces the **Strangler Fig** migration pattern: each phase locks a new layer's types, makes existing consumers compile-fail on `dict` usage, fixes all consumers, and runs the global quality gate before proceeding to the next layer. The authoritative reference catalog is `@[docs/CLEAN_PYDANTIC_TRANSITION_CATALOG.md]`.

### Quantitative Scope Summary (Deterministic Audit Results)

| Anti-Pattern Category | `services/` | `hooks/` | `core/` | `database/` | Total |
|---|---|---|---|---|---|
| `isinstance(..., dict)` | 48+ | 26+ | 0 | 0 | **74+** |
| `getattr(obj, "field", default)` | 36+ | 3 | 0 | 0 | **39+** |
| `hasattr(obj, "method")` | 11 | 0 | 0 | 0 | **11** |
| `.get("key", default)` | 15+ | 20+ | 0 | 0 | **35+** |
| `model_dump() -> dict mutation` | 18+ | 0 | 0 | 0 | **18+** |
| Repository methods returning `dict[str, Any]` | 0 | 0 | 0 | 25+ | **25+** |
| Loose Union types (`Model \| dict`) | 0 | 0 | 3 | 0 | **3** |
| Silent mandatory defaults | 0 | 0 | 0 | 0 | **2** (in `models/`) |
| **TOTAL VIOLATIONS** | | | | | **~207+** |

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)

| Symbol / Pattern | Location | Disposition |
|---|---|---|
| `HookState.inputs: dict[str, Any]` | `@[backend_v2/core/hook_registry.py]#L79` | REPLACE with typed `ExecutionInputsDTO` |
| `HookState.global_context_vars: dict[str, Any]` | `@[backend_v2/core/hook_registry.py]#L78` | REPLACE with typed `GlobalContextVarsDTO` |
| `HookResult.state_delta: dict[str, Any] \| None` | `@[backend_v2/core/hook_registry.py]#L86` | REPLACE with typed `HookDeltaDTO \| None` |
| `ExecutionMetadata(target_locale="en")` default_factory | `@[backend_v2/models/v2_core.py]#L1421` | REMOVE default; make `target_locale` mandatory |
| `target_locale: str = Field(default="en")` | `@[backend_v2/models/v2_core.py]#L1375` | REMOVE default; Fail-Fast on missing locale |
| `ExecutionRecord.context_variables: dict[str, Any]` | `@[backend_v2/models/v2_core.py]#L1378` | REPLACE with typed DTO |
| ALL `isinstance(..., dict)` branches in `services/` and `hooks/` | 74+ instances across 30+ files | INTENTIONALLY DROPPED (replaced by typed dot-notation) |
| ALL `getattr(obj, "field", default)` in `services/` | 36+ instances across 10+ files | INTENTIONALLY DROPPED (replaced by direct attribute access) |
| ALL `hasattr(repo, "method")` interface discovery | 11 instances in `usage_service.py`, `dag_executor.py`, `llm_task_executor.py`, `blueprint.py`, `context_builder.py` | INTENTIONALLY DROPPED (replaced by explicit interface methods) |
| ALL repository methods returning `dict[str, Any]` | 25+ methods across 14 repository files | REPLACE with typed Pydantic Domain model returns |

### Retained SSOT Invariants (What We Will RETAIN)

| Invariant | Justification |
|---|---|
| `ConfigDict(strict=True, extra="forbid")` on all domain models | Already enforced; this Epic extends coverage to ALL DTOs and state objects |
| Database driver (`JSONFileDriver`, `TinyDBDriver`) returns `dict[str, Any]` | Correct: the lowest I/O layer returns raw dicts; the Repository layer reconstitutes them into typed models |
| `model_dump()` for serialization to database/JSON | Correct: `model_dump()` is valid at the serialization boundary (Repository write path). Banned only for intermediate state manipulation in services |
| `noqa: QGR001/002/003` with valid `[REASON: ...]` justifications | Retained for legitimate edge cases (specifically: LLM adapter polymorphic message parsing in `vertex_adapter.py`/`ai_studio_adapter.py`/`base_adapter.py`, worker DLQ catch-all in `worker.py`, `LaxScoringStrategy` enum-or-string handling in `blueprint.py`) |
| `@[scripts/_ast_guardrails.py]` QGR rule definitions | Retained and strengthened: QGR001/002 severity promoted from WARNING to FATAL in `services/` and `hooks/` |

### Compliance & Modernity Gates

1. Zero Legacy State Support Mandate: Clean slate DB re-seeding.
2. Central Config Sovereignty: All limits in `@[backend_v2/settings.py]`.
3. Pydantic Strictness: `ConfigDict(strict=True, extra='forbid')` on ALL new DTOs.
4. Cross-Domain DTO Parity: Flutter Freezed models updated via `flutter_audit_loop.py --build` if API surface changes.
5. Python 3.14 Concurrency: `asyncio.TaskGroup` with `asyncio.Semaphore`.
6. RFC-7807 Dual-Reporting: Structured `logger.error` preceding `AppException`.
7. AST Guardrail Mandate: New AST tests for `isinstance(x, dict)` in `services/` and `hooks/`.
8. Scoped Boy Scout Rule: Technical debt cleaned exclusively in touched files.

### Producer-Consumer Integration Check

| Producer Layer | Consumer Layer | Current Contract | Target Contract |
|---|---|---|---|
| Database Driver (`JSONFileDriver`) | Repository | `dict[str, Any]` | `dict[str, Any]` (unchanged — correct I/O boundary) |
| Repository | Service Layer | `dict[str, Any]` | Typed Pydantic Domain Model |
| Hook Functions | Orchestrator (`DAGExecutor`) | `HookResult.state_delta: dict[str, Any]` | `HookResult.delta: HookDeltaDTO \| None` |
| `HookState.inputs` | All Hooks | `dict[str, Any]` | Typed `ExecutionInputsDTO` |
| `HookState.global_context_vars` | All Hooks | `dict[str, Any]` | Typed `GlobalContextVarsDTO` |
| LLM Execution Strategy | Synthesis Pipeline | `model_dump() -> dict -> dict mutation` | `model_copy(update={...})` on typed models |

---

## 3. Phased Execution Plan (Implementation Strategy)

> [!IMPORTANT]
> This Epic MUST be decomposed into **multiple implementation plans** via `/tier1-planner` due to its scope (~55+ files). Each plan MUST target a single phase or a tightly coupled subset of a phase. The Strangler Fig pattern requires that each phase's typed models are locked BEFORE downstream consumers are refactored.

### Phase 1: Pre-Implementation Technical Debt Cleanups & SSOT Foundation

**Objective**: Lock the foundational data models that all downstream layers depend on.

**Target Files** (exhaustive):
- `@[backend_v2/models/v2_core.py]` — Remove `target_locale="en"` default_factory from `ExecutionRecord.metadata` (line 1421) and `ExecutionCoreFields.target_locale` (line 1375 under `TYPE_CHECKING`). Make `target_locale` a mandatory field without default.
- `@[backend_v2/models/execution_core.py]` — Verify `target_locale` is already mandatory (line 27). Ensure `ExecutionMetadata` covers ALL telemetry fields currently written as ad-hoc dict keys in `@[backend_v2/worker.py]`.
- `@[backend_v2/core/hook_registry.py]` — Replace `inputs: dict[str, Any]` (line 79) with typed `ExecutionInputsDTO`, `global_context_vars: dict[str, Any]` (line 78) with typed `GlobalContextVarsDTO`, and `state_delta: dict[str, Any] | None` (line 86) with typed `HookDeltaDTO | None`.
- `@[backend_v2/core/registry.py]` — Replace 9 `dict[str, Any]` metadata/fields with typed models where applicable.
- Create new DTO models: `HookDeltaDTO`, `ExecutionInputsDTO`, `GlobalContextVarsDTO` in `@[backend_v2/models/dtos/]`.

**Dependency**: None. This phase MUST complete first.

### Phase 2: Repository Reconstitution (DAL -> Typed Domain Models)

**Objective**: Every Repository method returns a validated Pydantic Domain Model instead of `dict[str, Any]`.

**Target Files** (exhaustive — 14 repositories):
- `@[backend_v2/database/repositories/system.py]` (5 methods -> dict)
- `@[backend_v2/database/repositories/workflow.py]` (8 methods -> dict)
- `@[backend_v2/database/repositories/knowledge.py]` (5 methods -> dict)
- `@[backend_v2/database/repositories/identity.py]` (3 methods -> dict)
- `@[backend_v2/database/repositories/audit.py]` (2 methods -> dict)
- `@[backend_v2/database/repositories/component.py]` (2 methods -> dict)
- `@[backend_v2/database/repositories/components/task_blueprint.py]`
- `@[backend_v2/database/repositories/components/role.py]`
- `@[backend_v2/database/repositories/components/prompt_block.py]` (2 methods)
- `@[backend_v2/database/repositories/components/output_profile.py]`
- `@[backend_v2/database/repositories/components/matrix.py]`
- `@[backend_v2/database/repositories/components/extraction_protocol.py]`
- `@[backend_v2/database/repositories/components/execution_persona.py]`
- `@[backend_v2/database/repositories/components/agent.py]`

**Pattern**: Each repository method calls `Model.model_validate(raw_dict)` internally and returns the typed model. Service layer never sees `dict[str, Any]`.

**Dependency**: Phase 1 (typed DTOs must exist).

### Phase 3: Orchestration & Strategy Core Refactoring

**Objective**: Eliminate ALL `isinstance(..., dict)`, `getattr()`, `.get()` branches from the orchestration engine and execution strategies.

**Target Files** (exhaustive — 19 files):
- `@[backend_v2/services/orchestrator/dag_executor.py]` (1x isinstance, 1x getattr, 1x hasattr)
- `@[backend_v2/services/orchestrator/strategies/llm.py]` (6x isinstance, 2x getattr, model_dump -> dict)
- `@[backend_v2/services/orchestrator/strategies/base.py]` (2x isinstance + dict.pop chains)
- `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]` (**8x isinstance, 10x getattr** — critical hotspot)
- `@[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py]` (4x isinstance nested)
- `@[backend_v2/services/orchestrator/prompt_compiler.py]` (4x isinstance + model_dump -> dict traversal)
- `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]` (1x getattr delegation)
- `@[backend_v2/services/orchestrator/context_router.py]` (2x isinstance, 1x getattr)
- `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]` (3x isinstance)
- `@[backend_v2/services/orchestrator/synthesis_distiller.py]` (2x isinstance)
- `@[backend_v2/services/orchestrator/matrix_explanation_service.py]` (**6x isinstance** — heavy)
- `@[backend_v2/services/orchestrator/rag_preflight_service.py]` (2x isinstance)
- `@[backend_v2/services/orchestrator/localization_compiler.py]` (1x isinstance)
- `@[backend_v2/services/orchestrator/extraction_schema_factory.py]` (model_dump -> dict)
- `@[backend_v2/services/orchestrator/atomizer.py]` (model_dump optimizations)
- `@[backend_v2/services/orchestrator/anchor_validation_service.py]` (model_dump | dict union)
- `@[backend_v2/services/orchestrator/matrix_reducer.py]` (2x isinstance + dict nesting)
- `@[backend_v2/services/orchestrator/engines/tda_engine.py]` (1x isinstance)
- `@[backend_v2/services/orchestrator/engines/synthesis_engine.py]` (model_dump -> dict + dict mutation)

**Dependency**: Phase 1 (HookState typed), Phase 2 (repository returns typed).

### Phase 4: Hooks Refactoring & God Code Decomposition

**Objective**: Eliminate ALL `isinstance(..., dict)`, `.get()`, and `getattr()` from hook functions. `scoring.py` (65 KB, 20+ violations) MUST be decomposed into smaller modules first per `@[ki_god_code_prevention.md]`.

**Target Files** (exhaustive — 11 hooks):
- `@[backend_v2/hooks/scoring.py]` (**20x isinstance, multiple .get(), 1x getattr** — 65 KB God Code, MUST decompose first)
- `@[backend_v2/hooks/validation.py]` (3x isinstance, .get())
- `@[backend_v2/hooks/source_verification_hook.py]` (2x isinstance)
- `@[backend_v2/hooks/atom_flattening.py]` (dict reads)
- `@[backend_v2/hooks/input_processing.py]` (1x isinstance, .get())
- `@[backend_v2/hooks/integrity.py]` (.get() chains)
- `@[backend_v2/hooks/linguistics.py]` (multiple .get() calls)
- `@[backend_v2/hooks/llm.py]` (1x isinstance, .get())
- `@[backend_v2/hooks/context_mapper.py]` (2x getattr)
- `@[backend_v2/hooks/archival.py]` (1x isinstance)
- `@[backend_v2/hooks/security.py]` (dict reads)

**Pre-Requisite Sub-Phase**: `scoring.py` God Code Decomposition must be planned and executed BEFORE Pydantic migration of its contents. Use `/tier3-god-code-decomposition` targeting `@[backend_v2/hooks/scoring.py]`.

**Dependency**: Phase 1 (HookDeltaDTO, typed HookState).

### Phase 5: Service Layer & Utility Services

**Objective**: Eliminate ALL `getattr(initiator, "organization_id", None)` chains, `isinstance(x, dict)` branches, and `hasattr()` interface discovery from the service layer.

**Target Files** (exhaustive — 11 files):
- `@[backend_v2/services/execution.py]` (**15x getattr** `organization_id` + 2x getattr other — critical)
- `@[backend_v2/services/usage_service.py]` (1x isinstance, 1x getattr, 4x hasattr)
- `@[backend_v2/services/llm_task_executor.py]` (4x getattr, 1x hasattr)
- `@[backend_v2/services/translation_service.py]` (1x isinstance)
- `@[backend_v2/services/source_verification_service.py]` (1x isinstance)
- `@[backend_v2/services/blueprint.py]` (2x hasattr — currently noqa QGR001)
- `@[backend_v2/services/studio/output_profile_service.py]` (2x isinstance)
- `@[backend_v2/services/studio/prompt_block_service.py]` (1x isinstance)
- `@[backend_v2/services/studio/workflow_service.py]` (2x isinstance)
- `@[backend_v2/services/studio/system_config_service.py]` (2x getattr)
- `@[backend_v2/services/mcp/mcp_tool_loop.py]` (1x getattr)

**Dependency**: Phase 2 (repositories return typed models), Phase 1 (typed DTOs).

### Phase 6: Background Workers & Storage

**Objective**: Eliminate dict mutations in `worker.py` metadata handling.

**Target Files**:
- `@[backend_v2/worker.py]` (dict mutations in metadata fields)

**Dependency**: Phase 1 (`ExecutionMetadata` covers all telemetry fields).

### Phase 7: Test Modernization (Legacy Fixture Elimination)

**Objective**: Replace ALL test dictionary fixtures with valid Pydantic model instances or `polyfactory` factories.

**Target**: All test files in `@[backend_v2/tests/]` that feed `dict[str, Any]` fixtures to service methods expecting typed models.

**Rules** (from `@[docs/CLEAN_PYDANTIC_TRANSITION_CATALOG.md]` Section 8):
1. Anti-TDD Trap ban: NEVER weaken production code to make legacy dict-based tests pass.
2. All new fixtures MUST use Pydantic model instances or polyfactory.
3. ISTQB equivalence partitions: 2 negative tests per positive test.
4. Heterogeneous payload testing: cover dict, list, string, and falsy inputs.

**Dependency**: Phases 1-6 (production code must be fully typed first).

### Phase 8: AST Guardrail Hardening (Drift Prevention)

**Objective**: Promote `QGR001` (getattr/hasattr) and `QGR002` (.get(key, default)) from WARNING to FATAL severity in `services/` and `hooks/` directories, making it mathematically impossible for new anti-patterns to enter the codebase.

**Target Files**:
- `@[scripts/_ast_guardrails.py]` — Update severity configuration
- `@[scripts/backend_audit_loop.py]` — Ensure FATAL violations block the audit loop

**Dependency**: Phases 1-7 (all existing violations must be resolved before promoting to FATAL).

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)

1. **Zero `isinstance(..., dict)` in `services/` and `hooks/`**: Verified by `grep_search "isinstance.*dict" backend_v2/services/ --include="*.py" --exclude="*test*"` returning 0 results (excluding legitimately suppressed `noqa` lines).
2. **Zero `getattr(obj, "field", default)` in `services/` and `hooks/`**: Verified by deterministic grep returning 0 unsuppressed results.
3. **Zero `hasattr()` in `services/`**: Verified by deterministic grep returning 0 unsuppressed results.
4. **Zero repository methods returning `dict[str, Any]`**: All repository read methods return typed Pydantic Domain Models.
5. **Zero silent defaults on mandatory business fields**: `target_locale` has no default value; missing locale causes immediate `ValidationError`.
6. **100% typed HookState**: `inputs`, `global_context_vars`, and `state_delta` are typed DTOs.
7. **AST Guardrails QGR001/QGR002 at FATAL severity** in `services/` and `hooks/`.
8. **All tests pass** via `uv run python scripts/backend_audit_loop.py backend_v2/ --test` with >90% coverage.
9. **`scoring.py` decomposed** below 500 LOC per module (God Code Prevention mandate).

### Automated Unit Tests

```powershell
uv run python scripts/backend_audit_loop.py backend_v2/ --test
```

### AST Guardrails & Structural Tests

1. **New AST test**: `test_no_isinstance_dict_in_services` — Scans all `.py` files under `services/` and `hooks/` for `isinstance(..., dict)` without valid `noqa` suppression.
2. **New AST test**: `test_no_getattr_in_services` — Scans for `getattr(obj, "field", default)` without valid `noqa` suppression.
3. **New AST test**: `test_no_hasattr_in_services` — Scans for `hasattr()` without valid `noqa` suppression.
4. **New AST test**: `test_repositories_return_typed_models` — Verifies no repository method signature contains `-> dict[str, Any]`.
5. **Existing QGR001/QGR002 severity promotion** to FATAL.

### Manual Verification Steps

1. Full database re-seed: `uv run python backend_v2/seed/run_seed.py local`
2. Execute a full workflow end-to-end and verify PDF generation.
3. Verify Flutter client still renders correctly after any DTO surface changes.

### MANDATORY Final E2E REST API Verification Gate

```powershell
$env:RUN_LIVE_E2E = "true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 5. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.

### Key Governance References

| Rule / KI | Relevance |
|---|---|
| `@[.agents/rules/00-antigravity-core.md]` `zero_service_layer_fallbacks` | Foundational ban on `.get()`, `getattr()`, fallback chains in services |
| `@[.agents/rules/00-antigravity-core.md]` `the_zero_compromise_pledge` | Strict Pydantic enforcement; crash on unexpected keys |
| `@[.agents/rules/00-antigravity-core.md]` `the_duct_tape_ban` | Ban on `try...except Exception:`, empty returns, silent bypasses |
| `@[.agents/rules/00-antigravity-core.md]` `the_no_legacy_mandate` | Ban on backwards compatibility; ruthlessly delete obsolete code |
| `@[.agents/rules/01-python-backend.md]` `the_duct_tape_ban` | `.get("key", default)` explicitly banned |
| `@[.agents/rules/00-antigravity-core.md]` `ast_guardrail_mandate` | New architectural rules require AST enforcement tests |
| `@[.agents/rules/00-antigravity-core.md]` `anti_tdd_trap` | Never weaken production code to satisfy legacy tests |
| `@[ki_god_code_prevention.md]` | `scoring.py` (65 KB) requires decomposition before migration |
| `@[ki_python_314_concurrency_strictness.md]` | Global `ConfigDict(strict=True, extra='forbid')` on all models |
| `@[docs/CLEAN_PYDANTIC_TRANSITION_CATALOG.md]` | Authoritative reference catalog with 9 anti-pattern archetypes |
