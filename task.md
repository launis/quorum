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
- [ ] Constraint: `feature_sovereignty_mandate` - Preserve all cognitive features, metrics, and matrix metadata.
- [ ] Constraint: `the_zero_compromise_pledge` - Strict Pydantic V2 / Freezed schemas with extra='forbid' and zero naked dicts.
- [ ] Constraint: `zero_service_layer_fallbacks` - No fallback defaults; log warning and skip empty cosmetic directives without crashing.
- [ ] Constraint: `tripartite_phase_isolation` - Strict segregation: Phase 1 execution prompts in execution/, cross-phase in common/, Phase 2 in synthesis/.
- [ ] Constraint: `backwards_compat_barrel_reexport` - common/__init__.py must re-export relocated execution symbols for 1-hop callers.
- [ ] Constraint: `two_stage_testing` - Run isolated unit tests first, then backend_audit_loop and flutter_audit_loop.
- [ ] Constraint: `step_by_step_mode` - Stop after each cohesive milestone and request user approval before proceeding.

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

- [ ] **Phase 3: Tripartite Prompt Architecture Migration**
  - [ ] Move `global_mandates.py` from `common/` to `execution/`.
  - [ ] Move `field_prompts.py` from `common/` to `execution/`.
  - [ ] Update `models/prompts/execution/__init__.py` to re-export relocated symbols.
  - [ ] Update `models/prompts/common/__init__.py` to re-export execution symbols as backwards compatibility shim.
  - [ ] Update `models/prompts/__init__.py` root barrel exports.
  - [ ] Purge `DEFAULT_COACHING_TONE_MANDATE` and `SYNTHESIS_LENGTH_CONSTRAINT` from `style_directives.py`.
  - [ ] Rename `DEFAULT_*` system prompts in `synthesis_directives.py` and maintain backwards-compatible aliases.
  - [ ] Refactor `backend_v2/worker.py` synthesis prompt assembly:
    - [ ] Purge `GLOBAL_MANDATES_XML` from synthesis user messages.
    - [ ] Purge `DEFAULT_COACHING_TONE_MANDATE` and use dynamic `tone_instruction` (omit tone block if empty).
    - [ ] Replace `raise AppException` on empty directives with `logger.warning` and skip section.
    - [ ] Inject `<section_budget>{matrix_graph_length_constraint}</section_budget>` for matrix synthesis groups.
    - [ ] Clean unused imports in `worker.py`.
  - [ ] Update consumers and AST tests:
    - [ ] `test_ast_prompt_xml_sovereignty.py#L151` path update.
    - [ ] `test_global_mandates.py#L1` import update.
    - [ ] `test_field_prompts.py#L6` import update.
    - [ ] `test_extractive_sensor_service.py#L16` import update.
    - [ ] `test_worker_synthesis.py` assertions for directive skipping.
    - [ ] `test_output_profile_studio_parity.py` and `test_style_directives.py` test updates.

- [ ] **Phase 4: Frontend Dart Models & Studio UI**
  - [ ] Add `matrixGraphLengthConstraint` to Freezed `OutputProfile` in `output_profile.dart`.
  - [ ] Add localization keys in `app_en.arb` and `app_fi.arb`.
  - [ ] Add `TextFormField` bound to `payload.matrixGraphLengthConstraint` in `matrix_graphs_block_card.dart`.
  - [ ] Run `dart run build_runner build --delete-conflicting-outputs` and `flutter gen-l10n`.
  - [ ] Run flutter unit tests and `flutter_audit_loop.py`.

- [ ] **Phase 5: Rules & Directory Reference Update**
  - [ ] Update `backend_v2/models/` in `.agents/rules/04_directory_reference.md` to document tripartite prompt subpackages (`common/`, `execution/`, `synthesis/`).

- [ ] **Phase 6: Knowledge Items (KI) Synchronization**
  - [ ] Update `ki_prompt_generation_architecture.md`.
  - [ ] Update `ki_sdui_matrix_synthesis.md`.
  - [ ] Update `ki_domain_model_prompt_separation.md`.

## Session Handover Context
- **Achieved**: Pre-Flight codebase scan completed. Plan analyzed and all target files inspected. Task tracker initialized.
- **Learned**: Clean working tree. `variance_length_constraint` on `OutputProfileUpdateDTO` confirmed `ge=2000` typo. All 6 phases confirmed pending.
- **Remaining**: Execution of Phases 1-6 step-by-step.
