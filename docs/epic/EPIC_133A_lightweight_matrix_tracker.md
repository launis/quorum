# EPIC 133A Tracker: Lightweight Matrix God Code Decomposition

**Epic:** @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix.md]
**Task Directory:** @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix]

---

## Phase Execution Status

### Phase 1: Golden Master & Coverage Verification
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\01_golden_master_and_coverage.md]

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\01_golden_master_and_coverage.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\01_golden_master_and_coverage.md]`
  - [ ] Step 1.0: STRATEGIC ALIGNMENT CHECK — Verify `lightweight_matrix.py` is not modified and check test coverage.
  - [ ] Step 1.1: UN-SKIP LEGACY TESTS — Find and un-skip 10 tests marked with "Legacy architecture obsolete" in `test_lightweight_matrix.py` (lines 13, 32, 81, 187, etc.). Fix them to pass under current architecture before extraction.
  - [ ] Step 1.2: VERIFY COVERAGE — Run `uv run pytest --cov=backend_v2.models.dtos.lightweight_matrix backend_v2/tests/ --cov-report=term-missing` and verify >80% coverage. Write Golden Master tests if needed.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\01_golden_master_and_coverage.md]`

---

### Phase 2: DTO Extraction & Strangler Fig Proxy
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\02_dto_extraction.md]

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\02_dto_extraction.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\02_dto_extraction.md]`
  - [ ] Step 2.0: STRATEGIC ALIGNMENT CHECK — Verify Phase 1 completed successfully and test coverage >80% with no skipped tests in `test_lightweight_matrix.py`.
  - [ ] Step 2.1: CREATE NEW ATOM EVALUATION DTO FILE — Create `atom_evaluation.py` and physically extract 6 DTO classes (`ReasoningStepDTO`, `LightweightExtractionAtom`, `MatrixEvaluationItemDTO`, `AtomEvaluationItemDTO`, `ReducedAtomDTO`, `LightweightMatrixDTO`) in exact dependency order without altering any logic.
  - [ ] Step 2.2: IMPLEMENT STRANGLER FIG RE-EXPORTS — In `lightweight_matrix.py`, add re-export imports for ALL 6 migrated classes to prevent breaking 23+ consumers.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\02_dto_extraction.md]`

---

### Phase 3: Service Logic Extraction & Duck-Typing Eradication
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\03_service_logic.md]

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\03_service_logic.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\03_service_logic.md]`
  - [ ] Step 3.0: STRATEGIC ALIGNMENT CHECK — Verify `atom_evaluation.py` exists and tests pass.
  - [ ] Step 3.1: STRIP VALIDATION SERVICE IMPORTS — Remove `AnchorValidationService` and `AliasEngine` usage from `AtomEvaluationItemDTO` validators.
  - [ ] Step 3.1b: REDUCE CONTEXT CONTRACT — Reduce `ValidationInfo.context` in `AtomEvaluationItemDTO` to only expect `{"null_hypothesis_blacklist": set[str]}`.
  - [ ] Step 3.2: ERADICATE HASATTR DUCK-TYPING — Replace `hasattr(quote, "text")` checks with strict `quote.text` access in `evidence_found` properties.
  - [ ] Step 3.3: ERADICATE DICT AND GET FALLBACKS — Replace `isinstance(quote, dict)` and `.get()` fallbacks inside properties and validators with Pydantic typed access.
  - [ ] Step 3.3b: FIX DUPLICATE VALIDATOR BUG — Resolve duplicate `@field_validator("chart_display_label", mode="before")` on `AtomEvaluationItemDTO`.
  - [ ] Step 3.4: MOVE INLINE IMPORTS — Move `import re` statements from inline methods to the global import section.
  - [ ] Step 3.5: REPLACE HARDCODED FINNISH BLACKLISTS — Replace hardcoded arrays (e.g., "ei löydy") with injected `_null_hypothesis_blacklist` `PrivateAttr`.
  - [ ] Step 3.6: CLEANUP MODULE IMPORTS — Remove unused module-level imports like `get_lexical_fuzz_threshold`.
  - [ ] Step 3.7: ATOMIC TEST FIXTURE MIGRATION — Update test fixtures to inject `null_hypothesis_blacklist` and use instantiated quote objects.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\03_service_logic.md]`

---

### Phase 4: Import Migration (Batched Strangler Fig Sunset)
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\04_import_migration.md]

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\04_import_migration.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\04_import_migration.md]`
  - [ ] Step 4.0: STRATEGIC ALIGNMENT CHECK — Verify Phase 3 completed successfully and backend tests pass.
  - [ ] Step 4.1: UPDATE IMPORT PATHS — Update imports in 23+ consumer files to point to `atom_evaluation.py` instead of `lightweight_matrix.py` in batches of 5.
  - [ ] Step 4.2: REMOVE STRANGLER FIG EXPORTS — Delete the re-exports for the 6 migrated classes from `lightweight_matrix.py`.
  - [ ] Step 4.3: GLOBAL AUDIT — Run the global audit loop to confirm zero import errors.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\04_import_migration.md]`

---

### Phase 5: Frontend Flutter UI Enum Synchronization
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\05_flutter_sync.md]

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\05_flutter_sync.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\02_flutter_desktop.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\05_flutter_sync.md]`
  - [ ] Step 5.0: STRATEGIC ALIGNMENT CHECK — Verify Phase 4 is complete and backend is stable.
  - [ ] Step 5.1: FLUTTER AUDIT LOOP — Run `flutter_audit_loop.py` to ensure Enum parity. Update Dart enums in `enums.dart` if needed.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\05_flutter_sync.md]`

---

### Phase 6: Verification & E2E Integration Gate
**Plan:** @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\06_verification.md]

- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\06_verification.md] @[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\06_verification.md]`
  - [ ] Step 6.0: STRATEGIC ALIGNMENT CHECK — Verify all prior phases are complete.
  - [ ] Step 6.1: PYTHON BACKEND AUDIT — Execute the Python backend audit loop globally.
  - [ ] Step 6.2: FLUTTER AUDIT — Execute the Flutter audit loop.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\06_verification.md]`

---

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK]** Backend and Frontend full-stack integration test gates pass.

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in `<appDataDir>/knowledge/`.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

---

## Requirements Traceability Matrix

| Req ID | Requirement Description | Plan/Epic Step ID |
|--------|-------------------------|-------------------|
| R1 | Un-skip 10 legacy tests marked "Legacy architecture obsolete" | Phase 1, Step 1.1 |
| R2 | Verify test coverage of `lightweight_matrix.py` >80% | Phase 1, Step 1.2 |
| R3 | Create `atom_evaluation.py` and migrate 6 DTOs | Phase 2, Step 2.1 |
| R4 | Implement Strangler Fig re-exports in `lightweight_matrix.py` | Phase 2, Step 2.2 |
| R5 | Move `AnchorValidationService` usage from DTO to Service Layer | Phase 3, Step 3.1 |
| R6 | Reduce `ValidationInfo.context` contract for `AtomEvaluationItemDTO` | Phase 3, Step 3.1b |
| R7 | Eradicate `hasattr(quote, "text")` duck-typing patterns | Phase 3, Step 3.2 |
| R8 | Eradicate `isinstance(quote, dict)` and `.get()` fallbacks | Phase 3, Step 3.3 |
| R9 | Fix duplicate `chart_display_label` validator bug | Phase 3, Step 3.3b |
| R10 | Move inline `import re` statements | Phase 3, Step 3.4 |
| R11 | Refactor hardcoded Finnish blacklists to injected Context | Phase 3, Step 3.5 |
| R12 | Clean up module-level imports in `atom_evaluation.py` | Phase 3, Step 3.6 |
| R13 | Update test fixtures for injected Context and instantiated quotes | Phase 3, Step 3.7 |
| R14 | Update consumer imports in batches of 5 | Phase 4, Step 4.1 |
| R15 | Remove Strangler Fig re-exports from `lightweight_matrix.py` | Phase 4, Step 4.2 |
| R16 | Sync Flutter UI Enums | Phase 5, Step 5.1 |
| R17 | Final Verification (Backend/Frontend Audit Loops) | Phase 6, Steps 6.1, 6.2 |

---

## Instructions for the Execution Agent

- You MUST perform an atomic `git commit` after ANY successful run of the `universal_quality_gate` audit script that passes.
- For testing the local DB re-seed, run: `uv run python backend_v2/seed/run_seed.py local`.
- ALWAYS specify exact relative file paths for git commands (specifically: `git add <target_path>`). Git commit messages MUST ALWAYS be written in English.
- Use `@-reference` syntax (e.g. `@[c:\src\quorum\...]`) to provide the exact context files in prompts.
- **You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session. Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the `/tier5-resume` command in your chat response so the user can easily copy-paste it to continue. The mandatory workflow loop is: `/tier0-research-plan` (Phase N) -> `/tier2-execute` (Phase N) -> `/tier8-audit-plan` (Phase N) -> `/tier0-research-plan` (Phase N+1). Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`.**
- **CRITICAL RULE FOR `--rules` PARAMETER (DYNAMIC CONTEXT):** When generating or updating the `/tier5-resume` command, you MUST dynamically construct the `--rules` parameter based on the domain of the upcoming Phase to prevent Context Amnesia. You MUST ALWAYS include the global core (`@[c:\src\quorum\.agents\rules\00-antigravity-core.md]`), the Epic-specific KIs (`@[c:\Users\risto\.gemini\antigravity-ide\knowledge\tripartite_pipeline_architecture\artifacts\ki_tripartite_pipeline_architecture.md]` and `@[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]`), **PLUS** the domain-specific rule file for the next phase (e.g., use `@[c:\src\quorum\.agents\rules\01-python-backend.md]` for Python phases, or `@[c:\src\quorum\.agents\rules\02_flutter_desktop.md]` for Phase 5 / Flutter). Do NOT hardcode a static string; adjust it intelligently for the handover.

---

# Session Handover Context

## Achieved
- Regenerated `EPIC_133A_lightweight_matrix_tracker.md` completely from scratch to meet the hyper-granular standard of `EPIC_130_tracker.md`.
- Generated rigorous XML implementation plans (`01` through `06`) focusing strictly on structural rules and explicit legacy test restoration (un-skipping tests).

## Learned
- **Baseline State Snapshot**: 
  - `lightweight_matrix.py` is currently a monolithic file (728 lines) acting as a God Object.
  - `test_lightweight_matrix.py` has exactly 10 tests marked with `@pytest.mark.skip("Legacy architecture obsolete")`. These must be structurally repaired in Phase 1 before any DTO extraction happens, because bypassing failing tests mathematically violates the Fail-Fast architecture.
  - Granular Tracker templates must explicitly list out execution `<step>` definitions rather than rolling them up into high-level phases.

## Remaining
- Proceed to Phase 1 Execution: Golden Master & Coverage Verification (which now involves restoring the 10 legacy tests).

## Resume Command
`/tier5-resume --workflow=/tier0-research-plan --target="@[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_133A_lightweight_matrix\01_golden_master_and_coverage.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md] @[c:\Users\risto\.gemini\antigravity-ide\knowledge\tripartite_pipeline_architecture\artifacts\ki_tripartite_pipeline_architecture.md] @[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]"`
