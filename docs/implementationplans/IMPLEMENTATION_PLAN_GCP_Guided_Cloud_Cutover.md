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

1. **Interactive Human-in-the-Loop Runbook for Domain Reservation, GCP Billing, Tier Selection, Email Activation & Database `tenant_secrets` Migration (Section 1.1 – Section 1.5)**:
   - Step-by-step instructions for reserving `qrum.ai`, configuring registrar nameservers (`NS`), authenticating `gcloud`, attaching a GCP Billing Account, selecting between the cost-minimized `pilot` tier and high-availability `ha` production tier, activating transactional emails (`CONSOLE` vs. `HTTP_API` with Resend EU), and migrating local `.env` LLM/MCP keys and `service-account.json` into PostgreSQL 19 `tenant_secrets` (`ROOT_SYSTEM` `org_0195f3a0000070008000000000000001`).
2. **Typed 6-Stage GCP Provisioning, DNS Verification & Client Cutover CLI (`[NEW] @[scripts/provision_gcp_cloud.py]`) & Docker Compose Runtime SSOT Cleanup (`[MODIFY] @[docker-compose.yml#L1-L57]`)**:
   - A 100% Pydantic V2 (`ConfigDict(strict=True, extra="forbid", frozen=True)`) operational orchestrator built on `@[scripts/_script_base.py#L28-L51]` that runs in two deterministic modes:
     - **`--check` (Safe Diagnostic & Interactive Guidance Mode)**: Inspects local and cloud readiness across any stage (`preflight`, `secrets`, `network_data`, `deploy`, `dns_ssl`, `client_env`, `all`) without mutating cloud infrastructure, and outputs exact human action instructions whenever an external checkpoint is pending.
     - **`--apply` (Deterministic Provisioning & Cutover Mode)**: Executes the verified `gcloud` provisioning, Secret Manager infrastructure bootstrap secret generation (`secrets.token_urlsafe(48)` for `quorum-jwt-secret` and `quorum-db-url`), Cloud Build image compilation, Cloud Run service deployment (`quorum-api` and `quorum-worker` with zero legacy LLM `.env` flags), PostgreSQL 19 ontology seeding (`backend_v2.seed.run_seed`), SAN SSL Load Balancer attachment, and `client_app_v2/.env` cloud profile switching with bounded subprocess timeouts (`timeout_seconds`).
   - Removes legacy `USE_VERTEX_LLM`, `VERTEX_LOCATION`, and `service-account.json` volume mounts from `@[docker-compose.yml#L1-L57]` so container definitions align 100% with the PostgreSQL 19 `system_configs` and `tenant_secrets` SSOT.

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

### 1.5 Human Checkpoint E — B2B SaaS BYOK Best Practice, Migrating `.env` & `service-account.json` to PostgreSQL 19 `tenant_secrets`, and the Infrastructure `.env` Boundary

Under the runtime SSOT architecture (`@[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]`), Quorum enforces the industry-standard B2B SaaS separation between **Infrastructure Bootstrap Secrets** (required to start the container and connect to PostgreSQL 19) and **Runtime Application & BYOK Secrets** (stored 100% in the PostgreSQL 19 `tenant_secrets` table with zero `.env` or `os.environ` fallback):

#### 1.5.1 Three-Tier Secret Governance Matrix (Best Practice)

