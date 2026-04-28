# Phase 3: Downstream Consumption Refactoring

## Objective
With `StateProjector.fold_trace()` now returning a strict `List[StepOutputDTO]` instead of a flattened dictionary, all downstream consumers of the trace must be refactored to consume the list deterministically, dropping all `endswith()` and string-split hacks.

## Architectural Invariants (Mandatory Rules)
- **The Duct Tape Ban:** Extract deep mutation loops into pure, isolated, testable functions. If data is malformed, let the system CRASH loudly.
- **Zero Legacy Fallback Hacks:** Do NOT use duck typing (e.g., `isinstance(data, dict)`) to guess the state payload. Read the exact `block_id` and `data_type` from `StepOutputDTO`.
- **UI-Driven Synthesis Boundary:** Synthesis hooks must filter data based strictly on UI-defined `target_blocks`. Filter the `StepOutputDTO` list strictly matching `block_id` against `target_blocks`.

## Execution Steps

1. **Target (Modify): `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`**
   - Update `ContextBuilder` methods that consume the output of `StateProjector.fold_trace()`.
   - Instead of iterating over `dict.items()` and guessing keys, iterate over `List[StepOutputDTO]`.
   - Filter payloads accurately using `dto.step_id` and `dto.block_id`.

2. **Target (Modify): `backend_v2/services/blueprint.py` (BlueprintTransformer)**
   - Remove any logic utilizing `.endswith()` or `.split("_")` to parse out block IDs.
   - Refactor matrix extraction loops. Simply filter: `[dto.payload for dto in projected_state if dto.block_id == target_block_id]`.
   - Guarantee absolute 1-to-1 matching via Opaque IDs.

3. **Target (Modify): Other Consumers**
   - Run a global search for `fold_trace` and update any other service (like `dag_executor.py` or reporting hooks) that might be calling it.

## Verification & Quality Gate Plan
- **Script:** `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ backend_v2/services/blueprint.py`
- Ensure 0 MyPy typing errors. No dictionary `.items()` calls should remain on the projected state.
