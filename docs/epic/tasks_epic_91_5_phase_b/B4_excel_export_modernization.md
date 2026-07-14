# Epic 91.5 Phase B4: Excel Export Modernization

## Objective
Update the `backend_v2/services/execution.py` to ensure the `get_execution_export_bytes` logic pulls its data structurally from the new `v2_core.ReportDataDTO` model and `ScorecardAtomDTO`s rather than relying on legacy or deeply nested trace JSON parsing.

## Context & Architectural Mandates
- **SSOT Mandate:** The Excel export must reflect the exact `ReportDataDTO` (Single Source of Truth) evaluated and verified by the system.
- **Fail-Fast:** No silent duct-taping. The parsing logic should gracefully fail or omit rows clearly if structural assumptions fail.

## Target Files (Modify)
- `backend_v2/services/execution.py`

## Context Files (Read-Only)
- `backend_v2/models/v2_core.py`

## Proposed Changes

### 1. Update `backend_v2/services/execution.py`
- **Modernize `get_execution_export_bytes`:** Refactor the extraction loops in the function. Instead of recursively digging into `trace_data` to find atoms with `find_evals()`, construct the `df_raw` and `df_summary` by directly reading from `execution.step_states` and the generated `ReportDataDTO`.
- Ensure it properly maps `ReportDataDTO.evaluative_matrices` and `informational_matrices` into the Excel "Yhteenveto" sheet.
- Extract individual rows for the "Raakadata" sheet using the flat `ScorecardAtomDTO` objects present in `ExecutionStepState.scorecard_atoms`.

## Testing & Quality Gate Plan
- Execute the Universal Quality Gate (`scripts/backend_audit_loop.py backend_v2/services/execution.py --test`).

---
# Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
