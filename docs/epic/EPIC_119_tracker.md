# EPIC 119: Universal XML Sandwich & Context Quarantine Standardization Tracker

**Epic Reference**: @[c:\src\quorum\docs\epic\EPIC_119_XML_Sandwich_Standardization.md]
**Task Directory**: @[c:\src\quorum\docs\epic\tasks_EPIC_119/]

## Phase Execution Status

### Phase 1: Modernize God Code Decomposition
- [x] **[SKIPPED] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_119\01_god_code_modernization.md]`
- [x] **[OK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_119_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_119\01_god_code_modernization.md]`
  - [x] `step id="1"`: VERIFY CODEBASE STATE
  - [x] `step id="2"`: INJECT HYBRID XML SANDWICH MANDATE
  - [x] `step id="3"`: REINFORCE SESSION HANDOVER
  - [x] `step id="4"`: TESTING & QUALITY GATE PLAN

### Phase 2: Restructure Feature Refactoring (Conditional Quarantine)
- [x] **[SKIPPED] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_119\02_feature_refactor_quarantine.md]`
- [x] **[OK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_119_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_119\02_feature_refactor_quarantine.md]`
  - [x] `step id="1"`: VERIFY CODEBASE STATE
  - [x] `step id="2"`: ADD CONDITIONAL QUARANTINE RULE
  - [x] `step id="3"`: INJECT COMPLEXITY ASSESSMENT GATE
  - [x] `step id="4"`: MODIFY ATOMIC EXECUTION BATCH
  - [x] `step id="5"`: TESTING & QUALITY GATE PLAN

### Phase 3: Context Quarantine for Bug Hunting
- [x] **[SKIPPED] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_119\03_bug_hunting_quarantine.md]`
- [x] **[OK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\EPIC_119_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_119\03_bug_hunting_quarantine.md]`
  - [x] `step id="1"`: VERIFY CODEBASE STATE
  - [x] `step id="2"`: ADD RCA QUARANTINE MANDATE
  - [x] `step id="3"`: MODIFY BLAST RADIUS & GENERATE PLAN
  - [x] `step id="4"`: IMPLEMENT QUARANTINE HANDOVER AND DELETE OLD STEPS
  - [x] `step id="5"`: TESTING & QUALITY GATE PLAN

### Integration Checkpoint: Full-Stack Validation
- [x] **[OK] Backend Integrity**: `uv run python scripts/backend_audit_loop.py . --test`
- [x] **[OK] Frontend Integrity**: `uv run python scripts/flutter_audit_loop.py client_app_v2/`

### Post-Implementation Gates
- [x] (N/A) **[OK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [x] (N/A) **[OK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [x] (N/A) **[OK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [x] (N/A) **[OK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [x] (N/A) **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [x] (N/A) **[OK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [x] **[OK]** Create a Knowledge Item (KI) for new SSOTs in `<appDataDir>/knowledge/`. (Created `agent_context_quarantine`)
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_119_XML_Sandwich_Standardization.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
- **Atomic Commit Mandate**: After EVERY single successfully completed target file and successful test run, you MUST instruct the user to execute an atomic `git commit` (e.g., `git commit -m "feat(epic119): update tier3 god code"`).
- **Seeding Environment**: If a database wipe is required, use `uv run python backend_v2/seed/run_seed.py local`.
- **References**: Always use `@-reference` syntax when pointing to files in commands or paths.
- **Workflow State Updates**: You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session.
- **Execution Tracking**: After completing a `<step id>`, update its state to `[x]` in this tracker file.

## Requirements Traceability Matrix

| Req ID | Requirement Description | Plan Ref | Step Ref |
|---|---|---|---|
| R1 | Inject `HYBRID_XML_SANDWICH_MANDATE` into `tier3-god-code-decomposition.md` Step 3 | 01_god_code_modernization.md | `step id="2"` |
| R2 | Require `phaseX_extraction.md` to use `<execution_protocol>` blocks | 01_god_code_modernization.md | `step id="2"` |
| R3 | Update `tier3-god-code-decomposition.md` Phase 4 and 5 for mandatory `/tier5-resume` | 01_god_code_modernization.md | `step id="3"` |
| R4 | Inject `conditional_context_quarantine` rule block in `tier3-feature-refactor.md` | 02_feature_refactor_quarantine.md | `step id="2"` |
| R5 | Threshold definition: >2 target files OR >3 distinct execution steps requires plan & `/tier5-resume` | 02_feature_refactor_quarantine.md | `step id="2"` |
| R6 | Inject `<gate name="COMPLEXITY_ASSESSMENT">` in `tier3-feature-refactor.md` Step 1 | 02_feature_refactor_quarantine.md | `step id="3"` |
| R7 | Modify ATOMIC EXECUTION BATCH in `tier3-feature-refactor.md` to defer execution if threshold breached | 02_feature_refactor_quarantine.md | `step id="4"` |
| R8 | Add `rca_quarantine_mandate` to `tier4-bug-hunting.md` | 03_bug_hunting_quarantine.md | `step id="2"` |
| R9 | Enforce bug fix deferral via `/tier2-execute` after RCA in `tier4-bug-hunting.md` | 03_bug_hunting_quarantine.md | `step id="2"` |
| R10 | Append plan generation instruction to `tier4-bug-hunting.md` Step 4 | 03_bug_hunting_quarantine.md | `step id="3"` |
| R11 | Explicitly delete old execution steps (5, 6, 7) in `tier4-bug-hunting.md` | 03_bug_hunting_quarantine.md | `step id="4"` |
| R12 | Add `<step id="5" name="QUARANTINE HANDOVER">` in `tier4-bug-hunting.md` | 03_bug_hunting_quarantine.md | `step id="4"` |
| R13 | Preserve ATOMIC INTERFACE EXCEPTION in `tier4-bug-hunting.md` | 03_bug_hunting_quarantine.md | `step id="4"` |

# Session Handover Context
## Achieved
- Marked non-applicable code-level Post-Implementation Gates as `[x] (N/A)`.
- Created Knowledge Item `agent_context_quarantine` for the new Hybrid XML Sandwich & Context Quarantine architecture.

## Learned
- **Domain Scope Check**: EPIC 119 was strictly a meta-architectural update affecting `.agents/workflows/` (markdown files only). Therefore, Backend and Frontend hardening loops, proxy sunsets, and API tests were not applicable and were correctly skipped.
- **KI Creation**: The new agentic workflows enforcing strict or conditional boundaries require their own KI to serve as the SSOT for AI execution behavior.

## Remaining
- [x] Execute Post-Implementation Gates (Phase 4).
- [ ] As-Built Architectural Sync: Run `/tier7-describe-architecture`.
- [ ] System 2 Reverse Epic Analysis: Run `/tier8-audit-epic`.

## Resume Command
`/tier5-resume --workflow=/tier7-describe-architecture --target="@[c:\src\quorum\docs\epic\EPIC_119_tracker.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md]"`
