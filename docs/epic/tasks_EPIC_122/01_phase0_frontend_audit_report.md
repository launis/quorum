# Phase 0 Frontend DTO Parity Audit Report

## Audit Scope
- **Plan**: @[c:\src\quorum\docs\epic\tasks_EPIC_122\01_phase0_frontend_dto_parity_plan.md]
- **Target Directories**: `client_app_v2/lib/features/studio/models/`, `client_app_v2/lib/features/execution/models/`

## Traceability Matrix

| Requirement | Target File | Status | Notes |
| :--- | :--- | :--- | :--- |
| Add `matrix_visible_columns` to `OutputLayoutBlock` | `output_profile.dart` | ✅ PASS | Verified. |
| Add `matrix_visible_columns` to `ReportLayoutDto` | `report_layout_dto.dart` | ✅ PASS | Verified. |
| Remove `matrix_visible_columns` from `SynthesisConfigDto` | `synthesis_config_dto.dart` | ✅ PASS | Removed successfully. |
| Remove `matrix_visible_columns` from `SynthesisConfigDTO` | `output_profile.dart` | ❌ FAIL | Field remains in `SynthesisConfigDTO` inside `output_profile.dart`. |
| Remove `matrix_visible_columns` from `ReportDataDto` | `report_data_v2_dto.dart` | ✅ PASS | Removed successfully. |
| Add `user_role` & `justification` to `GlobalSynthesisDto` | `global_synthesis_dto.dart`| ✅ PASS | Verified. |
| Add `user_role_label` to `OutputProfile` / `Embedded` | `output_profile.dart` | ✅ PASS | Verified. |
| Run Flutter build runner / Quality Gate | `scripts/flutter_audit_loop.py` | ✅ PASS | Build passes. |

## Gap Analysis & Required Fixes
**1. Orphan Requirement (Step 1_2)**
The field `matrixVisibleColumns` was successfully removed from the `SynthesisConfigDto` in `client_app_v2/lib/features/execution/models/synthesis_config_dto.dart`, but it was **NOT removed** from the equivalent studio model `SynthesisConfigDTO` located in `client_app_v2/lib/features/studio/models/output_profile.dart`.

*Required Fix*: 
Remove the following lines from `SynthesisConfigDTO` in `@[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart#L70-L72]`:
```dart
    @Default(['label', 'score', 'distribution', 'row_explanation'])
    @JsonKey(name: 'matrix_visible_columns')
    List<String> matrixVisibleColumns,
```
Then re-run the `flutter_audit_loop.py --build` to regenerate `output_profile.g.dart` and `output_profile.freezed.dart`.

## Conclusion
**Audit Result**: ❌ FAIL
The plan is mostly complete but requires a small fix to achieve strict DTO parity, as the old field is still present in the Studio model.

## Resume Command
`/tier5-resume --workflow=/tier2-execute --target="@[c:\src\quorum\docs\epic\tasks_EPIC_122\01_phase0_frontend_dto_parity_plan.md] @[c:\src\quorum\docs\epic\EPIC_122_tracker.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\02_flutter_desktop.md]"`
