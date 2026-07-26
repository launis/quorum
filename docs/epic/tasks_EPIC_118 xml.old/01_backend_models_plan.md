# Phase 1: Backend Domain Models & Service Engine Hardening

## Overview
Move `FlattenedAtom` into the DTO layer to strictly enforce the No Naked Dicts rule without creating an architectural layer violation.

## Target Files
- `@[c:\src\quorum\backend_v2\models\dtos\engine.py]`
- `@[c:\src\quorum\backend_v2\hooks\atom_flattening.py]`

```xml
<execution_protocol level="2_execute">
  <context_rules>
    <constraint invariant="pydantic_annotated_fields_mandate">ALWAYS use PEP 593 Annotated syntax for Pydantic fields.</constraint>
    <constraint invariant="duck_typing_token_shield_exception">extra="ignore" is permitted for FlattenedAtom as it is an Internal Data Projection Model.</constraint>
    <constraint invariant="universal_fail_fast">Enforce "Fail-Fast" at every boundary.</constraint>
  </context_rules>
  
  <step id="phase_1.1" scope="MODIFY">
    <action>Move `FlattenedAtom` model definition into the DTO layer to strictly enforce the **No Naked Dicts** rule without creating an architectural layer violation (Models importing from Hooks) or a Circular Import. FlattenedAtom MUST use PEP 593 `Annotated` syntax for all fields per `pydantic_annotated_fields_mandate`.</action>
    <target>@[c:\src\quorum\backend_v2\models\dtos\engine.py]</target>
    <invariants>
      <must>Strict Pydantic V2 typing with ConfigDict(strict=True, frozen=True, extra='ignore') — duck_typing_token_shield_exception applies: FlattenedAtom is an Internal Data Projection Model deserializing from hook state_delta which may contain transient metadata keys.</must>
      <must>All fields use PEP 593 Annotated syntax per pydantic_annotated_fields_mandate.</must>
      <forbidden>Raw dict state passing, asyncio.gather, try/except Exception catch-all, bare Field() assignments without Annotated wrapper</forbidden>
    </invariants>
    <tests min_negative="2">
      <positive>Verify engine.py compiles and integrates correctly</positive>
      <negative>Verify missing required fields trigger ValidationError/AppException</negative>
      <negative>Verify invalid types trigger Pydantic ValidationError</negative>
    </tests>
    <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/models/dtos/engine.py --test</audit_command>
  </step>
  
  <step id="phase_1.2" scope="MODIFY">
    <action>Remove the `FlattenedAtom` definition and instead import it from the DTO layer.</action>
    <target>@[c:\src\quorum\backend_v2\hooks\atom_flattening.py]</target>
    <invariants>
      <must>Import FlattenedAtom from backend_v2.models.dtos.engine (dependency direction: Hooks → Models)</must>
      <forbidden>Raw dict state passing, asyncio.gather, try/except Exception catch-all, local FlattenedAtom class definition</forbidden>
    </invariants>
    <tests min_negative="2">
      <positive>Verify atom_flattening.py compiles and integrates correctly</positive>
      <negative>Verify missing required fields trigger ValidationError/AppException</negative>
      <negative>Verify invalid types trigger Pydantic ValidationError</negative>
    </tests>
    <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/hooks/atom_flattening.py --test</audit_command>
  </step>

  <step id="testing" scope="VERIFY">
    <action>Run backend audit loop on modified files.</action>
    <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/models/dtos/engine.py c:/src/quorum/backend_v2/hooks/atom_flattening.py --test</audit_command>
  </step>
</execution_protocol>
```
