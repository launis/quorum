from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class QuestionAnswerPair(BaseModel):
    """Strictly typed Question-Answer pair for questionnaire blocks."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)
    question: str
    answer: str


class GuidedReflectionInputDTO(BaseModel):
    """DTO for parsing flat questionnaire dictionaries into a strict schema.

    Enforces the Fail-Fast architecture by requiring structured data and explicitly
    handling arbitrary metadata without crashing the system, while ensuring
    deterministically ordered Markdown serialization.
    """  # noqa: W293

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)
    pairs: list[QuestionAnswerPair] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("pairs")
    @classmethod
    def require_at_least_one_pair(cls, v: list[QuestionAnswerPair]) -> list[QuestionAnswerPair]:
        if not v:
            raise ValueError("A valid questionnaire must contain at least one question-answer pair.")
        return v

    @model_validator(mode="before")
    @classmethod
    def parse_flat_dictionary(cls, data: Any) -> Any:
        """Transforms a flat raw dictionary (e.g. {'q0': 'Q', 'a0': 'A'}) into a structured model."""
        if isinstance(data, dict):
            # If already structured (e.g. from a future API update or internal tests)
            if "pairs" in data:
                return data

            pairs = []
            metadata = {}
            q_map = {}
            a_map = {}

            # Parse flat dictionary keys into categorized maps
            for k, v in data.items():
                k_str = str(k)
                if k_str.startswith("q"):
                    q_map[k_str[1:]] = str(v)
                elif k_str.startswith("a"):
                    a_map[k_str[1:]] = str(v)
                else:
                    metadata[k_str] = str(v)

            # Match questions and answers logically by index
            all_indices = sorted(list(set(q_map.keys()) | set(a_map.keys())))
            for idx in all_indices:
                q = q_map.get(idx, f"Question {idx}")
                a = a_map.get(idx, "No answer provided")
                pairs.append({"question": q, "answer": a})

            return {"pairs": pairs, "metadata": metadata}
        return data

    def to_markdown(self, title: str = "Questionnaire") -> str:
        """Deterministically serializes the questionnaire into a Markdown document."""
        parts = [f"# {title}\n"]

        for k, v in sorted(self.metadata.items()):
            parts.append(f"**{k}:** {v}\n")

        for pair in self.pairs:
            parts.append(f"### Q: {pair.question}")
            parts.append(f"> **A:** {pair.answer}\n")

        return "\n".join(parts).strip()
