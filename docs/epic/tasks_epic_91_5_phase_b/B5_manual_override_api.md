# Epic 91.5 Phase B5: N/A Manual Override API

## Goal
Implement the manual override capability to support `ExecutionStatus.N_A`. This enforces the Epic 91.5 DTO Bridge requirement that all statuses use the Single Source of Truth `ExecutionStatus` enum, replacing raw strings. It also mathematically corrects the scoring engine (`scoring.py`) to properly exclude `N_A` atoms from the penalty denominator.

## Target Files (Modify)

### 1. `backend_v2/models/v2_core.py`
- Modify `HumanOverrideRequest`
  - Update `new_status` from `str` to `LaxExecutionStatus` to ensure strict enum validation on the API boundary but accept valid string equivalents.
- Modify `HumanOverrideDTO`
  - Update `new_status` from `str` to `ExecutionStatus`.
- Modify `ScorecardAtomDTO`
  - Ensure `status` explicitly uses `ExecutionStatus` instead of `str | None`.

### 2. `backend_v2/services/execution.py`
- Modify `override_atom(payload: HumanOverrideRequest, ...)`:
  - When saving the override to `record.context_variables`, access the strict enum value by using `.value` to preserve JSON serialization in the `TraceEvent` log and `evaluated_atoms` dict mapping:
    ```python
    v["evaluated_atoms"][atom_id] = payload.new_status.value
    ```

### 3. `backend_v2/hooks/scoring.py`
- Modify `recalculate(payload, profile_id, deps)`:
  - Update the loop iterating over `evaluated_atoms.items()` (around line 1270) to natively handle `N_A` overrides.
  - An `N_A` atom is mathematically "Not Applicable" and MUST be completely excluded from the denominator.
  - Implement a check for `N_A`:
    ```python
    for atom_id, status in evaluated_atoms.items():
        if atom_id not in atom_to_scale:
            continue

        effective_status = status
        
        # Epic 91.5: N/A items are mathematically excluded from the evaluation completely.
        if effective_status == "N_A":
            continue

        s_val = atom_to_scale[atom_id]
        stats[s_val]["total"] += 1
        ...
    ```

## Context Files (Read-Only)
- `backend_v2/models/enums.py` (Verify `ExecutionStatus` and `LaxExecutionStatus` enum shapes).
- `docs/epic/EPIC_91_5_DTO_Bridge.md` (Epic 91.5 rules).

## Testing & Quality Gate Plan
- Ensure strict Universal Quality Gate execution (`scripts/backend_audit_loop.py`).
- No integration tests should break, as N_A logic was not mathematically supported before.
- Record `[BASELINE]` before changes.
- Ensure the `recalculate()` math handles 0 totals properly (which it already does via `is_indeterminate = global_total > 0 ...`).

---

# Session Handover
**Achieved:**
- Tier 1 Implementation Plan for B5 created.

**Remaining:**
- Execute this implementation plan using the Tier 2 Execute workflow.

To execute this Epic iteratively, start a NEW chat session and run the following command:
`/tier5-resume --workflow=/tier2-execute --target="docs/epic/epic_91_5_phase_b_tracker.md, docs/epic/tasks_epic_91_5_phase_b/B5_manual_override_api.md" --rules=".agents/rules/00-antigravity-core.md, .agents/rules/01-python-backend.md"`
