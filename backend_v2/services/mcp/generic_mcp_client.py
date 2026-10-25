"""Protocol-agnostic JSON-RPC 2.0 MCP client supporting Streamable HTTP and HTTP+SSE transports."""

import asyncio
import logging
import os
from urllib.parse import urljoin

import httpx
from pydantic import ValidationError
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    ServiceUnavailableError,
)
from backend_v2.llm.provider import _is_transient_llm_error
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.system_config import AllowedMCPTool, SystemConfigMCPGateways
from backend_v2.models.dtos.mcp import (
    MCPInitializeParamsDTO,
    MCPInitializeResultDTO,
    MCPJsonRpcRequestDTO,
    MCPJsonRpcResponseDTO,
    MCPToolCallParamsDTO,
    MCPToolCallResultDTO,
    MCPToolInvocationDTO,
    MCPToolsListResultDTO,
)
from backend_v2.models.enums import MCPAuthType, MCPTransportType, ToolCapability
from backend_v2.services.length_budget_enforcer import enforce_sentence_boundary_budget
from backend_v2.services.mcp.url_validator import MCPUrlValidator
from backend_v2.settings import get_settings

__all__ = ["GenericMCPClient"]

logger = logging.getLogger(__name__)

_REDIRECT_STATUS_CODES: frozenset[int] = frozenset({301, 302, 303, 307, 308})
_TRANSIENT_STATUS_CODES: frozenset[int] = frozenset({429, 502, 503, 504})


