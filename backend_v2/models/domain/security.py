"""Security Domain Models.

Provides strict Pydantic V2 validation schemas for the security hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

_dict_adapter = TypeAdapter(dict[str, Any])


class SecurityPayloadDTO:
    """Strict schema for inputs destined for text sanitization.

    By utilizing a TypeAdapter wrapper (RootModel is broken in Python 3.14),
    we strictly enforce that the incoming state payload is explicitly a dictionary
    before any iterative logic executes, satisfying the Phase 9 Zero-Compromise mandate.

    Attributes:
        root: The underlying dictionary representing raw state inputs.
    """

    def __init__(self, root: dict[str, Any]) -> None:
        """Initialize the DTO with the underlying dictionary.

        Args:
            root: The underlying dictionary representing raw state inputs.
        """
        self.root = root

    @classmethod
    def model_validate(cls, data: Any) -> SecurityPayloadDTO:
        """Validate using strict Pydantic TypeAdapter.

        Args:
            data: Arbitrary input data to validate as a dictionary.

        Returns:
            A validated SecurityPayloadDTO wrapping the dictionary.

        Raises:
            ValidationError: If the input data is not a valid dictionary.
        """
        validated = _dict_adapter.validate_python(data)
        return cls(root=validated)


class SanitizationResultDTO(BaseModel):
    """Result payload for text sanitization.

    Attributes:
        sanitized_inputs: Map of original keys to sanitized string values.
        security_status: Overall string status description of the security check.
        threat_detected: Boolean flag indicating if any threat was detected during sanitization.
    """

    sanitized_inputs: dict[str, str] = Field(..., description="The inputs after sanitization")
    security_status: str = Field(..., min_length=1, description="Status of the security check")
    threat_detected: bool = Field(..., description="Whether a threat was detected")

    model_config = ConfigDict(frozen=True, extra="forbid")
