# Phase 1: Backend Domain Models & Service Engine Hardening

Overview: Move `FlattenedAtom` to DTO layer and enforce strictly Pydantic V2 schemas.

```xml
<execution_protocol>
<execution_block phase="phase_1" consumer="tier2-execute">
  <summary><![CDATA[Backend Domain Models & Service Engine Hardening]]></summary>
  <step id="phase_1.1" scope="MODIFY">
    <action>Move `FlattenedAtom` model definition into the DTO layer to strictly enforce the No Naked Dicts rule without creating an architectural layer violation (Models importing from Hooks) or a Circular Import. FlattenedAtom MUST use PEP 593 Annotated syntax for all fields per pydantic_annotated_fields_mandate (ensure `from typing import Annotated` is imported). Create/update the corresponding unit test file.</action>
    <target>@[c:\src\quorum\backend_v2\models\dtos\engine.py]</target>
    <target>@[c:\src\quorum\backend_v2\tests\unit\models\dtos\test_engine.py]</target>
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
    <action>Remove the `FlattenedAtom` definition and instead import it from the DTO layer. You MUST also update the imports in `test_atom_flattening.py` so that it imports `FlattenedAtom` from the new DTO location, otherwise the unit tests will instantly crash.</action>
    <target>@[c:\src\quorum\backend_v2\hooks\atom_flattening.py]</target>
    <target>@[c:\src\quorum\backend_v2\tests\unit\hooks\test_atom_flattening.py]</target>
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
</execution_block>
</execution_protocol>
```
