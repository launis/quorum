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
  - [ ] Step 1: Phase 1 Cleanups — Production Settings, CORS Lockdown & Dynamic RFC 7807 Issuer URI
  - [ ] Step 2: Typed HealthCheckResponseDTO & System Health Endpoint
  - [ ] Step 3: Stateless Cloud Run Dockerfile & Docker Compose Hardening
  - [ ] Step 4: Global Quality Gate & Completion Verification
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md] @[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]" --gate backend --agent-cmd "agy --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`
  - [ ] @[backend_v2/settings.py]
  - [ ] @[backend_v2/models/dtos/system.py]
  - [ ] @[backend_v2/api/routers/system/health.py]
  - [ ] @[backend_v2/main.py]
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
     - `@[ki_global_config_sovereignty.md]`: Document the canonical GCP production settings (`gcp_project_id`, `gcp_region`, `primary_domain`, `jwt_issuer`, `jwt_audience`) and the Fail-Fast `validate_production_cors_origins` validator banning wildcard `["*"]` CORS in `production` mode.
     - `@[ki_api_router_ssot_governance.md]`: Document the canonical `GET /api/v2/system/health` Cloud Run and Load Balancer health probe endpoint in `@[backend_v2/api/routers/system/health.py]` returning `HealthCheckResponseDTO`.
     - `@[ki_zero_permissive_typing.md]`: Document `HealthCheckResponseDTO(BaseResponseDTO)` in `@[backend_v2/models/dtos/system.py]` with `ConfigDict(frozen=True, strict=True, extra="forbid")`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` if any new system router endpoints or DTO exports require indexing.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `@[docs/architecture/01_system_context_and_invariants.md]` and `@[docs/architecture/05_resilience_and_observability.md]` describing the GCP Cloud Run stateless deployment invariants, `qrum.ai` domain origin security, and `/api/v2/system/health` probe in present tense without historical language or plan IDs.

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
| **REQ-GCP-01** | Add `gcp_project_id`, `gcp_region`, `primary_domain`, `jwt_issuer`, and `jwt_audience` to `Settings` in `@[backend_v2/settings.py#L54-L1053]`. | Step 1 | `[ ]` |
| **REQ-GCP-02** | Lock default production `cors_origins` to `qrum.ai` origins in `_enforce_environment_limits` (`@[backend_v2/settings.py#L847-L908]`) and reject explicit wildcard `["*"]` in production via `validate_production_cors_origins`. | Step 1 | `[ ]` |
| **REQ-GCP-03** | Replace hardcoded `"https://api.quorum.fi/errors/validation-failed"` in `validation_exception_handler` (`@[backend_v2/main.py#L347-L380]`) with dynamic `get_settings().jwt_issuer`. | Step 1 | `[ ]` |
| **REQ-GCP-04** | Define immutable `HealthCheckResponseDTO(BaseResponseDTO)` in `@[backend_v2/models/dtos/system.py#L43-L52]` with `ConfigDict(frozen=True, strict=True, extra="forbid")`. | Step 2 | `[ ]` |
| **REQ-GCP-05** | Expose `GET /api/v2/system/health` (`get_system_health`) in `@[backend_v2/api/routers/system/health.py#L20-L52]` with `response_model=HealthCheckResponseDTO` and RFC 7807 Dual-Reporting. | Step 2 | `[ ]` |
| **REQ-GCP-06** | Remove `--reload` from `@[backend_v2/Dockerfile]`, configure non-root `quorum` user, and deduplicate `GOOGLE_APPLICATION_CREDENTIALS` in `@[docker-compose.yml]`. | Step 3 | `[ ]` |
| **REQ-GCP-07** | Pass the global 10-stage completion gate (`uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`) with >90% coverage and >=2 ISTQB negative tests per feature. | Step 4 | `[ ]` |

---

# Session Handover Context

## Achieved
- Modernized `@[docs/epic/EPIC_74_Production_Deployment_GCP.md]` to align 100% with the 2026 All-in-PostgreSQL 19 Sovereign Zero-ORM Architecture (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`), B2B SaaS IAM (`@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`), and `qrum.ai` domain origin security.
- Authored and hardened `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]` via Tier 0 Five-Axis System 2 Deconstruction, injecting AST-exact `#Lnn-mm` symbol boundaries, `Phase 1: Pre-Implementation Cleanups`, the 5-Column Architectural Directives Table, and the `<execution_protocol>` XML steps.
- Initialized `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]` with 1:1 step parity, file-level backend hardening checklists, and the Requirements Traceability Matrix.

## Learned
- `validation_exception_handler` in `@[backend_v2/main.py#L347-L380]` previously hardcoded `"https://api.quorum.fi/errors/validation-failed"`; resolving this dynamically from `Settings.jwt_issuer` (`"https://api.qrum.ai"`) eliminates cross-domain drift.
- `Settings` in `@[backend_v2/settings.py#L54-L1053]` defaulted `cors_origins` to `["*"]` in all environments; locking production defaults to the closed `qrum.ai` origin set in `_enforce_environment_limits` (`@[backend_v2/settings.py#L847-L908]`) and rejecting explicit `"*"` in production via `validate_production_cors_origins` prevents wildcard CORS exposure when `allow_credentials=True`.
- `@[backend_v2/api/routers/system/health.py#L20-L52]` previously exposed only `/api/v2/system/hooks`; adding `GET /api/v2/system/health` with `HealthCheckResponseDTO` provides a zero-dict, O(1) health probe for Cloud Run and Cloud Load Balancer without violating `single_router_ssot_mandate`.

## Remaining
- Execute Steps 1–4 of `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`.
- Complete Post-Implementation Backend Hardening and Final Plan Audit.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md] @[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]
```
