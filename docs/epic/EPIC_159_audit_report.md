# EPIC 159: Dynamic Protocol-Agnostic MCP Client & Gateway Architecture — System 2 Audit & Red-Team Report

**Target Epic**: `@[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]`
**Workflow**: `@[.agents/workflows/tier0-research-epic.md]`
**Audit Status**: **PASSED WITH IN-PLACE HARDENING APPLIED**

---

## 1. Context & Knowledge Item (KI) Coverage Audit

```text
📊 CONTEXT & KI COVERAGE AUDIT: 6 Rules verified, 14 KIs verified
```

### 1.1 Mandatory Rules Physically Loaded & Verified
1. `@[.agents/rules/00-antigravity-core.md]` — Global System & Meta-Cognition, Zero-Compromise Pledge, Full-Duplex Serialization Parity, Anti-Ambiguity Mandate.
2. `@[.agents/rules/01-python-backend.md]` — Strict Pydantic V2 (`ConfigDict(strict=True, extra="forbid", frozen=True)`), PEP 593 `Annotated` syntax, RFC 7807 Dual-Reporting, Async I/O Purity (`asyncio.to_thread` for blocking OS operations).
3. `@[.agents/rules/02_flutter_desktop.md]` — Freezed DTO parity (`@JsonSerializable(disallowUnrecognizedKeys: true)`), Riverpod Notifier state management, Theme Sovereignty (`Theme.of(context).textTheme` + `AppColors`), Desktop Pro-Tool Form Density (`isExpanded: true`).
4. `@[.agents/rules/03_seed_vault.md]` — Seed Vault SSOT invariants, `I18nText` preservation, foreign-key relational integrity (`allowed_mcp_tools` references).
5. `@[.agents/rules/04_directory_reference.md]` — Canonical workspace directory topology for `backend_v2/services/mcp/`, `backend_v2/models/dtos/`, `backend_v2/models/domain/`, and `client_app_v2/lib/features/studio/`.
6. `@[.agents/rules/05_llm_architecture.md]` — Four-Layer Clean Stack, Role Segregation & Fencing (`<![CDATA[...]]>` with `]]>` splitting), Alias Engine bijective mapping, OpenTelemetry/Logfire span instrumentation.

### 1.2 Knowledge Items Physically Loaded & Verified
1. `@[ki_mcp_tool_protocol.md]` — Multi-turn MCP Tool Execution Loop, `AliasRegistry` namespace resolution, `ToolDispatcher` routing, and XML `<mcp_tool_result>` injection.
2. `@[ki_zero_permissive_typing.md]` — Eradication of `Any`, `object`, and `JsonValue` in domain/DTO schemas; closed recursive JSON Schema AST DTOs (`MCPToolSchemaPropertyDTO`, `MCPToolInputSchemaDTO`, `MCPArgumentValue`) created in `@[backend_v2/models/dtos/mcp.py]`.
3. `@[ki_ast_guardrail_engine.md]` — `QGR001`–`QGR031` and `DGR001`–`DGR011` static AST guardrails and exemption list pruning in `@[scripts/_ast_guardrails.py]`.
4. `@[ki_system_audit_trail_xai.md]` — `MCPAuditTrace` provenance fields (`gateway_id`, `gateway_slug`, `namespaced_alias`) and UI rendering via `@[backend_v2/services/sdui/adapters/mcp_audit_adapter.py]` and `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]`.
5. `@[ki_sdui_matrix_synthesis.md]` — Cross-language DTO parity and full-duplex serialization guarantees between Python and Flutter.
6. `@[ki_desktop_pro_tool_studio_ux.md]` — Studio master-detail layout, form controllers, and dirty-state tracking in `McpGatewayView` and `StepBuilderView`.
7. `@[ki_workflow_context_governance.md]` — Step-level `allowed_mcp_tools` governance and positive ID-set filtering.
8. `@[ki_dual_axis_localization_architecture.md]` — `AppLocalizations` (`app_en.arb` / `app_fi.arb`) for UI chrome vs. `I18nText` for database-persisted entity labels.
9. `@[ki_app_error_boundary.md]` — RFC 7807 `ProblemDetails` handling and `AsyncErrorView` rendering in Flutter.
10. `@[ki_api_router_ssot_governance.md]` — Studio MCP gateway endpoint routing in `@[backend_v2/api/routers/studio/mcp_gateways.py]` and `@[client_app_v2/lib/core/api/studio_client.dart]`.
11. `@[ki_global_config_sovereignty.md]` — Centralized environment settings in `@[backend_v2/settings.py]` and `@[backend_v2/core/test_settings.py]`.
12. `@[ki_transient_error_resilience.md]` — Tenacity retry orchestration via `_is_transient_llm_error` bounded by `settings.llm_max_transient_retries` and `settings.llm_retry_delay`.
13. `@[ki_opentelemetry_logfire_observability.md]` — `logfire.span("mcp.client.initialize" | "mcp.client.list_tools" | "mcp.client.call_tool")` with DLP-safe metadata attributes (`gateway_id`, `gateway_slug`, `tool_id`, `transport_type`, `latency_ms`, `is_error`).
14. `@[ki_seed_vault_verification_and_sanitization.md]` — Atomic migration of `sys_8172bda70c8641c5` and workflow step `allowed_mcp_tools` arrays in `@[backend_v2/seed/seed_data.json]`.

