# C2 — DTO Relocation

## Goal
Extract shared scorecard models out of the legacy `scorecard_dto.dart` (which contains the obsolete `ScorecardResponseDto`) and into a clean `matrix_scorecard_dto.dart`. Update sibling model imports. Leave an export proxy in `scorecard_dto.dart` so widget-layer consumers continue to compile without modification until C4 rewiring.

## Proposed Changes

### client_app_v2/lib/features/execution/models/
#### [NEW] matrix_scorecard_dto.dart
Extract `MatrixScorecardRowDto`, `McpAuditTraceDto`, `ReasoningStepDto`, `QuoteEvidenceDto`, `HumanOverrideDto`, and `ScorecardAtomDto` from `scorecard_dto.dart` into this new file.

**Required file scaffolding (must be present before class definitions):**
```dart
// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/tda_state.dart';
import 'package:client_app/shared/models/i18n_text.dart';

part 'matrix_scorecard_dto.freezed.dart';
part 'matrix_scorecard_dto.g.dart';
```

**Preservation requirements:**
- All 6 classes MUST use `@Freezed(equal: false)` and `@JsonSerializable(disallowUnrecognizedKeys: true)`.
- `MatrixScorecardRowDto` MUST retain its custom private constructor (`const MatrixScorecardRowDto._();`) and the `atomsByLevel` computed getter.
- Class definition order matters for Dart: `ReasoningStepDto` → `QuoteEvidenceDto` → `HumanOverrideDto` → `ScorecardAtomDto` → `McpAuditTraceDto` → `MatrixScorecardRowDto` (dependencies-first).

#### [MODIFY] report_data_v2_dto.dart
Update the import from `scorecard_dto.dart` to `matrix_scorecard_dto.dart`.

#### [MODIFY] report_layout_dto.dart
Update the import from `scorecard_dto.dart` to `matrix_scorecard_dto.dart`. This file uses `MatrixScorecardRowDto` for the `axes` field.

#### [MODIFY] scorecard_dto.dart
Implement the Import Proxy Pattern:
1. Remove all 6 Freezed classes that were moved to `matrix_scorecard_dto.dart`.
2. Add `import 'matrix_scorecard_dto.dart';` — **CRITICAL**: Dart `export` does NOT bring symbols into the current library's scope. Without this import, `ScorecardResponseDto` cannot reference `MatrixScorecardRowDto` and the file will fail compilation.
3. Add `export 'matrix_scorecard_dto.dart';` — This ensures the 7 widget-layer consumers that still `import 'scorecard_dto.dart'` continue to resolve the moved classes without import changes.
4. Annotate `ScorecardResponseDto` with `@Deprecated('Use ReportDataDto. Removed in C3.')` for static analysis warnings.
5. Remove stale imports that were only used by the moved classes (e.g., `tda_state.dart`, `i18n_text.dart`) if `ScorecardResponseDto` doesn't use them.

## Verification Plan
- Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/ --build` (handles `build_runner` automatically).
- Verify zero analysis errors: `dart analyze client_app_v2/lib/features/execution/models/`.
- Spot-check that `scorecard_dto.dart` proxy export resolves correctly by confirming widget files compile without import changes.

---
# Session Handover Context
## Achieved
- Prepared C2 DTO Relocation plan.
## Learned
- Dart `export` can act as a proxy to prevent immediate import breakages.
## Remaining
- Execute C2.
