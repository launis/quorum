<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: Refine and Modernize Tier 3 God Code Decomposition Workflow & Tooling

## Executive Summary

Following the initial full execution of the modernized `/tier3-god-code-decomposition` workflow on `backend_v2/services/auth.py` and the subsequent decomposition of `backend_v2/services/export_service.py`, four structural improvement areas were identified to elevate decomposition quality, type safety, and automation ergonomics:

1. **Facade Class Size Limit & Immutable Dependency Injection**:
   - *Problem*: The `AuthService` package facade (`__init__.py`) swelled to 416 lines due to mechanical delegation and cross-cutting mutable property getters and setters (`use_firebase`, `firebase_auth`, `_initialized_firebase`).
   - *Modernization*: Establish a strict architectural cap: package facade classes in `__init__.py` MUST NOT exceed 300 lines. Enforce immutable dependency injection in `__init__`, banning mutable property setters across sub-services unless explicitly required by an external library/mock interface.
2. **Package Facade Test Discovery & Audit Loop Targeting**:
   - *Problem*: Targeting `backend_audit_loop.py` directly at `__init__.py` historically caused ambiguity in locating the matching test suite.
   - *Modernization*: Codify the execution rule: when auditing a package facade, agents must either target the entire package directory (specifically: `backend_v2/services/auth/ --test`) OR name the facade test explicitly as `test_{pkg}_facade.py` or `test_{pkg}.py`. Ensure `scripts/backend_audit_loop.py` candidate discovery documentation and handling reflect this standard.
3. **Strict Markdown Boundary `[NEW]` Tagging in Planning Workflows**:
   - *Problem*: Planning workflows frequently generated `@-reference` links for files that do not yet exist on disk without the `[NEW]` tag prefix, triggering fatal `MBD003` errors during `scripts/audit_markdown_boundaries.py` validation.
   - *Modernization*: Hardcode a zero-tolerance `MBD003` gate in both `@[.agents/workflows/tier0-create-plan.md]` and `@[.agents/workflows/tier3-god-code-decomposition.md]`, mandating that every planned file path not yet present on disk MUST be prefixed with `[NEW]` across all tables, lists, text references, and XML tags.
4. **Protocol-Driven Inversion for Inter-Bounded Context Collaboration**:
   - *Problem*: Cross-context service dependencies (specifically: `OrganizationService` requiring user creation capability from `UserService`) were resolved by passing loose callbacks (`Callable[..., Coroutine[Any, Any, User]]`), throwing away argument type safety and risking signature drift.
   - *Modernization*: Mandate the use of lightweight `typing.Protocol` interfaces (specifically: `UserCreatorProtocol`) in `services/[domain]/protocols.py` instead of raw `Callable` functions. This guarantees strict compile-time checking of all parameter types and return values by MyPy.
5. **Reference Implementation & Empirical Proof in Auth Package**:
   - *Proof of Invariants*: Apply these principles directly to `backend_v2/services/auth/`: introduce `[NEW] @[backend_v2/services/auth/protocols.py]`, update `OrganizationService` to consume `UserCreatorProtocol`, and refactor `AuthService` facade down from 416 lines to under 300 lines while preserving 100% test passing parity across all 116 tests.

---

## Scope & Target Boundaries

