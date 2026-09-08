"""Unit tests for Variance Validation SDUI Adapter.

Covers positive 2D scatter matrix generation, sycophancy detection,
fallback and localized synthesis paragraphs, 4-metric grid, bullet phrases,
and negative validation exception branches.
"""

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import VisualIntent, XaiExtensionType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExtensionMetricsDTO,
    I18nText,
    OutputProfile,
    RenderedSynthesisCache,
)
from backend_v2.models.view.sdui import (
    AlertBlock,
    BulletListBlock,
    MarkdownBlock,
    ParagraphBlock,
    SduiGridBlock,
    SduiQuadrantMatrixBlock,
)
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.variance_adapter import VarianceAdapter


def _create_profile(extensions: list[XaiExtensionType] | None = None) -> OutputProfile:
    return OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        visible_workflow_extensions=extensions if extensions is not None else [XaiExtensionType.VARIANCE_VALIDATION],
    )


def _create_execution(
    context_vars: dict | None = None,
) -> ExecutionRecord:
    return ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        output_profile_id="prf_0123456789abcdef0123456789abcdef",
        execution_trace=[],
        context_variables=context_vars if context_vars is not None else {},
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )


def test_build_missing_execution_raises_app_exception() -> None:
    """Assert that build raises AppException when execution is missing."""
    profile = _create_profile()
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )

    with pytest.raises(AppException) as exc_info:
        VarianceAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "context.execution cannot be None" in exc_info.value.message


def test_build_missing_metrics_raises_app_exception() -> None:
    """Assert that build raises AppException when extension metrics are missing in profile cache."""
    profile = _create_profile()
    execution = _create_execution()
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )

    with pytest.raises(AppException) as exc_info:
        VarianceAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "Strict Fail-Fast Enforced: 'variance_validation' requested" in exc_info.value.message


def test_build_incomplete_metrics_raises_app_exception() -> None:
    """Assert that build raises AppException when extension metrics fields are incomplete."""
    profile = _create_profile()
    execution = _create_execution()
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(
            authenticity_score=1.5,
            performative_phrases_count=None,
            variance_score=0.2,
            alignment_verdict="ALIGNED",
        ),
    )
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )

    with pytest.raises(AppException) as exc_info:
        VarianceAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "metrics are incomplete" in exc_info.value.message


def test_build_empty_when_extension_not_requested() -> None:
    """Assert that build returns empty list when variance validation extension is not enabled."""
    profile = _create_profile(extensions=[])
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    blocks = VarianceAdapter.build(context)
    assert blocks == []


def test_build_starved_returns_empty() -> None:
    """Assert that build returns empty list when execution data is starved."""
    from backend_v2.models.dtos.trace import DataStarvationEvent

    profile = _create_profile()
    cache = RenderedSynthesisCache(
        data_starvation=DataStarvationEvent(total_atoms=0, reason="insufficient_tokens"),
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    blocks = VarianceAdapter.build(context)
    assert blocks == []


def test_build_aligned_success() -> None:
    """Verify that build emits flat 2D scatter plot, grid metrics, and info alert for aligned verdict."""
    profile = _create_profile()
    execution = _create_execution()
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(
            authenticity_score=2.8,
            performative_phrases_count=0.0,
            variance_score=0.2,
            alignment_verdict="ALIGNED",
        ),
        variance_explanation="Model reasoning aligned closely with target assertions.",
    )
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )

    blocks = VarianceAdapter.build(context)
    # Sequence: MarkdownBlock, ParagraphBlock, SduiScatterPlotBlock, SduiGridBlock, AlertBlock
    assert len(blocks) == 5
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Cognitive Depth & Phrase Analysis"
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "Model reasoning aligned closely with target assertions."

    assert isinstance(blocks[2], SduiQuadrantMatrixBlock)
    assert len(blocks[2].axes) == 2
    assert blocks[2].axes[0].block_id == "axis_cognitive_depth"
    assert blocks[2].axes[0].score == 2.8
    assert blocks[2].axes[0].scale_min == 1.0
    assert blocks[2].axes[0].scale_max == 3.0
    assert blocks[2].axes[0].ui_plot_ratio == 0.9  # (2.8 - 1.0) / 2.0 = 0.9

    assert blocks[2].axes[1].block_id == "axis_mechanical_load"
    assert blocks[2].axes[1].score == 0.0
    assert blocks[2].axes[1].scale_min == 0.0
    assert blocks[2].axes[1].scale_max == 2.0
    assert blocks[2].axes[1].ui_plot_ratio == 0.0

    assert isinstance(blocks[3], SduiGridBlock)
    assert len(blocks[3].items) == 4
    assert "0 pcs" in blocks[3].items[0].text
    assert "2.8 / 3.0" in blocks[3].items[1].text

    assert isinstance(blocks[4], AlertBlock)
    assert blocks[4].severity == VisualIntent.INFO
    assert "Aligned" in blocks[4].text


