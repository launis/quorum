# Tracker: EPIC [NUM] — [Title]

**Epic:** @[docs/epic/EPIC_XXX.md]
**Task Directory:** @[docs/epic/tasks_EPIC_XXX/]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## Phase Execution Status

### Phase 1: [Phase Name]
**Plan:** @[docs/epic/tasks_EPIC_XXX/01_phase1_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_XXX/01_phase1_plan.md] @[docs/epic/EPIC_XXX_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_XXX/01_phase1_plan.md] @[docs/epic/EPIC_XXX_tracker.md]`
  - [ ] Step 1: [Step Title]
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_XXX/01_phase1_plan.md] @[docs/epic/EPIC_XXX_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Backend & Frontend Full-Stack Integration Gate**

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_XXX_tracker.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[backend_v2/path/to/target.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_XXX_tracker.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/epic/EPIC_XXX_tracker.md] @[docs/epic/EPIC_XXX.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: [Explicit summary of architectural mechanisms, rules, or schemas introduced in this Epic to document]
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register all newly created or structurally relocated modules, scripts, and utilities from this Epic.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing newly established invariants in present tense without historical language or Epic IDs.

### Final Epic Audit

- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_XXX.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent

- **Atomic CommitMandate**: Commit each verified logical step with explicit relative paths in English.
- **Database Seeding**: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local`
- **Workflow Loop**: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute --full-auto -> /tier8-audit-plan -> Post-Implementation Gates -> parameterized /tier7-describe-architecture -> /tier8-audit-epic`. Always pass BOTH the plan and the tracker file in all commands.

## Requirements Traceability Matrix

| Requirement | Description | Phase / Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | [Granular technical requirement] | Phase 1, Step 1 | [ ] Pending |

# Session Handover Context

## Achieved
- [Completed items in this session]

## Learned
- [Baseline State Snapshot and architectural discoveries]

## Remaining
- [Specific tasks left for the next session]

## Resume Command
```powershell
/tier0-research-plan @[docs/epic/tasks_EPIC_XXX/01_phase1_plan.md] @[docs/epic/EPIC_XXX_tracker.md]
```

