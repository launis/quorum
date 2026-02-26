import logging
import os
from typing import Any

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field

try:
    import vertexai
    from vertexai.preview.generative_models import GenerationConfig, GenerativeModel, Tool

    VERTEX_AVAILABLE = True
    _IMPORT_ERROR = None
except ImportError as e:
    VERTEX_AVAILABLE = False
    _IMPORT_ERROR = e
    vertexai: Any = None  # type: ignore[no-redef]
    GenerativeModel: Any = None  # type: ignore[no-redef]
    Tool: Any = None  # type: ignore[no-redef]
    GenerationConfig: Any = None  # type: ignore[no-redef]


from backend.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    ServiceUnavailableError,
)
from backend.settings import get_settings

logger = logging.getLogger(__name__)


class SearchResultItem(BaseModel):
    """Immutable model for a single search result."""

    title: str = Field(..., description="Result title")
    link: str = Field(..., description="Result URL")
    snippet: str = Field(default="", description="Text snippet (optional for Grounding)")
    query: str = Field(..., description="Original query")

    model_config = ConfigDict(frozen=True, extra="ignore")


class VertexAISearchTool:
    """Facade for Vertex AI Grounding Search (Gemini 2.0).

    Strictly adheres to RFC 7807 Error Handling:
    - Raises ConfigurationError if dependencies/settings missing.
    - Raises ServiceUnavailableError if Vertex AI is down/throttled.
    - Raises AppException(SEARCH_EXECUTION_FAILED) for other failures.
    """

    def __init__(self, project_id: str | None = None, location: str | None = None, model_id: str | None = None):
        """Initialize Vertex AI Search Tool.

        Args:
            project_id: Google Cloud Project ID. Defaults to env 'GOOGLE_CLOUD_PROJECT'.
            location: Vertex AI Location. Defaults to env 'VERTEX_LOCATION' or 'europe-north1'.
            model_id: Vertex AI Model ID (Grounding capable). Defaults to settings.vertex_search_model.

        Raises:
            ConfigurationError: If vertexai is not installed, project_id is missing, or settings invalid.
        """
        if not VERTEX_AVAILABLE:
            error_code = ErrorCodes.SERVICE_DEPENDENCY_MISSING
            msg = f"Python package 'google-cloud-aiplatform' (vertexai) is not installed or failed to load: {_IMPORT_ERROR}"
            logger.error(f"[VertexAISearchTool] {error_code}: {msg}")
            raise ConfigurationError(
                message=msg,
                details={
                    "error_code": error_code,
                    "instruction": "pip install google-cloud-aiplatform",
                    "original_error": str(_IMPORT_ERROR),
                },
            )

        # 1. Feature Flag Check (Fail Fast - Skip Init)
        try:
            settings = get_settings()
            if not settings.enable_vertex_search:
                logger.info(
                    "[VertexAISearchTool] Feature disabled via 'enable_vertex_search=False'. Skipping initialization."
                )
                self._model = None
                return
        except Exception as e:
            # If settings fail to load, we can't check the flag.
            # We assume enabled (Strict) or Disabled?
            # Strict: Raise error.
            logger.critical(f"[VertexAISearchTool] Failed to load settings during init: {e}")
            raise ConfigurationError(f"Settings load failure: {e}") from e

        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            error_code = ErrorCodes.SEARCH_CONFIG_ERROR
            msg = "GOOGLE_CLOUD_PROJECT environment variable is missing."
            logger.critical(f"[VertexAISearchTool] {error_code}: {msg}")
            raise ConfigurationError(msg, details={"error_code": error_code})

        self.location = location or os.getenv("VERTEX_LOCATION", "europe-north1")
        # Critical Fix: Respect the model_id passed dynamically from DB search hook
        # before falling back to the hardcoded env variable (vertex_search_model)
        self.model_id = model_id or settings.vertex_search_model

        # Initialize Vertex AI SDK
        try:
            vertexai.init(project=self.project_id, location=self.location)

            # Initialize Tool
            self._tools = [Tool.from_dict({"google_search": {}})]

            # Initialize Model
            if not self.model_id:
                raise ConfigurationError(
                    "Vertex Search Model ID is not configured.", details={"error_code": ErrorCodes.SEARCH_CONFIG_ERROR}
                )

            self._model = GenerativeModel(self.model_id)

        except Exception as e:
            error_code = ErrorCodes.SEARCH_CONFIG_ERROR
            msg = f"Failed to initialize Vertex AI SDK: {e}"
            logger.error(f"[VertexAISearchTool] {error_code}: {msg}", exc_info=True)
            raise ConfigurationError(msg, details={"error_code": error_code, "original_error": str(e)}) from e

    def search(self, queries: list[str], limit: int = 3, language: str = "en") -> list[SearchResultItem]:
        """Execute search via Vertex AI Grounding.

        Args:
            queries: List of query strings.
            limit: Max queries to execute (per call).
            language: Language code (e.g. 'en', 'fi'). Hints to the model context.

        Returns:
            List[SearchResultItem]: Strictly typed list of unique results.

        Raises:
            ServiceUnavailableError: If quota exceeded or service down.
            AppException: If execution fails critically.
        """
        all_results: list[SearchResultItem] = []

        if not queries:
            logger.warning("[VertexAISearchTool] No queries provided. Returning empty list.")
            return []

        # Feature Flag Logic (Runtime Check)
        model = getattr(self, "_model", None)
        if model is None:
            logger.info("[VertexAISearchTool] Search skipped (Disabled or Not Initialized).")
            return []

        # Grounding loop
        for i, query in enumerate(queries[:limit]):
            logger.debug(f"[VertexAISearchTool] Processing query {i + 1}: {query}")

            import asyncio
            import time

            max_retries = 3
            base_delay = 2.0

            for attempt in range(max_retries):
                try:
                    # Construct Prompt
                    prompt_text = f"Search for the following topic and provide key findings with sources: '{query}'"
                    if language == "fi":
                        prompt_text = f"Etsi tietoa seuraavasta aiheesta ja listaa lähteet: '{query}'"

                    response = model.generate_content(
                        prompt_text,
                        tools=self._tools,
                        generation_config=GenerationConfig(
                            temperature=0.0  # Deterministic
                        ),
                    )

                    # Extract Grounding Metadata
                    if not response.candidates:
                        logger.warning(f"[VertexAISearchTool] No candidates returned for query: {query}")
                        break

                    candidate = response.candidates[0]

                    # Check for blocking (Safety)
                    if candidate.finish_reason != 0 and candidate.finish_reason != 1:  # STOP or MAX_TOKENS
                        logger.warning(f"[VertexAISearchTool] Query blocked. Finish Reason: {candidate.finish_reason}")
                        break

                    if not candidate.grounding_metadata:
                        logger.warning(f"[VertexAISearchTool] No grounding metadata for query: {query}")
                        break

                    metadata = candidate.grounding_metadata

                    # Extract Chunks (Web Sources)
                    if metadata.grounding_chunks:
                        for chunk in metadata.grounding_chunks:
                            if getattr(chunk, "web", None):
                                # Normalize
                                title = chunk.web.title or "Untitled Source"
                                uri = getattr(chunk.web, "uri", None)
                                
                                # Google Search UI sometimes returns directly in url
                                if not uri and hasattr(chunk.web, "url"):
                                    uri = chunk.web.url

                                if not uri:
                                    continue

                                item = SearchResultItem(
                                    title=title,
                                    link=uri,
                                    snippet=f"Source via Vertex AI: {query}...",  # Placeholder
                                    query=query,
                                )
                                all_results.append(item)
                    
                    # Success
                    break

                except Exception as e:
                    error_msg = str(e)
                    is_quota_error = "429" in error_msg or "Quota exceeded" in error_msg or "RESOURCE_EXHAUSTED" in error_msg
                    
                    if is_quota_error and attempt < max_retries - 1:
                        # Exponential backoff: 2s, 4s, 8s
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"[VertexAISearchTool] Vertex AI Quota Exceeded (429). Retrying query '{query}' in {delay}s (Attempt {attempt + 1}/{max_retries})."
                        )
                        time.sleep(delay)  # We are in sync context, but inside async runner it might block. Time.sleep is safe enough for hook wrap.
                        continue
                        
                    # If out of retries or other error
                    if is_quota_error:
                        error_code = ErrorCodes.SEARCH_QUOTA_EXCEEDED
                        raise ServiceUnavailableError(
                            message="Vertex AI Quota Exceeded after retries",
                            details={"error_code": error_code, "original_error": error_msg},
                        ) from e

                    error_code = ErrorCodes.SEARCH_EXECUTION_FAILED
                    logger.error(f"[VertexAISearchTool] {error_code}: Grounding failed for '{query}': {e}", exc_info=True)

                    # Fail Fast: Raise exception immediately on critical failure
                    raise AppException(
                        message=f"Vertex AI Grounding failed: {e}",
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        details={"error_code": error_code, "query": query},
                    ) from e

        # Deduplication Strategy
        unique_results = []
        seen_links = set()
        for res in all_results:
            if res.link not in seen_links:
                unique_results.append(res)
                seen_links.add(res.link)

        return unique_results
