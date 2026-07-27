# EPIC 121: Admin Studio Output Profile SDUI Template Editor

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
>
> Server-Driven UI (SDUI) is the dominant architecture pattern for separating UI layout from business logic (Medium, 2025-2026). Industry best practice mandates that SDUI admin tools follow a **Block-Based Editor** pattern — a component palette, a canvas for arrangement, and a property inspector panel — matching the architecture used by Notion, WordPress Gutenberg, and Shopify Hydrogen. The critical success factor is that the admin editor outputs the **exact same JSON schema** the client renderer consumes, eliminating format translation bugs. Flutter's native `Draggable`/`DragTarget` widgets combined with `ReorderableListView` provide production-grade drag-and-drop without third-party dependencies.

---

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective
Provide Admin users with a visual, structured SDUI block editor within the existing Studio OutputProfile CRUD view (`@[c:\src\quorum\client_app_v2\lib\features\studio\views\output_profile_crud_view.dart]`), enabling them to construct and manage `content_blocks` for Output Profiles without requiring direct JSON editing or developer intervention.

### Problem Statement
Currently, the `content_blocks` field on `OutputProfile` is:
1. **Invisible in the Admin UI** — The existing `OutputProfileCrudView` (845 lines) manages layouts, synthesis config, visibility toggles, and metadata, but has **zero UI** for `content_blocks`. Admins cannot see, add, reorder, or edit content blocks.
2. **Data entry requires direct database manipulation** — To add a preamble `MarkdownBlock` or `HeroInsightBlock`, a developer must edit `seed_data.json` or call the REST API directly.
3. **Type-safe after EPIC 120** — Once EPIC 120 lands, `content_blocks` will be `list[AnySduiBlock]` (Python) / `List<SduiBlockDTO>` (Flutter), providing a strict typed foundation that makes a visual editor both safe and practical.

### Strategic Scope
This Epic adds **one new UI section** to the existing `OutputProfileCrudView` — a "Content Blocks Editor" card — following the same pattern as the existing `LayoutEditorCard` (`@[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\layout_editor_card.dart]`). It does NOT change the SDUI rendering pipeline, backend models, or execution flow.

### Dependency
> [!CAUTION]
> **EPIC 120 (Database-Driven SDUI Templates) is a HARD prerequisite.** This Epic cannot begin until EPIC 120 has landed and `content_blocks` is typed as `List<SduiBlockDTO>` in Flutter. Building a visual editor on top of `List<dynamic>` would violate the Zero Compromise Pledge.

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **Manual `seed_data.json` editing for `content_blocks`** — After this Epic, all `content_blocks` modifications are performed exclusively through the Admin Studio UI. Direct JSON editing of `content_blocks` in seed files is deprecated for production use (seed data retains defaults for local development only).

### Retained SSOT Invariants (What We Will RETAIN)
- **`SduiBlockDTO` sealed class** (`@[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart]` — post-EPIC 120) — The SSOT for block type definitions. The editor generates instances of this sealed class; no parallel type system is introduced.
- **`AnySduiBlock` discriminated union** (`@[c:\src\quorum\backend_v2\models\view\sdui.py#L594-L605]`) — The backend SSOT. The API accepts and validates `list[AnySduiBlock]` directly.
- **`OutputProfileCrudView`** (`@[c:\src\quorum\client_app_v2\lib\features\studio\views\output_profile_crud_view.dart]`) — The existing CRUD view is extended, NOT replaced. The Content Blocks Editor is added as a new expandable card section alongside the existing Layout Editor.
- **`LayoutEditorCard` pattern** (`@[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\layout_editor_card.dart]`) — The UI architecture pattern (card-based list with add/remove/reorder) is reused for consistency.
- **Backend REST API** — The existing `PUT /api/v2/output-profiles/{id}` endpoint already accepts `content_blocks` in the request body. No new endpoints are required.
- **Dumb Painter Principle** — The editor generates typed `SduiBlockDTO` data objects. The Flutter renderer paints them. No business logic leaks into the editor UI.

### Compliance & Modernity Gates
| Gate | Status |
|---|---|
| Pydantic V2 `ConfigDict(strict=True, extra='forbid')` | ✅ Inherited via `V2CoreBase` |
| Freezed `disallowUnrecognizedKeys: true` | ✅ Already on `SduiBlockDTO` (post-EPIC 120) |
| Cross-Domain DTO Parity | ✅ No DTO changes — reuses EPIC 120 types |
| Riverpod `@riverpod` code generation | ✅ All new state management uses `@riverpod` |
| Flutter Hooks for transient input state | ✅ Text editing via `useTextEditingController` |
| Design Token compliance | ✅ `AppSpacing`, `Theme.of(context)` — zero magic numbers |
| `AppLocalizations` for all UI strings | ✅ Zero hardcoded strings |
| Desktop Pro Tool UX | ✅ Keyboard shortcuts, hover states, focus traversal |
| Fail-Fast on invalid data | ✅ Typed sealed class enforces schema at parse time |

### Producer-Consumer Integration Check
| Producer | Consumer | Contract |
|---|---|---|
| Admin Studio Block Editor (this Epic) | `OutputProfile.contentBlocks: List<SduiBlockDTO>` | Editor produces typed `SduiBlockDTO` instances |
| `OutputProfile.contentBlocks` | Backend `PUT /api/v2/output-profiles/{id}` | Serialized via `.toJson()`, validated by `list[AnySduiBlock]` |
| Backend `content_blocks` | `BlueprintTransformer` (`@[c:\src\quorum\backend_v2\services\blueprint.py]`) | Consumed during report generation |
| Backend `content_blocks` | Flutter Execution Report Renderer | Rendered via SDUI pipeline |

---

## 3. Phased Execution Plan (Implementation Strategy)

