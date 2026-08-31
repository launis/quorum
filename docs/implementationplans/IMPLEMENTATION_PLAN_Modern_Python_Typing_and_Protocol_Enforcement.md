# Modern Python 3.12–3.14+ Typing & Protocol Enforcement Architecture

This plan establishes the implementation and enforcement architecture for modern Python (3.12–3.14+) typing paradigms, Protocol-driven contracts, In-Memory Protocol test fakes, automated test mock migration, and static AST guardrail rules across Quorum's backend codebase.

## User Review Required

> [!IMPORTANT]
> - **AST Rule Expansion (`QGR013`, `QGR014`, `QGR015`)**: Three new AST Guardrails will be added to `@[scripts/_ast_guardrails.py#L170-L665]` with full unit test coverage in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L836-L842]`.
>   - `QGR013`: Ban `TypeVar()` instantiation (mandate PEP 695 `[T: Bound]`).
>   - `QGR014`: Ban `AsyncMock` / `MagicMock` in `backend_v2/tests/unit/services/` for Protocol-defined repositories (mandate `InMemory` fakes).
>   - `QGR015`: Ban `typing.TypeGuard` (mandate `typing.TypeIs` per PEP 742).
> - **In-Memory Protocol Fakes**: A dedicated test infrastructure module (`[NEW] backend_v2/tests/fakes/in_memory_repositories.py`) will be introduced to host protocol-conforming fakes (`InMemoryWorkflowRepository`, `InMemoryExecutionRepository`, `InMemoryComponentRepository`), phasing out brittle `AsyncMock` stubbing.
> - **Automated Test Mock Migration (Codemod)**: A dedicated utility script (`[NEW] scripts/migrate_mocks_to_inmemory_fakes.py`) will be created to programmatically migrate legacy `AsyncMock` repository stubbing in service unit tests to `InMemory...Repository` fakes.
> - **PEP 695 / PEP 698 Modernization**: Legacy `TypeVar` usages (specifically in `@[backend_v2/core/hook_registry.py#L114-L141]`) will be refactored to PEP 695 generic syntax (`def register[F: HookFunction](...)`), and subclass overrides will enforce `@override`.

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **AST Guardrail Engine** (`@[scripts/_ast_guardrails.py#L170-L665]`) | Banned `TypeVar()`, raw `AsyncMock`/`MagicMock` for Protocol repos in service tests, and `typing.TypeGuard`. | Deterministic AST scanning with zero reflection using `QuorumGuardrailVisitor` and pure structural pattern matching. | Pruned speculative external linters or complex macro frameworks; enforce via native `ast.NodeVisitor`. | `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -v` (QGR013–QGR015 test cases). |
| **Hook Registry & Core Generics** (`@[backend_v2/core/hook_registry.py#L101-L231]`) | Banned module-level `F = TypeVar("F", bound=HookFunction)` and loose untyped decorator returns. | PEP 695 generic method syntax `def register[F: HookFunction](self, name: str) -> Callable[[F], F]:`. | Pruned redundant generic class wrappers or generic registry metaclasses; keep clean singleton with typed decorators. | `uv run pytest backend_v2/tests/unit/core/test_hook_registry.py -v` and `uv run python scripts/backend_audit_loop.py backend_v2/core/hook_registry.py --test`. |
| **In-Memory Test Fakes** (`[NEW] backend_v2/tests/fakes/in_memory_repositories.py`) | Banned brittle `AsyncMock(return_value={...})` dict-returning stubs that bypass domain model hydration. | 100% Protocol-conforming in-memory stores with `@override` and Pydantic V2 domain model return contracts (`IWorkflowRepository`, `IExecutionRepository`, `IComponentRepository`). | Pruned full SQLite/Postgres in-memory DB engines for unit tests; use simple atomic in-memory dictionaries with domain validation. | `uv run pytest backend_v2/tests/unit/fakes/test_in_memory_repositories.py -v`. |
| **Test Mock Migration Codemod** (`[NEW] scripts/migrate_mocks_to_inmemory_fakes.py`) | Banned manual error-prone find-and-replace across test files or leaving broken mock configurations intact. | Programmatic AST / regex codemod with `--dry-run` and `--apply` modes, replacing `AsyncMock` repository fixtures with `InMemory...Repository`. | Pruned heavy libcst dependencies; use Python standard `ast` / `re` for deterministic file transformations. | `uv run python scripts/migrate_mocks_to_inmemory_fakes.py --dry-run` followed by `uv run pytest backend_v2/tests/unit/services/ -v`. |
| **Rules & Knowledge Architecture** (`@[.agents/rules/01-python-backend.md]` & `@[docs/architecture/00_README_META_ARCHITECTURE.md]`) | Banned unrecorded architectural rules or out-of-sync documentation. | Synchronized `01-python-backend.md` rules and canonical Knowledge Item `ki_modern_python_typing_protocol_architecture.md`. | Pruned historical migration narratives; document current present-tense invariants and clear transition matrix. | `uv run python scripts/backend_audit_loop.py backend_v2/ --test` and dual-axis consistency verification. |

---

## Phase 1: Pre-Implementation Cleanups & Touched Scope Debt Sweep

Prior to modifying core systems, the following discovered technical debt items and baseline validations must be addressed:
1. **AST Guardrail Baseline Check**: Run `uv run python scripts/_ast_guardrails.py backend_v2/` to ensure zero existing fatal violations before introducing new rules.
2. **Hook Registry Import Cleanliness**: In `@[backend_v2/core/hook_registry.py#L101-L231]`, remove unused `TypeVar` import after migrating to PEP 695 generics.
3. **Boundary Exemption Confirmation**: Ensure `scripts/_ast_guardrails.py` maintains `BOUNDARY_EXEMPTION_FILES` without regressions while applying new rules.

---

## Proposed Changes

### AST Guardrails & Quality Gate (`scripts/`)

#### [MODIFY] [scripts/_ast_guardrails.py](file:///c:/src/quorum/scripts/_ast_guardrails.py)
- Implement `QGR013`: Ban `TypeVar()` instantiation (mandate PEP 695 `[T: Bound]`).
- Implement `QGR014`: Ban `AsyncMock` / `MagicMock` in `backend_v2/tests/unit/services/` for Protocol-defined repositories (mandate `InMemory` fakes).
- Implement `QGR015`: Ban `typing.TypeGuard` (mandate `typing.TypeIs` per PEP 742).

#### [MODIFY] [backend_v2/tests/unit/scripts/test_ast_guardrails.py](file:///c:/src/quorum/backend_v2/tests/unit/scripts/test_ast_guardrails.py)
- Add comprehensive positive and negative test cases for `QGR013`, `QGR014`, and `QGR015`.

---

### Core & Generic Modernization (`backend_v2/core/`)

#### [MODIFY] [backend_v2/core/hook_registry.py](file:///c:/src/quorum/backend_v2/core/hook_registry.py)
- Refactor `F = TypeVar("F", bound=HookFunction)` at line 98 to PEP 695 generic method: `def register[F: HookFunction](self, name: str) -> Callable[[F], F]:`.
- Remove `TypeVar` from `from typing import ...` at line 13.

---

### Test Infrastructure & Protocol Fakes (`backend_v2/tests/` & `scripts/`)

#### [NEW] [backend_v2/tests/fakes/in_memory_repositories.py](file:///c:/src/quorum/backend_v2/tests/fakes/in_memory_repositories.py)
- Implement `InMemoryWorkflowRepository` conforming strictly to `IWorkflowRepository(Protocol)` in `@[backend_v2/database/interfaces.py#L41-L60]`.
- Implement `InMemoryExecutionRepository` conforming strictly to `IExecutionRepository(Protocol)` in `@[backend_v2/database/interfaces.py#L25-L38]`.
- Implement `InMemoryComponentRepository` conforming strictly to `IComponentRepository(Protocol)` in `@[backend_v2/database/interfaces.py#L82-L95]`.
- All methods decorated with `@override` and strictly type-checked against domain DTOs.

#### [NEW] [backend_v2/tests/unit/fakes/test_in_memory_repositories.py](file:///c:/src/quorum/backend_v2/tests/unit/fakes/test_in_memory_repositories.py)
- Unit tests verifying contract fidelity of in-memory fakes.

#### [NEW] [scripts/migrate_mocks_to_inmemory_fakes.py](file:///c:/src/quorum/scripts/migrate_mocks_to_inmemory_fakes.py)
- Automated codemod script using AST / regex transformations to replace `AsyncMock` repository patterns with `InMemoryWorkflowRepository` and `InMemoryExecutionRepository`.

---

### Rules & Knowledge Base (`.agents/` & `<appDataDir>\knowledge\`)

#### [MODIFY] [.agents/rules/01-python-backend.md](file:///c:/src/quorum/.agents/rules/01-python-backend.md)
- Update `python_314_modern_syntax`, `pep742_typeis_over_typeguard`, and `pep695_generics` rule blocks to document QGR013–QGR015 enforcement.

#### [NEW] [<appDataDir>\knowledge\modern_python_typing_protocol_architecture\artifacts\ki_modern_python_typing_protocol_architecture.md](file:///c:/src/quorum/docs/architecture/ki_modern_python_typing_protocol_architecture.md)
- Create Knowledge Item documenting the 10-point transition matrix, Protocol fakes architecture, automated migration tooling, and quality gate enforcement pipeline.

---

## Execution Protocol

```xml
<execution_protocol>
  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  </required_context_rules>

  <step id="0" name="Strategic Alignment Check & Pre-Implementation Cleanups">
    <action>Verify clean working tree baseline and ensure zero pending AST violations.</action>
    <action>Run `uv run python scripts/_ast_guardrails.py backend_v2/` to ensure current clean baseline.</action>
    <constraint invariant="universal_quality_gate">Quality gate baseline must be 100% green.</constraint>
  </step>

  <step id="1" name="Implement AST Guardrails (QGR013-QGR015) in _ast_guardrails.py">
    <action>Add QGR013 (TypeVar Ban), QGR014 (Mock in Service Test Ban), and QGR015 (TypeGuard Ban) to `QuorumGuardrailVisitor` in @[scripts/_ast_guardrails.py#L170-L665].</action>
    <action>Add comprehensive ISTQB unit tests in @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L836-L842] covering both positive detections and suppressed / exempted cases.</action>
    <constraint invariant="ast_guardrail_mandate">All new rules must have 100% test coverage and explicit error codes.</constraint>
  </step>

  <step id="2" name="Refactor Core Generic Syntax in hook_registry.py">
    <action>Replace legacy `TypeVar` in @[backend_v2/core/hook_registry.py#L101-L231] with PEP 695 generic function syntax `def register[F: HookFunction](self, name: str) -> Callable[[F], F]:`.</action>
    <action>Run `uv run pytest backend_v2/tests/unit/core/test_hook_registry.py` and `uv run python scripts/backend_audit_loop.py backend_v2/core/hook_registry.py --test`.</action>
    <constraint invariant="python_314_modern_syntax">Use PEP 695 generics natively without TypeVar.</constraint>
  </step>

  <step id="3" name="Build In-Memory Protocol Fakes Infrastructure">
    <action>Create [NEW] `backend_v2/tests/fakes/in_memory_repositories.py` defining `InMemoryWorkflowRepository` and `InMemoryExecutionRepository` conforming to @[backend_v2/database/interfaces.py#L25-L60].</action>
    <action>Create [NEW] contract verification tests in `backend_v2/tests/unit/fakes/test_in_memory_repositories.py`.</action>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/fakes/in_memory_repositories.py --test`.</action>
    <constraint invariant="the_zero_compromise_pledge">Fakes must satisfy 100% of Protocol method signatures with @override.</constraint>
  </step>

  <step id="4" name="Implement Automated Mock Migration Codemod Script & Migrate Target Service Tests">
    <action>Create [NEW] `scripts/migrate_mocks_to_inmemory_fakes.py` with dry-run and apply modes to replace `AsyncMock` repository patching with `InMemory...Repository` instances.</action>
    <action>Execute migration on service test suites and verify all migrated tests pass with `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/ --test`.</action>
    <constraint invariant="zero_service_layer_fallbacks">Service unit tests must consume strictly typed In-Memory protocol fakes.</constraint>
  </step>

  <step id="5" name="Synchronize Architectural Rules & Knowledge Items">
    <action>Update @[.agents/rules/01-python-backend.md] with explicit QGR013–QGR015 mandates.</action>
    <action>Create Knowledge Item `ki_modern_python_typing_protocol_architecture.md` under `<appDataDir>\knowledge\modern_python_typing_protocol_architecture\`.</action>
    <action>Run full backend quality loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.</action>
    <constraint invariant="dual_axis_documentation_mandate">Rules and Knowledge Items must be synchronized synchronously.</constraint>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
- **AST Guardrails Unit Tests**: `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -v`
- **Core Hook Registry Tests**: `uv run pytest backend_v2/tests/unit/core/test_hook_registry.py -v`
- **In-Memory Fakes Contract Tests**: `uv run pytest backend_v2/tests/unit/fakes/test_in_memory_repositories.py -v`
- **Migrated Service Tests**: `uv run pytest backend_v2/tests/unit/services/ -v`
- **Global Backend Completion Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
- **Full AST Codebase Scan**: `uv run python scripts/_ast_guardrails.py backend_v2/ --strict`

### Manual Verification
- Verify that `mypy --strict` passes with 0 errors across all modified modules.
- Verify that Ruff formatting (`ruff check`, `ruff format`) reports 0 errors.


