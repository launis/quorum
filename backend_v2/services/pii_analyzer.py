"""Lazy-loading Microsoft Presidio and SpaCy NLP service for PII anonymization and text smoothing."""

from __future__ import annotations

import logging
import re
import threading
from functools import lru_cache
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import spacy.language

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

_MAX_CHUNK_SEARCH_MARGIN_CHARS = 10000

__all__ = [
    "PIIAnalyzerService",
    "get_pii_service",
]


class PIIAnalyzerService:
    """Lazy-loading service for Microsoft Presidio and SpaCy NLP processing.

    Ensures that the heavy ~500MB en_core_web_lg and fi_core_news_lg SpaCy models
    are only loaded into RAM when requested during an evaluation path, avoiding
    boot-time memory and latency overhead.
    """

    def __init__(self) -> None:
        """Initialize the lazy-loaded PII analyzer service state and synchronization lock."""
        self._analyzer: Any | None = None
        self._anonymizer: Any | None = None
        self._nlp_models: dict[str, spacy.language.Language] = {}
        self._lock = threading.Lock()

    def _resolve_spacy_model_name(self, language: str) -> str:
        """Resolve the canonical SpaCy model package name for a supported target language.

        Args:
            language: The target language code ('en' or 'fi').

        Returns:
            The canonical SpaCy model package identifier.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED (400) if the language is unsupported.
        """
        match language:
            case "en":
                return "en_core_web_lg"
            case "fi":
                return "fi_core_news_lg"
            case _:
                msg = f"Unsupported language '{language}' for PII analysis. Supported languages: 'en', 'fi'."
                logger.error(
                    "[PIIAnalyzerService] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                    exc_info=True,
                )
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

    def _ensure_initialized(self) -> None:
        """Initialize Presidio NLP and Anonymizer engines if not already loaded.

        Raises:
            AppException: With ErrorCodes.CONFIGURATION_ERROR (500) if the required SpaCy models
                cannot be found or loaded.
        """
        if self._analyzer is not None and self._anonymizer is not None:
            return

        with self._lock:
            if self._analyzer is None or self._anonymizer is None:
                logger.info("Initializing Microsoft Presidio and loading SpaCy model into memory...")
                try:
                    # Silence internal verbose Presidio loggers (e.g. "Loaded recognizer ...")
                    logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)
                    logging.getLogger("presidio_analyzer").setLevel(logging.ERROR)
                    logging.getLogger("presidio-anonymizer").setLevel(logging.ERROR)
                    logging.getLogger("presidio_anonymizer").setLevel(logging.ERROR)

                    from presidio_analyzer import AnalyzerEngine
                    from presidio_analyzer.nlp_engine import NlpEngineProvider
                    from presidio_anonymizer import AnonymizerEngine

                    configuration = {
                        "nlp_engine_name": "spacy",
                        "models": [
                            {"lang_code": "en", "model_name": "en_core_web_lg"},
                            {"lang_code": "fi", "model_name": "fi_core_news_lg"},
                        ],
                        "ner_model_configuration": {
                            "labels_to_ignore": [
                                "CARDINAL",
                                "MONEY",
                                "FAC",
                                "PRODUCT",
                                "WORK_OF_ART",
                                "LAW",
                                "PERCENT",
                                "QUANTITY",
                                "ORDINAL",
                                "LANGUAGE",
                                "EVENT",
                                "LOC",
                                "NORP",
                            ]
                        },
                    }
                    provider = NlpEngineProvider(nlp_configuration=configuration)
                    nlp_engine = provider.create_engine()

                    self._analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en", "fi"])
                    AnonymizerClass: Any = AnonymizerEngine
                    self._anonymizer = AnonymizerClass()
                    logger.info("Presidio initialized successfully.")
                except OSError as e:
                    msg = (
                        "Presidio model 'en_core_web_lg' or 'fi_core_news_lg' not found. "
                        "Please install the model via spacy download."
                    )
                    logger.error(
                        "[PIIAnalyzerService] %s: %s - Error: %s",
                        ErrorCodes.CONFIGURATION_ERROR.name,
                        msg,
                        e,
                        extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
                        exc_info=True,
                    )
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                    ) from e

    def _get_spacy_model(self, language: str) -> spacy.language.Language:
        """Retrieve and lazily load the SpaCy model for the specified language.

        Args:
            language: The target language code ('en' or 'fi').

        Returns:
            The loaded SpaCy language model instance.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED (400) if language is unsupported,
                or ErrorCodes.CONFIGURATION_ERROR (500) if the requested SpaCy model is not installed.
        """
        model_name = self._resolve_spacy_model_name(language)
        if language in self._nlp_models:
            return self._nlp_models[language]

        with self._lock:
            if language not in self._nlp_models:
                import spacy

                logger.info("Loading SpaCy model for language '%s'...", language)
                try:
                    self._nlp_models[language] = spacy.load(model_name)
                except OSError as e:
                    msg = f"SpaCy model '{model_name}' not found. Please install it."
                    logger.error(
                        "[PIIAnalyzerService] %s: %s - Error: %s",
                        ErrorCodes.CONFIGURATION_ERROR.name,
                        msg,
                        e,
                        extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
                        exc_info=True,
                    )
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                    ) from e
            return self._nlp_models[language]

    def _chunk_text(self, text: str, max_chars: int) -> list[str]:
        """Split a large string into smaller chunks safely to prevent NLP out-of-memory errors.

        Args:
            text: The raw text string to split.
            max_chars: The maximum character length of each chunk (must be > 0).

        Returns:
            The text divided into manageable chunks.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED (400) if max_chars is less than or equal to 0.
        """
        if max_chars <= 0:
            msg = f"Invalid max_chars={max_chars} for text chunking; must be a positive integer."
            logger.error(
                "[PIIAnalyzerService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        if len(text) <= max_chars:
            return [text]

        chunks: list[str] = []
        start = 0
        text_len = len(text)
        margin = min(_MAX_CHUNK_SEARCH_MARGIN_CHARS, max_chars // 2)

        while start < text_len:
            if text_len - start <= max_chars:
                chunks.append(text[start:])
                break

            end = start + max_chars
            search_window = text[end - margin : end]

            # Try splitting on the last newline within the margin
            split_idx = search_window.rfind("\n")
            if split_idx != -1:
                actual_end = end - margin + split_idx + 1
            else:
                # Try splitting on the last space
                split_idx = search_window.rfind(" ")
                if split_idx != -1:
                    actual_end = end - margin + split_idx + 1
                else:
                    # Hard fallback: split exactly at max_chars
                    actual_end = end

            chunks.append(text[start:actual_end])
            start = actual_end

        return chunks

    def smooth_text(self, text: str, language: str) -> str:
        """Run raw text through SpaCy to merge hyphenations and broken PDF lines.

        Args:
            text: The raw text string to process.
            language: The target language code ('en' or 'fi').

        Returns:
            The smoothed, concatenated text string.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED (400) if language is unsupported,
                or ErrorCodes.CONFIGURATION_ERROR (500) if the underlying SpaCy model cannot be loaded.
        """
        self._resolve_spacy_model_name(language)
        if not text or not text.strip():
            return text

        nlp = self._get_spacy_model(language)
        settings = get_settings()

        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

        chunks = self._chunk_text(text, settings.pii_spacy_max_chunk_chars)
        smoothed_sentences: list[str] = []

        for chunk in chunks:
            doc = nlp(chunk)
            for sent in doc.sents:
                sent_text = sent.text
                sent_text = re.sub(r"-\s*\n\s*", "", sent_text)
                sent_text = re.sub(r"\s*\n\s*", " ", sent_text)
                if sent_text.strip():
                    smoothed_sentences.append(sent_text.strip())

        return " ".join(smoothed_sentences)

    def mask_pii(self, text: str, language: str) -> str:
        """Analyze and anonymize PII in the given text for an explicit target language.

        Args:
            text: The raw text string containing potential PII.
            language: The target language code ('en' or 'fi').

        Returns:
            The anonymized text string with PII replaced by placeholders.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED (400) if language is unsupported,
                or ErrorCodes.CONFIGURATION_ERROR (500) if Presidio or SpaCy models fail to initialize.
        """
        self._resolve_spacy_model_name(language)
        if not text or not text.strip():
            return text

        self._ensure_initialized()

        assert self._analyzer is not None
        assert self._anonymizer is not None

        settings = get_settings()
        chunks = self._chunk_text(text, settings.pii_spacy_max_chunk_chars)

        anonymized_chunks: list[str] = []
        for chunk in chunks:
            # 1. Analyze
            results = self._analyzer.analyze(text=chunk, entities=[], language=language)

            # 2. Anonymize
            anonymized_result = self._anonymizer.anonymize(text=chunk, analyzer_results=results)
            anonymized_chunks.append(str(anonymized_result.text))

        return "".join(anonymized_chunks)


@lru_cache
def get_pii_service() -> PIIAnalyzerService:
    """FastAPI Dependency Provider for lazy-loaded PIIAnalyzerService.

    Returns:
        Singleton instance of PIIAnalyzerService.
    """
    return PIIAnalyzerService()
