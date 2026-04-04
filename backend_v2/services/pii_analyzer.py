import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

class PIIAnalyzerService:
    """
    Lazy-loading Singleton service for Microsoft Presidio.
    This ensures that the heavy ~500MB en_core_web_lg SpaCy model is only loaded into RAM 
    when actually requested during an evaluation path, avoiding boot-time overhead.
    """
    _instance: Optional["PIIAnalyzerService"] = None
    
    def __init__(self) -> None:
        self._analyzer: Any | None = None
        self._anonymizer: Any | None = None
        
    @classmethod
    def get_instance(cls) -> "PIIAnalyzerService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _ensure_initialized(self) -> None:
        if self._analyzer is None or self._anonymizer is None:
            logger.info("Initializing Microsoft Presidio and loading SpaCy model into memory...")
            from presidio_analyzer import AnalyzerEngine
            from presidio_anonymizer import AnonymizerEngine
            
            try:
                self._analyzer = AnalyzerEngine()
                self._anonymizer = AnonymizerEngine()  # type: ignore[no-untyped-call]
                logger.info("Presidio initialized successfully.")
            except OSError as e:
                # Generally happens if en_core_web_lg is missing.
                logger.error(f"Failed to initialize Presidio. Ensure 'python -m spacy download en_core_web_lg' is run. Error: {e}")
                raise RuntimeError("Presidio model 'en_core_web_lg' not found. Please install the model via spacy download.") from e

    def mask_pii(self, text: str, language: str = "en") -> str:
        """
        Analyzes and anonymizes PII in the given text.
        """
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
