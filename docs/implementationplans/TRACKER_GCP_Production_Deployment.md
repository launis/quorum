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

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md] @[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`
  - [x] Step 1: Phase 1 Cleanups — Production Settings, $PORT Contract, CORS Lockdown & Dynamic RFC 7807 Issuer URI
  - [x] Step 2: Typed HealthCheckResponseDTO & System Health Endpoint
  - [ ] Step 3: Cloud Run Worker Health Probe Responder, Non-Root Dockerfile & Docker Compose Hardening
  - [ ] Step 4: Global Quality Gate & Completion Verification
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md] @[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]" --gate backend --agent-cmd "agy --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`
  - [ ] @[backend_v2/settings.py]
  - [ ] @[backend_v2/models/dtos/system.py]
  - [ ] @[backend_v2/api/routers/system/health.py]
  - [ ] @[backend_v2/main.py]
  - [ ] @[backend_v2/run_worker.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]" --gate frontend --agent-cmd "agy --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

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
| **REQ-GCP-01** | Define `strip_trailing_slash` (`@[backend_v2/settings.py#L36-L47]`), add `app_version`, `port`, `worker_health_port`, `gcp_project_id`, `gcp_region`, `primary_domain` (`BeforeValidator(strip_trailing_slash)`), `jwt_issuer` (`BeforeValidator(strip_trailing_slash)`), and `jwt_audience` (`BeforeValidator(strip_trailing_slash)`), and normalize `frontend_app_base_url` (`BeforeValidator(strip_trailing_slash)`) on `Settings` in `@[backend_v2/settings.py#L53-L1335]`. | Step 1 | `[x]` |
| **REQ-GCP-02** | Consolidate default production `cors_origins` assignment (`[f"https://{self.primary_domain}", f"https://app.{self.primary_domain}", f"https://studio.{self.primary_domain}"]`, omitting `CORS_ORIGINS` from Cloud Run env vars) and unconditional per-origin HTTPS/wildcard/trailing-slash/non-empty validation inside `_enforce_environment_limits` (`@[backend_v2/settings.py#L1083-L1144]`). | Step 1 | `[x]` |
| **REQ-GCP-03** | Bind `version=get_settings().app_version` on `FastAPI`, pre-initialize and reset `app.state.arq_pool` and `app.state.pool_manager` in `lifespan` (`@[backend_v2/main.py#L182-L245]`), remove legacy `if not cors_origins: cors_origins = ["*"]` fallback, and replace hardcoded `"https://api.quorum.fi/errors/validation-failed"` in `validation_exception_handler` (`@[backend_v2/main.py#L386-L419]`) with dynamic `get_settings().jwt_issuer`. | Step 1 | `[x]` |
| **REQ-GCP-04** | Define immutable `HealthCheckResponseDTO(BaseResponseDTO)` in `@[backend_v2/models/dtos/system.py#L43-L52]` with `ConfigDict(frozen=True, strict=True, extra="forbid")`. | Step 2 | `[x]` |
| **REQ-GCP-05** | Expose `GET /api/v2/system/health` (`get_system_health(request: Request)`) in `@[backend_v2/api/routers/system/health.py#L25-L63]` with `response_model=HealthCheckResponseDTO`, $O(1)$ in-memory readiness evaluation (`"ok"` vs. `"degraded"`), `version=cfg.app_version`, and RFC 7807 Dual-Reporting. | Step 2 | `[x]` |
| **REQ-GCP-06** | Add single-loop `asyncio.start_server` health probe responder (`_handle_health_probe`) bound to `get_settings().worker_health_port` (`8081` locally, `$PORT` in Cloud Run) in `@[backend_v2/run_worker.py#L33-L67]`, configure non-root `quorum` (`UID 10001`) with `chown -R quorum:quorum /app/.venv` and direct `/app/.venv/bin/uvicorn` execution on `${PORT}` in `@[backend_v2/Dockerfile#L1-L36]`, and update `STORAGE_BACKEND=POSTGRES` and deduplicate `GOOGLE_APPLICATION_CREDENTIALS` in `@[docker-compose.yml#L1-L96]`. | Step 3 | `[ ]` |
| **REQ-GCP-07** | Pass the global 10-stage completion gate (`uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`) with >90% coverage and >=2 ISTQB negative tests per feature. | Step 4 | `[ ]` |

---

# Session Handover Context

## Achieved
- Consolidated the GCP production deployment specification into `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]` to align 100% with the 2026 All-in-PostgreSQL 19 Sovereign Zero-ORM Architecture (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`), B2B SaaS IAM (`@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`), and `qrum.ai` domain origin security.
- Executed Tier 8 Feature Audits on Container & Cloud Run runtime risks, Configuration & Validation edge cases (`settings.py` & `main.py` CORS validator consolidation, `https://` origin enforcement, wildcard/trailing-slash/empty-list rejection, and `BeforeValidator(strip_trailing_slash)` normalization on `jwt_issuer`/`jwt_audience`), and Health Check SSOT & Readiness (`Settings.app_version` and $O(1)$ in-memory `request.app.state` readiness evaluation for `"ok"` vs. `"degraded"`), and incorporated all hardened blueprints into `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`.
- Executed `/tier0-research-plan` Red-Team & System 2 Five-Axis verification on `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]` and `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`, confirming `CONVERGENCE ACHIEVED: 0 architectural defects found` across `audit_markdown_boundaries.py`, `audit_technical_debt.py`, `audit_plan_tracker_parity.py`, and `audit_tracker_output.py`.
- Synchronized `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]` with 1:1 step parity, file-level backend hardening checklists (including `@[backend_v2/run_worker.py]`), and the updated Requirements Traceability Matrix.

## Learned
- Consolidating production `cors_origins` default assignment and validation inside `_enforce_environment_limits` (`@[backend_v2/settings.py#L1083-L1144]`) eliminates declaration-order coupling between multiple `@model_validator(mode="after")` methods, while requiring `origin.startswith("https://")`, `"*" not in origin`, `not origin.endswith("/")`, `len(origin) > len("https://")`, and `min_length=1` (plus removing `if not cors_origins: cors_origins = ["*"]` in `@[backend_v2/main.py#L386-L419]`) prevents partial wildcards, cleartext HTTP origins, trailing-slash RFC 6454 mismatches, and empty-list wildcard fallbacks in production.
- Normalizing `jwt_issuer` and `jwt_audience` at the `Settings` ingress boundary via `BeforeValidator(strip_trailing_slash)` (`@[backend_v2/settings.py#L36-L47]`) prevents double-slash (`//`) URIs in `validation_exception_handler` (`@[backend_v2/main.py#L386-L419]`) and ensures slash-only strings (`"///"`) collapse to `""` and fail fast on `Field(min_length=1)`.
- `@[backend_v2/run_worker.py#L33-L67]` requires a lightweight stdlib `asyncio.start_server` health probe responder bound to `get_settings().worker_health_port` (`default=8081` locally so `run_local.bat` never collides with `uvicorn` on port `8000`, and `AliasChoices("worker_health_port", "WORKER_HEALTH_PORT", "PORT")` in Cloud Run) inside `async with health_server:` around `await worker.async_run()` so Cloud Run Service startup probes succeed without spawning OS threads or secondary web frameworks.
- `@[backend_v2/Dockerfile#L1-L36]` must assign `chown -R quorum:quorum /app/.venv`, set `VIRTUAL_ENV=/app/.venv`, `PATH="/app/.venv/bin:$PATH"`, `UV_NO_SYNC=1`, `UV_OFFLINE=1`, and `UV_CACHE_DIR=/tmp/uv-cache`, and invoke `/app/.venv/bin/uvicorn` directly via `exec` on `${PORT}` to prevent `PermissionError` and cold-start overhead under `USER quorum` (`UID 10001`).

## Remaining
- Execute Steps 1–4 of `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`.
- Complete Post-Implementation Backend Hardening and Final Plan Audit.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md] @[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]
```
