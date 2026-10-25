<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
  <knowledge_item>@[ki_api_router_ssot_governance.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
  <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
</required_context_rules>

# EPIC 159 Tracker: Dynamic Model Context Protocol (MCP) Architecture & Runtime Schema Introspection

- **Epic:** @[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]
- **Task Directory:** @[docs/epic/tasks_EPIC_159/]

## Phase Execution Status

### Phase 1: Pre-Implementation Technical Debt Cleanups, Strict Recursive MCP Schema DTOs & Seed Vault Migration
**Plan:** @[docs/epic/tasks_EPIC_159/01_phase1_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_159/01_phase1_plan.md`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_159/01_phase1_plan.md] @[docs/epic/EPIC_159_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_159/01_phase1_plan.md] @[docs/epic/EPIC_159_tracker.md]` (`1af98e486`)
  - [x] Step 1.1: Scoped Boy Scout Technical Debt Cleanups in Touched Targets (Zero-Behavioral-Change Gate resolving 64 Python & 18 Flutter findings)
  - [x] Step 1.2: Taxonomies & Recursive JSON Schema DTOs (Zero Permissive Typing: MCPTransportType, MCPAuthType, ToolCapability, JSONSchemaPropertyType, MCPToolSchemaPropertyDTO, MCPToolInputSchemaDTO, MCPToolInvocationDTO)
  - [x] Step 1.3: Seed Vault Integrity, Default Gateway & Workflow Step Reference Migration (seed_data.json#L209-L284, #L21696-L21700, #L22022-L22026)
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_159/01_phase1_plan.md] @[docs/epic/EPIC_159_tracker.md]`

### Phase 2: Protocol-Agnostic GenericMCPClient, SSRF Firewall & Studio Tool Discovery Endpoint
**Plan:** @[docs/epic/tasks_EPIC_159/02_phase2_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_159/02_phase2_plan.md`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_159/02_phase2_plan.md] @[docs/epic/EPIC_159_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_159/02_phase2_plan.md] @[docs/epic/EPIC_159_tracker.md]` (`e5820b81e`)
  - [x] Step 2.1: SSRF URL & Network Egress Validator (MCPUrlValidator with non-blocking DNS resolution and cloud metadata / CIDR blocking)
  - [x] Step 2.2: Protocol-Agnostic GenericMCPClient (Streamable HTTP & HTTP+SSE with Tenacity retries and dual wire framing)
  - [x] Step 2.3: Studio Introspection Endpoint, Multi-Gateway Slug Uniqueness & Cache Persistence (POST /api/studio/mcp-gateways/{gateway_id}/discover, delete_mcp_gateways, MCPGatewayCache)
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_159/02_phase2_plan.md] @[docs/epic/EPIC_159_tracker.md]`

### Phase 3: Dynamic Pydantic Schema Factory, Namespace Routing & Legacy Wrapper Demolition
**Plan:** @[docs/epic/tasks_EPIC_159/03_phase3_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_159/03_phase3_plan.md`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_159/03_phase3_plan.md] @[docs/epic/EPIC_159_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_159/03_phase3_plan.md] @[docs/epic/EPIC_159_tracker.md]` (`42b256d1c`)
  - [x] Step 3.1: Runtime Pydantic Schema Factory (pydantic.create_model) & LLM Provider Wiring (schema_factory.py, provider.py)
  - [x] Step 3.2: Deterministic Namespace Prefixing ({gateway_slug}__{tool_name}) & Dynamic ToolDispatcher (alias_registry.py, dispatcher.py, mcp_tool_loop.py, strategies/llm.py, source_verification_service.py)
  - [x] Step 3.3: Legacy Static Wrapper Demolition & Guardrail Allowlist Sync (Delete tavily.py, wikipedia.py, tavily_search_client.py, wikipedia_client.py, models/domain/tools.py, models/domain/wikipedia.py, settings cleanup)
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_159/03_phase3_plan.md] @[docs/epic/EPIC_159_tracker.md]`

### Phase 4: Frontend Flutter Studio Integration, Freezed DTO Synchronization & E2E Verification Gate
**Plan:** @[docs/epic/tasks_EPIC_159/04_phase4_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_159/04_phase4_plan.md`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_159/04_phase4_plan.md] @[docs/epic/EPIC_159_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_159/04_phase4_plan.md] @[docs/epic/EPIC_159_tracker.md]` (`d6a9d57ec`)
  - [x] Step 4.1: Studio Client API, Controller Discovery Action & Localization (studio_client.dart, mcp_gateways_controller.dart, arb files)
  - [x] Step 4.2: Studio MCP Gateway View, Step Builder View & Workflow Step Card Integration (mcp_gateway_view.dart, step_builder_view.dart, workflow_step_card.dart, AppErrorBoundary, 1200px constraint)
  - [x] Step 4.3: Mandatory Live E2E Integration Gate & SDUI Audit Trail Parity (test_dynamic_mcp_pipeline_e2e.py, test_sdui_semantic_parity.py, test_integration_real_llm.py)
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_159/04_phase4_plan.md] @[docs/epic/EPIC_159_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [x] **[OK] Backend Integration Suite**: Run `uv run pytest backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py`
- [x] **[OK] Frontend Compilation & Build Runner Gate**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`

