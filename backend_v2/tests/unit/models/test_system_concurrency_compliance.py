from backend_v2.models.enums import SystemConcurrency


def test_system_concurrency_mandatory_limits() -> None:
    """Verify that SystemConcurrency limits strictly follow the rules in 05_llm_architecture.md."""
    # Architectural law: MAX_CONCURRENT_LLM_STEPS is fixed at 10
    assert SystemConcurrency.MAX_CONCURRENT_LLM_STEPS.value == 10

    # Architectural law: LLM_MAX_RETRIES is fixed at 2
    assert SystemConcurrency.LLM_MAX_RETRIES.value == 2
