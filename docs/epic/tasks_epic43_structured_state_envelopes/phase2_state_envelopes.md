# Phase 2: Structured State Envelopes (Execution Layer)

## Objective
Refactor the Event Sourcing trace execution structure to eliminate "loose dictionary" flatteners. The `StateProjector` currently collapses DAG trace outputs into naked dicts (`"stp_123_blk_abc": { ... }`). This requires fragile string manipulation (`split("_")`, `endswith()`) to extract data. We will replace this with a strict `StepOutputDTO` list.

## Architectural Invariants (Mandatory Rules)
- **No Naked Dicts in State:** NEVER use raw dictionaries for state transit. ALWAYS intercept raw datastreams with `.model_validate()` or strongly typed models immediately at the boundary.
- **Universal Fail-Fast:** If an expected key is missing, the system MUST crash audibly (`AppException`). Zero tolerance for silent bypasses.
- **Frozen State Mutability:** DTOs MUST be immutable using `ConfigDict(frozen=True)`.

## Execution Steps

1. **Target (Modify): `backend_v2/models/state.py`**
   - Create a new strict Pydantic model `StepOutputDTO`.
   - Fields required:
     - `step_id: str` (The opaque DAG Step ID, e.g., 'stp_abc123')
     - `block_id: str` (The opaque PromptBlock ID, e.g., 'blk_xyz987')
     - `data_type: str` (e.g., 'matrix', 'text', 'logic')
     - `payload: Any` (The actual payload, ideally bounded by another base DTO if possible, but `Any` is acceptable for generic routing before specific step schema validation).
   - Inherit from `V2CoreBase`.

2. **Target (Modify): `backend_v2/services/flattener.py` (StateProjector)**
   - Locate the `fold_trace()` method.
   - Refactor the return type from `dict[str, Any]` to `list[StepOutputDTO]`.
   - Instead of building a dictionary keyed by `f"{step_id}_{block_id}"`, construct and append `StepOutputDTO` objects to a list.

3. **Context (Read-Only): `backend_v2/models/v2_core.py`**
   - Check `ExecutionRecord.step_states` type. If it expects a `dict`, this may also need to be updated to `list[StepOutputDTO]`, though the Epic says "Tietokanta (0%) ei kosketa". Thus, if `step_states` is stored in DB, `fold_trace()` is an *in-memory* projection. Keep DB models untouched, only modify the projected runtime representation.

## Verification & Quality Gate Plan
- **Script:** `uv run python scripts/backend_audit_loop.py backend_v2/models/state.py backend_v2/services/flattener.py`
- Mypy must pass strict typing without `# type: ignore` hacks.
