# EPIC 123: Legacy Matrix Synthesis and Pure SDUI Parity

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
>
> Implementing Server-Driven UI (SDUI) effectively in 2025-2026 requires a mature architectural pattern centered on "Design-First Contracts." Industry best practices emphasize avoiding deep nesting and data-model dependency on the client. Instead, the backend must construct explicit UI component blocks (specifically: `AlertBlock`, `QuoteBlock`) rather than transmitting flat string properties (specifically: `coaching: "Do this"`). This "demand-driven" approach ensures the client acts strictly as a "Dumb Painter", rendering the payload blindly, which guarantees 100% deterministic pixel-parity across Flutter apps and generated PDFs while preventing "re-hydration churn".

---

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective
Restore the rich synthesis styling and XAI output extensions (specifically and exhaustively: "Arjen Vinkki", "Vasta-argumentti", Jargon Ratio) that existed prior to Epic 110/122, ensuring complete visual parity between the interactive Flutter UI and the generated PDF report.

### Problem Statement
During the implementation of Epic 111 (Dumb Painter SDUI) and Epic 122 (Legacy Parity Output Profile), the hardcoded HTML logic responsible for styling Matrix extensions in `report_template.jinja2` was removed to enforce the strict ICU Markdown Parity rule. Furthermore, backend mapping for these extensions was flattened. As a result, the premium colored boxes and AI-generated synthesis text vanished from the final outputs. 

The challenge is to bring these rich visual elements back WITHOUT violating the new SDUI architecture. We cannot revert to "duct tape" hardcoded HTML or Flutter-side string-parsing.

