# Tracker: LLM Provider BYOK Runtime Credential Wiring

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_BYOK_Runtime_Wiring.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_BYOK_Runtime_Wiring.md]

- [x] **[OK] Tier 0 Research & Red-Teaming:** `/tier0-research-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_BYOK_Runtime_Wiring.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_BYOK_Runtime_Wiring.md] @[docs/implementationplans/TRACKER_LLM_BYOK_Runtime_Wiring.md]`
  - [x] Step 1: Phase 1, Step 1: Wire SecretService.resolve_llm_key and ResolvedCredentialDTO into LLMClient
  - [x] Step 2: Phase 1, Step 2: Propagate Tenant organization_id Through Execution Ingress and Phase 1 Stage 3
  - [x] Step 3: Phase 1, Step 3: Wire Tenant organization_id into Phase 2 Report and Variance Synthesis Workers
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_BYOK_Runtime_Wiring.md] @[docs/implementationplans/TRACKER_LLM_BYOK_Runtime_Wiring.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_LLM_BYOK_Runtime_Wiring.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[backend_v2/llm/client.py]
  - [x] @[backend_v2/services/execution/ingress_service.py]
  - [x] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]
  - [ ] @[backend_v2/workers/synthesis_worker.py]
  - [ ] @[backend_v2/workers/variance_synthesis.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_LLM_BYOK_Runtime_Wiring.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - N/A (No Frontend files touched in this plan)
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_LLM_BYOK_Runtime_Wiring.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_BYOK_Runtime_Wiring.md] @[ki_god_code_prevention.md] @[ki_global_config_sovereignty.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_global_config_sovereignty.md]`: Document the end-to-end Dual-Tier BYOK runtime credential resolution path from `LLMClient.from_tier` via `SecretService.resolve_llm_key` into `LLMFactory.create_provider` and `LiteLLMProvider`, including `SecretStr` encapsulation on `LLMClient._resolved_credential` and tenant `organization_id` propagation across Phase 1 Ingress/Stage 3 and Phase 2 Synthesis workers.
     - `@[ki_god_code_prevention.md]`: Record stage-decoupled `organization_id` forwarding in `execute_engine_retry_stage` (`_run_optional_mcp_retrieval` and `LLMClient.from_tier`) without adding redundant state fields to `StrategyContext`.
     - `@[ki_zero_permissive_typing.md]`: Document `QGR016`-compliant `effective_org_id` initialization to `ROOT_SYSTEM` on `SystemOrganizations` (`"org_0195f3a0000070008000000000000001"`) across `LLMClient`, `engine_retry_stage.py`, `synthesis_worker.py`, and `variance_synthesis.py`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` if any module responsibility descriptions in `backend_v2/llm/`, `backend_v2/services/execution/`, or `backend_v2/workers/` require synchronization.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing end-to-end tenant BYOK credential resolution across Phase 1 DAG execution and Phase 2 synthesis in present tense without historical language or plan IDs.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_BYOK_Runtime_Wiring.md] @[docs/implementationplans/TRACKER_LLM_BYOK_Runtime_Wiring.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[backend_v2/llm/client.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Extend `LLMClient.__init__` in `@[backend_v2/llm/client.py]` to accept keyword-only `organization_id: PrefixedUUID7 \| None = None` and `resolved_credential: ResolvedCredentialDTO \| None = None` and expose read-only `@property` accessors. | Step 1 | [x] Completed |
| REQ-002 | Wire `SecretService.resolve_llm_key` into `LLMClient.from_tier` for all non-mock providers with `QGR016`-compliant `effective_org_id` initialization to `ROOT_SYSTEM` on `SystemOrganizations` (`"org_0195f3a0000070008000000000000001"`), preserving `SecretStr` encapsulation inside `self._resolved_credential`. | Step 1 | [x] Completed |
| REQ-003 | Forward `organization_id=self._organization_id` and `resolved_credential=self._resolved_credential` to `LLMFactory.create_provider` inside `LLMClient.run_structured_task` and `LLMClient.run_chat`. | Step 1 | [x] Completed |
| REQ-004 | Add positive and negative unit tests in `@[backend_v2/tests/unit/llm/test_client.py]` verifying tenant BYOK resolution, platform fallback when no tenant BYOK exists, and Fail-Fast `ConfigurationError` (`ErrorCodes.SECRET_RESOLUTION_FAILED`) on corrupted BYOK ciphertext or missing platform API key. | Step 1 | [x] Completed |
| REQ-005 | Populate `global_context_vars=GlobalContextVarsDTO(organization_id=initiator.organization_id, initiator_id=initiator.id, target_locale=payload.target_locale, profile_id=resolved_profile_id)` on `ExecutionMetadata` in `ExecutionIngressService._persist_and_enqueue_execution` (`@[backend_v2/services/execution/ingress_service.py]`). | Step 2 | [x] Completed |
| REQ-006 | Verify `record.metadata.global_context_vars.organization_id == initiator.organization_id` and `initiator_id == initiator.id` in `@[backend_v2/tests/unit/services/execution/test_ingress_service.py]`. | Step 2 | [x] Completed |
| REQ-007 | Resolve `effective_org_id` in `_run_optional_mcp_retrieval` and `execute_engine_retry_stage` (`@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`) from `context.global_context_vars.organization_id` (defaulting to `ROOT_SYSTEM` on `SystemOrganizations`) and pass `organization_id=effective_org_id` to `ToolDispatcher` and `LLMClient.from_tier`. | Step 2 | [x] Completed |
| REQ-008 | Add positive and negative unit tests in `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]` verifying `organization_id` propagation to `LLMClient.from_tier` and `ToolDispatcher`, `ROOT_SYSTEM` default, and Fail-Fast `ConfigurationError` propagation. | Step 2 | [x] Completed |
| REQ-009 | Resolve `effective_org_id` from `execution.organization_id` or `execution.raw_inputs.organization_id` (defaulting to `ROOT_SYSTEM` on `SystemOrganizations`) in `generate_profile_synthesis_and_pdf_task` (`@[backend_v2/workers/synthesis_worker.py]`) and pass `organization_id=effective_org_id` to `GlobalContextVarsDTO` and `LLMClient.from_tier`. | Step 3 | [x] Completed |
| REQ-010 | Resolve `effective_org_id` from `execution.organization_id` or `execution.raw_inputs.organization_id` (defaulting to `ROOT_SYSTEM` on `SystemOrganizations`) in `build_variance_metrics_and_task` (`@[backend_v2/workers/variance_synthesis.py]`) and pass `organization_id=effective_org_id` to `LLMClient.from_tier`. | Step 3 | [x] Completed |
| REQ-011 | Add positive and negative unit tests in `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]` (using direct typed constructors `ExecutionRecord(...)`, `OutputProfile(...)`, `Workflow(...)` to satisfy `TD_MODEL_FACTORY`) verifying `organization_id` forwarding and Fail-Fast `ConfigurationError` handling. | Step 3 | [x] Completed |
| REQ-012 | Add positive and negative unit tests in `@[backend_v2/tests/unit/workers/test_variance_synthesis.py]` verifying `organization_id` forwarding to `LLMClient.from_tier` and Fail-Fast `ConfigurationError` propagation. | Step 3 | [x] Completed |

# Session Handover Context

## Achieved
- Completed Step 1 (`c15bcdffa`): Wired `SecretService.resolve_llm_key` and `ResolvedCredentialDTO` into `LLMClient.__init__`, `LLMClient.from_tier`, `LLMClient.run_structured_task`, and `LLMClient.run_chat` in `@[backend_v2/llm/client.py]`, with unit tests in `@[backend_v2/tests/unit/llm/test_client.py]`.
- Completed Step 2 (`28ebec232`): Populated `GlobalContextVarsDTO(organization_id=initiator.organization_id, initiator_id=initiator.id, target_locale=payload.target_locale, profile_id=resolved_profile_id)` on `ExecutionMetadata` in `@[backend_v2/services/execution/ingress_service.py]` and wired `effective_org_id` into `ToolDispatcher` and `LLMClient.from_tier` inside `@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`, with unit tests in `@[backend_v2/tests/unit/services/execution/test_ingress_service.py]` and `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]`.
- Completed Step 3 (`c6e5274cf`): Wired `effective_org_id` (from `execution.organization_id` or `execution.raw_inputs.organization_id`, initialized to `SystemOrganizations.ROOT_SYSTEM.value`) into `GlobalContextVarsDTO` and `LLMClient.from_tier` in `@[backend_v2/workers/synthesis_worker.py]` and `@[backend_v2/workers/variance_synthesis.py]`, with unit tests in `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]` and `@[backend_v2/tests/unit/workers/test_variance_synthesis.py]`.
- Completed Tier 8 Audit (`/tier8-audit-plan`): Verified 12/12 requirements (`REQ-001`–`REQ-012`), >90% test coverage across all 5 modified modules (`client.py` 93%, `ingress_service.py` 96%, `engine_retry_stage.py` 100%, `synthesis_worker.py` 92%, `variance_synthesis.py` 100%), 89/89 DTO parity, and 0 fatal/advisory AST or technical debt violations.

## Learned
- The `ROOT_SYSTEM` constant on `SystemOrganizations` in `@[backend_v2/models/auth.py]` is `"org_0195f3a0000070008000000000000001"` (ending in `1`).
- `LLMProviderConfig.api_key` is `str | None` and `LLMFactory._resolve_provider_api_key` (`@[backend_v2/llm/provider/provider_factory.py]`) prioritizes `resolved_credential.secret_value.get_secret_value()` over `config.api_key`, so `LLMClient.from_tier` preserves `SecretStr` encapsulation by storing `self._resolved_credential` and forwarding `resolved_credential=self._resolved_credential` to `LLMFactory.create_provider`.
- In `@[backend_v2/tests/unit/workers/test_variance_synthesis.py]`, `_make_execution` uses `dict[str, ContextVariableValue]` (from `backend_v2.models.dtos.context_variables`) rather than `dict[str, Any]` so `scripts/audit_warning_baseline.py` Census `P` remains at `0`.

## Remaining
- Run Tier 2 Hardening (`scripts/auto_hardening_runner.py`) and `/tier7-describe-architecture @[docs/implementationplans/TRACKER_LLM_BYOK_Runtime_Wiring.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_BYOK_Runtime_Wiring.md] @[ki_god_code_prevention.md] @[ki_global_config_sovereignty.md] @[ki_zero_permissive_typing.md]`.

## Resume Command
```powershell
/tier7-describe-architecture @[docs/implementationplans/TRACKER_LLM_BYOK_Runtime_Wiring.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_BYOK_Runtime_Wiring.md] @[ki_god_code_prevention.md] @[ki_global_config_sovereignty.md] @[ki_zero_permissive_typing.md]
```
