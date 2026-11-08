# Tracker: Vertex AI 100% BYOK Compatibility, Dynamic UI Secret Provisioning & Runtime LLM/MCP SSOT

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md] @[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]`
  - [ ] Step 1: Dynamic UI Secret Provisioning, Root System DB Secret Resolution & Studio MCP Discovery Wiring
  - [ ] Step 2: Vertex AI & AI Studio Context Caching SSOT, Service Account JSON BYOK & Location Wiring
  - [ ] Step 3: Orchestrator Pre-Caching, RAG Preflight, MCP Tool Loop, Hook Propagation & ISTQB Test Suite
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
     - `@[ki_global_config_sovereignty.md]`: Document dynamic UI secret provisioning (`_ByokSecretsCard` multiline Service Account JSON & vendor-agnostic `SystemConfigMCPGateways` name resolution), `SecretService` `ROOT_SYSTEM` DB secret inheritance before `.env` fallback (enabling custom MCP gateways with `auth_env_var=None` to authenticate 100% from `tenant_secrets`), Studio MCP tool discovery `organization_id` forwarding, and Vertex AI 100% BYOK compatibility (`vertex_location` DB SSOT + tenant-scoped Redis context cache isolation in `VertexCacheAdapter` and `GoogleAIStudioCacheAdapter`).
     - `@[ki_god_code_prevention.md]`: Document `LLMCachingService` and `BaseLLMAdapter` `config` and `resolved_credential` propagation across orchestrator pre-caching and hooks.
     - `@[ki_zero_permissive_typing.md]`: Document fail-fast `_parse_service_account_json` validation and removal of global `os.environ` location mutations in `VertexCacheAdapter`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` if any module descriptions in `backend_v2/llm/`, `backend_v2/services/`, or `client_app_v2/lib/features/settings/` require synchronization.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` (`05_PILLAR_1_SECURITY_AND_IDENTITY.md` and `07_PILLAR_3_ORCHESTRATION_AND_WORKFLOWS.md`) describing dynamic UI secret provisioning across any `LLMProvider` and any `SystemConfigMCPGateways` (`MCPTransportType` / `MCPAuthType`), Vertex AI BYOK Service Account JSON / Express Mode credential binding, and context caching SSOT in present tense.

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
| REQ-001 | Enable dynamic UI secret provisioning for both single-line API keys/URIs (OpenAI, AI Studio, Anthropic, Vertex Express API Key, any custom `SystemConfigMCPGateways` Bearer token or custom `auth_header_name` API key with or without `auth_env_var`, GCP Secret Manager URIs) and multiline Vertex AI GCP Service Account JSON in `_ByokSecretsCard`, display human-readable MCP gateway names in the configured secrets list, resolve `ROOT_SYSTEM` (`org_0195f3a0000070008000000000000001`) DB secrets in `SecretService` before `.env` fallback, and forward `organization_id` in `StudioSystemConfigService.discover_mcp_gateway_tools`. | Step 1 | [ ] Pending |
| REQ-002 | Extend `BaseLLMAdapter.prepare_caching_payload`, `BaseLLMAdapter.prepare_kwargs`, and `LLMCachingService` (`prepare_caching_payload`, `pre_cache_document`) with optional `config` and `resolved_credential` parameters, populate `vertex_location=target_strategy.additional_params.vertex_location` on `LLMProviderConfig` in `LLMClient.from_tier`, and forward `config` + `resolved_credential` from `LLMClient` and `LiteLLMProvider`. | Step 2 | [ ] Pending |
| REQ-003 | Support Vertex AI BYOK GCP Service Account JSON (`vertex_credentials` + `project_id` extraction + `google.oauth2.service_account.Credentials` + fail-fast validation) and Express Mode API keys in `VertexCacheAdapter`, enforce DB `vertex_location` SSOT, remove global `os.environ` location mutations, and scope tenant Redis cache keys by `organization_id` in both `VertexCacheAdapter` and `GoogleAIStudioCacheAdapter`. | Step 2 | [ ] Pending |
| REQ-004 | Forward `config` and `resolved_credential` in `EnrichedDagExecutor` and `TwoPassAtomizer` `pre_cache_document` calls, propagate tenant `organization_id` across `RAGPreflightService`, `mcp_tool_loop`, `interaction_hook`, `linguistics`, and `source_verification_hook`, and verify all positive and negative ISTQB boundary cases across backend and frontend test suites. | Step 3 | [ ] Pending |

# Session Handover Context

## Achieved
- Audited all UI, service, and runtime LLM/MCP configuration and credential touchpoints across `client_app_v2/` and `backend_v2/` against `.env` and database SSOT (`system_configs` + `tenant_secrets`).
- Updated `@[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md]` and `@[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]` to include dynamic UI secret provisioning (`_ByokSecretsCard`) across all `LLMProvider` values and any Studio-configured `SystemConfigMCPGateways` entity (`sys_<hex32>`, with or without `auth_env_var`), `SecretService` `ROOT_SYSTEM` DB secret inheritance, Studio MCP tool discovery secret binding, and 100% runtime execution/caching wiring.

## Learned
- `_ByokSecretsCard` in `organization_iam_settings_view.dart` dynamically loads all Studio-configured `SystemConfigMCPGateways` entities via `availableMcpGatewaysProvider` (`GET /api/v2/studio/mcp-gateways`) and needed a visibility toggle (`obscureSecret`) and `maxLines: obscureSecret.value ? 1 : 6` so multiline Vertex AI GCP Service Account JSON payloads can be pasted alongside single-line OpenAI, AI Studio, Anthropic, and custom MCP gateway secrets, plus human-readable MCP gateway name resolution in the saved secrets list.
- `SecretService.resolve_llm_key` and `SecretService.resolve_mcp_credential` needed to check `ROOT_SYSTEM` (`org_0195f3a0000070008000000000000001`) in `tenant_secrets` when a tenant has no override record, enabling 100% UI-managed global secrets for any LLM provider or custom MCP gateway (`auth_env_var=None`) without `.env` dependencies while preserving strict isolation between non-root tenants.

## Remaining
- Execute Steps 1, 2, and 3 via `/tier2-execute`.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Vertex_AI_BYOK_And_Runtime_SSOT.md] @[docs/implementationplans/TRACKER_Vertex_AI_BYOK_And_Runtime_SSOT.md]
```