### Root Cause / Gap Analysis
- **AlertBlock.severity Type Gap (Juurisyy 3):** Currently, Python's `AlertBlock` supports `Literal["info", "warning", "critical_override"]`. When legacy matrix extensions are converted to SDUI blocks, we also strictly require `"success"` (mapped strictly to Remediation Steps) and `"error"`. The `AlertBlock.severity` field MUST remain a standalone `Literal` type (NOT coupled to the `VisualIntent` enum, which serves a different domain — atom-level rendering intent). The Literal MUST be expanded to `Literal["info", "warning", "critical_override", "success", "error"]`. On the Dart side, `SduiAlertBoxBlock.severity` is currently a raw `String` (confirmed at `@[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart#L32]`). This MUST be refactored to a new strict `@JsonEnum() enum AlertSeverity` in `enums.dart`, whose values precisely mirror the backend `Literal`.
- **VisualIntent Enum Deficit (Juurisyy 4):** The `VisualIntent` enum (`@[c:\src\quorum\backend_v2\models\enums.py#L116-L123]`) currently contains `SUCCESS`, `WARNING`, `CRITICAL_OVERRIDE`, `INFO`, `NEUTRAL`. The Dart equivalent (`@[c:\src\quorum\client_app_v2\lib\core\models\enums.dart#L249-L260]`) mirrors this exactly. This Epic adds `ERROR` to `VisualIntent` for use in atom-level rendering (specifically, short-circuit atoms). `DANGER` is NOT added (YAGNI — no concrete use case exists in this Epic's scope).
- **HighlightBoxDisplay Duct Tape Parsing (Juurisyy 5):** In Flutter (`@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\xai_extensions_box.dart#L204-L205]`), `color_theme` is parsed loosely via `val['color_theme']?.toString() ?? 'info'` without a Freezed model. This violates the "Zero Duct Tape" SDUI rule. This entire widget (466 lines) is a legacy monument to anti-patterns (`List<dynamic>`, raw dict duck-typing, hardcoded colors) and MUST be fully sunset in Phase 4 once `inner_sdui_blocks` replaces its function.
- **AssessmentView & ReportView Type Gaps (Juurisyy 6):** `AssessmentView.uiVariant` lacks a corresponding Enum in Python (`enums.py`) and Dart (`enums.dart`). It currently uses literals ("default", "success", "warning", "error", "neutral"). `ReportView.status_theme` is typed loosely as `StrictStr` in Python. These must be synchronized across the stack using unified Enums (`UiVariant` and `VisualIntent`).
- **Dart Freezed "Silent Failure" Risk (Juurisyy 7):** When extending SDUI components and severity enums, there is a risk of using `@Default("unknown")` or `fallbackUnion: 'unknown'` in Dart to prevent crashes. This violates Quorum's Anti-Hallucination and Fail-Fast rules. An unknown SDUI block or an incorrect severity value MUST crash the view (throw `CheckedFromJsonException`) so the Error Boundary catches it immediately in CI/CD, rather than hiding the error from end users.
- **Backend Duck-Typing Risk in SDUI Mapper (Juurisyy 8):** The source of this duck-typing is `TraceMatrixPayloadDTO.extensions`, which is currently a loose `dict[str, Any]`. When extracting legacy flat fields (`coaching`, `falsification`, `remediation_steps`, `missing_context`, `emotional_sentiment`, `theory_link`, `risk_flag`) from this dict to generate `AlertBlock` models, using defensive programming (specifically `.get("coaching")`) circumvents static typing. This dict MUST be converted to a strict Pydantic model (`TraceMatrixExtensionsDTO`) with `extra="forbid"`. To prevent Fail-Fast serialization crashes on incoming LLM payloads, this DTO MUST explicitly define ALL fields the LLM payload expects inside the `extensions` node: `coaching` (str), `falsification` (str), `remediation_steps` (str), `missing_context` (str), `emotional_sentiment` (str), `theory_link` (str), `risk_flag` (bool), AND the retained backend mapping fields: `confidence` (float), `evidence_type` (str), `source_id` (str), `citation` (str), `google_citation` (str), `contextual_override` (bool), and `semantic_reasoning` (str). This allows `blueprint.py` to use strict attribute referencing (`if matrix_payload.extensions.coaching:`). If the underlying schema changes or a field is removed, it instantly triggers a `ValidationError`, ensuring Fail-Fast. **CRITICAL**: This `ValidationError` is intentional. Implementers MUST NOT bypass extra keys with `extra='ignore'`. Instead, the extraction execution MUST be routed through the `LLMTaskExecutor`'s structured retry loop. This guarantees that when the LLM hallucinates extra keys, the `ValidationError` is caught and fed back to the LLM for autonomous self-correction, preserving system resilience. If the LLM consistently fails after max retries, the Prompts must be synchronized to match the strict DTO.
- **`grouped_extensions` COMPLETE Sunset (Juurisyy 9):** The existing `ReportDataDTO.grouped_extensions: dict[str, list[Any]]` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1227]`) is the CURRENT mechanism for passing XAI extensions to both Flutter and Jinja. `blueprint.py` has 30+ references to it. This field MUST be COMPLETELY DELETED in this Epic. ALL extension data — both row-level (`coaching`, `falsification`, etc.) AND global (`variance_validation`) — MUST be migrated to typed `inner_sdui_blocks` arrays. Furthermore, `list[Any]` violates the 2026 `Any`-inside-lists ban. No old-style rendering paths may remain.
- **`confidence` Numeric Field Mismatch (Juurisyy 10):** The `confidence: float | None` field on `MatrixScorecardRowDTO` is a NUMERIC value. It cannot be meaningfully represented as an `AlertBlock` (which expects `text: str`). This field must be excluded from the `inner_sdui_blocks` migration and either retained as a standalone numeric field or mapped to a different SDUI block type (specifically a future `MetricBlock`).
- **`GlobalSynthesisDTO` SDUI Violation (Juurisyy 11):** The `global_synthesis` field on `ReportDataDTO` currently passes raw string fields (`executive_summary`, `user_role`, `user_role_justification`) to the frontend. This forces Flutter to use hardcoded, client-side UI logic to render the report's main summary, violating the SDUI Dumb Painter architecture.
- **Epic 120 Leftovers (`list[Any]` Leaks) (Juurisyy 12):** Epic 120 Phase 3 mandated the eradication of `list[Any]` from all SDUI models. However, `SduiGridBlock.items` and `SduiQuoteCard.citations` were skipped and remain loosely typed. These must be explicitly typed to enforce full SDUI strictness. To adhere to the Polymorphic Serialization KI and avoid Dart's `List<dynamic>` vulnerabilities, `SduiGridBlock.items` MUST be strictly typed as `list[AnySduiBlock]` (Python) and `List<SduiBlockDTO>` (Dart) to allow nested rich blocks. `SduiQuoteCard.citations` MUST be typed as `list[int]`.

### Strategic Scope
This Epic achieves visual restoration through **pure dynamic SDUI**. The backend (`blueprint.py`) will transform flat string properties extracted by the AI into a structured `inner_sdui_blocks` array (specifically utilizing existing models: `AnySduiBlock`). Both the Flutter frontend and the PDF Jinja template will simply execute their standard generic SDUI rendering pipelines over these inner blocks.

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **Hardcoded Extension Rendering Logic**: Any remaining Flutter code attempting to parse `coaching` or `falsification` strings to render specific UI containers will be INTENTIONALLY DROPPED in favor of the `SduiRenderer`. The entire `xai_extensions_box.dart` widget (466 lines) MUST be sunset once `inner_sdui_blocks` replaces its function.
- **Emoji Injection**: Hardcoded emojis in `extension_labels` will be purged to ensure clean, professional strings.
- **Legacy Flat STRING Fields**: The old STRING presentation fields (`coaching`, `falsification`, `missing_context`, `risk_flag`, `remediation_steps`, `emotional_sentiment`, `theory_link`) MUST be ruthlessly deleted from BOTH the Python `MatrixScorecardRowDTO` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L970-L978]`) and the Flutter Freezed equivalent (`@[c:\src\quorum\client_app_v2\lib\features\execution\models\matrix_scorecard_dto.dart#L138-L146]`). **EXCEPTION**: The `confidence: float | None` field is NUMERIC, not textual, and MUST be RETAINED as a standalone field (it does not map to `AlertBlock`). This enforces the Single Source of Truth (SSOT) and prevents "Legacy Flat Field Eradication" violations.
- **`grouped_extensions` COMPLETE Sunset**: The `grouped_extensions: dict[str, list[Any]]` field on `ReportDataDTO` (`@[c:\src\quorum\backend_v2\models\v2_core.py#L1227]`) MUST be **RUTHLESSLY DELETED** in this Epic. ALL extension categories — both row-level (`coaching`, `falsification`, `remediation_steps`, etc.) AND global (`variance_validation`) — MUST be migrated exclusively to typed `inner_sdui_blocks` arrays on their respective DTOs. The `variance_validation` extension MUST be mapped to the existing `SduiGridBlock` and `SduiAlertBoxBlock` (for the verdict). `blueprint.py` MUST be refactored to stop populating `grouped_extensions` entirely. The Flutter `XAIExtensionsBox` widget and the Jinja `grouped_extensions` rendering panel MUST be fully deleted. **Zero old-style rendering paths may remain.**
- **`GlobalSynthesisDTO` COMPLETE Sunset**: The `global_synthesis` field and the `GlobalSynthesisDTO` model itself MUST be entirely **DELETED** from both Python and Dart. All high-level report synthesis data (`executive_summary`, `user_role`, `user_role_justification`) MUST be mapped directly into separate `SduiMarkdownBlock` instances by the backend and appended to the `ReportView.sections` array.

