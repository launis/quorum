"""Unit tests for application settings and environment configuration invariants."""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.core.test_settings import get_test_settings, with_test_settings
from backend_v2.exceptions import AppException
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer
from backend_v2.settings import (
    Settings,
    StorageBackend,
    get_lexical_fuzz_threshold,
    get_settings,
    strip_whitespace,
)


def test_settings_initialization() -> None:
    """Test that settings can be instantiated with default or provided values."""
    settings = Settings(google_api_key="sk-google-test", use_mock_llm=True)
    assert settings.google_api_key == "sk-google-test"
    assert settings.use_mock_llm is True


def test_get_settings_lru_cache() -> None:
    """Test that get_settings is properly cached and returns a singleton instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_settings_model_post_init_mock_llm() -> None:
    """Test the Google AI post_init validation bypasses key check when mock LLM is enabled."""
    with patch.dict("backend_v2.settings.os.environ", {}, clear=True):
        settings = Settings(use_mock_llm=True)
        # Should not raise any validation error because mock LLM is true.
        assert settings.use_mock_llm is True


def test_authenticity_threshold_high_below_minimum_raises() -> None:
    """Boundary test: Setting authenticity_threshold_high below 0.0 raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings(authenticity_threshold_high=-0.1, use_mock_llm=True)


def test_authenticity_threshold_high_above_maximum_raises() -> None:
    """Boundary test: Setting authenticity_threshold_high above 3.0 raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings(authenticity_threshold_high=3.1, use_mock_llm=True)


def test_authenticity_threshold_low_below_minimum_raises() -> None:
    """Boundary test: Setting authenticity_threshold_low below 0.0 raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings(authenticity_threshold_low=-0.1, use_mock_llm=True)


def test_authenticity_threshold_low_above_maximum_raises() -> None:
    """Boundary test: Setting authenticity_threshold_low above 3.0 raises ValidationError."""
    with pytest.raises(ValidationError):
        Settings(authenticity_threshold_low=3.1, use_mock_llm=True)


def test_authenticity_threshold_inversion_raises() -> None:
    """Negative test: Setting high < low raises ValidationError with cross-field message."""
    with pytest.raises(ValidationError, match="must be >="):
        Settings(authenticity_threshold_high=1.0, authenticity_threshold_low=2.0, use_mock_llm=True)


def test_authenticity_threshold_equal_values_valid() -> None:
    """Boundary test: High == low is valid and passes validation."""
    settings = Settings(authenticity_threshold_high=2.0, authenticity_threshold_low=2.0, use_mock_llm=True)
    assert settings.authenticity_threshold_high == 2.0
    assert settings.authenticity_threshold_low == 2.0


