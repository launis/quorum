<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

# Phase 1: Pre-Implementation Technical Debt Cleanups, Strict Recursive MCP Schema DTOs & Seed Vault Migration

**Overview:** Execute scoped Boy Scout technical debt cleanups across 64 Python findings and 18 Flutter Theme Sovereignty violations in touched targets (Zero-Behavioral-Change Gate), establish strict recursive JSON Schema DTOs (`MCPToolSchemaPropertyDTO`, `MCPToolInputSchemaDTO`, `MCPToolInvocationDTO`, JSON-RPC wire envelopes) with zero permissive typing (`dict[str, JsonValue]` eradicated), synchronize Cross-Language Freezed models and enum taxonomies, and migrate `seed_data.json` gateway configurations.

**Source:** @[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md#L178-L246] Phase 1: Pre-Implementation Technical Debt Cleanups, Strict Recursive MCP Schema DTOs & Seed Vault Migration

**Target Files:**
- `[MODIFY] @[backend_v2/models/enums.py]`
- `[MODIFY] @[backend_v2/models/dtos/mcp.py]`
- `[MODIFY] @[backend_v2/models/domain/system_config.py]`
- `[MODIFY] @[backend_v2/models/domain/mcp.py]`
- `[MODIFY] @[backend_v2/services/mcp/mcp_tool_loop.py]`
- `[MODIFY] @[backend_v2/database/interfaces.py]`
- `[MODIFY] @[backend_v2/database/repositories/system.py]`
- `[MODIFY] @[backend_v2/services/cache/typed_cache.py]`
- `[MODIFY] @[backend_v2/settings.py]`
- `[MODIFY] @[backend_v2/core/test_settings.py]`
- `[MODIFY] @[backend_v2/seed/seed_data.json#L209-L284]`
- `[MODIFY] @[client_app_v2/lib/core/models/enums.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart]`
- `[MODIFY] @[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/step_builder_view.dart]`
- `[MODIFY] @[backend_v2/tests/factories/model_factories.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_enum_parity.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_settings.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_mcp_gateways.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_sdui_template_parity.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_system.py]`
- `[MODIFY] @[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/domain/test_mcp.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/domain/test_system_config.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_mcp.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/test_v2_core.py]`
- `[MODIFY] @[backend_v2/tests/unit/seed/test_seed_registry.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_system_config_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_mcp_schema_bug.py]`
- `[MODIFY] @[client_app_v2/test/features/studio/models/mcp_gateway_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/studio/views/mcp_gateways_master_view_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart]`
- `[MODIFY] @[scripts/_ast_guardrails.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/dtos/mcp.py]` & `@[backend_v2/models/domain/system_config.py]` | Banned `dict[str, JsonValue]` in `AllowedMCPTool.input_schema`, bare `Field(...)` assignments, and missing `frozen=True` on DTO contracts. | Introduce recursive self-referential `MCPToolSchemaPropertyDTO` (`model_rebuild()`) and `MCPToolInputSchemaDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)`. | Eradicate ad-hoc untyped schema dictionaries; enforce deterministic recursive DTO tree. | `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test --ast-strict` and `uv run python scripts/audit_dto_parity.py`. |
| `@[backend_v2/services/mcp/mcp_tool_loop.py]` | Banned duck-typing `isinstance(..., (int, float, dict))` checks, in-place dict mutation, and raw dict messages. | Encapsulate validation inputs in strictly typed `MCPValidationContextDTO` and assemble messages via `LLMMessageDTO` with immutable `.model_copy()`. | Pruned dynamic dict accumulation in favor of typed DTO boundary. | `pytest backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py`. |
| `@[backend_v2/database/repositories/system.py]` & `@[backend_v2/database/interfaces.py]` | Banned single-document overwrite bug where `limit=1` overwrote `res_list[0]["id"]` on update; banned `TD_DICT_GET`. | Introduce `get_all_mcp_gateways() -> list[SystemConfigMCPGateways]`; upsert strictly by `doc_id = gateways_data.id`; bind local driver references. | Retain canonical `system_config` table without adding parallel storage engines. | `pytest backend_v2/tests/unit/database/repositories/test_system.py`. |
| `@[backend_v2/tests/factories/model_factories.py]` & `@[backend_v2/tests/unit/test_sdui_template_parity.py]` | Banned 17 `QGR020` bare mutable class-level list/dict defaults (`[]`, `{}`) and 6 bare mutable defaults in fake report DTOs. | Convert class attributes to `@classmethod` factory builders returning fresh collections per invocation; initialize fake report fields in `__init__`. | Pruned shared mutable state leaking across isolated test fixtures. | `uv run python scripts/audit_technical_debt.py --plan docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md --strict`. |
| `@[client_app_v2/lib/features/studio/views/]` | Banned missing `AppErrorBoundary` (`DGR009`), 18 naked `TextStyle` declarations, and 5 non-codec `Map<String, dynamic>` (`DGR005`). | Wrap root view bodies in `AppErrorBoundary`; bind styles to `Theme.of(context).textTheme`; replace raw maps with `Map<String, Object?>`. | Pruned uncontained widget trees and hardcoded design tokens; conform to Theme Sovereignty. | `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` and `uv run python scripts/audit_flutter_theme_sovereignty.py`. |
| `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]` & `@[client_app_v2/lib/core/models/enums.dart]` | Banned untyped `Map<String, Object?> inputSchema` and raw string capability in Flutter models violating cross-language parity. | Define Freezed `McpToolSchemaPropertyDto` and `McpToolInputSchemaDto`; bind `@Default(ToolCapability.search) ToolCapability capability`. | Single cross-language contract parity across Python Pydantic and Dart Freezed. | `uv run python scripts/audit_dto_parity.py` and `pytest backend_v2/tests/unit/test_enum_parity.py`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Inspect current state in @[backend_v2/models/dtos/mcp.py], @[backend_v2/models/domain/system_config.py], @[backend_v2/services/mcp/mcp_tool_loop.py], and @[client_app_v2/lib/features/studio/models/mcp_gateway.dart].</action>
    <action>Look forward: Verify all 64 Python technical debt findings and 18 Flutter Theme Sovereignty violations are mapped to Step 1.1 before introducing new DTOs in Step 1.2.</action>
    <constraint invariant="zero_permissive_typing">Never allow dict[str, Any] or dict[str, JsonValue] to remain in AllowedMCPTool or MCPFunctionDefinitionDTO.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: Mark Step 1.1, 1.2, 1.3 checkboxes in @[docs/epic/EPIC_159_tracker.md] upon completion of each sub-step.</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/models/enums.py]</backend>
    <backend>@[backend_v2/models/dtos/mcp.py]</backend>
    <backend>@[backend_v2/models/domain/system_config.py]</backend>
    <backend>@[backend_v2/models/domain/mcp.py]</backend>
    <backend>@[backend_v2/services/mcp/mcp_tool_loop.py]</backend>
    <backend>@[backend_v2/database/interfaces.py]</backend>
    <backend>@[backend_v2/database/repositories/system.py]</backend>
    <backend>@[backend_v2/services/cache/typed_cache.py]</backend>
    <backend>@[backend_v2/settings.py]</backend>
    <backend>@[backend_v2/core/test_settings.py]</backend>
    <backend>@[backend_v2/seed/seed_data.json]</backend>
    <frontend>@[client_app_v2/lib/core/models/enums.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/step_builder_view.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>Step 1.1 Zero-Behavioral-Change Gate completed: 64 Python tech debt items and 18 Flutter Theme Sovereignty violations resolved.</item>
    <item>Multi-gateway repository method get_all_mcp_gateways() implemented and limit=1 overwrite bug in update_mcp_gateways fixed.</item>
    <item>Taxonomies MCPTransportType, MCPAuthType, ToolCapability, and JSONSchemaPropertyType defined with 1:1 Dart enum parity.</item>
    <item>Recursive MCPToolSchemaPropertyDTO and MCPToolInputSchemaDTO created with strict forbid extra and zero JsonValue usage.</item>
    <item>AllowedMCPTool.input_schema migrated from dict[str, JsonValue] to MCPToolInputSchemaDTO with enabled flag added.</item>
    <item>SystemConfigMCPGateways updated with slug, endpoint_url, transport_type, auth_type, auth_env_var, and timeout_seconds.</item>
    <item>Freezed models McpToolSchemaPropertyDto, McpToolInputSchemaDto, and McpGateway updated with 100% parity.</item>
    <item>seed_data.json#L209-L284 migrated with canonical gateway fields and seeded via run_seed.py local.</item>
    <item>All unit test fixtures updated to use typed factories and passing 100%.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  </required_context_rules>

  <step id="1.1" name="Scoped Boy Scout Technical Debt Cleanups">
    <action>In @[backend_v2/services/mcp/mcp_tool_loop.py], define MCPValidationContextDTO and replace duck-typing isinstance checks, in-place dict mutations, and json.dumps(msg.content) fallbacks with typed DTO access.</action>
    <action>In @[backend_v2/database/repositories/system.py], @[backend_v2/database/interfaces.py], and @[backend_v2/tests/fakes/in_memory_repositories.py], add get_all_mcp_gateways() and fix update_mcp_gateways doc_id overwrite.</action>
    <action>In @[backend_v2/tests/factories/model_factories.py], convert 17 bare mutable list/dict class defaults to @classmethod builders.</action>
    <action>In @[backend_v2/tests/unit/test_sdui_template_parity.py], initialize fake report DTO fields in __init__.</action>
    <action>In @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart] and @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart], wrap root views in AppErrorBoundary.</action>
    <action>In @[client_app_v2/test/features/execution/views/widgets/sdui_golden_master_parity_test.dart], replace 5 Map&lt;String, dynamic&gt; with Map&lt;String, Object?&gt;.</action>
    <action>In @[client_app_v2/lib/features/studio/views/], replace 18 naked TextStyle declarations with Theme.of(context).textTheme tokens.</action>
    <constraint invariant="zero_behavioral_change">Step 1.1 MUST NOT alter existing runtime behavior, endpoints, or response payloads.</constraint>
    <audit_command>uv run python scripts/audit_technical_debt.py --plan docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md --strict</audit_command>
    <audit_command>uv run python scripts/audit_flutter_theme_sovereignty.py client_app_v2/lib/features/studio/views/mcp_gateway_view.dart client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart client_app_v2/lib/features/studio/views/step_builder_view.dart client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart</audit_command>
  </step>

  <step id="1.2" name="Taxonomies &amp; Recursive JSON Schema DTOs">
    <action>In @[backend_v2/models/enums.py] and @[client_app_v2/lib/core/models/enums.dart], define MCPTransportType, MCPAuthType, ToolCapability, and JSONSchemaPropertyType with @JsonEnum() parity.</action>
    <action>In @[backend_v2/models/dtos/mcp.py], define recursive MCPToolSchemaPropertyDTO, MCPToolInputSchemaDTO, ParsedMCPToolAliasDTO, MCPToolDescriptorDTO, MCPToolInvocationDTO, and JSON-RPC wire DTOs with AliasChoices.</action>
    <action>In @[backend_v2/models/domain/system_config.py] and @[backend_v2/models/domain/mcp.py], upgrade AllowedMCPTool.input_schema to MCPToolInputSchemaDTO, add gateway fields to SystemConfigMCPGateways, and enforce Annotated PEP 593 syntax.</action>
    <action>In @[client_app_v2/lib/features/studio/models/mcp_gateway.dart] and @[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart], define Freezed McpToolSchemaPropertyDto and McpToolInputSchemaDto, and update AllowedMcpTool and McpAuditTraceDto.</action>
    <action>In @[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart], update McpGatewayForm.addTool() to pass const McpToolInputSchemaDto().</action>
    <action>In @[backend_v2/settings.py] and @[backend_v2/core/test_settings.py], add mcp_default_timeout_seconds, mcp_discovery_timeout_seconds, mcp_max_response_chars, and mcp_allow_private_networks.</action>
    <constraint invariant="zero_permissive_typing">Disallow naked dict[str, Any] across all DTO models.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/models/ --test --ast-strict</audit_command>
    <audit_command>uv run python scripts/flutter_audit_loop.py client_app_v2/ --build</audit_command>
    <audit_command>uv run python scripts/audit_dto_parity.py</audit_command>
  </step>

  <step id="1.3" name="Seed Vault Integrity &amp; Default Gateway Migration">
    <action>In @[backend_v2/seed/seed_data.json#L209-L284], update sys_8172bda70c8641c5 to include slug: "default_mcp_gateway", transport_type: "streamable_http", auth_type: "bearer", auth_env_var: "TAVILY_API_KEY", timeout_seconds: 30, and enabled: true on all tools.</action>
    <action>Execute seed verification: uv run python backend_v2/seed/run_seed.py local --dry-run; uv run python scripts/audit_database_atoms.py --strict; uv run python backend_v2/seed/run_seed.py local.</action>
    <action>Update coupled test fixtures in test_mcp.py, test_system_config.py, and test_mcp_schema_bug.py to construct typed DTOs.</action>
    <action>In @[scripts/_ast_guardrails.py], remove system_config.py and dtos/mcp.py from OPEN_JSON_EXEMPTION_FILES.</action>
    <constraint invariant="seed_vault_immutability">Preserve all UUIDs and root persistence collections in seed_data.json.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict</audit_command>
  </step>
</execution_protocol>
```
