# Phase 1.2: DTO-Kannan Rakentaminen - Atoms, Metrics, Root
Source: Epic Phase 1

## Objective
Finalize the new DTO bridge by implementing the Atom result structures, execution metrics, and the root `ReportDataDto` that enforces referential integrity.

## Target Files (Modify)
- `backend_v2/models/dtos/report/atoms.py` [NEW]
- `backend_v2/models/dtos/report/metrics.py` [NEW]
- `backend_v2/models/dtos/report/root.py` [NEW]

## Context Files (Read-Only)
- `backend_v2/models/enums.py`
- `backend_v2/models/dtos/report/shared.py`

## Architectural Invariants Injected
1. `universal_fail_fast`: The `@model_validator`s in atoms and root MUST raise ValueError instantly if referential integrity is broken or data constraints are violated.
2. `blind_extraction_null_hypothesis`: `AtomResultDTO` must enforce that if `contextual_override == True`, then `source_quote` is nullified securely.
3. `declarative_set_logic_mandate`: The `enforce_referential_integrity` validator in `root.py` must use strict Set logic for O(1) missing key detection.
4. `circular_dependency_prevention`: DTO files must not import ANY higher-level services. They form the absolute Layer 0.

## Proposed Changes
### `backend_v2/models/dtos/report/atoms.py`
- **[NEW]**: Implement `HydratedAtomDTO` (static cacheable ontology).
- **[NEW]**: Implement `ExtractedValueDTO` (quantitative value + unit).
- **[NEW]**: Implement `AtomResultDTO` (dynamic execution DAG node) with `validate_cognitive_vs_system_state` `@model_validator`.

### `backend_v2/models/dtos/report/metrics.py`
- **[NEW]**: Implement `ExecutionMetricsDTO` (total_atoms, evaluated, short_circuited_na, duration_ms).

### `backend_v2/models/dtos/report/root.py`
- **[NEW]**: Implement `GlobalSynthesisDTO` (executive_summary, urgency_level).
- **[NEW]**: Implement the root `ReportDataDto` that composes metrics, synthesis, `results` (topologically sorted list of `AtomResultDTO`), and `hydrated_references` (dict of `HydratedAtomDTO`). Include the `enforce_referential_integrity` `@model_validator` to guarantee Fail-Fast graph consistency.

## Destructive Operation Inventory
- None. New structures created.

## Bidirectional Integration Check
- Producer: The DAG Engine (Epic 92) will produce this payload.
- Consumer: Flutter SDUI (Epic 93) will consume this strictly typed payload.

## Knowledge Item Mandate
- **KI CREATION REQUIRED**: Since this establishes the new SSOT `ReportDataDto` standard, you MUST instruct the creation of a Knowledge Item summarizing the "DAG Engine and DTO Projection Rules" so future agents understand the split between `results` and `hydrated_references`.

## Testing & Quality Gate Plan
- Command: `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test`
- Goal: Create unit tests specifically targeting the `@model_validator` fail-fast logic (e.g., verifying it crashes when an invalid `tda_id` is referenced).

# Session Handover Context
**Achieved:** Phase 1.2 planned.
**Learned:** Strict Fail-Fast constraints enforced on the boundary payload.
**Remaining:** Execute Phase 1.2.

> To execute this Epic iteratively, start a NEW chat session and run the /tier5-resume command found at the bottom of your tracker.
