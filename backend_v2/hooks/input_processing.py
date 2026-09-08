"""Deterministic Input Processing Hook for V2 Architecture.

This hook replaces the legacy V1 `InputProcessorAgent` LLM overhead.
It safely merges and transforms structured `guided_reflection` questionnaires
and unstructured `reflection_text` strings into a unified text format for downstream AI nodes.
"""

import asyncio
import logging
import time
from collections.abc import Mapping

from fastapi import status
from pydantic import TypeAdapter, ValidationError

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.inputs import GuidedReflectionInputDTO, ProcessedChatDTO
from backend_v2.models.v2_core import ChatHistoryDTO, ChatMessageDTO, ExpectedInput, Workflow
from backend_v2.services.chat_normalizer import ChatNormalizerService
from backend_v2.services.pii_analyzer import get_pii_service
from backend_v2.services.storage import get_storage_driver
from backend_v2.utils.paths import get_forensic_input_path

logger = logging.getLogger(__name__)


# Phase 1, Step 1.1: Fix QGR016 resolve_input fallback
async def resolve_input(val: object | None) -> str:
    """Helper to detect string outputs from API layer Extractor or resolve natively.

    Args:
        val: The raw value extracted from the state.

    Returns:
        The stringified version of the value or an empty string.
    """
    if val is None:
        return ""
    return str(val)


# Phase 1, Step 1.2: Strict typing of _extract_raw_value without Any or dict duck typing
def _extract_raw_value(key_lower: str, state: HookState) -> object | None:
    """Extracts the raw value for a given key from the state inputs and global context.

    Args:
        key_lower: The expected input key in lower case.
        state: The current hook state.

    Returns:
        The extracted raw value, or None if not found.
    """
    raw_inputs: Mapping[str, object] = state.inputs.raw_inputs
    dynamic_inputs: Mapping[str, object] = state.inputs.dynamic_inputs
    gvars: Mapping[str, object] = state.global_context_vars.vars

    # 1. Check raw_inputs
    for k, v in raw_inputs.items():
        if k.lower() == key_lower:
            return v

    # 2. Check dynamic_inputs
    for k, v in dynamic_inputs.items():
        if k.lower() == key_lower:
            return v

    # 3. Check global_context_vars
    for k, v in gvars.items():
        if k.lower() == key_lower:
            return v

    return None


def _process_questionnaire(raw_val: object, key: str, expected_input: ExpectedInput) -> str:
    """Validates and processes a questionnaire dictionary into Markdown text.

    Args:
        raw_val: The raw dictionary value representing the questionnaire.
        key: The input key being processed.
        expected_input: The expected input schema definition.

    Returns:
        The resolved Markdown text for the questionnaire.

    Raises:
        AppException: If the dictionary is invalid or missing a mandatory English label.
    """
    logger.info(
        "Found questionnaire dict. Validating against GuidedReflectionInputDTO...",
        extra={"input_key": key},
    )
    try:
        dto = GuidedReflectionInputDTO.model_validate(raw_val)
        title_text = expected_input.label.resolve("en")
        if not title_text:
            logger.error(
                "Missing English label for expected input.",
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "input_key": key},
            )
            raise AppException(
                message=(f"System Configuration Error: Missing mandatory English label for '{key}' questionnaire."),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.name, "input_key": key},
            )
        return dto.to_markdown(title_text)
    except ValidationError as e:
        logger.error(
            "Invalid questionnaire dict format.",
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "input_key": key, "detail": str(e)},
        )
        raise AppException(
            message=f"Workflow Input Validation Error: Invalid questionnaire format for '{key}'.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.name, "input_key": key, "errors": e.errors()},
        ) from e


