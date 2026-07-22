# Phase 3B: Output Profile Sub-Tab Restructuring

## 1. Goal
Restructure the Output Profile Admin UI (`profile_editor_view.dart`) from a legacy monolithic scrollable form into clear sub-tabs: 1) Perustiedot (General), 2) XAI (Extensions), 3) Raporttipohjat (Layouts).

## 2. Architectural Rules Applied
- **Macro-Breakpoint Standard**: Component-level constraints.
- **No Magic Strings**: All tab titles must use `AppLocalizations`.
- **Form State Preservation**: The Riverpod `workflowFormProvider` must remain the SSOT.

## 3. Target Files
- TARGET: `@[c:\src\quorum\client_app_v2\lib\features\studio\views\profile_editor_view.dart]`
- CONTEXT: `@[c:\src\quorum\client_app_v2\lib\l10n\app_en.arb]` (for translation keys)
- CONTEXT: `@[c:\src\quorum\client_app_v2\lib\l10n\app_fi.arb]` (for translation keys)

## 4. Implementation Steps
1. In `profile_editor_view.dart`, modify `_buildProfileCard` to utilize a `DefaultTabController(length: 3)`.
2. Replace the monolithic `Column` with a `Column` containing a `TabBar` and a strictly bounded `SizedBox` (e.g. `height: 600`) holding a `TabBarView`.
3. **Tab 1 (Perustiedot / General)**:
   - Move the `profileId` row, Display Name `I18nTextField`, and Display Scale `DropdownButton` into this tab.
4. **Tab 2 (XAI / Extensions)**:
   - Move the Block Level Extensions (`XaiExtensionType` checkboxes), Workflow Level Extensions, and Max Extension Items slider into this tab.
5. **Tab 3 (Raporttipohjat / Layouts)**:
   - Move the `LayoutEditorCard` into this tab.
6. Ensure the `AppLocalizations` has keys for these new tabs. If missing, instruct the agent to add them to `app_en.arb` and `app_fi.arb` (e.g., `profileTabGeneral`, `profileTabXai`, `profileTabLayouts`).
7. Ensure the state mutation (`rebuildProfile`) remains intact and seamlessly triggers form updates across tab switches.

## 5. Testing & Quality Gate Plan
- Run: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/profile_editor_view.dart --build`
