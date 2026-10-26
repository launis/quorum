"""Abstract LLMProvider base contract, LogfireShieldedClient HTTPX wrapper, and MockProvider."""

import asyncio
import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from typing import Any

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


# Phase 2, Step 1: Relocate abstract LLMProvider contract, LogfireShieldedClient, and MockProvider
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
            LLMResponse: The generated response object.

        Raises:
            AgentExecutionError: On context bounds exceeded.
            AppException: On internal generation errors.
            ConfigurationError: On malformed config.
            SecurityViolationError: On blocked content.
            ServiceUnavailableError: On provider network failure.
        """
        pass


class LogfireShieldedClient:
    """Proxy class to hide httpx.AsyncClient from Logfire's deep serialization hook.

    Prevents 'RuntimeError: dictionary changed size during iteration' when Logfire
    iterates over kwargs containing a shared mutating httpx client.
    """

    __slots__ = ("_client",)

    def __init__(self, client: Any) -> None:
        """Initializes proxy."""
        self._client = client

    def __getattr__(self, name: str) -> Any:
        """Forwards attributes to actual client."""
        return object.__getattribute__(self._client, name)

    async def __aenter__(self) -> Any:
        """Forwards context manager enter to actual client."""
        if "__aenter__" in dir(self._client):
            return await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        """Forwards context manager exit to actual client."""
        if "__aexit__" in dir(self._client):
            return await self._client.__aexit__(exc_type, exc_val, exc_tb)

    def __repr__(self) -> str:
        """Returns safe representation string for Logfire."""
        return "<LogfireShieldedClient protecting httpx.AsyncClient>"


class MockProvider(LLMProvider):
    """Mock LLM Provider for offline testing and development.

    Uses cached/simulated responses from MockLLMService.
    """

    def __init__(
        self,
        model_name: str = "mock",
        usage_service: UsageService | None = None,
        organization_id: str | None = None,
    ) -> None:
        """Initialize the Mock Provider.

        Args:
            model_name: Identifier.
            usage_service: Optional usage tracking.
            organization_id: Identity.

        Raises:
            ConfigurationError: If mock environment is completely misconfigured.
        """
        self.model_name = model_name
        self.usage_service = usage_service
        if organization_id:
            self.organization_id = organization_id
        else:
            self.organization_id = "UNKNOWN_ORG"

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
            LLMResponse: A mocked success response matching the requested schema.

        Raises:
            ConfigurationError: If parameters missing or seed not found.
            AppException: If parsing fails.
        """
        logger.info("[MockProvider] Calling Mock Service (Simulating Async)... %s", kwargs)

        # STRICT CONFIGURATION (Jan 2026): Reject defaults in Mock too.
        if temperature is None:
            msg = "Strict Mode: 'temperature' must be explicitly provided from configuration. No default allowed."
            logger.error("[MockProvider] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise ConfigurationError(message=msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        if max_tokens is None:
            msg = "Strict Mode: 'max_tokens' must be explicitly provided from configuration. No default allowed."
            logger.error("[MockProvider] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise ConfigurationError(message=msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        # --- DIAGNOSTIC DUMP ---
        dump_file = os.getenv("DUMP_PROMPTS_FILE")
        if dump_file:
            try:
                payload_parts = []
                if prompt:
                    payload_parts.append(f"PROMPT:\n{prompt}")
                if messages:
                    payload_parts.append(f"MESSAGES:\n{messages}")
                if system_instruction:
                    payload_parts.append(f"SYSTEM:\n{system_instruction}")
                payload = "\n".join(payload_parts)
                await asyncio.to_thread(_sync_diagnostic_dump, dump_file, f"[MockProvider] {self.model_name}", payload)
            except Exception as e:
                logger.error("Failed to schedule diagnostic dump: %s", e)
                raise ConfigurationError(
                    message=f"Diagnostic dump dispatch failed: {e}",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                ) from e

        active_get_settings = get_settings
        active_mock_cls: Any = MockLLMService
        if "backend_v2.llm.provider" in sys.modules:
            provider_mod: Any = sys.modules["backend_v2.llm.provider"]
            if get_settings is _ORIG_GET_SETTINGS and "get_settings" in dir(provider_mod):
                active_get_settings = provider_mod.get_settings
            if MockLLMService is _ORIG_MOCK_LLM_SERVICE:
                active_mock_cls = _safe_static_getattr(provider_mod, "MockLLMService", MockLLMService)

        # Simulate network delay for verification of async behavior
        mock_pacing_delay = active_get_settings().pacing_delay_mock_seconds
        if mock_pacing_delay > 0:
            await asyncio.sleep(mock_pacing_delay)

        mock = active_mock_cls()

        # Extract explicit identity if provided
        agent_identity = mock_identity

        prompt_str = ""
        if prompt:
            prompt_str = prompt
        if messages and not prompt_str:
            # Fallback to serializing messages if prompt is empty
            prompt_str = json.dumps(
                [m.model_dump(mode="json", exclude_none=True) if isinstance(m, BaseModel) else m for m in messages]
            )

        result = mock.generate_content(
            prompt_str,
            system_instruction,
            agent_identity=agent_identity,
            response_schema=response_schema,
        )

        # Determine content string and parsed object
        content_str = ""
        parsed_result: Any = None

        if isinstance(result, dict) and "message" in result and result["message"] == "Mock data not found for key":
            # STRICT MANDATE: No mock hydration fallbacks. If seed missing, crash properly.
            prompt_preview = ""
            if prompt:
                prompt_preview = prompt[:100]
            raise ConfigurationError(
                message=(
                    f"Fail-Fast: Mock data not found in Seed Vault. Prompt missing mock definition: {prompt_preview}..."
                ),
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        if isinstance(result, dict):
            content_str = json.dumps(result, ensure_ascii=False)
            parsed_result = result
        elif isinstance(result, BaseModel):
            content_str = result.model_dump_json()
            parsed_result = result.model_dump()
        else:
            # Assume it's a string (JSON)
            content_str = str(result)
            try:
                parsed_result = json.loads(content_str)
            except Exception as parse_err:
                raise AppException(
                    message=f"Mock response parsing failed: {parse_err}",
                    status_code=500,
                    details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.value},
                ) from parse_err

        # Simulated Usage
        usage_data = {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150, "total_cost": 0.002}

        # --- COST TRACKING (Mock) ---
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
                    input_tokens=int(usage_data["prompt_tokens"]),
                    output_tokens=int(usage_data["completion_tokens"]),
                    cost_usd=usage_data["total_cost"],
                )
            except Exception as e:
                logger.error("[MockProvider] Usage Tracking Failed: %s", e)
                raise AppException(
                    message=f"Usage Tracking Failed: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.UNKNOWN_ERROR.value},
                ) from e

        mock_messages: list[LLMMessageDTO] = []
        if system_instruction:
            mock_messages.append(LLMMessageDTO(role="system", content=system_instruction))
        if prompt:
            mock_messages.append(LLMMessageDTO(role="user", content=prompt))
        return LLMResponse(
            content=content_str,
            parsed_content=parsed_result,
            reasoning_token="mock_thought_signature_123456",
            token_usage=TokenUsage(
                prompt_tokens=int(usage_data["prompt_tokens"]),
                completion_tokens=int(usage_data["completion_tokens"]),
                total_tokens=int(usage_data["total_tokens"]),
                cost_usd=float(usage_data["total_cost"]),
            ),
            tool_calls=None,
            provider_metadata=ProviderMetadataDTO(),
            messages=mock_messages,
        )
