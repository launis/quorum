# Phase 2: Riverpod State Providers (O(1) Data Binding)

**Source:** Epic 94, Phase 2

## Objective
Abstract the `report_data_v2_dto` payload into granular Riverpod Notifiers to prevent full-screen re-renders and utilize O(1) dictionary lookups.

## Scoping
**TARGET (Modify):**
- `client_app_v2/lib/features/execution/providers/report_data_v2_provider.dart` [NEW]
- `client_app_v2/lib/features/execution/providers/hydrated_reference_provider.dart` [NEW]
- `client_app_v2/lib/features/execution/providers/atom_result_provider.dart` [NEW]
- `client_app_v2/lib/features/execution/models/execution_record.dart`

**CONTEXT (Read-Only):**
- `client_app_v2/lib/features/execution/models/report_data_v2_dto.dart`
- `client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart`

## Architectural Invariants (Injected)
- **manual_riverpod_providers**: Riverpod Code Generation `@riverpod` is ABSOLUTELY MANDATORY for all state providers. No legacy `StateProvider`.
- **main_thread_jank_isolate**: Deserialization of the massive report payload from the backend MUST be wrapped in `await Isolate.run(() => ...)`.
- **tenant_data_isolation**: Ensure caches are invalidated (`ref.invalidate`) on execution or tenant switch.

## Requirements Mapping
1. **Payload Integration (`execution_record.dart`)**:
   - Update `ExecutionRecord` to accept `ReportDataV2Dto` instead of `ReportDataDTO`, or add it alongside temporarily for the migration phase (Zero Behavioral Change Mandate). *Recommendation: Add `ReportDataV2Dto? reportDataV2` to `ExecutionRecord` for dual-writing during the migration.*

2. **Root Provider (`report_data_v2_provider.dart`)**:
   - Implement an `@riverpod` class to fetch and hold the raw `ReportDataV2Dto` for a given `executionId`.

3. **Hydrated Reference Provider (`hydrated_reference_provider.dart`)**:
   - Create a computed provider `@riverpod HydratedAtomDTO? hydratedReference(ref, String tdaId)` that extracts the static reference from `ReportDataV2Dto.hydratedReferences[tdaId]` in O(1) time.

4. **Atom Result List Provider (`atom_result_provider.dart`)**:
   - Create an `@riverpod List<AtomResultDTO> atomResults(ref)` that simply returns `ReportDataV2Dto.results`.
   - The frontend MUST NOT perform topological sorting. Trust the backend list sequence.

## Testing & Quality Gate Plan
- **Baseline Metric**: Provider compilation success and dependency injection graphs.
- **Unit Tests**: Create `client_app_v2/test/features/execution/providers/report_data_v2_provider_test.dart` to verify `ref.watch` behaves optimally and O(1) lookups succeed.
- **Universal Quality Gate**: Must run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/providers --build`

---
## Session Handover Context
**Achieved**: Defined Phase 2 plans for Riverpod Providers.
**Learned**: We must use `Isolate.run` for the V2 parsing, and `@riverpod` annotations for all providers. O(1) lookups are implemented via `hydratedReference(ref, id)`.
**Remaining**: Execution of Phase 2, followed by Phase 3.

To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker (`docs\epic\EPIC_94_Frontend_SDUI_Synchronization_tracker.md`).
