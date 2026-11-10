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

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import ChatHistoryDTO, ChatMessageDTO
from backend_v2.models.dtos.inputs import ProcessedChatDTO
from backend_v2.services.chat_parser import ChatParserService

__all__ = [
    "AI_ROLE_LABELS",
    "USER_ROLE_LABELS",
    "ChatNormalizerService",
]

logger = logging.getLogger(__name__)

# Closed English and Finnish conversational role label vocabularies for deterministic fast-path parsing.
USER_ROLE_LABELS: frozenset[str] = frozenset({"user", "human", "you", "käyttäjä", "sinä", "ihminen"})
AI_ROLE_LABELS: frozenset[str] = frozenset(
    {"assistant", "ai", "chatgpt", "claude", "gemini", "assistentti", "avustaja", "tekoäly"}
)

_ZERO_WIDTH_CHARS_PATTERN: re.Pattern[str] = re.compile(r"[\u200b\u200c\u200d\ufeff\u00ad]")
_CONSECUTIVE_NEWLINES_PATTERN: re.Pattern[str] = re.compile(r"\n\s*\n\s*\n+")
_HORIZONTAL_ASCII_WHITESPACE_PATTERN: re.Pattern[str] = re.compile(r"[ \t]+")
_FAST_PATH_ROLE_PATTERN: re.Pattern[str] = re.compile(r"^([A-Za-zäöåÄÖÅ0-9_\- \t]{2,30})[ \t]*:[ \t]*(.*)$")

_ATTACHMENT_CHIP_LABELS: frozenset[str] = frozenset({"pdf", "liite"})
_ATTACHMENT_EXTENSIONS: tuple[str, ...] = (".pdf", ".docx", ".txt", ".csv", ".xlsx", ".md")
_MAX_ATTACHMENT_TITLE_WORDS: int = 4
_MAX_DISCLAIMER_FOOTER_LENGTH: int = 140
_MIN_DIALOGUE_TURNS: int = 2
_MIN_TABLE_ROWS: int = 2

_CHAT_MESSAGE_LIST_ADAPTER: TypeAdapter[list[ChatMessageDTO]] = TypeAdapter(list[ChatMessageDTO])

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
        "expand_more",
        "expand_less",
        "näytä lisää",
        "näytä lisää ⌵",
        "näytä lisää v",
        "show more",
        "show more ⌵",
        "show more v",
        "lue lisää",
        "katso lisää",
        "read more",
        "pidätkö tästä persoonasta?",
        "oliko tämä vastaus hyödyllinen?",
        "lataa, lue ja analysoi",
        "keskustelu geminin kanssa",
        "conversation with gemini",
        "uusi keskustelu",
        "new chat",
    }
)

_KNOWN_FLUFF_SUBSTRINGS: tuple[str, ...] = (
    "chatgpt can make mistakes",
    "chatgpt may produce inaccurate",
    "gemini may display inaccurate info",
    "gemini on tekoäly ja voi tehdä virheitä",
    "claude can make mistakes",
    "claude is an ai",
)

_KNOWN_FLUFF_LINE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^chatgpt\s+(?:4o|4o-mini|4|3\.5|mini|plus|team|enterprise)(?:\s+.*)?$", re.IGNORECASE),
    re.compile(r"^gemini\s+(?:advanced|pro|flash|1\.5|2\.0)(?:\s+.*)?$", re.IGNORECASE),
    re.compile(r"^searched\s+\d+\s+sites?$", re.IGNORECASE),
    re.compile(
        r"^(?:ma|ti|ke|to|pe|la|su|mon|tue|wed|thu|fri|sat|sun)\s+\d{1,2}\.\d{1,2}\.?\s+(?:klo\s+)?\d{1,2}[\.:]\d{2}$",
        re.IGNORECASE,
    ),
    re.compile(r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$", re.IGNORECASE),
)