# Phase 3, Step 3.1: Refactor _process_chat_history to delegate to ChatNormalizerService
async def _process_chat_history(
    resolved_text: str,
    key: str,
    system_repo: ISystemRepository,
    enable_semantic_smoothing: bool,
    enable_eager_anonymization: bool,
    language: str,
) -> ProcessedChatDTO:
    """Parses raw unstructured chat logs into ProcessedChatDTO via ChatNormalizerService.

    Args:
        resolved_text: The raw, unstructured chat text.
        key: The input key (e.g., 'chat_log').
        system_repo: The system configuration repository.
        enable_semantic_smoothing: Whether to run SpaCy smoothing on human user turns.
        enable_eager_anonymization: Whether to run Presidio masking on human user turns.
        language: The language of the text.

    Returns:
        ProcessedChatDTO: An immutable DTO containing 'combined', 'user_only', and 'ai_only'.
    """
    chat_dto = await ChatNormalizerService.parse_chat_to_dto(
        raw_text=resolved_text,
        key=key,
        system_repo=system_repo,
    )

    # Scoped NLP execution strictly on human user turns (user_only) after role segregation
    if enable_semantic_smoothing or enable_eager_anonymization:
        pii_service = get_pii_service()
        processed_turns: list[ChatMessageDTO] = []
        for turn in chat_dto.conversation:
            if turn.role.lower() == "user":
                user_content = turn.content
                if enable_semantic_smoothing:
                    logger.info("[InputProcessingHook] Running Scoped Semantic Smoothing for user turn in %s", key)
                    start_time = time.perf_counter()
                    user_content = await asyncio.to_thread(pii_service.smooth_text, user_content, language)
                    duration = time.perf_counter() - start_time
                    logger.info(
                        "[InputProcessingHook] Scoped Semantic Smoothing for %s completed in %.2fs",
                        key,
                        duration,
                    )

                if enable_eager_anonymization:
                    logger.info("[InputProcessingHook] Running Scoped Eager Anonymization for user turn in %s", key)
                    start_time = time.perf_counter()
                    user_content = await asyncio.to_thread(pii_service.mask_pii, user_content, language)
                    duration = time.perf_counter() - start_time
                    logger.info(
                        "[InputProcessingHook] Scoped Eager Anonymization for %s completed in %.2fs",
                        key,
                        duration,
                    )

                processed_turns.append(ChatMessageDTO(role=turn.role, content=user_content))
            else:
                processed_turns.append(turn)

        chat_dto = ChatHistoryDTO(conversation=processed_turns)

    logger.info("[InputProcessingHook] Successfully structured %s via ChatNormalizerService (XML Segregated).", key)
    return ChatNormalizerService.build_processed_chat(chat_dto)


async def _save_forensic_input(execution_id: str, key: str, resolved_text: str) -> None:
    """Saves the processed input to the forensic storage directory.

    Args:
        execution_id: The unique execution ID.
        key: The input key.
        resolved_text: The text to save.

    Raises:
        AppException: If the storage operation fails.
    """
    try:
        storage = get_storage_driver()
        forensic_path = get_forensic_input_path(execution_id, key)

        await storage.save(forensic_path, resolved_text)
        logger.info("[InputProcessingHook] Forensic Input saved successfully: %s", forensic_path)
    except Exception as e:
        logger.error(
            "Failed to save forensic input.",
            extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.name, "detail": str(e)},
            exc_info=True,
        )
        raise AppException(
            message="Failed to save forensic input.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "input_key": key},
        ) from e


