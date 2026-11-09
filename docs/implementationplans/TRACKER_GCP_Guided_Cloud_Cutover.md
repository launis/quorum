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
  <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
</required_context_rules>

---

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]`
  - [ ] Step 1: Phase 1 & Core Orchestrator — Implement Typed 6-Stage GCP Provisioning & Cutover CLI (scripts/provision_gcp_cloud.py)
  - [ ] Step 2: Unit & ISTQB Boundary Test Suite & Directory Reference Registration
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`
  - [ ] [NEW] @[scripts/provision_gcp_cloud.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[ki_global_config_sovereignty.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_global_config_sovereignty.md]`: Document the 6-stage GCP cloud provisioning and client environment cutover orchestrator (`@[scripts/provision_gcp_cloud.py]`), `@[docker-compose.yml#L1-L57]` cleanup, and the 3-tier B2B SaaS secret governance architecture (Tier 1: Infrastructure Bootstrap Secrets `quorum-jwt-secret` and `quorum-db-url` in `.env` / GCP Secret Manager; Tier 2: `ROOT_SYSTEM` `org_0195f3a0000070008000000000000001` platform baseline secrets in PostgreSQL 19 `tenant_secrets`; Tier 3: Customer Tenant `org_<hex32>` self-service BYOK secrets in PostgreSQL 19 `tenant_secrets` encrypted with NIST SP 800-57 `ENVELOPE_KMS` AES-256-GCM DEK/KEK), `.ai` registrar NS delegation verification, and `client_app_v2/.env` switching.
  2. **Directory Reference Sync:**
     - Verify `@[.agents/rules/04_directory_reference.md]` indexes `provision_gcp_cloud.py` and `scripts/test_provision_gcp_cloud.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `@[docs/architecture/01_system_context_and_invariants.md]` describing the GCP Cloud Run provisioning and domain cutover architecture in present tense.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

---

## Instructions for the Execution Agent

1. **Stateless Context Reset**: At the start of execution, physically load `@[.agents/rules/00-antigravity-core.md]`, `@[.agents/rules/01-python-backend.md]`, `@[.agents/rules/04_directory_reference.md]`, `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]`, and `@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]`.
2. **Quality Gate Enforcement**: After completing each Python code step, execute `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict` before checking off the step in `@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]`.
3. **Atomic Checkpoint Commits**: After each verified logical step passes the quality gate, stage the modified files explicitly and perform an atomic commit using Conventional Commits syntax (`feat(gcp): ...`).
4. **Interactive Live Cutover Execution**: Once Steps 1–2 are committed and verified by unit tests, the operator can run `uv run python scripts/provision_gcp_cloud.py --stage all --check` to inspect interactive human checkpoints and `uv run python scripts/provision_gcp_cloud.py --stage <stage> --apply` to provision each cloud stage step-by-step.

---

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-CUTOVER-01** | Implement `[NEW] @[scripts/provision_gcp_cloud.py]` with typed Pydantic V2 DTOs (`GCPProvisionConfigDTO`, `CommandSpecDTO`, `CommandExecutionResultDTO`, `DNSVerificationResultDTO`, `StageExecutionReportDTO`), `ProvisionStage`, `DeploymentTier` (`pilot` vs. `ha`), `ClientEnvMode` (`local` vs. `cloud`), `SecretStr` stdin secret injection (`quorum-jwt-secret`, `quorum-db-url`), pure infrastructure Cloud Run deployment flags (zero legacy `USE_VERTEX_LLM` / `VERTEX_PROJECT_ID` / `VERTEX_LOCATION` flags), DNS NS verification, HTTP health verification, and `client_app_v2/.env` switching, and clean `[MODIFY] @[docker-compose.yml#L1-L57]` to remove legacy LLM environment variables and `service-account.json` volume mounts. | Step 1 | `[ ]` |
| **REQ-CUTOVER-02** | Implement `[NEW] @[backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py]` with >90% coverage and >=2 ISTQB negative boundary tests per feature (including verification that `build_stage_commands` and `docker-compose.yml` contain zero legacy `USE_VERTEX_LLM`, `VERTEX_PROJECT_ID`, or `VERTEX_LOCATION` references), and register `provision_gcp_cloud.py` and `scripts/test_provision_gcp_cloud.py` in `@[.agents/rules/04_directory_reference.md#L25-L121]`. | Step 2 | `[ ]` |

---

# Session Handover Context

## Achieved
- Authored and hardened `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]` and `@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]` as the Stage 2 guided cloud provisioning and cutover companion to the completed `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`.
- Included complete Human-in-the-Loop interactive guides for `qrum.ai` domain registration and `.ai` registrar `NS` delegation (Section 1.1), GCP project and Billing Account setup (Section 1.2), `pilot` vs. `ha` infrastructure cost-tier selection (Section 1.3), transactional email activation from `CONSOLE` to `HTTP_API` with Resend EU (Section 1.4), and migrating local `.env` LLM/MCP keys and `service-account.json` into PostgreSQL 19 `tenant_secrets` (`ROOT_SYSTEM` `org_0195f3a0000070008000000000000001`) via `ENVELOPE_KMS` or `CLOUD_SECRET_MANAGER` (Section 1.5).
- Aligned `[NEW] @[scripts/provision_gcp_cloud.py]`, `[MODIFY] @[docker-compose.yml#L1-L57]`, and `[NEW] @[backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py]` with `@[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]` so zero legacy LLM `.env` variables (`USE_VERTEX_LLM`, `VERTEX_PROJECT_ID`, `VERTEX_LOCATION`) or `service-account.json` container mounts remain.

## Learned
- Because `@[docs/implementationplans/TRACKER_GCP_Production_Deployment.md]` is already 100% completed, consolidating the `@[docker-compose.yml#L1-L57]` legacy LLM environment variable and `service-account.json` mount cleanup directly into Step 1 of `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]` keeps completed trackers untouched while ensuring zero legacy LLM `.env` drift remains in container or Cloud Run specifications.
- Piping generated `SecretStr` infrastructure bootstrap secrets (`quorum-jwt-secret`, `quorum-db-url`) via `subprocess.run(..., input=...)` to `gcloud secrets versions add --data-file=-` prevents secret leakage in process tables and terminal logs (`QGR033`), while all LLM and MCP credentials reside in PostgreSQL 19 `tenant_secrets`.

## Remaining
- Execute Steps 1–2 of `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]` (after or alongside `@[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]`).

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]
```
