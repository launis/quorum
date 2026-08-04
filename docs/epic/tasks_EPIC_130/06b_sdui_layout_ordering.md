# Phase 7B: SDUI Layout Flattening — PDF/Jinja Dumb Painter Parity

**Overview:** Blow away the legacy Jinja template and replace it with a clean slate that exactly mirrors the Flutter Dumb Painter architecture. The PDF generator and `report_template.jinja2` MUST blindly iterate over the flattened `inner_sdui_blocks` array, executing polymorphic rendering based strictly on the `SduiBlockDTO` types.

**Source:** @[c:\src\quorum\docs\epic\EPIC_130_blueprint_decomposition.md#L176-L205] Phase 7 (second sub-phase)

**Expected Target Files:**
- @[c:\src\quorum\backend_v2\models\view\sdui.py] [MODIFY — add `SduiMetadataBlock`, `SduiScoreCardBlock`, `SduiAuditTrailBlock`]
- @[c:\src\quorum\backend_v2\services\blueprint.py] [MODIFY — wire new adapters into `inner_sdui_blocks`]
- @[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart] [MODIFY — via build_runner]
- @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart] [MODIFY — clear manual rendering]
- @[c:\src\quorum\backend_v2\services\pdf_generator.py] [MODIFY — flat layout iteration]
- @[c:\src\quorum\backend_v2\templates\report_template.jinja2] [OVERWRITE — clean slate polymorphic rendering]

## Execution Protocol

```xml
<execution_protocol level="2">
  <step id="1">
    <description>Extract 100% Pure SDUI Models</description>
    <action>In `backend_v2/models/view/sdui.py`, create `SduiMetadataBlock`, `SduiScoreCardBlock`, and `SduiAuditTrailBlock` inheriting from `BaseSduiBlock`. This removes the need for root-level DTO fields.</action>
  </step>
  <step id="2">
    <description>Wire 100% SDUI Adapters</description>
    <action>In `blueprint.py`, extract `GlobalScoreAdapter`, `MetadataAdapter` (expanded), and `McpAuditAdapter` to return these new blocks, and sequence them into the `inner_sdui_blocks` array (e.g. metadata at index 0, score and audit at the end).</action>
  </step>
  <step id="3">
    <description>Demolish Legacy Jinja Template</description>
    <action>Delete the entire 481-line `report_template.jinja2` and replace it with a Clean Slate.</action>
    <validation>The new template MUST ONLY contain a single generic `for block in report_data.inner_sdui_blocks:` loop inside the body. ZERO manual rendering logic.</validation>
  </step>
  <step id="4">
    <description>Implement Polymorphic Dumb Painter (PDF)</description>
    <action>Inside the loop, match on `block.block_type` and map each to a dedicated Jinja macro, including the newly created Metadata, ScoreCard, and Audit blocks.</action>
  </step>
  <step id="5">
    <description>Eradicate Flutter Manual Rendering</description>
    <action>Run Flutter `build_runner` to sync the new SDUI block models. Modify `report_renderer_v2_widget.dart` to DELETE all explicit rendering of `globalScore` and `metadata`. The widget must become a pure 1-loop Dumb Painter exactly like the Jinja template.</action>
  </step>
</execution_protocol>
```
