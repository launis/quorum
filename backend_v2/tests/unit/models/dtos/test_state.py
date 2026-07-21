from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.state import HookStateMetadata, I18nStatePayload


def test_hook_state_metadata_strictness() -> None:
    """Test HookStateMetadata enforces V2CoreBase strictness and immutability."""
    dto = HookStateMetadata(target_locale="en-US")
    assert dto.target_locale == "en-US"

    with pytest.raises(ValidationError):
        HookStateMetadata.model_validate({"target_locale": "fi", "unknown_field": True})


def test_i18n_state_payload_strictness() -> None:
    """Test I18nStatePayload enforces V2CoreBase strictness."""
    dto = I18nStatePayload(language="fi")
    assert dto.language == "fi"

    with pytest.raises(ValidationError):
        I18nStatePayload.model_validate({"language": "fi", "extra_field": "fail"})
