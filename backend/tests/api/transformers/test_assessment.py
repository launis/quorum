import pytest

from backend.api.transformers.assessment import AssessmentTransformer
from backend.models.view import AssessmentView


@pytest.fixture
def transformer():
    return AssessmentTransformer()


def test_transform_success_running(transformer):
    raw_data = {
        "execution_id": "exe-123",
        "status": "running",
        "results": {"step_results": {"step_1": {"status": "completed"}}},
    }

    view = transformer.transform(raw_data)
    assert isinstance(view, AssessmentView)
    assert view.sessionId == "exe-123"
    assert view.uiVariant == "default"
    assert "Valmis:" in view.statusMessage


def test_transform_success_completed(transformer):
    raw_data = {
        "execution_id": "exe-456",
        "status": "completed",
        "results": {"step_results": {"step_judge": {"total_score": 85}}},
    }

    view = transformer.transform(raw_data)
    assert view.uiVariant == "success"
    assert view.finalScore == 85


def test_transform_success_failed(transformer):
    raw_data = {"execution_id": "exe-789", "status": "failed", "error": "Something went wrong"}

    view = transformer.transform(raw_data)
    assert view.uiVariant == "error"
    assert "Something went wrong" in view.statusMessage


def test_transform_missing_data(transformer):
    # Should handle missing fields gracefully or fail fast if critical
    from typing import Any
    raw_data: dict[str, Any] = {}  # Missing status, id etc

    # transform logic defaults ID to "unknown" and status to None -> "Unknown"
    # so it should technically succeed but produce a "broken" view
    # UNLESS strict validation in AssessmentView catches it.
    # AssessmentView requires sessionId, statusLabel.
    # Code provides defaults.

    view = transformer.transform(raw_data)
    assert view.sessionId == "unknown"
    assert view.statusLabel == "Unknown"
    assert view.uiVariant == "default"
