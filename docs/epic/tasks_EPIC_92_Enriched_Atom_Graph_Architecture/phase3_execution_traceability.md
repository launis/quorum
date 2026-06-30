# EPIC 92: Phase 3 - Execution API & DAG Traceability

## Goal
Integrate the `tda_id` based Execution Graph (DAG) into the `executions.py` router and ensure the `depends_on_tda_ids` relationships and short-circuit metadata are correctly exposed to the frontend/client.

**Source**: [EPIC_92_Enriched_Atom_Graph_Architecture.md](file:///c:/src/quorum/docs/epic/EPIC_92_Enriched_Atom_Graph_Architecture.md) Phase 3 & 5

## Scoping
**TARGET (Modify)**
- `c:\src\quorum\backend_v2\api\routers\execution\executions.py`
- `c:\src\quorum\backend_v2\models\dtos\lightweight_matrix.py` (API response projections)

**CONTEXT (Read-Only)**
- `c:\src\quorum\backend_v2\hooks\scoring.py`

## Architectural Invariants (Hardening Mandates)
You MUST strictly adhere to these rules during execution:
- **Rule 32 (Anemic Routers)**: Routers encapsulate HTTP context. Absolutely no business logic or deep graph traversals in the router.
- **Rule 33 (Data Leak Prevention)**: Every endpoint MUST explicitly define a Pydantic `response_model=...` to prevent data layer bleeding.
- **Rule 78 (API Service Separation)**: No complex entity construction at the API boundary.

## Implementation Steps

### Step 1: Projection DTO Updates
- Update the execution response models in `lightweight_matrix.py` (or the relevant execution DTO file) to ensure `depends_on_tda_ids`, `short_circuit_reason_tda_id`, and `short_circuit_evaluation` are exposed in the JSON response payload.

### Step 2: Router Integration
- In `executions.py`, ensure the payload fetching mechanism retrieves the enriched metadata.
- Follow Rule 33 to guarantee these new fields pass through the `response_model` without triggering 500 Server Errors due to strict boundary validation.

### Step 3: Documentation Update
- Update `c:\src\quorum\docs\architecture\architecture\execution_orchestration.md` to document the DAG topology exposure.

## Testing & Quality Gate Plan
- **INTEGRATION TESTS**: Create/update `tests/unit/services/test_execution.py` to assert that:
  - A full execution JSON payload successfully serializes the DAG topology fields.
  - The `N/A` state is correctly routed to the client.
- **QUALITY GATE**: You MUST run `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/execution/executions.py --test` to verify code quality. Naked execution of `pytest` is forbidden.

---
## Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_92_tracker.md`
