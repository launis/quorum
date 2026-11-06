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

# Implementation Plan: Guided GCP Live Cloud Cutover, `qrum.ai` Domain Reservation & Provisioning Orchestrator

## 1. Objective & Architectural Background

This implementation plan is the **Stage 2 Live Cloud Cutover** companion to `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`. Once `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]` has been executed locally to harden `Settings`, `HealthCheckResponseDTO` (defined in `backend_v2/models/dtos/system.py`), `GET /api/v2/system/health`, `run_worker.py`, `Dockerfile`, and `docker-compose.yml`, this plan guides the operator and executing agent through the complete transition from a local Windows 11 development environment to a live, production-grade B2B SaaS cloud service on **Google Cloud Platform (`europe-north1` / Finland)** under the **`qrum.ai`** domain.

To ensure the transition is both **interactively guided for human-only external actions** (domain purchase, registrar NS delegation, GCP billing activation, and tier selection) and **deterministically automated in code**, this plan delivers:

1. **Interactive Human-in-the-Loop Runbook for Domain Reservation, GCP Billing, Tier Selection & Email Activation (Section 1.1 – Section 1.4)**:
   - Step-by-step instructions for reserving `qrum.ai`, configuring registrar nameservers (`NS`), authenticating `gcloud`, attaching a GCP Billing Account, selecting between the cost-minimized `pilot` tier and high-availability `ha` production tier, and activating transactional emails (`CONSOLE` vs. `HTTP_API` with Resend EU).
2. **Typed 6-Stage GCP Provisioning, DNS Verification & Client Cutover CLI (`[NEW] @[scripts/provision_gcp_cloud.py]`)**:
   - A 100% Pydantic V2 (`ConfigDict(strict=True, extra="forbid", frozen=True)`) operational orchestrator built on `@[scripts/_script_base.py#L28-L51]` that runs in two deterministic modes:
     - **`--check` (Safe Diagnostic & Interactive Guidance Mode)**: Inspects local and cloud readiness across any stage (`preflight`, `secrets`, `network_data`, `deploy`, `dns_ssl`, `client_env`, `all`) without mutating cloud infrastructure, and outputs exact human action instructions whenever an external checkpoint is pending.
     - **`--apply` (Deterministic Provisioning & Cutover Mode)**: Executes the verified `gcloud` provisioning, Secret Manager secret generation (`secrets.token_urlsafe(48)`), Cloud Build image compilation, Cloud Run service deployment (`quorum-api` and `quorum-worker`), PostgreSQL 19 ontology seeding (`backend_v2.seed.run_seed`), SAN SSL Load Balancer attachment, and `client_app_v2/.env` cloud profile switching with bounded subprocess timeouts (`timeout_seconds`).

---

### 1.1 Human Checkpoint A — `qrum.ai` Domain Reservation & Registrar Setup Guide

Before activating HTTPS on `https://qrum.ai`, `https://api.qrum.ai`, `https://app.qrum.ai`, and `https://studio.qrum.ai`, reserve the domain name so no third party can claim it:

1. **Where to Register `qrum.ai`**:
   - Register `qrum.ai` at an ICANN-accredited `.ai` registrar (specifically and exhaustively: **Porkbun**, **Namecheap**, **Cloudflare Registrar**, or **Google Cloud Domains**).
   - Note that `.ai` registry rules enforce a minimum 2-year registration period at initial purchase.
2. **Mandatory Registrar Account Settings at Purchase**:
   - **WHOIS Privacy / Redaction**: Enable **ON** (protects registrant contact details in public `whois.nic.ai` lookups).
   - **Auto-Renew**: Enable **ON** (prevents accidental domain expiration in production).
   - **DNSSEC**: Leave **OFF** during initial nameserver delegation to Google Cloud DNS (DNSSEC can be enabled inside Cloud DNS after `NS` delegation completes; leaving registrar DNSSEC enabled while switching nameservers breaks DNS resolution).
