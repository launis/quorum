<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
</required_context_rules>

# Phase 3: Dynamic Pydantic Schema Factory, Namespace Routing & Legacy Wrapper Demolition

**Overview:** Implement runtime Pydantic V2 schema compilation via `pydantic.create_model` in `SchemaFactory`, establish deterministic `{gateway_slug}__{tool_id}` prefixing in `AliasRegistry` and dynamic `ToolDispatcher` routing, migrate step `allowed_mcp_tools` references in `seed_data.json`, and execute the 30% Deletion Test by completely demolishing legacy static wrappers (`tavily.py`, `wikipedia.py`, `tools.py`, `models/domain/wikipedia.py`, settings, and tests).

**Source:** @[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md#L287-L346] Phase 3: Dynamic Pydantic Schema Factory, Namespace Routing & Legacy Wrapper Demolition

**Target Files:**
- `[MODIFY] @[backend_v2/services/orchestrator/schema_factory.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/prompt_compiler.py]`
- `[MODIFY] @[backend_v2/llm/schema_builder.py]`
- `[MODIFY] @[backend_v2/llm/provider.py]`
- `[MODIFY] @[backend_v2/services/mcp/alias_registry.py]`
- `[MODIFY] @[backend_v2/services/mcp/dispatcher.py]`
- `[MODIFY] @[backend_v2/services/mcp/mcp_tool_loop.py]`
- `[MODIFY] @[backend_v2/services/mcp/__init__.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/llm.py]`
- `[MODIFY] @[backend_v2/services/source_verification_service.py]`
- `[MODIFY] @[backend_v2/hooks/source_verification_hook.py]`
- `[MODIFY] @[backend_v2/services/blueprint.py]`
- `[MODIFY] @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`
- `[MODIFY] @[backend_v2/tests/fixtures/sdui_golden_master.json]`
- `[MODIFY] @[backend_v2/seed/seed_data.json#L21696-L21700]`
- `[MODIFY] @[backend_v2/seed/seed_data.json#L22022-L22026]`
- `[DELETE] @[backend_v2/services/mcp/tools/tavily.py]`
- `[DELETE] @[backend_v2/services/mcp/tools/wikipedia.py]`
- `[DELETE] @[backend_v2/services/mcp/tavily_search_client.py]`
- `[DELETE] @[backend_v2/services/mcp/wikipedia_client.py]`
- `[DELETE] @[backend_v2/models/domain/wikipedia.py]`
- `[DELETE] @[backend_v2/models/domain/tools.py]`
- `[DELETE] @[backend_v2/tests/unit/test_tavily_client.py]`
- `[DELETE] @[backend_v2/tests/unit/test_tavily_search_client.py]`
- `[DELETE] @[backend_v2/tests/unit/services/mcp/tools/test_tavily.py]`
- `[DELETE] @[backend_v2/tests/unit/services/mcp/tools/test_wikipedia.py]`
- `[DELETE] @[backend_v2/tests/unit/services/mcp/test_wikipedia_client.py]`
- `[DELETE] @[backend_v2/tests/unit/models/domain/test_wikipedia.py]`
- `[DELETE] @[backend_v2/tests/unit/models/domain/test_tools.py]`
- `[DELETE] @[backend_v2/tests/integration/test_tavily_live.py]`
- `[DELETE] @[backend_v2/scripts/test_tavily_live.py]`
- `[MODIFY] @[backend_v2/settings.py]`
- `[MODIFY] @[backend_v2/core/test_settings.py]`
- `[MODIFY] @[scripts/_ast_guardrails.py]`
- `[MODIFY] @[scripts/audit_dict_eradication.py]`
- `[MODIFY] @[pyproject.toml]`
- `[MODIFY] @[.agents/rules/04_directory_reference.md]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/services/orchestrator/schema_factory.py]` & `@[backend_v2/llm/provider.py]` | Banned static Python tool classes with hardcoded argument types and manual string parsing. | Compile dynamic Pydantic V2 models via `pydantic.create_model` and serialize outbound declarations with standard JSON Schema mappings. | Pruned per-tool Python classes; dynamic schemas synthesized just-in-time from discovered manifests. | `pytest backend_v2/tests/unit/services/orchestrator/test_mcp_schema_bug.py`. |
| `@[backend_v2/services/mcp/alias_registry.py]` & `@[backend_v2/services/mcp/dispatcher.py]` | Banned module-level `DISPATCHER` singleton, heuristic prefix splitting, and anonymous tuple returns (`QGR023`). | Bijective `{gateway_slug}__{tool_id}` namespace prefixing via `AliasRegistry` returning `ParsedMCPToolAliasDTO`; dynamic `ToolDispatcher` returning `MCPToolDescriptorDTO` and `MCPAuditTrace`. | Deleted `BaseTool`, `BaseSearchTool`, and intermediate wrappers; direct dispatch to `GenericMCPClient`. | `pytest backend_v2/tests/unit/services/mcp/test_dispatcher.py` and `test_alias_registry.py`. |
| `[DELETE] @[backend_v2/services/mcp/tools/tavily.py]` & `[DELETE] @[backend_v2/models/domain/wikipedia.py]` | Banned lingering legacy static wrappers and dead test files competing with dynamic MCP infrastructure. | Physically delete 6 legacy wrapper files, 8 obsolete unit/integration tests, and 2 legacy scripts; purge vendor settings. | 30% Deletion Test strictly applied; zero legacy shims or fallback execution paths. | File non-existence checks and AST guardrail verification (`scripts/_ast_guardrails.py`). |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify GenericMCPClient (Phase 2) and MCPToolInputSchemaDTO (Phase 1) are complete and operational.</action>
    <action>Look forward: Verify all consumers of TavilyTool, WikipediaTool, and DISPATCHER are rewired to ToolDispatcher before deleting legacy files.</action>
    <constraint invariant="zero_backward_compatibility_planning_ban">Legacy fallback chains and un-namespaced tool aliases are strictly prohibited.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: Mark Step 3.1, 3.2, 3.3 checkboxes in @[docs/epic/EPIC_159_tracker.md] upon completion of each sub-step.</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/schema_factory.py]</backend>
    <backend>@[backend_v2/llm/provider.py]</backend>
    <backend>@[backend_v2/services/mcp/alias_registry.py]</backend>
    <backend>@[backend_v2/services/mcp/dispatcher.py]</backend>
    <backend>@[backend_v2/services/mcp/mcp_tool_loop.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm.py]</backend>
    <backend>@[backend_v2/services/source_verification_service.py]</backend>
    <backend>@[backend_v2/hooks/source_verification_hook.py]</backend>
    <backend>@[backend_v2/services/blueprint.py]</backend>
    <backend>@[backend_v2/seed/seed_data.json]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>SchemaFactory compiles runtime Pydantic V2 models via pydantic.create_model with strict ConfigDict.</item>
    <item>LiteLLMProvider maps recursive enum_values and additional_properties to standard JSON Schema keys.</item>
    <item>AliasRegistry implements build_namespaced_tool_alias and parse_namespaced_tool_alias returning ParsedMCPToolAliasDTO.</item>
    <item>ToolDispatcher dynamically instantiated per execution context with O(1) alias lookup and OpenTelemetry spans.</item>
    <item>DISPATCHER singleton removed from mcp_tool_loop.py and __init__.py.</item>
    <item>SourceVerificationService rewired to dynamic ToolDispatcher without Tavily coupling.</item>
    <item>seed_data.json step allowed_mcp_tools references migrated to default_mcp_gateway__mcp_tavily_search.</item>
    <item>6 legacy static wrappers and 8 obsolete test suites physically deleted.</item>
    <item>Legacy vendor settings removed from settings.py and test_settings.py.</item>
    <item>AST guardrails updated and directory reference synchronized.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  </required_context_rules>

  <step id="3.1" name="Runtime Pydantic Schema Factory &amp; LLM Provider Wiring">
    <action>In @[backend_v2/services/orchestrator/schema_factory.py], implement create_mcp_tool_argument_model and build_mcp_tool_declaration.</action>
    <action>In @[backend_v2/llm/provider.py], update LiteLLMProvider.generate to serialize tools with by_alias=True and standard JSON Schema mappings.</action>
    <action>Remove dead allowed_mcp_prefixes computation from strategies/llm.py and prompt_compiler.py.</action>
    <constraint invariant="llm_structured_execution_mandate">Enforce strict Pydantic models on dynamic tool arguments.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/schema_factory.py backend_v2/llm/provider.py --test --ast-strict</audit_command>
  </step>

  <step id="3.2" name="Deterministic Namespace Prefixing &amp; Dynamic ToolDispatcher">
    <action>In @[backend_v2/services/mcp/alias_registry.py], implement bijective namespace formatting and parsing returning ParsedMCPToolAliasDTO.</action>
    <action>In @[backend_v2/services/mcp/dispatcher.py], refactor ToolDispatcher to accept active gateways and GenericMCPClient, returning MCPToolDescriptorDTO and MCPAuditTrace.</action>
    <action>In @[backend_v2/services/mcp/mcp_tool_loop.py], @[backend_v2/services/orchestrator/strategies/llm.py], @[backend_v2/services/source_verification_service.py], and @[backend_v2/hooks/source_verification_hook.py], rewire all tool executions to dynamic ToolDispatcher.</action>
    <action>In @[backend_v2/services/blueprint.py], index both namespaced and short tool IDs in mcp_tools_map.</action>
    <action>In @[backend_v2/seed/seed_data.json#L21696-L21700] and #L22022-L22026, migrate step allowed_mcp_tools references to default_mcp_gateway__mcp_tavily_search.</action>
    <constraint invariant="positive_id_set_filtering_mandate">Enforce tool_id in allowed_step_tools positive set check.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/ --test --ast-strict</audit_command>
  </step>

  <step id="3.3" name="Legacy Static Wrapper Demolition &amp; Guardrail Allowlist Sync">
    <action>Physically delete legacy static wrapper files: @[backend_v2/services/mcp/tools/tavily.py], @[backend_v2/services/mcp/tools/wikipedia.py], @[backend_v2/services/mcp/tavily_search_client.py], @[backend_v2/services/mcp/wikipedia_client.py], @[backend_v2/models/domain/wikipedia.py], and @[backend_v2/models/domain/tools.py].</action>
    <action>Physically delete obsolete unit/integration tests and scripts.</action>
    <action>Purge legacy vendor settings from settings.py and test_settings.py.</action>
    <action>Update scripts/_ast_guardrails.py, pyproject.toml, and .agents/rules/04_directory_reference.md.</action>
    <constraint invariant="the_no_legacy_mandate">Ensure zero legacy wrappers or import shims remain in the repository.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict</audit_command>
    <audit_command>uv run python scripts/audit_dict_eradication.py</audit_command>
  </step>
</execution_protocol>
```
