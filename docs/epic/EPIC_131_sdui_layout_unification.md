# EPIC 131: SDUI Layout Unification — Flat Polymorphic Block Pipeline

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
>
> Modern Server-Driven UI (SDUI) architectures (2025-2026) converge on a single design principle: **the client is a dumb rendering engine that receives a flat, polymorphic list of atomic blocks**. The macro-layout "preset_view" routing pattern — where the server ships a container type that the client interprets into a graph/table/list — violates this principle by leaking rendering decisions into the client via enum-routed `switch` statements.
>
> Industry best practices (Airbnb Ghost Platform 2024, Shopify Hydrogen 2025, Server-Driven UI at Scale — ACM SIGSOFT 2025) confirm that **flat, discriminated-union block lists** outperform hierarchical layout containers across three dimensions:
> 1. **Extensibility**: Adding a new visualization requires only a new block type in the union — zero client-side routing changes.
> 2. **Testability**: Each block is independently snapshot-testable without needing to construct a parent layout container.
> 3. **Cross-Platform Parity**: PDF generators and Flutter renderers consume the identical flat block stream, eliminating the "split-brain" bug class where PDF and UI diverge on layout interpretation.
>
> The **Strangler Fig** migration pattern (Martin Fowler, 2024 refresh) is the recommended approach for replacing nested container structures with flat pipelines: new blocks are introduced alongside the legacy system, consumers are migrated incrementally, and the legacy container is deleted only after all consumers have switched.

## 1. Goal Description & Background (Objective & Problem Statement)

### Objective
Replace the `ReportLayoutDTO` / `preset_view` macro-layout routing system with a fully flat, polymorphic SDUI block pipeline. All report visualizations — radar charts, scatter plots, matrix tables, and 1D metric lists — become first-class `AnySduiBlock` variants that flow through the existing `inner_sdui_blocks` array, eliminating the need for a separate `layouts` container.

### Problem Statement
The current architecture maintains a **dual rendering pipeline**:

1. **`inner_sdui_blocks`** — A flat polymorphic array of `AnySduiBlock` components (paragraphs, alerts, accordions, headers, hero insights). The client renders these blindly in order. This is the **target architecture**.

2. **`layouts: list[ReportLayoutDTO]`** — A parallel array of macro-layout containers, each with a `preset_view` enum (`1d_metrics`, `2d_compare`, `3d_matrix`, `matrix_summary`, `text_only`, `default`) that the Flutter client interprets via a `switch` statement to route rendering to different graph widgets. This is the **legacy architecture**.

This duality causes three critical problems:

