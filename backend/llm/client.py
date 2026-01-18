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
        model: str,  # STRICT: Model must be provided (No defaults)
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
                temperature=kwargs.get("temperature", 0.0),
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
