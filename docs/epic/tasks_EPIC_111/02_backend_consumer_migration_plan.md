# Phase 1B: Backend Consumer Migration (execution.py, flattener.py, linguistics.py, sdui_mapper_service.py)

> Source: @[c:\src\quorum\docs\epic\EPIC_111_sdui_legacy_eradication_and_ui_refactor.md#L56-L59] Phase 1

## Overview

After Phase 1A deletes the legacy fields from `ReportDataDTO`, this plan migrates the four backend **consumer** services that previously read data from the deleted top-level fields (`evaluative_matrices`, `informational_matrices`, `content_blocks`). Each consumer must be refactored to read exclusively from the `layouts` array.

## Target Files (MODIFY)

1. @[c:\src\quorum\backend_v2\services\execution.py#L763-L766] — Matrix consumption via legacy fields
2. @[c:\src\quorum\backend_v2\services\execution.py#L1272-L1273] — content_blocks consumption
3. @[c:\src\quorum\backend_v2\services\flattener.py#L38] — Matrix flattening via legacy fields
4. @[c:\src\quorum\backend_v2\hooks\linguistics.py#L176] — Linguistic matrix analysis

## Context Files (READ-ONLY)

- @[c:\src\quorum\backend_v2\models\v2_core.py] — ReportDataDTO (post-Phase 1A, without legacy fields)
- @[c:\src\quorum\backend_v2\services\blueprint.py] — Producer (already migrated in Phase 1A)
- @[c:\src\quorum\backend_v2\services\sdui_mapper_service.py#L61-L71] — content_blocks mapping

## Execution Steps

```xml
<execution_protocol level="2_tier2_execute">
  <step id="1B.1" name="REFACTOR execution.py MATRIX CONSUMPTION">
    <action>At @[c:\src\quorum\backend_v2\services\execution.py#L763-L766], replace:
      ```
      if report_dto.evaluative_matrices:
          matrices.extend(report_dto.evaluative_matrices)
      if report_dto.informational_matrices:
          matrices.extend(report_dto.informational_matrices)
      ```
      with code that extracts `MatrixScorecardRowDTO` data from the `report_dto.layouts` array by filtering for layouts with `preset_view == "MATRIX_SCORECARD_TABLE"` and extracting the matrix data from their structured payload.
    </action>
    <demolish>REMOVE: `report_dto.evaluative_matrices` and `report_dto.informational_matrices` direct access at L763-L766. REPLACE WITH: Layout-based matrix extraction from `report_dto.layouts`.</demolish>
    <constraint invariant="the_zero_compromise_pledge">Do NOT use `.get()` or `hasattr()` to check for the existence of matrix data. Filter layouts by their `preset_view` discriminator field.</constraint>
  </step>

  <step id="1B.2" name="REFACTOR execution.py CONTENT_BLOCKS CONSUMPTION">
    <action>At @[c:\src\quorum\backend_v2\services\execution.py#L1272-L1273], replace:
      ```
      if dto.content_blocks:
          for block in dto.content_blocks:
      ```
      with code that extracts content blocks from `dto.layouts` by filtering for layouts with `preset_view == "MARKDOWN_BLOCK"`.
    </action>
    <demolish>REMOVE: `dto.content_blocks` direct access at L1272-L1273. REPLACE WITH: Layout-based content block extraction.</demolish>
  </step>

  <step id="1B.3" name="REFACTOR flattener.py MATRIX FLATTENING">
    <action>At @[c:\src\quorum\backend_v2\services\flattener.py#L38], replace:
      ```
      matrices = (report_dto.evaluative_matrices or []) + (report_dto.informational_matrices or [])
      ```
      with code that extracts all matrix data from `report_dto.layouts` by filtering for `MATRIX_SCORECARD_TABLE` layout blocks.
    </action>
    <demolish>REMOVE: `report_dto.evaluative_matrices or []` and `report_dto.informational_matrices or []` fallback chain at L38. These are anti-patterns violating the Zero-Compromise Pledge.</demolish>
    <constraint invariant="the_zero_compromise_pledge">Do NOT introduce `or []` fallbacks on the new layout extraction. If no matrix layouts exist, the list should naturally be empty.</constraint>
  </step>

  <step id="1B.4" name="REFACTOR linguistics.py MATRIX ANALYSIS">
    <action>At @[c:\src\quorum\backend_v2\hooks\linguistics.py#L176], replace:
      ```
      all_matrices = (report_dto.evaluative_matrices or []) + (report_dto.informational_matrices or [])
      ```
      with code that extracts all matrix data from `report_dto.layouts` by filtering for `MATRIX_SCORECARD_TABLE` layout blocks.
    </action>
    <demolish>REMOVE: `report_dto.evaluative_matrices or []` and `report_dto.informational_matrices or []` fallback chain at L176.</demolish>
  </step>

  <step id="1B.5" name="REFACTOR sdui_mapper_service.py CONTENT_BLOCKS MAPPING">
    <action>At @[c:\src\quorum\backend_v2\services\sdui_mapper_service.py#L61-L71], the Phase B1 section maps `report.content_blocks` to MARKDOWN_BLOCK sections. Since `content_blocks` is now exclusively routed through `layouts` by blueprint.py, this entire mapping block is redundant. DELETE the `if report.content_blocks:` block entirely.</action>
    <demolish>REMOVE: The entire `Phase B1: Map global content_blocks to MARKDOWN_BLOCK sections` code block at L61-L71 in sdui_mapper_service.py. This is dead code since content_blocks are now natively injected into layouts by blueprint.py.</demolish>
  </step>

  <step id="1B.6" name="QUALITY GATE">
    <action>Run the backend audit loop on all modified consumer files.</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/services/execution.py --test</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/services/flattener.py --test</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/hooks/linguistics.py --test</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/services/sdui_mapper_service.py --test</command>
    <constraint invariant="zero_tolerance_audit_loop">All four files MUST pass MyPy and Ruff. Test failures related to the deleted fields in test fixtures are expected and will be addressed in Phase 2 (test hardening).</constraint>
  </step>
</execution_protocol>
```

## Testing & Quality Gate Plan

- **Unit Tests**: Run audit loop on each modified file individually.
- **Negative Tests**:
  1. Verify that `flattener.py` correctly returns an empty list when no `MATRIX_SCORECARD_TABLE` layouts exist.
  2. Verify that `execution.py` handles the absence of `MARKDOWN_BLOCK` layouts gracefully (empty iteration).
- **Integration**: After this plan, the `ReportDataDTO` pipeline should compile end-to-end on the backend without referencing any deleted fields.

> [!IMPORTANT]
> After step 1B.6 passes, instruct: `git add backend_v2/services/execution.py backend_v2/services/flattener.py backend_v2/hooks/linguistics.py backend_v2/services/sdui_mapper_service.py` then `git commit -m "epic111: migrate backend consumers from legacy fields to layouts array"`
