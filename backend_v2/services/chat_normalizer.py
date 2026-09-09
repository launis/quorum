"""Chat Normalizer Service for deterministic chat parsing, cleaning, and formatting.

This service normalizes unstructured pasted dialogue logs, JSON chat sequences,
and markdown-fenced transcripts into strictly typed ProcessedChatDTO instances.
It enforces non-destructive structural normalization (preserving paragraphs and tables)
and guarantees preservation of injected cryptographic Unicode noise markers in user turns.
"""

from __future__ import annotations

import html
import logging
import re
import unicodedata

from fastapi import status
from pydantic import TypeAdapter, ValidationError

from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.inputs import ProcessedChatDTO
from backend_v2.models.v2_core import ChatHistoryDTO, ChatMessageDTO
from backend_v2.services.chat_parser import ChatParserService

logger = logging.getLogger(__name__)

# Closed set of recognized conversational role labels
USER_ROLE_LABELS: frozenset[str] = frozenset({"user", "human", "you", "käyttäjä", "sinä", "ihminen"})
AI_ROLE_LABELS: frozenset[str] = frozenset(
    {"assistant", "ai", "chatgpt", "claude", "gemini", "assistentti", "avustaja", "tekoäly"}
)
# TODO(multi-lang): Expand role label vocabularies if non-Fi/En languages are formally adopted.

_ZERO_WIDTH_CHARS_PATTERN: re.Pattern[str] = re.compile(r"[\u200b\u200c\u200d\ufeff\u00ad]")
_CONSECUTIVE_NEWLINES_PATTERN: re.Pattern[str] = re.compile(r"\n\s*\n\s*\n+")
_HORIZONTAL_ASCII_WHITESPACE_PATTERN: re.Pattern[str] = re.compile(r"[ \t]+")

_KNOWN_FLUFF_EXACT_LINES: frozenset[str] = frozenset(
    {
        "copy code",
        "copy",
        "edit",
        "share",
        "regenerate",
        "retry",
        "listen",
        "kuuntele",
        "show drafts",
        "näytä luonnokset",
        "was this response better or worse?",
        "good response",
        "bad response",
        "thumbs up",
        "thumbs down",
    }
)

_KNOWN_FLUFF_SUBSTRINGS: tuple[str, ...] = (
    "chatgpt can make mistakes",
    "chatgpt may produce inaccurate",
    "gemini may display inaccurate info",
    "claude can make mistakes",
    "claude is an ai",
)

_KNOWN_FLUFF_LINE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^chatgpt\s+(?:4o|4o-mini|4|3\.5|mini|plus|team|enterprise)(?:\s+.*)?$", re.IGNORECASE),
    re.compile(r"^gemini\s+(?:advanced|pro|flash|1\.5|2\.0)(?:\s+.*)?$", re.IGNORECASE),
    re.compile(r"^searched\s+\d+\s+sites?$", re.IGNORECASE),
)


