# Epic 95 Phase 3b: Frontend E2E UI Parity

## Context
**Source:** Epic 95 Phase 3
**Goal:** Verify UI/UX parity in Flutter. Ensure `n_a_card` renders correctly based on the `SDUIComponentType.nACard` enum.

## Rules Injected
- `02_flutter_desktop.md`: DisallowUnrecognizedKeys, Riverpod SSOT, Strict UI Rendering.
- Tier 1 Mandate: No Backend modifications here.

## Target Files (Modify)
- `client_app_v2/test/features/execution/n_a_card_snapshot_test.dart` (or equivalent location)
  - [NEW] Create a widget test rendering `SDUIComponentType.nACard`.
  - Verify that the card is displayed with the `grey` / `neutral` theme (simulating the N/A state).
  - Verify `short_circuit_reason_tda_ids` are mapped to the UI.

- `docs/architecture/` and `.agents/rules/04_directory_reference.md`
  - [NEW] Document the exact SDUI block structure for `n_a_card` in the architectural markdown if SDUI blocks are tracked there.

## Target Files (Context / Read-Only)
- `client_app_v2/lib/core/models/enums.dart` (Contains `SDUIComponentType.nACard`)
- `client_app_v2/lib/features/execution/` (Existing SDUI renderers)

## Testing & Quality Gate Plan
- Run `flutter test client_app_v2/test/features/execution/n_a_card_snapshot_test.dart`
- Run global `flutter test`

## Session Handover
To execute this phase, run the following command in a new session:
`/tier5-resume --workflow=/tier2-execute --target="docs\epic\tasks_EPIC_95_Testing_Pyramid\epic_95_phase_3b_frontend_snapshot.md" --rules="00-antigravity-core.md, 02_flutter_desktop.md"`
