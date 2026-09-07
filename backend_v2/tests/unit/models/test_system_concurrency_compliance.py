"""Tests for system concurrency compliance and environment limits."""

from backend_v2.settings import Settings


def test_system_concurrency_mandatory_limits() -> None:
    """Verify that SystemConcurrency production limits strictly follow the rules in 05_llm_architecture.md."""
    prod_settings = Settings(environment="production")
    # Architectural law: MAX_CONCURRENT_LLM_STEPS is fixed at 3
    assert prod_settings.max_concurrent_llm_steps == 3
    # Architectural law: LLM_MAX_RETRIES is fixed at 2 in production
    assert prod_settings.llm_max_retries == 2
    # Architectural law: ENSEMBLE_PARALLELISM is fixed at 3 in production
    assert prod_settings.ensemble_parallelism == 3


def test_system_concurrency_fast_mode_limits() -> None:
    """Verify that development environment enforces fail-fast limits (0 retries, 1-pass ensemble)."""
    dev_settings = Settings(environment="development")
    assert dev_settings.llm_max_retries == 0
    assert dev_settings.ensemble_parallelism == 1
    assert dev_settings.matrix_sampling_limit == 1
