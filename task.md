# Task Tracking: Theory-Grounding Matrix Calibration & Micro-Slice Isolation Engine

Implementation Plan: `docs/implementationplans/IMPLEMENTATION_PLAN_Theory_Grounding_Matrix_Calibration_and_Micro_Slice_Engine.md`

- [x] **Phase 1: Pre-Implementation Cleanups & Technical Debt Remediation**
  - [x] Execute baseline test: `uv run pytest backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py`
  - [x] Substep 1.1: Eradicate Chained Dict Fallbacks in `scripts/matrix_hardening_loop.py` (`audit_matrix` #L110-L138) using `I18nText.resolve(target_locale="fi")`
  - [x] Substep 1.2: Eradicate Silent Exception Pass in `build_or_load_state` (`#L160-L175`) with `logger.warning`
  - [x] Substep 1.3: Ensure `tmp/slices/` directory exists and verify untracked in `.gitignore`
  - [x] Run quality gate: `uv run pytest backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py`

- [ ] **Phase 2: Core Matrix Slice Engine Implementation**
  - [ ] Substep 2.1: Implement `export_matrix_slice` in `scripts/matrix_slice_engine.py`
  - [ ] Substep 2.2: Implement `detect_empirical_contamination` and `audit_atom_coherence`
  - [ ] Substep 2.3: Implement `generate_theory_opponent_card`
  - [ ] Substep 2.4: Implement `apply_matrix_slice` with in-memory pre-flight audit and rollback
  - [ ] Substep 2.5: Add `enforce_pre_flight` check to `TDAAssertion` `@model_validator` in `backend_v2/models/v2_core.py`
  - [ ] Substep 2.6: Implement `append_matrix_theory_explanation`
  - [ ] Verify `scripts/matrix_slice_engine.py` is <= 250 lines

- [ ] **Phase 3: Studio UI Guardrails & CLI Facade Integration**
  - [ ] Substep 3.1: Studio Scale Editor Reactive Guardrails in `scale_editor_modal.dart`
  - [ ] Substep 3.2: CLI Facade Integration in `scripts/matrix_hardening_loop.py`
  - [ ] Verify `scripts/matrix_hardening_loop.py` is <= 335 lines

- [ ] **Phase 4: Comprehensive Unit & Anti-Happy-Path Testing**
  - [ ] Implement all 15 test contracts in `backend_v2/tests/unit/scripts/test_matrix_slice_engine.py`
  - [ ] Implement widget test in `client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart`
  - [ ] Run backend unit tests and Flutter widget tests

- [ ] **Phase 5: Quality Gate Auditing & Pilot Slice Execution**
  - [ ] Run backend audit loop: `uv run python scripts/backend_audit_loop.py scripts/matrix_slice_engine.py --test`
  - [ ] Run matrix hardening test suite
  - [ ] Execute live pilot export for `blk_440a5fef9331451b`
  - [ ] Audit empirical contamination on Toulmin pilot
  - [ ] Execute physical database calibration patch on `blk_440a5fef9331451b`
  - [ ] Initialize `docs/architecture/08_matrix_explanations.md`
  - [ ] Run database atom verification linter: `uv run python scripts/audit_database_atoms.py --strict`
