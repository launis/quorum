<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Bug Fix Plan: MCP Discovery Validation Failure & Client Form Disposed Crash

## 1. Overview & Problem Statement
When attempting to discover tools on remote MCP gateways that return structured metadata in their `serverInfo` (specifically: Exa AI at `https://mcp.exa.ai/mcp`), the backend fails with HTTP 502 `AGENT_RESPONSE_MALFORMED` (`Malformed JSON-RPC 2.0 frame in SSE stream`). Additionally, when this occurs, the Flutter Studio client throws an unhandled `ValueNotifier<String?> was used after being disposed` exception because the form unmounts into a fullscreen `ErrorView`.

## 2. Root Cause Analysis (5 Whys)
1. **Why did tool discovery fail for `exa_gateway` with HTTP 502?**
   Because `GenericMCPClient._perform_initialize_handshake` failed during JSON-RPC frame parsing in `_match_sse_jsonrpc_frame`.
2. **Why did `MCPJsonRpcResponseDTO.model_validate_json(frame)` throw a `ValidationError`?**
   Because `MCPInitializeResultDTO.server_info` was defined as `dict[str, str]`, but Exa AI returned structured metadata containing a list of icon objects (`"icons": [{"src": "...", "sizes": [...]}]`). Pydantic rejected `icons` as non-string (`Input should be a valid string`).
3. **Why did the validation error cascade across `MCPToolsListResultDTO` and `MCPToolCallResultDTO`?**
   Because `MCPJsonRpcResponseDTO.result` is an untagged union. When `MCPInitializeResultDTO` failed, Pydantic evaluated the other union variants, which failed due to `extra="forbid"`, producing 9 misleading errors.
4. **Why was `server_info` typed as `dict[str, str]`?**
   The initial implementation assumed all MCP servers return flat string key-values in `serverInfo`, violating the official Model Context Protocol specification for `Implementation` which specifies optional metadata specifically and exhaustively: `icons`, `title`, `description`, `website_url`, and violating Quorum's architectural ban on naked dictionaries.
5. **Why did the Flutter client throw `A ValueNotifier was used after being disposed`?**
   In `McpGatewayView.build`, the `switch (formState)` matched `AsyncLoading()` and `AsyncError(...)` before `AsyncData(...)`, and the hooks `bannerMessage = useState<String?>(null)` and `isBannerError = useState<bool>(false)` were declared conditionally inside `_buildScaffold` rather than unconditionally at the top of `McpGatewayView.build`. When `McpGatewayForm.discoverTools` set `state = const AsyncLoading()` and subsequently failed with HTTP 502 (`AsyncError`), `switch (formState)` stopped calling `_buildScaffold` even though `McpGatewayView` (`context.mounted == true`) remained mounted. `flutter_hooks` saw fewer hooks on rebuild and immediately disposed `bannerMessage` and `isBannerError` before the `catch` block set `bannerMessage.value`.

## 3. Blast Radius & Scope Analysis
#### [MODIFY] @[backend_v2/models/dtos/mcp.py#L487-L518]
  - Create [NEW] `MCPIconDTO(V2CoreBase)` with strict typing for MCP icons (`src`, `mime_type`, `sizes`).
  - Create [NEW] `MCPServerInfoDTO(V2CoreBase)` with strict typing for MCP `Implementation` metadata (`name`, `version`, `title`, `description`, `website_url`, `icons`).
  - Update `MCPInitializeResultDTO.server_info` to `MCPServerInfoDTO = Field(default_factory=MCPServerInfoDTO, validation_alias=AliasChoices("serverInfo", "server_info"))`.
  - Export new DTOs in `__all__` in `backend_v2/models/dtos/mcp.py`.
#### [MODIFY] @[backend_v2/tests/unit/models/dtos/test_mcp.py#L265-L326]
  - Contains failing regression test `test_mcp_initialize_result_dto_with_complex_server_info_metadata` asserting successful parsing of the Exa AI payload.
  - Add ISTQB negative boundary assertions verifying `extra="forbid"` Fail-Fast behavior.
#### [MODIFY] @[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart#L250-L288]
  - In `McpGatewayForm.discoverTools` and `McpGatewayForm.submit`, synchronize `state = AsyncData(currentPayload)` prior to `state = const AsyncLoading()` so Riverpod 3.1.0's internal `ElementWithFuture.asyncTransition` preserves the latest form payload (`hasValue == true`) across loading and error states without invoking the `@internal` `copyWithPrevious` API.
