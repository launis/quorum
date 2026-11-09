# Tracker: Streamline Epic and Tracker Verification Gates

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Streamline_Epic_And_Tracker_Verification_Gates.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Streamline_Epic_And_Tracker_Verification_Gates.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Streamline_Epic_And_Tracker_Verification_Gates.md] @[docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md]`
  - [ ] Step 1: Streamline Epic Template, Tier 0 Create Epic Skill, and Tier 1 Planner Skill
  - [ ] Step 2: Streamline Epic and Standalone Plan Tracker Templates and Generator Skills
  - [ ] Step 3: Update Tracker Structural & Parity Auditors and Unit Test Suites
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Streamline_Epic_And_Tracker_Verification_Gates.md] @[docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[scripts/audit_plan_tracker_parity.py]
  - [ ] @[scripts/audit_tracker_output.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Streamline_Epic_And_Tracker_Verification_Gates.md] @[ki_god_code_prevention.md] @[ki_deterministic_hardening_state.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_deterministic_hardening_state.md]`: Document the streamlined Epic and standalone Plan tracker verification gate architecture across `@[scripts/audit_tracker_output.py]` and `@[scripts/audit_plan_tracker_parity.py]`, retaining `TRK008` and `TPR008` AI subagent hardening gates (`--agent-cmd`), `As-Built Architectural Sync`, `Final Epic Audit` / `Final Plan Audit`, and `Session Handover Context` while removing duplicate per-phase `/tier8-audit-plan` requirements and redundant prose checkboxes.
     - `@[ki_god_code_prevention.md]`: Document `<rule_block id="ban_verification_only_phases">` in `@[.agents/skills/tier0-create-epic/SKILL.md]` and `@[.agents/skills/tier1-planner/SKILL.md]` enforcing vertical code and unit test pairing inside implementation phases.
  2. **Directory Reference Sync:**
     - Verify `@[.agents/rules/04_directory_reference.md]` reflects current descriptions for `@[scripts/audit_tracker_output.py]` and `@[scripts/audit_plan_tracker_parity.py]`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing the streamlined Epic and tracker verification gate invariants in present tense without historical language or plan IDs.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Streamline_Epic_And_Tracker_Verification_Gates.md] @[docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[scripts/audit_tracker_output.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Remove `### Phase 4: Verification & E2E Integration Gate` from `## 3. Phased Execution Plan (Implementation Strategy)` in `@[.agents/skills/tier0-create-epic/resources/epic_template.md]` and update Phase 2 and Phase 3 bullets so companion unit and widget tests pair directly with production code while global audit loops and Live E2E reside in `## 4. Definition of Done (DoD) & Verification Plan`. | Step 1 | [ ] Pending |
| REQ-002 | Add `<rule_block id="ban_verification_only_phases">` to `@[.agents/skills/tier0-create-epic/SKILL.md]` and `@[.agents/skills/tier1-planner/SKILL.md]` prohibiting standalone verification-only phases (`04_phase4_plan.md`) and removing per-phase `Test Coverage Assertions` and `Audit: /tier8-audit-plan` requirements from Step 3 of `tier1-planner` while preserving `REQUIRED_FACTORY_SKILL_TOKENS` (`SKL003`) and `mandatory_ai_hardening_subagent_gate`. | Step 1 | [ ] Pending |
| REQ-003 | Streamline `@[.agents/skills/tier1-tracker-generator/resources/epic_tracker_template.md]` and `@[.agents/skills/tier1-tracker-generator/SKILL.md]` by removing per-phase `Test Coverage Assertions` and `Audit: /tier8-audit-plan` rows and the 4 manual prose checkboxes (`Golden Master & Test Restoration Audit`, `Proxy Sunset & Consumer Migration`, `Pre-Delete Audit`, and `Semantic Coverage & Zero-Loss Audit`) while strictly retaining `Integration Checkpoint`, `Tier 2 Hardening (Backend & Frontend)` with `--agent-cmd`, `Documentation & Knowledge Item Update`, and `Final Epic Audit`. | Step 2 | [ ] Pending |
| REQ-004 | Streamline `@[.agents/skills/tier1-plan-tracker-generator/resources/plan_tracker_template.md]` and `@[.agents/skills/tier1-plan-tracker-generator/SKILL.md]` by removing the duplicate `Audit: /tier8-audit-plan` row under the execution status header and the 3 manual prose checkboxes under `### Post-Implementation Gates` while strictly preserving `Tier 2 Hardening (Backend & Frontend)` (`--agent-cmd`), `Documentation & Knowledge Item Update`, and `Final Plan Audit`. | Step 2 | [ ] Pending |
| REQ-005 | Update `check_phase_format` (`@[scripts/audit_tracker_output.py#L99-L171]`) and `check_step_format` (`@[scripts/audit_tracker_output.py#L174-L253]`) to validate `**Plan:** @[...]`, `Execution:`, and indented `Step` checkboxes (`TRK002`) without requiring duplicate per-phase or step-section `Audit:` lines, while `check_mandatory_sections` (`TRK001`) enforces `### Final Epic Audit` and `### Final Plan Audit`. | Step 3 | [ ] Pending |
| REQ-006 | Prune `has_golden_master_gate`, `has_pre_delete_gate`, and `has_semantic_coverage_gate` from `TrackerDocumentAST`, `parse_tracker_document`, and `audit_plan_tracker_parity` in `@[scripts/audit_plan_tracker_parity.py#L128-L155]`, `@[scripts/audit_plan_tracker_parity.py#L294-L455]`, and `@[scripts/audit_plan_tracker_parity.py#L458-L840]`, while strictly enforcing `TPR008` `FATAL` checks on `has_backend_hardening_agent_cmd`, `has_frontend_hardening_agent_cmd`, `has_doc_sync_gate`, `has_final_audit_gate`, `has_session_handover`, and `has_resume_command`. | Step 3 | [ ] Pending |
| REQ-007 | Update unit test suites in `@[backend_v2/tests/unit/scripts/test_audit_tracker_output.py#L65-L207]`, `@[backend_v2/tests/unit/scripts/test_audit_tracker_output.py#L599-L610]`, `@[backend_v2/tests/unit/scripts/test_audit_tracker_output.py#L613-L649]`, `@[backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py#L81-L93]`, and `@[backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py#L392-L471]` to verify positive and negative boundary cases for `TRK001`, `TRK002`, `TRK008`, and `TPR008`. | Step 3 | [ ] Pending |

# Session Handover Context

## Achieved
- Generated standalone plan tracker `@[docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md]` for `@[docs/implementationplans/IMPLEMENTATION_PLAN_Streamline_Epic_And_Tracker_Verification_Gates.md]`.
- Mapped all 3 execution steps, 7 granular requirements (`REQ-001` through `REQ-007`), and both surviving production Python scripts (`@[scripts/audit_plan_tracker_parity.py]` and `@[scripts/audit_tracker_output.py]`) into the `Tier 2 Hardening (Backend)` AI subagent checklist.

## Learned
- Pre-flight technical debt audit across `@[scripts/audit_tracker_output.py]`, `@[scripts/audit_plan_tracker_parity.py]`, `@[backend_v2/tests/unit/scripts/test_audit_tracker_output.py]`, and `@[backend_v2/tests/unit/scripts/test_audit_plan_tracker_parity.py]` passed with 0 findings (`PASSED Clean`).
- `Tier 2 Hardening (Backend)` and `Tier 2 Hardening (Frontend)` with `--agent-cmd` (`TRK008` and `TPR008`) remain 100% enforced across both Epic and standalone Plan trackers.

## Remaining
- Execute `/tier0-research-plan` to red-team and validate `@[docs/implementationplans/IMPLEMENTATION_PLAN_Streamline_Epic_And_Tracker_Verification_Gates.md]`, followed by `/tier2-execute --full-auto` to implement Steps 1 through 3.
- Execute post-implementation `Tier 2 Hardening (Backend)`, `As-Built Architectural Sync` (`/tier7-describe-architecture`), and `System 2 Red-Team Audit` (`/tier8-audit-plan`).

## Resume Command
```powershell
/tier0-research-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Streamline_Epic_And_Tracker_Verification_Gates.md] @[docs/implementationplans/TRACKER_Streamline_Epic_And_Tracker_Verification_Gates.md]
```