def test_build_misaligned_sycophancy_with_detected_phrases() -> None:
    """Verify that build emits warning alert and bullet list of phrases for sycophancy verdict."""
    profile = _create_profile()
    execution = _create_execution(
        context_vars={
            "step_linguistics": {
                "performative_patterns": [
                    {"pattern_id": "p1", "detected_phrase": "strateginen linjaus", "category": "filler"},
                    {"pattern_id": "p2", "detected_phrase": "optimaalinen suorite", "category": "filler"},
                ]
            }
        }
    )
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(
            authenticity_score=1.14,
            performative_phrases_count=2.0,
            variance_score=1.46,
            alignment_verdict="MISALIGNED_SYCOPHANCY",
        ),
    )
    context = AdapterContext(
        execution=execution,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )

    blocks = VarianceAdapter.build(context)
    # Sequence: MarkdownBlock, ParagraphBlock, SduiScatterPlotBlock, SduiGridBlock, BulletListBlock, AlertBlock
    assert len(blocks) == 6
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Ajattelun syvyys ja fraasianalyysi"

    assert isinstance(blocks[1], ParagraphBlock)
    # Fallback explanation when row_explanations omitted
    assert "Mekaanisia ja kognitiivisia" in blocks[1].text

    assert isinstance(blocks[2], SduiQuadrantMatrixBlock)
    assert blocks[2].axes[0].score == 1.14
    assert blocks[2].axes[0].ui_plot_ratio == 0.07  # round((1.14 - 1.0) / 2.0, 4) == 0.07
    assert blocks[2].axes[1].score == 2.0
    assert blocks[2].axes[1].ui_plot_ratio == 0.2  # min((2.0 / 10.0) * 2.0, 2.0) / 2.0 == 0.2

    assert isinstance(blocks[3], SduiGridBlock)
    assert len(blocks[3].items) == 4
    assert "2 kpl" in blocks[3].items[0].text
    assert "1.14 / 3.0" in blocks[3].items[1].text
    assert "2" in blocks[3].items[3].text

    assert isinstance(blocks[4], BulletListBlock)
    assert len(blocks[4].items) == 2
    assert "strateginen linjaus" in blocks[4].items[0].text
    assert "optimaalinen suorite" in blocks[4].items[1].text

    assert isinstance(blocks[5], AlertBlock)
    assert blocks[5].severity == VisualIntent.WARNING
    assert "Ristiriidassa (Mielistelyriski)" in blocks[5].text


def test_build_with_jargon_density_calibrates_y_axis_and_grid() -> None:
    """Verify that build correctly handles jargon_density on Y-axis and 4-metric grid."""
    profile = _create_profile()
    execution = _create_execution(
        context_vars={
            "step_linguistics": {
                "performative_patterns": [
                    {"pattern_id": "p1", "detected_phrase": "strateginen linjaus", "category": "filler"},
                    {"pattern_id": "p2", "detected_phrase": "optimaalinen suorite", "category": "filler"},
                ]
            }
        }
    )
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(
            authenticity_score=1.14,
            performative_phrases_count=2.0,
            variance_score=1.46,
            alignment_verdict="MISALIGNED_SYCOPHANCY",
            jargon_density=5.0,
            total_word_count=40,
        ),
    )
    context = AdapterContext(
        execution=execution,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )

    blocks = VarianceAdapter.build(context)
    assert len(blocks) == 6
    quadrant = blocks[2]
    assert isinstance(quadrant, SduiQuadrantMatrixBlock)
    assert quadrant.axes[1].score == 5.0
    assert quadrant.axes[1].ui_plot_ratio == 1.0  # min((5.0 / 5.0) * 2.0, 2.0) / 2.0 == 1.0

    grid = blocks[3]
    assert isinstance(grid, SduiGridBlock)
    assert "2 (5.0/100w)" in grid.items[3].text


def test_build_unmapped_verdict_raises_configuration_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Assert that build raises configuration AppException when rule mapping is missing."""
    profile = _create_profile()
    execution = _create_execution()
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(
            authenticity_score=1.5,
            performative_phrases_count=1.0,
            variance_score=0.5,
            alignment_verdict="UNKNOWN_CUSTOM_VERDICT",
        ),
    )
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )

    # Empty VARIANCE_RULES to force a KeyError lookup failure
    monkeypatch.setattr("backend_v2.services.sdui.adapters.variance_adapter.VARIANCE_RULES", {})

    with pytest.raises(AppException) as exc_info:
        VarianceAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "Missing rule mapping for type_key" in exc_info.value.message
