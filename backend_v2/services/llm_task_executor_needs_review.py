import logging
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, get_args, get_origin

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from backend_v2.exceptions import (
    AgentExecutionError,
    ErrorCodes,
    LLMSchemaValidationError,
    LogicalValidationError,
    SemanticEvidenceError,
)
from backend_v2.llm.caching_service import LLMCachingService
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import ExecutionPersona
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

logger = logging.getLogger(__name__)


class ValidationContextDTO(BaseModel):
    """Strict DTO for LLM Task Execution context to prevent .get() fallback patterns."""

    source_text: str | None = None
    persona: ExecutionPersona | None = None
    workflow_run_id: str | None = None


class LLMTaskExecutor:
    """Centralized orchestrator for AI tasks.

    Replaces raw client logic with zero-compromise Fail-Fast architecture,
    managing Self-Healing retries and strict FinOps token accumulation.
    """

    def __init__(self, prompt_compiler: PromptCompiler) -> None:
        """Initialize the executor with the prompt compiler."""
        self.prompt_compiler = prompt_compiler

    async def execute_structured_task[T: BaseModel](
        self,
        client: LLMClient,
        messages: list[dict[str, Any]] | CompiledPrompt,
        response_model: type[T],
        max_schema_retries: int = 2,
        max_logical_retries: int = 2,
        validator_hook: Callable[[T], Awaitable[None]] | None = None,
        mock_identity: str | None = None,
        validation_context: dict[str, Any] | None = None,
    ) -> tuple[T, TokenUsage]:
        """Execute a structured LLM task with Self-Healing, FinOps, and Strict Fail-Fast."""
        cumulative_usage = TokenUsage()
        context_dto = ValidationContextDTO.model_validate(validation_context or {})

        if isinstance(messages, CompiledPrompt):
            compiled_prompt = messages.model_copy(deep=True)
        else:
            # Minimal fallback if it is a list, adapting to CompiledPrompt
            dynamic = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in messages]
            compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=dynamic)
            if validation_context:
                compiled_prompt = compiled_prompt.model_copy(update={"metadata": validation_context})

        schema_attempts = 0
        logical_attempts = 0

        max_total_attempts = max_schema_retries + max_logical_retries + 1
        previous_error_msg = ""
        previous_raw_payload = ""
        validated_model: T | None = None

        try:
            for attempt in range(max_total_attempts):
                try:
                    validated_model, usage = await client.run_structured_task(
                        messages=compiled_prompt,
                        response_model=response_model,
                        mock_identity=mock_identity,
                        validation_context=validation_context,
                    )

                    cumulative_usage = cumulative_usage + TokenUsage.model_validate(usage)

                    if validator_hook:
                        await validator_hook(validated_model)

                    if context_dto.source_text is not None:
                        source_text = context_dto.source_text
                        persona = context_dto.persona

                        if not persona or persona == ExecutionPersona.DETERMINISTIC_PARSER:
                            if hasattr(validated_model, "model_dump"):

                                def validate_recursive(data: Any, src_text: str) -> None:
                                    if isinstance(data, dict):
                                        reasoning_trace = None
                                        if "reasoning_trace" in data and isinstance(data["reasoning_trace"], str):
                                            reasoning_trace = data["reasoning_trace"]
                                        elif "mechanical_trace" in data and isinstance(data["mechanical_trace"], str):
                                            reasoning_trace = data["mechanical_trace"]

                                        for k, v in data.items():
                                            if k in ("exact_quote", "step_2_quote", "step_1_evidence_quote"):
                                                if isinstance(v, str) and v.strip():
                                                    try:
                                                        AnchorValidationService.validate_evidence(
                                                            src_text, v, reasoning_trace=reasoning_trace
                                                        )
                                                    except SemanticEvidenceError as e:
                                                        raise LogicalValidationError(
                                                            validation_error_msg=e.message
                                                        ) from e
                                            elif isinstance(v, (dict, list)):
                                                validate_recursive(v, src_text)
                                    elif isinstance(data, list):
                                        for item in data:
                                            validate_recursive(item, src_text)

                                validate_recursive(validated_model.model_dump(), source_text)

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
                            detail=ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED.value,
                            original_error=e,
                        )
                        raise err from e

                    if raw_payload == previous_raw_payload or error_msg == previous_error_msg:
                        logger.error(
                            "Stuck Loop Detected in Schema Validation. Breaking immediately.",
                            extra={"error_code": ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED.name},
                        )
                        err = AgentExecutionError(
                            detail=ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED.value,
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

                    healing_content = f"\n\n<PREVIOUS_SCHEMA_ERROR>\n{correction_prompt}\n</PREVIOUS_SCHEMA_ERROR>"

                    new_dynamic = [m.copy() for m in compiled_prompt.dynamic_messages]
                    if new_dynamic:
                        target_msg = new_dynamic[-1]
                        original_content = target_msg.get("content", "")
                        new_dynamic[-1]["content"] = original_content + healing_content
                    else:
                        new_dynamic.append({"role": "user", "content": healing_content.strip()})
                    compiled_prompt = compiled_prompt.model_copy(update={"dynamic_messages": new_dynamic})

                except LogicalValidationError as e:
                    error_msg = e.validation_error_msg

                    def build_fallback(model_cls: type[BaseModel], existing: Any | None = None) -> Any:
                        fallback_data: dict[str, Any] = {}

                        for name, field_info in model_cls.model_fields.items():
                            annotation = field_info.annotation

                            is_list = False
                            inner_cls: type[BaseModel] | None = None

                            origin = get_origin(annotation)
                            if origin is list or origin is Sequence:
                                is_list = True
                                args = get_args(annotation)
                                if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
                                    inner_cls = args[0]
                            elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
                                inner_cls = annotation

                            existing_val = getattr(existing, name, None) if existing else None

                            if is_list and inner_cls:
                                if existing_val and isinstance(existing_val, list):
                                    fallback_data[name] = [build_fallback(inner_cls, item) for item in existing_val]
                                else:
                                    fallback_data[name] = []
                            elif inner_cls:
                                fallback_data[name] = build_fallback(inner_cls, existing_val)
                            else:
                                if name in ("exact_quote", "step_2_quote", "step_1_evidence_quote"):
                                    fallback_data[name] = None
                                elif name in ("score", "step_5_boolean"):
                                    fallback_data[name] = None
                                elif name in ("reasoning_trace", "step_1_reasoning_trace"):
                                    if existing_val and isinstance(existing_val, str):
                                        fallback_data[name] = existing_val
                                    else:
                                        fallback_data[name] = "[SYSTEM ERROR: LLM Unable to verify.]"
                                elif name in (
                                    "justification",
                                    "semantic_reasoning",
                                    "step_3_implicit_justification",
                                    "step_4_reasoning",
                                ):
                                    fallback_data[name] = "[SYSTEM ERROR: LLM Unable to verify.]"
                                elif name == "localized_anchors_found":
                                    fallback_data[name] = []
                                elif name == "contextual_override":
                                    fallback_data[name] = False
                                else:
                                    if existing_val is not None:
                                        fallback_data[name] = existing_val
                                    elif field_info.default is not PydanticUndefined:
                                        fallback_data[name] = field_info.default
                                    elif field_info.default_factory is not None:
                                        fallback_data[name] = field_info.default_factory()  # type: ignore[call-arg]
                                    else:
                                        fallback_data[name] = None

                        return model_cls.model_construct(**fallback_data)

                    if logical_attempts >= max_logical_retries:
                        logger.error(
                            "Max self-healing retries (%s) exhausted for %s. Injecting Null Object Fallback.",
                            max_logical_retries,
                            response_model.__name__,
                            extra={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.name},
                        )
                        fallback = build_fallback(response_model, validated_model)
                        return fallback, cumulative_usage

                    if error_msg == previous_error_msg:
                        logger.error(
                            "Stuck Loop Detected in Logical Validation for %s. Injecting Null Object Fallback.",
                            response_model.__name__,
                            extra={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.name},
                        )
                        fallback = build_fallback(response_model, validated_model)
                        return fallback, cumulative_usage

                    previous_error_msg = error_msg
                    logical_attempts += 1

                    failed_json = validated_model.model_dump_json() if validated_model else "{}"

                    correction_prompt = self.prompt_compiler.get_schema_healing_prompt(
                        error_msg=error_msg,
                        is_logical_error=True,
                        is_eof=False,
                    )

                    coaching_notes = []
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
                        f"\n\n<PREVIOUS_SCHEMA_ERROR>\n"
                        f"Failed Output: {failed_json}\n"
                        f"{correction_prompt}\n"
                        f"</PREVIOUS_SCHEMA_ERROR>"
                    )

                    new_dynamic = [m.copy() for m in compiled_prompt.dynamic_messages]
                    if new_dynamic:
                        target_msg = new_dynamic[-1]
                        original_content = target_msg.get("content", "")
                        new_dynamic[-1]["content"] = original_content + healing_content
                    else:
                        new_dynamic.append({"role": "user", "content": healing_content.strip()})
                    compiled_prompt = compiled_prompt.model_copy(update={"dynamic_messages": new_dynamic})
        finally:
            if client._config and client._config.caching_strategy:
                workflow_run_id = context_dto.workflow_run_id or "default_run"
                try:
                    await LLMCachingService.teardown_workflow_caches(
                        provider_name=client._config.provider, workflow_run_id=workflow_run_id
                    )
                except Exception as teardown_err:
                    logger.error("Error during cache teardown: %s", teardown_err, exc_info=True)
                    raise teardown_err

        logger.error("LLM task failed to complete within retry budgets.")
        raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL.value)

    async def execute_chat_task(self, client: LLMClient, **kwargs: Any) -> str | dict[str, Any]:
        """Execute a free-form chat task, delegating cleanly to the client."""
        return await client.run_chat(**kwargs)
