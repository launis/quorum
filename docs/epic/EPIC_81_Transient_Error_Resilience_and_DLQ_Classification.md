# EPIC 81: Transient Error Resilience & DLQ Classification Hardening

## 1. Context & Motivation

### Empirical Discovery (June 21, 2026)

During a controlled comparative execution (Run 1: `exe_174106f9...` vs Run 2: `exe_e50a6284...`), Run 2 suffered **26 atom-level crashes** routed to Dead Letter Queue (DLQ), while Run 1 completed with zero crashes. Both runs used identical inputs, identical seed data, and identical code.

Root Cause Analysis revealed a **three-layer failure cascade**:

1. **Google Vertex AI** returned a transient network error (likely 429/503) during Run 2.
2. **LiteLLM Router** (third-party library) attempted an automatic Health Check to verify model availability. This Health Check contains a hardcoded test query (`"current exchange rate EUR to USD"`) using a malformed `role: tool` message without a preceding `role: assistant` tool call. Google's API correctly rejected this as `"Missing corresponding tool call for tool response message"`.
3. **LiteLLM Router** erroneously concluded the entire `gemini-2.5-flash` deployment was `unhealthy`, causing all 26 concurrent Quorum requests queued in the Pacing Lock to receive `litellm.APIConnectionError`.
4. **Quorum's `chunk_worker.py`** caught these as generic `Exception`, classified them as non-retryable, and routed all 26 atoms directly to DLQ with `_dlq_status: "FAILED/DLQ"`.

### Impact on Scientific Validity

The `diff_executions.py` comparison tool filters out DLQ atoms (lines 232-236), reducing the common atom pool from ~164 to 138. This **biases** the remaining comparison set because the 26 lost atoms are not random — they are clustered in whichever matrices happened to be executing at the moment of the LiteLLM Health Check failure. This artificially inflates variance metrics (Kappa dropped from 0.41 to 0.23) and makes inter-run comparisons unreliable.

### Architectural Root Cause

The fundamental issue is that Quorum's error classification treats **all** non-Pydantic errors as terminal. There is no distinction between:

| Error Type | Current Behavior | Correct Behavior |
|---|---|---|
| `APIConnectionError` (network hiccup) | DLQ (permanent loss) | **Retry** (transient) |
| `RateLimitError` (429) | Retry at Provider level | Retry ✅ (already works) |
| `ValidationError` (bad JSON schema) | Self-Healing → Retry | Self-Healing ✅ (already works) |
| `TimeoutError` | DLQ (permanent loss) | **Retry** (transient) |
| `ServiceUnavailableError` (503) | DLQ (permanent loss) | **Retry** (transient) |

