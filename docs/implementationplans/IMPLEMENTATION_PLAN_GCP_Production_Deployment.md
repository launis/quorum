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

This implementation plan realizes **EPIC 74** (`@[docs/epic/EPIC_74_Production_Deployment_GCP.md]`), hardening Cognitive Quorum's backend configuration, health probes, container entrypoints, and multi-domain origin security for stateless production deployment on **Google Cloud Platform (`europe-north1` / Finland)**. Built atop the All-in-PostgreSQL 19 Sovereign Zero-ORM Architecture (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`) and B2B SaaS IAM & Enterprise Hardening (`@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`), this plan enforces four sovereign production invariants:

1. **Global Config Sovereignty for GCP & `qrum.ai` Domain Claims (`@[backend_v2/settings.py#L54-L1053]`)**:
   - Declares strongly typed PEP 593 `Annotated` fields on `Settings`: `gcp_project_id` (`"cognitive-quorum"`), `gcp_region` (`"europe-north1"`), `primary_domain` (`"qrum.ai"`), `jwt_issuer` (`"https://api.qrum.ai"`), and `jwt_audience` (`"https://qrum.ai"`).
   - Enforces closed-set production CORS origin security inside `_enforce_environment_limits` (`@[backend_v2/settings.py#L847-L908]`): when `environment == "production"` and `"cors_origins" not in self.model_fields_set`, `self.cors_origins` is deterministically set to `["https://qrum.ai", "https://app.qrum.ai", "https://studio.qrum.ai"]`.
   - Enforces a Fail-Fast `@model_validator(mode="after")` (`validate_production_cors_origins`) on `Settings`: if `environment == "production"` and `"*"` is explicitly passed in `cors_origins` (`"cors_origins" in self.model_fields_set`), immediately raise `ValueError` to prevent wildcard CORS with `allow_credentials=True` in production.
2. **Dynamic RFC 7807 Problem Type URI Sovereignty (`@[backend_v2/main.py#L347-L380]`)**:
   - Replaces the hardcoded legacy domain `"https://api.quorum.fi/errors/validation-failed"` inside `validation_exception_handler` (`@[backend_v2/main.py#L347-L380]`) with `f"{get_settings().jwt_issuer}/errors/validation-failed"` (resolving to `"https://api.qrum.ai/errors/validation-failed"`), ensuring 100% domain consistency with `qrum.ai`.
3. **Typed Cloud Run & Load Balancer Health Probe (`@[backend_v2/models/dtos/system.py#L43-L52]` & `@[backend_v2/api/routers/system/health.py#L20-L52]`)**:
   - Create `HealthCheckResponseDTO` (`class HealthCheckResponseDTO(BaseResponseDTO)`) defined in `@[backend_v2/models/dtos/system.py#L43-L52]` with `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")`, completely eliminating naked dictionary health responses (`zero_naked_dicts_and_permissive_typing`, `data_leak_prevention_firewall`).
   - Exposes `GET /api/v2/system/health` (`get_system_health`) in `@[backend_v2/api/routers/system/health.py#L20-L52]` with `response_model=HealthCheckResponseDTO` and RFC 7807 Dual-Reporting error translation for Cloud Run startup/liveness probes and Cloud Load Balancer health checks.
4. **Stateless Container & Compose Hardening (`@[backend_v2/Dockerfile]` & `@[docker-compose.yml]`)**:
   - Removes the development `--reload` flag from `@[backend_v2/Dockerfile]`, creates a dedicated non-root `quorum` user (`UID 10001`), and removes the duplicate `GOOGLE_APPLICATION_CREDENTIALS` environment entry in `@[docker-compose.yml]`.

### 1.1 `qrum.ai` Domain Acquisition, Cloud DNS & SAN SSL Protocol

