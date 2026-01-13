"""LLM Provider implementations (LiteLLM, Mock, Unconfigured)."""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

import litellm
from litellm import Router
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.llm.config import MODEL_LIMITS
from backend.models.llm import LLMResponse
from backend.services.usage_service import UsageService
from backend.settings import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Define retry strategy
_settings = get_settings()

retry_strategy = retry(
    stop=stop_after_attempt(_settings.llm_max_retries),
    wait=wait_exponential(multiplier=_settings.llm_retry_delay, min=1, max=60),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"Retrying LLM call... (Attempt {retry_state.attempt_number}/{_settings.llm_max_retries})"
    ),
)


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Defines the contract for text generation and structured data extraction.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        pass_reasoning_token: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """Generates content from the LLM.

        Args:
        prompt (str): The user prompt.
        system_instruction (str | None): System prompt/context.
        response_schema (type[BaseModel] | dict[str, Any] | None): Pydantic model or JSON Schema.
        temperature (float): Sampling temperature.
        max_tokens (int | None): Max tokens to generate.
        pass_reasoning_token (str | None): Encrypted state blob from previous turn.
        **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse: The generated response object.

        """
        pass


class LiteLLMProvider(LLMProvider):
    """Unified LLM Provider using LiteLLM to support multiple models (Gemini, OpenAI, etc.).

    Provides a consistent interface.
    """

    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        settings: Any = None,
        usage_service: UsageService | None = None,
        organization_id: str | None = None,
        limits: dict[str, int] | None = None,
    ):
        """Initializes the LiteLLM provider.

        Args:
            model_name (str): The model identifier.
            api_key (Optional[str]): API Key.
            settings (Any): System settings object.
            usage_service (Optional[UsageService]): Service for cost tracking.
            organization_id (Optional[str]): Context organization ID.
            limits (Optional[dict]): Override TPM/RPM limits (e.g. from Organization).
        """
        self.model_name = model_name
        self.api_key = api_key
        self.settings = settings
        self.usage_service = usage_service
        self.organization_id = organization_id or "UNKNOWN_ORG"

        # litellm general config
        litellm.drop_params = True

        # --- Configure Router for Rate Limiting ---
        # We construct a single-item model list for this provider instance
        # to leverage Router's TPM/RPM enforcement logic.

        # 1. Determine Limits
        # If dynamic limits are provided (e.g. per Organization), use them.
        # Otherwise fallback to static MODEL_LIMITS.
        static_defaults = MODEL_LIMITS.get(model_name, {"tpm": 10000, "rpm": 10})

        tpm = limits.get("tpm", static_defaults["tpm"]) if limits else static_defaults["tpm"]
        rpm = limits.get("rpm", static_defaults["rpm"]) if limits else static_defaults["rpm"]

        # 2. Build deployment config
        model_config = {
            "model_name": model_name,  # The alias we use
            "litellm_params": {
                "model": model_name,  # The actual provider model name
                "api_key": api_key,
                "tpm": tpm,
                "rpm": rpm,
            },
        }

        # 3. Initialize Router
        # set_verbose=False to reduce noise, unless debugging
        self.router = Router(
            model_list=[model_config],
            set_verbose=False,
        )

    @retry_strategy
    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        pass_reasoning_token: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """Generates content using LiteLLM.

        Returns unified LLMResponse with content and reasoning state.
        """
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        # Context Continuity (Stateless Reasoning Blob)
        if pass_reasoning_token:
            # Abstraction: We pass it as a developer hint for now.
            # Real implementation would use provider-specific params in `litellm.acompletion`
            messages.append(
                {
                    "role": "system",
                    "content": f"[SYSTEM: RESUME_THOUGHT_PROCESS] PREVIOUS_STATE_BLOB: {pass_reasoning_token}",
                }
            )

        messages.append({"role": "user", "content": prompt})

        response_format = None
        if response_schema:
            try:
                schema_name = getattr(response_schema, "__name__", "dict")
                logger.info(f"[LiteLLM] Enabling Structured Output for schema: {schema_name}")
                response_format = response_schema
            except Exception:
                pass

        try:
            logger.info(f"[LiteLLM] Calling {self.model_name}...")

            # Prepare arguments
            call_kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_format": response_format,
                "api_key": self.api_key,
                "drop_params": True,
            }

            # Explicitly force Vertex Location (Fixes 403 default-to-us-central1 issue)
            # Robustly resolve location (Settings attr or Env Var)

            # Ensure env is loaded from project root
            from pathlib import Path

            from dotenv import load_dotenv

            # provider.py is at backend/llm/provider.py
            # Go up 3 levels to reach project root
            root_dir = Path(__file__).resolve().parent.parent.parent
            env_path = root_dir / ".env"

            load_dotenv(dotenv_path=env_path)

            v_loc = None
            if self.settings and hasattr(self.settings, "vertex_location"):
                v_loc = self.settings.vertex_location

            if not v_loc:
                v_loc = os.getenv("VERTEX_LOCATION")

            # STRICT MODE: No defaults. Fail if missing.
            if not v_loc:
                logger.error(f"[LiteLLMProvider] Env load failed. Tried path: {env_path}, Exists: {env_path.exists()}")
                raise ValueError(
                    f"[LiteLLMProvider] Critical Error: VERTEX_LOCATION not found in settings or .env ({env_path}). "
                    "Cannot proceed."
                )

            logger.info(f"[LiteLLMProvider] Using Vertex Location: {v_loc}")
            call_kwargs["vertex_location"] = v_loc

            # --- ROUTER CALL ---
            # Remove keys that shouldn't be passed directly to router.acompletion
            # if they are already in deployment config (like api_key),
            # BUT Router overrides usually merge.
            # However, 'model' arg in kwargs MUST match the 'model_name' alias in model_list.
            call_kwargs["model"] = self.model_name

            # Using router.acompletion instead of litellm.acompletion
            # mypy: Router.acompletion signature is complex, ignore overlap
            response = await self.router.acompletion(**call_kwargs)  # type: ignore[call-overload]

            # Extract basic content
            choice = response.choices[0]
            message = choice.message
            raw_content = message.content or ""

            # Extract Reasoning Token (Gemini 3 / GPT-5.1)
            reasoning_token = None

            # Check standard LiteLLM extra fields
            if hasattr(message, "provider_specific_fields") and message.provider_specific_fields:
                reasoning_token = message.provider_specific_fields.get(
                    "thought_signature"
                ) or message.provider_specific_fields.get("reasoning_blob")

            # Fallback: Check top level attributes
            if not reasoning_token and hasattr(response, "model_extra"):
                reasoning_token = response.model_extra.get("thought_signature")

            # Extract Usage
            usage = {}
            if hasattr(response, "usage"):
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            # Handle Schema Parsing (Validation)
            # If schema was requested, we return the JSON string in 'content'
            # OR we populate 'tool_calls' if that mechanism was used.
            # For simplicity in this unified response, we ensure 'content' is the stringent result.

            final_content = raw_content
            if response_schema:
                if hasattr(message, "parsed") and message.parsed:
                    # If LiteLLM parsed it, dump back to JSON string for consistency
                    obj = message.parsed.dict() if hasattr(message.parsed, "dict") else message.parsed
                    final_content = json.dumps(obj, ensure_ascii=False)
                else:
                    # STRICT MODE: Fail Fast if not valid JSON
                    try:
                        # Attempt standard parsing
                        # Note: Some models return Markdown ```json ... ``` even with strict mode
                        # We do minimal stripping of code blocks only, no heuristic repair.
                        clean_text = raw_content
                        if "```" in raw_content:
                            clean_text = raw_content.replace("```json", "").replace("```", "").strip()

                        obj = json.loads(clean_text)
                        final_content = json.dumps(obj, ensure_ascii=False)
                    except json.JSONDecodeError as e:
                        logger.error(f"[LiteLLM] Strict JSON Parse Failed: {e}")
                        raise ValueError("Strict JSON parsing failed.") from e

            # --- COST TRACKING ---
            cost = 0.0
            if self.usage_service:
                try:
                    # Calculate cost using LiteLLM
                    cost = litellm.completion_cost(completion_response=response)

                    # Track usage asynchronously (fire and forget for now, or await)
                    # For strict async correctness, we await it.
                    await self.usage_service.track_usage(
                        org_id=self.organization_id,
                        user_id=kwargs.get("user_id", "system_agent"),
                        model=self.model_name,
                        input_tokens=int(usage.get("prompt_tokens", 0)),
                        output_tokens=int(usage.get("completion_tokens", 0)),
                        cost_usd=cost,
                    )
                except Exception as e:
                    logger.warning(f"[LiteLLMProvider] Usage Tracking Failed: {e}")

            # Inject cost into usage dict so BaseAgent can pick it up
            usage["total_cost"] = cost

            return LLMResponse(
                content=final_content,
                reasoning_token=reasoning_token,
                token_usage=usage,
                provider_metadata=response.model_dump() if hasattr(response, "model_dump") else {},
                tool_calls=[],
            )

        except Exception as e:
            logger.error(f"[LiteLLM] Error: {e}", exc_info=True)
            raise e


