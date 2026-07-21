from backend_v2.settings import get_settings


def test_system_concurrency_mandatory_limits() -> None:
    """Verify that SystemConcurrency limits strictly follow the rules in 05_llm_architecture.md."""
    # Architectural law: MAX_CONCURRENT_LLM_STEPS is fixed at 3
    assert get_settings().max_concurrent_llm_steps == 3

    # Architectural law: LLM_MAX_RETRIES is fixed at 2
    assert get_settings().llm_max_retries == 2