class GenericMCPClient:
    """Executes JSON-RPC 2.0 tool discovery and invocation against external MCP servers."""

    def __init__(self, transport: httpx.AsyncBaseTransport | None = None) -> None:
        """Initialize the MCP client with an optional custom HTTP transport.

        Args:
            transport: Optional httpx.AsyncBaseTransport for deterministic testing.
        """
        self._transport = transport

    async def initialize(self, gateway: SystemConfigMCPGateways) -> MCPInitializeResultDTO:
        """Execute the MCP 'initialize' handshake against the configured gateway.

        # Phase 2, Step 2.2: Protocol-Agnostic GenericMCPClient initialize handshake

        Args:
            gateway: Target MCP gateway configuration.

        Returns:
            Validated MCPInitializeResultDTO returned by the server.

        Raises:
            AppException: With ErrorCodes.SECURITY_VIOLATION on SSRF failure,
                ErrorCodes.VALIDATION_ERROR on configuration error, or
                ErrorCodes.SERVICE_UNAVAILABLE on transport error.
        """
        settings = get_settings()
        validated_url = await asyncio.to_thread(
            MCPUrlValidator.validate_mcp_endpoint_url,
            gateway.endpoint_url,
            allow_private_networks=settings.mcp_allow_private_networks,
        )
        headers = self._build_request_headers(gateway)
        discovery_timeout = min(
            float(gateway.timeout_seconds),
            float(settings.mcp_discovery_timeout_seconds),
        )

        async with httpx.AsyncClient(
            transport=self._transport,
            follow_redirects=False,
            timeout=discovery_timeout,
        ) as client:
            target_url, buffered_frames = await self._prepare_transport_endpoint(
                client=client,
                gateway=gateway,
                validated_url=validated_url,
                headers=headers,
                allow_private_networks=settings.mcp_allow_private_networks,
            )
            init_result, _ = await self._perform_initialize_handshake(
                client=client,
                target_url=target_url,
                headers=headers,
                buffered_frames=buffered_frames,
            )
            return init_result

    async def list_tools(self, gateway: SystemConfigMCPGateways) -> list[AllowedMCPTool]:
        """Discover all available tools exposed by the remote MCP gateway via 'tools/list'.

        # Phase 2, Step 2.2: Protocol-Agnostic GenericMCPClient list_tools discovery

        Args:
            gateway: Target MCP gateway configuration.

        Returns:
            List of AllowedMCPTool domain objects with recursive input_schema definitions.

        Raises:
            AppException: With ErrorCodes.SECURITY_VIOLATION on SSRF failure,
                ErrorCodes.VALIDATION_ERROR on configuration error, or
                ErrorCodes.SERVICE_UNAVAILABLE on transport error.
        """
        settings = get_settings()
        validated_url = await asyncio.to_thread(
            MCPUrlValidator.validate_mcp_endpoint_url,
            gateway.endpoint_url,
            allow_private_networks=settings.mcp_allow_private_networks,
        )
        headers = self._build_request_headers(gateway)
        discovery_timeout = min(
            float(gateway.timeout_seconds),
            float(settings.mcp_discovery_timeout_seconds),
        )

        async with httpx.AsyncClient(
            transport=self._transport,
            follow_redirects=False,
            timeout=discovery_timeout,
        ) as client:
            target_url, buffered_frames = await self._prepare_transport_endpoint(
                client=client,
                gateway=gateway,
                validated_url=validated_url,
                headers=headers,
                allow_private_networks=settings.mcp_allow_private_networks,
            )
            _, session_headers = await self._perform_initialize_handshake(
                client=client,
                target_url=target_url,
                headers=headers,
                buffered_frames=buffered_frames,
            )
            list_req = MCPJsonRpcRequestDTO(id=2, method="tools/list")
            rpc_response = await self._send_rpc_request(
                client=client,
                url=target_url,
                request_dto=list_req,
                headers=session_headers,
                buffered_frames=buffered_frames,
            )

        return self._parse_tools_list_response(rpc_response=rpc_response, gateway_id=gateway.id)

    async def call_tool(
        self,
        gateway: SystemConfigMCPGateways,
        invocation: MCPToolInvocationDTO,
    ) -> str:
        """Invoke a remote MCP tool via 'tools/call', enforce sentence budget, and encapsulate in CDATA.

        # Phase 2, Step 2.2: Protocol-Agnostic GenericMCPClient call_tool with sentence budget and CDATA

        Args:
            gateway: Target MCP gateway configuration.
            invocation: Validated tool invocation payload.

        Returns:
            CDATA-shielded and character-budgeted tool response string.

        Raises:
            AppException: With ErrorCodes.SECURITY_VIOLATION on SSRF failure,
                ErrorCodes.SERVICE_UNAVAILABLE on transport failure, or
                ErrorCodes.VALIDATION_ERROR on invalid tool execution payload.
        """
        settings = get_settings()
        validated_url = await asyncio.to_thread(
            MCPUrlValidator.validate_mcp_endpoint_url,
            gateway.endpoint_url,
            allow_private_networks=settings.mcp_allow_private_networks,
        )
        headers = self._build_request_headers(gateway)
        exec_timeout = float(gateway.timeout_seconds)

        async with httpx.AsyncClient(
            transport=self._transport,
            follow_redirects=False,
            timeout=exec_timeout,
        ) as client:
            target_url, buffered_frames = await self._prepare_transport_endpoint(
                client=client,
                gateway=gateway,
                validated_url=validated_url,
                headers=headers,
                allow_private_networks=settings.mcp_allow_private_networks,
            )
            _, session_headers = await self._perform_initialize_handshake(
                client=client,
                target_url=target_url,
                headers=headers,
                buffered_frames=buffered_frames,
            )
            call_req = MCPJsonRpcRequestDTO(
                id=3,
                method="tools/call",
                params=MCPToolCallParamsDTO(
                    name=invocation.tool_id,
                    arguments=invocation.arguments,
                ),
            )
            rpc_response = await self._send_rpc_request(
                client=client,
                url=target_url,
                request_dto=call_req,
                headers=session_headers,
                buffered_frames=buffered_frames,
            )

        raw_text = self._extract_tool_call_text(rpc_response=rpc_response, invocation=invocation)
        return self._apply_budget_and_cdata(raw_text=raw_text, max_chars=settings.mcp_max_response_chars)

    def _build_request_headers(self, gateway: SystemConfigMCPGateways) -> dict[str, str]:
        """Resolve authentication secrets from os.environ and build outbound HTTP headers.

        Args:
            gateway: Target MCP gateway configuration.

        Returns:
            Dictionary of HTTP request headers.

        Raises:
            ConfigurationError: If required auth_env_var or auth_header_name is missing or empty.
        """
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if gateway.auth_type == MCPAuthType.NONE:
            return headers

        env_var_name = gateway.auth_env_var
        if env_var_name is None or not env_var_name.strip():
            logger.error(
                "MCP gateway missing auth_env_var configuration",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "gateway_id": gateway.id},
            )
            raise ConfigurationError(
                f"MCP gateway '{gateway.id}' requires auth_env_var for auth_type '{gateway.auth_type}'."
            )

        clean_env_name = env_var_name.strip()
        if clean_env_name not in os.environ or not os.environ[clean_env_name].strip():
            logger.error(
                "MCP gateway secret environment variable is not set",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "gateway_id": gateway.id},
            )
            raise ConfigurationError(
                f"Environment variable '{clean_env_name}' required by MCP gateway '{gateway.id}' is not set."
            )

        secret_value = os.environ[clean_env_name].strip()
        if gateway.auth_type == MCPAuthType.BEARER:
            headers["Authorization"] = f"Bearer {secret_value}"
            return headers

        header_name = gateway.auth_header_name
        if header_name is None or not header_name.strip():
            logger.error(
                "MCP gateway missing auth_header_name for api_key_header",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "gateway_id": gateway.id},
            )
            raise ConfigurationError(
                f"MCP gateway '{gateway.id}' requires auth_header_name when auth_type is api_key_header."
            )

        headers[header_name.strip()] = secret_value
        return headers

    async def _prepare_transport_endpoint(
        self,
        *,
        client: httpx.AsyncClient,
        gateway: SystemConfigMCPGateways,
        validated_url: str,
        headers: dict[str, str],
        allow_private_networks: bool,
    ) -> tuple[str, list[str]]:
        """Negotiate SSE session POST endpoint when transport_type is SSE, or return Streamable HTTP URL.

        Args:
            client: Active httpx.AsyncClient instance.
            gateway: MCP gateway configuration.
            validated_url: Pre-validated base URL.
            headers: Outbound HTTP headers.
            allow_private_networks: Whether private CIDR ranges are permitted.

        Returns:
            2-tuple of (validated POST endpoint URL, buffered SSE data frames).

        Raises:
            AppException: If SSE negotiation fails or returns an SSRF-prohibited endpoint URL.
        """
        if gateway.transport_type != MCPTransportType.SSE:
            return validated_url, []

        sse_headers = dict(headers)
        sse_headers["Accept"] = "text/event-stream"
        response = await self._execute_http_with_retry(
            client=client,
            method="GET",
            url=validated_url,
            headers=sse_headers,
            json_body=None,
        )
        endpoint_uri, data_frames = self._parse_sse_stream_negotiation(response.text)
        if endpoint_uri is None:
            return validated_url, data_frames

        resolved_post_url = urljoin(validated_url, endpoint_uri)
        validated_post_url = await asyncio.to_thread(
            MCPUrlValidator.validate_mcp_endpoint_url,
            resolved_post_url,
            allow_private_networks=allow_private_networks,
        )
        return validated_post_url, data_frames

    async def _perform_initialize_handshake(
        self,
        *,
        client: httpx.AsyncClient,
        target_url: str,
        headers: dict[str, str],
        buffered_frames: list[str],
    ) -> tuple[MCPInitializeResultDTO, dict[str, str]]:
        """Send 'initialize' and 'notifications/initialized' messages and capture session headers.

        Args:
            client: Active httpx.AsyncClient instance.
            target_url: Validated MCP POST endpoint URL.
            headers: Base HTTP headers.
            buffered_frames: Any SSE data frames buffered during endpoint negotiation.

        Returns:
            2-tuple of (MCPInitializeResultDTO, updated session headers).

        Raises:
            AppException: If initialize returns a JSON-RPC error or malformed result.
        """
        init_req = MCPJsonRpcRequestDTO(
            id=1,
            method="initialize",
            params=MCPInitializeParamsDTO(),
        )
        http_response = await self._execute_http_with_retry(
            client=client,
            method="POST",
            url=target_url,
            headers=headers,
            json_body=init_req.model_dump(mode="json", by_alias=True, exclude_none=True),
        )

        session_headers = dict(headers)
        if "mcp-session-id" in http_response.headers:
            session_headers["Mcp-Session-Id"] = http_response.headers["mcp-session-id"]

        rpc_response = self._extract_jsonrpc_response(
            http_response=http_response,
            expected_id=init_req.id,
            buffered_frames=buffered_frames,
        )
        if rpc_response.error is not None:
            raise self._build_rpc_error(
                f"MCP initialize failed: {rpc_response.error.message}",
                error_code=ErrorCodes.SEARCH_EXECUTION_FAILED,
            )

        init_result = MCPInitializeResultDTO()
        if isinstance(rpc_response.result, MCPInitializeResultDTO):
            init_result = rpc_response.result

        notif_req = MCPJsonRpcRequestDTO(method="notifications/initialized")
        await self._execute_http_with_retry(
            client=client,
            method="POST",
            url=target_url,
            headers=session_headers,
            json_body=notif_req.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return init_result, session_headers

    async def _send_rpc_request(
        self,
        *,
        client: httpx.AsyncClient,
        url: str,
        request_dto: MCPJsonRpcRequestDTO,
        headers: dict[str, str],
        buffered_frames: list[str],
    ) -> MCPJsonRpcResponseDTO:
        """Send a JSON-RPC 2.0 request and extract the correlated response envelope.

        Args:
            client: Active httpx.AsyncClient instance.
            url: Target MCP endpoint URL.
            request_dto: Outbound MCPJsonRpcRequestDTO.
            headers: Outbound HTTP headers including session and auth headers.
            buffered_frames: Buffered SSE data frames when using SSE transport.

        Returns:
            Validated MCPJsonRpcResponseDTO matching request_dto.id.

        Raises:
            AppException: On transport failure, redirect attempt, or malformed JSON-RPC payload.
        """
        http_response = await self._execute_http_with_retry(
            client=client,
            method="POST",
            url=url,
            headers=headers,
            json_body=request_dto.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return self._extract_jsonrpc_response(
            http_response=http_response,
            expected_id=request_dto.id,
            buffered_frames=buffered_frames,
        )

    async def _execute_http_with_retry(
        self,
        *,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        headers: dict[str, str],
        json_body: object | None,
    ) -> httpx.Response:
        """Execute an HTTP request wrapped in Tenacity transient retry coordination.

        Args:
            client: Active httpx.AsyncClient instance.
            method: HTTP verb ('GET' or 'POST').
            url: Validated target URL.
            headers: Request headers.
            json_body: Serialized JSON-RPC request body or None for GET.

        Returns:
            Validated httpx.Response.

        Raises:
            AppException: On redirect (SECURITY_VIOLATION), transient exhaustion (SERVICE_UNAVAILABLE),
                or non-2xx HTTP status (SEARCH_EXECUTION_FAILED).
        """
        settings = get_settings()
        max_attempts = max(1, settings.llm_max_transient_retries)
        retryer = AsyncRetrying(
            retry=retry_if_exception(_is_transient_llm_error),
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential_jitter(
                initial=settings.llm_retry_delay,
                max=float(settings.llm_retry_max_seconds),
            ),
            reraise=True,
        )
        try:
            async for attempt in retryer:
                with attempt:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=json_body,
                    )
                    self._validate_http_status(response)
                    return response
        except AppException:
            raise
        except (httpx.TimeoutException, httpx.NetworkError, TimeoutError) as exc:
            logger.error(
                "MCP transport network or timeout failure",
                extra={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
            )
            raise ServiceUnavailableError(
                message="MCP gateway transport network or timeout failure.",
                details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value, "reason": str(exc)},
            ) from exc

        raise ServiceUnavailableError(
            message="MCP gateway is temporarily unavailable.",
            details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
        )

    def _validate_http_status(self, response: httpx.Response) -> None:
        """Inspect HTTP status code for prohibited redirects, transient 5xx/429, or fatal 4xx/5xx.

        Args:
            response: Inbound httpx.Response.

        Raises:
            AppException: On 3xx redirect (SECURITY_VIOLATION), 429/502/503/504 (SERVICE_UNAVAILABLE),
                or other >=400 status (SEARCH_EXECUTION_FAILED).
        """
        status_code = response.status_code
        if status_code in _REDIRECT_STATUS_CODES or (300 <= status_code < 400):
            logger.error(
                "MCP server attempted prohibited HTTP redirect",
                extra={"error_code": ErrorCodes.SECURITY_VIOLATION.value, "status_code": status_code},
            )
            raise AppException(
                message=f"MCP endpoint returned prohibited HTTP redirect ({status_code}).",
                status_code=403,
                details={"error_code": ErrorCodes.SECURITY_VIOLATION.value},
            )

        if status_code in _TRANSIENT_STATUS_CODES:
            logger.warning(
                "MCP endpoint returned transient HTTP status",
                extra={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value, "status_code": status_code},
            )
            raise ServiceUnavailableError(
                message=f"MCP endpoint returned transient HTTP status {status_code}.",
                details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value, "http_status": status_code},
            )

        if status_code >= 400:
            raise self._build_rpc_error(
                f"MCP endpoint returned HTTP error {status_code}.",
                error_code=ErrorCodes.SEARCH_EXECUTION_FAILED,
            )

    def _extract_jsonrpc_response(
        self,
        *,
        http_response: httpx.Response,
        expected_id: int | str | None,
        buffered_frames: list[str],
    ) -> MCPJsonRpcResponseDTO:
        """Extract and validate a JSON-RPC 2.0 response from application/json or text/event-stream.

        Args:
            http_response: Inbound httpx.Response.
            expected_id: Outbound request correlation ID.
            buffered_frames: Buffered SSE data payloads from SSE session stream.

        Returns:
            Validated MCPJsonRpcResponseDTO matching expected_id.

        Raises:
            AppException: With ErrorCodes.AGENT_RESPONSE_MALFORMED if payload is missing or invalid.
        """
        content_type = ""
        if "content-type" in http_response.headers:
            content_type = http_response.headers["content-type"].lower()

        body_text = http_response.text.strip()
        if "text/event-stream" in content_type or body_text.startswith(("event:", "data:", ":")):
            _, stream_frames = self._parse_sse_stream_negotiation(http_response.text)
            candidate_frames = stream_frames + buffered_frames
            return self._match_sse_jsonrpc_frame(frames=candidate_frames, expected_id=expected_id)

        if not body_text and buffered_frames:
            return self._match_sse_jsonrpc_frame(frames=buffered_frames, expected_id=expected_id)

        try:
            return MCPJsonRpcResponseDTO.model_validate_json(body_text)
        except ValidationError as exc:
            raise self._build_rpc_error(
                "Malformed JSON-RPC 2.0 response from MCP server.",
                error_code=ErrorCodes.AGENT_RESPONSE_MALFORMED,
            ) from exc

    def _parse_sse_stream_negotiation(self, raw_sse: str) -> tuple[str | None, list[str]]:
        """Parse SSE text into an optional 'endpoint' URI and a list of JSON data payloads.

        Args:
            raw_sse: Raw text/event-stream body.

        Returns:
            2-tuple of (negotiated endpoint URI or None, list of JSON data frame strings).
        """
        endpoint_uri: str | None = None
        data_frames: list[str] = []
        current_event = "message"
        current_data_lines: list[str] = []

        for raw_line in raw_sse.splitlines():
            line = raw_line.strip()
            if not line:
                if current_data_lines:
                    payload = "\n".join(current_data_lines).strip()
                    if current_event == "endpoint":
                        endpoint_uri = payload
                    elif payload:
                        data_frames.append(payload)
                    current_data_lines = []
                current_event = "message"
                continue

            if line.startswith(":"):
                continue
            if line.startswith("event:"):
                current_event = line.removeprefix("event:").strip()
            elif line.startswith("data:"):
                current_data_lines.append(line.removeprefix("data:").strip())

        if current_data_lines:
            payload = "\n".join(current_data_lines).strip()
            if current_event == "endpoint":
                endpoint_uri = payload
            elif payload:
                data_frames.append(payload)

        return endpoint_uri, data_frames

    def _match_sse_jsonrpc_frame(
        self,
        *,
        frames: list[str],
        expected_id: int | str | None,
    ) -> MCPJsonRpcResponseDTO:
        """Locate and validate the JSON-RPC response frame matching expected_id.

        Args:
            frames: Extracted SSE data strings.
            expected_id: Request correlation ID to match.

        Returns:
            Validated MCPJsonRpcResponseDTO.

        Raises:
            AppException: With ErrorCodes.AGENT_RESPONSE_MALFORMED if no matching frame is found.
        """
        fallback_response: MCPJsonRpcResponseDTO | None = None
        for frame in frames:
            if not frame.startswith("{"):
                continue
            if '"method"' in frame and '"result"' not in frame and '"error"' not in frame:
                continue
            try:
                parsed = MCPJsonRpcResponseDTO.model_validate_json(frame)
            except ValidationError as exc:
                raise self._build_rpc_error(
                    "Malformed JSON-RPC 2.0 frame in SSE stream.",
                    error_code=ErrorCodes.AGENT_RESPONSE_MALFORMED,
                ) from exc
            if expected_id is not None and parsed.id == expected_id:
                return parsed
            if parsed.id is not None and fallback_response is None:
                fallback_response = parsed

        if fallback_response is not None and expected_id is None:
            return fallback_response

        raise self._build_rpc_error(
            f"No matching JSON-RPC 2.0 response frame found in SSE stream for id={expected_id}.",
            error_code=ErrorCodes.AGENT_RESPONSE_MALFORMED,
        )

    def _parse_tools_list_response(
        self,
        *,
        rpc_response: MCPJsonRpcResponseDTO,
        gateway_id: str,
    ) -> list[AllowedMCPTool]:
        """Validate tools/list response and convert wire tool definitions into AllowedMCPTool models.

        Args:
            rpc_response: Validated JSON-RPC response envelope.
            gateway_id: Opaque ID of the gateway for structured logging.

        Returns:
            List of AllowedMCPTool models.

        Raises:
            AppException: If rpc_response contains an error or unexpected result payload.
        """
        if rpc_response.error is not None:
            raise self._build_rpc_error(
                f"MCP tools/list failed on gateway '{gateway_id}': {rpc_response.error.message}",
                error_code=ErrorCodes.SEARCH_EXECUTION_FAILED,
            )

        if not isinstance(rpc_response.result, MCPToolsListResultDTO):
            raise self._build_rpc_error(
                f"MCP tools/list returned unexpected result structure on gateway '{gateway_id}'.",
                error_code=ErrorCodes.AGENT_RESPONSE_MALFORMED,
            )

        discovered: list[AllowedMCPTool] = []
        for wire_tool in rpc_response.result.tools:
            description_text = wire_tool.description.strip()
            if not description_text:
                description_text = f"MCP tool {wire_tool.name}"
            discovered.append(
                AllowedMCPTool(
                    tool_id=wire_tool.name,
                    capability=ToolCapability.SEARCH,
                    name=I18nText(translations={"en": wire_tool.name, "fi": wire_tool.name}),
                    description=description_text,
                    input_schema=wire_tool.input_schema,
                    enabled=True,
                )
            )
        return discovered

    def _extract_tool_call_text(
        self,
        *,
        rpc_response: MCPJsonRpcResponseDTO,
        invocation: MCPToolInvocationDTO,
    ) -> str:
        """Validate tools/call JSON-RPC response and join text content blocks.

        Args:
            rpc_response: Validated JSON-RPC response envelope.
            invocation: Original tool invocation request.

        Returns:
            Concatenated text output from the MCP tool.

        Raises:
            AppException: If rpc_response.error is set or result.is_error is True.
        """
        if rpc_response.error is not None:
            raise self._build_rpc_error(
                f"MCP tools/call error for '{invocation.namespaced_alias}': {rpc_response.error.message}",
                error_code=ErrorCodes.SEARCH_EXECUTION_FAILED,
            )

        if not isinstance(rpc_response.result, MCPToolCallResultDTO):
            raise self._build_rpc_error(
                f"MCP tools/call returned malformed result for '{invocation.namespaced_alias}'.",
                error_code=ErrorCodes.AGENT_RESPONSE_MALFORMED,
            )

        if rpc_response.result.is_error:
            error_texts = [block.text for block in rpc_response.result.content if block.text.strip()]
            detail_msg = "Remote MCP tool reported isError=True."
            if error_texts:
                detail_msg = "; ".join(error_texts)
            raise self._build_rpc_error(
                f"MCP tool '{invocation.namespaced_alias}' execution failed: {detail_msg}",
                error_code=ErrorCodes.SEARCH_EXECUTION_FAILED,
            )

        text_parts = [block.text for block in rpc_response.result.content if block.text]
        return "\n".join(text_parts)

    def _apply_budget_and_cdata(self, *, raw_text: str, max_chars: int) -> str:
        """Enforce sentence-boundary character budget and encapsulate in CDATA.

        Args:
            raw_text: Raw concatenated tool output string.
            max_chars: Maximum character budget from settings.mcp_max_response_chars.

        Returns:
            CDATA-wrapped, sentence-boundary budgeted text string.
        """
        stripped = raw_text.strip()
        if not stripped:
            return TemplateProcessor.encapsulate_payload("")

        budgeted = enforce_sentence_boundary_budget(stripped, max_chars)
        return TemplateProcessor.encapsulate_payload(budgeted)

    def _build_rpc_error(self, message: str, *, error_code: ErrorCodes) -> AppException:
        """Log structured error and construct AppException with the given ErrorCodes member.

        Args:
            message: Human-readable debug message.
            error_code: Canonical ErrorCodes enum member.

        Returns:
            Configured AppException instance.
        """
        logger.error(
            "MCP protocol execution error",
            extra={"error_code": error_code.value, "reason": message},
        )
        return AppException(
            message=message,
            status_code=502,
            details={"error_code": error_code.value},
        )