---

## 2. Five-Axis System 2 Deconstruction & Pre-Flight Audit Results

### 2.1 Automated Pre-Flight Script Execution Summary
| Audit Script | Command | Result | Analysis |
| :--- | :--- | :--- | :--- |
| **Markdown Boundary Audit** | `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md` | **PASSED (Exit 0)** | Zero banned ambiguity tokens, zero absolute Windows paths, canonical `<required_context_rules>` XML header verified. |
| **Epic Coverage Audit** | `uv run python scripts/audit_epic_coverage.py --epic docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md` | **PRE-IMPL VERIFIED** | 100% of `[MODIFY]` target files exist on disk; only `[NEW]` files and `[DELETE]`/`<demolish>` legacy symbols report expected pre-implementation status. |
| **Technical Debt Audit (`--include-one-hop`)** | `uv run python scripts/audit_technical_debt.py --plan docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md --include-one-hop` | **70 Findings Mapped** | 64 findings across 78 direct target files + 6 findings across 172 1-hop caller files (`scripts/verify_e2e_report_parity.py`: 2, `scripts/verify_full_pipeline_e2e.py`: 4). All 64 target findings are explicitly cataloged in Phase 1.1. |
| **Flutter Theme Sovereignty Audit** | `uv run python scripts/audit_flutter_theme_sovereignty.py ...` | **18 Violations Mapped** | `mcp_gateway_view.dart` (4), `mcp_gateways_master_view.dart` (3), `step_builder_view.dart` (11), `workflow_step_card.dart` (0). All 18 violations are explicitly cataloged in Phase 1.1. |

### 2.2 Five-Axis Architectural Verification
1. **Structural Completeness & Cross-Layer Parity**:
   - Every Python DTO mutation in `@[backend_v2/models/dtos/mcp.py]` and `@[backend_v2/models/domain/system_config.py]` is paired with its exact Dart Freezed counterpart in `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]` and `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]` inside Phase 1.2 so Stage 8 (`scripts/audit_dto_parity.py`) passes at the end of Phase 1.
2. **Contract & Schema Integrity**:
   - Replaces untyped `dict[str, JsonValue]` (`AllowedMCPTool.input_schema` and `MCPFunctionDefinitionDTO.parameters`) with closed recursive Pydantic V2 models (`MCPToolSchemaPropertyDTO` and `MCPToolInputSchemaDTO` created in `@[backend_v2/models/dtos/mcp.py]`) and prunes `"backend_v2/models/domain/system_config.py"` and `"backend_v2/models/dtos/mcp.py"` from `OPEN_JSON_EXEMPTION_FILES` in `@[scripts/_ast_guardrails.py]`.
