"""Test Settings Factory and Sovereignty Configuration.

Provides centralized test settings inheriting base defaults with differential delta
overrides for the development environment.
"""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from backend_v2.settings import Settings

__all__ = [
    "TEST_SETTINGS_OVERRIDES",
    "get_test_settings",
    "with_test_settings",
]

TEST_SETTINGS_OVERRIDES: dict[str, Any] = {
    "environment": "development",
    "matrix_sampling_limit": 1,
    "ensemble_parallelism": 1,
    "ensemble_min_consensus": 1,
    "llm_max_retries": 0,
    "llm_max_schema_retries": 0,
    "llm_max_logical_retries": 0,
    "llm_max_transient_retries": 0,
    "strategy_aliases": {
        "strict_strategy": "fast",
        "evaluation_strategy": "fast",
        "test_strategy": "fast",
        "strict": "fast",
        "deep": "fast",
        "sdui": "fast",
        "reasoning": "fast",
        "synthesis": "fast",
    },
    "pacing_delay_vertex_seconds": 0,
    "pacing_delay_openai_seconds": 0,
    "pacing_delay_mock_seconds": 0,
    "max_development_chunks": 1,
    "rag_preflight_chunk_size": 4000,
    "max_precedent_scan_depth": 0,
    "max_precedent_return_count": 0,
    "tavily_max_results": 0,
    "tda_linker_window_size": 2,
    "tda_linker_overlap": 0,
}


def get_test_settings(**custom_overrides: Any) -> Settings:
    """Factory constructing a strongly typed Settings instance for testing.

    Args:
        **custom_overrides: Optional overrides taking precedence over test defaults.

    Returns:
        Configured Settings instance for development/testing.
    """
    merged: dict[str, Any] = {**TEST_SETTINGS_OVERRIDES, **custom_overrides}
    return Settings(**merged)


@contextmanager
def with_test_settings(**custom_overrides: Any) -> Generator[Settings]:
    """Context manager yielding a scoped test settings instance.

    Args:
        **custom_overrides: Optional overrides taking precedence over test defaults.

    Yields:
        Configured Settings instance for development/testing.
    """
    settings = get_test_settings(**custom_overrides)
    yield settings
