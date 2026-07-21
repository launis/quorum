from unittest.mock import AsyncMock
"""Unit tests for static_charts.py."""

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.v2_core import I18nText, MatrixScorecardRowDTO
from backend_v2.utils.static_charts import generate_radar_chart, generate_scatter_chart


def get_i18n(text: str) -> I18nText:
    """Helper to create I18nText."""
    return I18nText(default_locale="fi", translations={"fi": text, "en": text})


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


def test_generate_scatter_chart_success() -> None:
    """Test scatter chart generation succeeds and returns base64."""
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
    result = generate_scatter_chart(axes)
    assert result.startswith("iVBORw0KGgo") or len(result) > 100


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
