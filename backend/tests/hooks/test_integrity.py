from unittest.mock import patch

import pytest

from backend.exceptions import AppException
from backend.hooks.integrity import enforce_hypothesis_linking, verify_citation_integrity
from backend.models.state import WorkflowState


# Mock Data Classes
def create_mock_hypothesis(id, quotes=None):
    return {
        "id": id,
        "quotes": quotes or [],
        "claim_text": "Mock Claim",
        "evidence_found": True if quotes else False,
        "search_query": "mock query",
    }


def create_mock_analyst(hypotheses):
    return {
        "hypotheses": hypotheses,
        "thought_process": "Mock thought process",
        "conclusion": "Mock conclusion",
        "confidence_score": 0.9,
    }


# TESTS


def test_enforce_hypothesis_linking_success():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["683eb4b9-147c-4f5d-89a7-7b18d75c4202"] = create_mock_analyst(
        [create_mock_hypothesis("HYP-1"), create_mock_hypothesis("HYP-2"), create_mock_hypothesis("HYP-3")]
    )

    new_state = enforce_hypothesis_linking(state)
    assert new_state == state  # Should return same state if verified


def test_enforce_hypothesis_linking_bad_format():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["683eb4b9-147c-4f5d-89a7-7b18d75c4202"] = create_mock_analyst(
        [create_mock_hypothesis("HYP-1"), create_mock_hypothesis("INVALID-2")]
    )

    with pytest.raises(AppException) as exc:
        enforce_hypothesis_linking(state)

    assert "Invalid Hypothesis ID format" in str(exc.value)


def test_enforce_hypothesis_linking_sequence_gap():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["683eb4b9-147c-4f5d-89a7-7b18d75c4202"] = create_mock_analyst(
        [
            create_mock_hypothesis("HYP-1"),
            create_mock_hypothesis("HYP-3"),  # Skipped 2
        ]
    )

    with pytest.raises(AppException) as exc:
        enforce_hypothesis_linking(state)

    assert "Hypothesis ID sequence error" in str(exc.value)


def test_verify_citation_integrity_success():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["inputs"] = {
        "history_text": "The quick brown fox jumps over the lazy dog.",
        "product_text": "none",
        "reflection_text": "none",
    }
    state.context_variables["683eb4b9-147c-4f5d-89a7-7b18d75c4202"] = create_mock_analyst(
        [create_mock_hypothesis("HYP-1", quotes=["quick brown fox", "lazy dog"])]
    )

    new_state = verify_citation_integrity(state)
    audit = new_state.context_variables["integrity_audit"]
    assert audit.valid_citations == 2
    assert audit.integrity_score == 1.0


def test_verify_citation_integrity_fail_fast():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["inputs"] = {
        "history_text": "The quick brown fox jumps over the lazy dog.",
        "product_text": "none",
        "reflection_text": "none",
    }
    # 2 invalid vs 1 valid -> 0.33 score -> Fail
    state.context_variables["683eb4b9-147c-4f5d-89a7-7b18d75c4202"] = create_mock_analyst(
        [create_mock_hypothesis("HYP-1", quotes=["quick brown fox", "unicorn", "leprechaun"])]
    )

    with patch("backend.settings.get_settings") as mock_settings_func:
        mock_settings = mock_settings_func.return_value
        mock_settings.citation_integrity_threshold = 0.9
        with pytest.raises(AppException) as exc:
            verify_citation_integrity(state)

    assert "CITATION_INTEGRITY_FAILURE" in str(exc.value)
    assert exc.value.status_code == 422
