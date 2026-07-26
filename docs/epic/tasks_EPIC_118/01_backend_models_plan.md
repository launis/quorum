# 01 Backend Models Plan

Source: Epic Phase 1, Step 1 & 2

## Target Files (Modify)
- `@[c:\src\quorum\backend_v2\models\dtos\engine.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\models\dtos\test_engine.py]`
- `@[c:\src\quorum\backend_v2\hooks\atom_flattening.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\hooks\test_atom_flattening.py]`

## Execution Instructions

```xml
<execution_protocol>
  <execution_block phase="phase_1" consumer="tier2-execute">
    <summary><![CDATA[Backend Domain Models & Service Engine Hardening]]></summary>
    <step id="phase_1.1" scope="MODIFY">
      <action>Move `FlattenedAtom` model definition into the DTO layer to strictly enforce the **No Naked Dicts** rule without creating an architectural layer violation (Models importing from Hooks) or a Circular Import. FlattenedAtom MUST use PEP 593 `Annotated` syntax for all fields (ensure `from typing import Annotated` is imported). Create/update the corresponding unit test file.</action>
      <target>@[c:\src\quorum\backend_v2\models\dtos\engine.py]</target>
      <invariants>
        <constraint invariant="pydantic_annotated_fields_mandate">ALWAYS use PEP 593 Annotated syntax to separate pure Python types from Pydantic runtime metadata</constraint>
        <constraint invariant="no_naked_dicts_in_state">ALWAYS intercept raw datastreams with .model_validate() immediately at the boundary</constraint>
        <constraint invariant="duck_typing_token_shield_exception">The extra="ignore" configuration in Pydantic is STRICTLY PROHIBITED at all times, with the absolute exception of SynthesisStepDataDTO, Token Shield classes, and internal Data Projection Models.</constraint>
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
      <invariants>
        <constraint invariant="strict_dependency_injection">Import FlattenedAtom from backend_v2.models.dtos.engine (dependency direction: Hooks → Models)</constraint>
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
