# Phase 2: Extract XAI Highlights Adapter (Proof of Concept)

**Overview:** Create the first concrete adapter (`XaiHighlightsAdapter`) that extracts the `_hydrate_grouped_extensions_block` method from `blueprint.py` into a self-contained adapter file following the canonical KI template. Wire it into the dispatch table. Migrate all related tests from `test_blueprint.py` into a dedicated test file and add mandatory negative tests.

**Source:** @[c:\src\quorum\docs\epic\EPIC_130_blueprint_decomposition.md#L104-L112] Phase 2

**Target Files:**
- @[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py] [NEW]
- @[c:\src\quorum\backend_v2\services\blueprint.py] [MODIFY]
- @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_xai_highlights_adapter.py] [NEW]
- @[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py] [MODIFY — migrate XAI-related tests OUT]

**Context Files (READ-ONLY):**
- @[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py] (AdapterContext — created in Phase 1)
- @[c:\src\quorum\backend_v2\models\enums.py#L117-L155] (VisualIntent, XaiExtensionType)
- @[c:\src\quorum\backend_v2\models\view\sdui.py] (AccordionBlock, AlertBlock, AnySduiBlock)
- KI: `sdui_adapter_decomposition` (specifically `ki_sdui_adapter_pattern.md`)

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 1 was completed successfully. Confirm:
      1. @[c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py] exists and contains `class AdapterContext(BaseModel)` with `ConfigDict(frozen=True, strict=True, extra="forbid")`.
      2. The dispatch table in @[c:\src\quorum\backend_v2\services\blueprint.py] uses `Callable[[AdapterContext], list[AnySduiBlock]]`.
      3. The call site constructs AdapterContext and passes it as a single argument.
    </action>
    <action>Look forward: Verify that `_hydrate_grouped_extensions_block` still exists at @[c:\src\quorum\backend_v2\services\blueprint.py#L829-L841] and still uses `**kwargs: Any` signature (or the lambda bridge from Phase 1). If the method has already been extracted, STOP.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[c:\src\quorum\docs\epic\EPIC_130_blueprint_decomposition.md]) and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    <item>xai_highlights_adapter.py follows the EXACT two-section structure from KI sdui_adapter_decomposition</item>
    <item>The adapter uses strict dictionary key access (XAI_AESTHETICS_RULES[key]) — zero .get() fallbacks</item>
    <item>All imports are at the top of the file — zero inline imports</item>
    <item>The adapter uses VisualIntent enum values — zero bare string severity literals</item>
    <item>Zero bare except Exception: catch-alls</item>
    <item>The word "Epic" does NOT appear in any added code</item>
    <item>blueprint.py no longer contains _hydrate_grouped_extensions_block</item>
    <item>All tests that previously tested _hydrate_grouped_extensions_block are migrated to test_xai_highlights_adapter.py</item>
    <item>Negative tests assert AppException on unknown extension and KeyError on unmapped aesthetic key</item>
  </dod_checklist>

  <anti_targets>
    <file>c:\src\quorum\backend_v2\models\view\sdui.py — Do NOT modify SDUI block models</file>
    <file>c:\src\quorum\backend_v2\models\enums.py — Do NOT modify enums</file>
    <file>c:\src\quorum\backend_v2\services\sdui\adapters\base_adapter.py — Do NOT modify AdapterContext (already created in Phase 1)</file>
    <method>_hydrate_penalties_block — Adapter extraction is Phase 3</method>
    <method>_hydrate_printable_sources_block — Adapter extraction is Phase 5</method>
    <method>_extract_matrices_and_extensions — God Method decomposition is Phase 6</method>
    <method>Executive summary inline logic — Phase 4</method>
  </anti_targets>

  <step id="1" name="READ KNOWLEDGE ITEM">
    <action>Use view_file to read the canonical KI at C:\Users\risto\.gemini\antigravity-ide\knowledge\sdui_adapter_decomposition\artifacts\ki_sdui_adapter_pattern.md BEFORE writing any code.</action>
    <constraint invariant="knowledge_item_preflight">The executing agent MUST load the KI's canonical reference template, locked terminology, and forbidden anti-patterns before creating the adapter file.</constraint>
  </step>

  <step id="2" name="CREATE xai_highlights_adapter.py">
    <action>Create @[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py] following the EXACT two-section structure from KI `sdui_adapter_decomposition`.</action>
    <action>**SECTION 1 — AESTHETICS RULES**: Define `XAI_AESTHETICS_RULES` as a module-level dictionary. This dictionary is NOT a complex mapping — the current `_hydrate_grouped_extensions_block` at @[c:\src\quorum\backend_v2\services\blueprint.py#L829-L841] simply iterates over `accumulated_extensions.values()` and extends blocks. The aesthetic rules for severity are actually defined within the `_add_ext` closure at @[c:\src\quorum\backend_v2\services\blueprint.py#L714-L722] (which belongs to Phase 6). For Phase 2, the adapter is a simple pass-through that collects pre-built blocks. The `XAI_AESTHETICS_RULES` dictionary in this phase is a minimal placeholder mapping that will be fully populated in Phase 6 when `_add_ext` is decomposed:
```python
XAI_AESTHETICS_RULES: dict[str, dict[str, str | VisualIntent]] = {
    # NOTE: Full aesthetic rule mapping for severity/icon is populated in Phase 6
    # when the _add_ext closure is extracted from the God Method.
    # This Phase 2 adapter simply flattens pre-built AccordionBlock lists
    # from accumulated_extensions.
}
```
    </action>
    <action>**SECTION 2 — ADAPTER CLASS**: Define `XaiHighlightsAdapter` with a single `@staticmethod build(context: AdapterContext) -> list[AnySduiBlock]` method. The method:
      1. Reads `context.accumulated_extensions` (type: `dict[str, list[AnySduiBlock]]`)
      2. If empty, returns `[]`
      3. Iterates over all values and extends them into a flat `blocks` list
      4. Returns `blocks`
    This is a direct 1:1 extraction of the logic at @[c:\src\quorum\backend_v2\services\blueprint.py#L829-L841].
    </action>
    <action>Top-level imports (ALL at module level):
      - `import logging`
      - `from backend_v2.models.enums import VisualIntent`
      - `from backend_v2.models.view.sdui import AnySduiBlock`
      - `from backend_v2.services.sdui.adapters.base_adapter import AdapterContext`
    </action>
    <contract_freeze>
      class XaiHighlightsAdapter:
          @staticmethod
          def build(context: AdapterContext) -> list[AnySduiBlock]
    </contract_freeze>
    <constraint invariant="adapter_locked_terminology">Method name MUST be `build`, parameter name MUST be `context`, type MUST be `AdapterContext`, return type MUST be `list[AnySduiBlock]`.</constraint>
    <constraint invariant="adapter_fail_fast_dictionary_access">All aesthetic rule lookups MUST use strict `RULES[key]` access — no .get() fallbacks.</constraint>
  </step>

  <step id="3" name="MODIFY blueprint.py — DELETE _hydrate_grouped_extensions_block AND WIRE ADAPTER">
    <action>In @[c:\src\quorum\backend_v2\services\blueprint.py]:
      1. Add import at the top: `from backend_v2.services.sdui.adapters.xai_highlights_adapter import XaiHighlightsAdapter`
      2. In the dispatch table in `__init__`, replace the lambda for GROUPED_EXTENSIONS_BLOCK:
         FROM: `lambda ctx: self._hydrate_grouped_extensions_block(accumulated_extensions=ctx.accumulated_extensions,)`
         TO: `lambda ctx: XaiHighlightsAdapter.build(ctx)`
      3. DELETE the entire `_hydrate_grouped_extensions_block` method (approximately @[c:\src\quorum\backend_v2\services\blueprint.py#L829-L841]).
    </action>
    <demolish>REMOVE: The entire `_hydrate_grouped_extensions_block` method at @[c:\src\quorum\backend_v2\services\blueprint.py#L829-L841]:
```python
def _hydrate_grouped_extensions_block(self, **kwargs: Any) -> list[AnySduiBlock]:
    """Hydrates XAI extensions into grouped AccordionBlock elements."""
    accumulated_extensions = kwargs.get("accumulated_extensions", {})
    if not accumulated_extensions:
        return []
    blocks: list[AnySduiBlock] = []
    for ext_blocks in accumulated_extensions.values():
        blocks.extend(ext_blocks)
    return blocks
```
REPLACE WITH: XaiHighlightsAdapter.build(ctx) dispatch via lambda in the _target_block_hydrators dictionary.
    </demolish>
  </step>

  <step id="4" name="MIGRATE TESTS AND ADD NEGATIVE TESTS">
    <action>Search @[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py] for any tests that specifically test `_hydrate_grouped_extensions_block`. Use grep_search to find them. If found, PHYSICALLY MOVE them (not copy) to @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_xai_highlights_adapter.py]. Update the test imports to call `XaiHighlightsAdapter.build(context)` directly instead of the private method.</action>
    <action>Create @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_xai_highlights_adapter.py] with the migrated tests plus the following mandatory new tests:</action>
    <test_contracts>
      <test name="test_build_empty_extensions_returns_empty_list" category="boundary">
        <input>AdapterContext(accumulated_extensions={})</input>
        <expected>returns []</expected>
      </test>
      <test name="test_build_single_extension_group_returns_blocks" category="positive">
        <input>AdapterContext(accumulated_extensions={"global_extensions": [AccordionBlock(title="Risk Flags", severity="error", icon_name=None, children=[AlertBlock(severity="info", text="test", exact_quotes=[], citations=[])])]})</input>
        <expected>returns list containing the AccordionBlock</expected>
      </test>
      <test name="test_build_multiple_extension_groups_flattens_all" category="positive">
        <input>AdapterContext(accumulated_extensions={"group_a": [block1], "group_b": [block2, block3]})</input>
        <expected>returns [block1, block2, block3] — all groups flattened in order</expected>
      </test>
      <test name="test_build_does_not_mutate_context" category="negative">
        <input>Call build(ctx) and verify ctx.accumulated_extensions is unchanged after the call</input>
        <expected>context remains frozen — no mutation side effects</expected>
      </test>
      <test name="test_build_none_extensions_value_raises" category="error_path">
        <input>Attempt to construct AdapterContext with accumulated_extensions=None</input>
        <expected>raises ValidationError (accumulated_extensions is not Optional)</expected>
      </test>
    </test_contracts>
  </step>

  <step id="5" name="RUN QUALITY GATE">
    <action>Run: uv run python scripts/backend_audit_loop.py backend_v2/services/sdui --test</action>
    <action>Run: uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/sdui --test</action>
    <action>Run: uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test</action>
    <action>Verify: MyPy strict passes with zero new # type: ignore annotations.</action>
    <action>Verify: All existing blueprint tests still pass — no regressions.</action>
    <action>Verify: grep_search for "_hydrate_grouped_extensions_block" in blueprint.py returns ZERO results.</action>
  </step>

  <validation_gate>
    <check>grep_search for "_hydrate_grouped_extensions_block" in @[c:\src\quorum\backend_v2\services\blueprint.py] — MUST return zero results (method deleted)</check>
    <check>grep_search for "class XaiHighlightsAdapter" in @[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py] — confirms adapter exists</check>
    <check>grep_search for "XaiHighlightsAdapter.build" in @[c:\src\quorum\backend_v2\services\blueprint.py] — confirms wiring</check>
    <check>grep_search for ".get(" in @[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py] — MUST return zero results</check>
    <check>grep_search for "except Exception" in @[c:\src\quorum\backend_v2\services\sdui\adapters\xai_highlights_adapter.py] — MUST return zero results</check>
    <check>Run: uv run python scripts/backend_audit_loop.py backend_v2 --test</check>
  </validation_gate>
</execution_protocol>
```
