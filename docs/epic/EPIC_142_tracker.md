# EPIC 142 Tracker: Matrix Atom Boolean Evaluation Fix

**Epic Document:** @[docs/epic/EPIC_142_Matrix_Atom_Boolean_Evaluation_Fix.md]
**Task Directory:** @[docs/epic/EPIC_142/]

<required_context_rules>
- @[.agents/rules/00-antigravity-core.md]
- @[ki_god_code_prevention.md]
- @[ki_tripartite_pipeline_architecture.md]
- @[ki_sdui_matrix_synthesis.md]
- @[ki_dag_engine_dto_projection_rules.md]
- @[ki_ai_testing_standards.md]
- @[ki_ast_guardrail_testing.md]
- @[ki_python_314_concurrency_strictness.md]
</required_context_rules>

## Phase Execution Status

### Phase 1: DTO Boundary Lockdown & Pre-flight Coercion
**Plan:** @[docs/epic/EPIC_142/phase_1_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/EPIC_142/phase_1_plan.md] @[docs/epic/EPIC_142_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/EPIC_142/phase_1_plan.md] @[docs/epic/EPIC_142_tracker.md]`
  - [x] Step 1: Update LightweightMatrixOutput
  - [x] Step 2: Update TraceMatrixPayloadDTO
  - [x] Step 3: Verification
- [ ] **[FAILED] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit. (MISSING NEGATIVE TESTS)
- [x] **[FAILED] Audit:** `/tier8-audit-plan @[docs/epic/EPIC_142/phase_1_plan.md] @[docs/epic/EPIC_142_tracker.md]`

### Phase 1.5: Producer Contract Fix (scoring.py & execution.py)
**Plan:** @[docs/epic/EPIC_142/phase_1_5_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/EPIC_142/phase_1_5_plan.md] @[docs/epic/EPIC_142_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/EPIC_142/phase_1_5_plan.md] @[docs/epic/EPIC_142_tracker.md]`
  - [ ] Step 1: Update scoring.py
  - [ ] Step 2: Update execution.py
  - [ ] Step 3: Verification
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/EPIC_142/phase_1_5_plan.md] @[docs/epic/EPIC_142_tracker.md]`

### Phase 2: MatrixDomainParser Scoring Fix
**Plan:** @[docs/epic/EPIC_142/phase_2_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/EPIC_142/phase_2_plan.md] @[docs/epic/EPIC_142_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/EPIC_142/phase_2_plan.md] @[docs/epic/EPIC_142_tracker.md]`
  - [ ] Step 1: Update MatrixDomainParser
  - [ ] Step 2: Verification
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/EPIC_142/phase_2_plan.md] @[docs/epic/EPIC_142_tracker.md]`

### Phase 3: Synthesis Context Preservation
**Plan:** @[docs/epic/EPIC_142/phase_3_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/EPIC_142/phase_3_plan.md] @[docs/epic/EPIC_142_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/EPIC_142/phase_3_plan.md] @[docs/epic/EPIC_142_tracker.md]`
  - [ ] Step 1: Detailed plan will be generated during Tier 1 rolling planning.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/EPIC_142/phase_3_plan.md] @[docs/epic/EPIC_142_tracker.md]`

### Phase 4: Atomic Test Alignment (Test Expansion)
**Plan:** @[docs/epic/EPIC_142/phase_4_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/EPIC_142/phase_4_plan.md] @[docs/epic/EPIC_142_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/EPIC_142/phase_4_plan.md] @[docs/epic/EPIC_142_tracker.md]`
  - [ ] Step 1: Detailed plan will be generated during Tier 1 rolling planning.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/EPIC_142/phase_4_plan.md] @[docs/epic/EPIC_142_tracker.md]`

### Phase 5: Pydantic Schema CoT Ordering Audit & Fix
**Plan:** @[docs/epic/EPIC_142/phase_5_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/EPIC_142/phase_5_plan.md] @[docs/epic/EPIC_142_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/EPIC_142/phase_5_plan.md] @[docs/epic/EPIC_142_tracker.md]`
  - [ ] Step 1: Detailed plan will be generated during Tier 1 rolling planning.
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/EPIC_142/phase_5_plan.md] @[docs/epic/EPIC_142_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] Backend and Frontend full-stack integration test gates.

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in <appDataDir>/knowledge/.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** Epic Boundary Audit: Run `uv run python scripts/audit_markdown_boundaries.py --file @[docs\epic\EPIC_142_Matrix_Atom_Boolean_Evaluation_Fix.md]` to verify all AST line boundaries in the Epic are still correct.
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs\epic\EPIC_142_Matrix_Atom_Boolean_Evaluation_Fix.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
- Atomic commits are MANDATORY per file or cohesively related block of logic.
- If seeding is necessary, use `uv run python backend_v2/seed/run_seed.py local`.
- ALWAYS use `@-reference` syntax when referring to files (e.g. `@[backend_v2/models/dtos/lightweight_matrix.py]`).
- You MUST update the `/tier5-resume` or `/tier0-research-plan` command at the bottom of this tracker before handing over the session.
- Additionally, whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue.
- The mandatory workflow loop is: `/tier0-research-plan` (Phase N) -> `/tier2-execute` (Phase N) -> `/tier8-audit-plan` (Phase N) -> `/tier0-research-plan` (Phase N+1).
- You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands.
- Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates: `/tier2-hardening-backend` -> `/tier2-hardening-frontend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`.
- Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating.

