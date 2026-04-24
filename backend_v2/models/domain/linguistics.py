"""Linguistics Domain Models.

Provides strict Pydantic V2 validation schemas for the linguistics hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel


class PerformativePatternDTO(BaseModel):
    """Schema for a single detected performative pattern."""

    pattern_id: str = Field(description="Unique identifier for the detected pattern.")
    detected_phrase: str = Field(description="The exact matched substring.")
    category: str = Field(description="The categorization of the pattern (e.g., performative_filler).")

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class LinguisticsResultDTO(BaseModel):
    """Schema for the result of a linguistics scan."""

    performative_patterns: list[PerformativePatternDTO] = Field(default_factory=list)

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class LinguisticsPayloadDTO(RootModel[dict[str, Any]]):
    """Strict dictionary wrapper for linguistics inputs."""

    model_config = ConfigDict(frozen=True)

    def extract_language(self, global_vars: dict[str, Any]) -> str:
        """Determines language safely without dict.get() fallbacks."""
        if "language" in global_vars and global_vars["language"]:
            return str(global_vars["language"]).split("-")[0].lower()

        if "language" in self.root and self.root["language"]:
            return str(self.root["language"]).split("-")[0].lower()

        return "en"

    def get_text_to_scan(self) -> str:
        """Extracts and concatenates all string values for scanning."""
        return " ".join(str(v) for v in self.root.values() if v).lower()