3. **Connecting `qrum.ai` to Google Cloud DNS (`qrum-ai-zone`)**:
   - During **Stage 5 (`dns_ssl`)**, `uv run python scripts/provision_gcp_cloud.py --stage dns_ssl --apply` creates the `qrum-ai-zone` managed zone in Google Cloud DNS and prints the 4 authoritative Google Cloud nameservers:
     - `ns-cloud-x1.googledomains.com.`
     - `ns-cloud-x2.googledomains.com.`
     - `ns-cloud-x3.googledomains.com.`
     - `ns-cloud-x4.googledomains.com.`
   - Log into your domain registrar dashboard -> **Domain Management (`qrum.ai`)** -> **Nameservers** -> select **Custom Nameservers** -> paste those exact 4 `googledomains.com` hostnames (without trailing dots if the registrar UI strips them) -> Save.
   - Verify propagation from Windows 11 PowerShell using:
     ```powershell
     uv run python scripts/provision_gcp_cloud.py --stage dns_ssl --check
     ```
     Once `DNSVerificationResultDTO.is_delegated` reports `True`, Google Certificate Manager automatically validates and activates the `qrum-san-cert` TLS 1.3 certificate (`PROVISIONING` -> `ACTIVE`).

---

### 1.2 Human Checkpoint B — Google Cloud Project (`cognitive-quorum`), Billing & `gcloud` CLI Setup

1. **Install & Authenticate Google Cloud SDK on Windows 11**:
   - Verify `gcloud` is installed (`gcloud --version`).
   - Authenticate your Google account and application-default credentials in PowerShell:
     ```powershell
     gcloud auth login
     gcloud auth application-default login
     ```
2. **Create or Select the `cognitive-quorum` Project**:
   ```powershell
   gcloud projects create cognitive-quorum --name="Cognitive Quorum"
   gcloud config set project cognitive-quorum
   ```
3. **Link an Active Billing Account (Mandatory for Cloud Run, Cloud SQL, Memorystore & Vertex AI)**:
   - Open **Google Cloud Console -> Billing** (`https://console.cloud.google.com/billing`) and link your active billing account to project `cognitive-quorum`, or via CLI:
     ```powershell
     gcloud billing accounts list
     gcloud billing projects link cognitive-quorum --billing-account=01XXXX-XXXXXX-XXXXXX
     ```
4. **Verify Readiness via the Orchestrator**:
   ```powershell
   uv run python scripts/provision_gcp_cloud.py --stage preflight --check
   ```

---

### 1.3 Human Checkpoint C — Infrastructure Tier Selection (`pilot` vs. `ha`)

`scripts/provision_gcp_cloud.py` supports two explicit deployment tiers via `--tier pilot` (default for initial launch) and `--tier ha` (full enterprise high-availability):

| Resource | `--tier pilot` (Initial Launch / Low Monthly Cost) | `--tier ha` (Enterprise Production High Availability) |
| :--- | :--- | :--- |
| **Cloud SQL (PostgreSQL 19)** | `db-g1-small`, `ZONAL` availability, 10 GB SSD, automated daily backups | `db-custom-2-8192` (2 vCPU, 8 GB RAM), `REGIONAL` HA, PITR + 14 retained backups |
| **Memorystore (Redis)** | `BASIC` tier, `1 GB` capacity (`europe-north1`) | `STANDARD_HA` tier, `2 GB` capacity with automatic cross-zone failover |
| **Cloud Run (`quorum-api`)** | `min-instances=0`, `max-instances=4`, `2 GiB` RAM, `2` vCPU | `min-instances=1` (zero cold start), `max-instances=10`, `2 GiB` RAM, `2` vCPU |
| **Cloud Run (`quorum-worker`)** | `min-instances=1`, `max-instances=2`, `2 GiB` RAM, `2` vCPU | `min-instances=1`, `max-instances=5`, `4 GiB` RAM, `2` vCPU |

---

### 1.4 Human Checkpoint D — Transactional Email Activation (`CONSOLE` on Day 1 -> `HTTP_API` with Resend EU)

