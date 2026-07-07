import pytest

from backend_v2.models.v2_core import MatrixScorecardRowDTO
from backend_v2.utils.static_charts import generate_radar_chart, generate_scatter_chart


def test_generate_scatter_chart() -> None:
    axes = [
        MatrixScorecardRowDTO(
            block_id="1",
            name="X Axis",
            label_i18n={"default_locale": "en", "translations": {"fi": "X", "en": "X"}},  # type: ignore[arg-type]
            score=2.5,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="2",
            name="Y Axis",
            label_i18n={"default_locale": "en", "translations": {"fi": "Y", "en": "Y"}},  # type: ignore[arg-type]
            score=4.0,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="3",
            name="Z Axis",
            label_i18n={"default_locale": "en", "translations": {"fi": "Z", "en": "Z"}},  # type: ignore[arg-type]
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
            label_i18n={"default_locale": "en", "translations": {"fi": "D1", "en": "D1"}},  # type: ignore[arg-type]
            score=2.5,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="2",
            name="Dim 2",
            label_i18n={"default_locale": "en", "translations": {"fi": "D2", "en": "D2"}},  # type: ignore[arg-type]
            score=4.0,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="3",
            name="Dim 3",
            label_i18n={"default_locale": "en", "translations": {"fi": "D3", "en": "D3"}},  # type: ignore[arg-type]
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
            label_i18n={"default_locale": "en", "translations": {"fi": "O1", "en": "O1"}},  # type: ignore[arg-type]
            score=2.0,
            row_explanation="ok",
            is_evaluative=True,
        )
    ]
    from backend_v2.exceptions import AppException
    with pytest.raises(AppException):
        b64 = generate_scatter_chart(axes)


def test_empty_radar() -> None:
    axes = [
        MatrixScorecardRowDTO(
            block_id="1",
            name="Dim 1",
            label_i18n={"default_locale": "en", "translations": {"fi": "D1", "en": "D1"}},  # type: ignore[arg-type]
            score=2.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="2",
            name="Dim 2",
            label_i18n={"default_locale": "en", "translations": {"fi": "D2", "en": "D2"}},  # type: ignore[arg-type]
            score=2.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
    ]
    from backend_v2.exceptions import AppException
    with pytest.raises(AppException):
        b64 = generate_radar_chart(axes)
