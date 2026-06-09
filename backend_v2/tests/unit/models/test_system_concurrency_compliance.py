from backend_v2.models.enums import SystemConcurrency


def test_system_concurrency_mandatory_limits() -> None:
    """Verify that SystemConcurrency limits strictly follow the rules in 05_llm_architecture.md."""
    # SystemConcurrency.MAX_CONCURRENT_LLM_STEPS is raised to 15 to push limits, relying on Tenacity Jitter for 429 recovery
    assert SystemConcurrency.MAX_CONCURRENT_LLM_STEPS.value == 15

    # SystemConcurrency.LLM_MAX_RETRIES is set to 4 to give Tenacity enough room to backoff during massive concurrency
    assert SystemConcurrency.LLM_MAX_RETRIES.value == 4

    # SystemConcurrency.FAIL_FAST_MAX_RETRIES should also default to 1 to align with self-healing retry logic
    assert SystemConcurrency.FAIL_FAST_MAX_RETRIES.value == 1
