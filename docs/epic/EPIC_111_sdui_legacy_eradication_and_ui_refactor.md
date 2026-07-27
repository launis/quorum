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
- **Penalties Migration (NOT Deletion)**: `ReportDataDTO.penalties_applied` MUST be migrated into the existing `layouts` array using the standard `ReportLayoutDTO`. Do NOT create a polymorphic `ReportLayoutBase` or `ReportLayoutPenaltyBlockDTO` (this was an architectural hallucination that would trigger a Big-Bang UI refactor). Instead, map penalties into a `ReportLayoutDTO` with `preset_view="text_only"` (or similar) and inject the penalty text natively into `synthesis_blocks` using standard SDUI blocks. The slop detection logic in @[c:\src\quorum\backend_v2\worker.py#L444-L458] must be refactored to scan the `layouts` array (e.g., checking for specific `synthesis_blocks` types or content) without relying on a dedicated top-level array.
- **worker.py hasattr() Purge**: All `hasattr()` and `isinstance(x, dict)` checks inside @[c:\src\quorum\backend_v2\worker.py#L846-L874] MUST be deleted. The code must rely entirely on Pydantic's static typing and `.model_dump()` to extract `content_blocks` from known DTOs (e.g., `SynthesisOutputDTO`), strictly enforcing the "Zero-Compromise Pledge".
- **Flutter Rendering Fallbacks**: All conditional UI logic in @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart], @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\diagnostic_scorecard_widget.dart], @[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_report_view.dart], and @[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_view.dart] that parses legacy fields will be PURGED.
- **Jinja PDF Template**: @[c:\src\quorum\backend_v2\templates\report_template.jinja2] must be refactored to iterate exclusively over `layouts` instead of reading `evaluative_matrices`, `content_blocks`, or `penalties_applied` directly.
- **Test Hacks**: `factory_use_construct=True` will be DELETED from all Polyfactory fixtures.

> [!WARNING]
> **SCOPE BOUNDARY**: The `content_blocks` field on `SynthesisSectionDTO` and `SynthesisOutputDTO` (synthesis-domain DTOs) is architecturally DISTINCT from `ReportDataDTO.content_blocks` and MUST NOT be deleted. Similarly, the `_evaluative_matrices` internal state key in @[c:\src\quorum\backend_v2\hooks\scoring.py] is an internal DAG execution state alias, NOT a rendering field, and MUST be preserved.

### Retained SSOT Invariants (`What We Will RETAIN`)
- **Dumb Painter Layouts**: The `layouts` array (`List<ReportLayoutDto>`) remains the absolute Single Source of Truth for all report rendering.
- **Riverpod State Management**: `outputProfileFormProvider` remains the SSOT for the transient Output Profile form state.

### Compliance & Modernity Gates
1. **The "Zero Alternative Paths" Rule**: If data is to be rendered on the report, it MUST be wrapped in a `ReportLayoutDto` inside the `layouts` array.
2. **Pydantic Strictness / Validation Bypasses**: Bypassing validation via `model_construct` that results in nested dictionaries is explicitly BANNED when passing data to Jinja or Flutter.
3. **Anti-Semantic Drift**: DTO field names are PERMANENT architectural contracts. Python `snake_case` must perfectly match Flutter `camelCase` (e.g., `evaluation_reasoning` -> `evaluationReasoning`). Renaming for subjective "clarity" is strictly forbidden.
4. **Cross-Domain Parity**: All Pydantic schema changes MUST instantly trigger `flutter_audit_loop.py --build` to verify Freezed serialization.

### Producer-Consumer Integration Check
- **Producer**: @[c:\src\quorum\backend_v2\services\blueprint.py] must be upgraded to inject legacy concepts (like penalties, matrices, synthesis content) into dedicated `ReportLayoutDto` blocks.
- **Consumer (Flutter)**: @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart] blindly iterates over `layouts`. The legacy `DiagnosticScorecardWidget` must be refactored to consume a strictly defined `MATRIX_SCORECARD_TABLE` layout block instead of top-level metadata, adhering to the Dumb Painter pattern.
- **Consumer (Jinja)**: @[c:\src\quorum\backend_v2\templates\report_template.jinja2] must be migrated to iterate over `layouts`.
- **Consumer (Backend)**: @[c:\src\quorum\backend_v2\services\execution.py], @[c:\src\quorum\backend_v2\services\flattener.py], @[c:\src\quorum\backend_v2\hooks\linguistics.py], and @[c:\src\quorum\backend_v2\services\sdui_mapper_service.py] must be refactored to read from `layouts`.

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 0: Seed Data & Database Prerequisite / Migration
- Ensure the database is cleanly re-seeded without legacy definitions causing test failures.
- Run: `uv run python backend_v2/seed/run_seed.py local`

