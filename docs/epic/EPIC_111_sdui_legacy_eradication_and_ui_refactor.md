# EPIC 111: Eradicate Legacy SDUI Fields & Output Profile Refactoring

## 1. Goal Description & Background (Objective & Problem Statement)
The Quorum system has been migrating towards a 100% "Dumb Painter" Server-Driven UI (SDUI) architecture (Epic 110). However, critical technical debt remains in the `ReportDataDTO` pipeline. Legacy arrays (such as `content_blocks`, `evaluative_matrices`, and `penalties_applied`) were left as separate top-level variables alongside the new dynamic `layouts` generator to maintain backward compatibility. This violates the "Zero Alternative Output Paths" mandate established in Epics 106, 109, and 110. 

Additionally, the Flutter `OutputProfileCrudView` UI is currently a monolithic, deeply nested split-pane structure that is difficult to scale, and internal testing frameworks have relied on Pydantic `model_construct` validation bypasses, causing "Frankenstein" object/dictionary hybrids that break Jinja rendering rules. Finally, LLM "Semantic Drift" has caused unwanted renaming of DTO fields (e.g., `cognitive_status` to `status`), breaking cross-domain serialization.

**Objective:**
1. **Absolute SDUI Parity**: Completely delete all legacy top-level report arrays from `ReportDataDTO`. All data MUST route exclusively through the `layouts` array.
2. **UI Modernization**: Refactor the Output Profile Editor into a scalable 3-tab layout (`DefaultTabController`) to seamlessly manage Terminology and Extensions.
3. **Pydantic Strictness**: Remove `model_construct` bypasses in Polyfactory tests, enforcing mathematically coherent, 100% strictly validated mock objects.
4. **Semantic Anti-Drift**: Enforce strict 1:1 identical naming conventions between Python and Flutter without arbitrary AI-driven renames.

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)
- **Legacy SDUI Fields**: `ReportDataDTO.content_blocks`, `ReportDataDTO.evaluative_matrices`, `ReportDataDTO.informational_matrices`, and `ReportDataDTO.penalties_applied` will be permanently DELETED.
- **Flutter Rendering Fallbacks**: Any conditional UI logic in `report_renderer_v2_widget.dart` that attempts to parse legacy `contentBlocks` or `evaluativeMatrices` will be PURGED.
- **Test Hacks**: `factory_use_construct=True` will be DELETED from `test_sdui_semantic_parity.py`.

### Retained SSOT Invariants (`What We Will RETAIN`)
- **Dumb Painter Layouts**: The `layouts` array (`List<ReportLayoutDto>`) remains the absolute Single Source of Truth for all report rendering.
- **Riverpod State Management**: `outputProfileFormProvider` remains the SSOT for the transient Output Profile form state.

### Compliance & Modernity Gates
1. **The "Zero Alternative Paths" Rule**: If data is to be rendered on the report, it MUST be wrapped in a `ReportLayoutDto` inside the `layouts` array.
2. **Pydantic Strictness / Validation Bypasses**: Bypassing validation via `model_construct` that results in nested dictionaries is explicitly BANNED when passing data to Jinja or Flutter.
3. **Anti-Semantic Drift**: DTO field names are PERMANENT architectural contracts. Python `snake_case` must perfectly match Flutter `camelCase` (e.g., `evaluation_reasoning` -> `evaluationReasoning`). Renaming for subjective "clarity" is strictly forbidden.
4. **Cross-Domain Parity**: All Pydantic schema changes MUST instantly trigger `flutter_audit_loop.py --build` to verify Freezed serialization.

### Producer-Consumer Integration Check
- **Producer**: `blueprint.py` must be upgraded to inject legacy concepts (like penalties) into dedicated `ReportLayoutDto` blocks.
- **Consumer**: Flutter (`report_renderer_v2_widget.dart`) and Jinja (`report_template.jinja2`) blindly iterate over `layouts`.

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 0: Seed Data & Database Prerequisite / Migration
- Ensure the database is cleanly re-seeded without legacy definitions causing test failures.
- Run: `uv run python backend_v2/seed/run_seed.py local`

### Phase 1: Backend DTO Strictness & Eradicating Legacy Fields
- Modify @[c:\src\quorum\backend_v2\models\v2_core.py]: Delete `content_blocks`, `evaluative_matrices`, `informational_matrices`, and `penalties_applied` from `ReportDataDTO`.
- Modify @[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart]: Mirror the deletions in the Flutter Freezed model and run the code generator.
- Modify @[c:\src\quorum\backend_v2\services\blueprint.py]: Refactor the SDUI generator to route 100% of the dynamic report data exclusively through the `layouts` array.

### Phase 2: Polyfactory Strictness & Test Hardening
- Modify @[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py]: Remove `penalties_applied: []` and `content_blocks: []` mocks. Remove `factory_use_construct=True` from `ReportDataDTOFactory`.
- Implement `@post_generated` hooks or custom fields inside `ReportDataDTOFactory` to ensure the generated random data is mathematically coherent (e.g., syncing `tda_id` across arrays) so that standard `model_validate()` succeeds.

### Phase 3: Flutter UI Refactoring (3-Part Layout Editor)
- Modify @[c:\src\quorum\client_app_v2\lib\features\studio\views\output_profile_crud_view.dart]: Remove split-pane logic and implement a `DefaultTabController(length: 3)`.
- Create `output_profile_general_tab.dart` (Basic Info).
- Create `output_profile_extensions_tab.dart` (XAI Checkboxes).
- Create `output_profile_layouts_tab.dart` (Dynamic Section Builder & Terminology).
- Modify @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart]: Purge all fallback rendering logic.

### Phase 4: Widget Testing (SDUI Field Verification)
- Create `output_profile_crud_view_test.dart` to simulate the UI in a `ProviderScope`.
- Assert Tab Navigation rendering.
- Assert SDUI Parity Validation (ensure checkboxes for metadata and extension items exist in the DOM).
- Assert Terminology & Axis Definitions (ensure `I18nTextField`s exist for dynamic axis labels).

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- `ReportDataDTO` natively rejects legacy fields via Pydantic/Freezed `strict=True`.
- `test_sdui_semantic_parity.py` runs without `model_construct` bypasses.
- Flutter UI matches the 3-tab layout specification perfectly.

### Automated Unit Tests
- `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`
- `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/ --build`
- `flutter test client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart`

### Manual Verification Steps
1. Re-seed local database (`uv run python backend_v2/seed/run_seed.py local`).
2. Open Admin Studio -> Edit Output Profile, verify 3-tab layout.
3. Run a test execution and verify the report renders flawlessly without `content_blocks` or `penalties_applied` top-level variables.

### MANDATORY Final E2E REST API Verification Gate
- `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
