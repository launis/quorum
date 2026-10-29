"""Mock cache adapter for testing and verification.

This module implements network-free testing utilities matching the 2026 Enterprise core standard.
"""

from __future__ import annotations

import logging
from typing import Any, override

from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.llm import CachingPayloadResultDTO
from backend_v2.models.prompt import CompiledPrompt

logger = logging.getLogger(__name__)

__all__ = ["MockCacheAdapter"]


class MockCacheAdapter(BaseLLMAdapter):
    """Mock LLM cache adapter for network-free testing and verification.

    Conforms to structural protocols without making downstream API calls.
    """

    @override
    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> CachingPayloadResultDTO:
        """Return the flat compiled prompt messages as-is and set mock active flag.

        Args:
            compiled_prompt: The structured CompiledPrompt instance.
            model_name: The target model name.

        Returns:
            A CachingPayloadResultDTO with flat messages and 'mock_cache_active' enabled.

        Raises:
            AppException: VALIDATION_FAILED if model_name is empty or whitespace.
        """
        if not model_name or not model_name.strip():
            logger.error(
                "[MockCacheAdapter] %s: Target model_name cannot be empty.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="Target model_name cannot be empty for Mock cache payload preparation.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        flat_messages = compiled_prompt.to_flat_messages()
        return CachingPayloadResultDTO(messages=flat_messages, kwargs={"mock_cache_active": True})

    @override
    async def teardown_cache(self, workflow_run_id: str) -> None:
        """Validate workflow_run_id and perform a network-free cache teardown.

        Args:
            workflow_run_id: The ID of the workflow run to tear down.

        Returns:
            None.

        Raises:
            AppException: VALIDATION_FAILED if workflow_run_id is empty or whitespace.
        """
        if not workflow_run_id or not workflow_run_id.strip():
            logger.error(
                "[MockCacheAdapter] %s: workflow_run_id cannot be empty during cache teardown.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="workflow_run_id cannot be empty for Mock cache teardown.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

    @override
    def calculate_cost(self, usage: TokenUsage, pricing_config: PricingConfig) -> TokenUsage:
        """Return TokenUsage with estimated_savings_usd set to 0.05.

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider-specific pricing parameters.

        Returns:
            An instance of TokenUsage containing the calculated costs.
        """
        return usage.model_copy(update={"estimated_savings_usd": 0.05})

    @override
    def prepare_provider_kwargs(self, model_name: str) -> dict[str, Any]:
        """Prepare provider specific arguments for LiteLLM.

        Args:
            model_name: The target model name.

        Returns:
            An empty dictionary as no special static arguments are needed.

        Raises:
            AppException: VALIDATION_FAILED if model_name is empty or whitespace.
        """
        if not model_name or not model_name.strip():
            logger.error(
                "[MockCacheAdapter] %s: Target model_name cannot be empty.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="Target model_name cannot be empty for Mock provider kwargs.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return {}

    @override
    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Convert the Pydantic response model into strict JSON schema format for the Mock provider.

        Args:
            response_model: The Pydantic model defining the expected JSON structure.

        Returns:
            The formatted strict JSON schema dictionary with unsupported constraints stripped.

        Raises:
            AppException: VALIDATION_FAILED if response_model is not a Pydantic BaseModel subclass.
        """
        if not isinstance(response_model, type) or not issubclass(response_model, BaseModel):
            logger.error(
                "[MockCacheAdapter] %s: response_model must be a Pydantic BaseModel subclass.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="response_model must be a Pydantic BaseModel subclass for Mock structured output.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        json_schema = response_model.model_json_schema()
        self._strip_unsupported_constraints(json_schema)
        return {
            "type": "json_schema",
            "json_schema": {
                "name": response_model.__name__,
                "schema": json_schema,
                "strict": True,
            },
        }