1. **Domain Availability Verification & Acquisition (`qrum.ai`)**:
   - `whois.nic.ai` registry verification confirms `qrum.ai` is officially available to register as the 4-letter ultra-short global domain.
   - Register `qrum.ai` via Google Cloud Domains (`gcloud domains registrations search-domains qrum.ai`) or an accredited domain registrar (e.g., Cloudflare Registrar), and delegate authoritative nameservers (`NS` records) to Google Cloud DNS (`qrum-ai-zone`).
   - Inject domain settings at runtime via Cloud Run environment variables (`PRIMARY_DOMAIN=qrum.ai`, `JWT_ISSUER=https://api.qrum.ai`, `JWT_AUDIENCE=https://qrum.ai`, `CORS_ORIGINS`). Because `Settings` (`@[backend_v2/settings.py#L54-L1053]`) resolves all domain and JWT claims via `AliasChoices`, zero Python or Flutter source code edits are required.
2. **Cloud DNS Zone, Global Anycast IP & Google-Managed SAN SSL Provisioning (PowerShell)**:
   ```powershell
   gcloud domains registrations search-domains qrum.ai
   gcloud compute addresses create qrum-global-ip --global --ip-version IPV4
   gcloud dns managed-zones create qrum-ai-zone --dns-name="qrum.ai." --description="Quorum Primary Production DNS Zone" --visibility=public
   gcloud dns record-sets create qrum.ai. --zone=qrum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
   gcloud dns record-sets create api.qrum.ai. --zone=qrum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
   gcloud dns record-sets create app.qrum.ai. --zone=qrum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
   gcloud dns record-sets create studio.qrum.ai. --zone=qrum-ai-zone --type=A --ttl=300 --rrdatas="GLOBAL_ANYCAST_IP"
   gcloud compute ssl-certificates create qrum-san-cert --domains="qrum.ai,api.qrum.ai,app.qrum.ai,studio.qrum.ai" --global
   ```

---

## 2. Scope & Target Boundaries

### TARGET Files (Authorized for Modification)

| Category | File Reference | Architectural Responsibility |
| :--- | :--- | :--- |
| `[MODIFY]` | `@[backend_v2/settings.py#L54-L1053]` | Add `gcp_project_id`, `gcp_region`, `primary_domain`, `jwt_issuer`, and `jwt_audience` fields to `Settings`; lock production `cors_origins` in `_enforce_environment_limits` (`@[backend_v2/settings.py#L847-L908]`) and add `validate_production_cors_origins` `@model_validator(mode="after")`. |
| `[MODIFY]` | `@[backend_v2/models/dtos/system.py#L43-L52]` | Add `HealthCheckResponseDTO(BaseResponseDTO)` with `ConfigDict(frozen=True, strict=True, extra="forbid")` and export in `__all__`. |
| `[MODIFY]` | `@[backend_v2/api/routers/system/health.py#L20-L52]` | Implement `GET /api/v2/system/health` (`get_system_health`) returning `HealthCheckResponseDTO` with RFC 7807 Dual-Reporting. |
| `[MODIFY]` | `@[backend_v2/main.py#L347-L380]` | Replace hardcoded `"https://api.quorum.fi/errors/validation-failed"` in `validation_exception_handler` with `f"{get_settings().jwt_issuer}/errors/validation-failed"`. |
| `[MODIFY]` | `@[backend_v2/Dockerfile]` | Remove `--reload` from `CMD` and configure non-root `quorum` container user for Cloud Run security compliance. |
| `[MODIFY]` | `@[docker-compose.yml]` | Remove duplicate `GOOGLE_APPLICATION_CREDENTIALS` environment variable line in `backend` service. |
| `[MODIFY]` | `@[backend_v2/tests/unit/models/dtos/test_system.py#L7-L12]` | Add positive and ISTQB negative boundary tests for `HealthCheckResponseDTO`. |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_health.py#L14-L19]` | Add positive and ISTQB negative unit tests for `get_system_health` (`GET /api/v2/system/health`). |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_settings.py#L264-L290]` | Add positive and ISTQB negative unit tests for GCP settings, closed production CORS origins, and wildcard CORS rejection in production. |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_main.py#L172-L189]` | Assert `validation_exception_handler` RFC 7807 `type` URI dynamically uses `https://api.qrum.ai/errors/validation-failed`. |

