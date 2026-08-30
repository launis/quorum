<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
  <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
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
This Epic enforces the **Strangler Fig** migration pattern: each phase locks a new layer's types, makes existing consumers compile-fail on `dict` usage, fixes all consumers and atomically modernizes their corresponding tests, and runs the global quality gate before proceeding to the next layer. Furthermore, Phase 1 injects upfront Seed Data Vault sanitization to guarantee clean-boot stability before removing silent schema defaults. The authoritative reference catalog is `@[docs/CLEAN_PYDANTIC_TRANSITION_CATALOG.md]`.

### Clean-Slate Database Wipe & Absolute Zero-Fallback Mandate (Type Constitutionalist)
- **Approved Best Practice (Type Constitutionalist)**:
  - **Finding**: During massive refactoring (~55+ files across repositories, services, orchestrator, hooks), developers/agents are tempted to use `Union[NewModel, dict]` or `try/except` blocks to maintain a working state mid-epic or parse old database records.
  - **Action Taken**: Invoked `the_no_legacy_mandate` and `the_zero_compromise_pledge`. ALL temporary unions, fallback parsers (`try/except`), dictionary coercion chains (`getattr`, `.get()`), and backward-compatibility shims are STRICTLY FORBIDDEN.
- **Clean-Slate Database Wipe**: All local historical execution records, traces, and intermediate state files are completely purged. `uv run python backend_v2/seed/run_seed.py local` and `scripts/sanitize_seed_vault.py` wipe and rebuild a clean seed state. Incompatible historical execution records on disk are permanently abandoned with zero requirement for data migration.

### Temporary Non-Executable State Allowance & Phase-Boundary Quality Gate
- **In-Flight Non-Executable State Permitted**: Because this Epic executes an exhaustive, full-codebase type migration across ~55+ files (repositories, services, hooks, orchestrator), the codebase is explicitly permitted to be in a temporary non-executable / non-compilable state across intermediate file refactors within and between in-flight plan steps.
- **Phase Completion Boundary Invariant**: To prevent feedback starvation, unverified compounding regressions, and context amnesia, full system compilability, 100% test pass rates, and AST Guardrail passing status (`backend_audit_loop.py`) are strictly enforced at each phase's completion boundary (Strangler Fig isolation).

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
| `ConfigDict(strict=True, extra="forbid", frozen=True)` on all domain models and DTOs | Already enforced; this Epic extends coverage to ALL DTOs and state objects. `validate_assignment=True` is explicitly banned as a placebo/dead code on frozen models (does not validate `model_copy`). |
| Database driver (`JSONFileDriver`, `TinyDBDriver`) returns `dict[str, Any]` | Correct: the lowest I/O layer returns raw dicts; the Repository layer reconstitutes them into typed models |
| `model_dump()` for serialization to database/JSON | Correct: `model_dump()` is valid at the serialization boundary (Repository write path). Banned only for intermediate state manipulation in services |
| `noqa: QGR001/002/003` with valid `[REASON: ...]` justifications | Retained for legitimate edge cases (specifically: LLM adapter polymorphic message parsing in `vertex_adapter.py`/`ai_studio_adapter.py`/`base_adapter.py`, worker DLQ catch-all in `worker.py`, `LaxScoringStrategy` enum-or-string handling in `blueprint.py`) |
| `@[scripts/_ast_guardrails.py]` QGR rule definitions | Retained and hardened: `QGR001` (reflection/mutation) and `QGR002` (`.get` fallback) enforced at `FATAL` severity in `services/` and `hooks/`; `QGR012` added to detect `isinstance(..., dict)` at `FATAL` severity in `services/` and `hooks/` with bulletproof path normalization |

### Compliance & Modernity Gates

