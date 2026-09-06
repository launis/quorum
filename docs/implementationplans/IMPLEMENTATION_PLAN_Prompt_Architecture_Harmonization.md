# IMPLEMENTATION PLAN: Prompt Architecture Harmonization (Tripartite Subpackage Topology, FinOps Caching, Studio UI 1:1 Parity & SSOT Length Budgeting)

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_generation_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
</required_context_rules>

## Objective
Harmonize the prompt architecture across `backend_v2/models/prompts/`, caller modules, and the Flutter Studio UI (`client_app_v2`) according to Option B (Tripartite Domain Partitioning) with **Zero-Fallback Database Sovereignty**, **1:1 Studio UI Section Parity**, **Two-Tier SSOT Length Budgeting**, and **Matrix Synthesis Group Cardinality & Intra-Block Reordering Invariants**.
Specifically:
1. Centralize prompt assets into dedicated subpackages (`common/`, `execution/`, `synthesis/`), eradicating prompt repetition and tone leakage.
2. Decouple static linguistic protocols from dynamic parameters for maximum prefix context caching (95%+ hit rate).
3. Establish the database (`OutputProfile`) as the sole authoritative SSOT for substantive coaching directives and persona tones, permanently deleting code-level fallback registries (`synthesis_registry.py`), and enforcing strict Fail-Fast validation on missing directives.
4. Segregate Studio UI editing: Directives that map 1:1 to a specific report output section (specifically: Executive Summary, Matrix Summary Table, XAI Extensions, Variance Validation) reside strictly within their dedicated section detail cards on Tab 3 (`ProfileSectionConfigTab`), and are permanently pruned from Tab 1 (`ProfileGeneralTab`). Reusable multi-instance view type directives (specifically: 1D, 2D, 3D, and Text) remain in Tab 1 alongside general persona tone (`tone_instruction`), user role label (`user_role_label`), custom preface (`custom_preface`), and target locale (`target_locale`).
5. Mandate English-Only Plain Strings (`str`) for All 9 Prompt Directives and Tone Instructions: In accordance with Rule `native_language_system_prompts` and Rule `cross_language_mapping_mandate`, all LLM synthesis directives and persona tone instructions (`tone_instruction`, `executive_summary_directive`, `matrix_1d_synthesis_directive`, `matrix_2d_synthesis_directive`, `matrix_3d_synthesis_directive`, `matrix_text_synthesis_directive`, `row_explanation_directive`, `xai_synthesis_directive`, `variance_synthesis_directive`) MUST be defined strictly and exclusively in English (`str | None`). Eliminate bilingual `I18nText` wrappers and `I18nTextField` language-switching tabs from Studio UI prompt inputs, replacing them with clean single-language English text inputs (`TextFormField`). True report presentation headers (`name`, `description`, `user_role_label`, `custom_preface`) remain bilingual `I18nText` for human reader presentation. Target language report generation is instructed exclusively via Layer 4 dynamic parameter `<required_output_language>{target_locale}</required_output_language>`.
6. Implement Two-Tier SSOT character length budgeting across all 4 1:1 section blocks (`executiveSummaryBlock`, `matrixSummaryTableBlock`, `groupedExtensionsBlock`, `varianceValidationBlock`). Enforce length constraints via dynamic Layer 4 prompt budgets (`<section_budget>`) with sentence-boundary post-processing (`enforce_sentence_boundary_budget`), guaranteeing zero mid-sentence truncation and 100% prefix context caching preservation.
7. Reject user-facing UI checkboxes toggling `"- Structure your findings directly as SDUI blocks."` to prevent Pydantic validation crashes on non-SDUI string outputs (`row_explanation`, `xai_highlights`, `variance_explanation`). Purge technical formatting directives from substantive prompt fields, locking structural formatting strictly inside Layer 2 assets for polymorphic block tasks.
8. Enforce dimensional cardinality validation on matrix synthesis groups (specifically: 1D metrics == 1 block, 2D compare == 2 blocks, 3D radar == 3 blocks, and Text-only >= 1 block) via an explicit backend `@model_validator(mode="after")` on `MatrixSynthesisGroup` in `backend_v2/models/v2_core.py` and enforce unique synthesis group IDs via `@model_validator(mode="after")` on `OutputProfile`. In `backend_v2/services/studio/output_profile_service.py`, bind `create_output_profile_draft` directly to `output_profile_factory.py` so newly drafted profiles created headlessly via REST API are 100% valid and runnable out-of-the-box without requiring UI interaction. Persist the intra-block sequence of matrix synthesis groups directly into the MongoDB document array as the authoritative Single Source of Truth (SSOT). Eradicate the `seen_axes` bug in `backend_v2/services/sdui/adapters/matrix_graphs_adapter.py` so each visual group independently accesses its configured target blocks. Upgrade `MatrixGraphsBlockCard` in Studio UI (`client_app_v2`) to a dumb reordering list utilizing `ReorderableListView` (with dedicated drag handles and Up/Down `IconButton` controls), and enforce single-selection radio replacement and quota-based chip disabling in `MatrixGraphItemEditor` (completely eliminating client-side auto-clamping in favor of strict backend validation).

## Scope & File Boundaries

### Target Files (Modifications & Relocations)
- [NEW] `@[backend_v2/models/prompts/common/__init__.py]`
- [NEW] `@[backend_v2/models/prompts/common/global_mandates.py]`
- [NEW] `@[backend_v2/models/prompts/common/linguistic_directives.py]`
- [NEW] `@[backend_v2/models/prompts/common/field_prompts.py]`
- [NEW] `@[backend_v2/models/prompts/execution/__init__.py]`
- [NEW] `@[backend_v2/models/prompts/execution/matrix_evaluation.py]`
- [NEW] `@[backend_v2/models/prompts/execution/hook_prompts.py]`
- [NEW] `@[backend_v2/models/prompts/execution/mcp_prompts.py]`
- [NEW] `@[backend_v2/models/prompts/synthesis/__init__.py]`
- [NEW] `@[backend_v2/models/prompts/synthesis/style_directives.py]`
- [NEW] `@[backend_v2/models/prompts/synthesis/sdui_directives.py]`
- [NEW] `@[backend_v2/models/prompts/synthesis/synthesis_directives.py]`
- [NEW] `@[backend_v2/services/factories/output_profile_factory.py]`
- [NEW] `@[backend_v2/services/length_budget_enforcer.py]`
- [NEW] `@[backend_v2/tests/unit/services/test_length_budget_enforcer.py]`
- [MODIFY] `@[backend_v2/models/prompts/__init__.py]`
- [DELETE] `@[backend_v2/models/prompts/global_mandates.py]`
- [DELETE] `@[backend_v2/models/prompts/linguistic_directives.py]`
- [DELETE] `@[backend_v2/models/prompts/field_prompts.py]`
- [DELETE] `@[backend_v2/models/prompts/matrix_evaluation.py]`
- [DELETE] `@[backend_v2/models/prompts/hook_prompts.py]`
- [DELETE] `@[backend_v2/models/prompts/mcp_prompts.py]`
- [DELETE] `@[backend_v2/models/prompts/style_directives.py]`
- [DELETE] `@[backend_v2/models/prompts/sdui_directives.py]`
- [DELETE] `@[backend_v2/models/prompts/synthesis_directives.py]`
- [DELETE] `@[backend_v2/models/prompts/synthesis_registry.py]`
- [MODIFY] `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L25-L229]`
- [MODIFY] `@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L49-L222]`
- [MODIFY] `@[backend_v2/worker.py#L758-L1655]`
- [MODIFY] `@[backend_v2/hooks/interaction_hook.py#L40-L148]`
- [MODIFY] `@[backend_v2/services/orchestrator/extraction_schema_factory.py#L115-L180]`
- [MODIFY] `@[backend_v2/services/orchestrator/extractive_sensor_service.py#L90-L529]`
- [MODIFY] `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L240]`
- [MODIFY] `@[backend_v2/services/translation_service.py#L18-L76]`
- [MODIFY] `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py#L36-L109]`
- [MODIFY] `@[backend_v2/services/studio/output_profile_service.py#L22-L236]`
- [MODIFY] `@[backend_v2/models/dtos/evaluation_steps.py#L16-L75]`
- [MODIFY] `@[backend_v2/models/dtos/synthesis.py#L44-L61]`, `@[backend_v2/models/dtos/synthesis.py#L87-L106]`, `@[backend_v2/models/dtos/synthesis.py#L128-L159]`, `@[backend_v2/models/dtos/synthesis.py#L198-L241]`
- [MODIFY] `@[backend_v2/models/dtos/output_profile.py#L40-L238]`, `@[backend_v2/models/dtos/output_profile.py#L241-L427]`, `@[backend_v2/models/dtos/output_profile.py#L430-L562]`
- [MODIFY] `@[backend_v2/models/domain/output_profile.py]`
- [MODIFY] `@[backend_v2/models/v2_core.py#L906-L923]`, `@[backend_v2/models/v2_core.py#L926-L1159]`
- [MODIFY] `@[backend_v2/llm/schema_builder.py#L20-L202]`
- [MODIFY] `@[backend_v2/core/registry.py#L75-L159]`
- [MODIFY] `@[backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py]`
- [MODIFY] `@[backend_v2/tests/unit/models/prompts/test_global_mandates.py]`
- [MODIFY] `@[backend_v2/tests/unit/models/prompts/test_linguistic_directives.py]`
- [MODIFY] `@[backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py]`
- [MODIFY] `@[backend_v2/tests/unit/models/prompts/test_hook_prompts.py]`
- [MODIFY] `@[backend_v2/tests/unit/models/prompts/test_mcp_prompts.py]`
- [MODIFY] `@[backend_v2/tests/unit/models/prompts/test_style_directives.py]`
- [NEW] `@[backend_v2/tests/unit/models/prompts/test_sdui_directives.py]`
- [MODIFY] `@[backend_v2/tests/unit/models/prompts/test_synthesis_directives.py]`
- [MODIFY] `@[backend_v2/tests/unit/models/prompts/test_field_prompts.py]`
- [DELETE] `@[backend_v2/tests/unit/models/prompts/test_synthesis_registry.py]`
- [MODIFY] `@[backend_v2/tests/unit/models/prompts/test_prompts_init.py]`
- [MODIFY] `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]`
- [MODIFY] `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py]`
- [MODIFY] `@[backend_v2/tests/unit/test_worker_synthesis.py]`
- [MODIFY] `@[backend_v2/tests/unit/test_sdui_prompt_alignment.py]`
- [MODIFY] `@[backend_v2/tests/unit/services/test_translation_service.py]`
- [MODIFY] `@[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py]`
- [MODIFY] `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`
- [MODIFY] `@[backend_v2/tests/unit/services/test_output_profile_studio_parity.py]`
- [MODIFY] `@[backend_v2/tests/unit/services/sdui/adapters/test_matrix_graphs_adapter.py]`
- [MODIFY] `@[backend_v2/tests/unit/services/studio/test_output_profile_service.py]`
- [MODIFY] `@[backend_v2/tests/unit/test_v2_core_models.py]`
- [MODIFY] `@[backend_v2/seed/seed_data.json#L16750-L16780]`, `@[backend_v2/seed/seed_data.json#L18192-L18332]`
- [MODIFY] `@[client_app_v2/lib/features/studio/models/output_profile.dart#L1-L121]`
- [MODIFY] `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart#L1-L405]`
- [MODIFY] `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/executive_summary_block_card.dart#L1-L92]`
- [MODIFY] `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart#L1-L141]`
- [MODIFY] `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart#L1-L221]`
- [MODIFY] `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/variance_block_card.dart#L1-L174]`
- [MODIFY] `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L1-L245]`
- [MODIFY] `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart#L1-L136]`
- [MODIFY] `@[client_app_v2/test/features/studio/views/widgets/profile/tabs/profile_general_tab_test.dart#L1-L53]`
- [MODIFY] `@[client_app_v2/test/features/studio/views/widgets/profile/tabs/profile_section_config_tab_test.dart#L1-L170]`
- [MODIFY] `@[client_app_v2/test/unit/features/studio/matrix_graph_editor_test.dart#L1-L185]`
- [MODIFY] `@[client_app_v2/lib/l10n/app_en.arb#L1-L2365]`
- [MODIFY] `@[client_app_v2/lib/l10n/app_fi.arb#L1-L1664]`

### Context Files (Read-Only)
- `@[backend_v2/services/source_verification_service.py]`
- `@[backend_v2/services/mcp/mcp_tool_loop.py]`
- `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L1-L280]`

---

## Technical Debt & Anti-Pattern Pre-Flight Audit (Feature Audit & Database SDUI Alignment)

Per the System 2 Feature Audit findings in `feature_audit_sdui_directives_and_database.md` and `feature_audit_section_length_and_sdui_toggle.md`, the following concrete technical debt, contract fractures, and architectural violations are identified across target files and scheduled for resolution:

### 1. Python Backend Technical Debt (`backend_v2/models/prompts/` and `backend_v2/worker.py`)
- **Single Responsibility Principle (SRP) Violation in `sdui_directives.py`**: Lines 26-27 (`USER_ROLE_EXTRACTION` and `ROLE TRANSLATION`) embed user interaction role classification inside structural Server-Driven UI layout mandates. User role deduction belongs strictly to `@[backend_v2/hooks/interaction_hook.py]` and schema docstrings.
- **Dual-Prompt Contradiction & Instruction Clashing in `worker.py`**: `worker.py` (Line 1045) injects `SYNTHESIS_SDUI_MANDATES` (mandating literal discriminators `'paragraph'`, `'bullet_list'`, `'alert_box'`, `'quote_card'`, `'warning_card'`) into the static system prompt prefix, but then injects `active_profile_dto.executive_summary_directive` (mandating `"using SDUI ParagraphBlocks."`) into the user message dynamic context. This creates direct cognitive dissonance for LLM decoders and risks Pydantic validation failures.
- **Dual SSOT & Silent Fallback Anti-Pattern**: Substantive prompts exist in two competing places (database `OutputProfile` vs code constants in `synthesis_directives.py` and the shadow dictionary `synthesis_registry.py`). In `worker.py` (lines 1210, 1251-1254, 1382-1384), unconfigured profile fields silently execute fallback chains using direct constant imports (`if not directive: fallback`), violating `zero_service_layer_fallbacks` and `universal_ssot_and_normalization_mandate`. Note that `worker.py` uses direct constant imports (`VARIANCE_EXPLANATION_DIRECTIVE`, `XAI_EXPLANATIONS_DIRECTIVE`), NOT `SynthesisPromptRegistry`.
- **Linguistic Mandate Pollution in Schema Models (`backend_v2/models/dtos/synthesis.py`)**: Forensic Tier 0 inspection verified that `synthesis.py` (Line 12) imports `DESC_TRANSLATION_MANDATE` and injects it into 8 field descriptions across schema models: `XaiHighlightItem.content` (Line 60), `SynthesisRowExplanationDTO.row_explanation` (Line 101), `ExecutiveSummarySectionResult.user_role`, `user_role_justification`, `cited_sources` (Lines 143, 147, 151), and `SynthesisOutputDTO.user_role`, `user_role_justification`, `cited_sources` (Lines 217, 221, 226). This violates `linguistic_mandate_centralization_ssot` and `prompt_asset_ssot_mandate`. It must be permanently purged across all 8 field descriptions and the import removed, returning all schema field descriptions to pure semantic explanations without prompt translation directives.

