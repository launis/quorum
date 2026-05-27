# Phase 3: Exponential Jitter-Backoff & Cache Control Integration (LLM Layer)

This sub-plan covers implementing resilient exponential backoff with random jitter and mapping caching strategy headers in LiteLLM calls.

## Architectural Invariants (From Rules)
1. **Rule 1: Concurrency Limits and Retries SSOT** - `LLM_MAX_RETRIES` on tenacity retry loops must be strictly capped at 2 (`SystemConcurrency.LLM_MAX_RETRIES.value` which is locked at 2).
2. **Rule 2: Context Caching Standard (Lost in the Middle Prevention)** - System prompts must remain perfectly static to maximize prompt caching osumatarkkuus.

## Proposed Changes

### Target Files (Modify)
- [provider.py](file:///c:/src/quorum/backend_v2/llm/provider.py)

### Context Files (Read-Only)
- [client.py](file:///c:/src/quorum/backend_v2/llm/client.py)

---

## Milestones

### Milestone 1: Implement Resilient Jitter Backoff in provider.py
* **Source**: Epic Phase 3, Step 1
* **Files**: [provider.py](file:///c:/src/quorum/backend_v2/llm/provider.py)
* **Instructions**: Locate the tenacity `AsyncRetrying` loop in `LiteLLMProvider.generate` (around line 362). Replace the static rate limit cooldown with tenacity exponential backoff combined with random jitter:
```python
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(max_rate_limit_retries + 1),
                wait=wait_combine(
                    wait_exponential(multiplier=2, min=2, max=30),
                    wait_random(1, 5),
                ),
                retry=retry_if_exception(_is_transient_llm_error),
                reraise=True,
                before_sleep=lambda rs: logger.warning(
                    "[LiteLLMProvider] Transient Error or Quota Exhausted (Attempt %s/%s). "
                    "Initiating dynamic exponential backoff... | Error: %s",
                    rs.attempt_number,
                    max_rate_limit_retries,
                    type(rs.outcome.exception()).__name__ if rs.outcome and rs.outcome.failed else "Unknown",
                ),
            ):
```

### Milestone 2: Map Caching Strategy in client.py Caching Headers
* **Source**: Epic Phase 4, Step 1
* **Files**: [client.py](file:///c:/src/quorum/backend_v2/llm/client.py)
* **Instructions**: Verify that `LLMClient.run_structured_task` correctly implements universal context caching tags for different strategies. Support both `anthropic_ephemeral` (using `cache_control`) and `gemini_native` as documented:
```python
        has_ephemeral_caching = False
        if self._config and self._config.caching_strategy in ("prompt_caching", "ephemeral", "anthropic_ephemeral", "gemini_native"):
            logger.info("[LLMClient] Enabling Universal Ephemeral Context Caching strategy: %s", self._config.caching_strategy)
            has_ephemeral_caching = True
```

---

## Testing & Quality Gate Plan

### Automated Tests
1. Run LLM Client and Provider unit tests:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/llm/ --test
   ```
2. Verify all tests pass and coverage is >90%.

---

## Session Handover
To proceed, start a new session and invoke the next step via the Master Tracker:
```powershell
To execute this Epic iteratively, start a NEW chat session and run: /tier5-resume --target docs/epic/EPIC_62_tracker.md
```