1. Type Constitutionalist & Clean-Slate DB Wipe: Absolute ban on temporary `Union[NewModel, dict]`, fallback parsers (`try/except`), and backward-compatibility shims under `the_no_legacy_mandate`. All local execution data, traces, and intermediate files are permanently abandoned and deleted via `uv run python backend_v2/seed/run_seed.py local`. Upfront Seed Vault pre-sanitization is executed via `sanitize_seed_vault.py`.
2. Central Config Sovereignty: All limits in `@[backend_v2/settings.py]`.
3. Pydantic Strictness & Mutation Invariant: `ConfigDict(strict=True, extra='forbid', frozen=True)` on ALL models and DTOs. Banned `validate_assignment=True` as a placebo. Mutations to frozen models use `model_copy(update={...})` exclusively with typed instances (native Enums, validated DTOs) inside `async with _update_lock:`, while untrusted ingress data is validated via `Model.model_validate(raw_data)`.
4. Cross-Domain DTO Parity: Flutter Freezed models updated via `flutter_audit_loop.py --build` if API surface changes.
5. Python 3.14 Concurrency: `asyncio.TaskGroup` with `asyncio.Semaphore`.
6. RFC-7807 Dual-Reporting: Structured `logger.error` preceding `AppException`.
7. AST Guardrail Mandate: Static AST rules `QGR001` (reflection), `QGR002` (`.get` fallback), and `QGR012` (`isinstance(..., dict)`) enforced at `FATAL` severity in `services/` and `hooks/` via `@[scripts/backend_audit_loop.py]`, backed by dedicated unit tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`.
8. Scoped Boy Scout Rule: Technical debt cleaned exclusively in touched files.
9. Atomic Phase-Bound Quality Gate: Test modernization bound atomically to every single phase.
10. In-Flight Failure Tolerance vs. Phase Boundary Lock: The application is explicitly permitted to be in a temporary non-executable / non-compilable state across intermediate file modifications during in-flight refactor steps, but each phase's quality gate and unit test suite MUST pass 100% at the phase boundary.
11. Rule `service_layer_hydration_firewall` Deprecation: Rule `service_layer_hydration_firewall` in `@[.agents/rules/01-python-backend.md]#L176-L178` ("Repository returns raw `dict[str, Any]`") CONTRADICTS rule `repository_reconstitution_mandate` in `@[.agents/rules/01-python-backend.md]#L360-L362` ("Repository MUST return typed models"). This Epic aligns with `repository_reconstitution_mandate`. Upon Phase 2 completion, `service_layer_hydration_firewall` MUST be updated to state: "Repository returns strictly typed Pydantic Domain Models. The Service layer receives typed models directly and MUST NOT perform ad-hoc `model_validate()` on raw dicts."

### Producer-Consumer Integration Check

| Producer Layer | Consumer Layer | Current Contract | Target Contract |
|---|---|---|---|
| Database Driver (`JSONFileDriver`) | Repository | `dict[str, Any]` | `dict[str, Any]` (unchanged — correct I/O boundary) |
| Repository | Service Layer | `dict[str, Any]` | Typed Pydantic Domain Model |
| Hook Functions | Orchestrator (`DAGExecutor`) | `HookResult.state_delta: dict[str, Any]` | `HookResult.delta: HookDeltaDTO \| None` |
| `HookState.inputs` | All Hooks | `dict[str, Any]` | Typed `ExecutionInputsDTO` |
| `HookState.global_context_vars` | All Hooks | `dict[str, Any]` | Typed `GlobalContextVarsDTO` |
| LLM Execution Strategy | Synthesis Pipeline | `model_dump() -> dict -> dict mutation` | `model_copy(update={...})` with typed instances (native Enums, validated DTOs) inside `async with _update_lock:` |

---

