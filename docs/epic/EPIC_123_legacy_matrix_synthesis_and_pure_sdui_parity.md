# EPIC 123: Legacy Matrix Synthesis and Pure SDUI Parity

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
>
> Implementing Server-Driven UI (SDUI) effectively in 2025-2026 requires a mature architectural pattern centered on "Design-First Contracts." Industry best practices emphasize avoiding deep nesting and data-model dependency on the client. Instead, the backend must construct explicit UI component blocks (e.g., `AlertBlock`, `QuoteBlock`) rather than transmitting flat string properties (like `coaching: "Do this"`). This "demand-driven" approach ensures the client acts strictly as a "Dumb Painter", rendering the payload blindly, which guarantees 100% deterministic pixel-parity across Flutter apps and generated PDFs while preventing "re-hydration churn".

---

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective
Restore the rich synthesis styling and XAI output extensions (e.g., "Arjen Vinkki", "Vasta-argumentti", Jargon Ratio) that existed prior to Epic 110/122, ensuring complete visual parity between the interactive Flutter UI and the generated PDF report.

### Problem Statement
During the implementation of Epic 111 (Dumb Painter SDUI) and Epic 122 (Legacy Parity Output Profile), the hardcoded HTML logic responsible for styling Matrix extensions in `report_template.jinja2` was removed to enforce the strict ICU Markdown Parity rule. Furthermore, backend mapping for these extensions was flattened. As a result, the premium colored boxes and AI-generated synthesis text vanished from the final outputs. 

The challenge is to bring these rich visual elements back WITHOUT violating the new SDUI architecture. We cannot revert to "duct tape" hardcoded HTML or Flutter-side string-parsing.

