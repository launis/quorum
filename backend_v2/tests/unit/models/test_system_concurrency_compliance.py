from backend_v2.models.enums import SystemConcurrency


def test_system_concurrency_mandatory_limits() -> None:
    """Verify that SystemConcurrency limits strictly follow the rules in 05_llm_architecture.md."""
    # SystemConcurrency.MAX_CONCURRENT_LLM_STEPS MUST be fixed at 2 to prevent API Rate Limits (429)
    assert SystemConcurrency.MAX_CONCURRENT_LLM_STEPS.value == 2

    # SystemConcurrency.LLM_MAX_RETRIES MUST be fixed at 2 to prevent infinite retry loops and quota depletion
    assert SystemConcurrency.LLM_MAX_RETRIES.value == 2

    # SystemConcurrency.FAIL_FAST_MAX_RETRIES should also default to 2 to align with self-healing retry logic
    assert SystemConcurrency.FAIL_FAST_MAX_RETRIES.value == 2
