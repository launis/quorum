"""Unit tests for the ExtractiveSensorService."""

import pytest

from backend_v2.exceptions import AgentExecutionError
from backend_v2.models.dtos.dag_models import ExtractedAtom, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.extractive_sensor_service import ExtractiveSensorService


@pytest.fixture
def mock_nodes():
    atom1 = ExtractedAtom(tda_id="tda_11111111", resolved_claim="Claim 1", reasoning="Reasoning 1")
    atom2 = ExtractedAtom(tda_id="tda_22222222", resolved_claim="Claim 2", reasoning="Reasoning 2")
    return [
        LinkedAtomGraph(atom=atom1),
        LinkedAtomGraph(atom=atom2),
    ]


def test_resolve_majority_vote_consensus():
    """Test standard 2/3 consensus."""
    expected_ids = ["tda_11111111", "tda_22222222"]

    res1 = {
        "tda_11111111": (ExecutionStatus.PASSED, "R1", {"coaching": "c1"}),
        "tda_22222222": (ExecutionStatus.PASSED, "R2", {}),
    }
    res2 = {"tda_11111111": (ExecutionStatus.FAILED, "R3", {}), "tda_22222222": (ExecutionStatus.PASSED, "R2", {})}
    res3 = {"tda_11111111": (ExecutionStatus.PASSED, "R4", {}), "tda_22222222": (ExecutionStatus.PASSED, "R2", {})}

    final = ExtractiveSensorService.resolve_majority_vote(expected_ids, [res1, res2, res3])

    assert final["tda_11111111"][0] == ExecutionStatus.PASSED
    assert final["tda_11111111"][1] == "R1"

    assert final["tda_22222222"][0] == ExecutionStatus.PASSED


def test_resolve_majority_vote_1_fail_resilience():
    """Test that a single transient failure does not break the 2-vote consensus."""
    expected_ids = ["tda_11111111"]

    res1 = {"tda_11111111": (ExecutionStatus.FAILED, "R1", {})}
    res2 = None  # Transient failure sentinel
    res3 = {"tda_11111111": (ExecutionStatus.FAILED, "R2", {})}

    final = ExtractiveSensorService.resolve_majority_vote(expected_ids, [res1, res2, res3])

    assert final["tda_11111111"][0] == ExecutionStatus.FAILED


def test_resolve_majority_vote_2_fails():
    """Test that 2 transient failures correctly bubbles up the AgentExecutionError."""
    expected_ids = ["tda_11111111"]

    res1 = {"tda_11111111": (ExecutionStatus.FAILED, "R1", {})}
    res2 = None
    res3 = None

    with pytest.raises(AgentExecutionError) as exc_info:
        ExtractiveSensorService.resolve_majority_vote(expected_ids, [res1, res2, res3])

    assert "Insufficient valid Bo3 results" in str(exc_info.value)
    assert exc_info.value.status_code == 503


def test_resolve_majority_vote_split_system_error():
    """Test that a lack of consensus triggers a SYSTEM_ERROR."""
    expected_ids = ["tda_11111111"]

    res1 = {"tda_11111111": (ExecutionStatus.FAILED, "R1", {})}
    res2 = {"tda_11111111": (ExecutionStatus.PASSED, "R2", {})}
    res3 = None

    final = ExtractiveSensorService.resolve_majority_vote(expected_ids, [res1, res2, res3])

    assert final["tda_11111111"][0] == ExecutionStatus.SYSTEM_ERROR
    assert final["tda_11111111"][1] == "INSUFFICIENT_CONSENSUS"


def test_resolve_majority_vote_dropped_alias():
    """Test that if the LLM drops an alias across calls, it evaluates to SYSTEM_ERROR."""
    expected_ids = ["tda_11111111", "tda_22222222"]

    res1 = {"tda_11111111": (ExecutionStatus.PASSED, "R1", {})}
    res2 = {"tda_11111111": (ExecutionStatus.PASSED, "R2", {})}
    res3 = {"tda_11111111": (ExecutionStatus.PASSED, "R3", {})}

    final = ExtractiveSensorService.resolve_majority_vote(expected_ids, [res1, res2, res3])

    assert final["tda_11111111"][0] == ExecutionStatus.PASSED
    assert final["tda_22222222"][0] == ExecutionStatus.SYSTEM_ERROR
