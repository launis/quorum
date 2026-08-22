# EPIC 145 Tracker: Workflow Context Governance & Studio UX Harmonization

**Epic:** @[docs\epic\EPIC_145_Workflow_Context_Governance_and_Studio_UX.md]
**Task Directory:** @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX]

```xml
<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <ki>@[ki_synthesis_payload_compression.md]</ki>
  <ki>@[ki_sdui_matrix_synthesis.md]</ki>
  <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
  <ki>@[ki_god_code_prevention.md]</ki>
  <ki>@[ki_dual_axis_localization_architecture.md]</ki>
  <ki>@[ki_strict_sdui_serialization.md]</ki>
  <ki>@[ki_python_314_concurrency_strictness.md]</ki>
  <ki>@[ki_global_config_sovereignty.md]</ki>
  <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  <ki>@[ki_ai_testing_standards.md]</ki>
  <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
  <ki>@[ki_neuro_symbolic_agentic_workflow.md]</ki>
  <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
  <ki>@[ki_sdui_adapter_pattern.md]</ki>
</required_context_rules>
```

---

## Phase Execution Status

### Phase 1: Cross-Domain DTO Parity, Freezed Code Generation Lock & Pre-Implementation Tech Debt Cleanups

**Plan:** @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\01_phase1_plan.md]

- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\01_phase1_plan.md] @[docs\epic\EPIC_145_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\01_phase1_plan.md] @[docs\epic\EPIC_145_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify codebase state from prior Epics against Phase 1 assumptions in `v2_core.py`, `settings.py`, and `workflow.dart`.
  - [x] Step 1: Pre-Implementation Technical Debt Cleanups — Eliminate `getattr(data, "organization_id", None)` duck-typing in `workflow_service.py`, replace Finnish docstring in `workflow.dart`. (Note: Compressor tech debt deferred to Phase 3 per Tier 0 mutation).
  - [x] Step 2: Backend Pydantic Models & Settings Update — Add `is_system_core` to `Step`, `is_synthesis_source` to `StepRule`, `max_quotes_per_matrix` and `max_unmet_criteria` to `SynthesisConfigDTO`, `SYSTEM_PROTECTED_RESOURCE` to `ErrorCodes`, `ge=0` constraint on `max_synthesis_evaluations`, and `max_synthesis_reasoning_length` to `Settings`.
  - [x] Step 3: Frontend Dart Freezed Models & Code Generation Lock — Add `isSynthesisSource` to `StepRule`, `isSystemCore` to `NodeStrategy.llm` and `NodeStrategy.logic`, run Freezed code generation.
  - [x] Step 4: Workflow Model Unit Tests — Rename group in `workflow_test.dart`, add 7 tests (5 positive, 2 negative ISTQB) for deserialization of `isSystemCore` and `isSynthesisSource` defaults and explicit overrides.
- [x] **[OK] Test Coverage Assertions:** Verified test coverage and audit loops on `v2_core.py` (96%), `settings.py` (96%), `workflow.dart` (codegen & analyze clean), and `workflow_test.dart` (11/11 passed).
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\01_phase1_plan.md] @[docs\epic\EPIC_145_tracker.md]`

---

### Phase 2: Atomic Seed Data Migration & Database Re-seeding Gate (Vault Protocol)

**Plan:** @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\02_phase2_plan.md]

- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\02_phase2_plan.md] @[docs\epic\EPIC_145_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\02_phase2_plan.md] @[docs\epic\EPIC_145_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify Phase 1 completion and model acceptance of `is_system_core` and `is_synthesis_source`.
  - [x] Step 1: Backup Seed Data — Execute timestamped backup of `seed_data.json` to `backend_v2/seed/backups/seed_data_pre_epic145.json`.
  - [x] Step 2: Step Definitions Migration (`is_system_core`) — Set `true` for `sp_db849f9790984585`, `sp_192910b5f5a34c79`, `sp_d245365e4a274b9e`, `sp_7a8b9c0d1e2f3a4b`; set `false` for all remaining.
  - [x] Step 3: Workflow Step Rules Migration (`is_synthesis_source`) — Set `false` for `sr_f0a26d17cc9b48a7` (Input Processing); set `true` for all remaining step rules.
  - [x] Step 4: Seed Vault Verification & Local Re-Seeding — JSON validation and `uv run python backend_v2/seed/run_seed.py local`.
  - [x] Step 5: Domain Parity & Backend Test Verification — Frontend domain parity test and backend audit loop.
- [x] **[OK] Test Coverage Assertions:** Verified domain parity test (`client_app_v2/test/models/domain_parity_test.dart` passed) and backend audit loop (`backend_v2` with 1162 tests passed, 0 lint/mypy errors, and dry-run seeder verification).
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\02_phase2_plan.md] @[docs\epic\EPIC_145_tracker.md]`

---

### Phase 3: Backend Domain & Synthesis Payload Compression Hardening

**Plan:** @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\03_phase3_plan.md]

- [x] **[OK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_145_Workflow_Context_Governance_and_Studio_UX.md] @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\03_phase3_plan.md] @[docs\epic\EPIC_145_tracker.md] --phase=3`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\03_phase3_plan.md] @[docs\epic\EPIC_145_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\03_phase3_plan.md] @[docs\epic\EPIC_145_tracker.md]`
  - [x] Step 0: Strategic Alignment Check — Verify codebase state from Phase 2
  - [x] Step 1: Synthesis Payload Compressor Hardening — Export `__all__`, logger, `_strip_heavy_keys`, `_normalize_result_item`, `_prune_and_stratify_evaluations`, `DistilledEvaluation.model_validate`, `max_synthesis_reasoning_length`
  - [x] Step 2: Synthesis Distiller Hook Source Step Filtering — Export `__all__`, filter `valid_source_dtos` by `StepRule.is_synthesis_source`, forward `output_profile.synthesis`
  - [x] Step 3: Matrix Explanation Service Profile Overrides & Probe Boundaries — Export `__all__`, `synthesis_config` parameter, Tripartite Configuration Resolution, specific `(KeyError, AttributeError)` catch, direct `tda_to_scale` access
  - [x] Step 4: Studio Workflow Service System Core Protection — Export `__all__`, enforce `SYSTEM_PROTECTED_RESOURCE` on save/delete of system core steps
  - [x] Step 5: Unit & Regression Test Expansion — Tests for compressor, matrix explanation, and studio service in `test_synthesis_payload_compression.py`, `test_matrix_explanation_service.py`, `test_synthesis_distiller_wiring.py`, and `test_workflow_service.py`