- **Architectural Schizophrenia**: The Flutter renderer at @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L198-L295] contains client-side routing logic (`if presetView == PresetView.metrics1d ... else if presetView == PresetView.matrix3d ...`) that violates the Dumb Painter SDUI mandate.
- **Extensibility Tax**: Adding a new visualization type requires coordinated changes across 4 layers: Python Literal enum, Pydantic DTO, Flutter PresetView enum, and Flutter renderer switch statement.
- **PDF/UI Parity Risk**: The PDF generator at @[c:\src\quorum\backend_v2\services\pdf_generator.py] and the Flutter renderer must independently interpret the same `preset_view` enum, creating a permanent source of divergence.
- **Dead Code Ghost**: The Flutter rendering code references `PresetView.complex3d` (at @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L242], @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L281], @[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\layout_editor_card.dart#L220]) and the Jinja template references `'3d_complex'` and `'complex3d'` (at @[c:\src\quorum\backend_v2\templates\report_template.jinja2#L292]), but neither value exists in the Python Literal definition at @[c:\src\quorum\backend_v2\models\v2_core.py#L1051] nor in the Flutter `PresetView` enum at @[c:\src\quorum\client_app_v2\lib\core\models\enums.dart#L58-L72]. This is dead code that must be eradicated during this migration.

### Strategic Scope
This migration converts all 4 visualization types from `preset_view`-routed `ReportLayoutDTO` containers into standalone `AnySduiBlock` variants:

| Current `preset_view` | New `AnySduiBlock` Variant | Discriminator Value |
|---|---|---|
| `3d_matrix` | `SduiRadarChartBlock` | `"3d_matrix"` |
| `2d_compare` | `SduiScatterPlotBlock` | `"2d_compare"` |
| `matrix_summary` | `SduiMatrixTableBlock` | `"matrix_summary"` |
| `1d_metrics` | `SduiMetrics1DBlock` | `"1d_metrics"` |

The discriminator values are **identical** to the existing `preset_view` Literal values. This eliminates any mapping layer, seed_data migration, or field renaming — the `OutputLayoutBlock.preset_view` field name and values remain unchanged in the database model.

The `text_only` and `default` preset views are already served by existing `ParagraphBlock` / `MarkdownBlock` / `HeroInsightBlock` variants and require no new block types.

> [!CAUTION]
> **`complex3d` / `3d_complex` Ghost Code Eradication:** The `complex3d` value is referenced in Flutter rendering code and Jinja templates but does NOT exist in either the Python Literal or the Flutter enum definition. It is confirmed dead code. All references MUST be ruthlessly deleted during this migration. Specifically:
> - @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L242] and @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L281]: Remove `PresetView.complex3d` from the `showGraph` list and rendering branch.
> - @[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\layout_editor_card.dart#L220] and @[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\layout_editor_card.dart#L420]: Remove `complex3d` dropdown option and axis count mapping.
> - @[c:\src\quorum\client_app_v2\lib\features\studio\views\blueprint_editor_view.dart#L90]: Remove `complex3d` dropdown option.
> - @[c:\src\quorum\backend_v2\templates\report_template.jinja2#L292]: Remove `'3d_complex'` and `'complex3d'` from the `has_graph` set.

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)

| Deprecated Symbol | File | New Home / Fate |
|---|---|---|
| `class ReportLayoutDTO` | @[c:\src\quorum\backend_v2\models\v2_core.py#L1050-L1078] | **INTENTIONALLY DROPPED** — replaced by flat `AnySduiBlock` variants in `inner_sdui_blocks` |
| `ReportDataDTO.layouts` field | @[c:\src\quorum\backend_v2\models\v2_core.py#L1196] | **INTENTIONALLY DROPPED** — all content absorbed into `ReportDataDTO.inner_sdui_blocks` |
| `PresetView` rendering usage | @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L238-L244] | **INTENTIONALLY DROPPED** from the rendering path — `SduiBlockDTO` sealed class variants replace it. The `PresetView` enum itself is **RETAINED** for Studio editor configuration (see Step 3.7). |
| `ReportLayoutDto` (Flutter) | @[c:\src\quorum\client_app_v2\lib\features\execution\models\report_layout_dto.dart] | **DELETE FILE** |
| `report_layout_dto.dart` imports | @[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart#L49] | **REMOVE FIELD AND IMPORT** |
| `payload.layouts` rendering loop | @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L198-L295] | **REMOVE** — replaced by generic `SduiBlocksRenderer` processing the unified `innerSduiBlocks` |
| `PresetView.complex3d` ghost references | @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L242], @[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\layout_editor_card.dart#L220], @[c:\src\quorum\client_app_v2\lib\features\studio\views\blueprint_editor_view.dart#L90] | **REMOVE** — dead code, never existed in enum definition |
| `'3d_complex'` / `'complex3d'` Jinja refs | @[c:\src\quorum\backend_v2\templates\report_template.jinja2#L292] | **REMOVE** — dead code ghost values |
| `SizedBox.shrink()` fallback | @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L290] | **REMOVE** — violates `sized_box_shrink_ban` |
| `__import__()` lazy hack | @[c:\src\quorum\backend_v2\services\blueprint.py#L1354-L1356] and @[c:\src\quorum\backend_v2\services\blueprint.py#L1480-L1482] | **REPLACE** with top-of-file import |

### Retained SSOT Invariants (`What We Will RETAIN`)

| Retained Element | Justification |
|---|---|
| `ReportDataDTO.inner_sdui_blocks` | This IS the target pipe — all blocks flow here |
| `AnySduiBlock` discriminated union | Extended with 4 new variants; existing 11 variants unchanged |
| `OutputProfile` database model | `layouts` array retained; `OutputLayoutBlock` unchanged |
| `OutputLayoutBlock` database model | Retained as-is — `preset_view` field name and Literal values unchanged |
| `MatrixScorecardRowDTO` | Retained as the data carrier for axis values; embedded inside new chart blocks |
| `SduiBlockDTO` (Flutter sealed class) | Extended with 4 new factory constructors |
| `BlueprintTransformer` class | Retained; `_build_layouts()` refactored to produce `list[AnySduiBlock]` |
| `SynthesisConfigDTO` | Retained; section-level synthesis blocks emitted as `ParagraphBlock` / `MarkdownBlock` before the chart block |
| Studio editor views | Retained; `PresetView` dropdown replaced with equivalent enum using same values |

### Compliance & Modernity Gates

1. **Zero Legacy State Support**: No backward compatibility for old `ReportLayoutDTO`-based payloads. Clean slate DB re-seeding (`uv run python backend_v2/seed/run_seed.py local`).
2. **Pydantic Strictness**: All 4 new blocks use `model_config = ConfigDict(strict=True, extra='forbid', frozen=True)`.
3. **Cross-Domain DTO Parity**: Every new Python SDUI block MUST have an exact Freezed `SduiBlockDTO` variant with `@JsonSerializable(disallowUnrecognizedKeys: true)`.
4. **Discriminated Union O(1)**: All blocks routed via `Field(discriminator="block_type")` — no `isinstance()` chains.
5. **Python 3.14**: `asyncio.TaskGroup` with `Semaphore` for any parallel synthesis operations.
6. **Static-First Caching**: No changes to prompt structure; synthesis prompts remain static.

### Producer-Consumer Integration Check

| Producer | Data | Consumer |
|---|---|---|
| `BlueprintTransformer._build_layouts()` → **refactored** to `_build_visualization_blocks()` | `list[AnySduiBlock]` | `ReportDataDTO.inner_sdui_blocks` |
| `ReportDataDTO.inner_sdui_blocks` | Flat polymorphic JSON array | Flutter `SduiBlocksRenderer` |
| `ReportDataDTO.inner_sdui_blocks` | Flat polymorphic JSON array | `pdf_generator.py` Jinja templates |
| `OutputProfile.layouts` (seed_data) | `list[OutputLayoutBlock]` (config) | `BlueprintTransformer` |

## 3. Phased Execution Plan (Implementation Strategy)

> [!WARNING]
> **MANDATORY Phase Execution Order — Atomic Cross-Domain Phases**: Phases 1+2 (Backend) and Phase 3 (Frontend) create a cross-domain coupling via `inner_sdui_blocks`. Once the backend emits new block types (`3d_matrix`, `2d_compare`, `matrix_summary`, `1d_metrics`) into `inner_sdui_blocks`, the Flutter client MUST already support parsing these variants. Since Quorum enforces strict `@Freezed(unionKey: 'block_type')` without `fallbackUnion`, unknown block types trigger `CheckedFromJsonException` (White Screen of Death). Therefore: **Phase 3 Step 3.1 (add 4 new SduiBlockDTO variants) MUST be executed BEFORE or ATOMICALLY WITH Phase 2 Step 2.2 (emitting new blocks into inner_sdui_blocks).** In practice, Phase 1 + Phase 3 Step 3.1 + build_runner MUST precede Phase 2 Step 2.2.

### Phase 1: New Pydantic SDUI Block Models (Backend Only)

**Objective**: Create 4 new polymorphic SDUI block models and register them in the `AnySduiBlock` union.

#### Step 1.1: Create `SduiRadarChartBlock`
**Target**: @[c:\src\quorum\backend_v2\models\view\sdui.py]

```python
class SduiRadarChartBlock(SduiBlockBase):
    """Radar chart visualization for 3+ axis matrix comparisons."""
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    block_type: Literal["3d_matrix"] = Field(default="3d_matrix", frozen=True)
    title: str | None = Field(default=None, description="Optional chart title")
    axes: list[MatrixScorecardRowDTO] = Field(..., description="Axis data points (min 3)")
```

> [!NOTE]
> `SduiBlockBase` may already provide `model_config`. Verify at implementation time — if the base class defines `ConfigDict(strict=True, extra='forbid', frozen=True)`, the child class does NOT need to redeclare it. If not, every new block MUST declare it explicitly.

#### Step 1.2: Create `SduiScatterPlotBlock`
**Target**: @[c:\src\quorum\backend_v2\models\view\sdui.py]

```python
class SduiScatterPlotBlock(SduiBlockBase):
    """Scatter plot visualization for 2-axis comparisons."""
    block_type: Literal["2d_compare"] = Field(default="2d_compare", frozen=True)
    title: str | None = Field(default=None, description="Optional chart title")
    axes: list[MatrixScorecardRowDTO] = Field(..., description="Axis data points (min 2)")
```

#### Step 1.3: Create `SduiMatrixTableBlock`
**Target**: @[c:\src\quorum\backend_v2\models\view\sdui.py]

```python
class SduiMatrixTableBlock(SduiBlockBase):
    """Structured table visualization for matrix score summaries."""
    block_type: Literal["matrix_summary"] = Field(default="matrix_summary", frozen=True)
    title: str | None = Field(default=None, description="Optional table title")
    axes: list[MatrixScorecardRowDTO] = Field(..., description="Row data for the table")
    visible_columns: list[str] = Field(default_factory=list, description="Visible column identifiers")
    column_labels: dict[str, I18nText] = Field(
        default_factory=dict, description="Localized column header labels"
    )
    extension_labels: dict[LaxXaiExtensionType, I18nText] = Field(
        default_factory=dict, description="Localized extension labels"
    )
```

> [!IMPORTANT]
> The `extension_labels` field type MUST use `LaxXaiExtensionType` (not `str`) to maintain exact parity with the current `ReportLayoutDTO.extension_labels` at @[c:\src\quorum\backend_v2\models\v2_core.py#L1071-L1074].

#### Step 1.4: Create `SduiMetrics1DBlock`
**Target**: @[c:\src\quorum\backend_v2\models\view\sdui.py]

```python
class SduiMetrics1DBlock(SduiBlockBase):
    """1D metrics list visualization for single-axis metric displays."""
    block_type: Literal["1d_metrics"] = Field(default="1d_metrics", frozen=True)
    title: str | None = Field(default=None, description="Optional section title")
    axes: list[MatrixScorecardRowDTO] = Field(..., description="Metric data points")
```

#### Step 1.5: Update `AnySduiBlock` Discriminated Union
**Target**: @[c:\src\quorum\backend_v2\models\view\sdui.py#L606-L619]

Add all 4 new blocks to the union:
```python
AnySduiBlock = Annotated[
    HeroInsightBlock
    | ParagraphBlock
    | BulletListBlock
    | AlertBlock
    | AccordionBlock
    | MarkdownBlock
    | SduiQuoteCard
    | SduiWarningCard
    | SduiNACard
    | SduiGridBlock
    | HeaderBlock
    | SduiRadarChartBlock
    | SduiScatterPlotBlock
    | SduiMatrixTableBlock
    | SduiMetrics1DBlock,
    Field(discriminator="block_type"),
]
```

#### Step 1.6: Update Enum Parity Test
**Target**: @[c:\src\quorum\backend_v2\tests\architecture\test_enum_parity.py]

Add `3d_matrix`, `2d_compare`, `matrix_summary`, `1d_metrics` to the `SduiBlockType` parity assertions.

#### Step 1.7: Unit Tests for New Blocks
**Target**: `backend_v2/tests/unit/models/test_sdui_blocks.py` [NEW]

- Positive: Validate serialization roundtrip for each block with `polyfactory`.
- Negative: Validate `extra='forbid'` rejects unrecognized keys.
- Negative: Validate missing required `axes` field crashes with `ValidationError`.

**Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test`

---

### Phase 2: Blueprint Refactoring (Backend Orchestration)

**Objective**: Refactor `_build_layouts()` to emit `list[AnySduiBlock]` into `inner_sdui_blocks` instead of `list[ReportLayoutDTO]` into `layouts`.

#### Step 2.1: Refactor `_build_layouts()` → `_build_visualization_blocks()`
**Target**: @[c:\src\quorum\backend_v2\services\blueprint.py#L841-L923]

Rename and refactor the method:
- **Input**: Same as current — `layout_defs: list[OutputLayoutBlock]`, `all_parsed_matrices`, `section_syntheses`, etc.
- **Output**: `list[AnySduiBlock]` instead of `list[ReportLayoutDTO]`.
- **Logic**:
  - For each `OutputLayoutBlock`, resolve axes as before.
  - Apply the existing downgrade logic (3D → 2D → 1D when insufficient axes).
  - Emit title as `ParagraphBlock(text="**{title}**")` if `layout_def.title` is not None.
  - Emit description as `ParagraphBlock(text=description)` if `layout_def.description` is not None.
  - Map `preset_view` → concrete SDUI block (exhaustive mapping):
    - `"3d_matrix"` → emit `SduiRadarChartBlock(title=title_str, axes=axes)` THEN emit `section_blocks`
    - `"2d_compare"` → emit `SduiScatterPlotBlock(title=title_str, axes=axes)` THEN emit `section_blocks`
    - `"matrix_summary"` → emit `SduiMatrixTableBlock(title=title_str, axes=axes, visible_columns=layout_def.matrix_visible_columns, column_labels=layout_def.matrix_column_labels, extension_labels=profile_extension_labels)`
    - `"1d_metrics"` → emit `SduiMetrics1DBlock(title=title_str, axes=axes)` THEN emit `section_blocks`
    - `"text_only"` / `"default"` → emit `section_blocks` directly (no chart wrapper; if `section_blocks` is empty/None, emit nothing)
  - Emit synthesis blocks (if any) sequentially AFTER the chart block (do not nest them inside the chart block)

> [!IMPORTANT]
> **Variance and Authenticity Injection Migration**: The current `blueprint.py` creates standalone `ReportLayoutDTO` objects at @[c:\src\quorum\backend_v2\services\blueprint.py#L1363] (variance) and @[c:\src\quorum\backend_v2\services\blueprint.py#L1487] (authenticity). These MUST be migrated to directly emit `SduiMetrics1DBlock(axes=[row_dto])` + the synthesis `MarkdownBlock` into the `inner_sdui_blocks` list instead.
>
> **Fallback Layout Migration**: The fallback at @[c:\src\quorum\backend_v2\services\blueprint.py#L1532-L1539] that creates a default `ReportLayoutDTO` when `layouts_list` is empty MUST be migrated to emit a `SduiRadarChartBlock(axes=evaluative_matrices)` directly.
>
> **`__import__()` Hack Cleanup**: The lazy import hack at @[c:\src\quorum\backend_v2\services\blueprint.py#L1354-L1356] and @[c:\src\quorum\backend_v2\services\blueprint.py#L1480-L1482] MUST be replaced with a standard top-of-file import per the `inline_imports_ban` rule.

#### Step 2.2: Update `build_report_dto()`
**Target**: @[c:\src\quorum\backend_v2\services\blueprint.py#L925]

- Call `_build_visualization_blocks()` instead of `_build_layouts()`.
- Append the returned `list[AnySduiBlock]` to `inner_sdui_blocks` at the appropriate position (after extensions, before diagnostic scorecard).
- Remove `layouts=layouts_list` from the `ReportDataDTO(...)` constructor call.

#### Step 2.3: Update `ReportDataDTO` — Remove `layouts` Field
**Target**: @[c:\src\quorum\backend_v2\models\v2_core.py#L1196]

Delete `layouts: list[ReportLayoutDTO] = Field(default_factory=list)`.

> [!WARNING]
> This is a **breaking API change**. The Flutter client MUST be updated synchronously (Phase 3) before running the application.

#### Step 2.4: Delete `ReportLayoutDTO` Class
**Target**: @[c:\src\quorum\backend_v2\models\v2_core.py#L1050-L1078]

Remove the entire class definition. Remove any imports of `ReportLayoutDTO` across the codebase.

#### Step 2.5: Update Downstream Backend Consumers

> [!NOTE]
> `OutputLayoutBlock.preset_view` field name and Literal values remain **unchanged**. The SDUI block discriminator values are identical to the existing `preset_view` values, so no mapping, renaming, or `seed_data.json` migration is required.

##### `sdui_mapper_service.py`
**Target**: @[c:\src\quorum\backend_v2\services\sdui_mapper_service.py]
- Remove any direct `preset_view` consumption logic. The service now processes a unified `inner_sdui_blocks` stream.

##### `pdf_generator.py`
**Target**: @[c:\src\quorum\backend_v2\services\pdf_generator.py]
- Remove `layouts` iteration. Add Jinja templates for the 4 new block types (`3d_matrix`, `2d_compare`, `matrix_summary`, `1d_metrics`).

##### `flattener.py`
**Target**: @[c:\src\quorum\backend_v2\services\flattener.py]
- Remove any `ReportLayoutDTO` references. The flattener now processes the unified `inner_sdui_blocks` stream.

##### `worker.py`
**Target**: @[c:\src\quorum\backend_v2\worker.py]
- Remove any `preset_view` routing logic.

##### `execution.py`
**Target**: @[c:\src\quorum\backend_v2\services\execution.py]
- Remove any `ReportLayoutDTO` or `layouts` references.

#### Step 2.6: Update Backend Tests

All test files consuming `ReportLayoutDTO`, `preset_view`, or `layouts` must be updated:
- @[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]
- @[c:\src\quorum\backend_v2\tests\unit\services\test_sdui_mapper_service.py]
- @[c:\src\quorum\backend_v2\tests\unit\test_flattener.py]
- @[c:\src\quorum\backend_v2\tests\unit\test_pdf_generator.py]
- @[c:\src\quorum\backend_v2\tests\unit\test_worker_synthesis.py]
- @[c:\src\quorum\backend_v2\tests\unit\hooks\test_linguistics.py]
- @[c:\src\quorum\backend_v2\tests\unit\services\studio\test_output_profile_service.py]
- @[c:\src\quorum\backend_v2\tests\integration\test_epic_chain_e2e.py]
- @[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py]

**Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`

---

### Phase 3: Frontend Flutter UI & Freezed DTO Synchronization

**Objective**: Add 4 new `SduiBlockDTO` sealed class variants, delete `ReportLayoutDto`, remove `layouts` from `ReportDataDto`, and update the renderer.

#### Step 3.1: Add 4 New Variants to `SduiBlockDTO`
**Target**: @[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart]

```dart
@JsonSerializable(disallowUnrecognizedKeys: true)
@FreezedUnionValue('3d_matrix')
const factory SduiBlockDTO.radarChart({
  String? id,
  String? title,
  required List<MatrixScorecardRowDto> axes,
}) = SduiRadarChartBlock;

@JsonSerializable(disallowUnrecognizedKeys: true)
@FreezedUnionValue('2d_compare')
const factory SduiBlockDTO.scatterPlot({
  String? id,
  String? title,
  required List<MatrixScorecardRowDto> axes,
}) = SduiScatterPlotBlock;

@JsonSerializable(disallowUnrecognizedKeys: true)
@FreezedUnionValue('matrix_summary')
const factory SduiBlockDTO.matrixTable({
  String? id,
  String? title,
  required List<MatrixScorecardRowDto> axes,
  @JsonKey(name: 'visible_columns') @Default([]) List<String> visibleColumns,
  @JsonKey(name: 'column_labels') @Default({}) Map<String, I18nText> columnLabels,
  @JsonKey(name: 'extension_labels') @Default({}) Map<String, I18nText> extensionLabels,
}) = SduiMatrixTableBlock;

@JsonSerializable(disallowUnrecognizedKeys: true)
@FreezedUnionValue('1d_metrics')
const factory SduiBlockDTO.metrics1d({
  String? id,
  String? title,
  required List<MatrixScorecardRowDto> axes,
}) = SduiMetrics1DBlock;
```

#### Step 3.2: Update `SduiBlocksRenderer`
**Target**: @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\sdui_blocks_renderer.dart]

Add `switch` cases for the 4 new `SduiBlockDTO` variants:
- `SduiRadarChartBlock` → `LogicRadarChart(axes: block.axes)` widget
- `SduiScatterPlotBlock` → `LogicMatrixChart(xAxis: block.axes[0], yAxis: block.axes[1], zAxis: ...)` widget
- `SduiMatrixTableBlock` → existing matrix summary table widget (extracted from `report_renderer_v2_widget.dart`)
- `SduiMetrics1DBlock` → Column of `SduiBlocksRenderer(blocks: axis.innerSduiBlocks)` per axis

#### Step 3.3: Remove `layouts` from `ReportDataDto`
**Target**: @[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart#L49]

Delete: `@Default([]) List<ReportLayoutDto> layouts,`

Remove the import: `import 'report_layout_dto.dart';`

#### Step 3.4: Delete `ReportLayoutDto` File
**Target**: @[c:\src\quorum\client_app_v2\lib\features\execution\models\report_layout_dto.dart] — **DELETE FILE**

Also delete generated files:
- `report_layout_dto.freezed.dart`
- `report_layout_dto.g.dart`

#### Step 3.5: Update Report Renderer
**Target**: @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L198-L295]

Remove the entire `for (final layout in payload.layouts)` loop at @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L198-L451]. The unified `innerSduiBlocks` is already rendered by the existing `SduiBlocksRenderer` call. Ensure the renderer processes the full `payload.innerSduiBlocks` list which now contains chart blocks inline.

> [!CAUTION]
> **`SizedBox.shrink()` Anti-Pattern**: The current renderer at @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L290] uses `return const SizedBox.shrink()` as a fallback. This violates the `sized_box_shrink_ban` rule. The new `SduiBlocksRenderer` switch cases MUST NOT introduce any `SizedBox.shrink()` fallbacks. Unknown block types MUST crash via the sealed class exhaustiveness check.

#### Step 3.6: Update Studio Editor Views
The admin studio editors that use `PresetView` dropdown menus need updating:

##### `layout_editor_card.dart`
**Target**: @[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\layout_editor_card.dart]
- Replace `PresetView` dropdown with the retained `PresetView` enum (NOT deleted — see Step 3.7 below).
- Remove the `PresetView.complex3d` dropdown option at L220 and the axis count mapping at L420 — this is dead code that never existed in the enum definition.

##### `blueprint_editor_view.dart`
**Target**: @[c:\src\quorum\client_app_v2\lib\features\studio\views\blueprint_editor_view.dart]
- Same `PresetView` cleanup. Remove `PresetView.complex3d` at L90.

##### `profile_editor_view.dart`
**Target**: @[c:\src\quorum\client_app_v2\lib\features\studio\views\profile_editor_view.dart]
- No structural changes needed — default layout creation already uses valid `PresetView` values.

##### `output_profile.dart` (Studio Model)
**Target**: @[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart]
- **NO CHANGES** to the `OutputLayoutBlock` Freezed model. The `preset_view` field name and type (`PresetView`) are RETAINED because `OutputLayoutBlock` is a **database configuration model** (maps to `seed_data.json`), NOT a rendering DTO. The `preset_view` values in the database remain identical.

##### `blueprint_config.dart` (Studio Model)
**Target**: @[c:\src\quorum\client_app_v2\lib\features\studio\models\blueprint_config.dart]
- **NO CHANGES** — same rationale as `output_profile.dart` above.

#### Step 3.7: Retain `PresetView` Enum (NOT Deleted)
**Target**: @[c:\src\quorum\client_app_v2\lib\core\models\enums.dart#L58-L72]

> [!WARNING]
> **Architecture Decision: `PresetView` is RETAINED.** The `PresetView` enum is used by `OutputLayoutBlock` (the database configuration model at @[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart#L17-L19]) and `BlueprintConfig` (the studio editor model). These models map 1:1 to `seed_data.json` layout configuration. The `preset_view` field continues to exist in the database schema and the backend `OutputLayoutBlock` Pydantic model. Deleting the Flutter enum would break the Studio editor's ability to read/write layout configuration. The enum values remain unchanged: `metrics1d`, `compare2d`, `matrix3d`, `textOnly`, `defaultView`, `matrixSummary`.

What IS removed:
- The `PresetView` usage in the **rendering path** (`report_renderer_v2_widget.dart`'s layout loop) — because rendering now uses `SduiBlockDTO` variants.
- The `ReportLayoutDto` Freezed model (which was the rendering-side consumer of `PresetView`).

#### Step 3.8: Regenerate Freezed/JsonSerializable Files
Run: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`

#### Step 3.9: Flutter Tests
**Target**: @[c:\src\quorum\client_app_v2\test\features\studio\models\output_profile_test.dart]

- Update or rewrite tests that assert on `PresetView` or `ReportLayoutDto`.
- Add positive/negative serialization tests for the 4 new `SduiBlockDTO` variants.
- Run @[c:\src\quorum\backend_v2\tests\unit\models\test_contract_parity.py] to verify cross-domain parity now that both sides are updated.

**Quality Gate**: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`

---

### Phase 4: PDF Template & Jinja Synchronization

**Objective**: Ensure the PDF generator can render the 4 new block types and eradicate dead Jinja code.

#### Step 4.1: Modify Jinja Block Renderer Dispatch
**Target**: @[c:\src\quorum\backend_v2\templates\report_template.jinja2]

The Jinja template currently iterates `report.layouts` and uses `layout.preset_view` for conditional rendering. This must be migrated to iterate `report.inner_sdui_blocks` and dispatch on `block.block_type`.

Concrete rendering strategy per block type:
- `"3d_matrix"` (SduiRadarChartBlock) → Render an HTML table listing each axis name, score, and normalized percentage. Charts are NOT rendered in PDF — the Jinja template provides a **tabular data fallback** (consistent with the existing behavior at @[c:\src\quorum\backend_v2\templates\report_template.jinja2#L267-L320]).
- `"2d_compare"` (SduiScatterPlotBlock) → Render a 2-column HTML comparison table with axis labels and scores.
- `"matrix_summary"` (SduiMatrixTableBlock) → Render a full HTML `<table>` using `block.visible_columns` for headers and `block.axes` for rows. This directly replaces the existing matrix summary table at @[c:\src\quorum\backend_v2\templates\report_template.jinja2#L414].
- `"1d_metrics"` (SduiMetrics1DBlock) → Render a vertical list of metric blocks, iterating `block.axes` and rendering each axis's `inner_sdui_blocks` recursively.

#### Step 4.2: Eradicate Dead Jinja Code
**Target**: @[c:\src\quorum\backend_v2\templates\report_template.jinja2#L292]

Remove the dead `'3d_complex'` and `'complex3d'` strings from the `has_graph` set.

#### Step 4.3: Remove Legacy `layouts` Iteration from PDF Generator
**Target**: @[c:\src\quorum\backend_v2\services\pdf_generator.py#L190-L197]

The PDF generator currently iterates `ReportDataDTO.layouts`. Replace this with processing the unified `inner_sdui_blocks` stream, which now contains chart blocks inline.

#### Step 4.4: Update `pdf_generator.py` Rendering Context
**Target**: @[c:\src\quorum\backend_v2\services\pdf_generator.py]

Update the Jinja rendering context to pass `report.inner_sdui_blocks` instead of `report.layouts`.

**Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`

---

### Phase 5: Verification & E2E Integration Gate

#### Step 5.1: Database Re-Seed
```powershell
uv run python backend_v2/seed/run_seed.py local
```

#### Step 5.2: Backend Audit Loop (Full)
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/ --test
```

#### Step 5.3: Flutter Audit Loop (Full)
```powershell
uv run python scripts/flutter_audit_loop.py client_app_v2/ --build
```

#### Step 5.4: Contract Parity Test
Verify that @[c:\src\quorum\backend_v2\tests\unit\models\test_contract_parity.py] passes — confirming Python ↔ Flutter DTO field-level parity for `ReportDataDTO`/`ReportDataDto` (with `layouts` removed from both).

#### Step 5.5: SDUI Semantic Parity Test
Verify that @[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py] passes — confirming that the flat block pipeline produces identical visual semantics to the old layout pipeline.

#### Step 5.6: MANDATORY Final E2E REST API Verification Gate
```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

#### Step 5.7: Manual Verification
1. Run a full execution via the Flutter desktop app and verify:
   - Radar charts render correctly for 3+ axis configurations
   - Scatter plots render correctly for 2-axis configurations
   - Matrix summary tables render with correct columns
   - 1D metrics list renders with text blocks per axis
2. Export a PDF and verify visual parity with the Flutter rendering.
3. Verify the Admin Studio layout editor works with the new block type selector.

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- [ ] `ReportLayoutDTO` class is deleted from the codebase (Python and Flutter).
- [ ] `ReportDataDTO.layouts` field is deleted. All visualization data flows through `inner_sdui_blocks`.
- [ ] `PresetView` enum is **RETAINED** in Flutter for Studio editor configuration (NOT deleted — it maps to `seed_data.json`).
- [ ] `PresetView` is NO LONGER used in the rendering path.
- [ ] 4 new SDUI block types (`3d_matrix`, `2d_compare`, `matrix_summary`, `1d_metrics`) exist in both Python (`AnySduiBlock`) and Flutter (`SduiBlockDTO`).
- [ ] All `complex3d` / `3d_complex` dead code references are deleted from Flutter and Jinja.
- [ ] All `SizedBox.shrink()` fallbacks in the layout rendering path are removed.
- [ ] The `__import__()` lazy import hack in `blueprint.py` is replaced with standard top-of-file imports.
- [ ] `BlueprintTransformer._build_visualization_blocks()` produces `list[AnySduiBlock]` appended to `inner_sdui_blocks`.
- [ ] `SduiBlocksRenderer` renders all 4 new block types via Dart 3 `switch` pattern matching.
- [ ] PDF generator renders all 4 new block types via Jinja templates.
- [ ] Admin Studio layout editor uses updated block type selector.
- [ ] All backend tests pass (`backend_audit_loop.py`).
- [ ] All frontend tests pass (`flutter_audit_loop.py --build`).
- [ ] Contract parity test passes.
- [ ] E2E live LLM test passes.
- [ ] No references to `ReportLayoutDTO` remain in production code.
- [ ] `PresetView` references remain ONLY in Studio editor models (`output_profile.dart`, `blueprint_config.dart`) and `enums.dart`.

### Automated Unit Tests
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/ --test
uv run python scripts/flutter_audit_loop.py client_app_v2/ --build
```

### Manual Verification Steps
1. `uv run python backend_v2/seed/run_seed.py local` — re-seed database.
2. Run a full execution and inspect the PDF output.
3. Verify all 4 visualization types render correctly in the Flutter desktop app.
4. Verify the Admin Studio layout editor creates and saves layout blocks with the new type selector.

### MANDATORY Final E2E REST API Verification Gate
```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

## 5. Knowledge Item Mandate

This migration introduces a new architectural SSOT pattern. Upon completion, the following Knowledge Item MUST be created or updated:

- **UPDATE**: `sdui_matrix_synthesis_architecture` KI — replace all references to `ReportLayoutDTO`, `preset_view`, and `layouts` with the new flat block pipeline architecture. Update rule `unified_sdui_graphing_architecture` to reflect the 4 new `AnySduiBlock` variants.
- **UPDATE**: `dumb_painter_sdui_architecture` KI — remove references to `ReportLayoutDTO` as the container. Document that all visualizations are now first-class `AnySduiBlock` variants.
- **UPDATE**: `strict_sdui_polymorphic_serialization` KI — add the 4 new block discriminator values.
- **UPDATE**: `output_profile_layout_v2.md` — remove the `[!CAUTION]` target-state banner and mark as current-state architecture.
