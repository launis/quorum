# Tracker: GCP Production Deployment, Cloud Run & `qrum.ai` Domain Sovereignty

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_api_router_ssot_governance.md]</knowledge_item>
  <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
  <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
</required_context_rules>

---

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md] @[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`
  - [x] Step 1: Phase 1 Cleanups — Production Settings, $PORT Contract, CORS Lockdown & Dynamic RFC 7807 Issuer URI
  - [x] Step 2: Typed HealthCheckResponseDTO & System Health Endpoint
  - [x] Step 3: Cloud Run Worker Health Probe Responder, Non-Root Dockerfile & Docker Compose Hardening
  - [x] Step 4: Global Quality Gate & Completion Verification
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md] @[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]" --gate backend --agent-cmd "agy --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`
  - [x] @[backend_v2/settings.py]
  - [ ] @[backend_v2/models/dtos/system.py]
  - [ ] @[backend_v2/api/routers/system/health.py]
  - [ ] @[backend_v2/main.py]
  - [ ] @[backend_v2/run_worker.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]" --gate frontend --agent-cmd "agy --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_GCP_Production_Deployment.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md] @[ki_global_config_sovereignty.md] @[ki_api_router_ssot_governance.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_global_config_sovereignty.md]`: Document the canonical GCP production settings (`strip_trailing_slash`, `port`, `worker_health_port`, `gcp_project_id`, `gcp_region`, `primary_domain`, `jwt_issuer`, `jwt_audience`) and the consolidated production CORS origin enforcement inside `_enforce_environment_limits` (`https://` scheme required, wildcards and trailing slashes banned).
     - `@[ki_api_router_ssot_governance.md]`: Document the canonical `GET /api/v2/system/health` Cloud Run and Load Balancer health probe endpoint in `@[backend_v2/api/routers/system/health.py]` returning `HealthCheckResponseDTO`.
     - `@[ki_zero_permissive_typing.md]`: Document `HealthCheckResponseDTO(BaseResponseDTO)` in `@[backend_v2/models/dtos/system.py]` with `ConfigDict(frozen=True, strict=True, extra="forbid")`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` if any new system router endpoints or DTO exports require indexing.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `@[docs/architecture/01_system_context_and_invariants.md]` and `@[docs/architecture/05_resilience_and_observability.md]` describing the GCP Cloud Run stateless deployment invariants, `qrum.ai` domain origin security, `/api/v2/system/health` probe, `quorum-worker` single-loop `asyncio.start_server` health probe responder on `Settings.worker_health_port`, and non-root `UID 10001` `.venv` container execution in present tense without historical language or plan IDs.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md] @[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

---

## Instructions for the Execution Agent

1. **Stateless Context Reset**: At the start of execution, physically load `@[.agents/rules/00-antigravity-core.md]`, `@[.agents/rules/01-python-backend.md]`, `@[.agents/rules/04_directory_reference.md]`, `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`, and `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`.
2. **Quality Gate Enforcement**: After completing each Python code step, execute `uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict` before checking off the step in `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`.
3. **Atomic Checkpoint Commits**: After each verified logical step passes the quality gate, stage the modified files explicitly and perform an atomic commit using Conventional Commits syntax (`feat(gcp): ...` or `refactor(settings): ...`).
4. **Execution Modes**:
   - **Continuous Full-Auto Mode (`--full-auto`)**: Proceed autonomously across Steps 1–4 as long as all quality gates pass 100%.
   - **Post-Implementation Hardening**: Execute via `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]" --gate backend --agent-cmd "agy --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.

---

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-GCP-01** | Define `strip_trailing_slash` (`@[backend_v2/settings.py#L51-L62]`), add `app_version`, `port`, `worker_health_port`, `gcp_project_id`, `gcp_region`, `primary_domain` (`BeforeValidator(strip_trailing_slash)`), `jwt_issuer` (`BeforeValidator(strip_trailing_slash)`), and `jwt_audience` (`BeforeValidator(strip_trailing_slash)`), and normalize `frontend_app_base_url` (`BeforeValidator(strip_trailing_slash)`) on `Settings` in `@[backend_v2/settings.py#L51-L62]`. | Step 1 | `[x]` |
| **REQ-GCP-02** | Consolidate default production `cors_origins` assignment (`[f"https://{self.primary_domain}", f"https://app.{self.primary_domain}", f"https://studio.{self.primary_domain}"]`, omitting `CORS_ORIGINS` from Cloud Run env vars) and unconditional per-origin HTTPS/wildcard/trailing-slash/non-empty validation inside `_enforce_environment_limits` (`@[backend_v2/settings.py#L1214-L1302]`). | Step 1 | `[x]` |
| **REQ-GCP-03** | Bind `version=get_settings().app_version` on `FastAPI`, pre-initialize and reset `app.state.arq_pool` and `app.state.pool_manager` in `lifespan` (`@[backend_v2/main.py#L182-L249]`), remove legacy `if not cors_origins: cors_origins = ["*"]` fallback, and replace hardcoded `"https://api.quorum.fi/errors/validation-failed"` in `validation_exception_handler` (`@[backend_v2/main.py#L182-L249]`) with dynamic `get_settings().jwt_issuer`. | Step 1 | `[x]` |
| **REQ-GCP-04** | Define immutable `HealthCheckResponseDTO(BaseResponseDTO)` in `@[backend_v2/models/dtos/system.py#L57-L76]` with `ConfigDict(frozen=True, strict=True, extra="forbid")`. | Step 2 | `[x]` |
| **REQ-GCP-05** | Expose `GET /api/v2/system/health` (`get_system_health(request: Request)`) in `@[backend_v2/api/routers/system/health.py#L29-L79]` with `response_model=HealthCheckResponseDTO`, $O(1)$ in-memory readiness evaluation (`"ok"` vs. `"degraded"`), `version=cfg.app_version`, and RFC 7807 Dual-Reporting. | Step 2 | `[x]` |
| **REQ-GCP-06** | Add single-loop `asyncio.start_server` health probe responder (`_handle_health_probe`) bound to `get_settings().worker_health_port` (`8081` locally, `$PORT` in Cloud Run) in `@[backend_v2/run_worker.py#L46-L66]`, configure non-root `quorum` (`UID 10001`) with `chown -R quorum:quorum /app/.venv` and direct `/app/.venv/bin/uvicorn` execution on `${PORT}` in `@[backend_v2/Dockerfile#L1-L36]`, and update `STORAGE_BACKEND=POSTGRES` and deduplicate `GOOGLE_APPLICATION_CREDENTIALS` in `@[docker-compose.yml#L1-L96]`. | Step 3 | `[x]` |
| **REQ-GCP-07** | Pass the global 10-stage completion gate (`uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`) with >90% coverage and >=2 ISTQB negative tests per feature. | Step 4 | `[x]` |

