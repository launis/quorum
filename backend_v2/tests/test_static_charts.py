from backend_v2.models.v2_core import MatrixScorecardRowDTO
from backend_v2.utils.static_charts import generate_radar_chart, generate_scatter_chart


def test_generate_scatter_chart() -> None:
    axes = [
        MatrixScorecardRowDTO(
            block_id="1",
            name="X Axis",
            label_fi="X",
            label_en="X",
            score=2.5,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="2",
            name="Y Axis",
            label_fi="Y",
            label_en="Y",
            score=4.0,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="3",
            name="Z Axis",
            label_fi="Z",
            label_en="Z",
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
            label_fi="D1",
            label_en="D1",
            score=2.5,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="2",
            name="Dim 2",
            label_fi="D2",
            label_en="D2",
            score=4.0,
            scale_min=0.0,
            scale_max=5.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="3",
            name="Dim 3",
            label_fi="D3",
            label_en="D3",
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
            label_fi="O1",
            label_en="O1",
            score=2.0,
            row_explanation="ok",
            is_evaluative=True,
        )
    ]
    b64 = generate_scatter_chart(axes)
    assert b64 == ""


def test_empty_radar() -> None:
    axes = [
        MatrixScorecardRowDTO(
            block_id="1",
            name="Dim 1",
            label_fi="D1",
            label_en="D1",
            score=2.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
        MatrixScorecardRowDTO(
            block_id="2",
            name="Dim 2",
            label_fi="D2",
            label_en="D2",
            score=2.0,
            row_explanation="ok",
            is_evaluative=True,
        ),
    ]
    b64 = generate_radar_chart(axes)
    assert b64 == ""