### 2. Database Seed Vault Technical Debt (`@[backend_v2/seed/seed_data.json]`)
- **Literal Class Names in `output_profiles` (`prf_5d6e7f8091a2b3c4`)**: Line 18200 (`executive_summary_directive`) instructs the LLM to structure paragraphs `"using SDUI ParagraphBlocks."`. This violates `@[backend_v2/tests/unit/test_sdui_prompt_alignment.py]` which strictly asserts `assert "ParagraphBlock" not in SYNTHESIS_SDUI_MANDATES`.
- **De-Generator Architecture Breach in `output_profiles` (`prf_5d6e7f8091a2b3c4`)**: Lines 18206, 18212, 18218, 18224, 18236 (English) and 18237 (Finnish) repeatedly hardcode technical UI rendering directives: `"- Structure your findings directly as SDUI blocks."` and `"- Muotoile löydökset suoraan SDUI-lohkoina."`. Substantive coaching directives authored in Studio UI must contain zero technical formatting instructions; structural presentation rules belong exclusively to static Layer 2 code assets (`backend_v2/models/prompts/synthesis/sdui_directives.py` and `backend_v2/models/prompts/synthesis/style_directives.py`).
- **Legacy Orphan Prompt Block (`blk_eeea566da4ab45f9`)**: Line 16756 (`blk_synthesis_global_rules`) contains a monolithic prompt text with legacy V1 class names (`'ParagraphBlock'`, `'BulletListBlock'`, `'AlertBlock'`, `'QuoteBlock'`) and corrupted XML tags (`If is provided... current .`). It is referenced exclusively by orphan step `sp_9c6a85edc29347b9` (`sp_synthesis_llm`), which is not part of any active workflow in `workflows`.

### 3. Flutter Studio UI Technical Debt & Dual-Location Editing (`client_app_v2`)
- **Cognitive Dissonance & Dual-Location Editing in Tab 1 vs Tab 3**: Card 3 of `ProfileGeneralTab` (`client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart`, lines 279-398) duplicates input fields for all 8 directives. Specifically, `executiveSummaryDirective`, `rowExplanationDirective`, `xaiSynthesisDirective`, and `varianceSynthesisDirective` already possess dedicated `I18nTextField` editors in their respective section detail cards in Tab 3 (`ExecutiveSummaryBlockCard`, `MatrixSummaryTableCard`, `XaiExtensionsBlockCard`, `VarianceBlockCard`). This dual-entry anti-pattern causes UI confusion, breaks single-responsibility editing, and creates cognitive dissonance.
- **Conflation of 1:1 Section Directives with Multi-Instance Graph Directives**: Unlike 1:1 section blocks, 1D, 2D, 3D, and text matrix visualizations (`matrix_synthesis_groups`) can appear multiple times sequentially in a report (for instance: three 2D comparisons in a row). Tab 1 is the logical home for defining these 4 reusable view type directives, but Tab 1 mistakenly also hosts the 1:1 section directives.

### 4. Length Budgeting Technical Debt & Mid-Sentence Truncation Hazards
- **Missing Section Length Controls**: Only `executiveSummaryBlock` currently exposes `synthesis_length_constraint`. The other three 1:1 sections (`matrixSummaryTableBlock`, `groupedExtensionsBlock`, `varianceValidationBlock`) lack configurable length budgets, preventing fine-tuned executive layout balancing.
- **Brutal Slicing Hazard**: Naive character slicing (`text[:limit]`) produces malformed sentences ending mid-word, destroying executive credibility. A sentence-boundary aware budgeting engine is required.
- **Schema Collision Hazard**: Introducing a UI toggle to instruct the LLM to format outputs as SDUI blocks for non-block sections (`row_explanation`, `xai_highlights`, `variance_explanation`) clashes with Pydantic string validation contracts, causing fatal pipeline crashes.

### 5. Matrix Synthesis Group Cardinality, Seed Data Incoherence & Seen Axes Anti-Pattern
- **Absolute Ban on Client-Side "Auto-Clamping on Load"**: Attempting to "auto-clamp on load" (specifically: silently slicing or discarding invalid matrix block selections during Flutter widget initialization, `initState`, or `build` in `matrix_graph_item_editor.dart`) is a catastrophic duct-tape anti-pattern. It masks corrupted database records, introduces unprompted client-side mutations, violates CQRS and Dumb Screen invariants, and leaves external REST API callers completely unprotected. Quality assurance and data integrity MUST be locked 100% into the backend via `@model_validator(mode="after")` and database seed sanitization. The frontend UI remains strictly a dumb interactive reflection of backend state.
- **Missing Group ID Uniqueness Validation on `OutputProfile`**: `OutputProfile` in `@[backend_v2/models/v2_core.py#L926-L1159]` previously lacked validation asserting that all `MatrixSynthesisGroup.id` entries in `matrix_synthesis_groups` are distinct. If an external API client or cloned draft payload submits duplicate group IDs (specifically: `grp_440a5fef9331451b` duplicated), client-side Flutter widgets (`ReorderableListView`, `Key`, state tracking) and backend adapters suffer key collisions, race conditions, and silent data corruption. An explicit `@model_validator(mode="after")` must enforce unique group IDs.
- **Headless Incomplete Draft Anti-Pattern in `output_profile_service.py`**: In `@[backend_v2/services/studio/output_profile_service.py#L22-L236]`, `create_output_profile_draft` (`#L166-L197`) previously instantiated an empty skeleton `OutputProfile` with null substantive directives. When an external API client (or CLI script) invokes `POST /api/v2/studio/profiles/draft` and attempts runtime synthesis, execution immediately crashes with `AppException(ErrorCodes.OUTPUT_PROFILE_INCOMPLETE)`. The draft service MUST bind `output_profile_factory.py` (`build_draft_output_profile`) to pre-populate all 8 substantive directives (English `str`), valid default length constraints, a valid `target_block_order`, and an initial valid `MatrixSynthesisGroup`, guaranteeing that draft profiles created headlessly via REST API are 100% complete, valid, and runnable out-of-the-box without requiring UI interaction.
- **Missing Backend Model Validation on `MatrixSynthesisGroup`**: `MatrixSynthesisGroup` in `@[backend_v2/models/v2_core.py#L906-L923]` only asserts `target_blocks: list[str] = Field(min_length=1)`. It lacks an explicit `@model_validator(mode="after")` asserting that `len(target_blocks)` strictly satisfies the dimensional requirements of `view_type`. Backend validation must enforce: 1D == 1, 2D == 2, 3D == 3, Text >= 1.
- **Seed Data Incoherence in `seed_data.json`**: Lines 18289-18331 of `output_profiles` (`prf_5d6e7f8091a2b3c4`) in `@[backend_v2/seed/seed_data.json#L18289-L18331]` define 3 matrix groups with `"view_type": "1d_metrics"` while assigning 2 target blocks to each group (specifically: Toulmin and Bloom in Group 1, Causal Inference and Falsification in Group 2, XAI and Explainability in Group 3). This is the direct root cause of the visual glitch `2 / 1 valittu` in the Studio editor. The seed file must be sanitized by setting `view_type: "2d_compare"` for these 3 comparative groups.
- **`seen_axes` Cross-Group Drop Bug in `matrix_graphs_adapter.py`**: Forensic Tier 0 inspection verified that `seen_axes: set[str] = set()` in `@[backend_v2/services/sdui/adapters/matrix_graphs_adapter.py#L36-L109]` was declared outside the `context.profile.matrix_synthesis_groups` iteration loop. When multiple matrix synthesis groups target overlapping prompt blocks, downstream groups are starved of axes and silently fail to emit graphs. The `seen_axes` set must be eliminated or scoped locally within each group so each visual group independently accesses its configured target blocks.
- **Missing Reorder Functionality in `MatrixGraphsBlockCard`**: `MatrixGraphsBlockCard` maps groups to a static `Column`. Users cannot change the display order of matrix groups within the card. Furthermore, line 83 executes `newGroups.indexOf(group)`, which relies on referential identity on `@Freezed(equal: false)` models.
- **Unselected Chip Lockout & Missing Radio Behavior in `MatrixGraphItemEditor`**: In 1D mode, selecting a block does not replace the active selection if existing data exceeded 1 block. When `targetBlocks.length >= maxSlots`, unselected chips remain enabled but unresponsive on click, causing user confusion.

### 6. Bilingual Prompt Directive Anti-Pattern & Seed Data Contamination
- **Bilingual System Prompts & Active `resolve_i18n` in `worker.py`**: In `OutputProfile` (`models/v2_core.py`, `models/dtos/output_profile.py`, and `output_profile.dart`), all 9 prompt directives (`tone_instruction`, `executive_summary_directive`, `matrix_1d_synthesis_directive`, `matrix_2d_synthesis_directive`, `matrix_3d_synthesis_directive`, `matrix_text_synthesis_directive`, `row_explanation_directive`, `xai_synthesis_directive`, `variance_synthesis_directive`) are still mistakenly typed as `I18nText | None`. Furthermore, forensic Tier 0 inspection verified that `backend_v2/worker.py` contains 6 active calls to `compiler.resolve_i18n` on prompt directives (lines 1067, 1081, 1139, 1206, 1248, 1379). This directly violates Rule `native_language_system_prompts` ("ALL system prompts MUST be strictly in English for maximum model instruction adherence") and Rule `cross_language_mapping_mandate` ("LLM rules MUST ALWAYS be defined in English and dynamically instructed to map against Localized Target Language source documents"). All 9 directives must be converted to plain English strings (`str | None`), and `worker.py` must access them directly via dot notation with zero `resolve_i18n` calls.
- **Seed Data Contamination (`seed_data.json` lines 18192–18245)**: In profile `prf_5d6e7f8091a2b3c4`, five directives (`executive_summary_directive`, `matrix_1d_synthesis_directive`, `matrix_2d_synthesis_directive`, `matrix_3d_synthesis_directive`, `matrix_text_synthesis_directive`) have duplicate English text copied into the `"fi"` key, while the remaining four (`tone_instruction`, `row_explanation_directive`, `xai_synthesis_directive`, `variance_synthesis_directive`) contain Finnish-translated prompt instructions. All 9 directives must be converted deterministically to clean English plain strings (`str`), completely purging the bilingual dictionary structure.
- **Studio UI Cognitive Clutter**: In Flutter Studio UI (`client_app_v2`), prompt directives were edited using `I18nTextField` widgets with language toggle tabs (FI / EN). This confuses coaches into believing they must author translated prompt instructions for the LLM. All prompt directives must be edited as clean, single-language English `TextFormField` inputs.

### 7. Discovered 7-Item Technical Debt & Negative Boundary Gaps (Scope & 1-Hop Caller Sweep)
- **Hardcoded Hint in `executive_summary_block_card.dart#L72`**: The input field hardcodes `'esim. 1000 merkkiä'` instead of binding `l10n.profileSynthesisLengthHint`, violating Rule `no_magic_strings_l10n`.
- **Fragile Referential Identity in `matrix_graphs_block_card.dart#L83,L95`**: `indexOf(group)` and `remove(group)` operate on `@Freezed(equal: false)` instances where Dart pointer equality can desynchronize or fail during rebuilds. They must be refactored to lookups by unique entity ID: `indexWhere((g) => g.id == group.id)` and `removeWhere((g) => g.id == group.id)`.
- **Unselected FilterChip Lockout in `matrix_graph_item_editor.dart#L215-L235`**: When `targetBlocks.length >= maxSlots`, unselected chips provide an active `onSelected` callback that silently discards user clicks. Unselected chips must have `onSelected: null` when quota is reached, providing native visual disabled cues while 1D mode provides instant single-select radio replacement.
- **Hardcoded Workflow ID Fallback in `output_profile_service.py#L182`**: `create_output_profile_draft` falls back to `'wf_9d68c573802341db'` if no workflows are returned, masking missing tenant setup. Must raise `AppException(ErrorCodes.RESOURCE_NOT_FOUND)` instead of papering over empty state.
- **Missing SSOT Constants for Length Constraints**: Default limits (1000, 250, 300, 500) are scattered as magic numbers across models. They must be anchored in SSOT constants (`SystemUiConstraints` in Flutter and `settings.py` / `output_profile_factory.py` in Python).
- **Missing ISTQB Negative Partitions for Length Budgeting & Cardinality**:
  - `length_budget_enforcer`: tests must explicitly verify: 1) inputs below limit (pass-through), 2) inputs at exact limit (pass-through), 3) inputs exceeding limit with terminal punctuation within 60% window (clean sentence trim), 4) inputs exceeding limit without terminal punctuation (first sentence preserved), 5) empty or whitespace-only strings (`AppException(ErrorCodes.VALIDATION_FAILED)`).
  - `MatrixSynthesisGroup` cardinality: negative test cases for 1D (0 and 2 blocks), 2D (1 and 3 blocks), 3D (2 and 4 blocks), and Text (0 blocks).
  - `OutputProfile` group ID uniqueness: negative test case with duplicate `MatrixSynthesisGroup.id` entries asserting `ValidationError`.

### 8. Acknowledged Technical Debt (Out-of-Scope for This Plan)
- **`worker.py` God File (1655 lines)**: `worker.py` exceeds the 300-line God File threshold per `ki_god_code_prevention.md`. This plan modifies it heavily (caller harmonization, Fail-Fast injection, budget injection) but does NOT decompose it. Decomposition is deferred to a dedicated future Epic.
- **Multi-Session Execution Budget**: This plan contains 9 execution steps × 5-15 sub-actions (60-90 discrete operations), exceeding the `context_amnesia_prevention` threshold. Mandatory `/tier5-session-handover` checkpoints are required between step batches: Steps 1-3, Steps 4-5, Steps 6-7, and Steps 8-9.