def test_authenticity_threshold_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Positive test: Environment variables override default threshold values."""
    monkeypatch.setenv("AUTHENTICITY_THRESHOLD_HIGH", "2.8")
    monkeypatch.setenv("AUTHENTICITY_THRESHOLD_LOW", "1.2")
    settings = Settings(use_mock_llm=True)
    assert settings.authenticity_threshold_high == 2.8
    assert settings.authenticity_threshold_low == 1.2


def test_strip_whitespace_and_custom_types() -> None:
    """Test whitespace stripping validator and bool parsing."""
    assert strip_whitespace("  hello  ") == "hello"
    assert strip_whitespace(123) == 123


def test_settings_properties_and_computed_fields() -> None:
    """Test computed fields and properties on Settings."""
    settings = Settings(
        google_api_key="sk-test",
        openai_api_key="sk-openai",
        anthropic_api_key="sk-anthropic",
        use_mock_llm=True,
        environment="development",
        use_json_logging=True,
    )

    assert settings.active_backend == StorageBackend.POSTGRES
    assert settings.is_cloud_storage is False
    assert settings.log_format == "json"
    assert settings.allow_mock_tokens is True
    assert settings.schema_max_chunk_records == settings.llm_max_chunk_size + 5
    assert settings.schema_max_source_aliases == min(
        settings.schema_max_quotes_target, settings.schema_max_chunk_records
    )
    assert "ai_studio" in settings.enabled_providers
    assert "openai" in settings.enabled_providers
    assert "anthropic" in settings.enabled_providers
    assert "mock" in settings.enabled_providers

    # Path properties
    assert "backend_v2" in settings.base_dir
    assert "data" in settings.data_dir
    assert "files" in settings.files_dir
    assert "docs" in settings.docs_dir
    assert "database" in settings.db_dir
    assert "scripts" in settings.scripts_dir
    assert "postgres_v2.db" in settings.prod_db_path
    assert "seed_data.json" in settings.seed_data_path
    assert "mock_responses.json" in settings.mock_responses_path
    assert settings.log_file_name in settings.log_file_path
    assert len(settings.default_safety_settings) == 4


def test_settings_service_account_auto_detection() -> None:
    """Test auto-detection of service-account.json in root when credentials are not preset."""
    with (
        patch.dict("backend_v2.settings.os.environ", {}, clear=True) as scoped_env,
        patch("backend_v2.settings.Path.exists", return_value=True),
    ):
        settings = Settings(use_mock_llm=False)
        assert settings.use_mock_llm is False
        assert "GOOGLE_APPLICATION_CREDENTIALS" in scoped_env
        assert "vertex_ai" in settings.enabled_providers


def test_settings_storage_backend_fallback_and_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test PostgreSQL 19 sovereign storage backend and invalid STORAGE_BACKEND environment rejection."""
    s_default = Settings(use_mock_llm=True)
    assert s_default.active_backend == StorageBackend.POSTGRES
    assert s_default.is_cloud_storage is False

    s_none = Settings(use_mock_llm=True, storage_backend=None)
    assert s_none.active_backend == StorageBackend.POSTGRES

    monkeypatch.setenv("STORAGE_BACKEND", "UNSUPPORTED_DB")
    s_invalid = Settings(use_mock_llm=True)
    with pytest.raises(AppException, match="Unsupported STORAGE_BACKEND"):
        _ = s_invalid.active_backend
    with pytest.raises(AppException, match="Unsupported STORAGE_BACKEND"):
        _ = s_invalid.allow_mock_tokens
    monkeypatch.delenv("STORAGE_BACKEND", raising=False)

    s_dev = Settings(use_mock_llm=True, environment="development", use_json_logging=False)
    assert s_dev.log_format == "readable"

    s_prod = Settings(use_mock_llm=True, environment="production", use_json_logging=False)
    assert s_prod.log_format == "json"
    assert s_prod.allow_mock_tokens is False

    s_prod_local = Settings(use_mock_llm=True, environment="production", use_firebase_auth=False)
    assert s_prod_local.allow_mock_tokens is True

    s_cloud = Settings(
        use_mock_llm=True,
        environment="development",
        storage_bucket_name="quorum-prod-bucket",
    )
    assert s_cloud.is_cloud_storage is True
    assert s_cloud.allow_mock_tokens is False


def test_settings_allow_mock_tokens_defense_in_depth() -> None:
    """Test defense-in-depth firewall for allow_mock_tokens under PostgreSQL 19."""
    # Negative Partition: POSTGRES storage with active Firebase auth bans mock tokens in production
    s_pg_prod_fb = Settings(
        use_mock_llm=True,
        use_firebase_auth=True,
        environment="production",
    )
    assert s_pg_prod_fb.allow_mock_tokens is False

    # Positive Partition 1: POSTGRES storage in development allows mock tokens
    s_pg_dev = Settings(
        use_mock_llm=True,
        use_firebase_auth=True,
        environment="development",
    )
    assert s_pg_dev.allow_mock_tokens is True

    # Positive Partition 2: POSTGRES storage with disabled Firebase auth allows mock tokens
    s_pg_no_fb = Settings(
        use_mock_llm=True,
        use_firebase_auth=False,
        environment="production",
    )
    assert s_pg_no_fb.allow_mock_tokens is True


def test_settings_model_post_init_no_credentials_raises() -> None:
    """Test production mode without credentials raises AppException."""
    with (
        patch.dict("backend_v2.settings.os.environ", {}, clear=True),
        patch("backend_v2.settings.Path.exists", return_value=False),
    ):
        with pytest.raises(AppException):
            Settings(use_mock_llm=False, google_api_key=None)


