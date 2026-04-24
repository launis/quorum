# Epic 31 - Phase 4: Validating MCP Audit Trail Fail-Fast
**STATUS: [x] COMPLETE**

## 1. Goal
Harden the extraction of the MCP Tool Audit Trail inside `BlueprintTransformer.build_report_dto()`. Currently, the logic uses defensive `isinstance(audit, dict)` parsing to safely extract `tool_id` and `query` due to ambiguity between Pydantic models and raw dicts. This violates the Strict Pydantic V2 Rust mandate.

## 2. Context & Constraints
- **TARGET (Modify):**
  - `backend_v2/services/blueprint.py`
  - `backend_v2/tests/unit/test_blueprint_transformer.py`
- **CONTEXT (Read-Only):**
  - `backend_v2/models/v2_core.py` (Focus on `MCPAuditTrace` model)
  - `backend_v2/models/state.py`
- **Architectural Rules (00-antigravity-core & 01-python-backend):**
  - Zero-Compromise Pledge: The state trace must yield `MCPAuditTrace` natively. Access attributes directly via dot notation.

## 3. Execution Sequence
1. Locate the MCP Audit Trail extraction block near the end of `build_report_dto` (around `f_context.get("mcp_tool_audit")`).
2. Delete the defensive parsing:
   - Remove `audit.get("tool_id") if isinstance(audit, dict) else ""`
   - Remove `audit.get("query") if isinstance(audit, dict) else ""`
3. Enforce that `raw_audits` is validated against a list of `MCPAuditTrace` models. If an audit item lacks `tool_id` or `query`, the Pydantic boundary will fail-fast automatically or raise an explicit `AppException`.
4. Refactor the hashing mechanism to use native attribute access: `t_name = audit.tool_id`, `t_args = audit.query`.

## 4. Verification & Quality Gate Plan
- **Negative Tests:** Write tests passing raw dicts or incomplete `MCPAuditTrace` shapes into the context. Assert the system raises an exception rather than returning an empty string tool ID.
- **Quality Loop Execution:**
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py backend_v2/tests/unit/test_blueprint_transformer.py --test
  ```