#### [MODIFY] @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart#L21-L65]
  - Hoist `bannerMessage = useState<String?>(null)` and `isBannerError = useState<bool>(false)` from `_buildScaffold` to the top of `McpGatewayView.build` so hooks are never called conditionally.
  - Update pattern matching in `build` to match `_ when formState.hasValue => _buildScaffold(context, ref, l10n, formKey, formState, formState.requireValue, bannerMessage, isBannerError)` first, ensuring the form stays mounted and error banners display in-form rather than replacing the form with fullscreen `ErrorView`.

---

## 4. 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/models/dtos/mcp.py#L487-L518]`** | Banned naked dictionary `server_info: dict[str, str]` and loose unvalidated metadata dictionaries in JSON-RPC 2.0 initialize wire frames. | Implement strictly typed, immutable Pydantic V2 DTOs: `MCPIconDTO` and `MCPServerInfoDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)`. Update `MCPInitializeResultDTO.server_info: MCPServerInfoDTO = Field(default_factory=MCPServerInfoDTO)`. Export both in `__all__`. | Pruned speculative icon caching services, asset downloaders, or client-side icon rendering widgets. DTOs serve purely as typed protocol wire contracts. | `uv run pytest backend_v2/tests/unit/models/dtos/test_mcp.py::test_mcp_initialize_result_dto_with_complex_server_info_metadata` passes with 0 errors. |
| **`@[backend_v2/tests/unit/models/dtos/test_mcp.py#L265-L326]`** | Banned happy-path-only regression testing that skips strict schema boundary assertions and ISTQB negative partitions. | Add ISTQB negative boundary assertions verifying that unexpected fields in `serverInfo` or `icons` trigger Fail-Fast `ValidationError` (`extra="forbid"`). Verify type validation on scalar properties. | Pruned heavy mock servers or live HTTP calls; tests validate wire JSON-RPC frames directly against Pydantic V2 DTO contracts. | Pytest assertions verify successful hydration of Exa AI metadata and explicit `ValidationError` on malformed or unrecognized fields. |
| **`@[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart#L250-L288]`** | Banned transitioning to `AsyncLoading` without synchronizing `updatedData` into `AsyncData`, and banned calling Riverpod 3.1.0 `@internal` `.copyWithPrevious(state)` which triggers `invalid_use_of_internal_member`. | Enforce Riverpod 3.1.0 State Retention: assign `state = AsyncData(currentPayload)` before `state = const AsyncLoading()` in `discoverTools` and `submit` so `ElementWithFuture.asyncTransition` retains the latest form payload (`hasValue == true`) across loading and error states. | Pruned complex manual loading flags (`bool isLoading`) or secondary transient state controllers. | `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart` passes with 0 warnings. |
| **`@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart#L21-L65]`** | Banned declaring `useState` hooks conditionally inside `_buildScaffold` and unmounting the form into a fullscreen `ErrorView` on discovery or save failures, which disposed `ValueNotifier` hooks while `McpGatewayView` remained mounted. | Hoist `bannerMessage` and `isBannerError` `useState` hooks to the top of `McpGatewayView.build`, and pattern match `_ when formState.hasValue => _buildScaffold(...)` first so the form remains mounted whenever prior data exists. Fall back to fullscreen `ErrorView` only on initial load failure (`hasValue == false`). | Pruned global dialog overlays or separate banner notification services; uses standard in-form banner widgets and localized string errors. | Form UI remains mounted when discovery throws HTTP 502, error banner displays `l10n.mcpDiscoverToolsFailed`, and zero `ValueNotifier` disposal crashes occur. |
| **Universal Quality Gates Audit** | Banned skipping automated quality gates or assuming small schema changes do not impact callers or AST guardrails. | Enforce full Two-Stage Testing: run localized Pytest, then run global `backend_audit_loop.py --test --ast-strict` and `flutter_audit_loop.py`. | Pruned redundant full-suite re-runs of unrelated subsystems; focused precisely on MCP domain models and Studio controllers. | `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/mcp.py --test --ast-strict` and `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart` both return exit code 0. |

