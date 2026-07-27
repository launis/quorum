# EPIC 111: Eradicate Legacy SDUI Fields & Output Profile Refactoring

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> Modern software engineering research (e.g., *Undirwadkar, 2025: "The rise of server-driven UI"*) highlights that SDUI has evolved from a niche workaround to a foundational "server-first" distributed architecture. Industry standards in 2026 emphasize **Type-Driven Development** (schema-first validation) to prevent the severe risks of distributed UI failures. Attempting to maintain dual data pathways (legacy dictionaries alongside strict SDUI schemas) creates catastrophic operational overhead and undermines the core reliability of the "Dumb Painter" paradigm. Therefore, enforcing absolute strictness and eradicating legacy fallbacks is a mathematically mandated architectural requirement.

## 1. Goal Description & Background (Objective & Problem Statement)
The Quorum system has been migrating towards a 100% "Dumb Painter" Server-Driven UI (SDUI) architecture (Epic 110). However, critical technical debt remains in the `ReportDataDTO` pipeline. Legacy arrays (such as `content_blocks`, `evaluative_matrices`, and `penalties_applied`) were left as separate top-level variables alongside the new dynamic `layouts` generator to maintain backward compatibility. This violates the "Zero Alternative Output Paths" mandate established in Epics 106, 109, and 110. 

Additionally, the Flutter `OutputProfileCrudView` UI is currently a monolithic, deeply nested split-pane structure that is difficult to scale, and internal testing frameworks have relied on Pydantic `model_construct` validation bypasses, causing "Frankenstein" object/dictionary hybrids that break Jinja rendering rules. Finally, LLM "Semantic Drift" has caused unwanted renaming of DTO fields (e.g., `cognitive_status` to `status`), breaking cross-domain serialization.

