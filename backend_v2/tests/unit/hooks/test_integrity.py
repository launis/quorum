from collections.abc import Awaitable
from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.integrity import (
    _gather_rag_context,
    _is_hallucinated,
    _verify_payload_citations,
    enforce_hypothesis_linking_hook,
    verify_citation_integrity_hook,
)
from backend_v2.models.domain.analyst import AnalystOutput, Hypothesis
from backend_v2.models.execution_core import ExecutionMetadata


def test_is_hallucinated() -> None:
    norm_corpus = "thisisatestsentenceanothercompletelydifferentline"

    assert _is_hallucinated("This is a test sentence", norm_corpus, threshold=80.0) is False
    assert _is_hallucinated("This is a test sentenc", norm_corpus, threshold=80.0) is False
    assert _is_hallucinated("I am making this up", norm_corpus, threshold=80.0) is True
    assert _is_hallucinated("cat", norm_corpus, threshold=80.0) is False


def test_gather_rag_context_empty() -> None:
    assert _gather_rag_context(GlobalContextVarsDTO()) == ""


def test_gather_rag_context_valid() -> None:
    global_vars = GlobalContextVarsDTO(
        step_coach={"precedents": "Previous cases."},
        knowledge_base={"AI": "Artificial Intelligence"},
    )
    result = _gather_rag_context(global_vars)
    assert "Previous cases." in result
    assert "[AI]: Artificial Intelligence" in result


def test_enforce_hypothesis_linking_hook_bypass() -> None:
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={"not_analyst": "data"}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, enforce_hypothesis_linking_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


def test_enforce_hypothesis_linking_hook_valid() -> None:
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "thought_process": "Thinking...",
                "conclusion": "Concluded.",
                "confidence_score": 0.9,
                "hypotheses": [
                    {"id": "hyp_1", "claim_text": "C1", "evidence_found": False, "search_query": "Q1", "quotes": []},
                    {"id": "hyp_2", "claim_text": "C2", "evidence_found": False, "search_query": "Q2", "quotes": []},
                ],
            }
        ),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, enforce_hypothesis_linking_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


def test_enforce_hypothesis_linking_hook_duplicate_id() -> None:
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "thought_process": "Thinking...",
                "conclusion": "Concluded.",
                "confidence_score": 0.9,
                "hypotheses": [
                    {"id": "hyp_1", "claim_text": "C1", "evidence_found": False, "search_query": "Q1", "quotes": []},
                    {"id": "hyp_1", "claim_text": "C2", "evidence_found": False, "search_query": "Q2", "quotes": []},
                ],
            }
        ),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        enforce_hypothesis_linking_hook(state, deps)
    assert exc.value.status_code == 500
    assert "Duplicate Hypothesis ID" in exc.value.message


