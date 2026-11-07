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

# EPIC 163 — Tier 0 System 2 Red-Team & Architectural Audit Report

- **Target Epic:** `@[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md]`
- **Audit Status:** `CONVERGENCE ACHIEVED: 0 architectural defects found`
- **Epic Mutations Applied:** `0` (Idempotent Read-Only Pass)

---

## 1. Automated Verification & Boundary Gate Results

| Verification Check | Command | Findings | Status |
| :--- | :--- | :--- | :--- |
| **Markdown AST Boundary Audit** | `uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md` | `0` | PASS |
| **Touched-Scope Technical Debt Audit (Phase 1 + 1-Hop)** | `uv run --no-sync --offline python scripts/audit_technical_debt.py --targets ... --include-one-hop` | `0` (10 targets, 17 1-hop callers) | PASS |
| **Flutter Theme Sovereignty Audit** | `uv run --no-sync --offline python scripts/audit_flutter_theme_sovereignty.py` | `0` (197 files scanned) | PASS |
| **Epic Target Coverage Audit** | `uv run --no-sync --offline python scripts/audit_epic_coverage.py --epic docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md` | `0` missing files | PASS |

---

## 2. Five-Axis System 2 Deconstruction

### Axis 1: Target Scope & Boundary (Scope Inquisitor)
- All 10 transitional technical debt exemption ledgers across `@[scripts/_ast_guardrails.py]`, `@[scripts/_dart_guardrails.py]`, `@[scripts/audit_dict_eradication.py]`, `@[scripts/audit_warning_baseline.py]`, and `@[pyproject.toml]` are exhaustively accounted for across the 6 execution phases:
  1. `RESIDUAL_MISSING_DOCSTRING_FILES` (`QGR001` — 4 files in Phase 1).
  2. `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` (`QGR002` — 1 file in Phase 1).
  3. `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` & `[tool.ruff.lint.per-file-ignores]` (2 audit script files in Phase 1).
  4. `RESIDUAL_LOCAL_SHADOW_STATE_FILES` (`QGR030` — 3 service files in Phase 1).
  5. `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` (`QGR020` Check 20C — 8 files, 14 fields in Phase 2).
  6. `RESIDUAL_BARE_FIELD_FILES` (`QGR020` Check 20B — 26 files, 209 fields in Phase 2).
  7. `RESIDUAL_FUTURE_PHASE_QGR028_FILES` (`QGR028` — 10 files, 22 violations in Phase 3).
  8. `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` (`QGR027` — 19 files, 32 occurrences in Phase 4).
  9. `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` Groups 2 & 3 (`DGR005` — 36 Flutter DTO and UI files in Phase 5, leaving exclusively the 9 Group 1 HTTP/SSE/Dio transport boundary files).
  10. `CURRENT_RESIDUAL_CEILINGS["f"] = 44` (`Census F` — 6 worker unit test files in Phase 6).

### Axis 2: Eradicated Duct-Tape (Duct-Tape Prosecutor)
- Eliminates process-local RAM shadow state (`_local_invitations`, `_local_assignments`, `_memory_entries`) in `@[backend_v2/services/auth/organization_service.py#L61-L1271]`, `@[backend_v2/services/execution/assignment_service.py#L123-L1610]`, and `@[backend_v2/services/cache/typed_cache.py#L111-L187]`.
- Eliminates silent empty-string/placeholder defaults (`= ""`, `= "unknown"`, `= "system"`) on identity, relational, and display fields across 8 model files.
- Eliminates mutable dictionary clones (`dict(record.step_states)`, `dict(record.profile_syntheses)`) and redundant `.model_validate()` calls on already-hydrated Pydantic models across 10 worker, hook, and service files.
- Eliminates untyped `dict[str, JsonValue]` bags in backend DAG/matrix/synthesis DTOs and `Map<String, Object?>` open-JSON maps in 36 Flutter Freezed DTOs and UI widgets.
- Eliminates 44 string-patched `UnifiedWorkflowRepository` mocks across 6 worker unit test files.

