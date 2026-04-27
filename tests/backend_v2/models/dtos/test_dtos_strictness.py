import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.report import MatrixObservabilityDTO
from backend_v2.models.dtos.state import HookStateMetadata

def test_matrix_observability_dto_forbids_extra_fields():
    """Verify that we do not silently ignore extra fields, enforcing Fail-Fast."""
    with pytest.raises(ValidationError) as exc_info:
        MatrixObservabilityDTO(
            true_atoms_count=5,
            false_atoms_count=2,
            unknown_legacy_field="should crash"
        )
    assert "Extra inputs are not permitted" in str(exc_info.value) or "extra_forbidden" in str(exc_info.value)

def test_hook_state_metadata_forbids_extra_fields():
    """Verify that HookStateMetadata forbids extra fields."""
    with pytest.raises(ValidationError) as exc_info:
        HookStateMetadata(
            target_locale="en",
            legacy_stuff="not allowed"
        )
    assert "Extra inputs are not permitted" in str(exc_info.value) or "extra_forbidden" in str(exc_info.value)