### Post-Implementation Gates
- [x] **[OK] Golden Master & Test Restoration Audit**: Verified zero skipped (@pytest.mark.skip) or commented-out tests across modified domains.
- [x] **[OK] Proxy Sunset & Consumer Migration**: Verified zero legacy static tool wrappers or deprecated symbols remain across codebase (audit_epic_coverage 100% PASS).
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker @[docs/epic/EPIC_159_tracker.md] --gate backend --agent-cmd "agy --dangerously-skip-permissions -i '/tier2-hardening-backend @[{target}]'"`
  - [x] @[backend_v2/models/enums.py]
  - [x] @[backend_v2/models/dtos/mcp.py]
  - [x] @[backend_v2/models/domain/system_config.py]
  - [x] @[backend_v2/models/domain/mcp.py]
  - [x] @[backend_v2/database/interfaces.py]
  - [x] @[backend_v2/database/repositories/system.py]
  - [x] @[backend_v2/settings.py]
  - [x] @[backend_v2/services/mcp/url_validator.py]
  - [x] @[backend_v2/services/mcp/generic_mcp_client.py]
  - [x] @[backend_v2/services/mcp/alias_registry.py]
  - [x] @[backend_v2/services/mcp/dispatcher.py]
  - [x] @[backend_v2/services/mcp/mcp_tool_loop.py]
  - [x] @[backend_v2/services/mcp/__init__.py]
  - [x] @[backend_v2/services/orchestrator/schema_factory.py]
  - [x] @[backend_v2/services/orchestrator/prompt_compiler.py]
  - [x] @[backend_v2/llm/schema_builder.py]
  - [x] @[backend_v2/llm/provider.py]
  - [x] @[backend_v2/services/orchestrator/strategies/llm.py]
  - [x] @[backend_v2/services/studio/system_config_service.py]
  - [x] @[backend_v2/api/routers/studio/mcp_gateways.py]
  - [x] @[backend_v2/services/cache/typed_cache.py]
  - [x] @[backend_v2/services/source_verification_service.py]
  - [x] @[backend_v2/hooks/source_verification_hook.py]
  - [x] @[backend_v2/services/blueprint.py]
  - [x] @[scripts/_ast_guardrails.py]
  - [x] @[scripts/audit_dict_eradication.py]
  - [x] @[.agents/rules/04_directory_reference.md]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker @[docs/epic/EPIC_159_tracker.md] --gate frontend --agent-cmd "agy --dangerously-skip-permissions -i '/tier2-hardening-frontend @[{target}]'"`
  - [x] @[client_app_v2/lib/core/models/enums.dart]
  - [x] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]
  - [x] @[client_app_v2/lib/core/api/studio_client.dart]
  - [x] @[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart]
  - [x] @[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]
  - [x] @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]
  - [x] @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]
  - [x] @[client_app_v2/lib/features/studio/views/step_builder_view.dart]
  - [x] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]
