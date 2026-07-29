# Phase 5: Producer Logic (Backend SDUI Hydration - Part 2: Row Extensions & Cleanup)

## Objective
Transform matrix trace extensions into strict `AlertBlock` instances during SDUI mapping and completely eradicate the legacy `grouped_extensions` field from the backend.

## Target Files
- `@[c:\src\quorum\backend_v2\services\blueprint.py]` (Modify)
- `@[c:\src\quorum\backend_v2\models\v2_core.py]` (Modify)
- `@[c:\src\quorum\backend_v2\services\sdui_mapper_service.py]` (Modify)
- `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]` (Modify)
- `@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]` (Modify)
- `@[c:\src\quorum\backend_v2\tests\unit\services\test_sdui_mapper_service.py]` (Modify)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="universal_fail_fast">Do not use .get(), hasattr(), or silent fallbacks. Use strict attribute referencing on DTOs.</constraint>
  <constraint invariant="cross_language_mapping_mandate">Do not hardcode Finnish labels or emojis. Resolve labels dynamically via `extension_labels` using the execution's `target_language`.</constraint>
  <constraint invariant="anti_tdd_trap">Delete any legacy tests that expect `grouped_extensions` instead of restoring the removed logic.</constraint>

  <step id="1" name="TRANSFORM TRACE EXTENSIONS TO SDUI BLOCKS">
    <action>In `@[c:\src\quorum\backend_v2\services\blueprint.py]`, locate the `MatrixScorecardRowDTO` instantiation block (around line 650) and the loop iterating over `ext_dict` (around line 687).</action>
    <action>For each textual extension in `ext_dict.items()` (`ext_key`, `ext_val`), conditionally instantiate an `AlertBlock` (from `backend_v2.models.view.sdui`) if `ext_val` is truthy and `ext_key` is a valid `XaiExtensionType` enum string.</action>
    <action>Programmatic Label Resolution:
      1. Map the `ext_key` string to `XaiExtensionType`.
      2. Retrieve the `I18nText` object via `label_obj = profile.extension_labels.get(XaiExtensionType(ext_key))`.
      3. Resolve to string: `label_str = label_obj.resolve(execution.target_language) if label_obj else ext_key.replace('_', ' ').title()`.
    </action>
    <action>Exhaustive Severity Mapping:
      - `falsification`, `missing_context`, `variance_validation`, `authenticity_evaluation` -> `severity="warning"`
      - `risk_flag` -> `severity="error"`
      - `remediation_steps` -> `severity="success"`
      - All others (e.g., `coaching`, `justification`, `theory_link`, `citation`, `emotional_sentiment`) -> `severity="info"`
    </action>
    <action>Format `AlertBlock` text precisely: `text = f"**{label_str}**: {ext_val}"`.</action>
    <action>Append the `AlertBlock` directly into `row_dto.inner_sdui_blocks`.</action>
  </step>

  <step id="2" name="ERADICATE GROUPED_EXTENSIONS LOGIC IN BLUEPRINT">
    <action>In `@[c:\src\quorum\backend_v2\services\blueprint.py]`, delete all initialization, population, and assignment logic for `grouped_extensions`.</action>
    <demolish>REMOVE: `grouped_extensions: dict[str, list[Any]] = {...}` at approx line 918.</demolish>
    <demolish>REMOVE: The loop populating `grouped_extensions` from `xai_highlights_cache` (approx lines 979-1007).</demolish>
    <demolish>REMOVE: Any assignment of `grouped_extensions=grouped_extensions` when constructing `ReportDataDTO`.</demolish>
  </step>

  <step id="3" name="ERADICATE GROUPED_EXTENSIONS IN DOWNSTREAM BOUNDARIES (SDUI &amp; JINJA)">
    <action>In `@[c:\src\quorum\backend_v2\models\v2_core.py]`, explicitly delete the `grouped_extensions` field from `ReportDataDTO` (approx line 1199).</action>
    <action>In `@[c:\src\quorum\backend_v2\services\sdui_mapper_service.py]`, delete the `UiSection` block for `xai_extensions` (lines 131-142) which loops over `report.grouped_extensions`.</action>
    <action>In `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`, completely delete the `{% if report_data.grouped_extensions %}` global extensions block at the bottom of the template (approx lines 410-430), as well as the conditional confidence tag block using `grouped_extensions` (approx line 385).</action>
  </step>

  <step id="4" name="TESTING &amp; QUALITY GATE PLAN">
    <action>In `@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]`, update tests to verify that `AlertBlock` instances are correctly generated and appended to `row.inner_sdui_blocks`.</action>
    <action>In `@[c:\src\quorum\backend_v2\tests\unit\services\test_sdui_mapper_service.py]`, remove all tests asserting the presence of `xai_extensions` in the output sections.</action>
    <action>Include at least 2 negative test scenarios in `test_blueprint.py`: 1) Matrix payload with missing/none extension fields (verify no AlertBlocks are created). 2) Matrix payload with an unknown target language (verify fallback to english/default).</action>
    <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py backend_v2/models/v2_core.py backend_v2/services/sdui_mapper_service.py --test`</action>
    <action>Commit changes atomically upon success.</action>
  </step>
</execution_protocol>
