# Task Tracker: Matrix Graph Length Constraint & Tripartite Prompt Alignment

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_generation_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[c:\Users\risto\.gemini\antigravity-ide\brain\ae970c14-42ca-4c7c-8448-845d85a77ea7\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Constraint: `feature_sovereignty_mandate` - Preserve all cognitive features, metrics, and matrix metadata.
- [x] Constraint: `the_zero_compromise_pledge` - Strict Pydantic V2 / Freezed schemas with extra='forbid' and zero naked dicts.
- [x] Constraint: `zero_service_layer_fallbacks` - No fallback defaults; log warning and skip empty cosmetic directives without crashing.
- [x] Constraint: `tripartite_phase_isolation` - Strict segregation: Phase 1 execution prompts in execution/, cross-phase in common/, Phase 2 in synthesis/.
- [x] Constraint: `backwards_compat_barrel_reexport` - common/__init__.py must re-export relocated execution symbols for 1-hop callers.
- [x] Constraint: `two_stage_testing` - Run isolated unit tests first, then backend_audit_loop and flutter_audit_loop.
- [x] Constraint: `step_by_step_mode` - Stop after each cohesive milestone and request user approval before proceeding.

## Execution Tasks

- [x] **Phase 1: Pre-Implementation Cleanups & Technical Debt Sweeps**
  - [x] Fix `OutputProfileUpdateDTO.variance_length_constraint` constraint inconsistency in `backend_v2/models/dtos/output_profile.py` (`ge=50, le=2000`).
  - [x] Verify existing test suite passes before modifications (updated `test_output_profile_synthesis_directives` for `str` directives).

- [x] **Phase 2: Backend Core & Configuration**
  - [x] Add `default_matrix_graph_length_constraint` to `backend_v2/settings.py` (default: 400).
  - [x] Add `matrix_graph_length_constraint` to `OutputProfile` in `backend_v2/models/v2_core.py` (`ge=50, le=2000`).
  - [x] Add `matrix_graph_length_constraint` to `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO` in `backend_v2/models/dtos/output_profile.py`.
  - [x] Bind `matrix_graph_length_constraint` in `backend_v2/services/factories/output_profile_factory.py`.
  - [x] Update baseline output profile `prf_5d6e7f8091a2b3c4` in `backend_v2/seed/seed_data.json`.
  - [x] Run domain, DTO, and seed validation tests.

- [x] **Phase 3: Tripartite Prompt Architecture Migration**
  - [x] Move `global_mandates.py` from `common/` to `execution/`.
  - [x] Move `field_prompts.py` from `common/` to `execution/`.
  - [x] Update `models/prompts/execution/__init__.py` to re-export relocated symbols.
  - [x] Update `models/prompts/common/__init__.py` to re-export execution symbols as backwards compatibility shim.
  - [x] Update `models/prompts/__init__.py` root barrel exports.
  - [x] Purge `DEFAULT_COACHING_TONE_MANDATE` and `SYNTHESIS_LENGTH_CONSTRAINT` from `style_directives.py`.
  - [x] Rename `DEFAULT_*` system prompts in `synthesis_directives.py` and maintain backwards-compatible aliases.
  - [x] Refactor `backend_v2/worker.py` synthesis prompt assembly:
    - [x] Purge `GLOBAL_MANDATES_XML` from synthesis user messages.
    - [x] Purge `DEFAULT_COACHING_TONE_MANDATE` and use dynamic `tone_instruction` (omit tone block if empty).
    - [x] Replace `raise AppException` on empty directives with `logger.warning` and skip section.
    - [x] Inject `<section_budget>{matrix_graph_length_constraint}</section_budget>` for matrix synthesis groups.
    - [x] Clean unused imports in `worker.py`.
  - [x] Update consumers and AST tests:
    - [x] `test_ast_prompt_xml_sovereignty.py#L151` path update.
    - [x] `test_global_mandates.py#L1` import update.
    - [x] `test_field_prompts.py#L6` import update.
    - [x] `test_extractive_sensor_service.py#L16` import update.
    - [x] `test_worker_synthesis.py` assertions for directive skipping.
    - [x] `test_output_profile_studio_parity.py` and `test_style_directives.py` test updates.

- [x] **Phase 4: Frontend Dart Models & Studio UI**
  - [x] Add `matrixGraphLengthConstraint` to Freezed `OutputProfile` in `output_profile.dart`.
  - [x] Add localization keys in `app_en.arb` and `app_fi.arb`.
  - [x] Add `TextFormField` bound to `payload.matrixGraphLengthConstraint` in `matrix_graphs_block_card.dart`.
  - [x] Run `dart run build_runner build --delete-conflicting-outputs` and `flutter gen-l10n`.
  - [x] Run flutter unit tests and `flutter_audit_loop.py`.

- [x] **Phase 5: Rules & Directory Reference Update**
  - [x] Update `backend_v2/models/` in `.agents/rules/04_directory_reference.md` to document tripartite prompt subpackages (`common/`, `execution/`, `synthesis/`).

- [x] **Phase 6: Knowledge Items (KI) Synchronization**
  - [x] Update `ki_prompt_generation_architecture.md`.
  - [x] Update `ki_sdui_matrix_synthesis.md`.
  - [x] Update `ki_domain_model_prompt_separation.md`.

- [x] **Tier 7: Describe Architecture Synchronization & Rule Hardening**
  - [x] Ingested 6 Capability Pillars in `docs/architecture/` and meta-architecture.
  - [x] Anchored physical code paths and verified zero orphaned or rogue modules outside the 6 pillars.
  - [x] Synchronized `docs/architecture/` pillar documents to eliminate project phase labels and artificial Law/Enforcement framings, describing purely current system architecture.
  - [x] Hardened documentation rules in `.agents/workflows/tier7-describe-architecture.md`, `docs/architecture/00_README_META_ARCHITECTURE.md`, and `.agents/rules/00-antigravity-core.md` to permanently ban project phases and Law labels in architectural documentation.
  - [x] Verified prompt unit and AST guardrail test suite (55/55 passed).

## Session Handover Context
- **Achieved**: All 6 Phases of the implementation plan, the Tier 7 Architecture Synchronization, and the Documentation Rule Hardening have been completed, tested, and verified with 100% pass rates across all quality gates.
  - Phase 1: Pre-implementation cleanups & technical debt sweeps (fixed DTO constraint typo and English test strings).
  - Phase 2: Added `matrix_graph_length_constraint` across settings, domain models, DTOs, factories, and re-seeded baseline database.
  - Phase 3: Migrated execution prompts to `models/prompts/execution/`, added `common/` re-export shim, purged Phase 1 mandates and duplicate coaching tone from synthesis, implemented graceful skipping of empty directives with `logger.warning`, and injected `<section_budget>{matrix_graph_length_constraint}</section_budget>`.
  - Phase 4: Added `matrixGraphLengthConstraint` to Flutter Freezed `OutputProfile`, generated models and localization keys, added input field to `MatrixGraphsBlockCard`, fixed test fixtures, and verified all 133 studio unit tests and Flutter audit loop.
  - Phase 5: Updated `.agents/rules/04_directory_reference.md` to document the tripartite prompt layout.
  - Phase 6: Synchronized `ki_prompt_generation_architecture.md`, `ki_sdui_matrix_synthesis.md`, and `ki_domain_model_prompt_separation.md`.
  - Tier 7 & Rules: Streamlined all `docs/architecture/` pillar documents to pure as-built descriptions and codified the strict ban on project phases and Law labels into `tier7-describe-architecture.md`, `00_README_META_ARCHITECTURE.md`, and `00-antigravity-core.md`.
- **Learned**: Architectural documentation remains timeless and authoritative when it describes current functional mechanisms directly without project phase history or dogmatic meta-law framing.
- **Remaining**: None. Ready for atomic commit.
