"""Pydantic schemas for Prompt definitions and Semantic control.

Provides strict models for TDA validation prompts and other systemic queries,
replacing legacy f-strings and loosely typed dictionaries.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class BasePromptModel(BaseModel):
    """Base Pydantic schema for all prompt models.

    Enforces Strict V2 serialization and drops None fields.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    def model_dump_prompt(self) -> dict[str, Any]:
        """Dump the model for LLM inference, explicitly excluding None fields."""
        return self.model_dump(exclude_none=True, by_alias=True)


class TdaValidationPrompt(BasePromptModel):
    """Schema for Track A/Track B Semantic Validation prompts.

    Represents the structured context required to evaluate user input
    against a specific TDA Protocol Rule.
    """

    rule_id: str
    rule_description: str
    target_text: str
    strictness_calibration: str | None = None
    theory_context: str | None = None
    linguistic_mandate: str | None = None
