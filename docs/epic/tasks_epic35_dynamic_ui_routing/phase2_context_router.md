# Epic 35 Phase 2: Context Router & Targeted Pruning

## Context vs Target
*   **TARGET (Modify):** 
    *   `backend_v2/services/orchestrator/context_router.py` (New)
    *   `backend_v2/errors.py` (Modify to add new Exceptions if missing)
    *   `tests/unit/services/test_context_router.py` (New)
*   **CONTEXT (Read-Only):**
    *   `backend_v2/models/dto/lightweight_matrix.py`
    *   `backend_v2/utils/dict_utils.py`

## Tasks

1.  **[x] COMPLETE: ContextRouter Scaffolding**
    *   Create `ContextRouter` inside `backend_v2/services/orchestrator/`.
    *   The router is exclusively responsible for interpreting UI `input_mappings` and culling data according to `output_config`.

2.  **[x] COMPLETE: UI-Driven Pruning Logic**
    *   Implement method `route_and_prune(trace_event, output_profile) -> LightweightMatrixOutput`.
    *   Instantiate `LightweightMatrixOutput` mapping explicitly.
    *   Extract ONLY the extensions listed in `output_profile.visible_extensions`.
    *   **Fail-Fast Execution:** If an extension is requested by UI but missing in `TraceEvent`, raise `MissingXaiExtensionError` (RFC 7807) immediately. Do NOT use `dict.get()` or default strings.

3.  **[x] COMPLETE: Strict Routing Modes (Intermediate Routing Firewalls)**
    *   For step-to-step mappings (e.g. `$steps.step_A`), force the presence of a `routing_mode`.
    *   Raise `MissingRoutingModeError` if mapping lacks instructions on whether to inject `strict_booleans_only` vs `full_xai`.
    *   Raise `ConfigurationError` if synthesis requests lack `output_config`.


## Verification & Quality Gate Plan
*   **Unit Tests:** `test_context_router.py` verifying that `MissingXaiExtensionError`, `ConfigurationError`, and `MissingRoutingModeError` trigger precisely according to the Zero-Compromise pledge.
*   **Audit Loop:** `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/context_router.py --test`