### CONTEXT Files (Strictly Read-Only)

- `@[docs/epic/EPIC_74_Production_Deployment_GCP.md]`
- `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`
- `@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]`
- `@[backend_v2/worker.py]`
- `@[backend_v2/exceptions.py]`

---

### `[MODIFY]` Target Details

#### `[MODIFY]` @[backend_v2/settings.py#L54-L1053]
Add GCP deployment and `qrum.ai` domain sovereignty fields (`gcp_project_id`, `gcp_region`, `primary_domain`, `jwt_issuer`, `jwt_audience`) to `Settings` (`@[backend_v2/settings.py#L54-L1053]`), lock default production `cors_origins` in `_enforce_environment_limits` (`@[backend_v2/settings.py#L847-L908]`), and add `validate_production_cors_origins` validator.

#### `[MODIFY]` @[backend_v2/models/dtos/system.py#L43-L52]
Define `HealthCheckResponseDTO(BaseResponseDTO)` with `ConfigDict(frozen=True, strict=True, extra="forbid")` and export it in `__all__`.

#### `[MODIFY]` @[backend_v2/api/routers/system/health.py#L20-L52]
Add `get_system_health` (`GET /api/v2/system/health`) returning `HealthCheckResponseDTO` with RFC 7807 Dual-Reporting error handling.

#### `[MODIFY]` @[backend_v2/main.py#L347-L380]
Update `validation_exception_handler` (`@[backend_v2/main.py#L347-L380]`) to resolve the RFC 7807 `type` URI from `get_settings().jwt_issuer`.

#### `[MODIFY]` @[backend_v2/Dockerfile]
Remove `--reload` from Uvicorn `CMD` and configure a non-root `quorum` user for Cloud Run production containers.

#### `[MODIFY]` @[docker-compose.yml]
Eliminate the duplicate `GOOGLE_APPLICATION_CREDENTIALS` entry in the `backend` service definition.

#### `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_system.py#L7-L12]
Add positive and ISTQB negative unit tests for `HealthCheckResponseDTO`.

#### `[MODIFY]` @[backend_v2/tests/unit/test_health.py#L14-L19]
Add positive and ISTQB negative unit tests for `get_system_health`.

#### `[MODIFY]` @[backend_v2/tests/unit/test_settings.py#L264-L290]
Add positive and ISTQB negative unit tests for GCP settings and production CORS validation.

#### `[MODIFY]` @[backend_v2/tests/unit/test_main.py#L172-L189]
Verify `validation_exception_handler` emits `"https://api.qrum.ai/errors/validation-failed"`.

---

## 3. Pre-Implementation Technical Debt & Five-Axis System 2 Analysis

Pre-flight execution of `uv run python scripts/audit_technical_debt.py --plan docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md --include-one-hop` scanned all 9 target files and 65 1-hop callers. Production target files had **0 AST technical debt violations**, while test target scanning surfaced `TD_ISTQB_NEGATIVE` on `@[backend_v2/tests/unit/test_health.py#L14-L19]` (missing negative `test_*_failure` / `test_*_error` partitions) and 2 advisory `TD_MODEL_FACTORY` notices on intentional negative validation dict inputs in `test_system.py` and `test_main.py` (exempted under `QGR029` for `pytest.raises(ValidationError): Model.model_validate(...)`). Manual System 2 inspection identified four architectural deployment cleanups resolved in Phase 1:

### Phase 1: Pre-Implementation Cleanups

