from collections.abc import Awaitable
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.integrity import (
    _gather_rag_context,
    _is_hallucinated,
    _verify_payload_citations,
    enforce_hypothesis_linking_hook,
    verify_citation_integrity_hook,
)
from backend_v2.models.domain.analyst import AnalystOutput, Hypothesis


def test_is_hallucinated() -> None:
    corpus = ["this is a test sentence", "another completely different line"]

    assert _is_hallucinated("This is a test sentence", corpus, threshold=80.0) is False
    assert _is_hallucinated("This is a test sentenc", corpus, threshold=80.0) is False
    assert _is_hallucinated("I am making this up", corpus, threshold=80.0) is True
    assert _is_hallucinated("cat", corpus, threshold=80.0) is False


def test_gather_rag_context_empty() -> None:
    assert _gather_rag_context({}) == ""


def test_gather_rag_context_valid() -> None:
    global_vars = {
        "step_context": {
            "precedents": "Previous cases.",
            "knowledge_items": [{"term": "AI", "definition": "Artificial Intelligence"}],
        }
    }
    result = _gather_rag_context(global_vars)
    assert "Previous cases." in result
    assert "[AI]: Artificial Intelligence" in result


def test_enforce_hypothesis_linking_hook_bypass() -> None:
    state = HookState(
        execution_id="exe1", workflow_id="wf1", inputs={"not_analyst": "data"}, metadata={}, global_context_vars={}
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, enforce_hypothesis_linking_hook(state, deps))
    assert result.success is True
    assert result.state_delta == {}


def test_enforce_hypothesis_linking_hook_valid() -> None:
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs={
            "thought_process": "Thinking...",
            "conclusion": "Concluded.",
            "confidence_score": 0.9,
            "hypotheses": [
                {"id": "hyp_1", "claim_text": "C1", "evidence_found": False, "search_query": "Q1", "quotes": []},
                {"id": "hyp_2", "claim_text": "C2", "evidence_found": False, "search_query": "Q2", "quotes": []},
            ],
        },
        metadata={},
        global_context_vars={},
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, enforce_hypothesis_linking_hook(state, deps))
    assert result.success is True


def test_enforce_hypothesis_linking_hook_duplicate_id() -> None:
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs={
            "thought_process": "Thinking...",
            "conclusion": "Concluded.",
            "confidence_score": 0.9,
            "hypotheses": [
                {"id": "hyp_1", "claim_text": "C1", "evidence_found": False, "search_query": "Q1", "quotes": []},
                {"id": "hyp_1", "claim_text": "C2", "evidence_found": False, "search_query": "Q2", "quotes": []},
            ],
        },
        metadata={},
        global_context_vars={},
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        enforce_hypothesis_linking_hook(state, deps)
    assert exc.value.status_code == 500
    assert "Duplicate Hypothesis ID" in exc.value.message


@pytest.mark.asyncio
async def test_verify_citation_integrity_hook_bypass() -> None:
    state = HookState(
        execution_id="exe1", workflow_id="wf1", inputs={"not_analyst": "data"}, metadata={}, global_context_vars={}
    )
    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = AsyncMock()

    with patch("backend_v2.hooks.integrity._gather_source_texts", new_callable=AsyncMock) as mock_gather:
        mock_gather.return_value = ["Some source text"]
        with patch("backend_v2.hooks.integrity._read_docs", return_value=""):
            result = await cast(Awaitable[HookResult], verify_citation_integrity_hook(state, deps))

    assert result.success is True
    assert result.state_delta == {"not_analyst": "data"}


def test_verify_payload_citations_analyst() -> None:
    payload = AnalystOutput(
        thought_process="Thinking...",
        conclusion="Concluded.",
        confidence_score=0.9,
        hypotheses=[
            Hypothesis(
                id="hyp_1",
                claim_text="Claim",
                evidence_found=True,
                search_query="Query",
                quotes=["Valid quote", "Hallucinated quote"],
            )
        ],
    )
    corpus = ["this is a valid quote"]

    new_payload, total, valid, invalid = _verify_payload_citations(payload, corpus, threshold=80.0)
    assert total == 2
    assert valid == 1
    assert len(invalid) == 1
    assert "Hallucinated quote" in invalid
    assert "Valid quote" in cast(AnalystOutput, new_payload).hypotheses[0].quotes
