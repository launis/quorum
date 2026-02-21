
from unittest.mock import patch

import pytest

from backend.exceptions import AppException
from backend.services.chart_service import ChartService


class TestChartService:
    def test_generate_radar_chart_valid(self):
        """Test valid input returns a base64 encoded png string."""
        scores = {"Logic": 3.0, "Ethics": 4.0, "Clarity": 2.5}
        result = ChartService.generate_radar_chart(scores)
        assert isinstance(result, str)
        assert result.startswith("data:image/png;base64,")

    def test_generate_radar_chart_empty(self):
        """Test empty input raises AppException."""
        with pytest.raises(AppException):
            ChartService.generate_radar_chart({})

    def test_generate_radar_chart_none(self):
        """Test None raises AppException as per fail-fast."""
        with pytest.raises(AppException):
            ChartService.generate_radar_chart(None) # type: ignore

    def test_generate_radar_chart_failure(self):
        """Test that validation/generation errors raise AppException."""
        # Mocking Figure to raise an exception
        with patch("backend.services.chart_service.Figure") as mock_figure:
            mock_figure.side_effect = Exception("Matplotlib error")

            scores = {"Logic": 3.0}
            with pytest.raises(AppException) as excinfo:
                ChartService.generate_radar_chart(scores)

            assert "Failed to generate radar chart" in str(excinfo.value)
            assert excinfo.value.error_code == "CHART_GENERATION_FAILED"

