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
     - `@[ki_global_config_sovereignty.md]`: Document the 6-stage GCP cloud provisioning and client environment cutover orchestrator (`@[scripts/provision_gcp_cloud.py]`), covering `"pilot"` vs. `"ha"` sizing, `SecretStr` stdin secret injection, `.ai` registrar NS delegation verification, and `client_app_v2/.env` switching.
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
| **REQ-CUTOVER-01** | Implement `[NEW] @[scripts/provision_gcp_cloud.py]` with typed Pydantic V2 DTOs (`GCPProvisionConfigDTO`, `CommandSpecDTO`, `CommandExecutionResultDTO`, `DNSVerificationResultDTO`, `StageExecutionReportDTO`), `ProvisionStage`, `DeploymentTier` (`pilot` vs. `ha`), `ClientEnvMode` (`local` vs. `cloud`), `SecretStr` stdin secret injection, DNS NS verification, HTTP health verification, and `client_app_v2/.env` switching. | Step 1 | `[ ]` |
| **REQ-CUTOVER-02** | Implement `[NEW] @[backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py]` with >90% coverage and >=2 ISTQB negative boundary tests per feature, and register `provision_gcp_cloud.py` and `scripts/test_provision_gcp_cloud.py` in `@[.agents/rules/04_directory_reference.md#L25-L121]`. | Step 2 | `[ ]` |

---

# Session Handover Context

## Achieved
- Authored `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]` and `@[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]` as the Stage 2 guided cloud provisioning and cutover companion to `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`.
- Included complete Human-in-the-Loop interactive guides for `qrum.ai` domain registration and `.ai` registrar `NS` delegation (Section 1.1), GCP project and Billing Account setup (Section 1.2), `pilot` vs. `ha` infrastructure cost-tier selection (Section 1.3), and transactional email activation from `CONSOLE` to `HTTP_API` with Resend EU (Section 1.4).
- Designed the 6-stage typed provisioning and cutover CLI (`[NEW] @[scripts/provision_gcp_cloud.py]`) and its unit test suite (`[NEW] @[backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py]`).

## Learned
- Separating local cloud-readiness code hardening (`@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`) from interactive GCP infrastructure provisioning and client cutover (`@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]`) lets the team verify 100% of backend/container invariants locally with zero cloud spend before provisioning live GCP resources.
- Piping generated `SecretStr` secrets via `subprocess.run(..., input=...)` to `gcloud secrets versions add --data-file=-` prevents secret leakage in process tables and terminal logs (`QGR033`).

## Remaining
- Execute `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]` first, then execute Steps 1–2 of `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md]`.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md] @[docs/implementationplans/TRACKER_GCP_Guided_Cloud_Cutover.md]
```
