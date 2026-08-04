# Phase 5: Extract Printable Sources Adapter

**Overview:** Extract `_hydrate_printable_sources_block` from `blueprint.py` into a self-contained `PrintableSourcesAdapter` following the canonical KI template.

**Source:** @[c:\src\quorum\docs\epic\EPIC_130_blueprint_decomposition.md#L137-L145] Phase 5

**Target Files:** 
- @[c:\src\quorum\backend_v2\services\sdui\adapters\printable_sources_adapter.py] [NEW]
- @[c:\src\quorum\backend_v2\services\blueprint.py] [MODIFY]
- @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_printable_sources_adapter.py] [NEW]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify Phase 4 (ExecutiveSummaryAdapter) completed successfully and `blueprint.py` still contains `_hydrate_printable_sources_block`.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true. (Specifically ensuring `AdapterContext` has `profile_cache` attribute).</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    <item>Create `PrintableSourcesAdapter` implementing the two-section canonical structure.</item>
    <item>Remove `_hydrate_printable_sources_block` from `blueprint.py`.</item>
    <item>Wire `PrintableSourcesAdapter.build(ctx)` into the blueprint dispatch table.</item>
    <item>Add positive and negative unit tests achieving 100% coverage of the adapter.</item>
  </dod_checklist>

  <anti_targets>
    <target>backend_v2/models/view/sdui.py (Do not modify SDUI view models)</target>
    <target>client_app_v2/ (Frontend UI must not be touched)</target>
    <target>Phase 5a placeholders (_hydrate_global_score_block, _hydrate_audit_trail_block, _hydrate_jargon_ratio_block) at @[c:\src\quorum\backend_v2\services\blueprint.py#L802-L812] MUST NOT be deleted yet.</target>
  </anti_targets>

  <constraint invariant="knowledge_item_preflight">
    You MUST read the KI artifact `ki_sdui_adapter_pattern.md` located in `C:\Users\risto\.gemini\antigravity-ide\knowledge\sdui_adapter_decomposition\artifacts\` BEFORE writing the adapter code.
  </constraint>
  <constraint invariant="adapter_two_section_structure">
    The adapter file MUST have exactly two sections: SECTION 1 (AESTHETICS RULES) and SECTION 2 (ADAPTER CLASS). Even if no aesthetic rules are required, you must declare an empty `PRINTABLE_SOURCES_RULES: dict[str, typing.Any] = {}` to conform structurally.
  </constraint>
  <constraint invariant="adapter_direct_data_access">
    Adapter MUST read `context.profile_cache` directly without using `.get()` fallback methods.
  </constraint>

  <step id="1" name="Create PrintableSourcesAdapter">
    <action>Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\printable_sources_adapter.py]` [NEW].</action>
    <action>Implement SECTION 1: `PRINTABLE_SOURCES_RULES = {}`.</action>
    <action>Implement SECTION 2: `PrintableSourcesAdapter` with `@staticmethod def build(context: AdapterContext) -> list[AnySduiBlock]:`.</action>
    <action>Extract the logic from `_hydrate_printable_sources_block`. If `context.profile_cache` is `None` or `context.profile_cache.cited_sources` is empty AND `mcp_audit_map` has no `source_urls`, return an empty list.</action>
    <action>Iterate over `cited_sources`, prefix with "- " if not already prefixed. Also unconditionally extract `source_urls` from `context.mcp_audit_map` traces (if present) and append them as bullets to the end. Return `[MarkdownBlock(text=md_content)]`.</action>
  </step>

  <step id="2" name="Modify blueprint.py">
    <demolish>REMOVE: `_hydrate_printable_sources_block` at @[c:\src\quorum\backend_v2\services\blueprint.py#L801-L815].</demolish>
    <demolish>REMOVE: The lambda wiring for `TargetBlockType.PRINTABLE_SOURCES_BLOCK` referencing `self._hydrate_printable_sources_block` in the dispatch table.</demolish>
    <action>Modify `@[c:\src\quorum\backend_v2\services\blueprint.py]`: Import `PrintableSourcesAdapter`.</action>
    <action>Update the dispatch table at @[c:\src\quorum\backend_v2\services\blueprint.py#L104-L111] to wire `TargetBlockType.PRINTABLE_SOURCES_BLOCK: lambda ctx: PrintableSourcesAdapter.build(ctx)`.</action>
  </step>

  <step id="3" name="Implement Test Contracts">
    <action>Create `@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_printable_sources_adapter.py]` [NEW].</action>
    <action>Fulfill the test contracts explicitly.</action>
    <test_contracts>
      <test name="test_build_empty_profile_cache_returns_empty" category="boundary">
        <input>AdapterContext with profile_cache=None</input>
        <expected>returns []</expected>
      </test>
      <test name="test_build_empty_cited_sources_returns_empty" category="boundary">
        <input>AdapterContext with profile_cache.cited_sources=[]</input>
        <expected>returns []</expected>
      </test>
      <test name="test_build_formats_cited_sources_as_markdown" category="positive">
        <input>AdapterContext with profile_cache.cited_sources=["Source 1", "Source 2"]</input>
        <expected>returns [MarkdownBlock(text="- Source 1\n- Source 2", ...)]</expected>
      </test>
      <test name="test_build_preserves_existing_bullet_prefix" category="positive">
        <input>AdapterContext with profile_cache.cited_sources=["- Source 1", "Source 2"]</input>
        <expected>returns [MarkdownBlock(text="- Source 1\n- Source 2", ...)]</expected>
      </test>
      <test name="test_build_appends_mcp_urls" category="positive">
        <input>AdapterContext with cited_sources and mcp_audit_map containing traces with source_urls</input>
        <expected>returns MarkdownBlock ending with the MCP URLs</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
    <action>Verify `PrintableSourcesAdapter` has 100% unit test coverage.</action>
    <action>Verify `grep_search` for `_hydrate_printable_sources_block` returns no results in `blueprint.py`.</action>
  </validation_gate>
</execution_protocol>
```
