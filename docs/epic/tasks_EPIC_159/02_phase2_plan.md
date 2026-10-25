<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

# Phase 2: Protocol Transport (GenericMCPClient), Security Guardrails (SSRF Firewall, CDATA, Length Budget) & Studio Discovery API

**Overview:** Implement protocol-agnostic JSON-RPC 2.0 `GenericMCPClient` supporting both Streamable HTTP and SSE transports with non-blocking DNS pre-validation and Tenacity retry coordination, create `MCPUrlValidator` SSRF firewall blocking private subnets, cloud metadata IPs, and HTTP redirects, and build the Studio runtime introspection endpoint `POST /api/studio/mcp-gateways/{gateway_id}/discover` with cache persistence and unique gateway slug enforcement.

**Source:** @[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md#L248-L284] Phase 2: Protocol Transport (`GenericMCPClient`), Security Guardrails (SSRF, CDATA, Length Budget) & Studio Discovery API

**Target Files:**
- `[NEW] @[backend_v2/services/mcp/url_validator.py]`
- `[NEW] @[backend_v2/services/mcp/generic_mcp_client.py]`
- `[MODIFY] @[backend_v2/services/cache/typed_cache.py]`
- `[MODIFY] @[backend_v2/services/studio/system_config_service.py]`
- `[MODIFY] @[backend_v2/api/routers/studio/mcp_gateways.py]`
- `[NEW] @[backend_v2/tests/unit/services/mcp/test_url_validator.py]`
- `[NEW] @[backend_v2/tests/unit/services/mcp/test_generic_mcp_client.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_mcp_gateways.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_system_config_service.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `[NEW] @[backend_v2/services/mcp/url_validator.py]` | Banned unvalidated external endpoint URLs and blocking synchronous DNS calls on the async event loop. | Run `validate_mcp_endpoint_url` via `await asyncio.to_thread` inspecting all A/AAAA records; block cloud metadata (`169.254.169.254`), loopback, and private CIDR ranges. | Zero external networking packages; rely on native Python `ipaddress` and `socket.getaddrinfo`. | `pytest backend_v2/tests/unit/services/mcp/test_url_validator.py` with ISTQB boundary tests. |
| `[NEW] @[backend_v2/services/mcp/generic_mcp_client.py]` | Banned per-vendor HTTP client wrappers, open redirect following, unconstrained timeouts, and naive string model validation crashing on SSE. | Implement `GenericMCPClient` with `follow_redirects=False`, Tenacity retry coordination, dual `application/json` & `text/event-stream` framing, and sentence boundary budgeting. | Zero external MCP SDK dependencies; direct httpx client with Pydantic V2 wire DTOs. | `pytest backend_v2/tests/unit/services/mcp/test_generic_mcp_client.py`. |
| `@[backend_v2/services/studio/system_config_service.py]` & `@[backend_v2/api/routers/studio/mcp_gateways.py]` | Banned delete endpoint calling `delete_system_config` (failing with 404), duplicate slug values, and missing tool discovery endpoint. | Implement dedicated `delete_mcp_gateways`, enforce unique slug validation, and create `POST /{gateway_id}/discover` introspecting remote tools into `SystemConfigMCPGateways`. | Reused existing system repository and typed cache infrastructure. | `pytest backend_v2/tests/unit/test_mcp_gateways.py` and `pytest backend_v2/tests/unit/services/studio/test_system_config_service.py`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 1 completed models/dtos/mcp.py with wire DTOs (MCPJsonRpcRequestDTO, MCPJsonRpcResponseDTO, MCPDiscoveredToolWireDTO).</action>
    <action>Look forward: Verify GenericMCPClient uses wire DTOs with model_validate_json and by_alias=True without expanding BOUNDARY_EXEMPTION_FILES.</action>
    <constraint invariant="universal_fail_fast">Raise AppException(ErrorCodes.SECURITY_VIOLATION) on blocked IP/CIDR or redirect attempt.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: Mark Step 2.1, 2.2, 2.3 checkboxes in @[docs/epic/EPIC_159_tracker.md] upon completion of each sub-step.</directive>
  </step>

  <touched_artifacts>
    <backend>[NEW] @[backend_v2/services/mcp/url_validator.py]</backend>
    <backend>[NEW] @[backend_v2/services/mcp/generic_mcp_client.py]</backend>
    <backend>@[backend_v2/services/cache/typed_cache.py]</backend>
    <backend>@[backend_v2/services/studio/system_config_service.py]</backend>
    <backend>@[backend_v2/api/routers/studio/mcp_gateways.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>MCPUrlValidator implemented with non-blocking DNS resolution and cloud metadata / CIDR blocking.</item>
    <item>GenericMCPClient implemented supporting STREAMABLE_HTTP and SSE transports over JSON-RPC 2.0.</item>
    <item>Tenacity retry coordination bounded by settings.llm_max_transient_retries.</item>
    <item>Pre-flight URL validation executed on initial URL and negotiated SSE POST endpoint URLs.</item>
    <item>Typed cache MCPGatewayCache registered and updated upon discovery and gateway deletion.</item>
    <item>Studio endpoint POST /api/studio/mcp-gateways/{gateway_id}/discover implemented and tested.</item>
    <item>delete_mcp_gateways implemented in service layer and wired to DELETE /{gateway_id} router.</item>
    <item>Unique slug validation enforced on draft, clone, and save operations.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
  </required_context_rules>

  <step id="2.1" name="SSRF URL &amp; Network Egress Validator">
    <action>Create [NEW] @[backend_v2/services/mcp/url_validator.py] with MCPUrlValidator.validate_mcp_endpoint_url(url: str, *, allow_private_networks: bool) -&gt; str.</action>
    <action>Enforce https:// or http:// scheme rejection of file://, gopher://, ws://.</action>
    <action>Resolve hostnames via socket.getaddrinfo and inspect all A and AAAA records, blocking cloud metadata (169.254.169.254), loopback, link-local, and private subnets when allow_private_networks is False.</action>
    <action>Create [NEW] @[backend_v2/tests/unit/services/mcp/test_url_validator.py] asserting security violation on prohibited addresses.</action>
    <constraint invariant="credential_hardcoding_ban">Never hardcode test IP ranges outside test fixtures.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/url_validator.py --test --ast-strict</audit_command>
  </step>

  <step id="2.2" name="Protocol-Agnostic GenericMCPClient">
    <action>Create [NEW] @[backend_v2/services/mcp/generic_mcp_client.py] implementing initialize, list_tools, and call_tool.</action>
    <action>Enforce non-blocking DNS pre-flight checks via await asyncio.to_thread(MCPUrlValidator.validate_mcp_endpoint_url, ...).</action>
    <action>Instantiate httpx.AsyncClient with follow_redirects=False and timeouts bounded by settings.mcp_default_timeout_seconds and settings.mcp_discovery_timeout_seconds.</action>
    <action>Implement dual wire parsing: parse application/json directly and extract text/event-stream data: frames correlated to request.id.</action>
    <action>Pass tool responses through enforce_sentence_boundary_budget and CDATA encapsulation via TemplateProcessor.encapsulate_payload.</action>
    <action>Create [NEW] @[backend_v2/tests/unit/services/mcp/test_generic_mcp_client.py] covering positive discovery/calls and negative error conditions.</action>
    <constraint invariant="ai_bloatware_ban">Do NOT import external MCP SDK libraries; use native httpx and Pydantic wire DTOs.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/services/mcp/generic_mcp_client.py --test --ast-strict</audit_command>
  </step>

  <step id="2.3" name="Studio Introspection Endpoint, Multi-Gateway Slug Uniqueness &amp; Cache Persistence">
    <action>In @[backend_v2/services/cache/typed_cache.py], register MCPGatewayCache with deterministic invalidation.</action>
    <action>In @[backend_v2/services/studio/system_config_service.py], implement discover_mcp_gateway_tools and delete_mcp_gateways, and enforce unique single-underscore slugs.</action>
    <action>In @[backend_v2/api/routers/studio/mcp_gateways.py], add POST /{gateway_id}/discover and wire DELETE /{gateway_id} to delete_mcp_gateways.</action>
    <action>Update tests in @[backend_v2/tests/unit/test_mcp_gateways.py] and @[backend_v2/tests/unit/services/studio/test_system_config_service.py] covering discovery and slug collisions.</action>
    <constraint invariant="universal_fail_fast">Raise ResourceNotFoundError if gateway_id does not exist; raise AppException(ErrorCodes.VALIDATION_FAILED) on duplicate slug.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/api/routers/studio/mcp_gateways.py backend_v2/services/studio/system_config_service.py --test --ast-strict</audit_command>
  </step>
</execution_protocol>
```