## 3. Five-Axis System 2 Directives & Synthesis

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Foundation & Seed Vault**<br>`@[backend_v2/models/v2_core.py]`<br>`@[backend_v2/models/dtos/]`<br>`@[backend_v2/seed/seed_data.json]` | Banned: `target_locale="en"` default factories, loose `dict[str, Any]` fields in `HookState`, and placebo `validate_assignment=True` on `ConfigDict`. | Mandatory: Strict mandatory `target_locale`, new typed `ExecutionInputsDTO` [NEW], `GlobalContextVarsDTO` [NEW], `HookDeltaDTO` [NEW], and `ConfigDict(strict=True, extra="forbid", frozen=True)` across all models. | Pruned: Ad-hoc sanitization routines and unvalidated dict packing. | `uv run python scripts/audit_database_atoms.py --strict`<br>`uv run python backend_v2/seed/run_seed.py local` |
| **Repository Layer & Tests**<br>`@[backend_v2/database/repositories/]`<br>`@[backend_v2/tests/unit/database/]` (existing flat layout) | Banned: Methods returning `dict[str, Any]` and callers doing manual `.model_validate(raw_dict)`. | Mandatory: All repository methods return typed Pydantic Domain models (`frozen=True`). Update rule `service_layer_hydration_firewall` post-Phase 2 to align with `repository_reconstitution_mandate`. | Pruned: Duplicate dictionary transformation layers in repositories. | Unit test suite passing 100% with typed model assertions.<br>`uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/ --test` |
| **Orchestrator & Strategies**<br>`@[backend_v2/services/orchestrator/]`<br>`@[backend_v2/tests/unit/services/]` (existing flat layout) | Banned: `isinstance(..., dict)` checks, `.get("field")`, `model_dump()` dictionary unpacking, and unvalidated dictionary mutations in `model_copy(update={...})`. | Mandatory: Direct dot-notation access on typed `StrategyContext` and `ExecutionMetadata`; state mutations execute inside `async with _update_lock:` using `.model_copy(update=...)` strictly with typed instances (native Enums, validated DTOs). | Pruned: Defensive fallback branches and loose union types (`Model \| dict`). | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test` |
| **Hooks & God Code Decomposition**<br>`@[backend_v2/hooks/]`<br>`@[backend_v2/hooks/scoring/]` [NEW] | Banned: Monolithic 1,347 LOC (64.3 KB) `scoring.py`, in-place migration without decoupling, `_extract_payloads` dictionary traversal, loose `.get()` fallbacks, silent payload skipping via `isinstance`, and `state_delta: dict` returns. | Mandatory: Proactive decomposition of `scoring.py` into 4 isolated modules (<400 LOC each: `falsifier_hook.py`, `passivity_hook.py`, `matrix_hook.py`, `normalization_hook.py`) with Strangler Fig facade in `__init__.py`; Sub-Phase 4A is a mandatory hard gate before Sub-Phase 4B Pydantic V2 migration returning typed `HookDeltaDTO`. | Pruned: Speculative generic scoring strategy classes, visitor patterns, dynamic hook loaders, in-place state dictionary mutations, and legacy wrapper classes (`ScoringPayloadWrapper`, `StateInputWrapper`). | `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/hooks/test_scoring.py --test`<br>`uv run python scripts/backend_audit_loop.py backend_v2/hooks/ --test`<br>All decomposed modules <400 LOC; zero QGR001/002 violations. |
| **Service Layer & Identity**<br>`@[backend_v2/services/execution.py]`<br>`@[backend_v2/services/usage_service.py]` | Banned: `getattr(initiator, "organization_id", None)` and `hasattr(repo, "method")`. | Mandatory: Direct attribute access on `ExecutionMetadata` (which already contains `organization_id`, `user_id`) and explicit interface protocols. | Pruned: Speculative reflection wrappers, defensive null-coalescing chains, and unnecessary custom DTOs since `ExecutionMetadata` fields suffice. | AST Guardrail scans (`QGR001` FATAL) & Service unit tests. |
| **AST Guardrails Engine**<br>`@[scripts/_ast_guardrails.py]`<br>`@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` | Banned: Warning-only status for reflection/dict fallbacks in `services/` and `hooks/`, unvalidated `isinstance(..., dict)` checks, and relative path evasion. | Mandatory: Enforce `QGR001` (`getattr`/`hasattr`/`setattr`), `QGR002` (`.get(k, d)`), and new `QGR012` [NEW] (`isinstance(..., dict)`) at `FATAL` severity in `services/` and `hooks/` with bulletproof path normalization; `backend_audit_loop.py` stage 4/6 unconditionally halts on fatal violations. | Pruned: Blanket suppression comments without explicit `>=10` character justification; redundant runtime reflection proxies. | AST test suite execution verifying zero unsuppressed violations across `backend_v2/services/` and `backend_v2/hooks/`. |

---

## 4. Phased Execution Plan (Implementation Strategy)

> [!IMPORTANT]
> This Epic MUST be decomposed into **multiple implementation plans** via `/tier1-planner` due to its scope (~55+ files). Each plan MUST target a single phase or a tightly coupled subset of a phase. The Strangler Fig pattern requires that each phase's typed models are locked BEFORE downstream consumers are refactored.
> **PHASE 4 SUB-PHASE GATING**: Phase 4 MUST be planned as two distinct sequential implementation plans: `plan_phase_4a_scoring_god_code_decomposition.md` (structural decomposition) and `plan_phase_4b_hooks_pydantic_v2_migration.md` (Pydantic V2 state migration).
> **TYPE CONSTITUTIONALIST BAN**: ALL temporary `Union[NewModel, dict]`, fallback parsers (`try/except`), and backward-compatibility shims are strictly banned under `the_no_legacy_mandate`. Old execution records in local databases are permanently abandoned.
> **ATOMIC QUALITY GATE MANDATE**: Every phase MUST modernize its corresponding unit and integration tests *atomically in that exact phase*. Decoupling test fixes to a trailing phase is strictly prohibited.
> **IN-FLIGHT FAILURE TOLERANCE & PHASE BOUNDARY LOCK**: The program is explicitly permitted to be in a temporary non-executable / non-compilable state during intermediate in-flight file refactors within and between steps of a phase. Full compilability, 100% test pass rates, and AST Guardrail checks are enforced at each phase's completion boundary.
> **CLEAN-SLATE DB RESET (NO FALLBACKS)**: Zero backwards-compatibility fallbacks or legacy data translation shims are allowed. All local execution data is deleted via `uv run python backend_v2/seed/run_seed.py local`.

### Phase 1: Seed Vault Sanitization, Pre-Implementation Cleanups & SSOT Foundation

**Objective**: Sanitize Seed Vault data upfront, lock foundational data models, and modernize baseline models and core test fixtures.

**Target Files** (exhaustive):
- `@[backend_v2/seed/seed_data.json]` — Pre-flight audit and backfill of explicit `target_locale` for all executions and seed templates via `sanitize_seed_vault.py`.
- `@[backend_v2/models/v2_core.py]` — Remove `target_locale="en"` default_factory from `ExecutionRecord.metadata` (line 1421) and `ExecutionCoreFields.target_locale` (line 1375 under `TYPE_CHECKING`). Make `target_locale` a mandatory field without default.
- `@[backend_v2/models/execution_core.py]` — Verify `target_locale` is already mandatory (line 27). Ensure `ExecutionMetadata` covers ALL telemetry fields currently written as ad-hoc dict keys in `@[backend_v2/worker.py]`.
- `@[backend_v2/core/hook_registry.py]` — Replace `inputs: dict[str, Any]` (line 79) with typed `ExecutionInputsDTO`, `global_context_vars: dict[str, Any]` (line 78) with typed `GlobalContextVarsDTO`, and `state_delta: dict[str, Any] | None` (line 86) with typed `HookDeltaDTO | None`.
- `@[backend_v2/core/registry.py]` — Replace `TaskDefinition.metadata: dict[str, Any] | None` (line 52) with a typed `TaskMetadataDTO` or add explicit `noqa` justification; audit all remaining `dict[str, Any]` fields in `TaskRegistry`, `SchemaFieldFactory`, and related classes.
- [NEW] Create new DTO models: `HookDeltaDTO`, `ExecutionInputsDTO`, `GlobalContextVarsDTO` in `@[backend_v2/models/dtos/]`.
- **Atomic Test Modernization**: Update all tests in `@[backend_v2/tests/unit/models/]` and `@[backend_v2/tests/unit/core/]` to pass typed Pydantic models.

**Verification**: `uv run python scripts/audit_database_atoms.py --strict` (0 errors) and `uv run python backend_v2/seed/run_seed.py local`.

### Phase 2: Repository Reconstitution & DAL Test Modernization

**Objective**: Every Repository method returns a validated Pydantic Domain Model instead of `dict[str, Any]`, with 100% of repository tests modernized atomically.

**Target Files** (exhaustive — 14 repositories + tests):
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
- **Atomic Test Modernization**: Modernize all repository unit tests in `@[backend_v2/tests/unit/database/]` and existing flat repository tests (specifically `@[backend_v2/tests/unit/test_repositories_v2.py]`) to assert typed Pydantic Domain Models.
- **Rule Update Deliverable**: Upon Phase 2 completion, update `service_layer_hydration_firewall` in `@[.agents/rules/01-python-backend.md]#L176-L178` to align with the new Repository reconstitution paradigm.

