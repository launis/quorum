import pytest
from pydantic import TypeAdapter, ValidationError

from backend_v2.models.view.sdui import (
    AnySduiBlock,
    SduiMatrixTableBlock,
    SduiMetrics1DBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)


def test_sdui_radar_chart_roundtrip():
    """Positive serialization roundtrip test for SduiRadarChartBlock."""
    data = {
        "block_type": "3d_matrix",
        "title": {"default_locale": "en", "translations": {"en": "Radar Chart", "fi": "Tutkakaavio"}},
        "axes": [],
        "text_delivery_mode": "full",
    }
    block = SduiRadarChartBlock.model_validate(data)
    assert block.block_type == "3d_matrix"
    assert block.title.translations["en"] == "Radar Chart"
    assert block.text_delivery_mode == "full"

    # Test through union
    adapter = TypeAdapter(AnySduiBlock)
    union_block = adapter.validate_python(data)
    assert isinstance(union_block, SduiRadarChartBlock)


def test_sdui_scatter_plot_roundtrip():
    """Positive serialization roundtrip test for SduiScatterPlotBlock."""
    data = {
        "block_type": "2d_compare",
        "text_delivery_mode": "titles_only",
    }
    block = SduiScatterPlotBlock.model_validate(data)
    assert block.block_type == "2d_compare"
    assert block.text_delivery_mode == "titles_only"

    adapter = TypeAdapter(AnySduiBlock)
    union_block = adapter.validate_python(data)
    assert isinstance(union_block, SduiScatterPlotBlock)


def test_sdui_matrix_table_roundtrip():
    """Positive serialization roundtrip test for SduiMatrixTableBlock."""
    data = {
        "block_type": "matrix_summary",
        "matrix_column_labels": {"score": {"default_locale": "en", "translations": {"en": "Score"}}},
        "matrix_visible_columns": ["score"],
    }
    block = SduiMatrixTableBlock.model_validate(data)
    assert block.block_type == "matrix_summary"
    assert block.matrix_visible_columns == ["score"]

    adapter = TypeAdapter(AnySduiBlock)
    union_block = adapter.validate_python(data)
    assert isinstance(union_block, SduiMatrixTableBlock)


def test_sdui_metrics_1d_roundtrip():
    """Positive serialization roundtrip test for SduiMetrics1DBlock."""
    data = {
        "block_type": "1d_metrics",
        "title": {"default_locale": "en", "translations": {"en": "1D Metrics"}},
        "text_delivery_mode": "none",
    }
    block = SduiMetrics1DBlock.model_validate(data)
    assert block.block_type == "1d_metrics"
    assert block.text_delivery_mode == "none"

    adapter = TypeAdapter(AnySduiBlock)
    union_block = adapter.validate_python(data)
    assert isinstance(union_block, SduiMetrics1DBlock)


def test_sdui_matrix_table_block_missing_axes():
    """Negative test: Validation error when axes is given an invalid type (e.g. None)."""
    with pytest.raises(ValidationError):
        SduiMatrixTableBlock.model_validate({"block_type": "matrix_summary", "axes": None})


def test_sdui_radar_chart_extra_keys():
    """Negative test: Validation error on unrecognized keys, enforcing extra='forbid'."""
    with pytest.raises(ValidationError):
        SduiRadarChartBlock.model_validate(
            {
                "block_type": "3d_matrix",
                "random_extra_key": "should fail",
            }
        )


def test_sdui_scatter_plot_invalid_text_mode():
    """Negative test: Validation error for invalid text_delivery_mode."""
    with pytest.raises(ValidationError):
        SduiScatterPlotBlock.model_validate(
            {
                "block_type": "2d_compare",
                "text_delivery_mode": "invalid_mode",
            }
        )


def test_sdui_metrics_1d_invalid_type():
    """Negative test: Validation error if block_type is wrong."""
    with pytest.raises(ValidationError):
        SduiMetrics1DBlock.model_validate(
            {
                "block_type": "invalid_type",
            }
        )
