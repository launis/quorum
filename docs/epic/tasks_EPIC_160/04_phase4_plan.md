<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_api_router_ssot_governance.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
  <knowledge_item>@[ki_frontend_iam_role_segregation.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
</required_context_rules>

# Phase 4: Real-Time Dual-Key Redis Kill-Switch (`MGET`) & FinOps Rate Limiting

**Overview:** Create `[NEW] @[backend_v2/core/redis_security.py]` defining `RevocationCache` (atomic O(1) Dual-Key `MGET revoked:usr:{user_id} revoked:jti:{jti}` with strict **Fail-Closed** `ServiceUnavailableError` `503` semantics) and `TenantRateLimitService` (per-organization `rpm_limit` and `tpm_limit` sliding-window counters plus public auth/assignment edge IP rate limiting via `enforce_auth_edge_rate_limit`), wire `RevocationCache.assert_not_revoked(token_data)` into `get_current_user_from_header` (`@[backend_v2/api/dependencies.py#L379-L403]`), and update `UsageService.check_quota` (`@[backend_v2/services/usage_service.py#L25-L373]` and `@[backend_v2/services/usage_service.py#L216-L276]`) to enforce monthly USD `quota_limit` and active `SubscriptionStatus` (`ErrorCodes.QUOTA_EXCEEDED`).
**Source:** @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]