**Pattern**: Each repository method calls `Model.model_validate(raw_dict)` internally and returns the typed model. Service layer never sees `dict[str, Any]`.

**Dependency**: Phase 1 (typed DTOs must exist).

### Phase 3: Orchestration & Strategy Core Refactoring & Tests

**Objective**: Eliminate ALL `isinstance(..., dict)`, `getattr()`, `.get()` branches from the orchestration engine and execution strategies, modernizing orchestrator tests atomically.

**Target Files** (exhaustive — 19 files + tests):
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
- **Atomic Test Modernization**: Modernize all orchestrator-related tests in `@[backend_v2/tests/unit/services/]` (existing flat layout, specifically `test_dag_executor_prompt_blocks.py`, `test_dag_taskgroup.py`, `test_llm_task_executor.py`, and related orchestrator test files). Replace legacy dictionary fixtures with `polyfactory` or model instances.

**Dependency**: Phase 1 (HookState typed), Phase 2 (repository returns typed).

### Phase 4: Hooks Refactoring, God Code Decomposition & Hook Tests

**Objective**: Eliminate ALL `isinstance(..., dict)`, `.get()`, and `getattr()` from hook functions. Decompose `scoring.py` (1,347 LOC, 64.3 KB) into isolated modules under `@[backend_v2/hooks/scoring/]` [NEW] first per `@[ki_god_code_prevention.md]`, and modernize hook tests atomically.

