# Phase 5: Flutter Admin Studio Updates

Source: Epic 68 Phase 4

## Architectural Laws (from .agents/rules)
- **Rule 02 (Flutter Desktop-First):** Desktop-Class Pro Tool layout.

## Target Files (Modify)
- `client_app_v2/lib/features/studio/models/output_profile.dart`
- `client_app_v2/lib/features/studio/views/profile_editor_view.dart`
- `client_app_v2/lib/features/studio/views/output_profile_crud_view.dart`
- `client_app_v2/test/features/studio/models/output_profile_test.dart`
- `docs/architecture/02_flutter_desktop.md`

## Tasks

1. **`client_app_v2/lib/features/studio/models/output_profile.dart`**:
   - Update the model to replace `visibleExtensions` with `visibleBlockExtensions` and `visibleWorkflowExtensions`.
   - Run `uv run python scripts/flutter_audit_loop.py client_app_v2 --build` to regenerate Freezed and JsonSerializable files.

2. **`client_app_v2/lib/features/studio/views/profile_editor_view.dart` & `output_profile_crud_view.dart`**:
   - Split the "XAI Extensions" multiselect into two distinct semantic UI blocks:
     - **Vaihekohtaiset laajennokset (Block-level)**: bound to `visibleBlockExtensions`.
     - **Globaalit työnkulun laajennokset (Workflow-level)**: bound to `visibleWorkflowExtensions`.
   - **Dynamic Dropdown Population**: Populate the Block-level dropdown based on the newly available `/api/v2/workflows/{id}/available-extensions` (or Workflow DTO logic). If a workflow does not produce `emotional_sentiment`, it MUST NOT appear as a selectable option.
   - The Workflow-level dropdown should be populated by statically supported global metrics.
   - Ensure Optimistic UI updates handle the new dual-array state payload.

3. **`client_app_v2/test/features/studio/models/output_profile_test.dart`**:
   - Fix all test references to `visibleExtensions`.

4. **Documentation Update**:
   - Update `c:\src\quorum\docs\architecture\02_flutter_desktop.md` to explain the new dual-array state payload for output profiles and the dynamic Block-level UI filtering.

## Testing & Quality Gate Plan
- **Unit Tests:** Execute `cd client_app_v2 && dart test`
- **Quality Gate:** Execute `uv run python scripts/flutter_audit_loop.py client_app_v2`

## Session Handover
To execute this phase, start a NEW chat session and run:
`/tier2-hardening-frontend --target="c:\src\quorum\docs\epic\tasks_EPIC_68_Extension_Scope_Separation\phase5_flutter_ui.md"`
