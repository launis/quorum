from pydantic import Field

from backend_v2.models.core_base import V2CoreBase


class QuestionAnswerPair(V2CoreBase):
    """Strictly typed Question-Answer pair for questionnaire blocks."""

    question: str
    answer: str


class GuidedReflectionInputDTO(V2CoreBase):
    """DTO for parsing flat questionnaire dictionaries into a strict schema.

    Enforces the Fail-Fast architecture by requiring structured data and explicitly
    handling arbitrary metadata without crashing the system, while ensuring
    deterministically ordered Markdown serialization.
    """

    pairs: list[QuestionAnswerPair] = Field(min_length=1)
    metadata: dict[str, str] = Field(default_factory=dict)

    def to_markdown(self, title: str = "Questionnaire") -> str:
        """Deterministically serializes the questionnaire into a Markdown document."""
        parts = [f"# {title}\n"]

        for k, v in sorted(self.metadata.items()):
            parts.append(f"**{k}:** {v}\n")

        for pair in self.pairs:
            parts.append(f"### Q: {pair.question}")
            parts.append(f"> **A:** {pair.answer}\n")

        return "\n".join(parts).strip()
