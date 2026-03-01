import base64
import logging
from typing import Any

from fastapi import status

from backend.database.repository import AbstractWorkflowRepository
from backend.exceptions import AppException
from backend.models.dtos.execution import Base64FileDTO, ExecutionRequestDTO
from backend.services.document_service import DocumentService
from backend.services.reflection_service import ReflectionService

logger = logging.getLogger(__name__)


class ExecutionPrepService:
    """Service responsible for data preparation, extraction, and validation
    before workflow execution begins (Y-Funnel Architecture).
    """

    @staticmethod
    async def prepare_execution_inputs(
        request: ExecutionRequestDTO,
        execution_id: str,
        organization_id: str | None,
        current_user: Any,
        document_service: DocumentService,
        repository: AbstractWorkflowRepository,
    ) -> dict[str, Any]:
        """Validates and prepares the inputs for the workflow engine.
        Handles base64 decoding, specific file mapping, and LLM chat log parsing.
        """
        inputs: dict[str, Any] = {}
        files_to_process: dict[str, tuple[str, bytes]] = {}

        # 1. Separate explicit string inputs from Base64 File DTOs
        for key, value in request.inputs.items():
            if isinstance(value, Base64FileDTO):
                try:
                    content_bytes = base64.b64decode(value.content_base64)
                    files_to_process[key] = (value.filename, content_bytes)
                except Exception as e:
                    logger.error(f"INVALID_BASE64_FILE: {e} for key {key}")
                    raise AppException(
                        message=f"Failed to decode base64 file for {key}",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": "INVALID_BASE64_FILE"}
                    ) from e
            elif isinstance(value, dict) and "content_base64" in value:
                try:
                    content_bytes = base64.b64decode(value["content_base64"])
                    files_to_process[key] = (value.get("filename", "unknown"), content_bytes)
                except Exception as e:
                    raise AppException(
                        message=f"Failed to decode file {key}",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": "INVALID_BASE64_FILE"}
                    ) from e
            else:
                inputs[key] = str(value)

        # 2. Normalize Inputs (SSOT Pattern)
        # Ensure organization_id is ALWAYS in inputs
        if not inputs.get("organization_id"):
            if organization_id:
                inputs["organization_id"] = organization_id
            elif current_user and getattr(current_user, "organization_id", None):
                inputs["organization_id"] = current_user.organization_id

        # 3. Process Evidence Files via DocumentService
        if files_to_process:
            try:
                extracted_texts = await document_service.process_evidence_files(execution_id, files_to_process)

                for raw_key, text_content in extracted_texts.items():
                    # Smart Mapping targeting core system keys
                    lower_key = raw_key.lower()
                    target_key = raw_key

                    if "historia" in lower_key or "history" in lower_key or "chat" in lower_key:
                        target_key = "history_text"
                    elif "lopputuote" in lower_key or "product" in lower_key or "output" in lower_key:
                        target_key = "product_text"
                    elif "reflektio" in lower_key or "reflection" in lower_key or "self" in lower_key:
                        target_key = "reflection_text"

                    inputs[target_key] = text_content
                    logger.info(
                        f"[ExecutionPrep] Mapped uploaded file '{raw_key}' "
                        f"to input '{target_key}' ({len(text_content)} chars)"
                    )
            except Exception as e:
                logger.error(f"[ExecutionPrep] DocumentService failed: {e}")
                raise AppException(
                    message=f"File processing failed: {e}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": "FILE_PROCESSING_FAILED"}
                ) from e

        # 4. Y-Funnel Parse: Extract specific features
        if "history_text" in inputs:
            from backend.services.chat_parser import parse_pasted_chat
            try:
                logger.info("[ExecutionPrep] Y-Funnel: Parsing history_text with LLM ChatParser")
                chat_dto = await parse_pasted_chat(inputs["history_text"], repository=repository)
                # Store structured DTO as dict
                inputs["parsed_history"] = chat_dto.model_dump()
            except Exception as e:
                logger.error(f"[ExecutionPrep] Chat parsing failed in Y-Funnel: {e}")
                if isinstance(e, AppException):
                    raise e
                raise AppException(
                    message="Failed to parse chat history",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": "CHAT_PARSING_FAILED"}
                ) from e

        # 5. Guided Reflection Markdown Generation
        if request.guided_reflection:
            logger.info("[ExecutionPrep] Y-Funnel: Generating markdown from GuidedReflectionDTO")
            try:
                reflection_markdown = ReflectionService.generate_markdown_document(request.guided_reflection)
                inputs["reflection_text"] = reflection_markdown
                logger.info("[ExecutionPrep] Mapped GuidedReflection to 'reflection_text' input.")
            except Exception as e:
                logger.error(f"[ExecutionPrep] Reflection generation failed: {e}")
                raise AppException(
                    message="Failed to generate reflection document",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": "REFLECTION_GENERATION_FAILED"}
                ) from e

        logger.info(f"[ExecutionPrep] FINAL Resolved Execution Inputs Keys: {list(inputs.keys())}")
        return inputs
