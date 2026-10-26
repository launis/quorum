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

# EPIC 74: GCP Production Deployment, Cloud Run & `quorum.ai` Domain Sovereignty

> [!IMPORTANT]
> **SOVEREIGN 2026 PRODUCTION INFRASTRUCTURE**: This Epic defines Cognitive Quorum's production cloud infrastructure on Google Cloud Platform (`europe-north1` / Finland). It supersedes legacy Firestore, TinyDB, SQLAlchemy 2.0, and Alembic deployment drafts, anchoring directly on **All-in-PostgreSQL 19 Sovereign Zero-ORM** (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`) and **B2B SaaS IAM, Token Exchange & Enterprise Hardening** (`@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`).

---

## 1. Objective & Architectural Overview

This Epic provisions and hardens Cognitive Quorum's stateless production runtime on Google Cloud Platform (`europe-north1`) across six architectural pillars:

1. **Stateless Cloud Run Compute (`quorum-api` & `quorum-worker`)**:
   - FastAPI HTTP/SSE API server (`quorum-api`) and Arq 2026 background worker daemon (`quorum-worker`) execute inside hardened Python 3.14 containers (`@[backend_v2/Dockerfile]`) without development file-watcher flags (`--reload`).
2. **Cloud SQL for PostgreSQL 19 (Zero-ORM & Private IP)**:
   - Managed PostgreSQL 19 instance with native `uuidv7()`, `uuid_extract_timestamp() VIRTUAL`, `default_toast_compression = lz4`, built-in PgBouncer transaction pooling, Private IP VPC isolation (`quorum-vpc`), and 14-day Point-in-Time Recovery (PITR).
   - Initialized deterministically via idempotent SQL DDL (`[NEW] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`) without Alembic or SQLAlchemy.
3. **Memorystore for Redis 8 (Fail-Closed Kill-Switch, FinOps Rate Limiting & Arq Queue)**:
   - Managed Redis instance on Private IP serving sub-millisecond `revoked:usr:{id}` session revocation checks, per-tenant sliding-window TPM/RPM rate limiting, and Arq job queues.
4. **Global `quorum.ai` Primary Domain Acquisition, Cloud DNS & Multi-Domain SAN SSL**:
   - Verifies availability and registers the primary global domain `quorum.ai` (and secondary domestic domain `quorum.fi`) via Google Cloud Domains or an accredited domain registrar (`gcloud domains registrations search-domains quorum.ai`). If `quorum.ai` is already registered by a third party, the operator registers an available domain (`cognitivequorum.ai` or `quorum.fi`) and injects it via `PRIMARY_DOMAIN`, `JWT_ISSUER`, `JWT_AUDIENCE`, and `CORS_ORIGINS` environment variables with zero source code modifications.
   - Cloud Load Balancer + Cloud Armor + Cloud DNS (`quorum-ai-zone`) with Google-Managed multi-domain SAN SSL certificates (`quorum-san-cert`) covering `quorum.ai`, `api.quorum.ai`, `app.quorum.ai`, `studio.quorum.ai`, `quorum.fi`, `api.quorum.fi`, and `app.quorum.fi`.
   - Production CORS origin enforcement and RFC 8693 JWT issuer/audience claims (`jwt_issuer = "https://api.quorum.ai"`, `jwt_audience = "https://quorum.ai"`) centralized in `Settings` (`@[backend_v2/settings.py#L54-L1053]`).
5. **GCP Secret Manager & Zero-Plaintext Credential Injection**:
   - Database credentials (`DATABASE_URL`), JWT signing keys (`JWT_SECRET_KEY`), and Cloud KMS keys are injected into Cloud Run exclusively from GCP Secret Manager (`credential_hardcoding_ban`).
6. **Typed Cloud Run & Load Balancer Health Probe (`GET /api/v2/system/health`)**:
   - Exposes a strongly typed `[NEW] HealthCheckResponseDTO` (`class HealthCheckResponseDTO(BaseResponseDTO):` in `@[backend_v2/models/dtos/system.py#L43-L52]`) on `GET /api/v2/system/health` (`@[backend_v2/api/routers/system/health.py#L20-L52]`) for Cloud Run startup/liveness probes and Cloud Load Balancer health checks.

