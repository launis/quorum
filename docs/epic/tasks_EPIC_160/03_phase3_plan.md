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

# Phase 3: Enterprise BYOK & Cloud Secrets Engine for LLM & MCP Services

**Overview:** Create `SecretService` in `[NEW] @[backend_v2/services/auth/secret_service.py]` implementing Dual-Tier BYOK Secret Governance (`CLOUD_SECRET_MANAGER` and `ENVELOPE_KMS` with AES-256-GCM DEK + Cloud KMS KEK and `kek_version`), inject request-scoped `pydantic.SecretStr` credentials dynamically per `organization_id` into `LLMFactory._resolve_provider_api_key` (`@[backend_v2/llm/provider/provider_factory.py#L107-L176]`), `LLMFactory.create_provider` (`@[backend_v2/llm/provider/provider_factory.py#L178-L301]`), `LiteLLMProvider` (`@[backend_v2/llm/provider/litellm_provider.py#L74-L429]`), `ToolDispatcher` (`@[backend_v2/services/mcp/dispatcher.py]`), and `GenericMCPClient` (`@[backend_v2/services/mcp/generic_mcp_client.py#L54-L806]` and `@[backend_v2/services/mcp/generic_mcp_client.py#L237-L292]`), expose organization BYOK endpoints in `@[backend_v2/api/routers/iam/organizations.py#L19-L46]`, and enforce AST guardrails in `@[scripts/_ast_guardrails.py]` preventing `SecretStr.get_secret_value()` leakage in logs or `MCPAuditTrace`.
**Source:** @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]