@hook_registry.register(name="input_processing")
async def process_inputs(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: input_processing.

    Reads raw input modalities passed from the client, normalizes them,
    extracts PDF text if base64 encoded, and handles transformations like expanding
    `questionnaire` inputs into Markdown documents. Uses is_chat_history flag to
    dynamically route unstructured text to ChatParserService.

    Args:
        state: Current hook execution state.
        deps: Injected dependencies for the hook.

    Returns:
        Result containing the updated state delta with processed inputs and metadata.

    Raises:
        AppException: If execution context is missing, workflow is not found,
            required inputs are missing, or system configuration is invalid.
    """
    logger.info("[InputProcessingHook] Running deterministic input normalizer...")

    # Fetch workflow to know about expected_inputs
    workflow_repo = deps.workflow_repo
    system_repo = deps.system_repo
    workflow_id = state.workflow_id
    execution_id = state.execution_id

    if not workflow_repo or not workflow_id or not execution_id:
        logger.error(
            "Missing repository, workflow_id, or execution_id in context.",
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
        )
        raise AppException(
            message="Missing execution context for input processing.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    workflow_dict = await workflow_repo.get_workflow_by_id(workflow_id)
    if not workflow_dict:
        raise AppException(
            message=f"Workflow {workflow_id} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.WORKFLOW_NOT_FOUND.value},
        )

    workflow = TypeAdapter(Workflow).validate_python(workflow_dict)

    expected_inputs = workflow.expected_inputs
    output_dict: dict[str, str] = {}

    gvars = state.global_context_vars.vars
    # Phase 1, Step 1.1b: Explicit resolution for language without QGR016 ternary fallback
    language_raw: object | None = None
    if "language" in gvars:
        language_raw = gvars["language"]
    elif state.inputs and state.inputs.target_locale:
        language_raw = state.inputs.target_locale

    if not language_raw:
        logger.error("Missing language in global context.")
        raise AppException(
            message="System Configuration Error: Missing mandatory 'language' in global_context_vars.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
    language = str(language_raw)

    for expected_input in expected_inputs:
        key = expected_input.input_key
        key_lower = key.lower()

        raw_val = _extract_raw_value(key_lower, state)

        # 1. Handle Questionnaire mode specifically if it exists
        resolved_text: str = ""
        is_questionnaire = False
        if raw_val is not None and not isinstance(raw_val, (str, int, float, list)):
            try:
                resolved_text = _process_questionnaire(raw_val, key, expected_input)
                is_questionnaire = True
            # Phase 1, Step 1.2: Correct parenthesized exception tuple syntax
            except ValidationError, TypeError:
                is_questionnaire = False

        if not is_questionnaire:
            # 2. Standard resolution (File, Paste)
            resolved_text = await resolve_input(raw_val)

        # V2 STRICT FAIL-FAST: Validate required inputs immediately
        if expected_input.required and not resolved_text.strip():
            logger.error(
                "Missing required input.",
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "input_key": key},
            )
            raise AppException(
                message=(
                    f"Workflow Input Validation Error: The block '{key}' is required "
                    "but no content was provided or file extraction yielded empty text."
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "input_key": key},
            )

        # 3. V2 ChatParser LLM Hook (if designated as chat history)
        is_chat = expected_input.is_chat_history
        if is_chat and resolved_text:
            chat_result = await _process_chat_history(
                resolved_text=resolved_text,
                key=key,
                system_repo=system_repo,
                enable_semantic_smoothing=workflow.enable_semantic_smoothing,
                enable_eager_anonymization=workflow.enable_eager_anonymization,
                language=language,
            )
            # Phase 3, Step 3.1: Consume ProcessedChatDTO via static dot notation
            resolved_text = chat_result.combined
            output_dict[f"{key}_user_only"] = chat_result.user_only
            output_dict[f"{key}_ai_only"] = chat_result.ai_only

        # --- 1. SEMANTIC SMOOTHING (SpaCy - IN BACKGROUND THREAD) ---
        if not is_chat and workflow.enable_semantic_smoothing and resolved_text:
            pii_service = get_pii_service()
            logger.info("[InputProcessingHook] Running Semantic Smoothing for %s", key)
            start_time = time.perf_counter()
            resolved_text = await asyncio.to_thread(pii_service.smooth_text, resolved_text, language)
            duration = time.perf_counter() - start_time
            logger.info("[InputProcessingHook] Semantic Smoothing for %s completed in %.2fs", key, duration)

        # --- 2. EAGER ANONYMIZATION (Presidio - IN BACKGROUND THREAD) ---
        if not is_chat and workflow.enable_eager_anonymization and resolved_text:
            pii_service = get_pii_service()
            logger.info("[InputProcessingHook] Running Eager Anonymization for %s", key)
            start_time = time.perf_counter()
            resolved_text = await asyncio.to_thread(pii_service.mask_pii, resolved_text, language)
            duration = time.perf_counter() - start_time
            logger.info("[InputProcessingHook] Eager Anonymization for %s completed in %.2fs", key, duration)

        # 4. Inject `ai_description` (The English-Only Mandate)
        if expected_input.ai_description is not None:
            desc_text = expected_input.ai_description.strip()

            if not desc_text:
                logger.error(
                    "Missing English translation for ai_description.",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "input_key": key},
                )
                raise AppException(
                    message=(
                        f"System Configuration Error: Missing mandatory "
                        f"English instruction for '{key}' cognitive prompt block."
                    ),
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "input_key": key},
                )

            if resolved_text.strip():
                logger.info("[InputProcessingHook] Validating ai_description for %s (English-Only Mandate).", key)
                # DO NOT mutate resolved_text. PromptCompiler handles structural injection via <ai_context_mandate>.

        output_dict[key] = resolved_text.strip()

        # --- FORENSIC OBSERVABILITY INJECTION ---
        # Phase 3, Step 3.2: Extend forensic storage for all primary and segregated streams
        await _save_forensic_input(execution_id, key, output_dict[key])
        user_only_key = f"{key}_user_only"
        if user_only_key in output_dict:
            await _save_forensic_input(execution_id, user_only_key, output_dict[user_only_key])
        ai_only_key = f"{key}_ai_only"
        if ai_only_key in output_dict:
            await _save_forensic_input(execution_id, ai_only_key, output_dict[ai_only_key])

    # Phase 7: Token Proxy Score calculation
    total_chars = sum(len(text) for text in output_dict.values())
    estimated_token_count = total_chars // 4

    return HookResult(
        success=True,
        state_delta=HookDeltaDTO(
            delta={"inputs": output_dict},
            metadata_updates={"estimated_token_count": estimated_token_count},
        ),
    )
