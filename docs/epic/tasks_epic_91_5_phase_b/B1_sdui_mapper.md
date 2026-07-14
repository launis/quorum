# Epic 91.5 Phase B1: SDUI Mapper Service Implementation

## Objective
Implement the missing Server-Driven UI mapping logic inside `SduiMapperService` to produce a full `ReportView` component tree based on the new `v2_core.ReportDataDTO`.

## Context & Architectural Mandates
- **Tripartite Rendering Boundary:** The Backend passes structured data (`ReportView` containing `UiSection`s). The Backend MUST NOT generate raw HTML or UI code, but strictly populate the Pydantic DTOs.
- **Fail-Fast:** Do not use `dict.get()` or duct-tape missing fields. If required data for a UI component is missing from `ReportDataDTO`, raise an `AppException`.

## Target Files (Modify)
- `backend_v2/services/sdui_mapper_service.py`

## Context Files (Read-Only)
- `backend_v2/models/v2_core.py` (Source DTO: `ReportDataDTO`)
- `backend_v2/models/view/sdui.py` (Target DTO: `ReportView`, `UiSection`, `ScoreCardDisplay`, `SectionType`)

## Proposed Changes

### 1. Update `backend_v2/services/sdui_mapper_service.py`
- **Layout-Driven SDUI Mapping:** Modify `map_report_to_sdui` to iterate over `ReportDataDTO.layouts` instead of dumping `evaluative_matrices` blindly. The dynamic `layouts` dictate the component order and UI structure.
- **ScoreCard Translation:** When a `ReportLayoutDTO` represents a matrix view (e.g., `preset_view` is `1d_metrics` or `3d_matrix`), map its `axes` (`list[MatrixScorecardRowDTO]`) into a `UiSection` with `type=SectionType.SCORE_CARD`. The payload `data` MUST be a strictly validated `ScoreCardDisplay` where each axis is mathematically transformed into a `DimensionDisplay`.
- **Synthesis Block Mapping:** Translate `ReportLayoutDTO.synthesis_blocks` and global `ReportDataDTO.content_blocks` into `UiSection` blocks with `type=SectionType.MARKDOWN_BLOCK` or `HERO_INSIGHT`.
- **Metrics & Telemetry:** Ensure `ReportView`'s `metrics` dictionary captures `global_score` and `strictness_level`. Map the global `has_warning` flag to the `status_theme` property of `ReportView` (e.g., 'warning' if true, 'success' if false).
- **XAI Transparency:** Map `ReportDataDTO.mcp_tool_audit` and `grouped_extensions` to appropriate UI sections (like `EVIDENCE_LIST` or `USAGE_STATS`) to satisfy the System Audit Trail rule.

## Testing & Quality Gate Plan
- Write or update `backend_v2/tests/unit/services/test_sdui_mapper_service.py` to cover all mapping pathways with 100% test coverage.
- Execute the Universal Quality Gate (`scripts/backend_audit_loop.py backend_v2/services/sdui_mapper_service.py --test`).

---
# Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
