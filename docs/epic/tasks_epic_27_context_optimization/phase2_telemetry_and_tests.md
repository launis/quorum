# Epic 27 Phase 2: Telemetry and Schema Extensions Pruning

## Objective
Implement Phase 4, 5, and 6 of Epic 27. Prune excessive matrix extensions for surgical accuracy, add rigorous token telemetry to the backend, and establish the A/B test shadow mode script to empirically prove lossless compression.

## Target Architecture
- **TARGET (Modify):** 
  - `backend_v2/seed/seed_data.json`
  - `backend_v2/llm/client.py`
  - `scripts/verify_epic_27_ab_test.py` (Create [NEW])
- **CONTEXT (Read-Only):**
  - `backend_debug.log`
  - `backend_v2/models/enums.py` (XaiExtensionType definitions)

## Implementation Steps

### 1. Matrix Extensions Tuning (Phase 4: Output Extensions)
Modify `backend_v2/seed/seed_data.json`:
- Audit all matrices (e.g., `matrix_bloom`, `matrix_toulmin`, `matrix_kahneman`, `matrix_goodhart`, `matrix_archivist`, `matrix_causal_analyst`, `matrix_falsifier`, `matrix_judge`, `matrix_xai_reporter`).
- Prune their `output_extensions` arrays strictly to the minimum required extensions defined in the Epic 27 documentation.
  - *Example*: `matrix_kahneman` receives only `justification`, `falsification`, and `confidence`.
- Do not alter the scales or underlying theory logic, only the `output_extensions` array.

### 2. Telemetry and Cost Tracing (Phase 5: Telemetry)
Modify `LLMClient` in `backend_v2/llm/client.py`:
- Inject absolute latency timing around the `provider.generate()` call.
- Extract total tokens (`prompt_tokens`, `completion_tokens`) and log the API Latency ms and Token usage explicitly using `logger.info()`.
- Expose these fields in the `usage_obj` that rolls into the `TraceEvent` output, allowing empirical measurement of the payload compression (targeting 40-60% payload drop, 846kt max load baseline).

### 3. A/B Shadow Mode Script (Phase 6: Verification Strategy)
Create `scripts/verify_epic_27_ab_test.py`:
- A python validation script intended to parse or trigger a comparison between a legacy run (Pipeline A) and an optimized run (Pipeline B - post Epic 27).
- Print comparative analytics (Duration differences, Payload sizes, and Boolean `TRUE` distribution among Atom matrices) to confirm "lossless" theoretical fidelity.

## Verification & Quality Gate Plan
- Apply seed data changes via `uv run python scripts/run_seed.py`
- Verify updated client code architecture via `uv run python scripts/backend_audit_loop.py backend_v2/llm/client.py`
- Trigger the verification script: `uv run python scripts/verify_epic_27_ab_test.py`
