# Tracker: JIT Micro-LLM MCP Argument Synthesizer and Studio Tool Parameter Configuration
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md] @[docs/implementationplans/TRACKER_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]`
  - [x] Step 1: Backend DTO & Step Domain Model Extension for mcp_tool_params
  - [x] Step 2: JIT Micro-LLM Argument Synthesis Prompt Asset SSOT
  - [x] Step 3: ToolDispatcher JIT Micro-LLM Argument Synthesizer & Static Override Support
  - [x] Step 4: Wire JIT Argument Synthesis & Step mcp_tool_params into MCP Tool Loop and LLMNodeStrategy
  - [x] Step 5: Flutter NodeStrategy Model Parity, Localization & Studio McpToolParamsPanel Widget
  - [x] Step 6: Global Two-Stage Quality Gates & Cross-Language DTO Parity Verification
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md] @[docs/implementationplans/TRACKER_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]" --gate backend --agent-cmd "agy --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`
  - [x] @[backend_v2/models/dtos/mcp.py]
  - [ ] @[backend_v2/models/domain/step.py]
  - [ ] @[backend_v2/models/dtos/studio.py]
  - [ ] @[backend_v2/models/prompts/execution/mcp_prompts.py]
  - [ ] @[backend_v2/models/prompts/execution/__init__.py]
  - [ ] @[backend_v2/models/prompts/__init__.py]
  - [ ] @[backend_v2/services/mcp/dispatcher.py]
  - [ ] @[backend_v2/services/mcp/mcp_tool_loop.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm.py]
  - [ ] @[backend_v2/services/studio/workflow_service.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]" --gate frontend --agent-cmd "agy --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`
  - [ ] @[client_app_v2/lib/features/studio/models/workflow.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/step_builder_view.dart]
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md] @[ki_mcp_tool_protocol.md] @[ki_god_code_prevention.md] @[ki_desktop_pro_tool_studio_ux.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_mcp_tool_protocol.md]`: Document JIT Micro-LLM Argument Synthesizer (`synthesize_search_arguments`), 0ms deterministic fast-path, and schema-driven step `mcp_tool_params` overrides.
     - `@[ki_zero_permissive_typing.md]`: Document extension of `MCPArgumentValue` union to support `dict[str, MCPArgumentScalar]` with zero permissive dictionaries.
     - `@[ki_desktop_pro_tool_studio_ux.md]`: Document schema-driven `McpToolParamsPanel` in Studio StepBuilderView rendering dynamically from `AllowedMcpTool.inputSchema.properties`.
     - `@[ki_god_code_prevention.md]`: Document widget extraction pattern isolating parameter controls from `StepBuilderView`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register `client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart` and `MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION` in `backend_v2/models/prompts/execution/mcp_prompts.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/03_cognitive_orchestration_engine.md` and `docs/architecture/04_desktop_studio_and_client_architecture.md` describing dynamic MCP tool parameter configuration and JIT argument synthesis in present tense.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md] @[docs/implementationplans/TRACKER_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- Execute steps strictly in sequence or in Continuous Full-Auto mode via `/tier2-execute --full-auto`.
- Enforce atomic Git commits after passing quality gates (`backend_audit_loop.py` and `flutter_audit_loop.py`).
- Always wrap workspace-relative file paths in @-reference syntax.
- Trigger `/tier5-session-handover` if context limits are approached.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-001** | Extend `MCPArgumentValue` with `dict[str, MCPArgumentScalar]` and add `mcp_tool_params` to `Step`, `StepCreateDTO`, and `StepUpdateDTO`. | Step 1 | `[x]` |
| **REQ-002** | Define static XML constant `MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION` in `mcp_prompts.py` and export in barrels. | Step 2 | `[x]` |
| **REQ-003** | Implement `get_argument_model`, `build_search_arguments` parameter overlay, and `synthesize_search_arguments` with fast-path and JIT fallback in `ToolDispatcher`. | Step 3 | `[x]` |
| **REQ-004** | Forward `step_obj.mcp_tool_params` from `LLMNodeStrategy` to `execute_mcp_retrieval` and accumulate JIT synthesis token usage. | Step 4 | `[x]` |
| **REQ-005** | Add `mcpToolParams` with `@JsonKey(name: 'mcp_tool_params')` to `NodeStrategy`, create `McpToolParamsPanel` widget, wire in `StepBuilderView`, and add localization. | Step 5 | `[x]` |
| **REQ-006** | Pass global quality gates: `audit_dto_parity.py`, `backend_audit_loop.py`, and `flutter_audit_loop.py --build`. | Step 6 | `[x]` |

# Session Handover Context

## Achieved
- Authored and approved Implementation Plan: `@[docs/implementationplans/IMPLEMENTATION_PLAN_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]`.
- Executed Tier 0 Research & Red-Team Audit (`audit_markdown_boundaries.py`, `audit_technical_debt.py`, `audit_tracker_output.py`) with 0 architectural defects (`CONVERGENCE ACHIEVED: 0 architectural defects found`).
- Grounded in forensic analysis of live execution `exe_d25ac1ed38614a99` (Exa AI search verified; identified high-value optimization of Studio-configured `numResults`).
- Synchronized double-entry bookkeeping tracker: `@[docs/implementationplans/TRACKER_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]`.
- Executed Steps 1 through 6 via `/tier2-execute --full-auto`: implemented backend `MCPToolParamOverrides`, `Step.mcp_tool_params`, `MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION`, `ToolDispatcher.synthesize_search_arguments`, `execute_mcp_retrieval` wiring, Flutter `NodeStrategy.mcpToolParams`, and Studio `McpToolParamsPanel` widget.
- Passed all global quality gates (`audit_dto_parity.py`, `backend_audit_loop.py backend_v2/ --test --ast-strict` with 96.74% coverage, `flutter_audit_loop.py client_app_v2/ --build`, and live E2E `test_integration_real_llm.py`).

## Learned
- In `exe_d25ac1ed38614a99`, Exa AI executed search queries deterministically via `build_search_arguments` (2,547 ms latency), but lacked step-level static parameter tuning (`numResults`), defaulting to 10 results.
- `audit_markdown_boundaries.py` enforces AST check `QGR016` on embedded Python code blocks inside plans, prohibiting ternary and inline `or` fallbacks in favour of explicit `if` statements.
- `NodeStrategy` in Flutter requires `@JsonKey(name: 'mcp_tool_params')` to ensure 1:1 `snake_case` serialization parity with backend Pydantic V2 models.
- Defined PEP 695 type alias `type MCPToolParamOverrides = dict[str, MCPArgumentValue]` in `@[backend_v2/models/dtos/mcp.py]` to satisfy `audit_dict_eradication.py` (`primitive_obsession_nested_dicts`) while preserving 1:1 JSON serialization parity.
- Added `rate_limited` (`AliasChoices("rateLimited", "rate_limited", "ai.exa/rateLimited")`) to `MCPExecutionMetaDTO` in `@[backend_v2/models/dtos/mcp.py]` so rate-limit metadata on Exa AI JSON-RPC responses parses cleanly under `extra="forbid"`.

## Remaining
- Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md] @[docs/implementationplans/TRACKER_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]`.
- Run post-implementation hardening and quality gates.

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md] @[docs/implementationplans/TRACKER_JIT_MCP_Argument_Synthesizer_and_Studio_Params.md]
```
