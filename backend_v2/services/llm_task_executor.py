import logging
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel

from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    ErrorCodes,
    LLMSchemaValidationError,
    LogicalValidationError,
    SemanticEvidenceError,
)
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import ExecutionPersona
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService
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
        messages: list[dict[str, Any]] | CompiledPrompt,
        response_model: type[T],
        max_schema_retries: int = 2,
        max_logical_retries: int = 2,
        validator_hook: Callable[[T], Awaitable[None]] | None = None,
        mock_identity: str | None = None,
        validation_context: dict[str, Any] | None = None,
    ) -> tuple[T, TokenUsage]:
        """Execute a structured LLM task with Self-Healing, FinOps, and Strict Fail-Fast.

        Args:
            client: The properly initialized LLMClient.
            messages: The dialogue array or CompiledPrompt.
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

        from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter

        prompt_adapter = PromptCompilerAdapter()

        # Determine if we received a CompiledPrompt or a flat list of messages
        if isinstance(messages, CompiledPrompt):
            # Create a deep copy of the CompiledPrompt to prevent side-effects
            compiled_prompt = CompiledPrompt(
                static_messages=[dict(m) for m in messages.static_messages],
                dynamic_messages=[dict(m) for m in messages.dynamic_messages],
                metadata=dict(getattr(messages, "metadata", {})),
            )
        else:
            compiled_prompt = prompt_adapter.compile_prompt(messages)
            if validation_context:
                compiled_prompt = compiled_prompt.model_copy(update={"metadata": validation_context})

        schema_attempts = 0
        logical_attempts = 0

        # --- EMPTY PAYLOAD FAIL-FAST ---
        # If the user messages contain no meaningful text after stripping XML tags,
        # we must crash immediately to prevent the LLM from hallucinating an analysis.
        user_texts = []
        if isinstance(messages, CompiledPrompt):
            user_texts = [str(m.get("content", "")) for m in messages.dynamic_messages if m.get("role") == "user"]
        elif isinstance(messages, list):
            user_texts = [str(m.get("content", "")) for m in messages if m.get("role") == "user"]
            
        total_user_text = "".join(user_texts)
        if total_user_text:
            import re
            stripped_text = re.sub(r"<[^>]+>", "", total_user_text).strip()
            if len(stripped_text) < 10:
                logger.error("Fail-Fast: Task payload is suspiciously empty or short. Aborting to prevent hallucinations.")
                raise AppException(
                    message="Fail-Fast: Task payload is empty or too short. Nothing to analyze.",
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED}
                )

        # Max loop is the sum of both budgets + 1 (the initial attempt)
        max_total_attempts = max_schema_retries + max_logical_retries + 1
        previous_error_msg = ""
        previous_raw_payload = ""
        validated_model: T | None = None

        try:
            for attempt in range(max_total_attempts):
                try:
                    # Pass compiled_prompt directly!
                    validated_model, usage = await client.run_structured_task(
                        messages=compiled_prompt,
                        response_model=response_model,
                        mock_identity=mock_identity,
                        validation_context=validation_context,
                    )

                    # FinOps Accumulation
                    cumulative_usage = cumulative_usage + TokenUsage.model_validate(usage)

                    # Asynchronous Domain Validation
                    if validator_hook:
                        await validator_hook(validated_model)

                    # --- SYSTEM-WIDE LEXICAL VERIFIER (FAIL-FAST) ---
                    if validation_context and "source_text" in validation_context:
                        source_text = validation_context["source_text"]
                        persona = validation_context.get("persona")

                        if not persona or persona == ExecutionPersona.DETERMINISTIC_PARSER:
                            if hasattr(validated_model, "model_dump"):

                                def validate_recursive(data: Any, src_text: str) -> None:
                                    if isinstance(data, dict):
                                        trace_val = data.get("reasoning_trace") or data.get("mechanical_trace")
                                        reasoning_trace = trace_val if isinstance(trace_val, str) else None

                                        for k, v in data.items():
                                            # Target any extraction field known to contain verbatim quotes
                                            is_quote_key = k in [
                                                "exact_quote",
                                                "step_2_quote",
                                                "step_1_evidence_quote",
                                            ]
                                            if is_quote_key and isinstance(v, str) and v.strip():
                                                try:
                                                    AnchorValidationService.validate_evidence(
                                                        src_text, v, reasoning_trace=reasoning_trace
                                                    )
                                                except SemanticEvidenceError as e:
                                                    raise LogicalValidationError(validation_error_msg=e.message) from e
                                            elif isinstance(v, (dict, list)):
                                                validate_recursive(v, src_text)
                                    elif isinstance(data, list):
                                        for item in data:
                                            validate_recursive(item, src_text)

                                validate_recursive(validated_model.model_dump(), source_text)

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

                    # Quality-First Retries (Tail-End Injection strictly to CompiledPrompt.dynamic_messages)
                    # We inject the error at the absolute end of the User Prompt to preserve prefix caching.
                    healing_content = f"\n\n<PREVIOUS_SCHEMA_ERROR>\n{correction_prompt}\n</PREVIOUS_SCHEMA_ERROR>"

                    new_dynamic = [dict(m) for m in compiled_prompt.dynamic_messages]
                    if new_dynamic:
                        new_dynamic[-1] = {
                            **new_dynamic[-1],
                            "content": new_dynamic[-1].get("content", "") + healing_content,
                        }
                    else:
                        new_dynamic.append({"role": "user", "content": healing_content.strip()})
                    compiled_prompt = compiled_prompt.model_copy(update={"dynamic_messages": new_dynamic})

                except LogicalValidationError as e:
                    error_msg = e.validation_error_msg

                    if logical_attempts >= max_logical_retries:
                        logger.error(
                            "Max self-healing retries (%s) exhausted for %s. Injecting Null Object Fallback.",
                            max_logical_retries,
                            response_model.__name__,
                            extra={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.name},
                        )

                        def build_fallback(model_cls: type[BaseModel], existing: Any | None = None) -> Any:
                            fallback_data: dict[str, Any] = {}

                            # Inspect all fields of the Pydantic model class
                            for name, field_info in model_cls.model_fields.items():
                                annotation = field_info.annotation

                                # Determine if this field is a list/sequence of BaseModels
                                is_list = False
                                inner_cls: type[BaseModel] | None = None

                                from typing import get_args, get_origin

                                origin = get_origin(annotation)
                                if origin is list or origin is collections.abc.Sequence:
                                    is_list = True
                                    args = get_args(annotation)
                                    if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
                                        inner_cls = args[0]
                                elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
                                    inner_cls = annotation

                                # Retrieve the existing parsed value if present to retain structural attributes
                                # (like atom_ids)
                                existing_val = getattr(existing, name, None) if existing else None

                                if is_list and inner_cls:
                                    if existing_val and isinstance(existing_val, list):
                                        fallback_data[name] = [build_fallback(inner_cls, item) for item in existing_val]
                                    else:
                                        fallback_data[name] = []
                                elif inner_cls:
                                    fallback_data[name] = build_fallback(inner_cls, existing_val)
                                else:
                                    # Apply specialized logic based on expected fallback fields
                                    if name in ["exact_quote", "step_2_quote", "step_1_evidence_quote"]:
                                        fallback_data[name] = None
                                    elif name in ["score", "step_5_boolean"]:
                                        fallback_data[name] = None
                                    elif name in [
                                        "reasoning_trace",
                                        "step_1_reasoning_trace",
                                    ]:
                                        # Preserve original trace if existing, otherwise mark as system error
                                        if existing_val and isinstance(existing_val, str):
                                            fallback_data[name] = existing_val
                                        else:
                                            fallback_data[name] = "[SYSTEM ERROR: LLM Unable to verify.]"
                                    elif name in [
                                        "justification",
                                        "semantic_reasoning",
                                        "step_3_implicit_justification",
                                        "step_4_reasoning",
                                    ]:
                                        fallback_data[name] = "[SYSTEM ERROR: LLM Unable to verify.]"
                                    elif name in ["localized_anchors_found"]:
                                        fallback_data[name] = []
                                    elif name in ["contextual_override"]:
                                        fallback_data[name] = False
                                    else:
                                        # Fallback to existing or None/defaults
                                        if existing_val is not None:
                                            fallback_data[name] = existing_val
                                        elif field_info.default is not PydanticUndefined:
                                            fallback_data[name] = field_info.default
                                        elif field_info.default_factory is not None:
                                            # Use getattr to bypass Pyright's incorrect method-binding type resolution
                                            fallback_data[name] = field_info.default_factory()  # type: ignore[call-arg]
                                        else:
                                            fallback_data[name] = None

                            return model_cls.model_construct(**fallback_data)

                        import collections.abc

                        from pydantic_core import PydanticUndefined

                        fallback = build_fallback(response_model, validated_model)
                        return fallback, cumulative_usage

                    # Stuck Loop Detection
                    if error_msg == previous_error_msg:
                        logger.error(
                            "Stuck Loop Detected in Logical Validation for %s. Injecting Null Object Fallback.",
                            response_model.__name__,
                            extra={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.name},
                        )

                        def build_fallback(model_cls: type[BaseModel], existing: Any | None = None) -> Any:
                            fallback_data: dict[str, Any] = {}

                            # Inspect all fields of the Pydantic model class
                            for name, field_info in model_cls.model_fields.items():
                                annotation = field_info.annotation

                                is_list = False
                                inner_cls: type[BaseModel] | None = None

                                from typing import get_args, get_origin

                                origin = get_origin(annotation)
                                if origin is list or origin is collections.abc.Sequence:
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
                                    if name in ["exact_quote", "step_2_quote", "step_1_evidence_quote"]:
                                        fallback_data[name] = None
                                    elif name in ["score", "step_5_boolean"]:
                                        fallback_data[name] = None
                                    elif name in [
                                        "reasoning_trace",
                                        "step_1_reasoning_trace",
                                    ]:
                                        # Preserve original trace if existing, otherwise mark as system error
                                        if existing_val and isinstance(existing_val, str):
                                            fallback_data[name] = existing_val
                                        else:
                                            fallback_data[name] = "[SYSTEM ERROR: LLM Unable to verify.]"
                                    elif name in [
                                        "justification",
                                        "semantic_reasoning",
                                        "step_3_implicit_justification",
                                        "step_4_reasoning",
                                    ]:
                                        fallback_data[name] = "[SYSTEM ERROR: LLM Unable to verify.]"
                                    elif name in ["localized_anchors_found"]:
                                        fallback_data[name] = []
                                    elif name in ["contextual_override"]:
                                        fallback_data[name] = False
                                    else:
                                        if existing_val is not None:
                                            fallback_data[name] = existing_val
                                        elif field_info.default is not PydanticUndefined:
                                            fallback_data[name] = field_info.default
                                        elif field_info.default_factory is not None:
                                            # Use getattr to bypass Pyright's incorrect method-binding type resolution
                                            fallback_data[name] = field_info.default_factory()  # type: ignore[call-arg]
                                        else:
                                            fallback_data[name] = None

                            return model_cls.model_construct(**fallback_data)

                        import collections.abc

                        from pydantic_core import PydanticUndefined

                        fallback = build_fallback(response_model, validated_model)
                        return fallback, cumulative_usage

                    previous_error_msg = error_msg
                    logical_attempts += 1

                    correction_prompt = self.prompt_compiler.get_schema_healing_prompt(
                        error_msg=error_msg,
                        is_logical_error=True,
                        is_eof=False,
                    )

                    failed_json = validated_model.model_dump_json() if validated_model else "{}"

                    # Epic 54: Smart Coaching for Semantic Extraction Failures
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

                    # Quality-First Retries (Tail-End Injection strictly to CompiledPrompt.dynamic_messages)
                    healing_content = (
                        f"\n\n<PREVIOUS_SCHEMA_ERROR>\n"
                        f"Failed Output: {failed_json}\n"
                        f"{correction_prompt}\n"
                        f"</PREVIOUS_SCHEMA_ERROR>"
                    )

                    new_dynamic = [dict(m) for m in compiled_prompt.dynamic_messages]
                    if new_dynamic:
                        new_dynamic[-1] = {
                            **new_dynamic[-1],
                            "content": new_dynamic[-1].get("content", "") + healing_content,
                        }
                    else:
                        new_dynamic.append({"role": "user", "content": healing_content.strip()})
                    compiled_prompt = compiled_prompt.model_copy(update={"dynamic_messages": new_dynamic})
        finally:
            # Asynchronous caching facade teardown execution in finally block
            if client._config and client._config.caching_strategy:
                workflow_run_id = "default_run"
                if validation_context and "workflow_run_id" in validation_context:
                    workflow_run_id = validation_context["workflow_run_id"]

                try:
                    from backend_v2.llm.caching_service import LLMCachingService

                    await LLMCachingService.teardown_workflow_caches(
                        provider_name=client._config.provider, workflow_run_id=workflow_run_id
                    )
                except Exception as teardown_err:
                    logger.error("Error during cache teardown: %s", teardown_err)

        # Smart Stop if the loop exits without returning or raising
        logger.error("LLM task failed to complete within retry budgets.")
        raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL)

    async def execute_chat_task(self, client: LLMClient, **kwargs: Any) -> str | dict[str, Any]:
        """Execute a free-form chat task, delegating cleanly to the client."""
        return await client.run_chat(**kwargs)
