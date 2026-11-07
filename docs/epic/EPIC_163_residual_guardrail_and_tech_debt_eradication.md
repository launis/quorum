<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
</required_context_rules>

# EPIC 163: Complete Eradication of Residual Guardrail Exemption Ledgers, Open-JSON DTO Consumers & Worker Repository Mocks

## 1. Goal Description & Background (Objective & Problem Statement)

Following the prune of 50 obsolete file and inline guardrail exemptions across `@[scripts/_ast_guardrails.py]`, `@[scripts/audit_dict_eradication.py]`, and `@[pyproject.toml]`, the Quorum V2 codebase retains **10 transitional technical debt exemption ledgers** spanning Python AST guardrails (`QGR001`, `QGR002`, `QGR020`, `QGR027`, `QGR028`, `QGR030`), Ruff cyclomatic complexity per-file ignores (`C901`), Flutter Dart static guardrails (`DGR005`), and the zero-warning baseline ledger (`Census F`).

This Epic executes a deterministic 6-phase architectural eradication of all 10 transitional exemption ledgers so that **zero transitional `RESIDUAL_*` sets remain in `@[scripts/_ast_guardrails.py]`**, **zero `per-file-ignores` remain in `@[pyproject.toml]` and `@[scripts/audit_dict_eradication.py]`**, **`DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` in `@[scripts/_dart_guardrails.py]` contains exclusively the 9 pure HTTP/SSE/Dio transport boundary files**, and **`CURRENT_RESIDUAL_CEILINGS` in `@[scripts/audit_warning_baseline.py]` reaches `0` across all 10 categories (`d=0, f=0, k=0, x=0, n=0, t=0, p=0, m=0, r=0, s=0`) alongside `CURRENT_WARNING_CEILING = 0`**.

### Core Architectural Problems Addressed

1. **Phase 1 — Missing PEP 257 Docstrings (`QGR001`), Unlogged `AppException` Raises (`QGR002`), Audit Script Cyclomatic Complexity (`C901`), and Process-Local Shadow State (`QGR030`):**
   - `RESIDUAL_MISSING_DOCSTRING_FILES` in `@[scripts/_ast_guardrails.py]` exempts 4 files lacking class or function docstrings: `@[backend_v2/models/dtos/variance.py#L17-L38]`, `@[backend_v2/services/orchestrator/extraction_schema_factory.py#L171-L238]`, `@[backend_v2/services/orchestrator/rag_preflight_service.py#L108-L305]`, and `@[backend_v2/services/orchestrator/schema_factory.py#L39-L411]`.
   - `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` in `@[scripts/_ast_guardrails.py]` exempts `@[backend_v2/logging_config.py#L138-L269]`, which raises `AppException` at two points without preceding `logger.error` calls (`rfc7807_dual_reporting_mandate`).
   - `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` in `@[scripts/audit_dict_eradication.py]` and `[tool.ruff.lint.per-file-ignores]` in `@[pyproject.toml]` exempt `@[scripts/backend_audit_loop.py]` and `@[scripts/flutter_audit_loop.py]` from Ruff `C901` McCabe cyclomatic complexity enforcement.
   - `RESIDUAL_LOCAL_SHADOW_STATE_FILES` in `@[scripts/_ast_guardrails.py]` exempts 3 service files holding process-local in-memory dictionary fallbacks (`self._local_invitations` in `@[backend_v2/services/auth/organization_service.py#L61-L1271]`, `self._memory_entries` in `@[backend_v2/services/cache/typed_cache.py#L111-L187]`, and `self._local_assignments` in `@[backend_v2/services/execution/assignment_service.py#L123-L1610]`), violating multi-worker Cloud Run state consistency (`zero_compromise_cutover_mandate`).

2. **Phase 2 — Silent Identity/Display Field Defaults (`QGR020` Check 20C) and Bare `Field(...)` Declarations (`QGR020` Check 20B):**
   - `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` in `@[scripts/_ast_guardrails.py]` exempts 8 files containing 14 silent default values (`= ""`, `= "unknown"`, `= "system"`) on identity, relational, or display fields (`id`, `slug`, `name`, `title`, `storage_mode`, `gateway_id`, `mcp_gateway_id`, `target_id`, `step_id`, `sys_initiator_id`, `updated_by`).
   - `RESIDUAL_BARE_FIELD_FILES` in `@[scripts/_ast_guardrails.py]` exempts 26 files containing 209 legacy `field: T = Field(...)` annotations instead of PEP 593 `Annotated[T, Field(...)]` (`pydantic_annotated_fields_mandate`).

3. **Phase 3 — Mutable Dictionary Unpacking of `ExecutionRecord` Maps & Redundant `.model_validate()` Re-Hydration (`QGR028`):**
   - `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]` exempts 10 worker, hook, and service files containing 22 violations where `dict(record.step_states)` or `dict(record.profile_syntheses)` is copied into a mutable dictionary or `.model_validate()` is invoked on an already-typed Pydantic instance.

4. **Phase 4 — Backend `JsonValue` Dictionary Containers in DAG State, Matrix Evaluation & Synthesis DTOs (`QGR027`):**
   - `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` in `@[scripts/_ast_guardrails.py]` exempts 19 DTO, hook, LLM client, and orchestrator files containing 32 occurrences of `dict[str, JsonValue]` or `list[JsonValue]` for internal state transit instead of closed Pydantic V2 DTOs (`no_naked_dicts_in_state`).

