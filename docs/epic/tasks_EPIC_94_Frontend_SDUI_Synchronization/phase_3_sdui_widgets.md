# Phase 3: SDUI Widget Rendering Components

## Context & Objective
The objective of this phase is to implement new, Macro-Breakpoint compliant Flutter Widgets that natively consume the Phase 1 Freezed Models (`ReportDataDto`, `AtomResultDto`) and Phase 2 Riverpod Providers (O(1) Data Binding). The legacy monolithic `report_renderer_widget.dart` will be replaced with a decoupled `ReportRendererV2Widget` that iteratively renders isolated `SduiNodeRenderer` instances.

## User Review Required
> [!IMPORTANT]
> The legacy `ReportDataDTO` and its renderer (`report_renderer_widget.dart`) are being phased out. We are building the new V2 components alongside the old ones to ensure zero downtime before deletion in Phase 4. Please confirm this parallel construction strategy is approved.

## Architectural Invariants
1. **Riverpod SRP Boundary**: Widgets MUST ONLY render. The `SduiNodeRenderer` must watch providers to get its state; DO NOT pass massive object trees down the widget tree.
2. **Fail-Fast Boundary**: Do not use `SizedBox.shrink()` to hide broken components. Let `AppErrorBoundary` catch widget rendering failures natively.
3. **Dart 3 Switch Expressions**: Must use native `switch` on `SDUIComponentType` for declarative UI routing.
4. **Horizontal Overflow Prevention**: All dynamic text within Flex boundaries MUST be wrapped in `Expanded` or `Flexible` with `TextOverflow.ellipsis`.

## Proposed Changes

### UI Renderers

#### [NEW] [sdui_node_renderer.dart](file:///c:/src/quorum/client_app_v2/lib/features/execution/views/widgets/sdui_node_renderer.dart)
- Create a `ConsumerWidget` named `SduiNodeRenderer` that accepts a `String nodeId`.
- Use `ref.watch` against the providers created in Phase 2 to retrieve both the static `HydratedAtomDto` and the live `AtomResultDto` using O(1) lookups.
- Implement a Dart 3 `switch` expression on `hydratedAtom.sduiComponent` (`SDUIComponentType`) to branch rendering into specific layout functions (e.g., `booleanCard`, `extractedValueCard`, `errorCard`, `nACard`).
- Adhere to the "Macro-Breakpoint" standard using `LayoutBuilder` for desktop compatibility.

#### [NEW] [report_renderer_v2_widget.dart](file:///c:/src/quorum/client_app_v2/lib/features/execution/views/widgets/report_renderer_v2_widget.dart)
- Create `ReportRendererV2Widget` which takes the root `ReportDataDto` payload.
- Build the executive summary using `globalSynthesis` and `globalMetrics`.
- Instead of relying on nested layout arrays, iterate natively over the topologically sorted `results` flat array. For each `AtomResultDto`, instantiate an `SduiNodeRenderer(nodeId: atom.nodeId)`.
- Re-integrate `DiagnosticScorecardWidget` and `XAIEvidenceBox`. Since the V2 payload decoupled matrices, create a `scorecardProvider(executionId)` that fetches from `executionClient.getScorecard(executionId)`. Wrap `DiagnosticScorecardWidget` in a Consumer to render it asynchronously at the bottom of the scroll view.

#### [MODIFY] [execution_view.dart](file:///c:/src/quorum/client_app_v2/lib/features/execution/views/execution_view.dart)
- Update the live execution screen to parse `record['report_data']` as the new `ReportDataDto` structure.
- Replace the legacy `ReportRendererWidget` with the newly created `ReportRendererV2Widget`.

## Verification Plan

### Automated Tests
- Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/widgets` to enforce Freezed strictness and Dart analysis formatting.

### Manual Verification
- Recompile the desktop client and launch a live workflow execution.
- Observe that the UI gracefully maps `SDUIComponentType` cards to the screen without triggering `RenderFlex` layout overflow errors.
- Ensure live updates seamlessly update individual `SduiNodeRenderer` blocks without rebuilding the entire ListView.

---

## Session Handover Context
**Achieved**: Designed the architectural plan for Phase 3 SDUI Widget Rendering, enforcing O(1) Riverpod reads and Dart 3 destructuring.
**Learned**: The UI utilizes `SDUIComponentType` to map cards in the V2 payload.
**Remaining**: Execution of Phase 3, followed by Phase 4 cleanup.

## Next Session Resume Command
To execute this Epic iteratively, start a NEW chat session and run the following command:
`/tier5-resume --workflow=/tier2-execute --target="c:\src\quorum\docs\epic\EPIC_94_Frontend_SDUI_Synchronization_tracker.md, c:\src\quorum\docs\epic\tasks_EPIC_94_Frontend_SDUI_Synchronization\phase_3_sdui_widgets.md" --rules="c:\src\quorum\.agents\rules\00-antigravity-core.md, c:\src\quorum\.agents\rules\02_flutter_desktop.md"`
