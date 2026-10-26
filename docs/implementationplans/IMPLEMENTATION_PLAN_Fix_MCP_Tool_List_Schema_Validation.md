<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Bug Fix Plan: Fix MCP Tool List Schema Validation & Full-Duplex DTO Parity

## 1. Overview & Problem Statement
When discovering tools on external MCP servers (specifically Exa AI at `https://mcp.exa.ai/mcp`), the initial `initialize` handshake completes successfully, but the subsequent `tools/list` RPC request fails with HTTP 502 `AGENT_RESPONSE_MALFORMED` (`Malformed JSON-RPC 2.0 frame in SSE stream`). 

This failure occurs because Exa AI returns standard JSON Schema attributes (`$schema`, `minLength`, `maxLength`) and MCP specification tool metadata (`execution: {"taskSupport": "forbidden"}`), which are rejected by Quorum's strict Pydantic DTOs enforcing `ConfigDict(strict=True, extra="forbid")`.

## 2. Root Cause Analysis (5 Whys)
1. **Why did `tools/list` discovery fail for `exa_gateway` with HTTP 502?**
   Because `GenericMCPClient._send_rpc_request` encountered a Pydantic `ValidationError` in `_match_sse_jsonrpc_frame` while parsing the JSON-RPC response frame into `MCPJsonRpcResponseDTO`.
2. **Why did `MCPJsonRpcResponseDTO.model_validate_json(frame)` fail validation?**
   Because the union member `MCPToolsListResultDTO` rejected the payload with 9 `extra_forbidden` validation errors on `tools[i].execution`, `tools[i].inputSchema.$schema`, and `tools[i].inputSchema.properties[k].minLength` / `maxLength`.
3. **Why were `$schema`, `minLength`, and `maxLength` rejected in `inputSchema`?**
   Because `MCPToolInputSchemaDTO` and `MCPToolSchemaPropertyDTO` enforce `extra="forbid"` and lacked field mappings for JSON Schema Draft specifications (`$schema`) and string length bounds (`minLength`, `maxLength`).
4. **Why was `execution` rejected in tool descriptors?**
   Because `MCPDiscoveredToolWireDTO` enforces `extra="forbid"` and did not define a typed child DTO for MCP background task execution policies (`taskSupport`).
5. **Why were these fields not modeled previously?**
   Earlier implementations modeled only numeric limits (`minimum`, `maximum`) and top-level schema properties without accommodating string boundary constraints or modern MCP 2024-11-05 tool execution policies.

## 3. Blast Radius & Scope Analysis
#### [MODIFY] @[backend_v2/models/dtos/mcp.py#L87-L180]
  - In `MCPToolSchemaPropertyDTO`, add `min_length: Annotated[int | None, Field(default=None, ge=0, validation_alias=AliasChoices("minLength", "min_length"))]` and `max_length: Annotated[int | None, Field(default=None, ge=0, validation_alias=AliasChoices("maxLength", "max_length"))]`.
#### [MODIFY] @[backend_v2/models/dtos/mcp.py#L186-L229]
  - In `MCPToolInputSchemaDTO`, add `schema_uri: Annotated[str | None, Field(default=None, validation_alias=AliasChoices("$schema", "schema_uri", "schema"))]`.
#### [NEW] [MODIFY] @[backend_v2/models/dtos/mcp.py#L655-L671]
  - Create [NEW] `MCPToolExecutionDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)` and `task_support: Annotated[str | None, Field(default=None, validation_alias=AliasChoices("taskSupport", "task_support"))]`.
  - Add `execution: Annotated[MCPToolExecutionDTO | None, Field(default=None)] = None` to `MCPDiscoveredToolWireDTO`.
  - Export `MCPToolExecutionDTO` in `__all__` in `backend_v2/models/dtos/mcp.py`.
#### [MODIFY] @[backend_v2/tests/unit/models/dtos/test_mcp.py#L333-L441]
  - Add regression test `test_mcp_tools_list_result_dto_with_exa_metadata` verifying hydration of Exa AI's live `tools/list` response frame.
  - Add ISTQB negative boundary tests verifying `extra="forbid"` and negative integer bounds.