> [!WARNING]
> **Zero New Backend Models.** This Epic reuses the typed `AnySduiBlock` / `SduiBlockDTO` foundation from EPIC 120 entirely. No new Pydantic or Freezed models are introduced. If a new block type is needed, it MUST be added to the existing `AnySduiBlock` union first (separate Epic scope).

### Phase 1: Content Blocks Editor Widget

- **Target**: `@[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\content_blocks_editor_card.dart]` [NEW]
- Create a new `ContentBlocksEditorCard` widget following the exact architectural pattern of `LayoutEditorCard`:
  - Accepts `List<SduiBlockDTO> contentBlocks` and `Function(List<SduiBlockDTO>) onChanged` callback.
  - **Block Palette**: A dropdown/button bar allowing the admin to add any block type from the `SduiBlockDTO` sealed class variants: `paragraph`, `bulletList`, `alertBox`, `heroInsight`, `markdown`, `quoteCard`, `warningCard`, `naCard`, `grid`.
  - **Block List**: A `ReorderableListView` displaying each content block as an expandable card.
  - **Per-Block Property Editor**: Each block type renders its own property form:
    - `paragraph` / `heroInsight`: `TextFormField` for `text`, chip editor for `exactQuotes`.
    - `bulletList`: Dynamic list of `SduiBulletListItemDTO` entries.
    - `alertBox`: `TextFormField` for `text`, `DropdownButtonFormField` for `severity` (`info` / `warning`).
    - `markdown`: Multi-line `TextFormField` for `text` with markdown preview.
    - `quoteCard`: `TextFormField` for `quote`, chip editor for `sourceAliases`.
    - `warningCard`: `TextFormField` for `message`.
    - `naCard`: `TextFormField` for `message`.
    - `grid`: JSON editor for `items` (deferred to raw JSON input until grid item schema stabilizes).
  - **Reorder**: `ReorderableListView` with drag handles for ordering.
  - **Delete**: `IconButton` with confirmation dialog per block.
  - **Block Type Badge**: Colored chip displaying the `block_type` discriminator value.
- All transient editing state managed via `flutter_hooks` (`useTextEditingController`).
- All UI strings from `AppLocalizations` — add required `.arb` keys.
- Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/profile --build`.

### Phase 2: Integration into OutputProfileCrudView

- **Target**: `@[c:\src\quorum\client_app_v2\lib\features\studio\views\output_profile_crud_view.dart]`
- Add a new `ContentBlocksEditorCard` section BELOW the existing `LayoutEditorCard` section in the three-pane layout.
- Wire the `contentBlocks` field from the `OutputProfile` payload to the editor.
- Ensure the `saveProfile()` function includes the updated `contentBlocks` in the `newPayload.copyWith(...)` call (currently it only copies `layouts`).
- Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views --build`.

### Phase 3: Live Preview Panel (Optional Enhancement)

- **Target**: `@[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\content_blocks_preview_panel.dart]` [NEW]
- Add an optional live preview panel that renders the current `contentBlocks` list using the same rendering logic as the execution report renderer.
- Reuse the existing execution-side SDUI block rendering widgets (extract to `shared/` if needed).
- Toggle visibility via a "Preview" button in the editor card header.
- This phase is an enhancement and can be deferred if the core editor is delivered first.

### Phase 4: Verification & E2E Integration Gate

- **Automated Unit Tests**:
  - Widget tests for `ContentBlocksEditorCard` covering: add block, delete block, reorder blocks, edit block properties, serialization round-trip.
  - Run global frontend audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/`
- **Manual Verification**:
  - Re-seed database (`uv run python backend_v2/seed/run_seed.py local`).
  - Open Admin Studio → OutputProfile CRUD → verify Content Blocks Editor renders.
  - Add a `paragraph` and `markdown` block, save, reload — verify persistence.
  - Trigger a report execution with the modified profile — verify blocks render in the report.
- **MANDATORY Final E2E REST API Verification Gate**:
  - `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- [ ] Admin users can visually add, edit, reorder, and delete `content_blocks` within an OutputProfile via the Studio CRUD view.
- [ ] All 9 `SduiBlockDTO` variants are selectable from the block palette.
- [ ] Each block type has a dedicated property editor form.
- [ ] Block ordering is persisted via `ReorderableListView` → backend `PUT` API.
- [ ] The `saveProfile()` function includes `contentBlocks` in the saved payload.
- [ ] Zero hardcoded strings — all UI text from `AppLocalizations`.
- [ ] Zero magic numbers — all spacing/sizing from Design Tokens.
- [ ] Widget tests cover add, delete, reorder, and serialization round-trip.
- [ ] Flutter audit passes: `uv run python scripts/flutter_audit_loop.py client_app_v2/`.
- [ ] Report rendering produces identical output whether `content_blocks` were set via API or via the new editor.

---

## 5. Deferred Scope (Future Epics)

> [!NOTE]
> The following features are intentionally deferred to prevent scope creep.

- **Visual Drag-and-Drop from Palette to Canvas** — Phase 1 uses a "Add Block" dropdown + `ReorderableListView`. A full visual drag-from-palette-to-canvas experience (à la Notion/Gutenberg) is a UX enhancement that can be layered on later.
- **`SduiGridBlock` Property Editor** — The `grid` block type's `items` field is `list[Any]` (pre-existing strictness leak from EPIC 120 deferred scope). Until the grid item schema is typed, the editor exposes a raw JSON text field for this block type.
- **Content Block Templates / Presets** — Allowing admins to save and reuse named block configurations (e.g., "Standard Preamble Template") is a separate feature.
- **Multi-Language Preview** — Previewing content blocks in different locales requires ICU template resolution infrastructure not yet available in the Studio frontend.
