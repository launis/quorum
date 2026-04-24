# Epic 39: Phase 3 - Frontend & SDUI Layer (Flutter Client)

## Goal
Implement the Flutter user interface components to consume the strictly typed dynamic reporting API and visualize the scoring mechanics through the Matrix Observability Accordion.

## Target Files (Modify)
- `client_app_v2/lib/core/models/enums.dart`
- `client_app_v2/lib/features/studio/views/widgets/xai/fallback_error_card.dart` (Create/Modify)
- `client_app_v2/lib/features/studio/views/widgets/xai/matrix_observability_accordion.dart` (Create/Modify)

## Context Files (Read-Only)
- `client_app_v2/lib/core/models/`

## Architectural Invariants (MANDATORY)
1. **Silent JSON Fallbacks Ban (`silent_json_fallbacks`)**: Missing or malformed data MUST crash the Freezed parser. Use `disallow_unrecognized_keys: true`.
2. **No Raw String Enum Mappings (`no_raw_string_enum_mappings`)**: UI extensions must map 1:1 with `@JsonEnum()` definitions in `enums.dart`. Unrecognized strings must trigger a parsing failure.
3. **Graceful Degradation / Fallback UI**: While parsing must be strict, if a *known* enum type is selected in the UI but missing from the backend data payload, render a `FallbackErrorCard` instead of crashing the UI or using `SizedBox.shrink()`.
4. **SizedBox Shrink Ban (`sized_box_shrink_ban`)**: Never use `SizedBox.shrink()` to hide broken state.
5. **O(1) Lists (`o1_lists`)**: Use `List<T>` with `@Freezed(equal: false)` for observability lists.
6. **Flexbox Native Engine (`flexbox_native_engine_standard`)**: Use pure Flexbox (`Expanded`, `Row`, `Column`) for the accordion. No `MediaQuery` multipliers.
7. **Zero Compromise Pledge (`the_zero_compromise_pledge`)**: Adhere strictly to the defined data models without relying on legacy loose types.
8. **No Fallbacks (`the_duct_tape_ban`)**: Missing translation keys or unexpected strings must not default silently to empty text or incorrect fallbacks.
9. **Universal Fail-Fast (`universal_fail_fast`)**: If data payload doesn't conform perfectly to the Freezed definitions, crash the parser immediately, propagating the error to the AppErrorBoundary.

## Implementation Steps
1. Update `enums.dart` with any new L10N/Extension enums introduced in Phase 1.
2. Build the `FallbackErrorCard` widget for graceful degradation when XAI extensions are missing.
3. Build the `MatrixObservabilityAccordion` widget to visualize `true_atoms_count` and `false_atoms_count`.

## Verification Plan & Quality Gate
Run the Dart build runner to generate models and perform static analysis:
```bash
cd client_app_v2; dart run build_runner build -d;
cd ..
uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/xai/
```
