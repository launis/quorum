# Tracker: SlowAPI Dependency Removal (TenantRateLimitService Cutover) and Hermetic google.genai Module Restoration

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_SlowAPI_Removal_and_GenAI_Mock_Restoration.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_SlowAPI_Removal_and_GenAI_Mock_Restoration.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_SlowAPI_Removal_and_GenAI_Mock_Restoration.md] @[docs/implementationplans/TRACKER_SlowAPI_Removal_and_GenAI_Mock_Restoration.md]`
  - [x] Step 1: Phase 1: Eradicate slowapi Dependency, Legacy Rate Limit Module, Exception Handler, and Touched-Scope Tech Debt
  - [x] Step 2: Phase 2: Cut Over POST /api/v2/iam/auth/exchange to TenantRateLimitServiceDep
  - [x] Step 3: Phase 3: Refactor cleanup_genai_mock in test_ai_studio_adapter.py for Hermetic sys.modules Restoration and MyPy Strictness
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_SlowAPI_Removal_and_GenAI_Mock_Restoration.md] @[docs/implementationplans/TRACKER_SlowAPI_Removal_and_GenAI_Mock_Restoration.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_SlowAPI_Removal_and_GenAI_Mock_Restoration.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[backend_v2/api/routers/iam/auth.py]
  - [x] @[backend_v2/main.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_SlowAPI_Removal_and_GenAI_Mock_Restoration.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain (`slowapi`, `rate_limit.py`, `rate_limit_exception_handler`, `_resolve_exchange_rate_limit`).
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic (`@[backend_v2/api/routers/iam/auth.py]` and `@[backend_v2/main.py]`).

### Documentation & Knowledge Item Update

- [x] **[OK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_SlowAPI_Removal_and_GenAI_Mock_Restoration.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_SlowAPI_Removal_and_GenAI_Mock_Restoration.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the single-pipeline `TenantRateLimitService` authentication edge rate-limiting architecture (`TenantRateLimitServiceDep` on `POST /api/v2/iam/auth/exchange` after `slowapi` removal) and hermetic `sys.modules` reference snapshotting/restoration in `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]`.
  2. **Directory Reference Sync:**
     - Verify `@[.agents/rules/04_directory_reference.md]` reflects `redis_security.py` (`TenantRateLimitService`) as the sole rate-limiting SSOT under `backend_v2/core/` with zero references to `rate_limit.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/01_system_context_and_invariants.md` and `docs/architecture/05_resilience_and_observability.md` describing the single-pipeline Redis sliding-window rate-limiting architecture in present tense without historical language or plan IDs.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_SlowAPI_Removal_and_GenAI_Mock_Restoration.md] @[docs/implementationplans/TRACKER_SlowAPI_Removal_and_GenAI_Mock_Restoration.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[backend_v2/api/routers/iam/auth.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | `[DELETE]` legacy `@[backend_v2/core/rate_limit.py#L25-L78]` and `[DELETE]` `@[backend_v2/tests/unit/core/test_rate_limit.py#L13-L31]`, and remove `"slowapi>=0.1.9",` from `@[pyproject.toml#L38-L38]` and `@[uv.lock]`. | Step 1 | [x] Completed |
| REQ-002 | Remove `RateLimitExceeded` and `rate_limit_exceeded_handler` imports, remove `"rate_limit_exception_handler"` from `__all__`, and delete `rate_limit_exception_handler` in `@[backend_v2/main.py#L355-L383]`, routing HTTP 429 `TokenLimitExceededError` exclusively through `app_exception_handler` (`@[backend_v2/main.py#L355-L383]`). | Step 1 | [x] Completed |
| REQ-003 | Replace the manual `try...except ValidationError:` block in `@[backend_v2/tests/unit/test_main.py#L182-L202]` with `with pytest.raises(ValidationError) as exc_info:` to eliminate the `TD_MODEL_FACTORY` warning, and replace `test_rate_limit_exception_handler_delegation` in `@[backend_v2/tests/unit/test_main.py#L248-L281]` with `test_app_exception_handler_429_rate_limit_exceeded`. | Step 1 | [x] Completed |
| REQ-004 | Remove `limiter` and `_resolve_exchange_rate_limit` (`@[backend_v2/api/routers/iam/auth.py#L50-L84]`), inject `rate_limit_service: TenantRateLimitServiceDep` into `exchange_firebase_token` (`@[backend_v2/api/routers/iam/auth.py#L50-L84]`), extract `client_ip` via `QGR016`-compliant `if request.client is not None: client_ip = request.client.host`, and invoke `await rate_limit_service.enforce_auth_edge_rate_limit(client_ip=client_ip, endpoint_scope="POST /api/v2/iam/auth/exchange")`. | Step 2 | [x] Completed |
| REQ-005 | Update `@[backend_v2/tests/unit/test_auth.py#L200-L288]` and `@[backend_v2/tests/unit/test_auth.py#L633-L767]` to remove `_resolve_exchange_rate_limit` and verify positive token exchange within `auth_edge_rpm_limit` plus 3 negative ISTQB BVA boundaries (HTTP 429 `TokenLimitExceededError` at `auth_edge_rpm_limit + 1`, HTTP 400 `ErrorCodes.VALIDATION_FAILED` when `request.client` is `None`, and HTTP 503 `ServiceUnavailableError` when Redis is `None`). | Step 2 | [x] Completed |
| REQ-006 | Refactor `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L71-L89]` and `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L99-L130]` (`cleanup_genai_mock`) to pre-import and snapshot original `google`, `google.genai`, `google.genai.types`, and `google.genai.errors` module references via `importlib.import_module` inside a scoped `warnings.catch_warnings()` block, install `mod_genai` and `mod_genai_types` inside `cleanup_genai_mock` before `yield`, and restore exact original module references in `finally:` without `del` or teardown `importlib.import_module`. | Step 3 | [x] Completed |
| REQ-007 | Replace `sys._mock_genai_client` with a typed module-level `_mock_genai_client: MagicMock` variable, declare `errors: ModuleType` on `MockGenAIModule` (`@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L71-L89]`), update test fixtures in `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]` to pass `mypy --strict` and `QGR020`, and add `test_cleanup_genai_mock_preserves_and_restores_real_module_references` (`@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L590-L599]`) verifying `sys.modules["google.genai"]` and `sys.modules["google.genai.types"]` restoration. | Step 3 | [x] Completed |

# Session Handover Context

## Achieved
- Executed all 3 steps of `@[docs/implementationplans/IMPLEMENTATION_PLAN_SlowAPI_Removal_and_GenAI_Mock_Restoration.md]`:
  - **Step 1 (`cb9b31531`):** Deleted legacy `backend_v2/core/rate_limit.py` and `backend_v2/tests/unit/core/test_rate_limit.py`, removed `slowapi>=0.1.9` from `@[pyproject.toml#L38-L38]` and `@[uv.lock]`, deleted `rate_limit_exception_handler` from `@[backend_v2/main.py#L355-L383]`, fixed `TD_MODEL_FACTORY` in `@[backend_v2/tests/unit/test_main.py#L182-L202]`, and verified RFC 7807 HTTP 429 `TokenLimitExceededError` handling in `@[backend_v2/tests/unit/test_main.py#L248-L281]`.
  - **Step 2 (`7e8cbe888`):** Cut over `POST /api/v2/iam/auth/exchange` (`exchange_firebase_token` in `@[backend_v2/api/routers/iam/auth.py#L50-L84]`) to `rate_limit_service: TenantRateLimitServiceDep` with `QGR016`-compliant `client_ip` extraction and 4 ISTQB BVA test cases in `@[backend_v2/tests/unit/test_auth.py#L200-L288]` and `@[backend_v2/tests/unit/test_auth.py#L633-L767]`.
  - **Step 3 (`f3ed4506b`):** Refactored `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L71-L89]` and `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L99-L130]` (`cleanup_genai_mock`) to snapshot canonical `google.genai` modules once via `importlib.import_module` inside a scoped `warnings.catch_warnings()` block, restore exact original module references in `finally:`, and pass `mypy --strict` and `-W error::DeprecationWarning` with 0 warnings.
  - **Tier 2 Hardening, Tier 8 Audit & Tier 7 Architectural Sync:** Completed backend hardening on `@[backend_v2/api/routers/iam/auth.py]` and `@[backend_v2/main.py]`, resolved `StarletteDeprecationWarning` by adding `httpx2>=2.16.0` to dev dependencies (`714b32574`), passed `/tier8-audit-plan` (`58b15b1ea`), and synchronized `@[ki_god_code_prevention.md]`, `@[docs/architecture/01_system_context_and_invariants.md]`, and `@[docs/architecture/05_resilience_and_observability.md]` via `/tier7-describe-architecture`.

## Learned
- Importing `from types import ModuleType` at module top level in `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L71-L89]` avoids class-body shadowing of `types` on `MockGenAIModule`, while typing `_real_google_pkg: Any = None` satisfies `ruff` (`B010`), `mypy --strict`, and `QGR001` (`Banned dynamic .__dict__ access`) simultaneously.
- Narrowing `prepare_structured_output` return type via `assert not isinstance(result, type)` in `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L526-L541]` satisfies both `mypy --strict` and `QGR001` (`isinstance(..., dict)` ban).

## Remaining
- None. Plan implementation, hardening, Red-Team audit, and As-Built architectural documentation sync are 100% complete.

## Resume Command
```powershell
# Completed
```
