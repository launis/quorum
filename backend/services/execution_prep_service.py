import base64
import logging
from typing import Any

from backend.database.repository import AbstractWorkflowRepository
from backend.models.dtos.execution import Base64FileDTO, ExecutionRequestDTO
from backend.services.document_service import DocumentService

logger = logging.getLogger(__name__)


class ExecutionPrepService:
    """Service responsible for data preparation before workflow execution begins.

    Refactored in V5.1 (Phase 9): This service no longer does the heavy lifting of
    Base64 decoding or Y-Funnel LLM parsing. All raw payloads (images, dicts) are passed
    directly to the 'step_input_processor' agent via the graph engine to ensure standard
    fail-fast observability and worker process isolation.
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
        """Validates and prepares the inputs for the workflow engine by mapping
        Base64 payload models to raw dictionaries for the InputProcessorAgent.
        """
        inputs: dict[str, Any] = {}
        files_to_process = {}

        # 1. Pass explicit string inputs and decode Base64 File DTOs
        for key, value in request.inputs.items():
            if isinstance(value, Base64FileDTO):
                content_bytes = base64.b64decode(value.content_base64)
                files_to_process[key] = (value.filename, content_bytes)
            elif isinstance(value, dict) and "content_base64" in value:
                content_bytes = base64.b64decode(value["content_base64"])
                filename = value.get("filename", "unknown")
                files_to_process[key] = (filename, content_bytes)
            else:
                inputs[key] = str(value)

        # 1.5 Process decoded files via DocumentService
        if files_to_process and document_service:
            try:
                doc_texts = await document_service.process_evidence_files(execution_id, files_to_process)
                for raw_key, text_content in doc_texts.items():
                    logger.info(f"[ExecutionPrep] Extracted text from {raw_key} via DocumentService")
                    inputs[raw_key] = text_content
            except Exception as e:
                logger.error(f"[ExecutionPrep] Failed to process evidence files: {e}")
                from fastapi import status

                from backend.exceptions import AppException

                raise AppException(
                    message=f"File processing failed: {e}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": "FILE_PROCESSING_FAILED"},
                ) from e

        # 2. Normalize Inputs (SSOT Pattern)
        # Ensure organization_id is ALWAYS in inputs
        if not inputs.get("organization_id"):
            if organization_id:
                inputs["organization_id"] = organization_id
            elif current_user and getattr(current_user, "organization_id", None):
                inputs["organization_id"] = current_user.organization_id

        # 3. Y-Funnel Part 1: Pass GuidedReflection structure natively
        if request.guided_reflection:
            logger.info("[ExecutionPrep] Passing GuidedReflection directly to inputs.")
            inputs["guided_reflection"] = request.guided_reflection.model_dump(exclude_none=True)

        logger.info(f"[ExecutionPrep] FINAL Prepared Execution Inputs Keys: {list(inputs.keys())}")
        return inputs
