"""Tests for system concurrency compliance and environment limits."""

import pytest
from pydantic import ValidationError

from backend_v2.settings import Settings


def test_system_concurrency_mandatory_limits() -> None:
    """Verify that SystemConcurrency production limits strictly follow the rules in 05_llm_architecture.md."""
    prod_settings = Settings(environment="production")
    # Architectural law: MAX_CONCURRENT_LLM_STEPS is fixed at 3 (governs Phase 2 synthesis fan-out only)
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


def test_settings_concurrency_zero_limits_raise_validation_error() -> None:
    """Tests that setting concurrency limits to 0 raises a ValidationError (min-1 boundary partition)."""
    fields = [
        "semaphore_low_rpm_limit",
        "semaphore_max_concurrency",
        "semaphore_rpm_divisor",
        "max_concurrent_workflows",
        "max_concurrent_llm_steps",
    ]
    for field in fields:
        with pytest.raises(ValidationError):
            Settings(**{field: 0})


def test_settings_concurrency_min_limits_accepted() -> None:
    """Tests that setting concurrency limits to 1 validates successfully (min boundary partition)."""
    assert Settings(semaphore_low_rpm_limit=1).semaphore_low_rpm_limit == 1
    assert Settings(semaphore_max_concurrency=1).semaphore_max_concurrency == 1
    assert Settings(semaphore_rpm_divisor=1).semaphore_rpm_divisor == 1
    assert Settings(max_concurrent_workflows=1).max_concurrent_workflows == 1
    assert Settings(max_concurrent_llm_steps=1).max_concurrent_llm_steps == 1
