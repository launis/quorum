import pytest
from pydantic import ValidationError

from backend.api.view_models import AssessmentViewModel


def test_assessment_view_model_valid():
    model = AssessmentViewModel(
        session_id="sess-123",
        status_label="Completed",
        ui_variant="success",
        final_score=95,
        status_message="All good",
        show_warning_banner=False,
    )
    assert model.session_id == "sess-123"
    assert model.ui_variant == "success"


def test_assessment_view_model_invalid_variant():
    with pytest.raises(ValidationError) as excinfo:
        AssessmentViewModel(
            session_id="sess-123",
            status_label="Failed",
            ui_variant="invalid_variant",  # type: ignore[arg-type]
            status_message="Bad",
            final_score=0,
            show_warning_banner=False,
        )
    assert "Input should be 'success', 'warning', 'error', 'info' or 'neutral'" in str(excinfo.value)


def test_assessment_view_model_extra_forbid():
    with pytest.raises(ValidationError) as excinfo:
        AssessmentViewModel(
            session_id="sess-123", status_label="OK", ui_variant="info", status_message="Msg", final_score=100, show_warning_banner=False, extra_field="Not allowed"  # type: ignore[call-arg]
        )
    assert "Extra inputs are not permitted" in str(excinfo.value)
