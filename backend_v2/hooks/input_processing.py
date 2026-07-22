"""Deterministic Input Processing Hook for V2 Architecture.

This hook replaces the legacy V1 `InputProcessorAgent` LLM overhead.
It safely merges and transforms structured `guided_reflection` questionnaires
and unstructured `reflection_text` strings into a unified text format for downstream AI nodes.
"""

import asyncio
import logging
import re
import time
from typing import Any

from fastapi import status
from pydantic import TypeAdapter, ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.inputs import GuidedReflectionInputDTO
from backend_v2.models.v2_core import ChatHistoryDTO, ExpectedInput, Workflow
from backend_v2.services.chat_parser import ChatParserService
from backend_v2.services.pii_analyzer import get_pii_service
from backend_v2.services.storage import get_storage_driver
from backend_v2.utils.paths import get_forensic_input_path

logger = logging.getLogger(__name__)


async def resolve_input(val: str | int | float | list[object] | dict[str, object] | None) -> str:
    """Helper to detect string outputs from API layer Extractor or resolve natively.

    Args:
        val: The raw value extracted from the state.

    Returns:
        The stringified version of the value or an empty string.
    """
    return str(val) if val else ""


def _extract_raw_value(key_lower: str, state: HookState) -> Any:
    """Extracts the raw value for a given key from the state inputs and global context.

    Args:
        key_lower: The expected input key in lower case.
        state: The current hook state.

    Returns:
        The extracted raw value, or None if not found.
    """
    # 1. Check state.inputs
    for k, v in state.inputs.items():
        if k.lower() == key_lower:
            return v

    dynamic_inputs = state.inputs.get("dynamic_inputs")
    if isinstance(dynamic_inputs, dict):
        for k, v in dynamic_inputs.items():
            if k.lower() == key_lower:
                return v

    # 2. Check state.global_context_vars
    for k, v in state.global_context_vars.items():
        if k.lower() == key_lower:
            return v

    return None


def _process_questionnaire(raw_val: dict[str, Any], key: str, expected_input: ExpectedInput) -> str:
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


