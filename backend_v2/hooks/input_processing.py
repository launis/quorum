"""Deterministic Input Processing Hook for V2 Architecture.

This hook replaces the legacy V1 `InputProcessorAgent` LLM overhead.
It safely merges and transforms structured `guided_reflection` questionnaires
and unstructured `reflection_text` strings into a unified text format for downstream AI nodes.
"""

import logging

from fastapi import status
from pydantic import TypeAdapter, ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.inputs import GuidedReflectionInputDTO
from backend_v2.models.v2_core import Workflow
from backend_v2.services.chat_parser import ChatParserService
from backend_v2.services.storage import get_storage_driver

logger = logging.getLogger(__name__)


async def resolve_input(val: str | int | float | list[object] | dict[str, object] | None) -> str:
    """Helper to detect string outputs from API layer Extractor or resolve natively."""
    return str(val) if val else ""


@hook_registry.register(name="input_processing")
async def process_inputs(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: input_processing.

    Reads raw input modalities passed from the client, normalizes them,
    extracts PDF text if base64 encoded, and handles transformations like expanding
    `questionnaire` inputs into Markdown documents. Uses is_chat_history flag to
    dynamically route unstructured text to ChatParserService.
    """
    logger.info("[InputProcessingHook] Running deterministic input normalizer...")

    # Fetch workflow to know about expected_inputs
    repo = deps.repository
    workflow_id = state.workflow_id

    if not repo or not workflow_id:
        logger.error("Missing repository or workflow_id in context.", extra={"error_code": "MISSING_EXECUTION_CONTEXT"})
        raise AppException(
            message="Missing execution context for input processing.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": "MISSING_EXECUTION_CONTEXT"},
        )

    workflow_dict = await repo.get_workflow_by_id(workflow_id)
    if not workflow_dict:
        raise AppException(
            message=f"Workflow {workflow_id} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": "WORKFLOW_NOT_FOUND"},
        )

    workflow = TypeAdapter(Workflow).validate_python(workflow_dict)

    expected_inputs = workflow.expected_inputs
    output_dict: dict[str, str] = {}

    for expected_input in expected_inputs:
        key = expected_input.input_key
        # Case-insensitive fetch to support Flutter client sending snake_case while DB expects UPPER_SNAKE
        key_lower = key.lower()

        # 1. Check state.inputs
        raw_val = None
        for k, v in state.inputs.items():
            if k.lower() == key_lower:
                raw_val = v
                break

        # 2. Check state.global_context_vars
        if raw_val is None:
            for k, v in state.global_context_vars.items():
                if k.lower() == key_lower:
                    raw_val = v
                    break

        # 1. Handle Questionnaire mode specifically if it exists
        if isinstance(raw_val, dict):
            logger.info(
                "Found questionnaire dict. Validating against GuidedReflectionInputDTO...",
                extra={"input_key": key},
            )
            try:
                dto = GuidedReflectionInputDTO.model_validate(raw_val)
                title_text = expected_input.label.resolve("en") or "Questionnaire"
                resolved_text = dto.to_markdown(title_text)
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
        if expected_input.is_chat_history and resolved_text and not resolved_text.strip().startswith("{"):
            logger.info("[InputProcessingHook] Unstructured chat detected for %s. Invoking ChatParserLLM...", key)
            try:
                chat_dto = await ChatParserService.parse_pasted_chat(resolved_text, repository=repo)

                # Format to Markdown instead of raw JSON to prevent \n escaping in LLM prompt
                chat_lines = []
                for turn in chat_dto.conversation:
                    chat_lines.append(f"**{turn.role}**: {turn.content}")
                resolved_text = "\n\n".join(chat_lines)

                logger.info("[InputProcessingHook] Successfully structured %s via ChatParser (Markdown).", key)
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

        # 4. Injektoidaan `ai_description` suoraan raakatekstin yläpuolelle (The English-Only Mandate)
        if expected_input.ai_description is not None:
            # Enforce The English-Only Mandate
            desc_text = expected_input.ai_description.strip()

            # V2 STRICT FAIL-FAST: Missing English instruction is fatal
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
                logger.info("[InputProcessingHook] Injecting ai_description for %s (English-Only Mandate).", key)
                header = f"--- AI INSTRUCTION FOR THIS SOURCE ({key}) ---\n"
                footer = f"\n--- SOURCE: {key} ---"
                resolved_text = f"{header}{desc_text}\n{footer}\n\n{resolved_text}"

        output_dict[key] = resolved_text.strip()

        # --- FORENSIC OBSERVABILITY INJECTION ---
        # Save every processed input with injected prompts into the execution directory
        try:
            storage = get_storage_driver()
            exe_id = state.execution_id or "unknown_exe"
            safe_key = "".join(c for c in key if c.isalnum() or c in ("_", "-"))
            forensic_path = f"executions/{exe_id}/inputs/input_{safe_key}.md"

            await storage.save(forensic_path, output_dict[key])
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

    return HookResult(success=True, state_delta={"inputs": output_dict})