3. **Resilience, Security & Fail-Fast Boundaries**:
   - Enforces DNS-resolved SSRF egress validation (`MCPUrlValidator`), `follow_redirects=False`, environment-variable-only secret resolution (`auth_env_var in os.environ`), CDATA end-marker escaping (`]]>` -> `]]]]><![CDATA[>`), and pre-CDATA payload truncation (`mcp_max_response_chars` in `@[backend_v2/settings.py]`).
4. **Migration & Cutover Atomicity**:
   - Coordinates the cutover of `AliasRegistry`, `ToolDispatcher`, `StudioSystemConfigService`, `StudioWorkflowService`, and `@[backend_v2/seed/seed_data.json]` in Phase 3 so that workflow steps and gateways transition atomically to `{gateway_slug}__{tool_id}` namespaces before `[DELETE] @[backend_v2/services/mcp/tools/tavily.py]`, `[DELETE] @[backend_v2/services/mcp/tools/wikipedia.py]`, `[DELETE] @[backend_v2/services/mcp/tavily_search_client.py]`, and `[DELETE] @[backend_v2/services/mcp/wikipedia_client.py]` are deleted in Phase 3.3.
5. **Testability & Verification Completeness**:
   - Enforces mocked JSON-RPC fixtures, ISTQB negative/boundary tests, and global completion gates (`backend_audit_loop.py`, `flutter_audit_loop.py`, `test_sdui_semantic_parity.py`, and `audit_epic_coverage.py`).

---

## 3. Panel of Architects Evaluation

### 3.1 Global System Architect (SSOT & Blast Radius)
- **Assessment**: The 4-phase sequencing cleanly isolates DTO/Domain foundations (Phase 1) and protocol transport/discovery (Phase 2) before cutting over the runtime dispatcher and seed vault (Phase 3) and Studio UI discovery/multi-gateway binding (Phase 4).
- **Finding**: Phase 1.2 mutates `MCPToolSchemaPropertyDTO` and `MCPToolInputSchemaDTO` in Python and `McpToolSchemaPropertyDto` and `McpToolInputSchemaDto` in Dart. Both sides must maintain 1:1 field parity (`type`, `title`, `description`, `default`, `enum`, `items`, `properties`, `required`, `additional_properties`) so `scripts/audit_dto_parity.py` succeeds without mismatch.

### 3.2 Backend & Data Architect (JSON-RPC 2.0 Wire Protocol & Async I/O Purity)
- **Assessment**: Using `ConfigDict(strict=True, extra="forbid", frozen=True)` on all internal and wire DTOs upholds Zero Permissive Typing (`@[ki_zero_permissive_typing.md]`).
- **Critical Findings**:
  1. External MCP servers conforming to MCP `2025-03-26` serialize wire payloads using camelCase keys (`protocolVersion`, `clientInfo`, `serverInfo`, `inputSchema`, `isError`, `mimeType`) and include JSON Schema metadata fields (`title`, `additionalProperties`) in `tools/list` responses. Without explicit `AliasChoices` / `serialization_alias` mappings and `title` / `additional_properties` fields on `MCPToolSchemaPropertyDTO` and `MCPToolInputSchemaDTO`, `extra="forbid"` immediately crashes on real MCP servers (FastMCP, Pydantic, Zod).
  2. Calling synchronous `socket.getaddrinfo()` directly inside async methods (`GenericMCPClient` and `StudioSystemConfigService.discover_mcp_gateway_tools`) blocks the single-threaded Python `asyncio` event loop during slow DNS resolution.