| Secret Tier | Where It Lives | How It Is Provisioned & Rotated | What It Contains (Exhaustive) |
| :--- | :--- | :--- | :--- |
| **Tier 1: Infrastructure Bootstrap Secrets** | **Local**: `.env` file.<br>**Cloud**: GCP Secret Manager (`quorum-db-url`, `quorum-jwt-secret`) bound to Cloud Run at startup. | Set once during environment setup via `scripts/provision_gcp_cloud.py --stage secrets --apply`. | `DATABASE_URL`, `JWT_SECRET_KEY` (also used to derive the local 256-bit HKDF-SHA256 Master Key-Encryption-Key when `KMS_MASTER_KEY_ID` is unset), `KMS_MASTER_KEY_ID` (optional Cloud KMS KEK URI), `REDIS_HOST`, `REDIS_PORT`, `STORAGE_BACKEND=POSTGRES`, `STORAGE_BUCKET_NAME`, `GCP_PROJECT`, `GCP_REGION`, `PRIMARY_DOMAIN`, `API_URL`, `FRONTEND_APP_BASE_URL`, `LOGFIRE_TOKEN`, `EMAIL_TRANSPORT_MODE`, `EMAIL_API_KEY`. |
| **Tier 2: Platform Baseline Secrets (`ROOT_SYSTEM`)** | **PostgreSQL 19 `tenant_secrets` table** under `organization_id = "org_0195f3a0000070008000000000000001"` encrypted with `SecretStorageMode.envelopeKms` (`AES-256-GCM`). | Platform `SYSTEM_ADMIN` via Flutter UI (**Settings -> Organization & IAM -> BYOK & MCP Secrets**) or `PUT /api/v2/iam/organizations/org_0195f3a0000070008000000000000001/secrets`. | Default platform credentials for `vertex_ai` (full `service-account.json` JSON payload or Express API key), `ai_studio` (`GEMINI_API_KEY`), `openai` (`OPENAI_API_KEY`), `anthropic` (`ANTHROPIC_API_KEY`), `azure_openai`, `local`, and platform MCP gateways (`sys_0195f3a00000700080008172bda70c86`). |
| **Tier 3: Customer Tenant BYOK Secrets (`org_<hex32>`)** | **PostgreSQL 19 `tenant_secrets` table** under the customer organization's `organization_id` encrypted with `SecretStorageMode.envelopeKms` (`AES-256-GCM`). | Customer Organization `ADMIN` via self-service Flutter UI (**Settings -> Organization & IAM -> BYOK & MCP Secrets**). | Customer-owned LLM API keys (`openai`, `anthropic`, `ai_studio`, `azure_openai`, `local`), customer GCP `service-account.json` (`vertex_ai`), and customer MCP gateway keys (`sys_<hex32>`). |

#### 1.5.2 Why `ENVELOPE_KMS` (Database Envelope Encryption) Is Used Instead of Per-Key GCP Secret Manager Objects
1. **Self-Service B2B Customer UX**: Customer administrators never have IAM access to the SaaS provider's GCP project (`cognitive-quorum`). They manage their own BYOK keys directly in the Quorum UI (`_ByokSecretsCard`), which immediately masks the key to a 4-character hint (`****<alnum4>`) and never exposes plaintext again.
2. **NIST SP 800-57 Two-Tier Envelope Encryption (`DEK` + `KEK`)**: Every row in `tenant_secrets` is encrypted in memory with its own unique 256-bit AES-256-GCM **Data Encryption Key (DEK)** (`ciphertext_payload`), and that DEK is wrapped by the server's **Master Key-Encryption-Key (KEK)** (`encrypted_dek`). Even a full PostgreSQL database dump cannot be decrypted without the runtime KEK (`JWT_SECRET_KEY` / `KMS_MASTER_KEY_ID`).
3. **Sub-Millisecond Execution & Zero Cloud API Overhead**: Decrypting `ENVELOPE_KMS` rows from PostgreSQL 19 takes less than 1 millisecond in memory with zero external GCP Secret Manager HTTP calls during parallel DAG execution, and works 100% identically on a local Windows 11 workstation and in GCP Cloud Run. (`SecretStorageMode.cloudSecretManager` exists only as an optional URI-pointer mode for regulated enterprise customers who mandate external vault residency.)

