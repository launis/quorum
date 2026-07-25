# Phase 1: DTO Model & Hook Migration

> **Source**: EPIC 118 — Phase 1 (Backend Domain Models & Service Engine Hardening)
> **Scope**: Move `FlattenedAtom` to the DTO layer and wire `EngineExecutionRequest` with `shuffled_atoms`.

---

## Objective

Establish the correct dependency graph by relocating `FlattenedAtom` from the Hooks layer (`atom_flattening.py`) into the DTO layer (`engine.py`). This ensures:
1. The **No Naked Dicts** rule is satisfied via Pydantic V2 strict typing.
2. The dependency graph remains strictly unidirectional: `Hooks → Models`, never `Models → Hooks`.
3. `EngineExecutionRequest` carries `shuffled_atoms` as a typed field for downstream engine consumption.

---

## Architectural Invariants Applied

| Rule ID | Enforcement |
|:--------|:------------|
| `no_naked_dicts_in_state` | `FlattenedAtom` replaces raw `dict` in `state_data`. |
| `strict_pydantic_v2_rust` | `ConfigDict(strict=True, frozen=True, extra="ignore")` on `FlattenedAtom`. |
| `pydantic_annotated_fields_mandate` | PEP 593 `Annotated` syntax for all fields. |
| `duck_typing_token_shield_exception` | `extra="ignore"` permitted as this is an Internal Data Projection Model. |
| `strict_model_location` | All SSOT Pydantic models live in `backend_v2/models/`. |
| `anti_semantic_drift_renaming` | Field names (`atom_id`, `question`, `extraction_rule`, `anchor_target`, `is_inverse`) preserved exactly. |

---

## Target Files (Modify)

### [MODIFY] [engine.py](file:///c:/src/quorum/backend_v2/models/dtos/engine.py)

**Current State** (verified at @[c:\src\quorum\backend_v2\models\dtos\engine.py#L21-L56]):
- `EngineExecutionRequest` exists with fields for `bound_client`, `system_prompt`, `step`, `context`, etc.
- No `shuffled_atoms` field exists.
- No `FlattenedAtom` class exists in this file.

**Changes**:
1. Add `FlattenedAtom` class ABOVE `EngineExecutionRequest` with:
   ```python
   from typing import Annotated
   from pydantic import BaseModel, ConfigDict, Field

   class FlattenedAtom(BaseModel):
       """Strict Pydantic schema for individual shuffled items (No Naked Dicts rule).

       Attributes:
           atom_id: Opaque hashed ID for the extracted atom.
           question: The text content evaluated blindly.
           extraction_rule: The specific validation rule.
           anchor_target: Semantic bounding box target.
           is_inverse: True if this is an inverse assertion.
       """
       # duck_typing_token_shield_exception: Internal Data Projection Model — extra="ignore"
       # permits safe deserialization from hook state_delta which may contain
       # transient metadata keys outside this schema's concern.
       model_config = ConfigDict(strict=True, frozen=True, extra="ignore")
       atom_id: Annotated[str, Field(description="Opaque hashed ID for the extracted atom.")]
       question: Annotated[str, Field(description="The text content evaluated blindly.")]
       extraction_rule: Annotated[str, Field(default="", description="The specific validation rule.")] = ""
       anchor_target: Annotated[str, Field(default="", description="Semantic bounding box target.")] = ""
       is_inverse: Annotated[bool, Field(default=False, description="True if this is an inverse assertion.")] = False
   ```
2. Add `shuffled_atoms` field to `EngineExecutionRequest`:
   ```python
   shuffled_atoms: Annotated[list[FlattenedAtom] | None, Field(default=None, description="Predefined matrix assertions for TDA evaluation.")] = None
   ```
3. Ensure `Annotated` is imported from `typing`.

---

### [MODIFY] [atom_flattening.py](file:///c:/src/quorum/backend_v2/hooks/atom_flattening.py)

**Current State** (verified at @[c:\src\quorum\backend_v2\hooks\atom_flattening.py#L21-L38]):
- `FlattenedAtom` is defined locally (lines 21-38).
- `FlatteningHookOutput` references `FlattenedAtom` (line 48).
- The hook function uses `FlattenedAtom` for model construction (line 193).

**Changes**:
1. **DELETE** the local `FlattenedAtom` class definition (lines 21-38).
2. **ADD** import from DTO layer:
   ```python
   from backend_v2.models.dtos.engine import FlattenedAtom
   ```
3. Keep `FlatteningHookOutput` and the hook function unchanged — they reference `FlattenedAtom` by name which now resolves to the DTO import.
4. Remove `BaseModel`, `ConfigDict`, `Field` from the `pydantic` import line ONLY IF they are no longer used locally. Verify: `FlatteningHookOutput` still uses `BaseModel`, `ConfigDict`, `Field` → keep the pydantic import.

**Destructive Operation Inventory** (symbols being MOVED, not dropped):

| Symbol | Original Location | New Location | Status |
|:-------|:-------------------|:-------------|:-------|
| `FlattenedAtom` class | `atom_flattening.py:L21-38` | `engine.py` (new definition) | MOVED |

No symbols are INTENTIONALLY DROPPED.

---

## Context Files (Read-Only)

| File | Purpose |
|:-----|:--------|
| @[c:\src\quorum\backend_v2\services\orchestrator\engines\base.py] | `ExecutionEngine` protocol — verify `EngineExecutionRequest` is the only accepted input type. |
| @[c:\src\quorum\backend_v2\models\dtos\dag_models.py] | `ExtractedAtom` and `LinkedAtomGraph` — context for downstream consumers. |

---

## Testing & Quality Gate Plan

### Baseline Capture (MANDATORY FIRST STEP)
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/engine.py --test
uv run python scripts/backend_audit_loop.py backend_v2/hooks/atom_flattening.py --test
```
Record the passing test count and coverage as `[BASELINE]`.

### Unit Tests
No NEW test cases in Phase 1 — existing tests in `test_tda_engine.py` and `test_atom_flattening` must continue passing with the relocated model.

### Negative Verification
- Verify that importing `FlattenedAtom` from `atom_flattening.py` no longer works as a local definition — it must resolve via DTO import.
- Confirm `EngineExecutionRequest` rejects unknown extra fields (existing `extra="forbid"` behavior preserved).

### Quality Gate Commands
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/engine.py --test
uv run python scripts/backend_audit_loop.py backend_v2/hooks/atom_flattening.py --test
```
