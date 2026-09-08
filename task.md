# Task Tracker: SSOT Environment Governance & Startup Observability

<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[c:\Users\risto\.gemini\antigravity-ide\brain\ca3dd09b-8125-4837-89e6-87171caf3133\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Constraint: `inline_imports_ban` - No inline `from backend_v2.settings import get_settings` inside functions; imported globally at the top of `backend_v2/services/auth.py`.
- [x] Constraint: `english_language_mandate` - Replaced Finnish comments in `auth.py` with concise English comments.
- [x] Constraint: `builtin_shadowing_cleanup` - Renamed variable `id` shadowing Python builtin `id` in `auth.py`.
- [x] Constraint: `security_defense_in_depth` - In `settings.py`, `allow_mock_tokens` strictly requires `self.active_backend == StorageBackend.LOCAL`.
- [x] Constraint: `startup_observability_ssot` - `log_startup_system_parameters` is a pure, reusable helper logging fixed-width ASCII parameters to `backend_debug.log`.
- [x] Constraint: `cli_environment_isolation` - `run_e2e_variance_test.py` isolates `ENVIRONMENT` from local dirty `.env` without secondary flags.
- [x] Constraint: `metadata_ssot_governance` - `diff_executions.py` reads `matrix_sampling_strategy` directly from `ExecutionMetadata` per `ki_execution_record_ssot.md`.
- [x] Constraint: `launcher_environment_parity` - `run_local.bat` supports `--prod` / `--production` and `--dev`, displaying dynamic environment banners and synced window titles.

## Execution Tasks

- [x] **Phase 1: Pre-Implementation Cleanups (Technical Debt & 1-Hop Caller Normalization)**
  - [x] Step 1.1: Add global import `from backend_v2.settings import get_settings` at top of `backend_v2/services/auth.py`.
  - [x] Step 1.2: Remove inline import in `verify_token` at line 306 of `backend_v2/services/auth.py`.
  - [x] Step 1.3: Replace Finnish comment with English in `verify_token`.
  - [x] Step 1.4: Rename local variable `id` to `user_id` in `verify_token` to avoid shadowing builtin `id`.
  - [x] Quality Gate: Run unit tests and `backend_audit_loop.py` on `auth.py`.

- [x] **Phase 2: IAM Defense-in-Depth Firewall**
  - [x] Step 2.1: Update `allow_mock_tokens` in `backend_v2/settings.py` to enforce `self.active_backend == StorageBackend.LOCAL`.
  - [x] Step 2.2: Add unit tests in `backend_v2/tests/unit/test_settings.py` covering all 4 ISTQB partitions for `allow_mock_tokens`.
  - [x] Quality Gate: Run unit tests and `backend_audit_loop.py` on `settings.py`.

- [x] **Phase 3: Startup Parameter Logging in Backend & Worker**
  - [x] Step 3.1: Implement `log_startup_system_parameters(logger: logging.Logger, component_name: str) -> None` in `backend_v2/logging_config.py`.
  - [x] Step 3.2: Hook `log_startup_system_parameters` into `backend_v2/main.py` (`lifespan`).
  - [x] Step 3.3: Hook `log_startup_system_parameters` into `backend_v2/worker.py` (`startup`).
  - [x] Step 3.4: Add unit tests in `backend_v2/tests/unit/test_logging_isolation.py` asserting startup banner logging.
  - [x] Quality Gate: Run unit tests and `backend_audit_loop.py` on logging and startup entrypoints.

- [x] **Phase 4: Pure SSOT Environment Resolution in E2E Runner, Diff Tool & Launcher**
  - [x] Step 4.1: Eliminate `.env` leakage in `scripts/run_e2e_variance_test.py` (`run_variance_test`).
  - [x] Step 4.2: Update `scripts/diff_executions.py` to read `matrix_sampling_strategy` from `ExecutionMetadata`.
  - [x] Step 4.3: Enhance `run_local.bat` with CLI argument parsing loop (`--prod`, `--dev`, `--no-cache`, `--flush`), dynamic banner, and window titles.
  - [x] Step 4.4: Add unit tests in `backend_v2/tests/unit/test_run_e2e_variance_test.py` asserting environment isolation.
  - [x] Step 4.5: Py_compile verification for scripts and full audit gate.

## Session Handover Context
- **Achieved**: 100% of Phases 1, 2, 3, and 4 implemented and verified. All 100 unit tests pass across `test_settings.py`, `test_logging_isolation.py`, `test_auth.py`, `test_run_e2e_variance_test.py`, and `test_diff_executions.py`. All targets pass the Universal Quality Gate loop with zero Ruff errors, zero MyPy strict errors, and clean ISTQB partition coverage.
- **Learned**: In `Settings.allow_mock_tokens`, strictly gating on `self.active_backend == StorageBackend.LOCAL` provides defense-in-depth regardless of Firebase Auth configuration. In `scripts/run_e2e_variance_test.py`, deriving `ENVIRONMENT` purely from the `dev` CLI switch prevents dirty local `.env` files from hijacking production runs.
- **Remaining**: Implementation 100% complete. Ready for atomic git commit and routing to `/tier8-audit-plan`.