**Target Files:**
- `[NEW] @[backend_v2/services/auth/secret_service.py]`
- `[MODIFY] @[backend_v2/llm/provider/litellm_provider.py#L74-L429]`
- `[MODIFY] @[backend_v2/llm/provider/provider_factory.py#L107-L176]`
- `[MODIFY] @[backend_v2/llm/provider/provider_factory.py#L178-L301]`
- `[MODIFY] @[backend_v2/services/mcp/generic_mcp_client.py#L54-L806]`
- `[MODIFY] @[backend_v2/services/mcp/generic_mcp_client.py#L237-L292]`
- `[MODIFY] @[backend_v2/services/mcp/dispatcher.py]`
- `[MODIFY] @[backend_v2/api/routers/iam/organizations.py#L19-L46]`
- `[MODIFY] @[scripts/_ast_guardrails.py]`
- `[NEW] @[backend_v2/tests/unit/services/auth/test_secret_service.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **3. Enterprise BYOK & Cloud Secrets Governance**<br>`[NEW] @[backend_v2/services/auth/secret_service.py]`<br>`[MODIFY] @[backend_v2/llm/provider/litellm_provider.py#L74-L429]`<br>`[MODIFY] @[backend_v2/llm/provider/provider_factory.py#L107-L176]`<br>`[MODIFY] @[backend_v2/llm/provider/provider_factory.py#L178-L301]`<br>`[MODIFY] @[backend_v2/services/mcp/generic_mcp_client.py#L54-L806]`<br>`[MODIFY] @[backend_v2/services/mcp/generic_mcp_client.py#L237-L292]`<br>`[MODIFY] @[backend_v2/services/mcp/dispatcher.py]`<br>`[MODIFY] @[backend_v2/api/routers/iam/organizations.py#L19-L46]`<br>`[MODIFY] @[scripts/_ast_guardrails.py]`<br>`[NEW] @[backend_v2/tests/unit/services/auth/test_secret_service.py]` | Shared global `.env` API keys for all tenants; silent fallback to `os.environ` when a configured tenant BYOK secret fails decryption; caching initialized LLM clients across tenants; synchronous `os.environ.get` inside MCP header builders; logging raw headers in `MCPAuditTrace`. | Create `SecretService` in `[NEW] @[backend_v2/services/auth/secret_service.py]` resolving tenant keys via Cloud Secret Manager URI or Envelope Encryption (AES-256-GCM DEK + Cloud KMS KEK with `kek_version` on created `TenantSecretDTO`, `TenantSecretCreateDTO`, `TenantSecretResponseDTO`, and `ResolvedCredentialDTO`); request-scoped `pydantic.SecretStr` injection into `LiteLLMProvider` and `GenericMCPClient`; Fail-Fast `ConfigurationError` (`ErrorCodes.SECRET_RESOLUTION_FAILED`) on decryption failure. | Pruned per-step secret vaults and external HashiCorp Vault cluster requirements for local dev; centralized BYOK resolution at `(organization_id, LLMProvider)` and `(organization_id, gateway_id)` boundaries. | Cross-tenant isolation tests (`test_byok_cross_tenant_isolation`) in `[NEW] @[backend_v2/tests/unit/services/auth/test_secret_service.py]`, `SecretStr` redaction assertions on `TenantSecretResponseDTO` (`masked_hint` only), and `ConfigurationError` Fail-Fast when secret decryption fails. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Read the `<required_context_rules>` block, `00-antigravity-core.md`, `01-python-backend.md`, and `05_llm_architecture.md` before executing any changes.</action>
    <constraint>Enforce `credential_hardcoding_ban`, `security_logging_ban`, `zero_backward_compatibility_planning_ban`, and `single_pipeline_invariant_mandate` across all secret resolution and provider injection paths.</constraint>
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
    <backend>[NEW] @[backend_v2/services/auth/secret_service.py]</backend>
    <backend>@[backend_v2/llm/provider/litellm_provider.py#L74-L429]</backend>
    <backend>@[backend_v2/llm/provider/provider_factory.py#L107-L176]</backend>
    <backend>@[backend_v2/llm/provider/provider_factory.py#L178-L301]</backend>
    <backend>@[backend_v2/services/mcp/generic_mcp_client.py#L54-L806]</backend>
    <backend>@[backend_v2/services/mcp/generic_mcp_client.py#L237-L292]</backend>
    <backend>@[backend_v2/services/mcp/dispatcher.py]</backend>
    <backend>@[backend_v2/api/routers/iam/organizations.py#L19-L46]</backend>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>[NEW] @[backend_v2/tests/unit/services/auth/test_secret_service.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`SecretService` in `[NEW] @[backend_v2/services/auth/secret_service.py]` implements Dual-Tier BYOK Secret Governance (`CLOUD_SECRET_MANAGER` and `ENVELOPE_KMS` with AES-256-GCM + Cloud KMS KEK and `kek_version`) returning a non-nullable `ResolvedCredentialDTO` with zero fallback to platform keys when a configured tenant BYOK key fails decryption or lookup.</item>
    <item>`LLMFactory._resolve_provider_api_key` (`@[backend_v2/llm/provider/provider_factory.py#L107-L176]`), `LLMFactory.create_provider` (`@[backend_v2/llm/provider/provider_factory.py#L178-L301]`), `LiteLLMProvider` (`@[backend_v2/llm/provider/litellm_provider.py#L74-L429]`), `ToolDispatcher` (`@[backend_v2/services/mcp/dispatcher.py]`), and `GenericMCPClient._build_request_headers` (`@[backend_v2/services/mcp/generic_mcp_client.py#L237-L292]`) inject `pydantic.SecretStr` credentials dynamically per `organization_id` with zero cross-tenant bleed and zero secret leakage in `MCPAuditTrace`.</item>
    <item>Organization BYOK management endpoints (`GET`, `PUT`, `DELETE` under `/api/v2/iam/organizations/{org_id}/secrets`) in `@[backend_v2/api/routers/iam/organizations.py#L19-L46]` are guarded by `require_role` (`ROOT` and `ADMIN` members of `UserRole`) and record `TENANT_SECRET_UPSERTED` and `TENANT_SECRET_DELETED` audit events.</item>
    <item>AST guardrail in `@[scripts/_ast_guardrails.py]` and unit tests in `[NEW] @[backend_v2/tests/unit/services/auth/test_secret_service.py]` pass 100%.</item>
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
    <file>@[backend_v2/services/orchestrator/dag_executor/__init__.py] (Do not mutate DAG Orchestrator core during Phase 3 BYOK secret integration)</file>
    <file>@[client_app_v2/lib/router/router.dart] (Do not modify Flutter client files in Phase 3; reserved for Phase 6)</file>
  </anti_targets>

  <step id="3.1" name="`SecretService` (Cloud Secret Manager &amp; Envelope Encryption — Single-Pipeline Non-Nullable Resolution)">
    <action>
      - **`[NEW] @[backend_v2/services/auth/secret_service.py]` & `[NEW] @[backend_v2/tests/unit/services/auth/test_secret_service.py]`**:
        - Create and define `SecretService` in `[NEW] @[backend_v2/services/auth/secret_service.py]` (operating on `TenantSecretDTO`, `TenantSecretCreateDTO`, `TenantSecretResponseDTO`, and `ResolvedCredentialDTO` defined in `@[backend_v2/models/auth.py]`; Note: demolished `LoginResponse` was removed in Phase 1) implementing Dual-Tier BYOK Secret Governance with a **Single-Pipeline Non-Nullable Contract** (zero `| None` return types and zero caller fallback branches):
          - **Storage Tier 1 (`CLOUD_SECRET_MANAGER`)**: Persists the tenant's GCP Secret Manager resource URI (`projects/{project}/secrets/{name}/versions/{version}`) in `tenant_secrets` and resolves the payload at runtime within a bounded `asyncio.timeout`.
          - **Storage Tier 2 (`ENVELOPE_KMS`)**: Generates a unique 256-bit Data Encryption Key (DEK) via `secrets.token_bytes(32)`, encrypts the tenant's secret with AES-256-GCM (`cryptography.hazmat.primitives.ciphers.aead.AESGCM`), wraps the DEK using the configured Cloud KMS Key Encryption Key (or deterministic local KMS master key in development/test), and stores `encrypted_dek`, `nonce`, `ciphertext`, `kek_version` (NIST SP 800-57 KEK version identifier enabling zero-downtime master key rotation and DEK re-wrapping), and `masked_hint` (`f"****{raw_secret[-4:]}"`) in `tenant_secrets`.
          - Provide `async def resolve_llm_key(self, organization_id: PrefixedUUID7, provider: LLMProvider) -> ResolvedCredentialDTO` and `async def resolve_mcp_credential(self, organization_id: PrefixedUUID7, gateway: SystemConfigMCPGateways) -> ResolvedCredentialDTO` returning a non-nullable `ResolvedCredentialDTO(secret_value=SecretStr(...))`:
            1. If a `TenantSecretDTO` record exists for `(organization_id, provider.value)` or `(organization_id, gateway.id)`, `SecretService` decrypts/fetches and returns it; if decryption or Secret Manager lookup fails, it immediately logs `ErrorCodes.SECRET_RESOLUTION_FAILED` and raises `ConfigurationError` (with **zero fallback** to platform keys).
            2. If no `TenantSecretDTO` record is configured for that tenant, `SecretService` resolves the platform credential from typed `Settings` (or `gateway.auth_env_var` for MCP gateways); if the required credential is not configured or empty, `SecretService` immediately logs `ErrorCodes.SECRET_RESOLUTION_FAILED` and raises `ConfigurationError` Fail-Fast.
    </action>
  </step>

  <step id="3.2" name="Request-Scoped Credential Injection in `LiteLLMProvider` &amp; `GenericMCPClient`">
    <action>
      - **`[MODIFY] @[backend_v2/llm/provider/litellm_provider.py#L74-L429]`, `[MODIFY] @[backend_v2/llm/provider/provider_factory.py#L107-L176]`, & `[MODIFY] @[backend_v2/llm/provider/provider_factory.py#L178-L301]`**:
        - Update `LLMFactory._resolve_provider_api_key` (`@[backend_v2/llm/provider/provider_factory.py#L107-L176]`) and `LLMFactory.create_provider` (`@[backend_v2/llm/provider/provider_factory.py#L178-L301]`) to receive the non-nullable `ResolvedCredentialDTO` from `SecretService.resolve_llm_key(organization_id=organization_id, provider=config.provider)` with zero `if/else` fallback branches in `LLMFactory`.
        - Ensure `LiteLLMProvider` (`@[backend_v2/llm/provider/litellm_provider.py#L74-L429]`) binds tenant-resolved API keys strictly to the request scope or tenant-isolated provider key (`f"{model_id}:{organization_id}"`), preventing cross-tenant credential bleed across concurrent `asyncio.TaskGroup` executions.
      - **`[MODIFY] @[backend_v2/services/mcp/generic_mcp_client.py#L54-L806]`, `[MODIFY] @[backend_v2/services/mcp/generic_mcp_client.py#L237-L292]`, & `[MODIFY] @[backend_v2/services/mcp/dispatcher.py]`**:
        - Update `ToolDispatcher` (`@[backend_v2/services/mcp/dispatcher.py]`) and `GenericMCPClient` (`@[backend_v2/services/mcp/generic_mcp_client.py#L54-L806]` and `@[backend_v2/services/mcp/generic_mcp_client.py#L237-L292]`) to resolve MCP credentials asynchronously via `await secret_service.resolve_mcp_credential(organization_id=organization_id, gateway=gateway)` when `gateway.auth_type != MCPAuthType.NONE` prior to synchronous header assembly in `_build_request_headers(self, gateway: SystemConfigMCPGateways, resolved_credential: ResolvedCredentialDTO | None = None)` (where `resolved_credential` is mandatory whenever `gateway.auth_type != MCPAuthType.NONE`, raising `ConfigurationError` Fail-Fast if missing).
        - Enforce zero secret leakage: verify that neither `MCPAuditTrace` nor OpenTelemetry span attributes ever record authorization headers or resolved secret strings.
    </action>
  </step>

  <step id="3.3" name="Organization BYOK Management Endpoints &amp; DLP AST Guardrail">
    <action>
      - **`[MODIFY] @[backend_v2/api/routers/iam/organizations.py#L19-L46]` & `[MODIFY] @[scripts/_ast_guardrails.py]`**:
        - Add `GET /api/v2/iam/organizations/{org_id}/secrets` (`response_model=list[TenantSecretResponseDTO]`), `PUT /api/v2/iam/organizations/{org_id}/secrets` (`response_model=TenantSecretResponseDTO`), and `DELETE /api/v2/iam/organizations/{org_id}/secrets/{secret_id}` in `@[backend_v2/api/routers/iam/organizations.py#L19-L46]` guarded by `require_role` (`ROOT` and `ADMIN` members of `UserRole`) and strict tenant ownership verification (`user.organization_id == org_id` unless `user.role` is `ROOT`).
        - Record structured security audit events (`TENANT_SECRET_UPSERTED` and `TENANT_SECRET_DELETED`) via `audit_service.log_event` in `SecretService`, logging exclusively metadata (`secret_id`, `scope`, `provider`, `gateway_id`, `storage_mode`, `masked_hint`) with zero plaintext secret values.
        - Add an AST check in `@[scripts/_ast_guardrails.py]` verifying that `TenantSecretDTO` and `ResolvedCredentialDTO` never serialize `SecretStr` via `get_secret_value()` inside logger calls or `MCPAuditTrace` instantiations.
    </action>
  </step>

  <test_contracts>
    <contract name="test_secret_service_envelope_kms_roundtrip_positive" category="positive">
      <input>`TenantSecretCreateDTO` with `storage_mode="envelope_kms"` and raw API key for `organization_id`</input>
      <expected>Encrypts via AES-256-GCM DEK + KEK (`kek_version`), stores `masked_hint="****abcd"`, and `resolve_llm_key` returns `ResolvedCredentialDTO` with exact `SecretStr`</expected>
    </contract>
    <contract name="test_byok_cross_tenant_isolation_negative" category="negative">
      <input>Tenant A configures a BYOK key; Tenant B calls `resolve_llm_key` without a configured key when platform key is unset</input>
      <expected>Tenant B cannot resolve Tenant A's secret and receives `ConfigurationError` (`ErrorCodes.SECRET_RESOLUTION_FAILED`)</expected>
    </contract>
    <contract name="test_secret_service_corrupted_ciphertext_no_fallback_negative" category="negative">
      <input>`TenantSecretDTO` for Tenant A has corrupted `ciphertext` or invalid `encrypted_dek` even when a global `.env` platform key exists</input>
      <expected>Logs `ErrorCodes.SECRET_RESOLUTION_FAILED` and raises `ConfigurationError` immediately with zero fallback to platform key</expected>
    </contract>
    <contract name="test_generic_mcp_client_missing_resolved_credential_negative" category="negative">
      <input>`GenericMCPClient._build_request_headers` called with `gateway.auth_type = MCPAuthType.BEARER` and `resolved_credential=None`</input>
      <expected>Raises `ConfigurationError` (`ErrorCodes.SECRET_RESOLUTION_FAILED`) Fail-Fast</expected>
    </contract>
  </test_contracts>

  <validation_gate>
    $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/auth/secret_service.py backend_v2/llm/provider/ backend_v2/services/mcp/ backend_v2/api/routers/iam/organizations.py scripts/_ast_guardrails.py --test --ast-strict
  </validation_gate>
</execution_protocol>
```

