from typing import cast
from unittest.mock import AsyncMock

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.integrity import enforce_hypothesis_linking_hook, verify_citation_integrity_hook  # noqa: E501


@pytest.fixture
def mock_deps() -> HookDependencies:
    exec_repo_mock = AsyncMock()
    exec_repo_mock.get_execution.return_value = None
    
    return HookDependencies(
        exec_repo=exec_repo_mock,
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),  # noqa: E501
        search_client=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_verify_citation_integrity_hook_analyst_hallucination(mock_deps: HookDependencies) -> None:  # noqa: E501
    """Test that hallucinations in AnalystOutput quotes are stripped."""
    from unittest.mock import MagicMock, patch

    # Mock the ExecutionRecord so Fail-Fast doesn't trigger
    exec_record_mock = MagicMock()
    exec_record_mock.raw_inputs.model_dump.return_value = {"doc1": "content"}
    mock_deps.exec_repo.get_execution.return_value = exec_record_mock

    # Mock the Storage Driver so it returns our RAG context from disk
    storage_mock = AsyncMock()
    storage_mock.read.return_value = b"The quick brown fox jumps over the lazy dog."

    state = HookState(
        execution_id="exe_1",
        workflow_id="wf_1",
        step_id="step_analyst",
        metadata={},
        global_context_vars={},
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

    with patch("backend_v2.hooks.integrity.get_storage_driver", return_value=storage_mock):
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