### 3.3 SDUI & Frontend Architect (Studio UX & Capability Governance)
- **Assessment**: The Studio UI updates in Phase 4 (`mcp_gateway_view.dart` and `step_builder_view.dart`) properly group tools by gateway and enforce `DropdownButtonFormField` with `isExpanded: true`.
- **Critical Finding**: Standard MCP `tools/list` responses only return `name`, `description`, and `inputSchema`—they do not return Quorum's internal `ToolCapability` (`search`, `document_reader`, `action`, `general`). Without a per-tool capability selector in `McpGatewayView`, administrators cannot assign or change the `ToolCapability` of newly discovered tools, breaking `ToolDispatcher.resolve_primary_search_tool()` whenever a non-search tool is discovered or a search tool needs re-classification.

### 3.4 AI & Orchestration Architect (Prompt Injection, CDATA & Token Budgets)
- **Assessment**: Performing character budget truncation (`mcp_max_response_chars` in `@[backend_v2/settings.py]`) via `enforce_sentence_boundary_budget` (`@[backend_v2/services/length_budget_enforcer.py]`) *before* wrapping in `<![CDATA[...]]>` via `TemplateProcessor.encapsulate_payload` (`@[backend_v2/core/template_processor.py]`) prevents slicing a closing `]]>` tag in half and corrupting the XML prompt structure.

---

## 4. Red-Team Falsification & Root Cause Analysis

### 4.1 Failure Mode 1: External MCP JSON-RPC 2.0 CamelCase & JSON Schema Metadata Rejection under `extra="forbid"`
- **Vulnerability**: External MCP servers return camelCase keys (`protocolVersion`, `serverInfo`, `inputSchema`, `isError`, `mimeType`) and standard JSON Schema generators (FastMCP, Pydantic `model_json_schema()`, TypeScript `zod-to-json-schema`) emit `"title"` and `"additionalProperties": false` on both root `inputSchema` objects and nested property definitions. Under `ConfigDict(strict=True, extra="forbid", frozen=True)`, any un-aliased camelCase key or unmodeled `title` / `additionalProperties` key triggers an immediate `ValidationError` (`extra_forbidden`). Furthermore, MCP `tools/call` returns tool-level errors either as a JSON-RPC `error` object (`MCPJsonRpcErrorObjectDTO` defined in `@[backend_v2/models/dtos/mcp.py]`) or inside `result` with `isError: true`.
- **Hardening Applied to Epic**:
  1. Added `title: Annotated[str | None, Field(default=None, description="Optional JSON Schema property title emitted by external MCP servers.")] = None` and `additional_properties: Annotated[bool | None, Field(default=None, validation_alias=AliasChoices("additionalProperties", "additional_properties"), serialization_alias="additionalProperties", description="Whether additional properties are permitted on nested objects.")] = None` to both `MCPToolSchemaPropertyDTO` and `MCPToolInputSchemaDTO` created in `@[backend_v2/models/dtos/mcp.py]` and mirrored them in `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`.
  2. Specified explicit `validation_alias=AliasChoices(...)` and `serialization_alias=...` mappings across the wire DTOs created in `@[backend_v2/models/dtos/mcp.py]`: `MCPInitializeParamsDTO`, `MCPInitializeResultDTO`, `MCPDiscoveredToolWireDTO` (`inputSchema`), `MCPContentBlockDTO` (`mimeType`), `MCPToolCallResultDTO` (`isError`), and `MCPJsonRpcErrorObjectDTO`.
  3. Mandated Fail-Fast `AppException(ErrorCodes.EXTERNAL_SERVICE_ERROR)` with RFC-7807 `logger.error` whenever `response.error is not None` or `result.is_error is True`.

