# Phase 7A: SDUI Layout Flattening — Dispatch Loop Refactoring & Adapter Wiring

**Overview:** Refactor `blueprint.py`'s final assembly to concatenate all extracted adapter blocks into a single flat `inner_sdui_blocks` list. Configure the dispatch loop execution order to match the report structure defined in the Epic (metadata → executive summary → matrices → extensions → summary table → workflow extensions → sources).

**Key Epic References:**
- `ReportDataDTO` with `inner_sdui_blocks`: @[c:\src\quorum\backend_v2\models\v2_core.py#L1125-L1199]

**Target Files:**
- @[c:\src\quorum\backend_v2\services\blueprint.py]
- @[c:\src\quorum\backend_v2\services\sdui\adapters\metadata_adapter.py] [NEW]
- @[c:\src\quorum\backend_v2\services\sdui\adapters\synthesis_text_adapter.py] [NEW]
- @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_metadata_adapter.py] [NEW]
- @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_synthesis_text_adapter.py] [NEW]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    - [ ] `blueprint.py` contains ZERO direct `AccordionBlock`, `AlertBlock`, `ParagraphBlock`, or `MarkdownBlock` instantiation for the extracted adapters.
    - [ ] `blueprint.py` is reduced from 2012 lines to approximately 1200-1300 lines.
    - [ ] Every adapter file in `backend_v2/services/sdui/adapters/` is self-contained.
    - [ ] The `ReportDataDTO` JSON output is MIGRATED to the flat `inner_sdui_blocks` architecture.
    - [ ] The dispatch table `_target_block_hydrators` uses `dict[str, Callable[[AdapterContext], list[AnySduiBlock]]]` with uniform lambda-wrapped calling convention.
  </dod_checklist>

  <anti_targets>
    - `backend_v2/models/v2_core.py` (Do not delete OutputLayoutBlock)
  </anti_targets>

  <step id="1" name="CREATE MetadataAdapter and SynthesisTextAdapter">
    <constraint invariant="knowledge_item_preflight">Read KI `sdui_adapter_decomposition` (`ki_sdui_adapter_pattern.md`) before creating adapters.</constraint>
    <action>Modify `backend_v2/services/sdui/adapters/base_adapter.py` to add `user_name: str | None`, `org_name: str | None`, and `synthesis_md: str | None` to `AdapterContext`. (Justification: Adapters are synchronous and cannot use repositories to fetch identity data, so it must be passed in).</action>
    <action>Create `c:\src\quorum\backend_v2\services\sdui\adapters\metadata_adapter.py`. This adapter must generate the `HeaderBlock` using `context.execution` metadata (created_at) and the new `context.user_name` / `context.org_name` fields.</action>
    <action>Create `c:\src\quorum\backend_v2\services\sdui\adapters\synthesis_text_adapter.py`. This adapter must own the core Markdown content blocks splicing. It reads `context.profile.content_blocks` and `context.synthesis_md`, applies the `bleach.clean` HTML sanitization, and applies PII masking if `profile.layouts` requests it.</action>
    <action>Wire both new adapters into the `_target_block_hydrators` registry in `blueprint.py`.</action>
  </step>

  <step id="2" name="REFACTOR blueprint.py Dispatch Loop">
    <action>Modify `build_report_dto` in `blueprint.py`.</action>
    <action>Delete the legacy logic that builds a nested layout structure.</action>
    <action>Initialize `inner_sdui_blocks: list[AnySduiBlock] = []`.</action>
    <action>Configure the dispatch loop execution order EXACTLY as follows: Metadata, Executive Summary, Matrix Graphs & Justifications, Extensions (XAI + Penalties), Matrix Summary Table, Workflow Extensions, Sources.</action>
    <action>For each adapter in the ordered dispatch loop, call `build(context)` and `.extend()` the results into `inner_sdui_blocks`.</action>
    <action>Assign `inner_sdui_blocks` to `ReportDataDTO` and eliminate nested structural logic.</action>
    <demolish>REMOVE: all legacy `content_blocks.append(...)` and nested array assignments in `build_report_dto`. REPLACE WITH: flat `.extend()` onto `inner_sdui_blocks`.</demolish>
  </step>

  <step id="3" name="GLOBAL MANDATES PRESERVATION">
    <action>Ensure that `MetadataAdapter` and `SynthesisTextAdapter` strictly respect `global_mandates.py` and `linguistic_directives.py` rules for formatting and anti-truncation.</action>
    <action>They must pass text through exactly as produced by the LLM without shortening.</action>
  </step>

  <test_contracts>
    <test name="test_metadata_adapter_builds_header_block" category="positive">
      <input>AdapterContext with valid execution metadata</input>
      <expected>returns [HeaderBlock(...)]</expected>
    </test>
    <test name="test_dispatch_loop_flattens_blocks" category="positive">
      <input>Valid ReportDataDTO request to build_report_dto</input>
      <expected>returns ReportDataDTO where inner_sdui_blocks contains all adapter outputs sequentially</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
  </validation_gate>
</execution_protocol>
```