#### [MODIFY] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart#L12-L73]
  - In `McpToolSchemaPropertyDto`, add `@JsonKey(name: 'min_length') int? minLength` and `@JsonKey(name: 'max_length') int? maxLength`.
  - In `McpToolInputSchemaDto`, add `@JsonKey(name: 'schema_uri') String? schemaUri`.
  - Create [NEW] `McpToolExecutionDto` with `@JsonKey(name: 'task_support') String? taskSupport`.
  - In `AllowedMcpTool`, add `@JsonKey(name: 'execution') McpToolExecutionDto? execution`.
  - Run build runner to regenerate Freezed and JsonSerializable code.

---

## 4. 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/models/dtos/mcp.py#L87-L180]`**<br>**`@[backend_v2/models/dtos/mcp.py#L186-L229]`** | Banned ignoring JSON Schema constraints or dropping unrecognized fields via loose dictionaries. | Add typed fields `min_length` and `max_length` to `MCPToolSchemaPropertyDTO` and `schema_uri` to `MCPToolInputSchemaDTO` with strict typing and dual-casing `AliasChoices`. | Pruned generic unvalidated dictionary catch-alls. Every parameter constraint is explicitly typed. | Pydantic validation rejects negative lengths (`ge=0`) and recognizes camelCase wire keys. |
| **`@[backend_v2/models/dtos/mcp.py#L655-L671]`** | Banned naked dictionaries for tool execution policy metadata (`execution: dict[str, Any]`). | Create [NEW] `MCPToolExecutionDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)` and `task_support`. Export in `__all__`. | Pruned speculative background task orchestrators or worker execution engines. DTO serves purely as typed protocol wire model. | Unit tests verify successful validation of Exa AI `execution` object and rejection of unrecognized fields. |
| **`@[backend_v2/tests/unit/models/dtos/test_mcp.py#L333-L441]`** | Banned happy-path-only testing that ignores negative boundary partitions. | Add `test_mcp_tools_list_result_dto_with_exa_metadata` asserting roundtrip parsing of Exa AI live wire response alongside negative boundary tests asserting `ValidationError` on unexpected fields. | Pruned live external HTTP dependencies; tests execute hermetically against recorded wire frames. | `uv run pytest backend_v2/tests/unit/models/dtos/test_mcp.py` passes with 100% test coverage. |
| **`@[client_app_v2/lib/features/studio/models/mcp_gateway.dart#L12-L73]`** | Banned asymmetrical DTO definitions between backend and frontend. | Synchronously update `McpToolSchemaPropertyDto`, `McpToolInputSchemaDto`, and add `McpToolExecutionDto` to maintain 100% Full-Duplex DTO Parity. | Pruned custom manual JSON deserializers; utilize Freezed code generation. | `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/mcp_gateway.dart --build` passes with 0 warnings. |

---

