from typing import cast
from unittest.mock import AsyncMock

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.integrity import enforce_hypothesis_linking_hook, verify_citation_integrity_hook


@pytest.fixture
def mock_deps() -> HookDependencies:
    return HookDependencies(
        repository=AsyncMock(),
        search_client=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_verify_citation_integrity_hook_analyst_hallucination(mock_deps: HookDependencies) -> None:
    """Test that hallucinations in AnalystOutput quotes are stripped."""
    state = HookState(
        execution_id="exe_1",
        workflow_id="wf_1",
        step_id="step_analyst",
        metadata={},
        global_context_vars={"inputs": {"doc1": "The quick brown fox jumps over the lazy dog."}},
        inputs={
            "hypotheses": [
                {
                    "id": "hyp_123xyz",
                    "claim_text": "Fox is quick.",
                    "evidence_found": True,
                    "search_query": "fox",
                    "quotes": ["quick brown fox", "a slow red cat"],  # First is real, second is hallucinated
                }
            ],
            "rag_evidence": [],
            "critical_violation": False,
            "thought_process": "Thinking...",
            "conclusion": "It is true",
            "confidence_score": 0.9,
        },
    )

    from collections.abc import Awaitable

    result = await cast(Awaitable[HookResult], verify_citation_integrity_hook(state, mock_deps))
    assert result.success is True
    assert result.state_delta is not None

    delta = result.state_delta
    # The hallucinated quote should be stripped
    quotes = delta["hypotheses"][0]["quotes"]
    assert "quick brown fox" in quotes
    assert "a slow red cat" not in quotes

    assert "integrity_audit" in delta
    assert delta["integrity_audit"]["invalid_citations"] == ["a slow red cat"]


def test_enforce_hypothesis_linking_success(mock_deps: HookDependencies) -> None:
    """Test successful validation of opaque hypothesis IDs."""
    state = HookState(
        execution_id="exe_1",
        workflow_id="wf_1",
        step_id="step_analyst",
        metadata={},
        global_context_vars={},
        inputs={
            "hypotheses": [
                {
                    "id": "hyp_abc123",
                    "claim_text": "Claim 1",
                    "evidence_found": False,
                    "search_query": "test 1",
                    "quotes": [],
                },
                {
                    "id": "hyp_def456",
                    "claim_text": "Claim 2",
                    "evidence_found": False,
                    "search_query": "test 2",
                    "quotes": [],
                },
            ],
            "rag_evidence": [],
            "critical_violation": False,
            "thought_process": "Thinking...",
            "conclusion": "It is true",
            "confidence_score": 0.9,
        },
    )

    result = cast(HookResult, enforce_hypothesis_linking_hook(state, mock_deps))
    assert result.success is True
    assert result.state_delta == {}


def test_enforce_hypothesis_linking_duplicate_fails(mock_deps: HookDependencies) -> None:
    """Test Fail-Fast on duplicate opaque hypothesis IDs."""
    state = HookState(
        execution_id="exe_1",
        workflow_id="wf_1",
        step_id="step_analyst",
        metadata={},
        global_context_vars={},
        inputs={
            "hypotheses": [
                {
                    "id": "hyp_duplicate",
                    "claim_text": "Claim 1",
                    "evidence_found": False,
                    "search_query": "test 1",
                    "quotes": [],
                },
                {
                    "id": "hyp_duplicate",  # Duplicate!
                    "claim_text": "Claim 3",
                    "evidence_found": False,
                    "search_query": "test 3",
                    "quotes": [],
                },
            ],
            "rag_evidence": [],
            "critical_violation": False,
            "thought_process": "Thinking...",
            "conclusion": "It is true",
            "confidence_score": 0.9,
        },
    )

    with pytest.raises(AppException) as exc:
        enforce_hypothesis_linking_hook(state, mock_deps)

    assert exc.value.status_code == 500
    assert "Duplicate Hypothesis ID found" in exc.value.message
