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

# Implementation Plan: GCP Production Deployment, Cloud Run & `qrum.ai` Domain Sovereignty

## 1. Objective & Architectural Sovereignty

This implementation plan hardens Cognitive Quorum's backend configuration, health probes, container entrypoints, worker health responders, and multi-domain origin security for stateless production deployment on **Google Cloud Platform (`europe-north1` / Finland)**. Built atop the All-in-PostgreSQL 19 Sovereign Zero-ORM Architecture (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`) and B2B SaaS IAM & Enterprise Hardening (`@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`), this plan enforces five sovereign production invariants:

1. **Global Config Sovereignty for Application Version, Cloud Run `$PORT` / `worker_health_port`, GCP & `qrum.ai` Domain Claims (`@[backend_v2/settings.py#L37-L48]` & `@[backend_v2/settings.py#L68-L1494]`)**:
   - Defines `strip_trailing_slash(v: Any) -> Any` alongside `strip_whitespace` (`@[backend_v2/settings.py#L51-L62]`), stripping surrounding whitespace and trailing `/` characters (`v.strip().rstrip("/")` when `isinstance(v, str)`), and exports `"strip_trailing_slash"` in `__all__`.
   - Declares strongly typed PEP 593 `Annotated` fields on `Settings`: `app_version` (`"2.9.0"`, `min_length=1`, `BeforeValidator(strip_whitespace)`, `validation_alias=AliasChoices("app_version", "APP_VERSION")`), `port` (`8000`, `ge=1`, `le=65535`, `validation_alias=AliasChoices("port", "PORT")`), `worker_health_port` (`8081`, `ge=1`, `le=65535`, `validation_alias=AliasChoices("worker_health_port", "WORKER_HEALTH_PORT", "PORT")` — defaulting to `8081` locally so `run_local.bat` never collides with `uvicorn` on port `8000`, while automatically binding Cloud Run's injected `PORT` in container environments), `gcp_project_id` (`"cognitive-quorum"`), `gcp_region` (`"europe-north1"`), `primary_domain` (`"qrum.ai"`, normalized via `BeforeValidator(strip_trailing_slash)`), `jwt_issuer` (`"https://api.qrum.ai"`, normalized via `BeforeValidator(strip_trailing_slash)`), and `jwt_audience` (`"https://qrum.ai"`, normalized via `BeforeValidator(strip_trailing_slash)`), normalizes `frontend_app_base_url` (`"https://app.qrum.ai"`) via `BeforeValidator(strip_trailing_slash)`, and enforces `min_length=1` on `cors_origins`.
   - Consolidates deterministic production CORS default resolution and strict per-origin validation inside `_enforce_environment_limits` (`@[backend_v2/settings.py#L1214-L1302]`) without splitting logic across multiple `@model_validator(mode="after")` methods: when `environment == "production"`, if `"cors_origins" not in self.model_fields_set`, `self.cors_origins` is set to `[f"https://{self.primary_domain}", f"https://app.{self.primary_domain}", f"https://studio.{self.primary_domain}"]` (resolving to `["https://qrum.ai", "https://app.qrum.ai", "https://studio.qrum.ai"]` by default without requiring `CORS_ORIGINS` in Cloud Run environment variables); then unconditionally (regardless of `self.model_fields_set`), `_enforce_environment_limits` verifies `self.cors_origins` is non-empty and every `origin` in `self.cors_origins` satisfies `origin.startswith("https://")`, `"*" not in origin`, `not origin.endswith("/")`, and `len(origin) > len("https://")`, raising `ValueError` immediately on any violation.
2. **Dynamic RFC 7807 Problem Type URI Sovereignty, Direct CORS SSOT Binding & Lifespan State Hygiene (`@[backend_v2/main.py#L182-L249]` & `@[backend_v2/main.py#L389-L423]`)**:
   - Binds `version=get_settings().app_version` on `FastAPI(...)`, pre-initializes `app.state.arq_pool = None` and `app.state.pool_manager = None` at module scope, and resets `app.state.arq_pool = None` and `app.state.pool_manager = None` inside the `finally:` block of `lifespan` (`@[backend_v2/main.py#L182-L249]`) so in-memory readiness state accurately reflects startup and shutdown draining.
   - Removes the legacy `if not cors_origins: cors_origins = ["*"]` fallback block in `@[backend_v2/main.py#L389-L423]` (module-level `CORSMiddleware` setup) so `CORSMiddleware` consumes `allow_origins=get_settings().cors_origins` directly from the `Settings` SSOT.
   - Replaces the hardcoded legacy domain `"https://api.quorum.fi/errors/validation-failed"` inside `validation_exception_handler` (`@[backend_v2/main.py#L389-L423]`) with `f"{get_settings().jwt_issuer}/errors/validation-failed"` (resolving to `"https://api.qrum.ai/errors/validation-failed"` without double-slash `//` risk), ensuring 100% domain consistency with `qrum.ai`.
3. **Typed Cloud Run & Load Balancer Health Probe with $O(1)$ In-Memory Readiness (`@[backend_v2/models/dtos/system.py#L44-L53]` & `@[backend_v2/api/routers/system/health.py#L29-L79]`)**:
   - Creates `HealthCheckResponseDTO` (`class HealthCheckResponseDTO(BaseResponseDTO)`) defined in `@[backend_v2/models/dtos/system.py#L56-L75]` with `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")`, completely eliminating naked dictionary health responses (`zero_naked_dicts_and_permissive_typing`, `data_leak_prevention_firewall`).
   - Exposes `GET /api/v2/system/health` (`get_system_health`) in `@[backend_v2/api/routers/system/health.py#L29-L79]` with `response_model=HealthCheckResponseDTO`, evaluating `request.app.state` in $O(1)$ memory (`pool_manager` and `arq_pool` initialization) to report `"ok"` vs. `"degraded"`, resolving `version=cfg.app_version` from `Settings` SSOT, and enforcing RFC 7807 Dual-Reporting error translation.
4. **Single-Loop Asyncio Health Probe Responder for `quorum-worker` (`@[backend_v2/run_worker.py#L46-L66]`)**:
   - Adds a zero-dependency stdlib `asyncio.start_server` health probe responder (`_handle_health_probe` and `health_server`) in `@[backend_v2/run_worker.py#L46-L66]` bound to `host="0.0.0.0"` and `port=get_settings().worker_health_port` (`8081` locally on Windows host when `PORT` is unset; `$PORT` automatically in Cloud Run) inside an `async with health_server:` context wrapping `await worker.async_run()`. This satisfies Cloud Run Service startup and liveness TCP/HTTP probes on `$PORT` without spawning OS threads, secondary web frameworks, or colliding with local `uvicorn` on port `8000`.
5. **Stateless Non-Root Container, Pre-Built `.venv` Execution & Compose Hardening (`@[backend_v2/Dockerfile#L1-L36]` & `@[docker-compose.yml#L1-L96]`)**:
   - Creates a dedicated non-root `quorum` user (`UID 10001`) in `@[backend_v2/Dockerfile#L1-L36]`, assigns `quorum:quorum` ownership to `/app/backend_v2` and `/app/.venv`, sets `ENV PYTHONPATH=/app VIRTUAL_ENV=/app/.venv PATH="/app/.venv/bin:$PATH" UV_NO_SYNC=1 UV_OFFLINE=1 UV_CACHE_DIR=/tmp/uv-cache PORT=8000`, removes `--reload`, and executes `/app/.venv/bin/uvicorn` directly via `exec` on `${PORT}` to eliminate runtime `uv run` permission errors and cold-start overhead.
   - Removes the duplicate `GOOGLE_APPLICATION_CREDENTIALS` environment entry and replaces deprecated `STORAGE_BACKEND=LOCAL` / `USE_MOCK_DB=true` entries with `STORAGE_BACKEND=POSTGRES` / `USE_MOCK_DB=false` in `@[docker-compose.yml#L1-L96]`.

### 1.1 `qrum.ai` Domain Acquisition, Cloud DNS, SAN SSL & GCP Provisioning Protocol

```mermaid
flowchart TD
    Internet["Global Client Traffic (qrum.ai)"] -->|"HTTPS TLS 1.3 + SAN SSL"| GLB["Cloud Load Balancer + Cloud Armor"]
    GLB -->|"api.qrum.ai"| API["Cloud Run: quorum-api (Stateless FastAPI)"]
    API -->|"VPC Connector (Private IP)"| PG["Cloud SQL: PostgreSQL 19 (PgBouncer, PITR, lz4)"]
    API -->|"VPC Connector (Private IP)"| Redis["Memorystore: Redis 8 (Kill-Switch, Rate Limit, Arq)"]
    Worker["Cloud Run: quorum-worker (Arq Daemon)"] -->|"VPC Connector (Private IP)"| PG
    Worker -->|"VPC Connector (Private IP)"| Redis
    API -->|"Environment Secret Injection"| Secrets["GCP Secret Manager & Cloud KMS"]
    Worker -->|"Environment Secret Injection"| Secrets
    API -->|"Signed URLs / FileDriver"| GCS["Cloud Storage / Firebase Storage (europe-north1)"]
    Worker -->|"Artifact Streaming"| GCS
```

1. **Domain Availability Verification, `.ai` Registrar NS Delegation & SSOT Origin Locking (`qrum.ai`)**:
   - `whois.nic.ai` registry verification confirms `qrum.ai` is officially available to register as the 4-letter ultra-short global domain.
   - Register `qrum.ai` via Google Cloud Domains (`gcloud domains registrations search-domains qrum.ai`) or an accredited domain registrar, delegate authoritative nameservers (`NS` records) at the `.ai` registry (`whois.nic.ai`) to the 4 Cloud DNS nameservers assigned to `qrum-ai-zone` (`gcloud dns managed-zones describe qrum-ai-zone --format="value(nameServers)"`), and verify public propagation (`Resolve-DnsName -Name qrum.ai -Type NS`) before Google Certificate Manager ACME validation.
   - Inject scalar domain settings at runtime via Cloud Run environment variables (`PRIMARY_DOMAIN=qrum.ai`, `JWT_ISSUER=https://api.qrum.ai`, `JWT_AUDIENCE=https://qrum.ai`) while **intentionally omitting `CORS_ORIGINS`** from `gcloud run deploy --set-env-vars`. Because `pydantic-settings` decodes `list[str]` environment variables via `json.loads()` (which collides with `gcloud --set-env-vars` comma delimiters) and `Settings._enforce_environment_limits` (`@[backend_v2/settings.py#L68-L1494]`) automatically locks `self.cors_origins` to `[f"https://{self.primary_domain}", f"https://app.{self.primary_domain}", f"https://studio.{self.primary_domain}"]` (`["https://qrum.ai", "https://app.qrum.ai", "https://studio.qrum.ai"]`) whenever `environment == "production"` and `"cors_origins" not in self.model_fields_set`, zero CLI JSON-quoting workarounds and zero Python or Flutter source code edits are required during deployment or domain rotation.
2. **Production Environment Variables & Secret Manager Bindings**:

| Variable | Production Value | Source |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Cloud Run Env Var |
| `APP_VERSION` | `2.9.0` | Cloud Run Env Var |
| `PORT` | `8000` | Cloud Run `--port 8000` / Env Var |
| `STORAGE_BACKEND` | `POSTGRES` | Cloud Run Env Var |
| `GCP_PROJECT` | `cognitive-quorum` | Cloud Run Env Var |
| `GOOGLE_CLOUD_PROJECT` | `cognitive-quorum` | Cloud Run Env Var (consumed by Vertex AI ADC & `Settings.model_post_init`) |
| `VERTEX_PROJECT_ID` | `cognitive-quorum` | Cloud Run Env Var (consumed by `Settings.enabled_providers` & LiteLLM Vertex AI) |
| `USE_VERTEX_LLM` | `true` | Cloud Run Env Var |
| `GCP_REGION` | `europe-north1` | Cloud Run Env Var |
| `VERTEX_LOCATION` | `europe-north1` | Cloud Run Env Var |
| `PRIMARY_DOMAIN` | `qrum.ai` | Cloud Run Env Var (drives default production `cors_origins` in `Settings`) |
| `JWT_ISSUER` | `https://api.qrum.ai` | Cloud Run Env Var |
| `JWT_AUDIENCE` | `https://qrum.ai` | Cloud Run Env Var |
| `API_URL` | `https://api.qrum.ai` | Cloud Run Env Var |
| `FRONTEND_APP_BASE_URL` | `https://app.qrum.ai` | Cloud Run Env Var (normalized via `BeforeValidator(strip_trailing_slash)` for invitation/task links) |
| `EMAIL_TRANSPORT_MODE` | `console` (initial zero-dependency launch) / `http_api` (live HTTPS dispatch) | Cloud Run Env Var |
| `EMAIL_FROM_ADDRESS` | `no-reply@qrum.ai` | Cloud Run Env Var |
| `EMAIL_API_ENDPOINT` | `https://api.resend.com/emails` (active when `EMAIL_TRANSPORT_MODE=http_api`) | Cloud Run Env Var |
| `STORAGE_BUCKET_NAME` | `cognitive-quorum.firebasestorage.app` | Cloud Run Env Var |
| `REDIS_HOST` | `10.x.x.x` (Memorystore Private IP) | Cloud Run Env Var |
| `REDIS_PORT` | `6379` | Cloud Run Env Var |
| `DATABASE_URL` | `postgresql://quorum_app:***@10.x.x.x:5432/quorum` | GCP Secret Manager (`quorum-db-url:latest`, bound to `Settings.postgres_dsn` via `AliasChoices("postgres_dsn", "POSTGRES_DSN", "DATABASE_URL")`) |
| `JWT_SECRET_KEY` | `<256-bit cryptographic secret>` | GCP Secret Manager (`quorum-jwt-secret:latest`) |
| `EMAIL_API_KEY` | `<transactional email HTTPS bearer token>` (active when `EMAIL_TRANSPORT_MODE=http_api`) | GCP Secret Manager (`quorum-email-api-key:latest`) |

3. **Cloud DNS Zone, Global Anycast IP, Google-Managed SAN SSL, Load Balancer Attachment Chain & Cloud Run Provisioning (PowerShell)**:
   - Google Cloud's ACME authority cannot validate and activate `qrum-san-cert` (`PROVISIONING` -> `ACTIVE`) solely from `gcloud compute ssl-certificates create`. Both the `.ai` registry `NS` delegation to `qrum-ai-zone` AND the complete Global External Application Load Balancer front-end attachment chain (`quorum-api-neg` -> `quorum-api-backend` -> `qrum-url-map` -> `qrum-https-proxy` with `--ssl-certificates=qrum-san-cert` -> `qrum-https-forwarding-rule` on `qrum-global-ip:443`) MUST be active:
   ```powershell
   gcloud config set project cognitive-quorum
   gcloud domains registrations search-domains qrum.ai
   gcloud compute addresses create qrum-global-ip --global --ip-version IPV4
   $GLOBAL_ANYCAST_IP = (gcloud compute addresses describe qrum-global-ip --global --format="value(address)")
   gcloud dns managed-zones create qrum-ai-zone --dns-name="qrum.ai." --description="Quorum Primary Production DNS Zone" --visibility=public
   gcloud dns managed-zones describe qrum-ai-zone --format="value(nameServers)"
   # Delegate .ai registrar (whois.nic.ai) NS records to the 4 Cloud DNS nameServers above, then verify:
   Resolve-DnsName -Name qrum.ai -Type NS
   gcloud dns record-sets create qrum.ai. --zone=qrum-ai-zone --type=A --ttl=300 --rrdatas="$GLOBAL_ANYCAST_IP"
   gcloud dns record-sets create api.qrum.ai. --zone=qrum-ai-zone --type=A --ttl=300 --rrdatas="$GLOBAL_ANYCAST_IP"
   gcloud dns record-sets create app.qrum.ai. --zone=qrum-ai-zone --type=A --ttl=300 --rrdatas="$GLOBAL_ANYCAST_IP"
   gcloud dns record-sets create studio.qrum.ai. --zone=qrum-ai-zone --type=A --ttl=300 --rrdatas="$GLOBAL_ANYCAST_IP"
   gcloud compute ssl-certificates create qrum-san-cert --domains="qrum.ai,api.qrum.ai,app.qrum.ai,studio.qrum.ai" --global
   gcloud compute networks create quorum-vpc --subnet-mode=custom
   gcloud sql instances create quorum-pg19-prod --database-version=POSTGRES_19 --tier=db-custom-2-8192 --region=europe-north1 --availability-type=REGIONAL --network=quorum-vpc --no-assign-ip --enable-point-in-time-recovery --backup-start-time=02:00 --retained-backups-count=14
   gcloud redis instances create quorum-redis-prod --size=2 --region=europe-north1 --tier=STANDARD_HA --redis-version=redis_7_2 --network=quorum-vpc
   gcloud run jobs deploy quorum-seed --image europe-north1-docker.pkg.dev/cognitive-quorum/quorum-repo/quorum-api:latest --region europe-north1 --vpc-connector quorum-connector --command "/app/.venv/bin/python" --args="-m,backend_v2.seed.run_seed,postgres" --set-env-vars "ENVIRONMENT=production,STORAGE_BACKEND=POSTGRES,GCP_PROJECT=cognitive-quorum,GOOGLE_CLOUD_PROJECT=cognitive-quorum,VERTEX_PROJECT_ID=cognitive-quorum,USE_VERTEX_LLM=true,GCP_REGION=europe-north1,VERTEX_LOCATION=europe-north1" --set-secrets "DATABASE_URL=quorum-db-url:latest,JWT_SECRET_KEY=quorum-jwt-secret:latest" --execute-now --wait
   gcloud run deploy quorum-api --image europe-north1-docker.pkg.dev/cognitive-quorum/quorum-repo/quorum-api:latest --region europe-north1 --platform managed --port 8000 --vpc-connector quorum-connector --set-env-vars "ENVIRONMENT=production,APP_VERSION=2.9.0,STORAGE_BACKEND=POSTGRES,GCP_PROJECT=cognitive-quorum,GOOGLE_CLOUD_PROJECT=cognitive-quorum,VERTEX_PROJECT_ID=cognitive-quorum,USE_VERTEX_LLM=true,GCP_REGION=europe-north1,VERTEX_LOCATION=europe-north1,PRIMARY_DOMAIN=qrum.ai,JWT_ISSUER=https://api.qrum.ai,JWT_AUDIENCE=https://qrum.ai,API_URL=https://api.qrum.ai,FRONTEND_APP_BASE_URL=https://app.qrum.ai,EMAIL_TRANSPORT_MODE=console,EMAIL_FROM_ADDRESS=no-reply@qrum.ai" --set-secrets "DATABASE_URL=quorum-db-url:latest,JWT_SECRET_KEY=quorum-jwt-secret:latest" --min-instances 1 --max-instances 10 --memory 2Gi --cpu 2 --timeout 300 --allow-unauthenticated
   gcloud run deploy quorum-worker --image europe-north1-docker.pkg.dev/cognitive-quorum/quorum-repo/quorum-worker:latest --region europe-north1 --platform managed --port 8000 --vpc-connector quorum-connector --command "/app/.venv/bin/python" --args="-m,backend_v2.run_worker" --set-env-vars "ENVIRONMENT=production,APP_VERSION=2.9.0,STORAGE_BACKEND=POSTGRES,GCP_PROJECT=cognitive-quorum,GOOGLE_CLOUD_PROJECT=cognitive-quorum,VERTEX_PROJECT_ID=cognitive-quorum,USE_VERTEX_LLM=true,GCP_REGION=europe-north1,VERTEX_LOCATION=europe-north1,PRIMARY_DOMAIN=qrum.ai" --set-secrets "DATABASE_URL=quorum-db-url:latest,JWT_SECRET_KEY=quorum-jwt-secret:latest" --min-instances 1 --max-instances 5 --memory 4Gi --cpu 2 --timeout 900 --no-allow-unauthenticated
   gcloud compute network-endpoint-groups create quorum-api-neg --region=europe-north1 --network-endpoint-type=serverless --cloud-run-service=quorum-api
   gcloud compute backend-services create quorum-api-backend --global --load-balancing-scheme=EXTERNAL_MANAGED
   gcloud compute backend-services add-backend quorum-api-backend --global --network-endpoint-group=quorum-api-neg --network-endpoint-group-region=europe-north1
   gcloud compute url-maps create qrum-url-map --default-service=quorum-api-backend
   gcloud compute target-https-proxies create qrum-https-proxy --ssl-certificates=qrum-san-cert --url-map=qrum-url-map
   gcloud compute forwarding-rules create qrum-https-forwarding-rule --global --load-balancing-scheme=EXTERNAL_MANAGED --network-tier=PREMIUM --address=qrum-global-ip --target-https-proxy=qrum-https-proxy --ports=443
   gcloud compute ssl-certificates describe qrum-san-cert --global --format="value(managed.status,managed.domainStatus)"
   ```

---

## 2. Scope & Target Boundaries

### TARGET Files (Authorized for Modification)

| Category | File Reference | Architectural Responsibility |
| :--- | :--- | :--- |
| `[MODIFY]` | `@[backend_v2/settings.py#L51-L62]` | Add `strip_trailing_slash` (`@[backend_v2/settings.py#L51-L62]`), `app_version`, `port`, `worker_health_port`, `gcp_project_id`, `gcp_region`, `primary_domain`, `jwt_issuer`, and `jwt_audience` fields to `Settings`, enforce `min_length=1` on `cors_origins`, and consolidate production `cors_origins` default assignment and strict HTTPS/wildcard/trailing-slash validation inside `_enforce_environment_limits` (`@[backend_v2/settings.py#L51-L62]`). |
| `[MODIFY]` | `@[backend_v2/models/dtos/system.py#L56-L75]` | Add `HealthCheckResponseDTO(BaseResponseDTO)` with `ConfigDict(frozen=True, strict=True, extra="forbid")` and export in `__all__`. |
| `[MODIFY]` | `@[backend_v2/api/routers/system/health.py#L29-L79]` | Implement `GET /api/v2/system/health` (`get_system_health`) accepting `request: Request`, evaluating $O(1)$ in-memory readiness (`"ok"` vs. `"degraded"`), resolving `version=cfg.app_version`, and enforcing RFC 7807 Dual-Reporting. |
| `[MODIFY]` | `@[backend_v2/main.py#L182-L249]` | Bind `version=get_settings().app_version` on `FastAPI`, pre-initialize and reset `app.state.arq_pool` and `app.state.pool_manager` in `lifespan` (`@[backend_v2/main.py#L182-L249]`), remove `if not cors_origins: cors_origins = ["*"]` fallback, and replace hardcoded `"https://api.quorum.fi/errors/validation-failed"` in `validation_exception_handler` with `f"{get_settings().jwt_issuer}/errors/validation-failed"`. |
| `[MODIFY]` | `@[backend_v2/run_worker.py#L46-L66]` | Add `_HEALTH_RESPONSE_BYTES`, `_handle_health_probe`, and an `asyncio.start_server` listener bound to `get_settings().worker_health_port` inside `main()` to satisfy Cloud Run startup and liveness probes without colliding with local `uvicorn` on port `8000`. |
| `[MODIFY]` | `@[backend_v2/Dockerfile#L1-L36]` | Configure non-root `quorum` user (`UID 10001`), `chown -R quorum:quorum /app/.venv`, set `VIRTUAL_ENV`, `PATH`, `UV_NO_SYNC=1`, `UV_OFFLINE=1`, `UV_CACHE_DIR=/tmp/uv-cache`, `PORT=8000`, and invoke `/app/.venv/bin/uvicorn` via `exec` on `${PORT}` without `--reload`. |
| `[MODIFY]` | `@[docker-compose.yml#L1-L96]` | Remove duplicate `GOOGLE_APPLICATION_CREDENTIALS` line in `backend` service and update `STORAGE_BACKEND=POSTGRES` and `USE_MOCK_DB=false` in `backend` and `worker` services. |
| `[MODIFY]` | `@[backend_v2/tests/unit/models/dtos/test_system.py#L23-L49]` | Add positive and ISTQB negative boundary tests for `HealthCheckResponseDTO`. |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_health.py#L16-L23]` | Add positive and ISTQB negative unit tests for `get_system_health` (`GET /api/v2/system/health`), covering `"ok"` readiness, `"degraded"` uninitialized state, `cfg.app_version` SSOT binding, and `AppException` translation. |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_settings.py#L270-L294]` | Add positive and ISTQB negative unit tests for `app_version` (`APP_VERSION` alias, `""`, `"   "`), `port` and `worker_health_port` (`PORT` / `WORKER_HEALTH_PORT` aliases, `0`, `65536`), GCP settings, `strip_trailing_slash` normalization on `jwt_issuer`/`jwt_audience`, closed production CORS origins, and rejection of `"*"`, `"https://*.qrum.ai"`, `"http://qrum.ai"`, `"https://qrum.ai/"`, `"https://"`, and `[]` in production. |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_main.py#L182-L204]` | Assert `app.version` matches `get_settings().app_version`, `lifespan` resets `app.state.pool_manager` and `app.state.arq_pool` to `None` on shutdown, and `validation_exception_handler` RFC 7807 `type` URI dynamically uses `https://api.qrum.ai/errors/validation-failed` without double slashes (`//`). |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_run_worker.py#L11-L34]` | Add positive and ISTQB negative unit tests for `_handle_health_probe` and `main()` Cloud Run health server lifecycle bound to `get_settings().worker_health_port`. |

### CONTEXT Files (Strictly Read-Only)

- `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`
- `@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`
- `@[backend_v2/worker.py]`
- `@[backend_v2/exceptions.py]`

---

### `[MODIFY]` Target Details

#### `[MODIFY]` @[backend_v2/settings.py#L68-L1494]
Define `strip_trailing_slash` (`@[backend_v2/settings.py#L51-L62]`), add application version (`app_version`), Cloud Run `$PORT` (`port`), worker health probe port (`worker_health_port`, defaulting to `8081` locally and resolving `WORKER_HEALTH_PORT` / `PORT` in Cloud Run), GCP deployment (`gcp_project_id`, `gcp_region`), and `qrum.ai` domain sovereignty fields (`primary_domain`, `jwt_issuer`, `jwt_audience`) to `Settings` (`@[backend_v2/settings.py#L51-L62]`), enforce `min_length=1` on `cors_origins`, and consolidate default production `cors_origins` assignment and strict HTTPS/wildcard/trailing-slash validation inside `_enforce_environment_limits` (`@[backend_v2/settings.py#L51-L62]`).

#### `[MODIFY]` @[backend_v2/models/dtos/system.py#L44-L53]
Define `HealthCheckResponseDTO(BaseResponseDTO)` with `ConfigDict(frozen=True, strict=True, extra="forbid")` and export it in `__all__`.

#### `[MODIFY]` @[backend_v2/api/routers/system/health.py#L29-L79]
Add `get_system_health(request: Request) -> HealthCheckResponseDTO` (`GET /api/v2/system/health`) evaluating $O(1)$ in-memory lifespan readiness (`pool_manager` and `arq_pool` presence on `request.app.state`) to return `"ok"` vs. `"degraded"`, resolving `version=cfg.app_version`, and enforcing RFC 7807 Dual-Reporting error handling.

#### `[MODIFY]` @[backend_v2/main.py#L389-L423]
Bind `version=get_settings().app_version` on `FastAPI(...)`, pre-initialize `app.state.arq_pool = None` and `app.state.pool_manager = None` at module scope, reset both to `None` inside the `finally:` block of `lifespan` (`@[backend_v2/main.py#L182-L249]`), remove the `if not cors_origins: cors_origins = ["*"]` fallback when registering `CORSMiddleware`, and update `validation_exception_handler` (`@[backend_v2/main.py#L182-L249]`) to resolve the RFC 7807 `type` URI from `get_settings().jwt_issuer`.

#### `[MODIFY]` @[backend_v2/run_worker.py#L46-L66]
Add `_HEALTH_RESPONSE_BYTES` and `async def _handle_health_probe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None` with bounded read timeout `get_settings().http_client_timeout_seconds`, and bind `await asyncio.start_server(_handle_health_probe, host="0.0.0.0", port=get_settings().worker_health_port)` inside `async with health_server:` around `await worker.async_run()` in `main()`.

#### `[MODIFY]` @[backend_v2/Dockerfile#L1-L36]
Create dedicated non-root `quorum` user (`UID 10001`), set `chown -R quorum:quorum /app/.venv` and `--chown=quorum:quorum`, configure `VIRTUAL_ENV=/app/.venv`, `PATH="/app/.venv/bin:$PATH"`, `UV_NO_SYNC=1`, `UV_OFFLINE=1`, `UV_CACHE_DIR=/tmp/uv-cache`, and `PORT=8000`, remove `--reload`, and execute `/app/.venv/bin/uvicorn` directly via `exec` on `${PORT}`.

#### `[MODIFY]` @[docker-compose.yml#L1-L96]
Eliminate the duplicate `GOOGLE_APPLICATION_CREDENTIALS` entry in the `backend` service definition and replace legacy `STORAGE_BACKEND=LOCAL` and `USE_MOCK_DB=true` entries in `backend` and `worker` with `STORAGE_BACKEND=POSTGRES` and `USE_MOCK_DB=false`.

#### `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_system.py#L23-L49]
Add positive and ISTQB negative unit tests for `HealthCheckResponseDTO`.

#### `[MODIFY]` @[backend_v2/tests/unit/test_health.py#L16-L23]
Add positive and ISTQB negative unit tests for `get_system_health` (`status == "ok"`, `status == "degraded"` when `pool_manager` or `arq_pool` is uninitialized, `version == cfg.app_version`, and `AppException` translation).

#### `[MODIFY]` @[backend_v2/tests/unit/test_settings.py#L270-L294]
Add positive and ISTQB negative unit tests for `Settings.app_version` (`APP_VERSION` alias, `""`, `"   "`), `Settings.port` and `Settings.worker_health_port` (`PORT` and `WORKER_HEALTH_PORT` aliases, `0`, `65536`), GCP settings, `strip_trailing_slash` normalization (`"https://api.qrum.ai/"` and `"///"`), and unified production CORS validation (`["*"]`, `["https://*.qrum.ai"]`, `["http://qrum.ai"]`, `["https://qrum.ai/"]`, `["https://"]`, and `[]`).

#### `[MODIFY]` @[backend_v2/tests/unit/test_main.py#L182-L204]
Verify `app.version == get_settings().app_version`, `lifespan` shutdown resets `app.state.pool_manager` and `app.state.arq_pool` to `None`, and `validation_exception_handler` emits `"https://api.qrum.ai/errors/validation-failed"` without double slashes (`//`).

#### `[MODIFY]` @[backend_v2/tests/unit/test_run_worker.py#L11-L34]
Add positive and ISTQB negative unit tests for `_handle_health_probe` and `main()` Cloud Run health server lifecycle.

---

## 3. Pre-Implementation Technical Debt & Five-Axis System 2 Analysis

Pre-flight execution of `uv run python scripts/audit_technical_debt.py --plan docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md --include-one-hop` scanned all target files and 88 1-hop callers with **0 AST technical debt violations**. Manual System 2 and Tier 8 Red-Team inspection identified seven architectural deployment cleanups resolved across Phase 1 and Steps 2–3:

### Phase 1: Pre-Implementation Cleanups

1. **Wildcard CORS `["*"]`, Unencrypted HTTP, Partial Wildcards, Trailing Slashes & Empty-List Fallback in Production (`@[backend_v2/settings.py#L68-L1494]`, `@[backend_v2/settings.py#L1086-L1094]` & `@[backend_v2/main.py#L389-L423]`)**:
   - **Root Cause**: `cors_origins` in `Settings` defaults to `["*"]` even when `environment == "production"`, while `CORSMiddleware` in `backend_v2/main.py` sets `allow_credentials=True` and precedes middleware registration with a legacy `if not cors_origins: cors_origins = ["*"]` fallback. Splitting default assignment and validation across two `@model_validator(mode="after")` methods or checking only `"*" in self.cors_origins` creates implicit ordering dependencies and permits cleartext `"http://qrum.ai"`, partial wildcards (`"https://*.qrum.ai"`), trailing slashes (`"https://qrum.ai/"`), degenerate `"https://"`, or empty `cors_origins=[]`. Furthermore, injecting `CORS_ORIGINS` via `gcloud run deploy --set-env-vars` breaks CLI comma-delimited parsing because `pydantic-settings` requires a JSON array string (`json.loads()`).
   - **Cleanup Action**: Enforce `min_length=1` on `Settings.cors_origins`, remove `if not cors_origins: cors_origins = ["*"]` in `@[backend_v2/main.py#L389-L423]` (module-level `CORSMiddleware` setup), omit `CORS_ORIGINS` from Cloud Run environment variables, and consolidate production CORS handling inside `_enforce_environment_limits` (`@[backend_v2/settings.py#L68-L1494]`): when `self.environment == "production"`, if `"cors_origins" not in self.model_fields_set`, assign `self.cors_origins = [f"https://{self.primary_domain}", f"https://app.{self.primary_domain}", f"https://studio.{self.primary_domain}"]` (resolving to `["https://qrum.ai", "https://app.qrum.ai", "https://studio.qrum.ai"]` by default); then unconditionally verify `self.cors_origins` is non-empty and every `origin` in `self.cors_origins` satisfies `origin.startswith("https://")`, `"*" not in origin`, `not origin.endswith("/")`, and `len(origin) > len("https://")`, raising `ValueError` on any violation.
2. **Missing Centralized Cloud Run `$PORT` / `worker_health_port` & Application Version (`app_version`) Bindings in `Settings` (`@[backend_v2/settings.py#L68-L1494]`, `@[backend_v2/main.py#L182-L249]` & `@[backend_v2/api/routers/system/health.py#L29-L79]`)**:
   - **Root Cause**: Cloud Run injects a runtime `PORT` environment variable (`8080` default unless overridden), while application version `"2.9.0"` was hardcoded in `FastAPI(version="2.9.0", ...)` (`backend_v2/main.py`) and `get_system_health` (`backend_v2/api/routers/system/health.py`) without a centralized `Settings` SSOT field (`universal_ssot_and_normalization_mandate`, `strict_configuration_segregation`). Furthermore, on local Windows development hosts (`run_local.bat`), both `uvicorn` (bound to port `8000`) and `python -m backend_v2.run_worker` share the same host network stack, so binding the worker health listener to `default=8000` when `PORT` is unset would collide with `uvicorn`.
   - **Cleanup Action**: Declare `app_version: Annotated[str, BeforeValidator(strip_whitespace), Field(default="2.9.0", min_length=1, validation_alias=AliasChoices("app_version", "APP_VERSION"), description="Canonical application semantic version")] = "2.9.0"`, `port: Annotated[int, Field(default=8000, ge=1, le=65535, validation_alias=AliasChoices("port", "PORT"), description="Canonical HTTP listener port injected by Cloud Run or local runtime")] = 8000`, and `worker_health_port: Annotated[int, Field(default=8081, ge=1, le=65535, validation_alias=AliasChoices("worker_health_port", "WORKER_HEALTH_PORT", "PORT"), description="Canonical health probe listener port for the Arq background worker")] = 8081` on `Settings`, and bind `get_settings().app_version` in both `FastAPI(...)` and `get_system_health`.
3. **Unreachable `"degraded"` Health Status & Lifespan Readiness State Hygiene (`@[backend_v2/main.py#L182-L249]` & `@[backend_v2/api/routers/system/health.py#L29-L79]`)**:
   - **Root Cause**: Returning a hardcoded `status="ok"` in `get_system_health` renders the `"degraded"` literal in `HealthCheckResponseDTO` unreachable dead schema state and fails to report when `app.state.pool_manager` or `app.state.arq_pool` has not been initialized in `lifespan` or has been closed during shutdown. Furthermore, inspecting `request.app.state` via `getattr`/`hasattr` or `.get()` violates AST guardrails `QGR001` and `QGR002`.
   - **Cleanup Action**: Pre-initialize `app.state.arq_pool = None` and `app.state.pool_manager = None` at module scope in `@[backend_v2/main.py#L182-L249]`, reset both to `None` inside the `lifespan` `finally:` block on shutdown, and evaluate `is_ready = isinstance(request.app.state, State) and "pool_manager" in request.app.state._state and request.app.state.pool_manager is not None and "arq_pool" in request.app.state._state and request.app.state.arq_pool is not None` inside `get_system_health(request: Request)` to deterministically report `"ok"` vs. `"degraded"` in $O(1)$ memory with zero network I/O latency.
4. **Hardcoded `api.quorum.fi` Error Type URI & Double-Slash (`//`) Risk (`@[backend_v2/settings.py#L37-L48]` & `@[backend_v2/main.py#L389-L423]`)**:
   - **Root Cause**: `validation_exception_handler` in `@[backend_v2/main.py#L389-L423]` hardcodes `"type": "https://api.quorum.fi/errors/validation-failed"`, and interpolating `f"{get_settings().jwt_issuer}/errors/validation-failed"` without stripping trailing slashes from `JWT_ISSUER` (`"https://api.qrum.ai/"`) emits an invalid double-slash URI `"https://api.qrum.ai//errors/validation-failed"`.
   - **Cleanup Action**: Define `strip_trailing_slash(v: Any) -> Any` (`v.strip().rstrip("/")` when `isinstance(v, str)`) in `@[backend_v2/settings.py#L51-L62]`, bind `BeforeValidator(strip_trailing_slash)` with `Field(min_length=1)` on `Settings.jwt_issuer` and `Settings.jwt_audience`, and resolve `"type": f"{get_settings().jwt_issuer}/errors/validation-failed"` dynamically in `validation_exception_handler`.
5. **Non-Root `UID 10001` vs. `uv run` Permission Conflict & Hardcoded Port in `@[backend_v2/Dockerfile#L1-L36]`**:
   - **Root Cause**: Building `/app/.venv` as `root` and subsequently running `CMD ["uv", "run", "uvicorn", ..., "--port", "8000"]` as `USER quorum` (`UID 10001`) causes `uv` at container startup to attempt cache/lock writes into `root`-owned `/app/.venv` or `/home/quorum/.cache/uv` (`PermissionError`), adds cold-start latency, and fails to interpolate Cloud Run's `$PORT`.
   - **Cleanup Action**: Create `quorum` (`UID 10001`), `COPY --chown=quorum:quorum backend_v2 /app/backend_v2`, `RUN chown -R quorum:quorum /app/.venv`, set `ENV PYTHONPATH=/app VIRTUAL_ENV=/app/.venv PATH="/app/.venv/bin:$PATH" UV_NO_SYNC=1 UV_OFFLINE=1 UV_CACHE_DIR=/tmp/uv-cache PORT=8000`, switch to `USER quorum`, and invoke `CMD ["sh", "-c", "exec /app/.venv/bin/uvicorn backend_v2.main:app --host 0.0.0.0 --port ${PORT}"]`.
6. **Missing Cloud Run `$PORT` Health Listener in `quorum-worker` (`@[backend_v2/run_worker.py#L46-L66]`)**:
   - **Root Cause**: `main()` in `@[backend_v2/run_worker.py#L69-L116]` starts `await worker.async_run()` without opening a TCP/HTTP listening port, causing Cloud Run Service startup probes on `$PORT` to time out and terminate `quorum-worker`.
   - **Cleanup Action**: Add `_handle_health_probe` and wrap `await worker.async_run()` in `async with await asyncio.start_server(_handle_health_probe, host="0.0.0.0", port=get_settings().worker_health_port):` inside `@[backend_v2/run_worker.py#L46-L66]`, binding port `8081` locally when `PORT` is unset and Cloud Run's `$PORT` in container deployments.
7. **Legacy `STORAGE_BACKEND=LOCAL` & Duplicate Credential Env Var in `@[docker-compose.yml#L1-L96]`**:
   - **Root Cause**: `@[docker-compose.yml#L1-L96]` duplicates `GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json` on lines 19–20 and passes `STORAGE_BACKEND=LOCAL` on lines 15 and 42, which triggers an immediate `ConfigurationError` in `Settings.active_backend`.
   - **Cleanup Action**: Remove the duplicate `GOOGLE_APPLICATION_CREDENTIALS` line and set `STORAGE_BACKEND=POSTGRES` and `USE_MOCK_DB=false` in both `backend` and `worker` services.

### Canonical DTO Blueprint (`HealthCheckResponseDTO`)

```python
class HealthCheckResponseDTO(BaseResponseDTO):
    """Schema for Cloud Run and Cloud Load Balancer health probe responses."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    status: Annotated[Literal["ok", "degraded"], Field(default="ok", description="Service operational status")] = "ok"
    version: Annotated[str, Field(min_length=1, description="Application semantic version")]
    environment: Annotated[
        Literal["development", "production"], Field(description="Active runtime environment stage")
    ]
    storage_backend: Annotated[str, Field(min_length=1, description="Active storage backend identifier")]
    gcp_region: Annotated[str, Field(min_length=1, description="Configured GCP deployment region")]
    primary_domain: Annotated[str, Field(min_length=1, description="Canonical production domain")]
```

---

## 4. 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/settings.py#L51-L62]`, `@[backend_v2/settings.py#L51-L62]` & `@[backend_v2/settings.py#L51-L62]` (`strip_trailing_slash`, `Settings`, `_enforce_environment_limits`, `@[backend_v2/tests/unit/test_settings.py#L270-L294]`)** | Hardcoding `"2.9.0"` outside `Settings`, leaving wildcard `cors_origins = ["*"]` active in `production` mode, injecting `CORS_ORIGINS` via `gcloud run deploy --set-env-vars` (which breaks on comma delimiters), splitting CORS default assignment and validation across two `@model_validator(mode="after")` methods, checking only `"*" in self.cors_origins` while allowing `"http://..."`, `"https://*.qrum.ai"`, `"https://qrum.ai/"`, or `[]`, allowing trailing slashes in `primary_domain`/`jwt_issuer`/`jwt_audience`, colliding worker and API ports on `8000` in local `run_local.bat`, or reading `os.environ.get("PORT") or 8000` (`QGR016`). | Define `strip_trailing_slash` (`@[backend_v2/settings.py#L51-L62]`) and export in `__all__`; add PEP 593 `Annotated` fields `app_version` (`BeforeValidator(strip_whitespace), min_length=1, validation_alias=AliasChoices("app_version", "APP_VERSION")`), `port` (`default=8000, ge=1, le=65535, validation_alias=AliasChoices("port", "PORT")`), `worker_health_port` (`default=8081, ge=1, le=65535, validation_alias=AliasChoices("worker_health_port", "WORKER_HEALTH_PORT", "PORT")`), `gcp_project_id`, `gcp_region`, `primary_domain` (`BeforeValidator(strip_trailing_slash)`), `jwt_issuer` (`BeforeValidator(strip_trailing_slash)`), and `jwt_audience` (`BeforeValidator(strip_trailing_slash)`) to `Settings`; add `min_length=1` to `cors_origins`; inside `_enforce_environment_limits`, lock default production `cors_origins` to `[f"https://{self.primary_domain}", f"https://app.{self.primary_domain}", f"https://studio.{self.primary_domain}"]` when `"cors_origins" not in self.model_fields_set` and unconditionally validate that `self.cors_origins` is non-empty and every `origin` satisfies `origin.startswith("https://")`, `"*" not in origin`, `not origin.endswith("/")`, and `len(origin) > len("https://")`. | Prune the separate `validate_production_cors_origins` `@model_validator(mode="after")` method, runtime `CORS_ORIGINS` Cloud Run env var injection, runtime `pyproject.toml` file I/O parsing, and separate `GCPSettings` sub-models; keep all environment configuration and CORS invariants unified in `Settings` (`tripartite_configuration_segregation`). | `uv run python scripts/backend_audit_loop.py backend_v2/settings.py --test --ast-strict` and `test_settings.py::test_gcp_production_settings_and_cors_invariants` (including >=2 ISTQB negative tests for `app_version=""`, `app_version="   "`, `port=0`, `port=65536`, `worker_health_port=0`, `worker_health_port=65536`, `["*"]`, `["https://*.qrum.ai"]`, `["http://qrum.ai"]`, `["https://qrum.ai/"]`, `["https://"]`, `[]`, `jwt_issuer="///"`, and `primary_domain=""`). |
| **`@[backend_v2/main.py#L182-L249]` & `@[backend_v2/main.py#L182-L249]` (`lifespan`, `FastAPI`, `CORSMiddleware`, `validation_exception_handler`, `@[backend_v2/tests/unit/test_main.py#L182-L204]`)** | Hardcoding `version="2.9.0"` in `FastAPI(...)`, leaving `app.state.pool_manager` and `app.state.arq_pool` unset before `lifespan` or stale after shutdown, keeping `if not cors_origins: cors_origins = ["*"]` when configuring `CORSMiddleware`, and hardcoding `"https://api.quorum.fi/errors/validation-failed"` inside `validation_exception_handler`. | Bind `version=get_settings().app_version` on `FastAPI(...)`, pre-initialize `app.state.arq_pool = None` and `app.state.pool_manager = None` at module scope, reset both to `None` inside `lifespan`'s `finally:` block, pass `allow_origins=get_settings().cors_origins` directly to `CORSMiddleware`, and dynamically construct `"type": f"{get_settings().jwt_issuer}/errors/validation-failed"` using `Settings.jwt_issuer`. | Prune the legacy `if not cors_origins:` wildcard fallback, custom readiness polling tasks, and downstream `.rstrip("/")` string patching; rely directly on ingress-normalized `Settings` fields and `lifespan` state transitions. | `uv run python scripts/backend_audit_loop.py backend_v2/main.py --test --ast-strict` and `test_main.py::test_validation_exception_handler`. |
| **`@[backend_v2/models/dtos/system.py#L56-L75]` (`HealthCheckResponseDTO`, `@[backend_v2/tests/unit/models/dtos/test_system.py#L23-L49]`)** | Returning untyped naked dictionaries (`{"status": "ok"}`) from health check endpoints (`zero_naked_dicts_and_permissive_typing`). | Define `HealthCheckResponseDTO(BaseResponseDTO)` with `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")` and PEP 593 `Annotated` fields (`status`, `version`, `environment`, `storage_backend`, `gcp_region`, `primary_domain`). | Prune nested sub-DTO hierarchies for health probes; keep `HealthCheckResponseDTO` flat for O(1) Cloud Load Balancer serialization. | `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/system.py --test --ast-strict` and `test_system.py::test_health_check_response_dto_strictness` (>=2 ISTQB negative cases: extra field rejection and empty string rejection). |
| **`@[backend_v2/api/routers/system/health.py#L29-L79]` (`get_system_health`, `@[backend_v2/tests/unit/test_health.py#L16-L23]`)** | Creating a duplicate shadow router `backend_v2/routers/health.py` (`single_router_ssot_mandate`), hardcoding `status="ok"` and `version="2.9.0"`, or using `getattr`/`hasattr` (`QGR001`) or `.get()` (`QGR002`) to inspect `request.app.state`. | Add `GET /api/v2/system/health` (`get_system_health(request: Request)`) inside the canonical `@[backend_v2/api/routers/system/health.py#L29-L79]` router with `response_model=HealthCheckResponseDTO`, evaluating `is_ready = isinstance(request.app.state, State) and "pool_manager" in request.app.state._state and request.app.state.pool_manager is not None and "arq_pool" in request.app.state._state and request.app.state.arq_pool is not None` to set `status="ok"` vs. `"degraded"`, resolving `version=cfg.app_version`, and translating unexpected errors into `AppException(ErrorCodes.INTERNAL_SERVER_ERROR)` after `logger.error`. | Prune synchronous database or network ping calls (`SELECT 1` / `PING`) inside the liveness probe so Cloud Run health checks never block the FastAPI event loop (`non_blocking_fastapi`). | `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/system/health.py --test --ast-strict` and `test_health.py::test_get_system_health`, `test_health.py::test_get_system_health_degraded_when_state_uninitialized`, and `test_health.py::test_get_system_health_failure_raises_app_exception`. |
| **`@[backend_v2/run_worker.py#L46-L66]` (`_handle_health_probe`, `main`, `@[backend_v2/tests/unit/test_run_worker.py#L11-L34]`) & `@[backend_v2/Dockerfile#L1-L36]` & `@[docker-compose.yml#L1-L96]` (Container & Worker Runtime Hardening)** | Running `uv run` as non-root `UID 10001` against a `root`-owned `/app/.venv`, hardcoding uninterpolated `"--port", "8000"`, running `quorum-worker` on Cloud Run without a `$PORT` listener or colliding on port `8000` locally, or leaving `STORAGE_BACKEND=LOCAL` and duplicate `GOOGLE_APPLICATION_CREDENTIALS` in `@[docker-compose.yml#L1-L96]`. | In `@[backend_v2/run_worker.py#L46-L66]`, implement `_handle_health_probe` and bind `await asyncio.start_server(_handle_health_probe, host="0.0.0.0", port=get_settings().worker_health_port)` inside `async with health_server:` around `await worker.async_run()`. In `@[backend_v2/Dockerfile#L1-L36]`, create `quorum` (`UID 10001`), `chown -R quorum:quorum /app/.venv`, set `VIRTUAL_ENV`, `PATH`, `UV_NO_SYNC=1`, `UV_OFFLINE=1`, `UV_CACHE_DIR=/tmp/uv-cache`, `PORT=8000`, switch to `USER quorum`, and run `CMD ["sh", "-c", "exec /app/.venv/bin/uvicorn backend_v2.main:app --host 0.0.0.0 --port ${PORT}"]`. In `@[docker-compose.yml#L1-L96]`, deduplicate `GOOGLE_APPLICATION_CREDENTIALS` and set `STORAGE_BACKEND=POSTGRES` and `USE_MOCK_DB=false`. | Prune multi-container supervisor daemons (`supervisord`), OS threads (`threading.Thread`), and secondary FastAPI instances in the worker; Cloud Run manages `quorum-api` and `quorum-worker` as independent stateless services from the same image. | `uv run python scripts/backend_audit_loop.py backend_v2/run_worker.py --test --ast-strict`, `test_run_worker.py`, and `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md`. |

---

## 5. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Phase 1 Cleanups — Production Settings, $PORT Contract, CORS Lockdown &amp; Dynamic RFC 7807 Issuer URI">
    <Constraint invariant="tripartite_configuration_segregation">All environment configuration, application version, HTTP listener ports, GCP identifiers, and domain claims MUST reside centrally in backend_v2/settings.py using PEP 593 Annotated syntax.</Constraint>
    <Constraint invariant="zero_backward_compatibility_planning_ban">Production CORS origins MUST be consolidated in _enforce_environment_limits and fail fast with ValueError on any wildcard, non-HTTPS, trailing-slash, or empty origin without legacy main.py wildcard fallbacks.</Constraint>
    <action>Modify `@[backend_v2/settings.py#L68-L1494]` and `@[backend_v2/settings.py#L68-L1494]` (`Settings`) to:
      - Define `def strip_trailing_slash(v: Any) -> Any:` (`return v.strip().rstrip("/") if isinstance(v, str) else v`) alongside `strip_whitespace` (`@[backend_v2/settings.py#L37-L48]`) and export `"strip_trailing_slash"` in `__all__`.
      - Update `cors_origins` to enforce `min_length=1`: `cors_origins: Annotated[list[str], Field(default_factory=lambda: ["*"], min_length=1, description="Allowed CORS Origins")]`.
      - Add PEP 593 `Annotated` fields:
        - `app_version: Annotated[str, BeforeValidator(strip_whitespace), Field(default="2.9.0", min_length=1, validation_alias=AliasChoices("app_version", "APP_VERSION"), description="Canonical application semantic version")] = "2.9.0"`
        - `port: Annotated[int, Field(default=8000, ge=1, le=65535, validation_alias=AliasChoices("port", "PORT"), description="Canonical HTTP listener port injected by Cloud Run or local runtime")] = 8000`
        - `worker_health_port: Annotated[int, Field(default=8081, ge=1, le=65535, validation_alias=AliasChoices("worker_health_port", "WORKER_HEALTH_PORT", "PORT"), description="Canonical health probe listener port for the Arq background worker")] = 8081`
        - `gcp_project_id: Annotated[str, BeforeValidator(strip_whitespace), Field(default="cognitive-quorum", min_length=1, validation_alias=AliasChoices("gcp_project_id", "GCP_PROJECT", "GOOGLE_CLOUD_PROJECT"), description="Canonical Google Cloud project identifier")] = "cognitive-quorum"`
        - `gcp_region: Annotated[str, BeforeValidator(strip_whitespace), Field(default="europe-north1", min_length=1, validation_alias=AliasChoices("gcp_region", "GCP_REGION"), description="Canonical Google Cloud deployment region")] = "europe-north1"`
        - `primary_domain: Annotated[str, BeforeValidator(strip_trailing_slash), Field(default="qrum.ai", min_length=1, validation_alias=AliasChoices("primary_domain", "PRIMARY_DOMAIN"), description="Primary global B2B SaaS domain")] = "qrum.ai"`
        - `jwt_issuer: Annotated[str, BeforeValidator(strip_trailing_slash), Field(default="https://api.qrum.ai", min_length=1, validation_alias=AliasChoices("jwt_issuer", "JWT_ISSUER"), description="Canonical RFC 8693 Quorum Local JWT issuer claim")] = "https://api.qrum.ai"`
        - `jwt_audience: Annotated[str, BeforeValidator(strip_trailing_slash), Field(default="https://qrum.ai", min_length=1, validation_alias=AliasChoices("jwt_audience", "JWT_AUDIENCE"), description="Canonical RFC 8693 Quorum Local JWT audience claim")] = "https://qrum.ai"`
      - Update `frontend_app_base_url` to normalize trailing slashes via `BeforeValidator(strip_trailing_slash)` and explicit `AliasChoices`: `frontend_app_base_url: Annotated[str, BeforeValidator(strip_trailing_slash), Field(default="https://app.qrum.ai", min_length=8, validation_alias=AliasChoices("frontend_app_base_url", "FRONTEND_APP_BASE_URL"), description="Canonical frontend base URL for constructing /task/<token> and invitation links")] = "https://app.qrum.ai"`.
      - Update `postgres_dsn` (`@[backend_v2/settings.py#L68-L1494]`) to bind `DATABASE_URL` injected by GCP Secret Manager: `postgres_dsn: Annotated[str | None, BeforeValidator(strip_whitespace), Field(default=None, validation_alias=AliasChoices("postgres_dsn", "POSTGRES_DSN", "DATABASE_URL"), description="Optional environment-injected PostgreSQL DSN override.")] = None`.
      - Update `has_vertex` in `model_post_init` and `enabled_providers` (`@[backend_v2/settings.py#L1173-L1212]`) to include `"GCP_PROJECT"` alongside `"VERTEX_PROJECT_ID"`, `"GOOGLE_APPLICATION_CREDENTIALS"`, and `"GOOGLE_CLOUD_PROJECT"` (and `self.use_vertex_llm` in `enabled_providers`) so Cloud Run IAM Service Account workloads authenticate via ADC without requiring a local `service-account.json` file.
    </action>
    <action>Modify `_enforce_environment_limits` in `@[backend_v2/settings.py#L1214-L1302]` to deterministically consolidate production CORS default assignment and validation in a single `@model_validator(mode="after")` pass: when `self.environment == "production"`, first set `self.cors_origins = [f"https://{self.primary_domain}", f"https://app.{self.primary_domain}", f"https://studio.{self.primary_domain}"]` (resolving to `["https://qrum.ai", "https://app.qrum.ai", "https://studio.qrum.ai"]` by default without requiring `CORS_ORIGINS` in Cloud Run environment variables) if `"cors_origins" not in self.model_fields_set`; then unconditionally validate that `self.cors_origins` is non-empty and every `origin` in `self.cors_origins` satisfies `origin.startswith("https://")`, `"*" not in origin`, `not origin.endswith("/")`, and `len(origin) > len("https://")`, raising `ValueError` immediately if any origin violates these production security invariants.</action>
    <action>Modify `@[backend_v2/main.py#L182-L249]` and `@[backend_v2/main.py#L182-L249]` to reset `app.state.arq_pool = None` and `app.state.pool_manager = None` inside the `finally:` block of `lifespan`, bind `version=get_settings().app_version` on `FastAPI(...)` and pre-initialize `app.state.arq_pool = None` and `app.state.pool_manager = None` at module scope, remove the legacy `if not cors_origins: cors_origins = ["*"]` fallback block when configuring `CORSMiddleware` (passing `allow_origins=get_settings().cors_origins` directly), and replace the hardcoded `"https://api.quorum.fi/errors/validation-failed"` string in `validation_exception_handler` (`@[backend_v2/main.py#L182-L249]`) with `f"{get_settings().jwt_issuer}/errors/validation-failed"`.</action>
    <action>Modify `@[backend_v2/tests/unit/test_settings.py#L270-L294]` and `@[backend_v2/tests/unit/test_main.py#L182-L204]` to add unit tests and >=2 ISTQB negative boundary tests covering: (1) default `app_version == "2.9.0"`, `APP_VERSION` override, and `ValidationError` on empty/whitespace `app_version=""` or `"   "`, (2) default `port == 8000` and `worker_health_port == 8081` (preventing local `run_local.bat` port collision), `PORT=8080` alias resolution for both `port` and `worker_health_port`, and `WORKER_HEALTH_PORT=9091` precedence, (3) `ValidationError` when `port=0`, `port=65536`, `worker_health_port=0`, or `worker_health_port=65536` (ISTQB `min-1` / `max+1` bounds), (4) default production CORS origin locking to `["https://qrum.ai", "https://app.qrum.ai", "https://studio.qrum.ai"]` when `CORS_ORIGINS` is unset (and dynamic `PRIMARY_DOMAIN` rotation parity), (5) `ValidationError` in `production` mode when `cors_origins` contains `"*"`, partial wildcard `"https://*.qrum.ai"`, cleartext `"http://qrum.ai"`, trailing slash `"https://qrum.ai/"`, scheme-only `"https://"`, or is empty `[]`, (6) `primary_domain`, `jwt_issuer`, and `jwt_audience` trailing-slash normalization (`"https://api.qrum.ai/"` -> `"https://api.qrum.ai"`) and `ValidationError` on slash-only `"///"` or empty `primary_domain=""`, and (7) `app.version == get_settings().app_version`, `lifespan` shutdown resetting `app.state.pool_manager` and `app.state.arq_pool` to `None`, and `validation_exception_handler` RFC 7807 `type` URI matching `"https://api.qrum.ai/errors/validation-failed"` without double slashes (`//`).</action>
    <action>Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/settings.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/main.py --test --ast-strict`.</action>
  </step>

  <step id="2" name="Typed HealthCheckResponseDTO &amp; System Health Endpoint">
    <Constraint invariant="zero_naked_dicts_and_permissive_typing">Health check responses MUST use an immutable Pydantic V2 DTO inheriting from BaseResponseDTO with ConfigDict(frozen=True, strict=True, extra="forbid"). Returning naked dictionaries, using getattr/hasattr (QGR001), or calling .get() (QGR002) is strictly forbidden.</Constraint>
    <Constraint invariant="single_router_ssot_mandate">Health endpoints MUST reside inside the existing canonical system router backend_v2/api/routers/system/health.py without creating shadow router files.</Constraint>
    <action>Modify `@[backend_v2/models/dtos/system.py#L56-L75]` to define `HealthCheckResponseDTO(BaseResponseDTO)` with `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")` and fields:
      - `status: Annotated[Literal["ok", "degraded"], Field(default="ok", description="Service operational status")] = "ok"`
      - `version: Annotated[str, Field(min_length=1, description="Application semantic version")]`
      - `environment: Annotated[Literal["development", "production"], Field(description="Active runtime environment stage")]`
      - `storage_backend: Annotated[str, Field(min_length=1, description="Active storage backend identifier")]`
      - `gcp_region: Annotated[str, Field(min_length=1, description="Configured GCP deployment region")]`
      - `primary_domain: Annotated[str, Field(min_length=1, description="Canonical production domain")]`
      Export `"HealthCheckResponseDTO"` in `__all__`.
    </action>
    <action>Modify `@[backend_v2/api/routers/system/health.py#L29-L79]` to add `GET /api/v2/system/health` (`async def get_system_health(request: Request) -> HealthCheckResponseDTO:`) with `response_model=HealthCheckResponseDTO`. Inside `get_system_health`, resolve `cfg = get_settings()`, evaluate $O(1)$ in-memory readiness via `is_ready = isinstance(request.app.state, State) and "pool_manager" in request.app.state._state and request.app.state.pool_manager is not None and "arq_pool" in request.app.state._state and request.app.state.arq_pool is not None`, set `health_status: Literal["ok", "degraded"] = "ok" if is_ready else "degraded"`, return `HealthCheckResponseDTO(status=health_status, version=cfg.app_version, environment=cfg.environment, storage_backend=cfg.active_backend.value, gcp_region=cfg.gcp_region, primary_domain=cfg.primary_domain)`, and catch unexpected exceptions with `logger.error` + `raise AppException(ErrorCodes.INTERNAL_SERVER_ERROR) from e` (RFC 7807 Dual-Reporting).</action>
    <action>Modify `@[backend_v2/tests/unit/models/dtos/test_system.py#L23-L49]` and `@[backend_v2/tests/unit/test_health.py#L100-L119]` to add unit tests and >=2 ISTQB negative boundary tests per feature: (1) valid `HealthCheckResponseDTO` instantiation, (2) `ValidationError` on unrecognized extra key (`extra="forbid"`), (3) `ValidationError` on empty `version=""` or invalid `status`, (4) `GET /api/v2/system/health` returning `200 OK` with `status == "ok"` and `version == cfg.app_version` when `pool_manager` and `arq_pool` are initialized on `request.app.state`, (5) `test_get_system_health_degraded_when_state_uninitialized` returning `status == "degraded"` when `pool_manager` or `arq_pool` is `None` or missing on `request.app.state`, and (6) `test_get_system_health_failure_raises_app_exception` raising `AppException(ErrorCodes.INTERNAL_SERVER_ERROR)` with structured logging when an unexpected error occurs.</action>
    <action>Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/system.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/system/health.py --test --ast-strict`.</action>
  </step>

  <step id="3" name="Cloud Run Worker Health Probe Responder, Non-Root Dockerfile &amp; Docker Compose Hardening">
    <Constraint invariant="credential_hardcoding_ban">Containers MUST NOT bake credentials, run Uvicorn with --reload, or execute runtime uv sync/cache writes as non-root UID 10001.</Constraint>
    <Constraint invariant="unbounded_io_timeout_mandate">Worker health probe stream reads MUST specify an explicit timeout resolved from Settings.http_client_timeout_seconds and close streams deterministically.</Constraint>
    <action>Modify `@[backend_v2/run_worker.py#L69-L116]` to define `_HEALTH_RESPONSE_BYTES` and `async def _handle_health_probe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:` (reading up to 1024 bytes via `await asyncio.wait_for(reader.read(1024), timeout=get_settings().http_client_timeout_seconds)`, writing `HTTP/1.1 200 OK` JSON `"status":"ok"` bytes, and closing `writer` in `finally:`), and update `main()` to start `health_server = await asyncio.start_server(_handle_health_probe, host="0.0.0.0", port=get_settings().worker_health_port)` and execute `await worker.async_run()` inside `async with health_server:`.</action>
    <action>Modify `@[backend_v2/tests/unit/test_run_worker.py#L11-L34]` to add positive and >=2 ISTQB negative unit tests covering: (1) `main()` binding `asyncio.start_server` on `get_settings().worker_health_port` while running `worker.async_run()`, (2) `_handle_health_probe` returning `HTTP/1.1 200 OK` and closing the stream writer, (3) `_handle_health_probe` handling stream read timeout / disconnect gracefully while still closing `writer`, and (4) `main()` translating health server bind failures into `AppException(ErrorCodes.SERVICE_UNAVAILABLE)`.</action>
    <action>Modify `@[backend_v2/Dockerfile#L1-L36]` to create a dedicated non-root user (`RUN useradd --create-home --uid 10001 quorum`), copy application code with `--chown=quorum:quorum`, run `chown -R quorum:quorum /app/.venv`, set `ENV PYTHONPATH=/app VIRTUAL_ENV=/app/.venv PATH="/app/.venv/bin:$PATH" UV_NO_SYNC=1 UV_OFFLINE=1 UV_CACHE_DIR=/tmp/uv-cache PORT=8000`, switch to `USER quorum`, and update `CMD` to `["sh", "-c", "exec /app/.venv/bin/uvicorn backend_v2.main:app --host 0.0.0.0 --port ${PORT}"]` (removing `--reload` and runtime `uv run` wrapper).</action>
    <action>Modify `@[docker-compose.yml#L1-L96]` to remove the duplicate `- GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json` line in the `backend` service definition and update `STORAGE_BACKEND=POSTGRES` and `USE_MOCK_DB=false` in both `backend` and `worker` services.</action>
    <action>Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/run_worker.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_run_worker.py --test --ast-strict`.</action>
  </step>

  <step id="4" name="Global Quality Gate &amp; Completion Verification">
    <Constraint invariant="fragmented_quality_gates_prevention">Run the full 10-stage backend audit loop across backend_v2/ to prove zero regressions.</Constraint>
    <action>Execute the global backend completion gate: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Execute final live E2E verification gate when live credentials are active (Windows PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`).</action>
  </step>
</execution_protocol>
```