### Retained SSOT Invariants (What We Will RETAIN)
- **Universal Static vs Dynamic SDUI Routing**: It is categorically mandated that across ALL current and future matrices (and Epics), the process must operate identically. Static explanations, instructions, and titles MUST be fetched directly from the database templates (specifically, the `extension_labels` localized to the target language), while only the dynamic synthesized insights are passed via LLM generation. The Flutter client remains completely blind to this difference.
- **Strict Anti-Hallucination Deserialization (No Silent Failures)**: It is STRICTLY FORBIDDEN to use `@JsonKey(unknownEnumValue: ...)` or `@Freezed(fallbackUnion: ...)` in any Dart SDUI block or Enum model (specifically: `VisualIntent` or `SduiBlockDTO`). Unrecognized keys or invalid enums MUST intentionally throw a `CheckedFromJsonException` to trigger the Fail-Fast mechanism and Error Boundaries.
- **Strict Attribute Referencing (No Duck-Typing)**: When the backend translates domain objects to SDUI models, it MUST use direct static attribute referencing (for example: `if row.coaching:`). The use of `.get()`, `hasattr()`, or `getattr(..., default)` on strictly typed Pydantic models is strictly forbidden. This ensures that any schema refactoring instantly triggers an `AttributeError` or MyPy failure, enforcing the Fail-Fast mandate.
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
| Backend `blueprint.py` | `MatrixScorecardRowDTO.inner_sdui_blocks` | Transforms AI strings into `list[AnySduiBlock]` (specifically mapped to `AlertBlock` instances) |
| Backend `MatrixScorecardRowDTO` | Flutter `matrix_row_item_widget.dart` | Pipes `innerSduiBlocks` array to `SduiRenderer` |
| Backend `MatrixScorecardRowDTO` | Jinja `report_template.jinja2` | Passes `inner_sdui_blocks` to `render_sdui_blocks()` macro |

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Database Seed Restoration
- **Target**: `@[c:\src\quorum\backend_v2\seed\seed_data.json#L7800-L11000]`
- Locate the first `text_only` layout named `"YHTEENVETO"` in the `holistic_audit` profile (lines 9470-9550).
- Restore its `synthesis.system_prompt` and `synthesis.preamble_text` by pulling the exact original strings from commit **`22b16208`** (`git show 22b16208:backend_v2/seed/seed_data.json`) to prevent hallucinating the prompt. This commit contains the exact required static text ("Tämä raportti analysoi tapaasi hyödyntää tekoälyä...").
- For matrix layouts (`2d_compare`, `3d_matrix`) with synthesis, explicitly set `"row_explanations_block_id": "sp_row_explanations"`.
- **MATRIX COLUMNS FIX (from Epic 122 Audit)**: Ensure the `3d_matrix` layout block explicitly contains the array `"matrix_visible_columns": ["label", "distribution", "row_explanation", "normalized_score", "score"]`.
- Locate all 12 instances of the `extension_labels` block (used across various matrices between lines 7900 and 11000).
- Remove all Unicode emojis and the immediately following space character from the `extension_labels` structures (programmatically remove all unicode emojis and the immediately following space character). Update all 12 locations systematically.
- **ATOMIC TEST SYNC**: Use `grep_search` to check if `@[c:\src\quorum\backend_v2\tests\test_data\report_data_dto_fixture.json]` or `@[c:\src\quorum\backend_v2\tests\test_data\exe_c0bc_inputs.json]` assert on emoji-prefixed `extension_labels` strings. Update them atomically to match the stripped labels.

