import logging
import re
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
from backend_v2.llm.caching_service import LLMCachingService
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter

logger = logging.getLogger(__name__)


def _validate_non_empty_payload(messages: list[dict[str, Any]] | CompiledPrompt) -> None:
    """Phase 1: Extract payload validation to prevent hallucinations.

    Scans the prompt payload to ensure the user message is not empty. If the payload
    is too short, it aborts the generation process.

    Args:
        messages: The prompt payload to validate.

    Raises:
        AppException: If the user payload text is critically short.
    """
    user_texts = []
    if isinstance(messages, CompiledPrompt):
        static = [str(m.get("content", "")) for m in messages.static_messages if m.get("role") == "user"]
        dynamic = [str(m.get("content", "")) for m in messages.dynamic_messages if m.get("role") == "user"]
        user_texts = static + dynamic
    elif isinstance(messages, list):
        user_texts = [str(m.get("content", "")) for m in messages if m.get("role") == "user"]

    total_user_text = "".join(user_texts)
    if total_user_text:
        stripped_text = re.sub(r"<[^>]+>", "", total_user_text).strip()
        if len(stripped_text) < 10:
            logger.error(
                "Fail-Fast: Task payload is suspiciously empty or short. "
                f"Aborting to prevent hallucinations. Text: {stripped_text}"
            )
            raise AppException(
                message=(
                    "Fail-Fast: Task payload is empty or too short. "
                    f"Length: {len(stripped_text)}, Content: '{stripped_text}'"
                ),
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            )