## 5. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Pre-Implementation Cleanups &amp; Baseline Verification">
    <action>Verify clean technical debt baseline across target files using `uv run python scripts/audit_technical_debt.py --targets backend_v2/models/dtos/mcp.py client_app_v2/lib/features/studio/models/mcp_gateway.dart`.</action>
    <constraint invariant="touched_scope_tech_debt_mandate">Zero technical debt violations must exist across touched target files.</constraint>
  </step>

  <step id="2" name="Implement Backend MCP Schema Attributes &amp; Execution DTO">
    <action>In `backend_v2/models/dtos/mcp.py`:
      1. Add `min_length` and `max_length` to `MCPToolSchemaPropertyDTO`.
      2. Add `schema_uri` to `MCPToolInputSchemaDTO`.
      3. Create [NEW] `MCPToolExecutionDTO` with `task_support`.
      4. Add `execution: MCPToolExecutionDTO | None = None` to `MCPDiscoveredToolWireDTO`.
      5. Export `MCPToolExecutionDTO` in `__all__`.
    </action>
    <constraint invariant="the_zero_compromise_pledge">Enforce strict Pydantic V2 schemas with ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True).</constraint>
  </step>

  <step id="3" name="Implement Backend Unit &amp; Regression Tests">
    <action>In `backend_v2/tests/unit/models/dtos/test_mcp.py`:
      1. Implement `test_mcp_tools_list_result_dto_with_exa_metadata` validating the Exa AI live `tools/list` response frame.
      2. Implement ISTQB negative boundary assertions for `extra="forbid"` on `MCPToolExecutionDTO`, `MCPToolInputSchemaDTO`, and `MCPToolSchemaPropertyDTO`.
      3. Verify with `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/dtos/test_mcp.py --test --ast-strict`.
    </action>
    <constraint invariant="universal_quality_gates">Must achieve 100% test pass with 0 errors and 0 AST warnings.</constraint>
  </step>

  <step id="4" name="Implement Frontend Freezed DTO Parity &amp; Code Generation">
    <action>In `client_app_v2/lib/features/studio/models/mcp_gateway.dart`:
      1. Add `minLength` and `maxLength` to `McpToolSchemaPropertyDto`.
      2. Add `schemaUri` to `McpToolInputSchemaDto`.
      3. Create [NEW] `McpToolExecutionDto` with `taskSupport`.
      4. Add `execution` to `AllowedMcpTool`.
      5. Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/mcp_gateway.dart --build`.
    </action>
    <constraint invariant="anti_semantic_drift_renaming">Field nomenclature between Python snake_case and Dart camelCase must remain 1:1 identical at serialization layer.</constraint>
  </step>

  <step id="5" name="Universal Quality Gates &amp; End-to-End Verification">
    <action>Execute global quality gates:
      1. `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/mcp.py --test --ast-strict`
      2. `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/mcp_gateway.dart`
      3. Verify live discovery against Exa AI endpoint via scratch runner.
    </action>
    <constraint invariant="zero_tolerance_audit_loop">All modified files must pass linting, typechecking, and tests with 0 errors.</constraint>
  </step>
</execution_protocol>
```

---

## 6. Verification Plan & Test Scenarios

### Positive Test Scenarios
1. **Exa AI Live Tools List Hydration**:
   - Input: JSON-RPC response envelope containing `web_search_exa` and `web_fetch_exa` with `$schema`, `minLength`, `maxLength`, and `execution: {"taskSupport": "forbidden"}`.
   - Expected Output: `MCPJsonRpcResponseDTO.model_validate(payload)` successfully produces an instance of `MCPToolsListResultDTO` containing 2 tools with valid parameters and schemas.

### Negative Test Scenarios
1. **Extra Forbidden in `MCPToolExecutionDTO`**:
   - Input: `{"taskSupport": "forbidden", "unknownField": "invalid"}`.
   - Expected Output: Pydantic raises `ValidationError` with `extra_forbidden`.
2. **Extra Forbidden in `MCPToolInputSchemaDTO`**:
   - Input: `{"type": "object", "unexpectedSchemaField": true}`.
   - Expected Output: Pydantic raises `ValidationError` with `extra_forbidden`.
3. **Negative Integer for `minLength`**:
   - Input: `{"type": "string", "minLength": -1}`.
   - Expected Output: Pydantic raises `ValidationError` enforcing `ge=0`.

---

## 7. Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-001** | Verify clean technical debt baseline across target files via `audit_technical_debt.py`. | Step 1 | `[ ]` |
| **REQ-002** | Add `schema_uri`, `min_length`, `max_length`, and `MCPToolExecutionDTO` to `backend_v2/models/dtos/mcp.py`. | Step 2 | `[ ]` |
| **REQ-003** | Verify `test_mcp_tools_list_result_dto_with_exa_metadata` and negative boundary assertions pass in `test_mcp.py`. | Step 3 | `[ ]` |
| **REQ-004** | Update Flutter Freezed models in `mcp_gateway.dart` and regenerate code via `flutter_audit_loop.py --build`. | Step 4 | `[ ]` |
| **REQ-005** | Pass `backend_audit_loop.py` and `flutter_audit_loop.py` across all modified files with 0 errors and 0 warnings. | Step 5 | `[ ]` |