---

<execution_protocol>
<step id="1" name="Phase 1: Pre-Implementation Cleanups & Baseline Verification">
  <action>
    Verify clean technical debt baseline across target files and 1-hop callers (`uv run python scripts/audit_technical_debt.py --targets backend_v2/models/dtos/mcp.py client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart client_app_v2/lib/features/studio/views/mcp_gateway_view.dart --include-one-hop`).
    Confirm 0 debt findings and verified Git baseline.
  </action>
  <constraint>
    Zero unmapped technical debt allowed. Baseline must be clean before implementation begins.
  </constraint>
</step>

<step id="2" name="Implement Typed MCPServerInfoDTO and MCPIconDTO">
  <action>
    In `@[backend_v2/models/dtos/mcp.py#L427-L458]`, create [NEW] `MCPIconDTO` and `MCPServerInfoDTO` adhering to the MCP 2024-11-05 specification with strict Pydantic V2 contracts.
    Replace `server_info: dict[str, str]` in `MCPInitializeResultDTO` with `server_info: MCPServerInfoDTO = Field(default_factory=MCPServerInfoDTO, validation_alias=AliasChoices("serverInfo", "server_info"))`.
    Export `MCPIconDTO` and `MCPServerInfoDTO` in `__all__` in `backend_v2/models/dtos/mcp.py`.
  </action>
  <constraint>
    Must use `ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)`.
    Naked dictionaries or loose typing are strictly forbidden.
  </constraint>
</step>

<step id="3" name="Verify Backend Regression Test and Add Negative Boundaries">
  <action>
    In `@[backend_v2/tests/unit/models/dtos/test_mcp.py#L265-L326]`, run `uv run pytest backend_v2/tests/unit/models/dtos/test_mcp.py::test_mcp_initialize_result_dto_with_complex_server_info_metadata` to verify the Red test transitions to Green.
    Add ISTQB negative boundary assertions verifying that unexpected fields in `serverInfo` or `icons` raise `ValidationError` per `extra="forbid"`.
    Run the full test suite `uv run pytest backend_v2/tests/unit/models/dtos/test_mcp.py` and `uv run pytest backend_v2/tests/unit/services/mcp/test_generic_mcp_client.py`.
  </action>
  <constraint>
    Zero test failures or regressions allowed across all existing MCP tests.
  </constraint>
</step>

<step id="4" name="Harden Flutter MCP Gateway Form Controller State Retention">
  <action>
    In `@[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart#L250-L288]`:
    In `McpGatewayForm.submit` and `McpGatewayForm.discoverTools`, synchronize `state = AsyncData(updatedData)` / `state = AsyncData(currentPayload)` immediately before `state = const AsyncLoading()` so Riverpod 3.1.0 retains the latest form payload (`hasValue == true`) across loading and error transitions without calling `@internal` `copyWithPrevious`.
  </action>
  <constraint>
    Must not call `@internal` `copyWithPrevious` API.
    Form state and user inputs must be preserved when discovery or save fails.
  </constraint>
</step>

<step id="5" name="Harden Flutter MCP Gateway View Hook Registration and Pattern Matching">
  <action>
    In `@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart#L21-L65]`:
    Hoist `final bannerMessage = useState<String?>(null);` and `final isBannerError = useState<bool>(false);` from `_buildScaffold` to the top of `McpGatewayView.build` and pass them as parameters to `_buildScaffold`.
    Update `switch (formState)` to match `_ when formState.hasValue => _buildScaffold(context, ref, l10n, formKey, formState, formState.requireValue, bannerMessage, isBannerError)` first so the form stays mounted on background operation loading and error states.
    Preserve fallback to `ErrorView` only on initial load failure (`hasValue == false`).
  </action>
  <constraint>
    Hooks must be called unconditionally at the top of `McpGatewayView.build`.
    Form UI must remain mounted when discovery or save encounters an error.
  </constraint>
</step>

<step id="6" name="Universal Quality Gates Audit">
  <action>
    Run backend audit loop:
    `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/mcp.py --test --ast-strict`
    Run flutter audit loop:
    `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart`
    `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/mcp_gateway_view.dart`
  </action>
  <constraint>
    All quality gates must pass with 0 errors and 0 warnings.
  </constraint>
</step>
</execution_protocol>