1. **Day 1 Launch (`EMAIL_TRANSPORT_MODE=console`)**:
   - No external email provider account is required. `provision_gcp_cloud.py` defaults to `--email-mode console`, allowing the entire cloud stack to launch with zero third-party email dependencies while logging redacted invitation and task assignment paths (`_redact_action_url` in `@[backend_v2/services/auth/email_service.py#L26-L39]`).
2. **Enabling Automated Emails (`EMAIL_TRANSPORT_MODE=http_api`)**:
   - When ready to dispatch live invitation and assignment emails from `no-reply@qrum.ai`:
     1. Create a free EU-region (`eu-west-1` / Ireland) account at **Resend** (`https://resend.com`), add domain `qrum.ai`, and copy the 3 DKIM/SPF DNS records into Cloud DNS (`qrum-ai-zone`).
     2. Store the Resend API key in GCP Secret Manager and switch `quorum-api` to `http_api` mode using:
        ```powershell
        uv run python scripts/provision_gcp_cloud.py --stage deploy --email-mode http_api --email-endpoint https://api.resend.com/emails --apply
        ```

---

## 2. Scope & Target Boundaries (5-Column Directives Table)

### Context Files (Read-Only)
- `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`
- `@[scripts/_script_base.py#L28-L51]`
- `@[backend_v2/settings.py#L53-L1335]`
- `@[backend_v2/services/auth/email_service.py#L42-L298]`
- `@[client_app_v2/lib/core/environment/env.dart#L25-L80]`

