"""Security Domain Models.

Provides strict Pydantic V2 validation schemas for the security hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Annotated, Any

from pydantic import Field, TypeAdapter

from backend_v2.models.core_base import V2CoreBase

_dict_adapter = TypeAdapter(dict[str, Any])


class SecurityPayloadDTO:
    """Strict schema for inputs destined for text sanitization.

    By utilizing a TypeAdapter wrapper (RootModel is broken in Python 3.14),
    we strictly enforce that the incoming state payload is explicitly a dictionary
    before any iterative logic executes, satisfying the Phase 9 Zero-Compromise mandate.

    Attributes:
        root: Raw state inputs.
    """

    def __init__(self, root: dict[str, Any]) -> None:
        """Initialize the DTO with the underlying dictionary.

        Args:
            root: Raw state inputs.
        """
        self.root = root

    @classmethod
    def model_validate(cls, data: Any) -> SecurityPayloadDTO:
        """Validate using strict Pydantic TypeAdapter.

        Args:
            data: Arbitrary input data to validate.

        Returns:
            A validated SecurityPayloadDTO.

        Raises:
            ValidationError: If validation fails.
        """
        validated = _dict_adapter.validate_python(data)
        return cls(root=validated)


class SanitizationResultDTO(V2CoreBase):
    """Result payload for text sanitization.

    Attributes:
        sanitized_inputs: Original keys mapped to sanitized values.
        security_status: Overall status of the security check.
        threat_detected: Flag indicating if a threat was detected.
    """

    sanitized_inputs: Annotated[dict[str, str], Field(description="The inputs after sanitization")]
    security_status: Annotated[str, Field(min_length=1, description="Status of the security check")]
    threat_detected: Annotated[bool, Field(description="Whether a threat was detected")]