class MockProvider(LLMProvider):
    """Mock LLM Provider for offline testing and development.

    Uses cached/simulated responses from MockLLMService.
    """

    def __init__(
        self,
        model_name: str = "mock",
        usage_service: UsageService | None = None,
        organization_id: str | None = None,
    ):
        """Initialize the Mock Provider."""
        self.model_name = model_name
        self.usage_service = usage_service
        self.organization_id = organization_id or "UNKNOWN_ORG"

    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        pass_reasoning_token: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """Simulates generation by invoking the MockLLMService."""
        from backend.llm.mock import MockLLMService

        logger.info(f"[MockProvider] Calling Mock Service (Simulating Async)... {kwargs}")

        # Simulate network delay for verification of async behavior
        await asyncio.sleep(0.5)

        mock = MockLLMService()

        # Extract explicit identity if provided
        agent_identity = kwargs.get("mock_identity")

        result = mock.generate_content(prompt, system_instruction, agent_identity=agent_identity)

        # Determine content string
        content_str = ""
        if isinstance(result, dict):
            content_str = json.dumps(result, ensure_ascii=False)
        else:
            content_str = str(result)

        # Simulated Usage
        usage_data = {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
            "total_cost": 0.002,
        }

        # --- COST TRACKING (Mock) ---
        if self.usage_service:
            try:
                await self.usage_service.track_usage(
                    org_id=self.organization_id,
                    user_id=kwargs.get("user_id", "system_agent"),
                    model=self.model_name,
                    input_tokens=usage_data["prompt_tokens"],
                    output_tokens=usage_data["completion_tokens"],
                    cost_usd=usage_data["total_cost"],
                )
            except Exception as e:
                logger.warning(f"[MockProvider] Usage Tracking Failed: {e}")

        return LLMResponse(
            content=content_str,
            reasoning_token="mock_thought_signature_123456",
            token_usage=usage_data,
            tool_calls=[],
            provider_metadata={},
        )


