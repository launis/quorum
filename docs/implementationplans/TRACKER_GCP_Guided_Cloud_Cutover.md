# Tracker: Guided GCP Live Cloud Cutover, `qrum.ai` Domain Reservation & Provisioning Orchestrator

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_frontend_iam_role_segregation.md]</knowledge_item>
</required_context_rules>

---

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]`
  - [ ] Step 1: Phase 1: Clean Docker Compose Runtime SSOT & Implement Typed 6-Stage GCP Provisioning CLI (docker-compose.yml & scripts/provision_gcp_cloud.py)
  - [ ] Step 2: Phase 2: Unit & ISTQB Boundary Test Suite & Directory Reference Registration (test_provision_gcp_cloud.py & 04_directory_reference.md)
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend {target}'"`.
  - [ ] [NEW] @[scripts/provision_gcp_cloud.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend {target}'"`.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[ki_god_code_prevention.md] @[ki_global_config_sovereignty.md] @[ki_zero_permissive_typing.md] @[ki_frontend_iam_role_segregation.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_global_config_sovereignty.md]`: Document the 6-stage GCP cloud provisioning and client environment cutover orchestrator (`[NEW] @[scripts/provision_gcp_cloud.py]`), `@[docker-compose.yml#L1-L57]` cleanup, shared `JWT_SECRET_KEY` + `SECRET_VERTEX_AI_SA_JSON` bootstrap on the `quorum-seed` Cloud Run Job for first-boot `initialize_firebase_admin_from_secrets` and HKDF-SHA256 KEK parity, `SERVICE_AUTH_SECRET` (`quorum-service-auth-secret`) binding, Resend EU (`HTTP_API`) + SPF/MX/DMARC/DKIM DNS provisioning, `.ai` registrar NS delegation verification, and `client_app_v2/.env` switching.
     - `@[ki_frontend_iam_role_segregation.md]`: Verify cloud cutover alignment for Firebase Authentication TOTP 2FA, Email Enumeration Protection compatibility, `roles/firebaseauth.admin` on the `ROOT_SYSTEM` `vertex_ai` service account, and `app.qrum.ai` SPA rewrites (`/task/**` and `/invite/**`).
     - `@[ki_god_code_prevention.md]` & `@[ki_zero_permissive_typing.md]`: Verify `[NEW] @[scripts/provision_gcp_cloud.py]` enforces 100% frozen Pydantic V2 DTOs (`QGR020` Check 20B/20C compliant) with zero naked dicts or untyped subprocess boundaries.
  2. **Directory Reference Sync:**
     - Verify `@[.agents/rules/04_directory_reference.md]` indexes `provision_gcp_cloud.py` and `scripts/test_provision_gcp_cloud.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/01_system_context_and_invariants.md` describing the GCP Cloud Run provisioning, 3-tier secret bootstrap, and domain cutover architecture in present tense.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

---

## Instructions for the Execution Agent

- **Stateless Context Reset**: At the start of execution, physically load `@[.agents/rules/00-antigravity-core.md]`, `@[.agents/rules/01-python-backend.md]`, `@[.agents/rules/04_directory_reference.md]`, `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]`, and `@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]`.
- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/provision_gcp_cloud.py backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py --test --ast-strict`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[backend_v2/settings.py]`).
- **Interactive Live Cutover Execution**: Once Steps 1–2 are committed and verified by unit tests, run `uv run python scripts/provision_gcp_cloud.py --stage all --check` to inspect interactive human checkpoints and `uv run python scripts/provision_gcp_cloud.py --stage <stage> --apply` to provision each cloud stage step-by-step.