> [!IMPORTANT]
> **MANDATORY SUB-PHASE GATING**: Phase 4 MUST be executed across two sequentially gated implementation plans:
> 1. **Sub-Phase 4A (`plan_phase_4a_scoring_god_code_decomposition.md`)**: Structural `/tier3-god-code-decomposition` of `scoring.py` into `@[backend_v2/hooks/scoring/]` [NEW] package preserving 100% of existing behavior and passing `@[backend_v2/tests/unit/hooks/test_scoring.py]`.
> 2. **Sub-Phase 4B (`plan_phase_4b_hooks_pydantic_v2_migration.md`)**: Full Pydantic V2 Hook State transition across all 11 hook files and the 4 decomposed scoring modules.

#### Sub-Phase 4A: `scoring.py` God Code Decomposition (Strangler Fig Proxy Pattern)
- **Target**: Decompose `@[backend_v2/hooks/scoring.py]` (1,347 LOC, 64.3 KB) into modular `@[backend_v2/hooks/scoring/]` [NEW] package:
  - [NEW] `@[backend_v2/hooks/scoring/__init__.py]` — Strangler Fig facade re-exporting `apply_scoring_logic`, `enforce_passivity_penalty`, `matrix_scoring_hook`, `normalize_matrix_scores`, and `recalculate` with explicit `__all__` and redundant import aliases per PEP 484.
  - [NEW] `@[backend_v2/hooks/scoring/falsifier_hook.py]` — `apply_scoring_logic` hook (<200 LOC).
  - [NEW] `@[backend_v2/hooks/scoring/passivity_hook.py]` — `enforce_passivity_penalty` hook (<200 LOC).
  - [NEW] `@[backend_v2/hooks/scoring/matrix_hook.py]` — `matrix_scoring_hook` + quote evidence validation (<450 LOC).
  - [NEW] `@[backend_v2/hooks/scoring/normalization_hook.py]` — `normalize_matrix_scores` + `recalculate` (<350 LOC).
  - [NEW] `@[backend_v2/hooks/scoring/models.py]` — Strangler Fig temporary DTOs for structural decomposition. **MANDATORY SUNSET**: All models in this file MUST be either absorbed into individual hook modules or migrated to `@[backend_v2/models/dtos/]` during Sub-Phase 4B. This file MUST NOT persist beyond Sub-Phase 4B completion.