class LLMFactory:
    """Factory class to instantiate the appropriate LLMProvider based on configuration."""

    @staticmethod
    def create_provider(
        provider_type: str,
        model_name: str,
        context: dict[str, Any] | Any | None = None,
        organization_id: str | None = None,
        usage_service: UsageService | None = None,
        limits: dict[str, int] | None = None,
    ) -> LLMProvider:
        """Factory method to create an LLM Provider instance.

        Args:
            provider_type (str): Type key (e.g. 'litellm', 'mock').
            model_name (str): Model identifier.
            context (Optional[dict]): Additional context or settings.
            organization_id (Optional[str]): Organization ID for tracking.
            usage_service (Optional[UsageService]): Usage service instance.
            limits (Optional[dict]): Usage limits (tpm, rpm).

        Returns:
            LLMProvider: Configured provider instance.
        """
        settings = get_settings()

        # Placeholder for BYOK (Bring Your Own Key) Logic
        tenant_api_key = None

        if provider_type == "mock" or settings.use_mock_llm:
            return MockProvider(
                model_name=model_name or "mock",
                usage_service=usage_service,
                organization_id=organization_id,
            )

        # STRICT CONFIGURATION: If no model provided, Raise Error.
        if not model_name:
            raise ValueError("Model name is required for LLMProvider creation.")

        api_key = None
        if provider_type == "litellm":
            if "gemini" in model_name:
                api_key = tenant_api_key or settings.google_api_key
            elif "gpt" in model_name or "o1" in model_name:
                api_key = tenant_api_key or settings.openai_api_key
            elif "claude" in model_name:
                api_key = tenant_api_key or settings.anthropic_api_key

            return LiteLLMProvider(
                model_name=model_name,
                api_key=api_key,
                settings=settings,
                usage_service=usage_service,
                organization_id=organization_id,
                limits=limits,
            )

        # Fallback for explicit strategies (legacy)
        match provider_type.lower():
            case "gemini" | "vertex_ai":
                api_key = tenant_api_key or settings.google_api_key
            case "openai":
                api_key = tenant_api_key or settings.openai_api_key
                if not api_key:
                    import os

                    api_key = os.getenv("OPENAI_API_KEY")
            case _:
                pass

        return LiteLLMProvider(
            model_name=model_name,
            api_key=api_key,
            settings=settings,
            usage_service=usage_service,
            organization_id=organization_id,
            limits=limits,
        )
