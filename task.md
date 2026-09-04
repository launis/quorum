# Task Tracking: Sensor Reliability & Epistemic Variance Hardening (Phases 1–3)

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_matrix_boolean_evaluation_strictness.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[c:\Users\risto\.gemini\antigravity-ide\brain\78d4f10f-bb9e-4447-b1dc-ac6a9497bff9\implementation_plan.md]

## Execution Tasks
- [x] **Step 1: Null Hypothesis Tie-Breaker in Bo3 Reconciliation**
  - [x] Update `resolve_majority_vote` signature to accept `is_inverse_map: dict[str, bool] | None = None`
  - [x] Implement empty tally check (`not tally`) -> `ExecutionStatus.SYSTEM_ERROR` with `"UNRETURNED_BY_MODEL: No valid votes cast for atom"`
  - [x] Implement Null Hypothesis resolution for `is_inverse=True` -> `ExecutionStatus.PASSED`
  - [x] Implement Null Hypothesis resolution for `is_inverse=False` -> `ExecutionStatus.FAILED`
  - [x] Implement missing polarity fallback -> `ExecutionStatus.SYSTEM_ERROR` with `"INSUFFICIENT_CONSENSUS"`
  - [x] In `evaluate_atom_boolean_batch`, pre-compute `is_inverse_map` upfront and optimize ensemble call lookup to $O(1)$
  - [x] Pass `is_inverse_map` to `resolve_majority_vote`
- [x] **Step 2: Unit Tests for Tie-Breaker Resolution**
  - [x] Add 6-partition test in `test_extractive_sensor_service.py` covering positive split, inverse split, missing map, unregistered TDA, unanimous consensus, and zero votes cast
  - [x] Verify test suite passes with `backend_audit_loop.py` (19 passed, 92% coverage)
- [x] **Step 3: Contextual Override Directive Hardening**
  - [x] Harden `CONTEXTUAL_OVERRIDE_DIRECTIVE` in `matrix_evaluation.py` with banned speculative overrides, qualifying criteria, and null hypothesis burden
  - [x] Update `test_matrix_evaluation.py` to assert negative boundary presence and absence of banned ambiguity tokens
  - [x] Verify test suite passes with `backend_audit_loop.py` (4 passed, 100% coverage)
- [x] **Step 4: Top 5 Unstable Atom Calibration in Seed Vault**
  - [x] Backup `seed_data.json` before edits (`backend_v2/seed/backups/`)
  - [x] Calibrate `tda_6ecd649b48c24e68824e27e30ed8a63e` (Score 4)
  - [x] Calibrate `tda_680dc2c703b3425fa0b0d943dbd5af16` (Score 5)
  - [x] Calibrate `tda_37b0cf6ecd3146071662bd1bf899df74` (Score 3)
  - [x] Calibrate `tda_74711aa33ba39f6fcf767ea0b96ceab0` (Score 3)
  - [x] Calibrate `tda_43516f120e4a415bb0ee3a878a53a5bc` (Score 4)
- [x] **Step 5: Deterministic Quality Gates & Database Reseeding**
  - [x] Run `uv run python scripts/audit_database_atoms.py --strict` (PASSED 0 ERRORS)
  - [x] Run `uv run python backend_v2/seed/run_seed.py local --dry-run` (PASSED)
  - [x] Run `uv run python backend_v2/seed/run_seed.py local` (PASSED & PERSISTED)
  - [x] Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extractive_sensor_service.py --test` (PASSED)
  - [x] Run `uv run python scripts/backend_audit_loop.py backend_v2/models/prompts/matrix_evaluation.py --test` (PASSED)
- [x] **Step 6: End-to-End Variance Verification**
  - [x] Run `uv run python scripts/run_e2e_variance_test.py "tmp/e2e_inputs_run1.json"`
  - [x] Verify scratch diff report metrics in `scratch/diff_report_2026-09-04_2041.md`:
    - Zero `SYSTEM_ERROR` / `INSUFFICIENT_CONSENSUS` failures: **0** (target: 0)
    - Pairwise self-consistency: **97.38%** (target: >= 95.0%)
    - Fleiss Kappa: **0.9343** (target: >= 0.85)
    - Discrepancies reduced from 28 to 8 (71.4% improvement)
    - All 5 calibrated atoms achieved 100% consistency

## # Session Handover Context
- **Achieved:** Successfully executed Phases 1–3 of Sensor Reliability & Epistemic Variance Hardening. Built Null Hypothesis tie-breaker in `extractive_sensor_service.py`, added 6-partition unit tests, hardened `CONTEXTUAL_OVERRIDE_DIRECTIVE`, calibrated top 5 unstable atoms in `seed_data.json`, reseeded database, and mathematically proved with E2E variance tests that `SYSTEM_ERROR` is completely eliminated (0 errors) and Fleiss Kappa improved to 0.9343.
- **Learned:** Resolving inconclusive Best-of-Three split votes according to atom polarity (`is_inverse: true` -> `PASSED`, `is_inverse: false` -> `FAILED`) eliminated all 13 transient consensus failures and stabilized the whole pipeline without any regression.
- **Remaining:** None for this plan. Handover to `/tier8-audit-plan` for independent red-team verification.
