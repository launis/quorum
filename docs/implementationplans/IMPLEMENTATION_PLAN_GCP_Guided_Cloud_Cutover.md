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

# Implementation Plan: Guided GCP Live Cloud Cutover, `qrum.ai` Domain Reservation & Provisioning Orchestrator

## 1. Objective & Architectural Background

This implementation plan is the **Stage 2 Live Cloud Cutover** companion to the completed and audited `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`, `@[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]`, `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`, and `@[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]`, governed by the master production architecture roadmap `@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md]`.

All code-level prerequisites for Cloud Run, unified database secret seeding, Resend EU transactional email formatting, Task Brief ontology normalization, and Direct Task Portal (`/task/:token`) JIT onboarding are already implemented, hardened, and audited in the repository:
- **Cloud Run & Container Runtime Readiness (`@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`, commit `fa10bdb44`):** `Settings` (`@[backend_v2/settings.py#L67-L1399]`) enforces `strip_trailing_slash`, Cloud Run port bindings (`port`, `worker_health_port`), and automatic production `cors_origins` derivation (`https://qrum.ai`, `https://app.qrum.ai`, `https://studio.qrum.ai`) inside `_enforce_environment_limits` (`@[backend_v2/settings.py#L1171-L1258]`); `GET /api/v2/system/health` returns `HealthCheckResponseDTO`; `run_worker.py` exposes the background worker health probe; and `backend_v2/Dockerfile` builds a stateless non-root (`UID 10001`) container with pre-installed WeasyPrint C libraries.
- **Unified Secret Seeding, Startup DB Telemetry/Firebase Admin Init & Zero Mock Login (`@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`, commit `80f1a3116`):** All `.env` LLM/MCP/Logfire fallbacks, physical `service-account.json` file mounts, and mock login bypasses (`allow_mock_tokens`, `MOCK_*_USER_ID`, `MockLoginPanel`) are eradicated. At container startup, `main.py` and `worker.py` resolve the optional Logfire write token from `SecretScope.TELEMETRY` (`target_identifier="logfire"`) via `resolve_startup_logfire_token` (`@[backend_v2/core/telemetry.py#L302-L323]`), and `main.py` initializes the Firebase Admin SDK in memory from the encrypted `ROOT_SYSTEM` (`org_0195f3a0000070008000000000000001`) `vertex_ai` Service Account JSON in PostgreSQL 19 `tenant_secrets` via `initialize_firebase_admin_from_secrets` (`@[backend_v2/services/auth/token_service.py#L58-L143]`). During `quorum-seed`, `LocalSeedSecretsSettings` (`@[backend_v2/seed/run_seed.py#L131-L239]`) reads `SECRET_*` bootstrap values to populate `tenant_secrets` across the 11 `CANONICAL_SEED_TABLES` before `quorum-api` boots.
- **Canonical Resend EU REST Payload, Normalized `task_brief_id` FK & Direct Task Portal Hardening (`@[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]`, commits `f50520284`–`08385c09b`):** `EmailService` (`@[backend_v2/services/auth/email_service.py#L68-L378]`) already emits the strict 5-key Resend REST schema (`from`, `to`, `subject`, `html`, `tags`) with HTML-escaped English `"Open Quorum Portal"` call-to-action links (`_compose_transactional_html`) and `QGR033` token/PII-redacted logging (`_redact_action_url` and `mask_email_address`); `001_pg19_uuidv7_schema.sql` defines `execution_assignments.task_brief_id UUID REFERENCES prompt_blocks(id) ON DELETE SET NULL` (`92/92` Python-to-Dart DTO parity); `ExecutionAssignmentService._normalize_assignee_ingress_inputs` (`@[backend_v2/services/execution/assignment_service.py#L151-L1978]`) eagerly extracts assignee `Base64Attachment` uploads in memory on both `/draft` and `/submit`; and `_verify_onboarding_firebase_token` (`@[backend_v2/services/execution/assignment_service.py#L151-L1978]`) checks `IDENTITY_MISMATCH` before bootstrapping `fb_auth.update_user(..., email_verified=True)` and enforcing mandatory TOTP 2FA (`MFA_REQUIRED`).

To guide the operator and executing agent through the transition from local Windows 11 development to live production on **Google Cloud Platform (`europe-north1` / Finland)** under **`qrum.ai`**, this plan delivers:

1. **Interactive Human-in-the-Loop Runbook for Domain Reservation, GCP Billing, Tier Sizing, Resend EU Email Activation, 3-Tier Secret Bootstrap & Firebase TOTP / Task Portal Readiness (Section 1.1 – Section 1.6)**:
   - Deterministic operator instructions for reserving `qrum.ai`, delegating registrar `NS` records to Cloud DNS (`qrum-ai-zone`), linking GCP Billing, selecting between `--tier pilot` and `--tier ha`, activating Resend EU (`eu-west-1` / Ireland) over HTTPS port `443` plus Firebase SMTP relay, seeding `ROOT_SYSTEM` `vertex_ai` into PostgreSQL 19 `tenant_secrets` with shared `JWT_SECRET_KEY` HKDF-SHA256 KEK parity so `quorum-api` passes `initialize_firebase_admin_from_secrets` on its first boot, and configuring Firebase Authentication (Email/Password, TOTP MFA, Email Enumeration Protection compatibility, `roles/firebaseauth.admin`, and `app.qrum.ai` SPA rewrites for `/task/**` and `/invite/**`).
2. **Typed 6-Stage GCP Provisioning, DNS Verification & Client Cutover CLI (`[NEW] @[scripts/provision_gcp_cloud.py]`) & Docker Compose Runtime SSOT Cleanup (`[MODIFY] @[docker-compose.yml#L1-L57]`)**:
   - A 100% Pydantic V2 (`ConfigDict(strict=True, extra="forbid", frozen=True)`) operational orchestrator built on `@[scripts/_script_base.py#L28-L51]` operating in two deterministic modes:
     - **`--check` (Safe Diagnostic & Interactive Guidance Mode)**: Inspects local and cloud readiness across any stage (`preflight`, `secrets`, `network_data`, `deploy`, `dns_ssl`, `client_env`, `all`) without mutating cloud infrastructure, and outputs exact human checkpoint instructions whenever external action is required.
     - **`--apply` (Deterministic Provisioning & Cutover Mode)**: Executes verified `gcloud` provisioning, Secret Manager bootstrap secret creation (`secrets.token_urlsafe(48)` piped via `stdin` for `quorum-jwt-secret`, `quorum-service-auth-secret`, and `quorum-db-url`, plus secret containers `quorum-vertex-sa-json` and `quorum-email-api-key`), Cloud Build image compilation, `quorum-seed` Cloud Run Job execution with `JWT_SECRET_KEY` and `SECRET_VERTEX_AI_SA_JSON` bound so `tenant_secrets` and all 15 PostgreSQL 19 UUIDv7 tables are initialized prior to service startup, `quorum-api` and `quorum-worker` deployment with zero legacy LLM/Logfire `.env` flags or comma-delimited `CORS_ORIGINS` overrides, SAN SSL Load Balancer + Resend DNS provisioning, and `client_app_v2/.env` cloud profile switching (`API_URL` and `ENVIRONMENT` in `@[client_app_v2/lib/core/environment/env.dart#L24-L47]`).
   - Cleans `@[docker-compose.yml#L1-L57]` by removing legacy `USE_VERTEX_LLM`, `VERTEX_LOCATION`, `GOOGLE_APPLICATION_CREDENTIALS`, and `./service-account.json:/app/service-account.json` mounts and unifying `STORAGE_BUCKET_NAME=cognitive-quorum.firebasestorage.app` across `backend` and `worker`.

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

### 1.2 Human Checkpoint B — Google Cloud Project (`cognitive-quorum`), Billing, Service Account IAM & `gcloud` CLI Setup

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
4. **Verify Vertex AI + Firebase Auth Admin Service Account Permissions (`quorum-vertex-firebase-sa`)**:
   - Because `initialize_firebase_admin_from_secrets` (`@[backend_v2/services/auth/token_service.py#L58-L143]`), `run_seed.py` `_provision_root_firebase_user`, and `ExecutionAssignmentService._verify_onboarding_firebase_token` (`@[backend_v2/services/execution/assignment_service.py#L151-L1978]`) initialize the Firebase Admin SDK in memory from the `ROOT_SYSTEM` `vertex_ai` Service Account JSON stored in `tenant_secrets`, that service account MUST hold **both** `roles/aiplatform.user` (Vertex AI inference & context caching) **and** `roles/firebaseauth.admin` (verifying ID tokens and setting `email_verified=True` during Direct Task Portal JIT onboarding).
