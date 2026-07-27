# Phase 1A: Backend DTO Field Deletion & Blueprint Producer Migration

> Source: @[c:\src\quorum\docs\epic\EPIC_111_sdui_legacy_eradication_and_ui_refactor.md#L52-L60] Phase 1

## Overview

This is the **foundational backend plan** for Epic 111. It performs two coupled operations:
1. **Delete** the legacy top-level fields (`evaluative_matrices`, `informational_matrices`, `content_blocks`) from `ReportDataDTO` in `v2_core.py`.
2. **Migrate** the `penalties_applied` field into the `layouts` array as a standard `ReportLayoutDTO` block, then delete the top-level `penalties_applied` from `ReportDataDTO`.
3. **Refactor** `blueprint.py` (the **Producer**) to route all data exclusively through the `layouts` array.

> [!WARNING]
> **SCOPE BOUNDARY (from Epic)**: `content_blocks` on `SynthesisSectionDTO` and `SynthesisOutputDTO` is architecturally DISTINCT from `ReportDataDTO.content_blocks` and MUST NOT be deleted. Similarly, `_evaluative_matrices` in `scoring.py` is an internal DAG execution state alias (not a rendering field) and MUST be preserved.

## Target Files (MODIFY)

1. @[c:\src\quorum\backend_v2\models\v2_core.py#L1198-L1236] — DELETE legacy fields
2. @[c:\src\quorum\backend_v2\services\blueprint.py#L1036-L1050] — Migrate penalties into layouts
3. @[c:\src\quorum\backend_v2\services\blueprint.py#L1460-L1545] — Refactor `build_report_dto` to stop populating deleted fields

## Context Files (READ-ONLY)

- @[c:\src\quorum\backend_v2\models\dtos\synthesis.py] — SynthesisOutputDTO.content_blocks is RETAINED
- @[c:\src\quorum\backend_v2\hooks\scoring.py#L48] — `_evaluative_matrices` internal alias is RETAINED
- @[c:\src\quorum\backend_v2\models\v2_core.py#L1-L100] — ReportLayoutDTO definition (the target structure)

## Execution Steps

```xml
<execution_protocol level="2_tier2_execute">
  <step id="1A.1" name="DELETE LEGACY FIELDS FROM ReportDataDTO">
    <action>In @[c:\src\quorum\backend_v2\models\v2_core.py#L1198-L1207], DELETE the following three field declarations:
      - `evaluative_matrices: list[MatrixScorecardRowDTO] | None = Field(...)`
      - `informational_matrices: list[MatrixScorecardRowDTO] | None = Field(...)`
      - `content_blocks: list[dict[str, Any]] | None = Field(...)`
    </action>
    <action>In @[c:\src\quorum\backend_v2\models\v2_core.py#L1234-L1236], DELETE the field:
      - `penalties_applied: list[str] = Field(...)`
    </action>
    <action>Remove the comment line `# LEGACY FIELDS (Deprecated but kept for UI transition compatibility)` at L1198.</action>
    <constraint invariant="strict_type_fidelity_mandate">The `layouts: list[ReportLayoutDTO]` field at L1211 MUST remain. It is the SSOT for all report rendering.</constraint>
    <constraint invariant="anti_semantic_drift_renaming">Do NOT rename any retained fields.</constraint>
    <demolish>REMOVE: Lines 1198-1207 (evaluative_matrices, informational_matrices, content_blocks declarations and legacy comment). REMOVE: Lines 1234-1236 (penalties_applied declaration). These are replaced by exclusive routing through the `layouts` array.</demolish>
  </step>

  <step id="1A.2" name="MIGRATE PENALTIES INTO LAYOUTS IN blueprint.py">
    <action>In @[c:\src\quorum\backend_v2\services\blueprint.py#L1036-L1050], refactor the penalties assembly logic. Instead of collecting penalties into a standalone `penalties_applied: list[str]` variable, inject each penalty string as a `ReportLayoutDTO` block with `preset_view="text_only"` into the `layouts` array. Map penalty text into the `synthesis_blocks` field of the `ReportLayoutDTO`.</action>
    <constraint invariant="epic_source_of_truth">Per Epic 111 Section 2: "Map penalties into a ReportLayoutDTO with preset_view='text_only' and inject the penalty text natively into synthesis_blocks using standard SDUI blocks."</constraint>
    <constraint>Do NOT create polymorphic subclasses like `ReportLayoutPenaltyBlockDTO`. Use standard `ReportLayoutDTO`.</constraint>
  </step>

  <step id="1A.3" name="REFACTOR build_report_dto TO REMOVE DELETED FIELD ASSIGNMENTS">
    <action>In `build_report_dto()` at @[c:\src\quorum\backend_v2\services\blueprint.py#L1460-L1545]:
      - REMOVE the `evaluative_matrices=evaluative_matrices` kwarg from the `ReportDataDTO(...)` constructor (L1464, L1542).
      - REMOVE the `informational_matrices=informational_matrices` kwarg (L1465, L1543).
      - REMOVE the `penalties_applied=penalties_applied` kwarg (L1463, L1541).
      - Ensure `evaluative_matrices` and `informational_matrices` data is instead injected into the `layouts` array as `MATRIX_SCORECARD_TABLE` layout blocks (this should already be happening via the SDUI mapper — verify).
    </action>
    <demolish>REMOVE: All occurrences of `evaluative_matrices=`, `informational_matrices=`, `penalties_applied=` kwargs in ReportDataDTO constructor calls within blueprint.py.</demolish>
    <constraint invariant="the_zero_compromise_pledge">The `evaluative_matrices` and `informational_matrices` local variables within blueprint.py's matrix computation methods are RETAINED as intermediate computation state. Only the ASSIGNMENT to the DTO constructor is deleted.</constraint>
  </step>

  <step id="1A.4" name="REFACTOR SLOP PENALTY DETECTION IN blueprint.py">
    <action>In @[c:\src\quorum\backend_v2\services\blueprint.py#L1478-L1492], the slop detection currently checks `penalties_applied` list. Refactor this to scan the `layouts` array for the penalty `ReportLayoutDTO` blocks injected in step 1A.2 instead.</action>
    <constraint>The slop detection logic at worker.py L444-L458 will be refactored separately in Phase 1C (03_backend_worker_hasattr_purge_plan.md).</constraint>
  </step>

  <step id="1A.5" name="QUALITY GATE">
    <action>Run the backend audit loop to verify compilation and type safety.</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test</command>
    <constraint invariant="zero_tolerance_audit_loop">Tests WILL fail at this point because consumers still reference the deleted fields. This is expected — consumers are fixed in the next plan. The goal here is to verify v2_core.py and blueprint.py compile cleanly with no MyPy errors.</constraint>
  </step>
</execution_protocol>
```

## Testing & Quality Gate Plan

- **Unit Tests**: `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`
- **Unit Tests**: `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test`
- **Negative Tests**:
  1. Verify `ReportDataDTO` constructor rejects `evaluative_matrices=` kwarg with `ValidationError`.
  2. Verify penalties are correctly serialized as `ReportLayoutDTO` blocks in the `layouts` array.

> [!IMPORTANT]
> After step 1A.5 passes, instruct: `git add backend_v2/models/v2_core.py backend_v2/services/blueprint.py` then `git commit -m "epic111: delete legacy ReportDataDTO fields, migrate penalties to layouts"`