> [!CAUTION]
> **Architectural Justification for Phase Order (Fail-Fast Mandate):**
> Quorum operates with strict Zero-Tolerance typing. Updating the Producer before the Consumer causes WSOD crashes. We must atomically synchronize the DTO Contracts in both Python and Dart. However, to prevent **Context Amnesia** and AI output token saturation, this schema migration is split into two distinct AI execution phases (Phase 2 and Phase 3).

### Phase 2: Python Backend Schema & Enum Migration
- **Target Python**: `@[c:\src\quorum\backend_v2\models\v2_core.py]`, `@[c:\src\quorum\backend_v2\models\view\sdui.py]`, `@[c:\src\quorum\backend_v2\models\enums.py]`, `@[c:\src\quorum\backend_v2\models\dtos\trace.py]`
- **DTO Sync (Matrix)**: Update `MatrixScorecardRowDTO` to include `inner_sdui_blocks: list[AnySduiBlock] = Field(default_factory=list)` and delete legacy STRING XAI fields (`coaching`, `falsification`, `missing_context`, `risk_flag`, `remediation_steps`, `emotional_sentiment`, `theory_link`). **RETAIN** `confidence: float | None` as-is.
- **DTO Sync (Trace)**: Update `TraceMatrixPayloadDTO`. Convert `extensions: dict[str, Any] | None` into a strictly typed `extensions: Annotated[TraceMatrixExtensionsDTO | None, Field(...)] = None`. Create `TraceMatrixExtensionsDTO(BaseDTO)` with `model_config = ConfigDict(strict=True, frozen=True, extra="forbid")` containing EXACTLY the following optional fields (using strict `PEP 593 Annotated` syntax) to prevent payload deserialization crashes: `coaching`, `falsification`, `remediation_steps`, `missing_context`, `emotional_sentiment`, `theory_link`, `risk_flag` (bool), `confidence` (float), `evidence_type`, `source_id`, `citation`, `google_citation`, `contextual_override` (bool), and `semantic_reasoning`.
- **DTO Sync (GlobalSynthesis)**: Delete `GlobalSynthesisDTO` entirely. Delete the `global_synthesis` field from `ReportDataDTO`.
- **Enum & Literal Sync**: Add `ERROR = "error"` to `VisualIntent`. Expand `AlertBlock.severity` Literal to `Literal["info", "warning", "critical_override", "success", "error"]`. Refactor `ReportView.status_theme` from `StrictStr` to `VisualIntent`. Create a new `UiVariant(StrEnum)` enum with values (`default`, `success`, `warning`, `error`, `neutral`), refactor `AssessmentView.uiVariant` to use it, and create a `LaxUiVariant = Annotated[UiVariant, Field(strict=False)]` alias to adhere to the hydration patterns in `enums.py`.
- **Cross-Language Parity Gate**: The existing `test_enum_parity.py` MUST pass after these enum changes. Add a new `test_parity_ui_variant()` check to assert exact parity between Python `UiVariant` and Dart `UiVariant`.
- **EPIC 120 Leak Cleanup**: Fix the remaining `list[Any]` type leaks in `sdui.py`. Update `SduiGridBlock.items` to strictly `list[AnySduiBlock]` (as grid items can contain complex blocks, per the Polymorphic Serialization KI) and `SduiQuoteCard.citations` to `list[int]`.
- **Test Sync (Python)**: Update Python mock test fixtures (`backend_v2/tests/test_data/report_data_dto_fixture.json`, `backend_v2/tests/test_data/exe_c0bc_inputs.json`) to remove legacy flat fields and match the new `inner_sdui_blocks` schema. This MUST be done before running the audit loop, otherwise `extra='forbid'` will crash pytest.
- **CHECKPOINT**: Perform an atomic `git commit` before proceeding to Flutter.

