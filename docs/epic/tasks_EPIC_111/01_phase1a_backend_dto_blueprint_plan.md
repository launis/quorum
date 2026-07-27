# Phase 1a: Backend DTO Strictness & Blueprint Migration

## Overview
Delete legacy fields (`content_blocks`, `evaluative_matrices`, `informational_matrices`, `penalties_applied`) from `ReportDataDTO` and add pure Dumb Painter score formatting (`score_display_label`). Refactor `blueprint.py` to route all these structures into standard `layouts`.

## Target Files
- `@[c:\src\quorum\backend_v2\models\v2_core.py]` (Modify)
- `@[c:\src\quorum\backend_v2\services\blueprint.py]` (Modify)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="strict_pydantic_v2_rust">Force the Fail-Fast pipeline. Models must maintain strict extra='forbid'.</constraint>
  <constraint invariant="sdui_contract_fracture_prevention">Backend and Frontend DTOs are mathematically coupled.</constraint>
  
  <step id="1" name="ERADICATE LEGACY FIELDS FROM REPORTDATADTO">
    <action>Modify `ReportDataDTO` in `@[c:\src\quorum\backend_v2\models\v2_core.py]`. Delete `content_blocks`, `evaluative_matrices`, `informational_matrices`, and `penalties_applied`.</action>
    <demolish>REMOVE: `content_blocks: list[dict[str, Any]] | None`, `evaluative_matrices`, `informational_matrices`, and `penalties_applied` from `ReportDataDTO`.</demolish>
  </step>

  <step id="2" name="ADD SCORE DISPLAY LABEL TO MATRIXSCORECARDROWDTO">
    <action>Modify `MatrixScorecardRowDTO` in `@[c:\src\quorum\backend_v2\models\v2_core.py]`.</action>
    <action>Add `score_display_label: str | None = None` to enable pure Dumb Painter UI rendering where the frontend does not evaluate math conditions.</action>
  </step>
  
  <step id="3" name="REFACTOR BLUEPRINT GENERATOR - MATRICES & PENALTIES">
    <action>Modify `@[c:\src\quorum\backend_v2\services\blueprint.py]`. Refactor the SDUI generator (around `build_report_dto`) to route 100% of the dynamic report data exclusively through the `layouts` array.</action>
    <action>Matrices MUST be injected into `ReportLayoutDTO`'s `axes` array.</action>
    <action>Penalties MUST be assembled into a `ReportLayoutDTO` with `preset_view="text_only"` and mapped into `synthesis_blocks` (e.g. `alert_box`).</action>
    <action>Compute `score_display_label` internally (e.g. "5.0 / 10.0" or "-") and assign it to `MatrixScorecardRowDTO`.</action>
  </step>
  
  <step id="4" name="REFACTOR BLUEPRINT GENERATOR - CONTENT BLOCKS">
    <action>Modify `@[c:\src\quorum\backend_v2\services\blueprint.py]`. Refactor the processing of `profile.content_blocks` which previously assigned directly to `ReportDataDTO.content_blocks`.</action>
    <demolish>REMOVE: Assignment to `ReportDataDTO.content_blocks`.</demolish>
    <action>Inject content blocks as `synthesis_blocks` inside a `ReportLayoutDTO` within the `layouts` array.</action>
  </step>

  <step id="5" name="TESTING STRATEGY & QUALITY GATE PLAN">
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test`</action>
    <action>Tests for Blueprint must pass, though test data mocks will be broken and need fixing in Phase 2. Run strictly localized unit tests for `v2_core.py` and `blueprint.py`.</action>
    <action>Write negative tests confirming `ReportDataDTO` fails validation if legacy fields are passed in.</action>
  </step>
</execution_protocol>
```
