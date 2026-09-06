# Task Tracker: Option 4 Comprehensive E2E Isolation & Advanced Kappa Analytics Suite

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[c:\Users\risto\.gemini\antigravity-ide\brain\997a2478-eecb-490e-9077-1856c128bb73\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags & 5-Column Architectural Directives)
- [ ] Constraint: `target_scope_boundaries` - Changes strictly isolated to `scripts/run_e2e_variance_test.py`, `scripts/diff_executions.py`, and test suites.
- [ ] Constraint: `eradicated_duct_tape` - Eradicate bare `except Exception: pass`, Python 2 exception syntax, legacy `tmp/`, dynamic `getattr(enums, ...)`, and naked dictionaries.
- [ ] Constraint: `approved_best_practice` - Multi-field Unicode perturbation, `--no-cache` batch forwarding, `cooldown_seconds` TTL, immutable Pydantic V2 DTOs (`KappaMetricsDTO`, `IsolationAuditDTO`, `RootCauseBreakdownDTO`, `ScaleBreakdownDTO`, `BlockHeatmapDTO`, `MacroBlockScoreDTO`), `DisagreementRootCause(StrEnum)`, Fleiss SE/CI with singularity guard, Landis & Koch benchmarks, 0-100 normalized difficulty tiers, block heatmap, deterministic 4-tier root cause triage, macro score drift tracking, and lexical grounding audit.
- [ ] Constraint: `pruned_over_engineering` - 100% native stdlib math/argparse; zero external heavy dependencies (`scipy`, `statsmodels`).
- [ ] Constraint: `verification_and_fail_fast` - Fail-Fast on space-starved inputs, strict Pydantic V2 models, unit tests in `backend_v2/tests/unit/`, and `backend_audit_loop.py` compliance.
- [ ] Constraint: `step_by_step_mode` - Stop after completing each cohesive step and wait for user approval.

## Execution Tasks

- [x] **Phase 1: Pre-Implementation Cleanups & Technical Debt Sweeps**
  - [x] 1.0 Fix Python 2 exception syntax bug at `scripts/diff_executions.py#L369` (`except (UnicodeDecodeError, OSError):`).
  - [x] 1.1 Eradicate silent error suppression (`the_duct_tape_ban`) across `scripts/run_e2e_variance_test.py` and `scripts/diff_executions.py`.
  - [x] 1.2 Eradicate legacy `tmp/` usage in `scripts/run_e2e_variance_test.py` (replace with `scratch/variance_inputs/`).
  - [x] 1.3 Eradicate hardcoded magic values in `scripts/run_e2e_variance_test.py` (ISO timestamp fallback, workflow lookup Fail-Fast).
  - [x] 1.4 Fix fragile dynamic attribute access `getattr(enums, ...)` in `scripts/diff_executions.py#L514-522`.
  - [x] 1.5 Run baseline unit tests and `backend_audit_loop.py` to verify clean state.

- [x] **Phase 2: Test Runner Ingress & Isolation Suite (`scripts/run_e2e_variance_test.py`)**
  - [x] 2.1 Refactor `make_noise_injector(run_index)` and `run_variance_test` for multi-field perturbation across all whitespace-containing string fields with Fail-Fast check if 0 fields injected.
  - [x] 2.2 Add `--no-cache` parameter passing `"--no-cache"` as CLI argument to `run_local.bat` and setting `backend_env["DISABLE_VERTEX_CACHE"] = "true"`.
  - [x] 2.3 Add `--cooldown-seconds` TTL parameter for inter-run TCP socket drain.
  - [x] 2.4 Add standard `argparse.ArgumentParser` CLI interface with backward-compatible positional argument support.
  - [x] 2.5 Update unit tests in `backend_v2/tests/unit/test_run_e2e_variance_test.py` and run quality gate.

- [x] **Phase 3: Forensic Analytics & Advanced Kappa Suite (`scripts/diff_executions.py`)**
  - [x] 3.1 Define immutable Pydantic V2 DTOs (`KappaMetricsDTO`, `IsolationAuditDTO`, `RootCauseBreakdownDTO`, `ScaleBreakdownDTO`, `BlockHeatmapDTO`, `MacroBlockScoreDTO`) and `DisagreementRootCause(StrEnum)`.
  - [x] 3.2 Implement Execution Health Check (`ONNISTUNUT`) and Cross-Run Input Hash Isolation Audit (`TÄYSI SYÖTE-ERISTYS` vs `MAHDOLLINEN VÄLIMUISTIVUOTO`).
  - [x] 3.3 Refactor `calculate_cohens_kappa()` to return `KappaMetricsDTO` directly with Fleiss SE, 95% CI, singularity guard ($p_o = 1.0$, $p_e \ge 1.0$), Landis & Koch categorization, and marginal bias calculation.
  - [x] 3.4 Implement 0-100 Normalized Difficulty Tier Breakdown (5 standardized difficulty quintiles) using parent block extrema from `seed_data.json`.
  - [x] 3.5 Implement Block Heatmap analysis (mismatches and consistency rate per matrix block).
  - [x] 3.6 Implement Deterministic Disagreement Root Cause Triage (`DisagreementRootCause`: Retrieval Gap vs Reasoning Gap vs Contextual Override vs Technical Error).
  - [x] 3.7 Implement Macro Score Drift (0-100) extracting native `normalized_score` from `execution_trace.json` block payloads with $\Delta \text{normalized\_score}$.
  - [x] 3.8 Implement FinOps Cached Token Savings and $\Delta \text{Cost}$ calculations.
  - [x] 3.9 Implement Lexical Grounding Audit with exact `str.find()` validation of quotes against input snapshots.
  - [x] 3.10 Synthesize all sections into the differential Markdown report.

- [x] **Phase 4: Unit Test Verification Suite (`backend_v2/tests/unit/test_diff_executions.py`)**
  - [x] 4.1 Create `backend_v2/tests/unit/test_diff_executions.py` covering positive, negative, and boundary test contracts.
  - [x] 4.2 Run complete test suite and execute `backend_audit_loop.py` on both scripts.

## Session Handover Context
- **Achieved**: 100% of Phases 1, 2, 3, and 4 implemented and verified. All 59 unit tests pass across `test_run_e2e_variance_test.py` and `test_diff_executions.py`. Both scripts pass `backend_audit_loop.py` with strict >=90% test coverage (92% on runner, 90% on diff engine) and zero Ruff/MyPy errors.
- **Learned**: Fleiss standard error calculation requires a strict boundary singularity guard when $p_o = 1.0$ or $p_e \ge 1.0$ to prevent negative roots or division-by-zero. 0-100 normalization elegantly bridges heterogeneous block scale lengths (1-5 vs 1-6).
- **Remaining**: Implementation plan execution complete. Ready for atomic commit and mandatory Tier 8 Red-Team audit routing (`/tier8-audit-plan`).