### 4.2 Failure Mode 2: Blocking OS DNS Resolution (`socket.getaddrinfo`) on the Asyncio Event Loop & Unbounded Discovery Timeouts
- **Vulnerability**: `socket.getaddrinfo()` is a synchronous OS syscall. Executing it directly on the main `asyncio` event loop thread before every `initialize`, `tools/list`, and `tools/call` request stalls all concurrent FastAPI SSE streams and Arq tasks whenever DNS resolution experiences latency or timeouts. Additionally, using `gateway.timeout_seconds` (configurable up to `300` seconds) for interactive Studio `list_tools` discovery causes the FastAPI request to hang for up to 15 minutes across 3 Tenacity retries if an operator enters an unreachable host.
- **Hardening Applied to Epic**:
  1. Kept `MCPUrlValidator.validate_mcp_endpoint_url(url: str, *, allow_private_networks: bool) -> str` as a pure synchronous static method for deterministic unit testing, and mandated `await asyncio.to_thread(MCPUrlValidator.validate_mcp_endpoint_url, ...)` at all async call sites (`GenericMCPClient` and `StudioSystemConfigService.discover_mcp_gateway_tools`).
  2. Bounded the `httpx.AsyncClient` timeout during `list_tools` discovery to `min(float(gateway.timeout_seconds), float(mcp_discovery_timeout_seconds))` (using `mcp_discovery_timeout_seconds` defined in `@[backend_v2/settings.py]`) while retaining `float(gateway.timeout_seconds)` for runtime `call_tool` execution.

### 4.3 Failure Mode 3: Capability Assignment Blindspot on Newly Discovered Tools
- **Vulnerability**: Because MCP `tools/list` only provides `name`, `description`, and `inputSchema`, newly discovered tools receive a default `ToolCapability.SEARCH` (`LaxToolCapability`), while existing tools preserve their configured `capability`, `enabled` state, and localized `I18nText` `name` on re-discovery. Without a UI control in `McpGatewayView` to inspect and update `AllowedMcpTool.capability`, administrators cannot reclassify discovered tools (`search`, `document_reader`, `action`, `general`) or designate which tool `ToolDispatcher.resolve_primary_search_tool()` selects for `source_verification_hook.py`.
- **Hardening Applied to Epic**:
  1. Mandated that `StudioSystemConfigService.discover_mcp_gateway_tools` preserves existing `capability`, `enabled`, and `I18nText` `name` when merging re-discovered tools by `tool_id`, while defaulting newly discovered tools to `ToolCapability.SEARCH`.
  2. Added an explicit per-tool `capability` `DropdownButtonFormField<String>` (`isExpanded: true`, options: `search`, `document_reader`, `action`, `general`) and `McpGatewayForm.updateToolCapability(int index, String capability)` in `@[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart]` and `@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]`.

### 4.4 Mandatory Architectural Falsification Questions & Zero Behavioral Change Gate
1. **Can any requirement be achieved by extending an existing DTO, Service, or Widget instead of creating a new file?**
   - Verified: All domain and wire DTOs are consolidated into existing `@[backend_v2/models/dtos/mcp.py]`, `@[backend_v2/models/domain/mcp.py]`, and `@[backend_v2/models/domain/system_config.py]`; Studio discovery is added as an action endpoint on existing `@[backend_v2/api/routers/studio/mcp_gateways.py]` and `@[backend_v2/services/studio/system_config_service.py]`; only 2 new backend implementation files (`[NEW] @[backend_v2/services/mcp/url_validator.py]` and `[NEW] @[backend_v2/services/mcp/generic_mcp_client.py]`) are created while 6 legacy hardcoded wrapper/model files (`[DELETE] @[backend_v2/services/mcp/tools/tavily.py]`, `[DELETE] @[backend_v2/services/mcp/tools/wikipedia.py]`, `[DELETE] @[backend_v2/services/mcp/tavily_search_client.py]`, `[DELETE] @[backend_v2/services/mcp/wikipedia_client.py]`, `[DELETE] @[backend_v2/models/domain/wikipedia.py]`, and `[DELETE] @[backend_v2/models/domain/tools.py]`) are demolished.
2. **Does any proposed validation check rely on negative string matching (`not startswith`), substring heuristics, or hardcoded ID lists?**
   - Verified: Zero negative string checks or substring heuristics exist. `AliasRegistry` uses a bijective regex (`^[a-z0-9]+(?:_[a-z0-9]+)*$`) forbidding double underscores inside `gateway.slug` so `namespaced_alias.split("__", 1)` is 100% deterministic, and all gateway/tool lookups use positive dictionary/set membership (`namespaced_alias in self._entries`, `gateway.auth_env_var in os.environ`).
