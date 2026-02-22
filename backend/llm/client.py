import json
import logging
from typing import Any, TypeVar

from pydantic import BaseModel

from backend.exceptions import AgentExecutionError
from backend.llm.provider import LLMFactory

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class LLMClient:
    """Singleton LLM Client wrapper adapting LLMFactory for structured outputs.

    Replaces legacy Instructor/OpenAI implementation with unified V2.9 LLMProvider.
    """

    _instance = None

    def __new__(cls) -> LLMClient:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the client."""
        # No heavy initialization needed for Factory pattern
        pass

    async def run_structured_task(
        self,
        messages: list[dict[str, Any]],
        response_model: type[T],
        model: str,  # STRICT: Model must be provided (Zero-Fallback)
        **kwargs: Any,
    ) -> T:
        """Execute a structured LLM task enforcing a Pydantic schema using LLMProvider.

        Args:
            messages: List of chat messages (system, user, etc.)
            response_model: The Pydantic model class to valid output against.
            model: The specific model to use (MUST be provided).
            **kwargs: Additional arguments for the completion call.

        Returns:
            The validated Pydantic model instance.
        """
        # 1. Parse Messages to prompt/system inputs expected by LLMProvider.generate
        # Note: LLMProvider interface currently takes (prompt, system_instruction).
        # We flatten the chat history here. For multi-turn support, LLMProvider needs update.
        system_instruction = None
        prompt = ""

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                if system_instruction:
                    system_instruction += "\n\n" + content
                else:
                    system_instruction = content
            elif role == "user":
                if prompt:
                    prompt += "\n\n" + content
                else:
                    prompt = content
            # Flattening assistant/other roles into prompt if necessary,
            # but currently specific Tasks use only S+U.

        if not prompt:
            # Fallback if no user message found (rare)
            prompt = messages[-1]["content"] if messages else ""

        # 2. Create Provider via Factory
        # This handles provider resolution (Vertex vs OpenAI) based on model name
        provider = LLMFactory.create_provider(provider_type="litellm", model_name=model)

        try:
            # 3. Generate with Structured Output
            response = await provider.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                response_schema=response_model,
                temperature=kwargs.get("temperature"),
                max_tokens=kwargs.get("max_tokens"),
            )

            # 4. Parse Result
            # response.content is a JSON string (ensured by LiteLLMProvider)
            data = json.loads(response.content)
            return response_model.model_validate(data)

        except Exception as e:
            logger.error(f"[LLMClient] Execution Failed for model {model}: {e}")
            if "response" in locals() and response:
                logger.error(f"[LLMClient] Raw content causing error: {response.content}")
            raise AgentExecutionError(f"Structured Task Failed: {e}") from e

    async def run_chat(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a free-form chat task returning a string.

        Args:
            messages: List of chat messages.
            model: Model identifier. MUST be provided (Zero-Fallback).
            **kwargs: Additional args (temperature, max_tokens).

        Returns:
            The generated text content.
        """
        # ZERO-FALLBACK ENFORCEMENT
        if not model:
            from backend.exceptions import AppException, ErrorCodes, status

            raise AppException(
                message="Model Configuration Missing: 'model' argument is required for run_chat.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )

        # 1. Parse Prompt (Flattening)
        # Similar logic to run_structured_task
        system_instruction = None
        prompt = ""

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                system_instruction = (system_instruction + "\n\n" + content) if system_instruction else content
            elif role == "user":
                prompt = (prompt + "\n\n" + content) if prompt else content

        if not prompt:
            prompt = messages[-1]["content"] if messages else ""

        # 2. Create Provider
        provider = LLMFactory.create_provider(provider_type="litellm", model_name=model)

        # 3. Generate
        try:
            response = await provider.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=kwargs.get("temperature"),
                max_tokens=kwargs.get("max_tokens"),
                **kwargs,
            )
            return response.content
        except Exception as e:
            logger.error(f"[LLMClient] Chat Execution Failed: {e}")
            raise AgentExecutionError(f"Chat Task Failed: {e}") from e