5. **Verify Readiness via the Orchestrator**:
   ```powershell
   uv run python scripts/provision_gcp_cloud.py --stage preflight --check
   ```

---

### 1.3 Human Checkpoint C — Infrastructure Tier Selection (`pilot` vs. `ha`)

`[NEW] @[scripts/provision_gcp_cloud.py]` supports two explicit deployment tiers via `--tier pilot` (default for initial launch) and `--tier ha` (full enterprise high-availability):

| Resource | `--tier pilot` (Initial Launch / Low Monthly Cost) | `--tier ha` (Enterprise Production High Availability) |
| :--- | :--- | :--- |
| **Cloud SQL (PostgreSQL 19)** | `db-g1-small`, `ZONAL` availability, 10 GB SSD, automated daily backups | `db-custom-2-8192` (2 vCPU, 8 GB RAM), `REGIONAL` HA, PITR + 14 retained backups |
| **Memorystore (Redis)** | `BASIC` tier, `1 GB` capacity (`europe-north1`) | `STANDARD_HA` tier, `2 GB` capacity with automatic cross-zone failover |
| **Cloud Run (`quorum-api`)** | `min-instances=0`, `max-instances=4`, `2 GiB` RAM, `2` vCPU | `min-instances=1` (zero cold start), `max-instances=10`, `2 GiB` RAM, `2` vCPU |
| **Cloud Run (`quorum-worker`)** | `min-instances=1`, `max-instances=2`, `2 GiB` RAM, `2` vCPU | `min-instances=1`, `max-instances=5`, `4 GiB` RAM, `2` vCPU |

---

### 1.4 Human Checkpoint D — Complete Transactional & Identity Email Architecture (`CONSOLE` in Dev/Day 1 -> `HTTP_API` with Resend EU in Production)

Quorum separates outbound email communication into two distinct operational channels and two runtime transport modes (`EmailTransportMode.CONSOLE` vs. `EmailTransportMode.HTTP_API` in `@[backend_v2/settings.py#L67-L1399]`):

#### 1.4.1 As-Built Dual-Channel Email Architecture Overview (Development vs. Production)

| Email Channel | Triggering Workflows | Development & Day-1 Cloud Mode (`EMAIL_TRANSPORT_MODE=console`) | Live Production Mode (`EMAIL_TRANSPORT_MODE=http_api`) |
| :--- | :--- | :--- | :--- |
| **Channel 1: Quorum B2B Transactional Emails (`@[backend_v2/services/auth/email_service.py#L68-L378]`)** | 1. **B2B Organization Invitations (`B2B_INVITATION`)**: Single and batch organization invitations dispatched by `OrganizationService._dispatch_and_persist_invitations` (`@[backend_v2/services/auth/organization_service.py#L959-L1017]`) with action URL `{FRONTEND_APP_BASE_URL}/invite/accept?token=<raw_token>`.<br>2. **Time-Bound Task Assignments (`EXECUTION_ASSIGNMENT`)**: Single and batch (up to 50 recipients) magic-link task assignments (with optional normalized `task_brief_id` FK) dispatched by `ExecutionAssignmentService` (`@[backend_v2/services/execution/assignment_service.py#L151-L1978]`) with action URL `{FRONTEND_APP_BASE_URL}/task/<raw_token>`. | **Zero external network calls.** Appends `TransactionalEmailItemDTO` objects to `EmailService.console_outbox` for deterministic test inspection, logs token- and PII-redacted dispatch diagnostics (`_redact_action_url` replaces path tokens with `[REDACTED_TOKEN]` and strips query tokens while `mask_email_address` masks recipient addresses under `QGR033`), and marks `email_delivery_status = EmailDeliveryStatus.SENT`. | Dispatched asynchronously over HTTPS port `443` (`httpx.AsyncClient` with bounded `asyncio.timeout`) to **Resend EU (`POST https://api.resend.com/emails`)** from `no-reply@qrum.ai`. `EmailService._send_single_http_item` (`@[backend_v2/services/auth/email_service.py#L68-L378]`) emits strictly the 5 canonical Resend REST keys (`from`, `to`, `subject`, `html`, and `tags` carrying `category`, `entity_id`, and `locale`) with zero non-Resend root keys, embeds an `html.escape(raw_url, quote=True)` English `"Open Quorum Portal"` Call-to-Action button + copyable fallback URL via `_compose_transactional_html` (`@[backend_v2/services/auth/email_service.py#L68-L378]`), and isolates per-recipient HTTP `4xx`/`5xx` or transport errors (`EmailDeliveryStatus.SENT` vs. `EmailDeliveryStatus.FAILED`). |
| **Channel 2: Firebase Authentication Identity Emails** | **Password Reset & Account Recovery**: Triggered when a user clicks *"Forgot Password?"* on the login screen (`FirebaseAuth.instance.sendPasswordResetEmail`). | Handled by Google Firebase Authentication's default `.firebaseapp.com` mailer. | Routed through **Resend EU's SMTP Relay (`smtp.resend.com`, port `465` SSL/TLS)** configured in Firebase Console so password reset emails also originate from `no-reply@qrum.ai`. |

#### 1.4.2 Why Resend EU (`eu-west-1` / Ireland) Is Selected for Google Cloud Run
1. **Cloud Run Port 25 Restriction**: Google Cloud Run blocks outbound TCP port `25` and does not provide a native GCP transactional email service. Stateless containers require an HTTPS REST API on port `443`.
2. **EU/GDPR Data Residency**: Resend supports dedicated EU region hosting (`eu-west-1` in Dublin, Ireland), keeping recipient email addresses and transactional payloads strictly within European Union jurisdiction.
3. **Zero SDK Bloat & Strict Schema Compatibility**: Resend's REST API (`POST https://api.resend.com/emails`) works natively with Quorum's already-hardened `EmailService` (`httpx.AsyncClient` + `Authorization: Bearer re_...` + 5-key `from`/`to`/`subject`/`html`/`tags` payload) without adding any third-party package to `pyproject.toml` or `uv.lock`.
4. **Cost Structure**: Includes a free tier of `3,000` emails/month (`100` emails/day) for pilot deployments and scales to `50,000` emails/month on the Pro tier.

#### 1.4.3 Step-by-Step Guide: Setting Up Resend EU & `qrum.ai` DNS Records in Google Cloud DNS (`qrum-ai-zone`)
1. **Create Resend Account & Add Domain `qrum.ai` in `eu-west-1`**:
   - Sign up at `https://resend.com` -> open **Domains** -> click **Add Domain**.
   - Enter **`qrum.ai`** and select **Region: `Europe (Ireland - eu-west-1)`** -> click **Add**.
2. **Provision the 4 Email Authentication DNS Records (`DKIM`, `SPF`, `MX`, `DMARC`) in Google Cloud DNS (`qrum-ai-zone`)**:
   - Stage 5 (`dns_ssl`) automatically creates the `SPF`, `MX`, and `DMARC` record-sets in `qrum-ai-zone` and prints the human checkpoint command for your domain-specific `DKIM` public key (`resend._domainkey.qrum.ai.`). Copy the exact `p=...` TXT value shown in Resend Dashboard and run:
     ```powershell
     gcloud dns record-sets create resend._domainkey.qrum.ai. --zone="qrum-ai-zone" --type="TXT" --ttl=300 --rrdatas="\"p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC...\""
     ```
   - Return to **Resend Dashboard -> Domains -> `qrum.ai`** and click **Verify DNS Records** until status changes to **`Verified` (Green)**.
3. **Create a Scoped Sending API Key (`re_...`)**:
   - In Resend Dashboard -> **API Keys** -> **Create API Key** -> **Name**: `quorum-production-cloud-run`, **Permission**: **`Sending access`**, **Domain**: **`qrum.ai`**.

