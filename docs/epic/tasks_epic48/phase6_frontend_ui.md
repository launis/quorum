# Phase 6: Frontend UI Updates (Tier 2 Hardening)

## Context
**Epic:** `c:\src\quorum\docs\epic\epic48_atomization_refactor_plan 2.md`

## Architectural Invariants
- **Rule 1:** Dart Freezed Union Types (`02_flutter_desktop.md`). No manual `.when()` checks, use Dart 3 native `switch`. No null-coalescing `??` fallbacks in parsing.
- **Rule 2:** Tripartite Rendering Boundary (`01-python-backend.md`, `02_flutter_desktop.md`). No scoring math inside Riverpod or UI logic.
- **Rule 3:** Cross-Language Enum Parity. Mirror backend enums to `@JsonEnum()`.

## Targets (Modify)
- `c:\src\quorum\client_app_v2\lib\core\models\enums.dart`
- `c:\src\quorum\client_app_v2\lib\features\execution\views\`
- Relevant Riverpod State and Freezed models.

## Context (Read-Only)
- `c:\src\quorum\docs\epic\epic48_atomization_refactor_plan 2.md`
- `c:\src\quorum\.agents\rules\00-antigravity-core.md`
- `c:\src\quorum\.agents\rules\02_flutter_desktop.md`

## Milestones
### 1. Dart Freezed Models
- [x] Update or create `TDAState` as a Dart 3 Sealed Class (Union Type) with `pending`, `evaluated`, and `dlq` states as outlined in the Epic.
  ```dart
  @freezed
  sealed class TDAState with _$TDAState {
    const factory TDAState.pending() = Pending;
    const factory TDAState.evaluated({required bool passed, required String displayQuote, required String rawAnchor}) = Evaluated;
    const factory TDAState.dlq({required String userReason, required String backendTrace}) = Dlq;
  }
  ```
- [x] Ban the use of `??` operators during parsing. Unhandled states must crash via `AppErrorBoundary`.

### 2. UI Transparency & Tripartite Rendering Boundary
- [x] Update Matrix Editor to support `TDAAssertion` list.
- [x] Render `dlq` states as gray, with tooltip showing `backendTrace` directly from backend.
- [x] Update Backend's Jinja2 PDF-reports to include the same gray state (`{% if status == 'dlq' %}`) to enforce the **Strict PDF & UI Parity Mandate** (1:1 visual logic parity between Flutter rendering and PDF generation).
- [x] **ABSOLUTE BAN:** No scoring math is allowed in the UI (Riverpod or Dart models). The UI only renders `ReportDataDTO` values (`raw_score`, `normalized_score`, `system_confidence`).

### 3. Enum Parity
- [x] Ensure any new Enums (e.g. `AggregationMode`) are mapped to `@JsonEnum()` in `enums.dart`.

## Testing & Quality Gate Plan
- **Testing:** run `flutter test` for relevant widget and state parsing tests.
- **Execution:** Run `uv run python scripts/flutter_audit_loop.py client_app_v2`
- Run `cd client_app_v2; dart run build_runner build -d` to generate Freezed parsing logic.

## Documentation Update
- [x] Update `c:\src\quorum\docs\architecture\06_desktop_first_flutter_client.md` (or `07_desktop_first_flutter.md`) with `TDAState` rendering.

---
**Session Handover:**
To execute this plan, start a NEW chat session and run: `/tier2-hardening-frontend @[c:\src\quorum\docs\epic\tasks_epic48\phase6_frontend_ui.md]`