- **Pre-Requisite Verification**: Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/hooks/test_scoring.py --test` to prove zero behavioral regressions before proceeding to Sub-Phase 4B.

#### Sub-Phase 4B: Full Hooks Pydantic V2 Migration & Hook Tests
- **Target Files** (exhaustive — 11 hook files / modules + tests; all `scoring/` modules [NEW] created in Sub-Phase 4A):
  - [NEW] `@[backend_v2/hooks/scoring/falsifier_hook.py]` (created in Sub-Phase 4A)
  - [NEW] `@[backend_v2/hooks/scoring/passivity_hook.py]` (created in Sub-Phase 4A)
  - [NEW] `@[backend_v2/hooks/scoring/matrix_hook.py]` (created in Sub-Phase 4A)
  - [NEW] `@[backend_v2/hooks/scoring/normalization_hook.py]` (created in Sub-Phase 4A)
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
- **Implementation**:
  - Replace `HookState.inputs: dict[str, Any]` with typed `ExecutionInputsDTO`.
  - Replace `HookState.global_context_vars: dict[str, Any]` with typed `GlobalContextVarsDTO`.
  - Replace `HookResult.state_delta: dict[str, Any] | None` with typed `HookDeltaDTO | None`.
  - Eliminate all `isinstance(..., dict)` checks, `.get()`, and `getattr()`.
- **Atomic Test Modernization**: Modernize all hook unit tests in `@[backend_v2/tests/unit/hooks/]`. Verify 4 ISTQB partitions (structured dict, list, string, falsy).

**Dependency**: Phase 1 (HookDeltaDTO, typed HookState), Sub-Phase 4A (decomposed `scoring/` package).

### Phase 5: Service Layer, Utility Services & Service Tests

**Objective**: Eliminate ALL `getattr(initiator, "organization_id", None)` chains (replace with direct attribute access on `ExecutionMetadata` which already contains `organization_id` at `@[backend_v2/models/execution_core.py]#L47-L50`), `isinstance(x, dict)` branches, and `hasattr()` interface discovery from the service layer, modernizing service tests atomically.

**Target Files** (exhaustive — 11 files + tests):
- `@[backend_v2/services/execution.py]` (**15x getattr** `organization_id` + 2x getattr other — critical; replace with direct access on `ExecutionMetadata.organization_id`)
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
- **Atomic Test Modernization**: Modernize all service unit tests in `@[backend_v2/tests/unit/services/]`.

**Dependency**: Phase 2 (repositories return typed models), Phase 1 (typed DTOs).

### Phase 6: Background Workers & Storage

**Objective**: Eliminate dict mutations in `worker.py` metadata handling and modernize worker tests atomically.

**Target Files**:
- `@[backend_v2/worker.py]` (dict mutations in metadata fields)
- `@[backend_v2/tests/unit/test_worker.py]`

**Dependency**: Phase 1 (`ExecutionMetadata` covers all telemetry fields).

### Phase 7: AST Guardrail Hardening (Mathematical Drift Prevention)

**Objective**: Validate that `QGR001` (getattr/hasattr) and `QGR002` (.get(key, default)) are locked at FATAL severity in `services/` and `hooks/`, introduce new rule `QGR012` (`isinstance(..., dict)` detection at FATAL severity in `services/` and `hooks/`), harden path normalization against relative path evasion, and add automated AST verification tests to make it mathematically impossible for new duck-typing or anti-patterns to enter the codebase.

