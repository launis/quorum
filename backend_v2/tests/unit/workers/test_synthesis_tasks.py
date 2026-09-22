"""Unit tests for synthesis_tasks.py covering task construction and LLM execution."""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import MatrixSynthesisGroup, OutputProfile
from backend_v2.models.dtos.synthesis import (
    ExecutiveSummarySectionResult,
    MatrixExplanationContextDTO,
    MatrixExplanationsResult,
    MatrixSectionSynthesesResult,
    SynthesisDistillationDTO,
    SynthesisRowExplanationDTO,
    SynthesisSectionDTO,
    XaiHighlightItem,
    XaiHighlightsResult,
)
from backend_v2.models.enums import (
    ExecutionStatus,
    PresetView,
    TargetBlockType,
    XaiExtensionType,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.view.sdui import ParagraphBlock
from backend_v2.workers.synthesis_tasks import (
    create_executive_summary_task,
    create_matrix_sections_tasks,
    create_row_explanations_task,
    create_xai_highlights_task,
)


def _make_profile(
    requires_exec: bool = True,
    exec_directive: str | None = "Synthesize executive summary.",
    requires_groups: bool = False,
    groups: list[MatrixSynthesisGroup] | None = None,
    requires_rows: bool = True,
    row_directive: str | None = "Explain row scoring.",
    extensions: list[Any] | None = None,
    xai_directive: str | None = "Synthesize highlights.",
    synthesis_budget: int | None = None,
    row_budget: int | None = None,
    xai_budget: int | None = None,
    graph_budget: int | None = None,
    tone: str | None = None,
) -> OutputProfile:
    blocks = []
    if requires_exec:
        blocks.append(TargetBlockType.EXECUTIVE_SUMMARY_BLOCK)
    if requires_groups:
        blocks.append(TargetBlockType.MATRIX_GRAPHS_BLOCK)
    if requires_rows:
        blocks.append(TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK)
    if extensions:
        blocks.append(TargetBlockType.GROUPED_EXTENSIONS_BLOCK)

    variance_target = (
        "blk_0123456789abcdef01" if (extensions and XaiExtensionType.VARIANCE_VALIDATION in extensions) else None
    )
    return OutputProfile(
        id="pro_0123456789abcdef01",
        slug="prof_test",
        workflow_id="wor_0123456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=blocks or [TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
        executive_summary_directive=exec_directive,
        matrix_1d_synthesis_directive="Synthesize 1D",
        matrix_2d_synthesis_directive="Synthesize 2D",
        matrix_3d_synthesis_directive="Synthesize 3D",
        matrix_text_synthesis_directive="Synthesize Text",
        matrix_synthesis_groups=groups or [],
        row_explanation_directive=row_directive,
        visible_workflow_extensions=extensions or [],
        variance_target_block=variance_target,
        xai_synthesis_directive=xai_directive,
        synthesis_length_constraint=synthesis_budget,
        row_explanation_length_constraint=row_budget,
        xai_length_constraint=xai_budget,
        matrix_graph_length_constraint=graph_budget,
        tone_instruction=tone,
    )


def _make_execution() -> ExecutionRecord:
    return ExecutionRecord(
        id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        output_profile_id="pro_0123456789abcdef01",
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
    )


@pytest.mark.asyncio
async def test_create_executive_summary_task_skips_when_not_required() -> None:
    """Test create_executive_summary_task returns None when executive summary is not required."""
    prof = _make_profile(requires_exec=False, exec_directive="Directives")
    prof = prof.model_copy(update={"target_block_order": [TargetBlockType.PENALTIES_BLOCK]})

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    task = await create_executive_summary_task(AsyncMock(), "sys", [], "distilled", "matrix", prof, dummy_sem)
    assert task is None


@pytest.mark.asyncio
async def test_create_executive_summary_task_skips_when_directive_empty() -> None:
    """Test create_executive_summary_task returns None when directive is missing."""
    prof = _make_profile(requires_exec=True, exec_directive="")

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    task = await create_executive_summary_task(AsyncMock(), "sys", [], "distilled", "matrix", prof, dummy_sem)
    assert task is None


@pytest.mark.asyncio
async def test_create_executive_summary_task_happy_path() -> None:
    """Test create_executive_summary_task compiles context and executes LLM task."""
    prof = _make_profile(
        requires_exec=True,
        exec_directive="Clear executive directive.",
        synthesis_budget=200,
    )
    mock_client = AsyncMock()
    p_block = ParagraphBlock(text="Executive summary content", exact_quotes=[], citations=[])
    expected_result = ExecutiveSummarySectionResult(
        executive_summary=[p_block],
        user_role=None,
        user_role_justification=None,
        cited_sources=[],
    )
    mock_client.run_structured_task.return_value = expected_result

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    res = await create_executive_summary_task(
        mock_client, "sys_prompt", ["<base>1</base>"], "distilled_text", "matrix_text", prof, dummy_sem
    )
    assert res == expected_result
    mock_client.run_structured_task.assert_called_once()


@pytest.mark.asyncio
async def test_create_matrix_sections_tasks_skips_when_no_groups() -> None:
    """Test create_matrix_sections_tasks returns empty list when no groups required."""
    prof = _make_profile(requires_groups=False)
    distilled = SynthesisDistillationDTO(distilled_inputs="inputs")

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    tasks = await create_matrix_sections_tasks(
        AsyncMock(), "sys", [], "distilled", "matrix", prof, distilled, dummy_sem
    )
    assert tasks == []


@pytest.mark.asyncio
async def test_create_matrix_sections_tasks_executes_each_group() -> None:
    """Test create_matrix_sections_tasks generates LLM task for each valid matrix synthesis group."""
    grp1 = MatrixSynthesisGroup(
        id="grp_0123456789abcdef01",
        title=I18nText(translations={"en": "1D Metrics"}),
        view_type=PresetView.METRICS_1D,
        target_blocks=["blk_1"],
    )
    grp2 = MatrixSynthesisGroup(
        id="grp_0123456789abcdef02",
        title=I18nText(translations={"en": "2D Compare"}),
        view_type=PresetView.COMPARE_2D,
        target_blocks=["blk_2", "blk_3"],
    )
    grp3 = MatrixSynthesisGroup(
        id="grp_0123456789abcdef03",
        title=I18nText(translations={"en": "3D Matrix"}),
        view_type=PresetView.MATRIX_3D,
        target_blocks=["blk_1", "blk_2", "blk_3"],
    )
    grp4 = MatrixSynthesisGroup(
        id="grp_0123456789abcdef04",
        title=I18nText(translations={"en": "Text Only"}),
        view_type=PresetView.TEXT_ONLY,
        target_blocks=["blk_1"],
    )
    prof = _make_profile(
        requires_groups=True,
        groups=[grp1, grp2, grp3, grp4],
        graph_budget=100,
    )
    distilled = SynthesisDistillationDTO(
        distilled_inputs="inputs",
        title_map={"blk_1": "Block 1 Title", "blk_2": "Block 2 Title"},
        target_locale="en",
    )
    mock_client = AsyncMock()
    sec = SynthesisSectionDTO(
        layout_id="sec_1",
        content_blocks=[ParagraphBlock(text="Group text", exact_quotes=[], citations=[])],
    )
    mock_client.run_structured_task.return_value = MatrixSectionSynthesesResult(sections=[sec])

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    results = await create_matrix_sections_tasks(
        mock_client, "sys", ["<part>"], "distilled", "matrix", prof, distilled, dummy_sem
    )
    assert len(results) == 4
    assert results[0][0] == "grp_0123456789abcdef01"
    assert results[1][0] == "grp_0123456789abcdef02"
    assert results[2][0] == "grp_0123456789abcdef03"
    assert results[3][0] == "grp_0123456789abcdef04"
    assert mock_client.run_structured_task.call_count == 4


@pytest.mark.asyncio
async def test_create_matrix_sections_tasks_skips_missing_directive() -> None:
    """Test create_matrix_sections_tasks skips groups with missing directive."""
    grp1 = MatrixSynthesisGroup(
        id="grp_0123456789abcdef01",
        title=I18nText(translations={"en": "1D Metrics"}),
        view_type=PresetView.METRICS_1D,
        target_blocks=["blk_1"],
    )
    prof = _make_profile(
        requires_groups=True,
        groups=[grp1],
    )
    prof = prof.model_copy(update={"matrix_1d_synthesis_directive": ""})
    distilled = SynthesisDistillationDTO(distilled_inputs="inputs")

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    results = await create_matrix_sections_tasks(
        AsyncMock(), "sys", [], "distilled", "matrix", prof, distilled, dummy_sem
    )
    assert results == []


@pytest.mark.asyncio
async def test_create_xai_highlights_task_skips_when_no_extensions() -> None:
    """Test create_xai_highlights_task returns None when no extensions are visible."""
    prof = _make_profile(extensions=[])

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    task = await create_xai_highlights_task(AsyncMock(), "sys", [], "distilled", "matrix", prof, dummy_sem)
    assert task is None


@pytest.mark.asyncio
async def test_create_xai_highlights_task_missing_max_items_raises() -> None:
    """Test create_xai_highlights_task raises AppException if max_extension_items is None."""
    prof = OutputProfile.model_construct(
        id="pro_0123456789abcdef01",
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        max_extension_items=None,
    )

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with pytest.raises(AppException) as exc_info:
        await create_xai_highlights_task(AsyncMock(), "sys", [], "distilled", "matrix", prof, dummy_sem)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_create_xai_highlights_task_happy_path() -> None:
    """Test create_xai_highlights_task compiles curation prompt and executes."""
    prof = _make_profile(
        extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        xai_directive="Curate top highlights.",
        xai_budget=80,
    )
    mock_client = AsyncMock()
    item = XaiHighlightItem(extension_type="variance_validation", content="Synthesized highlight.")
    mock_client.run_structured_task.return_value = XaiHighlightsResult(xai_highlights=[item])

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    res = await create_xai_highlights_task(mock_client, "sys", [], "distilled", "matrix", prof, dummy_sem)
    assert isinstance(res, XaiHighlightsResult)
    assert len(res.xai_highlights) == 1


@pytest.mark.asyncio
async def test_create_row_explanations_task_skips_when_empty_matrices() -> None:
    """Test create_row_explanations_task returns None when matrices_to_explain is empty."""
    prof = _make_profile(requires_rows=True)

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    task = await create_row_explanations_task(AsyncMock(), [], prof, "en", _make_execution(), None, dummy_sem)
    assert task is None


@pytest.mark.asyncio
async def test_create_row_explanations_task_happy_path() -> None:
    """Test create_row_explanations_task executes FAST tier LLM client with tone and budget."""
    prof = _make_profile(
        requires_rows=True,
        row_directive="Explain causal row findings.",
        tone="Direct and concise",
        row_budget=60,
    )
    ctx_dto = MatrixExplanationContextDTO(
        matrix_id="m1",
        real_matrix_id="real_m1",
        matrix_label="Matrix 1",
        score=0.9,
        justification="Evidence quote.",
    )
    mock_client = AsyncMock()
    explanation_item = SynthesisRowExplanationDTO(matrix_id="m1", row_explanation="Short explanation.")
    mock_client.run_structured_task.return_value = MatrixExplanationsResult(explanations=[explanation_item])

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with patch("backend_v2.workers.synthesis_tasks.LLMClient.from_tier", return_value=mock_client):
        res = await create_row_explanations_task(
            AsyncMock(), [ctx_dto], prof, "en", _make_execution(), "reg_123", dummy_sem
        )
        assert isinstance(res, MatrixExplanationsResult)
        assert len(res.explanations) == 1
        assert res.explanations[0].row_explanation == "Short explanation."


@pytest.mark.asyncio
async def test_create_row_explanations_task_missing_directive_returns_none() -> None:
    """Test create_row_explanations_task returns None when row_explanation_directive is empty."""
    prof = _make_profile(requires_rows=True, row_directive="")
    ctx_dto = MatrixExplanationContextDTO(
        matrix_id="m1",
        real_matrix_id="real_m1",
        matrix_label="Matrix 1",
        score=0.9,
        justification="Evidence quote.",
    )

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with patch("backend_v2.workers.synthesis_tasks.LLMClient.from_tier", return_value=AsyncMock()):
        res = await create_row_explanations_task(AsyncMock(), [ctx_dto], prof, "en", _make_execution(), None, dummy_sem)
        assert res is None


@pytest.mark.asyncio
async def test_create_row_explanations_task_none_profile_returns_none() -> None:
    """Test create_row_explanations_task returns None when profile is None."""
    ctx_dto = MatrixExplanationContextDTO(
        matrix_id="m1",
        real_matrix_id="real_m1",
        matrix_label="Matrix 1",
        score=0.9,
        justification="Evidence quote.",
    )

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with patch("backend_v2.workers.synthesis_tasks.LLMClient.from_tier", return_value=AsyncMock()):
        res = await create_row_explanations_task(AsyncMock(), [ctx_dto], None, "en", _make_execution(), None, dummy_sem)
        assert res is None


@pytest.mark.asyncio
async def test_create_xai_highlights_task_missing_directive_returns_none() -> None:
    """Test create_xai_highlights_task returns None when xai_synthesis_directive is empty."""
    prof = _make_profile(extensions=[XaiExtensionType.VARIANCE_VALIDATION], xai_directive="")

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    res = await create_xai_highlights_task(AsyncMock(), "sys", [], "distilled", "matrix", prof, dummy_sem)
    assert res is None


@pytest.mark.asyncio
async def test_create_executive_summary_task_none_profile_returns_none() -> None:
    """Test create_executive_summary_task returns None when active_profile_dto is None."""

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    res = await create_executive_summary_task(AsyncMock(), "sys", [], "distilled", "matrix", None, dummy_sem)
    assert res is None


@pytest.mark.asyncio
async def test_create_matrix_sections_tasks_unknown_view_type_skips() -> None:
    """Test create_matrix_sections_tasks skips groups with unrecognized view_type."""
    grp = MatrixSynthesisGroup(
        id="grp_0123456789abcdef",
        title=I18nText(translations={"en": "Unknown Group"}),
        view_type=PresetView.METRICS_1D,
        target_blocks=["blk_0123456789abcdef01"],
    )
    grp_unknown = grp.model_copy(update={"view_type": "invalid_custom_type"})
    prof = _make_profile(requires_groups=True, groups=[grp_unknown])

    distilled = SynthesisDistillationDTO(distilled_inputs="inputs")

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    results = await create_matrix_sections_tasks(
        AsyncMock(), "sys", [], "distilled", "matrix", prof, distilled, dummy_sem
    )
    assert results == []


@pytest.mark.asyncio
async def test_create_xai_highlights_task_with_block_extensions() -> None:
    """Test create_xai_highlights_task includes visible_block_extensions."""
    prof = _make_profile(extensions=[XaiExtensionType.VARIANCE_VALIDATION]).model_copy(
        update={
            "visible_block_extensions": [XaiExtensionType.VARIANCE_VALIDATION],
            "max_extension_items": 5,
            "xai_synthesis_directive": "Synthesize block extensions.",
        }
    )

    mock_client = AsyncMock()
    mock_client.run_structured_task = AsyncMock(
        return_value=(
            XaiHighlightsResult(
                xai_highlights=[
                    XaiHighlightItem(
                        extension_type="variance_validation",
                        content="Synthesized highlight.",
                    )
                ]
            ),
            None,
        )
    )

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    res = await create_xai_highlights_task(mock_client, "sys", [], "distilled", "matrix", prof, dummy_sem)
    assert res is not None
