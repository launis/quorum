from unittest.mock import MagicMock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.pii_analyzer import PIIAnalyzerService


@pytest.fixture
def pii_service() -> PIIAnalyzerService:
    """Returns a fresh instance of PIIAnalyzerService for each test."""
    from backend_v2.services.pii_analyzer import get_pii_service

    get_pii_service.cache_clear()
    return get_pii_service()


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

    assert "Presidio model 'en_core_web_lg' or 'fi_core_news_lg' not found" in str(exc_info.value)


def test_mask_pii_succeeds_on_supported_language_fi(pii_service: PIIAnalyzerService) -> None:
    """Verify that mask_pii successfully initializes and parses Finnish without throwing ValueError."""
    # This should return a string (either masked or untouched depending on Presidio models),
    # but the key is that it NO LONGER raises a ValueError for missing language registry.
    result = pii_service.mask_pii("Matti Meikäläinen", language="fi")
    assert isinstance(result, str)


def test_chunk_text_splits_on_newline(pii_service: PIIAnalyzerService) -> None:
    """Test chunking logic prioritizes newlines within margin."""
    text = "A" * 50 + "\n" + "B" * 60
    # max_chars = 100, margin = 50. newline at index 50
    chunks = pii_service._chunk_text(text, 100)
    assert len(chunks) == 2
    assert chunks[0] == "A" * 50 + "\n"
    assert chunks[1] == "B" * 60


def test_chunk_text_hard_fallback(pii_service: PIIAnalyzerService) -> None:
    """Test chunking falls back to exact max_chars if no space or newline."""
    text = "A" * 150
    chunks = pii_service._chunk_text(text, 100)
    assert len(chunks) == 2
    assert chunks[0] == "A" * 100
    assert chunks[1] == "A" * 50


@patch("backend_v2.services.pii_analyzer.get_settings")
@patch("presidio_analyzer.AnalyzerEngine")
@patch("presidio_anonymizer.AnonymizerEngine")
def test_mask_pii_exceeds_spacy_limit(
    mock_anonymizer_class: MagicMock,
    mock_analyzer_class: MagicMock,
    mock_get_settings: MagicMock,
    pii_service: PIIAnalyzerService,
) -> None:
    """Test mask_pii chunks text gracefully when exceeding limit."""
    mock_settings = MagicMock()
    mock_settings.pii_spacy_max_chunk_chars = 10
    mock_get_settings.return_value = mock_settings

    mock_analyzer = MagicMock()
    mock_analyzer_class.return_value = mock_analyzer
    mock_analyzer.analyze.return_value = ["mocked_result"]

    mock_anonymizer = MagicMock()
    mock_anonymizer_class.return_value = mock_anonymizer

    def side_effect_anonymize(*args, **kwargs):
        res = MagicMock()
        res.text = kwargs["text"] + "_X"
        return res

    mock_anonymizer.anonymize.side_effect = side_effect_anonymize

    res = pii_service.mask_pii("A" * 15, language="en")

    assert mock_analyzer.analyze.call_count == 2
    assert mock_anonymizer.anonymize.call_count == 2
    assert res == "AAAAAAAAAA_XAAAAA_X"


@patch("backend_v2.services.pii_analyzer.get_settings")
def test_smooth_text_exceeds_spacy_limit(
    mock_get_settings: MagicMock,
    pii_service: PIIAnalyzerService,
) -> None:
    """Test smooth_text chunks text when exceeding limit."""
    mock_settings = MagicMock()
    mock_settings.pii_spacy_max_chunk_chars = 20
    mock_get_settings.return_value = mock_settings

    text = "Hello world! This is a test."

    mock_nlp = MagicMock()

    def nlp_side_effect(chunk):
        doc = MagicMock()
        sent = MagicMock()
        sent.text = chunk
        doc.sents = [sent]
        return doc

    mock_nlp.side_effect = nlp_side_effect

    with patch.object(pii_service, "_get_spacy_model", return_value=mock_nlp):
        res = pii_service.smooth_text(text, language="en")
        assert mock_nlp.call_count >= 2
        assert res.replace(" ", "") == text.replace(" ", "")
