"""Linguistics Domain Models.

Provides strict Pydantic V2 validation schemas for the linguistics hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field


class PerformativePatternDTO(BaseModel):
    """Schema for a single detected performative pattern.

    Attributes:
        pattern_id: Unique identifier for the detected pattern.
        detected_phrase: The exact matched substring.
        category: The categorization of the pattern (e.g., performative_filler).
    """

    pattern_id: Annotated[str, Field(min_length=1, description="Unique identifier for the detected pattern.")]
    detected_phrase: Annotated[str, Field(min_length=1, description="The exact matched substring.")]
    category: Annotated[
        str,
        Field(
            min_length=1,
            description="The categorization of the pattern (e.g., performative_filler).",
        ),
    ]
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class LinguisticsResultDTO(BaseModel):
    """Schema for the result of a linguistics scan.

    Attributes:
        performative_patterns: List of detected performative patterns.
    """

    performative_patterns: Annotated[list[PerformativePatternDTO], Field(default_factory=list)]

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class LinguisticsPayloadDTO(BaseModel):
    """Strict dictionary wrapper for linguistics inputs.

    Replaces legacy RootModel to strictly enforce Pydantic V2 schema.

    Attributes:
        language: Optional explicit language code.
        dynamic_inputs: Dictionary of texts to scan.
    """

    language: Annotated[str | None, Field(description="Optional explicit language code")] = None
    dynamic_inputs: Annotated[dict[str, Any], Field(default_factory=dict, description="Dictionary of texts to scan")]

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    def extract_language(self, global_vars: dict[str, Any]) -> str:
        """Determines language safely without dict.get() fallbacks.

        Args:
            global_vars: Dictionary of global variables.

        Returns:
            The extracted language code.
        """
        if "language" in global_vars and global_vars["language"]:
            return str(global_vars["language"]).split("-")[0].lower()

        if self.language:
            return str(self.language).split("-")[0].lower()

        return "en"

    def get_text_to_scan(self) -> str:
        """Extracts and concatenates all string values for scanning.

        Returns:
            The concatenated text.
        """
        return " ".join(str(v) for v in self.dynamic_inputs.values() if v).lower()
