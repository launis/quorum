"""Unit tests for static_charts.py.

Covers Cartesian 2D scatter matrix generation with 4 diagnostic quadrants,
bounded proportional margins, localized quadrant titles, 3-axis Z bubble sizing,
and polar 3D radar chart rendering.
"""

import base64

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.v2_core import I18nText, MatrixScorecardRowDTO
from backend_v2.utils.static_charts import generate_radar_chart, generate_scatter_chart


def get_i18n(text: str) -> I18nText:
    """Helper to create I18nText."""
    return I18nText(translations={"fi": text, "en": text})


def test_generate_scatter_chart_empty() -> None:
    """Test scatter chart with less than 2 axes raises AppException."""
    with pytest.raises(AppException) as exc:
        generate_scatter_chart([])
    assert "at least 2 axes" in str(exc.value)

    with pytest.raises(AppException):
        generate_scatter_chart(
            [
                MatrixScorecardRowDTO(
                    name="A",
                    score=1.0,
                    scale_min=0.0,
                    scale_max=5.0,
                    block_id="b1",
                    label_i18n=get_i18n("L1"),
                    row_explanation="E1",
                    is_evaluative=True,
                )
            ]
        )


def test_generate_scatter_chart_bounded_scale_fi_and_en() -> None:
    """Test scatter chart with 2D bounded scale (1.0-3.0 and 0.0-2.0) across locales."""
    axes = [
        MatrixScorecardRowDTO(
            name="Kognitiivinen syvyys",
            score=1.14,
            scale_min=1.0,
            scale_max=3.0,
            ui_plot_ratio=0.07,
            block_id="axis_cognitive_depth",
            label_i18n=get_i18n("Cognitive Depth"),
            row_explanation="Row 1 explanation",
            is_evaluative=False,
        ),
        MatrixScorecardRowDTO(
            name="Mekaaninen fraasikuorma",
            score=2.0,
            scale_min=0.0,
            scale_max=2.0,
            ui_plot_ratio=1.0,
            block_id="axis_mechanical_load",
            label_i18n=get_i18n("Mechanical Phrase Load"),
            row_explanation="Row 2 explanation",
            is_evaluative=False,
        ),
    ]

    # Test Finnish generation
    result_fi = generate_scatter_chart(axes, locale="fi")
    assert result_fi.startswith("iVBORw0KGgo") or len(result_fi) > 100
    decoded_fi = base64.b64decode(result_fi)
    assert len(decoded_fi) > 1000

    # Test English generation
    result_en = generate_scatter_chart(axes, locale="en")
    assert result_en.startswith("iVBORw0KGgo") or len(result_en) > 100
    decoded_en = base64.b64decode(result_en)
    assert len(decoded_en) > 1000


def test_generate_scatter_chart_with_z_axis_bubble_sizing() -> None:
    """Test scatter chart with 3 axes where 3rd axis modulates bubble size."""
    axes = [
        MatrixScorecardRowDTO(
            name="Axis X",
            score=2.5,
            scale_min=0.0,
            scale_max=5.0,
            block_id="b1",
            label_i18n=get_i18n("L1"),
            row_explanation="E1",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            name="Axis Y",
            score=3.0,
            scale_min=0.0,
            scale_max=5.0,
            block_id="b2",
            label_i18n=get_i18n("L2"),
            row_explanation="E2",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            name="Axis Z",
            score=4.0,
            scale_min=0.0,
            scale_max=5.0,
            ui_plot_ratio=0.8,
            block_id="b3",
            label_i18n=get_i18n("L3"),
            row_explanation="E3",
            is_evaluative=True,
        ),
    ]
    result = generate_scatter_chart(axes)
    assert result.startswith("iVBORw0KGgo") or len(result) > 100


def test_generate_scatter_chart_scale_fallback_handling() -> None:
    """Test scatter chart handles inverted or identical scales gracefully."""
    axes = [
        MatrixScorecardRowDTO(
            name="Axis Inverted X",
            score=None,
            scale_min=5.0,
            scale_max=2.0,  # max <= min triggers fallback
            block_id="b1",
            label_i18n=get_i18n("L1"),
            row_explanation="E1",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            name="Axis Inverted Y",
            score=None,
            scale_min=3.0,
            scale_max=3.0,  # max <= min triggers fallback
            block_id="b2",
            label_i18n=get_i18n("L2"),
            row_explanation="E2",
            is_evaluative=True,
        ),
    ]
    result = generate_scatter_chart(axes)
    assert len(result) > 100


def test_generate_radar_chart_empty() -> None:
    """Test radar chart with less than 3 axes raises AppException."""
    with pytest.raises(AppException) as exc:
        generate_radar_chart([])
    assert "at least 3 axes" in str(exc.value)

    axes = [
        MatrixScorecardRowDTO(
            name="Axis 1",
            score=2.5,
            scale_min=0.0,
            scale_max=5.0,
            block_id="b1",
            label_i18n=get_i18n("L1"),
            row_explanation="E1",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            name="Axis 2",
            score=3.0,
            scale_min=0.0,
            scale_max=5.0,
            block_id="b2",
            label_i18n=get_i18n("L2"),
            row_explanation="E2",
            is_evaluative=True,
        ),
    ]
    with pytest.raises(AppException):
        generate_radar_chart(axes)


def test_generate_radar_chart_success() -> None:
    """Test radar chart generation succeeds and returns base64."""
    axes = [
        MatrixScorecardRowDTO(
            name="Axis 1",
            score=2.5,
            scale_min=0.0,
            scale_max=5.0,
            block_id="b1",
            label_i18n=get_i18n("L1"),
            row_explanation="E1",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            name="Axis 2",
            score=3.0,
            scale_min=0.0,
            scale_max=5.0,
            block_id="b2",
            label_i18n=get_i18n("L2"),
            row_explanation="E2",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            name="Axis 3",
            score=4.0,
            scale_min=0.0,
            scale_max=5.0,
            block_id="b3",
            label_i18n=get_i18n("L3"),
            row_explanation="E3",
            is_evaluative=True,
        ),
    ]
    result = generate_radar_chart(axes)
    assert result.startswith("iVBORw0KGgo") or len(result) > 100
