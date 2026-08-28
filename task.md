# Task: Full Database Verification Engine & Complete Prompt/Seed Sanitization

- [x] **Phase 1: Pre-Implementation Cleanups & Prompt Protocol Hardening**
  - [x] Step 1.1: Inject epistemic decision protocol into `MATRIX_SENSOR_SYSTEM_PROMPT` in `@[backend_v2/models/prompts/matrix_evaluation.py]`
  - [x] Step 1.2: Update and expand unit tests with ISTQB negative partitions in `@[backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py]`

- [ ] **Phase 2: Automated Full Database Prompt Verification Engine & Test Suite**
  - [ ] Step 2.1: Build `@[scripts/audit_database_atoms.py]` with 4-Collection Inspection Gates
  - [ ] Step 2.2: Build comprehensive unit test suite in `@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]`
  - [ ] Step 2.3: Verify baseline failure before seed data sanitization (`uv run python scripts/audit_database_atoms.py --strict`)
- [ ] **Phase 3: Complete 4-Collection Seed Data Sanitization via Deterministic In-Memory Migration**
  - [ ] Step 3.1: Vault backup & comprehensive seed sanitization via `@[scratch/sanitize_seed_atoms.py]` and Dart parity test
  - [ ] Step 3.2: Execute verification engine on sanitized seed vault (`uv run python scripts/audit_database_atoms.py --strict`)
  - [ ] Step 3.3: Re-seed local database (`uv run python backend_v2/seed/run_seed.py local`)
- [ ] **Phase 4: Quality Gates & Statistical E2E Variance Validation**
  - [ ] Step 4.1: Execute backend quality gate (`uv run python scripts/backend_audit_loop.py backend_v2 --test`)
  - [ ] Step 4.2: Execute live E2E variance test on real PDF data (`$env:DEV_EXECUTION_MODE="full"; uv run python scripts/run_e2e_variance_test.py docs\jwdatat`)