1. **Missing ISTQB Negative Partition in Health Router Test Suite (`TD_ISTQB_NEGATIVE` in `@[backend_v2/tests/unit/test_health.py#L14-L19]`)**:
   - **Root Cause**: `@[backend_v2/tests/unit/test_health.py#L14-L19]` only tested the happy path of `get_system_hooks` and lacked `test_*_failure` / `test_*_error` negative test coverage.
   - **Cleanup Action**: Add negative failure partition tests (`test_get_system_hooks_failure_raises_app_exception` and `test_get_system_health_failure_raises_app_exception`) exercising RFC 7807 `AppException(ErrorCodes.INTERNAL_SERVER_ERROR)` translation.
2. **Wildcard CORS `["*"]` Default in Production (`@[backend_v2/settings.py#L54-L1053]` & `@[backend_v2/settings.py#L847-L908]`)**:
   - **Root Cause**: `cors_origins` in `Settings` defaults to `["*"]` even when `environment == "production"`, while `CORSMiddleware` in `backend_v2/main.py` sets `allow_credentials=True`. Leaving wildcard `["*"]` active in production violates B2B SaaS origin isolation (`qrum.ai`).
   - **Cleanup Action**: In `_enforce_environment_limits` (`@[backend_v2/settings.py#L847-L908]`), when `self.environment == "production"` and `"cors_origins" not in self.model_fields_set`, assign `self.cors_origins = ["https://qrum.ai", "https://app.qrum.ai", "https://studio.qrum.ai"]`. Add `@model_validator(mode="after")` `validate_production_cors_origins` raising `ValueError` if `self.environment == "production"`, `"cors_origins" in self.model_fields_set`, and `"*"` is in `self.cors_origins`.
3. **Hardcoded `api.quorum.fi` Error Type URI (`@[backend_v2/main.py#L347-L380]`)**:
   - **Root Cause**: `validation_exception_handler` in `@[backend_v2/main.py#L347-L380]` hardcodes `"type": "https://api.quorum.fi/errors/validation-failed"`, violating `localhost_endpoint_hardcoding_ban` and drifting from the canonical `https://api.qrum.ai` issuer domain.
   - **Cleanup Action**: Resolve `"type": f"{get_settings().jwt_issuer}/errors/validation-failed"` dynamically from `Settings.jwt_issuer`.
