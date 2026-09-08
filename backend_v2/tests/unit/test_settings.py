import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from backend_v2.settings import Settings, get_settings


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
    with patch.dict(os.environ, clear=True):
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
    from backend_v2.settings import strip_whitespace

    assert strip_whitespace("  hello  ") == "hello"
    assert strip_whitespace(123) == 123


def test_settings_properties_and_computed_fields() -> None:
    """Test computed fields and properties on Settings."""
    from backend_v2.settings import StorageBackend

    settings = Settings(
        google_api_key="sk-test",
        openai_api_key="sk-openai",
        anthropic_api_key="sk-anthropic",
        use_mock_llm=True,
        environment="development",
        storage_backend="FIRESTORE",
        use_json_logging=True,
    )

    assert settings.active_backend == StorageBackend.FIRESTORE
    assert settings.is_cloud_storage is True
    assert settings.model_strategies == {}
    assert settings.log_format == "json"
    assert settings.allow_mock_tokens is True
    assert settings.schema_max_chunk_records == settings.llm_max_chunk_size + 5
    assert settings.schema_max_source_aliases == min(
        settings.schema_max_quotes_target, settings.schema_max_chunk_records
    )
    assert "google" in settings.enabled_providers
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
    assert "db_v2.json" in settings.prod_db_path
    assert "seed_data.json" in settings.seed_data_path
    assert "mock_responses.json" in settings.mock_responses_path
    assert settings.log_file_name in settings.log_file_path
    assert len(settings.default_safety_settings) == 4


def test_settings_service_account_auto_detection() -> None:
    """Test auto-detection of service-account.json in root when credentials are not preset."""
    with patch.dict(os.environ, clear=True), patch("pathlib.Path.exists", return_value=True):
        settings = Settings(use_mock_llm=False)
        assert settings.use_mock_llm is False
        assert os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") is not None


def test_settings_storage_backend_fallback_and_invalid() -> None:
    """Test local storage backend fallback and invalid backend raising AppException."""
    from backend_v2.exceptions import AppException
    from backend_v2.settings import StorageBackend

    s_local = Settings(storage_backend=None, use_mock_llm=True)
    assert s_local.active_backend == StorageBackend.LOCAL

    s_tinydb = Settings(storage_backend="TINYDB", use_mock_llm=True)
    assert s_tinydb.active_backend == StorageBackend.LOCAL

    s_dev = Settings(use_mock_llm=True, environment="development", use_json_logging=False)
    assert s_dev.log_format == "readable"

    s_prod = Settings(use_mock_llm=True, environment="production", use_json_logging=False)
    assert s_prod.log_format == "json"
    assert s_prod.allow_mock_tokens is False

    s_prod_local = Settings(use_mock_llm=True, environment="production", use_firebase_auth=False)
    assert s_prod_local.allow_mock_tokens is True

    with pytest.raises(AppException):
        _ = Settings(storage_backend="INVALID_STORAGE", use_mock_llm=True).active_backend


def test_settings_model_post_init_no_credentials_raises() -> None:
    """Test production mode without credentials raises AppException."""
    from backend_v2.exceptions import AppException

    with patch.dict(os.environ, clear=True), patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(AppException):
            Settings(use_mock_llm=False, google_api_key=None)


def test_get_lexical_fuzz_threshold() -> None:
    """Test locale-based fuzzy threshold lookup."""
    from backend_v2.settings import get_lexical_fuzz_threshold

    assert get_lexical_fuzz_threshold(None) == 90.0
    assert get_lexical_fuzz_threshold("fi") == 85.0
    assert get_lexical_fuzz_threshold("hu") == 85.0
    assert get_lexical_fuzz_threshold("en") == 92.0
    assert get_lexical_fuzz_threshold("zh") == 98.0
    assert get_lexical_fuzz_threshold("unknown") == 90.0


def test_test_settings_factory_inherits_base_with_differential_delta() -> None:
    """Test that get_test_settings factory inherits base defaults and applies fast overrides."""
    from backend_v2.core.test_settings import get_test_settings, with_test_settings

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
    assert test_settings.tavily_max_results == 1
    assert test_settings.tda_linker_window_size == 2
    assert test_settings.tda_linker_overlap == 0
    assert test_settings.strategy_aliases["reasoning"] == "fast"

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
    from pydantic import ValidationError

    # Valid environments
    dev_settings = Settings(use_mock_llm=True, environment="development")
    assert dev_settings.environment == "development"
    assert dev_settings.llm_max_retries == 0
    assert dev_settings.ensemble_parallelism == 1
    assert dev_settings.matrix_sampling_limit == 1
    assert dev_settings.tavily_max_results == 1

    prod_settings = Settings(use_mock_llm=True, environment="production")
    assert prod_settings.environment == "production"
    assert prod_settings.llm_max_retries == 2
    assert prod_settings.ensemble_parallelism == 3
    assert prod_settings.matrix_sampling_limit == 0
    assert prod_settings.tavily_max_results == 5

    # Invalid environments must fail validation
    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, environment="staging")

    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, environment="test")

    with pytest.raises(ValidationError):
        Settings(use_mock_llm=True, environment="qa")
