import logging
import threading
from functools import lru_cache
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


class PIIAnalyzerService:
    """Lazy-loading service for Microsoft Presidio.
    This ensures that the heavy ~500MB en_core_web_lg SpaCy model is only loaded into RAM
    when actually requested during an evaluation path, avoiding boot-time overhead.
    """

    def __init__(self) -> None:
        self._analyzer: Any | None = None
        self._anonymizer: Any | None = None
        self._nlp_models: dict[str, Any] = {}
        self._lock = threading.Lock()

    def _ensure_initialized(self) -> None:
        """Initializes Presidio NLP and Anonymizer engines if not already loaded.

        Returns:
            None

        Raises:
            AppException: If the required SpaCy models cannot be found or loaded.
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
                    msg = "Presidio model 'en_core_web_lg' or 'fi_core_news_lg' not found. Please install the model via spacy download."
                    logger.error("[PIIAnalyzerService] %s: %s - Error: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, e)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                    ) from e

    def _get_spacy_model(self, language: str) -> Any:
        """Retrieves and lazily loads the SpaCy model for the specified language.

        Args:
            language: The target language code ('en' or 'fi').

        Returns:
            Any: The loaded SpaCy model instance.

        Raises:
            AppException: If the requested SpaCy model cannot be found.
        """
        if language in self._nlp_models:
            return self._nlp_models[language]

        with self._lock:
            if language not in self._nlp_models:
                import spacy

                logger.info("Loading SpaCy model for language '%s'...", language)
                model_name = "fi_core_news_lg" if language == "fi" else "en_core_web_lg"
                try:
                    self._nlp_models[language] = spacy.load(model_name)
                except OSError as e:
                    msg = f"SpaCy model '{model_name}' not found. Please install it."
                    logger.error("[PIIAnalyzerService] %s: %s - Error: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, e)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                    ) from e
            return self._nlp_models[language]

    def _chunk_text(self, text: str, max_chars: int) -> list[str]:
        """Splits a large string into smaller chunks safely to prevent NLP out-of-memory errors.

        Args:
            text: The raw text string to split.
            max_chars: The maximum length of each chunk.

        Returns:
            list[str]: The text divided into manageable chunks.
        """
        if len(text) <= max_chars:
            return [text]

        chunks = []
        start = 0
        text_len = len(text)
        margin = min(10000, max_chars // 2)

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
        """Runs raw text through SpaCy to merge hyphenations and broken PDF lines.

        Args:
            text: The raw text string to process.
            language: The target language code ('en' or 'fi').

        Returns:
            str: The smoothed, concatenated text string.

        Raises:
            AppException: If the underlying SpaCy model cannot be found or loaded.
        """
        if not text or not text.strip():
            return text

        import re

        nlp = self._get_spacy_model(language)
        settings = get_settings()

        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

        chunks = self._chunk_text(text, settings.pii_spacy_max_chunk_chars)
        smoothed_sentences = []

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
        """Analyzes and anonymizes PII in the given text (enforces explicit target language).

        Args:
            text: The raw text string containing potential PII.
            language: The target language code ('en' or 'fi').

        Returns:
            str: The anonymized text string with PII replaced by placeholders.

        Raises:
            AppException: If Presidio or the necessary SpaCy models cannot be initialized.
        """
        if not text or not text.strip():
            return text

        self._ensure_initialized()

        assert self._analyzer is not None
        assert self._anonymizer is not None

        settings = get_settings()
        chunks = self._chunk_text(text, settings.pii_spacy_max_chunk_chars)

        anonymized_chunks = []
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
        PIIAnalyzerService: A singleton instance of the service.
    """
    return PIIAnalyzerService()