- [x] **[OK] Pre-Delete Audit**: Verify zero orphaned references to deleted static tools (`tavily`, `wikipedia`, `BaseTool`) exist across the codebase.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for all surviving and new MCP services (`generic_mcp_client.py`, `url_validator.py`, `alias_registry.py`, `dispatcher.py`, `schema_factory.py`).

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/epic/EPIC_159_tracker.md] @[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md] @[ki_mcp_tool_protocol.md] @[ki_system_audit_trail_xai.md] @[ki_zero_permissive_typing.md] @[ki_desktop_pro_tool_studio_ux.md] @[ki_workflow_context_governance.md] @[ki_api_router_ssot_governance.md] @[ki_global_config_sovereignty.md] @[ki_transient_error_resilience.md] @[ki_opentelemetry_logfire_observability.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_mcp_tool_protocol.md]`: Document protocol-agnostic `GenericMCPClient` (Streamable HTTP and HTTP+SSE transport), SSRF / DNS-rebinding firewall (`MCPUrlValidator`), recursive `MCPToolSchemaPropertyDTO` and `MCPToolInputSchemaDTO` JSON Schema AST, dynamic `SchemaFactory` runtime compilation via `pydantic.create_model`, deterministic `{gateway_slug}__{tool_id}` namespace routing, and demolition of legacy static tool classes (`tavily.py`, `wikipedia.py`, `models/domain/tools.py`).
     - `@[ki_system_audit_trail_xai.md]`: Document `MCPAuditTrace` provenance propagation (`gateway_id`, `gateway_slug`, `namespaced_alias`), OpenTelemetry `mcp.tool_call` span attributes (`mcp.tool_id`, `mcp.gateway_id`, `mcp.step_id`, `mcp.capability`), and SDUI rendering via `MCPAuditAdapter`.
     - `@[ki_zero_permissive_typing.md]`: Document complete eradication of `dict[str, JsonValue]` in `AllowedMCPTool` and `MCPFunctionDefinitionDTO` in favor of strict recursive Pydantic V2 models, and removal of MCP models from `OPEN_JSON_EXEMPTION_FILES`.
     - `@[ki_desktop_pro_tool_studio_ux.md]`: Document Studio MCP Gateway View (`maxWidth: 1200` canvas containment, live "Connect and Discover Tools" action, horizontal scroll parameter schema preview table, `ToolCapability` dropdown, and per-tool allowlist switches) and Step Builder View (`{gateway.slug}__{tool.toolId}` chip selectors).
     - `@[ki_workflow_context_governance.md]`: Document step-level `allowed_mcp_tools` namespace binding and positive ID-set validation in `ToolDispatcher`.
     - `@[ki_api_router_ssot_governance.md]`: Document single-router SSOT for `/api/studio/mcp-gateways` including `POST /{gateway_id}/discover` and dedicated `delete_mcp_gateways`.
     - `@[ki_global_config_sovereignty.md]`: Document replacement of vendor-specific Wikipedia/Tavily settings with generic MCP settings in `settings.py` (`mcp_default_timeout_seconds`, `mcp_discovery_timeout_seconds`, `mcp_max_response_chars`, `mcp_allow_private_networks`).
     - `@[ki_transient_error_resilience.md]`: Document Tenacity retry coordination with `_is_transient_llm_error` across outbound JSON-RPC 2.0 requests.
     - `@[ki_opentelemetry_logfire_observability.md]`: Document distributed tracing spans for dynamic MCP discovery and tool execution loops.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to remove deleted static wrappers (`tavily.py`, `wikipedia.py`, `tavily_search_client.py`, `wikipedia_client.py`, `models/domain/wikipedia.py`, `models/domain/tools.py`) and register `generic_mcp_client.py` and `url_validator.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` (specifically `01_system_context_and_invariants.md`, `04_execution_engine_and_worker_pipeline.md`, and `05_resilience_and_observability.md`) describing protocol-agnostic tool transport, SSRF protection, and runtime schema compilation without historical language or Epic IDs.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
1. **Execution Protocol**: Execute sequentially through Phases 1 to 4. Each phase follows the mandatory workflow loop: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute --full-auto -> /tier8-audit-plan`. You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands.
2. **Atomic Commits**: After completing each cohesive logical step and verifying tests with `uv run python scripts/backend_audit_loop.py` or `flutter_audit_loop.py`, commit changes using conventional commits format (`feat(mcp): ...`, `fix(mcp): ...`).
3. **Database Seeding Mandate**: When migrating seed data in Phase 1.3, execute `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict` before applying changes via `uv run python backend_v2/seed/run_seed.py local`.
4. **Execution Mode**: Supports both Step-by-Step and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto` or via `scripts/auto_phase_runner.py`). Progresses autonomously across steps as long as quality gates pass 100%, and triggers clean session handover when the context budget limit is reached (>8 turns, 3 atomic commits, or >5 modified files).
5. **Post-Implementation Gates**: Once all 4 Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` (or unattended via `uv run python scripts/auto_hardening_runner.py --tracker @[docs/epic/EPIC_159_tracker.md] --gate backend --agent-cmd "agy --dangerously-skip-permissions -i '/tier2-hardening-backend @[{target}]'"`) -> `/tier2-hardening-frontend` (or unattended via `uv run python scripts/auto_hardening_runner.py --tracker @[docs/epic/EPIC_159_tracker.md] --gate frontend --agent-cmd "agy --dangerously-skip-permissions -i '/tier2-hardening-frontend @[{target}]'"`) -> parameterized `/tier7-describe-architecture` (with target KIs and directives) -> `/tier8-audit-epic`.

