"""OpenAI cache adapter with automatic prefix caching payload preparation and FinOps cost calculation."""

from __future__ import annotations

import logging
from typing import Any, Final, override

from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.system_config import ModelProfile
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.llm import CachingPayloadResultDTO, LLMProviderConfig
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.settings import Settings

logger = logging.getLogger(__name__)

__all__ = ["OpenAICacheAdapter"]

_DEFAULT_CACHE_READ_DISCOUNT: Final[float] = 0.50
_LOW_REASONING_BUDGET_THRESHOLD: Final[int] = 2048
_MEDIUM_REASONING_BUDGET_THRESHOLD: Final[int] = 4096


class OpenAICacheAdapter(BaseLLMAdapter):
    """Caching and pricing adapter for OpenAI models."""

    @override
    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> CachingPayloadResultDTO:
        """Prepare the OpenAI-specific prompt payload.

        OpenAI recognizes caching automatically by prefix matching. We simply flatten
        the messages and return empty extra keyword arguments.

        Args:
            compiled_prompt: The structured CompiledPrompt instance.
            model_name: The target model name.

        Returns:
            A CachingPayloadResultDTO containing flat messages and empty kwargs.

        Raises:
            AppException: VALIDATION_FAILED if model_name is empty or whitespace.
        """
        if not model_name or not model_name.strip():
            logger.error(
                "[OpenAICacheAdapter] %s: Target model_name cannot be empty.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="Target model_name cannot be empty for OpenAI cache payload preparation.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        flat_messages = compiled_prompt.to_flat_messages()
        return CachingPayloadResultDTO(messages=flat_messages, kwargs={})

    @override
    async def teardown_cache(self, workflow_run_id: str) -> None:
        """Validate workflow_run_id and execute passive cache teardown for OpenAI.

        Args:
            workflow_run_id: The execution tracking workflow identifier.

        Raises:
            AppException: VALIDATION_FAILED if workflow_run_id is empty or whitespace.
        """
        if not workflow_run_id or not workflow_run_id.strip():
            logger.error(
                "[OpenAICacheAdapter] %s: workflow_run_id cannot be empty during cache teardown.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="workflow_run_id cannot be empty for OpenAI cache teardown.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

    @override
    def calculate_cost(self, usage: TokenUsage, pricing_config: PricingConfig) -> TokenUsage:
        """Calculate the precise OpenAI cost and savings.

        Formula:
            Cost = (regular_input_tokens * P_in) + (cached_tokens * P_cached) + (output_tokens * P_out)
            Savings = cached_tokens * max(0.0, P_in - P_cached)

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider pricing parameters.

        Returns:
            An instance of TokenUsage with calculated values.
        """
        p_in = pricing_config.input_token_price
        p_out = pricing_config.output_token_price
        p_cached = (
            pricing_config.cached_input_token_price
            if pricing_config.cached_input_token_price is not None
            else p_in * _DEFAULT_CACHE_READ_DISCOUNT
        )

        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        cached_tokens = usage.cached_tokens
        reasoning_tokens = usage.reasoning_tokens

        regular_input = max(0, prompt_tokens - cached_tokens)

        # Compute cost and savings
        cost_regular = regular_input * p_in
        cost_cached = cached_tokens * p_cached
        cost_output = completion_tokens * p_out

        cost_usd = cost_regular + cost_cached + cost_output
        estimated_savings_usd = cached_tokens * max(0.0, p_in - p_cached)

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=usage.total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
            cache_creation_input_tokens=usage.cache_creation_input_tokens,
            cost_usd=cost_usd,
            estimated_savings_usd=estimated_savings_usd,
        )

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
                "[OpenAICacheAdapter] %s: Target model_name cannot be empty.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="Target model_name cannot be empty for OpenAI provider kwargs.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return {}

    @override
    def prepare_kwargs(
        self,
        call_kwargs: dict[str, Any],
        config: LLMProviderConfig | ModelProfile | None = None,
        settings: Settings | None = None,
    ) -> dict[str, Any]:
        """Prepare OpenAI specific kwargs, translating reasoning effort and stripping unsupported sampling params.

        Args:
            call_kwargs: The dictionary of arguments to pass to litellm.
            config: Optional config object for the provider.
            settings: Optional app settings.

        Returns:
            The potentially modified call_kwargs dictionary.
        """
        super().prepare_kwargs(call_kwargs, config=config, settings=settings)

        resolved_model: str = ""
        if "model" in call_kwargs and call_kwargs["model"]:
            resolved_model = str(call_kwargs["model"])
        elif isinstance(config, LLMProviderConfig | ModelProfile):
            resolved_model = config.model_name
        model_name = resolved_model.lower()

        thinking_budget: int | None = None
        if isinstance(config, ModelProfile) and config.thinking_budget_tokens is not None:
            thinking_budget = int(config.thinking_budget_tokens)

        # Epistemic SSOT: Query authoritative LiteLLM registry dynamically instead of hardcoded prefix guessing
        is_reasoning_model = False
        try:
            import litellm

            clean_model = model_name.removeprefix("openai/")
            info = litellm.get_model_info(clean_model)
            raw_params = None
            if "supported_openai_params" in info:
                raw_params = info["supported_openai_params"]
            supported_params: list[str] = []
            if isinstance(raw_params, list):
                supported_params = [str(param) for param in raw_params if isinstance(param, str)]
            has_reasoning = "supports_reasoning" in info and bool(info["supports_reasoning"])
            if has_reasoning or "reasoning_effort" in supported_params:
                is_reasoning_model = True
        except Exception as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            # For unindexed models, rely strictly on Studio-configured thinking_budget_tokens contract
            is_reasoning_model = thinking_budget is not None and thinking_budget > 0

        if is_reasoning_model:
            # Map thinking budget tokens to reasoning effort
            if thinking_budget is not None and thinking_budget == 0:
                # Explicit zero thinking budget: allow temperature, suppress reasoning_effort
                if "reasoning_effort" in call_kwargs:
                    del call_kwargs["reasoning_effort"]
            elif settings is not None and settings.environment == "development":
                call_kwargs["reasoning_effort"] = "low"
            elif thinking_budget is not None and thinking_budget > 0:
                if thinking_budget <= _LOW_REASONING_BUDGET_THRESHOLD:
                    call_kwargs["reasoning_effort"] = "low"
                elif thinking_budget <= _MEDIUM_REASONING_BUDGET_THRESHOLD:
                    call_kwargs["reasoning_effort"] = "medium"
                else:
                    call_kwargs["reasoning_effort"] = "high"

            # Strip sampling parameters that OpenAI reasoning models reject (400 Bad Request)
            if "reasoning_effort" in call_kwargs:
                for param in ("temperature", "top_p", "frequency_penalty", "presence_penalty"):
                    if param in call_kwargs:
                        del call_kwargs[param]

        return call_kwargs

    def _enforce_openai_strict_schema(
        self,
        schema_dict: dict[str, Any],
        known_discriminators: set[str] | None = None,
    ) -> None:
        """Enforce strict OpenAI JSON schema requirements across root and nested definitions.

        Args:
            schema_dict: The root or nested JSON schema dictionary to transform.
            known_discriminators: Optional set of discriminator property names.
        """
        if known_discriminators is None:
            known_discriminators = set()
            self._collect_discriminator_names(schema_dict, known_discriminators)

        self._strip_unsupported_constraints(schema_dict, known_discriminators=known_discriminators)
        self._apply_strict_schema_invariants(schema_dict)

    def _apply_strict_schema_invariants(self, node: Any) -> None:
        """Recursively enforce OpenAI strict invariants including anyOf conversion and discriminator removal.

        Mutates schema in-place to enforce additionalProperties=False, saturate required lists,
        strip default values, convert oneOf unions to anyOf, and remove unsupported discriminator objects.

        Args:
            node: Node within the JSON schema graph to inspect and mutate in-place.
        """
        if type(node) is dict:
            if "default" in node:
                del node["default"]
            if "discriminator" in node:
                del node["discriminator"]
            if "oneOf" in node:
                node["anyOf"] = node["oneOf"]
                del node["oneOf"]

            node_type = None
            if "type" in node:
                node_type = node["type"]
            if node_type == "object" or "properties" in node:
                node["additionalProperties"] = False
                if "properties" in node:
                    properties = node["properties"]
                    if type(properties) is dict:
                        if "required" not in node or not isinstance(node["required"], list):
                            node["required"] = []
                        for prop_name in properties:
                            if prop_name not in node["required"]:
                                node["required"].append(prop_name)

            for v in list(node.values()):
                self._apply_strict_schema_invariants(v)
        elif isinstance(node, list):
            for item in node:
                self._apply_strict_schema_invariants(item)

    @override
    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Convert a Pydantic model into OpenAI specific strict structured output format.

        OpenAI strict structured outputs (JSON Schema mode) require strict=True,
        additionalProperties=False, saturated required lists, and stripped constraints.

        Args:
            response_model: The Pydantic model defining the expected JSON structure.

        Returns:
            A dictionary matching LiteLLM's structured output format.

        Raises:
            AppException: VALIDATION_FAILED if response_model is not a Pydantic BaseModel subclass.
        """
        if not isinstance(response_model, type) or not issubclass(response_model, BaseModel):
            logger.error(
                "[OpenAICacheAdapter] %s: response_model must be a Pydantic BaseModel subclass.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="response_model must be a Pydantic BaseModel subclass for OpenAI structured output.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        json_schema = response_model.model_json_schema()
        self._enforce_openai_strict_schema(json_schema)

        return {
            "type": "json_schema",
            "json_schema": {
                "name": response_model.__name__,
                "schema": json_schema,
                "strict": True,
            },
        }