The Provider-level retry (`_is_transient_llm_error` in [`provider.py:73-84`](file:///c:/src/quorum/backend_v2/llm/provider.py#L73-L84)) correctly identifies `APIConnectionError` as transient. However, when the LiteLLM Router itself rejects the request (before Quorum's retry loop even fires), the error surfaces directly at the `chunk_worker.py` level, which has **no transient-vs-structural classification** — it catches `Exception` and routes everything to DLQ.

## 2. Proposed Architecture: Three-Tier Error Classification

### Tier 1: Provider-Level Retry (Already Exists ✅)
- Location: [`provider.py:448-486`](file:///c:/src/quorum/backend_v2/llm/provider.py#L448-L486)
- Handles: HTTP-level 429, 503, timeout within a single LLM call
- Uses: `tenacity` with exponential jitter backoff
- Status: **Working correctly**

### Tier 2: Chunk-Level Retry (NEW — This Epic)
- Location: [`chunk_worker.py:620-660`](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py#L620-L660)
- Current: Catches all `Exception` → DLQ
- **Proposed**: Add `_is_transient_chunk_error()` classifier before DLQ routing
- If transient: retry the entire chunk (max 2 attempts) with exponential backoff
- If structural (Pydantic, Config, Security): route to DLQ immediately (current behavior)

### Tier 3: LiteLLM Health Check Bypass (NEW — This Epic)
- Location: LiteLLM Router initialization in [`client.py`](file:///c:/src/quorum/backend_v2/llm/client.py)
- **Proposed**: Disable LiteLLM's internal Health Check entirely via `Router(enable_health_check=False)` or equivalent configuration
- Quorum already has its own robust retry and pacing infrastructure; LiteLLM's buggy Health Check adds zero value and introduces catastrophic false negatives

## 3. Affected Files & Detailed Changes

---

### Component 1: Chunk Worker (Error Classification)

#### [MODIFY] [chunk_worker.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py)

**Current behavior (lines 620-660):**
```python
# Current: ALL non-programmatic errors → DLQ (permanent data loss)
except (Exception, ExceptionGroup) as e:
    ...
    chunk_final = {"_dlq_status": "FAILED/DLQ", "reason": fallback_reason}
```

**Proposed behavior:**
```python
# NEW: Classify error before routing
except (Exception, ExceptionGroup) as e:
    if _has_programmatic_errors(e):
        raise e

    if _is_transient_chunk_error(e) and attempt < MAX_CHUNK_RETRIES:
        logger.warning("[ChunkWorker] Transient error detected. Retrying chunk (attempt %d/%d)...", ...)
        await asyncio.sleep(backoff_seconds)
        continue  # retry the chunk

    # Only route to DLQ if error is structural OR retries exhausted
    chunk_final = {"_dlq_status": "FAILED/DLQ", "reason": fallback_reason}
```

#### [NEW] Transient Error Classifier Function

```python
def _is_transient_chunk_error(exc: BaseException) -> bool:
    """Classify whether a chunk-level error is transient (retryable) or structural (terminal).

    Transient errors include network failures, rate limits, and upstream unavailability.
    Structural errors include Pydantic validation failures, configuration errors, and security violations.
    """
    import litellm

    TRANSIENT_TYPES = (
        asyncio.TimeoutError,
        ConnectionError,
        getattr(litellm, "APIConnectionError", type(None)),
        getattr(litellm, "RateLimitError", type(None)),
        getattr(litellm, "ServiceUnavailableError", type(None)),
        getattr(litellm, "Timeout", type(None)),
    )
    TRANSIENT_KEYWORDS = ("APIConnectionError", "ServiceUnavailable", "Timeout", "Resource exhausted")

    if isinstance(exc, ExceptionGroup):
        return all(_is_transient_chunk_error(inner) for inner in exc.exceptions)

    if isinstance(exc, TRANSIENT_TYPES):
        return True

    error_str = str(exc)
    return any(keyword in error_str for keyword in TRANSIENT_KEYWORDS)
```

---

### Component 2: LiteLLM Client (Health Check Bypass)

#### [MODIFY] [client.py](file:///c:/src/quorum/backend_v2/llm/client.py)

Locate the LiteLLM Router initialization and add health check bypass:

```python
# Current (hypothetical):
self.router = litellm.Router(model_list=model_list, ...)

# Proposed:
self.router = litellm.Router(
    model_list=model_list,
    enable_pre_call_checks=False,   # Disable LiteLLM's buggy health checks
    retry_after=0,                   # Let Quorum handle its own retries
    ...
)
```

> **Rationale:** LiteLLM's internal health check uses a hardcoded "EUR to USD exchange rate" test query with a malformed Tool Call structure that crashes against Vertex AI's strict message validation. Quorum's own Pacing Lock (`apply_provider_pacing`) and Tenacity retry loop provide superior, domain-aware resilience.

---

### Component 3: Orchestrator Strategy (DLQ Metrics)

#### [MODIFY] [llm.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py)

Add metrics tracking for DLQ events to distinguish transient-retried vs terminal-DLQ:

```python
# After DLQ routing (lines 510-516), add:
if c_final.get("_dlq_retry_count", 0) > 0:
    logger.info(
        "[Orchestrator] Chunk recovered after %d transient retries.",
        c_final["_dlq_retry_count"],
    )
```

---

### Component 4: diff_executions.py (Reporting Enhancement)

#### [MODIFY] [diff_executions.py](file:///c:/src/quorum/scratch/diff_executions.py)

Add DLQ count per run to the report output so that DLQ-induced bias is visible:

```python
# After "Tekniset virheet (Crash)" line, add:
dlq_count = raw_data.count('"_dlq_status": "FAILED/DLQ"')
f.write(f'  - **DLQ-pudotetut atomit:** `{dlq_count}` kpl\n')
```

## 4. Analytical Impact Assessment

### 🟢 Reliability (Estimated Impact: -90% DLQ Data Loss)
- **Current State:** A single Google 503 → LiteLLM Health Check bug → 26 atoms permanently lost.
- **Future State:** Chunk-level retry catches the transient error, waits 5-10 seconds, and re-executes. DLQ only fires for genuine structural failures (malformed prompts, security blocks).

### 🟢 Scientific Validity (Estimated Impact: +15-20% Kappa Improvement)
- **Current State:** DLQ-dropped atoms bias inter-run comparisons. Kappa artificially inflated or deflated depending on which matrices lost atoms.
- **Future State:** Near-100% atom completion rate ensures `diff_executions.py` compares the full atom set, producing statistically valid Kappa and consistency metrics.

### 🟢 Cost Efficiency (Estimated Impact: Neutral)
- Transient retries may add 1-2 extra API calls per execution, but this is negligible compared to the current cost of re-running entire executions when DLQ corruption is detected.

### 🔴 Risks
- **Retry Storms:** If Google has a prolonged outage, chunk-level retries could queue up. Mitigation: Cap at 2 retries with 10-second exponential backoff per chunk.
- **LiteLLM Version Lock:** Disabling health checks requires verifying the Router API in the current `litellm` version. If the parameter name changes in a future update, this could silently re-enable buggy health checks.

## 5. Implementation Phasing

### Phase 1: Diagnostic & Classification (Low Risk)
1. Add `_is_transient_chunk_error()` classifier to `chunk_worker.py`
2. Add DLQ telemetry to `diff_executions.py` report
3. Verify via unit test: `test_transient_error_classified_correctly`

### Phase 2: Chunk-Level Retry Loop (Medium Risk)
1. Wrap chunk execution in a retry loop (max 2 attempts)
2. Add `_dlq_retry_count` to chunk result metadata
3. Integration test: simulate `APIConnectionError` → verify retry → verify success

### Phase 3: LiteLLM Health Check Bypass (Low Risk)
1. Locate Router initialization in `client.py`
2. Add `enable_pre_call_checks=False` (or equivalent)
3. Verify via live test: intentionally trigger a 503 → confirm no "exchange rate" Health Check fires

### Phase 4: Validation Run
1. Execute two identical runs with the hardened pipeline
2. Run `diff_executions.py` and verify:
   - Zero DLQ atoms in both runs
   - Kappa returns to ≥ 0.35 baseline
   - No "Chunk Processing Failed" entries in `execution_trace.json`

## 6. Verification Plan

### Automated Tests
```bash
uv run python scripts/backend_audit_loop.py . --test
```
- `test_transient_error_classified_correctly`: Unit test for `_is_transient_chunk_error()`
- `test_chunk_retry_on_transient_error`: Integration test simulating `APIConnectionError` recovery
- `test_structural_error_routes_to_dlq`: Verify that Pydantic/Config errors still DLQ immediately

### Manual Verification
1. Run two identical executions (`run_local.bat`)
2. Compare with `uv run python scratch/diff_executions.py`
3. Confirm zero DLQ atoms and restored Kappa baseline

## 7. Conclusion

This Epic addresses a critical architectural gap where transient network failures are treated as permanent data loss events. The fix is surgical: add a single classifier function and a retry wrapper at the chunk level, plus disable LiteLLM's counterproductive Health Check. The result is a system that gracefully absorbs Google Cloud's inevitable network hiccups without sacrificing scientific validity or evaluation completeness.

### Forensic Evidence (Preserved for Audit)
- **Triggering Log Entry:** `backend_debug.log:2110` — `"Missing corresponding tool call for tool response message"`
- **LiteLLM Bug:** Hardcoded `"current exchange rate EUR to USD"` test query with malformed `role: tool` message
- **Affected Execution:** `exe_e50a6284c98e498ea228dfe7e325ef9c` — 26/164 atoms lost to DLQ
- **Comparative Report:** [`scratch/diff_report_2026-06-21_1650.md`](file:///c:/src/quorum/scratch/diff_report_2026-06-21_1650.md)