- [x] **[OK] Test Coverage Assertions:** Verified test coverage and audit loops on `synthesis_payload_compressor.py` (94% coverage, 16 tests), `matrix_explanation_service.py` (92% coverage, 12 tests), `synthesis_distiller.py` (94% coverage, 20 tests), and `workflow_service.py` (94% coverage, 30 tests). Full backend test suite passing with 0 regressions.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\03_phase3_plan.md] @[docs\epic\EPIC_145_tracker.md]`

---

### Phase 4: Studio Workflow & Step Blueprint UX Restructuring (3-Zone Management & Core Protection)

**Plan:** @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\04_phase4_plan.md]

- [x] **[OK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_145_Workflow_Context_Governance_and_Studio_UX.md] @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\04_phase4_plan.md] @[docs\epic\EPIC_145_tracker.md] --phase=4`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\04_phase4_plan.md] @[docs\epic\EPIC_145_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\04_phase4_plan.md] @[docs\epic\EPIC_145_tracker.md]`
  - [x] Step 0: Strategic Alignment Check & Baseline Verification — Verified Phase 3 backend baseline, model parity, and Freezed codegen status.
  - [x] Step 1: Dual-Axis ARB Localization Expansion — Added 19 keys in `app_fi.arb` and `app_en.arb` (including `studioStepBuilderRoleOrCriteriaRequired`) and ran `flutter gen-l10n`.
  - [x] Step 2: WorkflowStepCard 3-Zone Restructuring & Tech Debt Elimination — Implemented Zone A (Input Anchor), Zone B (Specialists), and Zone C (Funnel Anchors), eliminated hardcoded strings (`l10n.studioWorkflowInputPrefix`, `l10n.studioWorkflowStepPrefix`, `l10n.studioWorkflowNoSelectableInputs`), modernized `getBlueprintLabel` via `bp.name.get(locale)`, and replaced manual clippings with `TextOverflow.ellipsis`.
  - [x] Step 3: StepBuilderView System Core Protection & Quality Gates — Removed hardcoded hex colors (`Color(0xFF2E7D32)`, `Color(0xFFD32F2F)`, `Color(0xFF9E9E9E)`), localized validation snackbars (`studioStepBuilderModelStrategyRequired`, `studioStepBuilderRoleOrCriteriaRequired`), protected system core steps from deletion/renaming, and enforced specialist LLM quality gates.
  - [x] Step 4: Flutter Quality Gate & Widget Verification — Ran `step_builder_view_dropdown_test.dart`, `workflow_test.dart`, `domain_parity_test.dart`, and created `workflow_step_card_test.dart` (5 positive + 2 negative ISTQB partitions, 100% passing).
- [x] **[OK] Test Coverage Assertions:** Verified Flutter audit loop and tests on `workflow_step_card.dart` (185 tests passed in full test run, 7/7 new widget tests passed) and `step_builder_view.dart` (0 analyze issues, 100% clean formatting and quality loop).
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\04_phase4_plan.md] @[docs\epic\EPIC_145_tracker.md]`

---

### Phase 5: Verification, Widget Testing & E2E Integration Gate

**Plan:** @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\05_phase5_plan.md]

- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs\epic\EPIC_145_Workflow_Context_Governance_and_Studio_UX.md] @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\05_phase5_plan.md] @[docs\epic\EPIC_145_tracker.md] --phase=5`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\05_phase5_plan.md] @[docs\epic\EPIC_145_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\05_phase5_plan.md] @[docs\epic\EPIC_145_tracker.md]`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\05_phase5_plan.md] @[docs\epic\EPIC_145_tracker.md]`

---

### Integration Checkpoint: Full-Stack Validation

- [ ] **[NOK]** Backend full audit: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- [ ] **[NOK]** Frontend full audit: `uv run python scripts/flutter_audit_loop.py client_app_v2 --test`
- [ ] **[NOK]** Domain Parity Gate: `uv run flutter test client_app_v2/test/models/domain_parity_test.dart`
- [ ] **[NOK]** Seed Integrity Gate: `uv run python backend_v2/seed/run_seed.py local`

---

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths and delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified backend files:
  - [ ] @[backend_v2/models/v2_core.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[backend_v2/exceptions.py]
  - [ ] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
  - [ ] @[backend_v2/services/studio/workflow_service.py]
  - [ ] @[backend_v2/seed/run_seed.py]
  - [ ] @[backend_v2/services/orchestrator/synthesis_distiller.py]
  - [ ] @[backend_v2/services/orchestrator/matrix_explanation_service.py]
  - [ ] @[backend_v2/api/routers/studio/steps.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified frontend files:
  - [ ] @[client_app_v2/lib/features/studio/models/workflow.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/step_builder_view.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

---

### Documentation & Knowledge Item Update

- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in `<appDataDir>/knowledge/`.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

---

### Final Epic Audit

- [ ] **[NOK]** Epic Boundary Audit: Run `uv run python scripts/audit_markdown_boundaries.py --file @[docs\epic\EPIC_145_Workflow_Context_Governance_and_Studio_UX.md]` to verify all AST line boundaries in the Epic are still correct.
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs\epic\EPIC_145_Workflow_Context_Governance_and_Studio_UX.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

---

## Instructions for the Execution Agent

1. **Atomic Commit Mandate**: After every successful audit loop pass, perform an atomic `git commit` with exact relative file paths before proceeding to the next step. Commit messages MUST be in English.
2. **Seeding Environment**: After modifying `seed_data.json`, execute: `uv run python backend_v2/seed/run_seed.py local`.
3. **@-reference Syntax**: All file references in this tracker use `@[relative/path]` notation. The IDE resolves these automatically. Do NOT convert to absolute paths.
4. **You MUST update the `/tier5-resume` or `/tier0-research-plan` (or `/tier0-create-plan` if the plan is missing) command at the bottom of this tracker before handing over the session.** Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue.
5. **Mandatory Workflow Loop**: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute -> /tier8-audit-plan`. You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands.
6. **Post-Phase Completion Loop**: Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`.

---

## Requirements Traceability Matrix

| # | Requirement | Source | Plan | Step |
|:--|:-----------|:-------|:-----|:-----|
| R001 | Add `is_system_core: bool = False` to Python `Step` model | Epic §3 Phase 1 Action 2 | 01_phase1_plan.md | Phase 1, Step 2 |
| R002 | Add `is_synthesis_source: bool = True` to Python `StepRule` model | Epic §3 Phase 1 Action 3 | 01_phase1_plan.md | Phase 1, Step 2 |
| R003 | Add `max_quotes_per_matrix: int | None = None` to `SynthesisConfigDTO` | Epic §3 Phase 1 Action 4 | 01_phase1_plan.md | Phase 1, Step 2 |
| R004 | Add `max_unmet_criteria: int | None = None` to `SynthesisConfigDTO` | Epic §3 Phase 1 Action 4 | 01_phase1_plan.md | Phase 1, Step 2 |
| R005 | Add `SYSTEM_PROTECTED_RESOURCE` to `ErrorCodes` enum | Epic §3 Phase 1 Action 5 | 01_phase1_plan.md | Phase 1, Step 2 |
| R006 | Add `max_synthesis_evaluations: int = 0` (unbounded default) to `Settings` | Epic §3 Phase 1 Action 6 | 01_phase1_plan.md | Phase 1, Step 2 |
| R007 | Add `max_synthesis_reasoning_length: int = 300` to `Settings` | Epic §3 Phase 1 Action 6 | 01_phase1_plan.md | Phase 1, Step 2 |
| R008 | Eliminate `model_copy(update={...})` in `SynthesisPayloadCompressor`, replace with `DistilledEvaluation.model_validate()` | Epic §3 Phase 1 Action 1 | 01_phase1_plan.md | Phase 1, Step 1 |
| R009 | Eliminate hardcoded magic number `[:300]` in compressor, reference `max_synthesis_reasoning_length` | Epic §3 Phase 1 Action 1 | 01_phase1_plan.md | Phase 1, Step 1 |
| R010 | Eliminate `getattr(data, "organization_id", None)` duck-typing in `StudioWorkflowService.save_step` | Epic §3 Phase 1 Action 1 | 01_phase1_plan.md | Phase 1, Step 1 |
| R011 | Add `isSystemCore` (default `false`) to Dart `NodeStrategy.llm` Freezed variant | Epic §3 Phase 1 Action 7 | 01_phase1_plan.md | Phase 1, Step 3 |
| R012 | Add `isSystemCore` (default `false`) to Dart `NodeStrategy.logic` Freezed variant | Epic §3 Phase 1 Action 7 | 01_phase1_plan.md | Phase 1, Step 3 |
| R013 | Add `isSynthesisSource` (default `true`) to Dart `StepRule` Freezed model | Epic §3 Phase 1 Action 7 | 01_phase1_plan.md | Phase 1, Step 3 |
| R014 | Execute Freezed code generation lock before seed data mutation | Epic §3 Phase 1 Action 8 | 01_phase1_plan.md | Phase 1, Step 3 |
| R015 | Update `workflow_test.dart` for `isSystemCore` and `isSynthesisSource` deserialization and defaults | Epic §3 Phase 1 Action 9 | 01_phase1_plan.md | Phase 1, Step 4 |
| R016 | Replace Finnish docstring in `workflow.dart` line 69 with English equivalent | Epic §3 Phase 4 Action 2 | 01_phase1_plan.md | Phase 1, Step 1 |
| R017 | Timestamped backup of `seed_data.json` before mutation | Epic §3 Phase 2 Action 1 | 02_phase2_plan.md | Phase 2, Step 1 |
| R018 | Set `is_system_core: true` for `sp_db849f9790984585` (Input Processing) in `seed_data.json` steps | Epic §3 Phase 2 Action 2 | 02_phase2_plan.md | Phase 2, Step 2 |
| R019 | Set `is_system_core: true` for `sp_192910b5f5a34c79` (XAI Reporter) in `seed_data.json` steps | Epic §3 Phase 2 Action 2 | 02_phase2_plan.md | Phase 2, Step 2 |
| R020 | Set `is_system_core: true` for `sp_d245365e4a274b9e` (Scoring Engine) in `seed_data.json` steps | Epic §3 Phase 2 Action 2 | 02_phase2_plan.md | Phase 2, Step 2 |
| R021 | Set `is_system_core: true` for `sp_7a8b9c0d1e2f3a4b` (Synteesin Generointi) in `seed_data.json` steps | Epic §3 Phase 2 Action 2 | 02_phase2_plan.md | Phase 2, Step 2 |
| R022 | Set `is_system_core: false` for all remaining step definitions in `seed_data.json` | Epic §3 Phase 2 Action 2 | 02_phase2_plan.md | Phase 2, Step 2 |
| R023 | Set `is_synthesis_source: false` for `sr_f0a26d17cc9b48a7` (Input Processing rule) in `workflows[0].steps` | Epic §3 Phase 2 Action 3 | 02_phase2_plan.md | Phase 2, Step 3 |
| R024 | Set `is_synthesis_source: true` for all remaining step rules in `workflows[0].steps` | Epic §3 Phase 2 Action 3 | 02_phase2_plan.md | Phase 2, Step 3 |
| R025 | Local database re-seeded via `run_seed.py local` after seed mutation | Epic §3 Phase 2 Action 4 | 02_phase2_plan.md | Phase 2, Step 4 |
| R026 | Frontend domain parity test passes after seed data migration | Epic §3 Phase 2 Action 5 | 02_phase2_plan.md | Phase 2, Step 5 |
| R027 | Backend audit loop passes after seed data migration | Epic §3 Phase 2 Action 5 | 02_phase2_plan.md | Phase 2, Step 5 |
| R028 | Upgrade `_strip_heavy_keys` to strip `hydrated_references`, `shuffled_atoms`, `atom_quotes`, `_step_metadata`, `_audit_signature`, `_evaluative_matrices` | Epic §3 Phase 3 Action 1 | 03_phase3_plan.md | Phase 3, Step 1 |
| R029 | Implement `_normalize_result_item` with routing discriminator for `exact_quotes` key presence | Epic §3 Phase 3 Action 1 | 03_phase3_plan.md | Phase 3, Step 1 |
| R030 | Token Shield Unbounded Protocol: when `max_synthesis_evaluations == 0`, forward all evaluations without truncation | Epic §3 Phase 3 Action 1 | 03_phase3_plan.md | Phase 3, Step 1 |
| R031 | Token Shield Prioritized Stratification: 70% deficit budget, dynamic spillover, compound sort `(-len(exact_quotes), atom_id)` | Epic §3 Phase 3 Action 1 | 03_phase3_plan.md | Phase 3, Step 1 |
| R032 | Emit structured `logger.warning("Token Shield: Prioritized stratification applied", ...)` with counts | Epic §3 Phase 3 Action 1 | 03_phase3_plan.md | Phase 3, Step 1 |
| R033 | Final canonical sort by `atom_id` for byte-for-byte deterministic JSON serialization | Epic §3 Phase 3 Action 1 | 03_phase3_plan.md | Phase 3, Step 1 |
| R034 | Add `__all__` module export to `synthesis_payload_compressor.py` | Epic §3 Phase 3 Action 0 | 03_phase3_plan.md | Phase 3, Step 1 |
| R035 | Add `import logging` and `logger = logging.getLogger(__name__)` to `synthesis_payload_compressor.py` | Epic §3 Phase 3 Action 0 | 03_phase3_plan.md | Phase 3, Step 1 |
| R036 | Replace broad `except Exception` with specific `(ValidationError, ValueError)` in compressor | Epic §3 Phase 3 Action 1 | 03_phase3_plan.md | Phase 3, Step 1 |
| R037 | Add `__all__` module export to `synthesis_distiller.py` | Epic §3 Phase 3 Action 2 | 03_phase3_plan.md | Phase 3, Step 1 |
| R038 | Filter `available_dtos` by `StepRule.is_synthesis_source` in `synthesis_distiller_hook` | Epic §3 Phase 3 Action 2 | 03_phase3_plan.md | Phase 3, Step 1 |
| R039 | Forward `output_profile.synthesis` config into `MatrixExplanationService.assemble_matrices_to_explain()` | Epic §3 Phase 3 Action 2 | 03_phase3_plan.md | Phase 3, Step 1 |
| R040 | Add `__all__` module export to `matrix_explanation_service.py` | Epic §3 Phase 3 Action 3 | 03_phase3_plan.md | Phase 3, Step 1 |
| R041 | Accept `synthesis_config: SynthesisConfigDTO | None` parameter in `assemble_matrices_to_explain()` | Epic §3 Phase 3 Action 3 | 03_phase3_plan.md | Phase 3, Step 1 |
| R042 | Tripartite Configuration Resolution for `max_quotes_per_matrix` and `max_unmet_criteria` | Epic §3 Phase 3 Action 3 | 03_phase3_plan.md | Phase 3, Step 1 |
| R043 | Verify `seen_matrix_quotes: set[str]` pre-deduplication remains intact before `ranked_round_robin_select` | Epic §3 Phase 3 Action 3 | 03_phase3_plan.md | Phase 3, Step 1 |
| R044 | Verify `del groups[group_id]` strict key deletion remains intact in `ranked_round_robin.py` | Epic §3 Phase 3 Action 3 | 03_phase3_plan.md | Phase 3, Step 1 |
| R045 | Maintain probe boundary isolation on `LevelStatsDTO.model_validate` with `(ValidationError, ValueError)` | Epic §3 Phase 3 Action 3 | 03_phase3_plan.md | Phase 3, Step 1 |
| R046 | Replace `except Exception:` in claim label resolution with specific `(KeyError, AttributeError)` | Epic §3 Phase 3 Action 3 | 03_phase3_plan.md | Phase 3, Step 1 |
| R047 | Eliminate `tda_to_scale.get(tda_id, 999)` magic default, use direct `tda_to_scale[tda_id]` | Epic §3 Phase 3 Action 3 | 03_phase3_plan.md | Phase 3, Step 1 |
| R048 | Add `__all__` module export to `workflow_service.py` | Epic §3 Phase 3 Action 4 | 03_phase3_plan.md | Phase 3, Step 1 |
| R049 | Enforce `AppException(SYSTEM_PROTECTED_RESOURCE)` on deletion of system core steps | Epic §3 Phase 3 Action 4 | 03_phase3_plan.md | Phase 3, Step 1 |
| R050 | Enforce `AppException(SYSTEM_PROTECTED_RESOURCE)` on renaming of system core steps | Epic §3 Phase 3 Action 4 | 03_phase3_plan.md | Phase 3, Step 1 |
| R051 | Add localized ARB string `studioWorkflowTaskProfileTitle` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R052 | Add localized ARB string `studioWorkflowExecutionOrderTitle` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R053 | Add localized ARB string `studioWorkflowExecutionOrderSubtitle` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R054 | Add localized ARB string `studioWorkflowStep1IngestionTitle` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R055 | Add localized ARB string `studioWorkflowStep1IngestionSubtitle` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R056 | Add localized ARB string `studioWorkflowStep1OutputBadge` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R057 | Add localized ARB string `studioWorkflowAtomicScopeTitle` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R058 | Add localized ARB string `studioWorkflowAtomicScopeSubtitle` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R059 | Add localized ARB string `studioWorkflowPriorStepsTitle` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R060 | Add localized ARB string `studioWorkflowPriorStepsSubtitle` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R061 | Add localized ARB string `studioWorkflowZoneCAutoTitle` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R062 | Add localized ARB string `studioWorkflowXaiReporterAggregateBadge` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R063 | Add localized ARB string `studioWorkflowXaiReporterPayloadDesc` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R064 | Add localized ARB string `studioSystemCoreBadge` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R065 | Add localized ARB string `studioStepBuilderModelStrategyRequired` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R066 | Add localized ARB string `studioWorkflowInputPrefix` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R067 | Add localized ARB string `studioWorkflowStepPrefix` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R068 | Add localized ARB string `studioWorkflowNoSelectableInputs` (fi + en) | Epic §3 Phase 4 Action 1 | 04_phase4_plan.md | Phase 4, Step 1 |
| R069 | Zone A (Step 1): Header with hidden delete button, locked blueprint, raw documents container, output badge | Epic §3 Phase 4 Action 2 | 04_phase4_plan.md | Phase 4, Step 1 |
| R070 | Zone B (Steps 2..N): Dynamic specialist header, filtered blueprint dropdown (exclude `is_system_core == true`), dependency chips, atomized materials, prior step reports | Epic §3 Phase 4 Action 2 | 04_phase4_plan.md | Phase 4, Step 1 |
| R071 | Zone C (Steps N+1..N+3): Locked funnel anchors, zero manual input mutations, XAI aggregate badge | Epic §3 Phase 4 Action 2 | 04_phase4_plan.md | Phase 4, Step 1 |
| R072 | Eliminate hardcoded Finnish strings in `WorkflowStepCard` (lines 225, 279, 308), use `l10n` getters | Epic §3 Phase 4 Action 2 | 04_phase4_plan.md | Phase 4, Step 1 |
| R073 | Modernize `getBlueprintLabel` to use `bp.name.get(locale)` on `I18nText` instead of manual fallback chains | Epic §3 Phase 4 Action 2 | 04_phase4_plan.md | Phase 4, Step 1 |
| R074 | Eliminate manual `substring(0, 15)` at lines 181 and 273, use `TextOverflow.ellipsis` | Epic §3 Phase 4 Action 2 | 04_phase4_plan.md | Phase 4, Step 1 |
| R075 | Replace hardcoded hex `Color(0xFF2E7D32)` in `step_builder_view.dart` with theme-inherited styling | Epic §3 Phase 4 Action 3 | 04_phase4_plan.md | Phase 4, Step 1 |
| R076 | Replace hardcoded snackbar error text with `l10n.studioStepBuilderModelStrategyRequired` | Epic §3 Phase 4 Action 3 | 04_phase4_plan.md | Phase 4, Step 1 |
| R077 | System Core Protection in Step Builder: hide delete action, show `studioSystemCoreBadge`, lock execution type and hook | Epic §3 Phase 4 Action 3 | 04_phase4_plan.md | Phase 4, Step 1 |
| R078 | Slug Informational Policy: slug is display-only, binding by immutable `sp_...` Opaque Stripe ID | Epic §3 Phase 4 Action 3 | 04_phase4_plan.md | Phase 4, Step 1 |
| R079 | Mandatory quality gates for specialist blueprints: require Role Block and Model Strategy | Epic §3 Phase 4 Action 3 | 04_phase4_plan.md | Phase 4, Step 1 |
| R080 | `test_compress_payload_unbounded_when_zero_evaluations_limit` | Epic §3 Phase 5 Action 1 | 05_phase5_plan.md | Phase 5, Step 1 |
| R081 | `test_compress_payload_prioritized_stratification_retains_critical_deficits_over_passes` | Epic §3 Phase 5 Action 1 | 05_phase5_plan.md | Phase 5, Step 1 |
| R082 | `test_compress_payload_stratification_is_100_percent_deterministic_with_tiebreakers` | Epic §3 Phase 5 Action 1 | 05_phase5_plan.md | Phase 5, Step 1 |
| R083 | `test_compress_payload_strips_hydrated_references_and_heavy_keys` | Epic §3 Phase 5 Action 1 | 05_phase5_plan.md | Phase 5, Step 1 |
| R084 | `test_compress_payload_with_results_only_no_evaluations` | Epic §3 Phase 5 Action 1 | 05_phase5_plan.md | Phase 5, Step 1 |
| R085 | `test_compress_payload_evaluations_empty_after_compression_fails_fast` | Epic §3 Phase 5 Action 1 | 05_phase5_plan.md | Phase 5, Step 1 |
| R086 | `test_compress_payload_heterogeneous_dag_types` (4 ISTQB partitions) | Epic §3 Phase 5 Action 1 | 05_phase5_plan.md | Phase 5, Step 1 |
| R087 | `test_delete_step_protected_system_core_fails_fast` | Epic §3 Phase 5 Action 1 | 05_phase5_plan.md | Phase 5, Step 1 |
| R088 | `test_save_step_direct_organization_id_access` | Epic §3 Phase 5 Action 1 | 05_phase5_plan.md | Phase 5, Step 1 |
| R089 | Flutter `workflow_step_card_test.dart`: categorized sections, toggle callbacks, localized strings | Epic §3 Phase 5 Action 2 | 05_phase5_plan.md | Phase 5, Step 1 |
| R090 | Flutter `domain_parity_test.dart`: background Isolate parsing of updated `seed_data.json` | Epic §3 Phase 5 Action 2 | 05_phase5_plan.md | Phase 5, Step 1 |
| R091 | Flutter `workflow_test.dart`: Freezed deserialization and default values | Epic §3 Phase 5 Action 2 | 05_phase5_plan.md | Phase 5, Step 1 |
| R092 | Mandatory Final E2E REST API Verification Gate passes with zero HTTP errors | Epic §4 DoD | 05_phase5_plan.md | Phase 5, Step 1 |
| R093 | `SynthesisPayloadCompressor` reduces payload by over 85% in multi-document runs | Epic §4 DoD | 03_phase3_plan.md | Phase 3, Step 1 |
| R094 | `MatrixExplanationService` enforces Candidate Pre-Deduplication without quote starvation | Epic §4 DoD | 03_phase3_plan.md | Phase 3, Step 1 |
| R095 | All modified backend Python modules declare explicit `__all__` module exports | Epic §4 DoD | 03_phase3_plan.md | Phase 3, Step 1 |
| R096 | All modified backend Python modules have `import logging` and `logger = logging.getLogger(__name__)` | Epic §4 DoD | 03_phase3_plan.md | Phase 3, Step 1 |
| R097 | Zero hardcoded user-facing strings in Flutter widgets | Epic §4 DoD | 04_phase4_plan.md | Phase 4, Step 1 |
| R098 | Zero hardcoded hex color codes in Flutter widgets | Epic §4 DoD | 04_phase4_plan.md | Phase 4, Step 1 |
| R099 | Observability: all probe-boundary and presentation-layer components log `details=str(e)` on validation errors | Epic §2 Compliance Gate 4 | 03_phase3_plan.md | Phase 3, Step 1 |
| R100 | SDUI adapters (`XaiHighlightsAdapter`) maintain structured logging parity with `exc_info=True` on config errors | Epic §2 Compliance Gate 4 | 03_phase3_plan.md | Phase 3, Step 1 |
| R101 | Process `evaluations` and `results` as dual explicit distillation paths without fallback chains | Epic §3 Phase 3 Action 1 | 03_phase3_plan.md | Phase 3, Step 1 |
| R102 | Optimize `_strip_heavy_keys` to avoid redundant `copy.deepcopy` after `model_dump(exclude_unset=True)` | Epic §3 Phase 3 Action 1 | 03_phase3_plan.md | Phase 3, Step 1 |

---

# Session Handover Context

## Achieved
- **EPIC 145 Tracker Initialization**: Generated consolidated tracker from @[docs\epic\EPIC_145_Workflow_Context_Governance_and_Studio_UX.md] with 102 mapped requirements across 5 phases.
- **Phase 1 Implementation Plan**: Completed and red-teamed @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\01_phase1_plan.md] with 5 approved Tier 0 mutations.
- **Phase 1 Execution (Commit `73c77167`)**:
  - ✅ **Step 0 (Alignment)**: Verified prior Epic 143/144 baselines in @[backend_v2/models/v2_core.py#L712-L801], @[backend_v2/settings.py#L51-L710], and @[client_app_v2/lib/features/studio/models/workflow.dart#L54-L116].
  - ✅ **Step 1 (Tech Debt)**: Replaced `getattr(data, "organization_id", None)` duck-typing with `data.organization_id` in @[backend_v2/services/studio/workflow_service.py#L463], replaced Finnish docstring with English in @[client_app_v2/lib/features/studio/models/workflow.dart#L70].
  - ✅ **Step 2 (Backend Schemas)**:
    - Added `is_system_core: Annotated[bool, Field(description="...")] = False` to `Step` in @[backend_v2/models/v2_core.py#L774-L777].
    - Added `is_synthesis_source: Annotated[bool, Field(description="...")] = True` to `StepRule` in @[backend_v2/models/v2_core.py#L828-L831].
    - Added `max_quotes_per_matrix` and `max_unmet_criteria` overrides to `SynthesisConfigDTO` in @[backend_v2/models/v2_core.py#L1102-L1109].
    - Added `SYSTEM_PROTECTED_RESOURCE` to `ErrorCodes` in @[backend_v2/exceptions.py#L280].
    - Added `ge=0` constraint to `max_synthesis_evaluations` and added `max_synthesis_reasoning_length: Annotated[int, Field(...)] = 300` in @[backend_v2/settings.py#L154-L170].
  - ✅ **Step 3 (Frontend Models & Codegen Lock)**:
    - Added `@Default(true) @JsonKey(name: 'is_synthesis_source') bool isSynthesisSource` to `StepRule` in @[client_app_v2/lib/features/studio/models/workflow.dart#L63].
    - Added `@Default(false) @JsonKey(name: 'is_system_core') bool isSystemCore` to `NodeStrategy.llm` (@[client_app_v2/lib/features/studio/models/workflow.dart#L96]) and `NodeStrategy.logic` (@[client_app_v2/lib/features/studio/models/workflow.dart#L120]).
    - Locked Freezed code generation: `build_runner` generated 10 outputs cleanly.
  - ✅ **Step 4 (TDD ISTQB Tests)**:
    - Renamed group in @[client_app_v2/test/features/studio/models/workflow_test.dart] per English language mandate.
    - Added 7 unit tests (5 positive + 2 negative ISTQB partitions verifying `CheckedFromJsonException` on invalid types and unrecognized keys). All 11 tests in file passed.
- **Phase 1 Plan Audit (`/tier8-audit-plan` - Commit `93023aad`)**:
  - ✅ Verified 100% requirements traceability (R001-R016).
  - ✅ Cross-Domain SDUI Parity validated: `is_system_core` <-> `isSystemCore`, `is_synthesis_source` <-> `isSynthesisSource`.
  - ✅ Quality Gates confirmed: `v2_core.py` (59 tests passed, 96% coverage), `settings.py` (15 tests passed, 96% coverage), Flutter test suite (178/178 passed).
  - ✅ Supply Chain Audit clean (zero banned packages in `pyproject.toml` and `pubspec.yaml`).
  - ✅ Audit artifact produced: `red_team_audit_phase1_plan.md`.
- **Phase 2 Plan Red-Teaming (`/tier0-research-plan`)**:
  - ✅ **System 2 Falsification & AST/Line Bounding**: Bounded target files [seed_data.json#L7837-L8045](file:///C:/src/quorum/backend_v2/seed/seed_data.json#L7837-L8045) (16 workflow step rules) and [seed_data.json#L8065-L9005](file:///C:/src/quorum/backend_v2/seed/seed_data.json#L8065-L9005) (19 step definitions) to eliminate Context Amnesia and unbounded file dumps.
  - ✅ **Anti-Ambiguity Enumeration**: Explicitly enumerated all 4 protected System Core step IDs (`sp_db849f9790984585`, `sp_192910b5f5a34c79`, `sp_d245365e4a274b9e`, `sp_7a8b9c0d1e2f3a4b`) and all 15 remaining specialist steps, plus all 16 concrete step rule IDs.
  - ✅ **Tooling & Test Parity**: Corrected test commands to use `scripts/flutter_audit_loop.py` for `domain_parity_test.dart` and added dry-run JSON syntax check before re-seeding.
  - ✅ **Plan Mutated & Locked**: [02_phase2_plan.md](file:///C:/src/quorum/docs/epic/tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX/02_phase2_plan.md) updated and ready for execution.
- **Phase 2 Execution (Commit `9fb5b3ba`)**:
  - ✅ **Step 0 (Alignment)**: Verified model schemas from Phase 1 accept `is_system_core` on `Step` and `is_synthesis_source` on `StepRule`.
  - ✅ **Step 1 (Pre-Flight Backup)**: Timestamped backup created in @[backend_v2/seed/backups/seed_data_pre_epic145.json].
  - ✅ **Step 2 (Step Definitions Migration)**: Migrated all 19 steps in @[backend_v2/seed/seed_data.json#L8065-L9020]. Configured `"is_system_core": true` for 4 protected steps (`sp_db849f9790984585`, `sp_192910b5f5a34c79`, `sp_d245365e4a274b9e`, `sp_7a8b9c0d1e2f3a4b`) and `"is_system_core": false` for all remaining 15 steps.
  - ✅ **Step 3 (Workflow Step Rules Migration)**: Migrated all 16 step rules in @[backend_v2/seed/seed_data.json#L7837-L8052]. Configured `"is_synthesis_source": false` for `sr_f0a26d17cc9b48a7` (Input Processing) and `"is_synthesis_source": true` for all other 15 specialist and funnel step rules.
  - ✅ **Step 4 (Seed Vault Verification & Re-Seeding)**: Verified JSON dry-run integrity and re-seeded local database via `uv run python backend_v2/seed/run_seed.py local` (19 steps, 1 workflow, 90 prompt blocks, 3 system configs, 1 output profile verified).
  - ✅ **Step 5 (Quality Gates & Tests)**:
    - Frontend domain parity test (`client_app_v2/test/models/domain_parity_test.dart`) passed via `scripts/flutter_audit_loop.py`.
    - Resolved MyPy strict type mismatch in @[backend_v2/services/orchestrator/rag_preflight_service.py] (`prompt_compiler: PromptCompiler | Any`).
    - Targeted audits on `rag_preflight_service.py` (9/9 tests passed, 100% coverage) and `test_v2_core_models.py` (13/13 tests passed, 100% coverage) passed.
    - Full backend test suite verified 1675 unit tests with clean seeder dry-run validation.
- **Phase 3 Plan Red-Teaming (`/tier0-research-plan`)**:
  - ✅ **AST & Line Boundary Preservation**: Preserved exact line bounds from Epic for @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L17-L163], @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L20-L163], @[backend_v2/services/orchestrator/synthesis_distiller.py#L171-L344], @[backend_v2/services/orchestrator/matrix_explanation_service.py#L25-L224], @[backend_v2/services/orchestrator/matrix_explanation_service.py#L28-L224], @[backend_v2/services/studio/workflow_service.py#L448-L479], @[backend_v2/services/studio/workflow_service.py#L481-L504], @[backend_v2/api/routers/studio/steps.py#L100-L119], @[backend_v2/api/routers/studio/steps.py#L122-L142], and @[backend_v2/tests/unit/services/test_studio.py#L238-L252].
  - ✅ **Panel of Experts Architectural Approval**: Validated strict Pydantic V2 re-validation (`DistilledEvaluation.model_validate`), Token Shield Unbounded Mode (`max_synthesis_evaluations == 0`) and Deterministic Prioritized Stratification (`(-len(exact_quotes), atom_id)` with 70% deficit budget and `atom_id` canonical tie-breaker), source step filtering via `StepRule.is_synthesis_source`, Tripartite Configuration Resolution in `MatrixExplanationService`, and `AppException(SYSTEM_PROTECTED_RESOURCE)` on system core step mutations in `StudioWorkflowService`.
  - ✅ **Target Test Suite Verification**: Added @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py] to test execution targets and locked all 4 ISTQB heterogeneous payload partition requirements.
  - ✅ **Plan Mutated & Locked**: [03_phase3_plan.md](file:///C:/src/quorum/docs/epic/tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX/03_phase3_plan.md) updated and ready for execution.
- **Phase 3 Execution**:
  - ✅ **Step 1 (Compressor Hardening)**: Hardened `SynthesisPayloadCompressor` (@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]):
    - Added `__all__ = ["SynthesisPayloadCompressor"]` and structured RFC-7807 logging.
    - Hardened `_strip_heavy_keys` to purge `hydrated_references`, `shuffled_atoms`, `atom_quotes`, `_step_metadata`, `_audit_signature`, and `_evaluative_matrices`.
    - Enforced strict `DistilledEvaluation.model_validate()` with `settings.max_synthesis_reasoning_length` (eliminated magic numbers and model copies).
    - Implemented Token Shield Prioritized Stratification: Unbounded mode when `max_synthesis_evaluations == 0`, and prioritized stratification when bounded (70% deficit budget, `(-len(exact_quotes), atom_id)` sort, dynamic spillover, canonical `atom_id` sort).
    - Added `_normalize_result_item` supporting dual-path ingestion for `evaluations` and `results`.
  - ✅ **Step 2 (Distiller Hook Filtering)**: Hardened `synthesis_distiller_hook` (@[backend_v2/services/orchestrator/synthesis_distiller.py]):
    - Exported `__all__ = ["synthesis_distiller_hook"]`.
    - Mapped step rules by `id` and `task_blueprint` to evaluate `StepRule.is_synthesis_source`.
    - Filtered out non-synthesis source steps (`is_synthesis_source == False`, specifically Input Processing `sp_db849f9790984585` / `sr_f0a26d17cc9b48a7`), preventing 50k+ raw document tokens from polluting `<source>` blocks.
    - Forwarded `output_profile.synthesis` into `MatrixExplanationService.assemble_matrices_to_explain(..., synthesis_config=output_profile.synthesis)`.
  - ✅ **Step 3 (Matrix Explanation Overrides)**: Hardened `MatrixExplanationService` (@[backend_v2/services/orchestrator/matrix_explanation_service.py]):
    - Exported `__all__ = ["MatrixExplanationService"]`.
    - Accepted `synthesis_config: SynthesisConfigDTO | None = None` and implemented Tripartite Configuration Resolution for `max_quotes_per_matrix` and `max_unmet_criteria`.
    - Narrowed claim label exception handling to `(KeyError, AttributeError)` and replaced dict defaults with typed direct access `tda_to_scale[tda_id]`.
    - Hardened probe boundary logging with `ErrorCodes.INVALID_OUTPUT_SCHEMA`.
  - ✅ **Step 4 (System Core Protection)**: Hardened `StudioWorkflowService` (@[backend_v2/services/studio/workflow_service.py]):
    - Exported `__all__ = ["StudioWorkflowService"]`.
    - Enforced `AppException(SYSTEM_PROTECTED_RESOURCE, status_code=403)` on save/delete of system core steps (`is_system_core == True`).
  - ✅ **Step 5 (Unit & Regression Tests)**:
    - `test_synthesis_payload_compression.py` / `test_synthesis_payload_compressor.py`: 16 tests passing, **94% coverage**.
    - `test_matrix_explanation_service.py`: 12 tests passing, **92% coverage**.
    - `test_synthesis_distiller_wiring.py` / `test_synthesis_distiller.py`: 20 tests passing, **94% coverage**.
    - `test_workflow_service.py`: 30 tests passing, **94% coverage**.
    - Full backend test suite verified: **1,726 unit tests passing**, 0 lint/formatting/MyPy errors.
- **Phase 3 Plan Audit (`/tier8-audit-plan` - Artifact `red_team_audit_phase3_plan.md`)**:
  - ✅ Verified 100% requirements traceability across 39 mapped requirements (R028-R050, R080-R087, R093-R096, R099-R102).
  - ✅ Verified strict Pydantic V2 re-validation (`DistilledEvaluation.model_validate`) and Unbounded Protocol / Token Shield Prioritized Stratification (`(-len(exact_quotes), atom_id)` sort, 70% deficit budget, canonical tie-breaker).
  - ✅ Verified distillation `<source>` filtering by `StepRule.is_synthesis_source` and Tripartite Configuration Resolution in `MatrixExplanationService`.
  - ✅ Verified `AppException(SYSTEM_PROTECTED_RESOURCE, status_code=403)` on mutation or deletion of protected system core steps.
  - ✅ Quality Gates confirmed: `synthesis_payload_compressor.py` (94% coverage), `matrix_explanation_service.py` (92% coverage), `synthesis_distiller.py` (94% coverage), `workflow_service.py` (94% coverage). Supply chain audit clean (zero banned packages).
- **Phase 4 Plan Generation (`/tier0-create-plan`)**:
  - ✅ **Discovery & Structural Mapping Complete**: Analyzed `app_fi.arb`, `app_en.arb`, `workflow_step_card.dart`, and `step_builder_view.dart`.
  - ✅ **Dual-Axis Localization Expanded**: Enumerated and mapped all 18 new ARB keys (`studioWorkflowTaskProfileTitle`, `studioWorkflowExecutionOrderTitle`, `studioWorkflowExecutionOrderSubtitle`, `studioWorkflowStep1IngestionTitle`, `studioWorkflowStep1IngestionSubtitle`, `studioWorkflowStep1OutputBadge`, `studioWorkflowAtomicScopeTitle`, `studioWorkflowAtomicScopeSubtitle`, `studioWorkflowPriorStepsTitle`, `studioWorkflowPriorStepsSubtitle`, `studioWorkflowZoneCAutoTitle`, `studioWorkflowXaiReporterAggregateBadge`, `studioWorkflowXaiReporterPayloadDesc`, `studioSystemCoreBadge`, `studioStepBuilderModelStrategyRequired`, `studioWorkflowInputPrefix`, `studioWorkflowStepPrefix`, `studioWorkflowNoSelectableInputs`).
  - ✅ **3-Zone Layout & Tech Debt Elimination Mapped**:
    - **Zone A (Input Processing, Step 1)**: Locked blueprint selector with `studioSystemCoreBadge`, hidden/disabled delete button, `$inputs.*` source document scope container, output deconstruction badge.
    - **Zone B (Cognitive Specialists, Steps 2..N)**: Filtered blueprint dropdown (`blueprints.where((bp) => !bp.isSystemCore)`), active delete button, dependency chips with cycle prevention, dual-categorized inputs for Atomized Materials (`$inputs.*`) and Prior Step Reports (`$steps.*`).
    - **Zone C (Pipeline Funnel Anchors, Steps N+1..N+3)**: Locked blueprint selector with `studioSystemCoreBadge`, zero manual input mutations, hidden/disabled delete button, automated aggregation badges for XAI Reporter, Scoring Engine, and Synthesis.
    - **Tech Debt Remediated**: Replaced hardcoded Finnish strings (`'Syöte: $labelText'`, `'Askel: $labelStr'`, `'Ei valittavia syötteitä...'`), modernized `getBlueprintLabel` via `bp.name.get(locale)` on `I18nText`, and replaced manual `substring(0, 15)` clippings with `TextOverflow.ellipsis`.
  - ✅ **StepBuilderView System Core Protection & Quality Gates**: Removed hardcoded `Color(0xFF2E7D32)`, localized validation snackbar, hidden/disabled delete on system core steps, and enforced role block / model strategy validation on specialist blueprints.
  - ✅ **Self-Healing Boundary Verification**: Ran `scripts/audit_markdown_boundaries.py` — passed with 0 errors.
  - ✅ **Plan Mutated & Locked**: @[docs/epic/tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX/04_phase4_plan.md] fully detailed and synchronized.
- **Phase 4 Plan Red-Teaming (`/tier0-research-plan`)**:
  - ✅ **System 2 Falsification & Technical Debt Sweep**: Discovered and itemized hardcoded hex color values in `step_builder_view.dart` (`Color(0xFFD32F2F)` on delete action and `Color(0xFF9E9E9E)` on drag handle icon) in lines 940-1195, and injected their remediation into Step 3 per `design_token_absolute_rule`.
  - ✅ **ISTQB Negative Test Hardening**: Verified that the new widget test file `workflow_step_card_test.dart` includes 5 positive and 2 negative ISTQB partitions (verifying system core blueprint exclusion in specialist dropdown and disabled delete on Zone A/Zone C steps).
  - ✅ **Dual-Axis Localization Verification**: Verified that all 18 ARB keys in `app_fi.arb` and `app_en.arb` include proper metadata blocks and typed placeholders (`{name}`).
  - ✅ **Parity & Line Boundary Verification**: Verified AST and line bounds across all modified Flutter target files via `scripts/audit_markdown_boundaries.py` (0 errors).
  - ✅ **Plan Mutated & Locked**: [04_phase4_plan.md](file:///C:/src/quorum/docs/epic/tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX/04_phase4_plan.md) updated, verified, and locked for execution.

- **Phase 4 Execution**:
  - ✅ **Step 0 (Alignment)**: Verified Phase 3 backend baseline, model parity, and Freezed codegen status.
  - ✅ **Step 1 (Dual-Axis ARB Expansion)**: Added 19 localized keys to `app_fi.arb` and `app_en.arb` covering 3-zone titles, badges, and step-builder requirements, and cleanly regenerated `AppLocalizations` via `flutter gen-l10n`.
  - ✅ **Step 2 (WorkflowStepCard 3-Zone Restructuring)**:
    - Restructured card layout into Zone A (Input Processing, Step 1), Zone B (Dynamic Specialists, Steps 2..N), and Zone C (Automated Funnel Anchors, Steps N+1..N+3).
    - Eliminated hardcoded Finnish strings using `l10n.studioWorkflowInputPrefix(labelText)`, `l10n.studioWorkflowStepPrefix(labelStr)`, and `l10n.studioWorkflowNoSelectableInputs`.
    - Modernized `getBlueprintLabel` with `bp.name.get(locale)` on `I18nText`.
    - Replaced manual `substring(0, 15)` clippings with `TextOverflow.ellipsis`.
    - Enforced system core protection (hidden delete button and locked blueprint display).
  - ✅ **Step 3 (StepBuilderView System Core Protection & Quality Gates)**:
    - Removed hardcoded hex colors (`Color(0xFF2E7D32)`, `Color(0xFFD32F2F)`, `Color(0xFF9E9E9E)`), adopting semantic theme tokens (`colorScheme.error`, `colorScheme.onSurfaceVariant`).
    - Localized validation snackbar errors (`l10n.studioStepBuilderModelStrategyRequired`, `l10n.studioStepBuilderRoleOrCriteriaRequired`).
    - Added `studioSystemCoreBadge` to the configuration header and disabled delete and ID editing for system core steps.
    - Enforced specialist LLM blueprint quality gate requiring at least one role block, persona, or criteria block.
  - ✅ **Step 4 (Flutter Quality Gate & Tests)**:
    - Created `workflow_step_card_test.dart` implementing 5 positive and 2 negative ISTQB partitions (100% passing).
    - Verified existing tests `step_builder_view_dropdown_test.dart`, `workflow_test.dart`, and `domain_parity_test.dart`.
    - Full Flutter test suite passing (185 tests) with 0 analyze issues.

## Learned
- **Baseline Architecture State**: Both backend (Python Pydantic V2) and frontend (Dart 3 Freezed) models strictly enforce `is_system_core` on steps and `is_synthesis_source` on step rules with fail-fast validation.
- **Strict Freezed Serialization**: Dart models enforce `@JsonSerializable(disallowUnrecognizedKeys: true)` and strict boolean coercion, preventing unrecognized keys and type corruption.
- **Seed Data Layout & Vault Protocol**: `seed_data.json` houses 16 `StepRule` definitions at lines 7837-8052 and 19 `Step` definitions at lines 8065-9020. Native `multi_replace_file_content` with line bounding avoids CRLF grep bugs and prevents context truncation.
- **Service Type Tolerances**: `RAGPreflightService` accepts `PromptCompiler | Any` to maintain compatibility with `PromptCompilerAdapter` without requiring circular adapter abstractions.
- **Token Shield Prioritized Stratification Protocol**: Default `max_synthesis_evaluations = 0` provides Unbounded Mode for 100% forensic coverage. When bounded, deterministic multi-key sorting (`(-len(exact_quotes), atom_id)`) guarantees byte-for-byte prompt caching parity and prevents the "Auditing Whitewash" anti-pattern.
- **Dynamic Stratification Spillover**: In `_prune_and_stratify_evaluations`, if the deficit partition contains fewer items than the 70% budget, the unused allocation dynamically spills over to the strengths partition (and vice versa), ensuring exact budget utilization up to `limit` without artificial quote starvation.
- **Heterogeneous Partition Routing**: `_normalize_result_item` acts as a discriminator router for heterogeneous results: items containing `"exact_quotes"` are validated through `DistilledEvaluation.model_validate()`, while scalar/text step results undergo explicit field whitelisting (`{"output_text", "status", "atom_id"}`).
- **Tripartite Configuration Resolution**: Profile-level overrides (`output_profile.synthesis`) take precedence over global defaults (`settings.py`), allowing fine-grained token budgeting per report layout.
- **StepRule & Step Identifier Schemas**: `StepRule` is identified by `id` (DAG node, like `sr_...`) and references `task_blueprint` (like `sp_...`). It does not have a separate `step_id` attribute. In contrast, `Step` is identified by `id` (like `sp_...`) and requires `hook` when `type == "logic"`, or `criteria_block_ids` + `extraction_protocol_block_id` + `model_strategy` when `type == "llm"`.
- **System Core Immutability Guard**: `StudioWorkflowService` enforces slug and system-core immutability (`data.slug == existing.slug` and `data.is_system_core == existing.is_system_core`), effectively securing built-in system steps against accidental modification or deletion while allowing name/description updates.
- **Frontend Dual-Axis Localization SSOT**: Frontend static labels are managed through `.arb` files and generated into `AppLocalizations` (`l10n.studioWorkflowTaskProfileTitle`, etc.), while semantic text fields on domain models use `I18nText.get(locale)` which safely defaults to Finnish/English.
- **Workflow Step Zone Taxonomy**:
  - `Zone A (Step 1)`: Input Processing anchor (`sp_db849f9790984585`). Protected system step.
  - `Zone B (Steps 2..N)`: Dynamic Cognitive Specialists (`is_system_core == false`). Full mutation and dependency routing permitted.
  - `Zone C (Steps N+1..N+3)`: Automated Funnel Anchors (`sp_192910b5f5a34c79`, `sp_d245365e4a274b9e`, `sp_7a8b9c0d1e2f3a4b`). Protected system steps with locked inputs and automated aggregations.
- **Design Token Invariant in Step Builder**: All explicit `Color(...)` instantiations in Flutter widgets violate `design_token_absolute_rule` and must be replaced with themed `Theme.of(context).colorScheme` semantic properties (`error`, `onSurfaceVariant`, etc.).

## Remaining
- **Phase 4 Audit**: `/tier8-audit-plan @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\04_phase4_plan.md] @[docs\epic\EPIC_145_tracker.md]`.
- **Phase 5**: Verification, Widget Testing & E2E Integration Gate (`/tier0-create-plan` -> `/tier0-research-plan` -> `/tier2-execute` -> `/tier8-audit-plan`).
- **Post-Implementation Gates**: Full-stack audit, `/tier2-hardening-backend`, `/tier2-hardening-frontend`, `/tier7-describe-architecture`, `/tier8-audit-epic`.

## Resume Command
`/tier8-audit-plan @[docs\epic\tasks_EPIC_145_Workflow_Context_Governance_and_Studio_UX\04_phase4_plan.md] @[docs\epic\EPIC_145_tracker.md]`