---

# Session Handover Context

## Achieved
- Completed **Step 1 (`[x]`, Commit `15784637f`)**: Added `strip_trailing_slash`, `app_version`, `port`, `worker_health_port`, `http_client_timeout_seconds`, `gcp_project_id`, `gcp_region`, `primary_domain`, `jwt_issuer`, `jwt_audience`, `frontend_app_base_url` trailing-slash normalization, `postgres_dsn` `DATABASE_URL` alias, `GCP_PROJECT` Vertex ADC detection, and consolidated production `cors_origins` lockdown in `_enforce_environment_limits` in `@[backend_v2/settings.py]`. Bound `version=get_settings().app_version`, module-scope & `lifespan` `finally:` resets of `app.state.arq_pool` and `app.state.pool_manager`, direct `allow_origins=get_settings().cors_origins`, and dynamic `f"{get_settings().jwt_issuer}/errors/validation-failed"` in `@[backend_v2/main.py]`, with unit and ISTQB negative boundary tests in `@[backend_v2/tests/unit/test_settings.py]` and `@[backend_v2/tests/unit/test_main.py]`.
- Completed **Step 2 (`[x]`, Commit `64b1962e0`)**: Added `HealthCheckResponseDTO(BaseResponseDTO)` in `@[backend_v2/models/dtos/system.py]` and `GET /api/v2/system/health` (`get_system_health(request: Request) -> HealthCheckResponseDTO`) in `@[backend_v2/api/routers/system/health.py]` with $O(1)$ in-memory readiness evaluation (`"ok"` vs. `"degraded"`), `version=cfg.app_version`, RFC 7807 Dual-Reporting, and unit/ISTQB negative tests in `@[backend_v2/tests/unit/models/dtos/test_system.py]` and `@[backend_v2/tests/unit/test_health.py]`.
- Completed **Step 3 (`[x]`, Commit `d0bb7722a`)**: Added `_HEALTH_RESPONSE_BYTES`, `_handle_health_probe` (using `contextlib.suppress(TimeoutError, OSError)` and `timeout=get_settings().http_client_timeout_seconds` with deterministic `writer.close()` in `finally:`), and `asyncio.start_server` on `settings.worker_health_port` in `@[backend_v2/run_worker.py]`; hardened `@[backend_v2/Dockerfile]` (`UID 10001` non-root `quorum` user, `chown -R quorum:quorum /app/.venv`, direct `/app/.venv/bin/uvicorn` execution on `${PORT}`); updated `@[docker-compose.yml]` (`STORAGE_BACKEND=POSTGRES`, `USE_MOCK_DB=false`, deduplicated `GOOGLE_APPLICATION_CREDENTIALS`); and added positive and ISTQB negative tests in `@[backend_v2/tests/unit/test_run_worker.py]`.
- Completed **Step 4 (`[x]`)**: Passed the global 10-stage completion gate (`uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`) with `6895 passed, 0 failed`, `97.45%` total line coverage, and `0` AST guardrail violations.

## Learned
- Using `contextlib.suppress(TimeoutError, OSError)` inside `try ... finally: writer.close()` in `_handle_health_probe` (`@[backend_v2/run_worker.py]`) cleanly satisfies `QGR003` (which bans non-raising `try...except` blocks in domain modules) while still bounding socket read timeouts via `get_settings().http_client_timeout_seconds` and closing the probe socket deterministically.
- In `Settings.enabled_providers` (`@[backend_v2/settings.py]`), checking `os.getenv("VERTEX_PROJECT_ID") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GCP_PROJECT") or Path("service-account.json").exists()` enables Cloud Run ADC activation via `GCP_PROJECT` / `VERTEX_PROJECT_ID` without leaking local `.env` `GOOGLE_CLOUD_PROJECT` or `USE_VERTEX_LLM` flags into isolated AI Studio unit tests (`test_istqb_equivalence_enabled_providers_independence`).

## Remaining
- Execute Post-Implementation Backend Hardening (`auto_hardening_runner.py` on `@[backend_v2/settings.py]`, `@[backend_v2/models/dtos/system.py]`, `@[backend_v2/api/routers/system/health.py]`, `@[backend_v2/main.py]`, and `@[backend_v2/run_worker.py]`).
- Execute `/tier7-describe-architecture` and `/tier8-audit-plan`.

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md] @[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]
```
