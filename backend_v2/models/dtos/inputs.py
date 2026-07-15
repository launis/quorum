"""Input Data Transfer Objects (DTOs) for processing incoming data streams.

This module defines strict schemas for parsing and validating unstructured or flat
inputs into strict types, ensuring a Fail-Fast pipeline at the API boundary.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase


class QuestionAnswerPair(V2CoreBase):
    """Strictly typed Question-Answer pair for questionnaire blocks.

    Attributes:
        question: The text of the question.
        answer: The text of the answer.
    """

    question: str
    answer: str


class GuidedReflectionInputDTO(V2CoreBase):
    """DTO for parsing flat questionnaire dictionaries into a strict schema.

    Enforces the Fail-Fast architecture by requiring structured data and explicitly
    handling arbitrary metadata without crashing the system, while ensuring
    deterministically ordered Markdown serialization.

    Attributes:
        pairs: List of Question-Answer pairs containing the core input.
        metadata: Flat dictionary storing supplemental execution metadata.
    """

    pairs: Annotated[list[QuestionAnswerPair], Field(min_length=1)]
    metadata: Annotated[dict[str, str], Field(default_factory=dict)]

    def to_markdown(self, title: str = "Questionnaire") -> str:
        """Deterministically serializes the questionnaire into a Markdown document.

        Args:
            title: The title header of the rendered Markdown document.

        Returns:
            The formatted markdown string content.
        """
        parts: list[str] = [f'<questionnaire title="{title}">']

        if self.metadata:
            parts.append("  <metadata>")
            for k, v in sorted(self.metadata.items()):
                # Clean keys to be valid XML tags (alphanumeric and underscore)
                clean_k = "".join(c if c.isalnum() else "_" for c in k).strip("_")
                parts.append(f"    <{clean_k}>{v}</{clean_k}>")
            parts.append("  </metadata>")

        for pair in self.pairs:
            parts.append("  <qa_pair>")
            parts.append(f"    <question>{pair.question}</question>")
            parts.append(f"    <answer>{pair.answer}</answer>")
            parts.append("  </qa_pair>")

        parts.append("</questionnaire>")
        return "\n".join(parts).strip()