### Target Files (`[NEW]`, `[MODIFY]`)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`[NEW] @[scripts/provision_gcp_cloud.py]` (`ProvisionStage`, `DeploymentTier`, `ClientEnvMode`, `GCPProvisionConfigDTO`, `CommandExecutionResultDTO`, `DNSVerificationResultDTO`, `StageExecutionReportDTO`, `ProvisioningError`, `run_subprocess_command`, `verify_dns_delegation`, `generate_secret_value`, `build_stage_commands`, `switch_flutter_client_env`, `execute_provision_stage`, `main`)** | Running unvalidated ad-hoc shell one-liners without preflight verification, hardcoding secrets in scripts or git, using naked dictionaries (`dict[str, Any]`, `QGR005`), calling `json.loads` (`QGR011`) or `os.environ.get` (`QGR016`), logging raw secret tokens (`QGR033`), or executing unbounded `subprocess.run` calls without explicit timeouts. | Build a 100% typed Pydantic V2 CLI orchestrator (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with PEP 593 `Annotated` fields, `ProvisionStage(StrEnum)` (`preflight`, `secrets`, `network_data`, `deploy`, `dns_ssl`, `client_env`, `all`), `DeploymentTier(StrEnum)` (`pilot`, `ha`), bounded `subprocess.run(..., timeout=config.command_timeout_seconds)`, cryptographic secret generation via `secrets.token_urlsafe(48)` piped via `input=` to `gcloud secrets versions add --data-file=-`, HTTP health verification via `httpx.Client(timeout=config.http_timeout_seconds)`, and deterministic `client_app_v2/.env` switching (`local` vs. `cloud`). | Prune external Terraform/Pulumi state-locking dependencies and third-party cloud SDK wrappers; use Google Cloud's native idempotent `gcloud` CLI commands encapsulated in pure, testable Python functions with `--check` and `--apply` modes. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/provision_gcp_cloud.py --test --ast-strict` |
| **`[NEW] @[backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py]` (`test_provision_gcp_cloud`)** | Writing happy-path-only tests or executing live network/`gcloud` subprocess calls during unit test execution (`mocking_mandate_for_llm`, `scoped_mock_and_fault_isolation_mandate`). | Write comprehensive unit tests and >=2 ISTQB negative boundary tests per stage scoping `monkeypatch` strictly to `scripts.provision_gcp_cloud`, verifying `GCPProvisionConfigDTO` validation, `pilot` vs. `ha` command synthesis, secret redaction (`SecretStr` never leaked to stdout/logs), DNS NS verification (`is_delegated=True` vs. `False`), `client_app_v2/.env` roundtrip updates, and `ProvisioningError` on non-zero exit codes or timeouts. | Prune live GCP API calls in unit tests; verify command construction, timeout enforcement, and error translation deterministically in memory and `tmp_path`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py --test --ast-strict` |
| **`[MODIFY] @[.agents/rules/04_directory_reference.md#L25-L121]`** | Leaving new operational scripts or their companion unit tests undocumented in the repository directory index. | Register `scripts/test_provision_gcp_cloud.py` under `test_directory_isolation` (`@[.agents/rules/04_directory_reference.md#L25-L29]`) and `provision_gcp_cloud.py` under `<module path="scripts/">` (`@[.agents/rules/04_directory_reference.md#L118-L121]`). | Prune verbose prose in `04_directory_reference.md`; add concise single-clause index entries matching existing script entries. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md` |

---

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

Pre-flight execution of `uv run --no-sync --offline python scripts/audit_technical_debt.py --targets scripts/_script_base.py --include-one-hop` scanned `@[scripts/_script_base.py#L28-L51]` with **0 AST technical debt findings**. System 2 architectural analysis identified three operational cutover hazards that are prevented by design in Step 1:

1. **Plaintext Secret Exposure in CLI Arguments (`QGR033` & Process Table Leak Prevention)**:
   - **Root Cause**: Passing generated secrets (`JWT_SECRET_KEY`, `SECRET_ENCRYPTION_KEY`, `DATABASE_URL`) as command-line arguments makes them visible in host process tables and terminal transcripts.
   - **Prevention**: `provision_gcp_cloud.py` generates secrets in memory via `secrets.token_urlsafe(48)` wrapped in `SecretStr` and pipes the bytes exclusively through `stdin` (`gcloud secrets versions add <secret_name> --data-file=-`) while never logging or printing `.get_secret_value()`.
2. **Premature SSL Certificate & Load Balancer Cutover Before `.ai` NS Propagation**:
   - **Root Cause**: Attaching traffic or switching `client_app_v2/.env` to `https://api.qrum.ai` before `.ai` registry `NS` records resolve to `qrum-ai-zone` causes TLS handshake failures while Google Certificate Manager is still in `PROVISIONING` state.
   - **Prevention**: `verify_dns_delegation` in `scripts/provision_gcp_cloud.py` compares the live `NS` records against the authoritative `qrum-ai-zone` nameservers and prints explicit human registrar instructions until delegation is verified.
3. **Manual `client_app_v2/.env` Editing Errors During Local-to-Cloud Switching**:
   - **Root Cause**: Manually editing `client_app_v2/.env` risks losing required `MOCK_*_USER_ID` 32-hex UUIDv7 variables enforced by `@[client_app_v2/lib/core/environment/env.dart#L25-L80]` or leaving trailing slashes on `API_URL`.
   - **Prevention**: `switch_flutter_client_env` deterministically updates `API_URL` and `ENVIRONMENT` in `client_app_v2/.env` (`http://127.0.0.1:8000` + `development` in `"local"` mode vs. `https://api.qrum.ai` + `production` in `"cloud"` mode) while preserving all other `.env` keys intact.

---

## 4. Detailed Execution Protocol (Hybrid XML Sandwich)

```xml
<execution_protocol>
  <step id="1" name="Phase 1 &amp; Core Orchestrator — Implement Typed 6-Stage GCP Provisioning &amp; Cutover CLI (scripts/provision_gcp_cloud.py)">
    <constraint invariant="strict_pydantic_v2_rust">All configuration, command specs, DNS verification results, and stage execution reports MUST use immutable Pydantic V2 models with ConfigDict(strict=True, extra="forbid", frozen=True) and PEP 593 Annotated fields. Naked dictionaries (QGR005), json.loads (QGR011), getattr/hasattr (QGR001), and .get() (QGR002) are strictly forbidden.</constraint>
    <constraint invariant="credential_hardcoding_ban">Never hardcode or log secret values (QGR033). Generate secrets via stdlib secrets.token_urlsafe(48), store in SecretStr, and pass to gcloud secrets versions add --data-file=- via subprocess stdin.</constraint>
    <constraint invariant="unbounded_io_timeout_mandate">Every subprocess.run and httpx.Client invocation MUST specify an explicit timeout resolved from GCPProvisionConfigDTO (command_timeout_seconds and http_timeout_seconds).</constraint>
    <action>Create `[NEW] @[scripts/provision_gcp_cloud.py]` importing `setup_script_environment`, `ANSIColors`, and `get_repo_root` from `scripts._script_base` and defining:
      - `ProvisionStage(StrEnum)` with members: `PREFLIGHT = "preflight"`, `SECRETS = "secrets"`, `NETWORK_DATA = "network_data"`, `DEPLOY = "deploy"`, `DNS_SSL = "dns_ssl"`, `CLIENT_ENV = "client_env"`, `ALL = "all"`.
      - `DeploymentTier(StrEnum)` with members: `PILOT = "pilot"`, `HA = "ha"`.
      - `ClientEnvMode(StrEnum)` with members: `LOCAL = "local"`, `CLOUD = "cloud"`.
      - `ProvisioningError(Exception)` carrying `stage: ProvisionStage`, `message: str`, and `remediation: str`.
      - `GCPProvisionConfigDTO(BaseModel)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with PEP 593 `Annotated` fields:
        - `project_id: Annotated[str, Field(default="cognitive-quorum", min_length=1, description="Target Google Cloud project ID")] = "cognitive-quorum"`
        - `region: Annotated[str, Field(default="europe-north1", min_length=1, description="Target Google Cloud deployment region")] = "europe-north1"`
        - `primary_domain: Annotated[str, Field(default="qrum.ai", min_length=3, description="Primary production domain")] = "qrum.ai"`
        - `tier: Annotated[DeploymentTier, Field(default="pilot", description="Infrastructure sizing tier")]`
        - `email_mode: Annotated[Literal["console", "http_api"], Field(default="console", description="Transactional email transport mode")] = "console"`
        - `email_endpoint: Annotated[str, Field(default="https://api.resend.com/emails", min_length=8, description="HTTPS transactional email endpoint")] = "https://api.resend.com/emails"`
        - `client_env_mode: Annotated[ClientEnvMode, Field(default="cloud", description="Target mode for client_app_v2/.env")]`
        - `command_timeout_seconds: Annotated[int, Field(default=600, ge=5, le=3600, description="Bounded timeout in seconds for gcloud subprocess execution")] = 600`
        - `http_timeout_seconds: Annotated[float, Field(default=15.0, ge=1.0, le=120.0, description="Bounded timeout in seconds for health probe HTTP verification")] = 15.0`
        - `@field_validator("primary_domain", "email_endpoint")` rejecting trailing slashes (`"/"`) or whitespace-only values with `ValueError`.
      - `CommandSpecDTO(BaseModel)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with `description: str`, `args: tuple[str, ...]`, and `human_checkpoint_hint: str | None = None`.
      - `CommandExecutionResultDTO(BaseModel)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with `command: tuple[str, ...]`, `return_code: int`, `stdout: str`, `stderr: str`.
      - `DNSVerificationResultDTO(BaseModel)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with `domain: str`, `expected_nameservers: tuple[str, ...]`, `observed_nameservers: tuple[str, ...]`, `is_delegated: bool`, and `registrar_instructions: str`.
      - `StageExecutionReportDTO(BaseModel)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with `stage: ProvisionStage`, `mode: Literal["check", "apply"]`, `succeeded: bool`, `executed_commands: tuple[str, ...]`, and `human_actions_required: tuple[str, ...]`.
      - Pure helper and execution functions:
        - `generate_secret_value(nbytes: int = 48) -> SecretStr`: validates `32 <= nbytes <= 128` and returns `SecretStr(secrets.token_urlsafe(nbytes))`.
        - `run_subprocess_command(args: Sequence[str], *, timeout_seconds: int, stdin_secret: SecretStr | None = None) -> CommandExecutionResultDTO`: executes `subprocess.run` with `timeout=timeout_seconds`, passing `stdin_secret.get_secret_value()` only via `input=` if provided, and raising `ProvisioningError` on `subprocess.TimeoutExpired` or `OSError`.
        - `build_stage_commands(stage: ProvisionStage, config: GCPProvisionConfigDTO) -> tuple[CommandSpecDTO, ...]`: deterministically constructs the ordered `gcloud` command specifications for `"preflight"`, `"secrets"`, `"network_data"` (branching on `"pilot"` vs. `"ha"` sizing tiers), `"deploy"` (building the Artifact Registry image, executing the `quorum-seed` Cloud Run Job inside `quorum-vpc` via `--command "/app/.venv/bin/python" --args="-m,backend_v2.seed.run_seed,postgres" --execute-now --wait` so `_validate_database_preflight` passes, and then deploying `quorum-api` and `quorum-worker` via `--command "/app/.venv/bin/python" --args="-m,backend_v2.run_worker"` with `GOOGLE_CLOUD_PROJECT`, `VERTEX_PROJECT_ID`, `USE_VERTEX_LLM=true`, and `DATABASE_URL=quorum-db-url:latest`), and `"dns_ssl"`.
        - `verify_dns_delegation(domain: str, expected_nameservers: Sequence[str], *, timeout_seconds: int = 15) -> DNSVerificationResultDTO`: normalizes trailing dots and case on expected and observed NS hostnames and returns `is_delegated=True` when all expected Cloud DNS nameservers are present, alongside step-by-step registrar instructions.
        - `verify_cloud_health(health_url: str, *, timeout_seconds: float = 15.0) -> HealthCheckResponseDTO`: queries `health_url` via `httpx.Client(timeout=timeout_seconds)` and validates the payload via `HealthCheckResponseDTO.model_validate_json(response.text)`, raising `ProvisioningError` if HTTP status != 200 or `status != "ok"`.
        - `switch_flutter_client_env(env_file_path: Path, *, mode: ClientEnvMode, primary_domain: str) -> Path`: updates `API_URL` (`http://127.0.0.1:8000` for `LOCAL`, `f"https://api.{primary_domain}"` for `CLOUD`) and `ENVIRONMENT` (`development` for `LOCAL`, `production` for `CLOUD`) in `client_app_v2/.env` while preserving all existing `.env` keys, raising `ProvisioningError` if `env_file_path` does not exist.
        - `execute_provision_stage(stage: ProvisionStage, config: GCPProvisionConfigDTO, *, apply: bool = False, env_file_path: Path | None = None) -> StageExecutionReportDTO`: executes `--check` (returning planned commands and interactive human instructions without mutating state) or `--apply` (running stage commands and failing fast with `ProvisioningError` on non-zero return codes).
        - `main(argv: list[str] | None = None) -> int`: CLI entrypoint supporting `--stage`, `--tier`, `--project-id`, `--region`, `--primary-domain`, `--email-mode`, `--email-endpoint`, `--client-env-mode`, `--check`, and `--apply`.
    </action>
  </step>

  <step id="2" name="Unit &amp; ISTQB Boundary Test Suite &amp; Directory Reference Registration">
    <constraint invariant="anti_happy_path_mandate">Include at least 2 negative test cases per feature covering invalid inputs, boundary violations (min-1 / max+1), subprocess failures/timeouts, and non-200 / degraded health responses.</constraint>
    <constraint invariant="scoped_mock_and_fault_isolation_mandate">Scope all monkeypatch overrides strictly to scripts.provision_gcp_cloud without patching root stdlib modules.</constraint>
    <action>Create `[NEW] @[backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py]` testing:
      1. `GCPProvisionConfigDTO` positive defaults (`project_id="cognitive-quorum"`, `region="europe-north1"`, `primary_domain="qrum.ai"`, `tier="pilot"`) and negative `ValidationError` on trailing slash (`primary_domain="qrum.ai/"`), empty strings, `command_timeout_seconds=4` (`min-1`), `command_timeout_seconds=3601` (`max+1`), and `extra="forbid"`.
      2. `generate_secret_value` positive cryptographic token generation and negative `ValueError` on `nbytes=31` (`min-1`) and `nbytes=129` (`max+1`).
      3. `build_stage_commands` verification across `PREFLIGHT`, `SECRETS`, `NETWORK_DATA` (`"pilot"` vs. `"ha"` SQL/Redis/Cloud Run flags), `DEPLOY`, and `DNS_SSL`.
      4. `verify_dns_delegation` positive match (case/trailing-dot insensitive) and negative mismatch (`is_delegated=False` with registrar instructions).
      5. `verify_cloud_health` positive `HealthCheckResponseDTO` validation (`status="ok"`) and >=2 negative cases (`status="degraded"`, HTTP 503, and transport error raising `ProvisioningError`).
      6. `switch_flutter_client_env` roundtrip switching between `"cloud"` (`API_URL=https://api.qrum.ai`, `ENVIRONMENT=production`) and `"local"` (`API_URL=http://127.0.0.1:8000`, `ENVIRONMENT=development`) while preserving `MOCK_ADMIN_USER_ID`, plus negative `ProvisioningError` when the `.env` file path is missing.
      7. `execute_provision_stage` and `main()` in `--check` mode and `--apply` mode (including negative `ProvisioningError` / exit code `1` when a subprocess command returns non-zero or times out).
    </action>
    <action>Modify `@[.agents/rules/04_directory_reference.md#L25-L121]` to register `scripts/test_provision_gcp_cloud.py` in `<rule_block id="test_directory_isolation">` and `provision_gcp_cloud.py` in `<module path="scripts/">`.</action>
    <action>Run quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/provision_gcp_cloud.py --test --ast-strict` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py --test --ast-strict`.</action>
  </step>
</execution_protocol>
```

---

## 5. Architectural Safeguards & Verification Plan (ISTQB Test Matrix)

### Automated Unit & Structural Tests
- **Scenario 1 (Happy Path — Multi-Stage Check & Apply Orchestration):** `execute_provision_stage` with `"pilot"` and `"ha"` tiers generates deterministic `gcloud` command sequences across all 6 stages, pipes `SecretStr` secrets via `stdin`, verifies `DNSVerificationResultDTO.is_delegated == True`, validates `HealthCheckResponseDTO(status="ok")`, and switches `client_app_v2/.env` to `API_URL=https://api.qrum.ai` and `ENVIRONMENT=production`.
- **Scenario 2 (Negative Path 1 — Missing/Invalid Input & Unpropagated DNS / Degraded Health):** `GCPProvisionConfigDTO` rejects trailing slashes (`primary_domain="qrum.ai/"`, `email_endpoint="https://api.resend.com/emails/"`) and unrecognized keys (`extra="forbid"`); `verify_dns_delegation` returns `is_delegated=False` when registrar NS records do not match Cloud DNS; `verify_cloud_health` raises `ProvisioningError` when `/api/v2/system/health` returns `"degraded"` or HTTP `503`; `switch_flutter_client_env` raises `ProvisioningError` when target `.env` is missing.
- **Scenario 3 (Negative Path 2 — ISTQB Boundary Value Violations & Subprocess Timeout):** `GCPProvisionConfigDTO` rejects `command_timeout_seconds=4` (`min-1`) and `command_timeout_seconds=3601` (`max+1`), `http_timeout_seconds=0.5` (`min-1`) and `http_timeout_seconds=120.5` (`max+1`); `generate_secret_value` rejects `nbytes=31` (`min-1`) and `nbytes=129` (`max+1`); `run_subprocess_command` translates `subprocess.TimeoutExpired` into `ProvisioningError`.

### Global Completion Gates & Mandatory Final E2E REST API Verification Gate
- **Localized Script Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/provision_gcp_cloud.py --test --ast-strict`
- **Global Backend Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`
- **Mandatory Final E2E REST API Verification Gate:**
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
