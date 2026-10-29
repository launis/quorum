"""Deterministic Input Processing Hook for V2 Architecture.

Safely merges and transforms structured `guided_reflection` questionnaires
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
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.domain.step import ExpectedInput
from backend_v2.models.domain.system_config import ChatHistoryDTO, ChatMessageDTO
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.hook_delta import ExecutionInputsDTO, ExecutionMetadataDeltaDTO
from backend_v2.models.dtos.inputs import GuidedReflectionInputDTO, ProcessedChatDTO
from backend_v2.models.enums import LLMProvider, SystemLocale
from backend_v2.services.chat_normalizer import ChatNormalizerService
from backend_v2.services.ingress import MultiChannelIngressService
from backend_v2.services.pii_analyzer import get_pii_service
from backend_v2.services.storage import get_storage_driver
from backend_v2.utils.paths import get_forensic_input_path

__all__ = [
    "process_inputs",
    "resolve_input",
]

logger = logging.getLogger(__name__)


async def resolve_input(val: object | None) -> str:
    """Convert a raw input value from state into its string representation.

    Args:
        val: The raw value extracted from the state.

    Returns:
        The stringified version of the value or an empty string when None.
    """
    if val is None:
        return ""
    return str(val)


def _extract_raw_value(key_lower: str, state: HookState) -> object | None:
    """Extract the raw value for a given key from state inputs and global context.

    Args:
        key_lower: The expected input key in lower case.
        state: The current hook state.

    Returns:
        The extracted raw value, or None if not found.
    """
    raw_inputs: Mapping[str, DomainInputValue] = state.inputs.raw_inputs
    dynamic_inputs: Mapping[str, DomainInputValue] = state.inputs.dynamic_inputs

    # 1. Check raw_inputs
    for k, v in raw_inputs.items():
        if k.lower() == key_lower:
            return v

    # 2. Check dynamic_inputs
    for k, v in dynamic_inputs.items():
        if k.lower() == key_lower:
            return v

    # 3. Check global_context_vars typed fields
    if key_lower == "language" and state.global_context_vars.language is not None:
        return state.global_context_vars.language
    if key_lower == "target_locale" and state.global_context_vars.target_locale is not None:
        return state.global_context_vars.target_locale

    return None


def _process_questionnaire(
    raw_val: object,
    key: str,
    expected_input: ExpectedInput,
    target_locale: str = SystemLocale.EN.value,
) -> str:
    """Validate and transform a questionnaire payload into Markdown text.

    Args:
        raw_val: The raw dictionary value representing the questionnaire.
        key: The input key being processed.
        expected_input: The expected input schema definition.
        target_locale: The target localization code to resolve against.

    Returns:
        The resolved Markdown text for the questionnaire.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if the questionnaire payload is invalid.
    """
    logger.info(
        "Found questionnaire dict. Validating against GuidedReflectionInputDTO...",
        extra={"input_key": key},
    )
    try:
        dto = GuidedReflectionInputDTO.model_validate(raw_val)
        title_text = expected_input.label.resolve(target_locale)
        if not title_text:
            title_text = expected_input.label.resolve(SystemLocale.EN.value)
        if not title_text:
            title_text = key
        return dto.to_markdown(title_text)
    except ValidationError as e:
        logger.error(
            "Invalid questionnaire dict format.",
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "input_key": key},
            exc_info=True,
        )
        raise AppException(
            message=f"Workflow Input Validation Error: Invalid questionnaire format for '{key}'.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "error_code": ErrorCodes.VALIDATION_FAILED.name,
                "input_key": key,
                "errors": [
                    {
                        "loc": [str(loc_item) for loc_item in err["loc"]],
                        "msg": str(err["msg"]),
                        "type": str(err["type"]),
                    }
                    for err in e.errors()
                ],
            },
        ) from e


async def _process_chat_history(
    resolved_text: str,
    key: str,
    system_repo: ISystemRepository,
    enable_semantic_smoothing: bool = False,
    enable_eager_anonymization: bool = False,
    language: str = SystemLocale.EN.value,
    registry_id: str | None = None,
    provider: LLMProvider | None = None,
) -> ProcessedChatDTO:
    """Parse raw unstructured chat logs into ProcessedChatDTO via ChatNormalizerService.

    Args:
        resolved_text: The raw, unstructured chat text.
        key: The input key (e.g., 'chat_log').
        system_repo: The system configuration repository.
        enable_semantic_smoothing: Whether to run SpaCy smoothing on human user turns.
        enable_eager_anonymization: Whether to run Presidio masking on human user turns.
        language: The language of the text.
        registry_id: Optional authoritative model registry ID.
        provider: Optional explicit provider override.

    Returns:
        An immutable DTO containing 'combined', 'user_only', and 'ai_only'.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if chat history parsing fails.
    """
    ingress_service = MultiChannelIngressService()
    chat_dto = await ingress_service.process_chat(
        raw_input=resolved_text,
        system_repo=system_repo,
        key=key,
        registry_id=registry_id,
        provider=provider,
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
    """Save the processed input text to the forensic storage directory.

    Args:
        execution_id: The unique execution ID.
        key: The input key.
        resolved_text: The text to save.

    Raises:
        AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if the storage operation fails.
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