---

## Architectural Invariants & Key Findings

### 1. Option B Partitioning (Subpackage Sovereignty)
All prompt definitions reside exclusively within `backend_v2/models/prompts/` (SSOT), fulfilling the `prompt_asset_ssot_mandate`. They are physically separated into `common/`, `execution/`, and `synthesis/` subpackages according to the Tripartite Pipeline Architecture. The root `__init__.py` re-exports all public symbols so existing external imports remain operational without circular dependencies.

```
backend_v2/models/prompts/
├── __init__.py                     # Root barrel re-exporting all subpackages
├── common/                         # Cross-cutting foundational invariants
│   ├── __init__.py
│   ├── global_mandates.py          # Layer 1: Universal epistemic rules
│   ├── linguistic_directives.py    # Layer 4: Dynamic language context
│   └── field_prompts.py            # Layer 1/3: Pydantic field description strings
├── execution/                      # Phase 1: Heavy Execution, Sensors & Tools
│   ├── __init__.py
│   ├── matrix_evaluation.py        # Sensor Decision Engine & Contextual Override
│   ├── hook_prompts.py             # Execution hook directives (interaction detection)
│   └── mcp_prompts.py              # External evidence extraction & verification
└── synthesis/                      # Phase 2: Synthesis & Reporting
    ├── __init__.py
    ├── synthesis_directives.py     # Static system identity prompts & structural constants
    ├── style_directives.py         # Coaching tone & presentation posture
    └── sdui_directives.py          # SDUI block generation directives
```

### 2. Deduplication & Pure Epistemic Invariants
- `GLOBAL_MANDATES_XML` in `common/global_mandates.py` contains strictly Layer 1 epistemic invariants: Epistemic Glossary, Null Hypothesis, Verbatim Extraction, Semantic Bleed, Schema Purity, Anti-Score, Anti-ID, Context Segregation. `LANGUAGE_MANDATE` and `TONE_MANDATE` are permanently purged. It contains zero references to specific schema field names (`row_explanation`, `reasoning`), zero locale strings, and zero tone directives.
- `hook_prompts.py` is split along phase boundaries:
  - Lines 1-32 (`INTERACTION_OBJECTIVE`, `INTERACTION_RULES`) remain in `execution/hook_prompts.py`.
  - Lines 34-43 (`SYNTHESIS_XAI_CURATION`) and lines 45-52 (`SYNTHESIS_SECTION_RULES_PREFIX`) are relocated to `synthesis/synthesis_directives.py`.
  - Line 41 of `SYNTHESIS_XAI_CURATION` ("CRITICAL LANGUAGE MANDATE: All synthesized items MUST be generated in the <required_output_language>. Do NOT use English unless explicitly requested.") is stripped to eliminate duplicate language mandates.
- In `sdui_directives.py`, lines 26-27 (`USER_ROLE_EXTRACTION` and `ROLE TRANSLATION`) are purged, as role deduction belongs solely to `InteractionHook`.

### 3. Static Protocol Decoupling & FinOps Context Caching (`static_first_dynamic_last_topology`)
To maximize prefix-matching prompt cache hit rates (95%+ on Vertex AI Gemini 2.5, Anthropic Claude 3.5, and OpenAI) and prevent cache invalidation on multilingual requests:
- **Static Protocol Decoupling (`STATIC_LINGUISTIC_PROTOCOL`):** The complex linguistic behavioral mandate distinguishing hidden `reasoning_trace` from user-facing `reasoning`/`content` fields is 100% language-agnostic and contains zero f-strings:
  ```python
  STATIC_LINGUISTIC_PROTOCOL: str = (
      "<linguistic_mandate>\n"
      "- REASONING VS. OUTPUT LANGUAGE ISOLATION:\n"
      "  * The `<required_reasoning_language>` directive applies strictly to hidden internal thought traces (specifically `reasoning_trace`).\n"
      "  * ALL user-facing JSON string fields (specifically content blocks, xai_highlights, row_explanation, and atom evaluation `reasoning` / `semantic_reasoning` explanations) MUST be generated strictly in the language specified in `<required_output_language>`.\n"
      "  * Even when internal reasoning is conducted in English, NEVER emit English in user-facing fields unless `<required_output_language>` is 'en'.\n"
      "</linguistic_mandate>"
  )
  ```
- **Lightweight Dynamic Parameter Tail (`build_linguistic_parameters`):** Only dynamic parameter values (~10-15 tokens) are injected at the dynamic tail (Layer 4), decorated with `@functools.lru_cache(maxsize=32)` for token string determinism:
  ```python
  @functools.lru_cache(maxsize=32)
  def build_linguistic_parameters(
      target_locale: str,
      source_language: str = "Unknown/Original",
  ) -> str:
      """Return strictly the lightweight dynamic XML parameter block."""
      return (
          "<linguistic_parameters>\n"
          f"  <source_data_language>{source_language.strip()}</source_data_language>\n"
          f"  <required_output_language>{target_locale.strip().lower()}</required_output_language>\n"
          "  <required_reasoning_language>English</required_reasoning_language>\n"
          "</linguistic_parameters>"
      )
  ```
- **Heavy Source Document Cache Preservation:** Placing dynamic linguistic parameters strictly at the tail of the message payload (after `<context>{context_text}</context>`) ensures a massive 30,000-token source document remains 100% cached across executions even when generating multilingual reports.
- **Legacy Cleanup:** The legacy `include_mandate: bool = False` argument is eradicated across all callers.

### 4. Zero-Fallback Database Sovereignty & Factory Template Isolation
The database `OutputProfile` (`seed_data.json` / `db_v2.json`) is the **sole authoritative Single Source of Truth (SSOT)** for all 8 substantive directives, personas, and tones editable in Studio UI.
- In live runtime execution, `worker.py` derives prompt directives 100% dynamically from `active_profile_dto` via direct dot notation.
- `backend_v2/models/prompts/synthesis/synthesis_directives.py` contains strictly Layer 1 system prompt identities (`DEFAULT_SYNTHESIS_SYSTEM_PROMPT`, `DEFAULT_ROW_EXPLANATION_SYSTEM_PROMPT`, `DEFAULT_VARIANCE_SYSTEM_PROMPT`) and structural constants (`EXECUTIVE_SUMMARY_SECTION_ID`, `SYNTHESIS_SECTION_RULES_PREFIX`, `SYNTHESIS_XAI_CURATION`). It does NOT maintain duplicate substantive constants or runtime fallback lookups.
- `synthesis_registry.py` is permanently deleted. Zero code-level fallback dictionaries.
- Baseline templates for seeding and Studio "New Profile" creation are isolated in `backend_v2/services/factories/output_profile_factory.py`. They are used exclusively during profile initialization and are never invoked during runtime synthesis.

| Substantive Analytical Scope | Database `OutputProfile` Field (Studio UI) | Factory Seed Default (`output_profile_factory.py`) |
| :--- | :--- | :--- |
| High-level synthesis, systemic implications, and strategic advice. | `OutputProfile.executive_summary_directive` | `DEFAULT_FACTORY_EXECUTIVE_SUMMARY_DIRECTIVE` |
| Individual metric thresholds, isolated strengths, and anomalies. | `OutputProfile.matrix_1d_synthesis_directive` | `DEFAULT_FACTORY_MATRIX_1D_DIRECTIVE` |
| 2D quadrant comparisons, trade-offs, balance, and tensions. | `OutputProfile.matrix_2d_synthesis_directive` | `DEFAULT_FACTORY_MATRIX_2D_DIRECTIVE` |
| Holistic 3D radar profile, systemic center of gravity, vulnerabilities. | `OutputProfile.matrix_3d_synthesis_directive` | `DEFAULT_FACTORY_MATRIX_3D_DIRECTIVE` |
| Text-only cohesive analytical narrative and contextual explanations. | `OutputProfile.matrix_text_synthesis_directive` | `DEFAULT_FACTORY_MATRIX_TEXT_DIRECTIVE` |
| Matrix summary table causal score explanations (max 30 words, plain text). | `OutputProfile.row_explanation_directive` | `DEFAULT_FACTORY_ROW_EXPLANATION_DIRECTIVE` |
| Distillation of XAI extensions, risk flags, and coaching challenges. | `OutputProfile.xai_synthesis_directive` | `DEFAULT_FACTORY_XAI_DIRECTIVE` |
| Interpretation of Cognitive vs. Mechanical evaluation alignment. | `OutputProfile.variance_synthesis_directive` | `DEFAULT_FACTORY_VARIANCE_DIRECTIVE` |

### 5. Stripped-Down Purity Mandate, Centralized SDUI Block Structuring & Seed Vault Alignment

#### 5.1 Substantive Directives Purity & Centralized SDUI Presentation Invariant
- The 8 substantive directives must remain 100% stripped of technical formatting overhead. Redundant lines instructing "- Structure your findings directly as SDUI blocks.\n" are permanently purged.
- The requirement to structure findings as SDUI blocks is centralized as a universal presentation rule in `synthesis/sdui_directives.py` (`SYNTHESIS_SDUI_MANDATES`) and bound centrally in the static system prompt by `worker.py`. Domain coaches authoring prompts in Studio UI are never burdened with technical rendering instructions.
- `SYNTHESIS_SDUI_MANDATES` in `backend_v2/models/prompts/synthesis/sdui_directives.py` is purified to focus exclusively on allowed block discriminators (`paragraph`, `bullet_list`, `alert_box`, `quote_card`, `warning_card`), non-recursion, object structures for bullet lists, and citation arrays. Lines 26-27 (`USER_ROLE_EXTRACTION` and `ROLE TRANSLATION`) are purged.

#### 5.2 Database `output_profiles` Sanitization (`@[backend_v2/seed/seed_data.json]`)
To eradicate bilingual prompt directive confusion, enforce English-only prompt purity, resolve the Dual-Prompt Contradiction, and enforce De-Generator purity:

##### Exact Line-Guided Deterministic Pruning Map (`seed_data.json` in `prf_5d6e7f8091a2b3c4`)
In `backend_v2/seed/seed_data.json`, target document `prf_5d6e7f8091a2b3c4` in the `output_profiles` collection across **exact lines 18192–18245**:

| Field Name | Current Line Span | Current Structure | Target Sanitized Structure (Plain English `str`) |
| :--- | :--- | :--- | :--- |
| `tone_instruction` | Lines 18192–18196 | Bilingual `{"translations": {"en": "...", "fi": "..."}}` | Plain English `str`: `"Act as a Senior Executive Coach. Provide deep, provocative, and strategic analysis rather than merely listing data."` |
| `executive_summary_directive` | Lines 18198–18203 | Bilingual with `"using SDUI ParagraphBlocks."` | Plain English `str` with normalized narrative: `"EXECUTIVE SUMMARY SYNTHESIS MANDATE:\n- Synthesize the high-level findings, systemic implications, and strategic executive coaching advice.\n- Structure the narrative into clear, logical paragraphs.\n- Reference key strengths, vulnerabilities, and strategic focus areas from the evaluated data."` |
| `matrix_1d_synthesis_directive` | Lines 18204–18209 | Bilingual with `"- Structure your findings directly as SDUI blocks."` | Plain English `str` with SDUI boilerplate purged: `"1D METRICS SYNTHESIS MANDATE:\n- Focus on individual metric thresholds, isolated strengths, and isolated anomalies.\n- Provide clear, concise analytical takeaway for each evaluated dimension."` |
| `matrix_2d_synthesis_directive` | Lines 18210–18215 | Bilingual with `"- Structure your findings directly as SDUI blocks."` | Plain English `str` with SDUI boilerplate purged: `"2D COMPARISON SYNTHESIS MANDATE:\n- Analyze the cross-dimensional interactions, trade-offs, and tensions between the two evaluated axes.\n- Identify systemic correlations, divergence points, and strategic balance."` |
| `matrix_3d_synthesis_directive` | Lines 18216–18221 | Bilingual with `"- Structure your findings directly as SDUI blocks."` | Plain English `str` with SDUI boilerplate purged: `"3D RADAR SYNTHESIS MANDATE:\n- Provide a holistic multi-dimensional synthesis across all evaluated dimensions in the radar geometry.\n- Synthesize macro patterns, capability imbalances, and systemic maturity."` |
| `matrix_text_synthesis_directive` | Lines 18222–18227 | Bilingual with `"- Structure your findings directly as SDUI blocks."` | Plain English `str` with SDUI boilerplate purged: `"TEXT SYNTHESIS MANDATE:\n- Formulate a narrative, qualitative deep-dive synthesis based on the textual evidence and qualitative observations.\n- Highlight nuances, contextual subtleties, and qualitative coaching takeaways."` |
| `row_explanation_directive` | Lines 18228–18233 | Bilingual with Finnish translation lines 18231–18232 | Plain English `str`: `"ROW EXPLANATION SYNTHESIS MANDATE:\n- Formulate a clear, concise causal explanation for the score assigned to each evaluated matrix row.\n- Ground the explanation directly in the verified quotes and concrete textual evidence.\n- Explain why the score is justified based on the presence or absence of core criteria."` |
| `xai_synthesis_directive` | Lines 18234–18239 | Bilingual with Finnish translation and SDUI boilerplate | Plain English `str`: `"XAI EXTENSIONS SYNTHESIS MANDATE:\n- Synthesize explainable AI highlights, diagnostic extensions, and remediation recommendations.\n- Highlight actionable development points, key risks, and concrete next steps."` |
| `variance_synthesis_directive` | Lines 18240–18245 | Bilingual with Finnish translation lines 18243–18244 | Plain English `str`: `"VARIANCE EVALUATION SYNTHESIS MANDATE:\n- Evaluate the cognitive variance, performativity risk, and authenticity of the analyzed text.\n- Assess whether responses reflect authentic cognitive reasoning versus performative keyword compliance.\n- Provide an objective summary of linguistic signals and authenticity scores."` |

