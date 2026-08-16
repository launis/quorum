# EPIC 144: Output Profile Studio UI Modernization & Visual Block Builder

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Objective
Modernize and decompose the Output Profile editing interface in Quorum Studio (`@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]`) into a clean, 5-tab information architecture aligned with Quorum's Gold Standard Flat MVC and Sub-Tabs paradigm (matching `@[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]`). Replace the unintuitive, text-heavy layout block editor (`@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]`) with an **Adaptive Visual Block Builder** featuring card-based presentation selectors, dedicated X/Y axis bindings for 2D/3D matrices, and decoupled XAI explainability and metadata configuration panes.

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

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Sub-Tab Information Architecture & Scaffold Decomposition
Decompose `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` into a 5-tab `DefaultTabController` scaffold matching the visual stepper idiom of `@[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]`. This strictly enforces the **God Code Prevention mandate** (`@[ki_god_code_prevention.md]`) by physically splitting the 896-line monolithic file into dedicated sub-widgets rather than appending more private helpers. All violations listed in Section 2.4 (Modernity Gate) MUST be eradicated during this phase:
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
  - Master-Detail layout container (30% reorderable list, 70% adaptive visual block editor).
- **Tab 4: 🏷️ Metadata Header (`ProfileMetadataTab`)**
  - Grouped `FilterChip` wrap pills for header badges (`date`, `organization`, `evaluator`, `engine`, `strictness`, `cost`, `tokens`).
- **Tab 5: 🔍 XAI Explainability (`ProfileXaiTab`)**
  - Grouped `FilterChip` wrap pills for block-level and workflow-level XAI extensions (`source_quotes`, `evidence_reasoning`, `devils_advocate`, `risk_flags`, `coaching_recommendations`, `contextual_override`).
  - Numerical limiter for `maxExtensionItems`.

### Phase 2: Adaptive Visual Block Builder & UI Patterns
Refactor the UI (`@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]`) to strictly follow the new "Flat Master-Detail" architecture within the Report Structure tab. Implement the following approved UI patterns:

1. **Universal Baseline (The Block Visibility Toggle):**
   - EVERY block editor (Metadata, Exec Summary, Matrix Results, etc.) MUST start with a primary toggle: `Include this block in the final report`. This controls the baseline visibility of the block in the final PDF/SDUI output.

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
   - Option A (Pipeline Way): Dropdown to select a `synthesis_block_id` (fetches existing deep analysis).
   - Option B (On-the-Fly): Text fields for `tone_instruction` and `preamble_text` to generate summaries at render-time, optionally combining with `historical_context_mode`. (Structural `system_prompt` rules MUST remain locked in Python `prompt_compiler.py`).
   - Includes a multilingual `preamble_text` rich text editor.

