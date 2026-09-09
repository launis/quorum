"""Service for parsing unstructured pasted chat logs into strict JSON structures.

Uses an LLM (strategy: 'ChatParser') to decouple human conversation from UI garbage,
aligning with the V2 Fail-Fast architecture.
"""

import json
import logging

from fastapi import status
from pydantic import ValidationError

from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.llm.prompt_builder import build_system_directive
from backend_v2.models.dtos.ingress import ChatTurnAnchorsResponseDTO
from backend_v2.models.v2_core import ChatHistoryDTO, ChatMessageDTO
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTION = build_system_directive(
    objective=(
        "You are a boundary-detection expert. Your task is to identify the exact verbatim\n"
        "start and end boundary phrases of each conversational turn in raw, unstructured dialogue text\n"
        "originating from an AI chat (e.g. ChatGPT, Gemini, or Claude)."
    ),
    rules=[
        "Identify the chronological sequence of conversation turns between human ('user') and AI ('ai').",
        "For each turn, extract ONLY the boundary phrases verbatim from the source text:",
        "- 'speaker': MUST be either 'user' or 'ai'.",
        "- 'start_phrase': The FIRST 5-8 words of the turn verbatim (or fewer words only if the turn is shorter).",
        "- 'end_phrase': The LAST 5-8 words of the turn verbatim (or fewer words only if the turn is shorter).",
        "NEVER generate, summarize, paraphrase, or rewrite the turn content. The extraction MUST be 100% exact verbatim substrings.",
        "Ignore all UI fluff (e.g., 'Copy code', 'Share', 'Regenerate', sidebar text).",
        "Return the data EXACTLY matching the ChatTurnAnchorsResponseDTO schema.",
    ],
    fail_fast_mandate=(
        "If the raw text does not contain any conversational dialogue between a user and an AI, "
        "you MUST return an empty turns list."
    ),
)


class ChatParserService:
    @staticmethod
    async def parse_pasted_chat(raw_paste: str, system_repo: ISystemRepository) -> ChatHistoryDTO:
        """Parse raw pasted chat logs into strict JSON using LLM.

        Args:
            raw_paste: Raw unstructured text pasted from a chat UI.
            system_repo: ISystemRepository instance.

        Returns:
            ChatHistoryDTO: Strictly typed chat history object.

        Raises:
            AppException (EMPTY_INPUT): If input is empty.
            AppException (CONFIGURATION_ERROR): If LLM client fails to initialize.
            AppException (VALIDATION_FAILED): If the LLM output violates the Pydantic schema or does not contain a valid dialogue.
            AppException (PARSING_FAILED): If anchors cannot be found or are out of order.
            AppException (INTERNAL_SERVER_ERROR): If generation fails completely.
        """
        logger.debug("[ChatParser] parse_pasted_chat CALLED")

        if not raw_paste or not raw_paste.strip():
            # Fail Fast: Cannot parse empty text
            msg = "ChatParser received empty input."
            logger.error("[ChatParser] %s: %s", ErrorCodes.EMPTY_INPUT.name, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.EMPTY_INPUT.value},
            )

        # Initialize LLM Client via Strategy Pattern
        try:
            # Strategy must exist in the system model_registry
            llm_client = await LLMClient.from_strategy("fast", repository=system_repo, pipeline_name="chat_parser")

            executor = LLMTaskExecutor(prompt_compiler=PromptCompiler())
        except ConfigurationError as e:
            msg = f"Failed to initialize LLMClient for ChatParser: {e.message}"
            logger.error("[ChatParser] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            ) from e

        # Construct the Prompt
        # Mandates: Strip all AI UI fluff (Regenerate, Copy code, etc)
        # Role Segregation: Isolated System Instruction prevents prompt injection
        messages = [
            {"role": "system", "content": _SYSTEM_INSTRUCTION},
            {
                "role": "user",
                "content": (
                    "<context>\nHere is the raw text to process:\n</context>\n"
                    f"<source_data>\n{raw_paste}\n</source_data>\n"
                ),
            },
        ]

        try:
            # V2 Strict Output Generation: Anchor-based boundary extraction
            parsed_anchors, _ = await executor.execute_structured_task(
                client=llm_client,
                messages=messages,
                response_model=ChatTurnAnchorsResponseDTO,
                validation_context={"execution_id": "global", "step_id": "chat_parser"},
            )

            if not parsed_anchors.turns:
                msg = "Fail-Fast: Raw text did not contain a valid dialogue/conversation."
                logger.error("[ChatParser] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            # Monotonic verbatim anchor slicing
            turns: list[ChatMessageDTO] = []
            current_pos = 0
            for turn in parsed_anchors.turns:
                start_idx = raw_paste.find(turn.start_phrase, current_pos)
                if start_idx == -1:
                    msg = f"Start anchor not found in source text after position {current_pos}: '{turn.start_phrase}'"
                    logger.error("[ChatParser] %s: %s", ErrorCodes.PARSING_FAILED.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": ErrorCodes.PARSING_FAILED.value, "anchor": turn.start_phrase},
                    )

                end_idx = raw_paste.find(turn.end_phrase, start_idx)
                if end_idx == -1:
                    msg = f"End anchor not found in source text after position {start_idx}: '{turn.end_phrase}'"
                    logger.error("[ChatParser] %s: %s", ErrorCodes.PARSING_FAILED.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": ErrorCodes.PARSING_FAILED.value, "anchor": turn.end_phrase},
                    )

                end_idx += len(turn.end_phrase)
                content = raw_paste[start_idx:end_idx].strip(" \t\r\n")
                if content:
                    turns.append(ChatMessageDTO(role=turn.speaker, content=content))
                current_pos = end_idx

            if not turns:
                msg = "Fail-Fast: Raw text did not contain valid dialogue turns after anchor slicing."
                logger.error("[ChatParser] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            logger.info("[ChatParser] Parsing successful. Extracted %s messages.", len(turns))
            return ChatHistoryDTO(conversation=turns)

        except ValidationError as e:
            msg = f"LLM output validation failed to match ChatTurnAnchorsResponseDTO schema: {e}"
            logger.error("[ChatParser] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "original_error": str(e)},
            ) from e
        except json.JSONDecodeError as e:
            msg = f"LLM returned invalid JSON: {e}"
            logger.error("[ChatParser] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "original_error": str(e)},
            ) from e
        except AppException:
            raise
        except Exception as e:
            msg = f"LLM generation failed: {e}"
            logger.error("[ChatParser] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_502_BAD_GATEWAY,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            ) from e
