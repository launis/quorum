# Phase 1: Backend Domain Models & DTO Hardening

> Source: Epic 118, Phase 1 (Steps 1.1 + 1.2)

## Objective

Move `FlattenedAtom` from the Hooks layer to the DTO layer and extend `EngineExecutionRequest` with the `shuffled_atoms` field. This establishes the data contract needed by Phase 2.

## PERMISSION GRANTED to mutate DAG Orchestrator ecosystem

Per `orchestrator_god_object_fragility`, this Epic explicitly grants permission to mutate the DAG Orchestrator ecosystem. This step modifies the DTO boundary used by the orchestrator.

---

## Baseline Verification (MANDATORY FIRST STEP)

Before modifying any files, record the current test state:

```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/engine.py --test
uv run python scripts/backend_audit_loop.py backend_v2/hooks/atom_flattening.py --test
```

Record the passing test count and coverage as `[BASELINE]`.

---

## Step 1.1: Add `FlattenedAtom` to DTO layer

### Scope
- **TARGET (Modify):** @[c:\src\quorum\backend_v2\models\dtos\engine.py]
- **CONTEXT (Read-Only):** @[c:\src\quorum\backend_v2\hooks\atom_flattening.py#L21-L38]

### Actions

1. Add `FlattenedAtom` class definition to @[c:\src\quorum\backend_v2\models\dtos\engine.py] **above** the `EngineExecutionRequest` class.
2. The model MUST use:
   - `ConfigDict(strict=True, frozen=True, extra="ignore")` — `duck_typing_token_shield_exception` applies: FlattenedAtom is an Internal Data Projection Model deserializing from hook `state_delta` which may contain transient metadata keys.
   - PEP 593 `Annotated` syntax for ALL fields per `pydantic_annotated_fields_mandate`.
   - Import `Annotated` from `typing`.
3. Fields (exact contract — no semantic drift):
   - `atom_id: Annotated[str, Field(description="Opaque hashed ID for the extracted atom.")]`
   - `question: Annotated[str, Field(description="The text content evaluated blindly.")]`
   - `extraction_rule: Annotated[str, Field(default="", description="The specific validation rule.")] = ""`
   - `anchor_target: Annotated[str, Field(default="", description="Semantic bounding box target.")] = ""`
   - `is_inverse: Annotated[bool, Field(default=False, description="True if this is an inverse assertion.")] = False`

### Invariants
- `pydantic_annotated_fields_mandate`: All fields use PEP 593 Annotated syntax.
- `duck_typing_token_shield_exception`: `extra="ignore"` is justified — Internal Data Projection Model.
- `frozen_state_mutability`: `frozen=True` enforces immutability.

### FORBIDDEN
- Raw dict state passing
- `asyncio.gather`
- `try/except Exception` catch-all
- Bare `Field()` assignments without `Annotated` wrapper

---

## Step 1.2: Add `shuffled_atoms` to `EngineExecutionRequest`

### Scope
- **TARGET (Modify):** @[c:\src\quorum\backend_v2\models\dtos\engine.py]

### Actions

1. Add the `shuffled_atoms` field to `EngineExecutionRequest`:
   ```python
   shuffled_atoms: Annotated[list[FlattenedAtom] | None, Field(default=None, description="Predefined matrix assertions for TDA evaluation.")] = None
   ```
2. Update the class docstring `Attributes:` section to include `shuffled_atoms`.

### Invariants
- `pydantic_annotated_fields_mandate`: Must use `Annotated` syntax.
- The field is `None` by default (Regular TDA path does not use it).
- `extra="forbid"` on `EngineExecutionRequest` is preserved (no change).

---

## Step 1.3: Update `atom_flattening.py` import

### Scope
- **TARGET (Modify):** @[c:\src\quorum\backend_v2\hooks\atom_flattening.py]
- **CONTEXT (Read-Only):** @[c:\src\quorum\backend_v2\models\dtos\engine.py]

### Actions

1. Remove the `FlattenedAtom` class definition (lines 21–38 in the current file).
2. Add import: `from backend_v2.models.dtos.engine import FlattenedAtom`
3. Verify that `FlatteningHookOutput` still references `FlattenedAtom` correctly via the import.
4. The `pydantic` import of `BaseModel`, `ConfigDict`, `Field` can be reduced to only what `FlatteningHookOutput` and the hook function still need.

### Invariants
- Dependency direction: Hooks → Models (correct layer flow).
- No circular imports — `engine.py` does NOT import from `hooks/`.
- `FlatteningHookOutput` continues to use `list[FlattenedAtom]` type reference.

### FORBIDDEN
- Local `FlattenedAtom` class definition remaining in `atom_flattening.py`
- Inline imports inside functions

---

## Testing & Quality Gate Plan

### Unit Tests
All tests in @[c:\src\quorum\backend_v2\tests\unit\hooks\test_atom_flattening.py] MUST continue to pass. The `FlattenedAtom` import path changes, so any test importing directly from `atom_flattening` must be updated to import from `engine.py`.

New tests for the `FlattenedAtom` DTO MUST be written in its isolated test file: @[c:\src\quorum\backend_v2\tests\unit\models\dtos\test_engine.py].

### Positive Scenarios
1. **`test_engine.py`**: Verify `FlattenedAtom` can be instantiated with valid data and that `EngineExecutionRequest` accepts `shuffled_atoms`.
2. **`test_atom_flattening.py`**: Verify the hook still produces the correct output via `FlatteningHookOutput` using the imported DTO.

### Negative Scenarios (Minimum 2 - added to `test_engine.py`)
1. **Missing required fields:** Instantiating `FlattenedAtom` without `atom_id` or `question` MUST trigger `ValidationError`.
2. **Invalid types:** Passing `int` for `question` field MUST trigger `ValidationError` due to `strict=True`.

### Audit Commands

```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/engine.py --test
uv run python scripts/backend_audit_loop.py backend_v2/hooks/atom_flattening.py --test
```

### Atomic Commit

After passing audit, commit:
```powershell
git add backend_v2/models/dtos/engine.py backend_v2/hooks/atom_flattening.py
git commit -m "refactor: move FlattenedAtom to DTO layer and add shuffled_atoms to EngineExecutionRequest"
```