## Requirements Traceability Matrix

| Requirement ID | Technical Requirement Description | Implementation Phase & Step | Verification & Acceptance Gate |
| :--- | :--- | :--- | :--- |
| **REQ-159-001** | Resolve 17 `QGR020` FATAL bare mutable class-level defaults in `model_factories.py` and 6 in `test_sdui_template_parity.py` by converting to `@classmethod` / `__init__` builders. | Phase 1, Step 1.1 | `scripts/audit_technical_debt.py` reports 0 `QGR020` findings. |
| **REQ-159-002** | Resolve 5 `DGR005` FATAL non-codec `Map<String, dynamic>` violations in `sdui_golden_master_parity_test.dart` by converting to `Map<String, Object?>`. | Phase 1, Step 1.1 | `scripts/audit_technical_debt.py` reports 0 `DGR005` findings. |
| **REQ-159-003** | Resolve `DGR009` missing `AppErrorBoundary` violations in `mcp_gateways_master_view.dart` and `mcp_gateway_view.dart`. | Phase 1, Step 1.1 | `mcp_gateways_master_view_test.dart` asserts error boundary wrapper. |
| **REQ-159-004** | Resolve 18 `PROHIBITED_NAKED_TEXT_STYLE` violations across `mcp_gateway_view.dart`, `mcp_gateways_master_view.dart`, and `step_builder_view.dart` using `Theme.of(context).textTheme`. | Phase 1, Step 1.1 | `scripts/audit_flutter_theme_sovereignty.py` reports 0 findings on target views. |
| **REQ-159-005** | Fix single-document `limit=1` overwrite bug in `SystemRepositoryImpl.update_mcp_gateways` and resolve `TD_DICT_GET` in `system.py` and `typed_cache.py`. | Phase 1, Step 1.1 | `test_system.py` verifies in-place upsert by `doc_id = gateways_data.id`. |
| **REQ-159-006** | Replace duck-typing `isinstance(..., dict)` and raw message dictionaries in `mcp_tool_loop.py` with `MCPValidationContextDTO` and `LLMMessageDTO.model_copy`. | Phase 1, Step 1.1 | `test_mcp_tool_loop.py` and `scripts/audit_technical_debt.py --strict` pass with 0 findings. |
| **REQ-159-007** | Define `MCPTransportType(StrEnum)` and `MCPAuthType(StrEnum)` in Python with 1:1 `@JsonEnum()` parity in Dart (`enums.dart`). | Phase 1, Step 1.2 | `backend_v2/tests/unit/test_enum_parity.py` verifies 1:1 enum value parity. |
| **REQ-159-008** | Define `@JsonEnum() enum ToolCapability` in Dart with 1:1 parity with Python `ToolCapability(StrEnum)` resolving Dart raw string enum violation. | Phase 1, Step 1.2 | `backend_v2/tests/unit/test_enum_parity.py` passes with explicit `ToolCapability` mapping. |
| **REQ-159-009** | Define `JSONSchemaPropertyType(StrEnum)` in Python with 1:1 `@JsonEnum()` parity in Dart (`enums.dart`). | Phase 1, Step 1.2 | `backend_v2/tests/unit/test_enum_parity.py` passes. |
| **REQ-159-010** | Create recursive `MCPToolSchemaPropertyDTO` (`model_rebuild()`) and `MCPToolInputSchemaDTO` with strict `extra="forbid"`, `frozen=True`, and `AliasChoices`. | Phase 1, Step 1.2 | `test_mcp.py` asserts recursive serialization roundtrips without `dict[str, JsonValue]`. |
| **REQ-159-011** | Enforce `min_length=1` on `AllowedMCPTool.tool_id` and replace `input_schema: dict[str, JsonValue]` with `input_schema: MCPToolInputSchemaDTO`. | Phase 1, Step 1.2 | `scripts/_ast_guardrails.py` eliminates `system_config.py` from `OPEN_JSON_EXEMPTION_FILES`. |
| **REQ-159-012** | Create typed JSON-RPC 2.0 wire boundary DTOs (`MCPInitializeParamsDTO`, `MCPToolCallParamsDTO`, `MCPDiscoveredToolWireDTO`, `MCPToolCallResultDTO`, `MCPJsonRpcResponseDTO`). | Phase 1, Step 1.2 | `test_mcp.py` validates camelCase external wire serialization roundtrips. |
| **REQ-159-013** | Add `gateway_id`, `gateway_slug`, and `namespaced_alias` provenance fields to `MCPAuditTrace` with 1:1 Freezed parity on `McpAuditTraceDto`. | Phase 1, Step 1.2 | `scripts/audit_dto_parity.py` asserts 100% full-duplex DTO parity. |
| **REQ-159-014** | Atomically migrate default MCP gateway configuration in `seed_data.json#L209-L284` and step tool references in `#L21696-L21700` and `#L22022-L22026`. | Phase 1, Step 1.3 | `backend_v2/seed/run_seed.py local --dry-run` and `scripts/audit_database_atoms.py --strict` pass. |
| **REQ-159-015** | Implement `MCPUrlValidator` blocking SSRF loopback, private subnets, cloud metadata (`169.254.169.254`), and redirects via non-blocking `asyncio.to_thread`. | Phase 2, Step 2.1 | `test_url_validator.py` passes with ISTQB positive and negative boundary tests. |
| **REQ-159-016** | Implement protocol-agnostic `GenericMCPClient` supporting `STREAMABLE_HTTP` and `SSE` with Tenacity `_is_transient_llm_error` retry coordination. | Phase 2, Step 2.2 | `test_generic_mcp_client.py` passes unit tests for Streamable HTTP and SSE transports. |
| **REQ-159-017** | Implement dual wire-framing parser in `GenericMCPClient` handling both direct `application/json` and SSE `text/event-stream` (`data:` frame extraction). | Phase 2, Step 2.2 | `test_generic_mcp_client.py` asserts successful JSON-RPC extraction from SSE stream. |
| **REQ-159-018** | Enforce sentence boundary character truncation and mandatory CDATA encapsulation on all external MCP responses in `GenericMCPClient.call_tool`. | Phase 2, Step 2.2 | `test_cdata_hardening_comprehensive.py` and `test_tool_loop_sanitization.py` pass. |
| **REQ-159-019** | Register typed cache namespace `MCPGatewayCache` in `typed_cache.py` with deterministic invalidation upon gateway mutation. | Phase 2, Step 2.3 | `test_system_config_service.py` asserts cache invalidation on save and delete. |
| **REQ-159-020** | Implement `POST /api/studio/mcp-gateways/{gateway_id}/discover` runtime introspection endpoint in router and `StudioSystemConfigService`. | Phase 2, Step 2.3 | `test_mcp_gateways.py` and `test_system_config_service.py` assert discovery roundtrip. |
| **REQ-159-021** | Implement dedicated `delete_mcp_gateways` method in `StudioSystemConfigService` eliminating 404 crash on gateway deletion. | Phase 2, Step 2.3 | `test_mcp_gateways.py` asserts successful 204 deletion of MCP gateways. |
| **REQ-159-022** | Implement runtime Pydantic model compilation via `pydantic.create_model` in `SchemaFactory.create_mcp_tool_argument_model`. | Phase 3, Step 3.1 | `test_mcp_tool_loop.py` validates arguments against runtime Pydantic models. |
| **REQ-159-023** | Implement `SchemaFactory.build_mcp_tool_declaration` producing `MCPToolDeclarationDTO` serialized with `exclude_none=True` in `LiteLLMProvider`. | Phase 3, Step 3.1 | `test_llm.py` asserts provider function declaration generation with standard JSON Schema. |
| **REQ-159-024** | Implement deterministic `{gateway_slug}__{tool_id}` prefixing and bijective `split("__", 1)` parsing into `ParsedMCPToolAliasDTO` in `AliasRegistry`. | Phase 3, Step 3.2 | `test_alias_registry.py` passes collision-free namespace validation. |
| **REQ-159-025** | Refactor `ToolDispatcher` to accept active `list[SystemConfigMCPGateways]` and `GenericMCPClient`, returning `MCPAuditTrace` directly with OpenTelemetry spans. | Phase 3, Step 3.2 | `test_dispatcher.py` asserts positive ID-set enforcement and span emission. |
| **REQ-159-026** | Remove module-level static `DISPATCHER` singleton and purge all imports of `tavily` and `wikipedia` from `mcp_tool_loop.py` and `__init__.py`. | Phase 3, Step 3.2 | `backend_audit_loop.py` asserts clean imports across `backend_v2/services/mcp/`. |
| **REQ-159-027** | Update `SourceVerificationService` and `source_verification_hook` to dynamically resolve search tools from `ToolDispatcher`. | Phase 3, Step 3.2 | `test_source_verification_service.py` and `test_source_verification_hook.py` pass. |
| **REQ-159-028** | Physically delete all 6 legacy static wrapper files and 9 obsolete test files per `<demolish>` inventory. | Phase 3, Step 3.3 | Files physically absent from repository; `git status` shows deleted files. |
| **REQ-159-029** | Purge vendor-specific Wikipedia/Tavily settings from `settings.py`, `core/test_settings.py`, and `test_settings.py`. | Phase 3, Step 3.3 | `test_settings.py` passes with generic MCP settings SSOT. |
| **REQ-159-030** | Add AST guardrail ensuring zero imports of deleted legacy wrapper modules exist anywhere in `backend_v2/`. | Phase 3, Step 3.3 | `scripts/backend_audit_loop.py --ast-strict` passes with 0 violations. |
| **REQ-159-031** | Add `discoverMcpGatewayTools(String id)` to `StudioClient` and `discoverTools(String id)` to `McpGatewaysController` with unconditional error rethrow. | Phase 4, Step 4.1 | `mcp_gateways_controller_test.dart` passes. |
| **REQ-159-032** | Add Finnish and English localization keys for all MCP gateway connection parameters, discovery buttons, and parameter preview tables. | Phase 4, Step 4.1 | `client_app_v2/lib/l10n/` ARB files compile with 0 missing keys. |
| **REQ-159-033** | Modernize `McpGatewayView` with `maxWidth: 1200` canvas containment, live discovery action, parameter schema `DataTable`, and allowlist switches. | Phase 4, Step 4.2 | `mcp_gateway_view_test.dart` passes widget tree assertions. |
| **REQ-159-034** | Update `StepBuilderView` to display dynamically discovered tools grouped by gateway as `{gateway.slug}__{tool.toolId}` `FilterChip` selectors. | Phase 4, Step 4.2 | `step_builder_view.dart` passes widget tests with dynamic tool selection. |
| **REQ-159-035** | Implement full pipeline integration test in `test_dynamic_mcp_pipeline_e2e.py` verifying mock MCP server, discovery, execution, and SDUI audit trail. | Phase 4, Step 4.3 | `uv run pytest backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py` passes. |
| **REQ-159-036** | Execute mandatory SDUI semantic parity gate and live real-LLM E2E verification test. | Phase 4, Step 4.3 | `test_sdui_semantic_parity.py` and `test_integration_real_llm.py` pass. |