@pytest.mark.asyncio
async def test_verify_citation_integrity_hook_bypass() -> None:
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={"not_analyst": "data"}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = AsyncMock()

    with patch("backend_v2.hooks.integrity._gather_source_texts", new_callable=AsyncMock) as mock_gather:
        mock_gather.return_value = ["Some source text"]
        with patch("backend_v2.hooks.integrity._read_docs", return_value=""):
            result = await cast(Awaitable[HookResult], verify_citation_integrity_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta is None


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
    norm_corpus = "thisisavalidquote"

    res = _verify_payload_citations(payload, norm_corpus, threshold=80.0)
    assert res.total_count == 2
    assert res.valid_count == 1
    assert len(res.invalid_citations) == 1
    assert "Hallucinated quote" in res.invalid_citations
    assert "Valid quote" in cast(AnalystOutput, res.payload).hypotheses[0].quotes


def test_verify_payload_citations_evaluation_result() -> None:
    from datetime import datetime, timezone

    from backend_v2.models.domain.evaluation import EvaluationResult
    from backend_v2.models.domain.judge import DimensionResultItem

    payload = EvaluationResult(
        thought_process="Thinking...",
        conclusion="Concluded.",
        confidence_score=0.9,
        matrix_id="mat_1",
        timestamp=datetime.now(timezone.utc),
        total_score=5.0,
        final_verdict="PASSED",
        dimensions=[DimensionResultItem(dimension_id="dim_1", dimension_label="Dim 1", score=5.0, reasoning="Good")],
        scale_min=1.0,
        scale_max=5.0,
        citation_snippets=["Valid quote", "Hallucinated quote"],
    )
    norm_corpus = "thisisavalidquote"
    res = _verify_payload_citations(payload, norm_corpus, threshold=80.0)
    assert res.total_count == 2
    assert res.valid_count == 1
    assert len(res.invalid_citations) == 1
    assert "Hallucinated quote" in res.invalid_citations


@pytest.mark.asyncio
async def test_verify_citation_integrity_hook_missing_source_texts_raises() -> None:
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={"test": "data"}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = AsyncMock()

    with patch("backend_v2.hooks.integrity._gather_source_texts", new_callable=AsyncMock) as mock_gather:
        mock_gather.return_value = []
        with pytest.raises(AppException) as exc:
            await cast(Awaitable[HookResult], verify_citation_integrity_hook(state, deps))
        assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_verify_citation_integrity_hook_full_success_with_citations() -> None:
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "thought_process": "Thinking...",
                "conclusion": "Concluded.",
                "confidence_score": 0.9,
                "hypotheses": [
                    {
                        "id": "hyp_1",
                        "claim_text": "Claim",
                        "evidence_found": True,
                        "search_query": "Query",
                        "quotes": ["This is valid text"],
                    }
                ],
            }
        ),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = AsyncMock()

    with patch("backend_v2.hooks.integrity._gather_source_texts", new_callable=AsyncMock) as mock_gather:
        mock_gather.return_value = ["This is valid text in source document."]
        with patch("backend_v2.hooks.integrity._read_docs", return_value=""):
            result = await cast(Awaitable[HookResult], verify_citation_integrity_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta is not None
    assert result.state_delta.delta.integrity_audit is not None
    assert result.state_delta.delta.integrity_audit.integrity_score == 1.0


@pytest.mark.asyncio
async def test_gather_source_texts_with_storage() -> None:
    from backend_v2.hooks.integrity import _gather_source_texts
    from backend_v2.models.domain.execution import ExecutionRecord
    from backend_v2.models.domain.inputs import WorkflowInputs
    from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository

    exec_repo = InMemoryUnifiedWorkflowRepository()
    exec_record = ExecutionRecord(
        id="ex_1234567890abcdef",
        workflow_id="wf1",
        output_profile_id="prof_1234567890abcdef",
        target_locale="en",
        status="RUNNING",
        metadata=ExecutionMetadata(),
        raw_inputs=WorkflowInputs(dynamic_inputs={"dyn_b": "val2"}),
    )
    await exec_repo.save_execution(exec_record)

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = exec_repo

    mock_storage = AsyncMock()
    mock_storage.exists.return_value = True
    mock_storage.read.return_value = b"Loaded forensic input data"

    with patch("backend_v2.hooks.integrity.get_storage_driver", return_value=mock_storage):
        texts = await _gather_source_texts(exec_record.id, deps)

    assert len(texts) >= 1
    assert "Loaded forensic input data" in texts[0]


@pytest.mark.asyncio
async def test_gather_source_texts_missing_record_raises() -> None:
    from backend_v2.hooks.integrity import _gather_source_texts
    from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = InMemoryUnifiedWorkflowRepository()

    with pytest.raises(AppException) as exc:
        await _gather_source_texts("exe_nonexistent", deps)
    assert exc.value.status_code == 500


def test_enforce_hypothesis_linking_empty_hypotheses() -> None:
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "thought_process": "Thinking...",
                "conclusion": "Concluded.",
                "confidence_score": 0.9,
                "hypotheses": [],
            }
        ),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)
    result = cast(HookResult, enforce_hypothesis_linking_hook(state, deps))
    assert result.success is True


def test_read_docs_with_files(tmp_path: Path) -> None:
    from backend_v2.hooks.integrity import _read_docs

    doc_file = tmp_path / "test.md"
    doc_file.write_text("Markdown documentation content", encoding="utf-8")

    with patch("backend_v2.hooks.integrity.get_settings") as mock_settings:
        mock_settings.return_value.docs_dir = str(tmp_path)
        content = _read_docs()
    assert "Markdown documentation content" in content


@pytest.mark.asyncio
async def test_verify_citation_integrity_hook_read_docs_os_error() -> None:
    """Negative: test that OSError during reading local context docs raises AppException."""
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={"test": "data"}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = AsyncMock()

    with patch("backend_v2.hooks.integrity._gather_source_texts", new_callable=AsyncMock) as mock_gather:
        mock_gather.return_value = ["Source text"]
        with patch("backend_v2.hooks.integrity._read_docs", side_effect=OSError("Read failure")):
            with pytest.raises(AppException) as exc:
                await cast(Awaitable[HookResult], verify_citation_integrity_hook(state, deps))
            assert exc.value.status_code == 500
            assert "Failed to load local context documents" in exc.value.message


def test_enforce_hypothesis_linking_hook_missing_id() -> None:
    """Negative: test that hypothesis without ID raises AppException with VALIDATION_FAILED."""
    hyp = Hypothesis.model_construct(
        id="",
        claim_text="C1",
        evidence_found=False,
        search_query="Q1",
        quotes=[],
    )
    analyst_output = AnalystOutput.model_construct(
        thought_process="Thinking...",
        conclusion="Concluded.",
        confidence_score=0.9,
        hypotheses=[hyp],
    )
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO.model_construct(raw_inputs=analyst_output),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)
    with pytest.raises(AppException) as exc:
        enforce_hypothesis_linking_hook(state, deps)
    assert exc.value.status_code == 500
    assert "Hypothesis missing ID" in exc.value.message


def test_is_hallucinated_empty_normalized() -> None:
    """Negative: quote whose normalization produces empty text is treated as hallucinated."""
    with patch(
        "backend_v2.services.orchestrator.anchor_validation_service.AnchorValidationService.normalize_text_with_mapping",
        return_value=("", {}),
    ):
        assert _is_hallucinated("Valid quote text", "norm_corpus", threshold=80.0) is True
