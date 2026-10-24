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
</required_context_rules>

# EPIC 159 Audit Report: Dynamic Model Context Protocol (MCP) Architecture & Runtime Schema Introspection

## 1. Executive Summary & Automated Pre-Flight Verification

- **Audited Artifact**: `@[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]`
- **Workflow Executed**: `@[.agents/workflows/tier0-research-epic.md]` (System 2 Five-Axis Research & Red-Team Analysis)
- **Automated Boundary Gate**: `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md` -> **PASSED (0 violations)**
- **Automated Technical Debt Sweep**: `uv run python scripts/audit_technical_debt.py --targets ... --include-one-hop` -> Scanned 14 primary targets and 55 1-hop callers; identified 1 FATAL violation (`DGR009` missing `AppErrorBoundary` in `@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]`) scheduled for Phase 1.1 remediation.

---

## 2. Five-Axis System 2 Analysis & Hardening Actions Applied

### Axis 1: Systemic Coherence & Knowledge Item (KI) Registry
- **Finding**: `<required_context_rules>` in `@[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md]` originally declared only `@[ki_sdui_matrix_synthesis.md]` and omitted five directly overlapping Knowledge Items.
- **Hardening Applied**: Injected `<knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>`, `<knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>`, `<knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>`, `<knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>`, and `<knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>` into `<required_context_rules>`, and added **§1.4 Quantitative Scope Validation Table** mapping every target file, action, physical layer, and coupled 1-hop caller.

### Axis 2: First Principles & The 30% Deletion Test
- **Finding**: §2.1 and §3.2 originally claimed that `ToolParameter` and `ToolExecutionResult` in `@[backend_v2/models/domain/tools.py]` were retained and that `ToolDispatcher` returned `ToolExecutionResult`. Physical inspection of `@[backend_v2/models/domain/tools.py]` proved that `ToolParameter` and `ToolExecutionResult` do not exist on disk (`tools.py` contains only `StandardSearchInputDTO`, `BaseTool`, and `BaseSearchTool`), and `@[backend_v2/services/mcp/dispatcher.py]` returns `MCPAuditTrace` directly.
- **Hardening Applied**: Applied the 30% Deletion Test by promoting `@[backend_v2/models/domain/tools.py]` (`StandardSearchInputDTO`, `BaseTool`, `BaseSearchTool`) and its unit test `@[backend_v2/tests/unit/models/domain/test_tools.py]` to `[DELETE]`, pruning the hallucinated `ToolExecutionResult` wrapper, and standardizing `ToolDispatcher.execute_tool` to return `MCPAuditTrace` directly. Also injected **§2.5 5-Column Architectural Directive Table**.

### Axis 3: Sunset List & Physical Symbol Parity
- **Finding**:
  1. §2.1 listed non-existent MediaWiki symbol names for `@[backend_v2/models/domain/wikipedia.py]`.
  2. §2.1 and §3.3 referenced a non-existent test file (`backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py`) while omitting four physical files that import the deleted static tools (`@[backend_v2/tests/unit/services/mcp/tools/test_tavily.py]`, `@[backend_v2/tests/unit/services/mcp/tools/test_wikipedia.py]`, `@[backend_v2/tests/unit/models/domain/test_tools.py]`, and `@[backend_v2/scripts/test_tavily_live.py]`).
- **Hardening Applied**: Replaced the `wikipedia.py` symbols with the exact physical symbols (`SUPPORTED_WIKIPEDIA_LANGUAGES`, `WikimediaActionSearchItemDTO`, `WikimediaActionQueryDTO`, `WikimediaActionApiResponseDTO`, `WikimediaRestSummaryResponseDTO`, `WikipediaReadInputDTO`, `WikipediaSearchResultItem`, `WikipediaSearchResponseDTO`, `WikipediaPageSummaryResult`), removed the non-existent test path, and added all four physical test/script files to `[DELETE]` in §2.1 and §3.3.

### Axis 4: 1-Hop Caller Blast Radius & Full-Duplex Serialization Parity
- **Finding**:
  1. `@[backend_v2/services/source_verification_service.py]` and `@[backend_v2/services/mcp/__init__.py]` directly import `DISPATCHER` and `TAVILY_TOOL_ID`.
  2. `@[backend_v2/services/blueprint.py]` indexes `AllowedMCPTool` by `tool.tool_id` for `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`.
  3. `@[backend_v2/core/test_settings.py]` and `@[backend_v2/tests/unit/test_settings.py]` reference `mcp_wikipedia_*` fields removed from `@[backend_v2/settings.py]`.
  4. Six existing unit test files instantiate `AllowedMCPTool` or `MCPFunctionDefinitionDTO` with raw dictionaries and require synchronous migration in Phase 1.2.
- **Hardening Applied**:
  - Added `@[backend_v2/services/mcp/__init__.py]`, `@[backend_v2/services/source_verification_service.py]`, `@[backend_v2/tests/unit/services/test_source_verification_service.py]`, `@[backend_v2/services/blueprint.py]`, and `@[backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_adapter.py]` to Phase 3.2.
  - Added `@[backend_v2/core/test_settings.py]`, `@[backend_v2/tests/unit/test_settings.py]`, and the six coupled schema unit test files (`@[backend_v2/tests/unit/models/domain/test_mcp.py]`, `@[backend_v2/tests/unit/models/domain/test_system_config.py]`, `@[backend_v2/tests/unit/models/dtos/test_mcp.py]`, `@[backend_v2/tests/unit/models/test_v2_core.py]`, `@[backend_v2/tests/unit/seed/test_seed_registry.py]`, `@[backend_v2/tests/unit/services/studio/test_system_config_service.py]`) to Phase 1.2.
  - Specified `.model_dump(mode="json", by_alias=True, exclude_none=True)` serialization for `MCPToolInputSchemaDTO` defined in `@[backend_v2/models/dtos/mcp.py]` in Phase 3.1 across `@[backend_v2/llm/adapters/vertex_adapter.py]`, `@[backend_v2/llm/adapters/openai_adapter.py]`, `@[backend_v2/llm/adapters/ai_studio_adapter.py]`, and `@[backend_v2/llm/adapters/anthropic_adapter.py]`.