```mermaid
flowchart TD
    Internet["Global Client Traffic (quorum.ai / quorum.fi)"] -->|"HTTPS TLS 1.3 + SAN SSL"| GLB["Cloud Load Balancer + Cloud Armor"]
    GLB -->|"api.quorum.ai"| API["Cloud Run: quorum-api (Stateless FastAPI)"]
    API -->|"VPC Connector (Private IP)"| PG["Cloud SQL: PostgreSQL 19 (PgBouncer, PITR, lz4)"]
    API -->|"VPC Connector (Private IP)"| Redis["Memorystore: Redis 8 (Kill-Switch, Rate Limit, Arq)"]
    Worker["Cloud Run: quorum-worker (Arq Daemon)"] -->|"VPC Connector (Private IP)"| PG
    Worker -->|"VPC Connector (Private IP)"| Redis
    API -->|"Environment Secret Injection"| Secrets["GCP Secret Manager & Cloud KMS"]
    Worker -->|"Environment Secret Injection"| Secrets
    API -->|"Signed URLs / FileDriver"| GCS["Cloud Storage / Firebase Storage (europe-north1)"]
    Worker -->|"Artifact Streaming"| GCS
```

---

## 2. Scope & Target Codebase Boundaries

| Category | File Reference | Architectural Responsibility |
| :--- | :--- | :--- |
| `[MODIFY]` | `@[backend_v2/settings.py#L54-L1053]` | Add `gcp_project_id`, `gcp_region`, `primary_domain`, `jwt_issuer`, and `jwt_audience` settings; enforce closed `cors_origins` in `_enforce_environment_limits` (`@[backend_v2/settings.py#L847-L908]`) and reject wildcard `["*"]` CORS in production mode via `@model_validator(mode="after")`. |
| `[MODIFY]` | `@[backend_v2/models/dtos/system.py#L43-L52]` | Define immutable `HealthCheckResponseDTO(BaseResponseDTO)` with `ConfigDict(frozen=True, strict=True, extra="forbid")` for Cloud Run and Load Balancer probes. |
| `[MODIFY]` | `@[backend_v2/api/routers/system/health.py#L20-L52]` | Implement `GET /api/v2/system/health` (`get_system_health`) returning `HealthCheckResponseDTO` with RFC 7807 structured error handling. |
| `[MODIFY]` | `@[backend_v2/main.py#L347-L380]` | Replace hardcoded `https://api.quorum.fi/errors/validation-failed` in `validation_exception_handler` with `f"{get_settings().jwt_issuer}/errors/validation-failed"`. |
| `[MODIFY]` | `@[backend_v2/Dockerfile]` | Remove development `--reload` flag from `CMD`, add non-root `quorum` runtime user, and configure production Uvicorn worker entrypoint. |
| `[MODIFY]` | `@[docker-compose.yml]` | Remove duplicate `GOOGLE_APPLICATION_CREDENTIALS` environment entry and align container configuration. |
| `[MODIFY]` | `@[backend_v2/tests/unit/models/dtos/test_system.py#L7-L12]` | Add positive and ISTQB negative unit tests for `HealthCheckResponseDTO`. |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_health.py#L14-L19]` | Add positive and ISTQB negative unit tests for `get_system_health` (`GET /api/v2/system/health`). |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_settings.py#L264-L290]` | Add positive and ISTQB negative unit tests for GCP production settings, closed production CORS origins, and wildcard CORS rejection in production. |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_main.py#L172-L189]` | Verify `validation_exception_handler` RFC 7807 `type` URI resolves dynamically from `Settings.jwt_issuer`. |

---

## 3. Production Environment & Cloud Provisioning Specifications

### 3.1 Production Environment Variables & Secret Manager Bindings

| Variable | Production Value | Source |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Cloud Run Env Var |
| `STORAGE_BACKEND` | `POSTGRES` | Cloud Run Env Var |
| `GCP_PROJECT` | `cognitive-quorum` | Cloud Run Env Var |
| `GCP_REGION` | `europe-north1` | Cloud Run Env Var |
| `VERTEX_LOCATION` | `europe-north1` | Cloud Run Env Var |
| `PRIMARY_DOMAIN` | `quorum.ai` | Cloud Run Env Var |
| `JWT_ISSUER` | `https://api.quorum.ai` | Cloud Run Env Var |
| `JWT_AUDIENCE` | `https://quorum.ai` | Cloud Run Env Var |
| `API_URL` | `https://api.quorum.ai` | Cloud Run Env Var |
| `STORAGE_BUCKET_NAME` | `cognitive-quorum.firebasestorage.app` | Cloud Run Env Var |
| `REDIS_HOST` | `10.x.x.x` (Memorystore Private IP) | Cloud Run Env Var |
| `REDIS_PORT` | `6379` | Cloud Run Env Var |
| `DATABASE_URL` | `postgresql://quorum_app:***@10.x.x.x:5432/quorum` | GCP Secret Manager (`quorum-db-url:latest`) |
| `JWT_SECRET_KEY` | `<256-bit cryptographic secret>` | GCP Secret Manager (`quorum-jwt-secret:latest`) |

