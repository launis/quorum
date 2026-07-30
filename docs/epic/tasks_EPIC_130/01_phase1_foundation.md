# Phase 1: Foundation — New Directory Structure, Typed Protocol & AdapterContext DTO

This plan sets up the foundation for the Blueprint Transformer Decomposition by creating the `backend_v2/services/sdui/adapters/` directory and defining the `AdapterContext` DTO and `SduiAdapterProtocol` in `base_adapter.py`. It also updates `blueprint.py`'s `_target_block_hydrators` dispatch table to enforce typed dispatch.

Target Files:
- @[c:\src\quorum\backend_v2\services\sdui\__init__.py]
- @[c:\src\quorum\backend_v2\services\sdui\adapters\__init__.py]
- @[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py]
- @[c:\src\quorum\backend_v2\services\blueprint.py#L98-L101]
- @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_base_adapter.py]

```xml
<execution_protocol level="2_execute">
  <constraint invariant="frozen_state_mutability" />
  <constraint invariant="strict_pydantic_v2_rust" />
  
  <step id="1.1" name="CREATE DIRECTORY STRUCTURE">
    <action>Create empty `__init__.py` files to define the package structure.</action>
    <target>@[c:\src\quorum\backend_v2\services\sdui\__init__.py]</target>
    <target>@[c:\src\quorum\backend_v2\services\sdui\adapters\__init__.py]</target>
  </step>
  
  <step id="1.2" name="CREATE BASE ADAPTER PROTOCOL">
    <action>Create `base_adapter.py` defining `AdapterContext` and `SduiAdapterProtocol`.</action>
    <target>@[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py]</target>
    <instructions>
      1. Import specifically and exhaustively: `ExecutionRecord`, `MCPAuditTrace`, `OutputProfile`, `EmbeddedOutputProfile` from `backend_v2.models.v2_core`, and `AnySduiBlock` from `backend_v2.models.view.sdui`. Also import `typing.Protocol`, `pydantic.ConfigDict`, and `pydantic.BaseModel`.
      2. Define `AdapterContext` as a Pydantic `BaseModel` with `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")`.
      3. Fields for `AdapterContext`: `execution: ExecutionRecord`, `locale: str`, `penalties_applied: list[str]`, `mcp_audit_data: list[MCPAuditTrace]`, `global_score: float | None`, `accumulated_extensions: dict[str, list[dict[str, str]]]`, `profile: OutputProfile | EmbeddedOutputProfile`.
      4. Define `SduiAdapterProtocol` as a `typing.Protocol` with `@staticmethod build(context: AdapterContext) -> list[AnySduiBlock]`.
    </instructions>
  </step>
  
  <step id="1.3" name="UPDATE BLUEPRINT ORCHESTRATOR DISPATCH TABLE">
    <action>Update the typing of `_target_block_hydrators` in `blueprint.py`.</action>
    <target>@[c:\src\quorum\backend_v2\services\blueprint.py]</target>
    <demolish>REMOVE: `self._target_block_hydrators: dict[str, Callable[..., list[AnySduiBlock]]] = {` REPLACE WITH: `self._target_block_hydrators: dict[str, type[SduiAdapterProtocol] | Callable[..., list[AnySduiBlock]]] = {`</demolish>
    <instructions>
      1. Import `SduiAdapterProtocol` from `backend_v2.services.sdui.adapters.base_adapter`.
      2. Update the type hint for the `_target_block_hydrators` dictionary in `__init__` to explicitly allow both the new Protocol AND the legacy Callable during the transition phase. Do not delete the existing Callables from the dictionary values.
    </instructions>
  </step>

  <step id="1.4" name="TEST NEGATIVE ADAPTER CONTEXT VALIDATION">
    <action>Create strict unit tests to verify frozen mutability and forbid_extra constraints on AdapterContext.</action>
    <target>@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_base_adapter.py]</target>
    <instructions>
      1. Ensure standard polyfactory or explicit mocked fixtures are used to create valid inputs.
      2. Write positive test: AdapterContext instantiates successfully with valid data.
      3. Write negative test: Trigger `ValidationError` (using `pytest.raises`) by passing an unrecognized key (e.g., `invalid_key="test"`), proving `extra="forbid"` works.
      4. Write negative test: Trigger `ValidationError` by attempting to mutate a field after instantiation, proving `frozen=True` works.
    </instructions>
  </step>
</execution_protocol>
```
