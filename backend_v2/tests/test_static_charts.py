from typing import Any
from backend_v2.models.v2_core import ReportAxisDTO
from backend_v2.utils.static_charts import generate_radar_chart, generate_scatter_chart


def test_generate_scatter_chart() -> None:
    axes = [
        ReportAxisDTO(name="X Axis", score=2.5, scale_min=0.0, scale_max=5.0),
        ReportAxisDTO(name="Y Axis", score=4.0, scale_min=0.0, scale_max=5.0),
        ReportAxisDTO(name="Z Axis", score=3.0, scale_min=0.0, scale_max=5.0),
    ]
    b64 = generate_scatter_chart(axes)
    assert b64 != ""
    assert b64.startswith("iVBORw0K")  # PNG binary header signature


def test_generate_radar_chart() -> None:
    axes = [
        ReportAxisDTO(name="Dim 1", score=2.5, scale_min=0.0, scale_max=5.0),
        ReportAxisDTO(name="Dim 2", score=4.0, scale_min=0.0, scale_max=5.0),
        ReportAxisDTO(name="Dim 3", score=3.0, scale_min=0.0, scale_max=5.0),
    ]
    b64 = generate_radar_chart(axes)
    assert b64 != ""
    assert b64.startswith("iVBORw0K")


def test_empty_scatter() -> None:
    axes = [ReportAxisDTO(name="Only One", score=2.0)]
    b64 = generate_scatter_chart(axes)
    assert b64 == ""


def test_empty_radar() -> None:
    axes = [
        ReportAxisDTO(name="Dim 1", score=2.0),
        ReportAxisDTO(name="Dim 2", score=2.0),
    ]
    b64 = generate_radar_chart(axes)
    assert b64 == ""
