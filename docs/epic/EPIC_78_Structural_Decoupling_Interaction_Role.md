# Structural Decoupling for Interaction Role Localization

The goal is to implement a strict "Structural Decoupling" pattern (Option 1) for the interaction role classification (`Passenger`, `Navigator`, `Driver`, `Architect`). Instead of instructing the LLM to freely translate and inject the title (e.g., `**Käyttäjän Rooli: Arkkitehti**`) into the synthesized markdown, we will pass the role ID natively from the Backend through to the Frontend via `ReportDataDTO`, and let the Flutter client localize the string strictly using `.arb` files. This complies with the "No-String Mandate".

## Proposed Changes

### 1. Backend Core DTO (`backend_v2/models/v2_core.py`)
- Add a new field `interaction_role: str | None = Field(default=None)` to `ReportDataDTO`.

### 2. Backend Service (`backend_v2/services/blueprint.py`)
- During the construction of `ReportDataDTO`, extract the assigned interaction role from the execution state's `context_variables` (`interaction_analysis.role_classification`).
- Map the value to the `interaction_role` field on the DTO.

### 3. Database Seed Data (`backend_v2/seed/seed_data.json`)
- Locate the system prompt for the "Senior Executive Coach" (around line 8446).
- Remove the instruction to explicitly highlight the user's role with a title (`**Käyttäjän Rooli: X**`).
- Update the instruction for PARAGRAPH 2 to focus *only* on the justification and the quotes, since the title itself will be handled natively by the UI.
- Ensure the prompt doesn't ask the LLM to translate the role name arbitrarily.

### 4. Frontend Localization (`client_app_v2/lib/l10n/app_fi.arb` & `app_en.arb`)
- Add specific `.arb` keys for each role classification and the title:
  - `rolePassenger` (Matkustaja / Passenger)
  - `roleNavigator` (Suunnistaja / Navigator)
  - `roleDriver` (Ohjaaja / Driver)
  - `roleArchitect` (Arkkitehti / Architect)
  - `userRoleTitle` (Käyttäjän Rooli: / User Role:)

### 5. Frontend DTO (`client_app_v2/lib/features/execution/models/report_data_dto.dart`)
- Add `interaction_role` to the Dart `ReportDataDTO` model.

### 6. Frontend UI (`client_app_v2/lib/features/execution/views/widgets/report_renderer_widget.dart`)
- Update the widget that displays `payload.synthesizedMarkdown`.
- If `payload.interactionRole` is present, render a localized title element (e.g., `**[userRoleTitle] [mapped_role]**`) above the synthesized markdown container.

## Verification Plan
1. Re-seed the local database (`python scripts/run_seed.py local`).
2. Run Dart build runner (`dart run build_runner build -d`) to regenerate Dart models and localization files.
3. Validate through backend and frontend audit loops (`python scripts/backend_audit_loop.py . --test`).
4. Ensure the UI renders the translated role name strictly from `.arb` and the justification strictly from the LLM without double-printing the title.