**Target Files**:
- `@[scripts/_ast_guardrails.py]` — Add `QGR012` rule (`isinstance(..., dict)` banned in `services/` and `hooks/`), enforce `FATAL` severity for `QGR001`, `QGR002`, and `QGR012`, and implement robust path normalization (`is_services_or_hooks = any(p in norm_path for p in ["/services/", "/hooks/", "services/", "hooks/"])`)
- `@[scripts/backend_audit_loop.py]` — Ensure FATAL violations unconditionally block the audit loop with `sys.exit(1)`
- `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` — Verify 0 unsuppressed violations across entire `backend_v2/services/` and `backend_v2/hooks/`, add test partitions for `QGR012`, and verify relative path FATAL enforcement

**Dependency**: Phases 1-6 (all existing violations and test suites must be fully resolved before final global quality gate verification).

---

## 5. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)

1. **Zero `isinstance(..., dict)` in `services/` and `hooks/`**: Verified by `grep_search "isinstance.*dict" backend_v2/services/ --include="*.py" --exclude="*test*"` returning 0 results (excluding legitimately suppressed `noqa` lines).
2. **Zero `getattr(obj, "field", default)` in `services/` and `hooks/`**: Verified by deterministic grep returning 0 unsuppressed results.
3. **Zero `hasattr()` in `services/`**: Verified by deterministic grep returning 0 unsuppressed results.
4. **Zero repository methods returning `dict[str, Any]`**: All repository read methods return typed Pydantic Domain Models.
5. **Zero silent defaults on mandatory business fields**: `target_locale` has no default value; missing locale causes immediate `ValidationError`.
6. **100% typed HookState**: `inputs`, `global_context_vars`, and `state_delta` are typed DTOs.
7. **AST Guardrails QGR001/QGR002/QGR012 at FATAL severity** in `services/` and `hooks/`, with zero unsuppressed violations.
8. **All tests pass atomically** via `uv run python scripts/backend_audit_loop.py backend_v2/ --test` with >90% coverage.
9. **`scoring.py` decomposed** into `@[backend_v2/hooks/scoring/]` [NEW] package with every module <400 LOC, explicit Strangler Fig proxy in `__init__.py`, and zero unsuppressed `QGR001`/`QGR002` violations (God Code Prevention mandate).
10. **Seed Vault verified**: `uv run python scripts/audit_database_atoms.py --strict` returns 0 issues.
11. **Zero unvalidated raw dictionary mutations in `model_copy`**: All `model_copy(update={...})` calls pass strictly typed model instances or native Enums inside `async with _update_lock:`.
12. **Zero `validate_assignment=True` placebos**: `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` enforced across all domain models and DTOs.

### Automated Unit Tests

```powershell
uv run python scripts/backend_audit_loop.py backend_v2/ --test
```

### AST Guardrails & Structural Tests

1. **AST Rule QGR012**: `test_qgr012_isinstance_dict_detection` — Detects `isinstance(..., dict)` in `services/` and `hooks/` at `FATAL` severity without valid `noqa` suppression.
2. **AST Rule QGR001**: `test_qgr001_fatal_in_services_and_hooks` — Detects `getattr(obj, "field", default)`, `hasattr()`, and `setattr()` in `services/` and `hooks/` at `FATAL` severity.
3. **AST Rule QGR002**: `test_qgr002_fatal_in_services_and_hooks` — Detects `.get(key, default)` in `services/` and `hooks/` at `FATAL` severity.
4. **AST Path Normalization**: `test_ast_guardrails_relative_path_fatal` — Verifies that relative paths (specifically `services/sample.py` and `hooks/sample.py`) properly trigger `FATAL` severity.
5. **Full Codebase AST Scan**: `test_zero_unsuppressed_guardrail_violations` — Verifies 0 unsuppressed `FATAL` violations across `backend_v2/services/` and `backend_v2/hooks/`.
6. **Repository Signature AST Test**: `test_repositories_return_typed_models` — Verifies no repository method signature contains `-> dict[str, Any]`.

