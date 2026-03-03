"""Agent responsible for raw input processing (Y-Funnel)."""

import logging
from typing import Any

from fastapi import status

from backend.agents.base import BaseAgent
from backend.exceptions import AppException
from backend.models.domain.input_processor import InputProcessorDTO, InputProcessorOutput
from backend.models.domain.inputs import WorkflowInputs

logger = logging.getLogger(__name__)


class InputProcessorAgent(BaseAgent[WorkflowInputs, InputProcessorOutput]):
    """Agent that moves raw input processing to the async worker.

    Responsibilities:
    1. Base64 File Decoding
    2. Document Extraction (PDF, DOCX) via DocumentService
    3. Intelligent mapping of extracted text to core fields
    4. Chat History parsing via internal LLM hook (if text provided)
    """

    # We expect raw dictionary shapes matching WorkflowInputs or the model itself
    INPUT_SCHEMA = WorkflowInputs

    # We output strict Domain Models
    DTO_SCHEMA = InputProcessorDTO
    OUTPUT_SCHEMA = InputProcessorOutput

    REQUIRES_KEYS = ["inputs"]
    PRODUCES_KEYS = ["input_processor"]

    async def execute(
        self,
        input_data: WorkflowInputs,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        repository: Any = None,
        **kwargs: Any,
    ) -> InputProcessorOutput:
        """Executes the input processing logic synchronously without a main LLM call.

        This agent is unique; it doesn't primarily act as a prompt-driven LLM wrapper like JudgeAgent.
        Instead, it wraps the pure python Extraction logic, but optionally uses an LLM (via ChatParser)
        to format chat strings.
        """
        logger.info(f"[{self.__class__.__name__}] Starting execution...")

        context_dict = execution_context or {}
        execution_id = context_dict.get("execution_id", "unknown")

        # (Document extraction and Base64 OCR is handled upstream by ExecutionPrepService)
        extracted_data: dict[str, str] = {}

        # 1. Map raw text inputs
        if isinstance(input_data.history_text, str):
            extracted_data["history_text"] = input_data.history_text
        elif isinstance(input_data.history_text, dict) and "content_base64" in input_data.history_text:
            logger.warning("Base64 dict received via history_text but should have been parsed upstream! Ignoring.")

        if isinstance(input_data.product_text, str):
            extracted_data["product_text"] = input_data.product_text
        elif isinstance(input_data.product_text, dict) and "content_base64" in input_data.product_text:
            logger.warning("Base64 dict received via product_text but should have been parsed upstream! Ignoring.")

        if isinstance(input_data.reflection_text, str):
            extracted_data["reflection_text"] = input_data.reflection_text
        elif isinstance(input_data.reflection_text, dict) and "content_base64" in input_data.reflection_text:
            logger.warning("Base64 dict received via reflection_text but should have been parsed upstream! Ignoring.")

        # 3. Y-Funnel Parse: Extract specific features via LLM ChatParser if history_text is present
        final_history_text = extracted_data.get("history_text")

        if final_history_text:
            from backend.services.chat_parser import parse_pasted_chat

            try:
                logger.info(f"[{self.__class__.__name__}] Y-Funnel: Parsing history_text with LLM ChatParser")
                # Need a repository for ChatParser, should be in context
                repo = context_dict.get("repository")
                if not repo:
                    logger.warning(
                        "Repository not in execution context for ChatParser. Parsing might fail if it relies on DB."
                    )

                chat_dto = await parse_pasted_chat(final_history_text, repository=repo)

                # ChatParser returns a strictly enforced format, serialize to text for the Context Variables
                import json

                structured_text = json.dumps(chat_dto.model_dump(), indent=2, ensure_ascii=False)
                extracted_data["history_text"] = structured_text

                logger.info(f"[{self.__class__.__name__}] Successfully parsed chat history into strict JSON structure.")
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Chat parsing failed in Y-Funnel: {e}")
                if isinstance(e, AppException):
                    raise e
                raise AppException(
                    message="Failed to parse chat history",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": "CHAT_PARSING_FAILED"},
                ) from e

        # 4. Guided Reflection Markdown Generation (If guided_reflection dict was passed)
        logger.info(
            f"[{self.__class__.__name__}] Y-Funnel: Checking GuidedReflection input: {input_data.guided_reflection}"
        )
        if input_data.guided_reflection:
            from backend.models.dtos.reflection import GuidedReflectionDTO
            from backend.services.reflection_service import ReflectionService

            logger.info(f"[{self.__class__.__name__}] Y-Funnel: Generating markdown from GuidedReflection")
            try:
                gr_dto = GuidedReflectionDTO(**input_data.guided_reflection)
                reflection_markdown = ReflectionService.generate_markdown_document(gr_dto)
                extracted_data["reflection_text"] = reflection_markdown
                logger.info(f"[{self.__class__.__name__}] Mapped GuidedReflection to 'reflection_text'.")
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Failed to process guided reflection: {e}")

        # 5. Construct final DTO
        dto = InputProcessorDTO(
            history_text=extracted_data.get("history_text") or "",
            product_text=extracted_data.get("product_text") or "",
            reflection_text=extracted_data.get("reflection_text") or "",
            thought_process="Funnel extraction and text hydration complete.",
            conclusion="Inputs successfully processed and prepared for engine routing.",
            confidence_score=1.0,
        )

        # 6. Apply System Authority (Logging timestamps, checksums, promoting to Domain Model)
        org_id = context_dict.get("organization_id") or kwargs.get("organization_id")
        workflow_id = context_dict.get("workflow") or kwargs.get("workflow")
        user_id = context_dict.get("user_id") or kwargs.get("user_id")
        step_id = context_dict.get("step_id") or kwargs.get("step_id")

        final_domain_model = self._apply_python_authority(
            data=dto,
            organization_id=org_id,
            workflow=workflow_id,
            user_id=user_id,
            execution_id=execution_id,
            step_id=step_id,
            model="deterministic-extraction",  # No single LLM model for the agent itself
            provider="system",
        )

        return final_domain_model