# Session Handover Context

## Achieved
- Completed Phase 1 (`@[docs/epic/tasks_EPIC_159/01_phase1_plan.md]`), Phase 2 (`@[docs/epic/tasks_EPIC_159/02_phase2_plan.md]`), Phase 3 (`@[docs/epic/tasks_EPIC_159/03_phase3_plan.md]`), and Phase 4 (`@[docs/epic/tasks_EPIC_159/04_phase4_plan.md]`):
  - **Step 4.1 (`e98ccfa3d`)**: Implemented `StudioClient.discoverMcpGatewayTools(String id)` in `@[client_app_v2/lib/core/api/studio_client.dart]`, `McpGatewaysController.discoverTools(String id)` and `McpGatewayForm.discoverTools()` in `@[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart]` with `mcpGatewayByIdProvider` cache invalidation and Fail-Fast error propagation, Dual-Axis localization keys in `@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]`, and controller unit tests in `@[client_app_v2/test/features/studio/controllers/mcp_gateways_controller_test.dart]`.
  - **Step 4.2 (`426c9336c`)**: Modernized `@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]` (`1200px` `ConstrainedBox`, Connection & Auth Card, live "Connect and Discover Tools" button, `ToolCapability` dropdown, read-only parameter preview `DataTable`, allowlist `SwitchListTile`), updated `@[client_app_v2/lib/features/studio/views/step_builder_view.dart]` to render per-gateway `{gateway.slug}__{tool.toolId}` `FilterChip` selectors, updated `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]` to render read-only tool badges, and verified all 20 widget tests and `audit_flutter_theme_sovereignty.py` (0 violations).
  - **Step 4.3**: Implemented full-lifecycle dynamic MCP pipeline E2E tests in `@[backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py]` (6 tests: 2 positive + 4 ISTQB negative, 98% coverage), updated `@[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]` (2 tests, 97% coverage), `@[backend_v2/tests/integration/test_sdui_semantic_parity.py]` (2 tests, 94% coverage), and `@[backend_v2/tests/integration/test_integration_real_llm.py]` (100% coverage), and verified 0 technical debt findings across both `04_phase4_plan.md` and `EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md` (`audit_technical_debt.py --strict` and `audit_epic_coverage.py` 100% PASS).

## Learned
- All 4 phases of Epic 159 are implemented and pass `backend_audit_loop.py --test --ast-strict`, `flutter_audit_loop.py client_app_v2/ --build`, `audit_flutter_theme_sovereignty.py`, `audit_technical_debt.py --strict`, and `audit_epic_coverage.py`.

## Remaining
- Execute Tier 8 Plan Audit on Phase 4 via `/tier8-audit-plan @[docs/epic/tasks_EPIC_159/04_phase4_plan.md] @[docs/epic/EPIC_159_tracker.md]`.
- Proceed to Post-Implementation Gates (`Tier 2 Hardening (Backend)`, `Tier 2 Hardening (Frontend)`, `/tier7-describe-architecture`, and `/tier8-audit-epic @[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]`).

## Resume Command
`/tier8-audit-plan @[docs/epic/tasks_EPIC_159/04_phase4_plan.md] @[docs/epic/EPIC_159_tracker.md]`
