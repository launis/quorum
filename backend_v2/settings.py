"""Application Settings Module (V2 Isolated)."""

import logging
import os
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import AliasChoices, BeforeValidator, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


def strip_whitespace(v: Any) -> Any:
    """Validator to strip whitespace from strings.

    Args:
        v: Input value.

    Returns:
        Stripped string if input is a string, otherwise unchanged value.
    """
    if isinstance(v, str):
        return v.strip()
    return v


type MyBool = Annotated[bool, BeforeValidator(strip_whitespace)]


class StorageBackend(StrEnum):
    """Enumeration for Storage Backends."""

    FIRESTORE = "FIRESTORE"
    LOCAL = "LOCAL"


class Settings(BaseSettings):
    """Application Settings managed by Pydantic.

    Reads from environment variables and .env file.

    Attributes:
        use_mock_llm: Flag to use the mock LLM service.
        use_vertex_llm: Flag to use Google Cloud Vertex AI.
        use_firebase_auth: Flag to enforce Firebase authentication.
        cors_origins: List of allowed origins for CORS headers.
        use_json_logging: Flag to output logs as structured JSON.
        google_api_key: Developer API key for Gemini.
        openai_api_key: API key for OpenAI engines.
        anthropic_api_key: API key for Anthropic engines.
        tavily_api_key: API key for search orchestration.
        vertex_location: Regional anchor for GCP resources.
        discovery_location: Target region for Model Discovery.
        default_model_strategy: Preferred routing blueprint.
        llm_default_timeout: Connection and execution timeouts.
        llm_retry_delay: Backoff pause between transient faults.
        llm_default_tpm: Maximum tokens allowed per minute.
        llm_default_rpm: Maximum requests allowed per minute.
        citation_integrity_threshold: Strictness cut-off for sources.
        scoring_security_cap: Cap on score under security flags.
        scoring_logical_cap: Cap on score under logic flags.
        scoring_performative_threshold: Threshold tracking real vs performative.
        scoring_security_penalty: Multiplier penalty for threats.
        scoring_post_hoc_penalty: Multiplier penalty for post-hoc reasoning.
        scoring_passivity_multiplier: Leniency penalty mapping.
        metrics_short_response_word_count: Target limit for brief inputs.
        metrics_automation_bias_ratio: Bias flag threshold.
        metrics_reflection_min_length: Minimum chars for analytical scans.
        metrics_mechanical_ratio: Target ratio signaling automation risk.
        max_precedent_scan_depth: Lookback limits for similar entries.
        max_precedent_return_count: Count bounds for retrieved precedents.
        redis_host: Target address of cache server.
        redis_port: Connection port of cache server.
        worker_job_timeout: Safety threshold for backend arq tasks.
        storage_backend: Target strategy ('LOCAL', 'FIRESTORE').
        environment: Platform stage ('production', 'staging', 'development').
        storage_bucket_name: Google Storage Cloud bucket handle.
        api_url: Fully qualified presenting address.
        log_file_name: Base file handle for disk storage of logs.
    """

    # --- Feature Flags ---
    use_mock_llm: Annotated[bool, BeforeValidator(strip_whitespace), Field(description="Use Mock LLM Service")] = False
    use_vertex_llm: Annotated[bool, BeforeValidator(strip_whitespace), Field(description="Use Vertex AI for LLM")] = (
        False
    )
    disable_vertex_cache: Annotated[
        bool, BeforeValidator(strip_whitespace), Field(description="Bypass Vertex Context Cache for pure runs")
    ] = False
    use_firebase_auth: Annotated[
        bool, BeforeValidator(strip_whitespace), Field(description="Use Firebase Auth (vs Mock)")
    ] = True
    cors_origins: Annotated[list[str], Field(description="Allowed CORS Origins")] = ["*"]

    # --- System Concurrency (Migrated from Enums) ---
    linker_max_atoms_per_window: Annotated[
        int, Field(description="Max atoms per LLM sliding window to prevent output truncation")
    ] = 20
    tda_linker_window_size: Annotated[int, Field(description="Sliding window size for TDA linker.")] = 4
    tda_linker_overlap: Annotated[int, Field(description="Overlap between sliding windows in TDA linker.")] = 2
    sensor_batch_size: Annotated[
        int, Field(description="Max atoms per Boolean evaluation batch to avoid rate limits")
    ] = 15
    max_extracted_atoms_per_document: Annotated[
        int, Field(description="Global limit on number of extracted atoms per document to prevent DB bloat")
    ] = 1000
    max_concurrent_workflows: Annotated[int, Field(description="Max parallel workflow chunks")] = 10
    max_concurrent_llm_steps: Annotated[int, Field(description="Max parallel LLM calls in dag_executor")] = 10
    llm_max_schema_retries: Annotated[int, Field(description="Max retries for schema validation failures")] = 2
    llm_max_logical_retries: Annotated[int, Field(description="Max retries for logical validation failures")] = 2
    llm_retry_multiplier: Annotated[int, Field(description="Exponential backoff multiplier")] = 2
    llm_retry_min_seconds: Annotated[int, Field(description="Minimum backoff delay in seconds")] = 2
    llm_retry_max_seconds: Annotated[int, Field(description="Maximum backoff delay in seconds")] = 60
    llm_retry_jitter_initial_seconds: Annotated[int, Field(description="Initial jitter delay in seconds")] = 2
    llm_retry_jitter_exp_base: Annotated[int, Field(description="Exponential base for jitter")] = 2
    llm_max_chunk_size: Annotated[int, Field(description="Max documents per schema extraction chunk")] = 8
    rag_preflight_chunk_size: Annotated[
        int, Field(description="Chunk size in characters for RAG preflight document extraction")
    ] = 12000
    llm_min_payload_length: Annotated[int, Field(description="Minimum chars for LLM payload before fail-fast")] = 10
    llm_default_timeout_seconds: Annotated[int, Field(description="Network timeout in seconds for LLM calls")] = 300
    rate_limit_cooldown_seconds: Annotated[int, Field(description="Cooldown time after rate limits hit")] = 10
    semaphore_low_rpm_threshold: Annotated[int, Field(description="Threshold for applying strict concurrency")] = 20
    semaphore_low_rpm_limit: Annotated[int, Field(description="Concurrency limit for low RPM environments")] = 2
    semaphore_max_concurrency: Annotated[int, Field(description="Max simultaneous active LLM connections")] = 10
    semaphore_rpm_divisor: Annotated[int, Field(description="Divisor applied to requested RPM constraint")] = 10
    max_safe_tokens: Annotated[int, Field(description="Maximum token shield limit per context window")] = 2000000
    schema_max_evaluations: Annotated[int, Field(description="Max boolean metrics evaluation per prompt")] = 7
    context_cache_lock_ttl_seconds: Annotated[int, Field(description="Time-to-live for Vertex caching lock")] = 300
    context_cache_passive_ttl_seconds: Annotated[int, Field(description="Lifespan of Vertex context cache")] = 3600
    context_cache_lock_poll_interval_ms: Annotated[int, Field(description="Polling interval for lock acquire")] = 500
    context_cache_lock_wait_limit_seconds: Annotated[int, Field(description="Max wait time for caching lock")] = 20
    context_cache_minimum_token_limit: Annotated[int, Field(description="Minimum tokens to trigger caching")] = 2048
    pacing_delay_vertex_seconds: Annotated[int, Field(description="Forced delay between Vertex AI requests")] = 12
    pacing_delay_openai_seconds: Annotated[int, Field(description="Forced delay between OpenAI requests")] = 1
    pacing_delay_mock_seconds: Annotated[int, Field(description="Forced delay between Mock responses")] = 0
    redis_connection_timeout_seconds: Annotated[int, Field(description="Timeout for Redis connection in seconds")] = 10
    content_cache_enabled: Annotated[int, Field(description="Toggle for internal system response caching")] = 0
    pii_spacy_max_chunk_chars: Annotated[
        int, Field(description="Max characters per SpaCy NLP chunk to prevent E088 OOM")
    ] = 800000

    @computed_field  # type: ignore[prop-decorator]
    @property
    def llm_max_retries(self) -> int:
        """Dynamic retries based on execution mode."""
        return 0 if (self.environment.lower() == "development" and self.dev_execution_mode == "fast") else 2

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ensemble_parallelism(self) -> int:
        """Dynamic parallel BoX calls based on execution mode."""
        return 1 if self.environment.lower() == "development" else 3

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ensemble_min_consensus(self) -> int:
        """Dynamic consensus votes based on execution mode."""
        return 1 if self.environment.lower() == "development" else 2

    # --- Logging ---
    use_json_logging: Annotated[
        bool, BeforeValidator(strip_whitespace), Field(description="Force structured JSON logging in any environment")
    ] = False

    # --- API Keys & External Limits ---
    google_api_key: Annotated[str | None, Field(description="Google AI Provider API Key")] = None
    openai_api_key: Annotated[str | None, Field(description="OpenAI API Key (Optional)")] = None
    anthropic_api_key: Annotated[str | None, Field(description="Anthropic API Key (Optional)")] = None
    tavily_api_key: Annotated[str | None, Field(description="Tavily AI Search API Key")] = None
    tavily_api_url: Annotated[str, Field(description="Tavily API URL")] = "https://api.tavily.com/search"
    tavily_timeout_seconds: Annotated[int, Field(description="Timeout for Tavily requests")] = 15
    tavily_max_results: Annotated[int, Field(description="Max search results to fetch")] = 5
    tavily_content_char_limit: Annotated[int, Field(description="Max content characters from search")] = 8000
    vertex_location: Annotated[str | None, Field(description="Google Cloud Region (e.g. europe-north1)")] = None
    discovery_location: Annotated[
        str | None, Field(description="Source Region for Model Discovery (e.g. us-west1)")
    ] = None

    # --- LLM Configuration ---
    default_model_strategy: Annotated[
        str | None, Field(description="Default LLM strategy key (Optional). If None, explicit strategy is required.")
    ] = None
    llm_default_timeout: Annotated[float, Field(description="LLM Timeout in seconds")] = 120.0
    llm_retry_delay: Annotated[float, Field(description="Delay between retries in seconds")] = 10.0

    # --- Rate Limits (Strict Mode) ---
    llm_default_tpm: Annotated[int | None, Field(description="Default Tokens Per Minute (None = Strict)")] = None
    llm_default_rpm: Annotated[int | None, Field(description="Default Requests Per Minute (None = Strict)")] = None

    # --- Integrity Thresholds (Integrity, Scoring, Linguistics) ---
    citation_integrity_threshold: Annotated[float, Field(description="Minimum integrity score (0.0-1.0)")] = 0.0
    pre_flight_fuzz_agglutinative: Annotated[
        float, Field(description="Fuzzy threshold for Finnish/Hungarian/Turkish")
    ] = 85.0
    pre_flight_fuzz_analytic: Annotated[float, Field(description="Fuzzy threshold for English/Swedish/German")] = 92.0
    pre_flight_fuzz_isolating: Annotated[float, Field(description="Fuzzy threshold for Chinese/Japanese")] = 98.0
    pre_flight_fuzz_default: Annotated[float, Field(description="Fallback threshold")] = 90.0

    # --- Epic 91.5 Global DTO Policies ---
    auto_resolve_policy: Annotated[str, Field(description="Policy for automatic resolution of execution nodes")] = (
        "strict"
    )
    minimum_completeness_threshold: Annotated[
        float,
        Field(
            default=0.8,
            description="The minimum percentage of items that must be completed to finalize an execution",
            ge=0.0,
            le=1.0,
        ),
    ] = 0.8

    # Scoring Hooks
    scoring_security_cap: Annotated[float, Field(description="Max score if Security Threat detected")] = 1.0
    scoring_logical_cap: Annotated[float, Field(description="Max score if Logical Fallacy detected")] = 2.0
    scoring_performative_threshold: Annotated[
        float, Field(description="Max authenticity score to be considered performative")
    ] = 2.0

    # --- Scoring Penalties (Zero-Compromise: Configurable) ---
    scoring_security_penalty: Annotated[
        float, Field(description="Penalty multiplier for Security Threats (0.0 to 1.0)")
    ] = 0.0
    scoring_post_hoc_penalty: Annotated[
        float, Field(description="Penalty multiplier for Post-Hoc Rationalization (0.0 to 1.0)")
    ] = 0.0

    scoring_passivity_multiplier: Annotated[
        float, Field(description="Penalty multiplier for Passivity/Low Quality")
    ] = 1.0

    # Behavioral Metrics (Heuristics)
    metrics_short_response_word_count: Annotated[int, Field(description="Max words to consider a response 'short'")] = 5
    metrics_automation_bias_ratio: Annotated[
        float, Field(description="Ratio of short responses to trigger Automation Bias")
    ] = 0.7
    metrics_reflection_min_length: Annotated[
        int, Field(description="Min chars in reflection to enable Say-Do analysis")
    ] = 50
    slop_phrase_warning_threshold: Annotated[
        int, Field(description="Minimum performative slop phrases to trigger a warning flag")
    ] = 3
    metrics_mechanical_ratio: Annotated[float, Field(description="Ratio of mechanical words to trigger Say-Do Gap")] = (
        0.5
    )

    # --- Retrieval / Precedents ---
    max_precedent_scan_depth: Annotated[int, Field(description="Max executions to scan for precedents")] = 3
    max_precedent_return_count: Annotated[int, Field(description="Max precedents to return")] = 2

    # --- Redis & Arq ---
    redis_host: Annotated[str, Field(description="Redis Host")] = "127.0.0.1"
    redis_port: Annotated[int, Field(description="Redis Port")] = 6379
    worker_job_timeout: Annotated[int, Field(description="Max seconds Arq worker processes a job")] = 14400

    @computed_field  # type: ignore[prop-decorator]
    @property
    def default_safety_settings(self) -> list[dict[str, str]]:
        """Returns standard safety settings (Auditing Mode: BLOCK_NONE).

        Returns:
            List of dictionaries defining non-blocking threshold rules.
        """
        return [
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
        ]

    # --- Storage ---
    storage_backend: Annotated[
        str | None, BeforeValidator(strip_whitespace), Field(description="LOCAL, NONE, or FIRESTORE")
    ] = None
    environment: Annotated[str, Field(description="development, staging, or production")] = "production"
    dev_execution_mode: Annotated[
        Literal["fast", "full", "none"], Field(description="Execution Mode: fast, full, or none")
    ] = "none"
    storage_bucket_name: Annotated[str | None, Field(description="Firebase Storage Bucket Name")] = None

    api_url: Annotated[str | None, Field(description="Public API Base URL")] = "http://localhost:8000"

    # --- Paths ---
    log_file_name: Annotated[str, Field(description="Name of the debug log file")] = "backend_debug.log"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def base_dir(self) -> str:
        """Returns the base directory of the backend application.

        Returns:
            The absolute path to the settings directory as a string.
        """
        return str(Path(__file__).resolve().parent)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def data_dir(self) -> str:
        """Returns the path to the persistent data directory.

        Returns:
            The resolved data folder directory path.
        """
        return str(Path(self.base_dir).parent / "data")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def files_dir(self) -> str:
        """Returns the path to the central files directory.

        Returns:
            The resolved system files storage path.
        """
        return str(Path(self.data_dir) / "files")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def docs_dir(self) -> str:
        """Returns the path to the static docs directory.

        Returns:
            The resolved reference documentation path.
        """
        return str(Path(self.base_dir).parent / "docs")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def db_dir(self) -> str:
        """Returns the path to the database directory.

        Returns:
            The resolved local database adapter path.
        """
        return str(Path(self.base_dir) / "database")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def scripts_dir(self) -> str:
        """Returns the path to the scripts directory.

        Returns:
            The resolved migration and seeding tools path.
        """
        return str(Path(self.base_dir).parent / "scripts")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def prod_db_path(self) -> str:
        """Returns the path to the production database file. Isolated to V2.

        Returns:
            Path pointing directly to the target SQLite or JSON schema dynamic file.
        """
        return str(Path(self.data_dir) / "db_v2.json")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def seed_data_path(self) -> str:
        """Returns the path to the seed data file. Isolated to V2.

        Returns:
            Target layout to locate pre-configured records.
        """
        return str(Path(self.base_dir) / "seed" / "seed_data.json")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def mock_responses_path(self) -> str:
        """Returns the path to the mock responses file.

        Returns:
            The static simulated model reply repository.
        """
        return str(Path(self.data_dir) / "mock_responses.json")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def log_file_path(self) -> str:
        """Absolute path to the log file in the project root.

        Returns:
            Destination path for system-level logging captures.
        """
        return str(Path(self.base_dir).parent / self.log_file_name)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def active_backend(self) -> StorageBackend:
        """Determines the active storage backend based on configuration.

        Priority 1: Explicit FIRESTORE backend.
        Default: Local storage.

        Returns:
            The verified active target backend strategy.

        Raises:
            AppException: If storage backend is explicitly requested but invalid.
        """
        if not self.storage_backend:
            return StorageBackend.LOCAL

        value = self.storage_backend.upper()
        if value == "FIRESTORE":
            return StorageBackend.FIRESTORE
        if value in ("LOCAL", "TINYDB"):
            return StorageBackend.LOCAL

        msg = f"CRITICAL: Invalid STORAGE_BACKEND '{self.storage_backend}'. Must be LOCAL or FIRESTORE."
        logger.error("[Settings] %s", msg, extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}, exc_info=True)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_cloud_storage(self) -> bool:
        """Returns True if active_backend is FIRESTORE.

        Returns:
            Boolean value signifying cloud integration state.
        """
        return self.active_backend == StorageBackend.FIRESTORE

    @computed_field  # type: ignore[prop-decorator]
    @property
    def model_strategies(self) -> dict[str, Any]:
        """Returns empty dict by default.

        Strategies MUST be loaded from 'system_config' table in database.

        Returns:
            A map of dynamically fetched LLM settings.
        """
        return {}

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    def model_post_init(self, __context: Any) -> None:
        """Validates settings after initialization.

        Args:
            __context: Lifecycle contexts from Pydantic.

        Raises:
            AppException: If critical credentials are missing when mock mode is inactive.
        """
        if not self.use_mock_llm:
            if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                root_dir = Path(self.base_dir).parent
                sa_path = root_dir / "service-account.json"
                if sa_path.exists():
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(sa_path)
                    logger.info("Settings: Auto-detected service-account.json at %s", str(sa_path))

            has_vertex = bool(
                os.getenv("VERTEX_PROJECT_ID")
                or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                or os.getenv("GOOGLE_CLOUD_PROJECT")
            )

            if not self.google_api_key and not has_vertex:
                msg = (
                    "CRITICAL: No LLM Credentials found (GOOGLE_API_KEY or VERTEX_PROJECT_ID/Credentials). "
                    "Cannot proceed in Production Mode. Ensure 'service-account.json' exists in root or set env vars."
                )
                logger.error(
                    "[Settings] %s", msg, extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}, exc_info=True
                )
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def enabled_providers(self) -> list[str]:
        """Returns list of enabled LLM providers based on configuration.

        Hardcoded source of truth for UI and Discovery.

        Returns:
            Identified and verified cloud/mock options list.
        """
        providers = []
        if self.google_api_key or (
            not self.use_mock_llm and (os.getenv("VERTEX_PROJECT_ID") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        ):
            providers.append("google")

        if self.openai_api_key:
            providers.append("openai")

        if self.anthropic_api_key:
            providers.append("anthropic")

        if self.use_mock_llm and "mock" not in providers:
            providers.append("mock")

        return providers

    # --- 12-Factor Development Overrides ---

    @computed_field  # type: ignore[prop-decorator]
    @property
    def log_format(self) -> str:
        """Determines if logs should be JSON (production) or readable (development)."""
        if self.use_json_logging:
            return "json"
        return "readable" if self.environment.lower() == "development" else "json"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def allow_mock_tokens(self) -> bool:
        """Strictly disallow mock tokens in production."""
        return self.environment.lower() == "development"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def max_tool_calls_per_step(self) -> int:
        """Limits external searches (Tavily) in dev to save API quota."""
        return 1 if (self.environment.lower() == "development" and self.dev_execution_mode == "fast") else 3

    @computed_field  # type: ignore[prop-decorator]
    @property
    def schema_max_chunk_records(self) -> int:
        """Maximum number of records (main + context) the LLM is expected to parse in a single chunk."""
        return self.llm_max_chunk_size + 5

    @computed_field  # type: ignore[prop-decorator]
    @property
    def matrix_sampling_limit(self) -> int:
        """Limits items processed in V2 Matrix Execution."""
        return 2 if (self.environment.lower() == "development" and self.dev_execution_mode == "fast") else 0

    @computed_field  # type: ignore[prop-decorator]
    @property
    def schema_max_localized_anchors(self) -> int:
        """Strict limits for LLM token stability (localized context blocks)."""
        return 2 if (self.environment.lower() == "development" and self.dev_execution_mode == "fast") else 15

    @computed_field  # type: ignore[prop-decorator]
    @property
    def schema_max_source_aliases(self) -> int:
        """Target limits for source document array (logically bound to quote limit, capped by chunk size)."""
        return min(self.schema_max_quotes_target, self.schema_max_chunk_records)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def schema_max_quotes_target(self) -> int:
        """Target limits for JSON response quote counts."""
        return 1 if (self.environment.lower() == "development" and self.dev_execution_mode == "fast") else 5

    @computed_field  # type: ignore[prop-decorator]
    @property
    def schema_max_quote_length(self) -> int:
        """Target limits for JSON response quote lengths."""
        return 50 if (self.environment.lower() == "development" and self.dev_execution_mode == "fast") else 150

    @computed_field  # type: ignore[prop-decorator]
    @property
    def strategy_aliases(self) -> dict[str, str]:
        """Neutral map for strategy rerouting in development."""
        if self.environment.lower() == "development" and self.dev_execution_mode == "fast":
            return {
                "strict_strategy": "fast",
                "evaluation_strategy": "fast",
                "test_strategy": "fast",
                "strict": "fast",
                "deep": "fast",
                "synthesis": "fast",
                "reasoning": "fast",
            }
        return {}

    # Epic 13 M3: Centralized Mock Token IDs for testing
    mock_admin_user_id: str = Field(
        default="usr_18a0d5f6151349a5", validation_alias=AliasChoices("mock_admin_user_id", "MOCK_ADMIN_USER_ID")
    )
    mock_root_user_id: str = Field(
        default="usr_a3fd6b3d77c748f4", validation_alias=AliasChoices("mock_root_user_id", "MOCK_ROOT_USER_ID")
    )
    mock_analyst_user_id: str = Field(
        default="usr_8a9234f9a0c242a1", validation_alias=AliasChoices("mock_analyst_user_id", "MOCK_ANALYST_USER_ID")
    )


@lru_cache
def get_settings() -> Settings:
    """Singleton getter for Settings.

    Returns:
        The cached system-wide environment variables instantiation.
    """
    return Settings()


def get_lexical_fuzz_threshold(locale: str | None = None) -> float:
    """Centralized helper for fetching the correct fuzzy threshold based on locale.

    Args:
        locale: Optional language code.

    Returns:
        The fuzzy matching threshold percentage as a float.
    """
    settings = get_settings()
    if not locale:
        return settings.pre_flight_fuzz_default

    match locale.lower():
        case "fi" | "hu" | "tr":
            return settings.pre_flight_fuzz_agglutinative
        case "en" | "sv" | "de" | "fr" | "es":
            return settings.pre_flight_fuzz_analytic
        case "zh" | "ja" | "ko":
            return settings.pre_flight_fuzz_isolating
        case _:
            return settings.pre_flight_fuzz_default
