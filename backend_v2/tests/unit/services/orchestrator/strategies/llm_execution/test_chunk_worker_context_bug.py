import pytest

from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ConsensusVotePayload


def test_consensus_vote_payload_missing_context():
    # This should raise RuntimeError because we provide a source_id without context
    raw_payload = {
        "exact_quotes": [{"text": "Some quote", "source_id": "doc0"}],
        "contextual_override": False,
        "reasoning_steps": "test",
        "semantic_reasoning": "test",
    }

    with pytest.raises(RuntimeError) as exc_info:
        ConsensusVotePayload.model_validate(raw_payload)

    assert "ValidationInfo.context is missing" in str(exc_info.value)


def test_consensus_vote_payload_with_context():
    raw_payload = {
        "exact_quotes": [{"text": "Some quote", "source_id": "doc0"}],
        "contextual_override": False,
        "reasoning_steps": "test",
        "semantic_reasoning": "test",
    }

    val_context = {"alias_map": {"doc0": "doc123"}}

    # This should pass without raising RuntimeError
    model = ConsensusVotePayload.model_validate(raw_payload, context=val_context)
    assert model.exact_quotes[0].source_id == "doc123"