**Objective:**
1. **Absolute SDUI Parity**: Completely delete all legacy top-level report arrays from `ReportDataDTO`. All data MUST route exclusively through the `layouts` array.
2. **Pydantic Strictness**: Remove `model_construct` bypasses in Polyfactory tests, enforcing mathematically coherent, 100% strictly validated mock objects.
3. **Semantic Anti-Drift**: Enforce strict 1:1 identical naming conventions between Python and Flutter without arbitrary AI-driven renames.

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)
- **Legacy SDUI Rendering Fields**: `ReportDataDTO.content_blocks`, `ReportDataDTO.evaluative_matrices`, and `ReportDataDTO.informational_matrices` will be permanently DELETED from the DTO.
- **Penalties Migration (NOT Deletion)**: The `ReportDataDTO.penalties_applied` field will be DELETED from the model, but the `penalties_applied` local string list in `blueprint.py` MUST be retained for internal mathematical score deductions (e.g., calculating `effective_penalty`). **CRITICAL (Tier 0 Red-Team):** Only *after* the `global_score` calculation is complete should you map these penalties into a `ReportLayoutDTO` with `preset_view="text_only"`. Inject the penalty text natively into `synthesis_blocks` using standard SDUI markdown blocks (e.g., `alert_box` or `warning_card`), and ensure the UI title uses strict Pydantic syntax (`I18nText(default_locale="en", translations={"en": "Penalties Applied", "fi": "..."})`). The slop detection logic in @[c:\src\quorum\backend_v2\worker.py#L444-L458] must be refactored to read directly from the backend's internal domain states or synthesis DTOs — NOT by scanning frontend SDUI layouts for a generic `metadata` dictionary, which violates strict typing.
- **worker.py hasattr() Purge**: All `hasattr()` and `isinstance(x, dict)` checks inside @[c:\src\quorum\backend_v2\worker.py#L846-L874] MUST be deleted. The code must rely entirely on Pydantic's static typing and `.model_dump()` to extract `content_blocks` from known DTOs (e.g., `SynthesisOutputDTO`), strictly enforcing the "Zero-Compromise Pledge".
- **`or []` Coalescing Fallback Chain Purge**: All `or []` coalescing fallback patterns that mask `None` on legacy fields MUST be deleted as part of the Zero-Compromise Pledge. Specific targets: @[c:\src\quorum\backend_v2\services\flattener.py#L38] (`evaluative_matrices or []`), @[c:\src\quorum\backend_v2\hooks\linguistics.py#L176] (`evaluative_matrices or []`), and @[c:\src\quorum\backend_v2\worker.py#L445] (`penalties_applied or []`). After field deletion, these consumers must be refactored to read from `layouts` directly.
- **Flutter Rendering Fallbacks**: All conditional UI logic in @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart], @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\diagnostic_scorecard_widget.dart], @[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_report_view.dart], and @[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_view.dart] that parses legacy fields will be PURGED. Furthermore, the UI must be stripped of all conditional `scaleMax > scaleMin` formatting for scores and must strictly render a new `scoreDisplayLabel` pre-computed by the backend.
- **Jinja PDF Template**: ❌ **NOT YET MIGRATED** (Tier 0 Red-Team correction) — @[c:\src\quorum\backend_v2\templates\report_template.jinja2] still actively references `evaluative_matrices` at L584/L687 and `penalties_applied` at L730-L734. The template has DUAL rendering paths (layouts AND legacy) and MUST be fully migrated in Phase 1C to avoid `UndefinedError` crashes after field deletion.
- **Test Hacks**: `factory_use_construct=True` will be DELETED from all Polyfactory fixtures.

### Modernization & Restoration of Lost Functionality (`What We Will RESTORE via SDUI`)
- **Formatting Directives (XML Payload)**: The deleted `formatting_directives` list will NOT be restored to the Pydantic models. Instead, any LLM formatting instructions (e.g. "use short paragraphs") MUST be embedded natively as structured XML inside the `layouts[0].synthesis.tone_instruction` string in `seed_data.json` (e.g., `<formatting_rules><rule>...</rule></formatting_rules>`). The `worker.py` prompt compiler will dynamically inject this XML tree into the system prompt, keeping the DTO clean while restoring LLM control.
- **Row Forensics & Quotes**: The deleted `row_forensics` hierarchy will NOT be restored. Instead, `blueprint.py` MUST be updated to iterate over `evaluated_atoms` and map any `exact_quotes` or `semantic_reasoning` into standard SDUI `content_blocks` (Markdown format) beneath the matrix layout, allowing Flutter to render evidence seamlessly without needing complex nested data parsing.
- **Penalties UI Rendering**: Because Flutter UI now purely iterates over `layouts`, the mathematical penalty deduction MUST be accompanied by a dynamically generated `ReportLayoutDTO` (with `preset_view="text_only"` and `synthesis_blocks`) appended to the end of the report by `blueprint.py`. This ensures the user sees the SLOP/Security penalty explanation natively in the UI.
- **XAI Audit Trail (Tavily Quotes)** *(Post-Refactor Follow-Up — NOT in Epic 111 structural scope)*: The `XAIEvidenceBox` widget in Flutter was orphaned during the V2 migration. The `mcp_tool_audit` array still exists in `ReportDataDTO`, but it is no longer rendered. This is a **feature restoration**, not a structural refactor, and MUST be tracked separately (e.g., Epic 112 or a standalone ticket) to avoid violating the Zero-Behavioral Change Falsification Gate.

> [!WARNING]
> **SCOPE BOUNDARY**: The `content_blocks` field on `SynthesisSectionDTO` and `SynthesisOutputDTO` (synthesis-domain DTOs) is architecturally DISTINCT from `ReportDataDTO.content_blocks` and MUST NOT be deleted. Similarly, the `_evaluative_matrices` internal state key in @[c:\src\quorum\backend_v2\hooks\scoring.py] is an internal DAG execution state alias, NOT a rendering field, and MUST be preserved. The `hasattr(cache_b, "copy")` call at @[c:\src\quorum\backend_v2\services\blueprint.py#L1161] operates on `OutputProfile.content_blocks` (SB4), NOT `ReportDataDTO.content_blocks`, and MUST survive the `hasattr()` purge.

### Retained SSOT Invariants (`What We Will RETAIN`)
- **Dumb Painter Layouts**: The `layouts` array (`List<ReportLayoutDto>`) remains the absolute Single Source of Truth for all report rendering.
- **Riverpod State Management**: `outputProfileFormProvider` remains the SSOT for the transient Output Profile form state.

### Compliance & Modernity Gates
1. **The "Zero Alternative Paths" Rule**: If data is to be rendered on the report, it MUST be wrapped in a `ReportLayoutDto` inside the `layouts` array.
2. **Pydantic Strictness / Validation Bypasses**: Bypassing validation via `model_construct` that results in nested dictionaries is explicitly BANNED when passing data to Jinja or Flutter.
3. **Anti-Semantic Drift**: DTO field names are PERMANENT architectural contracts. Python `snake_case` must perfectly match Flutter `camelCase` (e.g., `evaluation_reasoning` -> `evaluationReasoning`). Renaming for subjective "clarity" is strictly forbidden.
4. **Cross-Domain Parity**: All Pydantic schema changes MUST instantly trigger `flutter_audit_loop.py --build` to verify Freezed serialization.
5. **Strict Localization Generation (Tier 0 Red-Team)**: Backend instantiations of localized text for SDUI MUST use the strict Pydantic schema (e.g., `I18nText(default_locale="en", translations={"en": "...", "fi": "..."})`). Legacy keyword instantiations (`I18nText(en="...")`) trigger immediate Fail-Fast `ValidationError`.

### Producer-Consumer Integration Check
- **Producer**: @[c:\src\quorum\backend_v2\services\blueprint.py] must be upgraded to inject legacy concepts (like penalties, matrices, synthesis content) into dedicated `ReportLayoutDto` blocks.
- **Consumer (Flutter)**: @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart] blindly iterates over `layouts`. The legacy `DiagnosticScorecardWidget` must be refactored to consume matrix data directly from the `axes` property of standard layouts instead of top-level metadata, adhering to the Dumb Painter pattern.
- **Consumer (Jinja)**: @[c:\src\quorum\backend_v2\templates\report_template.jinja2] must be migrated to iterate over `layouts`. **Tier 0 Red-Team verified**: Template still uses `evaluative_matrices` at @[c:\src\quorum\backend_v2\templates\report_template.jinja2#L584] and @[c:\src\quorum\backend_v2\templates\report_template.jinja2#L687], and `penalties_applied` at @[c:\src\quorum\backend_v2\templates\report_template.jinja2#L730-L734].
- **Consumer (Backend)**: @[c:\src\quorum\backend_v2\services\execution.py], @[c:\src\quorum\backend_v2\services\flattener.py], @[c:\src\quorum\backend_v2\hooks\linguistics.py], and @[c:\src\quorum\backend_v2\services\sdui_mapper_service.py] must be refactored to read from `layouts`. **Tier 0 Red-Team addition**: @[c:\src\quorum\backend_v2\services\execution.py#L763-L766] consumes `evaluative_matrices`/`informational_matrices` for Excel export summary rows, and @[c:\src\quorum\backend_v2\services\execution.py#L1272-L1275] consumes `content_blocks` with `.get()` coalescing patterns that violate Fail-Fast (these must be rewritten to use explicit `is not None` and dictionary `in` operator checks).

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 0: Seed Data & Database Prerequisite / Migration
- Ensure the database is cleanly re-seeded without legacy definitions causing test failures.
- Run: `uv run python backend_v2/seed/run_seed.py local`
- **Baseline Recording**: Record both Backend and Frontend test baselines *after* the database reset to establish a pristine starting state before legacy purges begin.

### Phase 1: Backend DTO Strictness & Eradicating Legacy Fields
- Modify @[c:\src\quorum\backend_v2\models\v2_core.py#L1160-L1260]: Delete `content_blocks`, `evaluative_matrices`, `informational_matrices`, and `penalties_applied` from `ReportDataDTO`. (Penalties will now be dynamically assembled into standard `ReportLayoutDTO` blocks by the blueprint service, avoiding polymorphic schema bloat).
- **[NEW] Pure Dumb Painter Score Formatting**: Modify @[c:\src\quorum\backend_v2\models\v2_core.py#L941-L1000] to add `score_display_label: str | None = None` to `MatrixScorecardRowDTO`. Refactor @[c:\src\quorum\backend_v2\services\blueprint.py] to compute the score fraction string (e.g. "5.0 / 10.0" or "5.0" or "-") internally so the UI doesn't evaluate `scale_max > scale_min` business logic.
- **[BLOCKING SUBTASK]** Modify @[c:\src\quorum\backend_v2\models\v2_core.py#L1050-L1080] and Flutter schemas: Abandon the idea of adding a generic `metadata` dictionary to `ReportLayoutDTO`. Adding generic dictionaries violates the Dumb Painter strict type paradigm. Penalties must be structurally represented purely as SDUI components (`alert_box`) within `synthesis_blocks`. *(SYNC NOTE: The execution plan 04_flutter_dto_parity_and_frontend_purge.md was discovered to be out of sync and still contained this banned step; it has now been manually purged to restore 100% architectural parity).*
- **[BLOCKING SUBTASK]** Modify @[c:\src\quorum\backend_v2\services\blueprint.py#L760-L1380]: Refactor the SDUI generator (starting at `build_report_dto`) to route 100% of the dynamic report data exclusively through the `layouts` array, including matrices and penalties. **CRITICAL**: The code block at @[c:\src\quorum\backend_v2\services\blueprint.py#L876-L1250] that processes `profile.content_blocks` currently assigns the result to `ReportDataDTO.content_blocks`. After deleting that field, this assignment MUST be refactored to inject content blocks as `synthesis_blocks` inside a `ReportLayoutDTO` in the `layouts` array.
- ❌ @[c:\src\quorum\backend_v2\templates\report_template.jinja2]: **NOT YET MIGRATED** (Tier 0 Red-Team correction). Must be refactored to read matrices from `layouts[*].axes` and penalties from penalty-type layouts instead of legacy top-level fields. Specific targets: L584 `all_matrices` construction, L687 `evaluative_matrices` conditional, L730-L734 `penalties_applied` loop.
- Modify @[c:\src\quorum\backend_v2\services\execution.py#L1-L1141]: Remove direct references to legacy matrix and content_blocks fields.
- Modify @[c:\src\quorum\backend_v2\services\flattener.py]: Refactor matrix flattening to use `layouts`.
- Modify @[c:\src\quorum\backend_v2\hooks\linguistics.py]: Refactor linguistic matrix analysis (slop detection) to extract texts from `report_dto.layouts` (synthesis_blocks and axes) instead of legacy evaluative and informational matrices.
- Modify @[c:\src\quorum\backend_v2\services\sdui_mapper_service.py]: Remove direct `content_blocks` mapping (already covered by layouts).
- Modify @[c:\src\quorum\backend_v2\worker.py]: Refactor slop penalty detection at L444-L458 to safely read from internal domain/synthesis outputs instead of relying on the deleted `dto.penalties_applied` field. Ensure zero usage of `.get()` or `or []` fallbacks. CRITICALLY: Purge all `hasattr()` and naked dictionary checks at L846-L874 to enforce pure Pydantic hydration (using `.model_dump()` on `SynthesisOutputDTO`).
- Modify @[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart]: Mirror the deletions in the Flutter Freezed model by permanently removing `contentBlocks`, `evaluativeMatrices`, `informationalMatrices`, **and `penaltiesApplied`**, then run the code generator. (**Note**: `penaltiesApplied` was originally omitted from the Flutter deletion scope — this has been corrected per Tier 0 Red-Team finding M4.)
- Modify @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\diagnostic_scorecard_widget.dart]: Refactor to accept `axes` from the layout instead of top-level legacy matrices, and pass it to `AtomMatrixTableWidget`.
- Modify @[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_report_view.dart]: Refactor the `DiagnosticScorecardWidget` instantiation to pass `axes: value.layouts.expand((l) => l.axes).toList()` instead of legacy passthrough variables.
- Modify @[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_view.dart]: Refactor the `DiagnosticScorecardWidget` instantiation to pass `axes` dynamically from the layouts.
- Modify @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart]: Purge all fallback rendering logic (specifically the hardcoded `1. Content Blocks` section iterating over `payload.contentBlocks`).
### Phase 2: Polyfactory Strictness & Global Test Hardening
- Modify `ReportDataDTOFactory`: Inject appropriate layout schemas (populating `axes` for matrices and `synthesis_blocks` for markdown content) into the `layouts` generation to natively replace the deleted legacy fields, ensuring existing tests automatically cover the new SDUI flow.
- Implement `@post_generated` hooks or custom fields inside `ReportDataDTOFactory` to ensure the generated random data is mathematically coherent (e.g., syncing `tda_id` across arrays) so that standard `model_validate()` succeeds.
- **Enforce Negative Testing**: Add explicit test cases to prove `ReportDataDTO` throws a `ValidationError` if `evaluative_matrices`, `content_blocks`, or `penalties_applied` are present (Anti-Happy Path Mandate).
- Remove `factory_use_construct=True` and legacy field references (`evaluative_matrices`, `content_blocks`, `penalties_applied`) from the following test blast radius:
  - @[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py#L50-L80] — `factory_use_construct=True` removal and Golden JSON generation update
  - @[c:\src\quorum\backend_v2\tests\unit\test_flattener.py#L30-L50] — `evaluative_matrices` in test data
  - @[c:\src\quorum\backend_v2\tests\unit\services\test_execution.py#L420-L450] — `evaluative_matrices`/`informational_matrices` mock assignment
  - @[c:\src\quorum\backend_v2\tests\unit\services\test_sdui_mapper_service.py#L70-L90] — `content_blocks` in test data
  - @[c:\src\quorum\backend_v2\tests\unit\services\test_execution_render_bug.py#L50-L70] — Legacy field mock
  - @[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py#L520-L570] — `content_blocks` / `penalties_applied` test fixtures
  - @[c:\src\quorum\backend_v2\tests\integration\test_epic_chain_e2e.py#L60-L80] — Legacy field fixtures
  - @[c:\src\quorum\backend_v2\tests\test_data\report_data_dto_fixture.json] — [NEW] Remove legacy fields from mock JSON
  - **CONTEXT AMNESIA PREVENTION**: Execution of the above test file purges must be chunked into two batches with a `/tier5-session-handover` in between to prevent >4 file context window exhaustion.
  - [NEW] `c:\src\quorum\backend_v2\tests\unit\models\test_v2_core.py` — Add negative tests for `ReportDataDTO` validation failure when legacy fields are provided.
  - [NEW] `c:\src\quorum\backend_v2\tests\unit\test_worker.py` — Add negative tests verifying slop penalty detection safely ignores layouts where `metadata` is `None` or missing `"penalty_type"`.
  - [NEW] `c:\src\quorum\backend_v2\tests\unit\hooks\test_linguistics.py` — Add negative tests for missing/empty layouts.

### Phase 3: Full-Stack Integration Checkpoint
- Execute global regression audits for both backend and frontend.
- Run `test_sdui_semantic_parity.py` to ensure 100% semantic parity between Jinja PDFs and Flutter UI.
- **Tier 0 Red-Team Finding**: A dry-run of the parity test revealed a bug where numeric score fractions (e.g., `score / max_score`) are successfully rendered in Flutter but are missing from the Jinja PDF (`backend_v2/templates/report_template.jinja2`). **Root Cause Analysis completed**: The UI layer was incorrectly evaluating business logic (`scaleMax > scaleMin`) to conditionally show the fraction, violating the "Dumb Painter" architecture. **Fix**: We are moving to a Pure Dumb Painter approach (Option A). The backend will compute a unified `score_display_label` inside `MatrixScorecardRowDTO`. Both Jinja and Flutter templates MUST be refactored to blindly render this string, eliminating all UI-side scale comparisons and resolving the `AssertionError`.



## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- `ReportDataDTO` natively rejects legacy fields via Pydantic/Freezed `strict=True`.
- `test_sdui_semantic_parity.py` runs without `model_construct` bypasses.

### Automated Unit Tests
- `uv run python scripts/backend_audit_loop.py backend_v2/ --test` (Global backend regression check)
- `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/ --build` (Cross-domain DTO parity)
- `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` (Strict SDUI semantic parity verification)

### Manual Verification Steps (Human Handover)
> [!IMPORTANT]
> **AI Execution Constraint:** The AI agent MUST NOT attempt to start the Flutter app or visually verify UI rendering autonomously. The AI must STOP execution and explicitly instruct the HUMAN USER to perform these manual validations.

1. Re-seed local database (`uv run python backend_v2/seed/run_seed.py local`).
2. Start the backend and Flutter app locally. Execute a test workflow and verify the report renders matrices correctly and penalties as styled blocks.
3. Verify that PDF export renders identically to the Flutter UI.
4. Verify the report renders flawlessly without `content_blocks` or `penalties_applied` top-level variables in the API response.

### MANDATORY Final E2E REST API Verification Gate
- `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

## 5. Known Technical Debt (Out of Scope for Epic 111)

> [!WARNING]
> **OutputProfile.content_blocks Naked-Dynamic Violation**
> The Flutter model @[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart#L162] has `contentBlocks` typed as `List<dynamic>` — a naked dynamic list that violates strict Freezed typing. The backend @[c:\src\quorum\backend_v2\models\dtos\output_profile.py#L104] mirrors this. While Epic 111 correctly scopes strictly to the `ReportDataDTO` rendering pipeline, this `OutputProfile` structure is a known architectural debt item. It requires its own dedicated Epic (e.g. Epic 112) to replace `List<dynamic>` with a strictly typed `List<OutputLayoutBlock>` discriminated union. Attempting to fix it inside Epic 111 would cause a "Big Bang" refactor across the Studio Editor views.