### Phase 3: Flutter Frontend Schema, Enum & Mock Migration
- **Target Flutter**: `@[c:\src\quorum\client_app_v2\lib\core\models\enums.dart]`, `@[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart]`, `@[c:\src\quorum\client_app_v2\lib\features\execution\models\matrix_scorecard_dto.dart]`, `@[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart]`
- **DTO Sync (SDUI Contract Fracture Prevention)**: Atomically mirror all Python changes from Phase 2 to Dart Freezed models. In `matrix_scorecard_dto.dart`, add `innerSduiBlocks: List<SduiBlockDTO>` and remove legacy strings, add `TraceMatrixExtensionsDTO` equivalent if used in Dart. Delete `GlobalSynthesisDto` and its reference in `report_data_v2_dto.dart`.
- **Enum Sync**: Add `error` to Dart `VisualIntent`. Create a NEW `@JsonEnum() enum AlertSeverity` with explicit `@JsonValue` mappings (`info`, `warning`, `criticalOverride` ('critical_override'), `success`, `error`) and sync `SduiAlertBoxBlock.severity` to it. Create a NEW `@JsonEnum() enum UiVariant` with explicit `@JsonValue` mappings: `defaultVariant` ('default' - avoid reserved keyword), `success`, `warning`, `error`, `neutral`. Refactor `ReportView.statusTheme` to `VisualIntent`.
- **SDUI Block Refactoring**: Update `SduiAlertBoxBlock.severity` to use the new `AlertSeverity` enum. Update `SduiGridBlock.items` to strictly `List<SduiBlockDTO>` (as grid items can contain complex blocks, per the Polymorphic Serialization KI). Update `SduiQuoteCard.citations` to `List<int>`. Ensure `List<dynamic>` is eradicated in these SDUI blocks.
- **Legacy Comment Cleanup**: Remove `// Epic 6:` and `// Epic 88` comments from `matrix_scorecard_dto.dart`.
- **Test Sync (Dart)**: Update Dart mock test fixtures (specifically `@[c:\src\quorum\client_app_v2\test\features\execution\models\matrix_scorecard_dto_test.dart]`, `@[c:\src\quorum\client_app_v2\test\features\execution\models\report_data_v2_dto_test.dart]`, and golden fixture files) to remove all deleted fields from mock JSON structures, use valid enum strings, and ensure all `innerSduiBlocks` are valid objects with a `block_type` discriminator.
- **CHECKPOINT**: Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models client_app_v2/lib/core/models client_app_v2/lib/shared/models client_app_v2/test/features/execution/models --build` and `git commit`.

### Phase 4: Producer Logic (Backend SDUI Hydration - Part 1: Global & Variance)
- **Target**: `@[c:\src\quorum\backend_v2\services\blueprint.py]`
- **Global Synthesis Hydration**: `GlobalSynthesisDTO` and `global_synthesis` references were demolished in Phase 2. To replace them, explicitly extract `executive_summary`, `user_role`, and `user_role_justification` from the `profile_cache` (`RenderedSynthesisCache`) inside `BlueprintTransformer.build_report_dto`. Convert these fields into strictly typed `ParagraphBlock` instances (from `backend_v2.models.view.sdui`) and append them into the `content_blocks` array (around line 950), which seamlessly injects them into the primary `ReportLayoutDTO`'s `synthesis_blocks` array. Use strict Pydantic V2 instantiation.
- **`variance_validation` Migration**: Map the variance verification results into typed SDUI blocks specifically into the `inner_sdui_blocks` array of the corresponding `MatrixScorecardRowDTO`. Specifically and exhaustively: use an `SduiGridBlock` (strict 2-column grid for "Mekaaninen" and "Kognitiivinen" metrics) and an `AlertBlock` (for the verdict). Ensure the grid items are mapped into strictly typed SDUI blocks (specifically `ParagraphBlock` instances) to satisfy the strict `list[AnySduiBlock]` typing. **CRITICAL INVARIANT (frozen_state_mutability)**: Because `MatrixScorecardRowDTO` inherits from `V2CoreBase` (frozen state), you MUST NOT mutate `.inner_sdui_blocks` in place. You MUST use `.model_copy(update={'inner_sdui_blocks': [...]})` or instantiate it cleanly. Do NOT create a domain-specific `SduiVarianceBlock`.
- **Telemetry Hydration**: Update `_hydrate_printable_sources_block` and `_hydrate_jargon_ratio_block` methods. Ensure they explicitly instantiate and return strictly typed `ParagraphBlock` objects within their `list[AnySduiBlock]` returns. This perfectly aligns with the Flutter frontend `SduiBlockDTO.paragraph` serialization.
- **TEST FIXTURE SYNC**: Locate `@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]`. Update tests to reflect the new SDUI block outputs. Explicitly add negative test scenarios (at least 2) for missing data in the synthesis and variance blocks.
- **CHECKPOINT**: Ensure `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test` passes and `git commit`.

### Phase 5: Producer Logic (Backend SDUI Hydration - Part 2: Row Extensions & Cleanup)
- **Target**: `@[c:\src\quorum\backend_v2\services\blueprint.py]`, `@[c:\src\quorum\backend_v2\models\v2_core.py]`, `@[c:\src\quorum\backend_v2\services\sdui_mapper_service.py]`, `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`
- **AlertBlock Transformation**: During matrix extraction in `blueprint.py` (around line 687), transform the textual fields from the trace payload (`ext_dict`) into `AlertBlock` models. Use **Strict Attribute Referencing** and programmatic mapping from string keys to `XaiExtensionType` enums to extract the `I18nText` from `extension_labels`. Format the `AlertBlock` text string exactly as `text = f"**{label_str}**: {ext_val}"`.
- **Exhaustive Severity Mapping**: Map extensions to `AlertBlock.severity` exhaustively: `falsification`, `missing_context`, `variance_validation`, `authenticity_evaluation` -> `warning`; `risk_flag` -> `error`; `remediation_steps` -> `success`; all others (e.g. `coaching`, `justification`, `theory_link`, `citation`, `emotional_sentiment`) -> `info`.
- **CRITICAL ARCHITECTURE INVARIANT**: Do NOT hardcode Finnish strings or emojis (specifically `"**💡 Arjen Vinkki:**"`) in Python. You MUST dynamically read the localized label from the matrix's `extension_labels` mapping. Emojis are purposefully stripped because the `AlertBlock` `severity` parameter (specifically, `info`) will command the Flutter frontend to render the appropriate native icon automatically.
- **Migration Boundary**: ALL `grouped_extensions` population logic in `blueprint.py` (30+ references) MUST be removed entirely.
- **`ReportDataDTO.grouped_extensions` Field Deletion**: After blueprint logic is refactored, the `grouped_extensions` field MUST be physically deleted from `ReportDataDTO` (and its Flutter equivalent). You MUST also strictly delete the legacy `xai_extensions` section generation in `sdui_mapper_service.py` (lines 131-142) and the `grouped_extensions` Jinja loops from `report_template.jinja2` (lines 410-430), enforcing the Tripartite Boundary.
- **CHECKPOINT**: Execute `backend_audit_loop.py` and `git commit`.

### Phase 6: Consumer Logic (Frontend & PDF Rendering)
- **Target Flutter**: `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\matrix_row_item_widget.dart]`
- **Target Jinja**: `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`
- In Flutter, explicitly import and render `SduiNodeRenderer(blocks: matrix.innerSduiBlocks)` immediately below `_buildLevelRow(context)` in `matrix_row_item_widget.dart`, adding defensive checks for null/empty arrays to prevent layout overflow.
- Ensure `SduiAlertBoxWidget` correctly parses and paints all required severities (`info`, `error`, `success`, `warning`, `critical_override`) utilizing dynamic colors from the theme.
- In Jinja, invoke `{{ render_sdui_blocks(axis.inner_sdui_blocks) }}` inside the matrix layout loop.
- **XAI Extensions Box DELETION & Report Renderer Update**: Delete `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\xai_extensions_box.dart]` entirely. Remove all import references and usages of `payload.groupedExtensions` from `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart]`. To maintain 1:1 parity with the Jinja matrix layout loop, `report_renderer_v2_widget.dart` MUST also explicitly render `SduiNodeRenderer(blocks: axis.innerSduiBlocks)` immediately beneath the `XAIAxisTelemetryGrid` call. The `XAIExtensionsBox` widget is fully superseded by `SduiNodeRenderer`. ALL code paths referencing `grouped_extensions` in Flutter MUST be removed, including deleting mocked injections from test files (e.g., `test_xai_audit_trail.dart`) to prevent compilation failures.
- **XAI Axis Telemetry Grid Cleanup**: In `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\xai_axis_telemetry_grid.dart]`, the `groupedExtensions` constructor parameter MUST be removed. The hardcoded UI rendering logic for `riskFlag`, `emotionalSentiment`, and `theoryLink` MUST be completely deleted (as these fields are deleted in Phase 2). The rendering of `confidence` MUST be updated to trigger simply on `axis.confidence != null` (removing the `groupedExtensions` dependency).
- **Jinja Confidence Rendering Fix**: In `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`, the rendering of `confidence` inside the matrix axis loop is currently gated by `grouped_extensions`. This MUST be refactored to simply check `{% if axis.confidence is not none %}`, mirroring the Flutter logic. The `axis.confidence` MUST be rendered in its own visual block BEFORE the `render_sdui_blocks(axis.inner_sdui_blocks) ` macro call.
- **Global Synthesis UI Refactoring (Flutter)**: Remove all hardcoded UI logic in Flutter that previously parsed the `globalSynthesis` object to render the header. The report header will now render automatically via the standard SDUI `sections` pipeline.
- **Jinja `global_synthesis` HTML DELETION**: Delete the hardcoded HTML block for `report_data.global_synthesis.executive_summary` (and `user_role`) in `report_template.jinja2`. Ensure the top of the PDF dynamically loops through `report_data.sections` instead, completely decoupling the PDF template from specific synthesis fields.
- **Jinja `grouped_extensions` Panel DELETION**: The entire global extensions panel in the Jinja template (the `{% if report_data.grouped_extensions %}` block) that renders `grouped_extensions` MUST be **DELETED**. All extension rendering (including `variance_validation`) is now handled exclusively by `render_sdui_blocks(axis.inner_sdui_blocks)` in the matrix loop. Zero old-style rendering paths may remain.

### Phase 7: Verification & E2E Integration Gate
- **NOTE**: Test fixture migration already completed atomically in Phase 3. This phase is VERIFICATION ONLY.
- Execute `backend_audit_loop.py` to ensure schema integrity and routing.
- Execute `flutter_audit_loop.py --build` to synchronize Freezed DTOs and verify widget compilation.
- **COMPLETE `grouped_extensions` Eradication Verification**: Confirm that the `grouped_extensions` field has been DELETED from `ReportDataDTO` (Python) and its Flutter equivalent. Verify with `grep_search` that ZERO references to `grouped_extensions` remain in `blueprint.py`, `sdui_mapper_service.py`, `report_template.jinja2`, and all Flutter widget files. Any remaining reference is a BLOCKING failure.
- **BREAKING CHANGE - Database Wipe & Seed**: Since the removal of `grouped_extensions` and `global_synthesis` is a breaking schema change (due to strict `extra='forbid'` parsing), all historical executions in the local database will crash on load. You MUST wipe the local database and re-seed before performing E2E tests:
  ```powershell
  uv run python backend_v2/seed/run_seed.py local
  ```
- Generate a holistic audit report via the UI or API to verify visual parity between Flutter and PDF.

### Phase 8: Multilingual & Localization (i18n) Verification
To guarantee complete multilingual support across all textual generation sources, the implementation MUST adhere to the following routing:
- **Database Source (`extension_labels`)**: Because `AlertBlock.text` expects a `str`, `blueprint.py` MUST resolve the `I18nText` object from `extension_labels` using the current Execution's `target_language` before injecting it into the SDUI block (for illustrative purposes only: `label_obj = ext_labels.get(XaiExtensionType(type)); label_str = label_obj.resolve(execution.target_language)`). The backend MUST ALWAYS provide the fully resolved string — the frontend NEVER performs translation lookups on SDUI block content.
- **Prompt Directory Features (`models/prompts`)**: If any textual prefixes (specifically: "Jargon Ratio:") are injected via static prompt configurations, the backend MUST utilize the localized properties matching the `target_language` rather than hardcoding.

> [!CAUTION]
> **SDUI Dumb Painter Mandate (Absolute Rule):** The frontend MUST NOT contain any translation resolution logic for SDUI block content. All `AlertBlock.text` values MUST arrive from the backend as fully resolved, render-ready strings in the correct `target_language`. Transmitting ARB translation keys inside `AlertBlock.text` for client-side resolution is **STRICTLY FORBIDDEN** — it violates the Dumb Painter architecture and creates frontend-side business logic.

- **LLM Prompt Generation (`linguistic_directives.py`)**: If the AI prompt itself is directed to generate the explanations or text (specifically for matrix synthesis), it MUST NOT use hardcoded natural language instructions (for illustrative purposes only: "Please write in Finnish"). Instead, the prompt MUST strictly utilize the `<linguistic_context>` XML pattern defined in `backend_v2/models/prompts/linguistic_directives.py`, ensuring the LLM dynamically respects the `target_locale` across all generated string fields.
- **Dynamic Enums and Roles (specifically: "Käyttäjän Rooli")**: Any dynamic labels referring to system states, user classifications, or assigned roles (specifically the "Arkkitehti" role in the output summary) MUST be mapped and retrieved dynamically through the system's official Enum definitions and their corresponding translation functions. Hardcoding such classification strings in templates, LLM prompts, or synthesis outputs is strictly forbidden.
- **Strict Extension Generation (`EXTENSION_ANCHORING_MANDATE`)**: The generation of these extensions (specifically: remediation_steps) is governed strictly by the `EXTENSION_ANCHORING_MANDATE` in `global_mandates.py`. The LLM MUST anchor every extension to the raw input data, ensuring the content is a directly actionable consequence of the data rather than generic theoretical advice.

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

This section defines the exact target payload expected after implementation. **This identical JSON structure MUST be utilized as the baseline mock fixture in both Backend and Frontend automated tests** (specifically `test_blueprint.py` and `matrix_scorecard_dto_test.dart`) to guarantee the polymorphic `inner_sdui_blocks` deserializer handles the SDUI mapping correctly. Note: the `confidence` field is retained as a standalone numeric value (not in `inner_sdui_blocks`). The example below represents the complete top-level `ReportView` payload to illustrate how the matrix sits within the broader ecosystem of summaries, graphs, and citations.

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
