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
</required_context_rules>

# EPIC 159 System 2 Architectural Audit & Red-Team Report

- **Target Epic**: `@[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]`
- **Workflow Tier**: `/tier0-research-epic` (`@[.agents/workflows/tier0-research-epic.md]`)
- **Audit Status**: **HARDENED & APPROVED FOR TIER 1 PLANNING**
- **Context & KI Coverage Audit**: `6 Rules verified, 11 KIs verified.`

---

## 1. Executive Summary

`@[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]` transitions Quorum's Model Context Protocol (MCP) subsystem from a semi-dynamic dispatcher wired to static Python vendor wrappers (`tavily.py`, `wikipedia.py`, `tavily_search_client.py`, `wikipedia_client.py`) to a 100% dynamic JSON-RPC 2.0 protocol transport (`GenericMCPClient`) and runtime schema introspection pipeline (`POST /api/studio/mcp-gateways/{gateway_id}/discover`), while enforcing **Zero Permissive Typing** (`MCPToolSchemaPropertyDTO` and `MCPToolInputSchemaDTO` defined in `@[backend_v2/models/dtos/mcp.py]`), **SSRF Egress Firewalls** (`MCPUrlValidator` in `[NEW] @[backend_v2/services/mcp/url_validator.py]`), and **Mandatory CDATA / XML Sandwich Isolation** (`@[backend_v2/models/prompts/execution/mcp_prompts.py]`).

During our neuro-symbolic inspection of the physical codebase (`backend_v2/`, `client_app_v2/`, `scripts/`), our System 2 Red-Team audit uncovered **8 critical architectural defects and scope omissions** in the initial draft of `EPIC_159` that would have caused persistence data loss, AST guardrail failures, broken UI tool selection, and SSRF redirect bypasses during implementation. All 8 defects have been surgically remediated in-place inside `@[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]`.

---

## 2. Phase A: Scoped Technical Debt & Theme Sovereignty Sweep

We executed `uv run python scripts/audit_technical_debt.py --targets ... --include-one-hop` and `uv run python scripts/audit_flutter_theme_sovereignty.py` across all target files and their 1-hop callers:

