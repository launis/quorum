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
- **Baseline Length:** 1234 lines
- **Symbol Migration Map:** `@[docs/epic/tasks_auth/symbol_migration_map.md]`
- **Baseline Unit Tests:** 30 passed (100% pass rate) in 7.31s
- **Baseline Line Coverage:** 93% (394 statements, 29 missed)
- **Phase 0 Coverage Bootstrap:** NOT REQUIRED (baseline 93% exceeds 75% prerequisite gate)

## Step Execution Status

### Phase 1: Repositories and Constants Extraction
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_auth/phase1_repositories_and_constants_extraction.md] @[docs/epic/auth_decomposition_tracker.md]`
  - [x] Extract constants to `@[backend_v2/services/auth/constants.py]` [NEW]
  - [x] Extract repositories to `@[backend_v2/services/auth/repositories.py]` [NEW]
  - [x] Rewire `@[backend_v2/services/auth.py]` with explicit re-exports
  - [x] Run quality gates: `uv run pytest backend_v2/tests/unit/test_auth.py --cov=backend_v2.services.auth`

### Phase 2: Token Service Extraction
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_auth/phase2_token_service_extraction.md] @[docs/epic/auth_decomposition_tracker.md]`
  - [ ] Extract `TokenService` [NEW] to `@[backend_v2/services/auth/token_service.py]` [NEW]
  - [ ] Delegate token methods from `AuthService` in `@[backend_v2/services/auth.py]`
  - [ ] Run quality gates: `uv run pytest backend_v2/tests/unit/test_auth.py --cov=backend_v2.services.auth`

### Mid-Extraction Planning Gate
- [ ] **[NOK] Re-Invoke Tier 3 Planner:** Invoke `/tier3-god-code-decomposition @[backend_v2/services/auth.py]` to generate detailed execution protocols for Phase 3 and Phase 4 based on updated codebase state.

### Phase 3: Organization Service Extraction (Lazy Placeholder)
- [ ] **[NOK] Execution:** `@[docs/epic/tasks_auth/phase3_organization_service_extraction.md]`
  - [ ] Extract `OrganizationService` [NEW] to `@[backend_v2/services/auth/organization_service.py]` [NEW]
  - [ ] Delegate organization methods from `AuthService` in `@[backend_v2/services/auth.py]`
  - [ ] Run quality gates: `uv run pytest backend_v2/tests/unit/test_auth.py --cov=backend_v2.services.auth`

### Phase 4: User Service and Facade Extraction (Lazy Placeholder)
- [ ] **[NOK] Execution:** `@[docs/epic/tasks_auth/phase4_user_service_and_facade_extraction.md]`
  - [ ] Extract `UserService` [NEW] to `@[backend_v2/services/auth/user_service.py]` [NEW]
  - [ ] Establish sovereign facade `AuthService` in `@[backend_v2/services/auth/__init__.py]` [NEW]
  - [ ] Retain temporary Strangler Fig proxy in `@[backend_v2/services/auth.py]`
  - [ ] Run quality gates: `uv run pytest backend_v2/tests/unit/test_auth.py --cov=backend_v2.services.auth`

### In-Flight Tier 2 Hardening (Before Consumer Migration)
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Verify 100% typing, linting, docstrings, and tests across newly extracted domain modules before migrating 1-hop consumers:
  - [x] [NEW] @[backend_v2/services/auth/constants.py]
  - [x] [NEW] @[backend_v2/services/auth/repositories.py]
  - [ ] [NEW] @[backend_v2/services/auth/token_service.py]
  - [ ] [NEW] @[backend_v2/services/auth/organization_service.py]
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
- Initialized Tier 3 God Code Decomposition planning for `@[backend_v2/services/auth.py]` (1234 lines).
- Executed AST boundary extraction discovering 30 symbol definitions.
- Baseline metrics: 30/30 unit tests passing, 93% line coverage.
- Created `symbol_migration_map.md` and detailed execution plans for Phase 1 and Phase 2.
- Implemented Phase 1: extracted `constants.py` and `repositories.py` (`OrganizationRepository`, `UserRepository`) into `backend_v2/services/auth/`.
- Rewired `backend_v2/services/auth.py` with explicit re-exports satisfying PEP 484 and MyPy Strict.
- Bound `__path__` in `auth.py` enabling Python package submodule resolution for `backend_v2.services.auth.*` during the Strangler Fig transitional phase.
- Implemented and validated all 13 test contracts TC-P1-01 through TC-P1-13 in `test_auth.py`.
- Passed 10-stage Universal Quality Gate: 0 lint errors, 0 type errors, 0 AST violations, 47/47 passing tests with 93% line coverage (100% coverage on `constants.py` and `repositories.py`).

## Learned
- During Strangler Fig decomposition where a file `auth.py` coexists with a new package directory `auth/`, Python rejects `from backend_v2.services.auth.constants import ...` unless `auth.py` declares `__path__ = [str(Path(__file__).parent / "auth")]` as a package search location.
- AST guardrail QGR028 enforces elimination of redundant `Model.model_validate()` calls when consuming repository returns, because `IIdentityRepository` already natively guarantees strongly typed domain models.
- All entity test identifiers must strictly conform to `OPAQUE_STRIPE_ID_REGEX` (`^([a-z]{2,5})_[a-zA-Z0-9]{8,}$`).

## Remaining
- Execute Phase 2: `/tier2-execute --full-auto docs/epic/tasks_auth/phase2_token_service_extraction.md docs/epic/auth_decomposition_tracker.md`

## Resume Command
```powershell
/tier2-execute --full-auto docs/epic/tasks_auth/phase2_token_service_extraction.md docs/epic/auth_decomposition_tracker.md
```