class ChatNormalizerService:
    """Service for parsing, normalizing, and assembling conversational transcripts.

    Provides deterministic fast-path regex parsing for structured dialogues,
    preservative text cleaning for downstream LLM cognition, and XML segregation.
    """

    @staticmethod
    def strip_known_ui_fluff(raw_text: str) -> str:
        """Deterministically strip known web UI artifacts from pasted chat transcripts.

        Removes web interface disclaimers, action buttons ('Copy code', 'Edit', 'Share'),
        and model switcher labels from ChatGPT, Google Gemini, and Claude while strictly
        preserving content inside markdown code fences.

        Args:
            raw_text: Uncleaned raw text pasted from a browser chat window.

        Returns:
            Cleaned text with UI fluff lines eliminated.
        """
        if not raw_text:
            return ""

        lines = raw_text.splitlines()
        cleaned_lines: list[str] = []
        in_code_fence = False

        for line in lines:
            trimmed = line.strip()
            if trimmed.startswith("```"):
                in_code_fence = not in_code_fence
                cleaned_lines.append(line)
                continue

            if in_code_fence:
                cleaned_lines.append(line)
                continue

            lower_trimmed = trimmed.lower()

            # 1. Exact match against known button/action labels
            if lower_trimmed in _KNOWN_FLUFF_EXACT_LINES:
                continue

            # 2. Pattern match for model headers / search status
            if any(p.match(trimmed) for p in _KNOWN_FLUFF_LINE_PATTERNS):
                continue

            # 3. Substring match for short disclaimer footers (< 140 chars)
            if len(trimmed) < 140 and any(s in lower_trimmed for s in _KNOWN_FLUFF_SUBSTRINGS):
                continue

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    @staticmethod
    def strip_code_fences(text: str) -> str:
        """Strip markdown code fence wrappers from raw text.

        Args:
            text: The raw input string potentially wrapped in triple backticks.

        Returns:
            The un-fenced inner text with leading and trailing ASCII whitespace stripped.
        """
        stripped = text.strip(" \t\r\n")
        if stripped.startswith("```"):
            first_newline = stripped.find("\n")
            if first_newline != -1:
                stripped = stripped[first_newline + 1 :]
            else:
                stripped = ""
            if stripped.endswith("```"):
                stripped = stripped[:-3].rstrip(" \t\r\n")
        return stripped.strip(" \t\r\n")

    @staticmethod
    def try_parse_json(text: str) -> ChatHistoryDTO | None:
        """Attempt to deserialize chat text as raw or fenced JSON into ChatHistoryDTO.

        Args:
            text: Raw input string containing possible JSON payload.

        Returns:
            ChatHistoryDTO if JSON matches schema, otherwise None.
        """
        stripped = ChatNormalizerService.strip_code_fences(text)
        if stripped.startswith("{"):
            try:
                return ChatHistoryDTO.model_validate_json(stripped)
            except ValidationError, ValueError:
                return None
        elif stripped.startswith("["):
            try:
                messages = TypeAdapter(list[ChatMessageDTO]).validate_json(stripped)
                return ChatHistoryDTO(conversation=messages)
            except ValidationError, ValueError:
                return None
        return None

    @staticmethod
    def try_parse_fast_path(text: str) -> ChatHistoryDTO | None:
        """Deterministically parse standard colon-delimited dialogues via regex.

        Requires at least two turns containing at least one user turn and at least
        one AI turn using closed label vocabularies.

        Args:
            text: Raw conversational text.

        Returns:
            ChatHistoryDTO if fast-path parsing succeeded, otherwise None.
        """
        stripped = ChatNormalizerService.strip_code_fences(text)
        lines = stripped.splitlines()

        # Anchored role prefix regex at start of line with strict ASCII whitespace matching
        role_pattern = re.compile(r"^([A-Za-zäöåÄÖÅ0-9_\- \t]{2,30})[ \t]*:[ \t]*(.*)$")

        turns: list[ChatMessageDTO] = []
        current_role: str | None = None
        current_content_lines: list[str] = []

        for line in lines:
            match = role_pattern.match(line)
            if match:
                prefix = match.group(1).strip().lower()
                content_start = match.group(2)
                matched_role: str | None = None
                if prefix in USER_ROLE_LABELS:
                    matched_role = "user"
                elif prefix in AI_ROLE_LABELS:
                    matched_role = "ai"

                if matched_role is not None:
                    # Save completed previous turn if present
                    if current_role is not None and current_content_lines:
                        full_content = "\n".join(current_content_lines).strip(" \t\r\n")
                        if full_content:
                            turns.append(ChatMessageDTO(role=current_role, content=full_content))
                    current_role = matched_role
                    current_content_lines = []
                    if content_start:
                        current_content_lines.append(content_start)
                    continue

            # Continuation line of current turn
            if current_role is not None:
                current_content_lines.append(line)

        # Flush final turn
        if current_role is not None and current_content_lines:
            full_content = "\n".join(current_content_lines).strip(" \t\r\n")
            if full_content:
                turns.append(ChatMessageDTO(role=current_role, content=full_content))

        # Validate minimum structural requirements
        if len(turns) < 2:
            return None

        has_user = any(t.role == "user" for t in turns)
        has_ai = any(t.role == "ai" for t in turns)
        if not (has_user and has_ai):
            return None

        return ChatHistoryDTO(conversation=turns)

    @staticmethod
    def clean_turn_content(content: str) -> str:
        r"""Apply non-destructive, noise-preserving normalization to turn content.

        1. Applies Unicode NFC normalization (UAX #15) for stable character encoding.
        2. Strips zero-width characters (BOM, ZWSP, soft hyphens).
        3. Consolidates structural linebreaks without crushing markdown tables or lists.
        4. Collapses horizontal ASCII whitespace ([ \t]+) while preserving all
           Unicode whitespace variants (\u00a0, \u2002, etc.).

        Args:
            content: Raw text content of a dialogue turn.

        Returns:
            Cleaned and normalized turn content.
        """
        if not content:
            return ""

        # 1. Unicode NFC composition
        normalized = unicodedata.normalize("NFC", content)

        # 2. Strip zero-width and invisible formatting characters
        normalized = _ZERO_WIDTH_CHARS_PATTERN.sub("", normalized)

        # 3. Consolidate structural paragraph linebreaks
        normalized = _CONSECUTIVE_NEWLINES_PATTERN.sub("\n\n", normalized)

        # 4. Collapse horizontal ASCII whitespace line-by-line, preserving Unicode spaces
        cleaned_lines: list[str] = []
        for line in normalized.splitlines():
            collapsed_line = _HORIZONTAL_ASCII_WHITESPACE_PATTERN.sub(" ", line).strip(" \t")
            cleaned_lines.append(collapsed_line)

        # Join lines and strip leading/trailing empty lines
        return "\n".join(cleaned_lines).strip(" \t\r\n")

    @staticmethod
    def build_processed_chat(chat_dto: ChatHistoryDTO) -> ProcessedChatDTO:
        """Assemble a ChatHistoryDTO into segregated streams in ProcessedChatDTO.

        Args:
            chat_dto: The typed chat history object containing conversation turns.

        Returns:
            ProcessedChatDTO with combined (XML-fenced), user_only, and ai_only streams.
        """
        combined_lines: list[str] = []
        user_lines: list[str] = []
        ai_lines: list[str] = []

        for turn in chat_dto.conversation:
            cleaned = ChatNormalizerService.clean_turn_content(turn.content)
            if not cleaned:
                continue

            if turn.role.lower() == "user":
                escaped = html.escape(cleaned, quote=False)
                combined_lines.append(f"<user_payload>\n{escaped}\n</user_payload>")
                user_lines.append(cleaned)
            else:
                combined_lines.append(f"<ai_draft_context>\n{cleaned}\n</ai_draft_context>")
                ai_lines.append(cleaned)

        return ProcessedChatDTO(
            combined="\n\n".join(combined_lines),
            user_only="\n\n".join(user_lines),
            ai_only="\n\n".join(ai_lines),
        )

    @staticmethod
    async def parse_chat_to_dto(
        raw_text: str,
        key: str,
        system_repo: ISystemRepository,
    ) -> ChatHistoryDTO:
        """Parse raw conversational text into a strictly typed ChatHistoryDTO.

        Args:
            raw_text: The raw chat input string.
            key: Input key identifier (e.g. 'chat_log').
            system_repo: System repository instance for fallback LLM configuration.

        Returns:
            ChatHistoryDTO containing dialogue turns.

        Raises:
            AppException: If raw_text is empty or parsing completely fails.
        """
        if not raw_text or not raw_text.strip(" \t\r\n"):
            logger.error(
                "Empty input received for chat key.",
                extra={"error_code": ErrorCodes.EMPTY_INPUT.name, "input_key": key},
            )
            raise AppException(
                message=f"Empty input received for {key}.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.EMPTY_INPUT.value, "input_key": key},
            )

        # 1. Try structured JSON parsing
        chat_dto = ChatNormalizerService.try_parse_json(raw_text)
        if chat_dto:
            logger.info("[ChatNormalizer] Valid JSON chat detected for %s.", key)
        else:
            # Clean known UI fluff for fast-path regex and LLM fallback
            cleaned_text = ChatNormalizerService.strip_known_ui_fluff(raw_text)

            # 2. Try fast-path regex parsing
            chat_dto = ChatNormalizerService.try_parse_fast_path(cleaned_text)
            if chat_dto:
                logger.info("[ChatNormalizer] Fast-path regex matched dialogue turns for %s.", key)
            else:
                # 3. Fallback to LLM parser
                logger.info("[ChatNormalizer] Falling back to ChatParserService LLM parsing for %s...", key)
                try:
                    chat_dto = await ChatParserService.parse_pasted_chat(cleaned_text, system_repo=system_repo)
                except AppException:
                    raise
                except Exception as e:
                    logger.error(
                        "LLM chat parser failed for %s: %s",
                        key,
                        e,
                        extra={"error_code": ErrorCodes.PARSING_FAILED.name, "input_key": key},
                    )
                    raise AppException(
                        message=f"Failed to parse dialogue conversation for {key}: {e}",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": ErrorCodes.PARSING_FAILED.value, "input_key": key},
                    ) from e

        if not chat_dto or not chat_dto.conversation:
            logger.error(
                "Failed to parse conversation turns.",
                extra={"error_code": ErrorCodes.PARSING_FAILED.name, "input_key": key},
            )
            raise AppException(
                message=f"Failed to parse dialogue conversation for {key}.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.PARSING_FAILED.value, "input_key": key},
            )

        return chat_dto

    @staticmethod
    async def normalize_chat(
        raw_text: str,
        key: str,
        system_repo: ISystemRepository,
    ) -> ProcessedChatDTO:
        """Orchestrate the complete chat ingestion, parsing, and normalization pipeline.

        Args:
            raw_text: The raw chat input string.
            key: Input key identifier (e.g. 'chat_log').
            system_repo: System repository instance for fallback LLM configuration.

        Returns:
            ProcessedChatDTO containing segregated dialogue streams.

        Raises:
            AppException: If raw_text is empty or parsing completely fails.
        """
        chat_dto = await ChatNormalizerService.parse_chat_to_dto(raw_text, key, system_repo)
        return ChatNormalizerService.build_processed_chat(chat_dto)
