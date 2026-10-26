"""MCP Tool Dispatcher Module.

Provides dynamic gateway-backed registry, runtime Pydantic argument validation,
and execution dispatching for MCP tools with OpenTelemetry instrumentation and timeouts.
"""

from __future__ import annotations

import asyncio
import html
import json
import logging
import re
import time
import uuid
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import opentelemetry.trace as trace
from pydantic import BaseModel, JsonValue, ValidationError

from backend_v2.core.telemetry import get_tracer
from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    MCPAuditTrace,
    SystemConfigMCPGateways,
)
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.mcp import (
    MCPArgumentValue,
    MCPToolDeclarationDTO,
    MCPToolDescriptorDTO,
    MCPToolInputSchemaDTO,
    MCPToolInvocationDTO,
)
from backend_v2.models.enums import JSONSchemaPropertyType, ToolCapability
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompts import MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION
from backend_v2.services.mcp.alias_registry import AliasRegistry
from backend_v2.services.mcp.generic_mcp_client import GenericMCPClient
from backend_v2.services.orchestrator.schema_factory import SchemaFactory

if TYPE_CHECKING:
    from backend_v2.llm.client import LLMClient
    from backend_v2.services.llm_task_executor import LLMTaskExecutor

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

    def get_argument_model(self, tool: MCPToolDescriptorDTO | AllowedMCPTool) -> type[BaseModel]:
        """Resolve the dynamically compiled Pydantic argument model for an MCP tool.

        Args:
            tool: Target MCPToolDescriptorDTO or AllowedMCPTool instance.

        Returns:
            Compiled Pydantic BaseModel subclass representing tool.input_schema.

        Raises:
            AppException: If schema compilation fails (ErrorCodes.VALIDATION_FAILED).
        """
        if isinstance(tool, MCPToolDescriptorDTO) and tool.namespaced_alias in self._arg_models:
            return self._arg_models[tool.namespaced_alias]
        alias_key = tool.tool_id
        if isinstance(tool, MCPToolDescriptorDTO) and tool.namespaced_alias:
            alias_key = tool.namespaced_alias
        return SchemaFactory.create_mcp_tool_argument_model(alias_key, tool.input_schema)

    def build_search_arguments(
        self,
        tool: MCPToolDescriptorDTO | AllowedMCPTool,
        query: str,
        *,
        claim_text: str | None = None,
        reasoning: str | None = None,
        objective: str | None = None,
        configured_params: Mapping[str, MCPArgumentValue] | None = None,
    ) -> dict[str, MCPArgumentValue]:
        """Construct a schema-aligned search argument dictionary for a search tool.

        Maps the search query, static Studio parameter overrides, and optional companion
        context (specifically objective or claim) to schema properties declared by the tool.

        Args:
            tool: Target search tool descriptor or AllowedMCPTool domain object.
            query: Search query string to bind.
            claim_text: Optional claim text being factually audited.
            reasoning: Optional reasoning string justifying the search turn.
            objective: Optional explicit search objective or goal override.
            configured_params: Optional static parameter overrides configured in Studio.

        Returns:
            Validated argument dictionary mapping schema parameter names to argument values.

        Raises:
            AppException: If tool.input_schema cannot deterministically satisfy all required
                parameters from the available search query and context (ErrorCodes.CONFIGURATION_ERROR).
        """
        props = tool.input_schema.properties
        required_keys = tool.input_schema.required

        args: dict[str, MCPArgumentValue] = {}
        if configured_params is not None:
            for param_key, param_val in configured_params.items():
                if param_key in props and param_val is not None:
                    args[param_key] = param_val

        query_key: str | None = None
        for candidate in ("query", "q", "search_query", "search_term"):
            if candidate in props and props[candidate].type == JSONSchemaPropertyType.STRING:
                query_key = candidate
                break

        if query_key is not None:
            args[query_key] = query

        self._bind_objective_parameter(
            schema=tool.input_schema,
            args=args,
            query=query,
            claim_text=claim_text,
            reasoning=reasoning,
            objective=objective,
        )

        if len(required_keys) == 1 and query_key is None:
            req_key = required_keys[0]
            if req_key in props and props[req_key].type == JSONSchemaPropertyType.STRING and req_key not in args:
                args[req_key] = query

        if not required_keys and query_key is None:
            string_keys = [k for k, v in props.items() if v.type == JSONSchemaPropertyType.STRING]
            if len(string_keys) == 1 and string_keys[0] not in args:
                args[string_keys[0]] = query

        has_bound_query = query_key is not None or query in args.values()
        if args and has_bound_query and set(required_keys).issubset(args.keys()):
            arg_model = self.get_argument_model(tool)
            validated = arg_model.model_validate(args, strict=False)
            return validated.model_dump(mode="json", exclude_none=True)

        msg = (
            f"MCP search tool '{tool.tool_id}' input_schema does not expose a single deterministic "
            "STRING search query parameter."
        )
        logger.error(
            "[ToolDispatcher] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "tool_id": tool.tool_id},
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "tool_id": tool.tool_id},
        )

    @staticmethod
    def _bind_objective_parameter(
        *,
        schema: MCPToolInputSchemaDTO,
        args: dict[str, MCPArgumentValue],
        query: str,
        claim_text: str | None,
        reasoning: str | None,
        objective: str | None,
    ) -> None:
        """Populate the 'objective' property in args when declared by the tool input schema.

        Args:
            schema: Tool input JSON schema definition.
            args: Mutable argument dictionary being constructed.
            query: Search query string.
            claim_text: Optional claim text being audited.
            reasoning: Optional reasoning string justifying the search turn.
            objective: Optional explicit search objective override.
        """
        props = schema.properties
        if "objective" not in props or props["objective"].type != JSONSchemaPropertyType.STRING or "objective" in args:
            return

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

    @staticmethod
    def _build_jit_synthesis_messages(
        tool: MCPToolDescriptorDTO | AllowedMCPTool,
        query: str,
        *,
        claim_text: str | None = None,
        reasoning: str | None = None,
        configured_params: Mapping[str, MCPArgumentValue] | None = None,
    ) -> list[LLMMessageDTO]:
        """Construct XML-fenced messages for JIT Micro-LLM MCP argument synthesis.

        Args:
            tool: Target search tool descriptor or AllowedMCPTool domain object.
            query: Search query string to bind.
            claim_text: Optional claim text being factually audited.
            reasoning: Optional reasoning string justifying the search turn.
            configured_params: Optional static parameter overrides configured in Studio.

        Returns:
            List of system and user LLMMessageDTO instances.
        """
        claim_val = ""
        if claim_text is not None:
            claim_val = html.escape(claim_text)
        reasoning_val = ""
        if reasoning is not None:
            reasoning_val = html.escape(reasoning)
        query_val = html.escape(query)
        tool_desc = ""
        if tool.description is not None:
            tool_desc = html.escape(tool.description)
        configured_json = "{}"
        if configured_params is not None:
            configured_json = json.dumps(dict(configured_params), ensure_ascii=False)

        user_content = TemplateProcessor.render_prompt(
            t"<user_payload>\n"
            t"  <tool_id>{tool.tool_id}</tool_id>\n"
            t"  <tool_description>{tool_desc}</tool_description>\n"
            t"  <search_query>{query_val}</search_query>\n"
            t"  <claim_text>{claim_val}</claim_text>\n"
            t"  <reasoning>{reasoning_val}</reasoning>\n"
            t"  <studio_configured_parameters>{configured_json}</studio_configured_parameters>\n"
            t"</user_payload>"
        )
        return [
            LLMMessageDTO(role="system", content=MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION),
            LLMMessageDTO(role="user", content=user_content),
        ]

    async def synthesize_search_arguments(
        self,
        tool: MCPToolDescriptorDTO | AllowedMCPTool,
        query: str,
        *,
        claim_text: str | None = None,
        reasoning: str | None = None,
        objective: str | None = None,
        configured_params: Mapping[str, MCPArgumentValue] | None = None,
        llm_client: LLMClient | None = None,
        executor: LLMTaskExecutor | None = None,
        mock_identity: str | None = None,
        validation_context: dict[str, JsonValue] | None = None,
    ) -> tuple[dict[str, MCPArgumentValue], TokenUsage]:
        """Resolve MCP tool arguments via 0ms deterministic fast-path or JIT Micro-LLM synthesis.

        Args:
            tool: Target search tool descriptor or AllowedMCPTool domain object.
            query: Search query string to bind.
            claim_text: Optional claim text being factually audited.
            reasoning: Optional reasoning string justifying the search turn.
            objective: Optional explicit search objective override.
            configured_params: Optional static parameter overrides configured in Studio.
            llm_client: Optional fast-tier LLMClient for JIT argument synthesis.
            executor: Optional LLMTaskExecutor for structured schema generation.
            mock_identity: Optional mock identity string for deterministic unit tests.
            validation_context: Optional validation context dictionary for executor.

        Returns:
            Tuple of validated argument dictionary and TokenUsage consumed during synthesis.

        Raises:
            AppException: If deterministic binding fails and either JIT synthesis dependencies
                are missing or micro-LLM synthesis fails validation (ErrorCodes.CONFIGURATION_ERROR).
        """
        zero_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        try:
            deterministic_args = self.build_search_arguments(
                tool,
                query,
                claim_text=claim_text,
                reasoning=reasoning,
                objective=objective,
                configured_params=configured_params,
            )
            return deterministic_args, zero_usage
        except AppException:
            if llm_client is None or executor is None:
                raise

        return await self._execute_jit_argument_synthesis(
            tool=tool,
            query=query,
            claim_text=claim_text,
            reasoning=reasoning,
            configured_params=configured_params,
            llm_client=llm_client,
            executor=executor,
            mock_identity=mock_identity,
            validation_context=validation_context,
            zero_usage=zero_usage,
        )

    async def _execute_jit_argument_synthesis(
        self,
        *,
        tool: MCPToolDescriptorDTO | AllowedMCPTool,
        query: str,
        claim_text: str | None,
        reasoning: str | None,
        configured_params: Mapping[str, MCPArgumentValue] | None,
        llm_client: LLMClient,
        executor: LLMTaskExecutor,
        mock_identity: str | None,
        validation_context: dict[str, JsonValue] | None,
        zero_usage: TokenUsage,
    ) -> tuple[dict[str, MCPArgumentValue], TokenUsage]:
        """Invoke JIT Micro-LLM structured synthesis and apply Studio parameter overrides.

        Args:
            tool: Target search tool descriptor or AllowedMCPTool domain object.
            query: Search query string to bind.
            claim_text: Optional claim text being factually audited.
            reasoning: Optional reasoning string justifying the search turn.
            configured_params: Optional static parameter overrides configured in Studio.
            llm_client: Fast-tier LLMClient for JIT argument synthesis.
            executor: LLMTaskExecutor for structured schema generation.
            mock_identity: Optional mock identity string for deterministic unit tests.
            validation_context: Optional validation context dictionary for executor.
            zero_usage: Baseline zero TokenUsage fallback instance.

        Returns:
            Tuple of validated argument dictionary and TokenUsage consumed during synthesis.

        Raises:
            AppException: If micro-LLM synthesis or post-override validation fails
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        arg_model = self.get_argument_model(tool)
        synth_messages = self._build_jit_synthesis_messages(
            tool,
            query,
            claim_text=claim_text,
            reasoning=reasoning,
            configured_params=configured_params,
        )
        try:
            synthesized_raw, synth_usage = await executor.execute_structured_task(
                client=llm_client,
                messages=synth_messages,
                response_model=arg_model,
                mock_identity=mock_identity,
                validation_context=validation_context,
            )
            if isinstance(synthesized_raw, BaseModel):
                synthesized_dict = synthesized_raw.model_dump(mode="json", exclude_none=True)
            else:
                validated_initial = arg_model.model_validate(synthesized_raw, strict=False)
                synthesized_dict = validated_initial.model_dump(mode="json", exclude_none=True)

            if configured_params:
                for param_key, param_val in configured_params.items():
                    if param_key in tool.input_schema.properties and param_val is not None:
                        synthesized_dict[param_key] = param_val

            final_validated = arg_model.model_validate(synthesized_dict, strict=False)
            resolved_usage = zero_usage
            if synth_usage is not None:
                resolved_usage = synth_usage
            return final_validated.model_dump(mode="json", exclude_none=True), resolved_usage
        except Exception as exc:
            msg = f"JIT Micro-LLM argument synthesis failed for MCP tool '{tool.tool_id}': {exc}"
            logger.error(
                "[ToolDispatcher] %s: %s",
                ErrorCodes.CONFIGURATION_ERROR.name,
                msg,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "tool_id": tool.tool_id},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "tool_id": tool.tool_id},
            ) from exc

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
        self._validate_tool_execution_request(
            tool_id=tool_id,
            raw_arguments=raw_arguments,
            allowed_step_tools=allowed_step_tools,
            step_name=step_name,
        )

        descriptor = self._descriptors[tool_id]
        gateway = self._gateways[tool_id]
        invocation_dto = MCPToolInvocationDTO(
            gateway_id=gateway.id,
            gateway_slug=gateway.slug,
            tool_id=descriptor.tool_id,
            namespaced_alias=descriptor.namespaced_alias,
            arguments=dict(raw_arguments),
        )
        query_str = self._extract_primary_query_string(raw_arguments)
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

    def _validate_tool_execution_request(
        self,
        *,
        tool_id: str,
        raw_arguments: Mapping[str, MCPArgumentValue],
        allowed_step_tools: set[str],
        step_name: str,
    ) -> None:
        """Enforce positive whitelist authorization, enabled state, registry presence, and schema validation.

        Args:
            tool_id: Namespaced tool alias ('{gateway_slug}__{tool_name}') to execute.
            raw_arguments: Raw tool arguments mapping provided by the caller or LLM.
            allowed_step_tools: Positive whitelist set of namespaced tool aliases permitted for the step.
            step_name: Identifier of the executing step or hook.

        Raises:
            AppException: On unauthorized tool (ErrorCodes.PERMISSION_DENIED),
                disabled tool or invalid arguments (ErrorCodes.VALIDATION_FAILED),
                or unknown tool (ErrorCodes.RESOURCE_NOT_FOUND).
        """
        if tool_id not in allowed_step_tools:
            msg = f"MCP tool '{tool_id}' is not authorized in allowed_step_tools for step '{step_name}'."
            logger.error(
                "[ToolDispatcher] %s: %s",
                ErrorCodes.PERMISSION_DENIED.name,
                msg,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value, "tool_id": tool_id},
                exc_info=True,
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
                exc_info=True,
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
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "tool_id": tool_id},
            )

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
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tool_id": tool_id},
            ) from val_err

    @staticmethod
    def _extract_primary_query_string(raw_arguments: Mapping[str, MCPArgumentValue]) -> str:
        """Extract the primary search query string from raw tool arguments for audit tracing.

        Args:
            raw_arguments: Validated mapping of tool argument keys to values.

        Returns:
            Primary query string if present, or empty string.
        """
        if "query" in raw_arguments and isinstance(raw_arguments["query"], str):
            return raw_arguments["query"]
        for val in raw_arguments.values():
            if isinstance(val, str):
                return val
        return ""
