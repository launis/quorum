from unittest.mock import MagicMock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.pii_analyzer import PIIAnalyzerService


@pytest.fixture
def pii_service() -> PIIAnalyzerService:
    """Returns a fresh instance of PIIAnalyzerService for each test."""
    # Reset singleton State
    PIIAnalyzerService._instance = None
    return PIIAnalyzerService.get_instance()


def test_lazy_loading_singleton(pii_service: PIIAnalyzerService) -> None:
    """Test that the models are not loaded until mask_pii is actively called."""
    assert pii_service._analyzer is None
    assert pii_service._anonymizer is None

    # Simulate an empty string bypass
    result = pii_service.mask_pii("", language="en")
    assert result == ""
    assert pii_service._analyzer is None


@patch("presidio_analyzer.AnalyzerEngine")
@patch("presidio_anonymizer.AnonymizerEngine")
def test_mask_pii_initialization(
    mock_anonymizer_class: MagicMock,
    mock_analyzer_class: MagicMock,
    pii_service: PIIAnalyzerService,
) -> None:
    """Test standard PII masking logic with mocked Presidio framework."""
    mock_analyzer = MagicMock()
    mock_analyzer_class.return_value = mock_analyzer
    mock_analyzer.analyze.return_value = ["mocked_result"]

    mock_anonymizer = MagicMock()
    mock_anonymizer_class.return_value = mock_anonymizer

    # Mock the return pattern of anonymizer to return a faux structure
    mock_anonymized_result = MagicMock()
    mock_anonymized_result.text = "Hello <PERSON>"
    mock_anonymizer.anonymize.return_value = mock_anonymized_result

    res = pii_service.mask_pii("Hello John Doe", language="en")

    # Verify the initialization triggered
    mock_analyzer_class.assert_called_once()
    mock_anonymizer_class.assert_called_once()

    # Verify processing calls
    mock_analyzer.analyze.assert_called_once_with(text="Hello John Doe", entities=[], language="en")
    mock_anonymizer.anonymize.assert_called_once_with(text="Hello John Doe", analyzer_results=["mocked_result"])
    assert res == "Hello <PERSON>"


@patch("presidio_analyzer.AnalyzerEngine", side_effect=OSError("Model missing"))
def test_mask_pii_spacy_model_missing(mock_analyzer_class: MagicMock, pii_service: PIIAnalyzerService) -> None:
    """Test Fail-Fast doctrine if Spacy en_core_web_lg model is missing."""
    with pytest.raises(AppException) as exc_info:
        pii_service.mask_pii("Some text", language="en")

    assert "Presidio model 'en_core_web_lg' not found" in str(exc_info.value)
