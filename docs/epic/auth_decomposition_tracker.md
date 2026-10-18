# Tracker: auth.py God Code Decomposition

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Target God File Baseline
- **Target File:** `@[backend_v2/services/auth.py]`
- **Baseline Length:** 1234 lines (current: 865 lines after Phase 1, 2, and 3)
- **Symbol Migration Map:** `@[docs/epic/tasks_auth/symbol_migration_map.md]`
- **Baseline Unit Tests:** 80 passed (100% pass rate) in 3.91s
- **Baseline Line Coverage:** 94% across auth modules (266 statements in auth.py, 24 missed)
- **Phase 0 Coverage Bootstrap:** NOT REQUIRED (baseline 94% exceeds 75% prerequisite gate)

## Step Execution Status

### Phase 1: Repositories and Constants Extraction
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_auth/phase1_repositories_and_constants_extraction.md] @[docs/epic/auth_decomposition_tracker.md]`
  - [x] Extract constants to `@[backend_v2/services/auth/constants.py]` [NEW]
  - [x] Extract repositories to `@[backend_v2/services/auth/repositories.py]` [NEW]
  - [x] Rewire `@[backend_v2/services/auth.py]` with explicit re-exports
  - [x] Run quality gates: `uv run pytest backend_v2/tests/unit/test_auth.py --cov=backend_v2.services.auth`

### Phase 2: Token Service Extraction
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_auth/phase2_token_service_extraction.md] @[docs/epic/auth_decomposition_tracker.md]`
  - [x] Extract `TokenService` [NEW] to `@[backend_v2/services/auth/token_service.py]` [NEW]
  - [x] Delegate token methods from `AuthService` in `@[backend_v2/services/auth.py]`
  - [x] Run quality gates: `uv run pytest backend_v2/tests/unit/test_auth.py --cov=backend_v2.services.auth`

### Mid-Extraction Planning Gate
- [x] **[OK] Re-Invoke Tier 3 Planner:** `/tier3-god-code-decomposition @[backend_v2/services/auth.py]` executed to generate detailed execution protocols and test contracts for Phase 3 and Phase 4.

### Phase 3: Organization Service Extraction
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_auth/phase3_organization_service_extraction.md] @[docs/epic/auth_decomposition_tracker.md]`
  - [x] Step 1: Create Organization Service Module `@[backend_v2/services/auth/organization_service.py]` [NEW]
  - [x] Step 2: Delegate and Re-export in `AuthService` (`@[backend_v2/services/auth.py]`)
  - [x] Step 3: Validate and Expand Unit Tests (`@[backend_v2/tests/unit/test_auth.py]`)

### Phase 4: User Service and Facade Extraction
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_auth/phase4_user_service_and_facade_extraction.md] @[docs/epic/auth_decomposition_tracker.md]`
  - [ ] Step 1: Create User Service Module `@[backend_v2/services/auth/user_service.py]` [NEW]
  - [ ] Step 2: Create Sovereign `AuthService` Facade in `@[backend_v2/services/auth/__init__.py]` [NEW]
  - [ ] Step 3: Convert Legacy Auth File to Strangler Fig Proxy (`@[backend_v2/services/auth.py]`)
  - [ ] Step 4: Validate and Expand Unit Tests (`@[backend_v2/tests/unit/test_auth.py]`)

### In-Flight Tier 2 Hardening (Before Consumer Migration)
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Verify 100% typing, linting, docstrings, and tests across newly extracted domain modules before migrating 1-hop consumers:
  - [x] [NEW] @[backend_v2/services/auth/constants.py]
  - [x] [NEW] @[backend_v2/services/auth/repositories.py]
  - [x] [NEW] @[backend_v2/services/auth/token_service.py]
  - [x] [NEW] @[backend_v2/services/auth/organization_service.py]
  - [ ] [NEW] @[backend_v2/services/auth/user_service.py]
  - [ ] [NEW] @[backend_v2/services/auth/__init__.py]

### Proxy Sunset and Consumer Migration (Bounded Batches)
Migration details mapped in `@[docs/epic/tasks_auth/symbol_migration_map.md]`:
- [ ] **[NOK] Batch 1: Dependency Injection Rewiring**: Rewire `@[backend_v2/api/dependencies.py]` to import `AuthService` directly from `backend_v2.services.auth`. Run `uv run python scripts/backend_audit_loop.py backend_v2/api/dependencies.py --test`. Atomic git commit.
- [ ] **[NOK] Batch 2: Unit Test Suite Modularization**: Decompose monolithic `@[backend_v2/tests/unit/test_auth.py]` into domain-specific test suites mirroring extracted modules (`test_token_service.py`, `test_organization_service.py`, `test_user_service.py`, `test_repositories.py`). Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/ --test`. Atomic git commit.

### Pre-Delete Verification Gates
- [ ] **[NOK] Pre-Delete Zero-Reference and Semantic Coverage Audit**:
  - Run `grep_search` across entire codebase (excluding `backend_v2/services/auth.py` itself) to mathematically prove 0 remaining references to the legacy proxy module.
  - Verify line coverage on surviving domain logic remains above 90%.
- [ ] **[NOK] Pre-Flight Global Integration and DI Boot Test**: While `@[backend_v2/services/auth.py]` proxy is still intact, run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` to ensure entire application compiles, all DI containers wire cleanly, and integration tests pass 100% green.