def _perform_semantic_validation(validated_model: BaseModel, validation_context: dict[str, Any]) -> None:
    """Phase 1: Extract recursive semantic verification.

    Recursively traces through the validated Pydantic model, searching for quote
    keys and asserting their presence in the original source text.

    Args:
        validated_model: The successfully parsed Pydantic model to verify.
        validation_context: The validation context containing source_text and locale.

    Raises:
        LogicalValidationError: If a semantic quote mismatch is found.
    """
    if not hasattr(validated_model, "model_dump"):
        return

    source_text = validation_context.get("source_text", "")
    locale = validation_context.get("locale")
    alias_map = validation_context.get("alias_map", {})

    mcp_source_texts = validation_context.get("mcp_source_texts", {})

    from backend_v2.models.enums import get_lexical_fuzz_threshold
    from backend_v2.services.mcp.alias_registry import AliasRegistry

    def validate_recursive(data: Any, src_text: str) -> None:
        if isinstance(data, BaseModel):
            trace_val = getattr(data, "reasoning_trace", None) or getattr(data, "mechanical_trace", None)
            reasoning_trace = trace_val if isinstance(trace_val, str) else None

            used_evidence_ids = getattr(data, "used_evidence_ids", None)
            mcp_texts_to_search = {}
            if isinstance(used_evidence_ids, list):
                if alias_map:
                    for e_id in used_evidence_ids:
                        if isinstance(e_id, str):
                            try:
                                AliasRegistry.resolve(e_id, alias_map)
                                if e_id in mcp_source_texts:
                                    mcp_texts_to_search[e_id] = mcp_source_texts[e_id]
                            except SemanticEvidenceError as e:
                                raise LogicalValidationError(validation_error_msg=e.message) from e

            for field_name in data.model_fields:
                v = getattr(data, field_name, None)
                is_quote_str = field_name in ["exact_quote", "step_2_quote", "step_1_evidence_quote"]
                is_quote_list = field_name in ["exact_quotes", "step_2_quotes", "step_1_evidence_quotes"]

                if mcp_texts_to_search and (is_quote_str or is_quote_list):
                    quotes = [v] if is_quote_str else (v if isinstance(v, list) else [])
                    valid_quotes = [q for q in quotes if isinstance(q, str) and q.strip()]

                    if valid_quotes:
                        threshold = get_lexical_fuzz_threshold(locale)
                        for quote in valid_quotes:
                            norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(quote)
                            if not norm_quote:
                                continue

                            match_found = False
                            matched_e_id = None
                            for e_id, mcp_text in mcp_texts_to_search.items():
                                norm_mcp, _ = AnchorValidationService.normalize_text_with_mapping(mcp_text)
                                score = AnchorValidationService.calculate_fuzzy_score(norm_quote, norm_mcp)
                                if score >= threshold:
                                    match_found = True
                                    matched_e_id = e_id
                                    break

                            if not match_found:
                                raise LogicalValidationError(
                                    validation_error_msg="Sitaattia ei löydy fyysisesti lähteestä. Älä tiivistä, kopioi sanatarkasti."
                                )

                            if hasattr(data, "is_mcp_verified"):
                                data.is_mcp_verified = True
                            if hasattr(data, "mcp_source_reference"):
                                data.mcp_source_reference = matched_e_id
                else:
                    if is_quote_str and isinstance(v, str) and v.strip():
                        try:
                            AnchorValidationService.validate_evidence(
                                src_text, [v], reasoning_trace=reasoning_trace, locale=locale
                            )
                        except SemanticEvidenceError as e:
                            raise LogicalValidationError(validation_error_msg=e.message) from e
                    elif is_quote_list and isinstance(v, list) and any(isinstance(i, str) and i.strip() for i in v):
                        try:
                            AnchorValidationService.validate_evidence(
                                src_text, v, reasoning_trace=reasoning_trace, locale=locale
                            )
                        except SemanticEvidenceError as e:
                            raise LogicalValidationError(validation_error_msg=e.message) from e

                if isinstance(v, (BaseModel, list, dict)):
                    validate_recursive(v, src_text)

        elif isinstance(data, dict):
            trace_val = data.get("reasoning_trace") or data.get("mechanical_trace")
            reasoning_trace = trace_val if isinstance(trace_val, str) else None

            used_evidence_ids = data.get("used_evidence_ids")
            mcp_texts_to_search = {}
            if isinstance(used_evidence_ids, list):
                if alias_map:
                    for e_id in used_evidence_ids:
                        if isinstance(e_id, str):
                            try:
                                AliasRegistry.resolve(e_id, alias_map)
                                if e_id in mcp_source_texts:
                                    mcp_texts_to_search[e_id] = mcp_source_texts[e_id]
                            except SemanticEvidenceError as e:
                                raise LogicalValidationError(validation_error_msg=e.message) from e

            for k, v in data.items():
                is_quote_str = k in ["exact_quote", "step_2_quote", "step_1_evidence_quote"]
                is_quote_list = k in ["exact_quotes", "step_2_quotes", "step_1_evidence_quotes"]

                if mcp_texts_to_search and (is_quote_str or is_quote_list):
                    quotes = [v] if is_quote_str else (v if isinstance(v, list) else [])
                    valid_quotes = [q for q in quotes if isinstance(q, str) and q.strip()]

                    if valid_quotes:
                        threshold = get_lexical_fuzz_threshold(locale)
                        for quote in valid_quotes:
                            norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(quote)
                            if not norm_quote:
                                continue

                            match_found = False
                            matched_e_id = None
                            for e_id, mcp_text in mcp_texts_to_search.items():
                                norm_mcp, _ = AnchorValidationService.normalize_text_with_mapping(mcp_text)
                                score = AnchorValidationService.calculate_fuzzy_score(norm_quote, norm_mcp)
                                if score >= threshold:
                                    match_found = True
                                    matched_e_id = e_id
                                    break

                            if not match_found:
                                raise LogicalValidationError(
                                    validation_error_msg="Sitaattia ei löydy fyysisesti lähteestä. Älä tiivistä, kopioi sanatarkasti."
                                )

                            data["is_mcp_verified"] = True
                            data["mcp_source_reference"] = matched_e_id
                else:
                    if is_quote_str and isinstance(v, str) and v.strip():
                        try:
                            AnchorValidationService.validate_evidence(
                                src_text, [v], reasoning_trace=reasoning_trace, locale=locale
                            )
                        except SemanticEvidenceError as e:
                            raise LogicalValidationError(validation_error_msg=e.message) from e
                    elif is_quote_list and isinstance(v, list) and any(isinstance(i, str) and i.strip() for i in v):
                        try:
                            AnchorValidationService.validate_evidence(
                                src_text, v, reasoning_trace=reasoning_trace, locale=locale
                            )
                        except SemanticEvidenceError as e:
                            raise LogicalValidationError(validation_error_msg=e.message) from e

                if isinstance(v, (BaseModel, list, dict)):
                    validate_recursive(v, src_text)

        elif isinstance(data, list):
            for item in data:
                validate_recursive(item, src_text)

    validate_recursive(validated_model, source_text)


