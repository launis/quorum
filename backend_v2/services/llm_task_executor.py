"""Centralized LLM task executor enforcing self-healing and Fail-Fast pipelines."""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any

from pydantic import BaseModel, JsonValue

from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    ErrorCodes,
    LLMSchemaValidationError,
    LogicalValidationError,
)
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.system_config import ChatMessageDTO
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.prompt_context import PromptContextDTO
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt, PromptMetadataDTO
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["LLMTaskExecutor"]


def _validate_non_empty_payload(
    messages: Sequence[LLMMessageDTO | ChatMessageDTO] | CompiledPrompt | PromptContextDTO,
) -> None:
    """Validate prompt payload text to prevent hallucinations.

    Scans the prompt payload to ensure the user message is not empty. If the payload
    is too short, it aborts the generation process immediately.

    Args:
        messages: The prompt payload to validate.

    Raises:
        AppException: If the user payload text is critically short (ErrorCodes.VALIDATION_FAILED).
    """
    raw_list: Sequence[LLMMessageDTO | ChatMessageDTO | object]
    if isinstance(messages, (CompiledPrompt, PromptContextDTO)):
        raw_list = list(messages.static_messages) + list(messages.dynamic_messages)
    elif isinstance(messages, (list, tuple, Sequence)):
        raw_list = list(messages)
    else:
        raw_list = []

    user_texts: list[str] = []
    for m in raw_list:
        if isinstance(m, (ChatMessageDTO, LLMMessageDTO)):
            if m.role == "user":
                if isinstance(m.content, str):
                    user_texts.append(m.content)
                else:
                    user_texts.append(json.dumps(m.content))
        else:
            typed_m = ChatMessageDTO.model_validate(m)
            if typed_m.role == "user":
                user_texts.append(typed_m.content)

    total_user_text = "".join(user_texts)
    settings = get_settings()

    # Step 1: Extract CDATA blocks to preserve genuine payload text
    cdata_contents = re.findall(r"<!\[CDATA\[([\s\S]*?)(?:\]\]>|$)", total_user_text)

    # Step 2: Remove CDATA blocks to isolate non-CDATA markup
    non_cdata_text = re.sub(r"<!\[CDATA\[[\s\S]*?(?:\]\]>|$)", "", total_user_text)

    # Step 3: Strip XML markup tags from non-CDATA remainder
    stripped_non_cdata = re.sub(r"<[^>]+>", "", non_cdata_text)

    # Step 4: Re-combine preserved CDATA text with non-CDATA text content
    clean_payload_text = ("".join(cdata_contents) + stripped_non_cdata).strip()

    if len(clean_payload_text) < settings.llm_min_payload_length:
        logger.error(
            "Fail-Fast: Task payload is suspiciously empty or short. "
            f"Aborting to prevent hallucinations. Text: {clean_payload_text}",
            extra={
                "error_code": ErrorCodes.VALIDATION_FAILED.name,
                "payload_length": len(clean_payload_text),
                "min_length": settings.llm_min_payload_length,
            },
            exc_info=True,
        )
        raise AppException(
            message=(
                "Fail-Fast: Task payload is empty or too short. "
                f"Length: {len(clean_payload_text)}, Content: '{clean_payload_text}'"
            ),
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )


class LLMTaskExecutor:
    """Centralized orchestrator for AI tasks.

    Replaces raw client logic with zero-compromise Fail-Fast architecture,
    managing Self-Healing retries and strict FinOps token accumulation.

    Attributes:
        prompt_compiler: The centralized compiler used for self-healing prompts.
        default_validation_context: Optional default context dictionary for validation.
    """

    def __init__(
        self, prompt_compiler: PromptCompiler, default_validation_context: Mapping[str, JsonValue] | None = None
    ) -> None:
        """Initialize the executor.

        Args:
            prompt_compiler: The centralized compiler used for self-healing prompts.
            default_validation_context: A fallback context containing execution_id and step_id.
        """
        self.prompt_compiler = prompt_compiler
        self.default_validation_context = default_validation_context

    def _compile_base_prompt(
        self,
        messages: Sequence[ChatMessageDTO | LLMMessageDTO] | CompiledPrompt | PromptContextDTO,
    ) -> CompiledPrompt:
        """Normalize incoming messages or prompt context into an immutable CompiledPrompt.

        Args:
            messages: Raw message sequence, PromptContextDTO, or pre-compiled prompt.

        Returns:
            Deep-copied CompiledPrompt ready for execution and self-healing retries.
        """
        if isinstance(messages, CompiledPrompt):
            compiled_prompt = messages
        elif isinstance(messages, PromptContextDTO):
            meta = PromptMetadataDTO.model_validate(messages.metadata) if messages.metadata else PromptMetadataDTO()
            compiled_prompt = CompiledPrompt(
                static_messages=messages.static_messages,
                dynamic_messages=messages.dynamic_messages,
                metadata=meta,
            )
        else:
            prompt_adapter = PromptCompilerAdapter()
            compiled_prompt = prompt_adapter.compile_prompt(messages)
        return compiled_prompt.model_copy(deep=True)

    def _extract_strictness_level(self, effective_validation_context: Mapping[str, JsonValue]) -> int | None:
        """Extract integer strictness level from the active validation context if present.

        Args:
            effective_validation_context: Active validation context mapping.

        Returns:
            Integer strictness level if present and numeric, otherwise None.
        """
        if "strictness_level" in effective_validation_context:
            raw_strict = effective_validation_context["strictness_level"]
            if isinstance(raw_strict, int):
                return raw_strict
            if isinstance(raw_strict, float):
                return int(raw_strict)
        return None

    def _append_healing_message(
        self,
        base_compiled_prompt: CompiledPrompt,
        healing_content: str,
    ) -> CompiledPrompt:
        """Append self-healing error feedback to the tail of dynamic messages.

        Args:
            base_compiled_prompt: Original unmutated compiled prompt prefix and dynamic tail.
            healing_content: XML-fenced error correction directive to append.

        Returns:
            Updated CompiledPrompt with healing instructions appended to the user message tail.
        """
        typed_dynamic: list[LLMMessageDTO] = [
            m if isinstance(m, LLMMessageDTO) else LLMMessageDTO.model_validate(m)
            for m in base_compiled_prompt.dynamic_messages
        ]
        if typed_dynamic:
            last_msg = typed_dynamic[-1]
            if isinstance(last_msg.content, str):
                merged_content = last_msg.content + healing_content
            else:
                merged_content = json.dumps(last_msg.content) + healing_content
            typed_dynamic[-1] = LLMMessageDTO(
                role=last_msg.role,
                content=merged_content,
            )
        else:
            typed_dynamic.append(LLMMessageDTO(role="user", content=healing_content.strip()))
        return base_compiled_prompt.model_copy(update={"dynamic_messages": typed_dynamic})

    def _log_contextual_override(self, validated_model: BaseModel, schema_name: str) -> None:
        """Log quality telemetry when the LLM applies a contextual override on a validated model.

        Args:
            validated_model: Validated Pydantic response model instance.
            schema_name: Name of the response model schema for structured logging.
        """
        model_dict = validated_model.model_dump(exclude_unset=False)
        if "contextual_override" in model_dict and model_dict["contextual_override"]:
            override_reason = "No reason provided"
            if "override_reason" in model_dict:
                raw_override_reason = model_dict["override_reason"]
                if raw_override_reason:
                    override_reason = str(raw_override_reason)
            logger.info(
                "[QUALITY] LLM applied Contextual Override.",
                extra={
                    "reason": override_reason,
                    "schema": schema_name,
                },
            )

    def _build_schema_healing_prompt(
        self,
        error: LLMSchemaValidationError,
        base_compiled_prompt: CompiledPrompt,
        effective_validation_context: Mapping[str, JsonValue],
    ) -> CompiledPrompt:
        """Construct an updated CompiledPrompt with schema error correction instructions.

        Args:
            error: Caught LLMSchemaValidationError instance.
            base_compiled_prompt: Base compiled prompt to append healing feedback onto.
            effective_validation_context: Active validation context mapping.

        Returns:
            Updated CompiledPrompt containing schema healing instructions.
        """
        error_msg = error.validation_error_msg
        logger.warning(
            f"LLM Schema Validation Failed. Error: {error_msg}",
            extra={"raw_payload_dump": error.raw_llm_payload, "validation_error": error_msg},
        )
        strictness_lvl_val = self._extract_strictness_level(effective_validation_context)
        correction_prompt = self.prompt_compiler.get_schema_healing_prompt(
            error_msg=error_msg,
            is_logical_error=False,
            is_eof=error.is_eof,
            strictness_level=strictness_lvl_val,
        )
        healing_content = f"\n\n<PREVIOUS_SCHEMA_ERROR>\n{correction_prompt}\n</PREVIOUS_SCHEMA_ERROR>"
        return self._append_healing_message(base_compiled_prompt, healing_content)

    def _build_logical_healing_prompt(
        self,
        error: LogicalValidationError,
        validated_model: BaseModel | None,
        base_compiled_prompt: CompiledPrompt,
        effective_validation_context: Mapping[str, JsonValue],
    ) -> CompiledPrompt:
        """Construct an updated CompiledPrompt with logical error correction and coaching instructions.

        Args:
            error: Caught LogicalValidationError instance.
            validated_model: Last syntactically valid model that failed logical validation.
            base_compiled_prompt: Base compiled prompt to append healing feedback onto.
            effective_validation_context: Active validation context mapping.

        Returns:
            Updated CompiledPrompt containing logical healing and coaching instructions.
        """
        error_msg = error.validation_error_msg
        strictness_lvl = self._extract_strictness_level(effective_validation_context)
        correction_prompt = self.prompt_compiler.get_schema_healing_prompt(
            error_msg=error_msg,
            is_logical_error=True,
            is_eof=False,
            strictness_level=strictness_lvl,
        )

        failed_json = "{}"
        if validated_model is not None:
            failed_json = validated_model.model_dump_json()

        logger.warning(
            f"LLM Logical Validation Failed. Error: {error_msg}",
            extra={"failed_json_dump": failed_json, "logical_error": error_msg},
        )

        # Smart Coaching: Anti-ellipsis and anti-bracket guidance
        coaching_notes: list[str] = []
        if "..." in failed_json:
            coaching_notes.append(
                "COACHING: You used ellipses (...) to bridge or shorten text. This is STRICTLY FORBIDDEN. "
                "You must extract a continuous, unbroken, verbatim string of text."
            )
        if "[" in failed_json or "]" in failed_json:
            coaching_notes.append(
                "COACHING: You injected square brackets [...] to add context. This is STRICTLY FORBIDDEN. "
                "Do not alter the text. Extract exactly what is written."
            )
        if coaching_notes:
            correction_prompt += "\n\n" + "\n".join(coaching_notes)

        healing_content = (
            f"\n\n<PREVIOUS_SCHEMA_ERROR>\nFailed Output: {failed_json}\n{correction_prompt}\n</PREVIOUS_SCHEMA_ERROR>"
        )
        return self._append_healing_message(base_compiled_prompt, healing_content)

    async def execute_structured_task[T: BaseModel](
        self,
        client: LLMClient,
        messages: Sequence[ChatMessageDTO | LLMMessageDTO] | CompiledPrompt | PromptContextDTO,
        response_model: type[T],
        max_schema_retries: int | None = None,
        max_logical_retries: int | None = None,
        validator_hook: Callable[[T], Awaitable[None]] | None = None,
        mock_identity: str | None = None,
        validation_context: Any | None = None,
    ) -> tuple[T, TokenUsage]:
        """Execute a structured LLM task with Self-Healing, FinOps, and Strict Fail-Fast.

        Executes the AI task against the given client, wrapping the execution in a robust
        schema and logical self-healing loop. Integrates semantic validation if provided in context.

        Args:
            client: The target LLM client to use.
            messages: The user messages or compiled prompt.
            response_model: The target Pydantic class to validate against.
            max_schema_retries: Maximum attempts to heal raw schema malformations.
            max_logical_retries: Maximum attempts to heal logical discrepancies.
            validator_hook: Asynchronous hook for additional domain validation.
            mock_identity: The mock identity for Pytest deterministic paths.
            validation_context: Additional parameters like `source_text`.

        Returns:
            A tuple containing the successfully validated model and accumulated token usage.

        Raises:
            AgentExecutionError: If maximum retries are exhausted or catastrophic failure occurs
                (ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED, ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED,
                ErrorCodes.AGENT_EXECUTION_CRITICAL).
            AppException: If the initial prompt payload validation fails (ErrorCodes.VALIDATION_FAILED).
        """
        cumulative_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

        effective_validation_context: dict[str, JsonValue] = {}
        if self.default_validation_context is not None:
            effective_validation_context.update(self.default_validation_context)
        if isinstance(validation_context, BaseModel):
            effective_validation_context.update(validation_context.model_dump(mode="json"))
        elif validation_context is not None:
            effective_validation_context.update(validation_context)

        base_compiled_prompt = self._compile_base_prompt(messages)
        compiled_prompt = base_compiled_prompt

        # --- EMPTY PAYLOAD FAIL-FAST ---
        _validate_non_empty_payload(base_compiled_prompt)

        settings = get_settings()
        actual_schema_retries = (
            max_schema_retries if max_schema_retries is not None else settings.llm_max_schema_retries
        )
        actual_logical_retries = (
            max_logical_retries if max_logical_retries is not None else settings.llm_max_logical_retries
        )

        schema_attempts = 0
        logical_attempts = 0
        max_total_attempts = actual_schema_retries + actual_logical_retries + 1
        previous_error_msg = ""
        previous_raw_payload = ""
        validated_model: T | None = None

        for attempt in range(max_total_attempts):
            try:
                validated_model, usage = await client.run_structured_task(
                    messages=compiled_prompt,
                    response_model=response_model,
                    mock_identity=mock_identity,
                    validation_context=effective_validation_context,
                )

                # FinOps Accumulation
                cumulative_usage = cumulative_usage + TokenUsage.model_validate(usage)

                # Asynchronous Domain Validation
                if validator_hook:
                    await validator_hook(validated_model)

                if isinstance(validated_model, BaseModel):
                    self._log_contextual_override(validated_model, response_model.__name__)

                if attempt > 0:
                    logger.info(
                        "Self-Healing successful.",
                        extra={"healing_attempts": attempt, "target_schema": response_model.__name__},
                    )

                return validated_model, cumulative_usage

            except LLMSchemaValidationError as e:
                raw_payload = e.raw_llm_payload
                error_msg = e.validation_error_msg

                if e.token_usage:
                    cumulative_usage = cumulative_usage + e.token_usage

                if schema_attempts >= actual_schema_retries:
                    logger.error(
                        "Max schema retries exceeded.",
                        extra={
                            "error_code": ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED.name,
                            "schema_attempts": schema_attempts,
                            "logical_attempts": logical_attempts,
                        },
                        exc_info=True,
                    )
                    err = AgentExecutionError(
                        detail=ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED,
                        original_error=e,
                    )
                    raise err from e

                if raw_payload == previous_raw_payload or error_msg == previous_error_msg:
                    logger.error(
                        "Stuck Loop Detected in Schema Validation. Breaking immediately.",
                        extra={
                            "error_code": ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED.name,
                            "schema_attempts": schema_attempts,
                            "logical_attempts": logical_attempts,
                        },
                        exc_info=True,
                    )
                    err = AgentExecutionError(
                        detail=ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED,
                        original_error=e,
                    )
                    raise err from e

                previous_raw_payload = raw_payload
                previous_error_msg = error_msg
                schema_attempts += 1
                compiled_prompt = self._build_schema_healing_prompt(
                    error=e,
                    base_compiled_prompt=base_compiled_prompt,
                    effective_validation_context=effective_validation_context,
                )

            except LogicalValidationError as e:
                error_msg = e.validation_error_msg

                if logical_attempts >= actual_logical_retries:
                    logger.error(
                        "Max self-healing retries (%s) exhausted for %s. Failing Fast.",
                        actual_logical_retries,
                        response_model.__name__,
                        extra={
                            "error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.name,
                            "schema_attempts": schema_attempts,
                            "logical_attempts": logical_attempts,
                        },
                        exc_info=True,
                    )
                    err = AgentExecutionError(
                        detail=ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED,
                        original_error=e,
                    )
                    raise err from e

                if error_msg == previous_error_msg:
                    logger.error(
                        "Stuck Loop Detected in Logical Validation for %s. Breaking immediately.",
                        response_model.__name__,
                        extra={
                            "error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.name,
                            "schema_attempts": schema_attempts,
                            "logical_attempts": logical_attempts,
                        },
                        exc_info=True,
                    )
                    err = AgentExecutionError(
                        detail=ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED,
                        original_error=e,
                    )
                    raise err from e

                previous_error_msg = error_msg
                logical_attempts += 1
                compiled_prompt = self._build_logical_healing_prompt(
                    error=e,
                    validated_model=validated_model,
                    base_compiled_prompt=base_compiled_prompt,
                    effective_validation_context=effective_validation_context,
                )

        logger.error(
            "LLM task failed to complete within retry budgets.",
            extra={
                "error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                "schema_attempts": schema_attempts,
                "logical_attempts": logical_attempts,
            },
            exc_info=True,
        )
        raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL)

    async def execute_chat_task(self, client: LLMClient, **kwargs: Any) -> str | dict[str, JsonValue]:
        """Execute a free-form chat task, delegating cleanly to the client.

        Args:
            client: The client responsible for executing the task.
            **kwargs: Additional arbitrary keyword arguments required by the client.

        Returns:
            The raw unstructured response from the LLM.

        Raises:
            AgentExecutionError: If the chat task execution fails (ErrorCodes.AGENT_EXECUTION_CRITICAL).
        """
        return await client.run_chat(**kwargs)