5. **Phase 5 — Frontend Flutter `Map<String, Object?>` Open-JSON Freezed Models & UI/Controller Consumers (`DGR005`):**
   - `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` in `@[scripts/_dart_guardrails.py]` exempts 13 Freezed DTO model files (Group 2) and 23 UI view, controller, and widget files (Group 3) that pass or index `Map<String, Object?>` payloads instead of strongly typed Freezed classes (`disallowUnrecognizedKeys: true`).

6. **Phase 6 — Deceptive String-Patched `UnifiedWorkflowRepository` Mocks in Worker Unit Tests (`Census F`):**
   - `CURRENT_RESIDUAL_CEILINGS["f"] = 44` in `@[scripts/audit_warning_baseline.py]` tracks 44 `patch("...UnifiedWorkflowRepository")` mocks across 6 worker unit test files (`deceptive_persistence_mocking_ban` and `hermetic_test_fixtures_mandate`).

### Quantitative Scope Summary

| Metric | Count | Details |
| :--- | :--- | :--- |
| **Guardrail & Baseline Ledger Scripts** | 5 | `@[scripts/_ast_guardrails.py]`, `@[scripts/_dart_guardrails.py]`, `@[scripts/audit_dict_eradication.py]`, `@[scripts/audit_warning_baseline.py]`, `@[pyproject.toml]` |
| **Production Backend & Operational Script Files** | 70 | Phase 1: 10 files (`variance.py`, `extraction_schema_factory.py`, `rag_preflight_service.py`, `schema_factory.py`, `logging_config.py`, `organization_service.py`, `typed_cache.py`, `assignment_service.py`, `backend_audit_loop.py`, `flutter_audit_loop.py`); Phase 2: 31 unique model/utility/script files; Phase 3: 10 worker/hook/service files; Phase 4: 19 DTO/orchestrator/LLM files |
| **Production Frontend Flutter Files** | 36 | 13 Freezed DTO model files (Group 2) + 23 UI view/controller/widget files (Group 3) in `client_app_v2/lib/` |
| **Test & Fake Files** | 20 | 6 worker unit test files (`Census F`) + guardrail unit test suites (`test_ast_guardrails.py`, `test_dart_guardrails.py`, `test_audit_dict_eradication.py`, `test_backend_audit_loop.py`, `test_flutter_audit_loop.py`) + service/model/Flutter companion test suites |
| **Execution Phases** | 6 | Phase 1: Guardrail Hygiene, C901 & `QGR030`; Phase 2: `QGR020` Checks 20C & 20B; Phase 3: `QGR028` Immutable Transitions; Phase 4: `QGR027` Typed Backend DTOs; Phase 5: `DGR005` Typed Flutter DTOs & UI; Phase 6: `Census F = 0` Worker Test Migration & Final Verification Gate |

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)

| Symbol / File / Field | Current Location | Target Destination / Disposition |
| :--- | :--- | :--- |
| Transitional `QGR001` docstring exemption set (`RESIDUAL_MISSING_DOCSTRING_FILES`) | `@[scripts/_ast_guardrails.py]` | INTENTIONALLY DROPPED — All 4 exempted files receive full PEP 257 Google-style docstrings |
| Transitional `QGR002` unlogged exception exemption set (`RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES`) | `@[scripts/_ast_guardrails.py]` | INTENTIONALLY DROPPED — `@[backend_v2/logging_config.py#L138-L269]` logs structured `logger.error` before raising `AppException` |
| Transitional `C901` complexity ignore list (`FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` & `[tool.ruff.lint.per-file-ignores]`) | `@[scripts/audit_dict_eradication.py]` & `@[pyproject.toml]` | INTENTIONALLY DROPPED — `@[scripts/backend_audit_loop.py]` and `@[scripts/flutter_audit_loop.py]` helper decomposition brings all functions to McCabe complexity $\le 15$ |
| Transitional `QGR030` local shadow state exemption set (`RESIDUAL_LOCAL_SHADOW_STATE_FILES`) and in-memory fallback dicts (`_local_invitations`, `_local_assignments`, `_memory_entries`) | `@[scripts/_ast_guardrails.py]`, `@[backend_v2/services/auth/organization_service.py#L61-L1271]`, `@[backend_v2/services/execution/assignment_service.py#L123-L1610]`, `@[backend_v2/services/cache/typed_cache.py#L111-L187]` | INTENTIONALLY DROPPED — Replaced 100% by `QuorumUnitOfWork` persistence and `RedisClientProtocol` cache adapter |
| Transitional `QGR020` Check 20C silent default exemption set (`RESIDUAL_DEFAULT_VALUE_MODEL_FILES`) | `@[scripts/_ast_guardrails.py]` | INTENTIONALLY DROPPED — All 14 identity, relational, and display fields across 8 files require explicit caller values |
| Transitional `QGR020` Check 20B bare `Field(...)` exemption set (`RESIDUAL_BARE_FIELD_FILES`) | `@[scripts/_ast_guardrails.py]` | INTENTIONALLY DROPPED — All 209 fields across 26 files converted to PEP 593 `Annotated[T, Field(...)]` |
| Transitional `QGR028` mutable dict unpacking & re-validation exemption set (`RESIDUAL_FUTURE_PHASE_QGR028_FILES`) | `@[scripts/_ast_guardrails.py]` | INTENTIONALLY DROPPED — Replaced by immutable `ExecutionRecord` transition helpers and direct typed DTO assignment across 10 files |
| Transitional `QGR027` `JsonValue` exemption set (`RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`) | `@[scripts/_ast_guardrails.py]` | INTENTIONALLY DROPPED — Replaced by closed Pydantic V2 DTOs across 19 files |
| Groups 2 & 3 (36 DTO/UI files) in `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` | `@[scripts/_dart_guardrails.py]` | INTENTIONALLY DROPPED — Replaced by typed Freezed DTO models and strongly typed widget/controller access across 36 Dart files |
| 44 `patch("...UnifiedWorkflowRepository")` test mocks (`CURRENT_RESIDUAL_CEILINGS["f"] = 44`) | `@[scripts/audit_warning_baseline.py]` & 6 worker test files | INTENTIONALLY DROPPED — Replaced by stateful `InMemoryUnitOfWork` and `InMemoryUnifiedWorkflowRepository` fixtures (`f = 0`) |

