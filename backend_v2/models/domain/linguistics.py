"""Linguistics Domain Models.

Provides strict Pydantic V2 validation schemas for the linguistics hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

type DynamicScalar = str | int | float | bool | None
type DynamicInputNode = DynamicScalar | list[DynamicScalar] | dict[str, DynamicScalar | list[DynamicScalar]]
type DynamicInputValue = (
    DynamicScalar
    | list[DynamicScalar]
    | list[DynamicInputNode]
    | dict[str, DynamicScalar]
    | dict[str, list[DynamicScalar]]
    | dict[str, DynamicInputNode]
)

__all__ = [
    "DynamicInputNode",
    "DynamicInputValue",
    "DynamicLinguisticsExtractorDTO",
    "DynamicScalar",
    "LinguisticsPayloadDTO",
    "LinguisticsResultDTO",
    "PerformativePatternDTO",
]


class DynamicLinguisticsExtractorDTO(BaseModel):
    """Schema for dynamic LLM extraction of performative and sycophantic phrases.

    Attributes:
        detected_phrases: List of verbatim performative phrases extracted from the text.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    detected_phrases: Annotated[
        list[str],
        Field(default_factory=list, description="Verbatim performative phrases extracted from the text."),
    ]


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
    dynamic_inputs: Annotated[
        dict[str, DynamicInputValue],
        Field(default_factory=dict, description="Dictionary of texts to scan"),
    ]

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    def extract_language(self, global_vars: dict[str, DynamicInputValue]) -> str:
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
        """Extracts and returns the text to scan, prioritizing chat_log_user_only if present.

        Returns:
            The extracted and concatenated lowercased text.
        """
        if "chat_log_user_only" in self.dynamic_inputs:
            user_val = self.dynamic_inputs["chat_log_user_only"]
            if isinstance(user_val, str) and user_val.strip():
                return user_val.strip().lower()

        results: list[str] = []

        def _extract(val: DynamicInputValue | DynamicInputNode) -> None:
            if isinstance(val, str):
                if val.strip():
                    results.append(val)
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                results.append(str(val))
            elif isinstance(val, list):
                for item in val:
                    _extract(item)
            elif val is not None and not isinstance(val, bool):
                for sub_val in val.values():
                    _extract(sub_val)

        for v in self.dynamic_inputs.values():
            _extract(v)

        return " ".join(results).lower()
