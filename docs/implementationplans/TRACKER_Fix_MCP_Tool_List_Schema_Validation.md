# Tracker: Fix MCP Tool List Schema Validation & Full-Duplex DTO Parity
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Fix_MCP_Tool_List_Schema_Validation.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Fix_MCP_Tool_List_Schema_Validation.md]

- [x] **Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Fix_MCP_Tool_List_Schema_Validation.md] @[docs/implementationplans/TRACKER_Fix_MCP_Tool_List_Schema_Validation.md]`
  - [x] Step 1: Pre-Implementation Cleanups & Baseline Verification
  - [x] Step 2: Implement Backend MCP Schema Attributes & Execution DTO
  - [x] Step 3: Implement Backend Unit & Regression Tests
  - [x] Step 4: Implement Frontend Freezed DTO Parity & Code Generation
  - [x] Step 5: Universal Quality Gates & End-to-End Verification
- [ ] **Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Fix_MCP_Tool_List_Schema_Validation.md] @[docs/implementationplans/TRACKER_Fix_MCP_Tool_List_Schema_Validation.md]`

### Post-Implementation Gates

- [ ] **Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_Fix_MCP_Tool_List_Schema_Validation.md] --gate backend --agent-cmd "agy --dangerously-skip-permissions --print '/tier2-hardening-backend {target}'"`
  - [ ] @[backend_v2/models/dtos/mcp.py]
- [ ] **Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_Fix_MCP_Tool_List_Schema_Validation.md] --gate frontend --agent-cmd "agy --dangerously-skip-permissions --print '/tier2-hardening-frontend {target}'"`
  - [ ] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]
- [ ] **Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Fix_MCP_Tool_List_Schema_Validation.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Fix_MCP_Tool_List_Schema_Validation.md] @[ki_mcp_tool_protocol.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_mcp_tool_protocol.md]`: Document `MCPToolExecutionDTO`, `min_length`, `max_length`, and `schema_uri` support in MCP tool discovery wire payloads.
     - `@[ki_zero_permissive_typing.md]`: Document typed modeling of `execution` metadata replacing loose dicts in MCP tool descriptors.
  2. **Directory Reference Sync:**
     - Verify `@[.agents/rules/04_directory_reference.md]` reflects `MCPToolExecutionDTO` under `backend_v2/models/dtos/mcp.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/03_cognitive_orchestration_engine.md` describing typed MCP tool discovery contracts in present tense.

### Final Plan Audit

- [ ] System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Fix_MCP_Tool_List_Schema_Validation.md] @[docs/implementationplans/TRACKER_Fix_MCP_Tool_List_Schema_Validation.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- Execute steps strictly in sequence or in Continuous Full-Auto mode via `/tier2-execute --full-auto`.
- Enforce atomic Git commits after passing quality gates (`backend_audit_loop.py` and `flutter_audit_loop.py`).
- Always wrap workspace-relative file paths in @-reference syntax.
- Trigger `/tier5-session-handover` if context limits are approached.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-001** | Verify clean technical debt baseline across target files via `audit_technical_debt.py`. | Step 1 | `[x]` |
| **REQ-002** | Add `schema_uri`, `min_length`, `max_length`, and `MCPToolExecutionDTO` to `backend_v2/models/dtos/mcp.py`. | Step 2 | `[x]` |
| **REQ-003** | Verify `test_mcp_tools_list_result_dto_with_exa_metadata` and negative boundary assertions pass in `test_mcp.py`. | Step 3 | `[x]` |
| **REQ-004** | Update Flutter Freezed models in `mcp_gateway.dart` and regenerate code via `flutter_audit_loop.py --build`. | Step 4 | `[x]` |
| **REQ-005** | Pass `backend_audit_loop.py` and `flutter_audit_loop.py` across all modified files with 0 errors and 0 warnings. | Step 5 | `[x]` |

# Session Handover Context

## Achieved
- Implemented `min_length` and `max_length` in `MCPToolSchemaPropertyDTO` and `McpToolSchemaPropertyDto`.
- Implemented `schema_uri` in `MCPToolInputSchemaDTO` and `McpToolInputSchemaDto`.
- Implemented `MCPToolExecutionDTO` and `McpToolExecutionDto` for typed MCP tool task execution policies.
- Bound `execution` on `AllowedMCPTool` and `AllowedMcpTool`, achieving 100% Full-Duplex DTO Parity (55/55 models aligned).
- Added regression test `test_mcp_tools_list_result_dto_with_exa_metadata` and ISTQB negative tests for extra="forbid" and ge=0 integer bounds.
- Validated live Exa AI tool discovery via `GenericMCPClient.list_tools`, discovering 2 tools (`web_search_exa`, `web_fetch_exa`).
- Passed `backend_audit_loop.py` across all modified backend targets with 100% strict coverage and zero AST violations.
- Passed `flutter_audit_loop.py` with code generation and zero errors.

## Learned
- In Pydantic V2 models, when fields use `Annotated[..., Field(default_factory=...)]` without explicit right-hand side default assignment, MyPy's plugin requires explicit arguments during direct constructor invocation.
- Exa AI's live endpoint (`https://mcp.exa.ai/mcp`) adheres to JSON Schema Draft-07 attributes and standard MCP tool execution definitions.

## Remaining
- Perform atomic git commit for modified files.
- Execute post-implementation gates: `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Fix_MCP_Tool_List_Schema_Validation.md] @[docs/implementationplans/TRACKER_Fix_MCP_Tool_List_Schema_Validation.md]`.