##### Deterministic Sanitization Delta (Lines 18192–18245)
```diff
-      "tone_instruction": {
-        "translations": {
-          "en": "Act as a Senior Executive Coach. Provide deep, provocative, and strategic analysis rather than merely listing data.",
-          "fi": "Toimi ylemmän johdon valmentajana (Senior Executive Coach). Tarjoa syvällistä, provosoivaa ja strategista analyysiä pelkän datan luettelemisen sijaan."
-        }
-      },
-      "executive_summary_directive": {
-        "translations": {
-          "en": "EXECUTIVE SUMMARY SYNTHESIS MANDATE:\n- Synthesize the high-level findings, systemic implications, and strategic executive coaching advice.\n- Structure the narrative into clear, logical paragraphs using SDUI ParagraphBlocks.\n- Reference key strengths, vulnerabilities, and strategic focus areas from the evaluated data.",
-          "fi": "EXECUTIVE SUMMARY SYNTHESIS MANDATE:\n- Synthesize the high-level findings, systemic implications, and strategic executive coaching advice.\n- Structure the narrative into clear, logical paragraphs using SDUI ParagraphBlocks.\n- Reference key strengths, vulnerabilities, and strategic focus areas from the evaluated data."
-        }
-      },
-      "matrix_1d_synthesis_directive": {
-        "translations": {
-          "en": "1D METRICS SYNTHESIS MANDATE:\n- Focus on individual metric thresholds, isolated strengths, and isolated anomalies.\n- Provide clear, concise analytical takeaway for each evaluated dimension.\n- Structure your findings directly as SDUI blocks.",
-          "fi": "1D METRICS SYNTHESIS MANDATE:\n- Focus on individual metric thresholds, isolated strengths, and isolated anomalies.\n- Provide clear, concise analytical takeaway for each evaluated dimension.\n- Structure your findings directly as SDUI blocks."
-        }
-      },
-      "matrix_2d_synthesis_directive": {
-        "translations": {
-          "en": "2D COMPARISON SYNTHESIS MANDATE:\n- Analyze the cross-dimensional interactions, trade-offs, and tensions between the two evaluated axes.\n- Identify systemic correlations, divergence points, and strategic balance.\n- Structure your findings directly as SDUI blocks.",
-          "fi": "2D COMPARISON SYNTHESIS MANDATE:\n- Analyze the cross-dimensional interactions, trade-offs, and tensions between the two evaluated axes.\n- Identify systemic correlations, divergence points, and strategic balance.\n- Structure your findings directly as SDUI blocks."
-        }
-      },
-      "matrix_3d_synthesis_directive": {
-        "translations": {
-          "en": "3D RADAR SYNTHESIS MANDATE:\n- Provide a holistic multi-dimensional synthesis across all evaluated dimensions in the radar geometry.\n- Synthesize macro patterns, capability imbalances, and systemic maturity.\n- Structure your findings directly as SDUI blocks.",
-          "fi": "3D RADAR SYNTHESIS MANDATE:\n- Provide a holistic multi-dimensional synthesis across all evaluated dimensions in the radar geometry.\n- Synthesize macro patterns, capability imbalances, and systemic maturity.\n- Structure your findings directly as SDUI blocks."
-        }
-      },
-      "matrix_text_synthesis_directive": {
-        "translations": {
-          "en": "TEXT SYNTHESIS MANDATE:\n- Formulate a narrative, qualitative deep-dive synthesis based on the textual evidence and qualitative observations.\n- Highlight nuances, contextual subtleties, and qualitative coaching takeaways.\n- Structure your findings directly as SDUI blocks.",
-          "fi": "TEXT SYNTHESIS MANDATE:\n- Formulate a narrative, qualitative deep-dive synthesis based on the textual evidence and qualitative observations.\n- Highlight nuances, contextual subtleties, and qualitative coaching takeaways.\n- Structure your findings directly as SDUI blocks."
-        }
-      },
-      "row_explanation_directive": {
-        "translations": {
-          "en": "ROW EXPLANATION SYNTHESIS MANDATE:\n- Formulate a clear, concise causal explanation for the score assigned to each evaluated matrix row.\n- Ground the explanation directly in the verified quotes and concrete textual evidence.\n- Explain why the score is justified based on the presence or absence of core criteria.",
-          "fi": "RIVIRAPORTOINNIN OHJEISTUS:\n- Muotoile selkeä ja tiivis kausaalinen perustelu kullekin arvioidulle matriisiriville annetulle pisteytykselle.\n- Ankkuroi selitys suoraan todennettuihin lainauksiin ja konkreettiseen tekstinäyttöön.\n- Selitä miksi pistemäärä on perusteltu ydinkriteerien täyttymisen tai puuttumisen perusteella."
-        }
-      },
-      "xai_synthesis_directive": {
-        "translations": {
-          "en": "XAI EXTENSIONS SYNTHESIS MANDATE:\n- Synthesize explainable AI highlights, diagnostic extensions, and remediation recommendations.\n- Highlight actionable development points, key risks, and concrete next steps.\n- Structure your findings directly as SDUI blocks.",
-          "fi": "XAI-LAAJENNUSTEN OHJEISTUS:\n- Tiivistä selitettävän tekoälyn (XAI) kohokohdat, diagnostiset laajennukset ja kehityssuositukset.\n- Korosta konkreettisia kehityskohteita, keskeisiä riskejä ja suositeltavia toimenpiteitä.\n- Muotoile löydökset suoraan SDUI-lohkoina."
-        }
-      },
-      "variance_synthesis_directive": {
-        "translations": {
-          "en": "VARIANCE EVALUATION SYNTHESIS MANDATE:\n- Evaluate the cognitive variance, performativity risk, and authenticity of the analyzed text.\n- Assess whether responses reflect authentic cognitive reasoning versus performative keyword compliance.\n- Provide an objective summary of linguistic signals and authenticity scores.",
-          "fi": "VARIANSSIN JA AITOUDEN ARVIOINTIOHJE:\n- Arvioi analysoidun tekstin kognitiivista varianssia, performatiivisuusriskiä ja aitoutta.\n- Analysoi heijastavatko vastaukset aitoa kognitiivista päättelyä vai pelkkää mekaanista avainsanojen toistoa.\n- Tarjoa objektiivinen tiivistelmä kielellisistä signaaleista ja aitouspisteistä."
-        }
-      },
+      "tone_instruction": "Act as a Senior Executive Coach. Provide deep, provocative, and strategic analysis rather than merely listing data.",
+      "executive_summary_directive": "EXECUTIVE SUMMARY SYNTHESIS MANDATE:\n- Synthesize the high-level findings, systemic implications, and strategic executive coaching advice.\n- Structure the narrative into clear, logical paragraphs.\n- Reference key strengths, vulnerabilities, and strategic focus areas from the evaluated data.",
+      "matrix_1d_synthesis_directive": "1D METRICS SYNTHESIS MANDATE:\n- Focus on individual metric thresholds, isolated strengths, and isolated anomalies.\n- Provide clear, concise analytical takeaway for each evaluated dimension.",
+      "matrix_2d_synthesis_directive": "2D COMPARISON SYNTHESIS MANDATE:\n- Analyze the cross-dimensional interactions, trade-offs, and tensions between the two evaluated axes.\n- Identify systemic correlations, divergence points, and strategic balance.",
+      "matrix_3d_synthesis_directive": "3D RADAR SYNTHESIS MANDATE:\n- Provide a holistic multi-dimensional synthesis across all evaluated dimensions in the radar geometry.\n- Synthesize macro patterns, capability imbalances, and systemic maturity.",
+      "matrix_text_synthesis_directive": "TEXT SYNTHESIS MANDATE:\n- Formulate a narrative, qualitative deep-dive synthesis based on the textual evidence and qualitative observations.\n- Highlight nuances, contextual subtleties, and qualitative coaching takeaways.",
+      "row_explanation_directive": "ROW EXPLANATION SYNTHESIS MANDATE:\n- Formulate a clear, concise causal explanation for the score assigned to each evaluated matrix row.\n- Ground the explanation directly in the verified quotes and concrete textual evidence.\n- Explain why the score is justified based on the presence or absence of core criteria.",
+      "xai_synthesis_directive": "XAI EXTENSIONS SYNTHESIS MANDATE:\n- Synthesize explainable AI highlights, diagnostic extensions, and remediation recommendations.\n- Highlight actionable development points, key risks, and concrete next steps.",
+      "variance_synthesis_directive": "VARIANCE EVALUATION SYNTHESIS MANDATE:\n- Evaluate the cognitive variance, performativity risk, and authenticity of the analyzed text.\n- Assess whether responses reflect authentic cognitive reasoning versus performative keyword compliance.\n- Provide an objective summary of linguistic signals and authenticity scores.",
```

##### Additional Seed Vault Sanitizations
- **Matrix Synthesis Groups view_type Correction**: Lines 18289–18331 in `seed_data.json` (groups `grp_440a5fef9331451b`, `grp_c5804a9143c34cb1`, `grp_6b8c766185294f7e`): Update `view_type` from `"1d_metrics"` to `"2d_compare"` because each group contains exactly 2 target blocks.
- **Orphan block `blk_eeea566da4ab45f9`**: Line 16756 (`blk_synthesis_global_rules`) in `prompt_blocks`: Sanitize or prune legacy V1 class names and corrupted XML fragments.
- **Seed Data Vault Protocol (`03_seed_vault.md`) Verification Gates**:
  1. Timestamped backup copy stored inside `backend_v2/seed/backups/`.
  2. In-memory pre-flight validation: `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict`.
  3. Parity test verification: `uv run pytest backend_v2/tests/unit/services/test_output_profile_studio_parity.py -v`.
  4. Local database re-seed synchronization: `uv run python backend_v2/seed/run_seed.py local`.

### 6. Strict Fail-Fast Ingress Validation (Zero Compromise Mandate)
In accordance with `zero_service_layer_fallbacks` and `the_zero_compromise_pledge`:
1. **Model Validation**: `OutputProfile` (`backend_v2/models/v2_core.py`) enforces cross-field completeness via `@model_validator(mode="after")`. If a block type is declared in `target_block_order`, its corresponding directive field must be populated and non-empty.
2. **Worker Pipeline Fail-Fast**: When `worker.py` compiles synthesis tasks, it accesses directives directly from `active_profile_dto`. If a required directive is missing or empty, it logs a structured error and immediately raises `AppException(ErrorCodes.OUTPUT_PROFILE_INCOMPLETE, f"Directive for active block '{block_type}' is missing in OutputProfile '{profile_id}'")`.
3. **Zero Fallback Chains**: Code never guesses, falls back, or substitutes degraded prompts silently.

### 7. Studio UI Directive Partitioning & 1:1 Parity Contract

