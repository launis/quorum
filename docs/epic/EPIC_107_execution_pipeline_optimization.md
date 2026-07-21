# EPIC 107: Execution Pipeline Optimization & Pacing Lock Resolution

## 1. Objective
Optimize the Quorum DAG execution pipeline to eliminate massive "Pacing Lock" bottlenecks, reduce redundant LLM Map-Reduce calls, and parallelize slow Agentic loops. This will drastically reduce execution time (from hours to minutes for large documents in Production) and minimize token burn.

## 2. Background & Problem Statement
### 2. Pacing Lockin Korvaaminen LiteLLM Routerilla (Vahvistettu)
**Ongelma:** `base_adapter.py`:n oma `_apply_provider_pacing` käyttää Rediksen asynkronista kyselyluuppia (`while True: await asyncio.sleep(0.5)`). Kun Gemini Flashin 100 RPM rajoitus ylittyy (esim. 9 rinnakkaisen roolin takia), silmukka synnyttää Thundering Herd -ilmiön (satoja tehtäviä heräämässä 0.5s välein tekemään verkkokutsua). Tämä tukkii Pythonin tapahtumasilmukan ja aikakatkaisee jopa kevyet taustatehtävät kuten `litellm_core_utils\logging_worker.py`.

**Ratkaisu (Option 2):**
- Poistetaan kokonaan oma `Semaphore`-logiikka `provider.py`:stä.
- Poistetaan `_apply_provider_pacing` -luuppi `base_adapter.py`:stä.
- Annetaan Redis-konfiguraatio (`redis_host`, `redis_port`) suoraan LiteLLM:n `Router`-luokalle `provider.py`:ssä.
- LiteLLM seuraa RPM-rajoituksia keskitetysti. Jos raja ylittyy, se heittää `RateLimitError`in. Tämä siirtää vetovastuun olemassa olevalle `Tenacity`-kirjastollemme (joka käyttää fiksua exponential backoffia jitterillä), poistaen tapahtumasilmukan ukkoutumisen.

During local development testing (Fast Mode) and Production telemetry analysis, severe performance bottlenecks were identified in the DAG Engine:
1. **Artificial RPM Bottleneck**: `LiteLLM` and the internal Vertex AI adapters are enforcing a 100 RPM Pacing Lock for `gemini-2.5-flash`, despite the GCP quota being 200 RPM. This causes the system to sleep (`0.6s` per request) when the 9-role Floodgate opens.
2. **Redundant Map-Reduce (Guard Step)**: The `Guard` step processes the entire document identically to `Input Processing`, doubling the LLM calls and token usage strictly for a security check.
3. **Agentic Loop Freezing (Faktantarkistaja)**: The Fact Checker utilizes an iterative agent loop (`mcp_tavily_search`) per atom. Executing this sequentially inside the concurrent Floodgate paralyzes the `asyncio.TaskGroup`, as all other roles must wait for the slowest agent to finish its network requests.

## 3. Architectural Constraints & Modernity Gates
* **Central Config Sovereignty**: All RPM limits and concurrency divisors must be strictly defined in `backend_v2/settings.py`. Hardcoding values inside the LLM adapters is strictly prohibited.
* **Fail-Fast & Strict Typing**: Any new schemas introduced for Multi-Search batching must enforce `ConfigDict(strict=True, extra='forbid')`.
* **Python 3.14 Concurrency**: The Fact Checker's Multi-Search network calls MUST be orchestrated using `asyncio.TaskGroup` (not `asyncio.gather`).
* **Zero-Compromise Pledge**: The Guard step fusion must not weaken security. If the merged Input Processing step detects a violation, it must Fail-Fast via a strictly typed exception or DTO flag, not via silent fallback.

## 4. Execution Phases

### Phase 1: RPM Quota Alignment (Option A)
* **Goal**: Unlock the full 200 RPM throughput for Gemini Flash.
* **Architecture**:
  * Modify `backend_v2/settings.py` to explicitly set `llm_default_rpm` or specific provider parameters to align with the 200 RPM GCP limit.
  * Tune the `semaphore_rpm_divisor` if necessary to ensure the `LiteLLM` router does not artificially throttle the `asyncio.TaskGroup` during the 9-role Floodgate burst.

### Phase 2: Guard Step Fusion
* **Goal**: Eliminate the standalone `Guard` DAG step to save ~120 LLM calls per large document.
* **Architecture**:
  * Update the system prompt (in `seed_data.json` or `directives.py`) for `Input Processing` to inherently include the Guard security constraints.
  * Define a strictly typed Pydantic response struct indicating `is_safe: bool` and `rejection_reason: str | None`.
  * If `is_safe == False`, the DAG orchestrator must trigger a Fail-Fast pipeline halt.
  * Purge the obsolete `Guard` step from the `seed_data.json` SSOT.

### Phase 3: Faktantarkistaja Multi-Search Architecture
* **Goal**: Replace the slow, sequential 1-by-1 Agentic Loop with a concurrent Batch Multi-Search.
* **Architecture**:
  * **Step 3.1**: The LLM evaluates all flattened atoms simultaneously and returns a `BatchSearchQueryDTO` containing a list of required Tavily queries.
  * **Step 3.2**: The Backend natively executes all Tavily queries concurrently using `asyncio.TaskGroup`.
  * **Step 3.3**: The aggregated search results are injected into a final synthesis prompt to generate the Fact Checker's definitive Output Matrix.
  * This reduces the LLM calls from `N * 3` to exactly `2`, completely bypassing the Pacing Lock queue.

## 5. Verification Plan
* **Telemetry Audit**: Run `finops_trace_analyzer.py` post-execution to verify that Pacing Locks (`Wait-and-Poll`) have decreased by at least 80%.
* **Token Burn**: Verify a 40-50% reduction in total tokens processed during the pre-floodgate phase due to the Guard fusion.
* **Unit Testing**: Ensure the new `BatchSearchQueryDTO` is covered by standard `backend_audit_loop.py` tests with mocked Tavily network responses.

## 6. Tier 4 RCA Findings: WinError 5 (File Locking)
* **Root Cause**: The DAG Executor crashed with `PermissionError: [WinError 5]` at 97% completion because `os.replace` on Windows is not atomic if another process (e.g. `finops_trace_analyzer.py` or antivirus) is reading the file. The original `LocalFileDriver` retry loop was too short (5 retries * 0.1s = 0.5s total), causing a hard timeout. Additionally, the specific `AppException(409)` thrown by the retry loop was incorrectly swallowed by an outer `except Exception` block and re-thrown as a generic `500` error, destroying the forensic audit trail.
* **Resolution**: 
  1. Increased `MAX_REPLACE_RETRIES` to 15 and `REPLACE_RETRY_DELAY_SEC` to 0.5s (7.5s total window).
  2. Fixed `LocalFileDriver.save` to explicitly catch and re-raise `AppException` without wrapping it, restoring the RFC-7807 Fail-Fast pipeline.
  3. Added `test_local_file_driver.py` regression tests to enforce retry logic exhaustion and success paths.