def test_get_lexical_fuzz_threshold() -> None:
    """Test locale-based fuzzy threshold lookup across locales and strictness levels."""
    assert get_lexical_fuzz_threshold(None) == 90.0
    assert get_lexical_fuzz_threshold("fi") == 85.0
    assert get_lexical_fuzz_threshold("hu") == 85.0
    assert get_lexical_fuzz_threshold("tr") == 85.0
    assert get_lexical_fuzz_threshold("en") == 92.0
    assert get_lexical_fuzz_threshold("sv") == 92.0
    assert get_lexical_fuzz_threshold("zh") == 98.0
    assert get_lexical_fuzz_threshold("ja") == 98.0
    assert get_lexical_fuzz_threshold("unknown") == 90.0

    # Strictness level BVA partitions: >= 100, >= 85, >= 50, >= 30, < 30
    assert get_lexical_fuzz_threshold("en", lexical_strictness_level=100) == 100.0
    assert get_lexical_fuzz_threshold("fi", lexical_strictness_level=85) == pytest.approx(85.0 * 1.02)
    assert get_lexical_fuzz_threshold("fi", lexical_strictness_level=30) == pytest.approx(85.0 * 0.90)
    assert get_lexical_fuzz_threshold("fi", lexical_strictness_level=29) == pytest.approx(85.0 * 0.80)


def test_test_settings_factory_inherits_base_with_differential_delta() -> None:
    """Test that get_test_settings factory inherits base defaults and applies fast overrides."""
    test_settings = get_test_settings()
    assert test_settings.environment == "development"
    assert test_settings.matrix_sampling_limit == 1
    assert test_settings.ensemble_parallelism == 1
    assert test_settings.ensemble_min_consensus == 1
    assert test_settings.llm_max_retries == 0
    assert test_settings.llm_max_schema_retries == 0
    assert test_settings.llm_max_logical_retries == 0
    assert test_settings.llm_max_transient_retries == 0
    assert test_settings.pacing_delay_vertex_seconds == 0
    assert test_settings.pacing_delay_openai_seconds == 0
    assert test_settings.pacing_delay_mock_seconds == 0
    assert test_settings.max_development_chunks == 1
    assert test_settings.rag_preflight_chunk_size == 4000
    assert test_settings.max_precedent_scan_depth == 0
    assert test_settings.max_precedent_return_count == 0
    assert test_settings.tda_linker_window_size == 2
    assert test_settings.tda_linker_overlap == 0

    # Verify custom overrides take precedence
    custom = get_test_settings(llm_max_retries=3, matrix_sampling_limit=5)
    assert custom.llm_max_retries == 3
    assert custom.matrix_sampling_limit == 5

    # Verify with_test_settings context manager
    with with_test_settings(llm_max_retries=2) as scoped:
        assert scoped.llm_max_retries == 2
        assert scoped.environment == "development"


def test_settings_binary_environment_validation() -> None:
    """Test that Settings validates binary environment strictly and rejects invalid strings."""
    # Valid environments
    dev_settings = Settings(use_mock_llm=True, environment="development")
    assert dev_settings.environment == "development"
    assert dev_settings.llm_max_retries == 0
    assert dev_settings.llm_max_transient_retries == 3
    assert dev_settings.ensemble_parallelism == 1
    assert dev_settings.matrix_sampling_limit == 1

    prod_settings = Settings(use_mock_llm=True, environment="production")
    assert prod_settings.environment == "production"
    assert prod_settings.llm_max_retries == 2
    assert prod_settings.ensemble_parallelism == 3
    assert prod_settings.matrix_sampling_limit == 0

    # Invalid environments must fail validation
    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, environment="staging")

    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, environment="test")

    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, environment="qa")


