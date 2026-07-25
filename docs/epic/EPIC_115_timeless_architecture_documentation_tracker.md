# Tracker: EPIC 115 - Timeless Architecture Documentation Reform

**Epic Reference**: @[c:\src\quorum\docs\epic\EPIC_115_timeless_architecture_documentation.md]
**Task Directory**: @[c:\src\quorum\docs\epic\tasks_EPIC_115/]

## Phase Execution Status

### Phase 1: Structural Scrubbing (Pillars 1-3)
- [ ] **[NOK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_115\01_structural_scrubbing_1_plan.md]`
- [ ] **[NOK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_115\01_structural_scrubbing_1_plan.md]`

### Phase 1: Structural Scrubbing (Pillars 4-6)
- [ ] **[NOK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_115\02_structural_scrubbing_2_plan.md]`
- [ ] **[NOK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_115\02_structural_scrubbing_2_plan.md]`

### Phase 1: Workflow Pillar Count Fix
- [ ] **[NOK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_115\03_structural_scrubbing_tier7_plan.md]`
- [ ] **[NOK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_115\03_structural_scrubbing_tier7_plan.md]`

### Phase 2: Dual-Axis Documentation Paradigm
- [ ] **[NOK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_115\04_dual_axis_core_plan.md]`
- [ ] **[NOK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_115\04_dual_axis_core_plan.md]`

### Phase 2: Workflow Re-Routing (Part 1)
- [ ] **[NOK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_115\05_workflow_rerouting_1_plan.md]`
- [ ] **[NOK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_115\05_workflow_rerouting_1_plan.md]`

### Phase 2: Workflow Re-Routing (Part 2)
- [ ] **[NOK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_115\06_workflow_rerouting_2_plan.md]`
- [ ] **[NOK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_115\06_workflow_rerouting_2_plan.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK]** Backend full-stack integration test gates.
- [ ] **[NOK]** Frontend full-stack integration test gates.

### Post-Implementation Gates
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py` (Note: Epic 115 specifies comprehensive `grep_search` verification as the functional equivalent for docs/rules)

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in `<appDataDir>/knowledge/`.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_115_timeless_architecture_documentation.md]`.

## Instructions for the Execution Agent
- Atomic commit mandates must be respected.
- If seeding is required, use: `uv run python backend_v2/seed/run_seed.py local`
- You MUST use `@-reference` syntax for all target file paths.
- **You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session.**

## Requirements Traceability Matrix

| Epic Requirement | Phase | Plan File | Status |
|---|---|---|---|
| Delete Rogue `__pycache__/` | Phase 0 | `02_structural_scrubbing_2_plan.md` | `[ ]` |
| Synthesize Physical Implementation Map Knowledge | Phase 1 | Plans `01_` and `02_` | `[ ]` |
| Remove Temporal Contamination & Physical Implementation Maps | Phase 1 | Plans `01_` and `02_` | `[ ]` |
| Fix Pillar Count References | Phase 1 | `03_structural_scrubbing_tier7_plan.md` | `[ ]` |
| Create Meta-Governance Document | Phase 2 | `04_dual_axis_core_plan.md` | `[ ]` |
| Harden Tier 7 Workflow | Phase 2 | `04_dual_axis_core_plan.md` | `[ ]` |
| Introduce Dual-Axis Documentation Mandate in Core Rules | Phase 2 | `04_dual_axis_core_plan.md` | `[ ]` |
| Re-route Execution Workflows | Phase 2 | Plans `05_` and `06_` | `[ ]` |
| Update Directory Reference | Phase 2 | `04_dual_axis_core_plan.md` | `[ ]` |
| Phase 1 Verification (Structural Scrubbing) | Phase 3 | Execution via Tracker Post-Gates | `[ ]` |
| Phase 2 Verification (Dual-Axis Paradigm) | Phase 3 | Execution via Tracker Post-Gates | `[ ]` |

# Session Handover Context
## Achieved
- 
## Learned
- 
## Remaining
- 

## Resume Command
`/tier5-resume --workflow=/tier2-execute --target="@[c:\src\quorum\docs\epic\EPIC_115_timeless_architecture_documentation_tracker.md] @[c:\src\quorum\docs\epic\EPIC_115_timeless_architecture_documentation.md] @[c:\src\quorum\docs\epic\tasks_EPIC_115\01_structural_scrubbing_1_plan.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\04_directory_reference.md]"`
