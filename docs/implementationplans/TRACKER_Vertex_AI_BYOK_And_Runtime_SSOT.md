# Tracker: Vertex AI 100% BYOK Compatibility, Dynamic UI Secret Provisioning & Runtime LLM/MCP SSOT

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md] @[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]`
  - [x] Step 1: Dynamic UI Secret Provisioning, .env Fallback Eradication, DB Secret Migration & Studio MCP Discovery Wiring
  - [x] Step 2: Vertex AI & AI Studio Context Caching SSOT, Service Account JSON BYOK & Location Wiring
  - [x] Step 3: Orchestrator Pre-Caching, RAG Preflight, MCP Tool Loop, Hook Propagation & ISTQB Test Suite
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md] @[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[backend_v2/services/auth/secret_service.py]
  - [ ] @[backend_v2/services/studio/system_config_service.py]
  - [ ] @[backend_v2/llm/adapters/base_adapter.py]
  - [ ] @[backend_v2/llm/caching_service.py]
  - [ ] @[backend_v2/llm/client.py]
  - [ ] @[backend_v2/llm/provider/litellm_provider.py]
  - [ ] @[backend_v2/llm/adapters/vertex_adapter.py]
  - [ ] @[backend_v2/llm/adapters/ai_studio_adapter.py]
  - [ ] @[backend_v2/llm/adapters/anthropic_adapter.py]
  - [ ] @[backend_v2/llm/adapters/openai_adapter.py]
  - [ ] @[backend_v2/llm/adapters/mock_adapter.py]
  - [ ] @[backend_v2/services/orchestrator/enriched_dag_executor.py]
  - [ ] @[backend_v2/services/orchestrator/two_pass_atomizer.py]
  - [ ] @[backend_v2/services/orchestrator/rag_preflight_service.py]
  - [ ] @[backend_v2/services/mcp/mcp_tool_loop.py]
  - [ ] @[backend_v2/hooks/interaction_hook.py]
  - [ ] @[backend_v2/hooks/linguistics.py]
  - [ ] @[backend_v2/hooks/source_verification_hook.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`.
  - [ ] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md] @[ki_god_code_prevention.md] @[ki_global_config_sovereignty.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_global_config_sovereignty.md]`: Document the 3-tier B2B SaaS secret governance best-practice architecture (Layer 1: Infrastructure Bootstrap Secrets in `.env` / GCP Secret Manager `DATABASE_URL` and `JWT_SECRET_KEY`; Layer 2: `ROOT_SYSTEM` `org_0195f3a0000070008000000000000001` platform baseline secrets in PostgreSQL 19 `tenant_secrets`; Layer 3: Customer Tenant `org_<hex32>` self-service BYOK secrets in PostgreSQL 19 `tenant_secrets` via NIST SP 800-57 `ENVELOPE_KMS` AES-256-GCM DEK/KEK encryption), dynamic UI secret provisioning (`_ByokSecretsCard` multiline Service Account JSON & vendor-agnostic `SystemConfigMCPGateways` name resolution), 100% database-only secret resolution in `SecretService` (`organization_id` -> `ROOT_SYSTEM` -> Fail-Fast `ConfigurationError` with zero `.env` / `os.environ` fallback and `_resolve_platform_llm_secret` / `_resolve_platform_mcp_secret` deleted), `"auth_env_var": null` in `seed_data.json`, Studio MCP tool discovery `organization_id` forwarding, and Vertex AI 100% BYOK compatibility (`vertex_location` DB SSOT + tenant-scoped Redis context cache isolation in `VertexCacheAdapter` and `GoogleAIStudioCacheAdapter`).
     - `@[ki_god_code_prevention.md]`: Document `LLMCachingService` and `BaseLLMAdapter` `config` and `resolved_credential` propagation across orchestrator pre-caching and hooks.
     - `@[ki_zero_permissive_typing.md]`: Document fail-fast `_parse_service_account_json` validation and removal of global `os.environ` location mutations in `VertexCacheAdapter`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` if any module descriptions in `backend_v2/llm/`, `backend_v2/services/`, or `client_app_v2/lib/features/settings/` require synchronization.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` (`05_PILLAR_1_SECURITY_AND_IDENTITY.md` and `07_PILLAR_3_ORCHESTRATION_AND_WORKFLOWS.md`) describing 100% database-driven dynamic UI secret provisioning across any `LLMProvider` and any `SystemConfigMCPGateways` (`MCPTransportType` / `MCPAuthType`) with zero `.env` fallback, Vertex AI BYOK Service Account JSON / Express Mode credential binding, and context caching SSOT in present tense.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md] @[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[backend_v2/target.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Enable dynamic UI secret provisioning for both single-line API keys/URIs (OpenAI, AI Studio, Anthropic, Vertex Express API Key, any custom `SystemConfigMCPGateways` Bearer token or custom `auth_header_name` API key with `auth_env_var=None`, GCP Secret Manager URIs) and multiline Vertex AI GCP Service Account JSON in `_ByokSecretsCard`, display human-readable MCP gateway names in the configured secrets list, eradicate all `.env` / `os.environ` secret fallbacks (`_resolve_platform_llm_secret` and `_resolve_platform_mcp_secret` deleted in `SecretService`, `"auth_env_var": null` in `seed_data.json`), migrate all current `.env` and `service-account.json` LLM and MCP secrets into PostgreSQL 19 `tenant_secrets` under `ROOT_SYSTEM` (`org_0195f3a0000070008000000000000001`), and forward `organization_id` in `StudioSystemConfigService.discover_mcp_gateway_tools`. | Step 1 | [x] Completed |
| REQ-002 | Extend `BaseLLMAdapter.prepare_caching_payload`, `BaseLLMAdapter.prepare_kwargs`, and `LLMCachingService` (`prepare_caching_payload`, `pre_cache_document`) with optional `config` and `resolved_credential` parameters, populate `vertex_location=target_strategy.additional_params.vertex_location` on `LLMProviderConfig` in `LLMClient.from_tier`, and forward `config` + `resolved_credential` from `LLMClient` and `LiteLLMProvider`. | Step 2 | [x] Completed |
| REQ-003 | Support Vertex AI BYOK GCP Service Account JSON (`vertex_credentials` + `project_id` extraction + `google.oauth2.service_account.Credentials` + fail-fast validation) and Express Mode API keys in `VertexCacheAdapter`, enforce DB `vertex_location` SSOT, remove global `os.environ` location mutations, and scope tenant Redis cache keys by `organization_id` in both `VertexCacheAdapter` and `GoogleAIStudioCacheAdapter`. | Step 2 | [x] Completed |
| REQ-004 | Forward `config` and `resolved_credential` in `EnrichedDagExecutor` and `TwoPassAtomizer` `pre_cache_document` calls, propagate tenant `organization_id` across `RAGPreflightService`, `mcp_tool_loop`, `interaction_hook`, `linguistics`, and `source_verification_hook`, and verify all positive and negative ISTQB boundary cases across backend and frontend test suites. | Step 3 | [x] Completed |

# Session Handover Context

## Achieved
- Implemented and verified `_ByokSecretsCard` multiline secret visibility toggle + MCP gateway name/badge display (`organization_iam_settings_view.dart`) and `StudioSystemConfigService.discover_mcp_gateway_tools` `organization_id` forwarding.
- Completed `/tier0-research-plan` System 2 red-team audit and hardened `@[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]` and `@[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]`:
  1. Added `@[backend_v2/tests/conftest.py]` (`isolate_default_uow_and_secret_service` [lines 157-166]) and `@[backend_v2/tests/unit/services/mcp/test_generic_mcp_client.py]` to Step 1 target boundaries so default test `InMemoryUnitOfWork` instances seed `ROOT_SYSTEM` (`org_0195f3a0000070008000000000000001`) `TenantSecretDTO` records and MCP client unit tests provision gateway secrets via `SecretService` in `tenant_secrets` instead of `monkeypatch.setenv`.
  2. Added Phase 1 technical debt remediation for `@[backend_v2/tests/unit/llm/test_caching_service.py]` (`TD_ISTQB_NEGATIVE`) and `@[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py]` (`TD_MODEL_FACTORY` at line 68 and `TD_ISTQB_NEGATIVE`) into Section 3, the 5-Column Directives Table, and Step 3.

## Learned
- `SecretService._derive_local_kek` derives the local 256-bit AES-GCM Key Encryption Key (KEK) from `settings.jwt_secret_key.get_secret_value()`. Pinning `JWT_SECRET_KEY` in `.env` before encrypting secrets into PostgreSQL 19 `tenant_secrets` guarantees deterministic KEK derivation across FastAPI server, Arq worker, and CLI restarts.
- Deleting `_resolve_platform_llm_secret` and `_resolve_platform_mcp_secret` in `SecretService` enforces 100% database-only secret resolution (`organization_id` -> `ROOT_SYSTEM` `org_0195f3a0000070008000000000000001` -> Fail-Fast `ConfigurationError`) with zero `.env` or `os.environ` fallback; therefore `conftest.py`'s `isolate_default_uow_and_secret_service` must seed `ROOT_SYSTEM` `TenantSecretDTO` records in its default `InMemoryUnitOfWork` while tests asserting missing secrets pass an isolated unseeded `InMemoryUnitOfWork`.

## Remaining
- Execute Steps 1, 2, and 3 via `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md] @[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]`.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md] @[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]
```
