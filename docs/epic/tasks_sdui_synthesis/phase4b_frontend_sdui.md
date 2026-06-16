# Epic SDUI Synthesis - Phase 4b: Flutter UI Refactoring
Source: Epic Phase 4

Flutter-clientin on luovuttava vanhasta vapaamuotoisesta Markdown-widgetistä ja siirryttävä puhdastyyliseen SDUI-pohjaiseen `switch`-rakenteeseen renderöidessään synteesin sisältöblokkeja.

## Proposed Changes
### Flutter Desktop Client
#### [MODIFY] [enums.dart](file:///c:/src/quorum/client_app_v2/lib/core/models/enums.dart)
- [x] Add new `SduiBlockType` enums: `paragraph`, `bullet_list`, `alert_box`.

#### [MODIFY] [report_data_dto.dart](file:///c:/src/quorum/client_app_v2/lib/features/execution/models/report_data_dto.dart)
- [x] Delete `synthesized_markdown`.
- [x] Implement Freezed `content_blocks: List<SduiBlockDTO>` pattern utilizing polymorphic parsing based on `block_type` (Riverpod `@Freezed`).

#### [NEW] [sdui_block_renderer.dart](file:///c:/src/quorum/client_app_v2/lib/features/execution/views/widgets/sdui_block_renderer.dart)
- [x] Create a new Widget that natively iterates over `content_blocks` utilizing Dart 3 pattern matching `switch (block)`.
- [x] Use native Flutter `Text()`, `Column()`, and styling to render paragraph, bullet_list, and alert_box.
- [x] Render `citations` as clickable native badges appended to the paragraph text.

#### [MODIFY] View Files
- [x] Replace `MarkdownWidget` with `SDUIBlockRenderer`. Do NOT implement legacy Markdown backwards compatibility (Rule #71 No Legacy Mandate).

## Architectural Rules Implemented
- **Flutter Rule: Sized Box Shrink Ban**: Ensure missing blocks crash natively rather than hiding behind empty UI.
- **Flutter Rule: Freezed When Ban**: Exclusively use Dart 3 native `switch` expressions (pattern matching) to map the SDUI types, no `.map()` or `.when()`.

## Testing & Quality Gate Plan
### UI Widget Tests
- Test parsing and rendering via `uv run python scripts/flutter_audit_loop.py client_app_v2 --build` and `flutter test`.

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_sdui_synthesis_tracker.md`