### Axis 3: Approved Best Practice (Type Constitutionalist)
- Enforces PEP 593 `Annotated[T, Field(...)]` across all 26 residual model/script files (`pydantic_annotated_fields_mandate`).
- Enforces immutable `ExecutionRecord` transition helpers (`with_updated_step_state`, `with_updated_profile_synthesis`, `with_cleared_profile_syntheses`) using `.model_copy(update=...)` (`frozen_state_mutability`).
- Enforces closed Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`) and 1:1 matching Dart 3 Freezed DTOs (`@JsonSerializable(disallowUnrecognizedKeys: true)`) (`full_duplex_serialization_parity_mandate`).
- Enforces stateful `InMemoryUnitOfWork` and `InMemoryUnifiedWorkflowRepository` roundtrip persistence verification in worker unit tests (`deceptive_persistence_mocking_ban` and `hermetic_test_fixtures_mandate`).

### Axis 4: Pruned Over-Engineering (Complexity Slayer — 30% Deletion Test)
- Deletes 7 entire `RESIDUAL_*` frozenset ledgers and their helper checks from `@[scripts/_ast_guardrails.py]`.
- Deletes dual-mode local dictionary fallback branches in `OrganizationService`, `ExecutionAssignmentService`, and `MCPGatewayCache`.
- Deletes intermediate dictionary copy-and-rehydrate loops in background workers and scoring hooks.

### Axis 5: Fail-Fast Proof Anchor (Incorruptible Judge)
- Locks `CURRENT_RESIDUAL_CEILINGS` in `@[scripts/audit_warning_baseline.py]` to `0` across all 10 census categories (`d=0, f=0, k=0, x=0, n=0, t=0, p=0, m=0, r=0, s=0`) with `CURRENT_WARNING_CEILING = 0`.
- Enforces full backend and frontend quality gates (`backend_audit_loop.py --test --ast-strict`, `flutter_audit_loop.py --build`, `audit_dict_eradication.py`, `audit_dto_parity.py`, `test_sdui_semantic_parity.py`, and live E2E verification).

---

## 3. Mandatory Falsification & Red-Team Checklist

1. **Fail-Fast Boundaries:** Verified. Removing silent defaults in Phase 2 (`QGR020` Check 20C) and removing local shadow dicts in Phase 1 (`QGR030`) forces immediate Pydantic `ValidationError` or RFC 7807 `AppException` (`ErrorCodes.CONFIGURATION_ERROR` / `ErrorCodes.VALIDATION_FAILED`) on missing inputs or unconfigured UoW/Redis adapters.
2. **Atomic Data & Test Migration:** Verified. Each phase pairs production code changes with synchronized companion unit tests and `Polyfactory` factories (`@[backend_v2/tests/factories/model_factories.py]`).
3. **Destructive Operation Inventory (`SUNSET_PHASE_PARITY_GATE`):** Verified. Every item in the Deprecations & Sunset List maps deterministically to Phases 1–6.
4. **Quantitative Scope Validation:** Verified. All file counts (5 ledger files, 70 backend/script files, 36 Flutter files, 20 test/fake files across 6 phases) match the physical repository state.
5. **Legacy Flat Field Eradication:** Verified. No legacy V1 shims or backwards-compatibility fallbacks are introduced (`zero_backward_compatibility_planning_ban`).
6. **Mandatory Phase Execution Order:** Verified. Phase 1 resolves foundational guardrail hygiene (`QGR001`, `QGR002`, `C901`, `QGR030`) before Phase 2–5 schema tightening and Phase 6 worker test migration.
7. **Context & KI Coverage Audit:** Verified. `<required_context_rules>` declares all 5 core/domain rules and 4 canonical Knowledge Items.

---

## 4. 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[scripts/_ast_guardrails.py]`, `@[backend_v2/logging_config.py#L138-L269]`, `@[backend_v2/services/auth/organization_service.py#L61-L1271]`, `@[backend_v2/services/execution/assignment_service.py#L123-L1610]`, `@[backend_v2/services/cache/typed_cache.py#L111-L187]`, `@[scripts/backend_audit_loop.py]`, `@[scripts/flutter_audit_loop.py]` | Exempting missing PEP 257 docstrings (`QGR001`), unlogged `AppException` raises (`QGR002`), C901 complexity in audit scripts, and process-local RAM shadow state (`_local_invitations`, `_local_assignments`, `_memory_entries`). | Add PEP 257 docstrings, log `logger.error` before `AppException` in `setup_logging`, decompose C901 functions into focused helpers, and persist invitations/assignments exclusively through `QuorumUnitOfWork`. | Zero dual-mode local dictionary fallback branches in `OrganizationService`, `ExecutionAssignmentService`, or `MCPGatewayCache`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/logging_config.py backend_v2/services/auth/organization_service.py backend_v2/services/execution/assignment_service.py backend_v2/services/cache/typed_cache.py scripts/ --test --ast-strict` |
| `@[scripts/_ast_guardrails.py]` & 31 model/utility/script files in `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` and `RESIDUAL_BARE_FIELD_FILES` | Silent string defaults (`= ""`, `= "unknown"`, `= "system"`) on identity/display fields (`QGR020` Check 20C) and legacy `field: T = Field(...)` syntax (`QGR020` Check 20B). | Remove all 14 silent identity/display defaults so missing fields fail fast at Pydantic validation, and convert all 209 bare `Field(...)` declarations to `Annotated[T, Field(...)]`. | Zero custom `@field_validator` shims for empty-string coercion; rely 100% on Rust-level Pydantic V2 `Annotated` constraints. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/core/ scripts/ --test --ast-strict` |
| `@[scripts/_ast_guardrails.py]` & 10 worker/hook/service files in `RESIDUAL_FUTURE_PHASE_QGR028_FILES` | Copying `dict(record.step_states)` or `dict(record.profile_syntheses)` for mutation and calling `.model_validate()` on already-hydrated Pydantic models (`QGR028`). | Encapsulate state map updates in immutable `ExecutionRecord` methods (`with_updated_step_state`, `with_updated_profile_synthesis`) using `model_copy(update=...)` and pass typed DTOs directly. | Zero intermediate mutable dictionary clones or redundant re-validation loops in workers and scoring hooks. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/hooks/ backend_v2/workers/ backend_v2/services/execution/ingress_service.py backend_v2/services/orchestrator/ --test --ast-strict` |
| `@[scripts/_ast_guardrails.py]` & 19 DTO/orchestrator/LLM files in `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` | Using `dict[str, JsonValue]` and `list[JsonValue]` for DAG step outputs, matrix evaluation cells, and synthesis payloads (`QGR027`). | Define closed Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`) and discriminated unions for all DAG, matrix, trace, and synthesis state transit. | Zero untyped `JsonValue` bags or runtime `isinstance(..., dict)` inspection inside orchestrator stages or hooks. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/llm/ backend_v2/services/orchestrator/ backend_v2/hooks/scoring/matrix_hook.py --test --ast-strict` |
| `@[scripts/_dart_guardrails.py]` & 36 Flutter files in `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` (Groups 2 & 3) | Declaring `Map<String, Object?>` fields on 13 Freezed DTOs and indexing raw maps across 23 Flutter views, controllers, and widgets (`DGR005`). | Replace open-JSON fields with strongly typed Freezed DTOs (`@JsonSerializable(disallowUnrecognizedKeys: true)`) and bind UI components to typed properties. | Zero client-side dynamic map casting or fallback map wrappers in Flutter views and controllers. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build` |
| `@[scripts/audit_warning_baseline.py]` & 6 worker unit test files (`test_worker.py`, `test_worker_synthesis.py`, `test_worker_synthesis_accumulation.py`, `test_report_worker.py`, `test_synthesis_reducers.py`, `test_synthesis_worker.py`) | Mocking `UnifiedWorkflowRepository` via 44 string-based `patch("...UnifiedWorkflowRepository")` calls (`Census F`). | Inject stateful `InMemoryUnitOfWork` and `InMemoryUnifiedWorkflowRepository` fixtures and assert persisted state via subsequent `get_*` roundtrip queries. | Zero `AsyncMock` repository return-value theater in worker unit tests; set `CURRENT_RESIDUAL_CEILINGS["f"] = 0`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/test_worker.py backend_v2/tests/unit/test_worker_synthesis.py backend_v2/tests/unit/test_worker_synthesis_accumulation.py backend_v2/tests/unit/workers/ --test --ast-strict` |

