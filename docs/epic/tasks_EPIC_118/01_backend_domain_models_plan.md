# Phase 1: Backend Domain Models & Service Engine Hardening

**Goal**: Move `FlattenedAtom` model definition into the DTO layer to enforce the No Naked Dicts rule, and update `EngineExecutionRequest` to accept `shuffled_atoms`.

**Target Files**:
- @[c:\src\quorum\backend_v2\models\dtos\engine.py] (Modify)
- @[c:\src\quorum\backend_v2\hooks\atom_flattening.py] (Modify)

**Destructive Operation Inventory**:
- `FlattenedAtom` is moved from `atom_flattening.py` to `engine.py`. No other files depend on it currently.

```xml
<execution_protocol level="2_execute">
  <constraint invariant="pydantic_annotated_fields_mandate">All fields must use PEP 593 Annotated syntax.</constraint>
  <constraint invariant="the_duct_tape_ban">No duck-typing or exceptions eating.</constraint>
  <constraint invariant="duck_typing_token_shield_exception">FlattenedAtom is an Internal Data Projection Model, extra="ignore" is permitted.</constraint>
  <constraint invariant="universal_quality_gate">Run backend audit loop.</constraint>
  <constraint invariant="atomic_checkpoint_mandate">Atomic commits required.</constraint>
  <constraint invariant="english_language_mandate">All variables and docstrings must be in English.</constraint>
  
  <step id="1" name="FlattenedAtom DTO Migration">
    <action>Move `FlattenedAtom` model definition into the DTO layer (`engine.py`).</action>
    <target>@[c:\src\quorum\backend_v2\models\dtos\engine.py]</target>
    <instruction>
      - Move the `FlattenedAtom` class definition here from `atom_flattening.py`.
      - Use `ConfigDict(strict=True, frozen=True, extra="ignore")`.
      - Use PEP 593 Annotated syntax for all fields.
      - Add `shuffled_atoms: Annotated[list[FlattenedAtom] | None, Field(default=None, description="Predefined matrix assertions for TDA evaluation.")] = None` to the existing `EngineExecutionRequest` class.
    </instruction>
  </step>
  
  <step id="2" name="FlattenedAtom Hook Refactor">
    <action>Remove `FlattenedAtom` definition and import it from the DTO layer.</action>
    <target>@[c:\src\quorum\backend_v2\hooks\atom_flattening.py]</target>
    <instruction>
      - Remove the `FlattenedAtom` definition.
      - Add `from backend_v2.models.dtos.engine import FlattenedAtom`.
    </instruction>
  </step>
  
  <step id="3" name="Testing &amp; Quality Gate Plan">
    <action>Run the backend audit loop.</action>
    <instruction>
      - Run `uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/models/dtos/engine.py --test`
      - Run `uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/hooks/atom_flattening.py --test`
      - Verify that missing required fields trigger ValidationError/AppException, and invalid types trigger ValidationError in unit tests.
    </instruction>
  </step>
</execution_protocol>
```
