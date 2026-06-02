from __future__ import annotations

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

    pairs: list[QuestionAnswerPair] = Field(min_length=1)
    metadata: dict[str, str] = Field(default_factory=dict)

    def to_markdown(self, title: str = "Questionnaire") -> str:
        """Deterministically serializes the questionnaire into a Markdown document.

        Args:
            title: The title header of the rendered Markdown document.

        Returns:
            The formatted markdown string content.
        """
        parts: list[str] = [f"# {title}\n"]

        for k, v in sorted(self.metadata.items()):
            parts.append(f"**{k}:** {v}\n")

        for pair in self.pairs:
            parts.append(f"### Q: {pair.question}")
            parts.append(f"> **A:** {pair.answer}\n")

        return "\n".join(parts).strip()
