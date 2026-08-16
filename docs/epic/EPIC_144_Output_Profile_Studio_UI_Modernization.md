# EPIC 144: Output Profile Studio UI Modernization & Visual Block Builder

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Objective
Modernize and decompose the Output Profile editing interface in Quorum Studio (`@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]`) into a clean, 3-tab information architecture aligned with Quorum's Gold Standard Flat MVC and Sub-Tabs paradigm (matching `@[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]`). Replace the unintuitive, text-heavy layout block editor (`@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]`) with an **Adaptive Visual Block Builder** where complex matrices have deep configuration cards, but straightforward components (like Metadata or Bibliography) are managed via simple toggle cards.

### 1.2 Problem Statement
The current Output Profile editor in Studio suffers from severe cognitive overload and architectural coupling:
1. **Monolithic God View**: `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` is an 896-line monolithic widget containing identity, scoring math, metadata checklists, XAI checkboxes, and layout blocks in an uneven, cramped 3-column layout.
2. **Conflated Responsibilities**: Mathematical scoring parameters (Strictness Level, Scoring Strategy, Display Scales) are crammed together with profile branding and I18n preface texts. Furthermore, technical header metadata (audit timestamps, engine badges) is mixed with deep cognitive explainability toggles (quotes, Devil's Advocate, coaching tips).
3. **Unintuitive Matrix & Layout Block Editing**: The current `@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]` relies on technical dropdown enums (`metrics1d`, `compare2d`, `matrix3d`, `textOnly`, `matrixSummary`) without visual previews. Switching views leaves orphaned or misleading axis selectors (`componentXAxisLabel`, `componentYAxisLabel`), prompts users to manually type comma-separated `steps` IDs into text inputs, and hides leipäteksti behind ambiguous `textDeliveryMode: none` settings.
4. **Inconsistent Studio UX**: Unlike `@[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]` which uses a structured top TabBar with number/icon indicators, the Output Profile editor uses a raw `LayoutBuilder` 3-pane Row toggle and responsive column wrappers that break visual consistency.

---

## 2. Architectural Impact & Compliance Matrix

### 2.1 Deprecations & Sunset List (`What We Will REMOVE`)
| Symbol / Component | File Location | Status | Rationale / Migration Target |
| :--- | :--- | :--- | :--- |
| Local function `buildIdentityPane()` (L244-L726) | `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` | REMOVED | Decomposed into `profile_general_tab.dart`, `profile_scoring_tab.dart`, `profile_metadata_tab.dart`, and `profile_xai_tab.dart`. |
| Local function `buildTargetBlockOrderPane()` (L755-L796) | `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` | REMOVED | Decomposed into `profile_layouts_tab.dart`. |
| Comma-separated `steps` text field | `@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]` | REMOVED | Eliminated manual string typing. Replaced by automatic resolution from workflow blueprints. |
| Sub-tab segmented button inside layout block | `@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]` | REMOVED | Replaced by single-page Adaptive Block Editor driven by selected visual presentation card. |
| Raw Checkbox lists for XAI & Metadata | `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` | REMOVED | Replaced with themed `FilterChip` and `ChoiceChip` wrap pills grouped by domain category. |

### 2.2 Retained SSOT Invariants (`What We Will RETAIN`)
1. **SSOT Data Models**: The underlying domain models (`OutputProfile`, `OutputLayoutBlock`, `PresetView`, `TextDeliveryMode`, `XaiExtensionType`, `DisplayScale`, `StrictnessLevel`, `ScoringStrategy`) remain 100% identical in Python (`@[backend_v2/models/v2_core.py]`) and Dart Freezed (`@[client_app_v2/lib/features/studio/models/output_profile.dart]`).
2. **Fail-Fast Boundary Parsing**: Strict Pydantic V2 and Dart Freezed deserialization (`disallowUnrecognizedKeys: true`) are strictly preserved.
3. **Riverpod State Management**: `outputProfileFormProvider(id)` notifier pattern in `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]` is retained as the single source of truth for form mutations.

### 2.3 Compliance & Modernity Gates
1. **Flat MVC Sub-Tabs Pattern**: All tab views are isolated into dedicated, single-responsibility HookConsumerWidgets under `@[client_app_v2/lib/features/studio/views/widgets/profile/]`.
2. **Desktop Pro-Tool Ergonomics**: Mouse hover cursors, focus traversal, and design token spacing (`@[client_app_v2/lib/core/theme/app_spacing.dart]`) enforced.
3. **No Hardcoded Magic Strings**: All tab titles, card descriptions, and button labels MUST be registered in `@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]`.

### 2.4 Mandatory Codebase Violations to Eradicate (Modernity Gate)
During codebase verification, the following 6 existing Fail-Fast violations were identified in the files being refactored. These MUST be eradicated as part of the decomposition phases (Phase 1 and Phase 2), NOT deferred:

| # | Violation | Location | Rule Violated | Mandatory Fix |
| :--- | :--- | :--- | :--- | :--- |
| V1 | `unknownEnumValue: PresetView.defaultView` and `unknownEnumValue: TextDeliveryMode.full` Freezed fallbacks | `@[client_app_v2/lib/features/studio/models/output_profile.dart#L17-L28]` | `silent_json_fallbacks` / Modernity Checklist (Dart Freezed `@Default("Fallback")` and `fallbackUnion` FORBIDDEN) | REMOVE `unknownEnumValue` parameters. Unknown enum values MUST crash the Freezed parser via `CheckedFromJsonException`. |
| V2 | `SizedBox.shrink()` to hide unavailable XAI extensions | `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart#L627]` and `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart#L635]` | `sized_box_shrink_ban` | Replace with programmatic filtering BEFORE the widget list is built (filter the iterable, not hide the output). |
| V3 | `AsyncValue<List<dynamic>>` untyped state parameters | `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart#L108-L110]` | Modernity Checklist (`List<dynamic>` → Typed sealed classes) | Type all 3 parameters: `AsyncValue<List<PromptBlock>>`, `AsyncValue<List<Workflow>>`, `AsyncValue<List<NodeStrategy>>`. |
| V4 | Hardcoded color `Color(0xFF2E7D32)` | `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart#L145]` | `design_token_absolute_rule` | Replace with `Theme.of(context).colorScheme.primary` or equivalent design token. |
| V5 | Hardcoded pixel values `EdgeInsets.symmetric(horizontal: 16.0)` and `SizedBox(width: 20, height: 20)` | `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart#L805-L810]` | `design_token_absolute_rule` | Replace with `AppSpacing` design tokens. |
| V6 | Raw `String displayScale` field (not a typed Enum) | `@[client_app_v2/lib/features/studio/models/output_profile.dart#L98]` | `no_raw_string_enum_mappings` / `cross_language_enum_parity` | Migrate to a strict `@JsonEnum() DisplayScale` enum in `enums.dart` with 3 values: `original`, `custom`, `normalized100`. |
| V7 | Hardcoded Finnish labels in `MetadataAdapter` (`"Käyttäjä:"`, `"Organisaatio:"`, `"Arviointimoottori:"`, `"Ankaruustaso:"`) | `@[backend_v2/services/sdui/adapters/metadata_adapter.py#L59-L80]` | `structural_localization_axis` / `@[ki_dual_axis_localization_architecture.md]` | Replace hardcoded Finnish strings with localized label resolution via `OutputProfile.metric_mappings` I18nText dictionary. The adapter MUST emit only locale-resolved strings using `context.profile.metric_mappings[key].resolve(context.locale)`. |
| V8 | `SynthesisTextAdapter` does not read `RenderedSynthesisCache.section_syntheses` | `@[backend_v2/services/sdui/adapters/synthesis_text_adapter.py#L39-L57]` | `tripartite_pipeline` / Dual-Mode synthesis | Extend adapter to read BOTH `context.profile.content_blocks` (static pre-defined blocks) AND `context.profile_cache.section_syntheses[layout_id]` (dynamic LLM-generated synthesis from Pipeline mode). Without this, Option A (Pipeline Way) produces no output. |

### 2.5 Block Data Pipeline Reference (DB → Pydantic → Adapter → SDUI → Renderer)

The following table exhaustively documents the complete data lineage for every rendering block in the system. The **dispatch loop** lives in `@[backend_v2/services/blueprint.py#L685-L691]`: it iterates `OutputProfile.target_block_order` and calls the matching adapter from the `_target_block_hydrators` registry (`@[backend_v2/services/blueprint.py#L89-L103]`).

**Block Type Enum SSOT:** `TargetBlockType` in `@[backend_v2/models/enums.py#L106-L121]`
**Block Order SSOT:** `OutputProfile.target_block_order` in `@[backend_v2/models/v2_core.py#L1375-L1389]`
**Adapter Context DTO:** `AdapterContext` in `@[backend_v2/services/sdui/adapters/base_adapter.py#L19-L41]`

#### Block 1: `metadata_block`
| Layer | Location | Detail |
| :--- | :--- | :--- |
| **DB Config** | `OutputProfile.visible_metadata: list[str]` | `@[backend_v2/models/v2_core.py#L1332-L1335]` — Controls which metadata fields (specifically and exhaustively: `date`, `organization`, `user`, `scoring_engine`, `strictness`) appear on the header. |
| **DTO** | `OutputProfileCreateDTO.visible_metadata` | `@[backend_v2/models/dtos/output_profile.py#L72-L78]` |
| **Adapter** | `MetadataAdapter.build(context)` | `@[backend_v2/services/sdui/adapters/metadata_adapter.py]` — Reads `context.profile.visible_metadata`, `context.user_name`, `context.org_name`, `context.local_time_str`, `context.scoring_engine`, `context.cost`, `context.tokens`. Emits `SduiMetadataBlock`. |
| **SDUI Output** | `SduiMetadataBlock` | `@[backend_v2/models/view/sdui.py]` |
| **UI Config** | Checkboxes for toggling visible metadata fields | Tab 3 → `metadata_block` card |

#### Block 2: `executive_summary_block`
| Layer | Location | Detail |
| :--- | :--- | :--- |
| **DB Config** | `OutputProfile.custom_preface: I18nText`, `OutputProfile.user_role_mappings: dict[str, I18nText]`, `OutputProfile.user_role_label: I18nText` | `@[backend_v2/models/v2_core.py#L1323-L1328]` and `@[backend_v2/models/v2_core.py#L1360-L1362]` |
| **Data Source** | `RenderedSynthesisCache.user_role`, `RenderedSynthesisCache.user_role_justification` | `@[backend_v2/models/v2_core.py#L1610-L1611]` — The LLM-classified user role and justification from synthesis Phase 2. |
| **Adapter** | `ExecutiveSummaryAdapter.build(context)` | `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]` — Uses `EXECUTIVE_SUMMARY_RULES` dict mapping `RoleClassification` enum to localized l10n keys. Reads from `context.profile_cache`. Emits `ParagraphBlock` instances. |
| **SDUI Output** | `ParagraphBlock` | `@[backend_v2/models/view/sdui.py]` |
| **UI Config** | Custom preface text editor, Role Mappings modal | Tab 1 (General) preface + Tab 3 card visibility toggle |

#### Block 3: `synthesis_text_block`
| Layer | Location | Detail |
| :--- | :--- | :--- |
| **DB Config** | `OutputProfile.synthesis: SynthesisConfigDTO`, `OutputProfile.content_blocks: list[AnySduiBlock]`, `OutputProfile.tone_instruction: I18nText` | `@[backend_v2/models/v2_core.py#L1330]`, `@[backend_v2/models/v2_core.py#L1372-L1374]`, `@[backend_v2/models/v2_core.py#L1393-L1395]` |
| **Data Source** | `RenderedSynthesisCache.section_syntheses` (LLM-generated markdown) | `@[backend_v2/models/v2_core.py#L1601-L1603]` — Pre-computed Section-Level synthesis keyed by layout ID. |
| **Adapter** | `SynthesisTextAdapter.build(context)` | `@[backend_v2/services/sdui/adapters/synthesis_text_adapter.py]` — Reads `context.profile.content_blocks` (pre-defined static blocks). Emits deep-copied `AnySduiBlock` instances. |
| **SDUI Output** | Polymorphic `AnySduiBlock` (typically `MarkdownBlock` or `ParagraphBlock`) | `@[backend_v2/models/view/sdui.py]` |
| **UI Config** | Dual-mode selector (Pipeline / On-the-Fly), tone instruction text field | Tab 3 → `synthesis_text_block` card |

#### Block 4: `matrix_graphs_block`
| Layer | Location | Detail |
| :--- | :--- | :--- |
| **DB Config** | `OutputLayoutBlock.preset_view: Literal["1d_metrics", "2d_compare", "3d_matrix", "default", "text_only", "matrix_summary"]`, `OutputLayoutBlock.steps: list[str]` | `@[backend_v2/models/v2_core.py#L1277-L1283]` — Defines the visual preset and which workflow step IDs provide the axes. |
| **Data Source** | `AdapterContext.parsed_matrices: dict[str, MatrixScorecardRowDTO]` | `@[backend_v2/services/sdui/adapters/base_adapter.py#L37]` — Pre-evaluated matrix scorecard rows from the DAG execution engine. Each `MatrixScorecardRowDTO` (`@[backend_v2/models/v2_core.py#L994-L1060]`) contains `score`, `normalized_score`, `ui_plot_ratio`, `ui_boundary_labels`, and `evaluated_atoms`. |
| **Adapter** | `MatrixGraphsAdapter.build(context)` | `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py]` — Validates axis count against `MATRIX_GRAPHS_RULES` (`3d_matrix` requires min 3 axes, `2d_compare` min 2). Emits `SduiRadarChartBlock`, `SduiScatterPlotBlock`, or `SduiMetrics1DBlock`. |
| **SDUI Output** | `SduiRadarChartBlock`, `SduiScatterPlotBlock`, `SduiMetrics1DBlock`, `ParagraphBlock` | `@[backend_v2/models/view/sdui.py]` |
| **UI Config** | Visual preset card selection (5 presets), Context-Adaptive X/Y/Z axis dropdowns | Tab 3 → `matrix_graphs_block` card (DEEP CONFIGURATION) |

#### Block 5: `grouped_extensions_block`
| Layer | Location | Detail |
| :--- | :--- | :--- |
| **DB Config** | `OutputProfile.visible_block_extensions: list[LaxXaiExtensionType]`, `OutputProfile.visible_workflow_extensions: list[LaxXaiExtensionType]`, `OutputProfile.max_extension_items: int`, `OutputProfile.extension_labels: dict[LaxXaiExtensionType, I18nText]` | `@[backend_v2/models/v2_core.py#L1336-L1349]` and `@[backend_v2/models/v2_core.py#L1364-L1367]` |
| **Data Source** | `RenderedSynthesisCache.xai_highlights: list[Any]` | `@[backend_v2/models/v2_core.py#L1609]` — LLM-extracted XAI highlight items from synthesis Phase 2 (parsed as `XaiHighlightItem` from `@[backend_v2/models/dtos/synthesis.py]`). |
| **Adapter** | `XaiHighlightsAdapter.build(context)` | `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]` — Filters highlights by `visible_block_extensions` and `visible_workflow_extensions`. Applies `ranked_round_robin_select` capped at `max_extension_items`. Uses `XAI_AESTHETICS_RULES` for severity/icon mapping. Emits `AccordionBlock` and `AlertBlock`. |
| **SDUI Output** | `AccordionBlock`, `AlertBlock` | `@[backend_v2/models/view/sdui.py]` |
| **UI Config** | FilterChip pills for extension types, max items slider | Tab 3 → `grouped_extensions_block` card |

#### Block 6: `penalties_block`
| Layer | Location | Detail |
| :--- | :--- | :--- |
| **DB Config** | Penalties are computed by the scoring engine, not configured per-profile. | Profile-level overrides: `OutputProfile.strictness_level` (`@[backend_v2/models/v2_core.py#L1358]`) and `OutputProfile.scoring_strategy` (`@[backend_v2/models/v2_core.py#L1359]`) affect penalty severity. |
| **Data Source** | `AdapterContext.penalties_applied: list[str]` | `@[backend_v2/services/sdui/adapters/base_adapter.py#L30]` — List of penalty description strings computed by the Waterfall/CDM scoring engine during execution. |
| **Adapter** | `PenaltiesAdapter.build(context)` | `@[backend_v2/services/sdui/adapters/penalties_adapter.py]` — Iterates `penalties_applied`. Uses `PENALTIES_RULES` for `VisualIntent.CRITICAL_OVERRIDE` severity. Emits `AlertBlock` per penalty. |
| **SDUI Output** | `AlertBlock` | `@[backend_v2/models/view/sdui.py]` |
| **UI Config** | Universal Baseline toggle only (penalties are computed, not manually configured) | Tab 3 → `penalties_block` card (simple toggle) |

#### Block 7: `matrix_summary_table_block`
| Layer | Location | Detail |
| :--- | :--- | :--- |
| **DB Config** | `OutputLayoutBlock.preset_view`, `OutputLayoutBlock.steps`, `OutputLayoutBlock.matrix_visible_columns: list[str]`, `OutputLayoutBlock.matrix_column_labels: dict[str, I18nText]` | `@[backend_v2/models/v2_core.py#L1277-L1310]` — Controls which columns are visible and their localized labels. |
| **Data Source** | `AdapterContext.parsed_matrices: dict[str, MatrixScorecardRowDTO]` | Same as Block 4. Matrix rows contain `score`, `true_atoms`, `total_atoms`, `row_explanation`, `level_breakdown`. |
| **Adapter** | `MatrixSummaryTableAdapter.build(context)` | `@[backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py]` — Reads `context.profile.layouts` and filters by `preset_view == "matrix_summary"`. Validates minimum axes via `MATRIX_SUMMARY_RULES`. Emits `SduiMatrixTableBlock`. |
| **SDUI Output** | `SduiMatrixTableBlock`, `MarkdownBlock`, `ParagraphBlock` | `@[backend_v2/models/view/sdui.py]` |
| **UI Config** | Matrix selection, column visibility toggles | Tab 3 → `matrix_summary_table_block` card (DEEP CONFIGURATION) |

#### Block 8: `variance_validation_block`
| Layer | Location | Detail |
| :--- | :--- | :--- |
| **DB Config** | No profile-level configuration fields. Block is purely computed. | Presence in `target_block_order` controls visibility. |
| **Data Source** | `ExtensionMetricsDTO.variance_score: float`, `ExtensionMetricsDTO.alignment_verdict: str` | `@[backend_v2/models/v2_core.py#L1593-L1594]` — Pre-calculated by the synthesis engine. Also reads `MatrixScorecardRowDTO` rows from `context.parsed_matrices` for per-matrix variance breakdowns. |
| **Adapter** | `VarianceAdapter.build(context)` | `@[backend_v2/services/sdui/adapters/variance_adapter.py]` — Uses `VARIANCE_RULES` (aligned → `VisualIntent.INFO`, misaligned → `VisualIntent.WARNING`). Emits `SduiMetrics1DBlock`, `SduiGridBlock`, `AlertBlock`, `MarkdownBlock`, `ParagraphBlock`. |
| **SDUI Output** | `SduiMetrics1DBlock`, `SduiGridBlock`, `AlertBlock`, `MarkdownBlock`, `ParagraphBlock` | `@[backend_v2/models/view/sdui.py]` |
| **UI Config** | Universal Baseline toggle only | Tab 3 → `variance_validation_block` card (simple toggle) |

#### Block 9: `authenticity_evaluation_block`
| Layer | Location | Detail |
| :--- | :--- | :--- |
| **DB Config** | No profile-level configuration fields. Block is purely computed. | Presence in `target_block_order` controls visibility. |
| **Data Source** | `ExtensionMetricsDTO.authenticity_score: float`, `ExtensionMetricsDTO.performative_phrases_count: float` | `@[backend_v2/models/v2_core.py#L1591-L1592]` — Pre-calculated metrics. Also reads `MatrixScorecardRowDTO` for per-matrix authenticity breakdowns. |
| **Adapter** | `AuthenticityAdapter.build(context)` | `@[backend_v2/services/sdui/adapters/authenticity_adapter.py]` — Uses `AUTHENTICITY_RULES` with 3 severity levels (`level_high` → INFO, `level_medium` → WARNING, `level_low` → ERROR) and `AUTHENTICITY_THRESHOLDS` (high: 80.0, low: 50.0). Emits `SduiMetrics1DBlock`, `SduiGridBlock`, `AlertBlock`, `MarkdownBlock`, `ParagraphBlock`. |
| **SDUI Output** | `SduiMetrics1DBlock`, `SduiGridBlock`, `AlertBlock`, `MarkdownBlock`, `ParagraphBlock` | `@[backend_v2/models/view/sdui.py]` |
| **UI Config** | Universal Baseline toggle only | Tab 3 → `authenticity_evaluation_block` card (simple toggle) |

#### Block 10: `printable_sources_block` (Bibliography)
| Layer | Location | Detail |
| :--- | :--- | :--- |
| **DB Config** | Currently: presence in `target_block_order`. NEW in Epic 144: `OutputProfile.include_bibliography: bool` (to be added). | `@[backend_v2/models/v2_core.py#L1375-L1389]` |
| **Data Source** | `RenderedSynthesisCache.cited_sources: list[str]` | `@[backend_v2/models/v2_core.py#L1608]` — Citations collected during synthesis Phase 2. Additionally, `AdapterContext.mcp_audit_map: dict[str, MCPAuditTrace]` provides `source_urls` from the MCP tool loop. |
| **Adapter** | `PrintableSourcesAdapter.build(context)` | `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` — Reads `profile_cache.cited_sources` and `mcp_audit_map` source URLs. Emits `MarkdownBlock` with formatted bibliography. |
| **SDUI Output** | `MarkdownBlock` | `@[backend_v2/models/view/sdui.py]` |
| **UI Config** | Visibility toggle, grouping mode (chronological/by_matrix), anonymization toggle | Tab 3 → `printable_sources_block` card |

#### Block 11: `global_score_block` (System Block)
| Layer | Location | Detail |
| :--- | :--- | :--- |
| **DB Config** | System-managed. Not user-configurable. | Always present in `target_block_order`. |
| **Data Source** | `AdapterContext.global_score: float` | `@[backend_v2/services/sdui/adapters/base_adapter.py#L33]` |
| **Adapter** | `GlobalScoreAdapter.build(context)` | `@[backend_v2/services/sdui/adapters/global_score_adapter.py]` |
| **UI Config** | N/A — System block, not editable in Studio | Not shown in Tab 3 block builder |

#### Block 12: `audit_trail_block` (System Block)
| Layer | Location | Detail |
| :--- | :--- | :--- |
| **DB Config** | System-managed. Not user-configurable. | Always present in `target_block_order`. |
| **Data Source** | `AdapterContext.mcp_audit_map: dict[str, MCPAuditTrace]` | `@[backend_v2/services/sdui/adapters/base_adapter.py#L31]` |
| **Adapter** | `McpAuditAdapter.build(context)` | `@[backend_v2/services/sdui/adapters/mcp_audit_adapter.py]` |
| **UI Config** | N/A — System block, not editable in Studio | Not shown in Tab 3 block builder |

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Sub-Tab Information Architecture & Scaffold Decomposition
Decompose `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` into a highly streamlined 3-tab `DefaultTabController` scaffold matching the visual stepper idiom of `@[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]`. This strictly enforces the **God Code Prevention mandate** (`@[ki_god_code_prevention.md]`) by physically splitting the 896-line monolithic file into dedicated sub-widgets rather than appending more private helpers. All violations listed in Section 2.4 (Modernity Gate) MUST be eradicated during this phase:
- **Tab 1: 📋 General & Preface (`ProfileGeneralTab`)**
  - Workflow binding selector (`DropdownButtonFormField<String>`).
  - Profile name and description (`I18nTextField`).
  - Custom report preface / introduction rich text (`I18nTextField`).
  - Advanced expandable accordion for opaque `id` and semantic `slug`.
- **Tab 2: ⚖️ Scoring & Scales (`ProfileScoringTab`)**
  - Strictness level slider / segmented selector (Level 1 to 5).
  - Scoring Strategy selector (`waterfall`, `average`, `weighted_average`, `pure_math`).
  - Display Scale selector (`original`, `custom`, `normalized_100`).
- **Tab 3: 📐 Report Structure (`ProfileLayoutsTab`)**
  - The master drag-and-drop canvas for the 9 execution blocks.
  - Contains all block-specific configuration cards (Metadata, Matrix Graphs, XAI, Bibliography, etc.).

### Phase 2: Adaptive Visual Block Builder & UI Patterns
Refactor the UI (`@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]`) to strictly follow the new "Flat Master-Detail" architecture within the Report Structure tab. Implement the following approved UI patterns:

1. **Universal Baseline (The Block Visibility Toggle):**
   - EVERY block editor (Metadata, Exec Summary, Matrix Results, etc.) MUST start with a primary toggle: `Include this block in the final report`. This controls the baseline visibility of the block in the final PDF/SDUI output.
   - **SSOT Mechanism:** The toggle MUST map exclusively to adding/removing the block's `TargetBlockType` string from `OutputProfile.target_block_order: list[str]` (`@[backend_v2/models/v2_core.py#L1375-L1389]`). No separate `include_X: bool` fields are permitted. This ensures a single, universal visibility mechanism for ALL blocks.

2. **Executive Summary Editor:**
   - Incorporates the `custom_preface` (multilingual preamble text).
   - User Role Mappings (specifically: "Architect", "Manager", or defined role strings) are hidden behind an explicit "Edit Role Translations ↗" modal to reduce cognitive overload in the main view.

3. **Matrix Results Editor (Collection Builder & Inline Accordion):**
   - Replaces monolithic routing with a **Collection Builder** (1-N matrices).
   - **Inline Editing (Accordion):** When editing a matrix, it expands inline rather than navigating to a new page, maintaining list context.
   - **Deterministic Visuals:** The "Auto Default" option is REMOVED. The user must explicitly select one of 5 presets (Summary Table, 1D, 2D, 3D, Text Only).
   - **Context-Adaptive Axes:** The UI reacts to the visual selection. Selecting 3D Bubble displays 3 axis dropdowns (X, Y, Z). Selecting 1D displays only 1.

4. **Synthesis Text Editor (Dual-Mode LLM Configuration):**
   - Exposes the architectural difference between Phase 1 deep analysis and Phase 3 on-the-fly generation.
   - Option A (Pipeline Way): Dropdown to select a `synthesis_block_id` (fetches existing deep analysis from `RenderedSynthesisCache.section_syntheses`).
   - Option B (On-the-Fly): Text fields for `tone_instruction` and `preamble_text` to generate summaries at render-time, optionally combining with `historical_context_mode`. (Structural `system_prompt` rules MUST remain locked in Python `prompt_compiler.py`).
   - Includes a multilingual `preamble_text` rich text editor.
   - **Adapter Gap (V8):** `SynthesisTextAdapter` (`@[backend_v2/services/sdui/adapters/synthesis_text_adapter.py]`) MUST be extended to read `context.profile_cache.section_syntheses` in addition to `context.profile.content_blocks`. Currently it only reads static blocks, which means Pipeline Way (Option A) synthesis output is silently dropped.

6. **AI Extensions Block Editor (FilterChip Pattern):**
   - Utilizes interactive `FilterChip` pills to quickly enable/disable specific XAI extensions (specifically and exhaustively: Practical Tips, Devil's Advocate, Remedial Actions, Risk Analysis, Source Quotes, Evidence Reasoning).
   - Includes a `Display Settings` slider to control `max_extension_items` (the maximum limit MUST be fetched programmatically from backend settings.py to respect global config sovereignty).

7. **Metadata & Bibliography Block Editors:**
   - Simple toggle-based cards in the block builder.
   - Metadata contains checkboxes for audit stamps and names.
   - Bibliography contains formatting toggles (grouped_by_matrix, anonymous mode).

8. **Variance & Authenticity Evaluation Blocks:**
   - Standalone, straightforward visual blocks available in the Report Structure builder.
   - Require no complex internal configuration beyond the Universal Baseline toggle (`Include this block in the final report`).
   - Maps directly to the static `variance_validation_block` and `authenticity_evaluation_block` rendering pipelines.

### Phase 3: Backend Execution & Synthesis Alignment

1. **Tripartite Synthesis & SDUI Alignment (V8 Fix):**
   - **Phase 2 (Synthesis Engine):** Must handle the LLM execution for Tapa B (`system_prompt`) and save the output to `profile_cache`.
   - **Phase 3 (SDUI Adapter):** Refactor `@[backend_v2/services/sdui/adapters/synthesis_text_adapter.py]` to read BOTH `context.profile.content_blocks` (static blocks) AND `context.profile_cache.section_syntheses` (dynamic Pipeline synthesis). It MUST strictly act as a "Dumb Painter" (`@[ki_tripartite_pipeline_architecture.md]`): no LLM calls, only reading pre-computed results.
   - Ensure `SynthesisConfigDTO` robustly supports dual-mode synthesis.
2. **Bibliography Alignment:** The `printable_sources_block` visibility is controlled exclusively via `target_block_order` (Universal Baseline Toggle SSOT). No separate `include_bibliography` boolean field is needed. Refactor `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` to support new grouping settings if needed.
3. **Metadata Localization Fix (V7):** Refactor `@[backend_v2/services/sdui/adapters/metadata_adapter.py#L59-L80]` to replace ALL hardcoded Finnish strings (`"Käyttäjä:"`, `"Organisaatio:"`, `"Arviointimoottori:"`, `"Ankaruustaso:"`) with locale-resolved labels from `OutputProfile.metric_mappings` I18nText dictionary, strictly adhering to Dual-Axis Localization (`@[ki_dual_axis_localization_architecture.md]`).
4. **Adapter Pattern Strictness:** All modified adapters MUST strictly follow the 2-section canonical template (AESTHETICS_RULES dictionary + Adapter Class), utilizing fail-fast dictionary access and immutable `AdapterContext` (`@[ki_sdui_adapter_pattern.md]`).

### Phase 4: Localization Synchronization & Freezed Validation

> [!IMPORTANT]
> **Dual-Axis Localization Mandate (`@[ki_dual_axis_localization_architecture.md]`):** All UI text in Epic 144 MUST follow the strict two-axis separation:
> - **Axis 1 (Structural / Flutter):** Tab titles, button labels, tooltip texts, card headers, and all compile-time-known UI chrome MUST be defined exclusively in `.arb` files (`@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]`) and accessed via `AppLocalizations.of(context)!.keyName`. The backend MUST remain completely unaware of these strings.
> - **Axis 2 (Semantic / Backend):** Dynamic, data-driven labels (profile names, matrix names, extension labels, metric labels) MUST be resolved by the backend via `I18nText.resolve(locale)` and delivered pre-localized to Flutter. Flutter blindly paints the `text` attribute.

1. Update `@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]` with comprehensive UI keys for all 3 tabs, all 9 block card titles, preset cards, and helper tooltips. Specifically and exhaustively:
   - Tab labels: `profileTabGeneral`, `profileTabScoring`, `profileTabReportStructure`
   - Block card titles: `blockMetadata`, `blockExecutiveSummary`, `blockSynthesisText`, `blockMatrixGraphs`, `blockAiExtensions`, `blockPenalties`, `blockMatrixSummary`, `blockVariance`, `blockAuthenticity`, `blockBibliography`
   - Universal toggle: `blockVisibilityToggleLabel`
   - Preset view labels: `presetView1d`, `presetView2d`, `presetView3d`, `presetViewTextOnly`, `presetViewSummaryTable`
2. **Backend Enum l10n Adapters:** Enforce that Backend Enums mapped to the UI (specifically and exhaustively: `PresetView`, `XaiExtensionType`, `DisplayScale`, `ScoringStrategy`) utilize strict `@property def l10n_key(self) -> str:` mapping. The Frontend MUST NOT use magic string manipulation (specifically: the Dart string manipulation method `.lower()`) or ID fallbacks to resolve translations.
3. Execute `flutter gen-l10n` to compile localization files.
4. Validate Freezed model serialization with `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`.

### Phase 5: Automated Verification & Quality Gates
1. Run localized Flutter unit and widget test suite on Studio output profile views.
2. Run global quality gates: `uv run python scripts/backend_audit_loop.py backend_v2 --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`.

---

## 4. Definition of Done (DoD) & Verification Plan

### 4.1 Definition of Done (DoD)
- [ ] `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` is decomposed into a 3-tab `DefaultTabController` scaffold.
- [ ] Three dedicated sub-tab widgets exist in `@[client_app_v2/lib/features/studio/views/widgets/profile/]`:
  - `profile_general_tab.dart`
  - `profile_scoring_tab.dart`
  - `profile_layouts_tab.dart`
- [ ] The `profile_layouts_tab.dart` contains dedicated block editor cards for all 9 layout blocks (Metadata, Exec Summary, Synthesis, Matrix Graphs, XAI Extensions, Penalties, Matrix Summary, Variance, Authenticity).
- [ ] `@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]` provides visual card selection for `PresetView` with adaptive form fields.
- [ ] No manual comma-separated `steps` text fields remain in the UI.
- [ ] All UI strings exist in both English (`app_en.arb`) and Finnish (`app_fi.arb`).
- [ ] `MetadataAdapter` contains ZERO hardcoded Finnish strings. All labels resolved via `OutputProfile.metric_mappings` I18nText.
- [ ] `SynthesisTextAdapter` reads both `content_blocks` (static) and `section_syntheses` (dynamic Pipeline synthesis).
- [ ] Block visibility is controlled exclusively via `target_block_order` manipulation (no `include_X: bool` fields).
- [ ] All `.arb` keys for block titles, tab labels, and preset views are registered in both `app_en.arb` and `app_fi.arb`.
- [ ] All automated tests pass without warnings or deprecations.

### 4.2 Automated Unit & Widget Tests
```powershell
# Localization compilation
cd client_app_v2; flutter gen-l10n; cd ..

# Frontend widget tests and Freezed build
uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build

# Global Quality Gate
uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/
```

### 4.3 Manual Verification Steps
1. Navigate to Quorum Studio -> Output Profiles -> Edit Profile.
2. Verify all 3 top tabs render with icons and labels matching the design standard of `WorkflowBuilderView`.
3. Switch between tabs: verify smooth transitions and zero layout overflow errors.
4. On Tab 3 (Report Structure), add a new layout block, select `2D Grid Comparison`, verify X and Y axis selectors appear cleanly, save profile, and verify database persistence.

---

## 5. Required Knowledge Items — Binding Constraints (Explicit)

> [!IMPORTANT]
> This section does NOT merely reference KI files. It **explicitly documents the binding constraints** from each KI that an implementing agent MUST obey during Epic 144 execution. If a constraint below conflicts with an instruction elsewhere in this document, this section takes precedence.

---

### 5.1 God Code Prevention (`@[ki_god_code_prevention.md]`)

**Why it applies:** Phase 1 decomposes an 896-line monolithic view. The agent MUST follow decomposition rules, not just move code into private helpers.

| Rule ID | Binding Constraint for Epic 144 |
|:--------|:-------------------------------|
| `anti_god_file_dumping` | The 3 new tab files (`profile_general_tab.dart`, `profile_scoring_tab.dart`, `profile_layouts_tab.dart`) MUST each be dedicated single-responsibility widgets. No generic `utils.dart` or `helpers.dart` for shared logic — extract into named domain files. |
| `private_helper_bloat_ban` | Extracted helper functions MUST NOT be placed as private methods in the parent `output_profile_crud_view.dart`. They MUST be physically separated into new widget files under `widgets/profile/`. |
| `strategy_pattern_mandate` | The block editor routing in Tab 3 (selecting which block card to render) MUST use a Registry/Map pattern (`Map<TargetBlockType, Widget Function()>`), NOT an `if/elif/else` chain. |
| `remedial_refactoring_coverage` | Before decomposing `output_profile_crud_view.dart`, existing widget test coverage MUST be verified. If below 80%, a Golden Master snapshot test MUST be written first. |
| File limit: **200 lines** per file as hard architectural smell. New tab widgets exceeding this limit MUST be further decomposed. |

---

### 5.2 SDUI Self-Contained Adapter Pattern (`@[ki_sdui_adapter_pattern.md]`)

**Why it applies:** Phase 3 modifies `MetadataAdapter` (V7) and `SynthesisTextAdapter` (V8). Both MUST follow the canonical template.

| Rule ID | Binding Constraint for Epic 144 |
|:--------|:-------------------------------|
| `adapter_two_section_structure` | Every adapter file MUST have exactly 2 sections: **Section 1** = module-level `{NAME}_RULES` dictionary, **Section 2** = Adapter class with `@staticmethod build(context: AdapterContext) -> list[AnySduiBlock]`. Visual decisions (severity, icon, label) MUST live ONLY in Section 1. |
| `adapter_locked_terminology` | Method name: `build`. Parameter: `context`. Type: `AdapterContext`. Return: `list[AnySduiBlock]`. Dictionary suffix: `_RULES`. Internal variable: `blocks: list[AnySduiBlock] = []`. These names are LOCKED and MUST NOT be renamed. |
| `adapter_fail_fast_dictionary_access` | All aesthetics lookups MUST use strict `RULES[key]`. `.get(key, default)` is BANNED. Missing keys MUST crash with `KeyError`. |
| `adapter_context_immutability` | `AdapterContext` is `ConfigDict(frozen=True, strict=True, extra="forbid")`. Constructed ONCE before the dispatch loop. Adapters MUST NOT mutate it. |
| `adapter_direct_data_access` | Adapters MUST read raw data directly from `AdapterContext` root objects (`context.profile`, `context.profile_cache`, `context.execution`). The orchestrator (`blueprint.py`) MUST NOT pre-process data for adapters. |
| `database_driven_dispatch_mandate` | Block dispatch order is 100% database-driven via `OutputProfile.target_block_order`. No hardcoded arrays in Python. |
| `adapter_pure_ssot_synthesis_rendering` | Adapters MUST read dynamic text from `section_syntheses` mapped by layout ID. Global fallback strings (`synthesis_md`) are BANNED. (This directly governs the V8 fix for `SynthesisTextAdapter`.) |

---

### 5.3 Tripartite Pipeline Architecture (`@[ki_tripartite_pipeline_architecture.md]`)

**Why it applies:** Phase 3 requires the Synthesis Text and Metadata adapters to be "Dumb Painters". This KI defines the exact boundary.

| Rule ID | Binding Constraint for Epic 144 |
|:--------|:-------------------------------|
| `tripartite_phase_isolation` | Three strict phases: **(1) Execution** = pure data extraction (NO UI formatting), **(2) Synthesis** = pure text generation (NO data extraction), **(3) SDUI** = pure visual mapping (NO LLM calls, NO domain parsing). `SynthesisTextAdapter` (V8 fix) MUST NOT call LLMs — it reads only pre-computed results from `RenderedSynthesisCache`. |
| `event_driven_data_envelopes` | Phase boundaries communicate via immutable Pydantic DTOs: Execution→Synthesis: `StepOutputDTO`, Synthesis→SDUI: `RenderedSynthesisCache` + `MatrixScorecardRowDTO`, SDUI→Client: `ReportDataDTO` with `inner_sdui_blocks`. |
| `sdui_adapter_dumb_painter` | SDUI Adapters (Phase 3) MUST be 100% "Dumb Painters". `blueprint.py` prepares domain data into `AdapterContext`. Adapters map this data to `AnySduiBlock`. No domain math or DB lookups inside adapters. |
| `synthesis_context_preservation_mandate` | UI layout selections (`OutputProfile.layouts` → `target_blocks`) control ONLY what is painted on screen (Phase 3). They MUST NEVER prune the data available to synthesis (Phase 2). The LLM needs full execution context. |

---

### 5.4 Dual-Axis Localization Architecture (`@[ki_dual_axis_localization_architecture.md]`)

**Why it applies:** Phase 4 localizes all UI strings. Phase 3 fixes hardcoded Finnish labels in `MetadataAdapter` (V7).

| Rule ID | Binding Constraint for Epic 144 |
|:--------|:-------------------------------|
| `structural_localization_axis` | **Axis 1 (Flutter):** Tab titles, button labels, card headers, toggle labels, and all compile-time-known UI chrome MUST use Flutter `.arb` files (`AppLocalizations.of(context)!.keyName`). Backend MUST NOT generate these. |
| `semantic_localization_axis` | **Axis 2 (Backend):** Dynamic labels (profile names, matrix axis names, extension labels, metric labels like "Käyttäjä:", "Organisaatio:") MUST be resolved by backend via `I18nText.resolve(locale)` from `OutputProfile.metric_mappings`. Flutter blindly paints the delivered `text`. |
| `strict_enum_l10n_adapter` | Backend Enums mapped to UI (specifically: `PresetView`, `XaiExtensionType`, `DisplayScale`, `ScoringStrategy`) MUST use explicit `@property def l10n_key(self) -> str:` mapping inside the Python Enum class. NO magic string manipulation (`.lower()`, `.split('_')`). |
| `dynamic_translation_fail_fast` | If a dynamic I18n translation is missing for the active locale, the resolution chain is: (1) active locale → (2) `en` fallback → (3) `throw AppException.validation('Fail-Fast: Missing required translation.')`. NEVER fallback to `fi` or raw IDs. |

---

### 5.5 Strict SDUI Polymorphic Serialization (`@[ki_strict_sdui_serialization.md]`)

**Why it applies:** All block editor changes produce `AnySduiBlock` output. The Python↔Flutter boundary MUST remain type-safe.

| Binding Constraint |
|:-------------------|
| All dynamic UI block arrays MUST be typed as `AnySduiBlock` (Python discriminated union) and `SduiBlockDTO` (Flutter Freezed sealed class). `List<dynamic>` or `list[dict[str, Any]]` is BANNED. |
| Every block MUST have a `block_type` discriminator. Unrecognized `block_type` on the Flutter side MUST crash via `CheckedFromJsonException` (Fail-Fast), NOT silently drop. |
| V3 violation (Section 2.4) directly enforces this: `AsyncValue<List<dynamic>>` → typed `AsyncValue<List<PromptBlock>>`. |

---

### 5.6 SDUI Flat Polymorphic Block Pipeline (`@[ki_flat_polymorphic_pipeline.md]`)

**Why it applies:** The block builder in Tab 3 configures `OutputLayoutBlock.preset_view`, which drives the flattening into `inner_sdui_blocks`.

| Binding Constraint |
|:-------------------|
| The Flutter frontend MUST remain a "Dumb Painter" iterating a flat `inner_sdui_blocks` array. No nested layout routing. |
| `OutputProfile.layouts` is used for authoring/configuration in Studio (Tab 3 block cards), but during rendering `blueprint.py` flattens them entirely into `inner_sdui_blocks`. |
| The Jinja HTML-PDF renderer and the Flutter UI MUST use the exact same flat list in the exact same order. |
| Strict Freezed deserialization (`disallowUnrecognizedKeys: true`) enforces zero data leakage across the Python↔Dart boundary. |

---

### 5.7 SDUI Matrix Synthesis Architecture (`@[ki_sdui_matrix_synthesis.md]`)

**Why it applies:** The Matrix Results block editor (Tab 3 deep configuration) configures `preset_view` which drives graph rendering.

| Rule ID | Binding Constraint for Epic 144 |
|:--------|:-------------------------------|
| `dumb_painter_ui` | Flutter MUST NOT compute scores or apply visual thresholds. Backend `BlueprintTransformer` maps `TargetBlockType` into explicit SDUI blocks. |
| `polymorphic_sdui_serialization` | Enum parity between Python and Dart MUST be verified with `test_enum_parity.py`. If `DisplayScale` enum is added (V6 violation fix), its Dart counterpart MUST have matching `@JsonValue` annotations. |
| `database_ssot_synthesis_outputs` | `seed_data.json` is the absolute SSOT. UI titles MUST come from `output_profile.extension_labels`. Prompt directives MUST NOT be hardcoded in Python. |
| `unified_sdui_graphing_architecture` | All graph visualizations (1D, 2D, 3D) are unified under `OutputLayoutBlock.preset_view`. Backend MUST ALWAYS generate baseline 1D textual blocks (`SduiGridBlock`, `MarkdownBlock`) into `inner_sdui_blocks` for every matrix row, ensuring 100% fallback parity. |

---

### 5.8 Global Config Sovereignty (`@[ki_global_config_sovereignty.md]`)

**Why it applies:** The AI Extensions block editor exposes `max_extension_items`. This limit MUST be fetched from backend `settings.py`, not hardcoded.

| Rule ID | Binding Constraint for Epic 144 |
|:--------|:-------------------------------|
| `global_config_sovereignty_mandate` | All numeric thresholds (`max_extension_items` slider max bound, UI timeout durations) MUST be defined in `backend_v2/settings.py` via Pydantic Settings. NO magic numbers in Flutter or Python business logic. |
| `tripartite_configuration_segregation` | Enums in `enums.py` (finite constants), limits in `settings.py` (configurable), DTOs combine them at runtime. |
| `frontend_enum_parity_mandate` | Any systemic Flutter constraints (like concurrency limits or max slider values) MUST be centralized in `client_app_v2/lib/core/models/enums.dart`. |

---

### 5.9 AI Testing Standards (`@[ki_ai_testing_standards.md]`)

**Why it applies:** Phase 5 runs automated quality gates. New widgets and modified adapters MUST have tests.

| Binding Constraint |
|:-------------------|
| New Flutter tab widgets MUST have widget tests verifying rendering and interaction. |
| Modified Python adapters (`MetadataAdapter`, `SynthesisTextAdapter`) MUST have unit tests with mock `AdapterContext`. |
| All enum parity (Python↔Dart) MUST be verified via `test_enum_parity.py` if new enums are added (`DisplayScale`). |
| Static test fixtures (`report_data_dto_fixture.json`, Flutter `mock_data` JSONs) MUST be updated if DTO schemas change. |