**Target Files:**
- `[NEW] @[backend_v2/core/redis_security.py]`
- `[MODIFY] @[backend_v2/api/dependencies.py#L379-L403]`
- `[MODIFY] @[backend_v2/services/usage_service.py#L25-L373]`
- `[MODIFY] @[backend_v2/services/usage_service.py#L216-L276]`
- `[NEW] @[backend_v2/tests/unit/core/test_redis_security.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_usage_service.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **4. Real-Time Dual-Key Redis Kill-Switch (`MGET`) & FinOps Rate Limiting**<br>`[NEW] @[backend_v2/core/redis_security.py]`<br>`[MODIFY] @[backend_v2/api/dependencies.py#L379-L403]`<br>`[MODIFY] @[backend_v2/services/usage_service.py#L25-L373]`<br>`[MODIFY] @[backend_v2/services/usage_service.py#L216-L276]`<br>`[NEW] @[backend_v2/tests/unit/core/test_redis_security.py]`<br>`[MODIFY] @[backend_v2/tests/unit/test_usage_service.py]` | Scanning PostgreSQL for revoked flags; Fail-Open behavior when Redis is unreachable; locking out a user for 15 minutes after normal single-session logout; unisolated global rate limits; billing checks inside inner DAG loops; missing TPM/RPM enforcement at API ingress. | Create `[NEW] @[backend_v2/core/redis_security.py]` defining `RevocationCache`, `TenantRateLimitService`, and `TenantRateLimitStatusDTO`: atomic O(1) Redis `MGET` check across `revoked:usr:{user_id}` (TTL = 900s) and `revoked:jti:{jti}` (remaining token TTL); strict **Fail-Closed** `ServiceUnavailableError` (`503`) if Redis is down; Redis sliding-window rate limiter keyed by `organization_id` enforcing `Organization.tpm_limit` and `Organization.rpm_limit` plus edge IP rate limiting; pre-flight monthly `quota_limit` gatekeeper in `UsageService.check_quota`. | Pruned distributed pub/sub revocation gossip protocols and external third-party billing microservices in favor of deterministic O(1) Redis TTL keys queried via single-roundtrip `MGET` and atomic Redis counters. | Unit and negative ISTQB boundary tests (`limit - 1`, `limit`, `limit + 1`) in `[NEW] @[backend_v2/tests/unit/core/test_redis_security.py]` and `@[backend_v2/tests/unit/test_usage_service.py]` verifying instant `401` on revoked user or logged-out `jti`, `503` Fail-Closed response on Redis connection failure, `429` (`ErrorCodes.RATE_LIMIT_EXCEEDED`), and `ErrorCodes.QUOTA_EXCEEDED`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Read the `<required_context_rules>` block, `00-antigravity-core.md`, and `01-python-backend.md` before executing any changes.</action>
    <constraint>Enforce `unbounded_io_timeout_mandate`, `rfc7807_dual_reporting_mandate`, and `universal_fail_fast` across all Redis security and FinOps quota checks.</constraint>
  </step>

  <demolish>
  - `LEGACY_SYSTEM`
  - `JWT_SECRET`
  - `JWT_ALGORITHM`
  - `LEGACY_SYSTEM_ROOT_USER_ID`
  - `LEGACY_SYSTEM_ORG_ID`
  - `LEGACY_ROOT_MASTER_ID`
  - `TokenPayload`
  - `LoginResponse`
  - `verify_user_token`
  </demolish>

  <touched_artifacts>
    <backend>[NEW] @[backend_v2/core/redis_security.py]</backend>
    <backend>@[backend_v2/api/dependencies.py#L379-L403]</backend>
    <backend>@[backend_v2/services/usage_service.py#L25-L373]</backend>
    <backend>@[backend_v2/services/usage_service.py#L216-L276]</backend>
    <backend>[NEW] @[backend_v2/tests/unit/core/test_redis_security.py]</backend>
    <backend>@[backend_v2/tests/unit/test_usage_service.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`RevocationCache` in `[NEW] @[backend_v2/core/redis_security.py]` implements `revoke_token_jti`, `revoke_user_sessions`, and `assert_not_revoked` using a single atomic O(1) Redis `MGET revoked:usr:{token_data.id} revoked:jti:{token_data.jti}` inside a bounded `asyncio.timeout` with strict **Fail-Closed** `ServiceUnavailableError` (`503`) semantics, and is wired into `get_current_user_from_header` (`@[backend_v2/api/dependencies.py#L379-L403]`).</item>
    <item>`TenantRateLimitService` in `[NEW] @[backend_v2/core/redis_security.py]` enforces per-organization `rpm_limit` and `tpm_limit` sliding-window counters and public auth/assignment edge IP rate limiting (`enforce_auth_edge_rate_limit`), raising `TokenLimitExceededError` (`429 Too Many Requests`, `ErrorCodes.RATE_LIMIT_EXCEEDED`).</item>
    <item>`UsageService.check_quota` (`@[backend_v2/services/usage_service.py#L25-L373]` and `@[backend_v2/services/usage_service.py#L216-L276]`) verifies both the tenant's monthly USD budget (`quota_limit`) and active `SubscriptionStatus` (`ACTIVE` or `TRIAL`), raising `AppException` with `ErrorCodes.QUOTA_EXCEEDED` when exhausted.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_api_router_ssot_governance.md]</knowledge_item>
    <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_frontend_iam_role_segregation.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <file>@[backend_v2/services/orchestrator/dag_executor/__init__.py] (Do not embed rate-limit or billing queries inside inner DAG loops)</file>
    <file>@[client_app_v2/lib/router/router.dart] (Do not modify Flutter client files in Phase 4; reserved for Phase 6)</file>
  </anti_targets>

  <step id="4.1" name="Fail-Closed Dual-Key Redis Kill-Switch (`RevocationCache`)">
    <action>
      - **`[NEW] @[backend_v2/core/redis_security.py]`, `[MODIFY] @[backend_v2/api/dependencies.py#L379-L403]`, & `[NEW] @[backend_v2/tests/unit/core/test_redis_security.py]`**:
        - Create and define `RevocationCache` in `[NEW] @[backend_v2/core/redis_security.py]` (note: demolished `LoginResponse` was removed in Phase 1) with:
          - `async def revoke_token_jti(self, jti: str, ttl_seconds: int) -> None`: Sets `revoked:jti:{jti} = "1"` with `EX ttl_seconds` (remaining lifetime of the logged-out JWT, up to 900 seconds).
          - `async def revoke_user_sessions(self, user_id: str, ttl_seconds: int) -> None`: Sets `revoked:usr:{user_id} = "1"` with `EX ttl_seconds` (900 seconds) for administrative kill-switch events and global "Sign out from all devices" requests.
          - `async def assert_not_revoked(self, token_data: TokenData) -> None`: Executes a single atomic O(1) `MGET revoked:usr:{token_data.id} revoked:jti:{token_data.jti}` inside a bounded `asyncio.timeout`. If either key exists, logs `ErrorCodes.AUTH_TOKEN_EXPIRED` and raises `AuthenticationError`. If Redis throws a connection or timeout error, enforces **Fail-Closed** security by logging `ErrorCodes.SERVICE_UNAVAILABLE` and raising `ServiceUnavailableError` (`503 Service Unavailable`).
        - Wire `RevocationCache.assert_not_revoked(token_data)` into `get_current_user_from_header` (`@[backend_v2/api/dependencies.py#L379-L403]`) immediately after `auth_service.verify_token(raw_token)`.
    </action>
  </step>

  <step id="4.2" name="Per-Tenant Redis Sliding-Window Rate Limiter &amp; FinOps Pre-Flight Gatekeeper">
    <action>
      - **`[NEW] @[backend_v2/core/redis_security.py]`, `[MODIFY] @[backend_v2/services/usage_service.py#L25-L373]`, `[MODIFY] @[backend_v2/services/usage_service.py#L216-L276]`, `[NEW] @[backend_v2/tests/unit/core/test_redis_security.py]`, & `[MODIFY] @[backend_v2/tests/unit/test_usage_service.py]`**:
        - Create and define `TenantRateLimitService` and `TenantRateLimitStatusDTO` in `[NEW] @[backend_v2/core/redis_security.py]` enforcing both per-organization `rpm_limit` and `tpm_limit` using atomic Redis sliding-window counters (`ratelimit:org:{org_id}:rpm` and `ratelimit:org:{org_id}:tpm`) AND public auth/assignment edge brute-force protection (`async def enforce_auth_edge_rate_limit(self, client_ip: str, endpoint_scope: str) -> None` keyed on `ratelimit:auth_edge:{endpoint_scope}:{client_ip}` using `auth_edge_rpm_limit` from `Settings` on `POST /api/v2/iam/auth/exchange`, `POST /api/v2/iam/auth/invitations/accept`, `GET /api/v2/execution/executions/assignments/preview`, and `POST /api/v2/execution/executions/assignments/onboard`). When exceeded, log `ErrorCodes.RATE_LIMIT_EXCEEDED` and raise `TokenLimitExceededError` (`429 Too Many Requests`).
        - Update `UsageService.check_quota` (`@[backend_v2/services/usage_service.py#L25-L373]` and `@[backend_v2/services/usage_service.py#L216-L276]`) to verify both the tenant's monthly USD budget (`quota_limit`) and active `SubscriptionStatus` (`ACTIVE` or `TRIAL`), raising `AppException` with `ErrorCodes.QUOTA_EXCEEDED` in 0 ms when exhausted.
    </action>
  </step>

  <test_contracts>
    <contract name="test_revocation_cache_dual_key_mget_unrevoked_positive" category="positive">
      <input>`TokenData` whose `id` (`revoked:usr:{id}`) and `jti` (`revoked:jti:{jti}`) both return `[None, None]` from Redis `MGET`</input>
      <expected>`assert_not_revoked` completes in `< 1 ms` without error; if `jti` #1 is revoked on logout, a newly minted `jti` #2 for the same user passes `assert_not_revoked`</expected>
    </contract>
    <contract name="test_revocation_cache_revoked_user_or_jti_negative" category="negative">
      <input>`TokenData` where either `revoked:usr:{id}` or `revoked:jti:{jti}` is `"1"` in Redis</input>
      <expected>Logs `ErrorCodes.AUTH_TOKEN_EXPIRED.name` and raises `AuthenticationError` (`401 Unauthorized`)</expected>
    </contract>
    <contract name="test_revocation_cache_redis_down_fail_closed_error_path" category="error_path">
      <input>Redis connection timeout or `ConnectionError` during `assert_not_revoked`</input>
      <expected>Enforces Fail-Closed policy by logging `ErrorCodes.SERVICE_UNAVAILABLE.name` and raising `ServiceUnavailableError` (`503 Service Unavailable`)</expected>
    </contract>
    <contract name="test_tenant_rate_limit_service_bva_boundary" category="boundary">
      <input>Requests at `rpm_limit - 1`, `rpm_limit`, and `rpm_limit + 1` (and `tpm_limit - 1`, `tpm_limit`, `tpm_limit + 1`)</input>
      <expected>`limit - 1` and `limit` succeed; `limit + 1` logs `ErrorCodes.RATE_LIMIT_EXCEEDED.name` and raises `TokenLimitExceededError` (`429 Too Many Requests`)</expected>
    </contract>
    <contract name="test_usage_service_check_quota_bva_and_subscription_boundary" category="boundary">
      <input>Monthly spend at `quota_limit - 0.01`, `quota_limit`, `quota_limit + 0.01`, or inactive `SubscriptionStatus`</input>
      <expected>`quota_limit - 0.01` with `ACTIVE`/`TRIAL` passes; `>= quota_limit` or inactive subscription raises `AppException` (`ErrorCodes.QUOTA_EXCEEDED`)</expected>
    </contract>
  </test_contracts>

  <validation_gate>
    $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/core/redis_security.py backend_v2/api/dependencies.py backend_v2/services/usage_service.py --test --ast-strict
  </validation_gate>
</execution_protocol>
```