5. **AI Extensions Editor (FilterChip Pattern):**
   - Utilizes interactive `FilterChip` pills to quickly enable/disable specific XAI extensions (specifically and exhaustively: Practical Tips, Devil's Advocate, Remedial Actions, Risk Analysis, Source Quotes, Evidence Reasoning).
   - Includes a `Display Settings` slider to control `max_extension_items` (the maximum limit MUST be fetched programmatically from backend settings.py to respect global config sovereignty).

6. **Source Quotes & Bibliography Editor:**
   - Follows the Universal Baseline toggle (`Include Bibliography in the final report`).
   - Configuration options for formatting (specifically: grouped_by_matrix or chronological) and determining if quotes should be printed anonymously or with explicit source document attribution.

### Phase 3: Backend Execution & Synthesis Alignment
> [!WARNING]
> **Atomic Cross-Domain Migration Mandate**: The `include_bibliography` field is NEW and does not exist in the current codebase. Because the Flutter model uses `@JsonSerializable(disallowUnrecognizedKeys: true)`, the Flutter Freezed model (`@[client_app_v2/lib/features/studio/models/output_profile.dart]`) MUST be updated to accept this field BEFORE the backend DTO starts sending it. Failure to enforce this order will cause an instant `CheckedFromJsonException` crash (White Screen of Death).

1. **DTO Synchronization (Flutter-First Order):**
   - **Step 3.1a (Flutter):** Add `@JsonKey(name: 'include_bibliography') @Default(false) bool includeBibliography` to `OutputProfile` in `@[client_app_v2/lib/features/studio/models/output_profile.dart]`. Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`.
   - **Step 3.1b (Backend):** Add `include_bibliography: bool = Field(default=False, ...)` to `OutputProfileCreateDTO` and `OutputProfileUpdateDTO` in `@[backend_v2/models/dtos/output_profile.py]` and to `OutputProfile` in `@[backend_v2/models/v2_core.py#L1313-L1398]`. Run `uv run python scripts/backend_audit_loop.py backend_v2/models --test`.
   - Ensure `SynthesisConfigDTO` robustly supports dual-mode synthesis.
2. **Tripartite Synthesis & SDUI Alignment:**
   - **Phase 2 (Synthesis Engine):** Must handle the LLM execution for Tapa B (`system_prompt`) and save the output to `profile_cache`.
   - **Phase 3 (SDUI Adapter):** Refactor `@[backend_v2/services/sdui/adapters/synthesis_text_adapter.py]` to strictly act as a "Dumb Painter" (`@[ki_tripartite_pipeline_architecture.md]`). It MUST NOT execute LLM calls. It must solely read the pre-computed Tapa A or Tapa B results from `profile_cache`.
3. **Bibliography Alignment:** Refactor `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` to strictly enforce the UI's `include_bibliography` baseline visibility toggle and any new grouping settings.
4. **Adapter Pattern Strictness:** All modified adapters MUST strictly follow the 2-section canonical template (AESTHETICS_RULES dictionary + Adapter Class), utilizing fail-fast dictionary access and immutable `AdapterContext` (`@[ki_sdui_adapter_pattern.md]`).

### Phase 4: Localization Synchronization & Freezed Validation
1. Update `@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]` with comprehensive UI keys for all 5 tabs, preset cards, and helper tooltips.
2. **Dual-Axis Compliance:** Enforce that Backend Enums mapped to the UI (specifically: PresetView, XaiExtensionType) utilize strict `@property def l10n_key(self) -> str:` mapping. The Frontend MUST NOT use magic string manipulation (specifically: the Dart string manipulation method `.lower()`) or ID fallbacks to resolve translations (`@[ki_dual_axis_localization_architecture.md]`).
3. Execute `flutter gen-l10n` to compile localization files.
4. Validate Freezed model serialization with `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`.

### Phase 5: Automated Verification & Quality Gates
1. Run localized Flutter unit and widget test suite on Studio output profile views.
2. Run global quality gates: `uv run python scripts/backend_audit_loop.py backend_v2 --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`.

---

## 4. Definition of Done (DoD) & Verification Plan

### 4.1 Definition of Done (DoD)
- [ ] `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` is decomposed into a 5-tab `DefaultTabController` scaffold.
- [ ] Five dedicated sub-tab widgets exist in `@[client_app_v2/lib/features/studio/views/widgets/profile/]`:
  - `profile_general_tab.dart`
  - `profile_scoring_tab.dart`
  - `profile_layouts_tab.dart`
  - `profile_metadata_tab.dart`
  - `profile_xai_tab.dart`
- [ ] `@[client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart]` provides visual card selection for `PresetView` with adaptive form fields.
- [ ] No manual comma-separated `steps` text fields remain in the UI.
- [ ] All UI strings exist in both English (`app_en.arb`) and Finnish (`app_fi.arb`).
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
2. Verify all 5 top tabs render with icons and labels matching the design standard of `WorkflowBuilderView`.
3. Switch between tabs: verify smooth transitions and zero layout overflow errors.
4. On Tab 3 (Report Structure), add a new layout block, select `2D Grid Comparison`, verify X and Y axis selectors appear cleanly, save profile, and verify database persistence.

---

## 5. Required Knowledge Items (KI Registry)

<required_knowledge_items>
- @[ki_god_code_prevention.md]
- @[ki_sdui_matrix_synthesis.md]
- @[ki_strict_sdui_serialization.md]
- @[ki_dual_axis_localization_architecture.md]
- @[ki_ai_testing_standards.md]
- @[ki_sdui_adapter_pattern.md]
- @[ki_tripartite_pipeline_architecture.md]
- @[ki_flat_polymorphic_pipeline.md]
- @[ki_global_config_sovereignty.md]
- @[ki_synthesis_payload_compression.md]
- @[ki_python_314_concurrency_strictness.md]
- @[ki_dag_engine_dto_projection_rules.md]
</required_knowledge_items>