3. **If a downstream consumer receives `None` or an empty collection from this Epic's output, does it fail-fast (`AppException`) or silently degrade?**
   - Verified: Missing gateways, disabled gateways/tools, unset environment variables, SSRF violations, JSON-RPC error objects, and `isError: true` tool results all log via RFC-7807 `logger.error` and raise `AppException` immediately.
4. **Zero Behavioral Change Gate**:
   - Verified: Phase 1.1 (Pre-Existing Technical Debt & Theme Sovereignty Cleanup) is a pure refactoring step and explicitly enforces the **ZERO BEHAVIORAL CHANGE GATE** in `@[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]` (preserving 100% identical runtime behavior, return values, and test assertions while resolving the 64 Python AST findings and 18 Flutter Theme Sovereignty violations).

---

## 5. Architectural Directive Table (Synchronized with Epic Section 2.5)

| Target File (`@[...]`) | Concrete Symbol / Function | Failure Mode / Debt Classification | Mandatory Action (`EXTEND` / `REFACTOR` / `DELETE` / `CREATE`) | Verification Command |
| :--- | :--- | :--- | :--- | :--- |
| `[MODIFY] @[backend_v2/models/dtos/mcp.py]` | `MCPToolSchemaPropertyDTO`, `MCPToolInputSchemaDTO`, `MCPFunctionDefinitionDTO`, `MCPDiscoveredToolWireDTO`, `MCPContentBlockDTO`, `MCPToolCallResultDTO` | `QGR001` (`JsonValue` in `parameters`) + External MCP JSON-RPC camelCase / JSON Schema metadata (`title`, `additionalProperties`) rejection under `extra="forbid"` | `REFACTOR` `MCPFunctionDefinitionDTO.parameters` to `MCPToolInputSchemaDTO`; `CREATE` closed recursive JSON Schema DTOs with `title` & `additional_properties` (`AliasChoices("additionalProperties", "additional_properties")`) and JSON-RPC wire DTOs with explicit camelCase `AliasChoices` (`inputSchema`, `isError`, `mimeType`, `protocolVersion`) | `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/mcp.py --test --ast-strict` |
| `[MODIFY] @[backend_v2/models/domain/system_config.py]` | `AllowedMCPTool`, `SystemConfigMCPGateways`, `MCPAuditTrace`, `MCPTransportType`, `MCPAuthType` | `QGR001` (`JsonValue` in `input_schema`), missing transport/auth/timeout config, and missing gateway provenance in `MCPAuditTrace` | `EXTEND` `SystemConfigMCPGateways` with `endpoint_url`, `transport_type`, `auth_type`, `auth_header_name`, `auth_env_var`, `timeout_seconds`, and single-underscore `slug` regex; `REFACTOR` `AllowedMCPTool.input_schema` to `MCPToolInputSchemaDTO` and add `enabled: bool = True`; `EXTEND` `MCPAuditTrace` with `gateway_id`, `gateway_slug`, `namespaced_alias` | `uv run python scripts/backend_audit_loop.py backend_v2/models/domain/system_config.py --test --ast-strict` |
| `[NEW] @[backend_v2/services/mcp/url_validator.py]` | `MCPUrlValidator.validate_mcp_endpoint_url` | SSRF vulnerability against cloud metadata (`169.254.169.254`), loopback (`127.0.0.0/8`, `::1`), and RFC 1918 private networks + Event-loop blocking during synchronous DNS lookup | `CREATE` pure validator resolving hostnames via `socket.getaddrinfo` (invoked via `await asyncio.to_thread(...)` in async callers) and blocking private/loopback/link-local/metadata IPs when `allow_private_networks=False` | `uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/url_validator.py --test --ast-strict` |
| `[NEW] @[backend_v2/services/mcp/generic_mcp_client.py]` | `GenericMCPClient` (`initialize`, `list_tools`, `call_tool`) | Missing protocol-agnostic MCP transport client (`STREAMABLE_HTTP` and `SSE`), unbounded discovery timeout, and JSON-RPC / `isError` silent failure | `CREATE` `httpx.AsyncClient` JSON-RPC 2.0 transport with `follow_redirects=False`, `asyncio.to_thread` DNS rebinding check, `mcp_discovery_timeout_seconds` cap on `list_tools`, env-var auth header injection, Fail-Fast `AppException` on `response.error` or `result.is_error`, and `tenacity` retry via `_is_transient_llm_error` | `uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/generic_mcp_client.py --test --ast-strict` |
| `[MODIFY] @[backend_v2/services/mcp/alias_registry.py]` | `AliasRegistry`, `ParsedMCPToolAliasDTO` | Flat tool namespace collisions across multiple gateways and `QGR023`/`QGR024` untyped return tuple | `REFACTOR` to build `{gateway_slug}__{tool_id}` bijective namespace mapping across enabled gateways/tools and return `ParsedMCPToolAliasDTO` created in `@[backend_v2/models/dtos/mcp.py]` | `uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/alias_registry.py --test --ast-strict` |
| `[MODIFY] @[backend_v2/services/mcp/dispatcher.py]` | `ToolDispatcher.execute_tool`, `ToolDispatcher.resolve_primary_search_tool` | Hardcoded `tool_id in ("tavily_search", "web_search")` / `"wikipedia_search"` routing (`ban_heuristic_identifier_matching`), missing CDATA escaping (`]]>`), and unbounded response length | `REFACTOR` to route 100% dynamically via `AliasRegistry` -> `GenericMCPClient.call_tool`, truncate raw output to `mcp_max_response_chars` before wrapping in `<![CDATA[...]]>` with `]]>` -> `]]]]><![CDATA[>` escaping, and resolve primary search tool via `ToolCapability.SEARCH` | `uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/dispatcher.py --test --ast-strict` |
| `[DELETE] @[backend_v2/services/mcp/tools/tavily.py]` & `[DELETE] @[backend_v2/services/mcp/tools/wikipedia.py]` | `TavilyTool`, `WikipediaSearchTool`, `WikipediaReadTool` | Obsolete hardcoded REST API wrappers superseded by `GenericMCPClient` (`the_no_legacy_mandate`) | `DELETE` legacy wrapper files and remove all imports from `dispatcher.py` and unit tests | `uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/ --test --ast-strict` |
| `[MODIFY] @[backend_v2/services/studio/system_config_service.py]` | `StudioSystemConfigService.discover_mcp_gateway_tools`, `StudioSystemConfigService.delete_mcp_gateways` | Missing live `tools/list` discovery orchestration, missing capability preservation on re-discovery, and broken gateway deletion flow | `EXTEND` with `discover_mcp_gateway_tools` (preserving existing `capability`, `enabled`, and `I18nText` `name` on re-discovered tools while defaulting new tools to `ToolCapability.SEARCH`) and `delete_mcp_gateways` invalidating `MCPGatewayCache` created in `@[backend_v2/services/cache/typed_cache.py]` | `uv run python scripts/backend_audit_loop.py backend_v2/services/studio/system_config_service.py --test --ast-strict` |
| `[MODIFY] @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]` & `[MODIFY] @[client_app_v2/lib/features/studio/views/step_builder_view.dart]` | `McpGatewayView`, `StepBuilderView` | 15 `PROHIBITED_NAKED_TEXT_STYLE` violations, missing transport/auth/discovery UI, missing per-tool `capability` selector, and single-gateway tool dropdown lock | `REFACTOR` naked `TextStyle` to `Theme.of(context).textTheme`; `EXTEND` `McpGatewayView` with endpoint/transport/auth controls, "Test & Discover Tools" action, and per-tool `capability` `DropdownButtonFormField<String>` (`isExpanded: true`) + `enabled` `Switch`; `REFACTOR` `StepBuilderView` to group tools across all enabled gateways using `{gateway_slug}__{tool_id}` | `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/ --build` |
