"""Service for parsing unstructured pasted chat logs into typed conversation structures.

Uses CognitiveTier.FAST via LLMTaskExecutor to decouple human conversation from UI artifacts
using monotonic boundary anchors and verbatim substring slicing.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Annotated

from fastapi import status
from pydantic import ConfigDict, Field, ValidationError

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.llm.prompt_builder import build_system_directive
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.system_config import ChatHistoryDTO, ChatMessageDTO
from backend_v2.models.dtos.ingress import ChatTurnAnchorsResponseDTO
from backend_v2.models.enums import CognitiveTier, LLMProvider
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.settings import get_settings

__all__ = [
    "AnchorSpanDTO",
    "ChatParserService",
]

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
        (
            "NEVER generate, summarize, paraphrase, or rewrite the turn content. "
            "The extraction MUST be 100% exact verbatim substrings."
        ),
        (
            "Include all formatting characters, markdown syntax, and table borders (such as '|') "
            "exactly as they appear in the source text without omitting or stripping them."
        ),
        "Ignore all UI fluff (e.g., 'Copy code', 'Share', 'Regenerate', sidebar text).",
        "Return the data EXACTLY matching the ChatTurnAnchorsResponseDTO schema.",
    ],
    fail_fast_mandate=(
        "If the raw text does not contain any conversational dialogue between a user and an AI, "
        "you MUST return an empty turns list."
    ),
)


class AnchorSpanDTO(V2CoreBase):
    """Character offset boundaries of an anchor phrase within text.

    Attributes:
        start: Inclusive start character offset within the source text.
        end: Exclusive end character offset within the source text.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    start: Annotated[int, Field(ge=0, description="Start character offset")]
    end: Annotated[int, Field(ge=0, description="End character offset")]