#### 1.4.4 Step-by-Step Guide: Storing `quorum-email-api-key` in GCP Secret Manager & Activating `HTTP_API` Mode on Cloud Run
1. **Store the Resend API Key in GCP Secret Manager via Stdin (Zero CLI Process Table Leak)**:
   ```powershell
   uv run python scripts/provision_gcp_cloud.py --stage secrets --apply
   $resendKey = Read-Host -Prompt "Paste Resend API Key (re_...)"
   $resendKey | gcloud secrets versions add quorum-email-api-key --data-file=-
   Remove-Variable resendKey
   ```
2. **Deploy `quorum-api` with `HTTP_API` Email Transport Enabled**:
   ```powershell
   uv run python scripts/provision_gcp_cloud.py --stage deploy --email-mode http_api --email-endpoint https://api.resend.com/emails --apply
   ```

#### 1.4.5 Step-by-Step Guide: Connecting Firebase Authentication Password Reset Emails to Resend (`smtp.resend.com`)
1. Open **Firebase Console (`https://console.firebase.google.com/project/cognitive-quorum/authentication/emails`) -> Authentication -> Templates -> SMTP Settings**.
2. Toggle **Enable custom SMTP server** to **ON** and enter: **Sender address**: `no-reply@qrum.ai`, **Sender name**: `Quorum`, **SMTP server host**: `smtp.resend.com`, **SMTP server port**: `465`, **Security mode**: `SSL/TLS`, **Username**: `resend`, **Password**: `<Resend Sending API Key re_...>`.

---

### 1.5 Human Checkpoint E — Unified 3-Tier Secret Governance (`EPIC 164` Parity), `quorum-seed` KEK/Firebase Bootstrap & Zero `service-account.json`

Under `@[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]` and `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`, Quorum enforces strict separation between **Tier 1 Infrastructure Bootstrap Secrets** and **Tier 2 / Tier 3 PostgreSQL 19 `tenant_secrets`**:

#### 1.5.1 Three-Tier Secret Governance Matrix (As-Built SSOT)

| Secret Tier | Where It Lives | How It Is Provisioned & Rotated | What It Contains (Exhaustive) |
| :--- | :--- | :--- | :--- |
| **Tier 1: Infrastructure Bootstrap Secrets** | **Local**: `.env` file.<br>**Cloud**: GCP Secret Manager (`quorum-db-url`, `quorum-jwt-secret`, `quorum-service-auth-secret`, `quorum-email-api-key`, plus seed-only `quorum-vertex-sa-json`) and Cloud Run infrastructure env vars. | Provisioned via `[NEW] @[scripts/provision_gcp_cloud.py]` (`--stage secrets --apply` & `--stage deploy --apply`). | `DATABASE_URL`, `JWT_SECRET_KEY` (signs 15-min Quorum Local JWTs AND derives the deterministic 256-bit HKDF-SHA256 Master KEK across `quorum-seed`, `quorum-api`, and `quorum-worker` when `KMS_MASTER_KEY_ID` is unset), `KMS_MASTER_KEY_ID` (optional Cloud KMS KEK URI), `SERVICE_AUTH_SECRET` (headless CLI/CI token exchange), `REDIS_HOST`, `REDIS_PORT`, `STORAGE_BACKEND=POSTGRES`, `STORAGE_BUCKET_NAME`, `GCP_PROJECT`, `GCP_REGION`, `PRIMARY_DOMAIN`, `JWT_ISSUER`, `JWT_AUDIENCE`, `API_URL`, `FRONTEND_APP_BASE_URL`, `OTEL_ENABLED`, `EMAIL_TRANSPORT_MODE`, `EMAIL_FROM_ADDRESS`, `EMAIL_API_ENDPOINT`, and `EMAIL_API_KEY`. (`LOGFIRE_TOKEN`, `USE_VERTEX_LLM`, `VERTEX_LOCATION`, `GOOGLE_APPLICATION_CREDENTIALS`, and comma-delimited `CORS_ORIGINS` are **never** passed in Cloud Run env vars.) |
| **Tier 2: Platform Baseline & Telemetry Secrets (`ROOT_SYSTEM`)** | **PostgreSQL 19 `tenant_secrets` table** under `organization_id = "org_0195f3a0000070008000000000000001"` encrypted with `SecretStorageMode.ENVELOPE_KMS` (`AES-256-GCM`). | Initial bootstrap via `LocalSeedSecretsSettings` (`@[backend_v2/seed/run_seed.py#L131-L239]`: `.env.secrets.local` locally or `SECRET_VERTEX_AI_SA_JSON=quorum-vertex-sa-json:latest` bound to the `quorum-seed` Cloud Run Job); live rotation by `UserRole.ROOT` in Flutter UI (`_ByokSecretsCard`). | 1. **`SecretScope.LLM_PROVIDER`**: `vertex_ai` (Service Account JSON powering **both** Vertex AI inference and startup in-memory `initialize_firebase_admin_from_secrets`), `ai_studio`, `openai`, `anthropic`, `azure_openai`, `local`.<br>2. **`SecretScope.MCP_GATEWAY`**: `sys_0195f3a00000700080008172bda70c86` (Tavily MCP Gateway).<br>3. **`SecretScope.TELEMETRY`** (`ROOT`-only): `"logfire"` (resolved at startup in `main.py` and `worker.py` via `resolve_startup_logfire_token`) and `"logfire_read"`. |
| **Tier 3: Customer Tenant BYOK Secrets (`org_<hex32>`)** | **PostgreSQL 19 `tenant_secrets` table** under the customer organization's `organization_id` encrypted with `SecretStorageMode.ENVELOPE_KMS` (`AES-256-GCM`). | Customer Organization `ADMIN` (or platform `ROOT`) via self-service Flutter UI (**Settings -> Organization & IAM -> BYOK & MCP Secrets**). | Customer-owned `SecretScope.LLM_PROVIDER` keys (`openai`, `anthropic`, `ai_studio`, `azure_openai`, `local`, or customer `vertex_ai` Service Account JSON) and `SecretScope.MCP_GATEWAY` keys (`sys_<hex32>`). |

#### 1.5.2 Solving the Cloud Run First-Boot Firebase Admin & KEK Bootstrap Requirement
When `quorum-api` starts in Cloud Run (`use_firebase_auth = True`), `lifespan` immediately executes `initialize_firebase_admin_from_secrets` (`@[backend_v2/services/auth/token_service.py#L58-L143]`), which decrypts the `ROOT_SYSTEM` `vertex_ai` row from `tenant_secrets`. To prevent a chicken-and-egg startup `ConfigurationError` (`ErrorCodes.SECRET_RESOLUTION_FAILED`) or AES-256-GCM KEK mismatch:
1. Before running Stage 4 (`deploy`), pipe the `cognitive-quorum` Vertex AI + Firebase Auth Admin Service Account JSON into `quorum-vertex-sa-json` via PowerShell `stdin`:
   ```powershell
   Get-Content -Raw .\path\to\vertex-firebase-sa.json | gcloud secrets versions add quorum-vertex-sa-json --data-file=-
   ```
2. During Stage 4 (`deploy`), `quorum-seed` (`backend_v2.seed.run_seed postgres`) runs **first** with `--set-secrets="DATABASE_URL=quorum-db-url:latest,JWT_SECRET_KEY=quorum-jwt-secret:latest,SECRET_VERTEX_AI_SA_JSON=quorum-vertex-sa-json:latest"`. Because `quorum-seed` receives the exact same `JWT_SECRET_KEY` secret as `quorum-api` and `quorum-worker`, `SecretService` encrypts `vertex_ai` into `tenant_secrets` under the identical HKDF-SHA256 Master KEK!
3. When `quorum-api` and `quorum-worker` subsequently start (without `SECRET_VERTEX_AI_SA_JSON` or any `service-account.json` file mounted), `quorum-api` decrypts `vertex_ai` from PostgreSQL 19 in `< 1 ms`, initializes Firebase Admin SDK in memory, and serves `/api/v2/system/health` (`200 OK`). All additional LLM (`ai_studio`, `openai`, `anthropic`), MCP (`sys_0195f3a00000700080008172bda70c86`), and Telemetry (`logfire`) secrets can then be added or rotated at any time via `_ByokSecretsCard` in `https://app.qrum.ai`.

