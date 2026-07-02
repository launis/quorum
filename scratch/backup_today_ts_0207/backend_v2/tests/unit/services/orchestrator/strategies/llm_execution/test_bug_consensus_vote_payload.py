from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ConsensusVotePayload


def test_bug_consensus_vote_payload_accepts_epic91_object():
    """TDD Repro (Green): Proves that ConsensusVotePayload correctly parses the Epic 91
    object structure for exact_quotes as LLMExtractedQuote.
    """
    # Simulate the LLM outputting the new Epic 91 format for quotes
    epic91_payload = {
        "exact_quotes": [{"source_alias": "inputs", "text": "This is a quote from the document."}],
        "contextual_override": False,
        "reasoning_steps": "[1. PRE-CHECK: PASS]",
        "semantic_reasoning": "Evidence found.",
    }

    # This should SUCCEED because ConsensusVotePayload now expects list[LLMExtractedQuote]
    payload = ConsensusVotePayload.model_validate(epic91_payload)

    assert len(payload.exact_quotes) == 1
    assert payload.exact_quotes[0].text == "This is a quote from the document."
