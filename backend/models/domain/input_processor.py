"""Domain model for the Input Processor Agent output."""

from pydantic import ConfigDict, Field

from backend.models.domain.base import ReasoningTrace, ReasoningTraceDTO


class InputProcessorDTO(ReasoningTraceDTO):
    """Data Transfer Object containing the processed string outputs."""

    history_text: str = Field(default="", description="Processed history text.")
    product_text: str = Field(default="", description="Processed product text.")
    reflection_text: str = Field(default="", description="Processed reflection text.")

    # Do not include metadata here as DTOs are LLM-safe
    model_config = ConfigDict(strict=True, extra="ignore")


class InputProcessorOutput(InputProcessorDTO, ReasoningTrace):
    """Domain Model resulting from input processing."""
    pass