async def _apply_text_nlp(
    resolved_text: str,
    key: str,
    workflow: Workflow,
    language: str,
) -> str:
    """Apply optional SpaCy semantic smoothing and Presidio PII masking to plain text inputs.

    Args:
        resolved_text: The resolved input text.
        key: The input key being processed.
        workflow: The active workflow configuration.
        language: The target language code for NLP models.

    Returns:
        The NLP-processed text string.
    """
    if workflow.enable_semantic_smoothing and resolved_text:
        pii_service = get_pii_service()
        logger.info("[InputProcessingHook] Running Semantic Smoothing for %s", key)
        start_time = time.perf_counter()
        resolved_text = await asyncio.to_thread(pii_service.smooth_text, resolved_text, language)
        duration = time.perf_counter() - start_time
        logger.info("[InputProcessingHook] Semantic Smoothing for %s completed in %.2fs", key, duration)

    if workflow.enable_eager_anonymization and resolved_text:
        pii_service = get_pii_service()
        logger.info("[InputProcessingHook] Running Eager Anonymization for %s", key)
        start_time = time.perf_counter()
        resolved_text = await asyncio.to_thread(pii_service.mask_pii, resolved_text, language)
        duration = time.perf_counter() - start_time
        logger.info("[InputProcessingHook] Eager Anonymization for %s completed in %.2fs", key, duration)

    return resolved_text


async def _process_single_expected_input(
    expected_input: ExpectedInput,
    state: HookState,
    workflow: Workflow,
    system_repo: ISystemRepository,
    execution_id: str,
    language: str,
    output_dict: dict[str, str],
) -> None:
    """Resolve, validate, normalize, and persist a single workflow expected input.

    Args:
        expected_input: The expected input definition from the workflow.
        state: Current hook execution state.
        workflow: The validated workflow domain model.
        system_repo: The system configuration repository.
        execution_id: The active execution identifier.
        language: The resolved language code.
        output_dict: Target dictionary collecting normalized input strings by key.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.STORAGE_ACCESS_FAILED
            if validation or forensic persistence fails.
    """
    key = expected_input.input_key
    raw_val = _extract_raw_value(key.lower(), state)

    if raw_val is not None and not isinstance(raw_val, (str, int, float, list, bool, bytes)):
        resolved_text = _process_questionnaire(raw_val, key, expected_input, target_locale=language)
    else:
        resolved_text = await resolve_input(raw_val)

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

    is_chat = expected_input.is_chat_history
    if is_chat and resolved_text:
        registry_id = (
            state.metadata.model_registry_id
            if state.metadata and state.metadata.model_registry_id
            else workflow.model_registry_id
        )
        chat_result = await _process_chat_history(
            resolved_text=resolved_text,
            key=key,
            system_repo=system_repo,
            enable_semantic_smoothing=workflow.enable_semantic_smoothing,
            enable_eager_anonymization=workflow.enable_eager_anonymization,
            language=language,
            registry_id=registry_id,
            provider=state.metadata.provider_override,
        )
        resolved_text = chat_result.combined
        output_dict[f"{key}_user_only"] = chat_result.user_only
        output_dict[f"{key}_ai_only"] = chat_result.ai_only
    elif not is_chat and resolved_text:
        resolved_text = await _apply_text_nlp(resolved_text, key, workflow, language)

    if expected_input.ai_description is not None:
        if not expected_input.ai_description.strip():
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

    output_dict[key] = resolved_text.strip()

    await _save_forensic_input(execution_id, key, output_dict[key])
    user_only_key = f"{key}_user_only"
    if user_only_key in output_dict:
        await _save_forensic_input(execution_id, user_only_key, output_dict[user_only_key])
    ai_only_key = f"{key}_ai_only"
    if ai_only_key in output_dict:
        await _save_forensic_input(execution_id, ai_only_key, output_dict[ai_only_key])


@hook_registry.register(name="input_processing")
async def process_inputs(state: HookState, deps: HookDependencies) -> HookResult:
    """Read, validate, and normalize raw workflow input modalities into structured text.

    Expands structured `questionnaire` inputs into Markdown documents, routes
    chat history inputs through `ChatNormalizerService`, applies optional NLP
    smoothing/anonymization, and persists forensic input snapshots.

    Args:
        state: Current hook execution state.
        deps: Injected dependencies for the hook.

    Returns:
        Result containing the updated state delta with processed inputs and metadata.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED, ErrorCodes.WORKFLOW_NOT_FOUND,
            ErrorCodes.CONFIGURATION_ERROR, or ErrorCodes.STORAGE_ACCESS_FAILED when
            execution context, workflow lookup, input validation, or forensic storage fails.
    """
    logger.info("[InputProcessingHook] Running deterministic input normalizer...")

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

    workflow_record = await workflow_repo.get_workflow_by_id(workflow_id)
    if not workflow_record:
        logger.error(
            "Workflow not found for input processing.",
            extra={"error_code": ErrorCodes.WORKFLOW_NOT_FOUND.name, "workflow_id": workflow_id},
        )
        raise AppException(
            message=f"Workflow {workflow_id} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.WORKFLOW_NOT_FOUND.value},
        )

    workflow = TypeAdapter(Workflow).validate_python(workflow_record)

    language = state.global_context_vars.language
    if not language and state.inputs and state.inputs.target_locale:
        language = state.inputs.target_locale

    if not language:
        logger.error(
            "Missing language in global context.",
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
        )
        raise AppException(
            message="System Configuration Error: Missing mandatory 'language' in global_context_vars.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    output_dict: dict[str, str] = {}
    for expected_input in workflow.expected_inputs:
        await _process_single_expected_input(
            expected_input=expected_input,
            state=state,
            workflow=workflow,
            system_repo=system_repo,
            execution_id=execution_id,
            language=language,
            output_dict=output_dict,
        )

    total_chars = sum(len(text) for text in output_dict.values())
    estimated_token_count = total_chars // 4

    return HookResult(
        success=True,
        state_delta=HookDeltaDTO(
            delta=ExecutionInputsDTO(raw_inputs=output_dict),
            metadata_updates=ExecutionMetadataDeltaDTO(estimated_token_count=estimated_token_count),
        ),
    )
