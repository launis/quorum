"""LLM Provider implementations (LiteLLM, Mock, Unconfigured)."""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

import litellm
import instructor
from litellm import Router
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

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
        # Otherwise fallback to generic defaults.
        generic_defaults = {"tpm": 10000, "rpm": 10}

        tpm = limits.get("tpm", generic_defaults["tpm"]) if limits else generic_defaults["tpm"]
        rpm = limits.get("rpm", generic_defaults["rpm"]) if limits else generic_defaults["rpm"]

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
        
        # Initialize Instructor Client checking compatibility with Router
        # Instructor expects a client-like object or a completion function.
        # We wrap the router's acompletion method.
        # mode=instructor.Mode.MD_JSON is standard for generic models.
        self.client = instructor.from_litellm(self.router.acompletion, mode=instructor.Mode.MD_JSON)

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
            # --- DEBUG LOGGING (Manual request) ---
            def _truncate_for_debug(text: str, label: str) -> None:
                if not text:
                    logger.info(f"[LiteLLM] DEBUG [{label}]: <empty>")
                    return
                
                # Format for log
                header = f"\n{'='*20} DEBUG: {label} {'='*20}"
                footer = f"{'='*50}\n"
                
                if len(text) > 3000:
                    content = f"{text[:1000]}\n\n... [TRUNCATED {len(text)-1500} CHARS] ...\n\n{text[-500:]}"
                else:
                    content = text
                
                # Log as a single block to keep it together
                logger.info(f"{header}\n{content}\n{footer}")

            if system_instruction:
                _truncate_for_debug(system_instruction, "SYSTEM INSTRUCTION")
            _truncate_for_debug(prompt, "USER PROMPT")

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

            # --- DIAGNOSTIC DUMP ---
            dump_file = os.getenv("DUMP_PROMPTS_FILE")
            if dump_file:
                try:
                    with open(dump_file, "a", encoding="utf-8") as f:
                        f.write(f"\n\n--- [LiteLLM] {self.model_name} ---\n")
                        f.write(json.dumps(messages, indent=2, ensure_ascii=False))
                except Exception as e:
                    logger.warning(f"Failed to dump prompt: {e}")

            # --- INSTRUCTOR CALL (Structured) ---
            if response_schema:
                # Use Instructor for Pydantic validation
                # we use 'create' because we wrapped self.router.acompletion in __init__
                # Note: instructor.from_litellm expects the *function* or client.
                # Since we wrapped it, we call client.chat.completions.create
                
                # Instructor might return the Model instance directly, or a tuple/Stream.
                # We expect the Model instance.
                
                # Adjust kwargs for Instructor
                call_kwargs["response_model"] = response_schema
                # Remove fields not needed or handled by Instructor/LiteLLM mixed
                call_kwargs.pop("response_format", None) 
                
                # We need to map 'max_tokens' -> 'max_tokens' (standard)
                
                # EXECUTE
                # Note: usage/cost tracking with Instructor + Router + LiteLLM is tricky.
                # We might need to inspect the raw response if available, or rely on LiteLLM callbacks.
                # For now, let's assume Instructor returns the Pydantic object.
                # BUT we lose the 'reasoning_token' and 'usage' stats if we just get the object.
                # Instructor allows `checks` and returning `(model, completion)`?
                # Let's try to get the raw completion to extract usage/reasoning.
                # from instructor import Response
                
                # Actually, standard Instructor usage:
                # resp = await self.client.chat.completions.create(...)
                # -> returns the Pydantic model.
                
                # To get usage, we might need to rely on LiteLLM's success callbacks or
                # use `response_model=[response_schema]` iterable trick (deprecated?)
                # OR use `instructor.patch()` on a client that returns raw response?
                
                # Let's stick to the simplest path first: Get the object.
                # We might lose Usage stats temporarily (or get them from callback logic in future).
                # For reasoning token, checks provider_specific_fields... strictly, Pydantic model
                # doesn't have it unless we add it to the model.
                
                # CRITICAL: We need 'reasoning_token' for chain-of-thought continuity.
                # If we lose it, we break CoT.
                
                # Strategy:
                # 1. We assume 'response_schema' is the content model.
                # 2. We can ask Instructor to return `(instance, raw_completion)` if configured? 
                #    No, `with_response=True` (in newer versions).
                
                # Let's try basic implementation and see.
                # I will wrap the Pydantic result into our LLMResponse.
                
                logger.info(f"[Instructor] Calling {self.model_name} with schema {response_schema.__name__}")
                
                structured_response = await self.client.chat.completions.create(**call_kwargs)
                
                # Check what we got. If standard usage, it's the Pydantic object.
                parsed_obj = structured_response
                final_content = parsed_obj.model_dump_json()
                
                # Mock usage for now or try to extract from 'structured_response._raw_response'?
                # (Implementation detail dependent).
                # For now, we'll use placeholder usage and reasoning_token for structured calls
                # as Instructor's direct return doesn't easily expose them without deeper integration.
                usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0} 
                reasoning_token = None
                
                return LLMResponse(
                    content=final_content,
                    parsed_content=parsed_obj.model_dump(),
                    reasoning_token=reasoning_token,
                    token_usage=usage,
                    provider_metadata={},
                    tool_calls=[],
                    messages=messages,
                )

            # --- STANDARD CALL (Unstructured) ---
            # Fallback to self.router.acompletion directly if no schema
            # Remove keys that shouldn't be passed directly
            call_kwargs["model"] = self.model_name
            
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

            # Handle Schema Parsing (Validation) - This block is now only for non-Instructor structured output
            # If schema was requested, we return the JSON string in 'content'
            # OR we populate 'tool_calls' if that mechanism was used.
            # For simplicity in this unified response, we ensure 'content' is the stringent result.

            final_content = raw_content
            parsed_obj = None # Initialize parsed_obj for unstructured path
            # The original `if response_schema:` block for regex parsing is removed
            # as Instructor handles structured output.
            # If response_schema was passed, the `if response_schema:` block above would have handled it.
            # This means if we reach here, response_schema was None, and we just return raw_content.

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
                parsed_content=parsed_obj if response_schema else None,
                reasoning_token=reasoning_token,
                token_usage=usage,
                provider_metadata=response.model_dump() if hasattr(response, "model_dump") else {},
                tool_calls=[],
                messages=messages,
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

        # --- DIAGNOSTIC DUMP ---
        dump_file = os.getenv("DUMP_PROMPTS_FILE")
        if dump_file:
            try:
                with open(dump_file, "a", encoding="utf-8") as f:
                    f.write(f"\n\n--- [MockProvider] {self.model_name} ---\n")
                    f.write(f"PROMPT:\n{prompt}\n")
                    if system_instruction:
                        f.write(f"SYSTEM:\n{system_instruction}\n")
            except Exception as e:
                logger.warning(f"Failed to dump prompt: {e}")

        # Simulate network delay for verification of async behavior
        await asyncio.sleep(0.5)

        mock = MockLLMService()

        # Extract explicit identity if provided
        agent_identity = kwargs.get("mock_identity")

        result = mock.generate_content(
            prompt,
            system_instruction,
            agent_identity=agent_identity,
            response_schema=response_schema,
        )

        # Determine content string and parsed object
        content_str = ""
        parsed_result = None

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
            except Exception:
                # If it's not JSON, it's just text
                parsed_result = None

        # Simulated Usage

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
                    input_tokens=int(usage_data["prompt_tokens"]),
                    output_tokens=int(usage_data["completion_tokens"]),
                    cost_usd=usage_data["total_cost"],
                )
            except Exception as e:
                logger.warning(f"[MockProvider] Usage Tracking Failed: {e}")

        return LLMResponse(
            content=content_str,
            parsed_content=parsed_result,
            reasoning_token="mock_thought_signature_123456",
            token_usage=usage_data,
            tool_calls=[],
            provider_metadata={},
            messages=[
                {"role": "system", "content": system_instruction} if system_instruction else {},
                {"role": "user", "content": prompt}
            ],
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

        # STRICT EXECUTION AUTHORITY (Jan 19 Update):
        # GLOBAL SAFETY: If 'settings.use_mock_llm' is True, we FORCE the MockProvider.
        # This guarantees that 'run_mock.bat' implies 100% offline mode, regardless of
        # what provider specific agents request (e.g. 'vertex_ai').
        if settings.use_mock_llm:
            logger.warning(f"[LLMFactory] Global USE_MOCK_LLM=True. Overriding request for '{provider_type}' -> MockProvider.")
            return MockProvider(
                model_name=model_name or "mock",
                usage_service=usage_service,
                organization_id=organization_id,
            )

        # STRICT CONFIGURATION:
        # If not in global mock mode, we DO NOT allow 'mock' to be implicitly selected
        # unless explicitly requested. If 'vertex_ai' is requested, we get Vertex (or fail).
        if provider_type == "mock":
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
