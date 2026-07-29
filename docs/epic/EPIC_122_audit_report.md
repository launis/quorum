# EPIC 122 Audit Report

**Date:** 2026-07-29
**Status:** ⚠️ PARTIALLY IMPLEMENTED (FAIL)

## 1. Traceability Matrix

| Requirement | Epic Phase | Codebase Status | Notes |
| :--- | :--- | :--- | :--- |
| **Matrix Columns Relocation** | Phase 0 | ✅ PASS | `matrix_visible_columns` removed from `SynthesisConfigDTO`/`ReportDataDTO` and added to `OutputLayoutBlock`/`ReportLayoutDTO` in Python and Flutter. |
| **User Role Extraction** | Phase 0 | ✅ PASS | `GlobalSynthesisDTO` updated with `user_role` and `user_role_justification`. `user_role_label` added to `OutputProfile`. |
| **Flutter DTO Parity** | Phase 0 | ✅ PASS | Freezed models updated to match backend schema. |
| **Seed Data: Expanded Header** | Phase 1 | ✅ PASS | `visible_metadata` array updated to include `execution_id`. |
| **Seed Data: Matrix Layout Configuration** | Phase 1 | ❌ FAIL | The `3d_matrix` block in `seed_data.json` is **MISSING** the `matrix_visible_columns` array that was explicitly required by the Epic. Emojis also remain in `extension_labels` but Epic 123 is scheduled to strip them. |
| **Blueprint Target Block Hydrators** | Phase 2 | ✅ PASS | `TARGET_BLOCK_HYDRATORS` implemented (e.g. `_hydrate_printable_sources_block`). |
| **Flutter/Jinja `normalized_score`** | Phase 4/2 | ✅ PASS | Both Flutter and Jinja `report_template.jinja2` include rendering logic for `normalized_score`. |

## 2. Orphan Requirements & Gap Analysis

- **`matrix_visible_columns` Missing in Seed Data:** Although the Pydantic/Dart models were updated to support `matrix_visible_columns` in `OutputLayoutBlock`, the actual JSON data in `backend_v2/seed/seed_data.json` was never populated with the required values `["label", "distribution", "row_explanation", "normalized_score", "score"]` for the `3d_matrix` layout.
- **`GlobalSynthesisDTO` Conflict:** Epic 122 explicitly extended `GlobalSynthesisDTO` (Phase 0), but Epic 123 mandates its complete deletion. Epic 123 must ensure that `user_role_justification` (added in Epic 122) is not silently dropped during the migration to pure SDUI blocks.

## 3. Conclusion

Epic 122 was structurally implemented (Phase 0 and Phase 2), but its configuration phase (Phase 1) was incomplete. The missing seed data values prevent the `3d_matrix` from rendering the columns properly in a pristine environment. 
This Epic is currently marked as **FAILED** in the audit due to the incomplete `seed_data.json` migration.
