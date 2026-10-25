"""Unit tests for GenericMCPClient JSON-RPC 2.0 Streamable HTTP and HTTP+SSE transports."""

import json
import socket

import httpx
import pytest

from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    ServiceUnavailableError,
)
from backend_v2.models.domain.system_config import SystemConfigMCPGateways
from backend_v2.models.dtos.mcp import MCPToolInvocationDTO
from backend_v2.models.enums import (
    JSONSchemaPropertyType,
    MCPAuthType,
    MCPTransportType,
    ToolCapability,
)
from backend_v2.services.mcp.generic_mcp_client import GenericMCPClient
from backend_v2.settings import get_settings


@pytest.fixture(autouse=True)
def mock_public_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub socket.getaddrinfo to resolve test domains to a public IPv4 address.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """

    def _fake_getaddrinfo(
        host: str,
        port: int | str | None,
        family: int = 0,
        type: int = 0,
        proto: int = 0,
        flags: int = 0,
    ) -> list[tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int]]]:
        resolved_port = int(port) if isinstance(port, (int, str)) and str(port).isdigit() else 443
        if host == "169.254.169.254":
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("169.254.169.254", resolved_port))]
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", resolved_port))]

    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo)
    fast_settings = get_settings().model_copy(update={"llm_retry_delay": 0.001, "llm_retry_max_seconds": 1})
    monkeypatch.setattr("backend_v2.services.mcp.generic_mcp_client.get_settings", lambda: fast_settings)


def _make_gateway(
    *,
    transport_type: MCPTransportType = MCPTransportType.STREAMABLE_HTTP,
    auth_type: MCPAuthType = MCPAuthType.NONE,
    auth_env_var: str | None = None,
    auth_header_name: str | None = None,
) -> SystemConfigMCPGateways:
    """Construct a SystemConfigMCPGateways instance for unit testing.

    Args:
        transport_type: Transport protocol for the gateway.
        auth_type: Authentication scheme.
        auth_env_var: Optional environment variable name for secret resolution.
        auth_header_name: Optional custom header name for api_key_header auth.

    Returns:
        Configured SystemConfigMCPGateways model.
    """
    return SystemConfigMCPGateways(
        id="sys_8172bda70c8641c5",
        slug="remote_search",
        endpoint_url="https://mcp.example.com/v1/mcp",
        transport_type=transport_type,
        auth_type=auth_type,
        auth_env_var=auth_env_var,
        auth_header_name=auth_header_name,
        timeout_seconds=10,
        tools=[],
    )


@pytest.mark.asyncio
async def test_generic_mcp_client_initialize_and_list_tools_streamable_http(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify initialize handshake, session header propagation, and tools/list over Streamable HTTP.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("MCP_BEARER_SECRET", "tok_test_value")
    captured_requests: list[httpx.Request] = []

    def _responder(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        payload = json.loads(request.content.decode("utf-8"))
        method = payload["method"]
        if method == "initialize":
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json", "Mcp-Session-Id": "sess_99"},
                json={
                    "jsonrpc": "2.0",
                    "id": payload["id"],
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "serverInfo": {"name": "mock-mcp", "version": "1.0.0"},
                        "capabilities": {"tools": {"listChanged": True}},
                    },
                },
            )
        if method == "notifications/initialized":
            return httpx.Response(202)
        if method == "tools/list":
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0",
                    "id": payload["id"],
                    "result": {
                        "tools": [
                            {
                                "name": "tavily_search",
                                "description": "",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "Search query string.",
                                        },
                                        "depth": {
                                            "type": "string",
                                            "enum": ["basic", "advanced"],
                                        },
                                    },
                                    "required": ["query"],
                                },
                            }
                        ]
                    },
                },
            )
        return httpx.Response(400)

    gateway = _make_gateway(auth_type=MCPAuthType.BEARER, auth_env_var="MCP_BEARER_SECRET")
    client = GenericMCPClient(transport=httpx.MockTransport(_responder))

    init_res = await client.initialize(gateway)
    assert init_res.protocol_version == "2025-03-26"

    tools = await client.list_tools(gateway)
    assert len(tools) == 1
    tool = tools[0]
    assert tool.tool_id == "tavily_search"
    assert tool.capability == ToolCapability.SEARCH
    assert tool.enabled is True
    assert tool.description == "MCP tool tavily_search"
    assert tool.name.resolve("en") == "tavily_search"
    assert "query" in tool.input_schema.properties
    assert tool.input_schema.properties["query"].type == JSONSchemaPropertyType.STRING
    assert tool.input_schema.properties["depth"].enum_values == ["basic", "advanced"]

    # Verify Authorization and Mcp-Session-Id headers were transmitted
    assert captured_requests[-1].headers["authorization"] == "Bearer tok_test_value"
    assert captured_requests[-1].headers["mcp-session-id"] == "sess_99"


@pytest.mark.asyncio
async def test_generic_mcp_client_sse_transport_and_event_stream_framing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify SSE endpoint negotiation, comment/notification filtering, and call_tool CDATA budgeting.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("CUSTOM_API_KEY", "key_abc")
    seen_urls: list[str] = []

    def _responder(request: httpx.Request) -> httpx.Response:
        seen_urls.append(str(request.url))
        if request.method == "GET":
            sse_handshake = (
                ": keep-alive comment\n"
                "event: endpoint\n"
                "data: /v1/messages?session_id=sse_1"
            )
            return httpx.Response(
                200,
                headers={"Content-Type": "text/event-stream"},
                text=sse_handshake,
            )

        payload = json.loads(request.content.decode("utf-8"))
        method = payload["method"]
        if method == "initialize":
            sse_init = (
                ": ping\n"
                "data: non-json-banner\n\n"
                'data: {"jsonrpc": "2.0", "method": "notifications/message", "params": {}}\n\n'
                f'data: {{"jsonrpc": "2.0", "id": {payload["id"]}, "result": {{"protocolVersion": "2025-03-26"}}}}'
            )
            return httpx.Response(
                200,
                headers={"Content-Type": "text/event-stream"},
                text=sse_init,
            )
        if method == "notifications/initialized":
            return httpx.Response(202)
        if method == "tools/call":
            result_payload = {
                "jsonrpc": "2.0",
                "id": payload["id"],
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": "First verified sentence with ]]> breakout attempt. Second complete sentence.",
                        }
                    ],
                    "isError": False,
                },
            }
            sse_call = f"event: message\ndata: {json.dumps(result_payload)}\n\n"
            return httpx.Response(
                200,
                headers={"Content-Type": "text/event-stream"},
                text=sse_call,
            )
        return httpx.Response(400)

    gateway = _make_gateway(
        transport_type=MCPTransportType.SSE,
        auth_type=MCPAuthType.API_KEY_HEADER,
        auth_env_var="CUSTOM_API_KEY",
        auth_header_name="X-Api-Key",
    )
    invocation = MCPToolInvocationDTO(
        gateway_id=gateway.id,
        gateway_slug=gateway.slug,
        tool_id="search_docs",
        namespaced_alias="remote_search__search_docs",
        arguments={"query": "quantum computing"},
    )

    client = GenericMCPClient(transport=httpx.MockTransport(_responder))
    output = await client.call_tool(gateway, invocation)

    assert "https://mcp.example.com/v1/messages?session_id=sse_1" in seen_urls
    assert output.startswith("<![CDATA[")
    assert output.endswith("]]>")
    assert "]]]]><![CDATA[>" in output


@pytest.mark.asyncio
async def test_generic_mcp_client_sse_buffered_frames_and_errors() -> None:
    """Verify SSE buffered frames without endpoint event, malformed SSE JSON, and missing frame errors."""
    mode = "buffered_init"

    def _responder(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(
                200,
                headers={"Content-Type": "text/event-stream"},
                text='data: {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-03-26"}}\n\n',
            )
        payload = json.loads(request.content.decode("utf-8"))
        method = payload["method"]
        if method == "initialize":
            if mode == "buffered_init":
                return httpx.Response(202, text="")
            if mode == "malformed_sse_frame":
                return httpx.Response(
                    200,
                    headers={"Content-Type": "text/event-stream"},
                    text="data: {bad-json\n\n",
                )
            return httpx.Response(
                200,
                headers={"Content-Type": "text/event-stream"},
                text='data: {"jsonrpc": "2.0", "id": 999, "result": {"protocolVersion": "2025-03-26"}}\n\n',
            )
        return httpx.Response(202)

    client = GenericMCPClient(transport=httpx.MockTransport(_responder))
    gateway = _make_gateway(transport_type=MCPTransportType.SSE)

    init_res = await client.initialize(gateway)
    assert init_res.protocol_version == "2025-03-26"

    mode = "malformed_sse_frame"
    with pytest.raises(AppException) as malformed_exc:
        await client.initialize(gateway)
    assert malformed_exc.value.details["error_code"] == ErrorCodes.AGENT_RESPONSE_MALFORMED.value

    mode = "unmatched_id"
    with pytest.raises(AppException) as unmatched_exc:
        await client.initialize(_make_gateway())
    assert unmatched_exc.value.details["error_code"] == ErrorCodes.AGENT_RESPONSE_MALFORMED.value


@pytest.mark.asyncio
async def test_generic_mcp_client_blocks_sse_redirect_to_metadata_ip() -> None:
    """Verify SSE endpoint negotiation pointing to 169.254.169.254 is blocked by MCPUrlValidator."""

    def _responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"Content-Type": "text/event-stream"},
            text="event: endpoint\ndata: http://169.254.169.254/latest/meta-data/\n\n",
        )

    gateway = _make_gateway(transport_type=MCPTransportType.SSE)
    client = GenericMCPClient(transport=httpx.MockTransport(_responder))

    with pytest.raises(AppException) as exc_info:
        await client.list_tools(gateway)

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value


@pytest.mark.asyncio
@pytest.mark.parametrize("redirect_code", [301, 302, 303, 307, 308])
async def test_generic_mcp_client_rejects_http_redirects(redirect_code: int) -> None:
    """Verify HTTP 3xx redirect responses are rejected with ErrorCodes.SECURITY_VIOLATION.

    Args:
        redirect_code: HTTP 3xx status code under test.
    """

    def _responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(redirect_code, headers={"Location": "http://169.254.169.254/"})

    client = GenericMCPClient(transport=httpx.MockTransport(_responder))

    with pytest.raises(AppException) as exc_info:
        await client.initialize(_make_gateway())

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value


@pytest.mark.asyncio
async def test_generic_mcp_client_retries_transient_503_and_succeeds() -> None:
    """Verify Tenacity retries transient 503 responses and succeeds when upstream recovers."""
    attempts = 0

    def _responder(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(503, text="Service Unavailable")
        payload = json.loads(request.content.decode("utf-8"))
        if payload["method"] == "initialize":
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json={"jsonrpc": "2.0", "id": payload["id"], "result": {"protocolVersion": "2025-03-26"}},
            )
        return httpx.Response(202)

    client = GenericMCPClient(transport=httpx.MockTransport(_responder))

    result = await client.initialize(_make_gateway())
    assert result.protocol_version == "2025-03-26"
    assert attempts >= 2


@pytest.mark.asyncio
async def test_generic_mcp_client_auth_configuration_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify missing auth_env_var, unset environment variable, and missing auth_header_name raise ConfigurationError.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.delenv("MISSING_MCP_SECRET", raising=False)
    client = GenericMCPClient()

    gw_missing_var = _make_gateway(auth_type=MCPAuthType.BEARER, auth_env_var=None)
    with pytest.raises(ConfigurationError) as exc1:
        await client.initialize(gw_missing_var)
    assert exc1.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value

    gw_unset_env = _make_gateway(auth_type=MCPAuthType.BEARER, auth_env_var="MISSING_MCP_SECRET")
    with pytest.raises(ConfigurationError) as exc2:
        await client.initialize(gw_unset_env)
    assert exc2.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value

    monkeypatch.setenv("PRESENT_MCP_SECRET", "sec_123")
    gw_missing_header = _make_gateway(
        auth_type=MCPAuthType.API_KEY_HEADER,
        auth_env_var="PRESENT_MCP_SECRET",
        auth_header_name="",
    )
    with pytest.raises(ConfigurationError) as exc3:
        await client.initialize(gw_missing_header)
    assert exc3.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_generic_mcp_client_handles_rpc_errors_is_error_and_malformed_payloads() -> None:
    """Verify JSON-RPC error objects, isError=True tool results, HTTP 500, and invalid JSON fail fast."""
    mode = "init_rpc_error"

    def _responder(request: httpx.Request) -> httpx.Response:
        if mode == "http_500":
            return httpx.Response(500, text="Internal Server Error")
        if mode == "malformed_json":
            return httpx.Response(200, headers={"Content-Type": "application/json"}, text="{not-json")

        payload = json.loads(request.content.decode("utf-8"))
        method = payload["method"]
        if method == "initialize":
            if mode == "init_rpc_error":
                return httpx.Response(
                    200,
                    headers={"Content-Type": "application/json"},
                    json={
                        "jsonrpc": "2.0",
                        "id": payload["id"],
                        "error": {"code": -32600, "message": "Invalid Request"},
                    },
                )
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json={"jsonrpc": "2.0", "id": payload["id"], "result": {"protocolVersion": "2025-03-26"}},
            )
        if method == "notifications/initialized":
            return httpx.Response(202)
        if method == "tools/list":
            if mode == "list_wrong_result":
                return httpx.Response(
                    200,
                    headers={"Content-Type": "application/json"},
                    json={"jsonrpc": "2.0", "id": payload["id"], "result": {"protocolVersion": "2025-03-26"}},
                )
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0",
                    "id": payload["id"],
                    "error": {"code": -32601, "message": "Method not found"},
                },
            )
        if method == "tools/call":
            if mode == "call_wrong_result":
                return httpx.Response(
                    200,
                    headers={"Content-Type": "application/json"},
                    json={"jsonrpc": "2.0", "id": payload["id"], "result": {"protocolVersion": "2025-03-26"}},
                )
            if mode == "call_is_error":
                return httpx.Response(
                    200,
                    headers={"Content-Type": "application/json"},
                    json={
                        "jsonrpc": "2.0",
                        "id": payload["id"],
                        "result": {
                            "content": [{"type": "text", "text": "Upstream search rate limit"}],
                            "isError": True,
                        },
                    },
                )
            if mode == "call_empty_output":
                return httpx.Response(
                    200,
                    headers={"Content-Type": "application/json"},
                    json={
                        "jsonrpc": "2.0",
                        "id": payload["id"],
                        "result": {"content": [], "isError": False},
                    },
                )
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0",
                    "id": payload["id"],
                    "error": {"code": -32602, "message": "Invalid params"},
                },
            )
        return httpx.Response(400)

    client = GenericMCPClient(transport=httpx.MockTransport(_responder))
    gateway = _make_gateway()
    invocation = MCPToolInvocationDTO(
        gateway_id=gateway.id,
        gateway_slug=gateway.slug,
        tool_id="search_docs",
        namespaced_alias="remote_search__search_docs",
        arguments={"query": "test"},
    )

    with pytest.raises(AppException) as init_err:
        await client.initialize(gateway)
    assert init_err.value.details["error_code"] == ErrorCodes.SEARCH_EXECUTION_FAILED.value

    mode = "list_rpc_error"
    with pytest.raises(AppException) as list_err:
        await client.list_tools(gateway)
    assert list_err.value.details["error_code"] == ErrorCodes.SEARCH_EXECUTION_FAILED.value

    mode = "list_wrong_result"
    with pytest.raises(AppException) as list_wrong_err:
        await client.list_tools(gateway)
    assert list_wrong_err.value.details["error_code"] == ErrorCodes.AGENT_RESPONSE_MALFORMED.value

    mode = "call_rpc_error"
    with pytest.raises(AppException) as call_err:
        await client.call_tool(gateway, invocation)
    assert call_err.value.details["error_code"] == ErrorCodes.SEARCH_EXECUTION_FAILED.value

    mode = "call_wrong_result"
    with pytest.raises(AppException) as call_wrong_err:
        await client.call_tool(gateway, invocation)
    assert call_wrong_err.value.details["error_code"] == ErrorCodes.AGENT_RESPONSE_MALFORMED.value

    mode = "call_is_error"
    with pytest.raises(AppException) as is_err:
        await client.call_tool(gateway, invocation)
    assert is_err.value.details["error_code"] == ErrorCodes.SEARCH_EXECUTION_FAILED.value
    assert "Upstream search rate limit" in is_err.value.message

    mode = "call_empty_output"
    empty_cdata = await client.call_tool(gateway, invocation)
    assert empty_cdata == "<![CDATA[]]>"

    mode = "http_500"
    with pytest.raises(AppException) as http_err:
        await client.initialize(gateway)
    assert http_err.value.details["error_code"] == ErrorCodes.SEARCH_EXECUTION_FAILED.value

    mode = "malformed_json"
    with pytest.raises(AppException) as json_err:
        await client.initialize(gateway)
    assert json_err.value.details["error_code"] == ErrorCodes.AGENT_RESPONSE_MALFORMED.value


@pytest.mark.asyncio
async def test_generic_mcp_client_translates_timeout_to_service_unavailable() -> None:
    """Verify persistent httpx.ReadTimeout is translated to ServiceUnavailableError after retries."""

    def _responder(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Timed out reading MCP response", request=request)

    client = GenericMCPClient(transport=httpx.MockTransport(_responder))

    with pytest.raises(ServiceUnavailableError) as exc_info:
        await client.initialize(_make_gateway())

    assert exc_info.value.details["error_code"] == ErrorCodes.SERVICE_UNAVAILABLE.value