### 3.2 Cloud Provisioning & Domain DNS Commands (PowerShell Single-Line Execution)

```powershell
gcloud config set project cognitive-quorum
gcloud domains registrations search-domains quorum.ai
gcloud compute addresses create quorum-global-ip --global --ip-version IPV4
gcloud dns managed-zones create quorum-ai-zone --dns-name="quorum.ai." --description="Cognitive Quorum Primary Production DNS Zone" --visibility=public
gcloud dns record-sets create quorum.ai. --zone=quorum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
gcloud dns record-sets create api.quorum.ai. --zone=quorum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
gcloud dns record-sets create app.quorum.ai. --zone=quorum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
gcloud dns record-sets create studio.quorum.ai. --zone=quorum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
gcloud compute ssl-certificates create quorum-san-cert --domains="quorum.ai,api.quorum.ai,app.quorum.ai,studio.quorum.ai,quorum.fi,api.quorum.fi,app.quorum.fi" --global
gcloud compute networks create quorum-vpc --subnet-mode=custom
gcloud sql instances create quorum-pg19-prod --database-version=POSTGRES_19 --tier=db-custom-2-8192 --region=europe-north1 --availability-type=REGIONAL --network=quorum-vpc --no-assign-ip --enable-point-in-time-recovery --backup-start-time=02:00 --retained-backups-count=14
gcloud redis instances create quorum-redis-prod --size=2 --region=europe-north1 --tier=STANDARD_HA --redis-version=redis_7_2 --network=quorum-vpc
gcloud run deploy quorum-api --image europe-north1-docker.pkg.dev/cognitive-quorum/quorum-repo/quorum-api:latest --region europe-north1 --platform managed --vpc-connector quorum-connector --set-env-vars "ENVIRONMENT=production,STORAGE_BACKEND=POSTGRES,GCP_PROJECT=cognitive-quorum,GCP_REGION=europe-north1,PRIMARY_DOMAIN=quorum.ai,JWT_ISSUER=https://api.quorum.ai,JWT_AUDIENCE=https://quorum.ai,API_URL=https://api.quorum.ai" --set-secrets "DATABASE_URL=quorum-db-url:latest,JWT_SECRET_KEY=quorum-jwt-secret:latest" --min-instances 1 --max-instances 10 --memory 2Gi --cpu 2 --timeout 300 --allow-unauthenticated
gcloud run deploy quorum-worker --image europe-north1-docker.pkg.dev/cognitive-quorum/quorum-repo/quorum-worker:latest --region europe-north1 --platform managed --vpc-connector quorum-connector --command "uv,run,python,-m,backend_v2.run_worker" --set-env-vars "ENVIRONMENT=production,STORAGE_BACKEND=POSTGRES,GCP_PROJECT=cognitive-quorum,GCP_REGION=europe-north1,PRIMARY_DOMAIN=quorum.ai" --set-secrets "DATABASE_URL=quorum-db-url:latest,JWT_SECRET_KEY=quorum-jwt-secret:latest" --min-instances 1 --max-instances 5 --memory 4Gi --cpu 2 --timeout 900 --no-allow-unauthenticated
```

---

## 4. Verification & Quality Gates

1. **Automated Backend Quality Gate**:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict
   ```
2. **Plan & Tracker Structural Verification**:
   ```powershell
   uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md
   uv run python scripts/audit_tracker_output.py --tracker docs/implementationplans/TRACKER_GCP_Production_Deployment.md --plan-file docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md
   uv run python scripts/audit_plan_tracker_parity.py --plan docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md --tracker docs/implementationplans/TRACKER_GCP_Production_Deployment.md
   ```
