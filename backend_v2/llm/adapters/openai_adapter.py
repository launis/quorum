"""OpenAI cache adapter with automatic prefix caching payload preparation and FinOps cost calculation."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.prompt import CompiledPrompt

logger = logging.getLogger(__name__)


class OpenAITokenUsage(TokenUsage):
    """Subclass of TokenUsage supporting OpenAI-specific caching telemetry and savings.

    Attributes:
        estimated_savings_usd: FinOps ROI estimated savings in USD.
    """

    estimated_savings_usd: float = Field(default=0.0, description="FinOps ROI estimated savings in USD.")

    @field_validator("estimated_savings_usd")
    @classmethod
    def validate_savings_ge_zero(cls, v: float) -> float:
        """Verify estimated savings are non-negative to bypass Vertex serving limitations.

        Args:
            v: The float value containing computed savings.

        Returns:
            The validated non-negative float.

        Raises:
            ValueError: Raised if the parsed savings are negative.
        """
        if v < 0.0:
            raise ValueError("estimated_savings_usd must be greater than or equal to 0.0")
        return v


class OpenAICacheAdapter(BaseLLMAdapter):
    """Caching and pricing adapter for OpenAI models."""

    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Prepare the OpenAI-specific prompt payload.

        OpenAI recognizes caching automatically by prefix matching. We simply flatten
        the messages and return empty extra keyword arguments.

        Args:
            compiled_prompt: The structured CompiledPrompt instance.
            model_name: The target model name.

        Returns:
            A tuple containing:
                - The flattened list of messages.
                - An empty extra kwargs dictionary.
        """
        flat_messages = compiled_prompt.to_flat_messages()
        return flat_messages, {}

    async def teardown_cache(self, workflow_run_id: str) -> None:
        """No-Op teardown for OpenAI.

        Args:
            workflow_run_id: The execution tracking workflow identifier.
        """
        pass

    def calculate_cost(self, usage: TokenUsage, pricing_config: dict[str, Any]) -> TokenUsage:
        """Calculate the precise OpenAI cost and savings.

        Formula:
            Cost = (regular_input_tokens * P_in) + (cached_tokens * P_in * discount_factor) + (output_tokens * P_out)
            Savings = cached_tokens * P_in * savings_factor

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider pricing parameters.

        Returns:
            An instance of OpenAITokenUsage with calculated values.

        Raises:
            AppException: Triggered if standard pricing elements are missing.
        """
        if "input_token_price" not in pricing_config or "output_token_price" not in pricing_config:
            logger.error(
                "Invalid pricing configuration: missing input_token_price or output_token_price", exc_info=True
            )
            raise AppException(
                message="Invalid pricing configuration: missing input_token_price or output_token_price",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        p_in = float(pricing_config["input_token_price"])
        p_out = float(pricing_config["output_token_price"])

        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        cached_tokens = usage.cached_tokens
        reasoning_tokens = usage.reasoning_tokens

        # Strict fetch for model identifier adhering to zero service layer fallback design rules
        model_name = pricing_config.get("model_name") or pricing_config.get("model", "")

        is_deepseek = "deepseek" in str(model_name).lower()

        # DeepSeek has 90% read discount, OpenAI has 50% read discount
        discount_factor = 0.10 if is_deepseek else 0.50
        savings_factor = 0.90 if is_deepseek else 0.50

        regular_input = max(0, prompt_tokens - cached_tokens)

        # Compute cost and savings
        cost_regular = regular_input * p_in
        cost_cached = cached_tokens * p_in * discount_factor
        cost_output = completion_tokens * p_out

        cost_usd = cost_regular + cost_cached + cost_output
        estimated_savings_usd = cached_tokens * p_in * savings_factor
        total_tokens = usage.total_tokens

        return OpenAITokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
            cost_usd=cost_usd,
            estimated_savings_usd=estimated_savings_usd,
        )

    def prepare_provider_kwargs(self, model_name: str) -> dict[str, Any]:
        """Prepare provider specific arguments for LiteLLM.

        Args:
            model_name: The target model name.

        Returns:
            An empty dictionary as no special static arguments are needed.
        """
        return {}

    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Convert a Pydantic model into OpenAI specific strict structured output format.

        OpenAI strict structured outputs (JSON Schema mode) require strict=True and
        stripped constraints.

        Args:
            response_model: The Pydantic model defining the expected JSON structure.

        Returns:
            A dictionary matching LiteLLM's structured output format.
        """
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
