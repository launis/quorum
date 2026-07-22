# Phase 3A: Top Navigation Refactor

## 1. Goal
Ensure the Studio Workflow Top Navigation uses a strict 3-tab layout, and `workflow_general_tab.dart` is properly decoupled. (Note: The `workflow_builder_view.dart` has already been migrated to a 3-tab layout `General`, `Inputs`, `Steps` in prior iterations, but we must verify compliance and ensure no monolithic forms remain).

## 2. Architectural Rules Applied
- **Macro-Breakpoint Standard**: LayoutBuilder must be used if responsive panes are needed.
- **Strict SDUI Rendering**: No hardcoded strings.
- **Fail-Fast Boundary**: If state is missing, crash loud.

## 3. Target Files
- TARGET: `@[c:\src\quorum\client_app_v2\lib\features\studio\views\workflow_builder_view.dart]`
- TARGET: `@[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\workflow\workflow_general_tab.dart]`

## 4. Implementation Steps
1. Verify `workflow_builder_view.dart` utilizes `DefaultTabController(length: 3)`. (Already implemented).
2. Verify `workflow_general_tab.dart` uses `AppLocalizations` for all UI strings.
3. If any legacy monolithic scrollable form code remains for the main builder, remove it. If the files are already compliant, this phase is a direct verification pass.
4. No Backend changes.

## 5. Testing & Quality Gate Plan
- Run: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/workflow_builder_view.dart --build`
- Run: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart --build`