### Manual Verification Steps

1. Full database re-seed: `uv run python backend_v2/seed/run_seed.py local`
2. Execute a full workflow end-to-end and verify PDF generation.
3. Verify Flutter client still renders correctly after any DTO surface changes.

### MANDATORY Final E2E REST API Verification Gate

```powershell
$env:RUN_LIVE_E2E = "true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 6. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.

### Key Governance References

| Rule / KI | Relevance |
|---|---|
| `@[.agents/rules/00-antigravity-core.md]` `zero_service_layer_fallbacks` | Foundational ban on `.get()`, `getattr()`, fallback chains in services |
| `@[.agents/rules/00-antigravity-core.md]` `the_zero_compromise_pledge` | Strict Pydantic enforcement; crash on unexpected keys |
| `@[.agents/rules/00-antigravity-core.md]` `the_duct_tape_ban` | Ban on `try...except Exception:`, empty returns, silent bypasses |
| `@[.agents/rules/00-antigravity-core.md]` `the_no_legacy_mandate` | Ban on backwards compatibility; ruthlessly delete obsolete code |
| `@[.agents/rules/01-python-backend.md]` `the_duct_tape_ban` | `.get("key", default)` explicitly banned |
| `@[.agents/rules/02_flutter_desktop.md]` `silent_json_fallbacks` | Strict Flutter Freezed JSON parsing (`disallowUnrecognizedKeys: true`) on DTO changes |
| `@[.agents/rules/03_seed_vault.md]` `vault_mutation_protocol` | Mandatory 6-step protocol for Phase 1 `seed_data.json` sanitization |
| `@[.agents/rules/00-antigravity-core.md]` `ast_guardrail_mandate` | New architectural rules require AST enforcement tests |
| `@[.agents/rules/00-antigravity-core.md]` `anti_tdd_trap` | Never weaken production code to satisfy legacy tests |
| `@[ki_god_code_prevention.md]` | `scoring.py` (65 KB) requires decomposition before migration |
| `@[ki_python_314_concurrency_strictness.md]` | Global `ConfigDict(strict=True, extra='forbid')` on all models |
| `@[ki_seed_vault_verification_and_sanitization.md]` | Upfront Seed Vault pre-flight sanitization and audit protocols |
| `@[ki_ast_guardrail_engine.md]` | AST guardrail visitor mechanics and zero-reflection self-testing |
| `@[ki_app_error_boundary.md]` | UI exception boundary architecture preventing silent failure "Ghost Bugs" |
| `@[docs/CLEAN_PYDANTIC_TRANSITION_CATALOG.md]` | Authoritative reference catalog with 9 anti-pattern archetypes |

### Chronological Drift & Hierarchy of Precedence Invariant
1. **Supreme Rule Authority**: The core rules in `@[.agents/rules/]` and the Phase 7 invariants in this Epic (`QGR001`, `QGR002`, and `QGR012` enforced at `FATAL` severity in `services/` and `hooks/`) possess absolute system authority and strictly override any historical advisory `WARNING` designations documented in older Knowledge Item snapshots (specifically `@[ki_ast_guardrail_engine.md]` which describes QGR001/QGR002 at `WARNING` severity).
2. **Zero-Fallback Legacy Ban**: No legacy data translation shims or backward-compatibility parsing branches may be introduced based on historical KI descriptions. All data models must strictly conform to Pydantic V2 `ConfigDict(strict=True, extra="forbid", frozen=True)`.
3. **Rule Contradiction Resolution**: Rule `service_layer_hydration_firewall` (`@[.agents/rules/01-python-backend.md]#L176-L178`) is superseded by `repository_reconstitution_mandate` (`@[.agents/rules/01-python-backend.md]#L360-L362`) effective with Phase 2 of this Epic. The executing agent MUST update `service_layer_hydration_firewall` to reflect the new paradigm as a Phase 2 deliverable.