---

### 1.6 Human Checkpoint F — Firebase Authentication, Mandatory TOTP 2FA, Email Enumeration Protection & Direct Task Portal (`/task/:token`) Cloud Readiness

Learnings from `@[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]` require verifying four Firebase Console and Web Hosting invariants before opening live B2B invitations and Direct Task Portal cohorts:

1. **Enable Email/Password & Multi-Factor Authentication (TOTP) in Firebase Console / Identity Platform**:
   - In **Firebase Console -> Authentication -> Sign-in method**, enable **Email/Password**.
   - Upgrade/enable **Identity Platform Multi-Factor Authentication** and set **TOTP (Time-based One-Time Password)** to **Enabled** (`Settings.require_mfa` defaults to `True` in `@[backend_v2/settings.py#L67-L1399]`).
   - Under **Authentication -> Settings -> Authorized domains**, add `qrum.ai`, `app.qrum.ai`, `studio.qrum.ai`, and `api.qrum.ai`.
2. **Firebase Email Enumeration Protection & Pre-MFA `email_verified=True` Portal Handshake (`Finding A`)**:
   - GCP Identity Platform enables **Email Enumeration Protection** by default, returning `'invalid-credential'` instead of `'user-not-found'` on `signInWithEmailAndPassword` for first-time external assignees. `AuthRepository.authenticateForTaskOnboarding` handles both `'user-not-found'` and `'invalid-credential'` by falling back to `createUserWithEmailAndPassword` (mapping `'email-already-in-use'` to `AUTHENTICATION_FAILED`).
   - On `POST /api/v2/execution/assignments/token/onboard`, `ExecutionAssignmentService._verify_onboarding_firebase_token` (`@[backend_v2/services/execution/assignment_service.py#L151-L1978]`) verifies `IDENTITY_MISMATCH` (`token_email == expected_email.lower()`) **first**, then calls `fb_auth.update_user(uid_str, email_verified=True)` via the in-memory Firebase Admin SDK (`roles/firebaseauth.admin`), and then enforces `_enforce_firebase_mfa_claim`. This unblocks client-side `multiFactor.getSession()` (`reloadUser: true`) so external assignees enroll their authenticator app (`task_portal_totp_secret_text`) directly inside `TaskAssignmentPortalView` without leaving `/task/:token`.
3. **Flutter Web Hosting SPA Deep-Link Rewrites (`app.qrum.ai`)**:
   - `FRONTEND_APP_BASE_URL=https://app.qrum.ai` generates magic links `{FRONTEND_APP_BASE_URL}/invite/accept?token=<raw_token>` and `{FRONTEND_APP_BASE_URL}/task/<raw_token>`. When deploying `client_app_v2/build/web` to Firebase Hosting (`app.qrum.ai`), ensure `firebase.json` configures the SPA rewrite rule (`"rewrites": [{"source": "**", "destination": "/index.html"}]`) so `/task/*` and `/invite/*` deep links route directly into `GoRouter` without HTTP 404 responses.
4. **Normalized `task_brief_id` Schema & Stateless Eager Portal File Uploads (`Findings D & E`)**:
   - `quorum-seed` automatically applies `001_pg19_uuidv7_schema.sql`, provisioning `execution_assignments.task_brief_id UUID REFERENCES prompt_blocks(id) ON DELETE SET NULL` (`ZORM004`/`ZORM006`/`ZORM007`) for `ADMIN`/`ROOT` Task Brief `CRUD + Clone` (`_TaskBriefsManagementCard`) and `TaskAssignmentConfigDialog` CSV cohort summaries.
   - Assignee `.pdf`, `.docx`, and `.txt` uploads in `TaskAssignmentPortalView` (`WorkflowInputValue.file`) are eagerly extracted into plain text in memory by `ExecutionAssignmentService._normalize_assignee_ingress_inputs` (`@[backend_v2/services/execution/assignment_service.py#L151-L1978]`) on both `PUT .../draft` and `POST .../submit` (`base64_amnesia_protocol`), operating statelessly within Cloud Run's `32 MB` HTTP/1.1 request limit with zero raw Base64 persisted in PostgreSQL 19.

---

## 2. Scope & Target Boundaries (5-Column Directives Table)

### Context Files (Read-Only)
- `@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md]`
- `@[docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md]`
- `@[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]`
- `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`
- `@[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]`
- `@[scripts/_script_base.py#L28-L51]`
- `@[backend_v2/settings.py#L67-L1399]`
- `@[backend_v2/core/telemetry.py#L302-L323]`
- `@[backend_v2/seed/run_seed.py#L661-L738]`
- `@[backend_v2/services/auth/token_service.py#L58-L143]`
- `@[backend_v2/services/auth/email_service.py#L68-L378]`
- `@[backend_v2/services/auth/organization_service.py#L959-L1017]`
- `@[backend_v2/services/execution/assignment_service.py#L1197-L1272]`
- `@[backend_v2/services/execution/assignment_service.py#L1879-L1917]`
- `@[client_app_v2/lib/core/environment/env.dart#L24-L47]`

