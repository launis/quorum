# Phase 2: Extract XAI Highlights Adapter (Proof of Concept)

This plan extracts the logic for building the XAI Highlights block from `blueprint.py` into a new, self-contained `xai_highlights_adapter.py` file, testing it independently.

Target Files:
- @[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py]
- @[c:\src\quorum\backend_v2\services\blueprint.py#L781-L859]
- @[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]
- @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_xai_highlights_adapter.py]

```xml
<execution_protocol level="2_execute">
  <constraint invariant="the_duct_tape_ban" />
  <constraint invariant="inline_imports_ban" />
  <constraint invariant="rfc7807_dual_reporting_mandate" />
  <constraint invariant="anti_ambiguity_mandate" />
  <constraint invariant="anti_happy_path_mandate" />
  
  <step id="2.1" name="CREATE XAI HIGHLIGHTS ADAPTER">
    <action>Create the new XAI Highlights Adapter and extract presentation rules.</action>
    <target>@[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py]</target>
    <instructions>
      1. Explicitly import: `XaiExtensionType`, `LaxXaiExtensionType`, `VisualIntent`, `ErrorCodes` from `backend_v2.models.enums`. Import `AccordionBlock`, `AlertBlock`, `AnySduiBlock` from `backend_v2.models.view.sdui`. Import `AppException` from `backend_v2.models.v2_core`. Import `SduiAdapterProtocol`, `AdapterContext` from `.base_adapter`. Import `logging`.
      2. Define a module-level dictionary `XAI_AESTHETICS_RULES: dict[XaiExtensionType | LaxXaiExtensionType, dict[str, Any]]` containing mapping for severity and icon_name.
      3. Lookups MUST use explicit dictionary key access `XAI_AESTHETICS_RULES[extension_type]`. Fallbacks via `.get()` are FORBIDDEN.
      4. Implement `XaiHighlightsAdapter` class conforming to `SduiAdapterProtocol`.
      5. Implement the `build(context: AdapterContext) -> list[AnySduiBlock]` method.
      6. The `except Exception:` block from `blueprint.py` MUST be replaced with `except ValueError`. Inside the except block, you MUST first log the failure with `logger.error` (RFC7807), then raise `AppException(ErrorCodes.VALIDATION_FAILED)`.
      7. Construct `AccordionBlock` and `AlertBlock` replacing string severities with `VisualIntent` enum values.
    </instructions>
  </step>
  
  <step id="2.2" name="REPLACE INLINE LOGIC IN BLUEPRINT">
    <action>Remove the inline `_hydrate_grouped_extensions_block` from `blueprint.py`.</action>
    <target>@[c:\src\quorum\backend_v2\services\blueprint.py]</target>
    <demolish>REMOVE: `def _hydrate_grouped_extensions_block` and its entire 80-line body. REPLACE WITH: Routing this block type to `XaiHighlightsAdapter` in `_target_block_hydrators`.</demolish>
    <instructions>
      1. Map the `TargetBlockType` (or corresponding key) in `_target_block_hydrators` to `XaiHighlightsAdapter`.
      2. Ensure the orchestrator calls `XaiHighlightsAdapter.build(context)` passing the newly constructed `AdapterContext` instead of 15 raw arguments.
    </instructions>
  </step>
  
  <step id="2.3" name="ATOMIC TEST MIGRATION">
    <action>Migrate and create tests for XaiHighlightsAdapter.</action>
    <target>@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_xai_highlights_adapter.py]</target>
    <target>@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]</target>
    <instructions>
      1. Create `test_xai_highlights_adapter.py` to independently test aesthetic rule lookups and block generation using mocked `AdapterContext`.
      2. MUST include a Negative Test: pass an invalid `extension_type` string that fails `XaiExtensionType()` coercion, and assert it raises `AppException` with `ErrorCodes.VALIDATION_FAILED`.
      3. MUST include a Negative Test: pass an unknown key to `XAI_AESTHETICS_RULES` and assert it raises a native `KeyError` (proving `.get()` is not used).
      4. Ensure `test_blueprint.py` assertions point to the new adapter or use proper mocks for `XaiHighlightsAdapter.build`.
    </instructions>
  </step>
</execution_protocol>
```
