# Implementation Plan: EPIC 90 Phase 5 - Frontend & PDF Pariteetti (SDUI Renderöinti)

Source: Epic Phase 5, Step 5.1, 5.2, 5.3, 5.4

## Goal
Implement Server-Driven UI (SDUI) rendering across Flutter and PDF generators, reacting blindly to the backend's `visual_intent` and `chart_display_label`.

## Target Files (Modify)
- `client_app_v2/lib/core/models/enums.dart`
- `client_app_v2/lib/features/execution/models/scorecard_dto.dart`
- `client_app_v2/lib/features/execution/widgets/atom_matrix_table_widget.dart` (or radar chart widget)
- `backend_v2/templates/report_template.jinja2`
- `tests/unit/test_enum_parity.py` (or equivalent backend test for enum parity)

## Context Files (Read-Only)
- `backend_v2/models/v2_core.py`

## Implementation Steps
1. Add `VisualIntent` to `enums.dart` mapping exactly to backend Literal values (`success`, `warning`, `critical_override`, `info`).
2. Update Dart DTOs with `chartDisplayLabel` and `visualIntent`. Run `build_runner`.
3. Update Flutter radar chart / scorecard to display `chartDisplayLabel` natively, mapping `visualIntent` to colors from `AppColors` theme. Remove old string-truncation logic from Dart.
4. Update `report_template.jinja2` to map `visual_intent` to dynamic CSS classes (e.g. `<div class="card intent-{{ atom.evaluation.visual_intent }}">`) and use `chart_display_label`.
5. Ensure `test_enum_parity.py` in backend checks `VisualIntent`.

## Hardening Rules & Architectural Invariants (from hardening.xml & .agents/rules)
- **Rule 44 (Cross Language Enum Parity):** `VisualIntent` in Dart must 100% match Python definitions. Backed by automated regex testing.
- **Rule 30 (Tripartite Rendering Boundary):** Backend produces raw DTOs only; Jinja2 and Flutter handle all visual rendering independently.
- **Rule 40 (No String L10n):** UI components must resolve colors/text via theme tokens and Enums, not hardcoded strings.

## Testing & Quality Gate Plan
- **Frontend Verification:** Run `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`
- **Backend Verification:** Run `uv run python scripts/backend_audit_loop.py tests/unit/test_enum_parity.py --test`
- Verify UI and PDF output visually matches.

---
<!-- Session Handover -->
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_90_Output_renewal_tracker.md`