class ChatNormalizerService:
    """Service for parsing, normalizing, and assembling conversational transcripts.

    Provides deterministic fast-path regex parsing for structured dialogues,
    preservative text cleaning for downstream LLM cognition, and XML segregation.
    """

    @staticmethod
    def _try_consume_attachment_chip_pair(
        lines: list[str],
        index: int,
        cleaned_lines: list[str],
    ) -> int | None:
        """Detect and normalize two-line browser attachment chips into canonical annotations.

        Args:
            lines: Source transcript lines split by linebreaks.
            index: Current line index outside markdown code fences.
            cleaned_lines: Output accumulator to append normalized `[Liite: <filename>]` lines to.

        Returns:
            Next line index after consuming the attachment pair, or None if not an attachment pair.
        """
        n = len(lines)
        if index + 1 >= n:
            return None

        j = index + 1
        while j < n and not lines[j].strip():
            j += 1
        if j >= n:
            return None

        trimmed = lines[index].strip()
        next_trimmed = lines[j].strip()

        if (
            trimmed
            and not trimmed.startswith("[Liite:")
            and next_trimmed.lower() in _ATTACHMENT_CHIP_LABELS
            and (
                trimmed.lower().endswith(_ATTACHMENT_EXTENSIONS)
                or (len(trimmed.split()) <= _MAX_ATTACHMENT_TITLE_WORDS and not any(ch in trimmed for ch in ":/?#\n"))
            )
        ):
            cleaned_lines.append(f"[Liite: {trimmed}]")
            return j + 1

        if (
            trimmed.lower() in _ATTACHMENT_CHIP_LABELS
            and next_trimmed
            and not next_trimmed.startswith("[Liite:")
            and (
                next_trimmed.lower().endswith(_ATTACHMENT_EXTENSIONS)
                or len(next_trimmed.split()) <= _MAX_ATTACHMENT_TITLE_WORDS
            )
        ):
            fname = next_trimmed if "." in next_trimmed else f"{next_trimmed}.pdf"
            cleaned_lines.append(f"[Liite: {fname}]")
            return j + 1

        return None

    @staticmethod
    def _is_known_fluff_line(trimmed: str) -> bool:
        """Evaluate whether a trimmed non-fenced line matches known web UI artifacts.

        Args:
            trimmed: Leading/trailing whitespace-trimmed line outside code fences.

        Returns:
            True if the line matches a button label, header pattern, or disclaimer footer.
        """
        lower_trimmed = trimmed.lower()
        if lower_trimmed in _KNOWN_FLUFF_EXACT_LINES:
            return True
        if any(p.match(trimmed) for p in _KNOWN_FLUFF_LINE_PATTERNS):
            return True
        return len(trimmed) < _MAX_DISCLAIMER_FOOTER_LENGTH and any(s in lower_trimmed for s in _KNOWN_FLUFF_SUBSTRINGS)

    @staticmethod
    def strip_known_ui_fluff(raw_text: str) -> str:
        """Deterministically strip known web UI artifacts from pasted chat transcripts.

        Removes web interface disclaimers, action buttons ('Copy code', 'Edit', 'Share'),
        and model switcher labels from ChatGPT, Google Gemini, and Claude while strictly
        preserving content inside markdown code fences. Normalizes attachment chip pairs
        into canonical [Liite: <filename>] annotations.

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
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            trimmed = line.strip()

            if trimmed.startswith("```"):
                in_code_fence = not in_code_fence
                cleaned_lines.append(line)
                i += 1
                continue

            if in_code_fence:
                cleaned_lines.append(line)
                i += 1
                continue

            next_index = ChatNormalizerService._try_consume_attachment_chip_pair(lines, i, cleaned_lines)
            if next_index is not None:
                i = next_index
                continue

            if not ChatNormalizerService._is_known_fluff_line(trimmed):
                cleaned_lines.append(line)
            i += 1

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
    def _deserialize_json_chat(stripped: str) -> ChatHistoryDTO:
        """Deserialize stripped JSON object or array text into a typed ChatHistoryDTO.

        Args:
            stripped: Code-fence-stripped text starting with '{' or '['.

        Returns:
            Populated ChatHistoryDTO on schema match, or an empty ChatHistoryDTO on validation failure.
        """
        if stripped.startswith("{"):
            try:
                return ChatHistoryDTO.model_validate_json(stripped)
            except ValidationError, ValueError:
                return ChatHistoryDTO(conversation=[])
        try:
            messages = _CHAT_MESSAGE_LIST_ADAPTER.validate_json(stripped)
            return ChatHistoryDTO(conversation=messages)
        except ValidationError, ValueError:
            return ChatHistoryDTO(conversation=[])

    @staticmethod
    def try_parse_json(text: str) -> ChatHistoryDTO | None:
        """Attempt to deserialize chat text as raw or fenced JSON into ChatHistoryDTO.

        Args:
            text: Raw input string containing possible JSON payload.

        Returns:
            ChatHistoryDTO if JSON matches schema with at least one turn, otherwise None.
        """
        stripped = ChatNormalizerService.strip_code_fences(text)
        if not stripped.startswith(("{", "[")):
            return None
        parsed = ChatNormalizerService._deserialize_json_chat(stripped)
        if not parsed.conversation:
            return None
        return parsed

    @staticmethod
    def _append_completed_turn(
        turns: list[ChatMessageDTO],
        role: str | None,
        content_lines: list[str],
    ) -> None:
        """Append a completed non-empty conversational turn to the turns accumulator.

        Args:
            turns: Chronological turn accumulator list.
            role: Speaker role ('user' or 'ai') of the active turn, if started.
            content_lines: Collected raw lines belonging to the active turn.
        """
        if role is not None and content_lines:
            full_content = "\n".join(content_lines).strip(" \t\r\n")
            if full_content:
                turns.append(ChatMessageDTO(role=role, content=full_content))

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

        turns: list[ChatMessageDTO] = []
        current_role: str | None = None
        current_content_lines: list[str] = []

        for line in lines:
            match = _FAST_PATH_ROLE_PATTERN.match(line)
            if match:
                prefix = match.group(1).strip().lower()
                content_start = match.group(2)
                matched_role: str | None = None
                if prefix in USER_ROLE_LABELS:
                    matched_role = "user"
                elif prefix in AI_ROLE_LABELS:
                    matched_role = "ai"

                if matched_role is not None:
                    ChatNormalizerService._append_completed_turn(turns, current_role, current_content_lines)
                    current_role = matched_role
                    current_content_lines = []
                    if content_start:
                        current_content_lines.append(content_start)
                    continue

            if current_role is not None:
                current_content_lines.append(line)

        ChatNormalizerService._append_completed_turn(turns, current_role, current_content_lines)

        if len(turns) < _MIN_DIALOGUE_TURNS:
            return None

        has_user = any(t.role == "user" for t in turns)
        has_ai = any(t.role == "ai" for t in turns)
        if not (has_user and has_ai):
            return None

        return ChatHistoryDTO(conversation=turns)

    @staticmethod
    def _format_tab_block_as_markdown(tab_block: list[str]) -> list[str]:
        """Format a block of tab-delimited lines into GitHub-Flavored Markdown table rows.

        Args:
            tab_block: Consecutive lines containing tab characters outside code fences.

        Returns:
            Markdown pipe table lines if at least two rows exist, otherwise the original lines.
        """
        if len(tab_block) < _MIN_TABLE_ROWS:
            return list(tab_block)

        rows = [line.split("\t") for line in tab_block]
        max_cols = max(len(r) for r in rows)

        formatted_rows: list[str] = []
        for idx, row in enumerate(rows):
            padded = row + [""] * (max_cols - len(row))
            sanitized_cells = [cell.strip().replace("\n", " ").replace("|", r"\|") for cell in padded]
            formatted_rows.append(f"| {' | '.join(sanitized_cells)} |")
            if idx == 0:
                formatted_rows.append(f"| {' | '.join([':---'] * max_cols)} |")

        return formatted_rows

    @staticmethod
    def normalize_tables(raw_text: str) -> str:
        r"""Convert tab-delimited tabular blocks into GitHub-Flavored Markdown tables.

        Detects blocks of 2 or more consecutive lines containing tab ('\t') characters
        outside of markdown code fences and formats them as standard Markdown pipe tables
        with header separator rows (| :--- | :--- |). Single-row tab data is rejected,
        and uneven column counts are padded with empty cells.

        Args:
            raw_text: Text potentially containing tab-delimited tabular data.

        Returns:
            Text with tab-delimited tables converted to standard Markdown pipe tables.
        """
        if not raw_text or "\t" not in raw_text:
            return raw_text

        result_lines: list[str] = []
        tab_block: list[str] = []
        in_code_fence = False

        for line in raw_text.splitlines():
            trimmed = line.strip()
            if trimmed.startswith("```"):
                if tab_block:
                    result_lines.extend(ChatNormalizerService._format_tab_block_as_markdown(tab_block))
                    tab_block = []
                in_code_fence = not in_code_fence
                result_lines.append(line)
                continue

            if in_code_fence:
                result_lines.append(line)
                continue

            if "\t" in line:
                tab_block.append(line)
            else:
                if tab_block:
                    result_lines.extend(ChatNormalizerService._format_tab_block_as_markdown(tab_block))
                    tab_block = []
                result_lines.append(line)

        if tab_block:
            result_lines.extend(ChatNormalizerService._format_tab_block_as_markdown(tab_block))

        return "\n".join(result_lines)

    @staticmethod
    def clean_turn_content(content: str) -> str:
        r"""Apply non-destructive, noise-preserving normalization to turn content.

        1. Applies Unicode NFC normalization (UAX #15) for stable character encoding.
        2. Strips zero-width characters (BOM, ZWSP, soft hyphens).
        3. Consolidates structural linebreaks without crushing markdown tables or lists.
        4. Normalizes tab-separated tabular blocks into GitHub-Flavored Markdown tables.
        5. Collapses horizontal ASCII whitespace ([ \t]+) while preserving all
           Unicode whitespace variants (\u00a0, \u2002, etc.), code blocks, and Markdown tables.

        Args:
            content: Raw text content of a dialogue turn.

        Returns:
            Cleaned and normalized turn content.
        """
        if not content:
            return ""

        normalized = unicodedata.normalize("NFC", content)
        normalized = _ZERO_WIDTH_CHARS_PATTERN.sub("", normalized)
        normalized = _CONSECUTIVE_NEWLINES_PATTERN.sub("\n\n", normalized)
        normalized = ChatNormalizerService.strip_known_ui_fluff(normalized)
        # Normalize tab-delimited tables before collapsing horizontal whitespace so tab cell boundaries survive.
        normalized = ChatNormalizerService.normalize_tables(normalized)

        cleaned_lines: list[str] = []
        in_code_fence = False
        for line in normalized.splitlines():
            trimmed = line.strip(" \t")
            if trimmed.startswith("```"):
                in_code_fence = not in_code_fence
                cleaned_lines.append(line)
                continue
            if in_code_fence:
                cleaned_lines.append(line)
                continue
            if trimmed.startswith("|") and trimmed.endswith("|"):
                cleaned_lines.append(trimmed)
            else:
                collapsed_line = _HORIZONTAL_ASCII_WHITESPACE_PATTERN.sub(" ", line).strip(" \t")
                cleaned_lines.append(collapsed_line)

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
                combined_lines.append(TemplateProcessor.render_prompt(t"<user_payload>\n{escaped}\n</user_payload>"))
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
    def _log_chat_error(error_code: ErrorCodes, message: str, key: str) -> None:
        """Emit a structured RFC 7807 error log entry with stack context for chat normalization failures.

        Args:
            error_code: Canonical RFC 7807 ErrorCodes identifier.
            message: Diagnostic failure description.
            key: Workflow input key identifier.
        """
        logger.error(
            "[ChatNormalizer] %s: %s",
            error_code.name,
            message,
            exc_info=True,
            extra={"error_code": error_code.name, "input_key": key},
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
            AppException: If raw_text is empty (ErrorCodes.EMPTY_INPUT) or parsing fails (ErrorCodes.PARSING_FAILED).
        """
        if not raw_text or not raw_text.strip(" \t\r\n"):
            ChatNormalizerService._log_chat_error(
                ErrorCodes.EMPTY_INPUT,
                f"Empty input received for chat key '{key}'.",
                key,
            )
            raise AppException(
                message=f"Empty input received for {key}.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.EMPTY_INPUT.value, "input_key": key},
            )

        chat_dto = ChatNormalizerService.try_parse_json(raw_text)
        if chat_dto is not None:
            logger.info("[ChatNormalizer] Valid JSON chat detected for %s.", key)
        else:
            cleaned_text = ChatNormalizerService.strip_known_ui_fluff(raw_text)
            chat_dto = ChatNormalizerService.try_parse_fast_path(cleaned_text)
            if chat_dto is not None:
                logger.info("[ChatNormalizer] Fast-path regex matched dialogue turns for %s.", key)
            else:
                logger.info("[ChatNormalizer] Falling back to ChatParserService LLM parsing for %s...", key)
                try:
                    chat_dto = await ChatParserService.parse_pasted_chat(cleaned_text, system_repo=system_repo)
                except AppException:
                    raise
                except Exception as exc:
                    ChatNormalizerService._log_chat_error(
                        ErrorCodes.PARSING_FAILED,
                        f"LLM chat parser failed for '{key}': {exc}",
                        key,
                    )
                    raise AppException(
                        message=f"Failed to parse dialogue conversation for {key}: {exc}",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": ErrorCodes.PARSING_FAILED.value, "input_key": key},
                    ) from exc

        if not chat_dto.conversation:
            ChatNormalizerService._log_chat_error(
                ErrorCodes.PARSING_FAILED,
                f"Failed to parse non-empty conversation turns for '{key}'.",
                key,
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
            AppException: If raw_text is empty (ErrorCodes.EMPTY_INPUT) or parsing fails (ErrorCodes.PARSING_FAILED).
        """
        chat_dto = await ChatNormalizerService.parse_chat_to_dto(raw_text, key, system_repo)
        return ChatNormalizerService.build_processed_chat(chat_dto)