### Phase 1: Backend DTO Strictness & Eradicating Legacy Fields
- Modify @[c:\src\quorum\backend_v2\models\v2_core.py]: Delete `content_blocks`, `evaluative_matrices`, `informational_matrices`, and `penalties_applied` from `ReportDataDTO`. (Penalties will now be dynamically assembled into standard `ReportLayoutDTO` blocks by the blueprint service, avoiding polymorphic schema bloat).
- Modify @[c:\src\quorum\backend_v2\services\blueprint.py]: Refactor the SDUI generator to route 100% of the dynamic report data exclusively through the `layouts` array, including matrices and penalties.
- Modify @[c:\src\quorum\backend_v2\templates\report_template.jinja2]: Migrate Jinja rendering to iterate exclusively over `layouts` for matrices, content blocks, and penalties.
- Modify @[c:\src\quorum\backend_v2\services\execution.py]: Remove direct references to legacy matrix and content_blocks fields.
- Modify @[c:\src\quorum\backend_v2\services\flattener.py]: Refactor matrix flattening to use `layouts`.
- Modify @[c:\src\quorum\backend_v2\hooks\linguistics.py]: Refactor linguistic matrix analysis to use `layouts`.
- Modify @[c:\src\quorum\backend_v2\services\sdui_mapper_service.py]: Remove direct `content_blocks` mapping (already covered by layouts).
- Modify @[c:\src\quorum\backend_v2\worker.py]: Refactor slop penalty detection at L444-L458. CRITICALLY: Purge all `hasattr()` and naked dictionary checks at L846-L874 to enforce pure Pydantic hydration.
- Modify @[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart]: Mirror the deletions in the Flutter Freezed model and run the code generator.
- Modify @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\diagnostic_scorecard_widget.dart]: Remove direct `evaluativeMatrices`/`informationalMatrices` consumption.
- Modify @[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_report_view.dart]: Remove `evaluativeMatrices` passthrough.
- Modify @[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_view.dart]: Remove `evaluativeMatrices` passthrough.
- Modify @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart]: Purge all fallback rendering logic.
### Phase 2: Polyfactory Strictness & Global Test Hardening
- Modify `ReportDataDTOFactory`: Inject `MATRIX_SCORECARD_TABLE` and `MARKDOWN_BLOCK` layout schemas into the `layouts` generation to natively replace the deleted legacy fields, ensuring existing tests automatically cover the new SDUI flow.
- Implement `@post_generated` hooks or custom fields inside `ReportDataDTOFactory` to ensure the generated random data is mathematically coherent (e.g., syncing `tda_id` across arrays) so that standard `model_validate()` succeeds.
- Remove `factory_use_construct=True` and legacy field references (`evaluative_matrices`, `content_blocks`, `penalties_applied`) from the following test blast radius:
  - @[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py]
  - @[c:\src\quorum\backend_v2\tests\unit\test_flattener.py]
  - @[c:\src\quorum\backend_v2\tests\unit\services\test_execution.py]
  - @[c:\src\quorum\backend_v2\tests\unit\services\test_sdui_mapper_service.py]
  - @[c:\src\quorum\backend_v2\tests\unit\services\test_execution_render_bug.py]
  - @[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]
  - @[c:\src\quorum\backend_v2\tests\integration\test_epic_chain_e2e.py]



## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- `ReportDataDTO` natively rejects legacy fields via Pydantic/Freezed `strict=True`.
- `test_sdui_semantic_parity.py` runs without `model_construct` bypasses.

### Automated Unit Tests
- `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`
- `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/ --build`

### Manual Verification Steps
1. Re-seed local database (`uv run python backend_v2/seed/run_seed.py local`).
2. Run a test execution and verify the report renders flawlessly without `content_blocks` or `penalties_applied` top-level variables.

### MANDATORY Final E2E REST API Verification Gate
- `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

## 5. Known Technical Debt (Out of Scope for Epic 111)

> [!WARNING]
> **OutputProfile.content_blocks Naked-Dynamic Violation**
> The Flutter model @[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart#L162] has `contentBlocks` typed as `List<dynamic>` — a naked dynamic list that violates strict Freezed typing. The backend @[c:\src\quorum\backend_v2\models\dtos\output_profile.py#L104] mirrors this. While Epic 111 correctly scopes strictly to the `ReportDataDTO` rendering pipeline, this `OutputProfile` structure is a known architectural debt item. It requires its own dedicated Epic (e.g. Epic 112) to replace `List<dynamic>` with a strictly typed `List<OutputLayoutBlock>` discriminated union. Attempting to fix it inside Epic 111 would cause a "Big Bang" refactor across the Studio Editor views.