4. **Container `--reload` Flag & Duplicate Compose Env Var (`@[backend_v2/Dockerfile]` & `@[docker-compose.yml]`)**:
   - **Root Cause**: `@[backend_v2/Dockerfile]` runs `uvicorn` with `--reload` in production and runs as `root`, while `@[docker-compose.yml]` duplicates `- GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json` on lines 19 and 20.
   - **Cleanup Action**: Remove `--reload` from `@[backend_v2/Dockerfile]`, add a non-root `quorum` user, and deduplicate `GOOGLE_APPLICATION_CREDENTIALS` in `@[docker-compose.yml]`.

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
| **`@[backend_v2/settings.py#L54-L1053]` & `@[backend_v2/settings.py#L847-L908]` (`Settings`, `_enforce_environment_limits`, `@[backend_v2/tests/unit/test_settings.py#L264-L290]`)** | Leaving wildcard `cors_origins = ["*"]` active in `production` mode or hardcoding GCP project/domain strings across routers and services. | Add PEP 593 `Annotated` fields `gcp_project_id`, `gcp_region`, `primary_domain`, `jwt_issuer`, and `jwt_audience` to `Settings`; lock default production `cors_origins` to `qrum.ai` origins in `_enforce_environment_limits`; raise `ValueError` in `validate_production_cors_origins` if `"*"` is explicitly passed in `production`. | Prune separate `GCPSettings` sub-models or external YAML config loaders; keep all environment configuration in the single `Settings` SSOT (`tripartite_configuration_segregation`). | `uv run python scripts/backend_audit_loop.py backend_v2/settings.py --test --ast-strict` and `test_settings.py::test_gcp_production_settings_and_cors_invariants` (including >=2 ISTQB negative tests for explicit `"*"` in production and empty `primary_domain`). |
| **`@[backend_v2/main.py#L347-L380]` (`validation_exception_handler`, `@[backend_v2/tests/unit/test_main.py#L172-L189]`)** | Hardcoding `"https://api.quorum.fi/errors/validation-failed"` inside `validation_exception_handler`. | Dynamically construct `"type": f"{get_settings().jwt_issuer}/errors/validation-failed"` using `Settings.jwt_issuer` (`"https://api.qrum.ai"`). | Prune custom URL builder classes; interpolate directly from `get_settings().jwt_issuer`. | `uv run python scripts/backend_audit_loop.py backend_v2/main.py --test --ast-strict` and `test_main.py::test_validation_exception_handler`. |
| **`@[backend_v2/models/dtos/system.py#L43-L52]` (`HealthCheckResponseDTO`, `@[backend_v2/tests/unit/models/dtos/test_system.py#L7-L12]`)** | Returning untyped naked dictionaries (`{"status": "ok"}`) from health check endpoints (`zero_naked_dicts_and_permissive_typing`). | Define `HealthCheckResponseDTO(BaseResponseDTO)` with `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")` and PEP 593 `Annotated` fields (`status`, `version`, `environment`, `storage_backend`, `gcp_region`, `primary_domain`). | Prune nested sub-DTO hierarchies for health probes; keep `HealthCheckResponseDTO` flat for O(1) Cloud Load Balancer serialization. | `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/system.py --test --ast-strict` and `test_system.py::test_health_check_response_dto_strictness` (>=2 ISTQB negative cases: extra field rejection and empty string rejection). |
| **`@[backend_v2/api/routers/system/health.py#L20-L52]` (`get_system_health`, `@[backend_v2/tests/unit/test_health.py#L14-L19]`)** | Creating a duplicate shadow router `backend_v2/routers/health.py` (`single_router_ssot_mandate`) or omitting `response_model` and RFC 7807 error handling. | Add `GET /api/v2/system/health` (`get_system_health`) inside the canonical `@[backend_v2/api/routers/system/health.py#L20-L52]` router with `response_model=HealthCheckResponseDTO`, resolving `get_settings()` and translating unexpected errors into `AppException(ErrorCodes.INTERNAL_SERVER_ERROR)` after `logger.error`. | Prune synchronous database or network ping calls inside the liveness probe so Cloud Run health checks never block the FastAPI event loop (`non_blocking_fastapi`). | `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/system/health.py --test --ast-strict` and `test_health.py::test_get_system_health` + `test_health.py::test_get_system_health_failure_raises_app_exception`. |
| **`@[backend_v2/Dockerfile]` & `@[docker-compose.yml]` (Container Runtime Hardening)** | Running Uvicorn with `--reload` in production containers, running container processes as `root`, or duplicating `GOOGLE_APPLICATION_CREDENTIALS` in `@[docker-compose.yml]`. | Remove `--reload` from `@[backend_v2/Dockerfile]`, create and switch to non-root user `quorum` (`UID 10001`), and deduplicate `GOOGLE_APPLICATION_CREDENTIALS` in `@[docker-compose.yml]`. | Prune multi-container supervisor daemons (`supervisord`); Cloud Run manages `quorum-api` and `quorum-worker` as independent stateless services from the same image. | Verified via `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_GCP_Production_Deployment.md` and global `backend_audit_loop.py`. |

---

