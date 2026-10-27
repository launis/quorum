"""Application Settings Module (V2 Isolated)."""

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from fastapi import status
from pydantic import AliasChoices, BeforeValidator, Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.domain.system_config import SystemConfigModelRegistry
from backend_v2.models.dtos.system import SafetySettingDTO
from backend_v2.models.enums import StorageBackend as StorageBackend

logger = logging.getLogger(__name__)

__all__ = [
    "MyBool",
    "Settings",
    "StorageBackend",
    "get_lexical_fuzz_threshold",
    "get_settings",
    "strip_whitespace",
]


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
        vertex_location: Regional anchor for GCP resources.
        discovery_location: Target region for Model Discovery.
        default_model_strategy: Preferred routing blueprint.
        llm_default_timeout: Connection and execution timeouts.
        mcp_default_timeout_seconds: Default timeout in seconds for MCP tool executions.
        mcp_discovery_timeout_seconds: Network timeout in seconds for MCP tools/list discovery handshakes.
        mcp_max_response_chars: Maximum character budget for external MCP tool responses before truncation.
        mcp_allow_private_networks: Whether MCP endpoint URL validator permits loopback and private networks.
        mcp_presentation_max_chars: Maximum character budget for external findings rendered in SDUI and executive report presentation before sentence-boundary truncation.
        llm_retry_delay: Backoff pause between transient faults.
        llm_default_tpm: Maximum tokens allowed per minute.
        llm_default_rpm: Maximum requests allowed per minute.
        citation_integrity_threshold: Strictness cut-off for sources.
        scoring_security_cap: Cap on score under security flags.
        scoring_logical_cap: Cap on score under logic flags.
        scoring_performative_threshold: Threshold tracking real vs performative.
        metrics_short_response_word_count: Target limit for brief inputs.
        metrics_automation_bias_ratio: Bias flag threshold.
        metrics_reflection_min_length: Minimum chars for analytical scans.
        metrics_mechanical_ratio: Target ratio signaling automation risk.
        min_verifiable_text_length: Minimum text character length required to trigger source verification.
        max_precedent_scan_depth: Lookback limits for similar entries.
        max_precedent_return_count: Count bounds for retrieved precedents.
        redis_host: Target address of cache server.
        redis_port: Connection port of cache server.
        worker_job_timeout: Safety threshold for backend arq tasks.
        storage_backend: Target strategy ('LOCAL', 'FIRESTORE').
        environment: Platform stage ('development', 'production').
        storage_bucket_name: Google Storage Cloud bucket handle.
        api_url: Fully qualified presenting address.
        log_file_name: Base file handle for disk storage of logs.
        otel_enabled: Flag to enable OpenTelemetry and Logfire distributed tracing.
        logfire_token: Authentication token for Pydantic Logfire cloud service.
        otel_service_name: Logical service name emitted in OpenTelemetry resource attributes.
        otel_exporter_otlp_endpoint: OTLP collector endpoint for exporting trace spans.
        otel_tracing_sample_rate: Sampling ratio for OpenTelemetry traces (0.0 to 1.0).
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
    cors_origins: Annotated[list[str], Field(default_factory=lambda: ["*"], description="Allowed CORS Origins")]

    # --- OpenTelemetry & Observability ---
    otel_enabled: Annotated[
        bool,
        BeforeValidator(strip_whitespace),
        Field(
            default=False,
            validation_alias=AliasChoices("otel_enabled", "OTEL_ENABLED"),
            description="Flag to enable OpenTelemetry and Logfire distributed tracing",
        ),
    ] = False
    logfire_token: Annotated[
        str | None,
        BeforeValidator(strip_whitespace),
        Field(
            default=None,
            validation_alias=AliasChoices("logfire_token", "LOGFIRE_TOKEN"),
            description="Authentication token for Pydantic Logfire cloud service",
        ),
    ] = None
    otel_service_name: Annotated[
        str,
        BeforeValidator(strip_whitespace),
        Field(
            default="quorum-backend",
            validation_alias=AliasChoices("otel_service_name", "OTEL_SERVICE_NAME"),
            description="Logical service name emitted in OpenTelemetry resource attributes",
        ),
    ] = "quorum-backend"
    otel_exporter_otlp_endpoint: Annotated[
        str | None,
        BeforeValidator(strip_whitespace),
        Field(
            default=None,
            validation_alias=AliasChoices("otel_exporter_otlp_endpoint", "OTEL_EXPORTER_OTLP_ENDPOINT"),
            description="OTLP collector endpoint for exporting trace spans",
        ),
    ] = None
    otel_tracing_sample_rate: Annotated[
        float,
        Field(
            default=1.0,
            ge=0.0,
            le=1.0,
            validation_alias=AliasChoices("otel_tracing_sample_rate", "OTEL_TRACING_SAMPLE_RATE"),
            description="Sampling ratio for OpenTelemetry traces (0.0 to 1.0)",
        ),
    ] = 1.0

    # --- System Concurrency (Migrated from Enums) ---
    linker_max_atoms_per_window: Annotated[
        int, Field(description="Max atoms per LLM sliding window to prevent output truncation")
    ] = 20
    linker_max_global_root_axioms: Annotated[
        int,
        Field(
            ge=0,
            le=20,
            description="Max persistent deliverable root axioms injected into window headers",
        ),
    ] = 8
    linker_max_bridge_axioms: Annotated[
        int,
        Field(
            ge=0,
            le=10,
            description="Max persistent deliverable deductive bridge lemmas injected into window headers",
        ),
    ] = 4
    linker_max_root_axioms: Annotated[
        int,
        Field(
            ge=0,
            le=10,
            description="Max persistent deliverable root axioms injected into window headers",
        ),
    ] = 4
    linker_min_window_atoms_quota: Annotated[
        int,
        Field(
            ge=1,
            le=20,
            description="Minimum current window atom quota before root axiom injection",
        ),
    ] = 12
    tda_linker_window_size: Annotated[int, Field(description="Sliding window size for TDA linker.")] = 4
    tda_linker_overlap: Annotated[int, Field(description="Overlap between sliding windows in TDA linker.")] = 2
    sensor_batch_size: Annotated[
        int, Field(description="Max atoms per Boolean evaluation batch to avoid rate limits")
    ] = 15
    max_extracted_atoms_per_document: Annotated[
        int, Field(description="Global limit on number of extracted atoms per document to prevent DB bloat")
    ] = 1000
    max_concurrent_workflows: Annotated[int, Field(ge=1, description="Max parallel workflow chunks")] = 10
    max_concurrent_llm_steps: Annotated[
        int, Field(ge=1, description="Max parallel Phase 2 synthesis LLM tasks per synthesis job")
    ] = 3
    llm_max_schema_retries: Annotated[int, Field(description="Max retries for schema validation failures")] = 2
    llm_max_logical_retries: Annotated[int, Field(description="Max retries for logical validation failures")] = 2
    llm_max_transient_retries: Annotated[int, Field(description="Max retries for transient network errors")] = 3
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
    rag_preflight_excluded_keys: Annotated[
        list[str],
        Field(
            default_factory=lambda: ["document_date"],
            description="Dynamic input keys excluded from RAG preflight character counting and LLM atomization",
        ),
    ]
    rag_preflight_min_input_chars: Annotated[
        int,
        Field(
            description=(
                "Minimum total character length across analytical dynamic inputs required for RAG preflight extraction."
            )
        ),
    ] = 100
    llm_default_timeout_seconds: Annotated[int, Field(description="Network timeout in seconds for LLM calls")] = 300
    # --- Protocol-Agnostic MCP Execution, Discovery, and SSRF Configuration ---
    mcp_default_timeout_seconds: Annotated[
        int, Field(default=30, ge=1, le=300, description="Default timeout in seconds for MCP tool executions")
    ] = 30
    mcp_discovery_timeout_seconds: Annotated[
        int,
        Field(
            default=10,
            ge=1,
            le=60,
            description="Network timeout in seconds for MCP tools/list discovery handshakes",
        ),
    ] = 10
    mcp_max_response_chars: Annotated[
        int,
        Field(
            default=8000,
            ge=500,
            le=50000,
            description="Maximum character budget for external MCP tool responses before sentence-boundary truncation",
        ),
    ] = 8000
    mcp_allow_private_networks: Annotated[
        bool,
        BeforeValidator(strip_whitespace),
        Field(
            default=False,
            description="Whether MCP endpoint URL validator permits loopback and private RFC-1918 networks",
        ),
    ] = False
    mcp_presentation_max_chars: Annotated[
        int,
        Field(
            default=300,
            ge=100,
            le=2000,
            description="Maximum character budget for external findings rendered in SDUI and executive report presentation before sentence-boundary truncation",
        ),
    ] = 300
    rate_limit_cooldown_seconds: Annotated[int, Field(description="Cooldown time after rate limits hit")] = 10
    semaphore_low_rpm_threshold: Annotated[int, Field(description="Threshold for applying strict concurrency")] = 20
    semaphore_low_rpm_limit: Annotated[int, Field(ge=1, description="Concurrency limit for low RPM environments")] = 2
    semaphore_max_concurrency: Annotated[int, Field(ge=1, description="Max simultaneous active LLM connections")] = 10
    semaphore_rpm_divisor: Annotated[int, Field(ge=1, description="Divisor applied to requested RPM constraint")] = 10
    max_safe_tokens: Annotated[int, Field(description="Maximum token shield limit per context window")] = 2000000
    schema_max_evaluations: Annotated[int, Field(description="Max boolean metrics evaluation per prompt")] = 7
    max_synthesis_evaluations: Annotated[int, Field(ge=0, description="Max evaluations for synthesis token shield")] = (
        40
    )
    max_synthesis_quote_length: Annotated[
        int, Field(description="Maximum character length for evidence quotes in synthesis payloads")
    ] = 300
    max_synthesis_quotes_per_matrix: Annotated[
        int, Field(description="Maximum number of evidence quotes per matrix in synthesis explanation context")
    ] = 5
    max_synthesis_unmet_criteria_per_matrix: Annotated[
        int,
        Field(description="Maximum number of unmet criteria descriptions per matrix in synthesis explanation context"),
    ] = 5
    max_synthesis_reasoning_length: Annotated[
        int, Field(description="Maximum character length for semantic reasoning in synthesis payloads")
    ] = 300
    synthesis_starvation_threshold: Annotated[
        int,
        Field(
            description=(
                "Atom count threshold at or below which synthesis unconditionally "
                "short-circuits with a DataStarvationEvent."
            )
        ),
    ] = 0
    synthesis_sparse_threshold: Annotated[
        int, Field(description="Atom count threshold below which sparse data gating and mandates are applied.")
    ] = 8
    context_cache_lock_ttl_seconds: Annotated[int, Field(description="Time-to-live for Vertex caching lock")] = 300
    context_cache_passive_ttl_seconds: Annotated[int, Field(description="Lifespan of Vertex context cache")] = 3600
    context_cache_lock_poll_interval_ms: Annotated[int, Field(description="Polling interval for lock acquire")] = 500
    context_cache_lock_wait_limit_seconds: Annotated[int, Field(description="Max wait time for caching lock")] = 20
    context_cache_min_tokens_vertex: Annotated[
        int,
        Field(
            ge=1024,
            le=1000000,
            description="Minimum non-system content tokens required by Vertex AI Context Caching",
        ),
    ] = 1024
    context_cache_min_tokens_ai_studio: Annotated[
        int,
        Field(
            ge=1024,
            le=1000000,
            description="Minimum non-system content tokens required by Google AI Studio Context Caching",
        ),
    ] = 32768
    context_cache_failed_ttl_seconds: Annotated[
        int,
        Field(
            ge=1,
            le=86400,
            description="TTL in seconds for marking context cache state as FAILED in Redis",
        ),
    ] = 300
    pacing_delay_vertex_seconds: Annotated[int, Field(description="Forced delay between Vertex AI requests")] = 4
    pacing_delay_ai_studio_seconds: Annotated[
        int, Field(description="Forced delay between Google AI Studio requests")
    ] = 0
    pacing_delay_openai_seconds: Annotated[int, Field(description="Forced delay between OpenAI requests")] = 1
    pacing_delay_mock_seconds: Annotated[int, Field(description="Forced delay between Mock responses")] = 0
    redis_connection_timeout_seconds: Annotated[int, Field(description="Timeout for Redis connection in seconds")] = 10
    db_lock_poll_interval_seconds: Annotated[
        float, Field(description="Polling interval in seconds for database file lock acquisition")
    ] = 0.02
    db_lock_timeout_seconds: Annotated[
        float, Field(description="Timeout in seconds for database file lock acquisition")
    ] = 15.0
    db_lock_stale_threshold_seconds: Annotated[
        float, Field(description="Threshold in seconds after which lock directory is considered stale")
    ] = 10.0
    content_cache_enabled: Annotated[int, Field(description="Toggle for internal system response caching")] = 0
    pii_spacy_max_chunk_chars: Annotated[
        int, Field(description="Max characters per SpaCy NLP chunk to prevent E088 OOM")
    ] = 800000

    max_tool_calls_per_step: Annotated[int, Field(description="Limits external searches")] = 3
    max_development_chunks: Annotated[int, Field(description="Limits chunks in dev")] = 0
    matrix_sampling_limit: Annotated[int, Field(description="Limits V2 Matrix items")] = 0
    tda_concept_min_length: Annotated[
        int, Field(description="Minimum character length for TDA assertion concept descriptions.")
    ] = 10
    min_verifiable_text_length: Annotated[
        int, Field(description="Minimum text character length required to trigger source verification.")
    ] = 15
    source_extraction_max_chars: Annotated[
        int, Field(description="Maximum character budget for input text truncation in source claim extraction.")
    ] = 30000
    source_evidence_max_chars: Annotated[
        int,
        Field(
            description="Maximum character budget for evidence XML injected into prompts to prevent token explosion."
        ),
    ] = 8000
    source_verification_min_text_length: Annotated[
        int,
        Field(
            description=(
                "Minimum character length of input text required to run source verification; "
                "payloads below this threshold short-circuit to prevent ghost executions."
            )
        ),
    ] = 15
    schema_max_localized_anchors: Annotated[int, Field(description="Max localized anchors")] = 15
    schema_max_quotes_target: Annotated[int, Field(description="Target quotes count")] = 5
    schema_max_quote_length: Annotated[int, Field(description="Target quote length")] = 150
    default_synthesis_length_constraint: Annotated[
        int, Field(description="Default character length constraint for Executive Summary.")
    ] = 1000
    default_row_explanation_length_constraint: Annotated[
        int, Field(description="Default character length constraint for Matrix Summary Table rows.")
    ] = 250
    default_xai_length_constraint: Annotated[
        int, Field(description="Default character length constraint for XAI Highlight items.")
    ] = 300
    default_variance_length_constraint: Annotated[
        int, Field(description="Default character length constraint for Variance Validation.")
    ] = 500
    default_matrix_graph_length_constraint: Annotated[
        int, Field(description="Default character length constraint for each Matrix Graph synthesis.")
    ] = 400

    llm_max_retries: Annotated[int, Field(description="Dynamic retries based on execution mode")] = 2
    ensemble_parallelism: Annotated[int, Field(description="Dynamic parallel BoX calls based on execution mode")] = 3
    ensemble_min_consensus: Annotated[int, Field(description="Dynamic consensus votes based on execution mode")] = 2

    # --- Causal Discovery & Dynamic DAG Settings ---
    causal_discovery_window_size: Annotated[
        int, Field(default=4, description="Sliding window size for causal argument linking")
    ] = 4
    causal_discovery_overlap: Annotated[
        int, Field(default=2, description="Overlap size for sliding window linking")
    ] = 2
    causal_discovery_max_atoms_per_window: Annotated[
        int, Field(default=25, description="Safety ceiling on claims extracted per window")
    ] = 25
    causal_discovery_max_total_atoms: Annotated[
        int, Field(default=100, description="Safety ceiling on total claims extracted for a document")
    ] = 100
    causal_secondary_fault_dampening: Annotated[
        float, Field(default=0.25, description="Penalty dampening factor for cascading secondary faults")
    ] = 0.25
    causal_cohesion_matrix_block_id: Annotated[
        str, Field(default="blk_c0a1e50000000001", description="Default PromptBlock ID for causal cohesion BARS matrix")
    ] = "blk_c0a1e50000000001"
    causal_cohesion_l2_threshold: Annotated[
        float, Field(default=0.40, description="Minimum logical cohesion score for Level 2 BARS threshold")
    ] = 0.40
    causal_cohesion_l3_threshold: Annotated[
        float, Field(default=0.60, description="Minimum logical cohesion score for Level 3 BARS threshold")
    ] = 0.60
    causal_cohesion_l4_threshold: Annotated[
        float, Field(default=0.80, description="Minimum logical cohesion score for Level 4 BARS threshold")
    ] = 0.80
    causal_cohesion_l5_threshold: Annotated[
        float, Field(default=0.90, description="Minimum logical cohesion score for Level 5 BARS threshold")
    ] = 0.90
    causal_cohesion_l3_isolation_max: Annotated[
        float,
        Field(
            default=0.20,
            description=(
                "Maximum isolated concept ratio for Level 3 BARS threshold (baseline SSOT: 0.20; "
                "exploratory calibrated profile: 0.30 for strategic scoping axioms)"
            ),
        ),
    ] = 0.20
    causal_cohesion_l4_isolation_max: Annotated[
        float, Field(default=0.10, description="Maximum isolated concept ratio for Level 4 BARS threshold")
    ] = 0.10
    causal_cohesion_l5_isolation_max: Annotated[
        float, Field(default=0.05, description="Maximum isolated concept ratio for Level 5 BARS threshold")
    ] = 0.05
    two_pass_atomizer_packet_size: Annotated[
        int, Field(default=50, description="Default block count per chunk packet in two-pass atomizer")
    ] = 50

    # --- Logging ---
    use_json_logging: Annotated[
        bool, BeforeValidator(strip_whitespace), Field(description="Force structured JSON logging in any environment")
    ] = False

    # --- API Keys & External Limits ---
    google_api_key: Annotated[
        str | None,
        Field(
            validation_alias=AliasChoices("google_api_key", "gemini_api_key"),
            description="Google AI Provider API Key",
        ),
    ] = None
    openai_api_key: Annotated[str | None, Field(description="OpenAI API Key (Optional)")] = None
    anthropic_api_key: Annotated[str | None, Field(description="Anthropic API Key (Optional)")] = None
    vertex_location: Annotated[str | None, Field(description="Google Cloud Region (e.g. europe-north1)")] = None
    discovery_location: Annotated[str, Field(description="Source Region for Model Discovery (e.g. us-central1)")] = (
        "us-central1"
    )

    # --- LLM Configuration ---

    default_model_strategy: Annotated[
        str | None, Field(description="Default LLM strategy key (Optional). If None, explicit strategy is required.")
    ] = None
    model_registry: Annotated[
        SystemConfigModelRegistry | None,
        Field(default=None, description="System Config Model Registry snapshot (Optional)."),
    ] = None
    llm_default_timeout: Annotated[
        float,
        Field(
            default=120.0,
            gt=0.0,
            le=3600.0,
            description="Network timeout in seconds for LLM calls",
        ),
    ] = 120.0
    llm_retry_delay: Annotated[float, Field(description="Delay between retries in seconds")] = 10.0
    sse_max_transient_retries: Annotated[
        int,
        Field(default=3, ge=1, le=10, description="Maximum transient retry count for SSE polling"),
    ] = 3
    sse_polling_interval_seconds: Annotated[
        float,
        Field(default=2.0, gt=0.0, le=30.0, description="Polling interval in seconds for SSE execution status stream"),
    ] = 2.0

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

    authenticity_threshold_high: Annotated[
        float,
        Field(
            default=2.5,
            ge=0.0,
            le=3.0,
            description="Minimum score required for HIGH authenticity level classification on 1.0-3.0 scale",
        ),
    ] = 2.5

    authenticity_threshold_low: Annotated[
        float,
        Field(
            default=1.5,
            ge=0.0,
            le=3.0,
            description="Minimum score required for MEDIUM authenticity level classification on 1.0-3.0 scale",
        ),
    ] = 1.5

    # --- Global DTO Policies ---
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

    # Mechanical-Cognitive Variance Validation Settings
    variance_threshold_misaligned: Annotated[
        float, Field(default=0.5, description="Variance threshold above which scores are considered misaligned")
    ] = 0.5
    variance_max_performative_cap: Annotated[
        float, Field(default=2.0, description="Maximum performative penalty cap on dampening scale")
    ] = 2.0
    variance_performative_normalizer: Annotated[
        float, Field(default=10.0, description="Performative phrase count scaling normalizer")
    ] = 10.0
    variance_jargon_density_normalizer: Annotated[
        float, Field(default=5.0, description="Phrases per 100 words normalizer for performative load cap")
    ] = 5.0
    enable_dynamic_performative_extraction: Annotated[
        bool, Field(default=True, description="Feature flag to enable dynamic LLM extraction of performative patterns")
    ] = True

    # Behavioral Metrics (Heuristics)
    metrics_short_response_word_count: Annotated[int, Field(description="Max words to consider a response 'short'")] = 5
    metrics_automation_bias_ratio: Annotated[
        float, Field(description="Ratio of short responses to trigger Automation Bias")
    ] = 0.7
    metrics_reflection_min_length: Annotated[
        int, Field(description="Min chars in reflection to enable Say-Do analysis")
    ] = 50
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

    @computed_field
    @property
    def default_safety_settings(self) -> list[SafetySettingDTO]:
        """Returns standard safety settings (Auditing Mode: BLOCK_NONE).

        Returns:
            List of SafetySettingDTO defining non-blocking threshold rules.
        """
        return [
            SafetySettingDTO(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_ONLY_HIGH",
            ),
            SafetySettingDTO(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_ONLY_HIGH",
            ),
            SafetySettingDTO(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_ONLY_HIGH",
            ),
            SafetySettingDTO(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_ONLY_HIGH",
            ),
        ]

    # --- Storage ---
    storage_backend: Annotated[
        str | None, BeforeValidator(strip_whitespace), Field(description="Sovereign storage backend (POSTGRES)")
    ] = "POSTGRES"
    # Environment-injected PostgreSQL 19 connection, pool, timeout, and TOAST settings
    postgres_host: Annotated[str, Field(description="PostgreSQL server host address.")] = "127.0.0.1"
    postgres_port: Annotated[int, Field(ge=1, le=65535, description="PostgreSQL server port.")] = 5432
    postgres_user: Annotated[str, Field(min_length=1, description="PostgreSQL role username.")] = "quorum"
    postgres_password: Annotated[
        str | None, Field(description="PostgreSQL role password injected from environment.")
    ] = None
    postgres_db: Annotated[str, Field(min_length=1, description="PostgreSQL database name.")] = "quorum"
    postgres_dsn: Annotated[str | None, Field(description="Optional environment-injected PostgreSQL DSN override.")] = (
        None
    )
    postgres_min_pool_size: Annotated[int, Field(ge=1, le=50, description="Minimum asyncpg pool connections.")] = 2
    postgres_max_pool_size: Annotated[int, Field(ge=2, le=200, description="Maximum asyncpg pool connections.")] = 20
    postgres_command_timeout_seconds: Annotated[
        float, Field(description="Command timeout in seconds for PostgreSQL queries.")
    ] = 15.0
    postgres_toast_compression: Annotated[
        str, Field(description="PostgreSQL TOAST compression algorithm (lz4 default).")
    ] = "lz4"
    environment: Annotated[
        Literal["development", "production"],
        Field(description="Runtime environment: 'development' (all fast) or 'production' (all thorough/accurate)"),
    ] = "production"
    dev_max_thinking_budget: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            description=(
                "Maximum thinking token budget applied in development environment. "
                "0 enforces zero-budget / lowest reasoning effort."
            ),
        ),
    ] = 0
    storage_bucket_name: Annotated[str | None, Field(description="Firebase Storage Bucket Name")] = None

    api_url: Annotated[str | None, Field(description="Public API Base URL")] = "http://localhost:8000"

    # --- Paths ---
    log_file_name: Annotated[str, Field(description="Name of the debug log file")] = "backend_debug.log"

    @computed_field
    @property
    def base_dir(self) -> str:
        """Returns the base directory of the backend application.

        Returns:
            The absolute path to the settings directory as a string.
        """
        return str(Path(__file__).resolve().parent)

    @computed_field
    @property
    def data_dir(self) -> str:
        """Returns the path to the persistent data directory.

        Returns:
            The resolved data folder directory path.
        """
        return str(Path(self.base_dir).parent / "data")

    @computed_field
    @property
    def files_dir(self) -> str:
        """Returns the path to the central files directory.

        Returns:
            The resolved system files storage path.
        """
        return str(Path(self.data_dir) / "files")

    @computed_field
    @property
    def docs_dir(self) -> str:
        """Returns the path to the static docs directory.

        Returns:
            The resolved reference documentation path.
        """
        return str(Path(self.base_dir).parent / "docs")

    @computed_field
    @property
    def db_dir(self) -> str:
        """Returns the path to the database directory.

        Returns:
            The resolved local database adapter path.
        """
        return str(Path(self.base_dir) / "database")

    @computed_field
    @property
    def scripts_dir(self) -> str:
        """Returns the path to the scripts directory.

        Returns:
            The resolved migration and seeding tools path.
        """
        return str(Path(self.base_dir).parent / "scripts")

    @computed_field
    @property
    def prod_db_path(self) -> str:
        """Returns the path to the production database marker file. Isolated to V2.

        Returns:
            Path pointing directly to the target PostgreSQL schema marker file.
        """
        return str(Path(self.data_dir) / "postgres_v2.db")

    @computed_field
    @property
    def seed_data_path(self) -> str:
        """Returns the path to the seed data file. Isolated to V2.

        Returns:
            Target layout to locate pre-configured records.
        """
        return str(Path(self.base_dir) / "seed" / "seed_data.json")

    @computed_field
    @property
    def mock_responses_path(self) -> str:
        """Returns the path to the mock responses file.

        Returns:
            The static simulated model reply repository.
        """
        return str(Path(self.data_dir) / "mock_responses.json")

    @computed_field
    @property
    def log_file_path(self) -> str:
        """Absolute path to the log file in the project root.

        Returns:
            Destination path for system-level logging captures.
        """
        return str(Path(self.base_dir).parent / self.log_file_name)

    @computed_field
    @property
    def active_backend(self) -> StorageBackend:
        """Determines the active storage backend based on configuration.

        PostgreSQL 19 (StorageBackend.POSTGRES) is the sole supported persistence backend.

        Returns:
            StorageBackend.POSTGRES when configured for PostgreSQL.

        Raises:
            ConfigurationError: If storage backend is LOCAL, TINYDB, FIRESTORE, or invalid.
        """
        if not self.storage_backend:
            return StorageBackend.POSTGRES

        value = self.storage_backend.upper()
        if value in ("POSTGRES", "POSTGRESQL"):
            return StorageBackend.POSTGRES

        msg = (
            f"CRITICAL: Unsupported STORAGE_BACKEND '{self.storage_backend}'. "
            "Only POSTGRES (PostgreSQL 19) is supported."
        )
        logger.error("[Settings] %s", msg, extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}, exc_info=True)
        raise ConfigurationError(
            message=msg,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    @computed_field
    @property
    def is_cloud_storage(self) -> bool:
        """Returns True if cloud bucket storage is configured.

        Returns:
            Boolean value signifying cloud integration state.
        """
        return bool(self.storage_bucket_name)

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    def model_post_init(self, __context: Any) -> None:
        """Validates settings after initialization.

        Args:
            __context: Lifecycle contexts from Pydantic.

        Raises:
            AppException: CONFIGURATION_ERROR if critical credentials are missing when mock mode is inactive.
        """
        if not self.use_mock_llm:
            if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                root_dir = Path(self.base_dir).parent
                sa_path = root_dir / "service-account.json"
                if sa_path.exists():
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(sa_path)
                    logger.info("Settings: Auto-detected service-account.json at %s", str(sa_path))

            has_vertex = any(
                bool(os.getenv(k))
                for k in ("VERTEX_PROJECT_ID", "GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT")
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
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

    @model_validator(mode="after")
    def _enforce_environment_limits(self) -> Self:
        """Enforce strict binary environment limits.

        When environment is 'development', enforce all 8 fast dimensions:
        immediate fail-fast logical/schema retries (0), single-pass ensemble (1), matrix sampling limit (1),
        zero pacing delays, minimal development chunks, preflight chunking, zero precedent/web scans,
        compact linker windows, and fast strategy aliases.
        External network and upstream gateway transient errors retain sovereign retry resilience (3).
        When environment is 'production', sovereign production defaults are preserved.

        Returns:
            The settings instance with environment invariants enforced.
        """
        if self.environment == "development":
            logger.info("⚡ Development environment active: Clamping LLM bounds and limits to fast profile.")

            self.max_tool_calls_per_step = 1
            self.max_development_chunks = 1
            if "matrix_sampling_limit" not in self.model_fields_set:
                self.matrix_sampling_limit = 1
            if "rag_preflight_chunk_size" not in self.model_fields_set:
                self.rag_preflight_chunk_size = 4000
            self.schema_max_localized_anchors = 2
            self.schema_max_quotes_target = 1
            self.schema_max_quote_length = 50
            self.schema_max_evaluations = 1
            if "max_precedent_scan_depth" not in self.model_fields_set:
                self.max_precedent_scan_depth = 0
            if "max_precedent_return_count" not in self.model_fields_set:
                self.max_precedent_return_count = 0
            if "tda_linker_window_size" not in self.model_fields_set:
                self.tda_linker_window_size = 2
            if "tda_linker_overlap" not in self.model_fields_set:
                self.tda_linker_overlap = 0

            # Zero Pacing Delays (Strictly typed as int)
            if "pacing_delay_vertex_seconds" not in self.model_fields_set:
                self.pacing_delay_vertex_seconds = 0
            if "pacing_delay_ai_studio_seconds" not in self.model_fields_set:
                self.pacing_delay_ai_studio_seconds = 0
            if "pacing_delay_openai_seconds" not in self.model_fields_set:
                self.pacing_delay_openai_seconds = 0
            if "pacing_delay_mock_seconds" not in self.model_fields_set:
                self.pacing_delay_mock_seconds = 0

            # Ensembles and Retries Overrides (Fail-Fast: 0 retries in development for schema/logical iterations)
            # Retain sovereign transient retries (default 3) for network and gateway errors
            if "llm_max_retries" not in self.model_fields_set:
                self.llm_max_retries = 0
            if "llm_max_schema_retries" not in self.model_fields_set:
                self.llm_max_schema_retries = 0
            if "llm_max_logical_retries" not in self.model_fields_set:
                self.llm_max_logical_retries = 0
            if "ensemble_parallelism" not in self.model_fields_set:
                self.ensemble_parallelism = 1
            if "ensemble_min_consensus" not in self.model_fields_set:
                self.ensemble_min_consensus = 1
            if "dev_max_thinking_budget" not in self.model_fields_set:
                self.dev_max_thinking_budget = 0

        return self

    @model_validator(mode="after")
    def validate_authenticity_thresholds(self) -> Self:
        """Enforce cross-field consistency: high threshold must be >= low threshold on 1.0-3.0 scale.

        Returns:
            The validated settings instance.

        Raises:
            ValueError: If authenticity_threshold_high is lower than authenticity_threshold_low.
        """
        if self.authenticity_threshold_high < self.authenticity_threshold_low:
            msg = (
                f"authenticity_threshold_high ({self.authenticity_threshold_high}) "
                f"must be >= authenticity_threshold_low ({self.authenticity_threshold_low}) on 1.0-3.0 scale"
            )
            raise ValueError(msg)
        return self

    @computed_field
    @property
    def enabled_providers(self) -> list[str]:
        """Returns list of enabled LLM providers based on configuration.

        Hardcoded source of truth for UI and Discovery.

        Returns:
            Identified and verified cloud/mock options list.
        """
        providers = []
        if not self.use_mock_llm and (
            os.getenv("VERTEX_PROJECT_ID")
            or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            or Path("service-account.json").exists()
        ):
            providers.append("vertex_ai")

        if self.google_api_key:
            providers.append("ai_studio")

        if self.openai_api_key:
            providers.append("openai")

        if self.anthropic_api_key:
            providers.append("anthropic")

        if self.use_mock_llm and "mock" not in providers:
            providers.append("mock")

        return providers

    # --- 12-Factor Development Overrides ---

    @computed_field
    @property
    def log_format(self) -> str:
        """Determines if logs should be JSON (production) or readable (development).

        Returns:
            String indicating log format ('json' or 'readable').
        """
        if self.use_json_logging:
            return "json"
        return "readable" if self.environment.lower() == "development" else "json"

    @computed_field
    @property
    def allow_mock_tokens(self) -> bool:
        """Strictly disallow mock tokens in cloud environments or active Firebase Auth production.

        Allow mock tokens ONLY on PostgreSQL storage backend when Firebase Auth is explicitly disabled
        or when running in development mode.

        Returns:
            True if mock tokens are permitted, False otherwise.
        """
        if self.is_cloud_storage:
            return False
        if self.active_backend != StorageBackend.POSTGRES:
            return False
        if not self.use_firebase_auth:
            return True
        return self.environment.lower() == "development"

    @computed_field
    @property
    def schema_max_chunk_records(self) -> int:
        """Maximum number of records (main + context) the LLM is expected to parse in a single chunk.

        Returns:
            Calculated integer limit for chunk records.
        """
        return self.llm_max_chunk_size + 5

    @computed_field
    @property
    def schema_max_source_aliases(self) -> int:
        """Target limits for source document array (logically bound to quote limit, capped by chunk size).

        Returns:
            Calculated integer limit for source aliases.
        """
        return min(self.schema_max_quotes_target, self.schema_max_chunk_records)

    # Centralized Mock Token IDs for testing
    mock_admin_user_id: Annotated[
        str,
        Field(
            default="usr_18a0d5f6151349a5",
            validation_alias=AliasChoices("mock_admin_user_id", "MOCK_ADMIN_USER_ID"),
            description="Mock Admin User ID",
        ),
    ] = "usr_18a0d5f6151349a5"
    mock_root_user_id: Annotated[
        str,
        Field(
            default="usr_a3fd6b3d77c748f4",
            validation_alias=AliasChoices("mock_root_user_id", "MOCK_ROOT_USER_ID"),
            description="Mock Root User ID",
        ),
    ] = "usr_a3fd6b3d77c748f4"
    mock_analyst_user_id: Annotated[
        str,
        Field(
            default="usr_8a9234f9a0c242a1",
            validation_alias=AliasChoices("mock_analyst_user_id", "MOCK_ANALYST_USER_ID"),
            description="Mock Analyst User ID",
        ),
    ] = "usr_8a9234f9a0c242a1"

    @model_validator(mode="after")
    def validate_linker_axiom_budgets(self) -> Self:
        """Validate that component axiom quotas do not exceed global root axiom ceiling.

        Returns:
            The validated Settings instance.

        Raises:
            ValueError: If combined component axiom budgets exceed the global ceiling.
        """
        if self.linker_max_bridge_axioms + self.linker_max_root_axioms > self.linker_max_global_root_axioms:
            raise ValueError(
                f"Combined linker axioms budget ({self.linker_max_bridge_axioms} bridges + "
                f"{self.linker_max_root_axioms} roots = {self.linker_max_bridge_axioms + self.linker_max_root_axioms}) "
                f"exceeds linker_max_global_root_axioms ({self.linker_max_global_root_axioms})."
            )
        return self

    @model_validator(mode="after")
    def validate_postgres_pool_and_timeout_bounds(self) -> Self:
        """Validate PostgreSQL pool size and command timeout bounds.

        Returns:
            The validated Settings instance.

        Raises:
            ValueError: If postgres_command_timeout_seconds is outside [1.0, 120.0]
                or postgres_min_pool_size exceeds postgres_max_pool_size.
        """
        if not 1.0 <= self.postgres_command_timeout_seconds <= 120.0:
            raise ValueError(
                f"postgres_command_timeout_seconds ({self.postgres_command_timeout_seconds}) "
                "must be within [1.0, 120.0]."
            )
        if self.postgres_min_pool_size > self.postgres_max_pool_size:
            raise ValueError(
                f"postgres_min_pool_size ({self.postgres_min_pool_size}) cannot exceed "
                f"postgres_max_pool_size ({self.postgres_max_pool_size})."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Singleton getter for Settings.

    Returns:
        The cached system-wide environment variables instantiation.
    """
    return Settings()


def get_lexical_fuzz_threshold(locale: str | None = None, lexical_strictness_level: int = 50) -> float:
    """Centralized helper for fetching the correct fuzzy threshold based on locale and strictness.

    Args:
        locale: Optional language code.
        lexical_strictness_level: Sovereign workflow lexical strictness level (0-100 continuous).

    Returns:
        The calibrated fuzzy matching threshold percentage as a float.
    """
    if lexical_strictness_level >= 100:
        return 100.0

    settings = get_settings()
    if not locale:
        base_threshold = settings.pre_flight_fuzz_default
    else:
        match locale.lower():
            case "fi" | "hu" | "tr":
                base_threshold = settings.pre_flight_fuzz_agglutinative
            case "en" | "sv" | "de" | "fr" | "es":
                base_threshold = settings.pre_flight_fuzz_analytic
            case "zh" | "ja" | "ko":
                base_threshold = settings.pre_flight_fuzz_isolating
            case _:
                base_threshold = settings.pre_flight_fuzz_default

    match lexical_strictness_level:
        case level if level >= 85:
            multiplier = 1.02
        case level if level >= 50:
            multiplier = 1.0
        case level if level >= 30:
            multiplier = 0.90
        case _:
            multiplier = 0.80

    return min(100.0, base_threshold * multiplier)
