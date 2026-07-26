# EPIC 118 - Phase 1: Backend Domain Models & Service Engine Hardening

## Overview
This plan implements Phase 1 of EPIC 118. It involves moving the `FlattenedAtom` model into the DTO layer to enforce the No Naked Dicts rule and decoupling the model from the hook.

## Target Files
- `@[c:\src\quorum\backend_v2\models\dtos\engine.py]`
- `@[c:\src\quorum\backend_v2\hooks\atom_flattening.py]`

## Execution Protocol

```xml
<execution_protocol>
    <step id="phase_1.1" name="Move FlattenedAtom to DTO Layer">
        <action>Move `FlattenedAtom` model definition into the DTO layer to strictly enforce the **No Naked Dicts** rule without creating an architectural layer violation (Models importing from Hooks) or a Circular Import. FlattenedAtom MUST use PEP 593 `Annotated` syntax for all fields per `pydantic_annotated_fields_mandate`. Add `shuffled_atoms` to `EngineExecutionRequest`.</action>
        <target>@[c:\src\quorum\backend_v2\models\dtos\engine.py]</target>
        <constraint invariant="duck_typing_token_shield_exception">Strict Pydantic V2 typing with ConfigDict(strict=True, frozen=True, extra='ignore') — duck_typing_token_shield_exception applies: FlattenedAtom is an Internal Data Projection Model deserializing from hook state_delta which may contain transient metadata keys.</constraint>
        <constraint invariant="pydantic_annotated_fields_mandate">All fields use PEP 593 Annotated syntax per pydantic_annotated_fields_mandate.</constraint>
        <tests>Verify engine.py compiles. Verify missing required fields trigger ValidationError.</tests>
        <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/models/dtos/engine.py --test</audit_command>
    </step>
    
    <step id="phase_1.2" name="Update atom_flattening.py imports">
        <action>Remove the `FlattenedAtom` definition and instead import it from the DTO layer.</action>
        <target>@[c:\src\quorum\backend_v2\hooks\atom_flattening.py]</target>
        <constraint>Import FlattenedAtom from backend_v2.models.dtos.engine (dependency direction: Hooks → Models).</constraint>
        <constraint>Forbidden: Raw dict state passing, asyncio.gather, try/except Exception catch-all, local FlattenedAtom class definition.</constraint>
        <tests>Verify atom_flattening.py compiles and integrates correctly.</tests>
        <audit_command>uv run python scripts/backend_audit_loop.py c:/src/quorum/backend_v2/hooks/atom_flattening.py --test</audit_command>
    </step>

    <step id="phase_1_checkpoint" name="Integration Checkpoint">
        <action>Run the full backend audit loop for all modified files to verify compilation and >90% test coverage.</action>
        <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/models/dtos backend_v2/hooks --test</audit_command>
    </step>
</execution_protocol>
```