### Target Files (Read-Write)
- `[MODIFY] @[.agents/workflows/tier3-god-code-decomposition.md]` (Facade <300 line cap, immutable DI, package audit convention, [NEW] tagging mandate, typed Protocol standard)
- `[MODIFY] @[.agents/workflows/tier0-create-plan.md]` (MBD003 Zero-Tolerance Gate & Universal [NEW] tagging instructions)
- `[MODIFY] @[.agents/rules/01-python-backend.md]` (Package facade architecture rule, immutable DI, Protocol over loose Callable)
- `[MODIFY] @[scripts/backend_audit_loop.py#L73-L348]` (Test discovery documentation & robust candidate handling for package facades)
- `[NEW] @[backend_v2/services/auth/protocols.py]` (Typed `UserCreatorProtocol` interface for cross-context dependency inversion)
- `[MODIFY] @[backend_v2/services/auth/organization_service.py#L42-L299]` (Consume `UserCreatorProtocol` instead of loose `Callable`, Fail-Fast on missing creator)
- `[MODIFY] @[backend_v2/services/auth/__init__.py#L78-L415]` (Refactor `AuthService` facade to <300 lines, prune mutable property setters, streamline DI via constructor)
- `[MODIFY] @[backend_v2/tests/unit/test_organization_service.py#L712-L770]` (Update `test_delete_organization_non_empty_with_force_cascades_deletion_and_logs_audit` to pass `firebase_auth=mock_fb` immutably)
- `[MODIFY] @[backend_v2/tests/unit/test_organization_service.py#L773-L816]` (Verify `UserCreatorProtocol` compliance and Fail-Fast on missing creator)
- `[MODIFY] @[backend_v2/tests/unit/test_auth.py#L308-L461]` (Verify streamlined facade delegations, immutable DI, and line count cap <300)
- `[MODIFY] @[backend_v2/tests/unit/test_user_service.py#L169-L257]` (Migrate mutable property setters to immutable constructor injection)
- `[MODIFY] @[backend_v2/tests/unit/test_token_service.py#L181-L226]` (Migrate mutable property setters to immutable constructor injection)

### Context Files (Read-Only)
- `@[.agents/rules/00-antigravity-core.md]`
- `@[.agents/rules/04_directory_reference.md]`
- `@[ki_god_code_prevention.md]`
- `@[ki_deterministic_hardening_state.md]`
- `@[ki_zero_permissive_typing.md]`
- `@[scripts/audit_markdown_boundaries.py]`
- `@[scripts/_ast_guardrails.py]`

---

### Pre-Implementation Technical Debt Cleanups

1. **OrganizationService Loose Callable & Silent Failure**:
   - `create_user_fn: Callable[..., Coroutine[Any, Any, User]] | None = None` in `@[backend_v2/services/auth/organization_service.py#L54-L78]` discards argument type safety and allows signature drift.
   - `create_organization` in `@[backend_v2/services/auth/organization_service.py#L80-L135]` silently skips admin user creation if `create_user_fn` is `None`, creating orphaned tenant records without an admin user.
2. **AuthService Monolithic Swell & Mutable Setters**:
   - `AuthService` in `@[backend_v2/services/auth/__init__.py#L78-L415]` reaches 416 lines due to duplicate cross-cutting mutable setters (`@use_firebase.setter`, `@firebase_auth.setter`, `@_initialized_firebase.setter`), un-grouped 33-line imports, and redundant private helper delegations.
   - `AuthService.__init__` lacks an explicit `firebase_auth` parameter, forcing unit tests (`test_user_service.py`, `test_token_service.py`) into mutating properties post-instantiation.
3. **MBD003 Pre-Creation Lint Failure Risk**:
   - Planning workflows frequently reference uncreated files without `[NEW]` prefixes, breaking Markdown boundary validation in automated CI.
4. **test_organization_service.py Post-Instantiation Mutation**:
   - `test_delete_organization_non_empty_with_force_cascades_deletion_and_logs_audit` in `@[backend_v2/tests/unit/test_organization_service.py#L712-L770]` mutates `auth_service.firebase_auth = mock_fb` post-instantiation instead of passing it to constructor.

---

