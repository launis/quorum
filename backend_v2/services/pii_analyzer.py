import logging
from functools import lru_cache
from typing import Any

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


class PIIAnalyzerService:
    """Lazy-loading service for Microsoft Presidio.
    This ensures that the heavy ~500MB en_core_web_lg SpaCy model is only loaded into RAM
    when actually requested during an evaluation path, avoiding boot-time overhead.
    """

    def __init__(self) -> None:
        self._analyzer: Any | None = None
        self._anonymizer: Any | None = None

    def _ensure_initialized(self) -> None:
        if self._analyzer is None or self._anonymizer is None:
            logger.info("Initializing Microsoft Presidio and loading SpaCy model into memory...")
            try:
                self._analyzer = AnalyzerEngine()
                self._anonymizer = AnonymizerEngine()  # type: ignore[no-untyped-call]
                logger.info("Presidio initialized successfully.")
            except OSError as e:
                msg = "Presidio model 'en_core_web_lg' not found. Please install the model via spacy download."
                logger.error("[PIIAnalyzerService] %s: %s - Error: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, e)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                ) from e

    def mask_pii(self, text: str, language: str) -> str:
        """Analyzes and anonymizes PII in the given text (enforces explicit target language)."""
        if not text or not text.strip():
            return text

        self._ensure_initialized()

        assert self._analyzer is not None
        assert self._anonymizer is not None

        # 1. Analyze
        results = self._analyzer.analyze(text=text, entities=[], language=language)

        # 2. Anonymize
        anonymized_result = self._anonymizer.anonymize(text=text, analyzer_results=results)
        return str(anonymized_result.text)


@lru_cache
def get_pii_service() -> PIIAnalyzerService:
    """FastAPI Dependency Provider for lazy-loaded PIIAnalyzerService."""
    return PIIAnalyzerService()