class LLMTaskExecutor:
    """Centralized orchestrator for AI tasks.

    Replaces raw client logic with zero-compromise Fail-Fast architecture,
    managing Self-Healing retries and strict FinOps token accumulation.
    """

    def __init__(self, prompt_compiler: PromptCompiler) -> None:
        """Initialize the executor.

        Args:
            prompt_compiler: The centralized compiler used for self-healing prompts.
        """
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
            AgentExecutionError: If maximum retries are exhausted or catastrophic failure occurs.
            AppException: If the initial prompt payload validation fails.
        """
        cumulative_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

        prompt_adapter = PromptCompilerAdapter()

        if isinstance(messages, CompiledPrompt):
            compiled_prompt = CompiledPrompt(
                static_messages=[dict(m) for m in messages.static_messages],
                dynamic_messages=[dict(m) for m in messages.dynamic_messages],
                metadata=dict(getattr(messages, "metadata", {})),
            )
        else:
            compiled_prompt = prompt_adapter.compile_prompt(messages)
            if validation_context:
                compiled_prompt = compiled_prompt.model_copy(update={"metadata": validation_context})

        base_compiled_prompt = compiled_prompt.model_copy(deep=True)

        # --- EMPTY PAYLOAD FAIL-FAST ---
        _validate_non_empty_payload(base_compiled_prompt)

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

                    # FinOps Accumulation
                    cumulative_usage = cumulative_usage + TokenUsage.model_validate(usage)

                    # Asynchronous Domain Validation
                    if validator_hook:
                        await validator_hook(validated_model)

                    # --- SYSTEM-WIDE LEXICAL VERIFIER (FAIL-FAST)
                    if validation_context and "source_text" in validation_context:
                        is_lightweight = validation_context.get("is_lightweight_extraction")
                        if not is_lightweight:
                            _perform_semantic_validation(validated_model, validation_context)

                    if getattr(validated_model, "contextual_override", False):
                        logger.info(
                            "💡 [QUALITY] LLM applied Contextual Override.",
                            extra={
                                "reason": getattr(validated_model, "override_reason", "No reason provided"),
                                "schema": response_model.__name__,
                            },
                        )

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
                            extra={
                                "error_code": ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED.name,
                                "schema_attempts": schema_attempts,
                                "logical_attempts": logical_attempts,
                            },
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
                            extra={
                                "error_code": ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED.name,
                                "schema_attempts": schema_attempts,
                                "logical_attempts": logical_attempts,
                            },
                        )
                        err = AgentExecutionError(
                            detail=ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED,
                            original_error=e,
                        )
                        raise err from e

                    previous_raw_payload = raw_payload
                    previous_error_msg = error_msg
                    schema_attempts += 1

                    logger.warning(
                        f"LLM Schema Validation Failed. Error: {error_msg}",
                        extra={"raw_payload_dump": raw_payload, "validation_error": error_msg},
                    )

                    correction_prompt = self.prompt_compiler.get_schema_healing_prompt(
                        error_msg=error_msg,
                        is_logical_error=False,
                        is_eof=is_eof,
                        strictness_level=validation_context.get("strictness_level") if validation_context else None,
                    )

                    healing_content = f"\n\n<PREVIOUS_SCHEMA_ERROR>\n{correction_prompt}\n</PREVIOUS_SCHEMA_ERROR>"

                    new_dynamic = [dict(m) for m in base_compiled_prompt.dynamic_messages]
                    if new_dynamic:
                        new_dynamic[-1] = {
                            **new_dynamic[-1],
                            "content": new_dynamic[-1].get("content", "") + healing_content,
                        }
                    else:
                        new_dynamic.append({"role": "user", "content": healing_content.strip()})
                    compiled_prompt = base_compiled_prompt.model_copy(update={"dynamic_messages": new_dynamic})

                except LogicalValidationError as e:
                    error_msg = e.validation_error_msg

                    if logical_attempts >= max_logical_retries:
                        logger.error(
                            "Max self-healing retries (%s) exhausted for %s. Failing Fast.",
                            max_logical_retries,
                            response_model.__name__,
                            extra={
                                "error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.name,
                                "schema_attempts": schema_attempts,
                                "logical_attempts": logical_attempts,
                            },
                        )
                        err = AgentExecutionError(
                            detail=ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED,
                            original_error=e,
                        )
                        raise err from e

                    # Stuck Loop Detection
                    if error_msg == previous_error_msg:
                        logger.error(
                            "Stuck Loop Detected in Logical Validation for %s. Breaking immediately.",
                            response_model.__name__,
                            extra={
                                "error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.name,
                                "schema_attempts": schema_attempts,
                                "logical_attempts": logical_attempts,
                            },
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
                        strictness_level=validation_context.get("strictness_level") if validation_context else None,
                    )

                    failed_json = validated_model.model_dump_json() if validated_model else "{}"

                    logger.warning(
                        f"LLM Logical Validation Failed. Error: {error_msg}",
                        extra={"failed_json_dump": failed_json, "logical_error": error_msg},
                    )

                    # Epic 54: Smart Coaching
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

                    new_dynamic = [dict(m) for m in base_compiled_prompt.dynamic_messages]
                    if new_dynamic:
                        new_dynamic[-1] = {
                            **new_dynamic[-1],
                            "content": new_dynamic[-1].get("content", "") + healing_content,
                        }
                    else:
                        new_dynamic.append({"role": "user", "content": healing_content.strip()})
                    compiled_prompt = base_compiled_prompt.model_copy(update={"dynamic_messages": new_dynamic})
        finally:
            if client._config and client._config.caching_strategy:
                workflow_run_id = "default_run"
                if validation_context and "workflow_run_id" in validation_context:
                    workflow_run_id = validation_context["workflow_run_id"]

                try:
                    await LLMCachingService.teardown_workflow_caches(
                        provider_name=client._config.provider, workflow_run_id=workflow_run_id
                    )
                except Exception as teardown_err:
                    logger.error("Error during cache teardown: %s", teardown_err)

        logger.error("LLM task failed to complete within retry budgets.")
        raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL)

    async def execute_chat_task(self, client: LLMClient, **kwargs: Any) -> str | dict[str, Any]:
        """Execute a free-form chat task, delegating cleanly to the client.

        Args:
            client: The client responsible for executing the task.
            **kwargs: Additional arbitrary keyword arguments required by the client.

        Returns:
            The raw unstructured response from the LLM.
        """
        return await client.run_chat(**kwargs)
