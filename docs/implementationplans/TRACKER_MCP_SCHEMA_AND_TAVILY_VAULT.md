# Tracker: Dynamic MCP Tool Schema Vocabulary, Studio `anyOf`/`array` Parameter Controls, and Tavily Seed Vault Upgrade

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_MCP_SCHEMA_AND_TAVILY_VAULT.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_MCP_SCHEMA_AND_TAVILY_VAULT.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_MCP_SCHEMA_AND_TAVILY_VAULT.md] @[docs/implementationplans/TRACKER_MCP_SCHEMA_AND_TAVILY_VAULT.md]`
  - [x] Step 1: Phase 1: Test Technical Debt Cleanup & Backend JSON Schema Draft 2020-12 Vocabulary in MCPToolSchemaPropertyDTO and MCPToolInputSchemaDTO
  - [x] Step 2: Phase 2: Frontend 1:1 Freezed DTO Parity & OpenAPI Sync
  - [x] Step 3: Phase 3: Studio McpToolParamsPanel Nullable anyOf/oneOf Unwrapping & Array Parameter Controls
  - [x] Step 4: Phase 4: Seed Vault Upgrade for Default Tavily Gateway & Global Verification Gates
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_MCP_SCHEMA_AND_TAVILY_VAULT.md] @[docs/implementationplans/TRACKER_MCP_SCHEMA_AND_TAVILY_VAULT.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_MCP_SCHEMA_AND_TAVILY_VAULT.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[backend_v2/models/dtos/mcp.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_MCP_SCHEMA_AND_TAVILY_VAULT.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]
  - [x] @[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart]
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_MCP_SCHEMA_AND_TAVILY_VAULT.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_MCP_SCHEMA_AND_TAVILY_VAULT.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the closed JSON Schema Draft 2020-12 vocabulary in `MCPToolSchemaPropertyDTO` and `MCPToolInputSchemaDTO` (`format`, `pattern`, `unique_items`, `exclusive_minimum`, `exclusive_maximum`, `multiple_of`, `one_of`, `all_of`, `examples`, `deprecated`, `read_only`, `write_only`, `ref`, `defs`), 1:1 Freezed DTO parity in `McpToolSchemaPropertyDto` / `McpToolInputSchemaDto`, nullable `anyOf`/`oneOf` unwrapping and `JsonSchemaPropertyType.array` controls in `McpToolParamsPanel`, and the full Tavily MCP schema in `seed_data.json`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` if any module descriptions require synchronization.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing newly established MCP schema and Studio parameter configuration invariants in present tense without historical language or plan IDs.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_MCP_SCHEMA_AND_TAVILY_VAULT.md] @[docs/implementationplans/TRACKER_MCP_SCHEMA_AND_TAVILY_VAULT.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

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
| REQ-001 | Add closed JSON Schema Draft 2020-12 vocabulary (`format`, `pattern`, `unique_items`, `exclusive_minimum`, `exclusive_maximum`, `multiple_of`, `one_of`, `all_of`, `examples`, `deprecated`, `read_only`, `write_only`, `ref`, `defs`) to `MCPToolSchemaPropertyDTO` and `MCPToolInputSchemaDTO` in `@[backend_v2/models/dtos/mcp.py#L93-L319]` and remediate `TD_MODEL_FACTORY` warnings in `@[backend_v2/tests/unit/models/dtos/test_mcp.py#L357-L421]`. | Step 1 | [x] Complete |
| REQ-002 | Synchronize 1:1 Freezed DTO parity in `McpToolSchemaPropertyDto` and `McpToolInputSchemaDto` in `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart#L12-L59]`, add positive/negative tests in `@[client_app_v2/test/features/studio/models/mcp_gateway_test.dart#L167-L227]`, and regenerate `@[docs/swagger/openapi.json]`. | Step 2 | [x] Complete |
| REQ-003 | Implement `_resolveEffectiveProperty` for nullable `anyOf`/`oneOf` unwrapping, `JsonSchemaPropertyType.array` comma-separated `List<String>` control, and focus-safe `_formatCurrentValue` in `@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart#L242-L447]` with `TC-STUDIO-UI-06` widget tests in `@[client_app_v2/test/features/studio/views/widgets/mcp_tool_params_panel_test.dart#L406-L527]`. | Step 3 | [x] Complete |
| REQ-004 | Upgrade `sys_0195f3a00000700080008172bda70c86` (`default_mcp_gateway`) in `@[backend_v2/seed/seed_data.json#L209-L552]` with full discovered Tavily tool schemas (`tavily_search` and `tavily_extract`), sanitize, validate in-memory, and re-seed via `run_seed.py local`. | Step 4 | [x] Complete |

# Session Handover Context

## Achieved
- Completed **Step 1 & Step 2** (commit `ffda18d62`): Added the closed 14-field JSON Schema Draft 2020-12 vocabulary (`format`, `pattern`, `unique_items`, `exclusive_minimum`, `exclusive_maximum`, `multiple_of`, `one_of`, `all_of`, `examples`, `deprecated`, `read_only`, `write_only`, `ref`, `defs`) to `MCPToolSchemaPropertyDTO` and `MCPToolInputSchemaDTO` in `@[backend_v2/models/dtos/mcp.py#L93-L319]`, remediated all 35 `TD_MODEL_FACTORY` findings in `@[backend_v2/tests/unit/models/dtos/test_mcp.py#L357-L421]` (0 technical debt findings), synchronized 1:1 Freezed DTO parity in `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart#L12-L73]` and `@[client_app_v2/test/features/studio/models/mcp_gateway_test.dart#L167-L280]`, and regenerated `@[docs/swagger/openapi.json]`.
- Completed **Step 3** (commit `be131832e`): Implemented `_resolveEffectiveProperty` for nullable `anyOf`/`oneOf` union unwrapping, `JsonSchemaPropertyType.array` comma-separated `List<String>` input rendering with `minItems`/`maxItems` BVA validation, and focus-safe `_formatCurrentValue` in `@[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart#L242-L515]`, verified by `TC-STUDIO-UI-06` in `@[client_app_v2/test/features/studio/views/widgets/mcp_tool_params_panel_test.dart#L406-L530]`.
- Completed **Step 4**: Upgraded `sys_0195f3a00000700080008172bda70c86` (`default_mcp_gateway`) in `@[backend_v2/seed/seed_data.json#L209-L552]` with the complete 17-property `tavily_search` schema and `tavily_extract` (`capability: "document_reader"`) schema, validated via `sanitize_seed_vault.py`, `run_seed.py local --dry-run`, `audit_database_atoms.py --strict`, and `run_seed.py local`, and passed both global quality gates (`flutter_audit_loop.py client_app_v2/ --build` and `backend_audit_loop.py backend_v2/ --test` with 6,900 tests passing and 97.45% coverage).

## Learned
- In `@[client_app_v2/lib/core/models/enums.dart#L553-L571]`, the Dart enum value for JSON Schema `"null"` is `JsonSchemaPropertyType.nullValue` (`@JsonValue('null') nullValue('null')`).
- Preserving `ConfigDict(strict=True, extra="forbid", frozen=True)` and `@JsonSerializable(disallowUnrecognizedKeys: true)` while explicitly declaring Draft 2020-12 keywords allows Tavily (`anyOf`), Jina (`format`), and Context7 (`pattern`, `uniqueItems`) tool schemas to hydrate deterministically without weakening schema boundaries.

## Remaining
- Execute Tier 2 AI Hardening (`scripts/auto_hardening_runner.py`), Tier 7 As-Built Architectural Sync (`/tier7-describe-architecture`), and Tier 8 System 2 Red-Team Plan Audit (`/tier8-audit-plan`).

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_MCP_SCHEMA_AND_TAVILY_VAULT.md] @[docs/implementationplans/TRACKER_MCP_SCHEMA_AND_TAVILY_VAULT.md]
```

