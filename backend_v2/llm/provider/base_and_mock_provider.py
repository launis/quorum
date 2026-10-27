"""Abstract LLMProvider base contract, LogfireShieldedClient HTTPX wrapper, and MockProvider."""

import asyncio
import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from typing import Any, override

from pydantic import BaseModel

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.mock import MockLLMService
from backend_v2.llm.provider.env_and_schema_utils import _safe_static_getattr, _sync_diagnostic_dump
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.llm import LLMMessageDTO, LLMResponse, ProviderMetadataDTO
from backend_v2.services.usage_service import UsageService
from backend_v2.settings import get_settings

__all__ = ["LLMProvider", "LogfireShieldedClient", "MockProvider"]

logger = logging.getLogger(__name__)
_ORIG_GET_SETTINGS = get_settings
_ORIG_MOCK_LLM_SERVICE = MockLLMService


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Defines the contract for text generation and structured data extraction.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str | None = None,
        system_instruction: str | None = None,
        messages: list[LLMMessageDTO] | list[dict[str, Any]] | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        pass_reasoning_token: str | None = None,
        validation_context: dict[str, Any] | None = None,
        mock_identity: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generates content from the LLM.

        Args:
            prompt: The user prompt.
            system_instruction: System prompt/context.
            messages: Fallback context or chat history.
            response_schema: Pydantic model or JSON Schema.
            temperature: Sampling temperature.
            max_tokens: Max tokens to generate.
            top_p: Nucleus sampling mass.
            top_k: Top-K sampling count.
            frequency_penalty: Penalizes tokens based on their frequency.
            presence_penalty: Penalizes tokens based on their presence.
            pass_reasoning_token: Encrypted state blob from previous turn.
            validation_context: Optional context for validation.
            mock_identity: Optional internal mock identity for unit test routing.
            **kwargs: Additional provider-specific arguments.

        Returns:
            The generated response object.

        Raises:
            AgentExecutionError: On context bounds exceeded (ErrorCodes.AGENT_EXECUTION_CRITICAL).
            AppException: On internal generation or parsing errors (ErrorCodes.AGENT_RESPONSE_PARSING_FAILED, ErrorCodes.UNKNOWN_ERROR).
            ConfigurationError: On malformed configuration (ErrorCodes.CONFIGURATION_ERROR).
            SecurityViolationError: On blocked content (ErrorCodes.SECURITY_VIOLATION).
            ServiceUnavailableError: On provider network failure (ErrorCodes.SERVICE_UNAVAILABLE).
        """
        pass


class LogfireShieldedClient:
    """Proxy class to hide httpx.AsyncClient from Logfire's deep serialization hook.

    Prevents 'RuntimeError: dictionary changed size during iteration' when Logfire
    iterates over kwargs containing a shared mutating httpx client.
    """

    __slots__ = ("_client",)

    def __init__(self, client: Any) -> None:
        """Initializes the shielded client proxy.

        Args:
            client: Underlying HTTPX async client or transport object to wrap.
        """
        self._client = client

    def __getattr__(self, name: str) -> Any:
        """Forwards attribute lookups to the underlying client.

        Args:
            name: Attribute name to resolve on the wrapped client.

        Returns:
            Resolved attribute value from the underlying client.
        """
        return object.__getattribute__(self._client, name)

    async def __aenter__(self) -> Any:
        """Forwards async context manager entry to the underlying client.

        Returns:
            Entered underlying client context or self if unsupported.
        """
        if "__aenter__" in dir(self._client):
            return await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        """Forwards async context manager exit to the underlying client.

        Args:
            exc_type: Exception type raised within the context, if any.
            exc_val: Exception instance raised within the context, if any.
            exc_tb: Traceback associated with the exception, if any.

        Returns:
            Result of underlying client context exit or None.
        """
        if "__aexit__" in dir(self._client):
            return await self._client.__aexit__(exc_type, exc_val, exc_tb)
        return None

    def __repr__(self) -> str:
        """Returns safe representation string for Logfire telemetry spans.

        Returns:
            Static diagnostic representation shielding internal client state.
        """
        return "<LogfireShieldedClient protecting httpx.AsyncClient>"


class MockProvider(LLMProvider):
    """Mock LLM Provider for offline testing and development.

    Uses cached and simulated responses from MockLLMService.

    Attributes:
        model_name: Target mock model identifier.
        usage_service: Optional usage tracking service instance.
        organization_id: Organization identifier for usage attribution.
    """

    def __init__(
        self,
        model_name: str = "mock",
        usage_service: UsageService | None = None,
        organization_id: str | None = None,
    ) -> None:
        """Initializes the MockProvider instance.

        Args:
            model_name: Identifier for the simulated model.
            usage_service: Optional usage tracking service.
            organization_id: Organization identifier for cost attribution.
        """
        self.model_name = model_name
        self.usage_service = usage_service
        if organization_id:
            self.organization_id = organization_id
        else:
            self.organization_id = "UNKNOWN_ORG"

    def _validate_required_sampling_params(
        self,
        temperature: float | None,
        max_tokens: int | None,
    ) -> None:
        """Validates that mandatory sampling parameters are explicitly provided.

        Args:
            temperature: Sampling temperature parameter.
            max_tokens: Maximum completion token limit.

        Raises:
            ConfigurationError: If temperature or max_tokens is None (ErrorCodes.CONFIGURATION_ERROR).
        """
        if temperature is None:
            msg = "Strict Mode: 'temperature' must be explicitly provided from configuration. No default allowed."
            logger.error("[MockProvider] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise ConfigurationError(message=msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        if max_tokens is None:
            msg = "Strict Mode: 'max_tokens' must be explicitly provided from configuration. No default allowed."
            logger.error("[MockProvider] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise ConfigurationError(message=msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

    async def _maybe_dump_diagnostics(
        self,
        prompt: str | None,
        messages: list[LLMMessageDTO] | list[dict[str, Any]] | None,
        system_instruction: str | None,
    ) -> None:
        """Writes diagnostic prompt payload to disk when DUMP_PROMPTS_FILE is configured.

        Args:
            prompt: User prompt text.
            messages: Optional chat message sequence.
            system_instruction: Optional system prompt instruction.

        Raises:
            ConfigurationError: If writing the diagnostic dump fails (ErrorCodes.CONFIGURATION_ERROR).
        """
        dump_file = os.getenv("DUMP_PROMPTS_FILE")
        if dump_file:
            try:
                payload_parts: list[str] = []
                if prompt:
                    payload_parts.append(f"PROMPT:\n{prompt}")
                if messages:
                    payload_parts.append(f"MESSAGES:\n{messages}")
                if system_instruction:
                    payload_parts.append(f"SYSTEM:\n{system_instruction}")
                payload = "\n".join(payload_parts)
                await asyncio.to_thread(_sync_diagnostic_dump, dump_file, f"[MockProvider] {self.model_name}", payload)
            except Exception as e:
                logger.error("Failed to schedule diagnostic dump: %s", e, exc_info=True)
                raise ConfigurationError(
                    message=f"Diagnostic dump dispatch failed: {e}",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                ) from e

    async def _resolve_mock_service_and_pace(self) -> Any:
        """Resolves active settings and MockLLMService class and applies mock pacing delay.

        Returns:
            Instantiated MockLLMService object.
        """
        active_get_settings = get_settings
        active_mock_cls: Any = MockLLMService
        if "backend_v2.llm.provider" in sys.modules:
            provider_mod: Any = sys.modules["backend_v2.llm.provider"]
            if get_settings is _ORIG_GET_SETTINGS and "get_settings" in dir(provider_mod):
                active_get_settings = provider_mod.get_settings
            if MockLLMService is _ORIG_MOCK_LLM_SERVICE:
                active_mock_cls = _safe_static_getattr(provider_mod, "MockLLMService", MockLLMService)

        mock_pacing_delay = active_get_settings().pacing_delay_mock_seconds
        if mock_pacing_delay > 0:
            await asyncio.sleep(mock_pacing_delay)

        return active_mock_cls()

    def _parse_mock_service_result(
        self,
        result: Any,
        prompt: str | None,
    ) -> tuple[str, Any]:
        """Normalizes raw MockLLMService output into serialized JSON text and parsed payload.

        Args:
            result: Raw output returned by MockLLMService.generate_content.
            prompt: Original prompt text for error reporting context.

        Returns:
            Two-tuple of (serialized_content_str, parsed_payload_object).

        Raises:
            ConfigurationError: If the seed vault lacks mock data for the key (ErrorCodes.CONFIGURATION_ERROR).
            AppException: If string result fails JSON parsing (ErrorCodes.AGENT_RESPONSE_PARSING_FAILED).
        """
        if isinstance(result, dict) and "message" in result and result["message"] == "Mock data not found for key":
            prompt_preview = ""
            if prompt:
                prompt_preview = prompt[:100]
            msg = f"Fail-Fast: Mock data not found in Seed Vault. Prompt missing mock definition: {prompt_preview}..."
            logger.error("[MockProvider] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise ConfigurationError(
                message=msg,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        if isinstance(result, dict):
            return json.dumps(result, ensure_ascii=False), result
        if isinstance(result, BaseModel):
            return result.model_dump_json(), result.model_dump()

        content_str = str(result)
        try:
            parsed_result = json.loads(content_str)
        except Exception as parse_err:
            logger.error(
                "[MockProvider] %s: Mock response parsing failed: %s",
                ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.name,
                parse_err,
                exc_info=True,
            )
            raise AppException(
                message=f"Mock response parsing failed: {parse_err}",
                status_code=500,
                details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.value},
            ) from parse_err
        return content_str, parsed_result

    async def _record_simulated_usage(self, kwargs: dict[str, Any]) -> TokenUsage:
        """Tracks simulated token usage via UsageService when configured and returns TokenUsage DTO.

        Args:
            kwargs: Provider keyword arguments containing optional organization_id and user_id overrides.

        Returns:
            Populated TokenUsage domain model with simulated metrics.

        Raises:
            AppException: If usage tracking persistence fails (ErrorCodes.UNKNOWN_ERROR).
        """
        prompt_tokens = 100
        completion_tokens = 50
        total_tokens = 150
        total_cost = 0.002

        if self.usage_service:
            try:
                target_org = self.organization_id
                if "organization_id" in kwargs and kwargs["organization_id"]:
                    target_org = kwargs["organization_id"]
                target_user = "system_agent"
                if "user_id" in kwargs and kwargs["user_id"]:
                    target_user = kwargs["user_id"]
                await self.usage_service.track_usage(
                    org_id=target_org,
                    user_id=target_user,
                    model=self.model_name,
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens,
                    cost_usd=total_cost,
                )
            except Exception as e:
                logger.error("[MockProvider] Usage Tracking Failed: %s", e, exc_info=True)
                raise AppException(
                    message=f"Usage Tracking Failed: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.UNKNOWN_ERROR.value},
                ) from e

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=total_cost,
        )

    @override
    async def generate(
        self,
        prompt: str | None = None,
        system_instruction: str | None = None,
        messages: list[LLMMessageDTO] | list[dict[str, Any]] | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        pass_reasoning_token: str | None = None,
        validation_context: dict[str, Any] | None = None,
        mock_identity: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Simulates generation by invoking the MockLLMService.

        Args:
            prompt: Text to generate from.
            system_instruction: System prompt.
            messages: Fallback conversational state.
            response_schema: Return type constraints.
            temperature: Sampling value.
            max_tokens: Limit.
            top_p: P-sample.
            top_k: K-sample.
            frequency_penalty: Penalty for repeated tokens.
            presence_penalty: Penalty for new topic presence.
            pass_reasoning_token: Blob.
            validation_context: Custom dict.
            mock_identity: Explicit mock fixture identity.
            **kwargs: Extra parameters.

        Returns:
            Mocked success response matching the requested schema.

        Raises:
            ConfigurationError: If mandatory parameters are missing or seed data is not found (ErrorCodes.CONFIGURATION_ERROR).
            AppException: If response parsing or usage tracking fails (ErrorCodes.AGENT_RESPONSE_PARSING_FAILED, ErrorCodes.UNKNOWN_ERROR).
        """
        logger.info("[MockProvider] Calling Mock Service (Simulating Async) for model=%s", self.model_name)

        self._validate_required_sampling_params(temperature=temperature, max_tokens=max_tokens)
        await self._maybe_dump_diagnostics(
            prompt=prompt,
            messages=messages,
            system_instruction=system_instruction,
        )

        mock = await self._resolve_mock_service_and_pace()

        prompt_str = ""
        if prompt:
            prompt_str = prompt
        if messages and not prompt_str:
            prompt_str = json.dumps(
                [m.model_dump(mode="json", exclude_none=True) if isinstance(m, BaseModel) else m for m in messages]
            )

        result = mock.generate_content(
            prompt_str,
            system_instruction,
            agent_identity=mock_identity,
            response_schema=response_schema,
        )

        content_str, parsed_result = self._parse_mock_service_result(result=result, prompt=prompt)
        token_usage = await self._record_simulated_usage(kwargs=kwargs)

        mock_messages: list[LLMMessageDTO] = []
        if system_instruction:
            mock_messages.append(LLMMessageDTO(role="system", content=system_instruction))
        if prompt:
            mock_messages.append(LLMMessageDTO(role="user", content=prompt))
        return LLMResponse(
            content=content_str,
            parsed_content=parsed_result,
            reasoning_token="mock_thought_signature_123456",
            token_usage=token_usage,
            tool_calls=None,
            provider_metadata=ProviderMetadataDTO(),
            messages=mock_messages,
        )
