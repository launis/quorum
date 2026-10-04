import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.utils.static_charts import generate_radar_chart, generate_scatter_chart


def _i18n(text: str) -> I18nText:
    return I18nText(translations={"fi": text, "en": text})


def test_generate_scatter_chart() -> None:
    axes = [
        MatrixScorecardRowDTO(
            block_id="1",
            name="X Axis",
            label_i18n=_i18n("X"),
            score=2.5,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="2",
            name="Y Axis",
            label_i18n=_i18n("Y"),
            score=4.0,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="3",
            name="Z Axis",
            label_i18n=_i18n("Z"),
            score=3.0,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
    ]
    b64 = generate_scatter_chart(axes)
    assert b64 != ""
    assert b64.startswith("iVBORw0K")  # PNG binary header signature


def test_generate_radar_chart() -> None:
    axes = [
        MatrixScorecardRowDTO(
            block_id="1",
            name="Dim 1",
            label_i18n=_i18n("D1"),
            score=2.5,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="2",
            name="Dim 2",
            label_i18n=_i18n("D2"),
            score=4.0,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="3",
            name="Dim 3",
            label_i18n=_i18n("D3"),
            score=3.0,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
    ]
    b64 = generate_radar_chart(axes)
    assert b64 != ""
    assert b64.startswith("iVBORw0K")


def test_empty_scatter() -> None:
    axes = [
        MatrixScorecardRowDTO(
            block_id="1",
            name="Only One",
            label_i18n=_i18n("O1"),
            score=2.0,
            row_explanation="ok",
            is_evaluative=True,
        )
    ]
    with pytest.raises(AppException):
        generate_scatter_chart(axes)


def test_empty_radar() -> None:
    axes = [
        MatrixScorecardRowDTO(
            block_id="1",
            name="Dim 1",
            label_i18n=_i18n("D1"),
            score=2.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="2",
            name="Dim 2",
            label_i18n=_i18n("D2"),
            score=2.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
    ]
    with pytest.raises(AppException):
        generate_radar_chart(axes)