### 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **@[.agents/workflows/tier3-god-code-decomposition.md]** | Uncapped package facades (>300 lines) with mutable cross-cutting property setters; loose `Callable` callbacks for cross-subservice calls; un-prefixed references to planned files violating MBD003. | Facade line cap (<300 lines); immutable DI in `__init__`; package audit convention (`<pkg_path>/ --test`); universal `[NEW]` tagging; `typing.Protocol` in `protocols.py`. | Pruned speculative generic DI containers or multi-class facade hierarchies in favor of single-file `<300` line aggregate facade. | `uv run python scripts/audit_markdown_boundaries.py --file .agents/workflows/tier3-god-code-decomposition.md` |
| **@[.agents/workflows/tier0-create-plan.md]** | Omitting `[NEW]` prefix on planned target files across tables, lists, text references, and XML tags causing MBD003 boundary lint failures. | Universal `[NEW]` Pre-Creation Tagging Mandate enforced in `context_rules` and `HYBRID_XML_SANDWICH_MANDATE`. | Pruned complex dynamic path existence scrapers in favor of explicit zero-tolerance static `[NEW]` tagging contract. | `uv run python scripts/audit_markdown_boundaries.py --file .agents/workflows/tier0-create-plan.md` |
| **@[.agents/rules/01-python-backend.md]** | Mutable property setters across sub-services in facades; passing untyped or loose `Callable[..., Coroutine[Any, Any, User]]` across domain boundaries. | Formalized `rule_block id="package_facade_and_inter_context_protocol_mandate"`: package facades <300 lines with immutable DI; sub-services communicating via typed `typing.Protocol` contracts. | Pruned abstract base classes or complex message brokers in favor of lightweight `typing.Protocol`. | `uv run python scripts/audit_markdown_boundaries.py --file .agents/rules/01-python-backend.md` |
| **@[scripts/backend_audit_loop.py#L73-L348]** | Ambiguous or missing candidate test matching when targeting package `__init__.py` files; unclear package directory audit documentation. | Explicit test candidate resolution for `__init__.py` (`test_{pkg}.py`, `test_{pkg}_facade.py`, `test_facade.py`) and documented package aggregate runner (`<package_dir>/ --test`). | Pruned complex heuristic AST import crawlers in favor of deterministic candidate pattern matching list. | `uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py --test` |
| **[NEW] @[backend_v2/services/auth/protocols.py]** | Loose `Callable` callbacks with `Any` types (`Callable[..., Coroutine[Any, Any, User]]`) or hallucinated signatures bypassing compile-time safety. | Sovereign `UserCreatorProtocol(Protocol)` with exact physical signature: `async def __call__(self, creator_id: str, user_data: UserCreate, force_org_id: str | None = None) -> User: ...`. | Pruned heavy base classes, runtime decorators, or wrapper adapters; pure structural `typing.Protocol`. | `uv run mypy --strict backend_v2/services/auth/protocols.py` |
| **@[backend_v2/services/auth/organization_service.py#L42-L299]** | `create_user_fn: Callable[..., Coroutine[Any, Any, User]] | None = None`; silent bypass in `create_organization` when `user_creator is None` creating tenant without admin user. | Inject `user_creator: UserCreatorProtocol | None = None`; enforce Fail-Fast `AppException(ErrorCodes.CONFIGURATION_ERROR)` in `create_organization` if `user_creator is None`. | Pruned dual-parameter fallback (`user_creator or create_user_fn`); clean single sovereign parameter `user_creator`. | `uv run python scripts/backend_audit_loop.py backend_v2/services/auth/organization_service.py --test --ast-strict` |
| **@[backend_v2/services/auth/__init__.py#L78-L415]** | Monolithic 416-line facade; mutable property setters (`@use_firebase.setter`, `@firebase_auth.setter`, `@_initialized_firebase.setter`); lack of `firebase_auth` parameter in `__init__`. | Refactor `AuthService` facade to <300 lines; pass `firebase_auth: Any = None` directly in `__init__`; wire `self.user_service._create_user_internal` to `OrganizationService(user_creator=...)`; prune mutable setters. | Pruned sprawling docstring repetitions and 33-line unfolded imports into concise, PEP 257 compliant docstrings and grouped imports. | `uv run python scripts/backend_audit_loop.py backend_v2/services/auth/__init__.py --test --ast-strict` |
| **@[backend_v2/tests/unit/test_organization_service.py#L712-L770]** | Relying on removed mutable property setter (`auth_service.firebase_auth = mock_fb`) in `test_delete_organization_non_empty_with_force_cascades_deletion_and_logs_audit`. | Pass `firebase_auth=mock_fb` immutably to `AuthService(mock_repo, audit_service=mock_audit, use_firebase=True, firebase_auth=mock_fb)`. | Pruned post-instantiation setter mutation in favor of immutable constructor dependency injection. | `uv run pytest backend_v2/tests/unit/test_organization_service.py -k test_delete_organization_non_empty_with_force_cascades_deletion_and_logs_audit` |
| **@[backend_v2/tests/unit/test_organization_service.py#L773-L816]** | Instantiating `OrganizationService` with loose mock callable without protocol signature verification; tolerating unverified admin creation bypass. | Update `test_direct_organization_service_execution` to pass `user_creator=mock_create_user`; add negative test verifying `create_organization` raises `AppException` when `user_creator is None`. | Pruned redundant mock wrapper fixtures. | `uv run pytest backend_v2/tests/unit/test_organization_service.py -v` |
| **@[backend_v2/tests/unit/test_auth.py#L308-L461]** | Testing mutable property setters on facade (`auth_service.use_firebase = True`, `auth_service.firebase_auth = mock_fb`); testing obsolete private delegations. | Update tests to verify immutable DI via `AuthService(..., use_firebase=True, firebase_auth=mock_fb)` and assert line count of `__init__.py` is strictly `< 300`. | Pruned obsolete test cases asserting mutable property mutations. | `uv run pytest backend_v2/tests/unit/test_auth.py -v` |
| **@[backend_v2/tests/unit/test_user_service.py#L169-L257]** | Relying on removed mutable property setters (`auth.use_firebase = True`, `auth.firebase_auth = mock_fb`) in `test_auth_service_create_user_firebase_flow`. | Refactor test to instantiate `AuthService` with immutable constructor parameters: `AuthService(mock_repo, use_firebase=True, firebase_auth=mock_fb)`. | Pruned 2-step mutable setup in favor of 1-line immutable constructor call. | `uv run pytest backend_v2/tests/unit/test_user_service.py -k test_auth_service_create_user_firebase_flow` |
| **@[backend_v2/tests/unit/test_token_service.py#L181-L226]** | Relying on removed mutable property setters (`auth.use_firebase = True`, `auth.firebase_auth = mock_fb`) in `test_auth_service_verify_token_firebase_branches`. | Refactor test to instantiate `AuthService` with immutable constructor parameters: `AuthService(mock_repo, use_firebase=True, firebase_auth=mock_fb)`. | Pruned 2-step mutable setup in favor of 1-line immutable constructor call. | `uv run pytest backend_v2/tests/unit/test_token_service.py -k test_auth_service_verify_token_firebase_branches` |

---

## Execution Instructions

```xml
<execution_protocol>
  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  </required_context_rules>

  <phase id="1" name="WORKFLOW_AND_RULES_MODERNIZATION">
    <step id="1" name="UPDATE_TIER3_DECOMPOSITION_WORKFLOW">
      <action>
        Update `@[.agents/workflows/tier3-god-code-decomposition.md]` to incorporate the 4 architectural improvements:
        1. In `strangler_fig_mandate` (lines 75-78), add the **Facade Size &amp; Immutability Standard**:
           - Package facade (`__init__.py`) classes MUST NOT exceed 300 lines of code.
           - Facades MUST wire dependencies immutably in `__init__`.
           - Sprawling mutable `@property` and `@setter` delegations across sub-services are strictly banned unless explicitly demanded by third-party library mock interfaces.
        2. In `test_baseline` and test discovery rules (line 139), document the **Package Audit Convention**:
           - When validating a package facade (`__init__.py`), the primary audit command MUST target the package directory: `uv run python scripts/backend_audit_loop.py <package_path>/ --test`.
           - When targeting `__init__.py` individually, the matching unit test file MUST follow the naming convention `test_{pkg_name}_facade.py` or `test_{pkg_name}.py`.
        3. In `anti_abstraction_and_context_amnesia_mandate` (line 119), harden the **Universal [NEW] Pre-Creation Tagging Mandate**:
           - Explicitly require `[NEW]` prefix on EVERY line where an uncreated target file is mentioned, specifically in tables, lists, text references, and XML tags, to mathematically satisfy MBD003.
        4. In `topological_leaf_first_extraction_mandate` (line 90), codify the **Protocol-Driven Inversion Law**:
           - Banned pattern: Passing untyped or loose `Callable[..., Coroutine]` callbacks for cross-subservice execution.
           - Mandatory pattern: Define a lightweight `typing.Protocol` in `protocols.py` within the domain subpackage to enforce full compile-time parameter and return type safety.
      </action>
      <verification>
        Run: `uv run python scripts/audit_markdown_boundaries.py --file .agents/workflows/tier3-god-code-decomposition.md`
      </verification>
    </step>

    <step id="2" name="UPDATE_TIER0_PLAN_WORKFLOW">
      <action>
        Update `@[.agents/workflows/tier0-create-plan.md]` in `context_rules` and `execution_protocol`:
        1. Inject `rule_block id="universal_new_tagging_mandate"`:
           - All proposed files that do not currently exist in the filesystem MUST be prefixed with `[NEW]` in all markdown tables, bullet points, file headers, and XML payloads.
           - Omitting `[NEW]` triggers fatal `MBD003` in `audit_markdown_boundaries.py`.
        2. Update `HYBRID_XML_SANDWICH_MANDATE` to explicitly mandate `[NEW]` tagging on every target boundary entry and table row for uncreated files.
      </action>
      <verification>
        Run: `uv run python scripts/audit_markdown_boundaries.py --file .agents/workflows/tier0-create-plan.md`
      </verification>
    </step>

    <step id="3" name="UPDATE_PYTHON_BACKEND_RULES">
      <action>
        Update `@[.agents/rules/01-python-backend.md]` to formalize the backend architectural laws:
        1. Add `rule_block id="package_facade_and_inter_context_protocol_mandate"`:
           - Package facades (`__init__.py`) MUST be strictly under 300 lines and act purely as immutable dependency injection routers and re-export entry points.
           - Mutable `@property` setters mutating sub-service state are strictly prohibited.
           - Sub-services collaborating across bounded contexts MUST communicate via typed `typing.Protocol` contracts rather than loose `Callable[..., Any]` functions.
      </action>
      <verification>
        Run: `uv run python scripts/audit_markdown_boundaries.py --file .agents/rules/01-python-backend.md`
      </verification>
    </step>

    <step id="4" name="VERIFY_BACKEND_AUDIT_LOOP_FACADE_HANDLING">
      <action>
        Inspect and verify `@[scripts/backend_audit_loop.py#L73-L348]`:
        1. Ensure candidates list for `__init__.py` explicitly documents and tests:
           - `test_{pkg_name}.py`
           - `test_{pkg_name}_facade.py`
           - `test_facade.py`
        2. Ensure comments and help strings clearly guide developers that auditing a package directory (specifically: `backend_v2/services/auth/ --test`) runs the aggregate package suite.
      </action>
      <verification>
        Run: `uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py --test`
      </verification>
    </step>
  </phase>

  <phase id="2" name="REFERENCE_IMPLEMENTATION_AND_AUTH_PROOF">
    <step id="5" name="CREATE_AUTH_PROTOCOLS_MODULE">
      <action>
        Create `[NEW] @[backend_v2/services/auth/protocols.py]` defining the `UserCreatorProtocol` matching the physical signature of `UserService._create_user_internal`:
        ```python
        """Protocol definitions for auth subpackage bounded context decoupling."""

        from __future__ import annotations

        from typing import Protocol

        from backend_v2.models.auth import User, UserCreate

        class UserCreatorProtocol(Protocol):
            """Protocol for decoupling organization-level user creation from UserService implementation."""

            async def __call__(
                self,
                creator_id: str,
                user_data: UserCreate,
                force_org_id: str | None = None,
            ) -> User:
                """Create a user within the specified organization."""
                ...
        ```
      </action>
      <verification>
        Run: `uv run mypy --strict backend_v2/services/auth/protocols.py`
      </verification>
    </step>

    <step id="6" name="UPDATE_ORGANIZATION_SERVICE_PROTOCOL_TYPING">
      <action>
        Update `@[backend_v2/services/auth/organization_service.py#L42-L299]`:
        1. Import `UserCreatorProtocol` from `backend_v2.services.auth.protocols`.
        2. Replace `create_user_fn: Callable[..., Coroutine[Any, Any, User]] | None = None` in `__init__` with:
           `user_creator: UserCreatorProtocol | None = None`.
        3. Store strictly as `self.user_creator = user_creator`.
        4. In `create_organization`, enforce Fail-Fast if `self.user_creator is None`:
           ```python
           if self.user_creator is None:
               raise AppException(
                   message="Cannot create organization: UserCreatorProtocol is not configured.",
                   status_code=500,
                   details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
               )
           await self.user_creator(initiator.id, admin_payload, force_org_id=org_id)
           ```
        5. Remove unneeded `from collections.abc import Callable, Coroutine`.
      </action>
      <verification>
        Run: `uv run python scripts/backend_audit_loop.py backend_v2/services/auth/organization_service.py --test`
      </verification>
    </step>

    <step id="7" name="STREAMLINE_AUTH_SERVICE_FACADE">
      <action>
        Refactor `@[backend_v2/services/auth/__init__.py#L78-L415]` to strictly satisfy the &lt;300 line cap:
        1. Retain all public facade methods and `__all__` symbols (`AuthService`, constants, repositories, subservices) and add `UserCreatorProtocol` to `__all__` and re-exports.
        2. In `__init__`, accept `firebase_auth: Any = None` directly to enable immutable dependency injection from callers.
        3. Pass `firebase_auth` to `self.token_service.firebase_auth`, `self.user_service.firebase_auth`, and `self.org_service.firebase_auth` during initialization.
        4. In `__init__`, pass `self.user_service._create_user_internal` to `user_creator` parameter of `OrganizationService`.
        5. Remove bloated cross-cutting mutable setters (`@use_firebase.setter`, `@firebase_auth.setter`, `@_initialized_firebase.setter`). Retain pure read-only properties if needed.
        6. Consolidate unpacked re-exports (grouping constants into single multi-line `from ... import` blocks) and streamline one-line delegation methods. Ensure total line count is strictly under 300 lines (target: ~240-270 lines).
      </action>
      <verification>
        Run: `uv run python scripts/backend_audit_loop.py backend_v2/services/auth/__init__.py --test`
      </verification>
    </step>

    <step id="8" name="UPDATE_AUTH_TEST_SUITE">
      <action>
        Update all 4 unit test suites consuming `AuthService` and `OrganizationService`:
        1. `@[backend_v2/tests/unit/test_organization_service.py#L712-L770]`: update `test_delete_organization_non_empty_with_force_cascades_deletion_and_logs_audit` to pass `firebase_auth=mock_fb` immutably to `AuthService(mock_repo, audit_service=mock_audit, use_firebase=True, firebase_auth=mock_fb)`.
        2. `@[backend_v2/tests/unit/test_organization_service.py#L773-L816]`: update `test_direct_organization_service_execution` to pass `user_creator=mock_create_user`, and add a negative test verifying `create_organization` raises `AppException` when `user_creator` is `None`.
        3. `@[backend_v2/tests/unit/test_auth.py#L308-L461]`: update `test_auth_service_facade_delegates_all_operations` to verify immutable DI without relying on mutable property setters, and assert line count of `backend_v2/services/auth/__init__.py` is &lt; 300 lines.
        4. `@[backend_v2/tests/unit/test_user_service.py#L169-L257]`: update `test_auth_service_create_user_firebase_flow` to pass `use_firebase=True, firebase_auth=mock_fb` immutably to `AuthService(...)`.
        5. `@[backend_v2/tests/unit/test_token_service.py#L181-L226]`: update `test_auth_service_verify_token_firebase_branches` to pass `use_firebase=True, firebase_auth=mock_fb` immutably to `AuthService(...)`.
      </action>
      <verification>
        Run: `uv run python scripts/backend_audit_loop.py backend_v2/services/auth/ --test --ast-strict`
      </verification>
    </step>
  </phase>

  <phase id="3" name="AUTOMATED_QUALITY_GATES_AND_AUDIT">
    <step id="9" name="MARKDOWN_BOUNDARY_VALIDATION">
      <action>
        Run `scripts/audit_markdown_boundaries.py` on all modified workflow files and the implementation plan.
      </action>
      <verification>
        Run:
        - `uv run python scripts/audit_markdown_boundaries.py --file .agents/workflows/tier3-god-code-decomposition.md`
        - `uv run python scripts/audit_markdown_boundaries.py --file .agents/workflows/tier0-create-plan.md`
        - `uv run python scripts/audit_markdown_boundaries.py --file .agents/rules/01-python-backend.md`
        - `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_refine_tier3_decomposition_workflow.md`
      </verification>
    </step>

    <step id="10" name="PACKAGE_AUDIT_COMPLETION_GATE">
      <action>
        Execute the global backend audit loop on the entire auth package with strict AST guardrails.
      </action>
      <verification>
        Run: `uv run python scripts/backend_audit_loop.py backend_v2/services/auth/ --test --ast-strict`
      </verification>
    </step>

    <step id="11" name="FULL_AUTH_REGRESSION_TEST_SUITE">
      <action>
        Execute all 5 modular test files in the auth test suite to mathematically prove 100% regression safety.
      </action>
      <verification>
        Run: `uv run pytest backend_v2/tests/unit/test_auth.py backend_v2/tests/unit/test_organization_service.py backend_v2/tests/unit/test_user_service.py backend_v2/tests/unit/test_token_service.py backend_v2/tests/unit/test_repositories.py`
      </verification>
    </step>
  </phase>
</execution_protocol>
```

---

## Testing & Verification Plan

### Automated Audit Scripts
1. **Markdown Boundaries Audit**:
   ```powershell
   uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_refine_tier3_decomposition_workflow.md
   uv run python scripts/audit_markdown_boundaries.py --file .agents/workflows/tier3-god-code-decomposition.md
   uv run python scripts/audit_markdown_boundaries.py --file .agents/workflows/tier0-create-plan.md
   ```
2. **Backend Package Audit Loop**:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/services/auth/ --test --ast-strict
   ```
3. **Comprehensive Auth Test Suite**:
   ```powershell
   uv run pytest backend_v2/tests/unit/test_auth.py backend_v2/tests/unit/test_organization_service.py backend_v2/tests/unit/test_user_service.py backend_v2/tests/unit/test_token_service.py backend_v2/tests/unit/test_repositories.py -v
   ```

### Negative ISTQB Test Scenarios
1. **Invalid Protocol Parameter Signature**: Pass an incompatible callable to `OrganizationService(user_creator=...)` in a type-checked test or negative test to verify MyPy rejection.
2. **Facade Size Violation**: Assert that `backend_v2/services/auth/__init__.py` has line count strictly `< 300` lines (asserting `len(lines) < 300`).
3. **Uninitialized / Missing User Creator**: Verify `OrganizationService` raises `AppException` with `ErrorCodes.CONFIGURATION_ERROR` if `create_organization` is invoked with initial user creation but `user_creator` is `None`.
4. **Disallowed Mutable Setter Mutation**: Assert that calling `auth.use_firebase = True` or `auth.firebase_auth = mock` raises `AttributeError` on the refactored immutable facade.