#### 7.1 Separation of 1:1 Section Directives vs Multi-Instance View Type Directives
In the Flutter Studio UI (`client_app_v2`), prompt directive editors are strictly partitioned according to their structural relationship to the generated report:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        STUDIO UI DIRECTIVE ALLOCATION CONTRACT                         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [TAB 3: SECTION CONFIGURATION (ProfileSectionConfigTab) - 1:1 SECTION PARITY]         │
│  • Executive Summary Block Card      --> executive_summary_directive (TextFormField EN)│
│                                          synthesis_length_constraint (numeric chars)   │
│  • Matrix Summary Table Card         --> row_explanation_directive (TextFormField EN)  │
│                                          row_explanation_length_constraint (numeric)   │
│  • XAI Highlights & Extensions Card  --> xai_synthesis_directive (TextFormField EN)    │
│                                          xai_length_constraint (numeric chars)         │
│  • Variance Validation Card          --> variance_synthesis_directive (TextFormField EN│
│                                          variance_length_constraint (numeric chars)    │
│  * Invariant: Each directive & its length budget is edited directly inside its card.   │
│    Directives are English-only text inputs; bilingual tabs are completely removed.     │
│                                                                                        │
│  [TAB 1: GENERAL & TONE (ProfileGeneralTab) - REUSABLE VIEW TYPES & PERSONA]           │
│  • Card 1 (Profile Identity)         --> id, slug, workflow_id                         │
│  • Card 2 (General & Persona Tone)   --> target_locale,                                │
│                                          tone_instruction (TextFormField EN),          │
│                                          user_role_label (I18nTextField),              │
│                                          custom_preface (I18nTextField)                │
│  • Card 3 (Matrix View Type Rules)   --> matrix_1d_synthesis_directive (TextForm EN)   │
│                                          matrix_2d_synthesis_directive (TextForm EN)   │
│                                          matrix_3d_synthesis_directive (TextForm EN)   │
│                                          matrix_text_synthesis_directive (TextForm EN) │
│  * Invariant: 1D, 2D, 3D, and Text govern analytical view types that can occur         │
│    multiple times sequentially in matrix_synthesis_groups (specifically 3 consecutive  │
│    2D quadrant graphs). They belong in Tab 1 as global reusable view type rules.       │
│    All prompt directives are single-language English text fields.                      │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### 7.2 Pruning Duplicated 1:1 Directives from Tab 1 & Removing Bilingual Tabs
- In `client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart`:
  - Prune `executiveSummaryDirective` (lines 279-292).
  - Prune `rowExplanationDirective` (lines 354-367).
  - Prune `xaiSynthesisDirective` (lines 369-382).
  - Prune `varianceSynthesisDirective` (lines 384-397).
- Retitle Card 3 from generic `profileAiSynthesisDirectivesTitle` ("AI Synthesis Directives") to `profileMatrixViewDirectivesTitle` ("Matrix View Type Synthesis Directives" / "Matriisinäkymien synteesiohjeet").
- Retain exclusively the 4 reusable view type directives in Card 3: `matrix1dSynthesisDirective`, `matrix2dSynthesisDirective`, `matrix3dSynthesisDirective`, and `matrixTextSynthesisDirective`.
- Replace `I18nTextField` widgets with standard multiline `TextFormField` widgets (with `OutlineInputBorder()`) for `tone_instruction` and the 4 matrix view type directives. `user_role_label` and `custom_preface` remain `I18nTextField` because they are user-facing report presentation headers.
- Result: Eliminates duplicate input fields across tabs, removes misleading translation tabs for prompt instructions, enforces Single Responsibility UI editing, and guarantees that coaches author prompt instructions strictly in English.

### 8. Dual-Axis Localization & English-Only Directive Protocol (Dual-Axis SSOT)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   DUAL-AXIS LOCALIZATION & ENGLISH-ONLY DIRECTIVE PROTOCOL             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  AXIS 1: HUMAN USER PRESENTATION (Bilingual via I18nText & I18nTextField)              │
│  • Target Fields: OutputProfile.name, description, user_role_label, custom_preface     │
│  • Audience: End-user human readers inspecting the UI and generated PDF reports.       │
│  • Behavior: Rendered directly on document cover pages and report section headers.     │
│  • Persistence: Stored as I18nText (dictionary of {'en': '...', 'fi': '...'}).         │
│  • UI Editor: I18nTextField with language switcher tabs (FI / EN).                     │
│                                                                                        │
│  AXIS 2: LLM MACHINE INSTRUCTION (Strictly English Plain String: str | None)           │
│  • Target Fields: tone_instruction, executive_summary_directive,                       │
│    matrix_1d_synthesis_directive, matrix_2d_synthesis_directive,                      │
│    matrix_3d_synthesis_directive, matrix_text_synthesis_directive,                     │
│    row_explanation_directive, xai_synthesis_directive, variance_synthesis_directive    │
│  • Audience: Foundational Large Language Models (Gemini 2.5, Claude 3.5, GPT-4o).      │
│  • Mandate: Defined EXCLUSIVELY in English for maximum model instruction adherence     │
│    (Rules native_language_system_prompts and cross_language_mapping_mandate).          │
│  • Persistence: Stored as clean str (or null) in database OutputProfile.               │
│  • UI Editor: Standard single-language English TextFormField (zero language tabs).     │
│                                                                                        │
│  DYNAMIC RUNTIME TARGET LANGUAGE ENFORCEMENT (Layer 4 Tail)                            │
│  • worker.py reads directives directly via dot notation:                               │
│    exec_directive = active_profile_dto.executive_summary_directive  (NO resolve_i18n!) │
│  • Target language is instructed strictly at prompt tail via build_linguistic_params:  │
│      <linguistic_parameters>                                                          │
│        <source_data_language>{source_lang}</source_data_language>                     │
│        <required_output_language>{target_locale}</required_output_language>           │
│        <required_reasoning_language>English</required_reasoning_language>             │
│      </linguistic_parameters>                                                         │
│  • STATIC_LINGUISTIC_PROTOCOL (Layer 1 cacheable prefix) commands the LLM in English   │
│    to generate all user-facing JSON content fields strictly in                        │
│    <required_output_language>, while keeping internal thought traces in English.       │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 9. Four-Tier Anti-Repetition Guarantee
```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FOUR-TIER ANTI-REPETITION GUARANTEE                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [TIER 1: SSOT PURIFICATION]                                            │
│  • Strip LANGUAGE_MANDATE from GLOBAL_MANDATES_XML (move to Layer 4)    │
│  • Strip TONE_MANDATE from GLOBAL_MANDATES_XML (move to Layer 2 Style)  │
│  • Result: Layer 1 contains ONLY universal epistemic invariants.        │
│                                                                         │
│  [TIER 2: FOUR-LAYER CLEAN STACK ASSEMBLY CONTRACT]                     │
│  • Layer 1 (System Prefix): ONLY static epistemic rules                 │
│  • Layer 2 (Presentation Style): ONLY tone & SDUI rules (Synthesis)     │
│  • Layer 3 (Task Directives): ONLY substantive analysis (Matrix/Syn)    │
│  • Layer 4 (Dynamic Tail): ONLY input data & build_linguistic_parameters│
│                                                                         │
│  [TIER 3: BUILDER & PROMPTCOMPILER DEDUPLICATION]                       │
│  • Remove include_mandate flag across all builders                      │
│  • Replace manual f-string concats with deduplicated Assembly Lists     │
│  • Automated set()-based section key enforcement in PromptCompiler      │
│                                                                         │
│  [TIER 4: AUTOMATED AST GUARDRAILS & FAIL-FAST REGRESSION TESTS]        │
│  • Unique XML Tag AST Guardrail (fails if <global_system_mandates> or   │
│    <coaching_tone_mandate> appears >1 time in assembled prompt)         │
│  • Forbidden Substring Test (fails if GLOBAL_MANDATES_XML contains DTO  │
│    field names row_explanation, reasoning, or locale names)            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10. AST Import Firewall & XML Sovereignty
- Phase 1 callers (`matrix_sensor_prompt_builder.py`, `dag_executor.py`, `extractive_sensor_service.py`) must never import from `backend_v2.models.prompts.synthesis`.
- Phase 2 callers (`worker.py`, synthesis adapters) must never import from `backend_v2.models.prompts.execution`.
- Top-level XML tags (`<global_system_mandates>`, `<linguistic_context>`, `<coaching_tone_mandate>`) must appear exactly once per compiled request payload.
- `test_global_mandates.py` asserts that `GLOBAL_MANDATES_XML` contains zero locale names, zero field names (`row_explanation`), and zero tone mandates.
- AST guardrail asserting that `DESC_TRANSLATION_MANDATE` does not appear in any `.py` file under `backend_v2/models/dtos/` (enforcing zero linguistic prompt pollution in schema models).

### 11. Two-Tier SSOT Length Budgeting & Sentence Boundary Preservation Engine

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   TWO-TIER SSOT LENGTH BUDGETING ARCHITECTURE                          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [TIER 1: PROMPT BUDGET INSTRUCTION (Layer 4 Dynamic Tail)]                            │
│  • Dynamically injects <section_budget> into the user message context:                 │
│      <section_budget>                                                                  │
│        <max_length_chars>{limit}</max_length_chars>                                    │
│        <budget_mandate>Conclude all analysis within this character budget.             │
│        Ensure all thoughts are expressed in complete, grammatically sound              │
│        sentences. Do NOT leave incomplete thoughts or truncated sentences.</budget>    │
│      </section_budget>                                                                 │
│  • Preserves 100% of static system prompt prefix caching across all executions.         │
│                                                                                        │
│  [TIER 2: DETERMINISTIC SENTENCE BOUNDARY ENFORCEMENT (Fail-Safe Guardrail)]           │
│  • Module: backend_v2/services/length_budget_enforcer.py                               │
│  • Function: enforce_sentence_boundary_budget(text: str, max_chars: int) -> str        │
│  • Logic:                                                                              │
│    1. If len(text) <= max_chars: return text unmodified.                               │
│    2. If len(text) > max_chars: scan backwards from max_chars to locate the nearest    │
│       terminal punctuation (specifically: '.', '!', '?').                              │
│    3. If a terminal sentence boundary exists >= max_chars * 0.6: trim cleanly at that  │
│       boundary, preserving complete sentence semantics.                                │
│    4. If no sentence boundary exists in that window: retain the first complete         │
│       sentence intact and emit a structured warning. NEVER slice words mid-sentence.   │
│                                                                                        │
│  [SSOT OUTPUTPROFILE SCHEMA CONTRACT]                                                  │
│  • synthesis_length_constraint: int | None (Executive Summary, default 1000)           │
│  • row_explanation_length_constraint: int | None (Matrix Table Row, default 250)       │
│  • xai_length_constraint: int | None (XAI Highlight Item, default 300)                 │
│  • variance_length_constraint: int | None (Variance Explanation, default 500)          │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 12. SDUI Formatting Instruction Purification & Schema Clash Prevention
- **Rejection of User-Facing SDUI Toggles**: Toggling `"- Structure your findings directly as SDUI blocks."` on non-SDUI sections (`row_explanation`, `xai_highlights`, `variance_explanation`) induces fatal schema collisions. The LLM attempts to generate block dictionaries into plain-string Pydantic fields, causing instant `ValidationError` crashes.
- **Architectural Separation of Concerns**:
  - Directives in `OutputProfile` contain purely substantive coaching and analytical instructions (Layer 3).
  - Technical serialization rules (`SYNTHESIS_SDUI_MANDATES` in `sdui_directives.py`) reside strictly in Layer 2 and are bound automatically by the orchestrator exclusively for tasks returning polymorphic `list[LlmSduiBlock]`.
  - For sections returning plain strings, the system instructions enforce concise causal prose without SDUI block overhead.

### 13. Matrix Synthesis Group Dimensional Cardinality, Database Order Persistence & Dumb Screen Protocol

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│             MATRIX SYNTHESIS GROUP DIMENSIONAL CARDINALITY & DUMB SCREEN PROTOCOL       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [DIMENSIONAL CARDINALITY INVARIANTS]                                                  │
│  • 1D Metrics (1d_metrics): Exactly 1 target block (len(target_blocks) == 1).           │
│  • 2D Compare (2d_compare): Exactly 2 target blocks (len(target_blocks) == 2).          │
│  • 3D Radar (3d_matrix): Exactly and strictly 3 target blocks (len(target_blocks) == 3).│
│  • Text Only (text_only): At least 1 target block (len(target_blocks) >= 1).           │
│                                                                                        │
│  [BACKEND VALIDATION SOVEREIGNTY (SSOT)]                                               │
│  • MatrixSynthesisGroup enforces @model_validator(mode="after") raising ValueError     │
│    if cardinality is violated. Handled as AppException(ErrorCodes.VALIDATION_FAILED).  │
│  • OutputProfile enforces unique group IDs across matrix_synthesis_groups.             │
│  • StudioOutputProfileService.create_output_profile_draft binds output_profile_factory  │
│    so headless API draft creation produces complete, runnable profiles immediately.    │
│                                                                                        │
│  [DATABASE ARRAY ORDER PERSISTENCE]                                                    │
│  • OutputProfile stores matrix_synthesis_groups as a native BSON/JSON array.           │
│  • The array index [0, 1, 2, ...] is the Single Source of Truth for display order.     │
│  • Zero redundant "order" integer fields. Preserves universal_ssot_mandate.            │
│                                                                                        │
│  [DUMB PAINTER SDUI ARCHITECTURE]                                                      │
│  • MatrixGraphsAdapter.build() iterates matrix_synthesis_groups in database order.     │
│  • Eliminates seen_axes [RESOLVED] so groups independently access their configured target blocks. │
│  • Client ReportView paints AnySduiBlock stream in exact delivered order. Zero logic.  │
│                                                                                        │
│  [DUMB STUDIO EDITOR]                                                                  │
│  • MatrixGraphsBlockCard renders ReorderableListView with drag handles and Up/Down     │
│    IconButton controls for single-click desktop precision.                             │
│  • Mutates payload.copyWith(matrixSynthesisGroups: reorderedList) on list swap.       │
│  • MatrixGraphItemEditor implements single-select radio replacement for 1D mode,       │
│    disables unselected chips when quota is reached. BANS client-side auto-clamping.    │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### 13.1 Backend Cardinality & Group ID Uniqueness Validation (@model_validator SSOT)
In accordance with `the_zero_compromise_pledge` and `universal_fail_fast`, all structural guarantees for matrix synthesis groups are enforced strictly on the backend domain models in `backend_v2/models/v2_core.py`:

1. **Dimensional Cardinality Enforcement (`MatrixSynthesisGroup`)**:
   `MatrixSynthesisGroup` enforces strict mathematical coupling between `view_type` and `target_blocks`:
   ```python
   @model_validator(mode="after")
   def validate_dimensional_cardinality(self) -> Self:
       """Enforce strict dimensional cardinality coupling between view_type and target_blocks."""
       num_blocks = len(self.target_blocks)
       # LaxPresetView coerces strings to PresetView before @model_validator runs.
       if self.view_type == PresetView.METRICS_1D:
           if num_blocks != 1:
               msg = (
                   f"MatrixSynthesisGroup '{self.id}': view_type '1d_metrics' requires exactly 1 target block, "
                   f"but received {num_blocks} ({self.target_blocks})."
               )
               logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
               raise ValueError(msg)
       elif self.view_type == PresetView.COMPARE_2D:
           if num_blocks != 2:
               msg = (
                   f"MatrixSynthesisGroup '{self.id}': view_type '2d_compare' requires exactly 2 target block, "
                   f"but received {num_blocks} ({self.target_blocks})."
               )
               logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
               raise ValueError(msg)
       elif self.view_type == PresetView.MATRIX_3D:
           if num_blocks != 3:
               msg = (
                   f"MatrixSynthesisGroup '{self.id}': view_type '3d_matrix' requires exactly 3 target block, "
                   f"but received {num_blocks} ({self.target_blocks})."
               )
               logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
               raise ValueError(msg)
       elif self.view_type == PresetView.TEXT_ONLY:
           if num_blocks < 1:
               msg = (
                   f"MatrixSynthesisGroup '{self.id}': view_type 'text_only' requires at least 1 target block, "
                   f"but received {num_blocks}."
               )
               logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
               raise ValueError(msg)
       return self
   ```

2. **Group ID Uniqueness Enforcement (`OutputProfile`)**:
   `OutputProfile` enforces that all group IDs within `matrix_synthesis_groups` are strictly distinct, preventing headless API callers from introducing duplicate IDs:
   ```python
   @model_validator(mode="after")
   def validate_matrix_group_ids_unique(self) -> Self:
       """Enforce that all MatrixSynthesisGroup IDs in matrix_synthesis_groups are strictly unique."""
       seen_ids: set[str] = set()
       duplicate_ids: list[str] = []
       for grp in self.matrix_synthesis_groups:
           if grp.id in seen_ids:
               duplicate_ids.append(grp.id)
           seen_ids.add(grp.id)
       if duplicate_ids:
           msg = (
               f"OutputProfile '{self.id}': Duplicate synthesis group IDs detected in "
               f"matrix_synthesis_groups: {duplicate_ids}. All group IDs must be strictly unique."
           )
           logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
           raise ValueError(msg)
       return self
   ```

#### 13.2 Headless API Sovereignty & Factory Draft Binding (`create_output_profile_draft`)
To guarantee that profiles created headlessly via REST API (or automation scripts) are 100% valid and runnable out-of-the-box without requiring any interaction in the Flutter UI:
- `backend_v2/services/factories/output_profile_factory.py` provides `build_draft_output_profile(...)`:
  ```python
  def build_draft_output_profile(
      profile_id: str,
      workflow_id: str,
      organization_id: str | None = None,
  ) -> OutputProfile:
      """Build a fully populated, runnable OutputProfile draft for headless API and Studio creation."""
      ...
  ```
- In `backend_v2/services/studio/output_profile_service.py`, `create_output_profile_draft` is updated from instantiating an incomplete skeleton to directly binding `output_profile_factory.build_draft_output_profile`:
  ```python
  async def create_output_profile_draft(self, initiator: TokenData) -> OutputProfile:
      workflows = await self.workflow_service.list_workflows(initiator)
      if not workflows:
          msg = f"No workflows available to associate with new OutputProfile for organization '{initiator.organization_id}'."
          logger.error("[StudioOutputProfileService] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
          raise ResourceNotFoundError(resource_type="workflow", resource_id="primary_default")
      target_wf_id = workflows[0].id
      new_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
      if initiator.role == UserRole.ROOT:
          target_org = SystemOrganizations.ROOT_SYSTEM
      else:
          target_org = initiator.organization_id

      draft = build_draft_output_profile(
          profile_id=new_id,
          workflow_id=target_wf_id,
          organization_id=target_org,
      )
      return await self.save_output_profile(initiator, new_id, draft)
  ```
- **Guaranteed Draft Contents**:
  - All 8 substantive directives populated with valid default English `str` strings.
  - All 4 section length constraints populated with default integer values (`synthesis_length_constraint=1000`, `row_explanation_length_constraint=250`, `xai_length_constraint=300`, `variance_length_constraint=500`).
  - An initial valid `MatrixSynthesisGroup` with unique opaque ID conforming to dimensional cardinality.
  - Complete `target_block_order` covering standard executive reporting sections.
- **Headless Runnable Contract**: Any profile created via `POST /api/v2/studio/profiles/draft` is instantly ready for runtime synthesis; calling synthesis immediately succeeds without `OUTPUT_PROFILE_INCOMPLETE`.

#### 13.3 Absolute Ban on Client-Side "Auto-Clamping on Load" & Dumb Screen Protocol
- **The Ban**: Flutter widgets (`matrix_graph_item_editor.dart`, `matrix_graphs_block_card.dart`) are STRICTLY FORBIDDEN from performing any "auto-clamp on load", silent truncation, or heuristic data scrubbing in `initState`, `didChangeDependencies`, `didUpdateWidget`, or `build`.
- **Architectural Rationale**: Auto-clamping papers over database corruption, causes unexpected state divergence between client and server, violates CQRS, and fails to protect headless API clients.
- **Strict Separation of Concerns**:
  1. **Quality Assurance (Backend)**: Locked exclusively in backend `@model_validator(mode="after")` and database seed sanitization (`seed_data.json`). If invalid data exists, backend fails fast with `AppException(ErrorCodes.VALIDATION_FAILED)`.
  2. **Dumb Display (Frontend)**: The UI renders the exact target blocks delivered by the DTO.
  3. **Interactive Affordances (Frontend)**:
     - In **1D Metrics mode**, selecting a new block replaces the previous single selection (radio button behavior).
     - In **2D Compare / 3D Radar modes**, when the exact quota is reached (`targetBlocks.length >= maxSlots`), unselected FilterChips are disabled (`onSelected: null`), preventing invalid additions before deselection.
     - Zero client-side data scrubbing on load.

#### 13.4 Database Array Order SSOT & Intra-Block Reordering UI (`ReorderableListView` + Up/Down Controls)
- **Database Sequence as SSOT**: In MongoDB and Pydantic V2, the JSON array sequence of `OutputProfile.matrix_synthesis_groups` (`[grp_0, grp_1, grp_2, ...]`) is the authoritative Single Source of Truth for display order. No redundant `order: int` integer field is maintained, upholding the `universal_ssot_and_normalization_mandate`.
- **Dumb Painter SDUI Execution**: `MatrixGraphsAdapter.build()` iterates `matrix_synthesis_groups` strictly in document array order, emitting corresponding `AnySduiBlock` items sequentially. The client `ReportView` paints them in delivered order with zero business logic.
- **Dumb Studio Editor Reordering**:
  - `MatrixGraphsBlockCard` replaces static `Column` with `ReorderableListView(buildDefaultDragHandles: false, shrinkWrap: true, physics: const NeverScrollableScrollPhysics())`.
  - Provides two redundant UX mechanisms for executive coaches:
    1. **Drag Handles**: `ReorderableDragStartListener` on card header.
    2. **Up/Down Buttons**: `IconButton(icon: Icon(Icons.arrow_upward))` and `IconButton(icon: Icon(Icons.arrow_downward))` for precise single-click movement without mouse dragging.
  - On reorder, the list is mutated in memory (`newGroups.insert(newIndex, newGroups.removeAt(oldIndex))`) and dispatched via `onChanged(payload.copyWith(matrixSynthesisGroups: newGroups))`.

---

## Five-Column Architectural Directive Table (Option B)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`common/global_mandates.py`** | Banned: `LANGUAGE_MANDATE` and `TONE_MANDATE` in `GLOBAL_MANDATES_XML`. Banned: referencing specific DTO field names. | Restructure to 100% static, field-agnemic epistemic invariants: Epistemic Glossary, Null Hypothesis, Verbatim Extraction, Semantic Bleed, Schema Purity, Anti-Score, Anti-ID, Context Segregation. | Eliminate `LANGUAGE_MANDATE` and `TONE_MANDATE` from global mandates. | `test_global_mandates.py`: assert `GLOBAL_MANDATES_XML` is 100% static and contains zero locale strings or field names. |
| **`common/linguistic_directives.py`** | Banned: `include_mandate` parameter gymnastics and embedding dynamic locale codes into static rule sentences. | Single Source of Truth for all language rules: Decoupled into `STATIC_LINGUISTIC_PROTOCOL` (100% static cacheable rule prefix) and `@functools.lru_cache(maxsize=32)` `build_linguistic_parameters(target_locale, source_language)` (lightweight 15-token dynamic tail). | Prune `include_mandate` argument across all callers; eliminate string interpolation inside static warning text. | `test_linguistic_directives.py`: verify complete separation of static protocol and dynamic parameters across locales; assert LRU cache determinism. |
| **`execution/matrix_evaluation.py`** | Banned: Adding coaching tone, UI instructions, or markdown styles to sensor evaluations. | Phase 1 Micro-Sensor Decision Protocol: `MATRIX_SENSOR_SYSTEM_PROMPT` and `CONTEXTUAL_OVERRIDE_DIRECTIVE` enforce strict Null Hypothesis, verbatim extraction in source language, and concise causal reasoning (<25 words). | Pure execution focus; zero UI or persona bloat. | `test_matrix_evaluation.py`: verify sensor protocol purity and verbatim extraction invariants. |
| **`execution/hook_prompts.py`** | Banned: Mixing Phase 2 synthesis curation prompts with Phase 1 execution hook rules. | Pure Execution Hook Directives: Retain `INTERACTION_OBJECTIVE` and `INTERACTION_RULES` for user interaction detection during Phase 1 DAG runs. | Relocate `SYNTHESIS_XAI_CURATION` and `SYNTHESIS_SECTION_RULES_PREFIX` to `synthesis/synthesis_directives.py`. | `test_hook_prompts.py`: verify pure execution hook focus. |
| **`execution/mcp_prompts.py`** | Banned: Scattering MCP verification prompt strings across service classes. | Phase 1 External Evidence Directives: `SOURCE_EXTRACTION_SYSTEM_INSTRUCTION`, `SOURCE_VERIFICATION_SYSTEM_INSTRUCTION`, `CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION`, `MCP_EVIDENCE_INJECTION_DIRECTIVE`, `build_mcp_citation_extraction_directive`. | Consolidate and maintain in `execution/mcp_prompts.py` as SSOT. | `test_mcp_prompts.py`: assert all constants and builders adhere to strict XML directives. |
| **`synthesis/style_directives.py`** | Banned: Duplicate tone mandates across multiple files. Banned: Hardcoding SDUI block formatting in individual domain directives. | Single Source of Truth for Behavioral & Presentation Posture: `DEFAULT_COACHING_TONE_MANDATE`, `ANTI_JARGON_MANDATE_BLOCK`, `SPARSE_DATA_SYNTHESIS_MANDATE`. Universal SDUI block formatting mandate centralized here as a general presentation rule. | Cut redundant tone strings; provide one canonical coaching tone constant; consolidate universal SDUI formatting rule. | `test_style_directives.py`: verify tone, anti-jargon, and sparse data constants, and general SDUI presentation rule. |
| **`synthesis/sdui_directives.py`** | Banned: Embedding domain-specific hook instructions (specifically `USER_ROLE_EXTRACTION`) inside generic SDUI structural rules. | Purify `SYNTHESIS_SDUI_MANDATES` to focus strictly on allowed block discriminators (`paragraph`, `bullet_list`, `alert_box`, `quote_card`, `warning_card`), non-recursion, and `SDUI_BLOCK_STRUCTURE_MANDATE`. | Delete lines 26-27 (`USER_ROLE_EXTRACTION`) from `SYNTHESIS_SDUI_MANDATES`. | `test_sdui_prompt_alignment.py`: verify pure structural block discriminators without role pollution. |
| **`synthesis/synthesis_directives.py`** | Banned: Duplicating database directives as code constants for runtime fallback. | Pure Layer 1 System Identity Prompts: `DEFAULT_SYNTHESIS_SYSTEM_PROMPT`, `DEFAULT_ROW_EXPLANATION_SYSTEM_PROMPT`, `DEFAULT_VARIANCE_SYSTEM_PROMPT`, `EXECUTIVE_SUMMARY_SECTION_ID`, and absorbed `SYNTHESIS_XAI_CURATION` & `SYNTHESIS_SECTION_RULES_PREFIX`. | Eradicate all 8 duplicate substantive directive constants from runtime prompt models. | `test_synthesis_directives.py`: assert Layer 1 identity constants and structural prefixes without substantive directive duplication. |
| **`synthesis/synthesis_registry.py`** | Banned: Shadow dictionary mapping `PresetView` to fallback prompt constants. | **PERMANENTLY DELETED FILE**. All directives are resolved directly from `OutputProfile` in database. Zero code fallback lookups. | Delete entire `SynthesisPromptRegistry` class and `synthesis_registry.py` file. | AST guardrail asserting `SynthesisPromptRegistry` does not exist in `backend_v2`. |
| **`services/factories/output_profile_factory.py`** | Banned: Mixing factory creation templates with runtime prompt models. | Factory Default Template Provider: Supplies initial default directive texts as clean English `str` constants when initializing seed data or creating a new `OutputProfile` draft in Studio UI. | Clean separation between factory creation and runtime synthesis execution. | Unit test verifying factory creates valid, fully populated `OutputProfile` instances with English `str` directives. |
| **`backend_v2/services/studio/output_profile_service.py`** | Banned: Incomplete skeleton drafts with null directives failing headless execution. | Bind `output_profile_factory.build_draft_output_profile` in `create_output_profile_draft` to populate all 8 substantive directives (English `str`), valid default length limits, valid `target_block_order`, and an initial valid `MatrixSynthesisGroup`. External API callers can run synthesis immediately without UI interaction. | Direct factory delegation in service layer; zero intermediate builder classes. | `test_output_profile_service.py` asserting headless draft creation yields a runnable, 100% valid profile. |
| **`backend_v2/services/length_budget_enforcer.py`** | Banned: Brutal character slicing (`text[:limit]`) that truncates sentences mid-word. Banned: Re-prompting loops that double token costs. | Two-Tier Budgeting: 1) Layer 4 dynamic `<section_budget>` prompt instruction; 2) Sentence-boundary post-processing `enforce_sentence_boundary_budget`. | Single-pass budgeting without speculative multi-turn loops. | Unit tests in `test_length_budget_enforcer.py` asserting terminal punctuation preservation on over-length inputs. |
| **`OutputProfile` Models (`v2_core.py`, `output_profile.py`, `output_profile.dart`)** | Banned: Bilingual `I18nText` on prompt directives. Banned: Naked dictionaries (`dict[str, int]`) for section length controls. Banned: Duplicate group IDs in `matrix_synthesis_groups`. | All 9 prompt directives (`tone_instruction` and 8 `*_directive` fields) typed strictly as English `str | None` (`String?` in Dart). 4 explicit integer fields for length. Add `@model_validator(mode="after")` enforcing strictly unique group IDs across `matrix_synthesis_groups`. | Direct fields on profile; no intermediate wrapper objects; eliminate `I18nText` for prompt instructions. | Freezed and Pydantic validation tests asserting string directives, integer constraints, and group ID uniqueness. |
| **`backend_v2/models/dtos/synthesis.py`** | Banned: Importing prompt directives (`DESC_TRANSLATION_MANDATE`) into Pydantic schema field descriptions. | Decouple schema descriptions from linguistic prompt directives: define pure semantic descriptions across all 8 fields in `XaiHighlightItem`, `SynthesisRowExplanationDTO`, `ExecutiveSummarySectionResult`, and `SynthesisOutputDTO` (lines 60, 101, 143, 147, 151, 217, 221, 226) without translation mandates. | Strip prompt imports from schema models; centralize language enforcement strictly in `linguistic_directives.py`. | Schema validation tests asserting field descriptions are clean strings with zero prompt imports, and AST guardrail in `test_ast_prompt_xml_sovereignty.py`. |
| **`backend_v2/models/v2_core.py` (`MatrixSynthesisGroup`)** | Banned unvalidated target block counts allowing mismatched views to persist in DB. | `@model_validator(mode="after")` enforcing: 1D == 1, 2D == 2, 3D == 3, Text $\ge$ 1. | Keep validation in single concise `@model_validator` method without external helper bloat. | `test_v2_core_models.py` asserting `ValidationError` on all mismatched cardinalities. |
| **`backend_v2/seed/seed_data.json` (`output_profiles` collection)** | Banned: Bilingual prompt directives on lines 18192–18245; `"using SDUI ParagraphBlocks"` and repeated `"- Structure your findings directly as SDUI blocks."`. Banned: 1d_metrics groups containing 2 target blocks. | Deterministically convert lines 18192–18245 of `prf_5d6e7f8091a2b3c4` to clean English `str` plain strings, purging all Finnish prompt translations. Substantive prompts contain exclusively analytical instructions (Layer 3). Set `view_type: "2d_compare"` for the 3 comparative 2-block groups. | Direct JSON correction with exact line guidance, preserving presentation fields (`name`, `description`, `user_role_label`, `custom_preface`). | `test_output_profile_studio_parity.py` and `test_seed_architectural_guardrails.py` passing 100%. |
| **`backend_v2/seed/seed_data.json` (`prompt_blocks` orphan block `blk_eeea566da4ab45f9`)** | Banned: Orphan block `blk_eeea566da4ab45f9` containing legacy V1 class names and corrupted XML text. | Prune or mark inactive orphan prompt blocks and steps that do not belong to active DAG workflows. | Delete or isolate `blk_eeea566da4ab45f9` from seed registry validation. | `uv run python backend_v2/seed/run_seed.py local --dry-run` passing with clean registry. |
| **`backend_v2/services/sdui/adapters/matrix_graphs_adapter.py`** | Banned: `seen_axes` variable dropping shared blocks across groups; loose string checks and count fallbacks. | Strict `match grp.view_type:` routing to `SduiMetrics1DBlock`, `SduiScatterPlotBlock`, `SduiRadarChartBlock`. Eliminate `seen_axes`. | Direct dictionary lookup per group; zero inter-group axis starvation. | `test_matrix_graphs_adapter.py` verifying 1:1 SDUI block emission per view type. |
| **`client_app_v2/.../profile_general_tab.dart` (Tab 1)** | Banned: Duplicating 1:1 section directives on general settings screen. Banned: Bilingual `I18nTextField` language tabs on prompt directives. | Tab 1 is dedicated strictly to Profile Identity (Card 1), Persona Posture & Target Audience (Card 2: `tone_instruction` as English `TextFormField`, `user_role_label`/`custom_preface` as `I18nTextField`), and Reusable Multi-Instance View Types (Card 3: 4 directives as English `TextFormField`). | Prune all 4 duplicated 1:1 directive input fields from Card 3; retitle Card 3 to `profileMatrixViewDirectivesTitle`; eliminate language tabs from prompt directives. | `profile_general_tab_test.dart` asserting only 4 matrix view type directives are rendered on Tab 1 with English `TextFormField`. |
| **`client_app_v2/.../profile_section_config_tab.dart` (Tab 3 Detail Cards)** | Banned: Inconsistent card inputs; bilingual `I18nTextField` language tabs on prompt directives; checkboxes toggling SDUI formatting for plain string tasks. | Tab 3 provides 1:1 parity between output section cards and their dedicated directives (English `TextFormField`) and numeric length budgets: `ExecutiveSummaryBlockCard`, `MatrixSummaryTableCard`, `XaiExtensionsBlockCard`, `VarianceBlockCard`. | Keep section-level directives and length inputs strictly within their dedicated cards; single-language English input. | `profile_section_config_tab_test.dart` verifying master-detail navigation and dedicated 1:1 directive and length inputs. |
| **`client_app_v2/.../matrix_graph_item_editor.dart`** | Banned: Client-side "auto-clamp on load" duct-tape or runtime data scrubbing; `2 / 1 valittu` display; unselected non-clickable chips; hardcoded strings. Quality validation is locked 100% to backend `@model_validator` and database seed sanitization. | Pure dumb editor: Renders state as delivered with zero auto-clamping on load; Radio single-select for 1D; disabled chips when max reached; `.arb` labels. Zero client-side data mutation. | Use standard `FilterChip(onSelected: canSelectMore ? ... : null)` without custom gesture layers or load-time auto-clamping. | `matrix_graph_editor_test.dart` verifying chip replacement, quota lock, and view type switching. |
| **`client_app_v2/.../matrix_graphs_block_card.dart`** | Banned: Static un-reorderable list and fragile `indexOf(group)` lookup. | `ReorderableListView` with explicit drag handle + Up/Down arrow buttons for desktop precision. Update items by unique ID. | Avoid complex drag overlays; use native `ReorderableListView(buildDefaultDragHandles: false)`. | `matrix_graphs_block_card_test.dart` testing drag-reorder and move-up/down button callbacks. |
| **Prompt Callers (`worker.py`, `prompt_factory.py`, `matrix_sensor_prompt_builder.py`, `interaction_hook.py`, services)** | Banned: Inconsistent prompt layer assembly; calling `compiler.resolve_i18n()` on prompt directives; silently resolving default directives when profile field is missing. | Standardize Layer 1-4 assembly: Layer 1 (`GLOBAL_MANDATES_XML`), Layer 2 (`style_directives`), Layer 3 (`build_linguistic_parameters` at dynamic tail), Layer 4 (100% database `OutputProfile` directives as plain English `str` and `<section_budget>`). Direct dot notation access without `resolve_i18n`. Enforce Fail-Fast (`OUTPUT_PROFILE_INCOMPLETE`) if required directives are missing. | Remove `include_mandate` flags; eliminate fallback chains; eliminate `resolve_i18n` on directives; normalize submodule imports. | `backend_audit_loop.py` across all prompt callers with 100% test pass and zero regressions; unit test verifying `OUTPUT_PROFILE_INCOMPLETE` is raised on missing directives. |

---

## Falsification & Red-Teaming (Failure Point Analysis)

In accordance with Tier 0 Red-Team audit protocols, the implementation plan is cross-examined against four realistic adversarial failure modes:

### Failure Point 1: Database Migration Deserialization Crash on Legacy I18nText Records
- **Vulnerability**: Existing MongoDB and local `db_v2.json` documents store prompt directives as bilingual `I18nText` dictionaries (`{"translations": {"en": "...", "fi": "..."}}`). Switching Pydantic models in `backend_v2/models/v2_core.py` and `models/dtos/output_profile.py` strictly to `str | None` with `ConfigDict(strict=True, extra="forbid")` will cause immediate `ValidationError` crashes upon hydrating un-sanitized records from the database.
- **Root Cause**: Pydantic strict mode forbids implicit coercion of dictionaries into strings.
- **Proof-Anchor Mitigation**: Enforce the `03_seed_vault.md` protocol:
  1. Automated pre-flight sanitization script converts all 9 directive fields in `seed_data.json` from `I18nText` to clean English `str` BEFORE model validation is enforced.
  2. Local database wipe and re-seed (`uv run python backend_v2/seed/run_seed.py local`) is executed as part of Phase 1 before running synthesis tasks.
  3. Pre-flight schema validation gate (`run_seed.py local --dry-run`) validates all documents 100% in-memory with strict schemas.

### Failure Point 2: Headless API Draft Creation Incompleteness (`OUTPUT_PROFILE_INCOMPLETE`)
- **Vulnerability**: Removing `SynthesisPromptRegistry` and fallback lookups (`if not directive: fallback`) in `worker.py` means any `OutputProfile` missing a directive for an active block type triggers an instant Fail-Fast crash: `AppException(ErrorCodes.OUTPUT_PROFILE_INCOMPLETE)`. If `POST /api/v2/studio/profiles/draft` instantiates an empty skeleton with `None` directives, calling synthesis on that profile immediately crashes without giving API consumers a runnable draft.
- **Root Cause**: Pure headless callers never interact with Flutter UI forms to populate empty text fields.
- **Proof-Anchor Mitigation**:
  1. `StudioOutputProfileService.create_output_profile_draft` directly binds `output_profile_factory.build_draft_output_profile(...)`.
  2. Factory pre-populates all 8 substantive directives with clean English `str` defaults, all 4 section length constraints with defaults, and an initial valid `MatrixSynthesisGroup`.
  3. Unit test `test_output_profile_service.py` asserts that newly drafted profiles are 100% complete and runnable immediately out-of-the-box.

### Failure Point 3: Sentence-Boundary Trimming Truncation Anomaly on Unpunctuated Text
- **Vulnerability**: If an LLM emits a single massive, unbroken sentence exceeding `max_chars` (or outputs raw text without terminal punctuation '.', '!', '?'), a naive backward scan looking for punctuation could fail to find any terminal boundary, either returning un-truncated text or slicing into an empty string.
- **Root Cause**: Heuristic sentence-boundary matching assuming standard punctuation.
- **Proof-Anchor Mitigation**:
  1. `enforce_sentence_boundary_budget` scans backwards within the window `[max_chars * 0.6, max_chars]`.
  2. If a terminal sentence boundary exists within that window, it trims at that boundary.
  3. If no terminal boundary exists, it retains the first sentence intact up to `max_chars` or trims cleanly at the last complete word boundary, emitting a structured warning. It NEVER returns an empty string or slices words mid-character.
  4. Covered by 5 ISTQB equivalence partition unit tests in `test_length_budget_enforcer.py`.

### Failure Point 4: Flutter Serialization Deserialization White Screen of Death
- **Vulnerability**: If Flutter Freezed models in `client_app_v2/lib/features/studio/models/output_profile.dart` are updated from `I18nText?` to `String?` without running `dart run build_runner build`, runtime deserialization will attempt to parse plain JSON strings into `I18nText` structures, triggering `CheckedFromJsonException` and crashing the profile editor into `AppErrorBoundary`.
- **Root Cause**: Out-of-sync Freezed `.g.dart` generated files.
- **Proof-Anchor Mitigation**:
  1. Execution step mandates running `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`.
  2. The flutter audit script automatically runs `build_runner` with `--delete-conflicting-outputs`.
  3. Automated test `profile_general_tab_test.dart` and `profile_section_config_tab_test.dart` verify clean JSON roundtrip serialization.

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="PHASE_1_PRE_IMPLEMENTATION_CLEANUPS_AND_SEED_PREPARATION">
    <action>Audit and resolve the 7 technical debt items across target boundaries before initiating new subpackage structures.</action>
    <action>Eradicate legacy SynthesisPromptRegistry fallback lookups: prepare deletion of backend_v2/models/prompts/synthesis_registry.py and its test test_synthesis_registry.py.</action>
    <action>Follow 03_seed_vault.md protocol: Create a timestamped backup copy of backend_v2/seed/seed_data.json inside backend_v2/seed/backups/seed_data_backup_<timestamp>.json.</action>
    <action>Deterministically sanitize output_profiles document prf_5d6e7f8091a2b3c4 across exact lines 18192–18245 in backend_v2/seed/seed_data.json: convert all 9 prompt directives (tone_instruction, executive_summary_directive, matrix_1d_synthesis_directive, matrix_2d_synthesis_directive, matrix_3d_synthesis_directive, matrix_text_synthesis_directive, row_explanation_directive, xai_synthesis_directive, variance_synthesis_directive) from bilingual translation dictionaries to clean plain English strings (str), completely pruning Finnish prompt translations and stripping all SDUI formatting boilerplate.</action>
    <action>Add baseline values for row_explanation_length_constraint (250), xai_length_constraint (300), and variance_length_constraint (500) to output_profiles in seed_data.json.</action>
    <action>Fix matrix_synthesis_groups in output_profiles (prf_5d6e7f8091a2b3c4) in seed_data.json: change view_type from 1d_metrics to 2d_compare for the 3 groups that target 2 complementary blocks (specifically: grp_440a5fef9331451b, grp_c5804a9143c34cb1, and grp_6b8c766185294f7e), eliminating the 2 / 1 valittu seed corruption.</action>
    <action>Sanitize or isolate orphan prompt block blk_eeea566da4ab45f9 in prompt_blocks to eliminate legacy V1 class names and corrupted XML text.</action>
    <action>In client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart, extract hardcoded Finnish strings ('1D Mittari', '2D Vertailu', '3D Tutka', 'Teksti', 'valittu', 'Ei matriiseja valittavissa työnkulussa.') into AppLocalizations (.arb files).</action>
    <action>In client_app_v2/lib/features/studio/views/widgets/profile/blocks/executive_summary_block_card.dart#L72, replace hardcoded hintText ('esim. 1000 merkkiä') with l10n.profileSynthesisLengthHint.</action>
    <action>In client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart#L83,L95, replace fragile indexOf(group) and remove(group) on @Freezed(equal: false) instances with indexWhere((g) => g.id == group.id) and removeWhere((g) => g.id == group.id).</action>
    <action>In client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart#L215-L235, disable unselected FilterChips when quota is reached (onSelected: null) while preserving 1D single-select radio replacement.</action>
    <action>In backend_v2/services/studio/output_profile_service.py#L182, purge hardcoded fallback workflow id ('wf_9d68c573802341db') when workflows list is empty, raising explicit ResourceNotFoundError.</action>
    <action>In backend_v2/models/dtos/synthesis.py, remove DESC_TRANSLATION_MANDATE import (L12) and strip it from all 8 field descriptions across XaiHighlightItem (L60), SynthesisRowExplanationDTO (L101), ExecutiveSummarySectionResult (L143, L147, L151), and SynthesisOutputDTO (L217, L221, L226), restoring them to pure semantic descriptions.</action>
    <action>Anchor length constraint limits in SSOT constants across Python (settings.py / factory) and Flutter (SystemUiConstraints).</action>
    <action>In client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart, replace manual client-side ID generation (const Uuid().v4().replaceAll('-', '').substring(0, 16)) with backend-aligned opaque ID generation, and replace magic SizedBox spacing with AppSpacing.h8 tokens.</action>
    <action>Execute two-phase in-memory pre-flight verification: uv run python backend_v2/seed/run_seed.py local --dry-run and uv run python scripts/audit_database_atoms.py --strict.</action>
    <action>Synchronize local development database: uv run python backend_v2/seed/run_seed.py local.</action>
    <constraint invariant="root_cause_first_over_reseed_mandate">All corrupting data paths and legacy fallback debt must be excised before building new logic.</constraint>
  </step>

  <step id="2" name="SCAFFOLDING_SUBPACKAGES_AND_COMMON_LAYER">
    <action>Create directories backend_v2/models/prompts/common/, backend_v2/models/prompts/execution/, and backend_v2/models/prompts/synthesis/.</action>
    <action>Create backend_v2/models/prompts/common/__init__.py exporting common prompt symbols.</action>
    <action>Create backend_v2/models/prompts/common/field_prompts.py transferring constants verbatim from legacy field_prompts.py.</action>
    <action>Create backend_v2/models/prompts/common/global_mandates.py containing purified GLOBAL_MANDATES_XML with LANGUAGE_MANDATE and TONE_MANDATE removed.</action>
    <action>Create backend_v2/models/prompts/common/linguistic_directives.py defining STATIC_LINGUISTIC_PROTOCOL and build_linguistic_parameters(target_locale, source_language) decorated with @functools.lru_cache(maxsize=32).</action>
    <constraint invariant="static_first_dynamic_last_topology">STATIC_LINGUISTIC_PROTOCOL must contain zero f-string interpolations. All dynamic parameters reside strictly inside build_linguistic_parameters.</constraint>
    <constraint invariant="anti_ambiguity_mandate">Do not use ambiguous terminology in comments or prompt definitions.</constraint>
  </step>

  <step id="3" name="EXECUTION_LAYER_RELOCATION_AND_PURIFICATION">
    <action>Create backend_v2/models/prompts/execution/__init__.py exporting execution prompt symbols.</action>
    <action>Create backend_v2/models/prompts/execution/matrix_evaluation.py transferring MATRIX_SENSOR_SYSTEM_PROMPT and CONTEXTUAL_OVERRIDE_DIRECTIVE.</action>
    <action>Create backend_v2/models/prompts/execution/hook_prompts.py retaining strictly INTERACTION_OBJECTIVE and INTERACTION_RULES (lines 1-32 of legacy file).</action>
    <action>Create backend_v2/models/prompts/execution/mcp_prompts.py containing all MCP verification and evidence prompts.</action>
    <constraint invariant="tripartite_pipeline_architecture">Execution layer prompts must contain zero Server-Driven UI instructions and zero coaching tone instructions.</constraint>
  </step>

  <step id="4" name="SYNTHESIS_LAYER_RELOCATION_AND_PURIFICATION">
    <action>Create backend_v2/models/prompts/synthesis/__init__.py exporting synthesis prompt symbols.</action>
    <action>Create backend_v2/models/prompts/synthesis/style_directives.py defining DEFAULT_COACHING_TONE_MANDATE, ANTI_JARGON_MANDATE_BLOCK, SPARSE_DATA_SYNTHESIS_MANDATE, and centralizing the universal SDUI block structuring rule.</action>
    <action>Create backend_v2/models/prompts/synthesis/sdui_directives.py retaining SYNTHESIS_SDUI_MANDATES, SECTION_SYNTHESIS_DIRECTIVE_BLOCK, and STATE_ISOLATION_BLOCK, with lines 26-27 (USER_ROLE_EXTRACTION and ROLE TRANSLATION) purged.</action>
    <action>Create backend_v2/models/prompts/synthesis/synthesis_directives.py defining Layer 1 identity prompts (DEFAULT_SYNTHESIS_SYSTEM_PROMPT, DEFAULT_ROW_EXPLANATION_SYSTEM_PROMPT, DEFAULT_VARIANCE_SYSTEM_PROMPT, EXECUTIVE_SUMMARY_SECTION_ID), and absorbing purified SYNTHESIS_XAI_CURATION (line 41 stripped) and SYNTHESIS_SECTION_RULES_PREFIX.</action>
    <action>Create backend_v2/services/factories/output_profile_factory.py defining baseline factory default templates as plain English str constants (DEFAULT_FACTORY_EXECUTIVE_SUMMARY_DIRECTIVE, etc.) used exclusively for seeding and Studio UI 'New Profile' creation.</action>
    <constraint invariant="zero_service_layer_fallbacks">Synthesis directives are derived 100% dynamically from database OutputProfile during runtime execution. No runtime fallback registries are created.</constraint>
  </step>

  <step id="5" name="ROOT_BARREL_REEXPORT_AND_LEGACY_PURGE">
    <action>Update backend_v2/models/prompts/__init__.py to re-export all symbols across common, execution, and synthesis subpackages; explicitly update __all__ to add STATIC_LINGUISTIC_PROTOCOL and build_linguistic_parameters, and remove LANGUAGE_MANDATE, TONE_MANDATE, SynthesisPromptRegistry, and build_linguistic_context.</action>
    <action>Delete legacy root files in backend_v2/models/prompts/: global_mandates.py, linguistic_directives.py, field_prompts.py, matrix_evaluation.py, hook_prompts.py, mcp_prompts.py, style_directives.py, sdui_directives.py, synthesis_directives.py, and synthesis_registry.py.</action>
    <action>Delete legacy backend_v2/tests/unit/models/prompts/test_synthesis_registry.py as SynthesisPromptRegistry is permanently removed.</action>
    <action>Verify test_prompts_init.py passes and confirms all symbols remain accessible from root models.prompts package.</action>
    <constraint invariant="anti_duplication">Legacy prompt files at models/prompts root must be removed immediately after subpackage relocation.</constraint>
  </step>

  <step id="6" name="TWO_TIER_LENGTH_BUDGET_ENGINE_AND_DTO_EXPANSION">
    <action>Create backend_v2/services/length_budget_enforcer.py implementing enforce_sentence_boundary_budget(text: str, max_chars: int) -> str.</action>
    <action>Create backend_v2/tests/unit/services/test_length_budget_enforcer.py testing sentence-ending punctuation preservation, under-length pass-through, and boundary truncation.</action>
    <action>Update backend_v2/models/v2_core.py, backend_v2/models/domain/output_profile.py, and backend_v2/models/dtos/output_profile.py to convert all 9 prompt directive fields (tone_instruction, executive_summary_directive, matrix_1d_synthesis_directive, matrix_2d_synthesis_directive, matrix_3d_synthesis_directive, matrix_text_synthesis_directive, row_explanation_directive, xai_synthesis_directive, variance_synthesis_directive) from I18nText | None to str | None, and add row_explanation_length_constraint, xai_length_constraint, and variance_length_constraint as optional integer fields with bounds validation.</action>
    <action>In backend_v2/models/v2_core.py, implement @model_validator(mode="after") on MatrixSynthesisGroup enforcing dimensional cardinality: 1d_metrics requires exactly 1 target block, 2d_compare requires exactly 2 target blocks, 3d_matrix requires exactly 3 target blocks, and text_only requires at least 1 target block. Raise ValueError on violation.</action>
    <action>In backend_v2/models/v2_core.py, implement @model_validator(mode="after") on OutputProfile asserting that all synthesis group IDs in matrix_synthesis_groups are unique, preventing duplicate ID collisions across headless API clients.</action>
    <action>In backend_v2/services/studio/output_profile_service.py, update create_output_profile_draft to bind output_profile_factory.build_draft_output_profile, populating all 8 substantive directives (English str), 4 default section length constraints, a valid target_block_order, and an initial valid MatrixSynthesisGroup so newly drafted profiles created headlessly via REST API are 100% valid and runnable out-of-the-box without requiring UI interaction.</action>
    <action>In backend_v2/services/sdui/adapters/matrix_graphs_adapter.py#L55-L77, eliminate global seen_axes set to prevent cross-group block starvation, allowing each synthesis group to independently access its configured target blocks.</action>
    <constraint invariant="the_duct_tape_ban">Never truncate text mid-sentence or slice strings with text[:limit] without sentence boundary analysis.</constraint>
  </step>

  <step id="7" name="STUDIO_UI_DIRECTIVE_SEGREGATION_AND_LENGTH_INPUTS">
    <action>In client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart, remove executiveSummaryDirective, rowExplanationDirective, xaiSynthesisDirective, and varianceSynthesisDirective from Card 3 (AI Synthesis Directives).</action>
    <action>Retain matrix1dSynthesisDirective, matrix2dSynthesisDirective, matrix3dSynthesisDirective, and matrixTextSynthesisDirective in Card 3, retitling it with profileMatrixViewDirectivesTitle.</action>
    <action>In client_app_v2/lib/features/studio/models/output_profile.dart, update all 9 prompt directives from I18nText? to String?, and add rowExplanationLengthConstraint, xaiLengthConstraint, and varianceLengthConstraint fields.</action>
    <action>Run flutter pub run build_runner build --delete-conflicting-outputs to update Freezed and JSON serialization models in client_app_v2.</action>
    <action>In client_app_v2/lib/features/studio/views/widgets/profile/blocks/, update ExecutiveSummaryBlockCard, MatrixSummaryTableCard, XaiExtensionsBlockCard, and VarianceBlockCard to replace I18nTextField with single-language English multiline TextFormField widgets, and add dedicated numeric length constraint TextFormField inputs.</action>
    <action>In client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart, replace I18nTextField on tone_instruction and the 4 matrix view type directives with English multiline TextFormField widgets.</action>
    <action>In client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart, completely remove any "auto-clamp on load" heuristics or data scrubbing in initState/didUpdateWidget/build, lock quality control strictly to backend @model_validator, enforce single-select radio replacement in 1D mode, disable unselected FilterChips when maxSlots is reached, and extract all hardcoded UI strings to AppLocalizations.</action>
    <action>In client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart, upgrade the static item list to a ReorderableListView (with buildDefaultDragHandles: false, shrinkWrap: true, physics: const NeverScrollableScrollPhysics()), add ReorderableDragStartListener drag handles and Up/Down IconButton controls to each card header, eliminate fragile indexOf(group) by updating items by unique ID, and dispatch list reordering via payload.copyWith(matrixSynthesisGroups: reorderedList).</action>
    <action>Add localization keys to client_app_v2/lib/l10n/app_en.arb and app_fi.arb for the 3 new length constraint inputs, reordering controls, and profileMatrixViewDirectivesTitle.</action>
    <action>Update client_app_v2/test/features/studio/views/widgets/profile/tabs/profile_general_tab_test.dart and profile_section_config_tab_test.dart to assert UI partitioning and length input presence.</action>
    <action>Update client_app_v2/test/unit/features/studio/matrix_graph_editor_test.dart to test 1D single-select replacement, quota-based chip disabling, and reordering callbacks.</action>
    <action>Run Flutter audit loop: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart --build.</action>
    <constraint invariant="dumb_painter_sdui">UI widgets strictly bind and emit DTO state; no semantic logic or fallback synthesis is performed in Dart layers.</constraint>
  </step>

  <step id="8" name="CALLER_HARMONIZATION_AND_BUDGET_INJECTION">
    <action>Update backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py to bind STATIC_LINGUISTIC_PROTOCOL in static_messages, inject build_linguistic_parameters() in dynamic_messages, and remove include_mandate.</action>
    <action>Update backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py to remove include_mandate argument and consume purified linguistic builder.</action>
    <action>Update backend_v2/worker.py to consume STATIC_LINGUISTIC_PROTOCOL and build_linguistic_parameters(), access directives directly as English str | None from active_profile_dto via direct dot notation, completely purge all 6 calls to compiler.resolve_i18n() (lines 1067, 1081, 1139, 1206, 1248, 1379), inject dynamic section_budget into Layer 4 dynamic_context for each of the 4 synthesis tasks, apply enforce_sentence_boundary_budget to generated string outputs, eliminate fallback lookups and direct directive constant imports (specifically VARIANCE_EXPLANATION_DIRECTIVE on L1383 and XAI_EXPLANATIONS_DIRECTIVE on L1210), and raise AppException(ErrorCodes.OUTPUT_PROFILE_INCOMPLETE) if required directives are missing for active blocks.</action>
    <action>Normalize imports in 1-hop caller modules: backend_v2/hooks/interaction_hook.py, backend_v2/services/orchestrator/extraction_schema_factory.py, backend_v2/services/orchestrator/extractive_sensor_service.py, backend_v2/services/orchestrator/engines/synthesis_engine.py, backend_v2/services/translation_service.py, backend_v2/models/dtos/evaluation_steps.py, backend_v2/models/dtos/synthesis.py, backend_v2/llm/schema_builder.py, and backend_v2/core/registry.py to import directly from backend_v2.models.prompts or canonical subpackages.</action>
    <constraint invariant="universal_fail_fast">Do not swallow missing configurations silently; fail fast with OUTPUT_PROFILE_INCOMPLETE.</constraint>
  </step>

  <step id="9" name="AST_GUARDRAILS_AND_TEST_SUITE_VALIDATION">
    <action>Update backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py to add Phase 1 vs Phase 2 import boundary firewall tests, unique XML tag verification, assertion that SynthesisPromptRegistry does not exist, AST guardrail asserting include_mandate parameter does not exist anywhere in backend_v2/ after purge, AST guardrail asserting I18nText does not appear as type annotation on the 9 directive fields in v2_core.py OutputProfile, and AST guardrail asserting DESC_TRANSLATION_MANDATE does not appear in any file under backend_v2/models/dtos/.</action>
    <action>Update all prompt unit tests in backend_v2/tests/unit/models/prompts/ (including test_sdui_directives.py) to test subpackages and verify Fail-Fast behavior.</action>
    <action>Update caller test files: test_sdui_prompt_alignment.py, test_output_profile_studio_parity.py, test_translation_service.py, test_extractive_sensor_service.py, test_synthesis_engine.py, and test_prompt_factory.py to reflect modernized imports, English str directives, and assert that output_profiles directives contain zero literal class names or redundant SDUI boilerplate.</action>
    <action>Update backend_v2/tests/unit/test_v2_core_models.py to assert ValidationError when MatrixSynthesisGroup cardinality is violated across 1D, 2D, 3D, and Text views, and when duplicate group IDs exist in matrix_synthesis_groups, and verify that prompt directives accept plain English strings.</action>
    <action>Update backend_v2/tests/unit/services/sdui/adapters/test_matrix_graphs_adapter.py to assert independent block emission across groups (seen_axes already resolved; verify no regression).</action>
    <action>Update backend_v2/tests/unit/services/studio/test_output_profile_service.py to assert that create_output_profile_draft initializes fully populated, valid profiles with factory default directives (English str), length constraints, and groups, verifying they pass Pydantic validation and are immediately runnable headlessly without UI interaction.</action>
    <action>Run localized prompt tests: uv run pytest backend_v2/tests/unit/models/prompts/ -v.</action>
    <action>Run length budget enforcer tests: uv run pytest backend_v2/tests/unit/services/test_length_budget_enforcer.py -v.</action>
    <action>Run core models unit tests: uv run pytest backend_v2/tests/unit/test_v2_core_models.py -v.</action>
    <action>Run matrix graphs adapter tests: uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_matrix_graphs_adapter.py -v.</action>
    <action>Run output profile service unit tests: uv run pytest backend_v2/tests/unit/services/studio/test_output_profile_service.py -v.</action>
    <action>Run worker synthesis unit tests: uv run pytest backend_v2/tests/unit/test_worker_synthesis.py -v.</action>
    <action>Run output profile studio parity test: uv run pytest backend_v2/tests/unit/services/test_output_profile_studio_parity.py -v.</action>
    <action>Run SDUI semantic parity integration test per sdui_contract_fracture_prevention: uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py -v.</action>
    <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/models/prompts/ --test.</action>
    <action>Run flutter audit loop: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart --build.</action>
    <constraint invariant="two_stage_testing">Execute isolated unit tests first, followed by the global quality gate audit loop.</constraint>
    <constraint invariant="multi_session_handover">This is a multi-session plan. Mandatory /tier5-session-handover checkpoints after Steps 1-3, Steps 4-5, Steps 6-7, and Steps 8-9.</constraint>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
- `uv run python backend_v2/seed/run_seed.py local --dry-run`
- `uv run python scripts/audit_database_atoms.py --strict`
- `uv run pytest backend_v2/tests/unit/models/prompts/ -v`
- `uv run pytest backend_v2/tests/unit/services/test_length_budget_enforcer.py -v`
- `uv run pytest backend_v2/tests/unit/test_v2_core_models.py -v`
- `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_matrix_graphs_adapter.py -v`
- `uv run pytest backend_v2/tests/unit/services/studio/test_output_profile_service.py -v`
- `uv run pytest backend_v2/tests/unit/test_ast_prompt_xml_sovereignty.py -v`
- `uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py -v`
- `uv run pytest backend_v2/tests/unit/test_worker_synthesis.py -v`
- `uv run pytest backend_v2/tests/unit/services/test_output_profile_studio_parity.py -v`
- `uv run pytest backend_v2/tests/unit/test_sdui_prompt_alignment.py -v`
- `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py -v`
- `uv run python scripts/backend_audit_loop.py backend_v2/models/prompts/ --test`
- `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart --build`

### Markdown Boundary Audit
- `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Prompt_Architecture_Harmonization.md`