def test_dev_max_thinking_budget_invariants() -> None:
    """ISTQB BVA & Equivalence Partitioning for dev_max_thinking_budget setting."""
    # 1. Default in dev mode is 0
    dev_settings = Settings(use_mock_llm=True, environment="development")
    assert dev_settings.dev_max_thinking_budget == 0

    # 2. Test settings parity
    assert get_test_settings().dev_max_thinking_budget == 0

    # 3. Explicit positive integer allowed
    custom_settings = Settings(use_mock_llm=True, environment="development", dev_max_thinking_budget=1024)
    assert custom_settings.dev_max_thinking_budget == 1024

    # 4. Negative BVA test: < 0 raises ValidationError
    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, dev_max_thinking_budget=-1)


def test_settings_llm_default_timeout_invariants() -> None:
    """Verify Settings.llm_default_timeout default, bounds, and test settings parity."""
    # 1. Default positive value: 120.0
    settings = Settings(use_mock_llm=True)
    assert settings.llm_default_timeout == 120.0

    # 2. Test settings parity
    assert get_test_settings().llm_default_timeout == 120.0

    # 3. Custom valid positive float
    custom = Settings(use_mock_llm=True, llm_default_timeout=60.0)
    assert custom.llm_default_timeout == 60.0

    # 4. Lower boundary valid (gt=0.0)
    lower_bound = Settings(use_mock_llm=True, llm_default_timeout=0.001)
    assert lower_bound.llm_default_timeout == 0.001

    # 5. Upper boundary valid (le=3600.0)
    upper_bound = Settings(use_mock_llm=True, llm_default_timeout=3600.0)
    assert upper_bound.llm_default_timeout == 3600.0

    # 6. Negative BVA boundary (<= 0.0)
    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, llm_default_timeout=0.0)

    # 7. Negative BVA boundary (< 0.0)
    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, llm_default_timeout=-1.0)

    # 8. Negative BVA boundary (> 3600.0)
    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, llm_default_timeout=3601.0)


def test_settings_causal_defaults() -> None:
    """Verify Settings causal discovery defaults and types."""
    settings = get_settings()
    assert settings.causal_discovery_window_size == 4
    assert settings.causal_discovery_overlap == 2
    assert settings.causal_discovery_max_atoms_per_window == 25
    assert settings.causal_discovery_max_total_atoms == 100
    assert settings.causal_secondary_fault_dampening == 0.25
    assert settings.two_pass_atomizer_packet_size == 50

    # Custom valid overrides
    custom = Settings(
        use_mock_llm=True,
        causal_discovery_window_size=6,
        causal_discovery_overlap=3,
        causal_discovery_max_atoms_per_window=30,
        causal_discovery_max_total_atoms=150,
        causal_secondary_fault_dampening=0.5,
        two_pass_atomizer_packet_size=25,
    )
    assert custom.causal_discovery_window_size == 6
    assert custom.causal_discovery_overlap == 3
    assert custom.causal_discovery_max_atoms_per_window == 30
    assert custom.causal_discovery_max_total_atoms == 150
    assert custom.causal_secondary_fault_dampening == 0.5
    assert custom.two_pass_atomizer_packet_size == 25


def test_two_pass_atomizer_dynamic_packet_size() -> None:
    """Verify TwoPassAtomizer dynamically resolves packet_size from settings when None."""
    mock_executor = MagicMock(spec=LLMTaskExecutor)
    atomizer = TwoPassAtomizer(executor=mock_executor)

    # 120 blocks: [B0000] text \n\n [B0001] text ...
    hydrated_lines = [f"[B{i:04d}] Block text {i}" for i in range(120)]
    hydrated_text = "\n\n".join(hydrated_lines)

    # When packet_size is None, should resolve to get_settings().two_pass_atomizer_packet_size == 50
    packets = atomizer._calculate_packets(hydrated_text, packet_size=None)
    assert len(packets) == 3
    assert len(packets[0].packet_keys) == 50
    assert len(packets[1].packet_keys) == 50
    assert len(packets[2].packet_keys) == 20
    assert packets[0].start_block == "B0000"
    assert packets[0].end_block == "B0049"

    # Explicit packet_size parameter takes precedence
    custom_packets = atomizer._calculate_packets(hydrated_text, packet_size=20)
    assert len(custom_packets) == 6
    assert len(custom_packets[0].packet_keys) == 20


