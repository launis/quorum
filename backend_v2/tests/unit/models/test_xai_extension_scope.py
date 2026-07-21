from unittest.mock import AsyncMock
from backend_v2.models.enums import XAI_EXTENSION_SCOPE, XaiExtensionType


def test_xai_extension_scope_completeness() -> None:
    """Meta-test to verify that every XaiExtensionType has a defined scope in XAI_EXTENSION_SCOPE."""
    for extension_type in XaiExtensionType:
        assert extension_type in XAI_EXTENSION_SCOPE, (
            f"Missing scope definition for XaiExtensionType '{extension_type.value}'. "
            f"Please add it to XAI_EXTENSION_SCOPE in enums.py."
        )