## 5. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Phase 1 Cleanups — Production Settings, CORS Lockdown &amp; Dynamic RFC 7807 Issuer URI">
    <Constraint invariant="tripartite_configuration_segregation">All environment configuration, GCP identifiers, and domain claims MUST reside centrally in backend_v2/settings.py using PEP 593 Annotated syntax.</Constraint>
    <Constraint invariant="zero_backward_compatibility_planning_ban">Wildcard CORS origins in production mode MUST fail fast with ValueError when explicitly configured.</Constraint>
    <action>Modify `@[backend_v2/settings.py#L54-L1053]` (`Settings`) to add PEP 593 `Annotated` fields:
      - `gcp_project_id: Annotated[str, BeforeValidator(strip_whitespace), Field(default="cognitive-quorum", min_length=1, validation_alias=AliasChoices("gcp_project_id", "GCP_PROJECT", "GOOGLE_CLOUD_PROJECT"), description="Canonical Google Cloud project identifier")] = "cognitive-quorum"`
      - `gcp_region: Annotated[str, BeforeValidator(strip_whitespace), Field(default="europe-north1", min_length=1, validation_alias=AliasChoices("gcp_region", "GCP_REGION"), description="Canonical Google Cloud deployment region")] = "europe-north1"`
      - `primary_domain: Annotated[str, BeforeValidator(strip_whitespace), Field(default="qrum.ai", min_length=1, validation_alias=AliasChoices("primary_domain", "PRIMARY_DOMAIN"), description="Primary global B2B SaaS domain")] = "qrum.ai"`
      - `jwt_issuer: Annotated[str, BeforeValidator(strip_whitespace), Field(default="https://api.qrum.ai", min_length=1, validation_alias=AliasChoices("jwt_issuer", "JWT_ISSUER"), description="Canonical RFC 8693 Quorum Local JWT issuer claim")] = "https://api.qrum.ai"`
      - `jwt_audience: Annotated[str, BeforeValidator(strip_whitespace), Field(default="https://qrum.ai", min_length=1, validation_alias=AliasChoices("jwt_audience", "JWT_AUDIENCE"), description="Canonical RFC 8693 Quorum Local JWT audience claim")] = "https://qrum.ai"`
    </action>
    <action>Modify `_enforce_environment_limits` in `@[backend_v2/settings.py#L847-L908]` so that when `self.environment == "production"` and `"cors_origins" not in self.model_fields_set`, `self.cors_origins` is set to `["https://qrum.ai", "https://app.qrum.ai", "https://studio.qrum.ai"]`. Add `@model_validator(mode="after")` `validate_production_cors_origins` on `Settings` (`@[backend_v2/settings.py#L54-L1053]`) that raises `ValueError("Wildcard CORS origin '*' is strictly prohibited when environment is 'production'.")` if `self.environment == "production"`, `"cors_origins" in self.model_fields_set`, and `"*"` in `self.cors_origins` (eradicating wildcard `cors_origins = ["*"]` in production).</action>
    <action>Modify `validation_exception_handler` in `@[backend_v2/main.py#L347-L380]` to replace the hardcoded `"https://api.quorum.fi/errors/validation-failed"` string with `f"{get_settings().jwt_issuer}/errors/validation-failed"`.</action>
    <action>Modify `@[backend_v2/tests/unit/test_settings.py#L264-L290]` and `@[backend_v2/tests/unit/test_main.py#L172-L189]` to add unit tests and >=2 ISTQB negative boundary tests covering: (1) default production CORS origin locking to `qrum.ai`, (2) `ValidationError` when `cors_origins=["*"]` is explicitly passed in `production` mode, (3) `ValidationError` when `primary_domain=""` (empty string violation of `min_length=1`), and (4) `validation_exception_handler` RFC 7807 `type` URI matching `"https://api.qrum.ai/errors/validation-failed"`.</action>
    <action>Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/settings.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/main.py --test --ast-strict`.</action>
  </step>

  <step id="2" name="Typed HealthCheckResponseDTO &amp; System Health Endpoint">
    <Constraint invariant="zero_naked_dicts_and_permissive_typing">Health check responses MUST use an immutable Pydantic V2 DTO inheriting from BaseResponseDTO with ConfigDict(frozen=True, strict=True, extra="forbid"). Returning naked dictionaries is strictly forbidden.</Constraint>
    <Constraint invariant="single_router_ssot_mandate">Health endpoints MUST reside inside the existing canonical system router backend_v2/api/routers/system/health.py without creating shadow router files.</Constraint>
    <action>Modify `@[backend_v2/models/dtos/system.py#L43-L52]` to define `HealthCheckResponseDTO(BaseResponseDTO)` with `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")` and fields:
      - `status: Annotated[Literal["ok", "degraded"], Field(default="ok", description="Service operational status")] = "ok"`
      - `version: Annotated[str, Field(min_length=1, description="Application semantic version")]`
      - `environment: Annotated[Literal["development", "production"], Field(description="Active runtime environment stage")]`
      - `storage_backend: Annotated[str, Field(min_length=1, description="Active storage backend identifier")]`
      - `gcp_region: Annotated[str, Field(min_length=1, description="Configured GCP deployment region")]`
      - `primary_domain: Annotated[str, Field(min_length=1, description="Canonical production domain")]`
      Export `"HealthCheckResponseDTO"` in `__all__`.
    </action>
    <action>Modify `@[backend_v2/api/routers/system/health.py#L20-L52]` to add `GET /api/v2/system/health` (`get_system_health`) with `response_model=HealthCheckResponseDTO`. Inside `get_system_health`, resolve `cfg = get_settings()`, return `HealthCheckResponseDTO(status="ok", version="2.9.0", environment=cfg.environment, storage_backend=cfg.active_backend.value, gcp_region=cfg.gcp_region, primary_domain=cfg.primary_domain)`, and catch unexpected exceptions with `logger.error` + `raise AppException(ErrorCodes.INTERNAL_SERVER_ERROR) from e` (RFC 7807 Dual-Reporting).</action>
    <action>Modify `@[backend_v2/tests/unit/models/dtos/test_system.py#L7-L12]` and `@[backend_v2/tests/unit/test_health.py#L14-L19]` to resolve `TD_ISTQB_NEGATIVE` and add unit tests and >=2 ISTQB negative boundary tests per feature: (1) valid `HealthCheckResponseDTO` instantiation, (2) `ValidationError` on unrecognized extra key (`extra="forbid"`), (3) `ValidationError` on empty `version=""` or invalid `status`, (4) `GET /api/v2/system/health` returning `200 OK` with `HealthCheckResponseDTO` payload, and (5) `test_get_system_hooks_failure_raises_app_exception` + `test_get_system_health_failure_raises_app_exception` raising `AppException(ErrorCodes.INTERNAL_SERVER_ERROR)` with structured logging when an unexpected error occurs.</action>
    <action>Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/system.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/system/health.py --test --ast-strict`.</action>
  </step>

  <step id="3" name="Stateless Cloud Run Dockerfile &amp; Docker Compose Hardening">
    <Constraint invariant="credential_hardcoding_ban">Containers MUST NOT bake credentials or run Uvicorn with --reload in production.</Constraint>
    <action>Modify `@[backend_v2/Dockerfile]` to create a dedicated non-root user (`useradd --create-home --uid 10001 quorum`), switch to `USER quorum`, and update `CMD` to `["uv", "run", "uvicorn", "backend_v2.main:app", "--host", "0.0.0.0", "--port", "8000"]` (removing `--reload`).</action>
    <action>Modify `@[docker-compose.yml]` to remove the duplicate `- GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json` line in the `backend` service definition.</action>
  </step>

  <step id="4" name="Global Quality Gate &amp; Completion Verification">
    <Constraint invariant="fragmented_quality_gates_prevention">Run the full 10-stage backend audit loop across backend_v2/ to prove zero regressions.</Constraint>
    <action>Execute the global backend completion gate: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Execute final live E2E verification gate when live credentials are active (Windows PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`).</action>
  </step>
</execution_protocol>
```