def test_generic_mcp_settings_invariants() -> None:
    """ISTQB BVA & Equivalence Partitioning for generic MCP protocol settings."""
    test_settings = get_test_settings()
    assert test_settings.mcp_default_timeout_seconds == 30
    assert test_settings.mcp_discovery_timeout_seconds == 10
    assert test_settings.mcp_max_response_chars == 8000
    assert test_settings.mcp_allow_private_networks is False

    custom = Settings(
        use_mock_llm=True,
        mcp_default_timeout_seconds=60,
        mcp_discovery_timeout_seconds=15,
        mcp_max_response_chars=12000,
        mcp_allow_private_networks=True,
    )
    assert custom.mcp_default_timeout_seconds == 60
    assert custom.mcp_discovery_timeout_seconds == 15
    assert custom.mcp_max_response_chars == 12000
    assert custom.mcp_allow_private_networks is True

    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, mcp_default_timeout_seconds=0)
    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, mcp_default_timeout_seconds=301)

    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, mcp_discovery_timeout_seconds=0)
    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, mcp_discovery_timeout_seconds=61)

    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, mcp_max_response_chars=499)
    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, mcp_max_response_chars=50001)


def test_postgres_settings_and_boundary_invariants() -> None:
    """Verify PostgreSQL 19 Settings defaults, custom overrides, and ISTQB negative boundaries."""
    defaults = Settings(use_mock_llm=True, postgres_password=None, postgres_dsn=None)
    assert defaults.postgres_host == "127.0.0.1"
    assert defaults.postgres_port == 5432
    assert defaults.postgres_user == "quorum"
    assert defaults.postgres_password is None
    assert defaults.postgres_db == "quorum"
    assert defaults.postgres_dsn is None
    assert defaults.postgres_min_pool_size == 2
    assert defaults.postgres_max_pool_size == 20
    assert defaults.postgres_command_timeout_seconds == 15.0
    assert defaults.postgres_toast_compression == "lz4"

    custom = Settings(
        use_mock_llm=True,
        postgres_host="db.internal",
        postgres_port=5433,
        postgres_user="quorum_app",
        postgres_password="env_injected_secret",
        postgres_db="quorum_prod",
        postgres_min_pool_size=5,
        postgres_max_pool_size=50,
        postgres_command_timeout_seconds=30.0,
        postgres_toast_compression="lz4",
    )
    assert custom.postgres_host == "db.internal"
    assert custom.postgres_port == 5433
    assert custom.postgres_min_pool_size == 5
    assert custom.postgres_max_pool_size == 50
    assert custom.postgres_command_timeout_seconds == 30.0

    # Negative BVA 1: postgres_command_timeout_seconds < 1.0
    with pytest.raises(ValidationError, match="postgres_command_timeout_seconds"):
        Settings(use_mock_llm=True, postgres_command_timeout_seconds=0.999)

    # Negative BVA 2: postgres_command_timeout_seconds > 120.0
    with pytest.raises(ValidationError, match="postgres_command_timeout_seconds"):
        Settings(use_mock_llm=True, postgres_command_timeout_seconds=120.001)

    # Negative BVA 3: postgres_min_pool_size > postgres_max_pool_size
    with pytest.raises(ValidationError, match="postgres_min_pool_size"):
        Settings(use_mock_llm=True, postgres_min_pool_size=25, postgres_max_pool_size=10)


def test_validate_linker_axiom_budgets_invariants() -> None:
    """Verify linker axiom budgets cross-field validation and ISTQB negative boundaries."""
    valid_boundary = Settings(
        use_mock_llm=True,
        linker_max_bridge_axioms=4,
        linker_max_root_axioms=4,
        linker_max_global_root_axioms=8,
    )
    assert valid_boundary.linker_max_global_root_axioms == 8

    # Negative BVA 1: bridge + root > global ceiling
    with pytest.raises(ValidationError, match="Combined linker axioms budget"):
        Settings(
            use_mock_llm=True,
            linker_max_bridge_axioms=5,
            linker_max_root_axioms=4,
            linker_max_global_root_axioms=8,
        )

    # Negative BVA 2: negative bridge axioms (< 0)
    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, linker_max_bridge_axioms=-1)
