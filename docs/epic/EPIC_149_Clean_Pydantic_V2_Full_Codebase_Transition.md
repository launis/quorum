<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
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
Despite strict architectural rules in `@[.agents/rules/00-antigravity-core.md]` and `@[.agents/rules/01-python-backend.md]` (`zero_service_layer_fallbacks`, `the_zero_compromise_pledge`, `no_naked_dicts_in_state`), a systematic `grep_search` audit (August 2026) revealed **~55+ production files** containing anti-patterns across **10 distinct archetypes**. This technical debt forces:

1. **Every downstream consumer** to write defensive `isinstance(x, dict)` branches (50+ instances in `services/`, 26+ in `hooks/`).
2. **Every service method** accessing `initiator.organization_id` to use `getattr(initiator, "organization_id", None)` (15 instances in `@[backend_v2/services/execution.py]` alone).
3. **Every repository consumer** to call `Model.model_validate(raw_dict)` ad-hoc instead of receiving typed domain models directly.
4. **Silent locale masking** where `target_locale="en"` default in `@[backend_v2/models/v2_core.py]#L1421` allows executions to silently run in the wrong language.
5. **Client-Backend Schema Fracture** where Flutter client (`client_app_v2`) transmits legacy untyped fields (`strictness_level`, `scoring_strategy`) without `target_locale` in `ExecutionClient.startExecution`, causing FastAPI ingress 422 errors, and deserializes SSE streams into an incomplete `ExecutionRecord` Freezed model with `disallowUnrecognizedKeys: true`, causing silent stream crashes and UI freezing.
6. **Cache Boundary Leak (Välimuistin tyyppivuoto)** where Redis cache and blob storage deserialization (`driver.read()`, `redis.get()`) relies on standard Python `json.loads()`, returning raw `dict` objects into `@[backend_v2/database/repositories/execution.py]#L92-L100` (`data[field] = json.loads(decoded)`) and `@[backend_v2/worker.py]`, leaking dictionaries back into caller services and worker pipelines.

### Strategic Scope
This Epic enforces the **Strangler Fig** migration pattern: each phase locks a new layer's types, makes existing consumers compile-fail on `dict` usage, fixes all consumers and atomically modernizes their corresponding tests, and runs the global quality gate before proceeding to the next layer. Furthermore, Phase 1 injects upfront Seed Data Vault sanitization to guarantee clean-boot stability before removing silent schema defaults. The authoritative reference catalog is `@[docs/CLEAN_PYDANTIC_TRANSITION_CATALOG.md]`.

### Clean-Slate Database Wipe & Absolute Zero-Fallback Mandate (Type Constitutionalist)
- **Approved Best Practice (Type Constitutionalist)**:
  - **Finding**: During massive refactoring (~55+ files across repositories, services, orchestrator, hooks), developers/agents are tempted to use `Union[NewModel, dict]` or `try/except` blocks to maintain a working state mid-epic or parse old database records.
  - **Action Taken**: Invoked `the_no_legacy_mandate` and `the_zero_compromise_pledge`. ALL temporary unions, fallback parsers (`try/except`), dictionary coercion chains (`getattr`, `.get()`), and backward-compatibility shims are STRICTLY FORBIDDEN.
