"""MCP Tool Dispatcher Module.

Provides dynamic gateway-backed registry, runtime Pydantic argument validation,
and execution dispatching for MCP tools with OpenTelemetry instrumentation and timeouts.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
import uuid
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime

import opentelemetry.trace as trace
from pydantic import BaseModel, ValidationError

from backend_v2.core.telemetry import get_tracer
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    MCPAuditTrace,
    SystemConfigMCPGateways,
)
from backend_v2.models.dtos.mcp import (
    MCPArgumentValue,
    MCPToolDeclarationDTO,
    MCPToolDescriptorDTO,
    MCPToolInvocationDTO,
)
from backend_v2.models.enums import JSONSchemaPropertyType, ToolCapability
from backend_v2.services.mcp.alias_registry import AliasRegistry
from backend_v2.services.mcp.generic_mcp_client import GenericMCPClient
from backend_v2.services.orchestrator.schema_factory import SchemaFactory

__all__ = ["ToolDispatcher"]

logger = logging.getLogger(__name__)

_URL_EXTRACT_PATTERN: re.Pattern[str] = re.compile(r"https?://[^\s<>\"'\])\]]+")


class ToolDispatcher:
    """Dynamic gateway-backed registry and dispatcher for MCP tools."""

    def __init__(
        self,
        gateways: Sequence[SystemConfigMCPGateways],
        mcp_client: GenericMCPClient | None = None,
    ) -> None:
        """Initialize the dispatcher from active SystemConfigMCPGateways definitions.

        Args:
            gateways: Sequence of SystemConfigMCPGateways domain models.
            mcp_client: Optional GenericMCPClient instance for protocol execution.

        Raises:
            AppException: If any enabled tool has an invalid slug or malformed input_schema
                (ErrorCodes.VALIDATION_FAILED).
        """
        if mcp_client is None:
            self._mcp_client = GenericMCPClient()
        else:
            self._mcp_client = mcp_client

        self._descriptors: dict[str, MCPToolDescriptorDTO] = {}
        self._gateways: dict[str, SystemConfigMCPGateways] = {}
        self._arg_models: dict[str, type[BaseModel]] = {}
        self._disabled_tools: set[str] = set()
        self._capability_index: dict[ToolCapability, list[MCPToolDescriptorDTO]] = {cap: [] for cap in ToolCapability}

        for gateway in gateways:
            for tool in gateway.tools:
                namespaced_alias = AliasRegistry.build_namespaced_tool_alias(gateway.slug, tool.tool_id)
                if not tool.enabled:
                    self._disabled_tools.add(namespaced_alias)
                    continue

                descriptor = MCPToolDescriptorDTO(
                    gateway_id=gateway.id,
                    gateway_slug=gateway.slug,
                    namespaced_alias=namespaced_alias,
                    tool_id=tool.tool_id,
                    description=tool.description,
                    capability=tool.capability,
                    input_schema=tool.input_schema,
                    enabled=tool.enabled,
                )
                self._descriptors[namespaced_alias] = descriptor
                self._gateways[namespaced_alias] = gateway
                self._arg_models[namespaced_alias] = SchemaFactory.create_mcp_tool_argument_model(
                    namespaced_alias,
                    tool.input_schema,
                )
                self._capability_index[tool.capability].append(descriptor)

    def get_declarations(self, allowed_tools: Sequence[str]) -> list[MCPToolDeclarationDTO]:
        """Build OpenAI-compatible function declarations for the specified allowed tools.

        Args:
            allowed_tools: Sequence of namespaced tool aliases to include.

        Returns:
            List of MCPToolDeclarationDTO objects preserving the order of allowed_tools.
        """
        declarations: list[MCPToolDeclarationDTO] = []
        for tool_alias in allowed_tools:
            if tool_alias in self._descriptors:
                descriptor = self._descriptors[tool_alias]
                declarations.append(SchemaFactory.build_mcp_tool_declaration(descriptor.namespaced_alias, descriptor))
        return declarations

    def get_all_enabled_tool_aliases(self, capability: ToolCapability | None = None) -> list[str]:
        """Return all enabled namespaced tool aliases across active gateways.

        Args:
            capability: Optional ToolCapability filter.

        Returns:
            Ordered list of enabled namespaced tool alias strings.
        """
        if capability is None:
            return list(self._descriptors.keys())
        return [desc.namespaced_alias for desc in self._capability_index[capability]]

    def get_tools_by_capability(
        self,
        allowed_tools: Sequence[str],
        capability: ToolCapability,
    ) -> list[MCPToolDescriptorDTO]:
        """Return allowed tool descriptors implementing the specified capability in allowed_tools order.

        Args:
            allowed_tools: Sequence of namespaced tool aliases to filter.
            capability: Operational capability category to match.

        Returns:
            List of matching MCPToolDescriptorDTO instances.
        """
        if not self._capability_index[capability]:
            return []
        return [
            self._descriptors[alias]
            for alias in allowed_tools
            if alias in self._descriptors and self._descriptors[alias].capability == capability
        ]

    def resolve_primary_search_tool(self, allowed_tools: Sequence[str]) -> MCPToolDescriptorDTO | None:
        """Resolve primary search tool descriptor preserving explicit step configuration priority.

        Args:
            allowed_tools: Ordered sequence of allowed namespaced tool aliases.

        Returns:
            First matching MCPToolDescriptorDTO with ToolCapability.SEARCH, or None.
        """
        for alias in allowed_tools:
            if alias in self._descriptors and self._descriptors[alias].capability == ToolCapability.SEARCH:
                return self._descriptors[alias]
        return None

    def has_capability(self, allowed_tools: Sequence[str], capability: ToolCapability) -> bool:
        """Check whether any allowed tool implements the given capability.

        Args:
            allowed_tools: Sequence of namespaced tool aliases to check.
            capability: Operational capability to test.

        Returns:
            True if at least one allowed tool implements capability.
        """
        return len(self.get_tools_by_capability(allowed_tools, capability)) > 0

    def build_search_arguments(
        self,
        tool: MCPToolDescriptorDTO | AllowedMCPTool,
        query: str,
        *,
        claim_text: str | None = None,
        reasoning: str | None = None,
        objective: str | None = None,
    ) -> dict[str, MCPArgumentValue]:
        """Construct a schema-aligned search argument dictionary for a search tool.

        Maps the search query and optional companion context (such as objective or claim)
        to schema properties declared by the tool.

        # Phase 1, Step 1: Support multi-parameter search tool schemas (e.g. Exa AI web_search_exa)

        Args:
            tool: Target search tool descriptor or AllowedMCPTool domain object.
            query: Search query string to bind.
            claim_text: Optional claim text being factually audited.
            reasoning: Optional reasoning string justifying the search turn.
            objective: Optional explicit search objective or goal override.

        Returns:
            Validated argument dictionary mapping schema parameter names to argument values.

        Raises:
            AppException: If tool.input_schema cannot deterministically satisfy all required
                parameters from the available search query and context (ErrorCodes.CONFIGURATION_ERROR).
        """
        props = tool.input_schema.properties
        required_keys = tool.input_schema.required

        args: dict[str, MCPArgumentValue] = {}

        # 1. Bind query parameter (prefer 'query', then 'q', 'search_query', 'search_term')
        query_key: str | None = None
        for candidate in ("query", "q", "search_query", "search_term"):
            if candidate in props and props[candidate].type == JSONSchemaPropertyType.STRING:
                query_key = candidate
                break

        if query_key is not None:
            args[query_key] = query

        # 2. Bind objective parameter if declared in properties
        if "objective" in props and props["objective"].type == JSONSchemaPropertyType.STRING:
            resolved_objective = objective
            if not resolved_objective and claim_text:
                resolved_objective = f"Verify factual accuracy for claim: {claim_text}"
            elif not resolved_objective and reasoning:
                resolved_objective = reasoning
            elif not resolved_objective:
                resolved_objective = f"Find external evidence regarding: {query}"

            prop_def = props["objective"]
            if prop_def.max_length is not None and len(resolved_objective) > prop_def.max_length:
                resolved_objective = resolved_objective[: prop_def.max_length]
            args["objective"] = resolved_objective

        # 3. Handle single required string property with custom name
        if len(required_keys) == 1 and not args:
            req_key = required_keys[0]
            if req_key in props and props[req_key].type == JSONSchemaPropertyType.STRING:
                args[req_key] = query

        # 4. Handle tool with zero required keys and single string property
        if not required_keys and not args:
            string_keys = [k for k, v in props.items() if v.type == JSONSchemaPropertyType.STRING]
            if len(string_keys) == 1:
                args[string_keys[0]] = query

        # 5. Check if all required keys are satisfied
        if args and set(required_keys).issubset(args.keys()):
            return args

        msg = (
            f"MCP search tool '{tool.tool_id}' input_schema does not expose a single deterministic "
            "STRING search query parameter."
        )
        logger.error(
            "[ToolDispatcher] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "tool_id": tool.tool_id},
        )
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "tool_id": tool.tool_id},
        )

    async def execute_tool(
        self,
        tool_id: str,
        raw_arguments: Mapping[str, MCPArgumentValue],
        allowed_step_tools: set[str],
        *,
        step_name: str,
        claim_text: str | None = None,
        reasoning: str = "",
    ) -> MCPAuditTrace:
        """Validate permissions and arguments, then dispatch tool execution via GenericMCPClient.

        # Phase 3, Step 3.2: Dynamic ToolDispatcher execution with positive ID-set whitelist and Pydantic validation

        Args:
            tool_id: Namespaced tool alias ('{gateway_slug}__{tool_name}') to execute.
            raw_arguments: Raw tool arguments mapping provided by the caller or LLM.
            allowed_step_tools: Positive whitelist set of namespaced tool aliases permitted for the step.
            step_name: Identifier of the executing step or hook.
            claim_text: Optional verbatim claim text being verified.
            reasoning: Optional reasoning string explaining why the tool was invoked.

        Returns:
            MCPAuditTrace recording provenance, latency, and CDATA-shielded response summary.

        Raises:
            AppException: On unauthorized tool (ErrorCodes.PERMISSION_DENIED),
                disabled tool or invalid arguments (ErrorCodes.VALIDATION_FAILED),
                unknown tool (ErrorCodes.RESOURCE_NOT_FOUND), or timeout (ErrorCodes.SERVICE_UNAVAILABLE).
        """
        if tool_id not in allowed_step_tools:
            msg = f"MCP tool '{tool_id}' is not authorized in allowed_step_tools for step '{step_name}'."
            logger.error(
                "[ToolDispatcher] %s: %s",
                ErrorCodes.PERMISSION_DENIED.name,
                msg,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value, "tool_id": tool_id},
            )
            raise AppException(
                message=msg,
                status_code=403,
                details={"error_code": ErrorCodes.PERMISSION_DENIED.value, "tool_id": tool_id},
            )

        if tool_id in self._disabled_tools:
            msg = f"MCP tool '{tool_id}' is disabled on its gateway."
            logger.error(
                "[ToolDispatcher] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tool_id": tool_id},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tool_id": tool_id},
            )

        if tool_id not in self._descriptors:
            msg = f"MCP tool '{tool_id}' not found in active gateway registry."
            logger.error(
                "[ToolDispatcher] %s: %s",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                msg,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "tool_id": tool_id},
            )
            raise AppException(
                message=msg,
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "tool_id": tool_id},
            )

        descriptor = self._descriptors[tool_id]
        gateway = self._gateways[tool_id]
        arg_model = self._arg_models[tool_id]

        try:
            arg_model.model_validate(dict(raw_arguments))
        except ValidationError as val_err:
            msg = f"Invalid arguments for MCP tool '{tool_id}': {val_err}"
            logger.error(
                "[ToolDispatcher] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tool_id": tool_id},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tool_id": tool_id},
            ) from val_err

        invocation_dto = MCPToolInvocationDTO(
            gateway_id=gateway.id,
            gateway_slug=gateway.slug,
            tool_id=descriptor.tool_id,
            namespaced_alias=descriptor.namespaced_alias,
            arguments=dict(raw_arguments),
        )

        query_str = ""
        if "query" in raw_arguments and isinstance(raw_arguments["query"], str):
            query_str = raw_arguments["query"]
        else:
            for val in raw_arguments.values():
                if isinstance(val, str):
                    query_str = val
                    break

        timeout_sec = float(gateway.timeout_seconds)
        tracer = get_tracer(__name__)

        with tracer.start_as_current_span("mcp.tool_call") as span:
            span.set_attribute("mcp.tool_id", descriptor.tool_id)
            span.set_attribute("mcp.gateway_id", gateway.id)
            span.set_attribute("mcp.step_id", step_name)
            span.set_attribute("mcp.capability", descriptor.capability.value)

            start_time = time.perf_counter()
            try:
                async with asyncio.timeout(timeout_sec):
                    response_summary = await self._mcp_client.call_tool(gateway, invocation_dto)
            except TimeoutError as te:
                span.record_exception(te)
                span.set_status(trace.StatusCode.ERROR, f"MCP tool execution timed out after {timeout_sec}s")
                logger.error(
                    "MCP tool execution timed out",
                    extra={
                        "error_code": ErrorCodes.SERVICE_UNAVAILABLE.value,
                        "tool_id": tool_id,
                        "timeout_seconds": timeout_sec,
                    },
                    exc_info=True,
                )
                raise AppException(
                    message=f"MCP tool '{tool_id}' timed out after {timeout_sec} seconds.",
                    status_code=504,
                    details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value, "tool_id": tool_id},
                ) from te
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(trace.StatusCode.ERROR, str(exc))
                raise

        duration_ms = max(0, int((time.perf_counter() - start_time) * 1000))
        extracted_urls = _URL_EXTRACT_PATTERN.findall(response_summary)
        deduped_urls = list(dict.fromkeys(extracted_urls))

        return MCPAuditTrace(
            id=f"trc_{uuid.uuid4().hex[:8]}",
            gateway_id=gateway.id,
            gateway_slug=gateway.slug,
            namespaced_alias=descriptor.namespaced_alias,
            tool_id=descriptor.tool_id,
            step_name=step_name,
            query=query_str,
            claim_text=claim_text,
            reasoning=reasoning,
            response_summary=response_summary,
            source_urls=deduped_urls,
            timestamp=datetime.now(UTC),
            duration_ms=duration_ms,
        )