### Target Files (`[NEW]`, `[MODIFY]`)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`[NEW] @[scripts/provision_gcp_cloud.py]` (`ProvisionStage`, `DeploymentTier`, `ClientEnvMode`, `GCPProvisionConfigDTO`, `CommandSpecDTO`, `CommandExecutionResultDTO`, `DNSVerificationResultDTO`, `StageExecutionReportDTO`, `ProvisioningError`, `generate_secret_value`, `run_subprocess_command`, `build_stage_commands`, `verify_dns_delegation`, `verify_cloud_health`, `switch_flutter_client_env`, `execute_provision_stage`, `main`)** | Running unvalidated ad-hoc shell one-liners without preflight verification, running `quorum-seed` without `JWT_SECRET_KEY` and `SECRET_VERTEX_AI_SA_JSON` (causing `quorum-api` `initialize_firebase_admin_from_secrets` startup failure or AES-GCM KEK mismatch), injecting eradicated `.env` flags (`USE_VERTEX_LLM`, `VERTEX_PROJECT_ID`, `VERTEX_LOCATION`, `LOGFIRE_TOKEN`, `GOOGLE_APPLICATION_CREDENTIALS`) or comma-delimited `CORS_ORIGINS` into Cloud Run services, using naked dicts (`QGR005`), calling `json.loads` (`QGR011`) or `os.environ.get` (`QGR016`), logging raw secret tokens (`QGR033`), or executing unbounded `subprocess.run` calls without explicit timeouts. | Build a 100% typed Pydantic V2 CLI orchestrator (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with PEP 593 `Annotated` fields, `ProvisionStage(StrEnum)` (`preflight`, `secrets`, `network_data`, `deploy`, `dns_ssl`, `client_env`, `all`), `DeploymentTier(StrEnum)` (`pilot`, `ha`), bounded `subprocess.run(..., timeout=config.command_timeout_seconds)`, `SecretStr` stdin secret provisioning (`quorum-jwt-secret`, `quorum-service-auth-secret`, `quorum-db-url`, plus secret containers `quorum-vertex-sa-json` and `quorum-email-api-key`), `quorum-seed` Cloud Run Job binding `DATABASE_URL=quorum-db-url:latest,JWT_SECRET_KEY=quorum-jwt-secret:latest,SECRET_VERTEX_AI_SA_JSON=quorum-vertex-sa-json:latest`, Cloud Run `quorum-api` and `quorum-worker` deployment injecting pure Tier 1 infrastructure settings (`OTEL_ENABLED=true`, `FRONTEND_APP_BASE_URL=https://app.{domain}`, conditional Resend EU `HTTP_API` bindings, and `SERVICE_AUTH_SECRET=quorum-service-auth-secret:latest`), Cloud DNS + Resend EU `SPF`/`MX`/`DMARC` record-sets + SAN SSL, `HealthCheckResponseDTO` verification, and deterministic `client_app_v2/.env` switching (`API_URL` and `ENVIRONMENT`). | Prune external Terraform/Pulumi state-locking dependencies and third-party cloud SDK wrappers; encapsulate Google Cloud's native idempotent `gcloud` CLI commands in pure, deterministically testable Python functions supporting `--check` and `--apply`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/provision_gcp_cloud.py backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py --test --ast-strict` |
| **`[MODIFY] @[docker-compose.yml#L1-L57]`** | Passing eradicated legacy LLM environment variables (`USE_VERTEX_LLM=true`, `VERTEX_LOCATION=europe-north1`, `GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json`), mounting `./service-account.json:/app/service-account.json` into containers after `EPIC 164` moved Vertex AI and Firebase Admin credentials into PostgreSQL 19 `tenant_secrets`, or declaring inconsistent `STORAGE_BUCKET_NAME` values between `backend` and `worker`. | Remove `USE_VERTEX_LLM`, `VERTEX_LOCATION`, `GOOGLE_APPLICATION_CREDENTIALS`, and `./service-account.json:/app/service-account.json` from both `backend` and `worker` services in `@[docker-compose.yml#L1-L57]`, and unify `STORAGE_BUCKET_NAME=cognitive-quorum.firebasestorage.app` across both services. | Prune redundant container environment overrides; let PostgreSQL 19 `system_configs` and `tenant_secrets` govern all LLM, MCP, telemetry, and Firebase Admin credentials. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/provision_gcp_cloud.py backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py --test --ast-strict` |
| **`[NEW] @[backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py]`** | Writing happy-path-only tests, referencing eradicated `MOCK_ADMIN_USER_ID` variables, or executing live network/`gcloud` subprocess calls during unit test execution (`mocking_mandate_for_llm`, `scoped_mock_and_fault_isolation_mandate`). | Write comprehensive unit tests and >=2 ISTQB negative boundary tests per stage scoping `monkeypatch` strictly to `scripts.provision_gcp_cloud`, verifying `GCPProvisionConfigDTO` validation, `pilot` vs. `ha` and `email_mode` (`console` vs. `http_api`) command synthesis, `quorum-seed` shared `JWT_SECRET_KEY` + `SECRET_VERTEX_AI_SA_JSON` bindings, absence of `SECRET_*`/`LOGFIRE_TOKEN`/`CORS_ORIGINS`/`USE_VERTEX_LLM`/`VERTEX_PROJECT_ID`/`VERTEX_LOCATION`/`GOOGLE_APPLICATION_CREDENTIALS` on `quorum-api` and `quorum-worker` and in `@[docker-compose.yml#L1-L57]`, `SecretStr` redaction, DNS NS verification, `HealthCheckResponseDTO` validation, `client_app_v2/.env` roundtrip updates preserving custom keys, and `ProvisioningError` translation. | Prune live GCP API calls in unit tests; verify command construction, timeout enforcement, and error translation deterministically in memory and `tmp_path`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/provision_gcp_cloud.py backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py --test --ast-strict` |
| **`[MODIFY] @[.agents/rules/04_directory_reference.md#L25-L121]`** | Leaving new operational scripts or their companion unit tests undocumented in the repository directory index. | Register `scripts/test_provision_gcp_cloud.py` under `test_directory_isolation` (`@[.agents/rules/04_directory_reference.md#L25-L29]`) and `provision_gcp_cloud.py` under `<module path="scripts/">` (`@[.agents/rules/04_directory_reference.md#L118-L121]`). | Prune verbose prose in `04_directory_reference.md`; add concise single-clause index entries matching existing script entries. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md` |

---

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

Pre-flight execution of `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets scripts/_script_base.py --include-one-hop` scanned `@[scripts/_script_base.py#L28-L51]` with **0 AST technical debt findings**. In addition, `@[backend_v2/services/auth/email_service.py#L68-L378]` was already refactored, hardened (`100%` line coverage), and Tier 8 audited in `@[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]` (`f50520284`–`a6bd5a7b5`), requiring zero further modifications to `EmailService`. System 2 architectural analysis identified five operational cutover hazards resolved deterministically in Step 1:

1. **Legacy LLM & `service-account.json` Leakage in `docker-compose.yml` (`EPIC 164` Drift Cleanup)**:
   - **Root Cause**: `@[docker-compose.yml#L1-L57]` still contains `USE_VERTEX_LLM=true`, `VERTEX_LOCATION=europe-north1`, `GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json`, and `./service-account.json:/app/service-account.json` from the pre-`EPIC 164` container specification, and `STORAGE_BUCKET_NAME` differs between `backend` (`cognitive-quorum.firebasestorage.app`) and `worker` (`cognitive-quorum.appspot.com`).
   - **Prevention**: Step 1 cleans `@[docker-compose.yml#L1-L57]` to remove all legacy LLM environment variables and `service-account.json` volume mounts while unifying `STORAGE_BUCKET_NAME=cognitive-quorum.firebasestorage.app` across both services.
2. **Cloud Run First-Boot `initialize_firebase_admin_from_secrets` & HKDF-SHA256 KEK Parity**:
   - **Root Cause**: `quorum-api` invokes `initialize_firebase_admin_from_secrets` (`@[backend_v2/services/auth/token_service.py#L58-L143]`) during `lifespan` startup, requiring a valid encrypted `vertex_ai` Service Account JSON row in `ROOT_SYSTEM` `tenant_secrets`. If `quorum-seed` runs without `SECRET_VERTEX_AI_SA_JSON` or without the shared `JWT_SECRET_KEY` KEK (`quorum-jwt-secret:latest`), `quorum-api` fails on boot with `ConfigurationError` (`ErrorCodes.SECRET_RESOLUTION_FAILED` or AES-GCM decryption failure).
   - **Prevention**: `build_stage_commands` in `[NEW] @[scripts/provision_gcp_cloud.py]` creates `quorum-vertex-sa-json` in Stage 2 (`secrets`) and binds `--set-secrets="DATABASE_URL=quorum-db-url:latest,JWT_SECRET_KEY=quorum-jwt-secret:latest,SECRET_VERTEX_AI_SA_JSON=quorum-vertex-sa-json:latest"` onto the `quorum-seed` Cloud Run Job in Stage 4 (`deploy`) while keeping `SECRET_VERTEX_AI_SA_JSON` completely absent from `quorum-api` and `quorum-worker`.
3. **Plaintext Secret Exposure in CLI Arguments (`QGR033` & Process Table Leak Prevention)**:
   - **Root Cause**: Passing generated infrastructure bootstrap secrets (`JWT_SECRET_KEY`, `SERVICE_AUTH_SECRET`, `DATABASE_URL`, `EMAIL_API_KEY`, `SECRET_VERTEX_AI_SA_JSON`) as CLI flags exposes them in host process tables and terminal logs.
   - **Prevention**: `[NEW] @[scripts/provision_gcp_cloud.py]` generates bootstrap secrets (`quorum-jwt-secret`, `quorum-service-auth-secret`, `quorum-db-url`) in memory via `secrets.token_urlsafe(48)` wrapped in `SecretStr` and pipes secret bytes exclusively through `stdin` (`gcloud secrets versions add <secret_name> --data-file=-`) while never logging `.get_secret_value()`.
4. **Cloud Run `CORS_ORIGINS` List-Parsing Hazard & Premature SSL Cutover**:
   - **Root Cause**: Passing comma-delimited `CORS_ORIGINS` via `gcloud run deploy --set-env-vars` breaks `pydantic-settings` JSON list parsing on `list[str]`, while switching `client_app_v2/.env` before `.ai` `NS` delegation completes triggers TLS handshake errors.
   - **Prevention**: `build_stage_commands` omits `CORS_ORIGINS` so `Settings._enforce_environment_limits` (`@[backend_v2/settings.py#L1171-L1258]`) deterministically derives `["https://qrum.ai", "https://app.qrum.ai", "https://studio.qrum.ai"]` from `ENVIRONMENT=production` and `PRIMARY_DOMAIN=qrum.ai`, and `verify_dns_delegation` gates DNS cutover with explicit registrar instructions.
5. **Deterministic `client_app_v2/.env` Switching (`Env` Fail-Fast Contract)**:
   - **Root Cause**: `@[client_app_v2/lib/core/environment/env.dart#L24-L47]` enforces Fail-Fast presence of `API_URL` and `ENVIRONMENT` with zero trailing slashes.
   - **Prevention**: `switch_flutter_client_env` deterministically updates `API_URL` and `ENVIRONMENT` (`http://127.0.0.1:8000` + `development` in `"local"` mode vs. `https://api.qrum.ai` + `production` in `"cloud"` mode) while preserving all comments and additional keys in `client_app_v2/.env`.

---

## 4. Detailed Execution Protocol (Hybrid XML Sandwich)

```xml
<execution_protocol>
  <step id="1" name="Phase 1: Clean Docker Compose Runtime SSOT &amp; Implement Typed 6-Stage GCP Provisioning CLI (docker-compose.yml &amp; scripts/provision_gcp_cloud.py)">
    <Requires>None</Requires>
    <Produces>Cleaned docker-compose.yml free of legacy LLM and service-account.json bindings plus typed 6-stage GCP provisioning and cutover orchestrator in scripts/provision_gcp_cloud.py</Produces>
    <constraint invariant="strict_pydantic_v2_rust">All configuration, command specs, DNS verification results, and stage execution reports MUST use immutable Pydantic V2 models with ConfigDict(strict=True, extra="forbid", frozen=True) and PEP 593 Annotated fields. Naked dictionaries (QGR005), json.loads (QGR011), getattr/hasattr (QGR001), and .get() (QGR002) are strictly forbidden.</constraint>
    <constraint invariant="credential_hardcoding_ban">Never hardcode or log secret values (QGR033). Generate secrets via stdlib secrets.token_urlsafe(48), store in SecretStr, and pass to gcloud secrets versions add --data-file=- exclusively via subprocess stdin.</constraint>
    <constraint invariant="unbounded_io_timeout_mandate">Every subprocess.run and httpx.Client invocation MUST specify an explicit timeout resolved from GCPProvisionConfigDTO (command_timeout_seconds and http_timeout_seconds).</constraint>
    <constraint invariant="universal_ssot_and_normalization_mandate">Bind JWT_SECRET_KEY=quorum-jwt-secret:latest and SECRET_VERTEX_AI_SA_JSON=quorum-vertex-sa-json:latest to the quorum-seed Cloud Run Job so PostgreSQL 19 tenant_secrets is seeded with identical HKDF-SHA256 KEK parity before quorum-api starts, and never inject SECRET_*, LOGFIRE_TOKEN, CORS_ORIGINS, USE_VERTEX_LLM, VERTEX_PROJECT_ID, VERTEX_LOCATION, or GOOGLE_APPLICATION_CREDENTIALS into quorum-api or quorum-worker.</constraint>
    <touched_artifacts>
      <artifact action="[NEW]" path="@[scripts/provision_gcp_cloud.py]" />
      <artifact action="MODIFY" path="@[docker-compose.yml#L1-L57]" />
    </touched_artifacts>
    <action>
      1. Modify `@[docker-compose.yml#L1-L57]` to remove `USE_VERTEX_LLM=true`, `VERTEX_LOCATION=europe-north1`, `GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json`, and `- ./service-account.json:/app/service-account.json` from both `backend` and `worker` services, and set `STORAGE_BUCKET_NAME=cognitive-quorum.firebasestorage.app` consistently across both `backend` and `worker`.
      2. Create `[NEW] @[scripts/provision_gcp_cloud.py]` importing `setup_script_environment`, `ANSIColors`, and `get_repo_root` from `scripts._script_base` and `HealthCheckResponseDTO` from `backend_v2.models.dtos.system` (with `setup_script_environment()` invoked prior to `backend_v2` imports), and defining (all exported in `__all__`):
         - `ProvisionStage(StrEnum)` with members: `PREFLIGHT = "preflight"`, `SECRETS = "secrets"`, `NETWORK_DATA = "network_data"`, `DEPLOY = "deploy"`, `DNS_SSL = "dns_ssl"`, `CLIENT_ENV = "client_env"`, `ALL = "all"`.
         - `DeploymentTier(StrEnum)` with members: `PILOT = "pilot"`, `HA = "ha"`.
         - `ClientEnvMode(StrEnum)` with members: `LOCAL = "local"`, `CLOUD = "cloud"`.
         - `ProvisioningError(Exception)` carrying `stage: ProvisionStage`, `message: str`, and `remediation: str`.
         - `GCPProvisionConfigDTO(BaseModel)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with PEP 593 `Annotated` fields (`QGR020` Check 20B/20C compliant — either mandatory keyword fields or optional `T | None = None` / `default_factory` where required by `QGR020`):
           - Verify `QGR020` compliance on every `BaseModel` field in `[NEW] @[scripts/provision_gcp_cloud.py]`! Remember `QGR020` Check 20C forbids non-`None` scalar defaults on `BaseModel` fields outside `Settings`: resolve CLI defaults in `argparse` (`main`) and construct `GCPProvisionConfigDTO` explicitly with validated keyword arguments (`project_id: Annotated[str, Field(min_length=1, description="Target Google Cloud project ID")]`, `region: Annotated[str, Field(min_length=1, description="Target Google Cloud deployment region")]`, `primary_domain: Annotated[str, Field(min_length=3, description="Primary production domain")]`, `tier: Annotated[DeploymentTier, Field(description="Infrastructure sizing tier")]`, `email_mode: Annotated[Literal["console", "http_api"], Field(description="Transactional email transport mode")]`, `email_endpoint: Annotated[str, Field(min_length=8, description="HTTPS transactional email endpoint")]`, `client_env_mode: Annotated[ClientEnvMode, Field(description="Target mode for client_app_v2/.env")]`, `command_timeout_seconds: Annotated[int, Field(ge=5, le=3600, description="Bounded timeout in seconds for gcloud subprocess execution")]`, `http_timeout_seconds: Annotated[float, Field(ge=1.0, le=120.0, description="Bounded timeout in seconds for health probe HTTP verification")]`), plus `@field_validator("primary_domain", "email_endpoint")` rejecting trailing slashes (`"/"`) or whitespace-only values with `ValueError`.
         - `CommandSpecDTO(BaseModel)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with PEP 593 `Annotated` fields: `description: str`, `args: tuple[str, ...]`, and `human_checkpoint_hint: str | None = None`.
         - `CommandExecutionResultDTO(BaseModel)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with PEP 593 `Annotated` fields: `command: tuple[str, ...]`, `return_code: int`, `stdout: str`, `stderr: str`.
         - `DNSVerificationResultDTO(BaseModel)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with PEP 593 `Annotated` fields: `domain: str`, `expected_nameservers: tuple[str, ...]`, `observed_nameservers: tuple[str, ...]`, `is_delegated: bool`, and `registrar_instructions: str`.
         - `StageExecutionReportDTO(BaseModel)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with PEP 593 `Annotated` fields: `stage: ProvisionStage`, `mode: Literal["check", "apply"]`, `succeeded: bool`, `executed_commands: tuple[str, ...]`, and `human_actions_required: tuple[str, ...]`.
         - Pure helper and execution functions:
           - `generate_secret_value(nbytes: int = 48) -> SecretStr`: validates `32 &lt;= nbytes &lt;= 128` and returns `SecretStr(secrets.token_urlsafe(nbytes))`.
           - `run_subprocess_command(args: Sequence[str], *, timeout_seconds: int, stage: ProvisionStage = ProvisionStage.PREFLIGHT, stdin_secret: SecretStr | None = None) -&gt; CommandExecutionResultDTO`: executes `subprocess.run` with `timeout=timeout_seconds`, passing `stdin_secret.get_secret_value()` exclusively via `input=` when provided, and raising `ProvisioningError` on `subprocess.TimeoutExpired` or `OSError`.
           - `build_stage_commands(stage: ProvisionStage, config: GCPProvisionConfigDTO) -&gt; tuple[CommandSpecDTO, ...]`: deterministically constructs ordered `gcloud` command specifications:
             - `PREFLIGHT`: verifying active `gcloud` project, active billing link, and enabling required GCP APIs (`run.googleapis.com`, `sqladmin.googleapis.com`, `redis.googleapis.com`, `secretmanager.googleapis.com`, `artifactregistry.googleapis.com`, `cloudbuild.googleapis.com`, `compute.googleapis.com`, `dns.googleapis.com`, `certificatemanager.googleapis.com`, `vpcaccess.googleapis.com`, `aiplatform.googleapis.com`, `identitytoolkit.googleapis.com`).
             - `SECRETS`: creating `quorum-jwt-secret`, `quorum-service-auth-secret`, `quorum-db-url`, `quorum-vertex-sa-json`, and `quorum-email-api-key` in GCP Secret Manager (`--replication-policy="automatic"`), with `human_checkpoint_hint` instructions for piping the Vertex AI + Firebase Auth Admin (`roles/aiplatform.user` + `roles/firebaseauth.admin`) Service Account JSON into `quorum-vertex-sa-json` and the Resend EU `re_...` key into `quorum-email-api-key` via `stdin`.
             - `NETWORK_DATA`: creating `quorum-vpc`, Serverless VPC Access connector `quorum-vpc-connector`, Cloud SQL PostgreSQL 19 instance `quorum-pg19` (`db-g1-small` + `ZONAL` for `PILOT` vs. `db-custom-2-8192` + `REGIONAL` for `HA`, private IP only `--no-assign-ip`), and Memorystore Redis `quorum-redis` (`BASIC` `1` GB for `PILOT` vs. `STANDARD_HA` `2` GB for `HA`).
             - `DEPLOY`: building Artifact Registry image `{config.region}-docker.pkg.dev/{config.project_id}/quorum/quorum-backend:latest`; executing the `quorum-seed` Cloud Run Job inside `quorum-vpc` via `--command "/app/.venv/bin/python" --args="-m,backend_v2.seed.run_seed,postgres" --set-env-vars="STORAGE_BACKEND=POSTGRES,GCP_PROJECT={config.project_id},GCP_REGION={config.region}" --set-secrets="DATABASE_URL=quorum-db-url:latest,JWT_SECRET_KEY=quorum-jwt-secret:latest,SECRET_VERTEX_AI_SA_JSON=quorum-vertex-sa-json:latest" --execute-now --wait`; and deploying `quorum-api` and `quorum-worker` (`--command "/app/.venv/bin/python" --args="-m,backend_v2.run_worker"`) sized per `config.tier` with pure Tier 1 infrastructure settings `ENVIRONMENT=production`, `STORAGE_BACKEND=POSTGRES`, `STORAGE_BUCKET_NAME={config.project_id}.firebasestorage.app`, `GCP_PROJECT={config.project_id}`, `GCP_REGION={config.region}`, `PRIMARY_DOMAIN={config.primary_domain}`, `JWT_ISSUER=https://api.{config.primary_domain}`, `JWT_AUDIENCE=https://{config.primary_domain}`, `API_URL=https://api.{config.primary_domain}`, `FRONTEND_APP_BASE_URL=https://app.{config.primary_domain}`, `OTEL_ENABLED=true`, `EMAIL_TRANSPORT_MODE={config.email_mode}`, `EMAIL_FROM_ADDRESS=no-reply@{config.primary_domain}`, conditional `EMAIL_API_ENDPOINT={config.email_endpoint}` when `config.email_mode == "http_api"`, and `--set-secrets` binding `DATABASE_URL=quorum-db-url:latest,JWT_SECRET_KEY=quorum-jwt-secret:latest,SERVICE_AUTH_SECRET=quorum-service-auth-secret:latest` (plus `,EMAIL_API_KEY=quorum-email-api-key:latest` when `config.email_mode == "http_api"`), with zero `CORS_ORIGINS`, `LOGFIRE_TOKEN`, `SECRET_*`, `USE_VERTEX_LLM`, `VERTEX_PROJECT_ID`, `VERTEX_LOCATION`, or `GOOGLE_APPLICATION_CREDENTIALS` flags, accompanied by `human_checkpoint_hint` reminders for `_ByokSecretsCard` (`ai_studio`, `openai`, `anthropic`, `sys_0195f3a00000700080008172bda70c86`, `logfire`) and Firebase Console TOTP + `/task/**` &amp; `/invite/**` SPA rewrites.
             - `DNS_SSL`: creating `qrum-ai-zone` in Cloud DNS, provisioning SAN SSL certificate `qrum-san-cert` (`{domain}`, `api.{domain}`, `app.{domain}`, `studio.{domain}`), and creating Resend EU DNS record-sets (`send.{config.primary_domain}.` `TXT` SPF `"v=spf1 include:amazonses.com ~all"`, `send.{config.primary_domain}.` `MX` `10 feedback-smtp.eu-west-1.amazonses.com.`, and `_dmarc.{config.primary_domain}.` `TXT` `"v=DMARC1; p=quarantine; pct=100; adkim=s; aspf=s;"`) alongside a `human_checkpoint_hint` for `resend._domainkey.{config.primary_domain}.` DKIM TXT and registrar `NS` delegation.
           - `verify_dns_delegation(domain: str, expected_nameservers: Sequence[str], *, timeout_seconds: int = 15) -&gt; DNSVerificationResultDTO`: normalizes trailing dots and case on expected and observed NS hostnames and returns `is_delegated=True` when all expected Cloud DNS nameservers are present, alongside step-by-step registrar instructions.
           - `verify_cloud_health(health_url: str, *, timeout_seconds: float = 15.0) -&gt; HealthCheckResponseDTO`: queries `health_url` via `httpx.Client(timeout=timeout_seconds)` and validates the payload via `HealthCheckResponseDTO.model_validate_json(response.text)`, raising `ProvisioningError` if HTTP status != 200 or `status != "ok"`.
           - `switch_flutter_client_env(env_file_path: Path, *, mode: ClientEnvMode, primary_domain: str) -&gt; Path`: updates `API_URL` (`http://127.0.0.1:8000` for `LOCAL`, `f"https://api.{primary_domain}"` for `CLOUD`) and `ENVIRONMENT` (`development` for `LOCAL`, `production` for `CLOUD`) in `client_app_v2/.env` while preserving comments and all other `.env` keys, raising `ProvisioningError` if `env_file_path` does not exist.
           - `execute_provision_stage(stage: ProvisionStage, config: GCPProvisionConfigDTO, *, apply: bool = False, env_file_path: Path | None = None) -&gt; StageExecutionReportDTO`: executes `--check` (returning planned commands and interactive human instructions without mutating cloud state) or `--apply` (executing stage commands or `switch_flutter_client_env` and failing fast with `ProvisioningError` on non-zero return codes).
           - `main(argv: Sequence[str] | None = None) -&gt; int`: CLI entrypoint providing defaults (`--stage all`, `--tier pilot`, `--project-id cognitive-quorum`, `--region europe-north1`, `--primary-domain qrum.ai`, `--email-mode console`, `--email-endpoint https://api.resend.com/emails`, `--client-env-mode cloud`, `--command-timeout-seconds 600`, `--http-timeout-seconds 15.0`, `--check` / `--apply`).
    </action>
    <test_contracts>
      - Positive: `build_stage_commands` synthesizes deterministic `gcloud` commands for all stages (`PILOT` and `HA`, `console` and `http_api`), binding `JWT_SECRET_KEY` and `SECRET_VERTEX_AI_SA_JSON` to `quorum-seed` and omitting all eradicated LLM/Logfire/CORS flags from `quorum-api`, `quorum-worker`, and `docker-compose.yml`.
      - Negative 1: Trailing slashes on `primary_domain` or `email_endpoint` or unrecognized extra fields on `GCPProvisionConfigDTO` raise `ValidationError`.
      - Negative 2: `subprocess.TimeoutExpired` or non-zero `gcloud` exit status in `--apply` mode raises `ProvisioningError`.
    </test_contracts>
    <validation_gate>
      $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/provision_gcp_cloud.py --ast-strict
    </validation_gate>
  </step>

  <step id="2" name="Phase 2: Unit &amp; ISTQB Boundary Test Suite &amp; Directory Reference Registration (test_provision_gcp_cloud.py &amp; 04_directory_reference.md)">
    <Requires>Step 1</Requires>
    <Produces>Hermetic unit and ISTQB boundary test suite (>90% line coverage) in backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py and updated directory index in .agents/rules/04_directory_reference.md</Produces>
    <constraint invariant="anti_happy_path_mandate">Include at least 2 negative test cases per feature covering invalid inputs, boundary violations (min-1 / max+1), subprocess failures/timeouts, and non-200 / degraded health responses.</constraint>
    <constraint invariant="scoped_mock_and_fault_isolation_mandate">Scope all monkeypatch overrides strictly to scripts.provision_gcp_cloud without patching root stdlib modules.</constraint>
    <constraint invariant="localhost_endpoint_hardcoding_ban">Avoid hardcoded http://127.0.0.1:8000 or http://localhost:8000 literals inside backend_v2/tests/ if flagged by AST guardrails, or construct local loopback strings from Settings / parameterized host constants compliant with _ast_guardrails.py.</constraint>
    <touched_artifacts>
      <artifact action="[NEW]" path="@[backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py]" />
      <artifact action="MODIFY" path="@[.agents/rules/04_directory_reference.md#L25-L121]" />
    </touched_artifacts>
    <action>
      1. Create `[NEW] @[backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py]` (with `__all__` exporting all `test_*` functions) testing:
         - `GCPProvisionConfigDTO` positive construction and negative `ValidationError` on trailing slash (`primary_domain="qrum.ai/"`, `email_endpoint="https://api.resend.com/emails/"`), empty strings, `command_timeout_seconds=4` (`min-1`), `command_timeout_seconds=3601` (`max+1`), `http_timeout_seconds=0.5` (`min-1`), `http_timeout_seconds=120.5` (`max+1`), and `extra="forbid"`.
         - `generate_secret_value` positive cryptographic token generation (`SecretStr` redaction verified on `str()` / `repr()`) and negative `ValueError` on `nbytes=31` (`min-1`) and `nbytes=129` (`max+1`).
         - `build_stage_commands` verification across `PREFLIGHT`, `SECRETS` (verifying `quorum-jwt-secret`, `quorum-service-auth-secret`, `quorum-db-url`, `quorum-vertex-sa-json`, and `quorum-email-api-key`), `NETWORK_DATA` (`PILOT` vs. `HA` SQL/Redis flags and `--no-assign-ip`), `DEPLOY` (verifying `quorum-seed` mounts `DATABASE_URL=quorum-db-url:latest,JWT_SECRET_KEY=quorum-jwt-secret:latest,SECRET_VERTEX_AI_SA_JSON=quorum-vertex-sa-json:latest`; verifying `quorum-api` and `quorum-worker` in both `console` and `http_api` modes mount `SERVICE_AUTH_SECRET=quorum-service-auth-secret:latest`, `FRONTEND_APP_BASE_URL=https://app.qrum.ai`, `OTEL_ENABLED=true`, and conditional `EMAIL_API_ENDPOINT` + `EMAIL_API_KEY=quorum-email-api-key:latest`; and asserting complete absence of `CORS_ORIGINS`, `LOGFIRE_TOKEN`, `SECRET_VERTEX_AI_SA_JSON`, `USE_VERTEX_LLM`, `VERTEX_PROJECT_ID`, `VERTEX_LOCATION`, and `GOOGLE_APPLICATION_CREDENTIALS` on `quorum-api`, `quorum-worker`, and `@[docker-compose.yml#L1-L57]`), and `DNS_SSL` (verifying `qrum-ai-zone`, `qrum-san-cert`, and Resend EU `send.qrum.ai` SPF/MX and `_dmarc.qrum.ai` DMARC record-sets).
         - `verify_dns_delegation` positive match (case and trailing-dot insensitive) and negative mismatch (`is_delegated=False` with registrar instructions).
         - `verify_cloud_health` positive `HealthCheckResponseDTO` validation (`status="ok"`) and >=2 negative cases (`status="degraded"`, HTTP `503`, and `httpx.HTTPError` transport failure raising `ProvisioningError`).
         - `switch_flutter_client_env` roundtrip switching between `CLOUD` (`ENVIRONMENT=production`) and `LOCAL` (`ENVIRONMENT=development`) while preserving custom `.env` keys and comments, plus negative `ProvisioningError` when `env_file_path` does not exist.
         - `execute_provision_stage` and `main()` in `--check` mode and `--apply` mode, including negative `ProvisioningError` / exit code `1` when a subprocess command returns non-zero or times out.
      2. Modify `@[.agents/rules/04_directory_reference.md#L25-L121]` to register `scripts/test_provision_gcp_cloud.py` in `&lt;rule_block id="test_directory_isolation"&gt;` and `provision_gcp_cloud.py` in `&lt;module path="scripts/"&gt;`.
    </action>
    <test_contracts>
      - Positive: Full unit suite passes with &gt;90% line coverage on `scripts/provision_gcp_cloud.py`, proving `EPIC 164` secret bootstrap parity, Resend EU `HTTP_API` wiring, and `Task_Assignment_Portal_Hardening` `FRONTEND_APP_BASE_URL` / Firebase Admin readiness.
      - Negative 1: `verify_cloud_health` raises `ProvisioningError` on HTTP `503` or `status="degraded"`, and `switch_flutter_client_env` raises `ProvisioningError` on missing `.env` path.
      - Negative 2: Boundary value violations (`command_timeout_seconds` `4` and `3601`, `http_timeout_seconds` `0.5` and `120.5`, `nbytes` `31` and `129`) raise `ValidationError` / `ValueError`.
    </test_contracts>
    <validation_gate>
      $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/provision_gcp_cloud.py backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py --test --ast-strict; $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Guided_Cloud_Cutover.md
    </validation_gate>
  </step>
</execution_protocol>
```

---

## 5. Architectural Safeguards & Verification Plan (ISTQB Test Matrix)

### Automated Unit & Structural Tests
- **Scenario 1 (Happy Path — Multi-Stage Check & Apply Orchestration, Shared KEK Seed Bootstrap & Resend EU `HTTP_API` Wiring):** `execute_provision_stage` with `PILOT` and `HA` tiers and `"console"` / `"http_api"` email modes generates deterministic `gcloud` command sequences across all 6 stages (including `quorum-jwt-secret`, `quorum-service-auth-secret`, `quorum-db-url`, `quorum-vertex-sa-json`, `quorum-email-api-key`, `quorum-seed` shared `JWT_SECRET_KEY` + `SECRET_VERTEX_AI_SA_JSON` bindings, and Resend EU SPF/MX/DMARC DNS records), pipes `SecretStr` values via `stdin`, verifies `DNSVerificationResultDTO.is_delegated == True`, validates `HealthCheckResponseDTO(status="ok")`, and switches `client_app_v2/.env` between `CLOUD` and `LOCAL` profiles while `@[docker-compose.yml#L1-L57]` contains zero legacy LLM or `service-account.json` entries.
- **Scenario 2 (Negative Path 1 — Missing/Invalid Input & Unpropagated DNS / Degraded Health):** `GCPProvisionConfigDTO` rejects trailing slashes (`primary_domain="qrum.ai/"`, `email_endpoint="https://api.resend.com/emails/"`) and unrecognized keys (`extra="forbid"`); `verify_dns_delegation` returns `is_delegated=False` when registrar NS records do not match Cloud DNS; `verify_cloud_health` raises `ProvisioningError` when `/api/v2/system/health` returns `"degraded"` or HTTP `503`; `switch_flutter_client_env` raises `ProvisioningError` when target `.env` is missing.
- **Scenario 3 (Negative Path 2 — ISTQB Boundary Value Violations & Subprocess Timeout):** `GCPProvisionConfigDTO` rejects `command_timeout_seconds=4` (`min-1`) and `command_timeout_seconds=3601` (`max+1`), `http_timeout_seconds=0.5` (`min-1`) and `http_timeout_seconds=120.5` (`max+1`); `generate_secret_value` rejects `nbytes=31` (`min-1`) and `nbytes=129` (`max+1`); `run_subprocess_command` translates `subprocess.TimeoutExpired` into `ProvisioningError`.

### Global Completion Gates & Mandatory Final E2E REST API Verification Gate
- **Localized Script & Companion Unit Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/provision_gcp_cloud.py backend_v2/tests/unit/scripts/test_provision_gcp_cloud.py --test --ast-strict`
- **Global Backend Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`
- **Global Flutter Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **Mandatory Final E2E REST API Verification Gate (Windows PowerShell):**
  - `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