### Root Cause / Gap Analysis
- **AlertBlock.severity Type Gap (Juurisyy 3):** Currently, Python's `AlertBlock` supports `Literal["info", "warning", "critical_override"]`. When legacy matrix extensions are converted to SDUI blocks, we also strictly require `"success"` (e.g., for Remediation Steps) and `"error"`. The `AlertBlock.severity` field MUST remain a standalone `Literal` type (NOT coupled to the `VisualIntent` enum, which serves a different domain — atom-level rendering intent). The Literal MUST be expanded to `Literal["info", "warning", "critical_override", "success", "error"]`. On the Dart side, `SduiAlertBoxBlock.severity` is currently a raw `String` (confirmed at `@[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart#L32]`). This MUST be refactored to a new strict `@JsonEnum() enum AlertSeverity` in `enums.dart`, whose values precisely mirror the backend `Literal`.
- **VisualIntent Enum Deficit (Juurisyy 4):** The `VisualIntent` enum (`@[c:\src\quorum\backend_v2\models\enums.py#L116-L123]`) currently contains `SUCCESS`, `WARNING`, `CRITICAL_OVERRIDE`, `INFO`, `NEUTRAL`. The Dart equivalent (`@[c:\src\quorum\client_app_v2\lib\core\models\enums.dart#L249-L260]`) mirrors this exactly. This Epic adds `ERROR` to `VisualIntent` for use in atom-level rendering (e.g., short-circuit atoms). `DANGER` is NOT added (YAGNI — no concrete use case exists in this Epic's scope).
- **HighlightBoxDisplay Duct Tape Parsing (Juurisyy 5):** In Flutter (`@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\xai_extensions_box.dart#L204-L205]`), `color_theme` is parsed loosely via `val['color_theme']?.toString() ?? 'info'` without a Freezed model. This violates the "Zero Duct Tape" SDUI rule. This entire widget (466 lines) is a legacy monument to anti-patterns (`List<dynamic>`, raw dict duck-typing, hardcoded colors) and MUST be fully sunset in Phase 4 once `inner_sdui_blocks` replaces its function.
- **AssessmentView & ReportView Type Gaps (Juurisyy 6):** `AssessmentView.uiVariant` lacks a corresponding Enum in Dart, and `ReportView.status_theme` is typed loosely as `StrictStr` in Python. These must be synchronized across the stack using unified Enums.
- **Dart Freezed "Silent Failure" Risk (Juurisyy 7):** When extending SDUI components and severity enums, there is a risk of using `@Default("unknown")` or `fallbackUnion: 'unknown'` in Dart to prevent crashes. This violates Quorum's Anti-Hallucination and Fail-Fast rules. An unknown SDUI block or an incorrect severity value MUST crash the view (throw `CheckedFromJsonException`) so the Error Boundary catches it immediately in CI/CD, rather than hiding the error from end users.
- **Backend Duck-Typing Risk in SDUI Mapper (Juurisyy 8):** The source of this duck-typing is `TraceMatrixPayloadDTO.extensions`, which is currently a loose `dict[str, Any]`. When extracting legacy flat fields (e.g., `coaching`) from this dict to generate `AlertBlock` models, using defensive programming like `.get("coaching")` circumvents static typing. This dict MUST be converted to a strict Pydantic model (`TraceMatrixExtensionsDTO`) so `blueprint.py` can use strict attribute referencing (`if matrix_payload.extensions.coaching:`). If the underlying schema changes or a field is removed, duck-typing causes a silent failure (returning `None` without crashing), leading to missing SDUI blocks in production.
- **`grouped_extensions` COMPLETE Sunset (Juurisyy 9):** The existing `ReportDataDTO.grouped_extensions: dict[str, list[Any]]` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1227]`) is the CURRENT mechanism for passing XAI extensions to both Flutter and Jinja. `blueprint.py` has 30+ references to it. This field MUST be COMPLETELY DELETED in this Epic. ALL extension data — both row-level (`coaching`, `falsification`, etc.) AND global (`variance_validation`) — MUST be migrated to typed `inner_sdui_blocks` arrays. Furthermore, `list[Any]` violates the 2026 `Any`-inside-lists ban. No old-style rendering paths may remain.
- **`confidence` Numeric Field Mismatch (Juurisyy 10):** The `confidence: float | None` field on `MatrixScorecardRowDTO` is a NUMERIC value. It cannot be meaningfully represented as an `AlertBlock` (which expects `text: str`). This field must be excluded from the `inner_sdui_blocks` migration and either retained as a standalone numeric field or mapped to a different SDUI block type (e.g., a future `MetricBlock`).
- **`GlobalSynthesisDTO` SDUI Violation (Juurisyy 11):** The `global_synthesis` field on `ReportDataDTO` currently passes raw string fields (e.g., `executive_summary`, `user_role`) to the frontend. This forces Flutter to use hardcoded, client-side UI logic to render the report's main summary, violating the SDUI Dumb Painter architecture.
- **Epic 120 Leftovers (`list[Any]` Leaks) (Juurisyy 12):** Epic 120 Phase 3 mandated the eradication of `list[Any]` from all SDUI models. However, `SduiGridBlock.items` and `SduiQuoteCard.citations` were skipped and remain loosely typed. These must be explicitly typed (e.g. `list[str | int | float]` or `list[int]`) to enforce full SDUI strictness.

### Strategic Scope
This Epic achieves visual restoration through **pure dynamic SDUI**. The backend (`blueprint.py`) will transform flat string properties extracted by the AI into a structured `inner_sdui_blocks` array (utilizing existing models like `AnySduiBlock`). Both the Flutter frontend and the PDF Jinja template will simply execute their standard generic SDUI rendering pipelines over these inner blocks.

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **Hardcoded Extension Rendering Logic**: Any remaining Flutter code attempting to parse `coaching` or `falsification` strings to render specific UI containers will be INTENTIONALLY DROPPED in favor of the `SduiRenderer`. The entire `xai_extensions_box.dart` widget (466 lines) MUST be sunset once `inner_sdui_blocks` replaces its function.
- **Emoji Injection**: Hardcoded emojis in `extension_labels` will be purged to ensure clean, professional strings.
- **Legacy Flat STRING Fields**: The old STRING presentation fields (e.g., `coaching`, `falsification`, `missing_context`, `risk_flag`, `remediation_steps`, `emotional_sentiment`, `theory_link`) MUST be ruthlessly deleted from BOTH the Python `MatrixScorecardRowDTO` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L970-L978]`) and the Flutter Freezed equivalent (`@[c:\src\quorum\client_app_v2\lib\features\execution\models\matrix_scorecard_dto.dart#L138-L146]`). **EXCEPTION**: The `confidence: float | None` field is NUMERIC, not textual, and MUST be RETAINED as a standalone field (it does not map to `AlertBlock`). This enforces the Single Source of Truth (SSOT) and prevents "Legacy Flat Field Eradication" violations.
- **`grouped_extensions` COMPLETE Sunset**: The `grouped_extensions: dict[str, list[Any]]` field on `ReportDataDTO` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1227]`) MUST be **RUTHLESSLY DELETED** in this Epic. ALL extension categories — both row-level (`coaching`, `falsification`, `remediation_steps`, etc.) AND global (`variance_validation`) — MUST be migrated exclusively to typed `inner_sdui_blocks` arrays on their respective DTOs. The `variance_validation` extension MUST be converted to a proper SDUI block type (e.g., a new `SduiVarianceBlock` or mapped to existing block types). `blueprint.py` MUST be refactored to stop populating `grouped_extensions` entirely. The Flutter `XAIExtensionsBox` widget and the Jinja `grouped_extensions` rendering panel MUST be fully deleted. **Zero old-style rendering paths may remain.**
- **`GlobalSynthesisDTO` COMPLETE Sunset**: The `global_synthesis` field and the `GlobalSynthesisDTO` model itself MUST be entirely **DELETED** from both Python and Dart. All high-level report synthesis data (e.g., `executive_summary`, `user_role`) MUST be mapped directly into standard SDUI blocks (like `MarkdownBlock` or `AlertBlock`) by the backend and appended to the `ReportView.sections` array.

### Retained SSOT Invariants (What We Will RETAIN)
- **Universal Static vs Dynamic SDUI Routing**: It is categorically mandated that across ALL current and future matrices (and Epics), the process must operate identically. Static explanations, instructions, and titles MUST be fetched directly from the database templates (e.g., `extension_labels` localized to target language), while only the dynamic synthesized insights are passed via LLM generation. The Flutter client remains completely blind to this difference.
- **Strict Anti-Hallucination Deserialization (No Silent Failures)**: It is STRICTLY FORBIDDEN to use `@JsonKey(unknownEnumValue: ...)` or `@Freezed(fallbackUnion: ...)` in any Dart SDUI block or Enum model (such as `VisualIntent` or `SduiBlockDTO`). Unrecognized keys or invalid enums MUST intentionally throw a `CheckedFromJsonException` to trigger the Fail-Fast mechanism and Error Boundaries.
- **Strict Attribute Referencing (No Duck-Typing)**: When the backend translates domain objects to SDUI models, it MUST use direct static attribute referencing (e.g., `if row.coaching:`). The use of `.get()`, `hasattr()`, or `getattr(..., default)` on strictly typed Pydantic models is strictly forbidden. This ensures that any schema refactoring instantly triggers an `AttributeError` or MyPy failure, enforcing the Fail-Fast mandate.
- **`SduiBlockDTO` / `AnySduiBlock`** (`@[c:\src\quorum\backend_v2\models\view\sdui.py]`): The backend and frontend will strictly utilize the existing sealed polymorphic models. No new parallel schemas will be introduced.
- **Strict ICU Markdown Parity**: The PDF template (`@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`) will remain devoid of manual HTML formatting for specific data fields, relying entirely on the `render_sdui_blocks()` macro.

### Compliance & Modernity Gates
| Gate | Status |
|---|---|
| Pydantic V2 `ConfigDict(strict=True, extra='forbid')` | ✅ Inherited via `V2CoreBase` |
| Cross-Domain DTO Parity | ✅ Backend `MatrixScorecardRowDTO` syncs with Flutter Freezed model |
| Fail-Fast SDUI Serialization | ✅ `SduiRenderer` consumes strictly typed `SduiBlockDTO`s |
| Zero Duct Tape Rule | ✅ No client-side conditional styling based on magic keys |
| RFC-7807 Dual-Reporting | ✅ Maintained during pipeline hydration |

### Producer-Consumer Integration Check
| Producer | Consumer | Contract |
|---|---|---|
| Backend `blueprint.py` | `MatrixScorecardRowDTO.inner_sdui_blocks` | Transforms AI strings into `list[AnySduiBlock]` (e.g. `AlertBlock`) |
| Backend `MatrixScorecardRowDTO` | Flutter `matrix_row_item_widget.dart` | Pipes `innerSduiBlocks` array to `SduiRenderer` |
| Backend `MatrixScorecardRowDTO` | Jinja `report_template.jinja2` | Passes `inner_sdui_blocks` to `render_sdui_blocks()` macro |

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Database Seed Restoration
- **Target**: @[c:\src\quorum\backend_v2\seed\seed_data.json#L7900-L11000]
- Locate the first `text_only` layout named `"YHTEENVETO"` in the `holistic_audit` profile.
- Restore its `synthesis.system_prompt` to the original XML prompt and `synthesis.preamble_text` to the rich default ("Raportti tekoälytaidoistasi...").
- For matrix layouts (`2d_compare`, `3d_matrix`) with synthesis, explicitly set `"row_explanations_block_id": "sp_row_explanations"`.
- **MATRIX COLUMNS FIX (from Epic 122 Audit)**: Ensure the `3d_matrix` layout block explicitly contains the array `"matrix_visible_columns": ["label", "distribution", "row_explanation", "normalized_score", "score"]`. Epic 122 created the DTO support for this but failed to add it to the seed data.
- Strip all emojis from `extension_labels` (e.g., `"💡 ARJEN VINKKI"` -> `"ARJEN VINKKI"`).
- **ATOMIC TEST SYNC**: If any backend test fixture (e.g., `@[c:\src\quorum\backend_v2\test_data\report_data_dto_fixture.json]`) asserts on emoji-prefixed `extension_labels` strings, those assertions MUST be updated atomically in this phase to match the stripped labels.

> [!CAUTION]
> **Architectural Justification for Phase Order (Fail-Fast Mandate):**
> Quorum operates with strict Zero-Tolerance typing (`extra='forbid'`, `disallowUnrecognizedKeys: true`). Updating the Producer (Backend logic) before the Consumer (Frontend schema) causes an immediate WSOD crash when the frontend encounters new/removed fields during deserialization. Therefore, **Phase 2 MUST atomically synchronize the DTO Contracts in both Python and Dart** BEFORE any backend data hydration (Phase 3) or UI rendering (Phase 4) is implemented.

### Phase 2: Atomic Schema & Contract Migration (Backend + Frontend)
- **Target Python**: `@[c:\src\quorum\backend_v2\models\v2_core.py#L943-L1010]`, `@[c:\src\quorum\backend_v2\models\view\sdui.py#L518-L526]`, `@[c:\src\quorum\backend_v2\models\enums.py#L116-L123]`
- **Target Flutter**: `@[c:\src\quorum\client_app_v2\lib\core\models\enums.dart#L249-L260]`, `@[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart#L27-L35]`, `@[c:\src\quorum\client_app_v2\lib\features\execution\models\matrix_scorecard_dto.dart#L112-L170]`
- **DTO Sync (Matrix)**: Update `MatrixScorecardRowDTO` in Python to include `inner_sdui_blocks: list[AnySduiBlock] = Field(default_factory=list)` and delete legacy STRING XAI fields (`coaching`, `falsification`, `missing_context`, `risk_flag`, `remediation_steps`, `emotional_sentiment`, `theory_link`). **RETAIN** `confidence: float | None` as-is (numeric, not textual). **ATOMICALLY** update the Flutter Freezed model for `MatrixScorecardRowDto` to add `innerSduiBlocks: List<SduiBlockDTO>` and delete the same legacy string fields.
- **DTO Sync (Trace)**: Update `TraceMatrixPayloadDTO` in `backend_v2/models/dtos/trace.py`. Convert `extensions: dict[str, Any] | None` into a strictly typed `extensions: TraceMatrixExtensionsDTO | None`. Create `TraceMatrixExtensionsDTO` containing all expected extension strings (`coaching`, `falsification`, `remediation_steps`, `missing_context`, `emotional_sentiment`, `theory_link`, `risk_flag`) as optional string fields. This eliminates the duct-tape dictionary extraction.
- **DTO Sync (GlobalSynthesis)**: Delete `GlobalSynthesisDTO` entirely from Python and Dart. Delete the `global_synthesis` field from `ReportDataDTO` in Python and the corresponding `ReportDataDto` Freezed model in Dart.
- **Backend Enum & Literal Sync**: Add `ERROR = "error"` to Python `VisualIntent` enum (`@[c:\src\quorum\backend_v2\models\enums.py#L116-L123]`). Expand `AlertBlock.severity` Literal to `Literal["info", "warning", "critical_override", "success", "error"]` (`@[c:\src\quorum\backend_v2\models\view\sdui.py#L523]`). These are SEPARATE type systems: `VisualIntent` is for atom-level rendering intent; `AlertBlock.severity` is for alert-specific severity.
- **Frontend Enum Sync**: Add `error` to Dart `VisualIntent` enum. Create a NEW `@JsonEnum() enum AlertSeverity` in `enums.dart` with values `info`, `warning`, `criticalOverride`, `success`, `error`. Refactor `SduiAlertBoxBlock.severity` from `String` to `AlertSeverity`. Do NOT add `danger` (YAGNI — no use case in this Epic).
- **Cross-Language Parity Gate**: The existing `test_enum_parity.py` (`@[c:\src\quorum\backend_v2\tests\architecture\test_enum_parity.py#L147-L162]`) MUST pass after these enum changes.
- **Legacy Comment Cleanup**: Remove `// Epic 6:` and `// Epic 88` comments from `matrix_scorecard_dto.dart` (violates `internal_language_and_epic_ban`).
- **Test Sync**: Update ALL mock test fixtures in Python and Dart ATOMICALLY in this phase to prevent WSOD crashes during CI, ensuring they remove legacy flat fields and utilize the `inner_sdui_blocks` structure.
- **EPIC 120 Leak Cleanup**: Fix the remaining `list[Any]` type leaks in `backend_v2/models/view/sdui.py`. Update `SduiGridBlock.items` to a strict union (e.g., `list[str | int | float]`) and `SduiQuoteCard.citations` to `list[int]`. Synchronize the corresponding Dart Freezed models to ensure full 2026 strictness.

### Phase 3: Producer Logic (Backend SDUI Hydration)
- **Target**: `@[c:\src\quorum\backend_v2\services\blueprint.py]`
- In `blueprint.py`, during matrix extraction, transform string fields (`coaching`, `falsification`) into `AlertBlock` models using **Strict Attribute Referencing** (`if row.coaching:`). **CRITICAL ARCHITECTURE INVARIANT**: Do NOT hardcode Finnish strings or emojis like `"**💡 Arjen Vinkki:**"` in Python. You MUST dynamically read the localized label from the matrix's `extension_labels` mapping. Emojis are purposefully stripped because the `AlertBlock` `severity` parameter (e.g., `info`) will command the Flutter frontend to render the appropriate native icon automatically.
- **Migration Boundary**: The current `blueprint.py` populates `grouped_extensions` with row-level extension data using raw dicts and duck-typing (e.g., `ext_val.get("_is_synthesized")` at `@[c:\src\quorum\backend_v2\services\blueprint.py#L692]`). This MUST be refactored: ALL extensions — both row-level (`coaching`, `falsification`, `remediation_steps`, `missing_context`, `emotional_sentiment`, `theory_link`, `risk_flag`) AND global (`variance_validation`) — MUST now be hydrated as typed SDUI block models (e.g., `AlertBlock` for text extensions, a typed block for variance data) and placed into `inner_sdui_blocks` arrays. ALL `grouped_extensions` population logic in `blueprint.py` (30+ references) MUST be removed entirely.
- **`variance_validation` Migration**: The `variance_validation` extension data (currently containing `variance_score`, `alignment_verdict`, `mechanical_metric_ref`, `cognitive_metric_ref`) MUST be converted to a proper typed SDUI block. Options: (a) create a new `SduiVarianceBlock` added to `AnySduiBlock`, or (b) map to an existing `SduiGridBlock` with strictly typed items. The chosen approach MUST be serializable through the existing `SduiRenderer` pipeline.
- **`GlobalSynthesisDTO` Migration**: Refactor `blueprint.py` to stop generating `GlobalSynthesisDTO`. Instead, map the `executive_summary`, `user_role`, AND `user_role_justification` directly into standard SDUI blocks (e.g., `MarkdownBlock`) and inject them into a `UiSection` in the `ReportView.sections` array. (Note: `user_role_justification` was recently added by Epic 122; it MUST be mapped here so it doesn't get silently dropped).
- **`ReportDataDTO.grouped_extensions` Field Deletion**: After all migration is complete, the `grouped_extensions` field MUST be deleted from `ReportDataDTO` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1227]`) and its Flutter equivalent.
- Implement `_hydrate_printable_sources_block` and `_hydrate_jargon_ratio_block`, converting them into `SduiBlockDTO` structures rather than raw strings.

### Phase 4: Consumer Logic (Frontend & PDF Rendering)
- **Target Flutter**: `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\matrix_row_item_widget.dart]`
- **Target Jinja**: `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`
- In Flutter, pass `row.innerSduiBlocks` directly to the `SduiRenderer` within the expandable container.
- Ensure `SduiAlertBoxWidget` correctly parses and paints all required severities (`info`, `error`, `success`, `warning`, `critical_override`) utilizing dynamic colors from the theme.
- In Jinja, invoke `{{ render_sdui_blocks(axis.inner_sdui_blocks) }}` inside the matrix layout loop.
- **XAI Extensions Box DELETION**: Delete `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\xai_extensions_box.dart]` entirely (466 lines). Remove all import references from `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart]`. The `XAIExtensionsBox` widget is fully superseded by the `SduiRenderer` consuming `inner_sdui_blocks`. ALL code paths referencing `grouped_extensions` in Flutter MUST be removed.
- **XAI Axis Telemetry Grid Cleanup**: In `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\xai_axis_telemetry_grid.dart]`, the `groupedExtensions` constructor parameter MUST be removed. The hardcoded UI rendering logic for `riskFlag`, `emotionalSentiment`, and `theoryLink` MUST be completely deleted (as these fields are deleted in Phase 2). The rendering of `confidence` MUST be updated to trigger simply on `axis.confidence != null` (removing the `groupedExtensions` dependency).
- **Global Synthesis UI Refactoring**: Remove all hardcoded UI logic in Flutter that previously parsed the `globalSynthesis` object to render the header. The report header will now render automatically via the standard SDUI `sections` pipeline.
- **Jinja `grouped_extensions` Panel DELETION**: The entire global extensions panel in the Jinja template (`@[c:\src\quorum\backend_v2\templates\report_template.jinja2#L385-L424]`) that renders `grouped_extensions` MUST be **DELETED**. All extension rendering (including `variance_validation`) is now handled exclusively by `render_sdui_blocks(axis.inner_sdui_blocks)` in the matrix loop. Zero old-style rendering paths may remain.

### Phase 5: Verification & E2E Integration Gate
- **NOTE**: Test fixture migration already completed atomically in Phase 2. This phase is VERIFICATION ONLY.
- Execute `backend_audit_loop.py` to ensure schema integrity and routing.
- Execute `flutter_audit_loop.py --build` to synchronize Freezed DTOs and verify widget compilation.
- **COMPLETE `grouped_extensions` Eradication Verification**: Confirm that the `grouped_extensions` field has been DELETED from `ReportDataDTO` (Python) and its Flutter equivalent. Verify with `grep_search` that ZERO references to `grouped_extensions` remain in `blueprint.py`, `sdui_mapper_service.py`, `report_template.jinja2`, and all Flutter widget files. Any remaining reference is a BLOCKING failure.
- Perform a live database seed and generate a holistic audit report to verify visual parity between Flutter and PDF.

### Phase 6: Multilingual & Localization (i18n) Verification
To guarantee complete multilingual support across all textual generation sources, the implementation MUST adhere to the following routing:
- **Database Source (`extension_labels`)**: Because `AlertBlock.text` expects a `str`, `blueprint.py` MUST resolve the `I18nText` object from `extension_labels` using the current Execution's `target_language` before injecting it into the SDUI block (e.g., `label = ext_labels[type].get_translation(execution.target_language)`). The backend MUST ALWAYS provide the fully resolved string — the frontend NEVER performs translation lookups on SDUI block content.
- **Prompt Directory Features (`models/prompts`)**: If any textual prefixes (e.g., "Jargon Ratio:") are injected via static prompt configurations, the backend MUST utilize the localized properties matching the `target_language` rather than hardcoding.

> [!CAUTION]
> **SDUI Dumb Painter Mandate (Absolute Rule):** The frontend MUST NOT contain any translation resolution logic for SDUI block content. All `AlertBlock.text` values MUST arrive from the backend as fully resolved, render-ready strings in the correct `target_language`. Transmitting ARB translation keys inside `AlertBlock.text` for client-side resolution is **STRICTLY FORBIDDEN** — it violates the Dumb Painter architecture and creates frontend-side business logic.

- **LLM Prompt Generation (`linguistic_directives.py`)**: If the AI prompt itself is directed to generate the explanations or text (e.g., matrix synthesis), it MUST NOT use hardcoded natural language instructions (e.g., "Please write in Finnish"). Instead, the prompt MUST strictly utilize the `<linguistic_context>` XML pattern defined in `backend_v2/models/prompts/linguistic_directives.py`, ensuring the LLM dynamically respects the `target_locale` across all generated string fields.
- **Dynamic Enums and Roles (e.g., "Käyttäjän Rooli")**: Any dynamic labels referring to system states, user classifications, or assigned roles (such as the "Arkkitehti" role in the output summary) MUST be mapped and retrieved dynamically through the system's official Enum definitions and their corresponding translation functions. Hardcoding such classification strings in templates, LLM prompts, or synthesis outputs is strictly forbidden.
- **Strict Extension Generation (`EXTENSION_ANCHORING_MANDATE`)**: The generation of these extensions (such as remediation_steps) is governed strictly by the `EXTENSION_ANCHORING_MANDATE` in `global_mandates.py`. The LLM MUST anchor every extension to the raw input data, ensuring the content is a directly actionable consequence of the data rather than generic theoretical advice.

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- [ ] Matrix extensions (Arjen Vinkki, jne.) are transmitted exclusively as `SduiBlockDTO` objects.
- [ ] Zero hardcoded HTML exists in `report_template.jinja2` for specific matrix extensions.
- [ ] Zero hardcoded string parsing exists in Flutter UI for specific matrix extensions.
- [ ] The generated PDF and Flutter UI display identical, visually rich colored boxes.
- [ ] The `grouped_extensions` field is completely DELETED from `ReportDataDTO` and all rendering paths.
- [ ] The `GlobalSynthesisDTO` model and `global_synthesis` field are completely DELETED.
- [ ] `xai_extensions_box.dart` is completely DELETED from the codebase.
- [ ] Python Pydantic models and Dart Freezed models are mathematically aligned and pass automated audits.

### Automated Unit Tests
- `uv run python scripts/backend_audit_loop.py backend_v2/seed/seed_data.json`
- `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/widgets --build`

### MANDATORY Final E2E REST API Verification Gate
```powershell
$env:RUN_LIVE_E2E="true"
uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 5. Expected Output & Test Fixture Payload

This section defines the exact target payload expected after implementation. **This identical JSON structure MUST be utilized as the baseline mock fixture in both Backend and Frontend automated tests** (e.g., `test_blueprint.py` and `matrix_scorecard_dto_test.dart`) to guarantee the polymorphic `inner_sdui_blocks` deserializer handles the SDUI mapping correctly. Note: the `confidence` field is retained as a standalone numeric value (not in `inner_sdui_blocks`). The example below represents the complete top-level `ReportView` payload to illustrate how the matrix sits within the broader ecosystem of summaries, graphs, and citations.

```json
{
  "view_id": "exe_1c38d59faaa94ae1aa48c3b9ba464c78",
  "title": "KOKONAISVALTAINEN AUDITOINTI",
  "status_theme": "success",
  "metrics": {
    "kokonaiskeskiarvo": "19.30/100",
    "radar_chart_data": {
      "labels": ["Episteeminen Nöyryys", "Harkintakyky", "Päättelyn rehellisyys"],
      "datasets": [{"label": "Tulos", "data": [29.0, 15.0, 15.0]}]
    }
  },
  "system_notification": null,
  "references": [],
  "sections": [
    {
      "id": "sec_summary",
      "type": "HEADER",
      "title": "Yhteenveto",
      "data": {
        "content": "**Raportti tekoälytaidoistasi**\n\nTämä raportti analysoi tapaasi hyödyntää tekoälyä ja auttaa sinua kehittymään sen strategiseksi ohjaajaksi. Arvioinnissa keskitytään kolmeen osa-alueeseen:\n- **Oivalluskyky**: Pureudutko syvälle aiheeseen vai jäätkö pintatasolle?\n- **Logiikka ja päättely**: Miten perustelet väitteesi ja haastat tekoälyn vastauksia?\n- **Luotettavuus**: Miten hallitset prosessia ja sen läpinäkyvyyttä?\n\nKäyttäjän Rooli: **Arkkitehti**."
      }
    },
    {
      "id": "sec_scorecard",
      "type": "SCORE_CARD",
      "title": "YHTEENVETO / MATRIX SUMMARY",
      "data": {
        "preset_view": "3d_matrix",
        "title": {
          "fi": "Yhteenveto / Matrix Summary",
          "en": "Matrix Summary"
        },
        "description": {
          "fi": "Arvioinnin yksityiskohtainen pisteytys ja erittely osa-alueittain.",
          "en": "Detailed scoring and breakdown by dimension."
        },
        "is_synthesis_enabled": true,
        "synthesis_blocks": [
          {
            "block_type": "paragraph",
            "text": "Osoitat poikkeuksellista kykyä jäsentää monimutkaisia ongelmia ja ohjata tekoälyä systemaattisella, iteratiivisella prosessilla.",
            "exact_quotes": [],
            "citations": []
          }
        ],
        "axes": [
          {
            "block_id": "mat_episteeminen_noyryys",
            "name": "Oman tiedon rajat (Episteeminen Nöyryys)",
            "label_i18n": {
              "fi": "Oman tiedon rajat",
              "en": "Epistemic Humility"
            },
            "description": "Arvioi kykyäsi tunnistaa, mitä et tiedä. Se varoittaa liiallisesta varmuudesta asioissa, jotka ovat todellisuudessa epävarmoja.",
            "score": 29.0,
            "scale_min": 0.0,
            "scale_max": 100.0,
            "inner_sdui_blocks": [
              {
                "block_type": "alert_box",
                "severity": "info",
                "text": "**💡 ARJEN VINKKI:**\n\nKun tekoäly tarjoaa spesifejä lähteitä, kuten tutkimuksia, on kriittisen tärkeää yrittää validoida ne ulkoisella hakukoneella. Tämä auttaa erottamaan aidot lähteet uskottavasti kuulostavista keksinnöistä.",
                "exact_quotes": [],
                "citations": []
              },
              {
                "block_type": "alert_box",
                "severity": "warning",
                "text": "**⚠️ VASTA-ARGUMENTTI:**\n\nVäite, että prosessi oli täysin turvallinen, voidaan kumota osoittamalla, että tekoäly tuotti todennäköisesti keksittyjä lähdeviitteitä. Ilman kriittistä käyttäjää virheellinen tieto olisi päätynyt lopputulokseen.",
                "exact_quotes": [],
                "citations": []
              },
              {
                "block_type": "alert_box",
                "severity": "success",
                "text": "**🛠️ KORJAAVAT TOIMENPITEET:**\n\n- Ota käyttöön pysyvä käytäntö, jossa kaikki tekoälyn tuottamat faktaväitteet ja lähteet tarkistetaan ulkoisesta, luotettavasta lähteestä.\n- Käytä \"paholaisen asianajaja\" -tyyppisiä kehotteita systemaattisesti monimutkaisissa tehtävissä paljastaaksesi piilevät oletukset ja heikkoudet.\n- Lisää kaikkiin lähdeviittauksiin automaattinen huomautus, joka kehottaa käyttäjää tarkistamaan tiedon oikeellisuuden ulkoisesta lähteestä.\n- Integroi proaktiivisesti \"mahdolliset riskit ja rajoitukset\" -osio kaikkiin suosituksiin, jotta itsekritiikki on sisäänrakennettu ominaisuus eikä vaadi erillistä kehotetta.",
                "exact_quotes": [],
                "citations": []
              }
            ]
          }
        ]
      }
    }
  ]
}
```