### Physical Proxy Deletion and Post-Delete Lockdown
- [ ] **[NOK] Physical Proxy Deletion**: Completely delete `backend_v2/services/auth.py` from disk.
- [ ] **[NOK] Post-Delete AST Guardrail QGR017 Lockdown**: Register `backend_v2/services/auth.py` in `@[scripts/_ast_guardrails.py]` under rule `QGR017` (FATAL severity), update `@[.agents/rules/04_directory_reference.md]`, and run parameterized `/tier7-describe-architecture` directives.
- [ ] **[NOK] Post-Delete Regression Smoke Test**: Run `uv run python backend_v2/seed/run_seed.py local` and `uv run python scripts/backend_audit_loop.py backend_v2/services/auth/ --test` to mathematically prove zero runtime regressions.

## Instructions for Execution Agent
- **Strangler Fig Invariant**: The proxy file `@[backend_v2/services/auth.py]` must remain in place and operational until Pre-Flight Global Integration and DI Boot Test passes.
- **In-Flight Hardening**: Complete Tier 2 Hardening on extracted modules before consumer migration begins to avoid the Double-Migration trap.
- **Atomic Commits**: Commit each verified phase individually using Conventional Commits syntax with English messages.

# Session Handover Context
## Achieved
- Initialized Tier 3 God Code Decomposition planning for `@[backend_v2/services/auth.py]`.
- Implemented Phase 1: extracted `constants.py` and `repositories.py` (`OrganizationRepository`, `UserRepository`) into `backend_v2/services/auth/`.
- Implemented Phase 2: extracted `TokenService` into `backend_v2/services/auth/token_service.py` [NEW] with 98% line coverage.
- Rewired `AuthService` in `backend_v2/services/auth.py` to delegate token methods and verified 55/55 unit tests passing with 93% line coverage.
- Completed Mid-Extraction Planning Gate: re-invoked `/tier3-god-code-decomposition @[backend_v2/services/auth.py]`.
- Generated comprehensive implementation plan for Phase 3: `@[docs/epic/tasks_auth/phase3_organization_service_extraction.md]` with 19 concrete test contracts (TC-P3-01 through TC-P3-19) covering `OrganizationService`.
- Generated comprehensive implementation plan for Phase 4: `@[docs/epic/tasks_auth/phase4_user_service_and_facade_extraction.md]` with 39 concrete test contracts (TC-P4-01 through TC-P4-39) covering `UserService` and sovereign `AuthService` facade.
- Implemented Phase 3: extracted `OrganizationService` into `backend_v2/services/auth/organization_service.py` [NEW] with 94% line coverage.
- Enhanced `OrganizationRepository` with `update` and `delete` methods for 1:1 symmetry.
- Rewired `AuthService` in `backend_v2/services/auth.py` to delegate organization operations (`create_organization`, `delete_organization`, `list_organizations`, `get_organization`, `update_organization`) to `self.org_service`.
- Implemented all 19 test contracts (TC-P3-01 through TC-P3-19) alongside repository update/delete and direct execution tests; verified 80/80 unit tests pass with 94% overall auth module coverage.
- Passed 10/10 Universal Quality Gate stages with strict AST verification (`scripts/backend_audit_loop.py backend_v2/services/auth.py --test --ast-strict`).

## Learned
- During Strangler Fig decomposition, newly extracted leaf modules must not import the God File. Dependency inversion via optional callbacks (`get_settings_fn`, `create_user_fn`) ensures seamless decoupling between `OrganizationService` and `UserService` without circular dependencies.
- AST boundary auditing (`scripts/audit_markdown_boundaries.py`) parses embedded Python codeblocks; abstract signatures inside markdown action blocks must include pass statements to satisfy AST grammar.
- `ResourceNotFoundError` embeds resource details inside `exc.details["resource_type"]` and `exc.details["resource_id"]` rather than public instance attributes.
- When creating an organization, `_create_user_internal` verifies that the initiator user exists in the repository, and emits a distinct `USER_CREATED` audit event alongside `ORG_CREATED`.

## Remaining
- Execute Phase 4: User Service and Facade Extraction (`@[docs/epic/tasks_auth/phase4_user_service_and_facade_extraction.md]`).
- Execute In-Flight Tier 2 Hardening on `user_service.py` and `__init__.py`.
- Execute Consumer Migration (Batch 1: DI rewiring, Batch 2: unit test modularization).
- Pre-Delete Audits, Physical Proxy Deletion, QGR017 lockdown, and regression smoke test.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/epic/tasks_auth/phase4_user_service_and_facade_extraction.md] @[docs/epic/auth_decomposition_tracker.md]
```