| Target File | Tool / Rule ID | Severity | Physical Finding | Scheduled Resolution in `EPIC_159` |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/services/mcp/mcp_tool_loop.py]` | `QGR012` / Dict Eradication | **FATAL (Ignored in Allowlist)** | Uses `isinstance(strictness_val, (int, float))`, `isinstance(validation_context, dict)`, in-place `validation_context["mcp_source_texts"] = ...`, and raw `list[dict[str, str]]` message structures. | **Phase 1.1 & Phase 3.3**: Replace with `MCPValidationContextDTO` (defined in `@[backend_v2/models/dtos/mcp.py]`) and `LLMMessageDTO` (`@[backend_v2/models/llm.py]`), and remove file from `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` in `@[scripts/audit_dict_eradication.py]`. |
| `@[backend_v2/database/repositories/system.py]` | `TD_DICT_GET` & Multi-Gateway Bug | **CRITICAL** | Line 75 uses `existing.get("id")` and line 127 queries `type == "mcp_gateways"` with `limit=1`, overwriting `doc_id = str(res_list[0]["id"])` on every save. | **Phase 1.1**: Replace `.get("id")` with positive key check `"id" in existing and existing["id"] is not None`, add `get_all_mcp_gateways()`, and upsert strictly by `doc_id = gateways_data.id`. |
| `@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]` | `DGR009` & `PROHIBITED_NAKED_TEXT_STYLE` | **FATAL** | Missing `AppErrorBoundary` at line 14; 3 naked `TextStyle(` calls at lines 56, 126, and 158. | **Phase 1.1**: Wrap view body in `AppErrorBoundary` and replace all 3 naked `TextStyle(` calls with `Theme.of(context).textTheme`. |
| `@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]` | `DGR009` & `PROHIBITED_NAKED_TEXT_STYLE` | **FATAL** | Missing `AppErrorBoundary`; 4 naked `TextStyle(` calls at lines 203, 258, 375, and 415. | **Phase 1.1**: Wrap view body in `AppErrorBoundary` and replace all 4 naked `TextStyle(` calls with `Theme.of(context).textTheme`. |
| `@[client_app_v2/lib/features/studio/views/step_builder_view.dart]` | `PROHIBITED_NAKED_TEXT_STYLE` | **FATAL** | 11 naked `TextStyle(` calls at lines 305, 325, 430, 491, 539, 593, 601, 688, 696, 783, and 791; lines 438–480 flatten `mcpGateways` tools without filtering `tool.enabled` or prefixing `{gateway.slug}__`. | **Phase 1.1 & Phase 4.2**: Replace all 11 naked `TextStyle(` calls with `Theme.of(context).textTheme` and group enabled tools by `McpGateway` using `{gateway.slug}__{tool.toolId}`. |

---

## 3. Phase B: Panel of Architects Evaluation

1. **Global System Architect**:
   - Verified zero backwards-compatibility shims (`zero_backward_compatibility_planning_ban`) and single-pipeline determinism (`single_pipeline_invariant_mandate`).
   - Intercepted an illegal instruction in Draft Phase 2.2 that proposed adding `GenericMCPClient` to `BOUNDARY_EXEMPTION_FILES` in `@[scripts/_ast_guardrails.py]`. Under `ki_zero_permissive_typing.md` (Rule 30), `BOUNDARY_EXEMPTION_FILES` is permanently locked to 15 files. Hardened Phase 2.2 to use `MCPJsonRpcResponseDTO.model_validate_json(response.text)` and `MCPJsonRpcRequestDTO.model_dump(mode="json", by_alias=True, exclude_none=True)` on DTOs defined in `@[backend_v2/models/dtos/mcp.py]`, requiring zero boundary exemptions.
2. **Backend & Data Architect**:
   - Audited `@[backend_v2/database/repositories/system.py]` and `@[backend_v2/services/studio/system_config_service.py]`. Discovered that `SystemRepositoryImpl.update_mcp_gateways` had a hardcoded `limit=1` query that overwrote the first `mcp_gateways` record whenever a second gateway draft or clone was saved. Hardened Phase 1.1 and Phase 2.3 to add `get_all_mcp_gateways() -> list[SystemConfigMCPGateways]` and enforce in-place upsert by `gateways_data.id` alongside unique `slug` validation across gateways.
3. **SDUI & Frontend Architect**:
   - Verified that `MCPAuditTrace` extensions (`gateway_id`, `gateway_slug`, `namespaced_alias`) integrate seamlessly with `@[backend_v2/services/sdui/adapters/mcp_audit_adapter.py]` and `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` via `@[backend_v2/services/blueprint.py]`.
   - Corrected the Flutter Studio target boundary: `allowed_mcp_tools` is authored in `StepBuilderView` (`@[client_app_v2/lib/features/studio/views/step_builder_view.dart#L427-L480]`), not in `WorkflowStepCard` (`@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]`), because `WorkflowStepCard` edits `StepRule` DAG routing edges rather than `Step` / `NodeStrategy.llm`.
4. **AI & Orchestration Architect**:
   - Verified that Layer 1–3 prompt caching prefixes remain 100% static while dynamic MCP evidence is injected into Layer 4 wrapped in `<![CDATA[...]]>` and `<external_evidence_source>` via `@[backend_v2/models/prompts/execution/mcp_prompts.py]`.
   - Added explicit dependency injection wiring for `@[backend_v2/services/orchestrator/strategies/llm.py]` and `@[backend_v2/hooks/source_verification_hook.py]` so `ToolDispatcher` is constructed dynamically from `ISystemRepository.get_all_mcp_gateways()` when `DISPATCHER` is deleted.

---

## 4. Phase C: Quorum 2026 Modernity Gate Verification

- **Anti-Ambiguity Mandate**: Verified 0 occurrences of banned vague terms in `@[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]` via `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md`.
- **Zero Permissive Typing (`ConfigDict(strict=True, extra="forbid", frozen=True)`)**: Enforced on `MCPToolSchemaPropertyDTO`, `MCPToolInputSchemaDTO`, `MCPToolDescriptorDTO`, `MCPToolInvocationDTO`, `MCPValidationContextDTO`, and all JSON-RPC 2.0 wire DTOs defined in `@[backend_v2/models/dtos/mcp.py]`.
- **30% Deletion Test Applied**: Eliminated `@[backend_v2/models/domain/tools.py]` (`BaseTool`, `BaseSearchTool`, `StandardSearchInputDTO`), `@[backend_v2/models/domain/wikipedia.py]`, `@[backend_v2/services/mcp/tools/tavily.py]`, `@[backend_v2/services/mcp/tools/wikipedia.py]`, `@[backend_v2/services/mcp/tavily_search_client.py]`, and `@[backend_v2/services/mcp/wikipedia_client.py]`, returning `MCPAuditTrace` directly from `ToolDispatcher.execute_tool`.

---

## 5. Step 3: Falsification, Red-Teaming & Root Cause Analysis (8 Failure Modes Remediated)

### Failure Mode 1: Wrong Flutter View Targeted for `allowed_mcp_tools` (`StepBuilderView` vs `WorkflowStepCard`)
- **Root Cause**: Draft Phase 4.2 instructed modifying `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]` to render interactive `FilterChip` selectors for `step.allowedMcpTools`. Physical inspection of `@[client_app_v2/lib/features/studio/models/workflow.dart#L52-L96]` and `@[client_app_v2/lib/features/studio/views/step_builder_view.dart#L427-L480]` revealed that `WorkflowStepCard` binds to `StepRule` (which only holds `id`, `stepId`, `dependsOn`, `inputMappings`, and `inputFilters`), whereas `allowedMcpTools` resides on `Step` / `NodeStrategy.llm` and is edited in `StepBuilderView` (`step_builder_view.dart`). Furthermore, `step_builder_view.dart` lines 438–480 currently flatten `mcpGateways.expand((gateway) => gateway.tools)` without checking `tool.enabled` and save bare `tool.toolId` strings instead of `{gateway.slug}__{tool.toolId}`.
- **Architectural Justification**: We updated Section 1.3, Table 1.4, Table 2.4, Table 2.5, Phase 1.1, and Phase 4.2 to target `@[client_app_v2/lib/features/studio/views/step_builder_view.dart]` for interactive `FilterChip` selection of enabled `{gateway.slug}__{tool.toolId}` tools grouped by `McpGateway`, while keeping `WorkflowStepCard` strictly for read-only badge display.

### Failure Mode 2: Multi-Gateway Database Overwrite Bug in `SystemRepositoryImpl` & `StudioSystemConfigService`
- **Root Cause**: In `@[backend_v2/database/repositories/system.py]` (`update_mcp_gateways`), `SystemRepositoryImpl.update_mcp_gateways()` queried `Filter("type", "==", "mcp_gateways")` with `limit=1` and overwrote `doc_id = str(res_list[0]["id"])` rather than upserting by `gateways_data.id`. Additionally, `StudioSystemConfigService.list_mcp_gateways()` (`@[backend_v2/services/studio/system_config_service.py]`) called `get_mcp_gateways()` (`limit=1`), returning at most 1 gateway, and `create_mcp_gateway_draft` / `clone_mcp_gateways` produced invalid or duplicate `slug` values.
- **Architectural Justification**: We injected `[MODIFY] @[backend_v2/database/interfaces.py]`, `[MODIFY] @[backend_v2/database/repositories/system.py]`, and `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py]` into Phase 1.1 and Phase 2.3 to add `get_all_mcp_gateways() -> list[SystemConfigMCPGateways]`, fix `update_mcp_gateways(gateways_data)` to upsert in-place under `doc_id = gateways_data.id`, and enforce unique single-underscore `slug` generation across all gateways.

### Failure Mode 3: Locked `BOUNDARY_EXEMPTION_FILES` Violation & Unsynchronized Guardrail Allowlists
- **Root Cause**: Draft Phase 2.2 proposed annotating `GenericMCPClient` in `@[scripts/_ast_guardrails.py]` as an external wire boundary exemption. However, `BOUNDARY_EXEMPTION_FILES` in `@[scripts/_ast_guardrails.py]` is permanently locked to 15 files under `ki_zero_permissive_typing.md`. Furthermore, deleting `backend_v2/tests/unit/test_tavily_search_client.py` and cleaning `backend_v2/services/mcp/mcp_tool_loop.py` and `backend_v2/models/domain/system_config.py` without removing their entries from `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` in `@[scripts/audit_dict_eradication.py]`, `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` in `@[scripts/_ast_guardrails.py]`, and `[tool.ruff.lint.per-file-ignores]` in `@[pyproject.toml]` would leave stale allowlist entries.
- **Architectural Justification**: We removed the boundary exemption instruction from Phase 2.2, mandated direct Pydantic V2 wire validation (`MCPJsonRpcResponseDTO.model_validate_json`), and added explicit Phase 1.2 and Phase 3.3 steps to synchronize `@[scripts/_ast_guardrails.py]`, `@[scripts/audit_dict_eradication.py]`, and `@[pyproject.toml]`.

### Failure Mode 4: Missing DI Wiring in `LLMNodeStrategy` (`llm.py`) & `SourceVerificationHook` (`source_verification_hook.py`)
- **Root Cause**: Deleting module-level `DISPATCHER` and `TAVILY_TOOL_ID` breaks `@[backend_v2/services/orchestrator/strategies/llm.py]` (`execute_mcp_retrieval`) and `@[backend_v2/hooks/source_verification_hook.py]` / `@[backend_v2/services/source_verification_service.py]`, which were not fully wired in Draft Phase 3.2.
- **Architectural Justification**: We added `[MODIFY] @[backend_v2/services/orchestrator/strategies/llm.py]` and `[MODIFY] @[backend_v2/hooks/source_verification_hook.py]` to Phase 3.2 so active `SystemConfigMCPGateways` are loaded via `ISystemRepository.get_all_mcp_gateways()` and injected into `ToolDispatcher`.

### Failure Mode 5: SSRF Bypass via HTTP 301/302 Redirects & SSE Endpoint Negotiation
- **Root Cause**: Pre-flight validation of `gateway.endpoint_url` via `MCPUrlValidator` can be bypassed if an external server returns an HTTP 301/302/307/308 redirect to `http://169.254.169.254/latest/meta-data/` or `http://127.0.0.1:8000`, or if an `SSE` transport server emits an `endpoint` SSE event pointing to an internal/loopback URI for subsequent JSON-RPC `POST` calls.
- **Architectural Justification**: We hardened Phase 2.2 to enforce `follow_redirects=False` on all `httpx.AsyncClient` instances in `GenericMCPClient` and require re-validating the negotiated `SSE` POST endpoint URL via `MCPUrlValidator.validate_mcp_endpoint_url` before any `POST` request is transmitted.

### Failure Mode 6: Misclassified Flutter Test Paths & Omitted Coupled Backend Tests
- **Root Cause**: Draft Section 4.2 listed `[NEW] @[client_app_v2/test/unit/features/studio/mcp_gateway_view_test.dart]`, whereas the test already exists at `@[client_app_v2/test/features/studio/views/mcp_gateway_view_test.dart]` (alongside `@[client_app_v2/test/features/studio/models/mcp_gateway_test.dart]`) and asserts the legacy "Add Tool" UI that Phase 4 replaces. Additionally, `@[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]` and `@[backend_v2/tests/unit/services/orchestrator/test_mcp_schema_bug.py]` were omitted from Phase 1/3/4 test updates.
- **Architectural Justification**: We updated Phase 1.2 and Section 4.2 to include `[MODIFY] @[client_app_v2/test/features/studio/views/mcp_gateway_view_test.dart]`, `[MODIFY] @[client_app_v2/test/features/studio/models/mcp_gateway_test.dart]`, `[MODIFY] @[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]`, and `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_mcp_schema_bug.py]`.

### Failure Mode 7: 18 Pre-Existing `PROHIBITED_NAKED_TEXT_STYLE` Violations in Touched Flutter Views
- **Root Cause**: Running `uv run python scripts/audit_flutter_theme_sovereignty.py` on the three touched Studio views (`mcp_gateway_view.dart`, `mcp_gateways_master_view.dart`, `step_builder_view.dart`) failed with 18 `PROHIBITED_NAKED_TEXT_STYLE` violations, which blocks `flutter_audit_loop.py`.
- **Architectural Justification**: We injected all 18 `PROHIBITED_NAKED_TEXT_STYLE` cleanups into Phase 1.1 (`Scoped Boy Scout Technical Debt Cleanups in Touched Targets`).

### Failure Mode 8: Missing Cross-Referenced Knowledge Items in `<required_context_rules>`
- **Root Cause**: `ki_desktop_pro_tool_studio_ux.md` mandates including `<knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>` and `<knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>` whenever Studio UI views are modified.
- **Architectural Justification**: We added `ki_workflow_context_governance.md`, `ki_dual_axis_localization_architecture.md`, `ki_app_error_boundary.md`, `ki_api_router_ssot_governance.md`, and `ki_global_config_sovereignty.md` to `<required_context_rules>`.

---

## 6. Step 4: 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape | 3. Approved Best Practice | 4. Pruned Over-Engineering | 5. Verification & Fail-Fast |
| :--- | :--- | :--- | :--- | :--- |
| **MCP Schema & Wire DTOs**<br>`@[backend_v2/models/dtos/mcp.py]`<br>`@[backend_v2/models/domain/system_config.py]` | Raw `dict[str, JsonValue]` in `AllowedMCPTool.input_schema` and `MCPFunctionDefinitionDTO.parameters`; hardcoded `TavilySearchRequestDTO` and `TavilyToolArgsDTO`. | Recursive self-referential `MCPToolSchemaPropertyDTO` (`model_rebuild()`) and `MCPToolInputSchemaDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)`; serialization at provider adapter boundary via `.model_dump(mode="json", by_alias=True, exclude_none=True)`. | Eliminated vendor-specific tool argument DTOs across domain models; single canonical `MCPToolInvocationDTO` envelope for all MCP gateways. | `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test --ast-strict`; `ValidationError` -> `AppException(ErrorCodes.VALIDATION_FAILED)` on unknown schema keys. |
| **Multi-Gateway Persistence & Studio Service**<br>`@[backend_v2/database/interfaces.py]`<br>`@[backend_v2/database/repositories/system.py]`<br>`@[backend_v2/services/studio/system_config_service.py]`<br>`@[backend_v2/tests/fakes/in_memory_repositories.py]` | `limit=1` query overwriting `doc_id = str(res_list[0]["id"])` in `update_mcp_gateways`; `list_mcp_gateways` returning only a single gateway; duplicate `slug` values on draft/clone. | `get_all_mcp_gateways() -> list[SystemConfigMCPGateways]` sorted deterministically by `(m.slug, m.id)`; in-place upsert strictly by `doc_id = gateways_data.id`; unique `slug` enforcement across all `SystemConfigMCPGateways` entities. | Reused existing `SystemConfigMCPGateways` `system_config` collection without adding parallel database collections or secondary routers. | `@[backend_v2/tests/unit/test_mcp_gateways.py]` and `@[backend_v2/tests/unit/services/studio/test_system_config_service.py]` stateful multi-gateway roundtrip persistence tests. |
| **Protocol Transport & SSRF Firewall**<br>`[NEW] @[backend_v2/services/mcp/generic_mcp_client.py]`<br>`[NEW] @[backend_v2/services/mcp/url_validator.py]` | Bespoke per-vendor HTTP wrappers (`TavilySearchClient`, `WikipediaClient`), unvalidated external endpoint URLs, and open HTTP redirect following. | Protocol-agnostic JSON-RPC 2.0 `GenericMCPClient` supporting `STREAMABLE_HTTP` and `SSE` via `httpx.AsyncClient(follow_redirects=False, timeout=...)`; pre-flight DNS/IP validation via `MCPUrlValidator` on both initial endpoint and negotiated `SSE` POST endpoint URLs; strict wire parsing via `MCPJsonRpcResponseDTO.model_validate_json` with zero `BOUNDARY_EXEMPTION_FILES` expansion. | Zero external MCP SDK dependencies (`dependency_hallucination_firewall`); implemented directly with native `httpx` and Pydantic V2 wire DTOs. | `[NEW] @[backend_v2/tests/unit/services/mcp/test_url_validator.py]` and `[NEW] @[backend_v2/tests/unit/services/mcp/test_generic_mcp_client.py]`; Fail-Fast `AppException(ErrorCodes.SECURITY_VIOLATION)` on blocked CIDR or redirect. |
| **Dynamic Schema Compilation, DI & Routing**<br>`@[backend_v2/services/orchestrator/schema_factory.py]`<br>`@[backend_v2/services/mcp/alias_registry.py]`<br>`@[backend_v2/services/mcp/dispatcher.py]`<br>`@[backend_v2/services/mcp/mcp_tool_loop.py]`<br>`@[backend_v2/services/orchestrator/strategies/llm.py]`<br>`@[backend_v2/services/source_verification_service.py]` | Module-level `DISPATCHER` singleton in `@[backend_v2/services/mcp/mcp_tool_loop.py]` and `@[backend_v2/services/mcp/__init__.py]`; duck-typing `isinstance(..., dict)` in `mcp_tool_loop.py`; static `BaseTool` and `BaseSearchTool` classes in `@[backend_v2/models/domain/tools.py]`. | Runtime Pydantic V2 model compilation via `pydantic.create_model` in `SchemaFactory`; deterministic `{gateway_slug}__{tool_id}` prefixing in `AliasRegistry`; dynamic `ToolDispatcher` injected via `ISystemRepository.get_all_mcp_gateways()` and returning `MCPAuditTrace` directly. | **30% Deletion Test Applied**: Deleted `@[backend_v2/models/domain/tools.py]` (`BaseTool`, `BaseSearchTool`, `StandardSearchInputDTO`) and pruned the redundant `ToolExecutionResult` intermediate wrapper in favor of returning `MCPAuditTrace` directly. | `[NEW] @[backend_v2/tests/unit/services/mcp/test_alias_registry.py]` and `@[backend_v2/tests/unit/services/mcp/test_dispatcher.py]`; positive ID-set check `namespaced_alias in allowed_step_tools`. |
| **Flutter Studio & Step Builder Integration**<br>`@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`<br>`@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]`<br>`@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]`<br>`@[client_app_v2/lib/features/studio/views/step_builder_view.dart]`<br>`@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]` | Missing `AppErrorBoundary` (`DGR009`); 18 naked `TextStyle(` violations; untyped `Map<String, Object?> inputSchema` in `AllowedMcpTool`; manual JSON schema text editing; un-namespaced `tool.toolId` chips in `StepBuilderView`. | Strict Freezed `McpToolInputSchema` and `McpToolSchemaProperty` models; `AppErrorBoundary` wrapping; 100% `Theme.of(context).textTheme` adherence; live "Connect and Discover Tools" introspection action and per-gateway `{gateway.slug}__{tool.toolId}` `FilterChip` selectors in `StepBuilderView`. | Pruned manual raw JSON schema authoring from `McpGatewayView` in favor of read-only inspected schema tables and per-tool `enabled` allowlist switches. | `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`, `@[client_app_v2/test/features/studio/views/mcp_gateway_view_test.dart]`, and `@[client_app_v2/test/features/studio/models/mcp_gateway_test.dart]`. |
