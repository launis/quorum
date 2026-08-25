"""Unit tests for engine DTOs."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.engine import (
    EngineExecutionRequest,
    EngineExecutionResult,
    FlattenedAtom,
    MatrixEvaluationContext,
)


def test_engine_execution_result_strictness() -> None:
    """Test that EngineExecutionResult forbids extra fields and is strict."""
    with pytest.raises(ValidationError):
        EngineExecutionResult.model_validate({"results": [], "hydrated_references": {}, "extra_field": "disallowed"})


def test_engine_execution_result_is_frozen() -> None:
    """Test that EngineExecutionResult is immutable."""
    result = EngineExecutionResult(results=[], hydrated_references={})
    with pytest.raises(ValidationError):
        result.results = []  # type: ignore


def test_engine_execution_request_is_frozen() -> None:
    """Test that EngineExecutionRequest is immutable."""
    assert EngineExecutionRequest.model_config.get("frozen") is True
    assert EngineExecutionRequest.model_config.get("extra") == "forbid"
    assert EngineExecutionRequest.model_config.get("strict") is True


def test_flattened_atom_forbids_extra_fields() -> None:
    """Test that FlattenedAtom forbids extra fields per Zero-Compromise mandate."""
    data = {
        "atom_id": "tda_123",
        "question": "Is the sky blue?",
        "extraction_rule": "Must be explicit.",
        "anchor_target": "Paragraph 1",
        "is_inverse": False,
        "extra_key": "allowed",
    }
    with pytest.raises(ValidationError):
        FlattenedAtom.model_validate(data)


def test_flattened_atom_missing_required_fields() -> None:
    """Test that missing required fields trigger ValidationError."""
    with pytest.raises(ValidationError):
        FlattenedAtom.model_validate({"question": "Missing ID"})

    with pytest.raises(ValidationError):
        FlattenedAtom.model_validate({"atom_id": "tda_123"})


def test_flattened_atom_invalid_types() -> None:
    """Test that invalid types trigger ValidationError."""
    with pytest.raises(ValidationError):
        FlattenedAtom.model_validate({"atom_id": "tda_123", "question": "Q", "is_inverse": "not-a-bool"})


def test_matrix_evaluation_context_strictness() -> None:
    """Test that MatrixEvaluationContext forbids extra fields."""
    with pytest.raises(ValidationError):
        MatrixEvaluationContext.model_validate({"allow_contextual_override": True, "extra_field": "disallowed"})


def test_matrix_evaluation_context_is_frozen() -> None:
    """Test that MatrixEvaluationContext is immutable."""
    context = MatrixEvaluationContext()
    with pytest.raises(ValidationError):
        context.allow_contextual_override = True  # type: ignore


def test_matrix_evaluation_context_invalid_types() -> None:
    """Test that invalid types trigger ValidationError."""
    with pytest.raises(ValidationError):
        MatrixEvaluationContext.model_validate({"allow_contextual_override": "not-a-bool"})


def test_engine_execution_request_semaphore_cm_and_fields() -> None:
    """Test EngineExecutionRequest semaphore_cm property with and without Semaphore."""
    import asyncio
    from unittest.mock import MagicMock

    from backend_v2.llm.client import LLMClient
    from backend_v2.models.dtos.dag_models import CausalEdge
    from backend_v2.models.dtos.engine import EngineExecutionRequest
    from backend_v2.models.v2_core import StepRule
    from backend_v2.services.orchestrator.strategies.base import StrategyContext

    edge = CausalEdge(
        edge_reasoning="Causal relation between atoms",
        tda_id="tda_11111111111111111111111111111111",
        source_id="chk_01",
    )
    atom = FlattenedAtom(atom_id="atm_1", question="Q", depends_on=(edge,))
    assert atom.depends_on[0].tda_id == "tda_11111111111111111111111111111111"

    step = StepRule(id="stp_1111111111111111", task_blueprint="bp_1")
    context = StrategyContext(
        execution_id="exe_1",
        workflow_id="wf_1",
        metadata={},
        model_strategy="fast",
    )
    client = MagicMock(spec=LLMClient)

    # Without semaphore -> nullcontext
    req = EngineExecutionRequest(
        bound_client=client,
        compiled_schema=None,
        hydrated_messages=None,
        system_prompt="System",
        step=step,
        context=context,
        global_source_text="Source",
        target_locale="en",
        prompt_compiler=MagicMock(),
    )
    assert req.semaphore_cm is not None

    # With semaphore -> semaphore
    sem = asyncio.Semaphore(1)
    req_sem = req.model_copy(update={"semaphore": sem})
    assert req_sem.semaphore_cm is sem