async def _process_chat_history(
    resolved_text: str,
    key: str,
    system_repo: Any,
    enable_semantic_smoothing: bool,
    enable_eager_anonymization: bool,
    language: str,
) -> dict[str, str]:
    """Parses raw unstructured chat logs into strict JSON via ChatParserService and formats to Markdown.

    Args:
        resolved_text: The raw, unstructured chat text.
        key: The input key (e.g., 'chat_log').
        system_repo: The system configuration repository.
        enable_semantic_smoothing: Whether to run SpaCy smoothing on raw text.
        enable_eager_anonymization: Whether to run Presidio masking on raw text.
        language: The language of the text.

    Returns:
        dict: A dictionary containing 'combined', 'user_only', and 'ai_only' Markdown formatted strings.
    """
    try:
        import ftfy

        resolved_text = ftfy.fix_text(resolved_text)
    except ImportError:
        logger.warning("[InputProcessingHook] ftfy is not installed, proceeding without text fixing.")

    chat_dto = None
    stripped_text = resolved_text.strip()
    if stripped_text.startswith("{") or stripped_text.startswith("["):
        try:
            chat_dto = ChatHistoryDTO.model_validate_json(stripped_text)
            logger.info("[InputProcessingHook] Valid JSON chat detected for %s. Bypassing NLP.", key)
        except ValidationError, ValueError:
            logger.warning(
                "[InputProcessingHook] Malformed JSON chat detected for %s. Falling back to raw text parsing.", key
            )

    if chat_dto is None:
        logger.info("[InputProcessingHook] Unstructured chat detected for %s. Running NLP & ChatParserLLM...", key)

        if enable_semantic_smoothing:
            pii_service = get_pii_service()
            logger.info("[InputProcessingHook] Running Semantic Smoothing for unstructured chat %s", key)
            start_time = time.perf_counter()
            resolved_text = await asyncio.to_thread(pii_service.smooth_text, resolved_text, language)
            duration = time.perf_counter() - start_time
            logger.info("[InputProcessingHook] Semantic Smoothing for chat %s completed in %.2fs", key, duration)

        if enable_eager_anonymization:
            pii_service = get_pii_service()
            logger.info("[InputProcessingHook] Running Eager Anonymization for unstructured chat %s", key)
            start_time = time.perf_counter()
            resolved_text = await asyncio.to_thread(pii_service.mask_pii, resolved_text, language)
            duration = time.perf_counter() - start_time
            logger.info("[InputProcessingHook] Eager Anonymization for chat %s completed in %.2fs", key, duration)

        try:
            logger.info(
                "[InputProcessingHook] Resolved %s text (length: %d): %r", key, len(resolved_text), resolved_text
            )
            chat_dto = await ChatParserService.parse_pasted_chat(resolved_text, system_repo=system_repo)
        except Exception as e:
            if isinstance(e, AppException):
                raise e
            logger.error(
                "Chat parsing failed.",
                extra={"error_code": "CHAT_PARSING_FAILED", "input_key": key, "detail": str(e)},
                exc_info=True,
            )
            raise AppException(
                message=f"Failed to parse unstructured chat for {key} using AI.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": "CHAT_PARSING_FAILED"},
            ) from e

    # Format to Markdown instead of raw JSON to prevent \n escaping in LLM prompt
    combined_lines = []
    user_lines = []
    ai_lines = []
    for turn in chat_dto.conversation:
        # Deterministic Normalization: Crush all whitespace/newlines into single spaces
        cleaned_content = re.sub(r"\s+", " ", turn.content).strip()
        if turn.role == "user":
            combined_lines.append(f"<user_payload>\n{cleaned_content}\n</user_payload>")
            user_lines.append(cleaned_content)
        else:
            combined_lines.append(f"<ai_draft_context>\n{cleaned_content}\n</ai_draft_context>")
            ai_lines.append(cleaned_content)

    logger.info("[InputProcessingHook] Successfully structured %s (XML Segregated).", key)
    return {
        "combined": "\n\n".join(combined_lines),
        "user_only": "\n\n".join(user_lines),
        "ai_only": "\n\n".join(ai_lines),
    }


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
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.name, "input_key": key},
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
            extra={"error_code": "MISSING_EXECUTION_CONTEXT"},
        )
        raise AppException(
            message="Missing execution context for input processing.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": "MISSING_EXECUTION_CONTEXT"},
        )

    workflow_dict = await workflow_repo.get_workflow_by_id(workflow_id)
    if not workflow_dict:
        raise AppException(
            message=f"Workflow {workflow_id} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": "WORKFLOW_NOT_FOUND"},
        )

    workflow = TypeAdapter(Workflow).validate_python(workflow_dict)

    expected_inputs = workflow.expected_inputs
    output_dict: dict[str, str] = {}

    language_raw = state.global_context_vars.get("language")
    if not language_raw:
        logger.error("Missing language in global context.")
        raise AppException(
            message="System Configuration Error: Missing mandatory 'language' in global_context_vars.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
        )
    language = str(language_raw)

    for expected_input in expected_inputs:
        key = expected_input.input_key
        key_lower = key.lower()

        raw_val = _extract_raw_value(key_lower, state)

        # 1. Handle Questionnaire mode specifically if it exists
        if isinstance(raw_val, dict):
            resolved_text = _process_questionnaire(raw_val, key, expected_input)
        else:
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
                details={"error_code": ErrorCodes.VALIDATION_FAILED.name, "input_key": key},
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
            resolved_text = chat_result["combined"]
            output_dict[f"{key}_user_only"] = chat_result["user_only"]
            output_dict[f"{key}_ai_only"] = chat_result["ai_only"]

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
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.name, "input_key": key},
                )

            if resolved_text.strip():
                logger.info("[InputProcessingHook] Validating ai_description for %s (English-Only Mandate).", key)
                # DO NOT mutate resolved_text. PromptCompiler handles structural injection via <ai_context_mandate>.

        output_dict[key] = resolved_text.strip()

        # --- FORENSIC OBSERVABILITY INJECTION ---
        await _save_forensic_input(execution_id, key, output_dict[key])

    # Phase 7: Token Proxy Score calculation
    total_chars = sum(len(text) for text in output_dict.values())
    estimated_token_count = total_chars // 4

    return HookResult(
        success=True, state_delta={"inputs": output_dict, "metadata": {"estimated_token_count": estimated_token_count}}
    )
