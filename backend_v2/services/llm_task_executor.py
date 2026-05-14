import logging
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel

from backend_v2.exceptions import AgentExecutionError, ErrorCodes, LLMSchemaValidationError, LogicalValidationError
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

logger = logging.getLogger(__name__)


class LLMTaskExecutor:
    """Centralized orchestrator for AI tasks.

    Replaces raw client logic with zero-compromise Fail-Fast architecture,
    managing Self-Healing retries and strict FinOps token accumulation.
    """

    def __init__(self, prompt_compiler: PromptCompiler) -> None:
        """Initialize the executor."""
        self.prompt_compiler = prompt_compiler

    async def execute_structured_task[T: BaseModel](
        self,
        client: LLMClient,
        messages: list[dict[str, Any]],
        response_model: type[T],
        max_schema_retries: int = 2,
        max_logical_retries: int = 1,
        validator_hook: Callable[[T], Awaitable[None]] | None = None,
        mock_identity: str | None = None,
        validation_context: dict[str, Any] | None = None,
    ) -> tuple[T, TokenUsage]:
        """Execute a structured LLM task with Self-Healing, FinOps, and Strict Fail-Fast.

        Args:
            client: The properly initialized LLMClient.
            messages: The dialogue array.
            response_model: Expected Pydantic output.
            max_schema_retries: Tech/syntax budget.
            max_logical_retries: Semantic budget.
            validator_hook: Optional async domain validator hook.
            mock_identity: Test identifier.
            validation_context: Optional context dict for Pydantic V2 validation (strictness_level, etc).

        Returns:
            Tuple of (Validated Pydantic Model, TokenUsage).
        """
        cumulative_usage = TokenUsage()

        # Shallow copy the message array and dicts so we can mutate the user message text safely
        current_messages = [dict(m) for m in messages]
        schema_attempts = 0
        logical_attempts = 0

        # Max loop is the sum of both budgets + 1 (the initial attempt)
        max_total_attempts = max_schema_retries + max_logical_retries + 1
        previous_error_msg = ""
        previous_raw_payload = ""
        validated_model: T | None = None

        for attempt in range(max_total_attempts):
            try:
                validated_model, usage = await client.run_structured_task(
                    messages=current_messages,
                    response_model=response_model,
                    mock_identity=mock_identity,
                    validation_context=validation_context,
                )

                # FinOps Accumulation
                cumulative_usage = cumulative_usage + TokenUsage.model_validate(usage)

                # Asynchronous Domain Validation
                if validator_hook:
                    await validator_hook(validated_model)

                # Success, log Healing Rate if applicable
                if attempt > 0:
                    logger.info(
                        "Self-Healing successful.",
                        extra={"healing_attempts": attempt, "target_schema": response_model.__name__},
                    )

                return validated_model, cumulative_usage

            except LLMSchemaValidationError as e:
                is_eof = e.is_eof
                raw_payload = e.raw_llm_payload
                error_msg = e.validation_error_msg

                if hasattr(e, "token_usage") and e.token_usage:
                    cumulative_usage = cumulative_usage + e.token_usage

                if schema_attempts >= max_schema_retries:
                    logger.error(
                        "Max schema retries exceeded.",
                        extra={"error_code": ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED.name},
                    )
                    err = AgentExecutionError(
                        detail=ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED,
                        original_error=e,
                    )
                    raise err from e

                # Stuck Loop Detection
                if raw_payload == previous_raw_payload or error_msg == previous_error_msg:
                    logger.error(
                        "Stuck Loop Detected in Schema Validation. Breaking immediately.",
                        extra={"error_code": ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED.name},
                    )
                    err = AgentExecutionError(
                        detail=ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED,
                        original_error=e,
                    )
                    raise err from e

                previous_raw_payload = raw_payload
                previous_error_msg = error_msg
                schema_attempts += 1

                correction_prompt = self.prompt_compiler.get_schema_healing_prompt(
                    error_msg=error_msg,
                    is_logical_error=False,
                    is_eof=is_eof,
                )

                # Quality-First Retries (Tail-End Injection)
                # We inject the error at the absolute end of the User Prompt to preserve prefix caching.
                # We drop the previous raw hallucination to avoid poisoning the LLM context.
                for i in range(len(current_messages) - 1, -1, -1):
                    if current_messages[i].get("role") == "user":
                        current_messages[i]["content"] = (
                            current_messages[i].get("content", "")
                            + f"\n\n<PREVIOUS_SCHEMA_ERROR>\n{correction_prompt}\n</PREVIOUS_SCHEMA_ERROR>"
                        )
                        break
                else:
                    current_messages.append(
                        {
                            "role": "user",
                            "content": (f"<PREVIOUS_SCHEMA_ERROR>\n{correction_prompt}\n</PREVIOUS_SCHEMA_ERROR>"),
                        }
                    )

            except LogicalValidationError as e:
                error_msg = e.validation_error_msg

                if logical_attempts >= max_logical_retries:
                    logger.error(
                        "Max logical retries exceeded.",
                        extra={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.name},
                    )
                    err = AgentExecutionError(
                        detail=ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED,
                        original_error=e,
                    )
                    raise err from e

                # Stuck Loop Detection
                if error_msg == previous_error_msg:
                    logger.error(
                        "Stuck Loop Detected in Logical Validation. Breaking immediately.",
                        extra={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.name},
                    )
                    err = AgentExecutionError(
                        detail=ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED,
                        original_error=e,
                    )
                    raise err from e

                previous_error_msg = error_msg
                logical_attempts += 1

                correction_prompt = self.prompt_compiler.get_schema_healing_prompt(
                    error_msg=error_msg,
                    is_logical_error=True,
                    is_eof=False,
                )

                failed_json = validated_model.model_dump_json() if validated_model else "{}"

                # Quality-First Retries (Tail-End Injection)
                for i in range(len(current_messages) - 1, -1, -1):
                    if current_messages[i].get("role") == "user":
                        current_messages[i]["content"] = (
                            current_messages[i].get("content", "")
                            + "\n\n<PREVIOUS_SCHEMA_ERROR>\n"
                            + f"Failed Output: {failed_json}\n"
                            + f"{correction_prompt}\n"
                            + "</PREVIOUS_SCHEMA_ERROR>"
                        )
                        break
                else:
                    current_messages.append(
                        {
                            "role": "user",
                            "content": (
                                "<PREVIOUS_SCHEMA_ERROR>\n"
                                f"Failed Output: {failed_json}\n"
                                f"{correction_prompt}\n"
                                "</PREVIOUS_SCHEMA_ERROR>"
                            ),
                        }
                    )

        # Smart Stop if the loop exits without returning or raising
        logger.error("LLM task failed to complete within retry budgets.")
        raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL)

    async def execute_chat_task(self, client: LLMClient, **kwargs: Any) -> str | dict[str, Any]:
        """Execute a free-form chat task, delegating cleanly to the client."""
        return await client.run_chat(**kwargs)
