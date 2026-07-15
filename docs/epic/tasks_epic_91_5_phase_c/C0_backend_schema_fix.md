# Phase C0: Backend Schema Fix — Add `execution_id` to `ReportDataDTO`

> Source: Red-Teamed Implementation Plan Phase C0 (PREREQUISITE)

## Context

The backend `ReportDataDTO` ([v2_core.py:1046-1103](file:///c:/src/quorum/backend_v2/models/v2_core.py#L1046-L1103)) is serialized via `model_dump(mode="json")` by the `/render?format=json` endpoint ([execution.py:1062-1064](file:///c:/src/quorum/backend_v2/services/execution.py#L1062-L1064)). The Flutter client's `ReportDataDto` requires `execution_id` as a `required String`, but the backend DTO does **not** include it. This causes the Flutter parser to crash silently.

## Architectural Rules Applied

- `00-antigravity-core.md`: `the_zero_compromise_pledge` — strict schemas, no fallbacks
- `01-python-backend.md`: `strict_pydantic_v2_rust` — ConfigDict(frozen=True, strict=True, extra="forbid")
- `01-python-backend.md`: `pydantic_annotated_fields_mandate` — use PEP 593 Annotated syntax
- `01-python-backend.md`: `pep257_google_style_docstrings` — docstrings mandatory

## Scope

| Role | File | Action |
|---|---|---|
| TARGET | `backend_v2/models/v2_core.py` | Add `execution_id: str` field to `ReportDataDTO` |
| TARGET | `backend_v2/services/blueprint.py` | Pass `execution_id` into `ReportDataDTO()` constructor |
| CONTEXT | `backend_v2/models/core_base.py` | Read-only — `V2CoreBase` base class |
| CONTEXT | `backend_v2/api/routers/execution/executions.py` | Read-only — verify `/render` response path |

## Milestones

### M1: Add `execution_id` to `ReportDataDTO`
**File:** `backend_v2/models/v2_core.py` (line ~1047)

Add after `workflow_id: str`:
```python
execution_id: str = Field(description="The execution's opaque Stripe ID.")
```

This field uses bare `Field` without `Annotated` because V2CoreBase DTOs use the simpler `= Field(...)` pattern consistently (matching existing fields like `workflow_id`, `profile_id`).

### M2: Pass `execution_id` in `build_report_dto`
**File:** `backend_v2/services/blueprint.py` (line ~1512)

In the `ReportDataDTO(...)` constructor call, add:
```python
execution_id=execution_id,
```

The `execution_id` variable is already available as a string parameter at line 789.

### M3: Also pass in `temp_dto` (secondary constructor)
**File:** `backend_v2/services/blueprint.py` (line ~1438)

The `temp_dto = ReportDataDTO(...)` constructor (used for intermediate profile caching) must also receive `execution_id`:
```python
execution_id=execution_id,
```

## Testing & Quality Gate

```powershell
# Run backend audit on models
uv run python scripts/backend_audit_loop.py backend_v2/models --test

# Run backend audit on blueprint service
uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test
```

### Verification
1. Verify that `ReportDataDTO.model_dump(mode="json")` now includes `execution_id` in the output.
2. Verify `/render?format=json` returns `execution_id` in the JSON response.

## Atomic Git Commit

```powershell
git add backend_v2/models/v2_core.py backend_v2/services/blueprint.py
git commit -m "feat(backend): add execution_id to ReportDataDTO for Flutter parity"
```

## Session Handover

**Achieved:** Added `execution_id` to backend `ReportDataDTO` and wired it through `build_report_dto()`.
**Remaining:** Phase C1 (Flutter DTO rewrite), C2 (DTO relocation), C3 (scorecard pipeline deletion), C4 (UI rewiring), C5 (controller updates).
