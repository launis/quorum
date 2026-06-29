"""Alias Registry Service.

Unifies external MCP searches and internal PDF sources into a common chunked representation.
Implements 'Sandwich Prompting' by chunking texts with 150-200 token overlap.
"""

from backend_v2.exceptions import ErrorCodes, SemanticEvidenceError


class AliasRegistry:
    """Manages source text chunking and alias resolution for LLM injection."""

    @classmethod
    def wrap_source_chunks(cls, text: str, source_id: str) -> list[str]:
        """Chunks text with overlap and wraps in search_result tags.

        Chunks text into approximately 1000-1500 tokens (5000 characters) with a
        150-200 token overlap (700 characters) to preserve context.

        Args:
            text: The raw source text.
            source_id: The alias ID (e.g., '<<QRM-SRC-1>>').

        Returns:
            List of XML-wrapped chunk strings.
        """
        max_chars = 5000
        overlap = 700

        if not text:
            return []

        raw_chunks: list[str] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + max_chars, text_length)

            if end < text_length:
                last_space = text.rfind(" ", end - 100, end)
                last_newline = text.rfind("\n", end - 100, end)
                break_point = max(last_space, last_newline)
                if break_point != -1:
                    end = break_point

            chunk_text = text[start:end].strip()
            if chunk_text:
                raw_chunks.append(chunk_text)

            if end >= text_length:
                break

            start = end - overlap

        total_chunks = len(raw_chunks)
        wrapped_chunks: list[str] = []
        for i, chunk_text in enumerate(raw_chunks, 1):
            wrapped = f'<search_result ID="{source_id}" chunk="{i}/{total_chunks}">\n{chunk_text}\n</search_result>'
            wrapped_chunks.append(wrapped)

        return wrapped_chunks

    @classmethod
    def resolve(cls, alias: str, alias_map: dict[str, str]) -> str:
        """Validates the alias and returns the mapped source.

        Args:
            alias: The source alias (e.g., '<<QRM-SRC-1>>').
            alias_map: Mapping of aliases to source identifiers.

        Returns:
            The resolved source identifier.

        Raises:
            SemanticEvidenceError: If alias is unknown.
        """
        if alias not in alias_map:
            raise SemanticEvidenceError(
                message="IF these sources do not actually contain your claim, RETURN AN EMPTY LIST []. Do not invent sources.",
                details={"error_code": ErrorCodes.SEMANTIC_EVIDENCE_HALLUCINATION.value, "alias": alias},
            )
        return alias_map[alias]

    @classmethod
    def resolve_graceful(cls, alias: str, alias_map: dict[str, str]) -> str | None:
        """Validates the alias gracefully and returns the mapped source.

        Args:
            alias: The source alias (e.g., '<<QRM-SRC-1>>').
            alias_map: Mapping of aliases to source identifiers.

        Returns:
            The resolved source identifier or None if the alias is unknown.
        """
        if alias not in alias_map:
            import logging

            logging.getLogger(__name__).warning(
                "Alias '%s' not found in alias_map. Graceful degradation applied.", alias
            )
            return None
        return alias_map[alias]
