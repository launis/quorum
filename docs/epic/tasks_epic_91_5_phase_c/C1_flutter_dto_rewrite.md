# Phase C1: Rewrite Flutter `ReportDataDto` + Create New Models

> Source: Red-Teamed Implementation Plan Phase C1, C2 (partial)

## Context

The current Flutter `ReportDataDto` ([report_data_v2_dto.dart](file:///c:/src/quorum/client_app_v2/lib/features/execution/models/report_data_v2_dto.dart)) is a **broken 6-field placeholder** that does not match the backend's actual `ReportDataDTO` (~30 fields). The `fromBackendResponse` factory uses a hardcoded `allowedKeys` whitelist that strips ALL scorecard data. This phase rewrites the model from scratch and creates supporting Freezed models.

## Prerequisite

- Phase C0 MUST be committed (backend now sends `execution_id`)

## Architectural Rules Applied

- `02_flutter_desktop.md`: `silent_json_fallbacks` — `disallowUnrecognizedKeys: true` mandatory
- `02_flutter_desktop.md`: `o1_lists` — `@Freezed(equal: false)` for large lists
- `02_flutter_desktop.md`: `main_thread_jank_isolate` — keep `safeIsolateRun` for parsing
- `00-antigravity-core.md`: `the_zero_compromise_pledge` — no fallback defaults
- KI `frontend_sdui_riverpod_caching` — Isolate parsing for heavy payloads

## Scope

| Role | File | Action |
|---|---|---|
| TARGET | `client_app_v2/lib/features/execution/models/report_data_v2_dto.dart` | FULL REWRITE (~30 fields) |
| TARGET | `client_app_v2/lib/features/execution/models/report_layout_dto.dart` | NEW — Freezed model for `ReportLayoutDTO` |
| TARGET | `client_app_v2/lib/features/execution/models/synthesis_config_dto.dart` | NEW — Freezed model for `SynthesisConfigDTO` |
| CONTEXT | `backend_v2/models/v2_core.py` | Read-only — field-level verification |
| CONTEXT | `client_app_v2/lib/features/execution/models/scorecard_dto.dart` | Read-only — classes referenced but not moved yet |
| CONTEXT | `client_app_v2/lib/shared/models/i18n_text.dart` | Read-only — `I18nText` Freezed model |
| CONTEXT | `client_app_v2/lib/features/execution/models/global_synthesis_dto.dart` | Read-only — kept temporarily |

## Milestones

### M1: Rewrite `report_data_v2_dto.dart`

**FULL REWRITE.** Replace the current 6-field model with ALL ~30 fields from the backend's `ReportDataDTO` ([v2_core.py:1046-1103](file:///c:/src/quorum/backend_v2/models/v2_core.py#L1046-L1103)).

**Field mapping (backend Python → Flutter Dart):**

| Backend Field | Dart Type | Required? | Default |
|---|---|---|---|
| `execution_id` | `String` | ✅ | — |
| `workflow_id` | `String` | ✅ | — |
| `scoring_strategy` | `String?` | ❌ | null |
| `user_name` | `String?` | ❌ | null |
| `scoring_engine_name` | `String?` | ❌ | null |
| `strictness_level` | `int?` | ❌ | null |
| `local_time_str` | `String?` | ❌ | null |
| `custom_preface_md` | `String?` | ❌ | null |
| `profile_id` | `String` | ✅ | — |
| `profile_name` | `I18nText?` | ❌ | null |
| `available_profiles` | `Map<String, I18nText>` | ❌ | `@Default({})` |
| `global_score` | `double?` | ❌ | null |
| `has_warning` | `bool` | ❌ | `@Default(false)` |
| `evaluative_matrices` | `List<MatrixScorecardRowDto>?` | ❌ | null |
| `informational_matrices` | `List<MatrixScorecardRowDto>?` | ❌ | null |
| `content_blocks` | `List<Map<String, dynamic>>?` | ❌ | null |
| `visible_metadata` | `List<String>` | ❌ | `@Default([])` |
| `layouts` | `List<ReportLayoutDto>` | ❌ | `@Default([])` |
| `matrix_visible_columns` | `List<String>` | ❌ | `@Default([])` |
| `created_at` | `String?` | ❌ | null |
| `org_name` | `String?` | ❌ | null |
| `cost_estimate` | `double?` | ❌ | null |
| `total_tokens` | `int?` | ❌ | null |
| `prompt_tokens` | `int?` | ❌ | null |
| `completion_tokens` | `int?` | ❌ | null |
| `reasoning_tokens` | `int?` | ❌ | null |
| `mcp_tool_audit` | `List<McpAuditTraceDto>` | ❌ | `@Default([])` |
| `grouped_extensions` | `Map<String, List<dynamic>>?` | ❌ | null |
| `penalties_applied` | `List<String>` | ❌ | `@Default([])` |

**Critical changes:**
1. **DELETE** the `fromBackendResponse` factory — no more `allowedKeys` stripping.
2. **DELETE** old imports for `ExecutionMetricsDTO`, `AtomResultDTO`, `HydratedAtomDTO`.
3. **ADD** imports for `MatrixScorecardRowDto` (from `scorecard_dto.dart` for now — will be moved in Phase C2), `ReportLayoutDto`, `I18nText`.
4. **ADD** import for `McpAuditTraceDto` (from `scorecard_dto.dart` for now).
5. **KEEP** `parseInBackground` with `safeIsolateRun` — update to use `fromJson` instead of `fromBackendResponse`.
6. **KEEP** `@Freezed(equal: false)` and `@JsonSerializable(disallowUnrecognizedKeys: true)`.

> [!WARNING]
> The backend `ReportDataDTO` does NOT have a `global_synthesis` field. Do NOT include `GlobalSynthesisDTO` in the rewritten model. The backend sends synthesis as `content_blocks`.

### M2: Create `report_layout_dto.dart`

New Freezed model mirroring backend `ReportLayoutDTO` ([v2_core.py:1024-1036](file:///c:/src/quorum/backend_v2/models/v2_core.py#L1024-L1036)):

```dart
@Freezed(equal: false)
abstract class ReportLayoutDto with _$ReportLayoutDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportLayoutDto({
    @JsonKey(name: 'preset_view') required String presetView,
    I18nText? title,
    I18nText? description,
    @Default([]) List<MatrixScorecardRowDto> axes,
    @JsonKey(name: 'text_delivery_mode') @Default('full') String textDeliveryMode,
    SynthesisConfigDto? synthesis,
    @JsonKey(name: 'synthesis_blocks') List<Map<String, dynamic>>? synthesisBlocks,
  }) = _ReportLayoutDto;

  factory ReportLayoutDto.fromJson(Map<String, dynamic> json) =>
      _$ReportLayoutDtoFromJson(json);
}
```

### M3: Create `synthesis_config_dto.dart`

New Freezed model for `SynthesisConfigDTO` ([v2_core.py:981-1021](file:///c:/src/quorum/backend_v2/models/v2_core.py#L981-L1021)).

**CRITICAL:** This model MUST use `@JsonSerializable(disallowUnrecognizedKeys: false)` because `SynthesisConfigDTO` is a backend-internal config object with 15+ fields. The Flutter client only needs to carry it opaquely, not parse every field. Per `01-python-backend.md` rule `duck_typing_token_shield_exception`, `disallowUnrecognizedKeys: false` is permitted for internal Data Projection Models.

Map the fields that the Flutter client actually needs (future-proofing for rendering):
```dart
@Freezed(equal: false)
abstract class SynthesisConfigDto with _$SynthesisConfigDto {
  // disallowUnrecognizedKeys: false — SynthesisConfigDTO is a backend config
  // object with 15+ internal fields. Flutter carries it opaquely.
  @JsonSerializable(disallowUnrecognizedKeys: false)
  const factory SynthesisConfigDto({
    @JsonKey(name: 'system_prompt') String? systemPrompt,
    @JsonKey(name: 'synthesis_block_id') String? synthesisBlockId,
    @JsonKey(name: 'row_explanations_block_id') String? rowExplanationsBlockId,
    @JsonKey(name: 'model_strategy') @Default('synthesis') String modelStrategy,
    @JsonKey(name: 'length_constraint') int? lengthConstraint,
    @JsonKey(name: 'enable_pii_masking') @Default(false) bool enablePiiMasking,
    @JsonKey(name: 'omit_empty_sections') @Default(true) bool omitEmptySections,
    @JsonKey(name: 'matrix_visible_columns') @Default([]) List<String> matrixVisibleColumns,
  }) = _SynthesisConfigDto;

  factory SynthesisConfigDto.fromJson(Map<String, dynamic> json) =>
      _$SynthesisConfigDtoFromJson(json);
}
```

### M4: Run `build_runner`

After all three files are created/modified:
```powershell
cd client_app_v2
dart run build_runner build -d
```

This regenerates `.freezed.dart` and `.g.dart` for:
- `report_data_v2_dto`
- `report_layout_dto`
- `synthesis_config_dto`

## Testing & Quality Gate

```powershell
# Flutter audit (includes build_runner regeneration)
uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution --build
```

### Verification
1. `build_runner` completes without errors.
2. `flutter analyze` passes with zero errors.
3. The new `ReportDataDto.fromJson()` can parse a mock JSON payload matching the backend's `ReportDataDTO.model_dump(mode="json")` output.

## Atomic Git Commit

```powershell
git add client_app_v2/lib/features/execution/models/report_data_v2_dto.dart
git add client_app_v2/lib/features/execution/models/report_layout_dto.dart
git add client_app_v2/lib/features/execution/models/synthesis_config_dto.dart
git add client_app_v2/lib/features/execution/models/report_data_v2_dto.freezed.dart
git add client_app_v2/lib/features/execution/models/report_data_v2_dto.g.dart
git add client_app_v2/lib/features/execution/models/report_layout_dto.freezed.dart
git add client_app_v2/lib/features/execution/models/report_layout_dto.g.dart
git add client_app_v2/lib/features/execution/models/synthesis_config_dto.freezed.dart
git add client_app_v2/lib/features/execution/models/synthesis_config_dto.g.dart
git commit -m "feat(flutter): rewrite ReportDataDto to match full backend contract"
```

## Session Handover

**Achieved:** Rewrote `ReportDataDto` with full ~30 field backend parity. Created `ReportLayoutDto` and `SynthesisConfigDto` Freezed models.
**Learned:** Backend `ReportDataDTO` has no `global_synthesis` field — it uses `content_blocks` instead. `SynthesisConfigDTO` needs `disallowUnrecognizedKeys: false` due to 15+ internal fields.
**Remaining:** Phase C2 (DTO relocation), C3 (scorecard pipeline deletion), C4 (UI rewiring), C5 (controller updates).