---

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-CUTOVER-01** | Clean `[MODIFY] @[docker-compose.yml#L1-L57]` to remove legacy `USE_VERTEX_LLM`, `VERTEX_LOCATION`, `GOOGLE_APPLICATION_CREDENTIALS`, and `service-account.json` volume mounts and unify `STORAGE_BUCKET_NAME=cognitive-quorum.firebasestorage.app`, and implement `[NEW] @[scripts/provision_gcp_cloud.py]` with `QGR020`-compliant frozen Pydantic V2 DTOs (`GCPProvisionConfigDTO`, `CommandSpecDTO`, `CommandExecutionResultDTO`, `DNSVerificationResultDTO`, `StageExecutionReportDTO`), `ProvisionStage`, `DeploymentTier` (`pilot` vs. `ha`), `ClientEnvMode` (`local` vs. `cloud`), `SecretStr` stdin secret injection (`quorum-jwt-secret`, `quorum-service-auth-secret`, `quorum-db-url`, `quorum-vertex-sa-json`, `quorum-email-api-key`), `quorum-seed` shared `JWT_SECRET_KEY` + `SECRET_VERTEX_AI_SA_JSON` bootstrap, pure Tier 1 Cloud Run deployment flags (omitting `CORS_ORIGINS`, `LOGFIRE_TOKEN`, `SECRET_*`, and legacy Vertex flags), Resend EU DNS records, DNS NS verification, `HealthCheckResponseDTO` verification, and `client_app_v2/.env` switching. | Step 1 | [ ] Pending |
| **REQ-CUTOVER-02** | Implement `[NEW] @[backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py]` with >90% line coverage and >=2 ISTQB negative boundary tests per feature (verifying `quorum-seed` secret bindings, absence of legacy/Tier-2 env vars on `quorum-api`, `quorum-worker`, and `docker-compose.yml`, `SecretStr` redaction, DNS/health validation, and `client_app_v2/.env` roundtrips), and register `provision_gcp_cloud.py` and `scripts/test_provision_gcp_cloud.py` in `@[.agents/rules/04_directory_reference.md#L25-L121]`. | Step 2 | [ ] Pending |

---

# Session Handover Context

## Achieved
- Synchronized `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]` and `@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]` with `@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md]`, `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]` (`Askel 4.5`), and `@[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]` (`Askel 4.6`, Findings A–E).
- Removed already-completed and Tier 8 audited `EmailService` modifications (`f50520284`–`08385c09b`) from Target Files, locking `@[backend_v2/services/auth/email_service.py#L68-L378]` as a Read-Only Context File with its canonical 5-key Resend EU REST contract (`from`, `to`, `subject`, `html`, `tags`, HTML-escaped `"Open Quorum Portal"` CTA, and `QGR033` `_redact_action_url` + `mask_email_address` console PII redaction).
- Resolved the `EPIC 164` Cloud Run first-boot dependency by binding `JWT_SECRET_KEY=quorum-jwt-secret:latest` and `SECRET_VERTEX_AI_SA_JSON=quorum-vertex-sa-json:latest` to the one-shot `quorum-seed` Cloud Run Job (`LocalSeedSecretsSettings`), ensuring `ROOT_SYSTEM` `vertex_ai` is encrypted into PostgreSQL 19 `tenant_secrets` with identical HKDF-SHA256 KEK parity before `quorum-api` starts and runs `initialize_firebase_admin_from_secrets`.
- Documented Human Checkpoint F covering Firebase Authentication Email/Password + TOTP 2FA enablement, `roles/firebaseauth.admin` on the `vertex_ai` service account (required for `fb_auth.update_user(..., email_verified=True)` after `IDENTITY_MISMATCH` during `/task/:token` JIT onboarding), Firebase Email Enumeration Protection compatibility (`'invalid-credential'`), `app.qrum.ai` SPA deep-link rewrites (`/task/**`, `/invite/**`), normalized `execution_assignments.task_brief_id` FK seeding, and stateless eager `Base64Attachment` portal file extraction.

## Learned
- `EmailService._compose_transactional_html` and `_send_single_http_item` are already 100% implemented and audited (`f50520284`–`a6bd5a7b5`); keeping an outdated duplicate `[MODIFY]` target in `IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md` would reintroduce non-Resend root JSON keys rejected by Resend's strict Zod schema and violate `english_language_mandate`.
- Under `EPIC 164` and `EPIC 163`, `quorum-api` initializes Firebase Admin SDK in memory from `ROOT_SYSTEM` `vertex_ai` in `tenant_secrets` at startup (`initialize_firebase_admin_from_secrets`), `LOGFIRE_TOKEN` lives in `SecretScope.TELEMETRY` (`resolve_startup_logfire_token`), `MOCK_*_USER_ID` variables are eradicated from `env.dart`, `CORS_ORIGINS` is derived automatically in `Settings._enforce_environment_limits`, and `QGR020` Check 20C forbids non-`None` scalar defaults on `BaseModel` fields outside `Settings` (so CLI defaults belong in `argparse` `main()`).

## Remaining
- Execute Steps 1–2 of `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]`, run Tier 2 Hardening on `[NEW] @[scripts/provision_gcp_cloud.py]`, synchronize Tier 7 documentation, and run `/tier8-audit-plan`.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]
```