### Retained SSOT Invariants (`What We Will RETAIN`)

- True Hexagonal Adapter Boundary sets in `@[scripts/_ast_guardrails.py]`: `BOUNDARY_EXEMPTION_FILES` (13 database, LLM provider, and telemetry boundary adapters) and `OPEN_JSON_EXEMPTION_FILES` (5 external RFC 7807, MCP JSON-Schema, and dynamic LLM schema boundary files).
- Group 1 Transport Boundary set in `@[scripts/_dart_guardrails.py]`: the 9 pure HTTP/SSE/Dio transport boundary files in `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` (`execution_client.dart`, `reports_client.dart`, `sse_client.dart`, `studio_client.dart`, `workflow_client.dart`, `app_exception.dart`, `error_interceptor.dart`, `auth_repository.dart`, `user_repository.dart`).
- `QuorumUnitOfWork` (`@[backend_v2/database/interfaces.py#L437-L477]`) and `InMemoryUnitOfWork` (`@[backend_v2/tests/fakes/in_memory_uow.py#L1960-L2034]`) as the authoritative persistence contract for `OrganizationInvitation` and `ExecutionTaskAssignment` entities.
- Full-Duplex Serialization Parity (`full_duplex_serialization_parity_mandate` and `sdui_contract_fracture_prevention`) across backend Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`), Jinja PDF templates, and Flutter Freezed models (`@JsonSerializable(disallowUnrecognizedKeys: true)`).

### 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[scripts/_ast_guardrails.py]`, `@[backend_v2/logging_config.py#L138-L269]`, `@[backend_v2/services/auth/organization_service.py#L61-L1271]`, `@[backend_v2/services/execution/assignment_service.py#L123-L1610]`, `@[backend_v2/services/cache/typed_cache.py#L111-L187]`, `@[scripts/backend_audit_loop.py]`, `@[scripts/flutter_audit_loop.py]` | Exempting missing PEP 257 docstrings (`QGR001`), unlogged `AppException` raises (`QGR002`), C901 complexity in audit scripts, and process-local RAM shadow state (`_local_invitations`, `_local_assignments`, `_memory_entries`). | Add PEP 257 docstrings, log `logger.error` before `AppException` in `setup_logging`, decompose C901 functions into focused helpers, and persist invitations/assignments exclusively through `QuorumUnitOfWork`. | Zero dual-mode local dictionary fallback branches in `OrganizationService`, `ExecutionAssignmentService`, or `MCPGatewayCache`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/logging_config.py backend_v2/services/auth/organization_service.py backend_v2/services/execution/assignment_service.py backend_v2/services/cache/typed_cache.py scripts/ --test --ast-strict` |
| `@[scripts/_ast_guardrails.py]` & 31 model/utility/script files in `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` and `RESIDUAL_BARE_FIELD_FILES` | Silent string defaults (`= ""`, `= "unknown"`, `= "system"`) on identity/display fields (`QGR020` Check 20C) and legacy `field: T = Field(...)` syntax (`QGR020` Check 20B). | Remove all 14 silent identity/display defaults so missing fields fail fast at Pydantic validation, and convert all 209 bare `Field(...)` declarations to `Annotated[T, Field(...)]`. | Zero custom `@field_validator` shims for empty-string coercion; rely 100% on Rust-level Pydantic V2 `Annotated` constraints. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/core/ scripts/ --test --ast-strict` |
| `@[scripts/_ast_guardrails.py]` & 10 worker/hook/service files in `RESIDUAL_FUTURE_PHASE_QGR028_FILES` | Copying `dict(record.step_states)` or `dict(record.profile_syntheses)` for mutation and calling `.model_validate()` on already-hydrated Pydantic models (`QGR028`). | Encapsulate state map updates in immutable `ExecutionRecord` methods (`with_updated_step_state`, `with_updated_profile_synthesis`) using `model_copy(update=...)` and pass typed DTOs directly. | Zero intermediate mutable dictionary clones or redundant re-validation loops in workers and scoring hooks. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/hooks/ backend_v2/workers/ backend_v2/services/execution/ingress_service.py backend_v2/services/orchestrator/ --test --ast-strict` |
| `@[scripts/_ast_guardrails.py]` & 19 DTO/orchestrator/LLM files in `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` | Using `dict[str, JsonValue]` and `list[JsonValue]` for DAG step outputs, matrix evaluation cells, and synthesis payloads (`QGR027`). | Define closed Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`) and discriminated unions for all DAG, matrix, trace, and synthesis state transit. | Zero untyped `JsonValue` bags or runtime `isinstance(..., dict)` inspection inside orchestrator stages or hooks. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/llm/ backend_v2/services/orchestrator/ backend_v2/hooks/scoring/matrix_hook.py --test --ast-strict` |
| `@[scripts/_dart_guardrails.py]` & 36 Flutter files in `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` (Groups 2 & 3) | Declaring `Map<String, Object?>` fields on 13 Freezed DTOs and indexing raw maps across 23 Flutter views, controllers, and widgets (`DGR005`). | Replace open-JSON fields with strongly typed Freezed DTOs (`@JsonSerializable(disallowUnrecognizedKeys: true)`) and bind UI components to typed properties. | Zero client-side dynamic map casting or fallback map wrappers in Flutter views and controllers. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build` |
| `@[scripts/audit_warning_baseline.py]` & 6 worker unit test files (`test_worker.py`, `test_worker_synthesis.py`, `test_worker_synthesis_accumulation.py`, `test_report_worker.py`, `test_synthesis_reducers.py`, `test_synthesis_worker.py`) | Mocking `UnifiedWorkflowRepository` via 44 string-based `patch("...UnifiedWorkflowRepository")` calls (`Census F`). | Inject stateful `InMemoryUnitOfWork` and `InMemoryUnifiedWorkflowRepository` fixtures and assert persisted state via subsequent `get_*` roundtrip queries. | Zero `AsyncMock` repository return-value theater in worker unit tests; set `CURRENT_RESIDUAL_CEILINGS["f"] = 0`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/test_worker.py backend_v2/tests/unit/test_worker_synthesis.py backend_v2/tests/unit/test_worker_synthesis_accumulation.py backend_v2/tests/unit/workers/ --test --ast-strict` |

### Producer-Consumer Integration Check

- **Producer 1 (Backend Domain & DTO Schemas in `@[backend_v2/models/state.py]`, `@[backend_v2/models/dtos/lightweight_matrix.py]`, `@[backend_v2/models/dtos/trace.py]`, `@[backend_v2/models/dtos/system.py]`, `@[backend_v2/models/view/sdui.py]`):** Serializes strongly typed Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with PEP 593 `Annotated[T, Field(...)]` metadata, explicit required identity/display fields (`ReportView.title`, `WorkflowCreateDTO.mcp_gateway_id`), and closed nested DTO structures replacing `dict[str, JsonValue]`.
- **Consumer 1 (Frontend Flutter Freezed DTOs in `@[client_app_v2/lib/features/execution/models/execution_record.dart]`, `@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]`, `@[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]`, `@[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]`, `@[client_app_v2/lib/features/studio/models/workflow_simulation.dart]` & UI Widgets):** Deserializes 1:1 matching JSON payloads via Freezed `@JsonSerializable(disallowUnrecognizedKeys: true)` models and renders strongly typed properties in `ResultDashboard`, `SpecialistSection`, `ComparisonMatrix`, `DynamicStartScreen`, and Studio simulation views without `Map<String, Object?>` indexing.
- **Producer 2 (`OrganizationService` in `@[backend_v2/services/auth/organization_service.py#L61-L1271]`, `ExecutionAssignmentService` in `@[backend_v2/services/execution/assignment_service.py#L123-L1610]`, & Background Workers in `backend_v2/workers/`):** Persists `OrganizationInvitation`, `ExecutionTaskAssignment`, and `ExecutionRecord` mutations deterministically through `QuorumUnitOfWork` and `UnifiedWorkflowRepository`.
- **Consumer 2 (`InMemoryUnitOfWork` in `@[backend_v2/tests/fakes/in_memory_uow.py#L1960-L2034]` & `InMemoryUnifiedWorkflowRepository` in `@[backend_v2/tests/fakes/in_memory_repositories.py#L1461-L2106]`):** Executes stateful in-memory persistence roundtrips (`save` followed by `get`) across all organization, assignment, and worker unit tests with zero `patch("...UnifiedWorkflowRepository")` mocks.

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Pre-Implementation Guardrail Hygiene (`QGR001`, `QGR002`), Audit Script `C901` Decomposition & `QGR030` Local Shadow-State Eradication

- **Objective:** Eliminate `RESIDUAL_MISSING_DOCSTRING_FILES`, `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES`, and `RESIDUAL_LOCAL_SHADOW_STATE_FILES` from `@[scripts/_ast_guardrails.py]`, and eliminate `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` and `[tool.ruff.lint.per-file-ignores]` from `@[scripts/audit_dict_eradication.py]` and `@[pyproject.toml]`.
- **Target Files:**
  - `[MODIFY]` `@[backend_v2/models/dtos/variance.py#L17-L38]`: Add PEP 257 Google-style class docstring with `Attributes:` section.
  - `[MODIFY]` `@[backend_v2/services/orchestrator/extraction_schema_factory.py#L27-L80]`, `@[backend_v2/services/orchestrator/extraction_schema_factory.py#L83-L168]`, and `@[backend_v2/services/orchestrator/extraction_schema_factory.py#L171-L238]`: Add PEP 257 Google-style module, class, and function docstrings (`Args:`, `Returns:`, `Raises:`).
  - `[MODIFY]` `@[backend_v2/services/orchestrator/rag_preflight_service.py#L108-L305]`: Add PEP 257 Google-style class and method docstrings.
  - `[MODIFY]` `@[backend_v2/services/orchestrator/schema_factory.py#L39-L411]`: Add PEP 257 Google-style class and method docstrings.
  - `[MODIFY]` `@[backend_v2/logging_config.py#L138-L269]`: Add structured `logger.error` calls with `extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name}` immediately preceding both `raise AppException(...)` statements in `setup_logging`.
  - `[MODIFY]` `@[scripts/backend_audit_loop.py#run_audit_loop]` and `@[scripts/flutter_audit_loop.py#L107-L313]`: Decompose high-branching CLI and stage-runner functions into single-responsibility helper functions so every function in `@[scripts/backend_audit_loop.py]` and `@[scripts/flutter_audit_loop.py]` achieves Ruff `C901` McCabe cyclomatic complexity $\le 15$.
  - `[MODIFY]` `@[pyproject.toml]` and `@[scripts/audit_dict_eradication.py]`: Remove `[tool.ruff.lint.per-file-ignores]` from `@[pyproject.toml]` and empty `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` to `frozenset()` in `@[scripts/audit_dict_eradication.py]`.
  - `[MODIFY]` `@[backend_v2/services/auth/organization_service.py#L61-L1271]`: Remove `self._local_invitations` and all in-memory dictionary fallback branches in `_save_invitation`, `_get_invitation_by_id`, `_list_org_invitations`, and `_find_invitation_by_token_hash`; enforce mandatory `QuorumUnitOfWork` persistence via `self._uow_factory`.
  - `[MODIFY]` `@[backend_v2/services/execution/assignment_service.py#L123-L1610]`: Remove `self._local_assignments` and all in-memory dictionary fallback branches in `get_assignment_by_execution_id`, `_get_assignment_or_raise`, `_save_assignment`, `_list_all_assignments`, and `_find_assignment_by_token_hash`; enforce mandatory `QuorumUnitOfWork` persistence via `self._uow_factory`.
  - `[MODIFY]` `@[backend_v2/services/cache/typed_cache.py#L111-L187]`: Remove `self._memory_entries` process-local dict fallback and route all cache operations through the injected `RedisClientProtocol` adapter (using `InMemoryRedisClient` in unit tests).
  - `[MODIFY]` `@[scripts/_ast_guardrails.py]`: Delete `RESIDUAL_MISSING_DOCSTRING_FILES`, `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES`, and `RESIDUAL_LOCAL_SHADOW_STATE_FILES` and their exemption checks.
  - **Synchronized Unit Test Targets:**
    - `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
    - `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`
    - `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]`
    - `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_flutter_audit_loop.py]`
    - `[MODIFY]` `@[backend_v2/tests/unit/test_organization_service.py]`
    - `[MODIFY]` `@[backend_v2/tests/unit/services/execution/test_assignment_service.py]`

### Phase 2: Pydantic V2 Schema Strictness — Zero Silent Defaults (`QGR020` Check 20C) & 100% PEP 593 `Annotated` (`QGR020` Check 20B)

- **Objective:** Eliminate `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` (8 files, 14 fields) and `RESIDUAL_BARE_FIELD_FILES` (26 files, 209 fields) from `@[scripts/_ast_guardrails.py]`.
- **Target Files (`RESIDUAL_DEFAULT_VALUE_MODEL_FILES` — 8 files):**
  - `[MODIFY]` `@[backend_v2/models/auth.py#L797-L826]` and `@[backend_v2/models/auth.py#L1361-L1437]`: Remove silent defaults `= ""` on `ImpersonationResponse.target_id`, `= "unknown"` on `TenantSecretDTO.storage_mode`, and `= "system"` on `TenantSecretDTO.updated_by`.
  - `[MODIFY]` `@[backend_v2/models/domain/metadata.py#L21-L38]`: Remove silent default `= "system"` on `sys_initiator_id`.
  - `[MODIFY]` `@[backend_v2/models/domain/system_config.py#L210-L260]` and `@[backend_v2/models/domain/system_config.py#L377-L437]`: Remove silent defaults `= ""` on `SystemConfigModelRegistry.name` and `SystemConfigMCPGateways.slug`.
  - `[MODIFY]` `@[backend_v2/models/dtos/mcp.py#L393-L431]`, `@[backend_v2/models/dtos/mcp.py#L520-L533]`, and `@[backend_v2/models/dtos/mcp.py#L651-L682]`: Remove silent defaults `= ""` on `gateway_id` and `= "unknown"` on `name`.
  - `[MODIFY]` `@[backend_v2/models/dtos/studio.py#L89-L156]`: Replace silent empty string default `= ""` on `mcp_gateway_id` with explicit nullable `Annotated[str | None, Field(default=None, ...)] = None`.
  - `[MODIFY]` `@[backend_v2/models/view/sdui.py#L228-L253]`: Remove silent default `= ""` on `ReportView.title` so every `ReportView` instantiation explicitly provides a localized title.
  - `[MODIFY]` `@[backend_v2/utils/finops_trace_analyzer.py#L92-L111]`: Remove silent default `= "unknown"` on `TraceStepRecord.step_id`.
  - `[MODIFY]` `@[scripts/ablation_live_executor.py#L344-L365]`: Remove silent defaults `= ""` on `SeedRegistryEntryDTO.id` and `SeedRegistryEntryDTO.name`.
- **Target Files (`RESIDUAL_BARE_FIELD_FILES` — 26 files):**
  - `[MODIFY]` `@[backend_v2/core/hook_registry.py#HookDefinition]`
  - `[MODIFY]` `@[backend_v2/core/registry.py#L78-L99]`
  - `[MODIFY]` `@[backend_v2/exceptions.py#ProblemDetails]`
  - `[MODIFY]` `@[backend_v2/models/chunking.py#DocumentChunk]`
  - `[MODIFY]` `@[backend_v2/models/domain/execution.py#L216-L394]`
  - `[MODIFY]` `@[backend_v2/models/domain/inputs.py#ExpectedInput]`
  - `[MODIFY]` `@[backend_v2/models/domain/matrix.py#ScaleItem]`
  - `[MODIFY]` `@[backend_v2/models/domain/output_profile.py#L44-L355]`
  - `[MODIFY]` `@[backend_v2/models/domain/prompt_blocks.py#L38-L61]`
  - `[MODIFY]` `@[backend_v2/models/domain/step.py#L42-L194]`
  - `[MODIFY]` `@[backend_v2/models/domain/system_config.py#SystemConfigBase]`
  - `[MODIFY]` `@[backend_v2/models/domain/workflow.py#L25-L213]`
  - `[MODIFY]` `@[backend_v2/models/dtos/context_variables.py#PromptContextVariablesDTO]`
  - `[MODIFY]` `@[backend_v2/models/dtos/engine.py#PromptEngineRequest]`
  - `[MODIFY]` `@[backend_v2/models/dtos/hook_state.py#NormalizationHookState]`
  - `[MODIFY]` `@[backend_v2/models/dtos/quote_evidence.py#L143-L251]`
  - `[MODIFY]` `@[backend_v2/models/dtos/schema_manifest.py#StepSchemaManifestDTO]`
  - `[MODIFY]` `@[backend_v2/models/dtos/theory_manifest.py#TheoryManifestDTO]`
  - `[MODIFY]` `@[backend_v2/models/dtos/workflow_schema.py#WorkflowInputFieldSchema]`
  - `[MODIFY]` `@[backend_v2/models/execution_core.py#ExecutionSummarySnapshot]`
  - `[MODIFY]` `@[backend_v2/models/llm.py#TokenUsage]`
  - `[MODIFY]` `@[backend_v2/models/state.py#AdapterContext]`
  - `[MODIFY]` `@[backend_v2/models/view/sdui.py#GlobalScoreBlock]`
  - `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py#PackedSourcePayload]`
  - `[MODIFY]` `@[scripts/diff_executions.py#StepTelemetrySummary]`
  - `[MODIFY]` `@[scripts/reconcile_storage.py#L58-L69]`
  - `[MODIFY]` `@[scripts/_ast_guardrails.py]`: Delete `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` and `RESIDUAL_BARE_FIELD_FILES`.
  - **Synchronized Unit Test Targets:**
    - `[MODIFY]` `@[backend_v2/tests/factories/model_factories.py]`
    - `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`

### Phase 3: Immutable `ExecutionRecord` State Transitions & Zero Redundant Re-Validation (`QGR028`)

- **Objective:** Eliminate all 22 `QGR028` violations across the 10 files in `RESIDUAL_FUTURE_PHASE_QGR028_FILES` and delete `RESIDUAL_FUTURE_PHASE_QGR028_FILES` from `@[scripts/_ast_guardrails.py]`.
- **Target Files:**
  - `[MODIFY]` `@[backend_v2/models/domain/execution.py#L216-L394]`: Define pure immutable transition helper methods on `ExecutionRecord` (`with_updated_step_state`, `with_updated_profile_synthesis`, `with_cleared_profile_syntheses`) encapsulating `model_copy(update=...)` transitions.
  - `[MODIFY]` `@[backend_v2/hooks/atom_flattening.py#atom_flattening_hook]`: Replace redundant `.model_validate()` on typed DTOs with direct typed instance access.
  - `[MODIFY]` `@[backend_v2/hooks/scoring/falsifier_hook.py#falsifier_adversarial_hook]`: Replace redundant `.model_validate()` with direct typed DTO access.
  - `[MODIFY]` `@[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook]`: Replace both redundant `.model_validate()` calls with direct typed DTO access.
  - `[MODIFY]` `@[backend_v2/hooks/scoring/normalization_hook.py#score_normalization_hook]`: Replace both redundant `.model_validate()` calls with direct typed DTO access.
  - `[MODIFY]` `@[backend_v2/services/execution/ingress_service.py#L360-L763]`: Replace 4 redundant `.model_validate()` calls on typed ingress/context models with direct typed instances.
  - `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/logic.py#L32-L231]`: Replace redundant `.model_validate()` call with direct typed DTO handling.
  - `[MODIFY]` `@[backend_v2/services/orchestrator/synthesis_distiller.py#L173-L395]`: Replace both redundant `.model_validate()` calls with direct typed DTO access.
  - `[MODIFY]` `@[backend_v2/workers/execution_worker.py#_mark_execution_failed]`: Replace `dict(record.step_states)` mutation with `ExecutionRecord` immutable transition helper.
  - `[MODIFY]` `@[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]`: Replace `dict(latest_record.profile_syntheses)` and `dict(latest_record.step_states)` copies with `ExecutionRecord` immutable transition helpers.
  - `[MODIFY]` `@[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase]`: Replace all 5 `dict(record.step_states)` / `dict(record.profile_syntheses)` and redundant `.model_validate()` calls with `ExecutionRecord` immutable transition helpers.
  - `[MODIFY]` `@[scripts/_ast_guardrails.py]`: Delete `RESIDUAL_FUTURE_PHASE_QGR028_FILES`.
  - **Synchronized Unit Test Targets:**
    - `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
    - `[MODIFY]` `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`
    - `[MODIFY]` `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]`

### Phase 4: Strongly Typed DAG Context, Matrix Evaluation & Synthesis DTOs (`QGR027` `JsonValue` Eradication)

- **Objective:** Replace all 32 `dict[str, JsonValue]` and `list[JsonValue]` occurrences across the 19 files in `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` with closed Pydantic V2 DTOs and discriminated unions, and delete `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` from `@[scripts/_ast_guardrails.py]`.
- **Target Files:**
  - `[MODIFY]` `@[backend_v2/models/dtos/atom_evaluation.py#L151-L174]`: Replace open `dict[str, JsonValue]` fields with closed Pydantic V2 DTOs.
  - `[MODIFY]` `@[backend_v2/models/dtos/hook_delta.py#HookStateDeltaDTO]`: Replace `dict[str, JsonValue]` payload fields with closed typed delta DTOs.
  - `[MODIFY]` `@[backend_v2/models/dtos/lightweight_matrix.py#L126-L189]` and `@[backend_v2/models/dtos/lightweight_matrix.py#L45-L59]`: Create closed Pydantic V2 models for matrix rows, scale distributions, and diagnostic trace metadata replacing `dict[str, JsonValue]`.
  - `[MODIFY]` `@[backend_v2/models/dtos/prompt_context.py#PromptCompilationContextDTO]`: Replace `dict[str, JsonValue]` context map with typed prompt context DTO fields.
  - `[MODIFY]` `@[backend_v2/models/dtos/schema_manifest.py#StepSchemaManifestDTO]`: Replace `dict[str, JsonValue]` schema descriptor fields with typed manifest DTOs.
  - `[MODIFY]` `@[backend_v2/models/dtos/system.py#L56-L75]`: Create typed health component entries replacing `dict[str, JsonValue]` diagnostic maps on `HealthCheckResponseDTO`.
  - `[MODIFY]` `@[backend_v2/models/dtos/trace.py#StepTraceEventDTO]`: Replace `dict[str, JsonValue]` trace output fields with typed trace payload DTOs (`exclude_none=True`).
  - `[MODIFY]` `@[backend_v2/models/state.py#AdapterContext]` and `@[backend_v2/models/state.py#ExecutionContext]`: Replace `dict[str, JsonValue]` step output maps with typed `StepOutputDTO` and discriminated union values.
  - `[MODIFY]` `@[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook]`: Consume and return typed `LightweightMatrixOutput` and `ScoringResultDTO` models without `dict[str, JsonValue]`.
  - `[MODIFY]` `@[backend_v2/llm/client.py#L42-L879]`: Replace `dict[str, JsonValue]` return/parameter annotations on structured execution helpers with generic Pydantic `BaseModel` type parameters.
  - `[MODIFY]` `@[backend_v2/llm/ingress_pipeline.py#LLMIngressPipeline]`: Replace `dict[str, JsonValue]` intermediate payload annotations with typed ingress DTOs.
  - `[MODIFY]` `@[backend_v2/llm/mock_data.py#get_mock_structured_response]`: Return typed Pydantic DTO fixtures instead of `dict[str, JsonValue]`.
  - `[MODIFY]` `@[backend_v2/services/llm_task_executor.py#L106-L525]`: Enforce generic `BaseModel` return typing across structured task execution methods.
  - `[MODIFY]` `@[backend_v2/services/orchestrator/context_router.py#L50-L196]`: Route typed `StepOutputDTO` payloads without `dict[str, JsonValue]` maps.
  - `[MODIFY]` `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L345-L436]`: Replace `dict[str, JsonValue]` wave accumulator maps with typed wave execution state DTOs.
  - `[MODIFY]` `@[backend_v2/services/orchestrator/matrix_reducer.py#L56-L246]`: Return typed `LightweightMatrixOutput` models from matrix reduction methods.
  - `[MODIFY]` `@[backend_v2/services/orchestrator/result_projector.py#L31-L272]`: Project atom and matrix results into typed `LightweightMatrixDTO` and `StepOutputDTO` models instead of `dict[str, JsonValue]`.
  - `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/logic.py#L32-L231]`: Return typed logic evaluation DTOs instead of `dict[str, JsonValue]`.
  - `[MODIFY]` `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L36-L501]`: Create typed compressed synthesis payload DTOs in `SynthesisPayloadCompressor` instead of `dict[str, JsonValue]`.
  - `[MODIFY]` `@[scripts/_ast_guardrails.py]`: Delete `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`.
  - **Synchronized Unit Test Targets:**
    - `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
    - `[MODIFY]` `@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`

### Phase 5: Frontend Flutter `DGR005` Open-JSON DTO & UI Consumer Eradication

- **Objective:** Replace all `Map<String, Object?>` fields and consumers across the 13 Freezed DTO files (Group 2) and 23 UI/controller/widget files (Group 3) in `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES`, shrinking `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` in `@[scripts/_dart_guardrails.py]` from 45 files to exclusively the 9 pure HTTP/SSE/Dio transport boundary files.
- **Target Files (Group 2 — 13 Freezed DTO Model Files):**
  - `[MODIFY]` `@[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/execution/models/execution_metadata.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/execution/models/execution_record.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/execution/models/workflow_inputs.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/models/model_config.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/models/step_simulation.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/models/workflow.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/models/workflow_simulation.dart]`
- **Target Files (Group 3 — 23 Flutter UI, Controller & Widget Consumer Files):**
  - `[MODIFY]` `@[client_app_v2/lib/features/execution/controllers/execution_controller.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/execution/views/dashboard_view.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/controllers/blueprint_editor_controller.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/views/blueprint_editor_view.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/views/step_builder_view.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/shared/widgets/audit_trail_viewer.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/shared/widgets/comparison_matrix.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/shared/widgets/dynamic_form.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/shared/widgets/generic_grid.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/shared/widgets/pre_mortem_card.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/shared/widgets/result_dashboard.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/shared/widgets/schema_mapper.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/shared/widgets/score_card_radar.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/shared/widgets/specialist_section.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/shared/widgets/validation_timeline_widget.dart]`
  - `[MODIFY]` `@[client_app_v2/lib/shared/widgets/workflow_selector.dart]`
  - `[MODIFY]` `@[scripts/_dart_guardrails.py]`: Remove all 36 Group 2 and Group 3 paths from `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES`, retaining only the 9 Group 1 transport boundary files.
  - **Synchronized Unit Test Targets:**
    - `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py]`
    - `[MODIFY]` `@[client_app_v2/test/unit/features/execution/models/execution_record_test.dart]`
    - `[MODIFY]` `@[client_app_v2/test/unit/features/execution/models/execution_step_test.dart]`

### Phase 6: Stateful `InMemoryUnitOfWork` Migration for Worker Test Suites (`Census F = 0`) & Final E2E Verification Gate

- **Objective:** Replace all 44 `patch("...UnifiedWorkflowRepository")` mocks across the 6 worker unit test files with stateful `InMemoryUnitOfWork` and `InMemoryUnifiedWorkflowRepository` fixtures (`deceptive_persistence_mocking_ban`), lower `CURRENT_RESIDUAL_CEILINGS["f"]` from `44` to `0` in `@[scripts/audit_warning_baseline.py]`, and execute the full backend, frontend, parity, and live E2E verification gates.
- **Target Files:**
  - `[MODIFY]` `@[backend_v2/tests/unit/test_worker.py]` (replace 18 `UnifiedWorkflowRepository` patches with stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixtures and verify persisted state via roundtrip `get_execution` / `get_workflow` calls).
  - `[MODIFY]` `@[backend_v2/tests/unit/test_worker_synthesis.py]` (replace 16 `UnifiedWorkflowRepository` patches with stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixtures).
  - `[MODIFY]` `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]` (replace 1 `UnifiedWorkflowRepository` patch with stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixture).
  - `[MODIFY]` `@[backend_v2/tests/unit/workers/test_report_worker.py]` (replace 2 `UnifiedWorkflowRepository` patches with stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixtures).
  - `[MODIFY]` `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]` (replace 3 `UnifiedWorkflowRepository` patches with stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixtures).
  - `[MODIFY]` `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]` (replace 4 `UnifiedWorkflowRepository` patches with stateful `InMemoryUnitOfWork` / `InMemoryUnifiedWorkflowRepository` fixtures).
  - `[MODIFY]` `@[scripts/audit_warning_baseline.py]`: Update `CURRENT_RESIDUAL_CEILINGS["f"]` from `44` to `0` so all 10 categories (`d`, `f`, `k`, `x`, `n`, `t`, `p`, `m`, `r`, `s`) equal `0`.

---

## 4. Definition of Done (DoD) & Verification Plan

- **Definition of Done (DoD):**
  1. Zero `RESIDUAL_*` exemption sets exist in `@[scripts/_ast_guardrails.py]` (specifically and exhaustively: `RESIDUAL_MISSING_DOCSTRING_FILES`, `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES`, `RESIDUAL_LOCAL_SHADOW_STATE_FILES`, `RESIDUAL_DEFAULT_VALUE_MODEL_FILES`, `RESIDUAL_BARE_FIELD_FILES`, `RESIDUAL_FUTURE_PHASE_QGR028_FILES`, and `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` are completely removed).
  2. `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` in `@[scripts/audit_dict_eradication.py]` is `frozenset()`, `[tool.ruff.lint.per-file-ignores]` is removed from `@[pyproject.toml]`, and `uv run ruff check scripts/ backend_v2/` passes with zero `C901` warnings.
  3. `OrganizationService` (`@[backend_v2/services/auth/organization_service.py#L61-L1271]`) and `ExecutionAssignmentService` (`@[backend_v2/services/execution/assignment_service.py#L123-L1610]`) persist all invitations and task assignments exclusively through `QuorumUnitOfWork` with zero process-local dictionary fallbacks.
  4. `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` in `@[scripts/_dart_guardrails.py]` contains exclusively the 9 Group 1 HTTP/SSE/Dio transport boundary files, with all 36 Group 2 and Group 3 DTO/UI files migrated to strongly typed Freezed models (`disallowUnrecognizedKeys: true`).
  5. `CURRENT_RESIDUAL_CEILINGS` in `@[scripts/audit_warning_baseline.py]` is `0` across all 10 categories (`d=0, f=0, k=0, x=0, n=0, t=0, p=0, m=0, r=0, s=0`) and `CURRENT_WARNING_CEILING = 0`.
- **Automated UnitTests & Quality Gates:**
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ scripts/ --test --ast-strict`
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_dict_eradication.py`
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_warning_baseline.py --verify-ceilings`
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_dto_parity.py`
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
- **AST Guardrails & Structural Tests:**
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py backend_v2/tests/unit/scripts/test_dart_guardrails.py backend_v2/tests/unit/scripts/test_audit_dict_eradication.py`
- **MANDATORY Final E2E REST API Verification Gate:**
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

---

## 5. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.