## Requirements Traceability Matrix
| Requirement ID | Description | Mapped Step (Phase & Step ID) |
|---|---|---|
| REQ-142-01 | Enforce `LaxExecutionStatus` typing on `LightweightMatrixOutput.evaluated_atoms` to coerce "FAILED" strictly to Enum. | Phase 1, Step 1 |
| REQ-142-02 | Enforce `LaxExecutionStatus | None` typing on `TraceMatrixPayloadDTO.evaluated_atoms`. | Phase 1, Step 2 |
| REQ-142-03 | Prevent the use of legacy `@field_validator(mode="before")` duct-tape logic in DTOs. | Phase 1, Step 3 |
| REQ-142-04 | Update `scoring.py` producer to emit `ExecutionStatus.PASSED` instead of raw `True`. | Phase 1.5, Step 1 |
| REQ-142-05 | Update `scoring.py` producer to emit `ExecutionStatus.FAILED` instead of raw `False`. | Phase 1.5, Step 1 |
| REQ-142-06 | Update `scoring.py` producer to emit `ExecutionStatus.SYSTEM_ERROR` instead of `"DLQ"`. | Phase 1.5, Step 1 |
| REQ-142-07 | Update `scoring.py` producer to emit `ExecutionStatus.PASSED` instead of `"CONTESTED"`. | Phase 1.5, Step 1 |
| REQ-142-08 | Update `execution.py` producer override to set `payload.new_status` directly (Enum) instead of string value. | Phase 1.5, Step 2 |
| REQ-142-09 | Refactor `MatrixDomainParser` to use pure domain logic comparing `v == ExecutionStatus.PASSED`. | Phase 2, Step 1 |
| REQ-142-10 | Exclude `ExecutionStatus.N_A` from the `total_atoms` denominator in `MatrixDomainParser`. | Phase 2, Step 1 |
| REQ-142-11 | Explicitly handle `total_atoms == 0` without crashing in `MatrixDomainParser` (logging an intentional bypass). | Phase 2, Step 1 |

# Session Handover Context
## Achieved
- Executed Phase 1 implementation. Enforced LaxExecutionStatus typing on LightweightMatrixOutput.evaluated_atoms and TraceMatrixPayloadDTO.evaluated_atoms.
- Passed local unit tests for dtos with 93% coverage and verified strict typing using mypy via universal audit script.
- Committed the Phase 1 changes atomically.
- Completed Tier 8 Red-Team Audit for Phase 1 (Report: `@[red_team_audit_phase_1.md]`).

## Learned
- DTO validation logic accurately enforces the LaxExecutionStatus, confirming that the boundary is now locked.
- Tier 8 Audit FAILED (Red-Teamed) due to a violation of the `anti_happy_path_mandate`. There are currently no negative tests in the test suite validating that `LightweightMatrixOutput` and `TraceMatrixPayloadDTO` correctly coerce `"FAILED"` strings or explicitly reject raw `bool` values (`True`/`False`).
- Tier 1 Planner also dropped domain-specific rules (`01-python-backend.md`) from the plan's context list.

## Remaining
- The next step is to hand the session back to Tier 2 execution to write the missing negative unit tests for the DTO boundaries.
- Once the missing test coverage is implemented, the Phase 1 changes should be re-audited or we can move forward to Phase 1.5 if test assertions pass.

## Resume Command
`/tier2-execute --target="@[docs\epic\EPIC_142_tracker.md] @[docs\epic\EPIC_142\phase_1_plan.md]"`
