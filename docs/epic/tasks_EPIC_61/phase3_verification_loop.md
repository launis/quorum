# Implementation Plan - Phase 3: Verification & Stability Loop

This sub-plan focuses on validating our changes by writing robust unit/integration tests for the newly hardened TDA rules and engine changes, running execution self-consistency checks, auditing with the backend hardening loop, and updating the architecture documentation.

## Architectural Rules Applied
- **Rule 1 (TDD Mandate)**: Write the tests first to verify expected behavior (including null mapping).
- **Rule 2 (Deterministic Testing Delegation)**: Ensure that tests use `polyfactory` for mock data where appropriate and thatconftest blocks actual network calls to prevent flaky suites.
- **Rule 3 (Documentation Update)**: Update the relevant `c:\src\quorum\docs\architecture\` documentation with the new evaluation invariants.

## Proposed Changes

### Component: Testing & Verification Suite

#### [NEW] [test_epic_61_hardening.py](file:///c:/src/quorum/backend_v2/tests/unit/test_epic_61_hardening.py)

##### Milestone 3.1: Write Unit/Integration Tests for Hardened Rules
- **Source**: Epic Phase 2, Step 2
- **Change**: Create a new test suite verifying that:
  1. The deterministic parser engine returns `null` when a vice rule lacks physical anchors (Zero-Trust Null-Filtering).
  2. The exact surrendering phrases are extracted correctly for `tda_c74c4367acc028cf`, and custom constraints trigger a `null` output.
  3. The prompt compiler correctly compiles both the updated `GLOBAL_HARDENING_FRAMEWORK` and the new zero-trust negative condition matching rule in `compile_blind_system_instruction`.

##### Milestone 3.2: Run Consistency Audit Script
- **Source**: Epic Phase 3, Step 1 & 2
- **Action**: Ask the user to run two consecutive evaluations and perform consistency diffing using:
  ```powershell
  uv run python scratch/diff_executions.py [run1_id] [run2_id]
  ```
  Ensure Fleiss' Kappa stays above 0.95 and average Shannon entropy is minimized towards zero.

##### Milestone 3.3: Execute Universal Backend Quality Gate
- **Source**: Epic Phase 3, Step 3
- **Action**: Ask the user to run the comprehensive backend audit script:
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/ --test
  ```

---

### Component: Documentation

#### [MODIFY] [02_domain_models.md](file:///c:/src/quorum/docs/architecture/02_domain_models.md)

##### Milestone 3.4: Update Architectural Guidelines for Rules & TDAs
- **Source**: Epic Section 5 (DoD)
- **Change**: Document the strict Zero-Trust Null Filtering and Syntactic Anchoring requirements for Vice Rules and TDA assertions under Section 3.15 (Roolijako) in `02_domain_models.md` to ensure ongoing developer compliance.

---

## Verification Plan

### Automated Tests
- Run newly added test suite:
  ```powershell
  uv run pytest backend_v2/tests/unit/test_epic_61_hardening.py
  ```
- Run the universal backend audit:
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/core/system_directives.py backend_v2/services/orchestrator/prompt_compiler.py --test
  ```

---

## Session Handover
To execute this sub-plan after approval:
1. Open a fresh context window.
2. Run command: `/tier2-execute --target docs/epic/tasks_EPIC_61/phase3_verification_loop.md`