- **Clean-Slate Database Wipe & Residual Poisoning Elimination**:
  - The local database path SSOT is [backend_v2/settings.py](file:///c:/src/quorum/backend_v2/settings.py#L473-L481) (`prod_db_path = data/db_v2.json`), driven by [TinyDBClient](file:///c:/src/quorum/backend_v2/database/wrapper.py#L650).
  - All local historical execution records, dirty runtime traces, and orphaned storage files are completely purged. `uv run python backend_v2/seed/run_seed.py local` drops all tables from `data/db_v2.json` and purges `data/files/executions/`.
  - Upfront in Phase 1, all vestigial 0-byte database artifacts (`data/app.db`, `data/app.sqlite`) are permanently removed from disk, and `run_seed.py` is modernized to dynamically source its target path from `get_settings().prod_db_path`.
  - Incompatible historical execution records on disk are permanently abandoned with zero requirement for data migration.

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
| Cache / Blob `json.loads()` -> `dict` | 0 | 0 | 0 | 4+ | **4+** |
| Loose Union types (`Model \| dict`) | 0 | 0 | 3 | 0 | **3** |
| Silent mandatory defaults | 0 | 0 | 0 | 0 | **2** (in `models/`) |
| **TOTAL VIOLATIONS** | | | | | **~211+** |

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
| `json.loads(decoded)` / `json.loads(raw_cache)` in repository blob hydration and cache retrieval | `@[backend_v2/database/repositories/execution.py]#L92-L100`, `@[backend_v2/worker.py]` | REPLACE with Rust-level `model_validate_json()` / `TypeAdapter(T).validate_json()` |
| `ExecutionClient.startExecution(strictnessLevel, scoringStrategy)` | `@[client_app_v2/lib/core/api/execution_client.dart]#L26-L43` | REPLACE with typed `@[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]` [NEW] |
| `allowedKeys` duct-tape key stripping in `executionList` | `@[client_app_v2/lib/features/execution/controllers/execution_controller.dart]#L40-L61` | DELETE; enforce complete Freezed `ExecutionRecord` 1:1 schema parity |
| `NewExecutionController.startExecution` duplicate `dio.post` | `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]#L44-L65` | DELETE; unify all execution requests through `executionClientProvider` |
| Vestigial 0-byte database files | `[DELETE]` `@[data/app.db]`, `[DELETE]` `@[data/app.sqlite]` | DELETE permanently in Phase 1 |

### Retained SSOT Invariants (What We Will RETAIN)

| Invariant | Justification |
|---|---|
| `ConfigDict(strict=True, extra="forbid", frozen=True)` on all domain models and DTOs | Already enforced; this Epic extends coverage to ALL DTOs and state objects. `validate_assignment=True` is explicitly banned as a placebo/dead code on frozen models (does not validate `model_copy`). |
| Database driver (`JSONFileDriver`, `TinyDBDriver`) returns `dict[str, Any]` | Correct: the lowest I/O layer returns raw dicts; the Repository layer reconstitutes them into typed models |
| `model_dump()` for serialization to database/JSON | Correct: `model_dump()` is valid at the serialization boundary (Repository write path). Banned only for intermediate state manipulation in services |
| `TypedCacheService` / Inbound Cache Hydration Firewall with auto-eviction on `ValidationError` | Redis and storage retrieval MUST deserialize directly via Rust parser (`model_validate_json()`) and evict stale/zombie cache entries (`redis.delete()`) on schema drift |
| `noqa: QGR001/002/003` with valid `[REASON: ...]` justifications | Retained for legitimate edge cases (specifically: LLM adapter polymorphic message parsing in `vertex_adapter.py`/`ai_studio_adapter.py`/`base_adapter.py`, worker DLQ catch-all in `worker.py`, `LaxScoringStrategy` enum-or-string handling in `blueprint.py`) |
| `@[scripts/_ast_guardrails.py]` QGR rule definitions | Retained and hardened: `QGR001` (reflection/mutation) and `QGR002` (`.get` fallback) enforced at `FATAL` severity in `services/` and `hooks/`; `QGR012` added to detect `isinstance(..., dict)` at `FATAL` severity in `services/` and `hooks/` with bulletproof path normalization |

### Compliance & Modernity Gates

1. Type Constitutionalist & Clean-Slate DB Wipe: Absolute ban on temporary `Union[NewModel, dict]`, fallback parsers (`try/except`), and backward-compatibility shims under `the_no_legacy_mandate`. All local execution data, traces, and intermediate files are permanently abandoned and deleted via `uv run python backend_v2/seed/run_seed.py local`. Upfront Seed Vault pre-sanitization is executed via `sanitize_seed_vault.py`.
2. Central Config Sovereignty: All limits and database paths in `@[backend_v2/settings.py]`.
3. Pydantic Strictness & Mutation Invariant: `ConfigDict(strict=True, extra='forbid', frozen=True)` on ALL models and DTOs. Banned `validate_assignment=True` as a placebo. Mutations to frozen models use `model_copy(update={...})` exclusively with typed instances (native Enums, validated DTOs) inside `async with _update_lock:`, while untrusted ingress data is validated via `Model.model_validate(raw_data)`.
4. Cross-Domain DTO & SDUI Semantic Parity: Flutter Freezed models (`ExecutionRecord`, `ExecutionCreateRequestDto` [NEW]) updated synchronously in Phase 1 via `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build` and validated against `backend_v2/tests/integration/test_sdui_semantic_parity.py` and `client_app_v2/bin/e2e_simulation.dart`.
5. Python 3.14 Concurrency: `asyncio.TaskGroup` with `asyncio.Semaphore`.
6. RFC-7807 Dual-Reporting: Structured `logger.error` preceding `AppException`.
7. AST Guardrail Mandate: Static AST rules `QGR001` (reflection), `QGR002` (`.get` fallback), and `QGR012` (`isinstance(..., dict)`) enforced at `FATAL` severity in `services/` and `hooks/` via `@[scripts/backend_audit_loop.py]`, backed by dedicated unit tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`.
8. Scoped Boy Scout Rule: Technical debt cleaned exclusively in touched files.
9. Atomic Phase-Bound Quality Gate: Test modernization bound atomically to every single phase.
10. In-Flight Failure Tolerance vs. Phase Boundary Lock: The application is explicitly permitted to be in a temporary non-executable / non-compilable state across intermediate file modifications during in-flight refactor steps, but each phase's quality gate and unit test suite MUST pass 100% at the phase boundary.
11. Rule `service_layer_hydration_firewall` Deprecation: Rule `service_layer_hydration_firewall` in `@[.agents/rules/01-python-backend.md]#L176-L178` ("Repository returns raw `dict[str, Any]`") CONTRADICTS rule `repository_reconstitution_mandate` in `@[.agents/rules/01-python-backend.md]#L360-L362` ("Repository MUST return typed models"). This Epic aligns with `repository_reconstitution_mandate`. Upon Phase 2 completion, `service_layer_hydration_firewall` MUST be updated to state: "Repository returns strictly typed Pydantic Domain Models. The Service layer receives typed models directly and MUST NOT perform ad-hoc `model_validate()` on raw dicts."
12. Producer-Before-Consumer Dependency Ordering: To prevent 100% CI deadlock during phased execution, Data Producers (Phase 3: Hooks) MUST be refactored to emit typed models (`HookDeltaDTO`) and accept typed state (`ExecutionInputsDTO`) BEFORE Consumers (Phase 4: Orchestrator & Strategies) remove defensive fallbacks and switch to strict typed dot-notation.
13. Startup Pre-Flight Schema Verification: To prevent silent startup crashes on residual dirty databases, FastAPI lifespan startup in `backend_v2/main.py` validates that database root documents conform to strict V2 models and cleanly aborts with explicit instructions to run `run_seed.py local` if unmigrated records exist.
14. Inbound Cache Hydration Firewall & Zombie Cache Eviction: All Redis cache retrievals and repository blob deserializations MUST use native Rust Pydantic V2 `model_cls.model_validate_json(raw_bytes)` or `TypeAdapter(T).validate_json(raw_bytes)`. Standard `json.loads()` returning `dict` is strictly banned at cache and storage boundaries. On `ValidationError` (schema mismatch or zombie cache caused by model migrations), the cache adapter logs an RFC 7807 telemetry warning, evicts the stale key via `redis.delete()`, and returns `None` (cache miss) for clean, safe recalculation.

### Producer-Consumer Integration Check

| Producer Layer | Consumer Layer | Current Contract | Target Contract |
|---|---|---|---|
| Database Driver (`JSONFileDriver`) | Repository | `dict[str, Any]` | `dict[str, Any]` (unchanged — correct I/O boundary) |
| Repository | Service Layer | `dict[str, Any]` | Typed Pydantic Domain Model |
| Redis Cache & Storage Drivers (`driver.read`, `redis.get`) | Repositories & Worker Pipelines | `raw_bytes -> json.loads() -> dict[str, Any]` | `raw_bytes -> model_validate_json() / TypeAdapter(T).validate_json() -> Typed Pydantic Model` |
| Hook Functions (Phase 3) | Orchestrator (`DAGExecutor`, Phase 4) | `HookResult.state_delta: dict[str, Any]` | `HookResult.delta: HookDeltaDTO \| None` |
| `HookState.inputs` | All Hooks (Phase 3) | `dict[str, Any]` | Typed `ExecutionInputsDTO` |
| `HookState.global_context_vars` | All Hooks (Phase 3) | `dict[str, Any]` | Typed `GlobalContextVarsDTO` |
| LLM Execution Strategy | Synthesis Pipeline | `model_dump() -> dict -> dict mutation` | `model_copy(update={...})` with typed instances (native Enums, validated DTOs) inside `async with _update_lock:` |
| Flutter `ExecutionClient` (Phase 1) | FastAPI `/executions/` Ingress | Naked `Map<String, dynamic>` (missing `target_locale`, with `strictness_level`) | Typed `ExecutionCreateRequestDto` [NEW] matching `ExecutionCreate` 1:1 |
| FastAPI `stream_status` SSE | Flutter `ExecutionController._connectToStream` | Monolithic `ExecutionRecord` JSON dump -> Incomplete Dart Freezed model | Full 1:1 Freezed `ExecutionRecord` schema with `disallowUnrecognizedKeys: true` |

---

## 3. Five-Axis System 2 Directives & Synthesis

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Foundation, Seed Vault, Lifecycle & Client Ingress**<br>`@[backend_v2/models/v2_core.py]`<br>`@[backend_v2/models/dtos/]`<br>`@[backend_v2/seed/seed_data.json]`<br>`@[backend_v2/seed/run_seed.py]`<br>`@[client_app_v2/lib/features/execution/models/]`<br>`@[client_app_v2/lib/core/api/execution_client.dart]` | Banned: `target_locale="en"` default factories, loose `dict[str, Any]` fields in `HookState`, placebo `validate_assignment=True`, naked Dart `Map<String, dynamic>` API calls, `allowedKeys` duct-tape filter, hardcoded seeder paths (`PROJECT_ROOT / "data" / "db_v2.json"`), leaving orphaned files (`app.db`, `app.sqlite`), and silent `catch (e)` in SSE stream. | Mandatory: Strict mandatory `target_locale`, new typed `ExecutionInputsDTO` [NEW], `GlobalContextVarsDTO` [NEW], `HookDeltaDTO` [NEW], `ConfigDict(strict=True, extra="forbid", frozen=True)`, Dart Freezed `ExecutionCreateRequestDto` [NEW], complete 1:1 Freezed `ExecutionRecord` schema with `disallowUnrecognizedKeys: true`, permanent purge of vestigial 0-byte `.db`/`.sqlite` files, dynamic DB path resolution via `get_settings().prod_db_path`, and lifespan pre-flight DB validation. | Pruned: Ad-hoc sanitization routines, unvalidated dict packing, duplicate `NewExecutionController` start mutations, legacy parameters (`strictness_level`, `scoring_strategy`), and complex SQL/Alembic migration engines (clean-slate wipe is sovereign for local development). | `uv run python scripts/audit_database_atoms.py --strict`<br>`uv run python backend_v2/seed/run_seed.py local`<br>`uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build`<br>`uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` |
| **Repository Layer & Tests**<br>`@[backend_v2/database/repositories/]`<br>`@[backend_v2/tests/unit/database/]` (existing flat layout) | Banned: Methods returning `dict[str, Any]` and callers doing manual `.model_validate(raw_dict)`. | Mandatory: All repository methods return typed Pydantic Domain models (`frozen=True`). Update rule `service_layer_hydration_firewall` post-Phase 2 to align with `repository_reconstitution_mandate`. | Pruned: Duplicate dictionary transformation layers in repositories. | Unit test suite passing 100% with typed model assertions.<br>`uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/ --test` |
| **Redis Cache Service & Storage Hydration**<br>`[NEW]` `@[backend_v2/services/cache/]`<br>`@[backend_v2/database/repositories/execution.py]`<br>`@[backend_v2/worker.py]` | Banned: `json.loads()` for cache/blob deserialization, returning `dict[str, Any]` to caller services, `isinstance(data, dict)`, and silent `except Exception: pass`. | Mandatory: Generic `get_cached[T: BaseModel](key: str, model_cls: type[T]) -> T \| None` using `model_cls.model_validate_json(raw_bytes)`. On `ValidationError`, log RFC 7807 warning, delete poisoned key (`redis.delete`), and return `None`. Repository blob hydration uses `TypeAdapter(list[StepOutputDTO]).validate_json(blob_data)` and `FrozenContextDTO.model_validate_json(blob_data)`. | Pruned: Heavy third-party caching frameworks (`aiocache`, `redis-om`). A lightweight ~60 LOC generic async helper wrapping `arq` / `redis.asyncio` pool is sovereign. | Unit test verifying that invalid JSON or mismatched schema in Redis raises `ValidationError`, triggers `redis.delete()`, and returns `None`. AST rule `QGR012` FATAL scan.<br>`uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/execution.py --test` |
| **Hooks & God Code Decomposition (PRODUCERS FIRST)**<br>`@[backend_v2/hooks/]`<br>`[NEW]` `@[backend_v2/hooks/scoring/]` | Banned: Monolithic 1,347 LOC (64.3 KB) `scoring.py`, in-place migration without decoupling, `_extract_payloads` dictionary traversal, loose `.get()` fallbacks, silent payload skipping via `isinstance`, and `state_delta: dict` returns. | Mandatory: Proactive decomposition of `scoring.py` into 4 isolated modules (<400 LOC each: `falsifier_hook.py`, `passivity_hook.py`, `matrix_hook.py`, `normalization_hook.py`) with Strangler Fig facade in `__init__.py`; Sub-Phase 3A is a mandatory hard gate before Sub-Phase 3B Pydantic V2 migration returning typed `HookDeltaDTO`. | Pruned: Speculative generic scoring strategy classes, visitor patterns, dynamic hook loaders, in-place state dictionary mutations, and legacy wrapper classes (`ScoringPayloadWrapper`, `StateInputWrapper`). | `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/hooks/test_scoring.py --test`<br>`uv run python scripts/backend_audit_loop.py backend_v2/hooks/ --test`<br>All decomposed modules <400 LOC; zero QGR001/002 violations. |
| **Orchestrator & Strategies (CONSUMERS SECOND)**<br>`@[backend_v2/services/orchestrator/]`<br>`@[backend_v2/tests/unit/services/]` (existing flat layout) | Banned: `isinstance(..., dict)` checks, `.get("field")`, `model_dump()` dictionary unpacking, and unvalidated dictionary mutations in `model_copy(update={...})`. | Mandatory: Direct dot-notation access on typed `StrategyContext` and `ExecutionMetadata`; state mutations execute inside `async with _update_lock:` using `.model_copy(update=...)` strictly with typed instances (native Enums, validated DTOs). | Pruned: Defensive fallback branches and loose union types (`Model \| dict`). | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test` |
| **Service Layer & Identity**<br>`@[backend_v2/services/execution.py]`<br>`@[backend_v2/services/usage_service.py]` | Banned: `getattr(initiator, "organization_id", None)` and `hasattr(repo, "method")`. | Mandatory: Direct attribute access on `ExecutionMetadata` (which already contains `organization_id`, `user_id`) and explicit interface protocols. | Pruned: Speculative reflection wrappers, defensive null-coalescing chains, and unnecessary custom DTOs since `ExecutionMetadata` fields suffice. | AST Guardrail scans (`QGR001` FATAL) & Service unit tests. |
| **AST Guardrails Engine**<br>`@[scripts/_ast_guardrails.py]`<br>`@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` | Banned: Warning-only status for reflection/dict fallbacks in `services/` and `hooks/`, unvalidated `isinstance(..., dict)` checks, and relative path evasion. | Mandatory: Enforce `QGR001` (`getattr`/`hasattr`/`setattr`), `QGR002` (`.get(k, d)`), and new `QGR012` (`isinstance(..., dict)`) at `FATAL` severity in `services/` and `hooks/` with bulletproof path normalization; `backend_audit_loop.py` stage 4/6 unconditionally halts on fatal violations. | Pruned: Blanket suppression comments without explicit `>=10` character justification; redundant runtime reflection proxies. | AST test suite execution verifying zero unsuppressed violations across `backend_v2/services/` and `backend_v2/hooks/`. |

---

## 4. Phased Execution Plan (Implementation Strategy)

> [!IMPORTANT]
> This Epic MUST be decomposed into **multiple implementation plans** via `/tier1-planner` due to its scope (~55+ files). Each plan MUST target a single phase or a tightly coupled subset of a phase. The Strangler Fig pattern requires that each phase's typed models are locked BEFORE downstream consumers are refactored.
> **PHASE 3 SUB-PHASE GATING**: Phase 3 MUST be planned as two distinct sequential implementation plans: `plan_phase_3a_scoring_god_code_decomposition.md` (structural decomposition) and `plan_phase_3b_hooks_pydantic_v2_migration.md` (Pydantic V2 state migration).
> **PRODUCER-BEFORE-CONSUMER INVARIANT**: Phase 3 (Hooks / Producers) MUST be refactored and pass unit tests before Phase 4 (Orchestrator / Consumers) to prevent 100% CI deadlock from typed consumers receiving unmigrated raw dictionaries.
> **TYPE CONSTITUTIONALIST BAN**: ALL temporary `Union[NewModel, dict]`, fallback parsers (`try/except`), and backward-compatibility shims are strictly banned under `the_no_legacy_mandate`. Old execution records in local databases are permanently abandoned.
> **ATOMIC QUALITY GATE MANDATE**: Every phase MUST modernize its corresponding unit and integration tests *atomically in that exact phase*. Decoupling test fixes to a trailing phase is strictly prohibited.
> **IN-FLIGHT FAILURE TOLERANCE & PHASE BOUNDARY LOCK**: The program is explicitly permitted to be in a temporary non-executable / non-compilable state during intermediate in-flight file refactors within and between steps of a phase. Full compilability, 100% test pass rates, and AST Guardrail checks are enforced at each phase's completion boundary.
> **CLEAN-SLATE DB RESET (NO FALLBACKS)**: Zero backwards-compatibility fallbacks or legacy data translation shims are allowed. All local execution data is deleted via `uv run python backend_v2/seed/run_seed.py local`.

### Phase 1: Seed Vault Sanitization, Pre-Implementation Cleanups & SSOT Foundation

**Objective**: Sanitize Seed Vault data upfront, lock foundational data models, modernize baseline models and core test fixtures, and synchronize Flutter client execution DTOs and API clients to prevent 422 ingress errors and SSE stream deserialization crashes.

**Target Files** (exhaustive):
- `@[backend_v2/seed/seed_data.json]` — Pre-flight audit and backfill of explicit `target_locale` for all executions and seed templates via `sanitize_seed_vault.py`.
- `@[backend_v2/seed/run_seed.py]` — Modernize seeder to dynamically resolve database path from `get_settings().prod_db_path` (@[backend_v2/settings.py#L473-L481]), unconditionally drop all tables, wipe `data/files/executions/`, and ensure clean lifecycle without hardcoded relative paths.
- `[DELETE]` `@[data/app.db]`, `[DELETE]` `@[data/app.sqlite]` — Permanently delete legacy 0-byte vestigial database files to prevent residual poisoning assumptions.
- `@[backend_v2/main.py]` — Add Lifespan startup pre-flight schema check that validates `system_config` and `workflows` against strict models, cleanly aborting with instructions to run `run_seed.py local` if dirty/unmigrated records are detected.
- `@[backend_v2/models/v2_core.py#L1368-L1431]` — Remove `target_locale="en"` default_factory from `ExecutionRecord.metadata` (line 1421) and `ExecutionCoreFields.target_locale` (line 1375 under `TYPE_CHECKING`). Make `target_locale` a mandatory field without default.
- `@[backend_v2/models/execution_core.py#L22-L82]` — Verify `target_locale` is already mandatory (line 27). Ensure `ExecutionMetadata` covers ALL telemetry fields currently written as ad-hoc dict keys in `@[backend_v2/worker.py]`.
- `@[backend_v2/core/hook_registry.py#L68-L79]` & `@[backend_v2/core/hook_registry.py#L82-L86]` — Replace `inputs: dict[str, Any]` (line 79) with typed `ExecutionInputsDTO`, `global_context_vars: dict[str, Any]` (line 78) with typed `GlobalContextVarsDTO`, and `state_delta: dict[str, Any] | None` (line 86) with typed `HookDeltaDTO | None`.
- `@[backend_v2/core/registry.py#L33-L52]` — Replace `TaskDefinition.metadata: dict[str, Any] | None` (line 52) with a typed `TaskMetadataDTO` or add explicit `noqa` justification; audit all remaining `dict[str, Any]` fields in `TaskRegistry`, `SchemaFieldFactory`, and related classes.
- `[NEW]` `@[backend_v2/models/dtos/hook_state.py]` — Create new DTO models: `HookDeltaDTO`, `ExecutionInputsDTO`, `GlobalContextVarsDTO` in `models/dtos/`.
- `[NEW]` `@[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]` — Create strictly typed Freezed request model with `workflow_id`, `target_locale`, `raw_inputs`, and optional `profile_id` (`disallowUnrecognizedKeys: true`).
- `@[client_app_v2/lib/features/execution/models/execution_record.dart]` — Update Dart Freezed model to 1:1 schema parity with backend `ExecutionRecord`, adding missing fields (`activeProfileId`, `rawInputs`, `durationMs`, `updatedAt`, `completedAt`, `createdBy`, `organizationId`, `cumulativeSynthesisTokens`, `cumulativeSynthesisCost`, `modelsUsed`).
- `@[client_app_v2/lib/core/api/execution_client.dart#L26-L43]` — Refactor `startExecution` to accept `ExecutionCreateRequestDto`, send `target_locale`, and eliminate obsolete legacy parameters (`strictness_level`, `scoring_strategy`).
- `@[client_app_v2/lib/features/execution/controllers/execution_controller.dart#L40-L61]` — Delete `allowedKeys` duct-tape dictionary filter in `executionList`, and remove silent exception swallowing in `_connectToStream`.
- `@[client_app_v2/lib/features/execution/views/new_execution_view.dart#L44-L65]` — Remove duplicate `dio.post` in `NewExecutionController` and unify execution requests through `executionClientProvider`.
- `@[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]` — Pass active `target_locale` resolved from `Localizations.localeOf(context).languageCode`.
- **Atomic Test Modernization**: Update all tests in `@[backend_v2/tests/unit/models/test_v2_core.py]`, `@[backend_v2/tests/unit/models/test_execution_core.py]`, `@[backend_v2/tests/unit/core/test_registry.py]`, `@[backend_v2/tests/unit/core/test_hook_registry.py]`, `@[backend_v2/tests/unit/seed/test_run_seed.py]`, and `@[client_app_v2/test/features/execution/controllers/execution_controller_test.dart]` to pass typed Pydantic and Freezed models.

**Verification**: `uv run python scripts/audit_database_atoms.py --strict` (0 errors), `uv run python backend_v2/seed/run_seed.py local`, `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build`, and `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.

### Phase 2: Repository Reconstitution, Storage Blob Hydration & DAL Tests

**Objective**: Every Repository method returns a validated Pydantic Domain Model instead of `dict[str, Any]`, all blob trace deserialization (`json.loads(decoded)`) is replaced with Rust-level Pydantic V2 hydration (`TypeAdapter(T).validate_json()`), and 100% of repository tests are modernized atomically.

**Target Files** (exhaustive — 15 repositories / drivers + tests):
- `@[backend_v2/database/repositories/execution.py]` (#L92-L100 — eliminate `data[field] = json.loads(decoded)` for `execution_trace`, `frozen_context`, `context_variables`, replacing with typed `TypeAdapter(list[StepOutputDTO]).validate_json(blob_data)` and `FrozenContextDTO.model_validate_json(blob_data)`)
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

**Pattern**: Each repository method calls `Model.model_validate(raw_dict)` or `model_validate_json(raw_bytes)` internally and returns the typed model. Service layer never sees `dict[str, Any]`.

**Dependency**: Phase 1 (typed DTOs must exist).

### Phase 3: Hooks Refactoring, God Code Decomposition & Hook Tests (PRODUCERS FIRST)

**Objective**: Eliminate ALL `isinstance(..., dict)`, `.get()`, and `getattr()` from hook functions. Decompose `scoring.py` (1,347 LOC, 64.3 KB) into isolated modules under `@[backend_v2/hooks/scoring/]` first per `@[ki_god_code_prevention.md]`, and modernize hook tests atomically.

> [!IMPORTANT]
> **MANDATORY SUB-PHASE GATING**: Phase 3 MUST be executed across two sequentially gated implementation plans:
> 1. **Sub-Phase 3A (`plan_phase_3a_scoring_god_code_decomposition.md`)**: Structural `/tier3-god-code-decomposition` of `scoring.py` into `@[backend_v2/hooks/scoring/]` package preserving 100% of existing behavior and passing `@[backend_v2/tests/unit/hooks/test_scoring.py]`.
> 2. **Sub-Phase 3B (`plan_phase_3b_hooks_pydantic_v2_migration.md`)**: Full Pydantic V2 Hook State transition across all 11 hook files and the 4 decomposed scoring modules.

#### Sub-Phase 3A: `scoring.py` God Code Decomposition (Strangler Fig Proxy Pattern)
- **Target**: Decompose `@[backend_v2/hooks/scoring.py]` (1,347 LOC, 64.3 KB) into modular `@[backend_v2/hooks/scoring/]` package:
  - `[NEW]` `@[backend_v2/hooks/scoring/__init__.py]` — Strangler Fig facade re-exporting `apply_scoring_logic`, `enforce_passivity_penalty`, `matrix_scoring_hook`, `normalize_matrix_scores`, and `recalculate` with explicit `__all__` and redundant import aliases per PEP 484.
  - `[NEW]` `@[backend_v2/hooks/scoring/falsifier_hook.py]` — `apply_scoring_logic` hook (<200 LOC).
  - `[NEW]` `@[backend_v2/hooks/scoring/passivity_hook.py]` — `enforce_passivity_penalty` hook (<200 LOC).
  - `[NEW]` `@[backend_v2/hooks/scoring/matrix_hook.py]` — `matrix_scoring_hook` + quote evidence validation (<450 LOC).
  - `[NEW]` `@[backend_v2/hooks/scoring/normalization_hook.py]` — `normalize_matrix_scores` + `recalculate` (<350 LOC).
  - `[NEW]` `@[backend_v2/hooks/scoring/models.py]` — Strangler Fig temporary DTOs for structural decomposition. **MANDATORY SUNSET**: All models in this file MUST be either absorbed into individual hook modules or migrated to `@[backend_v2/models/dtos/]` during Sub-Phase 3B. This file MUST NOT persist beyond Sub-Phase 3B completion.
- **Pre-Requisite Verification**: Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/hooks/test_scoring.py --test` to prove zero behavioral regressions before proceeding to Sub-Phase 3B.

#### Sub-Phase 3B: Full Hooks Pydantic V2 Migration & Hook Tests
- **Target Files** (exhaustive — 11 hook files / modules + tests; all `scoring/` modules [NEW] created in Sub-Phase 3A):
  - [NEW] `@[backend_v2/hooks/scoring/falsifier_hook.py]` (created in Sub-Phase 3A)
  - [NEW] `@[backend_v2/hooks/scoring/passivity_hook.py]` (created in Sub-Phase 3A)
  - [NEW] `@[backend_v2/hooks/scoring/matrix_hook.py]` (created in Sub-Phase 3A)
  - [NEW] `@[backend_v2/hooks/scoring/normalization_hook.py]` (created in Sub-Phase 3A)
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

**Dependency**: Phase 1 (HookDeltaDTO, typed HookState), Sub-Phase 3A (decomposed `scoring/` package).

### Phase 4: Orchestration & Strategy Core Refactoring & Tests (CONSUMERS SECOND)

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

**Dependency**: Phase 1 (HookState typed), Phase 2 (repository returns typed), Phase 3 (all hooks return typed HookDeltaDTO).

### Phase 5: Service Layer, Utility Services & Service Tests

**Objective**: Eliminate ALL `getattr(initiator, "organization_id", None)` chains (replace with direct attribute access on `ExecutionMetadata` which already contains `organization_id` at `@[backend_v2/models/execution_core.py#L22-L82]`), `isinstance(x, dict)` branches, and `hasattr()` interface discovery from the service layer, modernizing service tests atomically.

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

**Dependency**: Phase 2 (repositories return typed models), Phase 1 (typed DTOs), Phase 4 (orchestrator typed).

### Phase 6: Background Workers, Typed Cache Boundary & Storage

**Objective**: Eliminate dict mutations in `worker.py` metadata handling, integrate generic `TypedCacheService` / Inbound Cache Hydration Firewall with auto-eviction on `ValidationError`, lock `ExecutionRecord.profile_syntheses` as `dict[str, RenderedSynthesisCache]` with `model_validate_json()` hydration, and modernize worker tests atomically.

**Target Files**:
- `@[backend_v2/worker.py]` (dict mutations in metadata fields, `RenderedSynthesisCache` hydration)
- [NEW] `@[backend_v2/services/cache/typed_cache.py]` (or cache adapter helper — generic `get_cached[T: BaseModel]` with `model_validate_json` and `redis.delete` on `ValidationError`)
- `@[backend_v2/tests/unit/test_worker_synthesis_hydration.py]` (eliminate duct-tape `json.loads()` loop; assert clean Pydantic V2 discriminated union hydration)
- `@[backend_v2/tests/unit/test_worker.py]`

**Dependency**: Phase 1 (`ExecutionMetadata` covers all telemetry fields), Phase 2 (storage blob hydration typed).

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
8. **All backend tests pass atomically** via `uv run python scripts/backend_audit_loop.py backend_v2/ --test` with >90% coverage.
9. **`scoring.py` decomposed** into `@[backend_v2/hooks/scoring/]` [NEW] package with every module <400 LOC, explicit Strangler Fig proxy in `__init__.py`, and zero unsuppressed `QGR001`/`QGR002` violations (God Code Prevention mandate).
10. **Seed Vault verified**: `uv run python scripts/audit_database_atoms.py --strict` returns 0 issues.
11. **Zero unvalidated raw dictionary mutations in `model_copy`**: All `model_copy(update={...})` calls pass strictly typed model instances or native Enums inside `async with _update_lock:`.
12. **Zero `validate_assignment=True` placebos**: `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` enforced across all domain models and DTOs.
13. **Zero `allowedKeys` duct-tape in Flutter**: Verified by `grep_search "allowedKeys" client_app_v2/` returning 0 results.
14. **100% Freezed schema parity & Flutter quality gate**: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build` passes 100% with zero analyzer warnings and `ExecutionCreateRequestDto` fully integrated.
15. **SDUI Semantic Parity**: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` passes 100%.
16. **Zero Residual Database Artifacts**: Verified that legacy vestigial files (`data/app.db`, `data/app.sqlite`) are permanently removed and `run_seed.py` cleanly purges orphaned execution files.
17. **Lifespan Startup Verification Gate**: Verified that FastAPI lifespan startup cleanly validates root collections against strict models on boot and fails fast if un-migrated records exist.
18. **Zero `json.loads()` in Cache and Blob Hydration**: Verified that all Redis and storage blob deserialization in `repositories/execution.py`, `worker.py`, and cache services uses native Pydantic V2 Rust `model_validate_json()` or `TypeAdapter(T).validate_json()` with automated zombie-cache eviction.

### Automated Unit & Quality Gate Tests

```powershell
# Backend Quality Gate
uv run python scripts/backend_audit_loop.py backend_v2/ --test

# Flutter Quality Gate & Freezed Code Generation
uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build

# SDUI Cross-Domain Semantic Parity
uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py
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
3. Verify Flutter client execution simulation via `dart run client_app_v2/bin/e2e_simulation.dart`.

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