class ChatParserService:
    """Service for parsing conversational text using boundary anchors and verbatim slicing."""

    @staticmethod
    def _log_parser_error(
        error_code: ErrorCodes,
        message: str,
        anchor: str | None = None,
    ) -> None:
        """Emit a structured RFC 7807 error log entry with stack context for chat parser failures.

        Args:
            error_code: Canonical RFC 7807 error identifier.
            message: Diagnostic error message describing the failure.
            anchor: Optional boundary phrase that failed monotonic matching.
        """
        if anchor is not None:
            logger.error(
                "[ChatParser] %s: %s",
                error_code.name,
                message,
                exc_info=True,
                extra={"error_code": error_code.name, "anchor": anchor},
            )
            return

        logger.error(
            "[ChatParser] %s: %s",
            error_code.name,
            message,
            exc_info=True,
            extra={"error_code": error_code.name},
        )

    @staticmethod
    def _validate_raw_paste_input(raw_paste: str) -> None:
        """Validate non-empty and minimum character length invariants before LLM initialization.

        Args:
            raw_paste: Raw unstructured text pasted from a chat UI.

        Raises:
            AppException: If input is empty/whitespace (EMPTY_INPUT) or shorter than
                settings.llm_min_payload_length (VALIDATION_FAILED).
        """
        if not raw_paste or not raw_paste.strip():
            msg = "ChatParser received empty input."
            ChatParserService._log_parser_error(ErrorCodes.EMPTY_INPUT, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.EMPTY_INPUT.value},
            )

        stripped = raw_paste.strip()
        min_length = get_settings().llm_min_payload_length
        if len(stripped) < min_length:
            msg = f"ChatParser input length ({len(stripped)}) is below minimum required payload length ({min_length})."
            ChatParserService._log_parser_error(ErrorCodes.VALIDATION_FAILED, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

    @staticmethod
    def _find_anchor_span(
        text: str,
        phrase: str,
        start_pos: int,
    ) -> AnchorSpanDTO:
        """Find the start and end indices of an anchor phrase in text.

        First attempts exact substring match via str.find(). If that fails due to
        Unicode whitespace variations (e.g. non-breaking spaces, en spaces, newlines),
        falls back to exact token sequence matching with flexible whitespace.
        If that fails, falls back to delimiter-flexible token sequence matching
        to handle phrases separated by markdown table pipes and borders.

        Args:
            text: Source text to search within.
            phrase: Target anchor phrase to locate.
            start_pos: Monotonic start position in text.

        Returns:
            Character offset boundaries (start, end) of phrase in text.

        Raises:
            ValueError: If phrase cannot be found after start_pos or contains no valid tokens.
        """
        clean_phrase = phrase.strip()
        if not clean_phrase:
            msg = "Anchor phrase cannot be empty"
            raise ValueError(msg)

        # 1. Exact verbatim fast path
        idx = text.find(clean_phrase, start_pos)
        if idx != -1:
            return AnchorSpanDTO(start=idx, end=idx + len(clean_phrase))

        # 2. Whitespace-flexible exact token sequence match
        words = clean_phrase.split()
        pattern = re.compile(r"\s+".join(map(re.escape, words)))
        match = pattern.search(text, start_pos)
        if match:
            return AnchorSpanDTO(start=match.start(), end=match.end())

        # 3. Delimiter-flexible token sequence match for markdown tables
        clean_tokens = [t.strip("| \t\r\n") for t in words if t.strip("| \t\r\n")]
        if not clean_tokens:
            msg = f"Anchor phrase contains no valid tokens after delimiter normalization: '{phrase}'"
            raise ValueError(msg)

        table_pattern = re.compile(r"[\s|]+".join(map(re.escape, clean_tokens)))
        table_match = table_pattern.search(text, start_pos)
        if table_match:
            return AnchorSpanDTO(start=table_match.start(), end=table_match.end())

        msg = f"Anchor phrase not found in source text after position {start_pos}: '{phrase}'"
        raise ValueError(msg)

    @staticmethod
    def _resolve_turn_anchor(
        raw_paste: str,
        phrase: str,
        search_from: int,
        boundary_label: str,
    ) -> AnchorSpanDTO:
        """Resolve a turn boundary anchor monotonically or raise a RFC 7807 PARSING_FAILED error.

        Args:
            raw_paste: Source text being sliced into turns.
            phrase: Verbatim boundary phrase returned by the LLM.
            search_from: Monotonic character offset from which searching starts.
            boundary_label: Boundary role label ('Start' or 'End') for diagnostics.

        Returns:
            Resolved AnchorSpanDTO within raw_paste.

        Raises:
            AppException: If the anchor phrase cannot be found monotonically (PARSING_FAILED).
        """
        try:
            return ChatParserService._find_anchor_span(raw_paste, phrase, search_from)
        except ValueError as e:
            msg = f"{boundary_label} anchor not found in source text after position {search_from}: '{phrase}'"
            ChatParserService._log_parser_error(ErrorCodes.PARSING_FAILED, msg, anchor=phrase)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.PARSING_FAILED.value, "anchor": phrase},
            ) from e

    @staticmethod
    async def _initialize_llm_client(
        system_repo: ISystemRepository,
        registry_id: str | None = None,
        provider: LLMProvider | None = None,
    ) -> LLMClient:
        """Initialize the FAST cognitive tier LLM client for chat parsing.

        Args:
            system_repo: System configuration repository instance.
            registry_id: Optional authoritative model registry ID.
            provider: Optional explicit provider override.

        Returns:
            Initialized LLM client bound to the chat_parser pipeline.

        Raises:
            AppException: If LLM client initialization fails (CONFIGURATION_ERROR).
        """
        try:
            if registry_id is not None or provider is not None:
                return await LLMClient.from_tier(
                    CognitiveTier.FAST,
                    repository=system_repo,
                    pipeline_name="chat_parser",
                    registry_id=registry_id,
                    provider=provider,
                )
            return await LLMClient.from_tier(
                CognitiveTier.FAST,
                repository=system_repo,
                pipeline_name="chat_parser",
            )
        except ConfigurationError as e:
            msg = f"Failed to initialize LLMClient for ChatParser: {e.message}"
            ChatParserService._log_parser_error(ErrorCodes.CONFIGURATION_ERROR, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            ) from e

    @staticmethod
    def _extract_turns_from_anchors(
        raw_paste: str,
        parsed_anchors: ChatTurnAnchorsResponseDTO,
    ) -> list[ChatMessageDTO]:
        """Slice verbatim conversational turns from raw text using monotonic boundary anchors.

        Args:
            raw_paste: Raw unstructured text pasted from a chat UI.
            parsed_anchors: Validated boundary anchors returned by the LLM.

        Returns:
            Extracted chronological list of chat messages.

        Raises:
            AppException: If turns list is empty (VALIDATION_FAILED) or an anchor cannot be
                located monotonically in source text (PARSING_FAILED).
        """
        if not parsed_anchors.turns:
            msg = "Fail-Fast: Raw text did not contain a valid dialogue/conversation."
            ChatParserService._log_parser_error(ErrorCodes.VALIDATION_FAILED, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        turns: list[ChatMessageDTO] = []
        current_pos = 0
        for turn in parsed_anchors.turns:
            start_span = ChatParserService._resolve_turn_anchor(
                raw_paste=raw_paste,
                phrase=turn.start_phrase,
                search_from=current_pos,
                boundary_label="Start",
            )
            end_span = ChatParserService._resolve_turn_anchor(
                raw_paste=raw_paste,
                phrase=turn.end_phrase,
                search_from=start_span.start,
                boundary_label="End",
            )
            content = raw_paste[start_span.start : end_span.end].strip(" \t\r\n")
            if content:
                turns.append(ChatMessageDTO(role=turn.speaker, content=content))
            current_pos = end_span.end

        if not turns:
            msg = "Fail-Fast: Raw text did not contain valid dialogue turns after anchor slicing."
            ChatParserService._log_parser_error(ErrorCodes.VALIDATION_FAILED, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        return turns

    @staticmethod
    async def parse_pasted_chat(
        raw_paste: str,
        system_repo: ISystemRepository,
        registry_id: str | None = None,
        provider: LLMProvider | None = None,
    ) -> ChatHistoryDTO:
        """Parse raw pasted chat logs into typed ChatHistoryDTO turns using LLM boundary anchors.

        Args:
            raw_paste: Raw unstructured text pasted from a chat UI.
            system_repo: System repository instance for model registry resolution.
            registry_id: Optional authoritative model registry ID.
            provider: Optional explicit provider override.

        Returns:
            Strictly typed chat history object.

        Raises:
            AppException: If input is empty (EMPTY_INPUT), input is shorter than minimum payload
                length or violates output schema (VALIDATION_FAILED), LLM initialization fails
                (CONFIGURATION_ERROR), anchors cannot be located (PARSING_FAILED), or LLM
                execution fails (INTERNAL_SERVER_ERROR).
        """
        logger.debug("[ChatParser] parse_pasted_chat CALLED")
        ChatParserService._validate_raw_paste_input(raw_paste)

        llm_client = await ChatParserService._initialize_llm_client(
            system_repo=system_repo,
            registry_id=registry_id,
            provider=provider,
        )
        executor = LLMTaskExecutor(prompt_compiler=PromptCompiler())

        user_content = TemplateProcessor.render_prompt(
            t"<context>\nHere is the raw text to process:\n</context>\n<source_data>\n{raw_paste}\n</source_data>\n"
        )
        messages = [
            ChatMessageDTO(role="system", content=_SYSTEM_INSTRUCTION),
            ChatMessageDTO(role="user", content=user_content),
        ]

        try:
            parsed_anchors, _ = await executor.execute_structured_task(
                client=llm_client,
                messages=messages,
                response_model=ChatTurnAnchorsResponseDTO,
                validation_context={"execution_id": "global", "step_id": "chat_parser"},
            )
            turns = ChatParserService._extract_turns_from_anchors(raw_paste, parsed_anchors)
            logger.info("[ChatParser] Parsing successful. Extracted %s messages.", len(turns))
            return ChatHistoryDTO(conversation=turns)

        except (ValidationError, json.JSONDecodeError) as e:
            msg = f"LLM output validation failed for ChatTurnAnchorsResponseDTO: {e}"
            ChatParserService._log_parser_error(ErrorCodes.VALIDATION_FAILED, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "original_error": str(e)},
            ) from e
        except AppException:
            raise
        except Exception as e:
            msg = f"LLM generation failed: {e}"
            ChatParserService._log_parser_error(ErrorCodes.INTERNAL_SERVER_ERROR, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_502_BAD_GATEWAY,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            ) from e