#### 1.5.3 Step-by-Step: Provisioning `ROOT_SYSTEM` Secrets After `quorum-seed` & Cleaning `.env` / `service-account.json`
1. **After Stage 4 (`deploy`) executes `quorum-seed` (`backend_v2.seed.run_seed postgres`)**, log into the Flutter application as `SYSTEM_ADMIN` (`ROOT_SYSTEM` `org_0195f3a0000070008000000000000001`) and open **Settings -> Organization & IAM -> BYOK & MCP Secrets (`_ByokSecretsCard`)**:
   - Keep **Storage Mode** on the default **`ENVELOPE_KMS`**.
   - Select **Provider: `vertex_ai`**, click the eye icon (`org_secret_visibility_toggle_btn`) to expand the multiline editor, paste the complete JSON contents of `service-account.json` (`type`, `project_id`, `private_key_id`, `private_key`, `client_email`, `token_uri`), and click **Save**.
   - Select each additional active LLM provider (`ai_studio`, `openai`, `anthropic`) or MCP gateway (`Tavily MCP Gateway (sys_0195f3a00000700080008172bda70c86)`), paste its API key, and click **Save**.
2. **Delete Legacy LLM/MCP Keys from `.env` and Unmount `service-account.json`**:
   - Once saved in PostgreSQL 19 `tenant_secrets`, `service-account.json` on disk and `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `TAVILY_API_KEY`, `USE_VERTEX_LLM`, `VERTEX_PROJECT_ID`, `VERTEX_LOCATION`, and `GOOGLE_APPLICATION_CREDENTIALS` in `.env` are never read by the runtime and are removed from `.env` and `@[docker-compose.yml#L1-L57]`.

---

## 2. Scope & Target Boundaries (5-Column Directives Table)

### Context Files (Read-Only)
- `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`
- `@[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]`
- `@[scripts/_script_base.py#L28-L51]`
- `@[backend_v2/settings.py#L68-L1494]`
- `@[backend_v2/services/auth/email_service.py#L42-L298]`
- `@[client_app_v2/lib/core/environment/env.dart#L25-L80]`

### Target Files (`[NEW]`, `[MODIFY]`)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`[NEW] @[scripts/provision_gcp_cloud.py]` (`ProvisionStage`, `DeploymentTier`, `ClientEnvMode`, `GCPProvisionConfigDTO`, `CommandExecutionResultDTO`, `DNSVerificationResultDTO`, `StageExecutionReportDTO`, `ProvisioningError`, `run_subprocess_command`, `verify_dns_delegation`, `generate_secret_value`, `build_stage_commands`, `switch_flutter_client_env`, `execute_provision_stage`, `main`)** | Running unvalidated ad-hoc shell one-liners without preflight verification, injecting obsolete LLM `.env` flags (`USE_VERTEX_LLM`, `VERTEX_PROJECT_ID`, `VERTEX_LOCATION`) into Cloud Run services, hardcoding secrets in scripts or git, using naked dictionaries (`dict[str, Any]`, `QGR005`), calling `json.loads` (`QGR011`) or `os.environ.get` (`QGR016`), logging raw secret tokens (`QGR033`), or executing unbounded `subprocess.run` calls without explicit timeouts. | Build a 100% typed Pydantic V2 CLI orchestrator (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with PEP 593 `Annotated` fields, `ProvisionStage(StrEnum)` (`preflight`, `secrets`, `network_data`, `deploy`, `dns_ssl`, `client_env`, `all`), `DeploymentTier(StrEnum)` (`pilot`, `ha`), bounded `subprocess.run(..., timeout=config.command_timeout_seconds)`, cryptographic infrastructure secret generation (`quorum-jwt-secret`, `quorum-db-url`) via `secrets.token_urlsafe(48)` piped via `input=` to `gcloud secrets versions add --data-file=-`, Cloud Run deployment injecting only pure infrastructure bootstrap variables (zero LLM/MCP `.env` flags), HTTP health verification via `httpx.Client(timeout=config.http_timeout_seconds)`, and deterministic `client_app_v2/.env` switching (`local` vs. `cloud`). | Prune external Terraform/Pulumi state-locking dependencies and third-party cloud SDK wrappers; use Google Cloud's native idempotent `gcloud` CLI commands encapsulated in pure, testable Python functions with `--check` and `--apply` modes. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/provision_gcp_cloud.py --test --ast-strict` |
| **`[MODIFY] @[docker-compose.yml#L1-L57]`** | Passing removed legacy LLM environment variables (`USE_VERTEX_LLM=true`, `VERTEX_LOCATION=europe-north1`, `GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json`), mounting `./service-account.json:/app/service-account.json` into containers when LLM credentials live in PostgreSQL 19 `tenant_secrets`, or declaring inconsistent `STORAGE_BUCKET_NAME` values between `backend` and `worker`. | Remove `USE_VERTEX_LLM`, `VERTEX_LOCATION`, `GOOGLE_APPLICATION_CREDENTIALS`, and `./service-account.json:/app/service-account.json` from both `backend` and `worker` services in `@[docker-compose.yml#L1-L57]`, and unify `STORAGE_BUCKET_NAME=cognitive-quorum.firebasestorage.app` across both services. | Prune redundant LLM container environment overrides; let PostgreSQL 19 `system_configs` and `tenant_secrets` govern all LLM routing and credentials. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py --test --ast-strict` |
| **`[NEW] @[backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py]` (`test_provision_gcp_cloud`)** | Writing happy-path-only tests or executing live network/`gcloud` subprocess calls during unit test execution (`mocking_mandate_for_llm`, `scoped_mock_and_fault_isolation_mandate`). | Write comprehensive unit tests and >=2 ISTQB negative boundary tests per stage scoping `monkeypatch` strictly to `scripts.provision_gcp_cloud`, verifying `GCPProvisionConfigDTO` validation, `pilot` vs. `ha` command synthesis, absence of deprecated `USE_VERTEX_LLM`/`VERTEX_PROJECT_ID`/`VERTEX_LOCATION` flags in `build_stage_commands` and `docker-compose.yml`, secret redaction (`SecretStr` never leaked to stdout/logs), DNS NS verification (`is_delegated=True` vs. `False`), `client_app_v2/.env` roundtrip updates, and `ProvisioningError` on non-zero exit codes or timeouts. | Prune live GCP API calls in unit tests; verify command construction, timeout enforcement, and error translation deterministically in memory and `tmp_path`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py --test --ast-strict` |
| **`[MODIFY] @[.agents/rules/04_directory_reference.md#L25-L121]`** | Leaving new operational scripts or their companion unit tests undocumented in the repository directory index. | Register `scripts/test_provision_gcp_cloud.py` under `test_directory_isolation` (`@[.agents/rules/04_directory_reference.md#L25-L29]`) and `provision_gcp_cloud.py` under `<module path="scripts/">` (`@[.agents/rules/04_directory_reference.md#L118-L121]`). | Prune verbose prose in `04_directory_reference.md`; add concise single-clause index entries matching existing script entries. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md` |

---

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

Pre-flight execution of `uv run --no-sync --offline python scripts/audit_technical_debt.py --targets scripts/_script_base.py --include-one-hop` scanned `@[scripts/_script_base.py#L28-L51]` with **0 AST technical debt findings**. System 2 architectural analysis identified four operational cutover hazards that are resolved deterministically in Step 1:

1. **Plaintext Secret Exposure in CLI Arguments (`QGR033` & Process Table Leak Prevention)**:
   - **Root Cause**: Passing generated infrastructure bootstrap secrets (`JWT_SECRET_KEY`, `KMS_MASTER_KEY_ID`, `DATABASE_URL`) as command-line arguments makes them visible in host process tables and terminal transcripts.
   - **Prevention**: `provision_gcp_cloud.py` generates bootstrap secrets (`quorum-jwt-secret`, `quorum-db-url`) in memory via `secrets.token_urlsafe(48)` wrapped in `SecretStr` and pipes the bytes exclusively through `stdin` (`gcloud secrets versions add <secret_name> --data-file=-`) while never logging or printing `.get_secret_value()`.
2. **Legacy LLM Environment Variable Leakage in `docker-compose.yml` and Cloud Run Deploy Specs**:
   - **Root Cause**: `@[docker-compose.yml#L17-L51]` still contains `USE_VERTEX_LLM=true`, `VERTEX_LOCATION=europe-north1`, `GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json`, and `./service-account.json:/app/service-account.json` from the pre-SSOT container specification, and `STORAGE_BUCKET_NAME` differs between `backend` (`cognitive-quorum.firebasestorage.app`) and `worker` (`cognitive-quorum.appspot.com`).
   - **Prevention**: Step 1 cleans `@[docker-compose.yml#L1-L57]` to remove all legacy LLM environment variables and `service-account.json` volume mounts while unifying `STORAGE_BUCKET_NAME=cognitive-quorum.firebasestorage.app`, and ensures `build_stage_commands` in `scripts/provision_gcp_cloud.py` injects only pure infrastructure bootstrap settings (`ENVIRONMENT=production`, `STORAGE_BACKEND=POSTGRES`, `GCP_PROJECT`, `GCP_REGION`, `PRIMARY_DOMAIN`, `JWT_ISSUER`, `JWT_AUDIENCE`, `API_URL`, `FRONTEND_APP_BASE_URL`, `DATABASE_URL=quorum-db-url:latest`, `JWT_SECRET_KEY=quorum-jwt-secret:latest`).
3. **Premature SSL Certificate & Load Balancer Cutover Before `.ai` NS Propagation**:
   - **Root Cause**: Attaching traffic or switching `client_app_v2/.env` to `https://api.qrum.ai` before `.ai` registry `NS` records resolve to `qrum-ai-zone` causes TLS handshake failures while Google Certificate Manager is still in `PROVISIONING` state.
   - **Prevention**: `verify_dns_delegation` in `scripts/provision_gcp_cloud.py` compares the live `NS` records against the authoritative `qrum-ai-zone` nameservers and prints explicit human registrar instructions until delegation is verified.
4. **Manual `client_app_v2/.env` Editing Errors During Local-to-Cloud Switching**:
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
        - `build_stage_commands(stage: ProvisionStage, config: GCPProvisionConfigDTO) -> tuple[CommandSpecDTO, ...]`: deterministically constructs the ordered `gcloud` command specifications for `"preflight"`, `"secrets"` (`quorum-jwt-secret` and `quorum-db-url`), `"network_data"` (branching on `"pilot"` vs. `"ha"` sizing tiers), `"deploy"` (building the Artifact Registry image, executing the `quorum-seed` Cloud Run Job inside `quorum-vpc` via `--command "/app/.venv/bin/python" --args="-m,backend_v2.seed.run_seed,postgres" --execute-now --wait` so `_validate_database_preflight` passes, and then deploying `quorum-api` and `quorum-worker` via `--command "/app/.venv/bin/python" --args="-m,backend_v2.run_worker"` with pure infrastructure bootstrap settings `ENVIRONMENT=production`, `STORAGE_BACKEND=POSTGRES`, `GCP_PROJECT`, `GCP_REGION`, `PRIMARY_DOMAIN`, `JWT_ISSUER`, `JWT_AUDIENCE`, `API_URL`, `FRONTEND_APP_BASE_URL`, and Secret Manager bindings `DATABASE_URL=quorum-db-url:latest,JWT_SECRET_KEY=quorum-jwt-secret:latest`, with zero `USE_VERTEX_LLM`, `VERTEX_PROJECT_ID`, or `VERTEX_LOCATION` flags, plus a `human_checkpoint_hint` instructing the operator to provision `ROOT_SYSTEM` `org_0195f3a0000070008000000000000001` LLM and MCP secrets in PostgreSQL 19 `tenant_secrets` via `_ByokSecretsCard`), and `"dns_ssl"`.
        - `verify_dns_delegation(domain: str, expected_nameservers: Sequence[str], *, timeout_seconds: int = 15) -> DNSVerificationResultDTO`: normalizes trailing dots and case on expected and observed NS hostnames and returns `is_delegated=True` when all expected Cloud DNS nameservers are present, alongside step-by-step registrar instructions.
        - `verify_cloud_health(health_url: str, *, timeout_seconds: float = 15.0) -> HealthCheckResponseDTO`: queries `health_url` via `httpx.Client(timeout=timeout_seconds)` and validates the payload via `HealthCheckResponseDTO.model_validate_json(response.text)`, raising `ProvisioningError` if HTTP status != 200 or `status != "ok"`.
        - `switch_flutter_client_env(env_file_path: Path, *, mode: ClientEnvMode, primary_domain: str) -> Path`: updates `API_URL` (`http://127.0.0.1:8000` for `LOCAL`, `f"https://api.{primary_domain}"` for `CLOUD`) and `ENVIRONMENT` (`development` for `LOCAL`, `production` for `CLOUD`) in `client_app_v2/.env` while preserving all existing `.env` keys, raising `ProvisioningError` if `env_file_path` does not exist.
        - `execute_provision_stage(stage: ProvisionStage, config: GCPProvisionConfigDTO, *, apply: bool = False, env_file_path: Path | None = None) -> StageExecutionReportDTO`: executes `--check` (returning planned commands and interactive human instructions without mutating state) or `--apply` (running stage commands and failing fast with `ProvisioningError` on non-zero return codes).
        - `main(argv: list[str] | None = None) -> int`: CLI entrypoint supporting `--stage`, `--tier`, `--project-id`, `--region`, `--primary-domain`, `--email-mode`, `--email-endpoint`, `--client-env-mode`, `--check`, and `--apply`.
    </action>
    <action>Modify `@[docker-compose.yml#L1-L57]` to remove `USE_VERTEX_LLM=true`, `VERTEX_LOCATION=europe-north1`, `GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json`, and `- ./service-account.json:/app/service-account.json` from both `backend` and `worker` services, and set `STORAGE_BUCKET_NAME=cognitive-quorum.firebasestorage.app` consistently across both services.</action>
  </step>

  <step id="2" name="Unit &amp; ISTQB Boundary Test Suite &amp; Directory Reference Registration">
    <constraint invariant="anti_happy_path_mandate">Include at least 2 negative test cases per feature covering invalid inputs, boundary violations (min-1 / max+1), subprocess failures/timeouts, and non-200 / degraded health responses.</constraint>
    <constraint invariant="scoped_mock_and_fault_isolation_mandate">Scope all monkeypatch overrides strictly to scripts.provision_gcp_cloud without patching root stdlib modules.</constraint>
    <action>Create `[NEW] @[backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py]` testing:
      1. `GCPProvisionConfigDTO` positive defaults (`project_id="cognitive-quorum"`, `region="europe-north1"`, `primary_domain="qrum.ai"`, `tier="pilot"`) and negative `ValidationError` on trailing slash (`primary_domain="qrum.ai/"`), empty strings, `command_timeout_seconds=4` (`min-1`), `command_timeout_seconds=3601` (`max+1`), and `extra="forbid"`.
      2. `generate_secret_value` positive cryptographic token generation and negative `ValueError` on `nbytes=31` (`min-1`) and `nbytes=129` (`max+1`).
      3. `build_stage_commands` verification across `PREFLIGHT`, `SECRETS`, `NETWORK_DATA` (`"pilot"` vs. `"ha"` SQL/Redis/Cloud Run flags), `DEPLOY` (asserting presence of `quorum-seed` job execution, `GCP_PROJECT`, `GCP_REGION`, `DATABASE_URL=quorum-db-url:latest`, `JWT_SECRET_KEY=quorum-jwt-secret:latest`, and asserting complete absence of legacy `USE_VERTEX_LLM`, `VERTEX_PROJECT_ID`, and `VERTEX_LOCATION` flags in `build_stage_commands` and `@[docker-compose.yml#L1-L57]`), and `DNS_SSL`.
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
